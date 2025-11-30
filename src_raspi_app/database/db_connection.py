"""
Database connection module for Ginseng Menu AI
Provides MongoDB connection and data insertion functionality
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import pytz

# Load environment variables and configuration
load_dotenv()

# Import database configuration
try:
    from config.database import database as db_config
except ImportError:
    # Fallback to environment variables if config module is not available
    import os
    db_config = {
        'url': os.getenv('DATABASE_URL', 'mongodb://localhost:27017/'),
        'name': os.getenv('DATABASE_NAME', 'menu_ai'),
        'connection_timeout': int(os.getenv('DB_CONNECTION_TIMEOUT', '5000')),
        'server_selection_timeout': int(os.getenv('DB_SERVER_SELECTION_TIMEOUT', '5000')),
    }

# Set up logging
logger = logging.getLogger(__name__)

def convert_datetime_to_utc(data):
    """
    Recursively convert datetime objects in data to UTC timezone
    """
    if isinstance(data, dict):
        return {key: convert_datetime_to_utc(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_datetime_to_utc(item) for item in data]
    elif isinstance(data, datetime):
        if data.tzinfo is None:
            # Assume local timezone is Asia/Shanghai (UTC+8) if no timezone info
            local_tz = pytz.timezone('Asia/Shanghai')
            data = local_tz.localize(data)
        # Convert to UTC
        return data.astimezone(timezone.utc)
    else:
        return data

class DatabaseConnection:
    """
    Singleton class for managing MongoDB connection
    """
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._connect()

    def _connect(self):
        """Establish MongoDB connection"""
        try:
            self._client = MongoClient(
                db_config['url'],
                serverSelectionTimeoutMS=db_config['server_selection_timeout'],  # timeout from config
                connectTimeoutMS=db_config['connection_timeout'],
                socketTimeoutMS=db_config['connection_timeout']
            )
            # Test the connection
            self._client.admin.command('ping')
            self._db = self._client[db_config['name']]
            logger.info(f"Successfully connected to MongoDB: {db_config['url']}, Database: {db_config['name']}")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during MongoDB connection: {e}")
            raise

    def get_database(self):
        """Get database instance"""
        if self._db is None:
            self._connect()
        return self._db

    def close_connection(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            logger.info("MongoDB connection closed")


def get_db_connection():
    """
    Get database connection instance
    
    Returns:
        Database: MongoDB database instance
    """
    db_conn = DatabaseConnection()
    return db_conn.get_database()


def insert_data(collection_name: str, data: Dict[str, Any]) -> Optional[str]:
    """
    Insert data into specified collection

    Args:
        collection_name (str): Name of the collection to insert data into
        data (dict): Data to be inserted

    Returns:
        str: Inserted document ID, or None if insertion failed
    """
    try:
        db = get_db_connection()
        collection = db[collection_name]

        # Convert datetime objects to UTC before inserting
        data_with_converted_dates = convert_datetime_to_utc(data)

        # Insert the data
        result = collection.insert_one(data_with_converted_dates)

        logger.info(f"Data inserted successfully into collection '{collection_name}' with ID: {result.inserted_id}")
        return str(result.inserted_id)

    except OperationFailure as e:
        logger.error(f"Database operation failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inserting data: {e}")
        return None


def insert_many_data(collection_name: str, data_list: list) -> Optional[list]:
    """
    Insert multiple documents into specified collection

    Args:
        collection_name (str): Name of the collection to insert data into
        data_list (list): List of data dictionaries to be inserted

    Returns:
        list: List of inserted document IDs, or None if insertion failed
    """
    try:
        db = get_db_connection()
        collection = db[collection_name]

        # Convert datetime objects to UTC before inserting
        converted_data_list = [convert_datetime_to_utc(data) for data in data_list]

        # Insert multiple documents
        result = collection.insert_many(converted_data_list)

        inserted_ids = [str(id) for id in result.inserted_ids]
        logger.info(f"Multiple data inserted successfully into collection '{collection_name}', count: {len(inserted_ids)}")
        return inserted_ids

    except OperationFailure as e:
        logger.error(f"Database operation failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inserting multiple data: {e}")
        return None


def close_db_connection():
    """
    Close the database connection
    """
    db_conn = DatabaseConnection()
    db_conn.close_connection()


# Context manager for database operations
class DatabaseManager:
    """
    Context manager for database operations
    Ensures proper connection handling
    """
    
    def __enter__(self):
        self.db = get_db_connection()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # In this implementation, we don't close the connection here
        # because it's a singleton, but we could implement connection pooling
        pass