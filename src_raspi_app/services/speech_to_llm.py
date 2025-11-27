#!/usr/bin/env python3
"""
语音识别结果处理模块
将语音识别结果传递给大模型进行处理
"""

import logging
from typing import Optional
from services.llm_service import ask_llm


def process_speech_to_llm(speech_text: str) -> Optional[str]:
    """
    处理语音识别结果并传递给大模型
    
    Args:
        speech_text: 语音识别得到的文本
        
    Returns:
        str: 大模型处理结果，如果处理失败则返回 None
    """
    if not speech_text or not speech_text.strip():
        logging.warning("语音识别结果为空，跳过大模型处理")
        return None
    
    try:
        # 构造提示词，可以针对具体业务场景进行优化
        prompt = f"User voice input:{speech_text}\nPlease provide appropriate responses or perform corresponding actions based on the user's voice input.(DO NOT over 50 words)"
        logging.info(f"向大模型发送请求: {speech_text}")
        
        # 调用大模型服务
        result = ask_llm(prompt)
        logging.info(f"大模型返回结果: {result}")
        
        return result
    except Exception as e:
        logging.error(f"处理语音识别结果时发生错误: {e}")
        return None


def process_command_speech_to_llm(speech_text: str, command_context: Optional[str] = None) -> Optional[str]:
    """
    处理语音识别结果并传递给大模型，支持命令上下文
    
    Args:
        speech_text: 语音识别得到的文本
        command_context: 命令上下文（可选）
        
    Returns:
        str: 大模型处理结果，如果处理失败则返回 None
    """
    if not speech_text or not speech_text.strip():
        logging.warning("语音识别结果为空，跳过大模型处理")
        return None
    
    try:
        if command_context:
            prompt = f"在{command_context}场景下，用户语音输入: {speech_text}\n请根据用户的语音输入和当前场景提供适当的回复或执行相应的操作。"
        else:
            prompt = f"用户语音输入: {speech_text}\n请根据用户的语音输入提供适当的回复或执行相应的操作。"
        
        logging.info(f"向大模型发送请求 (上下文: {command_context}): {speech_text}")
        
        # 调用大模型服务
        result = ask_llm(prompt)
        logging.info(f"大模型返回结果: {result}")
        
        return result
    except Exception as e:
        logging.error(f"处理语音识别结果时发生错误: {e}")
        return None