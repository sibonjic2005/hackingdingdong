import sqlite3
import sys
import os
from Data.crypto import encrypt
from Models.traveller import Traveller
from session import get_current_user
from datetime import datetime
from config import DB_FILE

def insert_traveller(traveller: Traveller):
    """Insert a new traveller into the database."""
    conn = sqlite3.connect(DB_FILE)
    print(f"Using database at: {DB_FILE}")
    print("Connected to the database.")
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
            mobile_phone TEXT,
            driving_license TEXT,
            registration_date TEXT
        )
    ''')
    print("Traveller table created (if it didn't exist already).")


    data = traveller.as_dict()
    encrypted_fields = ["street_name", "zip_code", "email", "mobile_phone"]

    for field in encrypted_fields:
        data[field] = encrypt(data[field])

    values = tuple(data.values())
    cursor.execute('''
        INSERT INTO travellers (traveller_id, first_name, last_name, birthday, gender, 
                              street_name, house_number, zip_code, city, email, 
                              mobile_phone, driving_license, registration_date) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', values)

    conn.commit()
    conn.close()
    print("[✓] Traveller registered successfully.")
