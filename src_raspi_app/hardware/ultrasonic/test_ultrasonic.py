#!/usr/bin/env python3
"""
Test script for ultrasonic sensor functionality
"""

import time

from hardware.ultrasonic.sensor import UltrasonicDistanceSensor
from hardware.ultrasonic.proximity import ProximityDetector, is_proximity_detected

def test_basic_sensor():
    """Test basic distance measurement functionality."""
    print("Testing basic sensor functionality...")
    sensor = UltrasonicDistanceSensor()
    
    try:
        for i in range(5):
            distance = sensor.measure_distance()
            print(f"Distance measurement {i+1}: {distance:.2f} cm")
            time.sleep(0.5)
    finally:
        sensor.cleanup()
    
    print("Basic sensor test completed.\n")


def test_proximity_detection():
    """Test proximity detection with timing."""
    print("Testing proximity detection with timing...")
    detector = ProximityDetector()
    
    try:
        print("Measuring distance for 100 seconds. Move your hand closer than 15cm...")
        start_time = time.time()
        
        while time.time() - start_time < 100:
            is_close = detector.is_within_distance()
            current_distance = detector.get_current_distance()
            print(f"Distance: {current_distance:.2f} cm, Within range (1s/5s logic): {is_close}")
            time.sleep(0.5)
    finally:
        detector.cleanup()
    
    print("Proximity detection test completed.\n")


def test_simple_proximity():
    """Test simple proximity detection function."""
    print("Testing simple proximity detection function...")
    
    # Test with default configuration
    result = is_proximity_detected()
    print(f"Is object within default distance (15cm)? {result}")
    
    # Test with custom distance
    result_custom = is_proximity_detected(distance_threshold_cm=20)
    print(f"Is object within 20cm? {result_custom}")
    
    print("Simple proximity test completed.\n")


if __name__ == "__main__":
    print("Starting ultrasonic sensor tests...\n")
    
    try:
        test_basic_sensor()
        test_simple_proximity()
        test_proximity_detection()
        
        print("All tests completed successfully!")
    except KeyboardInterrupt:
        print("\nTests interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred during testing: {str(e)}")
        import traceback
        traceback.print_exc()