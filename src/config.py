# src/config.py
import os

# Database configuration
DB_FILE = os.path.join('data', 'urban_mobility.db')  # Path to your SQLite database
LOG_FILE = os.path.join('data', 'activity.log')     # Path to your log file

# Encryption settings
ENCRYPTION_KEY_FILE = os.path.join('data', 'encryption_key.key')    