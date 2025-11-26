#!/usr/bin/env python3
"""
Utility functions for ultrasonic sensor proximity detection with timing.
"""

import time
from typing import Dict, Any
import yaml
import threading
from .sensor import UltrasonicDistanceSensor
from pathlib import Path


class ProximityDetector:
    """
    A class to detect proximity using ultrasonic sensor with timing functionality.
    It can return True when distance is below threshold for 1 second and False 
    when distance exceeds threshold for 5 seconds.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the proximity detector with configuration.
        
        Args:
            config_path: Path to the hardware configuration file
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "hardware.yaml"
        
        self.config = self._load_config(config_path)
        self.wake_distance_cm = self.config.get('ultrasonic', {}).get('wake_distance_cm', 15)
        self.wake_trigger_duration = self.config.get('ultrasonic', {}).get('wake_trigger_duration', 1.0)  # seconds
        self.sleep_trigger_duration = self.config.get('ultrasonic', {}).get('sleep_trigger_duration', 5.0)  # seconds
        
        self.sensor = UltrasonicDistanceSensor()
        self._last_detection_time = time.time()
        self._detection_state = False  # True when object is close
        self._state_lock = threading.Lock()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Return default config if file not found
            print(f"Config file {config_path} not found, using defaults")
            return {
                'ultrasonic': {
                    'wake_distance_cm': 15,
                    'wake_trigger_duration': 1.0,
                    'sleep_trigger_duration': 5.0
                }
            }
    
    def is_within_distance(self, distance_threshold_cm: float = None) -> bool:
        """
        Check if the distance is within the specified threshold for the required duration.

        Args:
            distance_threshold_cm: Distance threshold in cm (uses config default if None)

        Returns:
            True if distance is below threshold for specified duration (person approached),
            False if distance is above threshold for specified duration (person left)
        """
        if distance_threshold_cm is None:
            distance_threshold_cm = self.wake_distance_cm

        current_distance = self.sensor.measure_distance()

        with self._state_lock:
            current_time = time.time()

            if current_distance <= distance_threshold_cm:
                # Object is close
                if not self._detection_state:
                    # Just detected, record the time
                    self._last_detection_time = current_time
                    self._detection_state = True
                    # Check if we've been close for the required duration
                    return False  # Not triggered yet
                else:
                    # Already in detection state, check if duration has passed
                    elapsed_time = current_time - self._last_detection_time
                    if elapsed_time >= self.wake_trigger_duration:
                        return True  # Has been close for required duration (person approached)
                    else:
                        return False  # Still measuring for approach
            else:
                # Object is far
                if self._detection_state:
                    # Was close before, start measuring for sleep trigger
                    self._last_detection_time = current_time
                    # Still returning True until timeout is reached
                    elapsed_time = current_time - self._last_detection_time
                    # Just set detection state to False to track that we're now in far state
                    self._detection_state = False
                    return True  # Still in the process of checking for departure
                else:
                    # In far state, check if duration has passed for timeout
                    elapsed_time = current_time - self._last_detection_time
                    if elapsed_time >= self.sleep_trigger_duration:
                        return False  # Timeout reached, confirmed person left
                    else:
                        return True  # Still counting down to departure confirmation

    def continuously_monitor(self, callback_func=None):
        """
        Continuously monitor proximity and call the callback function when state changes.

        Args:
            callback_func: Function to call when state changes (receives the current state as bool)
        """
        last_state = None
        while True:
            try:
                current_state = self.is_within_distance()
                if current_state != last_state:
                    last_state = current_state
                    if callback_func:
                        callback_func(current_state)
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
            except KeyboardInterrupt:
                break

    def get_current_distance(self) -> float:
        """
        Get the current distance measurement without affecting timing state.

        Returns:
            Current distance in cm
        """
        return self.sensor.measure_distance()


    def cleanup(self):
        """Clean up resources."""
        self.sensor.cleanup()


def is_proximity_detected(distance_threshold_cm: float = None, config_path: str = None) -> bool:
    """
    Utility function to check if an object is within the specified distance.
    This function creates a temporary sensor instance and returns True if 
    the distance is less than the threshold.
    
    Args:
        distance_threshold_cm: Distance threshold in cm (uses config default if None)
        config_path: Path to the hardware configuration file
        
    Returns:
        True if distance is less than threshold, False otherwise
    """
    if config_path is None:
        config_path = Path(__file__).parent / ".." / "config" / "hardware.yaml"
    
    # Load config to get default threshold
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        if distance_threshold_cm is None:
            distance_threshold_cm = config.get('ultrasonic', {}).get('wake_distance_cm', 15)
    except FileNotFoundError:
        # Use default value if config not found
        if distance_threshold_cm is None:
            distance_threshold_cm = 15
    
    sensor = UltrasonicDistanceSensor()
    try:
        distance = sensor.measure_distance()
        return distance <= distance_threshold_cm
    finally:
        sensor.cleanup()