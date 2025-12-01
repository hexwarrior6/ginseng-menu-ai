"""
Test script for database logging functionality
"""

import sys
import os

# Add the project root to the Python path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import logger


def test_database_logging():
    """Test the database logging functionality"""
    print("Testing database logging functionality...")
    
    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # Test with extra information
    logger.info("User action", extra={
        "user_id": "12345",
        "action": "login",
        "ip_address": "192.168.1.1"
    })
    
    # Test exception logging
    try:
        result = 10 / 0
    except ZeroDivisionError:
        logger.exception("Division by zero error occurred")
    
    print("Test messages sent to both file and database logs.")
    print("Please check the logs/app.log file and the 'logs' collection in MongoDB to verify.")


if __name__ == "__main__":
    test_database_logging()