from flask import Flask
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, ConfigurationError
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('menu_ai_db')

# 数据库客户端实例
db_client = None

# 数据库实例
db = None

def init_db(app: Flask):
    """初始化数据库连接"""
    global db_client, db
    
    # 获取数据库连接URL
    db_url = app.config.get('DATABASE_URL') or os.getenv('DATABASE_URL')
    
    if not db_url:
        raise ValueError("数据库连接URL未设置，请在.env文件中配置DATABASE_URL")
    
    try:
        # MongoDB连接参数配置
        connection_params = {
            'serverSelectionTimeoutMS': 5000,  # 连接超时时间（毫秒）
            'connectTimeoutMS': 20000,         # 连接池超时时间
            'socketTimeoutMS': 60000,          # 套接字超时时间
            'maxPoolSize': 50,                 # 最大连接池大小
            'minPoolSize': 10,                 # 最小连接池大小
            'retryWrites': True,               # 启用重试写入
            'w': 'majority'                    # 写关注点
        }
        
        # 连接MongoDB
        db_client = MongoClient(db_url, **connection_params)
        
        # 测试连接
        db_client.admin.command('ping')
        logger.info("MongoDB连接成功!")
        
        # 获取数据库实例
        db = db_client.menu_ai
        
        # 初始化集合（如果需要）
        initialize_collections()
        
    except ConfigurationError as e:
        logger.error(f"MongoDB配置错误（可能是认证信息问题）: {e}")
        raise
    except OperationFailure as e:
        logger.error(f"MongoDB操作失败（可能是认证失败）: {e}")
        raise
    except ConnectionFailure as e:
        logger.error(f"MongoDB连接错误（网络或服务器问题）: {e}")
        raise
    except Exception as e:
        logger.error(f"MongoDB连接失败: {e}")
        raise

def initialize_collections():
    """初始化数据库集合（表）"""
    global db
    
    # 检查并创建菜品集合
    if 'dishes' not in db.list_collection_names():
        db.create_collection('dishes')
        # 创建索引以提高查询性能
        db.dishes.create_index('name', unique=True)
        db.dishes.create_index('category')
        db.dishes.create_index('tags')
        print("菜品集合创建成功")
    
    # 检查并创建用户集合
    if 'users' not in db.list_collection_names():
        db.create_collection('users')
        db.users.create_index('user_id', unique=True)
        print("用户集合创建成功")
    
    # 检查并创建订单历史集合
    if 'order_history' not in db.list_collection_names():
        db.create_collection('order_history')
        db.order_history.create_index('user_id')
        db.order_history.create_index('dish_id')
        print("订单历史集合创建成功")

def get_db():
    """获取数据库实例"""
    global db
    if db is None:
        raise Exception("数据库尚未初始化")
    return db

def close_db():
    """关闭数据库连接"""
    global db_client
    if db_client:
        db_client.close()
        print("MongoDB连接已关闭")