"""
app.py
======
Main Flask application for the College Lost-and-Found Management System.

Run locally:
    set FLASK_SECRET_KEY=change-this-key
    python app.py
"""

import os
import re
from datetime import datetime
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   flash, abort, send_from_directory, session, g)
from werkzeug.utils import secure_filename

import database as db
from data_structures import activity_feed, item_cache, request_queue
from matching import find_matches, find_all_matches, get_match_label

# ===========================================================================
# APPLICATION FACTORY
# ===========================================================================

app = Flask(__name__, instance_relative_config=False)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")

# ------------------------------------------------------------------
# Upload configuration
# ------------------------------------------------------------------
if os.environ.get("VERCEL"):
    UPLOAD_FOLDER = os.path.join("/tmp", "uploads")
else:
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024   # 5 MB limit
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# ------------------------------------------------------------------
# Item categories
# ------------------------------------------------------------------
CATEGORIES = [
    "ID Card",
    "Books and Stationery",
    "Electronics",
    "Wallet and Personal Belongings",
    "Water Bottle",
    "Clothing",
    "Keys",
    "Other",
]

# Admin passcode (set via environment variable; default for development only)
ADMIN_PASSCODE = os.environ.get("ADMIN_PASSCODE", "admin123")


# ===========================================================================
# STARTUP: initialize DB and rebuild in-memory data structures
# ===========================================================================

_initialized = False


def init_app():
    """Initialize database and in-memory data structures on startup."""
    global _initialized
    db.init_db()
    # In Vercel demo mode without DATABASE_URL, auto-seed with sample data if empty
    if db.is_temporary_storage():
        try:
            stats = db.get_dashboard_stats()
            if stats["total_lost"] == 0 and stats["total_found"] == 0:
                import seed_data
                seed_data.run_seed()
        except Exception as exc:
            app.logger.warning(f"Demo auto-seed skipped: {exc}")
    _rebuild_data_structures()
    _initialized = True


@app.before_request
def ensure_initialized():
    """Ensure database schema and cache are initialized in serverless environments."""
    if request.path.startswith("/static/"):
        return
    global _initialized
    if not _initialized:
        init_app()


def _rebuild_data_structures():
    """
    Load data from SQLite and populate the in-memory data structures.

    This keeps the custom data structures consistent with the database
    every time the application starts.
    """
    # --- Rebuild Hash Table: item_id -> item dict ---
    all_items, _ = db.get_items(per_page=10000)  # load all
    for item in all_items:
        item_cache.insert(item['id'], item)

    # --- Rebuild Linked List: recent activity ---
    recent = db.get_recent_activity(limit=20)
    for entry in reversed(recent):     # oldest first, so head = newest
        activity_feed.insert_at_head(entry)
    activity_feed.trim(20)

    # --- Rebuild Queue: pending collection requests ---
    pending = db.get_all_requests(status='pending')
    for req in reversed(pending):      # oldest first (FIFO order)
        request_queue.enqueue(req)


# ===========================================================================
# HELPER FUNCTIONS
# ===========================================================================

def allowed_file(filename):
    """Return True if the filename has an allowed extension."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def save_uploaded_file(file):
    """
    Validate and save an uploaded image file.
    Returns the saved filename, or None if no file was provided.
    Raises ValueError for invalid files.
    """
    if not file or file.filename == "":
        return None

    if not allowed_file(file.filename):
        raise ValueError(
            "Invalid file type. Allowed types: PNG, JPG, JPEG, GIF, WEBP."
        )

    # Generate a safe, unique filename
    ext = file.filename.rsplit(".", 1)[1].lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    safe_name = secure_filename(f"{timestamp}.{ext}")

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], safe_name))
    return safe_name


def validate_date(date_str):
    """
    Validate that date_str is a valid YYYY-MM-DD date that is not in
    the future. Returns the date string, or raises ValueError.
    """
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        raise ValueError("Please enter a valid date in YYYY-MM-DD format.")

    if date > datetime.now().date():
        raise ValueError("The date cannot be in the future.")

    return date_str


def is_admin():
    """Return True if the current session has admin privileges."""
    return session.get("is_admin", False)


def admin_required(f):
    """Decorator that requires admin login for state-changing operations."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_admin():
            flash("Administrator access is required for this action.", "error")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


# ===========================================================================
# CONTEXT PROCESSOR — make helpers available in all templates
# ===========================================================================

@app.context_processor
def inject_globals():
    return {
        "current_year": datetime.now().year,
        "is_admin": is_admin(),
        "categories": CATEGORIES,
        "is_temporary_storage": db.is_temporary_storage(),
    }


# ===========================================================================
# ERROR HANDLERS
# ===========================================================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404


@app.errorhandler(413)
def file_too_large(e):
    flash("The uploaded file is too large. Maximum size is 5 MB.", "error")
    return redirect(request.referrer or url_for("index"))


@app.errorhandler(db.DatabaseConnectionError)
def database_connection_error(e):
    app.logger.error(f"Database connection error: {e}")
    return render_template("errors/500.html", db_error=str(e)), 500


@app.errorhandler(500)
def internal_error(e):
    return render_template("errors/500.html"), 500



# ===========================================================================
# STATIC UPLOADS
# ===========================================================================

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """Serve uploaded images from the uploads folder."""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ===========================================================================
# DASHBOARD
# ===========================================================================

@app.route("/")
def index():
    stats = db.get_dashboard_stats()
    recent_lost  = db.get_recent_items("lost",  limit=5)
    recent_found = db.get_recent_items("found", limit=5)
    return render_template(
        "index.html",
        stats=stats,
        recent_lost=recent_lost,
        recent_found=recent_found,
    )


# ===========================================================================
# LOST ITEMS LISTING
# ===========================================================================

@app.route("/lost-items")
def lost_items():
    search    = request.args.get("search", "").strip()
    category  = request.args.get("category", "").strip()
    location  = request.args.get("location", "").strip()
    date_from = request.args.get("date_from", "").strip()
    date_to   = request.args.get("date_to", "").strip()
    page      = max(1, int(request.args.get("page", 1)))
    per_page  = 12

    items, total = db.get_items(
        item_type="lost",
        search=search or None,
        category=category or None,
        location=location or None,
        date_from=date_from or None,
        date_to=date_to or None,
        page=page,
        per_page=per_page,
    )

    total_pages = max(1, (total + per_page - 1) // per_page)
    locations = db.get_locations()

    return render_template(
        "lost_items.html",
        items=items,
        total=total,
        page=page,
        total_pages=total_pages,
        search=search,
        category=category,
        location=location,
        date_from=date_from,
        date_to=date_to,
        locations=locations,
    )


# ===========================================================================
# FOUND ITEMS LISTING
# ===========================================================================

@app.route("/found-items")
def found_items():
    search    = request.args.get("search", "").strip()
    category  = request.args.get("category", "").strip()
    location  = request.args.get("location", "").strip()
    date_from = request.args.get("date_from", "").strip()
    date_to   = request.args.get("date_to", "").strip()
    page      = max(1, int(request.args.get("page", 1)))
    per_page  = 12

    items, total = db.get_items(
        item_type="found",
        search=search or None,
        category=category or None,
        location=location or None,
        date_from=date_from or None,
        date_to=date_to or None,
        page=page,
        per_page=per_page,
    )

    total_pages = max(1, (total + per_page - 1) // per_page)
    locations = db.get_locations()

    return render_template(
        "found_items.html",
        items=items,
        total=total,
        page=page,
        total_pages=total_pages,
        search=search,
        category=category,
        location=location,
        date_from=date_from,
        date_to=date_to,
        locations=locations,
    )


# ===========================================================================
# REPORT A LOST ITEM
# ===========================================================================

@app.route("/report-lost", methods=["GET", "POST"])
def report_lost():
    if request.method == "POST":
        errors = []

        name     = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        desc     = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        date_str = request.form.get("event_date", "").strip()
        c_name   = request.form.get("contact_name", "").strip()
        c_info   = request.form.get("contact_info", "").strip()

        # Validation
        if not name:
            errors.append("Item name is required.")
        elif len(name) > 150:
            errors.append("Item name must be 150 characters or fewer.")

        if not category or category not in CATEGORIES:
            errors.append("Please select a valid category.")

        if not location:
            errors.append("Last-seen location is required.")
        elif len(location) > 200:
            errors.append("Location must be 200 characters or fewer.")

        if not date_str:
            errors.append("Date lost is required.")
        else:
            try:
                date_str = validate_date(date_str)
            except ValueError as e:
                errors.append(str(e))

        if not c_name:
            errors.append("Contact name is required.")

        if not c_info:
            errors.append("Contact information is required.")

        # File upload
        image_filename = None
        if "image" in request.files:
            try:
                image_filename = save_uploaded_file(request.files["image"])
            except ValueError as e:
                errors.append(str(e))

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template("report_lost.html",
                                   form=request.form,
                                   categories=CATEGORIES)

        # Save to database
        try:
            item_id = db.insert_item(
                name=name,
                category=category,
                description=desc,
                location=location,
                event_date=date_str,
                item_type="lost",
                image_filename=image_filename,
                contact_name=c_name,
                contact_info=c_info,
            )

            # Update in-memory structures
            new_item = db.get_item_by_id(item_id)
            if new_item:
                item_cache.insert(item_id, new_item)
                activity_feed.insert_at_head({
                    'item_id': item_id,
                    'item_name': name,
                    'item_type': 'lost',
                    'action': 'reported',
                    'details': f'Lost item reported: {name}',
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                })
                activity_feed.trim(20)

            flash(f"Lost item '{name}' has been reported successfully. Item ID: {item_id}", "success")
            return redirect(url_for("item_details", item_id=item_id))

        except Exception as e:
            flash("An error occurred while saving the report. Please try again.", "error")
            return render_template("report_lost.html",
                                   form=request.form,
                                   categories=CATEGORIES)

    return render_template("report_lost.html", form={}, categories=CATEGORIES)


# ===========================================================================
# REPORT A FOUND ITEM
# ===========================================================================

@app.route("/report-found", methods=["GET", "POST"])
def report_found():
    if request.method == "POST":
        errors = []

        name     = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        desc     = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        date_str = request.form.get("event_date", "").strip()
        c_info   = request.form.get("contact_info", "").strip()

        if not name:
            errors.append("Item name is required.")
        elif len(name) > 150:
            errors.append("Item name must be 150 characters or fewer.")

        if not category or category not in CATEGORIES:
            errors.append("Please select a valid category.")

        if not location:
            errors.append("Found location is required.")

        if not date_str:
            errors.append("Date found is required.")
        else:
            try:
                date_str = validate_date(date_str)
            except ValueError as e:
                errors.append(str(e))

        if not c_info:
            errors.append("Contact information is required.")

        image_filename = None
        if "image" in request.files:
            try:
                image_filename = save_uploaded_file(request.files["image"])
            except ValueError as e:
                errors.append(str(e))

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template("report_found.html",
                                   form=request.form,
                                   categories=CATEGORIES)

        try:
            item_id = db.insert_item(
                name=name,
                category=category,
                description=desc,
                location=location,
                event_date=date_str,
                item_type="found",
                image_filename=image_filename,
                contact_name=None,
                contact_info=c_info,
            )

            new_item = db.get_item_by_id(item_id)
            if new_item:
                item_cache.insert(item_id, new_item)
                activity_feed.insert_at_head({
                    'item_id': item_id,
                    'item_name': name,
                    'item_type': 'found',
                    'action': 'reported',
                    'details': f'Found item reported: {name}',
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                })
                activity_feed.trim(20)

            flash(f"Found item '{name}' has been registered successfully. Item ID: {item_id}", "success")
            return redirect(url_for("item_details", item_id=item_id))

        except Exception as e:
            flash("An error occurred while saving the report. Please try again.", "error")
            return render_template("report_found.html",
                                   form=request.form,
                                   categories=CATEGORIES)

    return render_template("report_found.html", form={}, categories=CATEGORIES)


# ===========================================================================
# REPORT AN ITEM (unified page linking to both)
# ===========================================================================

@app.route("/report")
def report():
    return render_template("report.html")


# ===========================================================================
# ITEM DETAILS
# ===========================================================================

@app.route("/item/<int:item_id>")
def item_details(item_id):
    # Try hash table first (O(1) average), fall back to database
    item = item_cache.search(item_id)
    if item is None:
        item = db.get_item_by_id(item_id)
    if item is None:
        abort(404)

    # Find possible matches
    possible_matches = []
    if item['status'] == 'active':
        if item['type'] == 'lost':
            found_items = db.get_active_items_by_type('found')
            raw_matches = find_matches(item, found_items)
        else:
            lost_items = db.get_active_items_by_type('lost')
            raw_matches = find_matches(item, lost_items)

        for m in raw_matches:
            m['label'] = get_match_label(m['score'])
        possible_matches = raw_matches

    # Existing collection requests for this item
    requests = db.get_all_requests()
    item_requests = [r for r in requests if r['item_id'] == item_id]

    return render_template(
        "item_details.html",
        item=item,
        possible_matches=possible_matches,
        item_requests=item_requests,
    )


# ===========================================================================
# SUBMIT COLLECTION REQUEST
# ===========================================================================

@app.route("/item/<int:item_id>/request", methods=["GET", "POST"])
def submit_request(item_id):
    item = db.get_item_by_id(item_id)
    if item is None:
        abort(404)

    if item['status'] not in ('active', 'verification_pending'):
        flash("This item is no longer accepting collection requests.", "error")
        return redirect(url_for("item_details", item_id=item_id))

    if request.method == "POST":
        errors = []
        req_name    = request.form.get("requester_name", "").strip()
        req_contact = request.form.get("requester_contact", "").strip()
        req_desc    = request.form.get("description", "").strip()

        if not req_name:
            errors.append("Your name is required.")
        if not req_contact:
            errors.append("Your contact information is required.")
        if not req_desc:
            errors.append("Please describe how you can prove ownership.")

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template("submit_request.html", item=item)

        try:
            req_id = db.insert_collection_request(
                item_id=item_id,
                requester_name=req_name,
                requester_contact=req_contact,
                description=req_desc,
            )
            # Add to in-memory queue
            new_req = db.get_request_by_id(req_id)
            if new_req:
                request_queue.enqueue(new_req)

            # Refresh item in cache
            updated_item = db.get_item_by_id(item_id)
            if updated_item:
                item_cache.insert(item_id, updated_item)

            flash("Your collection request has been submitted. "
                  "An administrator will review it shortly.", "success")
            return redirect(url_for("item_details", item_id=item_id))

        except ValueError as e:
            flash(str(e), "error")
        except Exception:
            flash("An error occurred. Please try again.", "error")

    return render_template("submit_request.html", item=item)


# ===========================================================================
# COLLECTION REQUESTS — public listing (limited info)
# ===========================================================================

@app.route("/collection-requests")
def collection_requests():
    status_filter = request.args.get("status", "").strip()
    all_requests = db.get_all_requests(status=status_filter or None)
    # Count pending items in the queue
    queue_size = request_queue.size()
    return render_template(
        "collection_requests.html",
        requests=all_requests,
        status_filter=status_filter,
        queue_size=queue_size,
    )


# ===========================================================================
# ADMIN LOGIN
# ===========================================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        passcode = request.form.get("passcode", "")
        if passcode == ADMIN_PASSCODE:
            session["is_admin"] = True
            flash("Logged in as administrator.", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Incorrect passcode.", "error")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("index"))


# ===========================================================================
# ADMIN DASHBOARD
# ===========================================================================

@app.route("/admin")
@admin_required
def admin_dashboard():
    pending_requests = db.get_all_requests(status="pending")
    stats = db.get_dashboard_stats()
    # Show current queue state from in-memory queue
    queue_snapshot = request_queue.to_list()
    return render_template(
        "admin_dashboard.html",
        pending_requests=pending_requests,
        stats=stats,
        queue_snapshot=queue_snapshot,
    )


# ===========================================================================
# ADMIN: UPDATE REQUEST STATUS
# ===========================================================================

@app.route("/admin/request/<int:request_id>/update", methods=["POST"])
@admin_required
def admin_update_request(request_id):
    new_status = request.form.get("status", "").strip()
    if new_status not in ("approved", "rejected"):
        flash("Invalid action.", "error")
        return redirect(url_for("admin_dashboard"))

    try:
        req = db.get_request_by_id(request_id)
        db.update_request_status(request_id, new_status)

        # Update hash table cache for the item
        if req:
            updated_item = db.get_item_by_id(req['item_id'])
            if updated_item:
                item_cache.insert(req['item_id'], updated_item)

        # Dequeue from the request_queue if it was at the front
        # (simplified: rebuild queue from pending requests)
        while not request_queue.is_empty():
            request_queue.dequeue()
        for pending in db.get_all_requests(status='pending'):
            request_queue.enqueue(pending)

        flash(f"Request #{request_id} has been {new_status}.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception:
        flash("An error occurred. Please try again.", "error")

    return redirect(url_for("admin_dashboard"))


# ===========================================================================
# ADMIN: UPDATE ITEM STATUS
# ===========================================================================

@app.route("/admin/item/<int:item_id>/status", methods=["POST"])
@admin_required
def admin_update_item_status(item_id):
    new_status = request.form.get("status", "").strip()
    try:
        db.update_item_status(item_id, new_status)
        updated_item = db.get_item_by_id(item_id)
        if updated_item:
            item_cache.insert(item_id, updated_item)
        flash(f"Item #{item_id} status updated to '{new_status}'.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception:
        flash("An error occurred.", "error")

    return redirect(url_for("item_details", item_id=item_id))


# ===========================================================================
# POSSIBLE MATCHES PAGE
# ===========================================================================

@app.route("/matches")
def matches_page():
    lost_items  = db.get_active_items_by_type("lost")
    found_items = db.get_active_items_by_type("found")
    all_matches = find_all_matches(lost_items, found_items)

    # Add confidence labels
    for group in all_matches:
        for m in group['matches']:
            m['label'] = get_match_label(m['score'])

    return render_template(
        "matches.html",
        all_matches=all_matches,
        total_lost=len(lost_items),
        total_found=len(found_items),
    )


# ===========================================================================
# ABOUT PAGE
# ===========================================================================

@app.route("/about")
def about():
    return render_template("about.html")


# ===========================================================================
# DATA STRUCTURES DEMO PAGE (for academic demonstration)
# ===========================================================================

@app.route("/ds-demo")
def ds_demo():
    """
    Shows the current state of the in-memory data structures.
    Useful for FDS project demonstration to faculty.
    """
    ll_items = activity_feed.to_list()
    ht_size  = item_cache.size()
    queue_items = request_queue.to_list()

    return render_template(
        "ds_demo.html",
        ll_items=ll_items,
        ht_size=ht_size,
        queue_items=queue_items,
        ll_size=activity_feed.size(),
    )


# ===========================================================================
# ENTRY POINT
# ===========================================================================

if __name__ == "__main__":
    init_app()
    app.run(debug=True, host="127.0.0.1", port=5000)
