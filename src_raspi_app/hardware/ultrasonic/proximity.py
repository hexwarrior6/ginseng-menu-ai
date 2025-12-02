#!/usr/bin/env python3
"""
Utility functions for ultrasonic sensor proximity detection with timing.
"""

import time
from typing import Dict, Any, Optional, Callable
import yaml
import threading
from .sensor import UltrasonicDistanceSensor
from pathlib import Path
import sys
import os

# Add parent directory to path to import services
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from services.telemetry import send_telemetry

ULTRASONIC_TOKEN = "kjwlj56sxpdm767jgqpk"

class ProximityDetector:
    """
    A class to detect proximity using ultrasonic sensor with timing functionality.
    It returns True when distance is below threshold for 1 second and False 
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
        self.wake_distance_cm = self.config.get('ultrasonic', {}).get('wake_distance_cm', 30)  # 改为30cm
        self.wake_trigger_duration = self.config.get('ultrasonic', {}).get('wake_trigger_duration', 1.0)  # seconds
        self.sleep_trigger_duration = self.config.get('ultrasonic', {}).get('sleep_trigger_duration', 5.0)  # seconds
        
        self.sensor = UltrasonicDistanceSensor()
        
        # 状态变量
        self._current_output_state = False  # 当前输出状态
        self._last_distance_state = False  # 上次距离状态（True=靠近，False=远离）
        self._state_start_time = time.time()  # 当前状态开始时间
        self._state_lock = threading.Lock()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Config file {config_path} not found, using defaults")
            return {
                'ultrasonic': {
                    'wake_distance_cm': 30,
                    'wake_trigger_duration': 1.0,
                    'sleep_trigger_duration': 5.0
                }
            }
    
    def is_within_distance(self, distance_threshold_cm: float = None) -> bool:
        """
        Check proximity with timing logic:
        - Returns True only after being close for 1 second
        - Returns False only after being far for 5 seconds
        
        Args:
            distance_threshold_cm: Distance threshold in cm

        Returns:
            True if confirmed close, False if confirmed far
        """
        if distance_threshold_cm is None:
            distance_threshold_cm = self.wake_distance_cm

        try:
            current_distance = self.sensor.measure_distance()
            # 过滤无效距离读数
            if current_distance < 2 or current_distance > 400:
                return self._current_output_state
        except Exception as e:
            print(f"Error measuring distance: {e}")
            return self._current_output_state

        with self._state_lock:
            current_time = time.time()
            is_close_now = current_distance <= distance_threshold_cm
            
            # 如果距离状态发生变化
            if is_close_now != self._last_distance_state:
                # 状态变化，重置计时器
                self._last_distance_state = is_close_now
                self._state_start_time = current_time
                print(f"状态变化: {'靠近' if is_close_now else '远离'}, 距离: {current_distance:.1f}cm")
            
            # 计算在当前状态下的持续时间
            time_in_current_state = current_time - self._state_start_time
            
            if is_close_now:
                # 当前处于靠近状态
                if not self._current_output_state:
                    # 输出状态为False，检查是否应该切换到True
                    if time_in_current_state >= self.wake_trigger_duration:
                        self._current_output_state = True
                        print(f"确认靠近! 持续时间: {time_in_current_state:.1f}s")
                        # Send telemetry
                        send_telemetry(ULTRASONIC_TOKEN, {"presence": True, "distance": current_distance})
                # 如果已经是True状态，保持True
            else:
                # 当前处于远离状态
                if self._current_output_state:
                    # 输出状态为True，检查是否应该切换到False
                    if time_in_current_state >= self.sleep_trigger_duration:
                        self._current_output_state = False
                        print(f"确认远离! 持续时间: {time_in_current_state:.1f}s")
                        # Send telemetry
                        send_telemetry(ULTRASONIC_TOKEN, {"presence": False, "distance": current_distance})
                # 如果已经是False状态，保持False
            
            return self._current_output_state

    def is_within_distance_robust(self, distance_threshold_cm: float = None, num_readings: int = 3) -> bool:
        """
        Robust version with multiple readings and filtering.
        
        Args:
            distance_threshold_cm: Distance threshold in cm
            num_readings: Number of readings for filtering
            
        Returns:
            Filtered proximity detection result
        """
        if distance_threshold_cm is None:
            distance_threshold_cm = self.wake_distance_cm
        
        # 取多次读数进行中值滤波
        readings = []
        for _ in range(num_readings):
            try:
                distance = self.sensor.measure_distance()
                if 2 <= distance <= 400:  # 合理范围过滤
                    readings.append(distance)
                time.sleep(0.01)
            except Exception as e:
                print(f"Error in robust measurement: {e}")
                continue
        
        if not readings:
            return self._current_output_state
        
        # 使用中值滤波
        readings.sort()
        median_distance = readings[len(readings) // 2]
        
        with self._state_lock:
            current_time = time.time()
            is_close_now = median_distance <= distance_threshold_cm
            
            # 如果距离状态发生变化
            if is_close_now != self._last_distance_state:
                self._last_distance_state = is_close_now
                self._state_start_time = current_time
                print(f"状态变化: {'靠近' if is_close_now else '远离'}, 滤波距离: {median_distance:.1f}cm")
            
            time_in_current_state = current_time - self._state_start_time
            
            if is_close_now:
                if not self._current_output_state and time_in_current_state >= self.wake_trigger_duration:
                    self._current_output_state = True
                    print(f"确认靠近! 持续时间: {time_in_current_state:.1f}s")
                    # Send telemetry
                    send_telemetry(ULTRASONIC_TOKEN, {"presence": True, "distance": median_distance})
            else:
                if self._current_output_state and time_in_current_state >= self.sleep_trigger_duration:
                    self._current_output_state = False
                    print(f"确认远离! 持续时间: {time_in_current_state:.1f}s")
                    # Send telemetry
                    send_telemetry(ULTRASONIC_TOKEN, {"presence": False, "distance": median_distance})
            
            return self._current_output_state

    def debug_proximity(self, distance_threshold_cm: float = None):
        """
        Debug function to show current state and timing information.
        """
        if distance_threshold_cm is None:
            distance_threshold_cm = self.wake_distance_cm
        
        try:
            distance = self.sensor.measure_distance()
            with self._state_lock:
                current_time = time.time()
                time_in_state = current_time - self._state_start_time
                
                print(f"距离: {distance:.2f} cm, 阈值: {distance_threshold_cm} cm")
                print(f"当前距离状态: {'靠近' if distance <= distance_threshold_cm else '远离'}")
                print(f"上次距离状态: {'靠近' if self._last_distance_state else '远离'}")
                print(f"输出状态: {self._current_output_state}")
                print(f"当前状态持续时间: {time_in_state:.1f}s")
                print(f"需要靠近时间: {self.wake_trigger_duration}s, 需要远离时间: {self.sleep_trigger_duration}s")
                print("-" * 50)
                
        except Exception as e:
            print(f"调试错误: {e}")

    def continuously_monitor(self, callback_func: Optional[Callable] = None, use_robust: bool = True, debug: bool = False):
        """
        Continuously monitor proximity.
        """
        last_output_state = None
        while True:
            try:
                if use_robust:
                    current_state = self.is_within_distance_robust()
                else:
                    current_state = self.is_within_distance()
                
                if debug:
                    self.debug_proximity()
                
                if current_state != last_output_state:
                    last_output_state = current_state
                    if callback_func:
                        callback_func(current_state)
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print("监测被用户中断")
                break
            except Exception as e:
                print(f"连续监测错误: {e}")
                time.sleep(0.5)

    def get_current_distance(self, num_readings: int = 3) -> float:
        """Get current distance with filtering."""
        readings = []
        for _ in range(max(1, num_readings)):
            try:
                distance = self.sensor.measure_distance()
                if 2 <= distance <= 400:
                    readings.append(distance)
                time.sleep(0.01)
            except Exception as e:
                print(f"获取距离错误: {e}")
                continue
        
        if not readings:
            return -1
        
        readings.sort()
        return readings[len(readings) // 2]

    def reset_state(self):
        """Reset the detector state."""
        with self._state_lock:
            self._current_output_state = False
            self._last_distance_state = False
            self._state_start_time = time.time()
            print("状态已重置")

    def cleanup(self):
        """Clean up resources."""
        try:
            self.sensor.cleanup()
        except Exception as e:
            print(f"清理错误: {e}")


def is_proximity_detected(distance_threshold_cm: float = None, config_path: str = None, 
                         use_filtering: bool = True) -> bool:
    """
    Simple proximity check without timing logic.
    """
    if config_path is None:
        config_path = Path(__file__).parent / ".." / "config" / "hardware.yaml"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        if distance_threshold_cm is None:
            distance_threshold_cm = config.get('ultrasonic', {}).get('wake_distance_cm', 30)
    except FileNotFoundError:
        if distance_threshold_cm is None:
            distance_threshold_cm = 30
    
    sensor = UltrasonicDistanceSensor()
    try:
        if use_filtering:
            readings = []
            for _ in range(3):
                try:
                    distance = sensor.measure_distance()
                    if 2 <= distance <= 400:
                        readings.append(distance)
                    time.sleep(0.01)
                except Exception:
                    continue
            
            if not readings:
                return False
            
            readings.sort()
            distance = readings[len(readings) // 2]
        else:
            distance = sensor.measure_distance()
        
        return distance <= distance_threshold_cm
    except Exception as e:
        print(f"接近检测错误: {e}")
        return False
    finally:
        try:
            sensor.cleanup()
        except Exception:
            pass


# 测试代码
if __name__ == "__main__":
    def state_change_callback(state: bool):
        if state:
            print("🚨 检测到接近！")
        else:
            print("✅ 物体已远离")
    
    detector = ProximityDetector()
    try:
        print(f"开始监测，触发距离: {detector.wake_distance_cm}cm")
        print("接近触发时间: 1秒，远离确认时间: 5秒")
        
        # 测试模式：显示详细状态信息
        import sys
        if len(sys.argv) > 1 and sys.argv[1] == "debug":
            detector.continuously_monitor(state_change_callback, use_robust=True, debug=True)
        else:
            detector.continuously_monitor(state_change_callback, use_robust=True)
            
    except KeyboardInterrupt:
        print("程序被用户中断")
    finally:
        detector.cleanup()