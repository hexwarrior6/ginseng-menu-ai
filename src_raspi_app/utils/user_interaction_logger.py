"""
User Interaction Logging Module for Ginseng Menu AI
This module provides logging for user interactions and pipeline operations
"""

import logging
import json
import functools
from datetime import datetime
from typing import Dict, Any, Optional
from .database_log_handler import DatabaseLogHandler


class UserInteractionLogger:
    """
    A specialized logger for tracking user interactions with the system
    """
    
    def __init__(self, collection_name: str = "user_interactions", level: int = logging.INFO):
        """
        Initialize the User Interaction Logger

        Args:
            collection_name (str): Name of the MongoDB collection to store user interaction logs
            level (int): Minimum logging level to record
        """
        self.collection_name = collection_name
        self.logger = logging.getLogger("ginseng_menu_ai.interactions")
        self.logger.setLevel(level)
        
        # Clear any existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Add database handler specifically for user interactions
        try:
            db_handler = DatabaseLogHandler(collection_name=collection_name, level=level)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
            )
            db_handler.setFormatter(formatter)
            self.logger.addHandler(db_handler)
        except Exception as e:
            print(f"Warning: Could not set up database logging for user interactions: {e}")
    
    def log_user_action(self, uid: str, action: str, module: str, details: Optional[Dict[str, Any]] = None):
        """
        Log a user action with detailed information

        Args:
            uid (str): User identifier
            action (str): Action performed by the user
            module (str): Module where the action occurred
            details (dict, optional): Additional details about the action
        """
        log_message = f"User {uid} performed action: {action} in module: {module}"
        extra_data = {
            "uid": uid,
            "action": action,
            "module_name": module,  # Changed from 'module' to 'module_name' to avoid conflict
            "details": details or {}
        }

        self.logger.info(log_message, extra=extra_data)
    
    def log_pipeline_operation(self, uid: str, pipeline: str, operation: str, input_data: Optional[Dict[str, Any]] = None, 
                              output_data: Optional[Dict[str, Any]] = None, success: bool = True):
        """
        Log a pipeline operation with input/output data

        Args:
            uid (str): User identifier
            pipeline (str): Pipeline name (e.g., 'dish_suggest', 'dish_enter', 'plate_analyze')
            operation (str): Specific operation within the pipeline
            input_data (dict, optional): Input data to the operation
            output_data (dict, optional): Output data from the operation
            success (bool): Whether the operation was successful
        """
        log_message = f"Pipeline {pipeline} operation {operation} {'succeeded' if success else 'failed'} for user {uid}"
        extra_data = {
            "uid": uid,
            "pipeline_name": pipeline,  # Changed from 'pipeline' to avoid potential conflict
            "operation": operation,
            "input_data": input_data or {},
            "output_data": output_data or {},
            "success": success
        }

        if success:
            self.logger.info(log_message, extra=extra_data)
        else:
            self.logger.error(log_message, extra=extra_data)
    
    def log_user_dish_analysis(self, uid: str, image_path: str, analysis_result: Dict[str, Any]):
        """
        Log dish analysis performed by a user

        Args:
            uid (str): User identifier
            image_path (str): Path to the analyzed image
            analysis_result (dict): Result of the dish analysis
        """
        log_message = f"User {uid} analyzed dish image: {image_path}"
        extra_data = {
            "uid": uid,
            "image_path": image_path,
            "analysis_result": analysis_result,
            "module_name": "plate_analyze"  # Changed from 'module' to 'module_name'
        }

        self.logger.info(log_message, extra=extra_data)
    
    def log_user_dish_suggestion(self, uid: str, speech_input: str, suggestion_result: str):
        """
        Log dish suggestion request made by a user

        Args:
            uid (str): User identifier
            speech_input (str): User's speech input
            suggestion_result (str): Result from dish suggestion system
        """
        log_message = f"User {uid} requested dish suggestion with input: {speech_input[:50]}..."
        extra_data = {
            "uid": uid,
            "speech_input": speech_input,
            "suggestion_result": suggestion_result,
            "module_name": "dish_suggest"  # Changed from 'module' to 'module_name'
        }

        self.logger.info(log_message, extra=extra_data)


# Create a global instance of the user interaction logger
interaction_logger = UserInteractionLogger()


def log_user_interaction(action: str, module: str):
    """
    Decorator to automatically log user interactions with functions

    Args:
        action (str): Description of the action
        module (str): Module name
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Try to extract uid from the first argument or from kwargs
            uid = "unknown"
            if args and len(args) > 0:
                # If the first argument is a string, treat it as uid
                if isinstance(args[0], str) and len(args[0]) == 8:  # Assuming 8-char hex UID
                    uid = args[0]
            elif 'uid' in kwargs:
                uid = kwargs['uid']
            
            # Log the start of the function
            interaction_logger.log_user_action(uid, action, module, {
                "function": func.__name__,
                "args_length": len(args),
                "kwargs_keys": list(kwargs.keys())
            })
            
            try:
                result = func(*args, **kwargs)
                
                # Log successful completion
                interaction_logger.log_user_action(uid, f"{action}_completed", module, {
                    "function": func.__name__,
                    "result_type": type(result).__name__,
                    "result_length": len(result) if hasattr(result, '__len__') else None
                })
                
                return result
            except Exception as e:
                # Log errors
                interaction_logger.log_user_action(uid, f"{action}_failed", module, {
                    "function": func.__name__,
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                raise
        
        return wrapper
    return decorator