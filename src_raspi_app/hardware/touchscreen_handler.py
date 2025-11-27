#!/usr/bin/env python3
"""
触摸屏命令处理模块
处理来自串口屏的各种十六进制指令
"""

import time
from typing import Callable, Dict, Any
from enum import Enum
import threading
from hardware.display import ScreenDriver


class TouchscreenCommand(Enum):
    """触摸屏命令枚举"""
    # 命令格式: 55 + [CMD_BYTE] + 0d0a
    VISITOR_MODE = b'\x01'   # 访客模式登录 -> 55 01 0d0a
    START_RECORD = b'\x05'   # 开始录音 -> 55 05 0d0a
    STOP_RECORD = b'\x06'    # 结束录音 -> 55 06 0d0a
    ENABLE_NFC = b'\x03'     # 启动NFC -> 55 03 0d0a
    DISABLE_NFC = b'\x04'    # 关闭NFC -> 55 04 0d0a
    BACK_BUTTON = b'\x02'    # 返回按钮 -> 55 02 0d0a (保留原有功能)
    MENU_PAGE = b'\x07'      # 菜单页面 -> 55 07 0d0a (调整编号)
    ANALYZE_BUTTON = b'\x08' # 分析按钮 -> 55 08 0d0a (调整编号)
    RFID_PAGE = b'\x09'      # 刷卡页面 -> 55 09 0d0a (调整编号)


class TouchscreenCommandHandler:
    """触摸屏命令处理器"""

    def __init__(self, display: ScreenDriver, on_user_approach_callback: Callable = None):
        """
        初始化命令处理器

        Args:
            display: 显示屏驱动实例
            on_user_approach_callback: 用户接近回调函数（用于启动会话）
        """
        self.display = display
        self.on_user_approach_callback = on_user_approach_callback
        self.is_listening = False
        self.listen_thread = None
        self._lock = threading.Lock()

        # 命令处理映射表 - 更新为新的命令映射
        self.command_handlers = {
            TouchscreenCommand.VISITOR_MODE.value: self._handle_visitor_mode,
            TouchscreenCommand.START_RECORD.value: self._handle_start_record,
            TouchscreenCommand.STOP_RECORD.value: self._handle_stop_record,
            TouchscreenCommand.ENABLE_NFC.value: self._handle_enable_nfc,
            TouchscreenCommand.DISABLE_NFC.value: self._handle_disable_nfc,
            TouchscreenCommand.BACK_BUTTON.value: self._handle_back_command,
            TouchscreenCommand.MENU_PAGE.value: self._handle_menu_command,
            TouchscreenCommand.ANALYZE_BUTTON.value: self._handle_analyze_command,
            TouchscreenCommand.RFID_PAGE.value: self._handle_rfid_page_command,
        }

    def start_listening(self):
        """开始监听触摸屏命令"""
        if self.is_listening:
            print("⚠️  触摸屏监听已在运行")
            return

        if not self.display.serial_port or not self.display.serial_port.is_open:
            print("⚠️  串口未打开，无法启动触摸屏监听")
            return

        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        print("📱 触摸屏命令监听已启动")

    def stop_listening(self):
        """停止监听触摸屏命令"""
        self.is_listening = False
        if self.listen_thread:
            self.listen_thread.join(timeout=1)
        print("🛑 触摸屏命令监听已停止")

    def _listen_loop(self):
        """监听循环"""
        buffer = b''
        while self.is_listening:
            try:
                with self._lock:
                    # 检查串口是否有数据可读
                    if self.display.serial_port.in_waiting > 0:
                        data = self.display.serial_port.read(self.display.serial_port.in_waiting)
                    else:
                        data = b''

                if data:
                    buffer += data
                    print(f"📲 触摸屏收到数据: {data.hex()}")

                    # 尝试处理完整的指令（根据结束符 0d0a 分割）
                    while b'\x0d\x0a' in buffer:
                        # 寻找以 0d0a 结尾的完整数据包
                        parts = buffer.split(b'\x0d\x0a', 1)

                        # 假设整个数据包以 55 开头
                        packet_data = parts[0]

                        # 检查数据包是否以 55 开头（协议头）
                        if packet_data.startswith(b'\x55'):
                            # 处理命令（去掉头部的 55）
                            cmd_payload = packet_data[1:]
                            self._process_command(cmd_payload)
                        else:
                            # 如果不是以 55 开头，可能发生了粘包或数据错乱
                            print(f"⚠️ 无效数据包头: {packet_data.hex()}")

                        # 保留剩余数据
                        buffer = parts[1] if len(parts) > 1 else b''

            except Exception as e:
                print(f"⚠️  触摸屏监听异常：{e}")

            time.sleep(0.05)  # 降低CPU占用

    def _process_command(self, command: bytes):
        """处理接收到的命令"""
        print(f"⚙️  处理命令: {command.hex()}")

        # 尝试匹配预定义命令
        handler = self.command_handlers.get(command)
        if handler:
            try:
                handler()
            except Exception as e:
                print(f"❌ 命令处理错误: {e}")
        else:
            # 处理未定义的命令
            self._handle_unknown_command(command)

    def _handle_visitor_mode(self):
        """处理访客模式登录命令"""
        print("👤 收到访客模式登录命令")
        # 这里可以添加访客模式登录的具体逻辑
        # 例如：显示访客登录页面或执行访客认证流程
        self.display.send_nextion_cmd("page visitor_login")

    def _handle_start_record(self):
        """处理开始录音命令"""
        print("🎤 收到开始录音命令")
        # 这里可以添加开始录音的具体逻辑
        # 例如：启动录音设备，开始录制音频
        # 可以调用相关的录音模块函数

    def _handle_stop_record(self):
        """处理结束录音命令"""
        print("⏹️ 收到结束录音命令")
        # 这里可以添加结束录音的具体逻辑
        # 例如：停止录音设备，保存录音文件
        # 可以调用相关的录音模块函数

    def _handle_enable_nfc(self):
        """处理启动NFC命令"""
        print("🔛 收到启动NFC命令")
        # 这里可以添加启动NFC的具体逻辑
        # 例如：启用NFC读卡器，开始监听NFC卡片
        # 可以调用相关的NFC模块函数

    def _handle_disable_nfc(self):
        """处理关闭NFC命令"""
        print("🔚 收到关闭NFC命令")
        # 这里可以添加关闭NFC的具体逻辑
        # 例如：禁用NFC读卡器，停止监听NFC卡片
        # 可以调用相关的NFC模块函数

    def _handle_back_command(self):
        """处理返回命令"""
        print("🔙 收到返回命令")
        self.display.send_nextion_cmd("page 0")

    def _handle_menu_command(self):
        """处理菜单命令"""
        print("📋 收到菜单命令")
        self.display.send_nextion_cmd("page menu")

    def _handle_analyze_command(self):
        """处理分析命令"""
        print("🔍 收到分析命令")
        # 可以触发拍照分析流程
        self.display.send_nextion_cmd("page analyze")

    def _handle_rfid_page_command(self):
        """处理进入刷卡页面命令"""
        print("💳 收到刷卡页面命令")
        self.display.send_nextion_cmd("page read_card_page")

    def _handle_unknown_command(self, command: bytes):
        """处理未知命令"""
        print(f"❓ 未知命令: {command.hex()}")
        # 根据实际情况扩展处理逻辑

    def register_custom_command(self, command_hex: bytes, handler_func: Callable):
        """注册自定义命令处理器"""
        with self._lock:
            self.command_handlers[command_hex] = handler_func
            print(f"✅ 已注册自定义命令: {command_hex.hex()}")


def create_default_command_handler(display: ScreenDriver, on_user_approach_callback: Callable = None):
    """
    创建默认的触摸屏命令处理器

    Args:
        display: 显示屏驱动实例
        on_user_approach_callback: 用户接近回调函数
    """
    return TouchscreenCommandHandler(display, on_user_approach_callback)