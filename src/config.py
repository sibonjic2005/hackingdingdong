import os

# Database configuration
DB_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'urban_mobility.db')

# Log file configuration
LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'activity.log')

# Create data directory if it doesn't exist
data_dir = os.path.dirname(DB_FILE)
os.makedirs(data_dir, exist_ok=True)