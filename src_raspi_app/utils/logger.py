import logging
import os
from datetime import datetime
from .database_log_handler import DatabaseLogHandler


def setup_logging(
    log_file_path: str = "../logs/app.log",
    db_collection: str = "logs",
    log_level: int = logging.INFO
):
    """
    Set up centralized logging with both file and database handlers

    Args:
        log_file_path (str): Path to the log file
        db_collection (str): MongoDB collection name for logs
        log_level (int): Minimum logging level
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # Get the root logger
    logger = logging.getLogger("ginseng_menu_ai")
    logger.setLevel(log_level)

    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )

    # File handler
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Database handler
    try:
        db_handler = DatabaseLogHandler(collection_name=db_collection, level=log_level)
        db_handler.setFormatter(formatter)
        logger.addHandler(db_handler)
    except Exception as e:
        print(f"Warning: Could not set up database logging: {e}")
        print("Continuing with file-only logging")

    return logger


# Initialize the logger with default settings
logger = setup_logging()
