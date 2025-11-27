"""
Database configuration loader
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Extract database configuration from environment variables
database = {
    'url': os.getenv('DATABASE_URL', 'mongodb://localhost:27017/'),
    'name': os.getenv('DATABASE_NAME', 'menu_ai'),
    'connection_timeout': int(os.getenv('DB_CONNECTION_TIMEOUT', '5000')),
    'server_selection_timeout': int(os.getenv('DB_SERVER_SELECTION_TIMEOUT', '5000')),
}