from flask import Blueprint, request, jsonify
from datetime import datetime
import threading
import time

from services.recommendation_service import RecommendationService
from services.user_service import UserService

# 创建蓝图
bp = Blueprint('recommendation', __name__, url_prefix='/api/recommendations')

# 初始化服务
recommendation_service = RecommendationService()
user_service = UserService()

# 存储推荐任务的状态
recommendation_tasks = {}

@bp.route('/guest', methods=['GET'])
def get_guest_recommendations():
    """
    获取访客推荐菜单
    
    ---
    tags:
      - 推荐系统
    summary: 获取访客推荐
    description: 为未登录用户提供菜品推荐，支持根据饮食偏好筛选
    parameters:
      - name: count
        in: query
        type: integer
        description: 推荐数量，默认为5
        required: false
        default: 5
      - name: dietary_preference
        in: query
        type: string
        description: 饮食偏好（如素食、无麸质等）
        required: false
    responses:
      200:
        description: 成功返回推荐列表
        schema:
          type: object
          properties:
            recommendations:
              type: array
              items:
                $ref: '#/definitions/Recommendation'
      500:
        description: 服务器内部错误
    """
    try:
        # 获取查询参数
        count = request.args.get('count', default=5, type=int)
        dietary_preference = request.args.get('dietary_preference', default=None, type=str)
        
        # 构建偏好设置
        preferences = {}
        if dietary_preference:
            preferences["dietary_preference"] = dietary_preference
        
        # 获取推荐
        recommendations = recommendation_service.get_guest_recommendations(count, preferences)
        
        # 转换为JSON格式
        result = []
        for rec in recommendations:
            result.append({
                "dish_id": rec.dish_id,
                "dish_name": rec.dish_name,
                "reason": rec.reason,
                "score": rec.score
            })
        
        return jsonify({"recommendations": result}), 200
    except Exception as e:
        print(f"获取访客推荐异常: {e}")
        return jsonify({"error": f"获取访客推荐异常: {str(e)}"}), 500

@bp.route('/user/<user_id>', methods=['GET'])
def get_user_recommendations(user_id):
    """
    获取特定用户的个性化推荐菜单
    
    ---
    tags:
      - 推荐系统
    summary: 获取用户个性化推荐
    description: 根据用户历史行为和偏好提供个性化菜品推荐
    parameters:
      - name: user_id
        in: path
        type: string
        description: 用户ID
        required: true
      - name: count
        in: query
        type: integer
        description: 推荐数量，默认为5
        required: false
        default: 5
    responses:
      200:
        description: 成功返回用户推荐列表
        schema:
          type: object
          properties:
            recommendations:
              type: array
              items:
                $ref: '#/definitions/Recommendation'
      404:
        description: 用户不存在
      500:
        description: 服务器内部错误
    """
    try:
        # 获取查询参数
        count = request.args.get('count', default=5, type=int)
        
        # 验证用户是否存在
        user = user_service.get_user_profile(user_id)
        if not user:
            return jsonify({"error": "用户不存在"}), 404
        
        # 获取用户推荐
        recommendations = recommendation_service.get_user_recommendations(user_id, count)
        
        # 转换为JSON格式
        result = []
        for rec in recommendations:
            result.append({
                "dish_id": rec.dish_id,
                "dish_name": rec.dish_name,
                "reason": rec.reason,
                "score": rec.score
            })
        
        return jsonify({"recommendations": result}), 200
    except Exception as e:
        print(f"获取用户推荐异常: {e}")
        return jsonify({"error": f"获取用户推荐异常: {str(e)}"}), 500

@bp.route('/refresh', methods=['POST'])
def refresh_recommendations():
    """
    刷新推荐数据（管理员操作）
    
    ---
    tags:
      - 推荐系统
    summary: 刷新推荐数据
    description: 触发后台任务来重新计算和刷新所有推荐数据
    responses:
      202:
        description: 任务已接受并开始处理
        schema:
          type: object
          properties:
            message:
              type: string
              example: "推荐数据刷新任务已启动"
            task_id:
              type: string
              example: "1623456789"
      500:
        description: 服务器内部错误
    """
    try:
        # 这里应该是一个后台任务
        task_id = str(int(time.time()))
        recommendation_tasks[task_id] = {
            "status": "processing",
            "start_time": datetime.now().isoformat(),
            "progress": 0
        }
        
        # 启动后台线程处理
        thread = threading.Thread(
            target=_background_refresh_task, 
            args=(task_id,)
        )
        thread.start()
        
        return jsonify({
            "message": "推荐数据刷新任务已启动",
            "task_id": task_id
        }), 202
    except Exception as e:
        print(f"刷新推荐异常: {e}")
        return jsonify({"error": f"刷新推荐异常: {str(e)}"}), 500

def _background_refresh_task(task_id):
    """后台刷新推荐数据的任务"""
    try:
        # 模拟长时间运行的任务
        recommendation_tasks[task_id]["progress"] = 25
        time.sleep(2)
        
        recommendation_tasks[task_id]["progress"] = 50
        time.sleep(2)
        
        recommendation_tasks[task_id]["progress"] = 75
        time.sleep(2)
        
        # 执行实际的推荐数据刷新
        recommendation_service.refresh_all_recommendations()
        
        recommendation_tasks[task_id]["progress"] = 100
        recommendation_tasks[task_id]["status"] = "completed"
        recommendation_tasks[task_id]["end_time"] = datetime.now().isoformat()
    except Exception as e:
        print(f"后台刷新任务异常: {e}")
        recommendation_tasks[task_id]["status"] = "failed"
        recommendation_tasks[task_id]["error"] = str(e)
        recommendation_tasks[task_id]["end_time"] = datetime.now().isoformat()

@bp.route('/refine', methods=['POST'])
def refine_recommendations():
    """
    根据用户反馈优化推荐
    
    ---
    tags:
      - 推荐系统
    summary: 优化推荐算法
    description: 根据用户对推荐结果的反馈来调整和优化推荐算法
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            user_id:
              type: string
              description: 用户ID
              example: "user_001"
            feedback:
              type: object
              description: 用户反馈数据
              properties:
                liked_dishes:
                  type: array
                  items:
                    type: string
                  example: ["dish_001", "dish_002"]
                disliked_dishes:
                  type: array
                  items:
                    type: string
                  example: ["dish_003"]
    responses:
      200:
        description: 成功更新用户偏好
        schema:
          type: object
          properties:
            message:
              type: string
              example: "用户偏好已更新"
      400:
        description: 请求参数错误
      500:
        description: 服务器内部错误
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "请提供反馈数据"}), 400
        
        user_id = data.get("user_id")
        feedback = data.get("feedback")
        
        if not user_id or not feedback:
            return jsonify({"error": "请提供用户ID和反馈数据"}), 400
        
        # 处理用户反馈
        success = recommendation_service.refine_user_preferences(user_id, feedback)
        
        if success:
            return jsonify({"message": "用户偏好已更新"}), 200
        else:
            return jsonify({"error": "更新用户偏好失败"}), 500
    except Exception as e:
        print(f"优化推荐异常: {e}")
        return jsonify({"error": f"优化推荐异常: {str(e)}"}), 500

@bp.route('/test/mock', methods=['GET'])
def mock_recommendations():
    """
    模拟推荐测试接口
    
    ---
    tags:
      - 推荐系统
    summary: 获取模拟推荐数据
    description: 返回预设的模拟推荐数据，用于测试和开发
    responses:
      200:
        description: 成功返回模拟推荐数据
        schema:
          type: object
          properties:
            recommendations:
              type: array
              items:
                $ref: '#/definitions/Recommendation'
      500:
        description: 服务器内部错误
    """
    try:
        # 返回固定的模拟数据
        mock_data = [
            {
                "dish_id": "dish_001",
                "dish_name": "宫保鸡丁",
                "reason": "经典川菜，微辣口感",
                "score": 0.95
            },
            {
                "dish_id": "dish_002",
                "dish_name": "麻婆豆腐",
                "reason": "麻辣鲜香，下饭佳品",
                "score": 0.92
            },
            {
                "dish_id": "dish_003",
                "dish_name": "糖醋里脊",
                "reason": "酸甜可口，老少皆宜",
                "score": 0.88
            }
        ]
        
        return jsonify({"recommendations": mock_data}), 200
    except Exception as e:
        print(f"模拟推荐异常: {e}")
        return jsonify({"error": f"模拟推荐异常: {str(e)}"}), 500