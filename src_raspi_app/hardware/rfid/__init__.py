"""
RFID 读卡器模块

提供 NFC/RFID 卡片 UID 读取功能
"""

from .rfid_reader import read_uid, read_uid_wait

__all__ = ['read_uid', 'read_uid_wait']
__version__ = '1.0.0'
