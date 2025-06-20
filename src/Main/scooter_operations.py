import sqlite3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from session import get_current_user
from Models.scooter import Scooter
from Data.scooter_db import insert_scooter
from Data.input_validation import *
from Data.user_db import get_current_user
from config import DB_FILE

ENGINEER_ALLOWED_FIELDS = {
    "state_of_charge",
    "target_soc_min",
    "target_soc_max",
    "location_lat",
    "location_long",
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
        location_lat=lat,
        location_long=lon,
        out_of_service=out,
        mileage=km,
        last_maintenance_date=last_service
    )

    insert_scooter(scooter)
    print("[✓] Scooter registered successfully.")

def search_scooters():
    """Unified scooter search interface."""
    print("\n=== Search Scooters ===")
    print("Search by:")
    print("1. Scooter ID")
    print("2. Location")
    print("3. Status")
    print("4. Brand")
    print("5. Model")
    print("6. Serial Number")
    print("\n0. Back")

    choice = input("\nChoose search option: ").strip()
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    try:
        if choice == "1":
            scooter_id = input("Enter scooter ID: ").strip()
            if scooter_id:
                cur.execute("SELECT * FROM scooters WHERE scooter_id = ?", (scooter_id,))
        elif choice == "2":
            location = input("Enter location (city or area): ").strip()
            if location:
                cur.execute("SELECT * FROM scooters WHERE location LIKE ?", (f"%{location}%",))
        elif choice == "3":
            print("\nStatus options:")
            print("1. Available")
            print("2. In use")
            print("3. Maintenance")
            status_choice = input("\nChoose status: ").strip()
            statuses = {"1": "available", "2": "in_use", "3": "maintenance"}
            status = statuses.get(status_choice)
            if status:
                cur.execute("SELECT * FROM scooters WHERE status = ?", (status,))
            else:
                print("Invalid status selection.")
                return
        elif choice in ["4", "5", "6"]:
            field_map = {"4": "brand", "5": "model", "6": "serial_number"}
            field = field_map[choice]
            keyword = input(f"Enter {field} keyword to search: ").strip()
            cur.execute(f"SELECT * FROM scooters WHERE UPPER({field}) LIKE UPPER(?)", (f"%{keyword}%",))
        elif choice == "0":
            return
        else:
            print("Invalid selection.")
            return

        results = cur.fetchall()
        if not results:
            print("❌ No scooters found.")
        else:
            print("\nMatching scooters:")
            for row in results:
                print(row)
    except Exception as e:
        print(f"Error during search: {str(e)}")
    finally:
        conn.close()

def update_scooter_information(scooter_id, updates):
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

def update_scooter_via_cli():
    """Update scooter information via CLI and call update_scooter_information() with proper role checks."""
    scooter_id = input("Enter scooter ID to update: ").strip()
    if not scooter_id:
        print("❌ No scooter ID provided.")
        return

    # Haal bestaande scootergegevens op
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM scooters WHERE scooter_id = ?", (scooter_id,))
    scooter = cur.fetchone()

    if not scooter:
        print(f"❌ Scooter with ID {scooter_id} not found.")
        conn.close()
        return

    print("\nCurrent information:")
    print(f"Brand: {scooter[1]}")
    print(f"Model: {scooter[2]}")
    print(f"Serial: {scooter[3]}")
    print(f"Battery Capacity: {scooter[5]} Wh")
    print(f"SoC: {scooter[6]}%")
    print(f"Target SoC Min/Max: {scooter[7]}/{scooter[8]}")
    print(f"Location: ({scooter[9]}, {scooter[10]})")
    print(f"Out of Service: {scooter[11]}")
    print(f"Mileage: {scooter[12]}")
    print(f"Last maintenance: {scooter[13]}")

    updates = {}

    soc = input("New State of Charge (0-100): ").strip()
    if soc:
        try:
            soc = int(soc)
            if validate_soc(soc):
                updates["state_of_charge"] = soc
        except:
            pass

    soc_min = input("New Target SoC Min: ").strip()
    soc_max = input("New Target SoC Max: ").strip()
    if soc_min and soc_max:
        try:
            soc_min = int(soc_min)
            soc_max = int(soc_max)
            if validate_soc(soc_min) and validate_soc(soc_max) and soc_min < soc_max:
                updates["target_soc_min"] = soc_min
                updates["target_soc_max"] = soc_max
        except:
            pass

    lat = input("New Latitude: ").strip()
    lon = input("New Longitude: ").strip()
    if lat and lon:
        try:
            lat = float(lat)
            lon = float(lon)
            if validate_lat(lat) and validate_long(lon):
                updates["location_lat"] = lat
                updates["location_long"] = lon
        except:
            pass

    mileage = input("New Mileage (km): ").strip()
    if mileage:
        try:
            mileage = float(mileage)
            if validate_positive_float(mileage):
                updates["mileage"] = mileage
        except:
            pass

    last_service = input("New Last Maintenance Date (YYYY-MM-DD): ").strip()
    if last_service and validate_iso_date(last_service):
        updates["last_maintenance_date"] = last_service

    out_of_service = input("Out of service (0 = No, 1 = Yes): ").strip()
    if out_of_service in ["0", "1"]:
        updates["out_of_service"] = int(out_of_service)

    if updates:
        update_scooter_information(scooter_id, updates)
    else:
        print("❌ No valid updates entered.")

    conn.close()

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

def view_scooter_details(scooter_id=None):
    """View detailed information about a scooter."""
    if not scooter_id:
        scooter_id = input("Enter scooter ID: ").strip()
    
    if not scooter_id:
        print("❌ No scooter ID provided.")
        return
    
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM scooters WHERE scooter_id = ?
    """, (scooter_id,))
    
    scooter = cur.fetchone()
    if not scooter:
        print(f"❌ Scooter with ID {scooter_id} not found.")
        conn.close()
        return

    fields = [
        "Scooter ID", "Brand", "Model", "Serial Number", "Top Speed (km/h)", "Battery Capacity (Wh)",
        "State of Charge (%)", "Target SoC Min", "Target SoC Max", "Latitude", "Longitude",
        "Out of Service", "Mileage (km)", "Last Maintenance", "In Service Date"
    ]

    print("\n=== Scooter Details ===")
    for label, value in zip(fields, scooter):
        print(f"{label}: {value}")
    
    conn.close()