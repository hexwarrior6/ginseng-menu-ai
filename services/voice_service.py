import os
import speech_recognition as sr
from pydub import AudioSegment
from typing import Optional
import io
import wave
import tempfile
import sys

class VoiceService:
    """语音服务类，处理语音识别和语音合成功能"""
    
    def __init__(self):
        # Explicitly set the path to ffmpeg if not in system PATH
        ffmpeg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  'ffmpeg-8.0-essentials_build', 'bin')
        if os.path.exists(ffmpeg_path):
            os.environ["PATH"] += os.pathsep + ffmpeg_path
            AudioSegment.ffmpeg = os.path.join(ffmpeg_path, "ffmpeg.exe")
            AudioSegment.ffprobe = os.path.join(ffmpeg_path, "ffprobe.exe")
        
        # 初始化语音识别器
        self.recognizer = sr.Recognizer()
        
        # 支持的音频格式
        self.supported_formats = ['.wav', '.mp3', '.flac', '.aac', '.m4a']
    
    def recognize_speech_from_audio(self, audio_file_path: str) -> Optional[str]:
        """
        从音频文件中识别语音内容
        
        Args:
            audio_file_path (str): 音频文件路径
            
        Returns:
            Optional[str]: 识别出的文本内容，如果识别失败则返回None
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"音频文件不存在: {audio_file_path}")
            
            # 获取文件扩展名
            _, ext = os.path.splitext(audio_file_path)
            
            # 如果不是WAV格式，需要转换
            if ext.lower() != '.wav':
                audio_file_path = self._convert_to_wav(audio_file_path)
            
            # 使用SpeechRecognition库识别语音
            with sr.AudioFile(audio_file_path) as source:
                # 调整环境噪声
                self.recognizer.adjust_for_ambient_noise(source)
                
                # 读取音频数据
                audio_data = self.recognizer.record(source)
                
                # 识别语音（使用Google Web Speech API）
                text = self.recognizer.recognize_google(audio_data, language="zh-CN")
                return text
                
        except sr.UnknownValueError:
            print("语音识别失败：无法理解音频内容")
            return None
        except sr.RequestError as e:
            print(f"语音识别服务错误: {e}")
            return None
        except Exception as e:
            print(f"语音识别过程中发生错误: {e}")
            return None
        finally:
            # 清理临时转换的WAV文件
            if ext.lower() != '.wav' and 'temp_wav_path' in locals():
                try:
                    os.remove(temp_wav_path)
                except:
                    pass
    
    def recognize_speech_from_microphone(self, timeout: int = 5) -> Optional[str]:
        """
        从麦克风实时识别语音内容
        
        Args:
            timeout (int): 监听超时时间（秒）
            
        Returns:
            Optional[str]: 识别出的文本内容，如果识别失败则返回None
        """
        try:
            # 初始化麦克风
            with sr.Microphone() as source:
                print("请说话...")
                # 调整环境噪声
                self.recognizer.adjust_for_ambient_noise(source)
                
                # 监听音频输入
                audio_data = self.recognizer.listen(source, timeout=timeout)
                
                # 识别语音（使用Google Web Speech API）
                text = self.recognizer.recognize_google(audio_data, language="zh-CN")
                return text
                
        except sr.UnknownValueError:
            print("语音识别失败：无法理解音频内容")
            return None
        except sr.RequestError as e:
            print(f"语音识别服务错误: {e}")
            return None
        except Exception as e:
            print(f"麦克风语音识别过程中发生错误: {e}")
            return None
    
    def _convert_to_wav(self, audio_file_path: str) -> str:
        """
        将音频文件转换为WAV格式
        
        Args:
            audio_file_path (str): 原始音频文件路径
            
        Returns:
            str: 转换后的WAV文件路径
        """
        try:
            # 使用pydub加载音频文件
            audio = AudioSegment.from_file(audio_file_path)
            
            # 创建临时WAV文件
            temp_wav_fd, temp_wav_path = tempfile.mkstemp(suffix='.wav')
            
            # 转换为WAV格式并保存
            audio.export(temp_wav_path, format="wav")
            
            # 关闭临时文件描述符
            os.close(temp_wav_fd)
            
            return temp_wav_path
        except Exception as e:
            raise Exception(f"音频格式转换失败: {e}")
    
    def validate_audio_file(self, audio_file_path: str) -> bool:
        """
        验证音频文件是否有效
        
        Args:
            audio_file_path (str): 音频文件路径
            
        Returns:
            bool: 文件是否有效
        """
        try:
            if not os.path.exists(audio_file_path):
                return False
                
            _, ext = os.path.splitext(audio_file_path)
            if ext.lower() not in self.supported_formats:
                return False
                
            # 尝试加载音频文件
            AudioSegment.from_file(audio_file_path)
            return True
        except:
            return False