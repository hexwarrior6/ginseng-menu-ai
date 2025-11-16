from flask import Blueprint, request, jsonify
import os
import uuid
from datetime import datetime

from services.dish_service import DishService

# 创建蓝图
bp = Blueprint('dish', __name__, url_prefix='/api/dishes')

# 初始化菜品服务
dish_service = DishService()

@bp.route('/', methods=['POST'])
def add_dish():
    """
    添加新菜品（支持从树莓派摄像头上传图片）
    
    ---
    tags:
      - 菜品管理
    summary: 添加新菜品
    description: 添加一个新的菜品到菜单中，支持通过图片上传或JSON数据
    parameters:
      - name: image
        in: formData
        type: file
        description: 菜品图片文件（可选）
        required: false
      - name: name
        in: formData
        type: string
        description: 菜品名称（当上传图片时可选）
        required: false
      - name: description
        in: formData
        type: string
        description: 菜品描述（当上传图片时可选）
        required: false
      - name: price
        in: formData
        type: number
        format: float
        description: 菜品价格（当上传图片时可选）
        required: false
      - name: body
        in: body
        required: false
        schema:
          $ref: '#/definitions/DishCreate'
    responses:
      201:
        description: 成功添加菜品
        schema:
          type: object
          properties:
            message:
              type: string
              example: "菜品添加成功"
            dish_id:
              type: string
              example: "dish_001"
      400:
        description: 请求参数错误
      500:
        description: 服务器内部错误
    """
    try:
        # 检查是否有文件上传
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename == '':
                return jsonify({"error": "未选择图片文件"}), 400
            
            # 保存图片到临时目录
            temp_dir = os.getenv('TEMP_IMAGE_PATH', './temp_images/')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            # 生成唯一的文件名
            unique_filename = f"{uuid.uuid4()}_{image_file.filename}"
            image_path = os.path.join(temp_dir, unique_filename)
            image_file.save(image_path)
            
            # 调用AI分析图片
            dish_data = dish_service.analyze_dish_by_image(image_path)
            dish_data["image_path"] = image_path
            
            # 从表单中获取其他信息（如果有）
            if request.form.get('name'):
                dish_data["name"] = request.form.get('name')
            if request.form.get('description'):
                dish_data["description"] = request.form.get('description')
            if request.form.get('price'):
                try:
                    dish_data["price"] = float(request.form.get('price'))
                except ValueError:
                    pass
            
        else:
            # 从JSON获取菜品数据
            dish_data = request.json
            if not dish_data:
                return jsonify({"error": "请提供菜品数据"}), 400
        
        # 添加菜品到数据库
        dish = dish_service.add_dish(dish_data)
        if dish:
            return jsonify({"message": "菜品添加成功", "dish_id": dish.dish_id}), 201
        else:
            return jsonify({"error": "菜品添加失败"}), 500
    except Exception as e:
        print(f"添加菜品异常: {e}")
        return jsonify({"error": f"添加菜品异常: {str(e)}"}), 500

@bp.route('/', methods=['GET'])
def get_all_dishes():
    """
    获取所有菜品列表
    
    ---
    tags:
      - 菜品管理
    summary: 获取所有菜品
    description: 获取所有菜品列表，支持按分类和可用性筛选
    parameters:
      - name: category
        in: query
        type: string
        description: 菜品分类筛选
        required: false
      - name: is_available
        in: query
        type: boolean
        description: 可用性筛选
        required: false
    responses:
      200:
        description: 成功返回菜品列表
        schema:
          type: object
          properties:
            dishes:
              type: array
              items:
                $ref: '#/definitions/Dish'
            total_count:
              type: integer
              example: 10
      500:
        description: 服务器内部错误
    """
    try:
        # 获取查询参数
        category = request.args.get('category')
        is_available = request.args.get('is_available')
        
        # 构建过滤条件
        filters = {}
        if category:
            filters["category"] = category
        if is_available is not None:
            filters["is_available"] = is_available.lower() == 'true'
        
        # 获取菜品列表
        dishes = dish_service.get_all_dishes(filters)
        
        # 转换为JSON格式
        result = []
        for dish in dishes:
            dish_dict = dish.to_dict()
            # 移除一些敏感或不必要的字段
            dish_dict.pop('created_at', None)
            dish_dict.pop('updated_at', None)
            result.append(dish_dict)
        
        return jsonify({"dishes": result, "total_count": len(result)}), 200
    except Exception as e:
        print(f"获取菜品列表异常: {e}")
        return jsonify({"error": f"获取菜品列表异常: {str(e)}"}), 500

@bp.route('/<dish_id>', methods=['GET'])
def get_dish_by_id(dish_id):
    """
    通过ID获取菜品详情
    
    ---
    tags:
      - 菜品管理
    summary: 获取菜品详情
    description: 根据菜品ID获取特定菜品的详细信息
    parameters:
      - name: dish_id
        in: path
        type: string
        description: 菜品ID
        required: true
    responses:
      200:
        description: 成功返回菜品信息
        schema:
          $ref: '#/definitions/Dish'
      404:
        description: 菜品不存在
      500:
        description: 服务器内部错误
    """
    try:
        dish = dish_service.get_dish_by_id(dish_id)
        if dish:
            dish_dict = dish.to_dict()
            return jsonify(dish_dict), 200
        else:
            return jsonify({"error": "未找到该菜品"}), 404
    except Exception as e:
        print(f"获取菜品详情异常: {e}")
        return jsonify({"error": f"获取菜品详情异常: {str(e)}"}), 500

@bp.route('/<dish_id>', methods=['PUT'])
def update_dish(dish_id):
    """
    更新菜品信息
    
    ---
    tags:
      - 菜品管理
    summary: 更新菜品
    description: 根据菜品ID更新菜品信息
    parameters:
      - name: dish_id
        in: path
        type: string
        description: 菜品ID
        required: true
      - name: body
        in: body
        required: true
        schema:
          $ref: '#/definitions/DishUpdate'
    responses:
      200:
        description: 成功更新菜品
        schema:
          type: object
          properties:
            message:
              type: string
              example: "菜品更新成功"
      400:
        description: 请求参数错误
      404:
        description: 菜品不存在
      500:
        description: 服务器内部错误
    """
    try:
        update_data = request.json
        if not update_data:
            return jsonify({"error": "请提供更新数据"}), 400
        
        success = dish_service.update_dish(dish_id, update_data)
        if success:
            return jsonify({"message": "菜品更新成功"}), 200
        else:
            return jsonify({"error": "菜品更新失败或菜品不存在"}), 404
    except Exception as e:
        print(f"更新菜品异常: {e}")
        return jsonify({"error": f"更新菜品异常: {str(e)}"}), 500

@bp.route('/<dish_id>', methods=['DELETE'])
def delete_dish(dish_id):
    """
    删除菜品
    
    ---
    tags:
      - 菜品管理
    summary: 删除菜品
    description: 根据菜品ID删除菜品
    parameters:
      - name: dish_id
        in: path
        type: string
        description: 菜品ID
        required: true
    responses:
      200:
        description: 成功删除菜品
        schema:
          type: object
          properties:
            message:
              type: string
              example: "菜品删除成功"
      404:
        description: 菜品不存在
      500:
        description: 服务器内部错误
    """
    try:
        success = dish_service.delete_dish(dish_id)
        if success:
            return jsonify({"message": "菜品删除成功"}), 200
        else:
            return jsonify({"error": "菜品删除失败或菜品不存在"}), 404
    except Exception as e:
        print(f"删除菜品异常: {e}")
        return jsonify({"error": f"删除菜品异常: {str(e)}"}), 500

@bp.route('/<dish_id>/availability', methods=['PATCH'])
def update_dish_availability(dish_id):
    """
    更新菜品的可用性状态
    
    ---
    tags:
      - 菜品管理
    summary: 更新菜品可用性
    description: 根据菜品ID更新菜品的可用性状态
    parameters:
      - name: dish_id
        in: path
        type: string
        description: 菜品ID
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            is_available:
              type: boolean
              example: true
    responses:
      200:
        description: 成功更新菜品可用性
        schema:
          type: object
          properties:
            message:
              type: string
              example: "菜品已设置为可用"
      400:
        description: 请求参数错误
      404:
        description: 菜品不存在
      500:
        description: 服务器内部错误
    """
    try:
        data = request.json
        if 'is_available' not in data:
            return jsonify({"error": "请提供is_available字段"}), 400
        
        is_available = data['is_available']
        success = dish_service.update_dish_availability(dish_id, is_available)
        
        if success:
            status = "可用" if is_available else "不可用"
            return jsonify({"message": f"菜品已设置为{status}"}), 200
        else:
            return jsonify({"error": "更新菜品可用性失败或菜品不存在"}), 404
    except Exception as e:
        print(f"更新菜品可用性异常: {e}")
        return jsonify({"error": f"更新菜品可用性异常: {str(e)}"}), 500

@bp.route('/analyze/text', methods=['POST'])
def analyze_dish_by_text():
    """
    通过文本描述分析菜品信息
    
    ---
    tags:
      - 菜品管理
    summary: 文本分析菜品
    description: 通过文本描述分析菜品的成分、营养信息等
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            description:
              type: string
              example: "这是一道宫保鸡丁，主要由鸡肉、花生米等制成"
    responses:
      200:
        description: 成功分析菜品
        schema:
          type: object
          properties:
            name:
              type: string
              example: "宫保鸡丁"
            ingredients:
              type: array
              items:
                type: string
              example: ["鸡肉", "花生米", "辣椒"]
      400:
        description: 请求参数错误
      500:
        description: 服务器内部错误
    """
    try:
        data = request.json
        if not data or 'description' not in data:
            return jsonify({"error": "请提供菜品描述"}), 400
        
        analysis_result = dish_service.analyze_dish_by_text(data['description'])
        return jsonify(analysis_result), 200
    except Exception as e:
        print(f"文本分析异常: {e}")
        return jsonify({"error": f"文本分析异常: {str(e)}"}), 500

@bp.route('/batch', methods=['POST'])
def add_multiple_dishes():
    """
    批量添加多个菜品（支持从多张图片上传）
    
    ---
    tags:
      - 菜品管理
    summary: 批量添加菜品
    description: 通过上传多张图片批量添加菜品到菜单中
    parameters:
      - name: images
        in: formData
        type: array
        items:
          type: file
        description: 菜品图片文件列表
        required: true
    responses:
      201:
        description: 成功批量添加菜品
        schema:
          type: object
          properties:
            message:
              type: string
              example: "批量添加菜品成功"
            dish_ids:
              type: array
              items:
                type: string
              example: ["dish_001", "dish_002"]
      400:
        description: 请求参数错误
      500:
        description: 服务器内部错误
    """
    try:
        # 检查是否有文件上传
        if 'images' not in request.files:
            return jsonify({"error": "请上传图片文件"}), 400
        
        image_files = request.files.getlist('images')
        if not image_files or all(f.filename == '' for f in image_files):
            return jsonify({"error": "未选择图片文件"}), 400
        
        # 保存图片到临时目录
        temp_dir = os.getenv('TEMP_IMAGE_PATH', './temp_images/')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # 保存所有图片并获取路径
        image_paths = []
        for image_file in image_files:
            if image_file.filename != '':
                # 生成唯一的文件名
                unique_filename = f"{uuid.uuid4()}_{image_file.filename}"
                image_path = os.path.join(temp_dir, unique_filename)
                image_file.save(image_path)
                image_paths.append(image_path)
        
        if not image_paths:
            return jsonify({"error": "未保存任何图片文件"}), 400
        
        # 调用AI批量分析图片
        dishes_data = dish_service.analyze_multiple_dishes_by_images(image_paths)
        
        # 添加所有菜品到数据库
        dish_ids = []
        for i, dish_data in enumerate(dishes_data):
            # 将图片路径添加到菜品数据中
            dish_data["image_path"] = image_paths[i] if i < len(image_paths) else ""
            
            # 添加菜品到数据库
            dish = dish_service.add_dish(dish_data)
            if dish:
                dish_ids.append(dish.dish_id)
        
        return jsonify({
            "message": "批量添加菜品成功", 
            "dish_ids": dish_ids,
            "count": len(dish_ids)
        }), 201
        
    except Exception as e:
        print(f"批量添加菜品异常: {e}")
        return jsonify({"error": f"批量添加菜品异常: {str(e)}"}), 500