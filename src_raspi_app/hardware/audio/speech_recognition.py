#!/usr/bin/env python3
import pyaudio
import json
from vosk import Model, KaldiRecognizer
import time

# 全局配置
RATE = 16000
CHUNK = 8000
MODEL_PATH = "/home/ginseng/myprograms/ginseng-menu-ai/local_models/vosk-model-small-en-us-0.15"

# 全局模型实例（避免重复加载）
_model = None
_recognizer = None

def init_recognizer():
    """初始化识别器（只需调用一次）"""
    global _model, _recognizer
    if _model is None:
        print("正在加载语音识别模型...")
        _model = Model(MODEL_PATH)
        _recognizer = KaldiRecognizer(_model, RATE)
        _recognizer.SetWords(True)
        print("模型加载完成！")
    return _recognizer

def recognize_speech(timeout=10, device_index=None, silence_threshold=1.5, 
                     on_partial=None, on_final=None):
    """
    录音并识别语音，返回识别结果
    
    参数:
        timeout: 最大录音时长（秒），默认10秒
        device_index: 音频设备索引，None表示使用默认设备
        silence_threshold: 静音判断时长（秒），连续静音超过此时间则停止录音
        on_partial: 回调函数，接收实时的部分识别结果 (text: str) -> None
        on_final: 回调函数，接收完整句子的识别结果 (text: str) -> None
    
    返回:
        str: 识别到的文本，如果没有识别到则返回空字符串
    """
    # 确保模型已加载
    recognizer = init_recognizer()
    recognizer.Reset()  # 重置识别器状态
    
    p = pyaudio.PyAudio()
    
    try:
        # 打开音频流
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=CHUNK
        )
        
        print("🎤 开始录音... (请说话)")
        stream.start_stream()
        
        start_time = time.time()
        last_sound_time = time.time()
        recognized_text = ""
        
        while True:
            # 检查超时
            if time.time() - start_time > timeout:
                print("\n⏱️  录音超时")
                break
            
            # 读取音频数据
            data = stream.read(CHUNK, exception_on_overflow=False)
            
            # 计算音量
            volume = max(abs(int.from_bytes(data[i:i+2], 'little', signed=True)) 
                        for i in range(0, len(data), 2))
            
            # 显示音量指示
            if volume > 1000:
                print(f"🔊 音量: {volume}  ", end='\r')
                last_sound_time = time.time()
            
            # 识别音频
            if recognizer.AcceptWaveform(data):
                # 完整句子识别
                result = json.loads(recognizer.Result())
                text = result.get('text', '').strip()
                if text:
                    recognized_text = text
                    print(f"\n✓ 识别到: {text}")
                    last_sound_time = time.time()
                    # 调用完整结果回调
                    if on_final:
                        on_final(text)
            else:
                # 部分识别结果
                partial = json.loads(recognizer.PartialResult())
                text = partial.get('partial', '').strip()
                if text:
                    print(f"[实时] {text}        ", end='\r')
                    # 调用部分结果回调
                    if on_partial:
                        on_partial(text)
            
            # 检查静音时长（如果已经识别到内容）
            if recognized_text and time.time() - last_sound_time > silence_threshold:
                print("\n🔇 检测到静音，结束录音")
                break
        
        # 获取最终结果
        final_result = json.loads(recognizer.FinalResult())
        final_text = final_result.get('text', '').strip()
        if final_text and not recognized_text:
            recognized_text = final_text
            print(f"✓ 最终识别: {final_text}")
        
        stream.stop_stream()
        stream.close()
        
        return recognized_text
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return ""
    finally:
        p.terminate()

def recognize_speech_continuous(callback, device_index=None, stop_callback=None):
    """
    持续识别语音并通过回调函数返回结果
    
    参数:
        callback: 回调函数，接收识别到的文本作为参数
        device_index: 音频设备索引
        stop_callback: 返回True时停止识别的函数
    """
    recognizer = init_recognizer()
    recognizer.Reset()
    
    p = pyaudio.PyAudio()
    
    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=CHUNK
        )
        
        print("🎤 开始持续监听... (按Ctrl+C停止)")
        stream.start_stream()
        
        while True:
            # 检查是否需要停止
            if stop_callback and stop_callback():
                break
            
            data = stream.read(CHUNK, exception_on_overflow=False)
            
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get('text', '').strip()
                if text:
                    callback(text)
            else:
                partial = json.loads(recognizer.PartialResult())
                text = partial.get('partial', '').strip()
                if text:
                    print(f"[实时] {text}        ", end='\r')
        
        stream.stop_stream()
        stream.close()
        
    except KeyboardInterrupt:
        print("\n\n停止识别")
    finally:
        p.terminate()


# 使用示例
if __name__ == '__main__':
    # 方式1: 单次识别（不使用回调）
    print("=== 方式1: 简单用法 ===")
    result = recognize_speech(timeout=10, silence_threshold=2.0)
    if result:
        print(f"\n最终结果: '{result}'")
    else:
        print("\n未识别到语音")
    
    # 方式2: 使用回调获取流式结果
    print("\n=== 方式2: 流式识别（带回调）===")
    
    def on_partial_result(text):
        """实时部分结果回调"""
        print(f"\r[流式] {text}                    ", end='')
    
    def on_final_result(text):
        """完整句子结果回调"""
        print(f"\n[完成] {text}")
    
    result = recognize_speech(
        timeout=10,
        silence_threshold=2.0,
        on_partial=on_partial_result,
        on_final=on_final_result
    )
    print(f"\n最终返回: '{result}'")
    
    # 方式3: 持续识别
    # print("\n=== 方式3: 持续识别 ===")
    # def on_speech(text):
    #     print(f"\n识别到: {text}")
    # 
    # recognize_speech_continuous(on_speech)