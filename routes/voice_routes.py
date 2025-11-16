from flask import Blueprint, request, jsonify, current_app
import os
import tempfile
from services.voice_service import VoiceService

# 创建蓝图
bp = Blueprint('voice', __name__, url_prefix='/api/voice')

# 初始化服务
voice_service = VoiceService()

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