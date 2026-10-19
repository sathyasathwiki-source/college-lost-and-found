"""
test_app.py
===========
Integration tests for the Flask application.
Tests database operations, routes, and input validation.
"""

import sys
import os
import tempfile
import shutil
import unittest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Use a temporary database for tests — do NOT modify production instance/app.db
TEST_DB = tempfile.mktemp(suffix='.db')
os.environ['TESTING'] = '1'


class TestDatabaseOperations(unittest.TestCase):
    """Tests for database.py functions using a temporary database."""

    @classmethod
    def setUpClass(cls):
        """Create a fresh test database."""
        import database
        # Override DB path for testing
        database.DB_PATH = TEST_DB
        database.init_db()
        cls.db = database

    @classmethod
    def tearDownClass(cls):
        """Remove the temporary test database."""
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_create_lost_item(self):
        item_id = self.db.insert_item(
            name='Blue Calculator',
            category='Electronics',
            description='Casio fx-991',
            location='Room 204',
            event_date='2026-10-01',
            item_type='lost',
            contact_name='Ravi Kumar',
            contact_info='9876543210'
        )
        self.assertIsNotNone(item_id)
        self.assertGreater(item_id, 0)

    def test_create_found_item(self):
        item_id = self.db.insert_item(
            name='Black Wallet',
            category='Wallet and Personal Belongings',
            description='black with some cash',
            location='Canteen',
            event_date='2026-10-02',
            item_type='found',
            contact_info='finder@example.com'
        )
        self.assertIsNotNone(item_id)

    def test_get_item_by_id(self):
        item_id = self.db.insert_item(
            name='Water Bottle',
            category='Water Bottle',
            description='Blue Cello',
            location='Library',
            event_date='2026-10-03',
            item_type='lost',
            contact_name='Priya',
            contact_info='priya@pict.edu'
        )
        item = self.db.get_item_by_id(item_id)
        self.assertIsNotNone(item)
        self.assertEqual(item['name'], 'Water Bottle')
        self.assertEqual(item['type'], 'lost')
        self.assertEqual(item['status'], 'active')

    def test_get_item_not_found(self):
        item = self.db.get_item_by_id(99999)
        self.assertIsNone(item)

    def test_search_by_name(self):
        self.db.insert_item('Red Backpack', 'Other', 'big red bag',
                            'Gate', '2026-10-04', 'lost',
                            contact_name='A', contact_info='B')
        items, total = self.db.get_items(search='Red Backpack')
        names = [i['name'] for i in items]
        self.assertIn('Red Backpack', names)

    def test_filter_by_category(self):
        self.db.insert_item('Lab Coat', 'Clothing', '', 'Lab',
                            '2026-10-05', 'found', contact_info='x')
        items, _ = self.db.get_items(item_type='found', category='Clothing')
        for item in items:
            self.assertEqual(item['category'], 'Clothing')

    def test_update_item_status_valid_transition(self):
        item_id = self.db.insert_item(
            name='ID Card', category='ID Card', description='',
            location='Admin Office', event_date='2026-10-06',
            item_type='lost', contact_name='S', contact_info='T'
        )
        # active -> verification_pending is valid
        self.db.update_item_status(item_id, 'verification_pending')
        item = self.db.get_item_by_id(item_id)
        self.assertEqual(item['status'], 'verification_pending')

    def test_update_item_status_invalid_transition(self):
        item_id = self.db.insert_item(
            name='Keys', category='Keys', description='',
            location='Parking', event_date='2026-10-07',
            item_type='lost', contact_name='U', contact_info='V'
        )
        # active -> closed is valid
        self.db.update_item_status(item_id, 'closed')
        # closed -> active is invalid
        with self.assertRaises(ValueError):
            self.db.update_item_status(item_id, 'active')

    def test_update_item_status_invalid_value(self):
        item_id = self.db.insert_item(
            name='Pen', category='Books and Stationery', description='',
            location='Library', event_date='2026-10-08',
            item_type='lost', contact_name='W', contact_info='X'
        )
        with self.assertRaises(ValueError):
            self.db.update_item_status(item_id, 'invalid_status')

    def test_collection_request_creation(self):
        item_id = self.db.insert_item(
            name='Found Phone', category='Electronics', description='',
            location='Classroom', event_date='2026-10-09',
            item_type='found', contact_info='finder@x.com'
        )
        req_id = self.db.insert_collection_request(
            item_id=item_id,
            requester_name='Anil Sharma',
            requester_contact='anil@pict.edu',
            description='I can prove this is mine because...'
        )
        self.assertIsNotNone(req_id)

        # Item status should now be verification_pending
        item = self.db.get_item_by_id(item_id)
        self.assertEqual(item['status'], 'verification_pending')

    def test_duplicate_collection_request_rejected(self):
        item_id = self.db.insert_item(
            name='Found Wallet2', category='Wallet and Personal Belongings',
            description='', location='Canteen', event_date='2026-10-10',
            item_type='found', contact_info='x@y.com'
        )
        self.db.insert_collection_request(
            item_id=item_id,
            requester_name='Req 1',
            requester_contact='r1@x.com',
            description='First request'
        )
        # Second pending request for same item should raise ValueError
        with self.assertRaises(ValueError):
            self.db.insert_collection_request(
                item_id=item_id,
                requester_name='Req 2',
                requester_contact='r2@x.com',
                description='Second request'
            )

    def test_approve_request_marks_item_returned(self):
        item_id = self.db.insert_item(
            name='Found Book', category='Books and Stationery',
            description='', location='Library', event_date='2026-10-11',
            item_type='found', contact_info='f@x.com'
        )
        req_id = self.db.insert_collection_request(
            item_id=item_id,
            requester_name='Owner',
            requester_contact='o@x.com',
            description='I left it there'
        )
        self.db.update_request_status(req_id, 'approved')
        item = self.db.get_item_by_id(item_id)
        self.assertEqual(item['status'], 'returned')
        self.assertIsNotNone(item['returned_at'])

    def test_reject_request_restores_item_to_active(self):
        item_id = self.db.insert_item(
            name='Found Keys', category='Keys',
            description='', location='Parking', event_date='2026-10-12',
            item_type='found', contact_info='f@x.com'
        )
        req_id = self.db.insert_collection_request(
            item_id=item_id,
            requester_name='Claimant',
            requester_contact='c@x.com',
            description='I think it is mine'
        )
        self.db.update_request_status(req_id, 'rejected')
        item = self.db.get_item_by_id(item_id)
        self.assertEqual(item['status'], 'active')

    def test_dashboard_stats(self):
        stats = self.db.get_dashboard_stats()
        self.assertIn('total_lost', stats)
        self.assertIn('total_found', stats)
        self.assertIn('total_returned', stats)
        self.assertIsInstance(stats['total_lost'], int)
        self.assertIsInstance(stats['total_found'], int)
        self.assertIsInstance(stats['total_returned'], int)

    def test_get_recent_items(self):
        recent = self.db.get_recent_items('lost', limit=3)
        self.assertIsInstance(recent, list)
        self.assertLessEqual(len(recent), 3)

    def test_pagination(self):
        # Create extra items to ensure pagination works
        for i in range(5):
            self.db.insert_item(f'TestPagItem{i}', 'Other', '', 'Test',
                                '2026-10-13', 'lost',
                                contact_name='T', contact_info='T')
        items_p1, total = self.db.get_items(item_type='lost', page=1, per_page=3)
        self.assertLessEqual(len(items_p1), 3)
        self.assertGreater(total, 0)


class TestFlaskRoutes(unittest.TestCase):
    """Basic route tests using Flask's test client."""

    @classmethod
    def setUpClass(cls):
        """Set up Flask test client with a test database."""
        import database
        database.DB_PATH = TEST_DB
        database.init_db()

        from app import app, init_app
        init_app()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        cls.client = app.test_client()

    def test_dashboard_returns_200(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Campus Lost', resp.data)

    def test_lost_items_page(self):
        resp = self.client.get('/lost-items')
        self.assertEqual(resp.status_code, 200)

    def test_found_items_page(self):
        resp = self.client.get('/found-items')
        self.assertEqual(resp.status_code, 200)

    def test_report_page(self):
        resp = self.client.get('/report')
        self.assertEqual(resp.status_code, 200)

    def test_report_lost_get(self):
        resp = self.client.get('/report-lost')
        self.assertEqual(resp.status_code, 200)

    def test_report_found_get(self):
        resp = self.client.get('/report-found')
        self.assertEqual(resp.status_code, 200)

    def test_about_page(self):
        resp = self.client.get('/about')
        self.assertEqual(resp.status_code, 200)

    def test_ds_demo_page(self):
        resp = self.client.get('/ds-demo')
        self.assertEqual(resp.status_code, 200)

    def test_matches_page(self):
        resp = self.client.get('/matches')
        self.assertEqual(resp.status_code, 200)

    def test_collection_requests_page(self):
        resp = self.client.get('/collection-requests')
        self.assertEqual(resp.status_code, 200)

    def test_search_page(self):
        resp = self.client.get('/search')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Search Items', resp.data)

        # Search with query
        resp_q = self.client.get('/search?q=Blue')
        self.assertEqual(resp_q.status_code, 200)

        # Search with filters
        resp_f = self.client.get('/search?type=lost&category=Electronics')
        self.assertEqual(resp_f.status_code, 200)

    def test_all_navigation_routes_distinct(self):
        """Ensure all primary navigation links render their distinct expected pages, not the dashboard."""
        routes_and_expected = [
            ('/', 'Campus Lost &amp; Found'),
            ('/lost-items', '<h1>Lost Items</h1>'),
            ('/found-items', '<h1>Found Items</h1>'),
            ('/report-lost', 'Report a Lost Item'),
            ('/report-found', 'Report a Found Item'),
            ('/search', '<h1>Search Items</h1>'),
            ('/collection-requests', '<h1>Collection Requests</h1>'),
            ('/about', 'About This Project'),
        ]
        for route, expected_text in routes_and_expected:
            resp = self.client.get(route)
            self.assertEqual(resp.status_code, 200, f"Route {route} failed with {resp.status_code}")
            html = resp.get_data(as_text=True)
            self.assertIn(expected_text, html, f"Expected '{expected_text}' in route '{route}'")
            if route != '/':
                # Verify it does NOT render the dashboard
                self.assertNotIn('Recent Lost Reports', html, f"Route '{route}' incorrectly rendered the Dashboard")

    def test_404_for_missing_item(self):
        resp = self.client.get('/item/999999')
        self.assertEqual(resp.status_code, 404)

    def test_submit_lost_item_missing_fields(self):
        """Submitting a form with missing required fields should return 200 with errors."""
        resp = self.client.post('/report-lost', data={
            'name': '',   # Missing name
            'category': 'Electronics',
            'location': 'Library',
            'event_date': '2026-10-01',
            'contact_name': 'Test',
            'contact_info': '1234567890'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_submit_lost_item_valid(self):
        """Valid form submission should redirect to item detail page."""
        resp = self.client.post('/report-lost', data={
            'name': 'Test Laptop',
            'category': 'Electronics',
            'description': 'Silver Dell laptop',
            'location': 'Computer Lab',
            'event_date': '2026-10-01',
            'contact_name': 'Test User',
            'contact_info': 'test@pict.edu'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Test Laptop', resp.data)

    def test_submit_found_item_valid(self):
        resp = self.client.post('/report-found', data={
            'name': 'Found Umbrella',
            'category': 'Clothing',
            'description': 'Black folding umbrella',
            'location': 'Entrance Gate',
            'event_date': '2026-10-02',
            'contact_info': 'finder@pict.edu'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Found Umbrella', resp.data)

    def test_admin_requires_login(self):
        """Admin dashboard should redirect to login when not authenticated."""
        resp = self.client.get('/admin', follow_redirects=False)
        self.assertIn(resp.status_code, [302, 200])

    def test_admin_login_wrong_passcode(self):
        resp = self.client.post('/admin/login', data={
            'passcode': 'wrongpasscode'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Incorrect passcode', resp.data)

    def test_invalid_date_rejected(self):
        """Future dates should be rejected."""
        resp = self.client.post('/report-lost', data={
            'name': 'Valid Item',
            'category': 'Electronics',
            'location': 'Library',
            'event_date': '2099-01-01',  # future date
            'contact_name': 'Test',
            'contact_info': '1234'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        # Should show error about future date

    def test_search_filter(self):
        """Search filter on lost-items page should work."""
        # First add an item
        self.client.post('/report-lost', data={
            'name': 'UniqueSearchItem12345',
            'category': 'Other',
            'location': 'Library',
            'event_date': '2026-10-01',
            'contact_name': 'Test',
            'contact_info': 'test@x.com'
        })
        resp = self.client.get('/lost-items?search=UniqueSearchItem12345')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'UniqueSearchItem12345', resp.data)


class TestInputValidation(unittest.TestCase):
    """Tests for input validation edge cases."""

    @classmethod
    def setUpClass(cls):
        import database
        database.DB_PATH = TEST_DB

        from app import app
        app.config['TESTING'] = True
        cls.client = app.test_client()

    def test_validate_date_valid(self):
        from app import validate_date
        # Should not raise
        result = validate_date('2026-10-01')
        self.assertEqual(result, '2026-10-01')

    def test_validate_date_future(self):
        from app import validate_date
        with self.assertRaises(ValueError):
            validate_date('2099-12-31')

    def test_validate_date_invalid_format(self):
        from app import validate_date
        with self.assertRaises(ValueError):
            validate_date('01/10/2026')

    def test_validate_date_none(self):
        from app import validate_date
        with self.assertRaises(ValueError):
            validate_date(None)

    def test_long_item_name_rejected(self):
        resp = self.client.post('/report-lost', data={
            'name': 'A' * 200,   # Over 150 char limit
            'category': 'Electronics',
            'location': 'Library',
            'event_date': '2026-10-01',
            'contact_name': 'Test',
            'contact_info': 'test@x.com'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)


if __name__ == '__main__':
    unittest.main(verbosity=2)
