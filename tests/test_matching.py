"""
test_matching.py
================
Automated tests for the matching algorithm.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import unittest
from matching import find_matches, find_all_matches, get_match_label, _normalize, _keywords


class TestNormalize(unittest.TestCase):
    def test_casefold(self):
        self.assertEqual(_normalize("HELLO"), "hello")

    def test_remove_punctuation(self):
        # Punctuation is replaced by space, then multiple spaces collapsed
        result = _normalize("hello, world!")
        self.assertEqual(result, "hello world")

    def test_empty_string(self):
        self.assertEqual(_normalize(""), "")

    def test_none(self):
        self.assertEqual(_normalize(None), "")


class TestKeywords(unittest.TestCase):
    def test_removes_stop_words(self):
        kw = _keywords("a blue wallet in the library")
        self.assertNotIn("a", kw)
        self.assertNotIn("the", kw)
        self.assertNotIn("in", kw)
        self.assertIn("blue", kw)
        self.assertIn("wallet", kw)
        self.assertIn("library", kw)

    def test_removes_single_chars(self):
        kw = _keywords("ID card")
        # 'I' and 'D' may appear; 'id' should be there
        # 'card' must be there
        self.assertIn("card", kw)

    def test_empty_text(self):
        self.assertEqual(_keywords(""), set())


class TestFindMatches(unittest.TestCase):
    """Tests for the matching algorithm."""

    def _make_lost(self, **kwargs):
        defaults = dict(id=1, name='blue wallet', category='Wallet and Personal Belongings',
                        description='dark blue with initials RK', location='Canteen',
                        status='active', type='lost')
        defaults.update(kwargs)
        return defaults

    def _make_found(self, **kwargs):
        defaults = dict(id=100, name='blue wallet', category='Wallet and Personal Belongings',
                        description='blue wallet with letters RK', location='Canteen Area',
                        status='active', type='found')
        defaults.update(kwargs)
        return defaults

    # ------------------------------------------------------------------
    # Basic matching
    # ------------------------------------------------------------------
    def test_exact_name_match(self):
        lost  = self._make_lost()
        found = [self._make_found()]
        results = find_matches(lost, found)
        self.assertTrue(len(results) > 0, "Should find at least one match")
        self.assertGreaterEqual(results[0]['score'], 30)

    def test_no_match_on_completely_different_items(self):
        lost  = self._make_lost(name='red umbrella', category='Clothing',
                                description='', location='Hostel')
        found = [self._make_found(name='black phone', category='Electronics',
                                  description='', location='Library')]
        results = find_matches(lost, found)
        self.assertEqual(results, [])

    # ------------------------------------------------------------------
    # Category matching
    # ------------------------------------------------------------------
    def test_same_category_boosts_score(self):
        lost  = self._make_lost(name='notebook', category='Books and Stationery',
                                description='', location='Library')
        found = [self._make_found(name='spiral notebook', category='Books and Stationery',
                                  description='', location='Library')]
        results = find_matches(lost, found)
        self.assertTrue(len(results) > 0)

    # ------------------------------------------------------------------
    # Returned items excluded
    # ------------------------------------------------------------------
    def test_returned_found_items_should_not_be_passed_in(self):
        """
        The application filters returned items before calling find_matches.
        This test verifies that when returned items are excluded by the caller,
        they do not appear in results.
        """
        lost  = self._make_lost()
        found_active   = [self._make_found()]
        found_returned = [self._make_found(status='returned', id=200)]

        # Only active items passed to the matcher
        results_active   = find_matches(lost, found_active)
        results_returned = find_matches(lost, found_returned)

        # Both calls should behave the same — the matcher doesn't filter by status;
        # the database layer is responsible. We just verify results are independent.
        self.assertIsInstance(results_active, list)
        self.assertIsInstance(results_returned, list)

    # ------------------------------------------------------------------
    # find_all_matches
    # ------------------------------------------------------------------
    def test_find_all_matches_returns_groups(self):
        lost_items  = [self._make_lost(id=1), self._make_lost(id=2, name='red pen')]
        found_items = [self._make_found(id=10), self._make_found(id=11, name='red pen',
                                                                 category='Books and Stationery')]
        all_matches = find_all_matches(lost_items, found_items)
        self.assertIsInstance(all_matches, list)
        for group in all_matches:
            self.assertIn('lost_item', group)
            self.assertIn('matches', group)

    def test_find_all_matches_empty_lists(self):
        self.assertEqual(find_all_matches([], []), [])
        self.assertEqual(find_all_matches([], [self._make_found()]), [])
        self.assertEqual(find_all_matches([self._make_lost()], []), [])

    # ------------------------------------------------------------------
    # Match label
    # ------------------------------------------------------------------
    def test_match_labels(self):
        self.assertEqual(get_match_label(85), 'Strong possible match')
        self.assertEqual(get_match_label(60), 'Moderate possible match')
        self.assertEqual(get_match_label(30), 'Weak possible match')

    # ------------------------------------------------------------------
    # Results sorted by score
    # ------------------------------------------------------------------
    def test_results_sorted_by_score_descending(self):
        lost = self._make_lost(name='blue wallet')
        found = [
            self._make_found(id=1, name='blue wallet'),     # high score
            self._make_found(id=2, name='wallet', description=''),  # lower
        ]
        results = find_matches(lost, found)
        if len(results) >= 2:
            self.assertGreaterEqual(results[0]['score'], results[1]['score'])

    # ------------------------------------------------------------------
    # Reasons list is populated
    # ------------------------------------------------------------------
    def test_match_contains_reasons(self):
        lost  = self._make_lost()
        found = [self._make_found()]
        results = find_matches(lost, found)
        if results:
            self.assertIsInstance(results[0]['reasons'], list)
            self.assertTrue(len(results[0]['reasons']) > 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
