import sqlite3
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Models.scooter import Scooter
from config import DB_FILE

def insert_scooter(scooter: Scooter):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scooters (
            scooter_id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT,
            model TEXT,
            serial_number TEXT UNIQUE,
            top_speed REAL,
            battery_capacity INTEGER,
            state_of_charge INTEGER,
            target_soc_min INTEGER,
            target_soc_max INTEGER,
            location_lat REAL,
            location_long REAL,
            out_of_service INTEGER,
            mileage REAL,
            last_maintenance_date TEXT,
            in_service_date TEXT
        )
    ''')

    data = scooter.as_dict()
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    values = tuple(data.values())

    cursor.execute(f'''
        INSERT INTO scooters ({columns}) VALUES ({placeholders})
    ''', values)

    conn.commit()
    conn.close()
    print("[✓] Scooter registered.")