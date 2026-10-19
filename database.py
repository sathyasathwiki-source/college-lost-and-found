"""
database.py
===========
Database initialization and all database helper functions.

Supports persistent PostgreSQL databases (configured via DATABASE_URL or POSTGRES_URL)
for cloud serverless deployments (such as Vercel), with seamless fallback to SQLite
for local development and automated testing.
All queries use parameterized statements to prevent SQL injection.
"""

import os
import re
import sqlite3
from datetime import datetime, date


class DatabaseConnectionError(Exception):
    """Raised when connecting to or initializing the database fails."""
    pass


def get_db_url():
    """
    Return the persistent PostgreSQL database connection URL from the environment.
    Supports both DATABASE_URL and POSTGRES_URL.
    Normalizes 'postgres://' to 'postgresql://'.
    """
    url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if url:
        url = url.strip()
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
    return url


def is_postgres():
    """
    Return True if PostgreSQL should be used.
    In testing environments (TESTING=1) or when no DATABASE_URL is set,
    falls back to SQLite.
    """
    if os.environ.get("TESTING") == "1":
        return False
    return bool(get_db_url())


def get_default_db_path():
    """
    Determine a safe default path for SQLite.
    Does not depend on a rigid, unavailable directory in serverless environments.
    """
    custom_path = os.environ.get("DB_PATH") or os.environ.get("SQLITE_DB_PATH")
    if custom_path:
        return custom_path
    if os.environ.get("VERCEL"):
        # Filesystems outside /tmp are read-only on Vercel
        return os.path.join("/tmp", "app.db")
    return os.path.join(os.path.dirname(__file__), "instance", "app.db")


# Path to the SQLite database file (can be overridden by tests or env)
DB_PATH = get_default_db_path()


def _format_val(v):
    """Convert datetime/date objects to string formatted like SQLite/Jinja expect."""
    if isinstance(v, (datetime, date)):
        return v.strftime("%Y-%m-%d %H:%M:%S")
    return v


class RowDict(dict):
    """
    A dict subclass that also supports access by integer index (like sqlite3.Row).
    Supports:
      - row['col_name']
      - row[0]
      - dict(row)
    """
    def __init__(self, mapping=None, indexed=None):
        super().__init__(mapping or {})
        self._indexed = list(indexed) if indexed is not None else list(self.values())

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._indexed[key]
        return super().__getitem__(key)


class PostgresCursorWrapper:
    """
    Wraps a psycopg2 cursor to provide sqlite3-compatible behaviors:
      - Automatically translates SQL parameter placeholders from '?' to '%s'
      - Converts 'LIKE' to 'ILIKE' for case-insensitive keyword searching
      - Handles RETURNING id for INSERT statements to populate cursor.lastrowid
      - Formats fetched rows into RowDict with string timestamps
    """
    def __init__(self, raw_cursor):
        self._cursor = raw_cursor
        self.lastrowid = None

    @property
    def description(self):
        return self._cursor.description

    def execute(self, sql, params=None):
        # 1. Parameter placeholder translation
        converted_sql = sql.replace("?", "%s")

        # 2. Case-insensitive search keyword replacement
        converted_sql = re.sub(r"\bLIKE\b", "ILIKE", converted_sql)

        # 3. Handle INSERT statements with auto-increment ID
        trimmed = converted_sql.strip()
        is_insert = trimmed.upper().startswith("INSERT INTO")
        has_returning = "RETURNING" in trimmed.upper()

        if is_insert and not has_returning:
            sql_returning = trimmed.rstrip("; \t\n") + " RETURNING id"
            try:
                if params is not None:
                    self._cursor.execute(sql_returning, tuple(params))
                else:
                    self._cursor.execute(sql_returning)
                row = self._cursor.fetchone()
                if row:
                    self.lastrowid = row[0]
                return self
            except Exception:
                # If table does not have an 'id' column or RETURNING is unsupported,
                # fall through to standard execute
                pass

        if params is not None:
            self._cursor.execute(converted_sql, tuple(params))
        else:
            self._cursor.execute(converted_sql)
        return self

    def fetchone(self):
        if not self._cursor.description:
            return None
        row = self._cursor.fetchone()
        if row is None:
            return None
        return self._format_row(row)

    def fetchall(self):
        if not self._cursor.description:
            return []
        rows = self._cursor.fetchall()
        return [self._format_row(r) for r in rows]

    def _format_row(self, raw_tuple):
        if not self._cursor.description:
            return raw_tuple
        col_names = [col[0] for col in self._cursor.description]
        formatted = [_format_val(v) for v in raw_tuple]
        mapping = dict(zip(col_names, formatted))
        return RowDict(mapping, formatted)

    def close(self):
        self._cursor.close()

    def __iter__(self):
        return iter(self.fetchall())


class PostgresConnectionWrapper:
    """
    Wraps a psycopg2 connection to provide sqlite3.Connection compatible interface:
      - conn.execute(sql, params)
      - conn.cursor()
      - conn.commit()
      - conn.rollback()
      - conn.close()
    """
    def __init__(self, raw_conn):
        self._conn = raw_conn

    def cursor(self):
        return PostgresCursorWrapper(self._conn.cursor())

    def execute(self, sql, params=None):
        cur = self.cursor()
        cur.execute(sql, params)
        return cur

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.close()


def get_connection():
    """
    Open and return a connection to the database.

    If DATABASE_URL or POSTGRES_URL is configured (and not in testing mode),
    opens a connection to the persistent PostgreSQL database.
    Otherwise, opens a connection to the local SQLite database.
    """
    if is_postgres():
        try:
            import psycopg2
        except ImportError as exc:
            raise DatabaseConnectionError(
                "PostgreSQL driver 'psycopg2' is not installed. "
                "Please install 'psycopg2-binary'."
            ) from exc

        db_url = get_db_url()
        try:
            raw_conn = psycopg2.connect(db_url)
            return PostgresConnectionWrapper(raw_conn)
        except Exception as exc:
            raise DatabaseConnectionError(
                f"Failed to connect to PostgreSQL database: {exc}. "
                "Please check your DATABASE_URL in Vercel project environment variables."
            ) from exc
    else:
        # Check if running on Vercel without DATABASE_URL
        if os.environ.get("VERCEL") and not os.environ.get("TESTING"):
            raise DatabaseConnectionError(
                "DATABASE_URL environment variable is missing in the Vercel serverless environment. "
                "Vercel serverless filesystems are read-only and ephemeral, so persistent SQLite storage is unavailable. "
                "Please configure DATABASE_URL in your Vercel Project Settings -> Environment Variables."
            )

        try:
            db_dir = os.path.dirname(os.path.abspath(DB_PATH))
            if db_dir:
                try:
                    os.makedirs(db_dir, exist_ok=True)
                except OSError:
                    pass

            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            # Enforce foreign-key constraints (SQLite disables them by default)
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except Exception as exc:
            raise DatabaseConnectionError(
                f"Failed to connect to SQLite database at '{DB_PATH}': {exc}"
            ) from exc


def init_db():
    """
    Create all tables and indexes if they do not already exist.
    Called once when the Flask application starts.
    """
    if not is_postgres():
        db_dir = os.path.dirname(os.path.abspath(DB_PATH))
        if db_dir:
            try:
                os.makedirs(db_dir, exist_ok=True)
            except OSError:
                pass

    conn = get_connection()
    try:
        cursor = conn.cursor()

        if is_postgres():
            # ----------------------------------------------------------
            # PostgreSQL Tables & Schema
            # ----------------------------------------------------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id              SERIAL PRIMARY KEY,
                    name            TEXT    NOT NULL,
                    category        TEXT    NOT NULL,
                    description     TEXT,
                    location        TEXT    NOT NULL,
                    event_date      TEXT    NOT NULL,
                    type            TEXT    NOT NULL CHECK(type IN ('lost','found')),
                    status          TEXT    NOT NULL DEFAULT 'active'
                                            CHECK(status IN ('active','verification_pending','returned','closed')),
                    image_filename  TEXT,
                    contact_name    TEXT,
                    contact_info    TEXT,
                    created_at      TEXT    NOT NULL DEFAULT TO_CHAR(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS'),
                    returned_at     TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS collection_requests (
                    id              SERIAL PRIMARY KEY,
                    item_id         INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
                    requester_name  TEXT    NOT NULL,
                    requester_contact TEXT  NOT NULL,
                    description     TEXT,
                    request_date    TEXT    NOT NULL DEFAULT TO_CHAR(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS'),
                    status          TEXT    NOT NULL DEFAULT 'pending'
                                            CHECK(status IN ('pending','approved','rejected'))
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id          SERIAL PRIMARY KEY,
                    item_id     INTEGER REFERENCES items(id) ON DELETE SET NULL,
                    action      TEXT    NOT NULL,
                    details     TEXT,
                    created_at  TEXT    NOT NULL DEFAULT TO_CHAR(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS')
                )
            """)
        else:
            # ----------------------------------------------------------
            # SQLite Tables & Schema
            # ----------------------------------------------------------
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    name            TEXT    NOT NULL,
                    category        TEXT    NOT NULL,
                    description     TEXT,
                    location        TEXT    NOT NULL,
                    event_date      TEXT    NOT NULL,
                    type            TEXT    NOT NULL CHECK(type IN ('lost','found')),
                    status          TEXT    NOT NULL DEFAULT 'active'
                                            CHECK(status IN ('active','verification_pending','returned','closed')),
                    image_filename  TEXT,
                    contact_name    TEXT,
                    contact_info    TEXT,
                    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
                    returned_at     TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS collection_requests (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id         INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
                    requester_name  TEXT    NOT NULL,
                    requester_contact TEXT  NOT NULL,
                    description     TEXT,
                    request_date    TEXT    NOT NULL DEFAULT (datetime('now')),
                    status          TEXT    NOT NULL DEFAULT 'pending'
                                            CHECK(status IN ('pending','approved','rejected'))
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id     INTEGER REFERENCES items(id) ON DELETE SET NULL,
                    action      TEXT    NOT NULL,
                    details     TEXT,
                    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
                )
            """)

        # --------------------------------------------------------------
        # Indexes — speed up common queries (same for both dialects)
        # --------------------------------------------------------------
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_type     ON items(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_status   ON items(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_category ON items(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_created  ON items(created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_requests_item  ON collection_requests(item_id)")

        conn.commit()
    except Exception as exc:
        conn.rollback()
        raise DatabaseConnectionError(f"Failed to initialize database schema: {exc}") from exc
    finally:
        conn.close()


# ===========================================================================
# ITEM CRUD
# ===========================================================================

def insert_item(name, category, description, location, event_date,
                item_type, image_filename=None, contact_name=None,
                contact_info=None):
    """
    Insert a new item record and return its generated ID.
    item_type must be 'lost' or 'found'.
    """
    conn = get_connection()
    try:
        cursor = conn.execute("""
            INSERT INTO items
                (name, category, description, location, event_date,
                 type, image_filename, contact_name, contact_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, category, description, location, event_date,
              item_type, image_filename, contact_name, contact_info))
        item_id = cursor.lastrowid

        # Log the action
        conn.execute("""
            INSERT INTO activity_logs (item_id, action, details)
            VALUES (?, ?, ?)
        """, (item_id, 'reported', f'{item_type.capitalize()} item reported: {name}'))

        conn.commit()
        return item_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_item_by_id(item_id):
    """Return a single item row as a dict, or None if not found."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_items(item_type=None, status=None, category=None,
              search=None, location=None, date_from=None,
              date_to=None, page=1, per_page=12):
    """
    Return a paginated list of items matching the given filters.

    Returns: (items_list, total_count)
    """
    conditions = []
    params = []

    if item_type:
        conditions.append("type = ?")
        params.append(item_type)
    if status:
        conditions.append("status = ?")
        params.append(status)
    if category:
        conditions.append("category = ?")
        params.append(category)
    if search:
        conditions.append("(name LIKE ? OR description LIKE ? OR location LIKE ?)")
        like = f"%{search}%"
        params.extend([like, like, like])
    if location:
        conditions.append("location LIKE ?")
        params.append(f"%{location}%")
    if date_from:
        conditions.append("event_date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("event_date <= ?")
        params.append(date_to)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    offset = (page - 1) * per_page

    conn = get_connection()
    try:
        total = conn.execute(
            f"SELECT COUNT(*) FROM items {where}", params
        ).fetchone()[0]

        rows = conn.execute(
            f"SELECT * FROM items {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
            params + [per_page, offset]
        ).fetchall()

        return [dict(r) for r in rows], total
    finally:
        conn.close()


def update_item_status(item_id, new_status):
    """
    Update an item's status with a validated transition.

    Valid transitions:
      active -> verification_pending
      active -> returned
      verification_pending -> returned
      verification_pending -> active   (rejected claim)
      any -> closed
    """
    valid_statuses = {'active', 'verification_pending', 'returned', 'closed'}
    if new_status not in valid_statuses:
        raise ValueError(f"Invalid status: {new_status}")

    conn = get_connection()
    try:
        item = conn.execute(
            "SELECT status FROM items WHERE id = ?", (item_id,)
        ).fetchone()

        if item is None:
            raise ValueError(f"Item {item_id} not found.")

        current = item['status']

        # Define allowed transitions
        allowed = {
            'active': {'verification_pending', 'returned', 'closed'},
            'verification_pending': {'returned', 'active', 'closed'},
            'returned': {'closed'},
            'closed': set(),
        }

        if new_status not in allowed.get(current, set()):
            raise ValueError(
                f"Cannot transition from '{current}' to '{new_status}'."
            )

        returned_at = (
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if new_status == 'returned' else None
        )

        conn.execute("""
            UPDATE items SET status = ?, returned_at = ?
            WHERE id = ?
        """, (new_status, returned_at, item_id))

        conn.execute("""
            INSERT INTO activity_logs (item_id, action, details)
            VALUES (?, ?, ?)
        """, (item_id, 'status_change', f'Status changed to {new_status}'))

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_dashboard_stats():
    """Return aggregate counts for the dashboard."""
    conn = get_connection()
    try:
        total_lost = conn.execute(
            "SELECT COUNT(*) FROM items WHERE type='lost'"
        ).fetchone()[0]
        total_found = conn.execute(
            "SELECT COUNT(*) FROM items WHERE type='found'"
        ).fetchone()[0]
        total_returned = conn.execute(
            "SELECT COUNT(*) FROM items WHERE status='returned'"
        ).fetchone()[0]
        return {
            'total_lost': total_lost,
            'total_found': total_found,
            'total_returned': total_returned,
        }
    finally:
        conn.close()


def get_recent_items(item_type, limit=5):
    """Return the `limit` most recently reported items of a given type."""
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT * FROM items
            WHERE type = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (item_type, limit)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_active_items_by_type(item_type):
    """Return all active items of a given type (for matching)."""
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT * FROM items
            WHERE type = ? AND status = 'active'
        """, (item_type,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ===========================================================================
# COLLECTION REQUESTS
# ===========================================================================

def insert_collection_request(item_id, requester_name, requester_contact,
                               description=None):
    """
    Insert a new collection request and return its ID.
    Also updates the item's status to 'verification_pending'.
    """
    conn = get_connection()
    try:
        # Prevent duplicate pending requests for the same item
        existing = conn.execute("""
            SELECT id FROM collection_requests
            WHERE item_id = ? AND status = 'pending'
        """, (item_id,)).fetchone()
        if existing:
            raise ValueError("A pending request already exists for this item.")

        cursor = conn.execute("""
            INSERT INTO collection_requests
                (item_id, requester_name, requester_contact, description)
            VALUES (?, ?, ?, ?)
        """, (item_id, requester_name, requester_contact, description))
        request_id = cursor.lastrowid

        # Move item to verification_pending
        conn.execute("""
            UPDATE items SET status = 'verification_pending' WHERE id = ?
        """, (item_id,))

        conn.execute("""
            INSERT INTO activity_logs (item_id, action, details)
            VALUES (?, ?, ?)
        """, (item_id, 'collection_request',
              f'Collection request submitted by {requester_name}'))

        conn.commit()
        return request_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_all_requests(status=None):
    """Return all collection requests, optionally filtered by status."""
    conn = get_connection()
    try:
        if status:
            rows = conn.execute("""
                SELECT cr.*, i.name AS item_name, i.type AS item_type,
                       i.category AS item_category
                FROM collection_requests cr
                JOIN items i ON cr.item_id = i.id
                WHERE cr.status = ?
                ORDER BY cr.request_date DESC
            """, (status,)).fetchall()
        else:
            rows = conn.execute("""
                SELECT cr.*, i.name AS item_name, i.type AS item_type,
                       i.category AS item_category
                FROM collection_requests cr
                JOIN items i ON cr.item_id = i.id
                ORDER BY cr.request_date DESC
            """).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_request_by_id(request_id):
    """Return a single collection request as a dict."""
    conn = get_connection()
    try:
        row = conn.execute("""
            SELECT cr.*, i.name AS item_name, i.type AS item_type
            FROM collection_requests cr
            JOIN items i ON cr.item_id = i.id
            WHERE cr.id = ?
        """, (request_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_request_status(request_id, new_status):
    """Approve or reject a collection request."""
    valid = {'pending', 'approved', 'rejected'}
    if new_status not in valid:
        raise ValueError(f"Invalid request status: {new_status}")

    conn = get_connection()
    try:
        req = conn.execute(
            "SELECT * FROM collection_requests WHERE id = ?", (request_id,)
        ).fetchone()
        if req is None:
            raise ValueError(f"Request {request_id} not found.")

        conn.execute(
            "UPDATE collection_requests SET status = ? WHERE id = ?",
            (new_status, request_id)
        )

        # Update item status based on decision
        if new_status == 'approved':
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conn.execute("""
                UPDATE items SET status = 'returned',
                                 returned_at = ?
                WHERE id = ?
            """, (now_str, req['item_id']))
            conn.execute("""
                INSERT INTO activity_logs (item_id, action, details)
                VALUES (?, ?, ?)
            """, (req['item_id'], 'returned', 'Item returned to owner'))
        elif new_status == 'rejected':
            conn.execute("""
                UPDATE items SET status = 'active' WHERE id = ?
            """, (req['item_id'],))

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ===========================================================================
# ACTIVITY LOGS (for in-memory data structure population)
# ===========================================================================

def get_recent_activity(limit=20):
    """Return the most recent activity log entries."""
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT al.*, i.name AS item_name, i.type AS item_type
            FROM activity_logs al
            LEFT JOIN items i ON al.item_id = i.id
            ORDER BY al.created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_locations():
    """Return a sorted list of distinct locations for filter dropdowns."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT DISTINCT location FROM items ORDER BY location"
        ).fetchall()
        return [r['location'] for r in rows]
    finally:
        conn.close()
