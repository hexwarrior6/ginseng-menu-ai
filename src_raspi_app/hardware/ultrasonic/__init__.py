"""
Ultrasonic sensor module for the Ginseng Menu AI project.
"""

from .sensor import UltrasonicDistanceSensor
from .proximity import ProximityDetector, is_proximity_detected

__all__ = ['UltrasonicDistanceSensor', 'ProximityDetector', 'is_proximity_detected']