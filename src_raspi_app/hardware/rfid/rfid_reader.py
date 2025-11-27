import subprocess
import re
import threading
import time
from typing import Callable, Optional


class NFCReader:
    """
    NFC读卡器类，支持启动和停止读卡功能
    """
    def __init__(self):
        self.is_reading = False
        self.reading_thread = None
        self.uid_callback = None
        self.verbose = False

    def start_reading(self, uid_callback: Callable[[str], None], verbose: bool = False):
        """
        启动NFC读卡功能

        Args:
            uid_callback: 读取到UID后的回调函数
            verbose: 是否打印详细信息
        """
        if self.is_reading:
            print("⚠️  NFC读卡已在运行")
            return

        self.uid_callback = uid_callback
        self.verbose = verbose
        self.is_reading = True

        self.reading_thread = threading.Thread(target=self._reading_loop, daemon=True)
        self.reading_thread.start()
        print("💳 NFC读卡已启动")

    def stop_reading(self):
        """停止NFC读卡功能"""
        self.is_reading = False
        if self.reading_thread:
            self.reading_thread.join(timeout=1)
        print("🛑 NFC读卡已停止")

    def _reading_loop(self):
        """持续读取NFC卡片的循环"""
        while self.is_reading:
            try:
                # 使用 nfc-list 读取卡片信息
                result = subprocess.run(
                    ['nfc-list'],
                    capture_output=True,
                    text=True,
                    timeout=1  # Short timeout to allow quick stopping
                )

                # 在输出中查找 UID
                if 'UID' in result.stdout:
                    for line in result.stdout.split('\n'):
                        if 'UID' in line:
                            # 提取 UID 值并去除所有空格
                            uid_match = re.search(r'UID[^:]*:\s*([0-9a-fA-F\s]+)', line)
                            if uid_match:
                                uid = uid_match.group(1).strip().replace(' ', '')
                                if self.verbose:
                                    print(f"读取成功: {uid}")

                                # 调用回调函数
                                if self.uid_callback:
                                    self.uid_callback(uid)

                                # 短暂延迟后继续，避免重复读取同一张卡
                                time.sleep(1)
                                break
                            else:
                                # 如果正则匹配失败，返回整行并去除空格
                                uid = line.split(':', 1)[-1].strip().replace(' ', '')
                                if self.verbose:
                                    print(f"读取成功: {uid}")

                                # 调用回调函数
                                if self.uid_callback:
                                    self.uid_callback(uid)

                                # 短暂延迟后继续，避免重复读取同一张卡
                                time.sleep(1)
                                break

            except subprocess.TimeoutExpired:
                # 超时正常，继续循环
                continue
            except FileNotFoundError:
                if self.verbose:
                    print("错误: 未找到 nfc-list 命令，请确保已安装 libnfc")
                break
            except Exception as e:
                if self.verbose:
                    print(f"读取出错: {e}")
                time.sleep(0.5)  # 错误后短暂延迟再继续

            # 小延迟以降低CPU使用率
            time.sleep(0.1)

    def read_uid(self, timeout=5, verbose=False):
        """
        读取 RFID 卡片的 UID (保持原有功能以向后兼容)

        参数:
            timeout: 超时时间(秒)，默认5秒
            verbose: 是否打印详细信息，默认False

        返回:
            str: 成功时返回 UID 字符串（例如: "04a3b2c1"，无空格）
            None: 未检测到卡片或读取失败
        """
        if verbose:
            print("开始读取卡片，请将卡片靠近读卡器...")

        try:
            # 使用 nfc-list 读取卡片信息
            result = subprocess.run(
                ['nfc-list'],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            # 在输出中查找 UID
            if 'UID' in result.stdout:
                for line in result.stdout.split('\n'):
                    if 'UID' in line:
                        # 提取 UID 值并去除所有空格
                        uid_match = re.search(r'UID[^:]*:\s*([0-9a-fA-F\s]+)', line)
                        if uid_match:
                            uid = uid_match.group(1).strip().replace(' ', '')
                            if verbose:
                                print(f"读取成功: {uid}")
                            return uid
                        else:
                            # 如果正则匹配失败，返回整行并去除空格
                            uid = line.split(':', 1)[-1].strip().replace(' ', '')
                            if verbose:
                                print(f"读取成功: {uid}")
                            return uid

            if verbose:
                print("未检测到卡片")
            return None

        except subprocess.TimeoutExpired:
            if verbose:
                print(f"读取超时（{timeout}秒）")
            return None
        except FileNotFoundError:
            if verbose:
                print("错误: 未找到 nfc-list 命令，请确保已安装 libnfc")
            return None
        except Exception as e:
            if verbose:
                print(f"读取出错: {e}")
            return None


def read_uid(timeout=5, verbose=False):
    """
    读取 RFID 卡片的 UID (保持原有功能以向后兼容)

    参数:
        timeout: 超时时间(秒)，默认5秒
        verbose: 是否打印详细信息，默认False

    返回:
        str: 成功时返回 UID 字符串（例如: "04a3b2c1"，无空格）
        None: 未检测到卡片或读取失败
    """
    reader = NFCReader()
    return reader.read_uid(timeout, verbose)


def read_uid_wait(max_attempts=None, interval=1, verbose=False):
    """
    持续尝试读取 UID，直到读取成功 (保持原有功能以向后兼容)

    参数:
        max_attempts: 最大尝试次数，None 表示无限尝试
        interval: 每次尝试之间的间隔(秒)
        verbose: 是否打印详细信息

    返回:
        str: UID 字符串
    """
    attempts = 0
    while max_attempts is None or attempts < max_attempts:
        uid = read_uid(verbose=verbose)
        if uid:
            return uid
        attempts += 1
        if max_attempts is None or attempts < max_attempts:
            if verbose:
                print(f"重试中... ({attempts})")
            time.sleep(interval)

    return None