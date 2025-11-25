"""
树莓派端语音数据发送示例代码

此文件展示了如何在树莓派上通过WebSocket向服务器发送麦克风音频数据

安装依赖:
    pip install python-socketio pyaudio

注意: 需要根据实际情况调整服务器地址和端口
"""

import socketio
import pyaudio
import base64
import time
import threading

# 配置
SERVER_URL = 'http://localhost:5000'  # 修改为实际的服务器地址
CHUNK = 1024  # 音频块大小
FORMAT = pyaudio.paInt16  # 音频格式
CHANNELS = 1  # 单声道
RATE = 44100  # 采样率

# 创建Socket.IO客户端
sio = socketio.Client()

# 全局变量
is_recording = False
audio_stream = None
p = None

@sio.event
def connect():
    """连接成功回调"""
    print('已连接到服务器')

@sio.event
def disconnect():
    """断开连接回调"""
    print('已断开连接')

@sio.event
def connected(data):
    """服务器确认连接"""
    print(f'服务器确认: {data}')

@sio.event
def recording_started(data):
    """开始录音确认"""
    print(f'开始录音: {data}')
    global is_recording
    is_recording = True

@sio.event
def recording_stopped(data):
    """停止录音确认"""
    print(f'停止录音: {data}')
    global is_recording
    is_recording = False

@sio.event
def transcript(data):
    """收到识别结果"""
    print(f'识别结果: {data.get("text", "")}')

@sio.event
def recommendations(data):
    """收到推荐结果"""
    print(f'推荐结果: {data}')

@sio.event
def error(data):
    """错误处理"""
    print(f'错误: {data}')

def send_audio_stream():
    """发送音频流"""
    global is_recording, audio_stream, p
    
    # 初始化PyAudio
    p = pyaudio.PyAudio()
    
    # 打开音频流
    audio_stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    
    print('开始录音...')
    
    try:
        while is_recording:
            # 读取音频数据
            audio_data = audio_stream.read(CHUNK, exception_on_overflow=False)
            
            # 将音频数据编码为base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # 发送音频块
            sio.emit('audio_chunk', {'audio': audio_base64})
            
            # 控制发送频率，避免过快
            time.sleep(0.1)
            
    except Exception as e:
        print(f'发送音频流错误: {e}')
    finally:
        # 清理资源
        if audio_stream:
            audio_stream.stop_stream()
            audio_stream.close()
        if p:
            p.terminate()
        print('录音结束')

def main():
    """主函数"""
    try:
        # 连接到服务器
        print(f'正在连接到服务器: {SERVER_URL}')
        sio.connect(SERVER_URL)
        
        # 等待连接建立
        time.sleep(1)
        
        # 开始录音
        print('发送开始录音信号...')
        sio.emit('start_recording')
        
        # 启动音频流发送线程
        audio_thread = threading.Thread(target=send_audio_stream)
        audio_thread.daemon = True
        audio_thread.start()
        
        # 等待用户输入停止
        input('按回车键停止录音...\n')
        
        # 停止录音
        print('发送停止录音信号...')
        sio.emit('stop_recording')
        
        # 等待处理完成
        time.sleep(5)
        
        # 断开连接
        sio.disconnect()
        
    except Exception as e:
        print(f'错误: {e}')
    finally:
        if sio.connected:
            sio.disconnect()

if __name__ == '__main__':
    main()

