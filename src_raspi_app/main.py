#!/usr/bin/env python3
"""
人参菜单AI系统主程序
协调所有硬件模块与服务，提供多模态智能用餐体验
"""

import time
import threading
import signal
import sys
from typing import Optional

# 硬件模块
from hardware.ultrasonic import ProximityDetector           # 超声波接近检测
from hardware.audio import recognize_speech_continuous, init_recognizer  # 语音识别
from hardware.camera import capture_image                   # 拍照功能
from hardware.display import ScreenDriver                   # 显示屏驱动
from hardware.rfid import read_uid                     # RFID读卡
from hardware.touchscreen_handler import TouchscreenCommandHandler  # 触摸屏命令处理器

# 服务模块
from services.dish_analyze import analyze_latest_dish       # 菜品分析
from services.llm_service import ask_llm                     # 大模型问答

# 配置模块
from config.base import app, flask
from config.hardware import ultrasonic
from config.model import vision_model, text_model


class GinsengMenuApp:
    """主应用类：协调所有组件运行"""

    def __init__(self):
        self.running = False
        self.user_id = None              # RFID识别后赋值
        self.proximity_detector = ProximityDetector()
        self.display = ScreenDriver(port="/dev/ttyUSB1", baudrate=9600)
        self.touchscreen_handler = None

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

    def on_touchscreen_user_state_change(self, is_present: bool):
        """触摸屏启动会话回调函数"""
        if is_present:
            print("👋 触摸屏检测到用户启动会话！激活系统...")
            self.activate_session()
        else:
            print("😴 触摸屏停止会话，进入休眠...")
            self.clear_display()

    def start(self):
        """启动主循环"""
        self.running = True
        print(" 人参菜单AI系统启动中... ")

        # 打开显示屏
        if not self.display.open():
            print("⚠️ 显示屏连接失败")

        # 初始化触摸屏命令处理器
        self.init_touchscreen_handler()

        # 启动触摸屏命令监听
        if self.touchscreen_handler:
            self.touchscreen_handler.start_listening()

        # 显示欢迎页
        self.display.send_nextion_cmd("page start")

        # 设置用户状态改变的回调函数
        def on_ultrasonic_user_state_change(is_present: bool):
            if is_present:
                print("👋 超声波检测到用户！激活系统...")
                self.activate_session()
            else:
                print("😴 超声波检测无用户，进入休眠...")
                self.clear_display()

        # 启动超声波检测监听线程（与触摸屏命令监听并行运行）
        ultrasonic_thread = threading.Thread(
            target=self._run_ultrasonic_monitoring,
            args=(on_ultrasonic_user_state_change,),
            daemon=True
        )
        ultrasonic_thread.start()

        # 保持主线程运行
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n🛑 正在关闭...")
        finally:
            self.proximity_detector.cleanup()

    def _run_ultrasonic_monitoring(self, callback_func):
        """在单独线程中运行超声波检测"""
        last_state = None
        while self.running:
            try:
                current_state = self.proximity_detector.is_within_distance()
                if current_state != last_state:
                    last_state = current_state
                    if callback_func:
                        callback_func(current_state)
                time.sleep(0.1)  # 小延迟防止CPU过度使用
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"⚠️ 超声波监测异常：{e}")
                time.sleep(0.1)

    def activate_session(self):
        # 靠近后启动会话
        self.display.send_nextion_cmd("page read_card_page")
        print("💳 等待刷卡...")

        # ⏱️ 阻塞等待（30秒超时）
        uid = read_uid(timeout=30)

        # 🔒 强校验：必须是非空字符串
        if not uid or not isinstance(uid, str) or len(uid.strip()) == 0:
            print("❌ 登录失败：未检测到有效卡")
            self.display.send_nextion_cmd("status.txt=\"登录失败\"")
            time.sleep(2)
            return  # ⚠️ 直接退出，不启动语音！

        # ✅ 登录成功
        self.user_id = uid.strip()
        print(f"👤 用户登录：{self.user_id}")
        self.display.send_nextion_cmd("page voice_reco")
        self.display.send_nextion_cmd(f"uid.txt=\"{self.user_id}\"")

    def clear_display(self):
        """休眠时清屏"""
        if self.display.serial_port:
            try:
                self.display.send_nextion_cmd("page start")
            except:
                pass

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
    finally:
        app.stop()


if __name__ == "__main__":
    main()