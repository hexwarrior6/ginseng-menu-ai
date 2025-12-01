#!/usr/bin/env python3
"""
Database module usage example — Revised for minimal schema:
- users: uid (8-digit hex, PK), preferences, created_at, last_active
- dishes: name, category, timestamp, calories, nutrition
"""

import sys
import os
from datetime import datetime, timezone
import pytz

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from database import insert_data, get_db_connection


def example_insert_user():
    print("=== Insert User (uid + preferences + timestamps) ===")

    # Using timezone-aware datetime in Asia/Shanghai timezone
    local_tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(local_tz)

    user_data = {
        "uid": "A1B2C3D4",  # 8-digit hex, treated as primary key
        "preferences": {
            "dietary_restrictions": ["vegetarian"],
            "favorite_cuisines": ["Italian", "Chinese"],
            "allergies": ["nuts"]
        },
        "created_at": current_time,
        "last_active": current_time
    }

    # Insert into 'users' collection
    result_id = insert_data("users", user_data)
    if result_id:
        print(f"✅ User {user_data['uid']} inserted, DB ID: {result_id}")
        return user_data["uid"]
    else:
        print("❌ Failed to insert user")
        return None


def example_insert_dish():
    print("\n=== Insert Dish (name, category, time, calories, nutrition) ===")

    # Using timezone-aware datetime in Asia/Shanghai timezone
    local_tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(local_tz)

    dish_data = {
        "name": "Beef Tacos",
        "category": "Mexican",
        "timestamp": current_time,
        "calories": 420,
        "nutrition": {
            "protein_g": 22,
            "carbs_g": 38,
            "fat_g": 24,
            "fiber_g": 5
        }
    }

    result_id = insert_data("dishes", dish_data)
    if result_id:
        print(f"✅ Dish '{dish_data['name']}' inserted, DB ID: {result_id}")
        return result_id
    else:
        print("❌ Failed to insert dish")
        return None


def example_multiple_dishes():
    print("\n=== Insert Multiple Dishes ===")
    
    from database.db_connection import insert_many_data

    # Using timezone-aware datetime in Asia/Shanghai timezone
    local_tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(local_tz)

    dishes = [
        {
            "name": "Ramen",
            "category": "Japanese",
            "timestamp": current_time,
            "calories": 580,
            "nutrition": {"protein_g": 18, "carbs_g": 78, "fat_g": 20}
        },
        {
            "name": "Pad Thai",
            "category": "Thai",
            "timestamp": current_time,
            "calories": 490,
            "nutrition": {"protein_g": 15, "carbs_g": 70, "fat_g": 18}
        },
        {
            "name": "Grilled Salmon",
            "category": "Seafood",
            "timestamp": current_time,
            "calories": 360,
            "nutrition": {"protein_g": 34, "carbs_g": 2, "fat_g": 22}
        }
    ]
    
    result_ids = insert_many_data("dishes", dishes)
    if result_ids:
        print(f"✅ {len(result_ids)} dishes inserted, IDs: {result_ids}")
        return result_ids
    else:
        print("❌ Failed to insert dishes")
        return None


def main():
    print("Ginseng Menu AI — Minimal DB Schema Demo")
    print("=" * 50)
    
    try:
        # Check connection
        db = get_db_connection()
        print(f"✅ Connected to DB: {db.name}")

        # Run minimal examples
        uid = example_insert_user()
        if uid:
            example_insert_dish()
            example_multiple_dishes()

        print("\n" + "=" * 50)
        print("✅ Done: Schema limited to 'users' & 'dishes' only.")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()