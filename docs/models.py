"""API文档模型定义"""

from flask_restplus import fields
from app import api

# 菜品模型
dish_model = api.model('Dish', {
    'dish_id': fields.String(description='菜品ID', example='dish_001'),
    'name': fields.String(required=True, description='菜品名称', example='宫保鸡丁'),
    'description': fields.String(description='菜品描述', example='经典川菜，鸡肉鲜嫩，花生酥脆'),
    'category': fields.String(description='菜品类别', example='主菜'),
    'price': fields.Float(description='价格', example=28.8),
    'ingredients': fields.List(fields.String, description='主要配料'),
    'allergens': fields.List(fields.String, description='过敏原'),
    'nutrition_info': fields.Raw(description='营养信息'),
    'is_available': fields.Boolean(description='是否可用', example=True),
    'image_path': fields.String(description='图片路径'),
    'created_at': fields.DateTime(description='创建时间'),
    'updated_at': fields.DateTime(description='更新时间')
})

# 菜品创建模型
dish_create_model = api.model('DishCreate', {
    'name': fields.String(required=True, description='菜品名称'),
    'description': fields.String(description='菜品描述'),
    'category': fields.String(description='菜品类别'),
    'price': fields.Float(description='价格'),
    'ingredients': fields.List(fields.String, description='主要配料'),
    'allergens': fields.List(fields.String, description='过敏原'),
    'nutrition_info': fields.Raw(description='营养信息'),
    'is_available': fields.Boolean(description='是否可用')
})

# 菜品更新模型
dish_update_model = api.model('DishUpdate', {
    'name': fields.String(description='菜品名称'),
    'description': fields.String(description='菜品描述'),
    'category': fields.String(description='菜品类别'),
    'price': fields.Float(description='价格'),
    'ingredients': fields.List(fields.String, description='主要配料'),
    'allergens': fields.List(fields.String, description='过敏原'),
    'nutrition_info': fields.Raw(description='营养信息'),
    'is_available': fields.Boolean(description='是否可用')
})

# 推荐请求模型
recommendation_request_model = api.model('RecommendationRequest', {
    'request': fields.String(required=True, description='用户需求描述', example='我想吃点辣的菜'),
    'sensor_data': fields.Raw(description='传感器数据')
})

# 推荐响应模型
recommendation_model = api.model('Recommendation', {
    'id': fields.String(description='菜品ID'),
    'name': fields.String(description='菜品名称'),
    'reason': fields.String(description='推荐理由')
})

recommendation_response_model = api.model('RecommendationResponse', {
    'status': fields.String(description='状态'),
    'mode': fields.String(description='模式'),
    'recommendations': fields.List(fields.Nested(recommendation_model)),
    'total_count': fields.Integer(description='推荐总数')
})