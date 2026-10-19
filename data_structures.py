"""
data_structures.py
==================
Custom data structures for the College Lost-and-Found Management System.

This module implements three fundamental data structures from scratch:
  1. Singly Linked List  — stores recent activity records in memory
  2. Hash Table          — enables O(1) average-case item lookup by ID
  3. Queue               — manages collection/verification requests (FIFO)

These are genuine implementations, NOT wrappers around Python built-ins.
They are integrated with the Flask application and SQLite database.
"""


# ===========================================================================
# 1. SINGLY LINKED LIST
# ===========================================================================

class LLNode:
    """
    A single node in the singly linked list.

    Each node holds a piece of data (an item record dictionary) and a
    reference (pointer) to the next node in the chain.

    Visual representation:
        +----------+------+     +----------+------+     +----------+------+
        |  data    | next | --> |  data    | next | --> |  data    | None |
        +----------+------+     +----------+------+     +----------+------+
    """

    def __init__(self, data):
        self.data = data      # The payload — any Python object
        self.next = None      # Pointer to the next node (None = end of list)


class LinkedList:
    """
    Singly Linked List

    Used in this application to maintain an in-memory list of the most
    recent item-activity records (new reports, status changes).

    Why a linked list here?
      - New activity is always inserted at the head (O(1)).
      - We only need to traverse the first few records for the dashboard.
      - Dynamic size: no need to know the number of records in advance.

    Time Complexity:
      Operation         | Best Case | Worst Case | Assumption
      ------------------|-----------|------------|-------------------------------
      Insert at head    |   O(1)    |    O(1)    | Always at head
      Insert at tail    |   O(n)    |    O(n)    | Must traverse to find tail
      Search            |   O(1)    |    O(n)    | Best: first node; Worst: last
      Delete by key     |   O(1)    |    O(n)    | Best: head; Worst: last
      Traversal         |   O(n)    |    O(n)    | Must visit every node
      Get size          |   O(n)    |    O(n)    | No cached size counter
    """

    def __init__(self):
        self.head = None    # Points to the first node; None when empty

    # ------------------------------------------------------------------
    # INSERT at the head (most-recent-first ordering)
    # ------------------------------------------------------------------
    def insert_at_head(self, data):
        """
        Create a new node and make it the new head of the list.

        Steps:
          1. Create a new LLNode with the given data.
          2. Set new_node.next = current head.
          3. Update self.head = new_node.

        Time complexity: O(1)  — no traversal needed.
        """
        new_node = LLNode(data)
        new_node.next = self.head
        self.head = new_node

    # ------------------------------------------------------------------
    # INSERT at the tail
    # ------------------------------------------------------------------
    def insert_at_tail(self, data):
        """
        Append a new node at the end of the list.

        Steps:
          1. Create a new LLNode.
          2. If the list is empty, set head = new_node.
          3. Otherwise traverse to the last node and set last.next = new_node.

        Time complexity: O(n) — must reach the last node.
        """
        new_node = LLNode(data)
        if self.head is None:
            self.head = new_node
            return
        current = self.head
        while current.next is not None:
            current = current.next
        current.next = new_node

    # ------------------------------------------------------------------
    # SEARCH by a specific key-value pair in the stored dict
    # ------------------------------------------------------------------
    def search(self, key, value):
        """
        Traverse the list and return the first node whose data[key] == value.

        Example: search('id', 7) finds the item with id 7.

        Time complexity: O(n) — may need to visit every node.
        Returns: The node's data dict if found, else None.
        """
        current = self.head
        while current is not None:
            if isinstance(current.data, dict) and current.data.get(key) == value:
                return current.data
            current = current.next
        return None

    # ------------------------------------------------------------------
    # DELETE by a specific key-value pair
    # ------------------------------------------------------------------
    def delete(self, key, value):
        """
        Remove the first node whose data[key] == value.

        Steps:
          1. Check if the head matches — if so, move head forward.
          2. Otherwise traverse until we find the node before the target.
          3. Skip over the target node by updating the previous node's .next.

        Time complexity:
          - Best case  O(1): target is the head node.
          - Worst case O(n): target is the last node or not present.

        Returns: True if deleted, False if not found.
        """
        if self.head is None:
            return False

        # Case 1: head node is the target
        if isinstance(self.head.data, dict) and self.head.data.get(key) == value:
            self.head = self.head.next
            return True

        # Case 2: search for the node before the target
        current = self.head
        while current.next is not None:
            if isinstance(current.next.data, dict) and current.next.data.get(key) == value:
                current.next = current.next.next   # bypass the target node
                return True
            current = current.next

        return False  # not found

    # ------------------------------------------------------------------
    # TRAVERSAL — collect all data into a Python list
    # ------------------------------------------------------------------
    def to_list(self):
        """
        Walk through every node and collect their data values.

        Time complexity: O(n)
        Returns: A plain Python list of all data items.
        """
        result = []
        current = self.head
        while current is not None:
            result.append(current.data)
            current = current.next
        return result

    # ------------------------------------------------------------------
    # SIZE — count the nodes
    # ------------------------------------------------------------------
    def size(self):
        """Return the number of nodes in the list. Time complexity: O(n)."""
        count = 0
        current = self.head
        while current is not None:
            count += 1
            current = current.next
        return count

    # ------------------------------------------------------------------
    # IS EMPTY
    # ------------------------------------------------------------------
    def is_empty(self):
        """Return True if the list has no nodes. O(1)."""
        return self.head is None

    # ------------------------------------------------------------------
    # DISPLAY — print a textual representation
    # ------------------------------------------------------------------
    def display(self):
        """
        Print each node's data separated by ' -> ', ending with 'NULL'.
        Useful for debugging and demonstration.
        Time complexity: O(n)
        """
        parts = []
        current = self.head
        while current is not None:
            parts.append(str(current.data))
            current = current.next
        print(" -> ".join(parts) + " -> NULL")

    # ------------------------------------------------------------------
    # TRIM — keep only the first `n` nodes (for bounded activity feed)
    # ------------------------------------------------------------------
    def trim(self, n):
        """
        Remove all nodes after the nth node.
        Keeps the list bounded so memory does not grow indefinitely.
        Time complexity: O(n)
        """
        if n <= 0:
            self.head = None
            return
        current = self.head
        count = 1
        while current is not None and count < n:
            current = current.next
            count += 1
        if current is not None:
            current.next = None


# ===========================================================================
# 2. CUSTOM HASH TABLE
# ===========================================================================

class HashTable:
    """
    Custom Hash Table with Chaining for Collision Resolution

    Used in this application for fast O(1) average-case item lookup by item ID.

    How it works:
      - An array of `capacity` buckets is created.
      - Each bucket is a Python list acting as a chain (linked list of pairs).
      - To store (key, value): compute bucket_index = hash(key) % capacity,
        then append (key, value) to that bucket's chain.
      - If two keys hash to the same bucket, they coexist in the same chain
        (collision handling by chaining).

    Why not just use Python's dict?
      Python's dict is a hash table internally, but using it directly would
      not demonstrate the implementation. This class explicitly shows the
      hash function, bucket array, chaining, and each operation's logic.

    Time Complexity:
      Operation  | Average Case | Worst Case  | Note
      -----------|--------------|-------------|-----------------------------
      Insert     |    O(1)      |    O(n)     | Worst: all keys same bucket
      Search     |    O(1)      |    O(n)     | Worst: all keys same bucket
      Update     |    O(1)      |    O(n)     | Finds then replaces in chain
      Delete     |    O(1)      |    O(n)     | Worst: all keys same bucket

    Average case assumes a good hash function and load factor < 0.75.
    """

    def __init__(self, capacity=64):
        """
        Initialize the hash table.

        capacity: number of buckets. A prime-like power of 2 (64) works well
                  for small datasets and keeps the modulo operation fast.
        """
        self.capacity = capacity
        # Each element is a list of [key, value] pairs (the "chain")
        self.buckets = [[] for _ in range(self.capacity)]
        self._count = 0     # total number of stored key-value pairs

    # ------------------------------------------------------------------
    # HASH FUNCTION
    # ------------------------------------------------------------------
    def _hash(self, key):
        """
        Compute the bucket index for a given key.

        Strategy:
          - Convert key to a string.
          - Use Python's built-in hash() on the string.
          - Take the absolute value (hash() can be negative).
          - Apply modulo capacity to map it into [0, capacity).

        Time complexity: O(len(key)) for string hashing.
        """
        return abs(hash(str(key))) % self.capacity

    # ------------------------------------------------------------------
    # INSERT / PUT
    # ------------------------------------------------------------------
    def insert(self, key, value):
        """
        Store a key-value pair.

        If the key already exists in its bucket chain, update its value
        (upsert behaviour). Otherwise append a new pair to the chain.

        Time complexity: O(1) average, O(n) worst case.
        """
        index = self._hash(key)
        chain = self.buckets[index]

        # Check if key already exists in the chain
        for pair in chain:
            if pair[0] == key:
                pair[1] = value   # update existing entry
                return

        # Key not found — append new pair
        chain.append([key, value])
        self._count += 1

    # ------------------------------------------------------------------
    # SEARCH / GET
    # ------------------------------------------------------------------
    def search(self, key):
        """
        Retrieve the value associated with key.

        Steps:
          1. Compute the bucket index.
          2. Walk the chain at that index.
          3. Return value if key matches, else return None.

        Time complexity: O(1) average, O(n) worst case.
        """
        index = self._hash(key)
        chain = self.buckets[index]
        for pair in chain:
            if pair[0] == key:
                return pair[1]
        return None

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------
    def update(self, key, value):
        """
        Update an existing key's value.

        Returns True if the key was found and updated, False otherwise.
        Time complexity: O(1) average, O(n) worst case.
        """
        index = self._hash(key)
        chain = self.buckets[index]
        for pair in chain:
            if pair[0] == key:
                pair[1] = value
                return True
        return False

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------
    def delete(self, key):
        """
        Remove the key-value pair with the given key.

        Returns True if deleted, False if not found.
        Time complexity: O(1) average, O(n) worst case.
        """
        index = self._hash(key)
        chain = self.buckets[index]
        for i, pair in enumerate(chain):
            if pair[0] == key:
                chain.pop(i)
                self._count -= 1
                return True
        return False

    # ------------------------------------------------------------------
    # CONTAINS
    # ------------------------------------------------------------------
    def contains(self, key):
        """Return True if the key exists. O(1) average."""
        return self.search(key) is not None

    # ------------------------------------------------------------------
    # SIZE
    # ------------------------------------------------------------------
    def size(self):
        """Return the total number of stored key-value pairs. O(1)."""
        return self._count

    # ------------------------------------------------------------------
    # ALL KEYS
    # ------------------------------------------------------------------
    def keys(self):
        """Return a list of all keys stored. O(n)."""
        result = []
        for chain in self.buckets:
            for pair in chain:
                result.append(pair[0])
        return result

    # ------------------------------------------------------------------
    # ALL VALUES
    # ------------------------------------------------------------------
    def values(self):
        """Return a list of all values stored. O(n)."""
        result = []
        for chain in self.buckets:
            for pair in chain:
                result.append(pair[1])
        return result

    # ------------------------------------------------------------------
    # DISPLAY (for debugging/demonstration)
    # ------------------------------------------------------------------
    def display(self):
        """
        Print a visual representation of non-empty buckets and their chains.
        Time complexity: O(capacity + n) where n = total pairs.
        """
        for i, chain in enumerate(self.buckets):
            if chain:
                pairs = ", ".join(f"{p[0]}:{p[1]}" for p in chain)
                print(f"Bucket[{i}]: [{pairs}]")


# ===========================================================================
# 3. QUEUE (using linked list internally)
# ===========================================================================

class QNode:
    """A single node in the queue's internal linked list."""

    def __init__(self, data):
        self.data = data
        self.next = None


class Queue:
    """
    FIFO Queue implemented with a Singly Linked List

    Used in this application to manage collection requests in arrival order.

    Why a linked list for the queue?
      - Enqueue at the tail: O(1) because we maintain a tail pointer.
      - Dequeue from the head: O(1) because we only move head forward.
      - No wasted space from pre-allocated arrays.

    How it works:
      - `front` points to the node to be dequeued next (oldest request).
      - `rear` points to the node most recently enqueued (newest request).
      - Enqueueing appends to rear; dequeuing removes from front.

      Visual:
        front --> [req_1] --> [req_2] --> [req_3] --> None
                                                   ^
                                                  rear

    Time Complexity:
      Operation  | Time   | Note
      -----------|--------|--------------------------------------------
      Enqueue    |  O(1)  | Append to rear pointer directly
      Dequeue    |  O(1)  | Remove from front pointer directly
      Peek       |  O(1)  | Read front.data without removing
      Is Empty   |  O(1)  | Check front is None
      Size       |  O(n)  | Must traverse (no cached counter shown here)
      Display    |  O(n)  | Must traverse all nodes
    """

    def __init__(self):
        self.front = None   # Points to the oldest (first to be removed) node
        self.rear = None    # Points to the newest (last added) node
        self._size = 0      # Cached size for O(1) size queries

    # ------------------------------------------------------------------
    # ENQUEUE — add to rear
    # ------------------------------------------------------------------
    def enqueue(self, data):
        """
        Add a new request to the back of the queue.

        Steps:
          1. Create a new QNode with the given data.
          2. If queue is empty, both front and rear point to new node.
          3. Otherwise set current rear.next = new_node, then move rear forward.

        Time complexity: O(1)
        """
        new_node = QNode(data)
        if self.rear is None:           # Queue was empty
            self.front = new_node
            self.rear = new_node
        else:
            self.rear.next = new_node   # Link to end of chain
            self.rear = new_node        # Advance rear pointer
        self._size += 1

    # ------------------------------------------------------------------
    # DEQUEUE — remove from front
    # ------------------------------------------------------------------
    def dequeue(self):
        """
        Remove and return the front (oldest) request.

        Steps:
          1. If queue is empty, return None.
          2. Save front.data.
          3. Move front forward to front.next.
          4. If queue is now empty, reset rear to None.

        Time complexity: O(1)
        """
        if self.front is None:
            return None                 # Queue is empty

        data = self.front.data
        self.front = self.front.next    # Move front forward

        if self.front is None:          # Queue is now empty
            self.rear = None

        self._size -= 1
        return data

    # ------------------------------------------------------------------
    # PEEK — view the front without removing
    # ------------------------------------------------------------------
    def peek(self):
        """
        Return the front data without removing it.
        Time complexity: O(1)
        """
        if self.front is None:
            return None
        return self.front.data

    # ------------------------------------------------------------------
    # IS EMPTY
    # ------------------------------------------------------------------
    def is_empty(self):
        """Return True if the queue has no elements. O(1)."""
        return self.front is None

    # ------------------------------------------------------------------
    # SIZE
    # ------------------------------------------------------------------
    def size(self):
        """Return the number of elements in the queue. O(1) — uses cache."""
        return self._size

    # ------------------------------------------------------------------
    # DISPLAY
    # ------------------------------------------------------------------
    def display(self):
        """
        Print all queue elements from front to rear.
        Time complexity: O(n)
        """
        if self.is_empty():
            print("Queue is empty.")
            return
        parts = []
        current = self.front
        while current is not None:
            parts.append(str(current.data))
            current = current.next
        print("FRONT -> " + " -> ".join(parts) + " -> REAR")

    # ------------------------------------------------------------------
    # TO LIST — collect elements in order (for serialization)
    # ------------------------------------------------------------------
    def to_list(self):
        """Return all elements as a Python list (front to rear). O(n)."""
        result = []
        current = self.front
        while current is not None:
            result.append(current.data)
            current = current.next
        return result


# ===========================================================================
# APPLICATION-LEVEL DATA STRUCTURE INSTANCES
# ===========================================================================
# These module-level singletons are imported by app.py and used throughout
# the application lifecycle.

# Stores up to 20 most-recent item activity records (for the dashboard feed).
activity_feed: LinkedList = LinkedList()

# Maps item_id (int) -> item dict for O(1) average-case lookup.
item_cache: HashTable = HashTable(capacity=128)

# Holds pending collection requests in FIFO order.
request_queue: Queue = Queue()
