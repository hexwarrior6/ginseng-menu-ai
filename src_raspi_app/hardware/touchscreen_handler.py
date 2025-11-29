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
import json
from threading import Event
from hardware.audio.speech_recognition import recognize_speech_continuous_with_stop_flag
from hardware.rfid.rfid_reader import NFCReader
from pipeline.dish_suggest import process_speech_to_llm
from pipeline.dish_enter import capture_and_analyze_dishes
from utils.tts_util import text_to_speech, VOICE_OPTIONS


class TouchscreenCommand(Enum):
    """触摸屏命令枚举"""
    # 命令格式: 55 + [CMD_BYTE] + 0d0a
    VISITOR_MODE = b'\x01'   # 访客模式登录 -> 55 01 0d0a
    START_RECORD = b'\x05'   # 开始录音 -> 55 05 0d0a
    STOP_RECORD = b'\x06'    # 结束录音 -> 55 06 0d0a
    ENABLE_NFC = b'\x03'     # 启动NFC -> 55 03 0d0a
    DISABLE_NFC = b'\x04'    # 关闭NFC -> 55 04 0d0a
    BACK_BUTTON = b'\x02'    # 返回按钮 -> 55 02 0d0a (保留原有功能)
    MENU_PAGE = b'\x07'      # 拍照分析菜品 -> 55 07 0d0a (调整编号)
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

        # NFC相关属性
        self.nfc_reader = NFCReader()
        self.nfc_enabled = False

        # 录音相关属性
        self.is_recording = False
        self.recording_thread = None
        self.stop_recording_event = Event()
        self.recognized_text = ""

        # TTS相关属性
        self.tts_enabled = True  # 默认启用TTS
        self.tts_voice = VOICE_OPTIONS["female_us"]  # 默认使用美式英语女声

        # 用户相关属性
        self.current_user_uid = None

        # 日志相关属性
        self.dish_enter_log_history = []
        self.MAX_LINES = 9  # 最多显示9行
        self.MAX_CHARS_PER_LINE = 32  # 每行最多32个字符

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

    def _split_text_to_lines(self, text: str) -> list:
        """
        将文本分割成适合串口屏显示的行
        
        Args:
            text: 要分割的文本
            
        Returns:
            list: 分割后的行列表
        """
        lines = []
        current_line = ""
        
        for char in text:
            # 如果当前行长度达到限制，或者遇到换行符
            if len(current_line) >= self.MAX_CHARS_PER_LINE or char == '\n':
                if current_line:
                    lines.append(current_line)
                    current_line = ""
                if char == '\n':
                    continue
            
            # 添加字符到当前行
            current_line += char
        
        # 添加最后一行
        if current_line:
            lines.append(current_line)
        
        return lines

    def _truncate_text_to_fit(self, text: str, max_lines: int = None) -> str:
        """
        截断文本以适应显示限制
        
        Args:
            text: 要截断的文本
            max_lines: 最大行数（默认使用类属性）
            
        Returns:
            str: 截断后的文本
        """
        if max_lines is None:
            max_lines = self.MAX_LINES
            
        lines = self._split_text_to_lines(text)
        
        # 如果行数超过限制，只保留最后max_lines行
        if len(lines) > max_lines:
            lines = lines[-max_lines:]
            
        return "\\r".join(lines)

    def _append_dish_enter_log(self, message: str):
        """Append a message with timestamp to the dish enter log and send to display"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"

        # 将消息分割成适合显示的行
        message_lines = self._split_text_to_lines(formatted_message)
        
        # 将分割后的行添加到日志历史
        self.dish_enter_log_history.extend(message_lines)

        # 限制总行数不超过MAX_LINES
        if len(self.dish_enter_log_history) > self.MAX_LINES:
            self.dish_enter_log_history = self.dish_enter_log_history[-self.MAX_LINES:]

        # 将日志历史连接成适合串口屏显示的格式
        # 使用\\r作为换行符（Nextion显示器的换行符）
        display_text = "\\r".join(self.dish_enter_log_history)
        
        # 发送到串口屏
        self.display.send_nextion_cmd(f'dish_enter_log.txt="{display_text}"')

    def _append_dish_enter_log_advanced(self, message: str, auto_split: bool = True):
        """
        高级版本的日志追加函数，提供更多控制选项
        
        Args:
            message: 要添加的消息
            auto_split: 是否自动分割长文本
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if auto_split:
            # 自动分割长消息
            lines_to_add = self._split_text_to_lines(f"[{timestamp}] {message}")
        else:
            # 手动控制，假设消息已经格式化为单行
            formatted_message = f"[{timestamp}] {message}"
            # 确保单行不超过字符限制
            if len(formatted_message) > self.MAX_CHARS_PER_LINE:
                formatted_message = formatted_message[:self.MAX_CHARS_PER_LINE-3] + "..."
            lines_to_add = [formatted_message]
        
        # 添加新行
        self.dish_enter_log_history.extend(lines_to_add)
        
        # 限制总行数
        if len(self.dish_enter_log_history) > self.MAX_LINES:
            self.dish_enter_log_history = self.dish_enter_log_history[-self.MAX_LINES:]
        
        # 更新显示
        display_text = "\\r".join(self.dish_enter_log_history)
        self.display.send_nextion_cmd(f'dish_enter_log.txt="{display_text}"')

    def clear_dish_enter_log(self):
        """清空菜品录入日志"""
        self.dish_enter_log_history = []
        self.display.send_nextion_cmd('dish_enter_log.txt=""')

    def start_listening(self):
        """开始监听触摸屏命令"""
        if not self.display.serial_port or not self.display.serial_port.is_open:
            print("⚠️  串口未打开，无法启动触摸屏监听")
            return

        # 使用屏幕驱动的内置监听机制
        self.display.start_listen(self._handle_received_command)
        print("📱 触摸屏命令监听已启动")

    def stop_listening(self):
        """停止监听触摸屏命令"""
        # 停止屏幕驱动的监听
        self.display.stop_listen()
        print("🛑 触摸屏命令监听已停止")

    def _handle_received_command(self, cmd: bytes):
        """处理接收到的命令（来自屏幕驱动的回调）"""
        print(f"📲 触摸屏收到数据: {cmd.hex()}")
        self._process_command(cmd)

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
        # 重置当前用户uid以启用访客模式
        self.current_user_uid = None
        # 这里可以添加访客模式登录的具体逻辑
        # 例如：显示访客登录页面或执行访客认证流程
        self.display.send_nextion_cmd("page visitor_login")

    def _handle_start_record(self):
        """处理开始录音命令"""
        print("🎤 收到开始录音命令")
        if self.is_recording:
            print("⚠️  录音已在进行中")
            return

        # 重置停止事件
        self.stop_recording_event.clear()
        self.is_recording = True
        self.recognized_text = ""

        # 清空显示屏上的文本区域（如果有的话）
        # 为语音识别文本预留一个文本组件
        self.display.send_nextion_cmd("reco_result.txt=\"\"")  # 清空文本组件reco_result
        self.display.send_nextion_cmd("reco_result.pco=0")

        # 启动录音线程
        self.recording_thread = threading.Thread(target=self._start_recording, daemon=True)
        self.recording_thread.start()

    def _handle_stop_record(self):
        """处理结束录音命令"""
        print("⏹️ 收到结束录音命令")
        if not self.is_recording:
            print("⚠️  没有正在进行的录音")
            return

        # 设置停止标志
        self.stop_recording_event.set()
        self.is_recording = False

        # 等待录音线程结束
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2)

        print(f"📝 最终识别结果: {self.recognized_text}")

        # 获取当前显示的uid（如果有的话）
        current_uid = self._get_current_uid()

        # 如果识别到文本，则将其传递给大模型处理
        if self.recognized_text.strip():
            print("🤖 将语音识别结果交给大模型处理...")
            llm_result = process_speech_to_llm(self.recognized_text, current_uid)
            if llm_result:
                print(f"🤖 大模型处理结果: {llm_result}")
                # 将大模型结果发送到显示屏组件
                escaped_result = llm_result.replace('"', '\\"')  # 转义引号
                self.display.send_nextion_cmd(f'reco_result.txt="{escaped_result}"')
                self.display.send_nextion_cmd("reco_result.pco=64512")
                
                # 新增：使用TTS朗读大模型返回的文本
                self._speak_llm_result(llm_result)
            else:
                print("⚠️ 大模型处理失败或返回结果为空")
        else:
            print("⚠️ 语音识别结果为空，跳过大模型处理")

    def _speak_llm_result(self, text: str):
        """
        使用TTS朗读大模型返回的文本

        Args:
            text: 要朗读的文本
        """
        if not self.tts_enabled:
            print("🔇 TTS功能已禁用，跳过朗读")
            return

        if not text or not text.strip():
            print("⚠️ 要朗读的文本为空")
            return

        try:
            print(f"🔊 开始TTS朗读: {text}")
            # 在单独的线程中运行TTS，避免阻塞主线程
            tts_thread = threading.Thread(
                target=self._run_tts,
                args=(text,),
                daemon=True
            )
            tts_thread.start()
            print("✅ TTS朗读任务已启动")

        except Exception as e:
            print(f"❌ TTS朗读失败: {e}")

    def _speak_analysis_result(self, text: str):
        """
        使用TTS朗读分析结果

        Args:
            text: 要朗读的文本
        """
        if not self.tts_enabled:
            print("🔇 TTS功能已禁用，跳过朗读")
            return

        if not text or not text.strip():
            print("⚠️ 要朗读的文本为空")
            return

        try:
            print(f"🔊 开始TTS朗读分析结果: {text}")
            # 在单独的线程中运行TTS，避免阻塞主线程
            tts_thread = threading.Thread(
                target=self._run_tts,
                args=(text,),
                daemon=True
            )
            tts_thread.start()
            print("✅ TTS朗读任务已启动")

        except Exception as e:
            print(f"❌ TTS朗读失败: {e}")

    def _run_tts(self, text: str):
        """
        在单独线程中运行TTS
        
        Args:
            text: 要朗读的文本
        """
        try:
            text_to_speech(text, self.tts_voice)
            print("✅ TTS朗读完成")
        except Exception as e:
            print(f"❌ TTS执行错误: {e}")

    def _get_current_uid(self) -> str:
        """从显示屏获取当前uid"""
        try:
            return getattr(self, 'current_user_uid', None)
        except Exception as e:
            print(f"⚠️ 获取当前uid时发生错误: {e}")
            return None

    def _start_recording(self):
        """内部录音函数，在单独线程中运行"""
        try:
            def on_partial(text):
                """处理部分识别结果（流式）"""
                print(f"[流式识别] {text}")
                # 将部分识别结果显示到串口屏上
                escaped_text = text.replace('"', '\\"')  # 转义引号
                self.display.send_nextion_cmd(f'reco_result.txt="{escaped_text}"')
                self.display.send_nextion_cmd("reco_result.pco=0")

            def on_final(text):
                """处理完整识别结果"""
                print(f"[完整识别] {text}")
                # 将完整结果更新到串口屏
                escaped_text = text.replace('"', '\\"')  # 转义引号
                self.display.send_nextion_cmd(f'reco_result.txt="{escaped_text}"')
                self.display.send_nextion_cmd("reco_result.pco=0")
                # 保存识别结果
                self.recognized_text = text

            # 开始持续录音，直到停止标志被设置
            recognize_speech_continuous_with_stop_flag(
                stop_flag=self.stop_recording_event,
                on_partial=on_partial,
                on_final=on_final
            )

        except Exception as e:
            print(f"❌ 录音过程中出现错误: {e}")
        finally:
            self.is_recording = False
            print("🎙️ 录音结束")

    def _handle_enable_nfc(self):
        """处理启动NFC命令"""
        print("🔛 收到启动NFC命令")
        if not self.nfc_enabled:
            # 启动NFC读卡
            self.nfc_reader.start_reading(self._on_uid_read, verbose=True)
            self.nfc_enabled = True
            print("✅ NFC读卡已启动")
        else:
            print("⚠️ NFC读卡已在运行")

    def _handle_disable_nfc(self):
        """处理关闭NFC命令"""
        print("🔚 收到关闭NFC命令")
        if self.nfc_enabled:
            # 停止NFC读卡
            self.nfc_reader.stop_reading()
            self.nfc_enabled = False
            print("✅ NFC读卡已停止")
        else:
            print("⚠️ NFC读卡当前未运行")

    def _on_uid_read(self, uid: str):
        """NFC读取到UID的回调函数"""
        print(f"👤 用户登录：{uid}")
        # 发送串口屏指令跳转到dish_suggest页面，并设置uid.txt
        self.display.send_nextion_cmd("page dish_suggest")
        self.display.send_nextion_cmd(f"uid.txt=\"{uid}\"")
        # Store the uid in an instance variable for later use
        self.current_user_uid = uid
        # 在另一个线程中停止NFC读卡，避免在读卡线程内停止自身
        stop_thread = threading.Thread(target=self._stop_nfc_safely, daemon=True)
        stop_thread.start()

    def _stop_nfc_safely(self):
        """安全停止NFC读卡功能"""
        # 停止NFC读卡，直到再次被启用
        self.nfc_reader.stop_reading()
        self.nfc_enabled = False
        print("✅ NFC读卡已自动停止，等待手动重启")

    def _handle_back_command(self):
        """处理返回命令"""
        print("🔙 收到返回命令")
        self.display.send_nextion_cmd("page 0")

    def _handle_menu_command(self):
        """处理拍照分析菜品命令"""
        print("📸 收到拍照分析菜品命令")
        
        # 清空日志
        self.clear_dish_enter_log()
        
        # 发送带时间戳的英文日志到串口屏
        self._append_dish_enter_log("Starting dish analysis...")

        try:
            # 调用dish_enter.py中的功能进行拍照
            print("📷 Capturing image...")
            self._append_dish_enter_log("Capturing image...")

            result = capture_and_analyze_dishes()

            if result and result.get('dishes'):
                # 拍摄成功
                self._append_dish_enter_log("Image captured successfully!")

                # 开始大模型分析
                self._append_dish_enter_log("Starting AI analysis...")

                dish_count = len(result.get('dishes', []))

                # 显示具体的菜名
                dish_names = [dish.get('name', 'Unknown') for dish in result.get('dishes', [])]
                dish_names_str = ", ".join(dish_names)
                
                # 直接显示菜名，不做截断处理
                self._append_dish_enter_log(f"Found {dish_count} dishes:")
                for dish_name in dish_names:
                    self._append_dish_enter_log(f"- {dish_name}")

                success_msg = f"Analysis complete! Found {dish_count} dishes."
                print(f"🎉 {success_msg}")

                # 发送成功消息到串口屏
                self._append_dish_enter_log(success_msg)

            else:
                error_msg = "Analysis failed or no dishes found."
                print(f"❌ {error_msg}")

                # 发送错误消息到串口屏
                self._append_dish_enter_log(error_msg)

        except Exception as e:
            error_msg = f"Error during dish analysis: {str(e)}"
            print(f"❌ {error_msg}")

            # 发送错误消息到串口屏
            self._append_dish_enter_log(error_msg)
            
    def _handle_analyze_command(self):
        """处理分析命令"""
        print("🔍 收到分析命令")

        # 导入plate_analyze模块
        from pipeline.plate_analyze import capture_and_identify_dishes_for_user

        # 获取当前用户的UID，如果没有则传入None
        current_uid = self.current_user_uid or "Anonymous"
        self.display.send_nextion_cmd('identify_ret.txt="Capturing image..."')

        # 调用plate_analyze模块进行拍摄和分析
        try:
            print(f"📸 开始菜品拍照和分析，用户ID: {current_uid}")

            # 调用plate_analyze模块的函数
            result = capture_and_identify_dishes_for_user(current_uid) if current_uid else capture_and_identify_dishes_for_user(None)

            if result:
                print(f"✅ 分析结果: {result}")

                # 将结果发送到串口屏的identify_ret文本框
                escaped_result = result.replace('"', '\\"')  # 转义引号
                self.display.send_nextion_cmd(f'identify_ret.txt="{escaped_result}"')

                # 使用TTS朗读结果（类似于菜品推荐逻辑）
                self._speak_analysis_result(result)
            else:
                print("⚠️ 分析结果为空")
                self.display.send_nextion_cmd('identify_ret.txt="分析失败，请重试"')

        except Exception as e:
            print(f"❌ 菜品分析过程中出现错误: {e}")
            error_msg = "菜品分析失败，请重试"
            self.display.send_nextion_cmd(f'identify_ret.txt="{error_msg}"')
            # 使用TTS朗读错误信息
            self._speak_analysis_result(error_msg)

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

    def enable_tts(self, enabled: bool = True):
        """启用或禁用TTS功能"""
        self.tts_enabled = enabled
        status = "启用" if enabled else "禁用"
        print(f"🔊 TTS功能已{status}")

    def set_tts_voice(self, voice_option: str):
        """设置TTS语音选项"""
        if voice_option in VOICE_OPTIONS:
            self.tts_voice = VOICE_OPTIONS[voice_option]
            print(f"🔊 TTS语音已设置为: {voice_option}")
        else:
            print(f"⚠️ 未知的TTS语音选项: {voice_option}")


def create_default_command_handler(display: ScreenDriver, on_user_approach_callback: Callable = None):
    """
    创建默认的触摸屏命令处理器

    Args:
        display: 显示屏驱动实例
        on_user_approach_callback: 用户接近回调函数
    """
    return TouchscreenCommandHandler(display, on_user_approach_callback)