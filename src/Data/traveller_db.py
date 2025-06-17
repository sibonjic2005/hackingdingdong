import sqlite3
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Data.crypto import encrypt
from Models.traveller import Traveller
from datetime import datetime




def insert_traveller(traveller: Traveller):
    
    db_path = os.path.join(os.path.dirname(__file__), 'urban_mobility.db')
    conn = sqlite3.connect(db_path)
    print(f"Using database at: {db_path}")
    print("Connected to the database.")
    cursor = conn.cursor()

    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS travellers (
            traveller_id TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            birthday TEXT,
            gender TEXT,
            street TEXT,
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
    encrypted_fields = ["street", "zip_code", "email", "mobile_phone"]

    for field in encrypted_fields:
        data[field] = encrypt(data[field])

    values = tuple(data.values())
    cursor.execute('''
        INSERT INTO travellers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', values)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    traveller = Traveller(
    first_name="Fatima",
    last_name="Ali",
    birthday="2001-05-12",
    gender="female",
    street="Tulipstraat",
    house_number="17",
    zip_code="1234AB",
    city="Rotterdam",
    email="fatima@example.com",
    mobile_phone="0612345678",
    driving_license="AB1234567",
    )
    insert_traveller(traveller)
