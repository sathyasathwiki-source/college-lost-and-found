"""
test_postgres_compat.py
=======================
Tests for PostgreSQL compatibility layer, RowDict, SQL query translation,
and database error handling.
"""

import sys
import os
from datetime import datetime, date
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import database as db
from database import (
    RowDict,
    PostgresCursorWrapper,
    PostgresConnectionWrapper,
    DatabaseConnectionError,
    _format_val,
)


class DummyPsycopgCursor:
    """Mock psycopg2 cursor for testing wrapper behavior without a live database."""

    def __init__(self):
        self.description = None
        self.executed_sql = None
        self.executed_params = None
        self.results = []
        self._pos = 0
        self.closed = False

    def execute(self, sql, params=None):
        self.executed_sql = sql
        self.executed_params = params

        if "COUNT(*)" in sql:
            self.description = [("count", 23, None, None, None, None, None)]
            self.results = [(15,)]
        elif "RETURNING id" in sql:
            self.description = [("id", 23, None, None, None, None, None)]
            self.results = [(99,)]
        elif "SELECT * FROM items" in sql:
            self.description = [
                ("id", 23, None, None, None, None, None),
                ("name", 25, None, None, None, None, None),
                ("created_at", 1114, None, None, None, None, None),
            ]
            self.results = [(1, "Casio Calculator", datetime(2026, 10, 19, 14, 30, 0))]
        elif "SELECT DISTINCT location" in sql:
            self.description = [("location", 25, None, None, None, None, None)]
            self.results = [("Canteen",), ("Library",)]
        else:
            self.description = None
            self.results = []
        self._pos = 0

    def fetchone(self):
        if self._pos < len(self.results):
            row = self.results[self._pos]
            self._pos += 1
            return row
        return None

    def fetchall(self):
        res = self.results[self._pos:]
        self._pos = len(self.results)
        return res

    def close(self):
        self.closed = True


class DummyPsycopgConnection:
    """Mock psycopg2 connection."""

    def __init__(self):
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self):
        return DummyPsycopgCursor()

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


class TestPostgresCompatibility(unittest.TestCase):
    """Test the PostgreSQL emulation layer and data types."""

    def test_row_dict_key_and_index_access(self):
        r = RowDict({"id": 5, "name": "Keys"}, [5, "Keys"])
        self.assertEqual(r["name"], "Keys")
        self.assertEqual(r["id"], 5)
        self.assertEqual(r[0], 5)
        self.assertEqual(r[1], "Keys")
        self.assertEqual(dict(r), {"id": 5, "name": "Keys"})

    def test_format_val_datetime_to_string(self):
        dt = datetime(2026, 10, 19, 10, 15, 30)
        formatted = _format_val(dt)
        self.assertEqual(formatted, "2026-10-19 10:15:30")
        self.assertEqual(formatted[:10], "2026-10-19")

        d = date(2026, 10, 19)
        formatted_d = _format_val(d)
        self.assertEqual(formatted_d[:10], "2026-10-19")

        self.assertEqual(_format_val("already string"), "already string")
        self.assertIsNone(_format_val(None))

    def test_cursor_placeholder_and_ilike_translation(self):
        raw_cur = DummyPsycopgCursor()
        cur = PostgresCursorWrapper(raw_cur)

        cur.execute("SELECT * FROM items WHERE name LIKE ? AND category = ?", ["%book%", "Books"])
        self.assertEqual(raw_cur.executed_sql, "SELECT * FROM items WHERE name ILIKE %s AND category = %s")
        self.assertEqual(raw_cur.executed_params, ("%book%", "Books"))

    def test_cursor_insert_returning_lastrowid(self):
        raw_cur = DummyPsycopgCursor()
        cur = PostgresCursorWrapper(raw_cur)

        cur.execute("INSERT INTO items (name, category) VALUES (?, ?)", ["Umbrella", "Clothing"])
        self.assertIn("RETURNING id", raw_cur.executed_sql)
        self.assertEqual(cur.lastrowid, 99)

    def test_cursor_count_and_slice(self):
        raw_cur = DummyPsycopgCursor()
        cur = PostgresCursorWrapper(raw_cur)

        row = cur.execute("SELECT COUNT(*) FROM items WHERE type = ?", ["lost"]).fetchone()
        self.assertEqual(row[0], 15)
        self.assertEqual(row["count"], 15)

    def test_cursor_datetime_row_formatting(self):
        raw_cur = DummyPsycopgCursor()
        cur = PostgresCursorWrapper(raw_cur)

        item = cur.execute("SELECT * FROM items WHERE id = ?", [1]).fetchone()
        self.assertEqual(item["name"], "Casio Calculator")
        self.assertEqual(item["created_at"], "2026-10-19 14:30:00")
        # Ensure Jinja string slicing works without TypeError
        self.assertEqual(item["created_at"][:10], "2026-10-19")

    def test_connection_wrapper_methods(self):
        raw_conn = DummyPsycopgConnection()
        conn = PostgresConnectionWrapper(raw_conn)

        cur = conn.execute("SELECT DISTINCT location FROM items ORDER BY location")
        locations = cur.fetchall()
        self.assertEqual(len(locations), 2)
        self.assertEqual(locations[0]["location"], "Canteen")

        conn.commit()
        self.assertTrue(raw_conn.committed)

        conn.rollback()
        self.assertTrue(raw_conn.rolled_back)

        conn.close()
        self.assertTrue(raw_conn.closed)

    def test_database_url_normalization(self):
        os.environ["DATABASE_URL"] = "postgres://user:pass@ep-host.neon.tech/neondb?sslmode=require"
        try:
            url = db.get_db_url()
            self.assertTrue(url.startswith("postgresql://"))
        finally:
            del os.environ["DATABASE_URL"]

    def test_vercel_missing_database_url_fallback(self):
        """On Vercel, if DATABASE_URL is missing, it falls back to temporary SQLite storage."""
        orig_vercel = os.environ.get("VERCEL")
        orig_testing = os.environ.get("TESTING")
        orig_url = os.environ.get("DATABASE_URL")

        try:
            os.environ["VERCEL"] = "1"
            if "TESTING" in os.environ:
                del os.environ["TESTING"]
            if "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]

            self.assertTrue(db.is_temporary_storage())
            conn = db.get_connection()
            self.assertIsNotNone(conn)
            conn.close()
        finally:
            if orig_vercel is not None:
                os.environ["VERCEL"] = orig_vercel
            else:
                os.environ.pop("VERCEL", None)

            if orig_testing is not None:
                os.environ["TESTING"] = orig_testing
            else:
                os.environ.pop("TESTING", None)

            if orig_url is not None:
                os.environ["DATABASE_URL"] = orig_url

    def test_vercel_path_middleware_restores_path(self):
        """Verify that VercelPathMiddleware preserves client routes and does not force dashboard."""
        from app import app
        client = app.test_client()

        # 1. When Vercel sets X-Matched-Path: / on home dashboard
        resp = client.get('/', headers={'X-Matched-Path': '/'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Campus Lost", resp.get_data(as_text=True))

        # 2. When Vercel sets X-Matched-Path: / on sub-routes, route MUST NOT be overwritten with /
        resp_found = client.get('/found-items', headers={'X-Matched-Path': '/'})
        self.assertEqual(resp_found.status_code, 200)
        html_found = resp_found.get_data(as_text=True)
        self.assertIn("Found Items", html_found)
        self.assertNotIn("Recent Lost Reports", html_found)

        resp_lost = client.get('/lost-items', headers={'X-Matched-Path': '/'})
        self.assertEqual(resp_lost.status_code, 200)
        html_lost = resp_lost.get_data(as_text=True)
        self.assertIn("Lost Items", html_lost)
        self.assertNotIn("Recent Lost Reports", html_lost)

        resp_search = client.get('/search', headers={'X-Matched-Path': '/'})
        self.assertEqual(resp_search.status_code, 200)
        self.assertIn("Search Items", resp_search.get_data(as_text=True))

        resp_req = client.get('/collection-requests', headers={'X-Matched-Path': '/'})
        self.assertEqual(resp_req.status_code, 200)
        self.assertIn("Collection Requests", resp_req.get_data(as_text=True))

        resp_rep_l = client.get('/report-lost', headers={'X-Matched-Path': '/'})
        self.assertEqual(resp_rep_l.status_code, 200)
        self.assertIn("Report a Lost Item", resp_rep_l.get_data(as_text=True))

        resp_rep_f = client.get('/report-found', headers={'X-Matched-Path': '/'})
        self.assertEqual(resp_rep_f.status_code, 200)
        self.assertIn("Report a Found Item", resp_rep_f.get_data(as_text=True))

        # 3. Direct access to serverless entrypoint /api/index
        resp_root = client.get('/api/index')
        self.assertEqual(resp_root.status_code, 200)

        # 4. Entrypoint prefix stripping (/api/index/about -> /about)
        resp_prefix = client.get('/api/index/about')
        self.assertEqual(resp_prefix.status_code, 200)
        self.assertIn("About This Project", resp_prefix.get_data(as_text=True))

        # 5. Reverse proxy X-Forwarded-Uri header on /api/index
        resp_fwd = client.get('/api/index', headers={'X-Forwarded-Uri': '/found-items'})
        self.assertEqual(resp_fwd.status_code, 200)
        self.assertIn("Found Items", resp_fwd.get_data(as_text=True))

        # 6. Specific X-Matched-Path (non-root) on /api/index
        resp_matched = client.get('/api/index', headers={'X-Matched-Path': '/about'})
        self.assertEqual(resp_matched.status_code, 200)
        self.assertIn("About This Project", resp_matched.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
