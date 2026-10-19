"""
seed_data.py
============
Utility script for development and demonstration purposes only.
Populates the database with realistic sample items, matched pairs,
and sample collection requests.

Note:
  Do NOT run this in production. These records are explicitly tagged
  for academic demonstration purposes.

Usage:
  python seed_data.py
"""

import os
import sys
from datetime import datetime, timedelta

# Ensure root directory is on the import path
sys.path.insert(0, os.path.dirname(__file__))

import database as db
from data_structures import activity_feed, item_cache, request_queue

def run_seed():
    print("Initializing database...")
    db.init_db()

    today = datetime.now()
    d1 = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    d2 = (today - timedelta(days=2)).strftime("%Y-%m-%d")
    d3 = (today - timedelta(days=4)).strftime("%Y-%m-%d")
    d5 = (today - timedelta(days=7)).strftime("%Y-%m-%d")

    sample_items = [
        # Pair 1: Blue Casio Scientific Calculator (Matching pair)
        {
            "name": "Casio fx-991EX Scientific Calculator",
            "category": "Electronics",
            "description": "Black and silver Casio scientific calculator with student sticker 'FE-IT-24' on the rear cover.",
            "location": "Room 204, Academic Block A",
            "event_date": d2,
            "type": "lost",
            "contact_name": "Rohan Deshmukh",
            "contact_info": "rohan.deshmukh@college.edu",
        },
        {
            "name": "Casio Scientific Calculator",
            "category": "Electronics",
            "description": "Casio fx-991EX calculator found on bench in Room 204 after FDS lecture.",
            "location": "Room 204, Academic Block A",
            "event_date": d2,
            "type": "found",
            "contact_name": None,
            "contact_info": "Prof. Kulkarni (Cabin 12) or Security Desk",
        },

        # Pair 2: Student College ID Card
        {
            "name": "College ID Card - Aarav Sharma",
            "category": "ID Card",
            "description": "First-year Computer Engineering ID card with blue lanyard and library barcode.",
            "location": "Central Library Reading Hall",
            "event_date": d1,
            "type": "lost",
            "contact_name": "Aarav Sharma",
            "contact_info": "aarav.sharma@college.edu",
        },
        {
            "name": "Student ID Card (Computer Engg)",
            "category": "ID Card",
            "description": "Found on 2nd-floor reading table near reference book rack. Name on card is Aarav S.",
            "location": "Central Library",
            "event_date": d1,
            "type": "found",
            "contact_name": None,
            "contact_info": "Central Library Circulation Counter",
        },

        # Pair 3: Water Bottle
        {
            "name": "Milton Insulated Steel Bottle (Black, 750ml)",
            "category": "Water Bottle",
            "description": "Black stainless steel water bottle with slight scratch near the cap.",
            "location": "College Canteen Main Hall",
            "event_date": d3,
            "type": "lost",
            "contact_name": "Sneha Patil",
            "contact_info": "sneha.patil@college.edu",
        },
        {
            "name": "Milton Stainless Steel Water Bottle",
            "category": "Water Bottle",
            "description": "Black metallic bottle left near corner table in canteen.",
            "location": "College Canteen",
            "event_date": d3,
            "type": "found",
            "contact_name": None,
            "contact_info": "Canteen Manager Desk",
        },

        # Standalone Lost Items
        {
            "name": "Fundamentals of Data Structures in C (Textbook)",
            "category": "Books and Stationery",
            "description": "Horowitz & Sahni textbook, 2nd Edition, with highlighter marks in Chapter 3 and 4.",
            "location": "Computer Center Lab 3",
            "event_date": d5,
            "type": "lost",
            "contact_name": "Kavita Rao",
            "contact_info": "kavita.rao@college.edu",
        },
        {
            "name": "Two Bike Keys on Honda Keychain",
            "category": "Keys",
            "description": "Silver ignition key and small disc brake key on a black fabric strap.",
            "location": "Two-Wheeler Student Parking Area",
            "event_date": d1,
            "type": "lost",
            "contact_name": "Siddharth Verma",
            "contact_info": "siddharth.v@college.edu",
        },

        # Standalone Found Items
        {
            "name": "SanDisk 64GB Dual USB Drive",
            "category": "Electronics",
            "description": "Silver metallic OTG flash drive with Type-C and Type-A connectors.",
            "location": "Mechanical Seminar Hall",
            "event_date": d2,
            "type": "found",
            "contact_name": None,
            "contact_info": "Security Cabin Gate 1",
        },
        {
            "name": "Navy Blue College Windcheater / Jacket",
            "category": "Clothing",
            "description": "Size M dark navy zip-up hooded jacket found on basketball court bleachers.",
            "location": "Sports Ground / Basketball Court",
            "event_date": d5,
            "type": "found",
            "contact_name": None,
            "contact_info": "Sports Department Office",
        },
    ]

    print("Inserting sample items...")
    inserted_ids = []
    for item_data in sample_items:
        item_id = db.insert_item(
            name=item_data["name"],
            category=item_data["category"],
            description=item_data["description"],
            location=item_data["location"],
            event_date=item_data["event_date"],
            item_type=item_data["type"],
            contact_name=item_data.get("contact_name"),
            contact_info=item_data.get("contact_info")
        )
        inserted_ids.append((item_id, item_data["name"], item_data["type"]))

    print(f"Successfully inserted {len(inserted_ids)} sample items.")

    # Create a realistic sample collection request for item #2 (Found Calculator)
    # The student who lost item #1 submits a request for item #2
    found_calc_id = inserted_ids[1][0]
    print(f"Adding sample collection request for found item #{found_calc_id}...")
    req_id = db.insert_collection_request(
        item_id=found_calc_id,
        requester_name="Rohan Deshmukh",
        requester_contact="rohan.deshmukh@college.edu / 9876543210",
        description="I am a FE-IT student. The calculator has 'FE-IT-24' marked with silver permanent marker under the back slider cover, and battery cap is slightly loose."
    )
    print(f"Created sample collection request #{req_id} for item #{found_calc_id}.")

    # Also add a completed/returned item for realistic dashboard statistics
    returned_item_id = db.insert_item(
        name="Brown Leather Titan Wallet",
        category="Wallet and Personal Belongings",
        description="Brown bifold wallet containing student bus pass and college smart card.",
        location="Auditorium",
        event_date=d5,
        item_type="found",
        contact_name=None,
        contact_info="Security Office Gate 2"
    )
    db.update_item_status(returned_item_id, "verification_pending")
    db.update_item_status(returned_item_id, "returned")
    print(f"Created sample returned item #{returned_item_id} for historical statistics.")

    print("\nSample data population completed successfully!")
    print("You can now view items, matching suggestions, and collection requests in the web UI.")

if __name__ == "__main__":
    run_seed()
