"""
Comprehensive test for user interaction logging functionality
"""

import sys
import os

# Add the project root to the Python path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.user_interaction_logger import interaction_logger
from utils.logger import logger
import logging


def test_comprehensive_logging():
    """Test the comprehensive logging functionality"""
    print("Testing comprehensive user interaction logging...")
    
    # Test basic user interaction logging
    print("\n1. Testing basic user action logging...")
    interaction_logger.log_user_action("test_user_123", "speech_input", "dish_suggest", {
        "speech_text": "I would like a recommendation for today's lunch",
        "timestamp": "2023-10-01 12:00:00"
    })
    
    # Test pipeline operation logging
    print("\n2. Testing pipeline operation logging...")
    interaction_logger.log_pipeline_operation(
        "test_user_123", 
        "dish_suggest", 
        "llm_request", 
        {"prompt": "Recommend dishes for lunch"}, 
        {"result": "Here are some recommendations..."}, 
        success=True
    )
    
    # Test user dish analysis logging
    print("\n3. Testing user dish analysis logging...")
    interaction_logger.log_user_dish_analysis(
        "test_user_123", 
        "/path/to/image.jpg", 
        {
            "dishes_count": 2,
            "dishes_saved": 2,
            "dishes": ["Kung Pao Chicken", "Mapo Tofu"]
        }
    )
    
    # Test user dish suggestion logging
    print("\n4. Testing user dish suggestion logging...")
    interaction_logger.log_user_dish_suggestion(
        "test_user_123", 
        "What should I eat for lunch?", 
        "I recommend the Kung Pao Chicken today."
    )
    
    # Test error logging
    print("\n5. Testing error logging...")
    interaction_logger.log_user_action("test_user_123", "operation_failed", "dish_enter", {
        "error": "Database connection failed",
        "error_type": "ConnectionError"
    })
    
    # Test logging with the main logger as well
    print("\n6. Testing integration with main logger...")
    logger.info("Main logger test message")
    logger.error("Main logger error message")
    
    print("\n✅ All logging tests completed successfully!")
    print("\nPlease check the logs in:")
    print("- File: logs/app.log")
    print("- Database: 'user_interactions' collection in MongoDB")
    print("- Database: 'logs' collection in MongoDB")


def test_decorator_logging():
    """Test the logging decorator functionality"""
    print("\n7. Testing logging decorator...")
    
    from utils.user_interaction_logger import log_user_interaction
    
    @log_user_interaction("test_operation", "test_module")
    def sample_user_function(uid, data):
        """Sample function to test the decorator"""
        print(f"Processing data for user {uid}: {data}")
        return f"Processed: {data}"
    
    # Call the decorated function
    result = sample_user_function("test_user_456", {"item": "test_data", "value": 123})
    print(f"Function returned: {result}")


if __name__ == "__main__":
    test_comprehensive_logging()
    test_decorator_logging()