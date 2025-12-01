"""
Database Logging Handler for Ginseng Menu AI
This module provides a logging handler that writes logs to MongoDB
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from database.db_connection import insert_data


class DatabaseLogHandler(logging.Handler):
    """
    A logging handler that stores log records in MongoDB
    """
    
    def __init__(self, collection_name: str = "logs", level: int = logging.DEBUG):
        """
        Initialize the DatabaseLogHandler

        Args:
            collection_name (str): Name of the MongoDB collection to store logs
            level (int): Minimum logging level to record
        """
        super().__init__(level)
        self.collection_name = collection_name
        
        # Set up formatter to include more detailed information
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )

    def emit(self, record: logging.LogRecord):
        """
        Emit a log record by inserting it into MongoDB

        Args:
            record (logging.LogRecord): The log record to emit
        """
        try:
            # Format the log record into a dictionary for MongoDB
            log_entry = self.format_log_record(record)
            
            # Insert the log entry into MongoDB
            result = insert_data(self.collection_name, log_entry)
            
            if result is None:
                # If insertion fails, write to stderr to ensure the error is captured
                print(f"Failed to insert log entry into database: {log_entry}")
                
        except Exception as e:
            # Handle any exceptions during log emission
            print(f"Error in DatabaseLogHandler.emit: {e}")
            # Don't raise the exception as it could cause issues in the calling code

    def format_log_record(self, record: logging.LogRecord) -> Dict[str, Any]:
        """
        Format a log record into a dictionary suitable for MongoDB storage

        Args:
            record (logging.LogRecord): The log record to format

        Returns:
            Dict[str, Any]: Formatted log entry as a dictionary
        """
        # Convert the log record to a dictionary
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line_number": record.lineno,
            "logger_name": record.name,
            "process_id": record.process,
            "thread_id": str(record.thread),
            "thread_name": record.threadName,
        }
        
        # Add exception information if present
        if record.exc_info:
            # Format the exception info
            exc_text = self.format_exception(record.exc_info)
            log_entry["stack_trace"] = exc_text
            
        # Add any extra fields that were passed in the log call
        if hasattr(record, '__dict__'):
            extra_fields = {}
            for key, value in record.__dict__.items():
                if key not in [
                    'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                    'filename', 'module', 'lineno', 'funcName', 'created', 
                    'msecs', 'relativeCreated', 'thread', 'threadName', 
                    'processName', 'process', 'exc_info', 'exc_text', 
                    'stack_info'
                ]:
                    extra_fields[key] = value
            if extra_fields:
                log_entry["extra"] = extra_fields
                
        return log_entry

    def format_exception(self, exc_info) -> str:
        """
        Format exception information as a string

        Args:
            exc_info: Exception information from the log record

        Returns:
            str: Formatted exception string
        """
        import traceback
        return ''.join(traceback.format_exception(*exc_info))