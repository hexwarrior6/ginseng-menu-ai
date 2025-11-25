from flask import Blueprint, request, jsonify, current_app
from flask_socketio import emit
import os
import tempfile
import base64
import io
import threading
from services.voice_service import VoiceService
from services.recommendation_service import RecommendationService

# 创建蓝图
bp = Blueprint('voice', __name__, url_prefix='/api/voice')

# 初始化服务
voice_service = VoiceService()
recommendation_service = RecommendationService()

# 存储每个连接的音频数据
audio_buffers = {}

@bp.route('/recognize', methods=['POST'])
def recognize_speech():
    """
    语音识别接口
    
    ---
    tags:
      - 语音服务
    summary: 语音识别
    description: 上传音频文件进行语音识别
    parameters:
      - name: audio
        in: formData
        type: file
        description: 音频文件（支持wav, mp3, flac, aac, m4a格式）
        required: true
    responses:
      200:
        description: 成功识别语音内容
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            text:
              type: string
              example: "我想点一个宫保鸡丁"
      400:
        description: 请求参数错误
      500:
        description: 服务器内部错误
    """
    try:
        # 检查是否有上传文件
        if 'audio' not in request.files:
            return jsonify({"success": False, "error": "请上传音频文件"}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"success": False, "error": "请选择有效的音频文件"}), 400
        
        # 保存上传的音频文件到临时位置
        temp_dir = current_app.config.get('TEMP_IMAGE_PATH', './temp_images/')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # 创建临时文件
        temp_fd, temp_path = tempfile.mkstemp(
            suffix=os.path.splitext(audio_file.filename)[1],
            dir=temp_dir
        )
        
        try:
            # 保存文件
            audio_file.save(temp_path)
            os.close(temp_fd)
            
            # 验证音频文件
            if not voice_service.validate_audio_file(temp_path):
                return jsonify({"success": False, "error": "不支持的音频格式或文件损坏"}), 400
            
            # 进行语音识别
            recognized_text = voice_service.recognize_speech_from_audio(temp_path)
            
            if recognized_text:
                return jsonify({
                    "success": True, 
                    "text": recognized_text
                }), 200
            else:
                return jsonify({
                    "success": False, 
                    "error": "无法识别音频内容，请确保音频清晰且包含语音"
                }), 400
                
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        print(f"语音识别异常: {e}")
        return jsonify({"success": False, "error": f"语音识别异常: {str(e)}"}), 500

@bp.route('/recognize/microphone', methods=['POST'])
def recognize_speech_from_microphone():
    """
    实时语音识别接口（需要服务器有麦克风设备）
    
    ---
    tags:
      - 语音服务
    summary: 实时语音识别
    description: 通过服务器麦克风进行实时语音识别
    parameters:
      - name: timeout
        in: query
        type: integer
        description: 监听超时时间（秒），默认5秒
        required: false
        default: 5
    responses:
      200:
        description: 成功识别语音内容
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            text:
              type: string
              example: "我想点一个宫保鸡丁"
      400:
        description: 请求参数错误
      500:
        description: 服务器内部错误
    """
    try:
        # 获取超时参数
        timeout = request.args.get('timeout', default=5, type=int)
        
        # 进行实时语音识别
        recognized_text = voice_service.recognize_speech_from_microphone(timeout)
        
        if recognized_text:
            return jsonify({
                "success": True, 
                "text": recognized_text
            }), 200
        else:
            return jsonify({
                "success": False, 
                "error": "无法识别语音内容，请确保麦克风工作正常且有语音输入"
            }), 400
            
    except Exception as e:
        print(f"实时语音识别异常: {e}")
        return jsonify({"success": False, "error": f"实时语音识别异常: {str(e)}"}), 500

# 健康检查端点
@bp.route('/health', methods=['GET'])
def voice_health_check():
    """
    语音服务健康检查
    
    ---
    tags:
      - 语音服务
    summary: 健康检查
    description: 检查语音服务是否正常运行
    responses:
      200:
        description: 服务正常
        schema:
          type: object
          properties:
            status:
              type: string
              example: "healthy"
      500:
        description: 服务异常
    """
    return jsonify({"status": "healthy", "service": "voice recognition"}), 200

# WebSocket事件处理函数
def register_socketio_events(socketio):
    """注册WebSocket事件处理器"""
    
    @socketio.on('connect')
    def handle_connect():
        """客户端连接时调用"""
        print(f'客户端已连接: {request.sid}')
        audio_buffers[request.sid] = []
        emit('connected', {'status': 'connected', 'message': '已连接到语音服务'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """客户端断开连接时调用"""
        print(f'客户端已断开: {request.sid}')
        if request.sid in audio_buffers:
            del audio_buffers[request.sid]
    
    @socketio.on('start_recording')
    def handle_start_recording():
        """开始录音"""
        print(f'开始录音: {request.sid}')
        audio_buffers[request.sid] = []
        emit('recording_started', {'status': 'recording', 'message': '开始接收语音数据'})
    
    @socketio.on('audio_chunk')
    def handle_audio_chunk(data):
        """接收音频数据块（从树莓派）"""
        try:
            # 接收base64编码的音频数据
            if 'audio' in data:
                audio_data = base64.b64decode(data['audio'])
                audio_buffers[request.sid].append(audio_data)
                
                # 发送确认
                emit('audio_received', {'status': 'ok'})
        except Exception as e:
            print(f'处理音频数据块错误: {e}')
            emit('error', {'message': f'处理音频数据失败: {str(e)}'})
    
    @socketio.on('stop_recording')
    def handle_stop_recording():
        """停止录音并处理"""
        print(f'停止录音: {request.sid}')
        
        # 先发送停止录音确认
        emit('recording_stopped', {'status': 'stopped', 'message': '正在处理音频...'})
        
        if request.sid not in audio_buffers or len(audio_buffers[request.sid]) == 0:
            emit('error', {'message': '没有接收到音频数据，请确保树莓派正在发送音频'})
            # 清空缓冲区
            if request.sid in audio_buffers:
                audio_buffers[request.sid] = []
            return
        
        # 在后台线程中处理音频
        def process_audio():
            try:
                # 合并所有音频块
                audio_data = b''.join(audio_buffers[request.sid])
                
                # 保存到临时文件（使用固定路径，避免在后台线程中使用current_app）
                temp_dir = './temp_images/'
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                temp_fd, temp_path = tempfile.mkstemp(suffix='.wav', dir=temp_dir)
                try:
                    with open(temp_path, 'wb') as f:
                        f.write(audio_data)
                    os.close(temp_fd)
                    
                    # 发送处理中状态
                    emit('processing', {'status': 'processing', 'message': '正在识别语音...'})
                    
                    # 进行语音识别
                    recognized_text = voice_service.recognize_speech_from_audio(temp_path)
                    
                    if recognized_text:
                        # 发送识别结果
                        emit('transcript', {
                            'status': 'success',
                            'text': recognized_text,
                            'message': '语音识别成功'
                        })
                        
                        # 调用推荐服务
                        emit('recommending', {
                            'status': 'recommending',
                            'message': '正在生成推荐...'
                        })
                        
                        try:
                            recommendations = recommendation_service.get_guest_recommendations(
                                user_request=recognized_text,
                                sensor_data=None
                            )
                            
                            emit('recommendations', {
                                'status': 'success',
                                'recommendations': recommendations.get('recommendations', []),
                                'total_count': recommendations.get('total_count', 0),
                                'message': '推荐生成成功'
                            })
                        except Exception as e:
                            print(f'生成推荐失败: {e}')
                            emit('recommendation_error', {
                                'status': 'error',
                                'message': f'生成推荐失败: {str(e)}'
                            })
                    else:
                        emit('transcript_error', {
                            'status': 'error',
                            'message': '无法识别语音内容，请重试'
                        })
                    
                finally:
                    # 清理临时文件
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    
                    # 清空缓冲区
                    if request.sid in audio_buffers:
                        audio_buffers[request.sid] = []
                        
            except Exception as e:
                print(f'处理音频错误: {e}')
                import traceback
                traceback.print_exc()
                emit('error', {
                    'status': 'error',
                    'message': f'处理音频失败: {str(e)}'
                })
                # 确保清空缓冲区
                if request.sid in audio_buffers:
                    audio_buffers[request.sid] = []
        
        # 启动后台线程处理
        thread = threading.Thread(target=process_audio)
        thread.daemon = True
        thread.start()