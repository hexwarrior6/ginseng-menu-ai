# 树莓派语音输入功能使用说明

## 功能概述

本系统支持通过树莓派麦克风实时采集语音数据，通过WebSocket传输到服务器，进行语音识别并自动生成AI推荐。

## 工作流程

1. 前端点击"开始录音"按钮
2. 树莓派通过WebSocket连接到服务器
3. 树莓派开始采集麦克风音频数据并实时发送
4. 服务器接收音频数据并进行语音识别
5. 识别结果自动传递给大模型生成推荐
6. 前端实时显示识别结果和推荐建议

## 后端配置

### 1. 安装依赖

```bash
pip install flask-socketio pydub
```

### 2. 启动服务器

服务器会自动启动WebSocket服务，监听在 `http://localhost:5000`

## 前端使用

1. 打开前端页面
2. 进入语音测试页面（会自动连接到服务器）
3. 点击"开始录音"按钮
4. 树莓派开始发送音频数据
5. 等待识别和推荐结果

## 树莓派端配置

### 1. 安装依赖

```bash
pip install python-socketio pyaudio
```

### 2. 配置服务器地址

编辑 `raspberry_pi_example.py`，修改 `SERVER_URL` 为实际的服务器地址：

```python
SERVER_URL = 'http://your-server-ip:5000'
```

### 3. 运行树莓派客户端

```bash
python raspberry_pi_example.py
```

### 4. 树莓派端代码说明

树莓派需要：
- 连接到WebSocket服务器
- 监听 `start_recording` 事件确认
- 开始采集麦克风音频
- 将音频数据编码为base64
- 通过 `audio_chunk` 事件发送音频数据
- 监听 `stop_recording` 事件停止采集

## WebSocket事件说明

### 客户端（树莓派/前端）发送的事件

- `start_recording`: 开始录音
- `audio_chunk`: 发送音频数据块
  ```json
  {
    "audio": "base64_encoded_audio_data"
  }
  ```
- `stop_recording`: 停止录音

### 服务器发送的事件

- `connected`: 连接成功
- `recording_started`: 开始录音确认
- `recording_stopped`: 停止录音确认
- `processing`: 正在处理音频
- `transcript`: 语音识别结果
  ```json
  {
    "status": "success",
    "text": "识别出的文字",
    "message": "语音识别成功"
  }
  ```
- `recommending`: 正在生成推荐
- `recommendations`: 推荐结果
  ```json
  {
    "status": "success",
    "recommendations": [
      {
        "id": "dish_id",
        "name": "菜品名称",
        "reason": "推荐理由"
      }
    ],
    "total_count": 3
  }
  ```
- `error`: 错误信息

## 音频格式要求

- 格式: WAV
- 采样率: 44100 Hz
- 声道: 单声道
- 位深: 16位

## 注意事项

1. 确保树莓派和服务器在同一网络或可以互相访问
2. 树莓派需要安装并配置好麦克风驱动
3. 音频数据需要实时发送，建议每100ms发送一次
4. 服务器会自动处理音频格式转换
5. 语音识别使用Google Web Speech API，需要网络连接

## 故障排查

1. **连接失败**: 检查服务器地址和端口是否正确，防火墙是否开放
2. **音频无法识别**: 检查麦克风是否正常工作，音频格式是否正确
3. **推荐失败**: 检查大模型API配置（DEEPSEEK_API_KEY）是否正确
4. **前端无法显示**: 检查浏览器控制台错误信息，确认WebSocket连接正常


