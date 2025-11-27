#!/usr/bin/env python3
"""
简单的Edge-TTS测试脚本
在树莓派上将文本转换为语音并播放
"""

import os
import asyncio
from edge_tts import Communicate
import pygame
import tempfile

def text_to_speech(text, voice="en-US-AriaNeural"):
    """
    将文本转换为语音并播放
    
    Args:
        text (str): 要转换的文本
        voice (str): 语音模型，默认为美式英语-Aria
    """
    
    async def generate_audio():
        """异步生成音频文件"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            temp_filename = tmp_file.name
        
        try:
            # 使用Edge-TTS生成语音
            communicate = Communicate(text, voice)
            await communicate.save(temp_filename)
            return temp_filename
        except Exception as e:
            # 如果出错，清理临时文件
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
            raise e
    
    async def play_audio(filename):
        """播放音频文件"""
        # 初始化pygame mixer
        pygame.mixer.init()
        
        try:
            # 加载并播放音频
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            
            # 等待播放完成
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
                
        finally:
            pygame.mixer.quit()
            # 清理临时文件
            if os.path.exists(filename):
                os.unlink(filename)
    
    async def main():
        """主异步函数"""
        print(f"正在生成语音: '{text}'")
        audio_file = await generate_audio()
        print("语音生成完成，开始播放...")
        await play_audio(audio_file)
        print("播放结束")
    
    # 运行异步主函数
    asyncio.run(main())

if __name__ == "__main__":
    # 测试文本
    test_text = "Hello, this is a test of text to speech on Raspberry Pi using Edge TTS."
    
    # 可选的语音列表（如果需要可以切换）
    voices = [
        "en-US-AriaNeural",      # 美式英语 - Aria (女性)
        "en-US-GuyNeural",       # 美式英语 - Guy (男性)
        "en-GB-SoniaNeural",     # 英式英语 - Sonia (女性)
        "en-GB-RyanNeural",      # 英式英语 - Ryan (男性)
    ]
    
    try:
        text_to_speech(test_text, voices[0])
    except Exception as e:
        print(f"发生错误: {e}")
        print("请确保已安装必要的依赖:")
        print("pip install edge-tts pygame")