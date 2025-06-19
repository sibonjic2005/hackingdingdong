import sqlite3
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Data.crypto import encrypt
from datetime import datetime
from Models.scooter import Scooter
from config import DB_FILE

def insert_scooter(scooter: Scooter):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Ensure table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scooters (
            scooter_id TEXT PRIMARY KEY,
            brand TEXT,
            model TEXT,
            serial_number TEXT UNIQUE,
            top_speed REAL,
            battery_capacity INTEGER,
            state_of_charge INTEGER,
            target_soc_min INTEGER,
            target_soc_max INTEGER,
            latitude REAL,
            longitude REAL,
            out_of_service INTEGER,
            mileage REAL,
            last_maintenance_date TEXT,
            in_service_date TEXT
        )
    ''')

    # Prepare data
    data = scooter.as_dict()
    values = tuple(data.values())

    # Insert into table
    cursor.execute('''
        INSERT INTO scooters VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', values)

    conn.commit()
    conn.close()
    print("[✓] Scooter registered.")
