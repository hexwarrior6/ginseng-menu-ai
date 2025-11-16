# Menu.ai (What to eat today) 后端项目

Menu.ai是一个智能菜单推荐系统的后端服务，使用Python和LangChain开发，用于处理来自前端树莓派的数据，并提供菜品录入和推荐功能。

## 项目功能

1. **菜品录入模块**
   - 通过摄像头拍摄食堂菜品，上传至后端
   - 调用AI大模型接口（如OpenAI）分析菜品成分、热量、辣度等营养信息
   - 将菜品信息保存到数据库

2. **推荐模块**
   - 访客模式：根据用户需求、环境传感器数据提供菜品推荐
   - 用户模式（预留）：支持RFID或人脸识别登录，结合用户习惯提供个性化推荐
   - 支持推荐结果的刷新和优化

## 技术栈

- **后端框架**：Flask
- **AI集成**：LangChain、OpenAI API
- **数据库**：MongoDB（默认）/ SQLite（可选）
- **图像处理**：OpenCV、Pillow
- **语音识别**：SpeechRecognition
- **环境依赖**：python-dotenv

## 项目结构

```
menu-ai/
├── app.py                 # 主应用入口
├── database.py            # 数据库连接配置
├── models/
│   ├── dish_model.py      # 菜品数据模型
│   └── user_model.py      # 用户数据模型
├── services/
│   ├── dish_service.py    # 菜品相关业务逻辑
│   └── recommendation_service.py  # 推荐相关业务逻辑
├── routes/
│   ├── dish_routes.py     # 菜品相关API路由
│   └── recommendation_routes.py  # 推荐相关API路由
├── requirements.txt       # 项目依赖
├── .env                   # 环境变量配置
└── README.md              # 项目说明文档
```

## 安装与配置

1. **克隆项目**
   ```bash
   git clone <项目地址>
   cd menu-ai
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   # Windows激活
   venv\Scripts\activate
   # Linux/Mac激活
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   - 复制`.env`文件并根据实际情况修改配置
   - 至少需要配置`OPENAI_API_KEY`（用于大语言模型调用）
   - 配置`DATABASE_URL`（默认使用MongoDB）

5. **启动服务**
   ```bash
   python app.py
   ```
   服务将在`http://localhost:5000`启动

## API文档

### 菜品管理API

- **POST /api/dishes**：添加新菜品（支持图片上传）
- **GET /api/dishes**：获取所有菜品列表（支持过滤）
- **GET /api/dishes/<dish_id>**：获取菜品详情
- **PUT /api/dishes/<dish_id>**：更新菜品信息
- **DELETE /api/dishes/<dish_id>**：删除菜品
- **PATCH /api/dishes/<dish_id>/availability**：更新菜品可用性
- **POST /api/dishes/analyze/text**：通过文本描述分析菜品

### 推荐API

- **POST /api/recommendations/guest**：访客模式获取推荐
- **POST /api/recommendations/user/<user_id>**：用户模式获取推荐
- **POST /api/recommendations/refresh**：刷新推荐列表
- **POST /api/recommendations/refine**：优化推荐结果
- **GET /api/recommendations/test/mock**：获取模拟推荐数据（测试用）

## 环境变量配置说明

```
# OpenAI API Key（必需）
OPENAI_API_KEY=

# 数据库配置
DATABASE_URL=mongodb://localhost:27017/menu_ai
# 或者使用SQLite
# DATABASE_URL=sqlite:///menu_ai.db

# Flask配置
FLASK_APP=app.py
FLASK_ENV=development
FLASK_RUN_PORT=5000

# 图像临时存储路径
TEMP_IMAGE_PATH=./temp_images/
```

## 注意事项

1. **AI模型配置**：确保已配置有效的OpenAI API密钥
2. **数据库**：默认使用MongoDB，请确保MongoDB服务已启动
3. **图像分析**：由于实际环境限制，当前版本使用模拟数据进行演示
4. **开发环境**：在生产环境中，请将`FLASK_ENV`设置为`production`

## 预留功能

1. 用户身份验证系统（RFID/人脸识别）
2. 更精确的菜品图像识别集成
3. 用户偏好学习和个性化推荐优化
4. 多语言支持

## License

[MIT](LICENSE)