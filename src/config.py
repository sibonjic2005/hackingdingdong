import os
import sqlite3

DB_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'urban_mobility.db')

sqlite3.connect(DB_FILE).execute('PRAGMA journal_mode=WAL')

LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'activity.log')

data_dir = os.path.dirname(DB_FILE)
os.makedirs(data_dir, exist_ok=True)