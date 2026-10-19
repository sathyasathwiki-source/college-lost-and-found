# College Lost-and-Found Management System
*(Campus Lost & Found)*

An academic mini-project developed for the **Fundamentals of Data Structures (FDS)** subject (BTech First Year).

---

## Table of Contents
1. [Project Title](#1-project-title)
2. [Abstract](#2-abstract)
3. [Problem Statement](#3-problem-statement)
4. [Objectives](#4-objectives)
5. [Existing-System Limitations](#5-existing-system-limitations)
6. [Proposed Solution](#6-proposed-solution)
7. [Technology Stack](#7-technology-stack)
8. [Functional Requirements](#8-functional-requirements)
9. [Non-Functional Requirements](#9-non-functional-requirements)
10. [System Architecture](#10-system-architecture)
11. [Database Design](#11-database-design)
12. [Data Structures Used](#12-data-structures-used)
13. [Algorithms and Pseudocode](#13-algorithms-and-pseudocode)
14. [Flowchart Description](#14-flowchart-description)
15. [Time Complexity Analysis](#15-time-complexity-analysis)
16. [Installation Instructions](#16-installation-instructions)
17. [Commands to Run on Windows (VS Code)](#17-commands-to-run-on-windows-vs-code)
18. [How to Run Automated Tests](#18-how-to-run-automated-tests)
19. [Sample Test Cases](#19-sample-test-cases)
20. [Limitations](#20-limitations)
21. [Future Enhancements](#21-future-enhancements)
22. [Conclusion](#22-conclusion)

---

## 1. Project Title
**College Lost-and-Found Management System**  
*Short Title:* **Campus Lost & Found**

---

## 2. Abstract
Colleges and universities host thousands of students daily across lecture halls, laboratory complexes, sports amenities, libraries, and canteens. Incidents of misplaced belongings—such as student ID cards, calculators, laboratory record books, keys, flash drives, and personal accessories—occur frequently. Currently, recovery relies on scattered social media groups, physical pin-boards, or uncoordinated inquiries with campus security. 

The **Campus Lost & Found** system provides a centralized, authenticated web portal engineered with a Python Flask backend, SQLite persistence, and custom in-memory data structures. The system explicitly incorporates three core Fundamentals of Data Structures (FDS) topics: a **Custom Singly Linked List** for chronological activity tracking, a **Custom Hash Table with Chaining** for $O(1)$ item caching and retrieval, and a **Queue Data Structure** for FIFO processing of item collection claims. Furthermore, an explainable keyword-based matching algorithm connects active lost and found reports without opaque artificial intelligence claims. The interface follows a restrained, human-crafted university design system with zero visual clutter.

---

## 3. Problem Statement
College students frequently lose personal items on campus. Finding these items is difficult because:
- Information is fragmented across informal WhatsApp and Telegram groups, campus security booths, department offices, and departmental bulletin boards.
- Communication latency often leads to unclaimed items accumulating in security offices or getting permanently discarded.
- There is no structured, auditable mechanism to verify authentic ownership before handing over an item to a claimant.
- Students lack visibility into whether a lost article has already been deposited at a campus facility.

---

## 4. Objectives
1. **Centralized Platform:** Establish a unified, accessible digital repository for all campus lost and found occurrences.
2. **Student Self-Service Reporting:** Enable students to quickly lodge lost item notices and register found belongings with timestamps, descriptions, and category tags.
3. **Keyword-Based Match Detection:** Correlate lost and found item records based on category, item naming, and description keywords to suggest potential matches to students.
4. **Claim and Verification Management:** Enforce a systematic collection-request workflow preventing unauthorized retrieval of belongings.
5. **Academic FDS Demonstration:** Implement genuine custom data structures (Singly Linked List, Hash Table with Chaining, Queue) directly in Python, maintaining two-way synchronization with persistent database storage.
6. **Data Integrity & Security:** Protect sensitive student contact details from unauthenticated harvesting, sanitize file uploads, and validate state transitions.

---

## 5. Existing-System Limitations
| Feature | Informal Channels (WhatsApp/Notices) | Physical Security Register | Campus Lost & Found System |
| :--- | :--- | :--- | :--- |
| **Searchability** | Poor; buried in chat feeds | Manual page-by-page inspection | Indexed SQL & in-memory hash lookup |
| **Ownership Proof** | None; first to ask often claims | Subjective verbal questioning | Audited collection request queue with proof field |
| **Automated Matching**| Non-existent | Non-existent | Explainable keyword scoring engine |
| **Contact Privacy** | Contact details publicly broadcasted | Open register accessible to visitors | Hidden behind role-based admin authorization |
| **Historical Records** | Disappears when chats are cleared | Paper wear-and-tear, loss of logs | Persistent SQLite database audit log |

---

## 6. Proposed Solution
The proposed web portal bridges the communication gap through:
- A standardized reporting format with category classification and optional image upload verification.
- A deterministic match suggestion engine evaluating semantic similarity between lost and found entries.
- A FIFO-ordered claim review queue allowing security administrators to evaluate ownership claims sequentially.
- A live **Data Structures Demonstration** page (`/ds-demo`) showcasing the real-time node connections, hash bucket distributions, and queue pointers in memory for academic review.

---

## 7. Technology Stack
- **Backend:** Python 3.10+ (tested on Python 3.13), Flask 3.0+
- **Frontend:** Semantic HTML5, CSS3 (Custom design system), Vanilla JavaScript (ES6)
- **Database:** SQLite 3 (using standard library `sqlite3` module with foreign key enforcement)
- **Data Structures:** Custom Python classes for Singly Linked List, Hash Table (Chaining), and Queue (Linked-node based)
- **Testing:** Python `unittest` framework (94 automated test cases covering data structures, matching, database transactions, and route endpoints)

---

## 8. Functional Requirements
1. **User Module:**
   - Report a lost item with name, category, location, event date, and personal contact info.
   - Report a found item with location, date, and finder contact info.
   - Browse lost and found item catalogs with pagination.
   - Search records by keyword, category, location, and date range.
   - View detailed item profiles with status indicators (`Active`, `Verification Pending`, `Returned`, `Closed`).
   - Submit a collection request with descriptive proof of ownership.
2. **Matching Engine:**
   - Scan active lost items against active found items.
   - Calculate match scores based on exact names, categories, and keyword intersections.
   - Categorize matches into confidence tiers (`Strong`, `Moderate`, `Weak`) with clear explanations.
3. **Administration Module:**
   - Secure login using environment-configured administrator passcode.
   - Access the collection request queue in strict FIFO order.
   - Approve or reject claims, automatically updating item statuses and setting return timestamps.
   - Manually override item lifecycle statuses.
4. **Academic Demonstration Module:**
   - Visual display of active Singly Linked List nodes representing recent activity.
   - Visual display of Hash Table bucket distribution and load factor.
   - Visual display of Queue front and rear pointers.

---

## 9. Non-Functional Requirements
- **Usability:** Strictly adheres to university design standards using a muted navy/grey/white color palette (`#263746`, `#F8F8F5`, `#E1E5E8`). Free of neon gradients, glassmorphism, or AI aesthetics.
- **Performance:** In-memory hash table lookups execute in $O(1)$ average time.
- **Portability:** Operates cross-platform on Windows, macOS, and Linux without external database server installation.
- **Maintainability:** Modular separation between database access (`database.py`), data structures (`data_structures.py`), matching algorithms (`matching.py`), and HTTP routing (`app.py`).

---

## 10. System Architecture

```
                       +-----------------------------------+
                       |        Client Web Browser         |
                       |  (Desktop / Tablet / Mobile View) |
                       +-----------------+-----------------+
                                         | HTTP / HTTPS
                                         v
+--------------------------------------------------------------------------+
|                       Flask Application (app.py)                         |
|                                                                          |
|  +--------------------+  +----------------------+  +------------------+  |
|  | Route Handlers     |  | Session & Admin Auth |  | Input Validation |  |
|  +--------------------+  +----------------------+  +------------------+  |
+---------------------+-------------------+-------------------+------------+
                      |                   |                   |
                      v                   v                   v
      +---------------------+    +-----------------+   +-------------------+
      | In-Memory Cache &   |    | Matching Engine |   | SQLite Database   |
      | Data Structures     |    | (matching.py)   |   | (database.py)     |
      | (data_structures.py)|    +-----------------+   +-------------------+
      |                     |            |                       |
      | - SinglyLinkedList  |<-----------+                       |
      | - HashTable         |                                    |
      | - Queue             |<===================================+
      +---------------------+      (Loaded on startup / synchronized)
```

---

## 11. Database Design

### Schema Overview (SQLite)

#### Table: `items`
| Column Name | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique item identifier |
| `name` | `TEXT` | `NOT NULL` | Name of the article |
| `category` | `TEXT` | `NOT NULL` | One of 8 standard categories |
| `description`| `TEXT` | | Detailed description & identifying marks |
| `location` | `TEXT` | `NOT NULL` | Place where lost or found |
| `event_date` | `TEXT` | `NOT NULL` | Date of occurrence (`YYYY-MM-DD`) |
| `type` | `TEXT` | `NOT NULL CHECK(type IN ('lost','found'))` | Report classification |
| `status` | `TEXT` | `NOT NULL DEFAULT 'active'` | Current lifecycle status |
| `image_filename` | `TEXT` | | Safe filename of uploaded photograph |
| `contact_name` | `TEXT` | | Reporter's name (Lost reports) |
| `contact_info` | `TEXT` | | Contact email or phone number |
| `created_at` | `TEXT` | `DEFAULT (datetime('now'))` | Timestamp of lodging |
| `returned_at`| `TEXT` | | Timestamp when handed over |

#### Table: `collection_requests`
| Column Name | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique request identifier |
| `item_id` | `INTEGER` | `FOREIGN KEY REFERENCES items(id)` | Target found item |
| `requester_name` | `TEXT` | `NOT NULL` | Full name of claimant |
| `requester_contact`| `TEXT` | `NOT NULL` | Phone or email of claimant |
| `description` | `TEXT` | `NOT NULL` | Confidential ownership proof |
| `request_date` | `TEXT` | `DEFAULT (datetime('now'))` | Date of submission |
| `status` | `TEXT` | `CHECK(status IN ('pending','approved','rejected'))` | Claim status |

#### Table: `activity_logs`
| Column Name | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Audit log record ID |
| `item_id` | `INTEGER` | `REFERENCES items(id)` | Associated item |
| `action` | `TEXT` | `NOT NULL` | Action code (`reported`, `returned`, etc.) |
| `details` | `TEXT` | | Plain English summary |
| `created_at` | `TEXT` | `DEFAULT (datetime('now'))` | Event timestamp |

---

## 12. Data Structures Used

### A. Custom Singly Linked List
- **Purpose:** Manages the in-memory **Recent Activity Feed** presented on the dashboard.
- **Node Structure:** Each node (`LLNode`) holds a dictionary payload (`item_id`, `name`, `action`, `timestamp`) and a pointer (`next`) to the successive node.
- **Head Pointer:** Maintained at `self.head`. New reports are inserted directly at the head, ensuring the most recent activities are encountered first in $O(1)$ time.
- **Bounded Capacity:** Implements a `trim(n)` method to keep memory footprint bounded to the latest 20 actions.

### B. Custom Hash Table (with Chaining)
- **Purpose:** Acts as a high-speed in-memory **Item Cache** mapping `item_id -> item_dictionary`.
- **Bucket Array:** Initialized with 128 buckets.
- **Hash Function:**
  $$\text{Index} = |\text{hash}(\text{str}(\text{key}))| \pmod{\text{capacity}}$$
- **Collision Resolution:** Implements separate chaining. Each bucket contains a linked list of key-value pairs (`[key, value]`).
- **Operations:** Explicit implementations of `insert(key, value)`, `search(key)`, `update(key, value)`, and `delete(key)`.

### C. Queue (Linked-Node FIFO Structure)
- **Purpose:** Manages pending **Collection & Ownership Claims** in strict First-In, First-Out (FIFO) sequence.
- **Pointers:** Maintains explicit `front` and `rear` node references alongside a cached `_size` counter.
- **Operations:**
  - `enqueue(data)`: Appends to the `rear` in $O(1)$ time.
  - `dequeue()`: Extracts from the `front` in $O(1)$ time.
  - `peek()`: Reads front data without extraction in $O(1)$ time.
  - `is_empty()`: Checks if queue contains elements in $O(1)$ time.

---

## 13. Algorithms and Pseudocode

### 1. Hash Table Search Algorithm
```text
Algorithm HashTableSearch(key):
    Input: key (Integer item ID)
    Output: Stored item record or None

    1. index <- abs(hash(str(key))) % capacity
    2. chain <- buckets[index]
    3. for each pair in chain:
    4.     if pair[0] == key then:
    5.         return pair[1]
    6. return None
```

### 2. Queue Dequeue Algorithm
```text
Algorithm QueueDequeue():
    Input: None
    Output: Dequeued request record or None

    1. if front is None then:
    2.     return None
    3. data <- front.data
    4. front <- front.next
    5. if front is None then:
    6.     rear <- None
    7. size <- size - 1
    8. return data
```

### 3. Match Scoring Algorithm
```text
Algorithm ComputeItemMatch(lost_item, found_item):
    Input: lost_item dict, found_item dict
    Output: match_score (Integer), reasons (List of strings)

    1. score <- 0
    2. reasons <- Empty List
    3. Normalize strings (lowercase, strip punctuation)
    4. Extract non-stopwords into sets: L_words, F_words
    
    5. if lost_item.name == found_item.name and lost_item.category == found_item.category then:
    6.     score <- score + 60
    7.     reasons.append("Exact name and category match")
    8. else if (L_name_words INTERSECT F_name_words) is not empty then:
    9.     score <- score + (count * 30)
    10.    reasons.append("Shared keywords in title")
    
    11. if lost_item.category == found_item.category (not already scored) then:
    12.    score <- score + 20
    13.    reasons.append("Category match")
    
    14. score <- score + min(|L_desc INTERSECT F_desc| * 5, 25)
    15. score <- score + min(|L_loc INTERSECT F_loc| * 8, 16)
    
    16. return score, reasons
```

---

## 14. Flowchart Description

### Lost Item Reporting Flow
1. **Start:** User clicks "Report a Lost Item" from navigation.
2. **Form Input:** Student supplies title, category, description, location, date, contact details, and optional photo.
3. **Validation:** System checks mandatory fields, ensures date $\le$ today, and validates file extension and size ($\le 5\text{ MB}$).
   - *If invalid:* Form re-renders with specific error banners.
4. **Database Insertion:** SQL statement writes new record to `items` table; auto-generates unique `item_id`.
5. **In-Memory Updates:**
   - New item inserted into Hash Table cache.
   - Activity logged and pushed to Singly Linked List head.
6. **End:** User redirected to detailed Item View with active match suggestions.

### Collection Request Verification Flow
1. **Start:** Claimant visits found item details and clicks "Submit Collection Request".
2. **Input Proof:** User provides contact details and unique proof-of-ownership details.
3. **Queue Enqueue:** Request inserted into `collection_requests` database table and enqueued into in-memory FIFO `request_queue`.
4. **Status Update:** Target item status transitions from `Active` to `Verification Pending`.
5. **Admin Review:** Administrator views request at the head of the FIFO queue.
   - *If Approved:* Item status transitions to `Returned` with timestamp; claim marked `approved`.
   - *If Rejected:* Item status restored to `Active`; claim marked `rejected`.
6. **End:** Item cache refreshed; transaction logged in audit trail.

---

## 15. Time Complexity Analysis

| Data Structure / Operation | Best Case | Average Case | Worst Case | Governing Factors & Assumptions |
| :--- | :---: | :---: | :---: | :--- |
| **Linked List: Insert (Head)** | $O(1)$ | $O(1)$ | $O(1)$ | Pointer reassignment only |
| **Linked List: Search** | $O(1)$ | $O(n)$ | $O(n)$ | Best case: target at head; Worst: target at tail |
| **Linked List: Delete** | $O(1)$ | $O(n)$ | $O(n)$ | Traversing to predecessor node |
| **Hash Table: Insert** | $O(1)$ | $O(1)$ | $O(n)$ | Worst case: all keys hash to the same bucket |
| **Hash Table: Search / Lookup** | $O(1)$ | $O(1)$ | $O(n)$ | Average case assumes uniform hashing & load factor $< 0.75$ |
| **Hash Table: Delete** | $O(1)$ | $O(1)$ | $O(n)$ | Node removal within collision bucket chain |
| **Queue: Enqueue** | $O(1)$ | $O(1)$ | $O(1)$ | Direct insertion via rear pointer |
| **Queue: Dequeue** | $O(1)$ | $O(1)$ | $O(1)$ | Direct removal via front pointer |
| **Matching Algorithm** | $O(L \cdot F \cdot W)$ | $O(L \cdot F \cdot W)$ | $O(L \cdot F \cdot W)$ | $L = \text{Lost Items}, F = \text{Found Items}, W = \text{Avg Words}$ |

---

## 16. Installation Instructions

### Prerequisites
- Windows 10/11 operating system
- Python 3.10 or higher (Python 3.13 tested and verified)
- VS Code (Visual Studio Code)

### Step 1: Clone or Navigate to the Project
Open PowerShell or Command Prompt:
```powershell
cd c:\coding\college_lost_and_found
```

### Step 2: Create and Activate Virtual Environment (Recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If execution of scripts is disabled on Windows, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

---

## 17. Commands to Run on Windows (VS Code)

### Option A: Running from VS Code Terminal
1. Open the project folder in VS Code:
   ```powershell
   code c:\coding\college_lost_and_found
   ```
2. Open the integrated terminal (`Ctrl + \``).
3. Set your secret key and start the server:
   ```powershell
   $env:FLASK_SECRET_KEY="campus-secret-key"
   python app.py
   ```
4. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

### Option B: Seeding Sample Data for Faculty Demonstration
To populate the database with realistic sample lost/found pairs and test requests:
```powershell
python seed_data.py
```
Then restart or run `python app.py`.

### Default Credentials
- **Admin Login Route:** `/admin/login`
- **Default Admin Passcode:** `admin123` *(Configurable via `ADMIN_PASSCODE` in `.env`)*

---

## 18. How to Run Automated Tests
The project contains 94 unit and integration tests executing across three test suites:
- `tests/test_data_structures.py`: 39 tests verifying linked list, hash table chaining, and FIFO queue.
- `tests/test_matching.py`: 16 tests verifying tokenization, stop-word removal, and keyword scoring.
- `tests/test_app.py`: 39 tests verifying database operations, validation rules, transitions, and HTTP endpoints.

### Run All 94 Tests with Verbose Output:
```powershell
python -m unittest discover tests -v
```
*(Expected Result: `Ran 94 tests ... OK`)*

---

## 19. Sample Test Cases

| Test Case ID | Unit Tested | Input Condition | Expected Result | Pass/Fail |
| :--- | :--- | :--- | :--- | :---: |
| **TC-DS-01** | Singly Linked List | Insert 3 items at head | Order inverted: third item at head ($O(1)$) | **PASS** |
| **TC-DS-02** | Singly Linked List | Delete head item | Head shifts to node 2, size decreases by 1 | **PASS** |
| **TC-DS-03** | Hash Table | 20 keys with modulo 8 | Collision chains handle all keys without loss | **PASS** |
| **TC-DS-04** | Hash Table | Lookup non-existent ID | Returns `None` without exception | **PASS** |
| **TC-DS-05** | FIFO Queue | Enqueue 1, 2, 3; Dequeue | Items retrieved in exact order: 1, then 2, then 3 | **PASS** |
| **TC-MATCH-01** | Matching Engine | Exact title & category match | Score $\ge 60$, labeled "Strong possible match" | **PASS** |
| **TC-MATCH-02** | Matching Engine | Completely distinct items | Score $= 0$, omitted from suggestions | **PASS** |
| **TC-DB-01** | Database Item CRUD | Insert lost item | ID auto-incremented, status initialized to `active` | **PASS** |
| **TC-SEC-01** | Input Validation | Date set to future year | Rejected with validation message | **PASS** |
| **TC-SEC-02** | Authorization | Access `/admin` without auth | Redirected to `/admin/login` with flash error | **PASS** |

---

## 20. Limitations
1. **Single-Node In-Memory Synchronization:** In-memory data structures are hosted within the single Flask server process. In a multi-worker production deployment (e.g. Gunicorn with multiple worker processes), a distributed cache like Redis would be required to synchronize memory across processes.
2. **Text-Based Matching Scope:** The keyword algorithm relies on textual descriptions; it does not parse non-standard abbreviations or OCR text from uploaded ID card photographs.
3. **Local File Storage:** Image uploads are saved to the local filesystem (`static/uploads/`) rather than cloud object storage (e.g. AWS S3).

---

## 21. Future Enhancements
1. **Email / SMS Notification Dispatch:** Integrate automated alerts via SMTP when an item matching a student's lost report is lodged.
2. **Optical Character Recognition (OCR):** Automatically parse student names and PRN numbers from uploaded images of college ID cards.
3. **Multi-Factor Administrative Authentication:** Integrate college LDAP / Google Workspace Single Sign-On (SSO) for security staff.
4. **Enhanced Scalability:** Implement database read replicas and persistent caching layers for university systems with 20,000+ students.

---

## 22. Conclusion
The **College Lost-and-Found Management System** demonstrates how theoretical Fundamentals of Data Structures (FDS) principles directly solve daily campus logistical challenges. By combining custom Singly Linked Lists, Hash Tables with Chaining, and FIFO Queues with a responsive Python Flask web architecture, the project provides a clean, secure, and user-friendly university application. The codebase is fully verified with 94 automated tests, free of unnecessary dependencies, and structured for first-year engineering students to explain and defend in academic viva examinations.
