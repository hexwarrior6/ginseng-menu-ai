"""
Database module for Ginseng Menu AI
Provides database connection and data insertion functionality
"""

from .db_connection import get_db_connection, insert_data

__all__ = ['get_db_connection', 'insert_data']