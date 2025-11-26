"""
Audio 模块
提供语音识别功能
"""

from .speech_recognition import (
    recognize_speech,
    recognize_speech_continuous,
    init_recognizer,
    RATE,
    CHUNK,
    MODEL_PATH
)

__all__ = [
    'recognize_speech',
    'recognize_speech_continuous',
    'init_recognizer',
    'RATE',
    'CHUNK',
    'MODEL_PATH'
]

__version__ = '1.0.0'
__author__ = 'HexWarrior6'