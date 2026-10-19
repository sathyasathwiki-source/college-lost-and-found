# ACADEMIC PROJECT REPORT
## On
# CAMPUS LOST & FOUND: COLLEGE LOST-AND-FOUND MANAGEMENT SYSTEM

**Course:** Fundamentals of Data Structures (FDS)  
**Degree:** Bachelor of Technology (B.Tech) in Computer Engineering  
**Academic Year:** 2026–2027  

---

## CANDIDATE DECLARATION

I hereby declare that this project report titled **"Campus Lost & Found: College Lost-and-Found Management System"** submitted in partial fulfillment of the requirements for the course **Fundamentals of Data Structures (FDS)** is an authentic record of our own work carried out under the guidance of the Department of Computer Engineering.

The matter embodied in this report has not been submitted for the award of any other degree or diploma. All algorithms, data structures, and application routines have been implemented and tested on local development environments.

---

## ACKNOWLEDGMENTS

We express our sincere gratitude to our faculty guide and the Department of Computer Engineering for providing the opportunity, resources, and technical guidance necessary to develop this project. The principles of data organization, algorithmic complexity analysis, and modular software engineering imparted during the Fundamentals of Data Structures course formed the foundational basis of this implementation.

We also thank the campus laboratory technical staff and our peer reviewers whose critical evaluations during testing helped refine the user interface and strengthen our test suites.

---

## ABSTRACT

In collegiate campus environments spanning multiple departments, academic blocks, lecture halls, and common facilities, the misplacement of essential items—such as student identity cards, scientific calculators, laboratory journals, keys, electronic storage drives, and personal accessories—is a recurring administrative challenge. Current recovery practices rely on fragmented social media broadcasts, physical noticeboards, or unorganized inquiries at security checkpoints. These conventional methods lack audit trails, exhibit severe communication delays, and fail to verify legitimate ownership before item handovers.

This project presents the design and realization of **Campus Lost & Found**, a centralized, data-structure-driven web application developed with Python, Flask, SQLite, and vanilla frontend technologies. Crucially, the system demonstrates the practical integration of core syllabus data structures:
1. A **Custom Singly Linked List** operating as an in-memory chronological activity buffer.
2. A **Custom Hash Table with Chaining** providing $O(1)$ average-case item retrieval by identifier.
3. A **FIFO Queue** implemented via dynamic linked nodes to manage student collection and ownership claims sequentially.

In addition, an explainable keyword-based text matching algorithm analyzes active lost and found records to suggest probable correlations to students without reliance on opaque artificial intelligence techniques. The interface adheres strictly to a human-designed, accessible university portal aesthetic using a restrained navy, white, and slate color palette. The entire system is validated through an automated test suite containing 94 unit and integration test cases.

---

## TABLE OF CONTENTS

- [Chapter 1: Introduction](#chapter-1-introduction)
  - 1.1 Motivation and Context
  - 1.2 Problem Statement
  - 1.3 Project Objectives
  - 1.4 Scope and Feasibility
- [Chapter 2: Literature Survey and Existing System Analysis](#chapter-2-literature-survey-and-existing-system-analysis)
  - 2.1 Analysis of Informal Channels
  - 2.2 Physical Logbook Registers
  - 2.3 Comparative Evaluation
- [Chapter 3: Software Requirements Specification (SRS)](#chapter-3-software-requirements-specification-srs)
  - 3.1 User Classes and Characteristics
  - 3.2 Hardware Environment
  - 3.3 Software Environment
  - 3.4 Functional Requirements
  - 3.5 Non-Functional Requirements
- [Chapter 4: System Architecture and Design](#chapter-4-system-architecture-and-design)
  - 4.1 High-Level Architectural Model
  - 4.2 Data Flow Diagrams (DFD Level 0 & Level 1)
  - 4.3 Database Schema and Relational Design
  - 4.4 Item Lifecycle State Machine
- [Chapter 5: Data Structures and Algorithms Implementation](#chapter-5-data-structures-and-algorithms-implementation)
  - 5.1 Custom Singly Linked List
  - 5.2 Custom Hash Table with Collision Chaining
  - 5.3 Custom Queue (FIFO Linked Implementation)
  - 5.4 Automatic Keyword Matching Engine
  - 5.5 Asymptotic Complexity Proofs & Summary
- [Chapter 6: Application Implementation and UI Design](#chapter-6-application-implementation-and-ui-design)
  - 6.1 Codebase Modular Organization
  - 6.2 Data Persistence and Memory Synchronization
  - 6.3 Security Controls and Input Sanitization
  - 6.4 University Design System Specification
- [Chapter 7: Testing, Verification, and Results](#chapter-7-testing-verification-and-results)
  - 7.1 Test Strategy
  - 7.2 Automated Test Suites Breakdown
  - 7.3 Representative Test Cases
  - 7.4 Verification of Execution
- [Chapter 8: Conclusion and Future Scope](#chapter-8-conclusion-and-future-scope)
  - 8.1 Summary of Work Done
  - 8.2 Academic Learning Outcomes
  - 8.3 Limitations and Proposed Enhancements
- [References](#references)

---

## CHAPTER 1: INTRODUCTION

### 1.1 Motivation and Context
On any bustling college campus, students carry portable valuables vital to their academic routine—laptops, scientific calculators, college identity badges, USB drives, laboratory records, and keys. When misplaced in high-traffic zones such as libraries, canteens, computer clusters, or seminar rooms, locating these belongings often proves frustrating. 

While computer engineering students frequently study abstract data structures in isolation, their direct application in resolving tangible, real-world campus logistics provides invaluable educational insight. This project connects theoretical computer science with practical software engineering.

### 1.2 Problem Statement
Existing campus lost-and-found practices are uncoordinated, fragmented, and inefficient:
- Disconnected Communication: Announcements are scattered across transient WhatsApp groups and unofficial Telegram channels.
- Lack of Ownership Verification: No structured mechanism exists to require claimants to describe unique, unpublicized identifiers of found items.
- Inefficient Manual Record-Keeping: Physical notebooks kept by security guards suffer from illegibility, lack search capabilities, and deteriorate over time.
- Privacy Exposures: Phone numbers and student details are often publicly broadcast in group chats.

### 1.3 Project Objectives
The engineering objectives of the **Campus Lost & Found** system include:
1. Provide a single, centralized digital registry for both lost and found articles.
2. Implement custom, genuine data structures in Python (Singly Linked List, Hash Table, Queue) without relying on high-level Python library wrappers.
3. Establish automated, two-way synchronization between persistent SQLite tables and in-memory data structures.
4. Devise an explainable, deterministic matching algorithm that suggests possible correlations between lost reports and found items.
5. Create an orderly, fair claim review system using a First-In, First-Out (FIFO) queue structure.
6. Deliver a professional, uncluttered user interface appropriate for university administrative deployment.

### 1.4 Scope and Feasibility
The software is engineered as a lightweight, server-rendered web application that runs seamlessly on local college hardware, requiring only a standard Python runtime. The scope encompasses item reporting, search and filtering, automated match detection, ownership claim queuing, administrator verification, and an interactive data structures visualization dashboard.

---

## CHAPTER 2: LITERATURE SURVEY AND EXISTING SYSTEM ANALYSIS

### 2.1 Analysis of Informal Channels
Currently, students heavily utilize peer-to-peer messaging networks (e.g., WhatsApp, Discord, Telegram) and social platforms (e.g., Instagram student confessions or batch pages). 

*Deficiencies Observed:*
- Information Volatility: Messages are rapidly buried under subsequent chatter within minutes.
- No Indexing: Users cannot filter messages by date, item classification, or campus quadrant.
- Security Risks: Posting pictures of keys or wallets allows dishonest actors to falsely claim belongings.

### 2.2 Physical Logbook Registers
Campus security stations and department offices maintain physical ledger books where security guards note deposited items.

*Deficiencies Observed:*
- Single Point of Access: A student who lost an item in the library must physically walk to individual department offices and main gates to check paper logs.
- Search Inefficiency: Linear manual scanning of paper entries scales at $O(n)$ human time per inquiry.
- Storage Degradation: Paper records are easily stained, torn, or misplaced at the conclusion of academic semesters.

### 2.3 Comparative Evaluation

| Evaluation Metric | Social Media / Group Chats | Physical Security Registers | Campus Lost & Found System |
| :--- | :--- | :--- | :--- |
| **Search Speed** | Poor (manual scrolling) | Poor (linear paper reading) | High ($O(1)$ cached lookup, indexed SQL) |
| **Centralization** | Fragmented across groups | Decentralized by office | Unified central web repository |
| **Verification Logic** | None | Ad-hoc questioning | Systematic claim queue with proof notes |
| **Audit Log** | Unreliable | Incomplete | Automated SQLite transaction log |
| **Pedagogical Value** | None | None | Explicit FDS implementation & demo |

---

## CHAPTER 3: SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

### 3.1 User Classes and Characteristics
1. **Student Reporter (Lost):** Students who have lost a personal article and wish to notify the campus community.
2. **Student Finder (Found):** Students or staff members who have discovered an unattended item and deposited it safely.
3. **Claimant:** A student who identifies their lost possession in the found catalog and submits an ownership collection claim.
4. **Campus Administrator / Security Staff:** Authorized personnel who review pending claims, verify proof of ownership, and update item lifecycle states.
5. **Academic Faculty / Evaluator:** Reviewers examining the internal data structures, algorithms, and complexity profiles.

### 3.2 Hardware Environment
- **Processor:** Intel Core i3 / AMD Ryzen 3 or higher
- **Memory (RAM):** 4 GB minimum (8 GB recommended)
- **Disk Storage:** 200 MB free hard drive space
- **Display Resolution:** Minimum $1024 \times 768$ (Fully responsive down to mobile viewports)

### 3.3 Software Environment
- **Operating System:** Microsoft Windows 10/11, Linux (Ubuntu/Debian), or macOS
- **Programming Language:** Python 3.10+ (Verified on Python 3.13)
- **Web Framework:** Flask 3.0+
- **Database Engine:** SQLite 3 (Standard Python `sqlite3` driver)
- **Web Browser:** Google Chrome, Mozilla Firefox, Microsoft Edge, or Safari

### 3.4 Functional Requirements
- **FR-1:** System shall permit users to report lost belongings with required fields (name, category, last-seen location, date, contact details).
- **FR-2:** System shall permit users to register found belongings without publicly exposing their contact credentials.
- **FR-3:** System shall validate that reported dates do not occur in the future.
- **FR-4:** System shall securely accept optional photograph uploads with strict filetype (PNG, JPG, JPEG, GIF, WEBP) and size limits ($\le 5\text{ MB}$).
- **FR-5:** System shall provide search and multifaceted filtering (by name keyword, category, location, and date range).
- **FR-6:** System shall execute an explainable keyword matching algorithm to calculate correlation scores between active lost and found items.
- **FR-7:** System shall enqueue collection requests into a FIFO queue and transition target items into `verification_pending`.
- **FR-8:** System shall provide role-protected administrative interfaces to approve or reject collection claims.
- **FR-9:** System shall provide a dedicated visual inspection route (`/ds-demo`) showcasing the real-time memory state of all custom data structures.

### 3.5 Non-Functional Requirements
- **NFR-1 (Usability & Design):** The UI must strictly utilize a restrained, accessible university color palette (`#263746` navy, `#F8F8F5` off-white, `#E1E5E8` border grey) without neon gradients, glassmorphism, or AI template characteristics.
- **NFR-2 (Security):** All database operations must execute via parameterized queries to eliminate SQL injection vulnerabilities. State transitions must be restricted via session-authenticated administrative guards.
- **NFR-3 (Performance):** In-memory lookups via custom hash table must execute within $O(1)$ average time.

---

## CHAPTER 4: SYSTEM ARCHITECTURE AND DESIGN

### 4.1 High-Level Architectural Model
The application adopts a clean, layered architectural pattern comprising:
1. **Presentation Layer (Jinja2 Templates & CSS/JS):** Renders clean semantic HTML, provides accessible form inputs, and performs client-side validation.
2. **Controller & Business Logic Layer (`app.py` & `matching.py`):** Handles HTTP request dispatching, input sanitization, matching algorithm execution, and session management.
3. **In-Memory Data Structures Layer (`data_structures.py`):** Houses the custom singly linked list, hash table with collision chaining, and FIFO queue.
4. **Data Persistence Layer (`database.py`):** Encapsulates SQLite schema creation, connection pooling, and parameterized CRUD operations.

```
+----------------------------------------------------------------------+
|                           CLIENT TIER                                |
|        Web Browser (HTML5 / CSS3 / Vanilla JavaScript ES6)           |
+-----------------------------------+----------------------------------+
                                    | HTTP Requests (GET / POST)
                                    v
+----------------------------------------------------------------------+
|                     APPLICATION CONTROLLER TIER                      |
|                            (Flask app.py)                            |
|                                                                      |
|  - Request Routing & Context Processing                              |
|  - Form Input Sanitization & File Upload Handling                    |
|  - Session-Based Admin Passcode Authorization                        |
+-------------------+------------------------------+-------------------+
                    |                              |
                    v                              v
+-----------------------------------+  +-------------------------------+
|     IN-MEMORY DATA STRUCTURES     |  |       MATCHING ENGINE         |
|        (data_structures.py)       |  |         (matching.py)         |
|                                   |  |                               |
|  1. SinglyLinkedList (Activity)   |  |  - Case-normalization         |
|  2. HashTable (Item Cache)        |  |  - Stop-word filtering        |
|  3. Queue (Collection Claims)     |  |  - Keyword intersection       |
+-------------------+---------------+  +---------------+---------------+
                    |                                  |
                    | Rebuilt on startup / synced      |
                    v                                  v
+----------------------------------------------------------------------+
|                         PERSISTENCE TIER                             |
|                    SQLite Database (database.py)                     |
|                                                                      |
|  Tables: items | collection_requests | activity_logs                 |
|  Storage: instance/app.db                                            |
+----------------------------------------------------------------------+
```

### 4.2 Data Flow Diagrams

#### Level 0 Context Diagram
```
                     +-----------------------+
                     |  Student Reporter /   |
                     |       Claimant        |
                     +-----------+-----------+
                                 | Lodges lost/found reports
                                 | Submits collection requests
                                 v
                     +-----------------------+
                     |  Campus Lost & Found  |<---+
                     |      Core System      |    | Reviews claims
                     +-----------+-----------+    | Updates statuses
                                 |                |
                                 v                |
                     +-----------+-----------+    |
                     |    Campus Security    +----+
                     |     Administrator     |
                     +-----------------------+
```

#### Level 1 DFD: Item Lifecycle and Verification
```
[User] ---> (1.0 Submit Report) ---> [Validate Input] ---> (Store in SQLite: items)
                                                                |
                                                                +---> (Insert in HashTable Cache)
                                                                |
                                                                +---> (Prepend to LinkedList Activity)
                                                                v
[Claimant] -> (2.0 Submit Claim) -> (Enqueue to FIFO Queue) -> (Update Status: verification_pending)
                                                                |
                                                                v
[Admin] ----> (3.0 Process Head) --> [Verify Ownership] ----> (Approve/Reject Claim)
                                                                |
                                        +-----------------------+-----------------------+
                                        |                                               |
                                  [If Approved]                                   [If Rejected]
                                        v                                               v
                          (Status -> 'returned')                           (Status -> 'active')
                          (Set returned_at timestamp)                      (Restore to matching)
```

### 4.3 Database Schema and Relational Design
The database contains three normalized tables:

```
  +----------------------------------+          +-----------------------------------+
  |              items               |          |        collection_requests        |
  +----------------------------------+          +-----------------------------------+
  | PK  id             INTEGER       |<----1--* | PK  id                INTEGER     |
  |     name           TEXT          |          | FK  item_id           INTEGER     |
  |     category       TEXT          |          |     requester_name    TEXT        |
  |     description    TEXT          |          |     requester_contact TEXT        |
  |     location       TEXT          |          |     description       TEXT        |
  |     event_date     TEXT          |          |     request_date      TEXT        |
  |     type           TEXT          |          |     status            TEXT        |
  |     status         TEXT          |          +-----------------------------------+
  |     image_filename TEXT          |
  |     contact_name   TEXT          |          +-----------------------------------+
  |     contact_info   TEXT          |          |           activity_logs           |
  |     created_at     TEXT          |          +-----------------------------------+
  |     returned_at    TEXT          |<----1--* | PK  id                INTEGER     |
  +----------------------------------+          | FK  item_id           INTEGER     |
                                                |     action            TEXT        |
                                                |     details           TEXT        |
                                                |     created_at        TEXT        |
                                                +-----------------------------------+
```

### 4.4 Item Lifecycle State Machine
```
            +----------------------------------------+
            |                                        |
            v                                        | (Rejected Claim)
     +------------+     Claim Submitted       +----------------------+
[*]--|   Active   |-------------------------->| Verification Pending |
     +-----+------+                           +----------+-----------+
           |                                             |
           | Administrative                              | Claim Approved
           | Direct Close                                v
           |                                      +--------------+
           +------------------------------------->|   Returned   |
           |                                      +-------+------+
           v                                              |
     +------------+                                       |
     |   Closed   |<--------------------------------------+
     +------------+
```

---

## CHAPTER 5: DATA STRUCTURES AND ALGORITHMS IMPLEMENTATION

### 5.1 Custom Singly Linked List
- **Source File:** `data_structures.py` (`LinkedList`, `LLNode`)
- **Application Role:** Maintains an in-memory chronological buffer of the latest system activities (new reports, claim submissions, returns) for display on the dashboard feed.
- **Node Structure:**
  ```python
  class LLNode:
      def __init__(self, data):
          self.data = data      # Item dictionary payload
          self.next = None      # Reference pointer to succeeding node
  ```
- **Key Operations:**
  - `insert_at_head(data)`: New activities are prepended to the head pointer in $O(1)$ time, ensuring most recent items are encountered first during traversal.
  - `trim(n)`: Limits list length to $n=20$ nodes by traversing to the $n$-th node and severing its `next` pointer, preventing unbounded memory growth.
  - `search(key, value)`: Scans nodes sequentially in $O(n)$ time.
  - `delete(key, value)`: Splices out matching nodes by updating the predecessor pointer.

### 5.2 Custom Hash Table with Collision Chaining
- **Source File:** `data_structures.py` (`HashTable`)
- **Application Role:** Serves as a high-speed item cache mapping primary keys (`item_id`) to item dictionaries, avoiding redundant disk I/O when viewing item details.
- **Architecture:** Initialized with $M = 128$ buckets. Each bucket contains a dynamic chain (list of `[key, value]` pairs).
- **Hash Function:**
  $$h(k) = |\text{hash}(\text{str}(k))| \pmod{128}$$
- **Key Operations:**
  - `insert(key, value)`: Computes bucket index; if key exists in bucket chain, updates value in-place; otherwise appends pair ($O(1)$ average).
  - `search(key)`: Computes index and searches the target bucket's chain ($O(1)$ average).
  - `delete(key)`: Computes index, locates key in chain, and removes it ($O(1)$ average).

### 5.3 Custom Queue (FIFO Linked Implementation)
- **Source File:** `data_structures.py` (`Queue`, `QNode`)
- **Application Role:** Manages item collection and verification claims. Claims must be reviewed strictly in the order they were lodged to ensure fairness.
- **Architecture:** Implemented using dynamic linked nodes with explicit `front` and `rear` pointers.
- **Key Operations:**
  - `enqueue(data)`: Links new node to `rear.next` and advances `rear` pointer ($O(1)$ time).
  - `dequeue()`: Reads `front.data`, advances `front = front.next`, and resets pointers if queue becomes empty ($O(1)$ time).
  - `peek()`: Reads `front.data` without pointer alteration ($O(1)$ time).

### 5.4 Automatic Keyword Matching Engine
- **Source File:** `matching.py` (`find_matches`, `find_all_matches`)
- **Application Role:** Suggests potential correlations between active lost items and active found items.
- **Methodology:**
  1. *Normalization:* Text is lowercased via `casefold()`, non-alphanumeric characters are stripped, and whitespace is collapsed.
  2. *Stop-Word Elimination:* High-frequency English words ('the', 'a', 'in', 'near', etc.) are filtered out.
  3. *Multi-Criteria Scoring:*
     - Exact Name + Category match: $+60$ points.
     - Title keyword overlap: $+30$ points per common word.
     - Shared category: $+20$ points.
     - Description keyword overlap: $+5$ points per shared word (capped at $+25$).
     - Location keyword overlap: $+8$ points per shared word (capped at $+16$).
  4. *Confidence Tiers:* Scores $\ge 80 \implies$ "Strong possible match"; $50\text{--}79 \implies$ "Moderate possible match"; $30\text{--}49 \implies$ "Weak possible match". Scores $< 30$ are suppressed.

### 5.5 Asymptotic Complexity Proofs & Summary

Let:
- $N$ = Number of items in linked list or hash table
- $M$ = Number of buckets in hash table ($M=128$)
- $\alpha = N/M$ = Load factor of hash table
- $L$ = Number of active lost items
- $F$ = Number of active found items
- $W$ = Average number of words per item record

| Data Structure / Algorithm | Operation | Best Case | Average Case | Worst Case | Governing Factors |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Singly Linked List** | `insert_at_head` | $O(1)$ | $O(1)$ | $O(1)$ | Modifies head pointer directly |
| | `search` | $O(1)$ | $O(N)$ | $O(N)$ | Best: target is head node |
| | `delete` | $O(1)$ | $O(N)$ | $O(N)$ | Requires predecessor traversal |
| **Hash Table (Chaining)**| `insert` | $O(1)$ | $O(1 + \alpha)$ | $O(N)$ | Worst case: all keys hash to 1 bucket |
| | `search` | $O(1)$ | $O(1 + \alpha)$ | $O(N)$ | Average case assumes uniform distribution |
| | `delete` | $O(1)$ | $O(1 + \alpha)$ | $O(N)$ | Chains traversed via linear probe |
| **FIFO Queue** | `enqueue` | $O(1)$ | $O(1)$ | $O(1)$ | Uses cached rear pointer |
| | `dequeue` | $O(1)$ | $O(1)$ | $O(1)$ | Uses cached front pointer |
| **Matching Algorithm** | `find_matches` | $O(F \cdot W)$ | $O(F \cdot W)$ | $O(F \cdot W)$ | Tokenizes lost item once, scans $F$ items |
| | `find_all_matches` | $O(L \cdot F \cdot W)$ | $O(L \cdot F \cdot W)$ | $O(L \cdot F \cdot W)$ | Pairwise comparison over word sets |

---

## CHAPTER 6: APPLICATION IMPLEMENTATION AND UI DESIGN

### 6.1 Codebase Modular Organization
```
College_Lost_And_Found/
├── app.py                     # Flask application factory, routes, and admin controllers
├── database.py                # SQLite table definitions, indexes, and parameterized CRUD
├── data_structures.py         # LinkedList, HashTable, and Queue classes from scratch
├── matching.py                # Normalized keyword similarity engine
├── seed_data.py               # Development utility for faculty demonstration data
├── requirements.txt           # Minimal dependencies (Flask, Werkzeug)
├── .env.example               # Template for secret keys and admin passcodes
├── .gitignore                 # Excludes database, uploads, bytecode, and virtual environments
├── templates/
│   ├── base.html              # University navigation, flash messages, and footer
│   ├── index.html             # Dashboard with real-time stats and recent activity
│   ├── lost_items.html        # Filterable catalog of lost items with pagination
│   ├── found_items.html       # Filterable catalog of found items with pagination
│   ├── report.html            # Selection landing page for reporting
│   ├── report_lost.html       # Form for reporting lost items with file upload
│   ├── report_found.html      # Form for registering found items
│   ├── item_details.html      # Comprehensive item profile, actions, and match cards
│   ├── submit_request.html    # Ownership verification claim submission form
│   ├── collection_requests.html # Public/admin listing of claims and queue count
│   ├── matches.html           # Campus-wide matching dashboard with score badges
│   ├── about.html             # Project details, technology stack, and complexity tables
│   ├── ds_demo.html           # Live memory visualization of nodes, buckets, and queue
│   ├── admin_login.html       # Passcode authentication form
│   ├── admin_dashboard.html   # Admin claims management and queue processor
│   └── errors/
│       ├── 404.html           # Resource not found error template
│       └── 500.html           # Internal server error template
├── static/
│   ├── css/style.css          # Restrained navy/grey design system
│   ├── js/main.js             # Vanilla JS: mobile navigation, previews, auto-dismiss
│   └── uploads/.gitkeep       # Directory for user-uploaded photographs
└── tests/
    ├── __init__.py            # Test package marker
    ├── test_data_structures.py# 39 unit tests for custom data structures
    ├── test_matching.py       # 16 unit tests for text matching algorithms
    └── test_app.py            # 39 integration tests for database and routes
```

### 6.2 Data Persistence and Memory Synchronization
When the application launches (`init_app()`), it:
1. Calls `db.init_db()` to ensure SQLite tables, constraints, and indexes exist.
2. Reconstructs in-memory data structures via `_rebuild_data_structures()`:
   - Reads existing items and populates `item_cache` (`HashTable`).
   - Reads historical logs and populates `activity_feed` (`LinkedList`).
   - Reads active `pending` claims and enqueues them into `request_queue` (`Queue`).

Whenever an item is reported, claimed, or returned through web endpoints, the operation writes to SQLite first within an ACID transaction. Upon database commit, the corresponding in-memory structures are immediately updated.

### 6.3 Security Controls and Input Sanitization
- **SQL Injection Prevention:** Every query executed in `database.py` utilizes parameterized `?` placeholders.
- **Upload Hardening:** Uploaded files are inspected for extension whitelisting (`png`, `jpg`, `jpeg`, `gif`, `webp`), capped at $5\text{ MB}$, and renamed using `werkzeug.utils.secure_filename` with timestamped hashes.
- **Date Sanitization:** Future dates are rejected to prevent erroneous reporting.
- **Role-Based Authorization:** State-modifying endpoints (`/admin/*`) require session authentication validated against an environment-supplied passcode (`ADMIN_PASSCODE`).
- **Contact Masking:** Finders' personal phone numbers and lost item claimants' proofs are hidden from general viewers and visible only to authenticated administrators.

### 6.4 University Design System Specification
The user interface was styled to emulate a distinguished university portal:
- **Main Canvas:** `#F8F8F5` (Warm natural light grey)
- **Primary Navy:** `#263746` (Used for headers, primary action buttons, brand identity)
- **Secondary Slate:** `#657786` (Used for subtle borders, secondary labels)
- **Card Background:** `#FFFFFF` (Pure white cards with subtle $1\text{px}$ `#E1E5E8` border)
- **Status Indicators:**
  - *Active:* Soft green (`#E6F2E8`, text `#2D6A35`)
  - *Verification Pending:* Soft amber (`#F5EBD7`, text `#7A5015`)
  - *Returned:* Neutral grey (`#E8EDF2`, text `#4A5568`)
  - *Rejected:* Soft rose (`#F7E5E5`, text `#8B2020`)
- **Typography:** Standardized on `Inter` with fallbacks to system sans-serif.

---

## CHAPTER 7: TESTING, VERIFICATION, AND RESULTS

### 7.1 Test Strategy
Testing was conducted using Python's native `unittest` framework across three test suites:
1. `tests/test_data_structures.py`: Isolated algorithmic testing of custom classes.
2. `tests/test_matching.py`: Semantic normalization, keyword extraction, and score boundary tests.
3. `tests/test_app.py`: Database operations, invalid input rejections, and Flask route integration tests using a isolated temporary SQLite database file.

### 7.2 Automated Test Suites Breakdown

```
======================================================================
TEST SUITE SUMMARY
======================================================================
1. tests/test_data_structures.py:
   - TestLinkedList: 15 tests (head/tail insert, search, delete, trim, empty)
   - TestHashTable:  13 tests (insert, search, upsert, chaining collisions, delete)
   - TestQueue:      11 tests (enqueue, dequeue FIFO order, peek, empty queue)
   Subtotal: 39 Tests

2. tests/test_matching.py:
   - TestNormalize:   5 tests (casefold, punctuation, space collapse)
   - TestKeywords:    3 tests (stop-words, single-char filtering)
   - TestFindMatches: 8 tests (exact match, category boost, sorting, reasons)
   Subtotal: 16 Tests

3. tests/test_app.py:
   - TestDatabaseOperations: 15 tests (CRUD, status transitions, duplicate claim guard)
   - TestFlaskRoutes:        18 tests (HTTP 200/404, forms, filters, auth gates)
   - TestInputValidation:     6 tests (date bounds, name limits, format checks)
   Subtotal: 39 Tests
----------------------------------------------------------------------
TOTAL AUTOMATED TESTS EXECUTED: 94
TOTAL TESTS PASSED:             94 (100% Pass Rate)
TOTAL TIME:                     0.955 seconds
======================================================================
```

### 7.3 Representative Test Cases

```python
# Verifying FIFO sequencing in custom Queue
def test_dequeue_fifo_order(self):
    self.q.enqueue({'id': 1, 'name': 'first'})
    self.q.enqueue({'id': 2, 'name': 'second'})
    self.q.enqueue({'id': 3, 'name': 'third'})

    self.assertEqual(self.q.dequeue()['id'], 1)
    self.assertEqual(self.q.dequeue()['id'], 2)
    self.assertEqual(self.q.dequeue()['id'], 3)

# Verifying collision handling in custom Hash Table
def test_collision_chaining(self):
    # With capacity=8, multiple keys are guaranteed to collide
    for i in range(20):
        self.ht.insert(i, f'val_{i}')
    for i in range(20):
        self.assertEqual(self.ht.search(i), f'val_{i}')

# Verifying duplicate claim prevention in database
def test_duplicate_collection_request_rejected(self):
    item_id = self.db.insert_item(...)
    self.db.insert_collection_request(item_id, 'Claimant 1', ...)
    with self.assertRaises(ValueError):
        self.db.insert_collection_request(item_id, 'Claimant 2', ...)
```

### 7.4 Verification of Execution
The application was launched and verified on Windows PowerShell. HTTP endpoints were tested via automated test clients and web browsers. Real-time feedback, flash alerts, and live memory state on the `/ds-demo` route responded consistently with zero console warnings or database locks.

---

## CHAPTER 8: CONCLUSION AND FUTURE SCOPE

### 8.1 Summary of Work Done
The **College Lost-and-Found Management System** successfully addresses campus lost property retrieval through a structured, transparent software solution. By explicitly implementing a Singly Linked List for chronological logs, a Hash Table with Chaining for high-speed item caching, and a FIFO Queue for fair claim review, the project achieves all functional, aesthetic, and academic objectives set forth in the curriculum.

### 8.2 Academic Learning Outcomes
Through the conceptualization and development of this project, we acquired practical mastery over:
1. Implementing pointer-based linear and hash-based non-linear data structures in Python.
2. Quantifying real-world asymptotic time and space complexities ($O(1)$ vs $O(n)$ vs $O(L \cdot F \cdot W)$).
3. Synchronizing transient in-memory memory structures with persistent ACID relational databases.
4. Designing human-centric, professional university interfaces free of distracting generative aesthetic clichés.
5. Authoring rigorous automated unit test suites achieving 100% pass rates.

### 8.3 Limitations and Proposed Enhancements
- **Multi-Process Concurrency:** While SQLite and Python handle development workloads efficiently, scaling to a distributed multi-server deployment would necessitate an external distributed cache (e.g., Redis) to synchronize data structures across disparate worker processes.
- **Image Recognition:** Future iterations may incorporate Optical Character Recognition (OCR) to automatically extract roll numbers and student names from photographed ID cards.
- **Automated Notifications:** Integrating campus SMTP or SMS gateways would allow automated status notifications to be dispatched to claimants upon claim approvals.

---

## REFERENCES

1. Horowitz, E., Sahni, S., & Anderson-Freed, S. *Fundamentals of Data Structures in C*, 2nd Edition, Silicon Press.
2. Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. *Introduction to Algorithms*, 4th Edition, MIT Press.
3. Grinberg, M. *Flask Web Development: Developing Web Applications with Python*, 2nd Edition, O'Reilly Media.
4. Python Software Foundation. *Python 3 Standard Library Documentation: `sqlite3`, `unittest`, `hashlib`*, Available at: https://docs.python.org/3/
5. SQLite Consortium. *SQLite Documentation and Query Language Specifications*, Available at: https://www.sqlite.org/docs.html
