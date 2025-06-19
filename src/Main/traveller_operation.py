import sqlite3
import os, sys
from Data.crypto import decrypt, encrypt
from session import get_current_user
from Models.traveller import Traveller
from Data.traveller_db import insert_traveller
from Data.input_validation import *
from config import DB_FILE

def is_admin_user():
    return get_current_user()["role"] in ["System Administrator", "Super Administrator"]

def create_traveller_from_input():
    """Register a new traveller interactively with input validation."""
    if not is_admin_user():
        print("❌ You do not have permission to perform this action.")
        return
    first_name = input("First name: ")
    last_name = input("Last name: ")
    birthday = input("Birthday (YYYY-MM-DD): ")
    while not validate_birthday(birthday):
        birthday = input("Invalid date. Try again (YYYY-MM-DD): ")

    gender = input("Gender (male/female): ")
    while not validate_gender(gender):
        gender = input("Invalid gender. Enter 'male' or 'female': ")

    street_name = input("Street: ")
    house_number = input("House number: ")
    zip_code = input("ZIP code (e.g. 1234AB): ")
    while not validate_zip(zip_code):
        zip_code = input("Invalid ZIP. Try again: ")

    city = input("City: ")
    email = input("Email: ")
    mobile_phone = input("Mobile (start with 06, 10 digits total): ")
    while not validate_mobile(mobile_phone):
        mobile_phone = input("Invalid mobile. Try again: ")

    driving_license = input("Driving license (X/DDDDDDD or XXDDDDDDD): ")
    while not validate_driving_license(driving_license):
        driving_license = input("Invalid license. Try again: ")

    traveller = Traveller(first_name, last_name, birthday, gender, street_name,
                          house_number, zip_code, city, email,
                          mobile_phone, driving_license)

    insert_traveller(traveller)
    print("Traveller registered successfully!")

def search_travellers():
    """Search for travellers using partial matches on specified field."""
    if not is_admin_user():
        print("❌ You do not have permission to perform this action.")
        return
    fields = ["first_name", "last_name", "traveller_id"]
    print("Search travellers by:")
    for i, f in enumerate(fields, start=1):
        print(f"{i}. {f}")

    try:
        field = fields[int(input("Choose field (1–3): ")) - 1]
    except (ValueError, IndexError):
        print("❌ Invalid selection.")
        return []

    keyword = input(f"Enter {field} keyword: ").strip()

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM travellers WHERE UPPER({field}) LIKE UPPER(?)", (f"%{keyword}%",))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("🔍 No matching travellers found.")
        return []

    print("\nMatching travellers:")
    decrypted = []
    for row in rows:
        row = list(row)
        # Decrypt sensitive fields
        row[5] = decrypt(row[5])     # street
        row[7] = decrypt(row[7])     # zip code
        row[9] = decrypt(row[9])     # email
        row[10] = decrypt(row[10])   # mobile phone
        print(row)
        decrypted.append(row)

    return decrypted


def update_traveller_record(traveller_id, update_data):
    """Update fields of an existing traveller record."""
    if not is_admin_user():
        print("❌ You do not have permission to perform this action.")
        return
    if not update_data:
        print("No update data provided.")
        return

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    fields = []
    values = []

    for key, val in update_data.items():
        if key in ['street', 'zip_code', 'email', 'mobile_phone']:
            val = encrypt(val)
        fields.append(f"{key} = ?")
        values.append(val)

    values.append(traveller_id)
    sql = f"UPDATE travellers SET {', '.join(fields)} WHERE traveller_id = ?"
    cur.execute(sql, values)
    conn.commit()
    conn.close()
    print("Traveller record updated successfully.")


def remove_traveller(traveller_id):
    """Delete a traveller by their unique ID."""
    if not is_admin_user():
        print("❌ You do not have permission to perform this action.")
        return
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM travellers WHERE traveller_id = ?", (traveller_id,))
    conn.commit()
    conn.close()
    print("Traveller record deleted.")
