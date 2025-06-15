import sqlite3

def init_db():
    conn = sqlite3.connect("data/urban_mobility.db")
    c = conn.cursor()

    # USERS table (SysAdmin, Service Engineer)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            registration_date TEXT
        )
    ''')

    # TRAVELLERS table
    c.execute('''
        CREATE TABLE IF NOT EXISTS travellers (
            traveller_id INTEGER PRIMARY KEY AUTOINCREMENT,
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

    # SCOOTERS table
    c.execute('''
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

    conn.commit()
    conn.close()