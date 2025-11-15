"""API文档配置"""

from flask import Blueprint
from flask_restplus import Api
from docs.models import (
    dish_model, dish_create_model, dish_update_model,
    recommendation_request_model, recommendation_response_model
)

# 创建API文档蓝图
blueprint = Blueprint('api_docs', __name__)

# 配置API文档
api = Api(
    blueprint,
    title='Menu AI API',
    version='1.0',
    description='智能菜单推荐系统API文档',
    doc='/docs/',
    prefix='/api'
)

# 定义命名空间
dishes_ns = api.namespace('dishes', description='菜品管理相关接口')
recommendations_ns = api.namespace('recommendations', description='菜品推荐相关接口')