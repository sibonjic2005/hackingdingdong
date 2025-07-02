import sqlite3
from Data.crypto import decrypt, encrypt

from Models.traveller import Traveller
from Data.traveller_db import insert_traveller
from Data.input_validation import *
from config import DB_FILE
from Data.logging_util import SystemLogger
logger = SystemLogger()
from session import get_current_user
current_user = get_current_user()

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
    mobile = input("Mobile (start with 06, 10 digits total): ")
    while not validate_mobile(mobile):
        mobile = input("Invalid mobile. Try again: ")

    driving_license = input("Driving license (X/DDDDDDD or XXDDDDDDD): ")
    while not validate_driving_license(driving_license):
        driving_license = input("Invalid license. Try again: ")

    traveller = Traveller(first_name, last_name, birthday, gender, street_name,
                          house_number, zip_code, city, email,
                          mobile, driving_license)

    insert_traveller(traveller)
    logger.log_activity(current_user["username"], "New traveller registered",
                        details=f"Traveller ID: {traveller.traveller_id}")

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
        row[5] = decrypt(row[5])
        row[7] = decrypt(row[7])
        row[9] = decrypt(row[9])
        row[10] = decrypt(row[10])
        print(row)
        decrypted.append(row)

    return decrypted

def update_traveller_record():
    """Interactively update editable fields for a traveller."""
    if not is_admin_user():
        print("❌ You do not have permission to perform this action.")
        return

    traveller_id = input("Enter Traveller ID to update: ").strip()
    if not traveller_id or len(traveller_id) < 5:
        print("Invalid Traveller ID format.")
        return

    editable_fields = {
        "1": "first_name",
        "2": "last_name",
        "3": "street_name",
        "4": "house_number",
        "5": "zip_code",
        "6": "city",
        "7": "email",
        "8": "mobile"
    }

    print("\nChoose fields to update (one at a time):")
    for key, field in editable_fields.items():
        print(f"{key}. {field}")

    update_data = {}

    while True:
        choice = input("\nEnter number of field to update (or ENTER to finish): ").strip()
        if choice == "":
            break
        if choice not in editable_fields:
            print("❌ Invalid choice.")
            continue

        field = editable_fields[choice]
        new_value = input(f"Enter new value for {field}: ").strip()

        # Validation
        if field == "zip_code" and not validate_zip(new_value):
            print("❌ Invalid ZIP code.")
            continue
        if field == "email" and not validate_email(new_value):
            print("❌ Invalid email address.")
            continue
        if field == "mobile" and not validate_mobile(new_value):
            print("❌ Invalid mobile number.")
            continue
        if field == "house_number":
            if not new_value.isdigit():
                print("❌ House number must be numeric.")
                continue
            new_value = str(new_value)

        if field in ["street_name", "zip_code", "email", "mobile"]:
            new_value = encrypt(new_value)

        update_data[field] = new_value

    if not update_data:
        print("⚠ No updates made.")
        return

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    parts = [f"{k} = ?" for k in update_data]
    values = list(update_data.values()) + [traveller_id]

    cur.execute(f"UPDATE travellers SET {', '.join(parts)} WHERE traveller_id = ?", values)
    conn.commit()
    conn.close()

    print("✅ Traveller record updated successfully.")
    logger.log_activity(current_user["username"], "Traveller record updated",
                        details=f"Updated fields: {', '.join(update_data.keys())}")
    

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
    print("🗑️ Traveller record deleted.")


    logger.log_activity(current_user["username"], "Traveller record deleted")