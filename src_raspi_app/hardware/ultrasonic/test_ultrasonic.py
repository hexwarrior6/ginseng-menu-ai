#!/usr/bin/env python3
"""
Test script for ultrasonic sensor functionality
支持通过输入数字选择测试模块
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


def show_menu():
    """Display test menu options."""
    print("\n" + "="*50)
    print("Ultrasonic Sensor Test Menu")
    print("="*50)
    print("1. Test basic sensor functionality")
    print("2. Test simple proximity detection")
    print("3. Test proximity detection with timing")
    print("4. Run all tests")
    print("0. Exit")
    print("="*50)


def main():
    """Main function with interactive test selection."""
    print("Starting ultrasonic sensor tests...")
    
    test_functions = {
        1: test_basic_sensor,
        2: test_simple_proximity,
        3: test_proximity_detection
    }
    
    try:
        while True:
            show_menu()
            choice = input("\nPlease select a test (0-4): ").strip()
            
            if choice == '0':
                print("Exiting test program.")
                break
            elif choice == '4':
                # Run all tests
                print("\nRunning all tests...")
                for test_name, test_func in test_functions.items():
                    print(f"\nStarting test {test_name}...")
                    test_func()
                print("\nAll tests completed successfully!")
            elif choice in ['1', '2', '3']:
                # Run single test
                test_num = int(choice)
                test_func = test_functions[test_num]
                print(f"\nStarting test {test_num}...")
                test_func()
                print(f"Test {test_num} completed successfully!")
            else:
                print("Invalid selection. Please enter a number between 0 and 4.")
            
            if choice != '0':
                input("\nPress Enter to continue...")
                
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred during testing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()