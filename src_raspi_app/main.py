#!/usr/bin/env python3
"""
人参菜单AI系统主程序 - 优化版
修复超声波检测失效问题
"""

import time
import threading
import signal
import sys
from typing import Optional

# 硬件模块
from hardware.ultrasonic import ProximityDetector
from hardware.audio import recognize_speech_continuous, init_recognizer
from hardware.camera import capture_image
from hardware.display import ScreenDriver
from hardware.rfid import read_uid
from hardware.touchscreen_handler import TouchscreenCommandHandler

# 服务模块
from pipeline.dish_enter import capture_and_analyze_dishes

# 配置模块
from config.base import app, flask
from config.hardware import ultrasonic
from config.model import vision_model, text_model


class GinsengMenuApp:
    """主应用类：协调所有组件运行"""

    def __init__(self):
        self.running = False
        self.user_id = None
        self.proximity_detector = ProximityDetector()
        self.display = ScreenDriver(port="/dev/ttyUSB1", baudrate=9600)
        self.touchscreen_handler = None
        
        # 添加线程锁保护共享资源
        self.display_lock = threading.Lock()
        self.session_active = False
        self.session_lock = threading.Lock()
        
        # 超声波检测控制标志
        self.ultrasonic_enabled = True
        self.ultrasonic_lock = threading.Lock()

        # 初始化音频
        self.init_audio()

    def init_audio(self):
        """初始化语音识别"""
        try:
            init_recognizer()
            print("✅ 语音系统已初始化")
        except Exception as e:
            print(f"❌ 语音初始化失败：{e}")

    def init_touchscreen_handler(self):
        """初始化触摸屏命令处理器"""
        try:
            self.touchscreen_handler = TouchscreenCommandHandler(
                display=self.display,
                on_user_approach_callback=self.on_touchscreen_user_state_change
            )
            print("✅ 触摸屏命令处理器已初始化")
        except Exception as e:
            print(f"❌ 触摸屏命令处理器初始化失败：{e}")

    def set_ultrasonic_enabled(self, enabled: bool):
        """启用/禁用超声波检测"""
        with self.ultrasonic_lock:
            self.ultrasonic_enabled = enabled
            print(f"🔧 超声波检测: {'启用' if enabled else '禁用'}")

    def on_touchscreen_user_state_change(self, is_present: bool):
        """触摸屏启动会话回调函数"""
        if is_present:
            print("👋 触摸屏检测到用户启动会话！激活系统...")
            # 触摸屏触发时，临时禁用超声波检测避免冲突
            self.set_ultrasonic_enabled(False)
            self.activate_session(source="touchscreen")
        else:
            print("😴 触摸屏停止会话，进入休眠...")
            # 重新启用超声波检测
            self.set_ultrasonic_enabled(True)
            self.clear_display()

    def start(self):
        """启动主循环"""
        self.running = True
        print("🚀 人参菜单AI系统启动中...")

        # 打开显示屏
        if not self.display.open():
            print("⚠️ 显示屏连接失败")

        # 初始化触摸屏命令处理器
        self.init_touchscreen_handler()

        # 启动触摸屏命令监听
        if self.touchscreen_handler:
            self.touchscreen_handler.start_listening()

        # 显示欢迎页
        with self.display_lock:
            self.display.send_nextion_cmd("page start")

        # 设置用户状态改变的回调函数
        def on_ultrasonic_user_state_change(is_present: bool):
            # 检查超声波检测是否启用
            with self.ultrasonic_lock:
                if not self.ultrasonic_enabled:
                    return  # 如果禁用，直接返回
            
            if is_present:
                print("👋 超声波检测到用户！激活系统...")
                self.activate_session(source="ultrasonic")
            else:
                print("😴 超声波检测无用户，进入休眠...")
                self.clear_display()

        # 启动超声波检测监听线程
        ultrasonic_thread = threading.Thread(
            target=self._run_ultrasonic_monitoring,
            args=(on_ultrasonic_user_state_change,),
            daemon=True,
            name="UltrasonicMonitor"
        )
        ultrasonic_thread.start()
        print("✅ 超声波监测线程已启动")

        # 保持主线程运行
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n🛑 正在关闭...")
        finally:
            self.cleanup()

    def _run_ultrasonic_monitoring(self, callback_func):
        """在单独线程中运行超声波检测"""
        last_state = None
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.running:
            try:
                # 检查是否启用
                with self.ultrasonic_lock:
                    if not self.ultrasonic_enabled:
                        time.sleep(0.5)  # 禁用时休眠更长时间
                        continue
                
                # 执行检测
                current_state = self.proximity_detector.is_within_distance()
                
                # 重置错误计数
                consecutive_errors = 0
                
                # 状态变化时触发回调
                if current_state != last_state:
                    last_state = current_state
                    print(f"🔍 超声波状态变化: {current_state}")
                    if callback_func:
                        callback_func(current_state)
                
                time.sleep(0.2)  # 适当延迟防止CPU过度使用
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                consecutive_errors += 1
                print(f"⚠️ 超声波监测异常 ({consecutive_errors}/{max_consecutive_errors}): {e}")
                
                # 连续错误过多时尝试重新初始化
                if consecutive_errors >= max_consecutive_errors:
                    print("🔧 尝试重新初始化超声波传感器...")
                    try:
                        self.proximity_detector.cleanup()
                        time.sleep(1)
                        self.proximity_detector = ProximityDetector()
                        consecutive_errors = 0
                        print("✅ 超声波传感器重新初始化成功")
                    except Exception as reinit_error:
                        print(f"❌ 重新初始化失败: {reinit_error}")
                
                time.sleep(1)  # 发生错误时等待更长时间

    def activate_session(self, source: str = "unknown"):
        """启动会话"""
        with self.session_lock:
            if self.session_active:
                print(f"⚠️ 会话已激活，忽略来自 {source} 的请求")
                return
            self.session_active = True
        
        print(f"🎯 会话激活 (来源: {source})")
        
        # 使用锁保护显示操作
        with self.display_lock:
            self.display.send_nextion_cmd("page read_card_page")
        
        print("💳 等待刷卡...")

    def clear_display(self):
        """休眠时清屏"""
        with self.session_lock:
            self.session_active = False
        
        with self.display_lock:
            if self.display.serial_port:
                try:
                    self.display.send_nextion_cmd("page start")
                    print("🖥️ 显示屏已重置")
                except Exception as e:
                    print(f"⚠️ 清屏失败: {e}")

    def cleanup(self):
        """清理资源"""
        print("🧹 清理资源中...")
        self.proximity_detector.cleanup()

    def stop(self):
        """停止应用"""
        self.running = False

        # 停止触摸屏命令监听
        if self.touchscreen_handler:
            self.touchscreen_handler.stop_listening()

        # 关闭显示屏
        self.display.close()

        print("🛑 系统已停止")


def signal_handler(sig, frame):
    """响应 Ctrl+C 优雅退出"""
    print('\n🛑 收到中断信号')
    if 'app' in globals():
        app.stop()
    sys.exit(0)


def main():
    """程序入口"""
    global app
    app = GinsengMenuApp()
    signal.signal(signal.SIGINT, signal_handler)

    try:
        app.start()
    except Exception as e:
        print(f"❌ 程序异常：{e}")
        import traceback
        traceback.print_exc()
    finally:
        app.stop()


if __name__ == "__main__":
    main()