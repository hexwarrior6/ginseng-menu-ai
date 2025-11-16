from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置应用
app.config['SECRET_KEY'] = os.urandom(24)
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
app.config['TEMP_IMAGE_PATH'] = os.getenv('TEMP_IMAGE_PATH', './temp_images/')

# 创建临时图片目录（如果不存在）
if not os.path.exists(app.config['TEMP_IMAGE_PATH']):
    os.makedirs(app.config['TEMP_IMAGE_PATH'])

# 导入数据库连接
from database import db, init_db

# 初始化数据库
init_db(app)

# 导入API路由
from routes import dish_routes, recommendation_routes, voice_routes

# 注册蓝图
app.register_blueprint(dish_routes.bp)
app.register_blueprint(recommendation_routes.bp)
app.register_blueprint(voice_routes.bp)

# 配置Swagger UI
SWAGGER_URL = '/api/docs'  # Swagger UI的URL
API_URL = '/static/swagger.json'  # Swagger文档文件的URL

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Menu AI API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/')
def home():
    return jsonify({"message": "Menu.ai Backend Service is running!", "docs": "/api/docs"})

# 健康检查端点
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "message": "Menu AI API is running"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('FLASK_RUN_PORT', 5000)), debug=True)