#!/usr/bin/env python3
"""
Ultrasonic distance sensor module for measuring distances using HC-SR04 sensor.
"""

import RPi.GPIO as GPIO
import time
from typing import Optional


class UltrasonicDistanceSensor:
    """
    A class to interface with HC-SR04 ultrasonic sensor for distance measurements.
    """
    
    def __init__(self, trig_pin: int = 11, echo_pin: int = 12):
        """
        Initialize the ultrasonic sensor with specified GPIO pins.
        
        Args:
            trig_pin: GPIO pin number for TRIG (default 11)
            echo_pin: GPIO pin number for ECHO (default 12)
        """
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.setup()
    
    def setup(self):
        """Setup GPIO pins for the ultrasonic sensor."""
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.trig_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
    
    def measure_distance(self) -> float:
        """
        Measure the distance using ultrasonic sensor.
        
        Returns:
            Distance in centimeters as a float
        """
        GPIO.output(self.trig_pin, 0)
        time.sleep(0.000002)

        GPIO.output(self.trig_pin, 1)
        time.sleep(0.00001)
        GPIO.output(self.trig_pin, 0)

        # Wait for echo to start
        while GPIO.input(self.echo_pin) == 0:
            pass
        time1 = time.time()
        
        # Wait for echo to end
        while GPIO.input(self.echo_pin) == 1:
            pass
        time2 = time.time()

        during = time2 - time1
        distance = during * 340 / 2 * 100  # Convert to cm
        return distance
    
    def cleanup(self):
        """Clean up GPIO resources."""
        GPIO.cleanup()