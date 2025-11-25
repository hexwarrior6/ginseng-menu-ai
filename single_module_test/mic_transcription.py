#!/usr/bin/env python3
import pyaudio
import json
from vosk import Model, KaldiRecognizer
import wave

# 音频参数
RATE = 16000
CHUNK = 8000

def list_audio_devices():
    """列出所有可用的音频设备"""
    p = pyaudio.PyAudio()
    print("\n=== 可用音频设备 ===")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            print(f"设备 {i}: {info['name']}")
            print(f"  - 输入声道: {info['maxInputChannels']}")
            print(f"  - 采样率: {info['defaultSampleRate']}")
    p.terminate()
    print("=====================\n")

def test_microphone(device_index=None):
    """测试麦克风是否有声音输入"""
    p = pyaudio.PyAudio()
    
    print("正在测试麦克风（5秒）...")
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        input_device_index=device_index,
        frames_per_buffer=CHUNK
    )
    
    max_volume = 0
    for i in range(0, int(RATE / CHUNK * 5)):  # 5秒
        data = stream.read(CHUNK, exception_on_overflow=False)
        volume = max(abs(int.from_bytes(data[i:i+2], 'little', signed=True)) 
                    for i in range(0, len(data), 2))
        max_volume = max(max_volume, volume)
        
        # 实时显示音量
        bar = '█' * int(volume / 1000)
        print(f"音量: {volume:6d} {bar}", end='\r')
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    print(f"\n最大音量: {max_volume}")
    if max_volume < 500:
        print("⚠️  警告: 麦克风音量太低或没有检测到声音！")
        return False
    else:
        print("✓ 麦克风工作正常！")
        return True

def setup(device_index=None):
    """初始化Vosk模型"""
    print("正在加载语音识别模型...")
    # 下载模型后，将路径改为你的模型路径
    model = Model("/home/ginseng/myprograms/ginseng-menu-ai/local_models/vosk-model-small-en-us-0.15")  # 或指定完整路径
    rec = KaldiRecognizer(model, RATE)
    rec.SetWords(True)
    print("模型加载完成！")
    return rec

def loop(recognizer, device_index=None):
    """实时语音识别循环"""
    p = pyaudio.PyAudio()
    
    # 打开音频流
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        input_device_index=device_index,
        frames_per_buffer=CHUNK
    )
    
    print("开始监听... (按Ctrl+C停止)")
    print("请对着麦克风说话...\n")
    stream.start_stream()
    
    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            
            # 显示音量指示
            volume = max(abs(int.from_bytes(data[i:i+2], 'little', signed=True)) 
                        for i in range(0, len(data), 2))
            if volume > 1000:
                print(f"🎤 检测到声音 (音量: {volume})", end='\r')
            
            if recognizer.AcceptWaveform(data):
                # 完整句子识别结果
                result = json.loads(recognizer.Result())
                text = result.get('text', '')
                if text:
                    print(f"\n[完整] {text}")
            else:
                # 部分识别结果（实时显示）
                partial = json.loads(recognizer.PartialResult())
                text = partial.get('partial', '')
                if text:
                    print(f"[实时] {text}                    ", end='\r')
                    
    except KeyboardInterrupt:
        print("\n\n停止识别")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == '__main__':
    # 显示所有音频设备
    list_audio_devices()
    
    # 选择设备（如果默认设备不工作，修改这里的数字）
    device_index = None  # None 表示使用默认设备，也可以指定设备号，如 device_index = 1
    
    # 先测试麦克风
    print("步骤1: 测试麦克风")
    if not test_microphone(device_index):
        print("\n请检查:")
        print("1. 麦克风是否正确连接")
        print("2. 是否需要指定设备编号（修改代码中的 device_index）")
        print("3. 运行 'alsamixer' 检查音量设置")
        exit(1)
    
    # 初始化识别器
    print("\n步骤2: 加载语音识别模型")
    recognizer = setup(device_index)
    
    # 开始识别
    print("\n步骤3: 开始语音识别")
    loop(recognizer, device_index)