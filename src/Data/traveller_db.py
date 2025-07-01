import sqlite3
from crypto import encrypt
from Models.traveller import Traveller
from config import DB_FILE

def insert_traveller(traveller: Traveller):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS travellers (
            traveller_id TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            birthday TEXT,
            gender TEXT,
            street_name TEXT,
            house_number TEXT,
            zip_code TEXT,
            city TEXT,
            email TEXT,
            mobile TEXT,
            driving_license TEXT,
            registration_date TEXT
        )
    ''')

    data = traveller.as_dict()

    for field in ["street_name", "zip_code", "email", "mobile"]:
        data[field] = encrypt(data[field])

    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    values = tuple(data.values())

    cursor.execute(f'''
        INSERT INTO travellers ({columns}) VALUES ({placeholders})
    ''', values)

    conn.commit()
    conn.close()
    print("[✓] Traveller registered successfully.")