from flask import Blueprint, request, jsonify
from services.recommendation_service import RecommendationService

# 创建蓝图
bp = Blueprint('recommendation', __name__, url_prefix='/api/recommendations')

# 初始化推荐服务
recommendation_service = RecommendationService()

@bp.route('/guest', methods=['POST'])
def get_guest_recommendations():
    """访客模式下获取菜品推荐"""
    try:
        # 获取请求数据
        data = request.json
        if not data:
            return jsonify({"error": "请提供请求数据"}), 400
        
        # 获取用户需求（必填）
        user_request = data.get('request')
        if not user_request:
            return jsonify({"error": "请提供用户需求(request)"}), 400
        
        # 获取传感器数据（可选）
        sensor_data = data.get('sensor_data', {})
        
        # 调用推荐服务
        recommendations = recommendation_service.get_guest_recommendations(user_request, sensor_data)
        
        return jsonify({
            "status": "success",
            "mode": "guest",
            "recommendations": recommendations.get("recommendations", []),
            "total_count": recommendations.get("total_count", 0)
        }), 200
    except Exception as e:
        print(f"获取访客推荐异常: {e}")
        return jsonify({"error": f"获取推荐异常: {str(e)}"}), 500

@bp.route('/user/<user_id>', methods=['POST'])
def get_user_recommendations(user_id):
    """用户模式下获取菜品推荐（预留功能）"""
    try:
        # 获取请求数据
        data = request.json
        if not data:
            return jsonify({"error": "请提供请求数据"}), 400
        
        # 获取用户需求（必填）
        user_request = data.get('request')
        if not user_request:
            return jsonify({"error": "请提供用户需求(request)"}), 400
        
        # 获取传感器数据（可选）
        sensor_data = data.get('sensor_data', {})
        
        # 调用推荐服务
        recommendations = recommendation_service.get_user_recommendations(user_id, user_request, sensor_data)
        
        return jsonify({
            "status": "success",
            "mode": "user",
            "user_id": user_id,
            "recommendations": recommendations.get("recommendations", []),
            "total_count": recommendations.get("total_count", 0)
        }), 200
    except Exception as e:
        print(f"获取用户推荐异常: {e}")
        return jsonify({"error": f"获取推荐异常: {str(e)}"}), 500

@bp.route('/refresh', methods=['POST'])
def refresh_recommendations():
    """刷新推荐列表"""
    try:
        # 获取请求数据
        data = request.json
        if not data:
            return jsonify({"error": "请提供请求数据"}), 400
        
        # 获取模式（guest或user）
        mode = data.get('mode', 'guest')
        
        # 获取用户需求
        user_request = data.get('request')
        if not user_request:
            return jsonify({"error": "请提供用户需求(request)"}), 400
        
        # 获取传感器数据
        sensor_data = data.get('sensor_data', {})
        
        # 根据模式调用不同的推荐方法
        if mode == 'user':
            user_id = data.get('user_id')
            if not user_id:
                return jsonify({"error": "用户模式下请提供user_id"}), 400
            recommendations = recommendation_service.get_user_recommendations(user_id, user_request, sensor_data)
        else:
            # 默认使用访客模式
            recommendations = recommendation_service.get_guest_recommendations(user_request, sensor_data)
        
        return jsonify({
            "status": "success",
            "mode": mode,
            "recommendations": recommendations.get("recommendations", []),
            "total_count": recommendations.get("total_count", 0)
        }), 200
    except Exception as e:
        print(f"刷新推荐异常: {e}")
        return jsonify({"error": f"刷新推荐异常: {str(e)}"}), 500

@bp.route('/refine', methods=['POST'])
def refine_recommendations():
    """根据用户反馈优化推荐结果"""
    try:
        # 获取请求数据
        data = request.json
        if not data:
            return jsonify({"error": "请提供请求数据"}), 400
        
        # 获取原始推荐的条件
        original_request = data.get('original_request')
        if not original_request:
            return jsonify({"error": "请提供原始请求(original_request)"}), 400
        
        # 获取用户的优化要求
        refinement_request = data.get('refinement_request')
        if not refinement_request:
            return jsonify({"error": "请提供优化要求(refinement_request)"}), 400
        
        # 获取模式和其他数据
        mode = data.get('mode', 'guest')
        sensor_data = data.get('sensor_data', {})
        
        # 组合原始请求和优化要求
        combined_request = f"原始需求: {original_request}\n优化要求: {refinement_request}"
        
        # 根据模式调用不同的推荐方法
        if mode == 'user':
            user_id = data.get('user_id')
            if not user_id:
                return jsonify({"error": "用户模式下请提供user_id"}), 400
            recommendations = recommendation_service.get_user_recommendations(user_id, combined_request, sensor_data)
        else:
            # 默认使用访客模式
            recommendations = recommendation_service.get_guest_recommendations(combined_request, sensor_data)
        
        return jsonify({
            "status": "success",
            "mode": mode,
            "refined": True,
            "recommendations": recommendations.get("recommendations", []),
            "total_count": recommendations.get("total_count", 0)
        }), 200
    except Exception as e:
        print(f"优化推荐异常: {e}")
        return jsonify({"error": f"优化推荐异常: {str(e)}"}), 500

@bp.route('/test/mock', methods=['GET'])
def get_mock_recommendations():
    """获取模拟推荐数据（用于测试）"""
    try:
        # 提供一些预定义的模拟推荐数据
        mock_recommendations = {
            "recommendations": [
                {
                    "id": "mock_1",
                    "name": "宫保鸡丁",
                    "reason": "这道川菜色香味俱全，鸡肉鲜嫩，花生酥脆，辣味适中，非常适合下饭。"
                },
                {
                    "id": "mock_2",
                    "name": "清炒时蔬",
                    "reason": "新鲜蔬菜清炒，保留了食材的原汁原味，低热量高纤维，健康营养。"
                },
                {
                    "id": "mock_3",
                    "name": "番茄鸡蛋汤",
                    "reason": "家常汤品，番茄的酸甜搭配鸡蛋的鲜香，开胃又营养，适合各种人群。"
                }
            ],
            "total_count": 3
        }
        
        return jsonify({
            "status": "success",
            "mode": "test",
            "recommendations": mock_recommendations["recommendations"],
            "total_count": mock_recommendations["total_count"]
        }), 200
    except Exception as e:
        print(f"获取模拟推荐异常: {e}")
        return jsonify({"error": f"获取模拟推荐异常: {str(e)}"}), 500