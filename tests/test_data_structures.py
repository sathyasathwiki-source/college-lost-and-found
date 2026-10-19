"""
test_data_structures.py
=======================
Automated tests for the custom data structures:
  - LinkedList
  - HashTable
  - Queue
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import unittest
from data_structures import LinkedList, HashTable, Queue


class TestLinkedList(unittest.TestCase):
    """Tests for the custom singly linked list."""

    def setUp(self):
        self.ll = LinkedList()

    # ------------------------------------------------------------------
    # Empty state
    # ------------------------------------------------------------------
    def test_empty_on_creation(self):
        self.assertTrue(self.ll.is_empty())
        self.assertEqual(self.ll.size(), 0)
        self.assertEqual(self.ll.to_list(), [])

    # ------------------------------------------------------------------
    # Insert at head
    # ------------------------------------------------------------------
    def test_insert_at_head_single(self):
        self.ll.insert_at_head({'id': 1, 'name': 'book'})
        self.assertFalse(self.ll.is_empty())
        self.assertEqual(self.ll.size(), 1)

    def test_insert_at_head_order(self):
        """Head insertion means most-recently inserted item is first."""
        self.ll.insert_at_head({'id': 1, 'name': 'book'})
        self.ll.insert_at_head({'id': 2, 'name': 'wallet'})
        self.ll.insert_at_head({'id': 3, 'name': 'keys'})
        result = self.ll.to_list()
        self.assertEqual(result[0]['id'], 3)   # Most recent at head
        self.assertEqual(result[1]['id'], 2)
        self.assertEqual(result[2]['id'], 1)

    # ------------------------------------------------------------------
    # Insert at tail
    # ------------------------------------------------------------------
    def test_insert_at_tail_order(self):
        self.ll.insert_at_tail({'id': 1})
        self.ll.insert_at_tail({'id': 2})
        self.ll.insert_at_tail({'id': 3})
        result = self.ll.to_list()
        self.assertEqual(result[0]['id'], 1)
        self.assertEqual(result[2]['id'], 3)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    def test_search_found(self):
        self.ll.insert_at_head({'id': 10, 'name': 'calculator'})
        self.ll.insert_at_head({'id': 20, 'name': 'water bottle'})
        found = self.ll.search('id', 10)
        self.assertIsNotNone(found)
        self.assertEqual(found['name'], 'calculator')

    def test_search_not_found(self):
        self.ll.insert_at_head({'id': 1, 'name': 'book'})
        result = self.ll.search('id', 999)
        self.assertIsNone(result)

    def test_search_empty_list(self):
        result = self.ll.search('id', 1)
        self.assertIsNone(result)

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------
    def test_delete_head(self):
        self.ll.insert_at_head({'id': 1, 'name': 'book'})
        self.ll.insert_at_head({'id': 2, 'name': 'pen'})
        deleted = self.ll.delete('id', 2)   # head is id=2
        self.assertTrue(deleted)
        self.assertEqual(self.ll.size(), 1)
        self.assertIsNone(self.ll.search('id', 2))
        self.assertIsNotNone(self.ll.search('id', 1))

    def test_delete_middle(self):
        self.ll.insert_at_tail({'id': 1})
        self.ll.insert_at_tail({'id': 2})
        self.ll.insert_at_tail({'id': 3})
        deleted = self.ll.delete('id', 2)
        self.assertTrue(deleted)
        self.assertEqual(self.ll.size(), 2)
        ids = [item['id'] for item in self.ll.to_list()]
        self.assertNotIn(2, ids)
        self.assertIn(1, ids)
        self.assertIn(3, ids)

    def test_delete_tail(self):
        self.ll.insert_at_tail({'id': 1})
        self.ll.insert_at_tail({'id': 2})
        deleted = self.ll.delete('id', 2)
        self.assertTrue(deleted)
        self.assertEqual(self.ll.size(), 1)

    def test_delete_not_found(self):
        self.ll.insert_at_head({'id': 1})
        deleted = self.ll.delete('id', 999)
        self.assertFalse(deleted)

    def test_delete_from_empty(self):
        deleted = self.ll.delete('id', 1)
        self.assertFalse(deleted)

    # ------------------------------------------------------------------
    # Traversal
    # ------------------------------------------------------------------
    def test_to_list(self):
        for i in range(5):
            self.ll.insert_at_tail({'id': i})
        result = self.ll.to_list()
        self.assertEqual(len(result), 5)

    # ------------------------------------------------------------------
    # Trim
    # ------------------------------------------------------------------
    def test_trim(self):
        for i in range(10):
            self.ll.insert_at_head({'id': i})
        self.ll.trim(5)
        self.assertEqual(self.ll.size(), 5)

    def test_trim_to_zero(self):
        for i in range(5):
            self.ll.insert_at_head({'id': i})
        self.ll.trim(0)
        self.assertTrue(self.ll.is_empty())


class TestHashTable(unittest.TestCase):
    """Tests for the custom hash table with chaining."""

    def setUp(self):
        self.ht = HashTable(capacity=8)   # Small capacity to force collisions

    # ------------------------------------------------------------------
    # Basic operations
    # ------------------------------------------------------------------
    def test_insert_and_search(self):
        self.ht.insert(1, {'name': 'book'})
        result = self.ht.search(1)
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'book')

    def test_search_missing_key(self):
        result = self.ht.search(999)
        self.assertIsNone(result)

    def test_size_after_inserts(self):
        self.ht.insert(1, 'a')
        self.ht.insert(2, 'b')
        self.ht.insert(3, 'c')
        self.assertEqual(self.ht.size(), 3)

    # ------------------------------------------------------------------
    # Update (upsert)
    # ------------------------------------------------------------------
    def test_insert_updates_existing_key(self):
        self.ht.insert(5, {'status': 'active'})
        self.ht.insert(5, {'status': 'returned'})
        result = self.ht.search(5)
        self.assertEqual(result['status'], 'returned')
        self.assertEqual(self.ht.size(), 1)   # Still one entry

    def test_update_existing_key(self):
        self.ht.insert(10, 'old')
        updated = self.ht.update(10, 'new')
        self.assertTrue(updated)
        self.assertEqual(self.ht.search(10), 'new')

    def test_update_missing_key(self):
        updated = self.ht.update(999, 'value')
        self.assertFalse(updated)

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------
    def test_delete_existing(self):
        self.ht.insert(7, 'value')
        deleted = self.ht.delete(7)
        self.assertTrue(deleted)
        self.assertIsNone(self.ht.search(7))
        self.assertEqual(self.ht.size(), 0)

    def test_delete_missing_key(self):
        deleted = self.ht.delete(999)
        self.assertFalse(deleted)

    # ------------------------------------------------------------------
    # Collision handling (chaining)
    # ------------------------------------------------------------------
    def test_collision_chaining(self):
        """
        With capacity=8, keys 0 and 8 both hash to bucket 0.
        Both should be stored and retrievable.
        """
        self.ht.insert(0, 'zero')
        self.ht.insert(8, 'eight')   # abs(hash('8')) % 8 != abs(hash('0')) % 8
        # Insert many keys to ensure some collide
        for i in range(20):
            self.ht.insert(i, f'val_{i}')
        # All must be retrievable
        for i in range(20):
            self.assertEqual(self.ht.search(i), f'val_{i}')

    # ------------------------------------------------------------------
    # Contains
    # ------------------------------------------------------------------
    def test_contains(self):
        self.ht.insert('alpha', 1)
        self.assertTrue(self.ht.contains('alpha'))
        self.assertFalse(self.ht.contains('beta'))

    # ------------------------------------------------------------------
    # Keys and values
    # ------------------------------------------------------------------
    def test_keys(self):
        self.ht.insert('a', 1)
        self.ht.insert('b', 2)
        keys = self.ht.keys()
        self.assertIn('a', keys)
        self.assertIn('b', keys)

    def test_values(self):
        self.ht.insert('x', 100)
        self.ht.insert('y', 200)
        values = self.ht.values()
        self.assertIn(100, values)
        self.assertIn(200, values)


class TestQueue(unittest.TestCase):
    """Tests for the FIFO queue."""

    def setUp(self):
        self.q = Queue()

    # ------------------------------------------------------------------
    # Empty state
    # ------------------------------------------------------------------
    def test_empty_on_creation(self):
        self.assertTrue(self.q.is_empty())
        self.assertEqual(self.q.size(), 0)
        self.assertIsNone(self.q.peek())
        self.assertIsNone(self.q.dequeue())

    # ------------------------------------------------------------------
    # Enqueue
    # ------------------------------------------------------------------
    def test_enqueue_single(self):
        self.q.enqueue({'id': 1})
        self.assertFalse(self.q.is_empty())
        self.assertEqual(self.q.size(), 1)

    def test_enqueue_multiple(self):
        self.q.enqueue({'id': 1})
        self.q.enqueue({'id': 2})
        self.q.enqueue({'id': 3})
        self.assertEqual(self.q.size(), 3)

    # ------------------------------------------------------------------
    # Dequeue — FIFO order
    # ------------------------------------------------------------------
    def test_dequeue_fifo_order(self):
        """First enqueued must be first dequeued."""
        self.q.enqueue({'id': 1, 'name': 'first'})
        self.q.enqueue({'id': 2, 'name': 'second'})
        self.q.enqueue({'id': 3, 'name': 'third'})

        first  = self.q.dequeue()
        second = self.q.dequeue()
        third  = self.q.dequeue()

        self.assertEqual(first['id'],  1)
        self.assertEqual(second['id'], 2)
        self.assertEqual(third['id'],  3)

    def test_dequeue_empty_returns_none(self):
        result = self.q.dequeue()
        self.assertIsNone(result)

    def test_dequeue_until_empty(self):
        self.q.enqueue('a')
        self.q.enqueue('b')
        self.q.dequeue()
        self.q.dequeue()
        self.assertTrue(self.q.is_empty())
        self.assertIsNone(self.q.dequeue())   # Already empty

    # ------------------------------------------------------------------
    # Peek
    # ------------------------------------------------------------------
    def test_peek_does_not_remove(self):
        self.q.enqueue({'id': 42})
        peeked = self.q.peek()
        self.assertEqual(peeked['id'], 42)
        self.assertEqual(self.q.size(), 1)   # Still in queue

    def test_peek_empty_queue(self):
        self.assertIsNone(self.q.peek())

    # ------------------------------------------------------------------
    # Size
    # ------------------------------------------------------------------
    def test_size_after_operations(self):
        self.q.enqueue('a')
        self.q.enqueue('b')
        self.q.dequeue()
        self.assertEqual(self.q.size(), 1)

    # ------------------------------------------------------------------
    # To List
    # ------------------------------------------------------------------
    def test_to_list_preserves_order(self):
        for i in range(5):
            self.q.enqueue(i)
        lst = self.q.to_list()
        self.assertEqual(lst, list(range(5)))

    def test_to_list_empty(self):
        self.assertEqual(self.q.to_list(), [])

    # ------------------------------------------------------------------
    # Enqueue after full dequeue
    # ------------------------------------------------------------------
    def test_reuse_after_empty(self):
        self.q.enqueue(1)
        self.q.dequeue()
        self.q.enqueue(2)
        self.assertEqual(self.q.size(), 1)
        self.assertEqual(self.q.dequeue(), 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
