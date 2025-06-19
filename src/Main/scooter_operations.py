import sqlite3
import os, sys
from session import get_current_user
from Models.scooter import Scooter
from Data.scooter_db import insert_scooter
from Data.input_validation import *
from Data.user_db import get_current_user
from config import DB_FILE

# Fields editable by Service Engineers
ENGINEER_ALLOWED_FIELDS = {
    "state_of_charge",
    "target_soc_min",
    "target_soc_max",
    "latitude",
    "longitude",
    "out_of_service",
    "mileage",
    "last_maintenance_date"
}
def is_admin_user():
    return get_current_user()["role"] in ["System Administrator", "Super Administrator"]

def create_scooter_from_input():
    """Collect scooter details from user input and create a Scooter object."""
    if not is_admin_user():
        print("❌ You do not have permission to perform this action.")
        return
    brand = input("Brand: ")
    model = input("Model: ")

    serial = input("Serial Number (10–17 alphanumeric): ")
    while not validate_serial_number(serial):
        serial = input("Invalid serial. Try again: ")

    try:
        top_speed = float(input("Top speed (km/h): "))
        while not validate_positive_float(top_speed):
            top_speed = float(input("Must be a positive number. Try again: "))
    except:
        print("Invalid input.")
        return

    try:
        capacity = int(input("Battery capacity (Wh): "))
        while not validate_positive_int(capacity):
            capacity = int(input("Must be a positive number. Try again: "))
    except:
        print("Invalid input.")
        return

    try:
        soc = int(input("State of charge (%): "))
        while not validate_soc(soc):
            soc = int(input("0–100 only. Try again: "))
    except:
        print("Invalid input.")
        return

    try:
        soc_min = int(input("Target SoC MIN (%): "))
        soc_max = int(input("Target SoC MAX (%): "))
        while not (validate_soc(soc_min) and validate_soc(soc_max) and soc_min < soc_max):
            print("Enter valid min/max between 0–100 (min < max)")
            soc_min = int(input("Target SoC MIN (%): "))
            soc_max = int(input("Target SoC MAX (%): "))
    except:
        print("Invalid input.")
        return

    try:
        lat = float(input("Latitude (5 decimals): "))
        while not validate_lat(lat):
            lat = float(input("Out of bounds. Try again: "))
    except:
        print("Invalid input.")
        return

    try:
        lon = float(input("Longitude (5 decimals): "))
        while not validate_long(lon):
            lon = float(input("Out of bounds. Try again: "))
    except:
        print("Invalid input.")
        return

    try:
        out = int(input("Out of service (0 = No, 1 = Yes): "))
        while out not in [0, 1]:
            out = int(input("Only 0 or 1 allowed: "))
    except:
        print("Invalid input.")
        return

    try:
        km = float(input("Mileage (km): "))
        while not validate_positive_float(km):
            km = float(input("Must be a positive number. Try again: "))
    except:
        print("Invalid input.")
        return

    last_service = input("Last maintenance date (YYYY-MM-DD): ")
    while not validate_iso_date(last_service):
        last_service = input("Invalid format. Try again: ")

    scooter = Scooter(
        brand=brand,
        model=model,
        serial_number=serial,
        top_speed=top_speed,
        battery_capacity=capacity,
        state_of_charge=soc,
        target_soc_min=soc_min,
        target_soc_max=soc_max,
        latitude=lat,
        longitude=lon,
        out_of_service=out,
        mileage=km,
        last_maintenance_date=last_service
    )

    insert_scooter(scooter)
    print("[✓] Scooter registered successfully.")
    
def search_scooters():
    """Prompt user to search for scooters by brand, model, or serial_number."""
    print("Search scooters by:")
    fields = ["brand", "model", "serial_number"]
    for i, field in enumerate(fields, start=1):
        print(f"{i}. {field}")

    choice = input("Choose a field (1–3): ").strip()
    try:
        field = fields[int(choice) - 1]
    except (ValueError, IndexError):
        print("❌ Invalid selection.")
        return []

    keyword = input(f"Enter {field} keyword to search: ").strip()

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM scooters WHERE UPPER({field}) LIKE UPPER(?)", (f"%{keyword}%",))
    results = cur.fetchall()
    conn.close()

    if not results:
        print("🔍 No scooters found.")
    else:
        print("\nMatching scooters:")
        for row in results:
            print(row)

    return results


def update_scooter(scooter_id, updates):
    """Update a scooter, with field-level restrictions based on user role."""
    actor_role = get_current_user()["role"]
    if not updates:
        print("No update fields provided.")
        return

    if actor_role == "Service Engineer":
        illegal = [k for k in updates if k not in ENGINEER_ALLOWED_FIELDS]
        if illegal:
            print(f"❌ You are not allowed to update: {', '.join(illegal)}")
            return

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    columns = []
    values = []

    for k, v in updates.items():
        columns.append(f"{k} = ?")
        values.append(v)

    values.append(scooter_id)
    cur.execute(
        f"UPDATE scooters SET {', '.join(columns)} WHERE scooter_id = ?",
        values
    )

    conn.commit()
    conn.close()
    print("✅ Scooter updated.")


def delete_scooter(scooter_id):
    """Delete a scooter. Only allowed for SysAdmin or SuperAdmin."""
    actor_role = get_current_user()["role"]
    if actor_role not in ["System Administrator", "Super Administrator"]:
        print("❌ Access denied: only System or Super Admin may delete scooters.")
        return

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM scooters WHERE scooter_id = ?", (scooter_id,))
    conn.commit()
    conn.close()
    print("✅ Scooter deleted.")
