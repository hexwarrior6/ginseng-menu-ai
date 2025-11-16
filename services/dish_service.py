import os
import sys
import base64
from datetime import datetime
from typing import List, Dict, Optional

# 添加site-packages到路径
site_packages_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.venv', 'lib', 'site-packages'))
if site_packages_path not in sys.path:
    sys.path.insert(0, site_packages_path)

from zai import ZhipuAiClient
from dotenv import load_dotenv

from database import get_db
from models.dish_model import Dish

# 加载环境变量
load_dotenv()

class DishService:
    """菜品服务类，处理菜品相关的业务逻辑"""
    
    def __init__(self):
        # 初始化ZhipuAI客户端，从环境变量获取API密钥
        api_key = os.getenv('ZHIPUAI_API_KEY')
        if not api_key:
            raise ValueError("ZHIPUAI_API_KEY环境变量未设置")
        self.zhipu_client = ZhipuAiClient(api_key=api_key)
        
        # 初始化数据库连接
        self.db = get_db()
    
    def analyze_multiple_dishes_by_images(self, image_paths: List[str]) -> List[Dict]:
        """通过多张图像批量分析菜品信息"""
        results = []
        
        try:
            # 准备图像数据
            image_contents = []
            for image_path in image_paths:
                with open(image_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                    image_contents.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    })
            
            # 构建提示词
            prompt = """
            请分析这些图片中的菜品，每张图片可能包含多个菜品。
            对于每张图片，请提供以下信息：
            1. 菜品名称
            2. 主要食材列表
            3. 营养信息（热量、蛋白质、碳水化合物、脂肪、纤维、糖分、钠含量）
            4. 辣度（0-5级）
            5. 菜品类别（如：主食、肉类、蔬菜、汤品等）
            6. 标签（如：健康、家常、油腻等）
            
            请以JSON格式返回结果，格式如下：
            [
              {
                "name": "菜品名称",
                "ingredients": ["食材1", "食材2", ...],
                "nutrition_info": {
                  "calories": 0,
                  "protein": 0,
                  "carbohydrates": 0,
                  "fat": 0,
                  "fiber": 0,
                  "sugar": 0,
                  "sodium": 0
                },
                "spiciness": 0,
                "category": "菜品类别",
                "tags": ["标签1", "标签2"]
              },
              ...
            ]
            不要包含其他文本，只返回JSON数组。
            """
            
            # 添加文本提示到第一个位置
            content_list = [{"type": "text", "text": prompt}] + image_contents
            
            # 调用ZhipuAI的glm-4.5v模型进行批量图像分析
            response = self.zhipu_client.chat.completions.create(
                model="glm-4.5v",
                messages=[
                    {
                        "role": "user",
                        "content": content_list
                    }
                ]
            )
            
            # 解析返回的JSON结果
            import json
            result = json.loads(response.choices[0].message.content)
            
            # 验证返回的数据结构
            if isinstance(result, list):
                for item in result:
                    required_fields = ["name", "ingredients", "nutrition_info", "spiciness", "category", "tags"]
                    for field in required_fields:
                        if field not in item:
                            raise ValueError(f"Missing required field: {field}")
                    
                    # 确保nutrition_info包含所有必需的子字段
                    required_nutrition_fields = ["calories", "protein", "carbohydrates", "fat", "fiber", "sugar", "sodium"]
                    for field in required_nutrition_fields:
                        if field not in item["nutrition_info"]:
                            item["nutrition_info"][field] = 0  # 设置默认值
                
                results = result
            else:
                raise ValueError("Expected a list of dishes")
                
        except Exception as e:
            print(f"批量图像分析失败: {e}")
            # 如果AI分析失败，为每张图片返回默认模拟数据
            for image_path in image_paths:
                mock_result = self._mock_ai_image_analysis(image_path)
                results.append(mock_result)
        
        return results
        
    def analyze_dish_by_image(self, image_path: str) -> Dict:
        """通过图像分析菜品信息"""
        try:
            # 将图像编码为base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 调用ZhipuAI的glm-4.5v模型进行图像分析
            response = self.zhipu_client.chat.completions.create(
                model="glm-4.5v",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            },
                            {
                                "type": "text",
                                "text": "请分析这张图片中的菜品，提供以下信息：\n1. 菜品名称\n2. 主要食材列表\n3. 营养信息（热量、蛋白质、碳水化合物、脂肪、纤维、糖分、钠含量）\n4. 辣度（0-5级）\n5. 菜品类别（如：主食、肉类、蔬菜、汤品等）\n6. 标签（如：健康、家常、油腻等）\n\n请以JSON格式返回结果，不要包含其他文本。"
                            }
                        ]
                    }
                ]
            )
            
            # 解析返回的JSON结果
            import json
            result = json.loads(response.choices[0].message.content)
            
            # 确保返回的数据结构完整
            required_fields = ["name", "ingredients", "nutrition_info", "spiciness", "category", "tags"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            # 确保nutrition_info包含所有必需的子字段
            required_nutrition_fields = ["calories", "protein", "carbohydrates", "fat", "fiber", "sugar", "sodium"]
            for field in required_nutrition_fields:
                if field not in result["nutrition_info"]:
                    result["nutrition_info"][field] = 0  # 设置默认值
            
            return result
        except Exception as e:
            print(f"图像分析失败: {e}")
            # 如果AI分析失败，返回默认模拟数据
            return self._mock_ai_image_analysis(image_path)
    
    def _mock_ai_image_analysis(self, image_path: str) -> Dict:
        """模拟AI图像分析结果（用于演示）"""
        # 简单的文件名分析，提取可能的菜品名
        dish_name = os.path.basename(image_path).split('.')[0].replace('_', ' ')
        
        # 根据文件名生成不同的模拟数据
        if "chicken" in dish_name.lower() or "鸡肉" in dish_name:
            return {
                "name": dish_name,
                "ingredients": ["鸡肉", "青椒", "洋葱", "大蒜", "姜", "酱油", "盐"],
                "nutrition_info": {
                    "calories": 320,
                    "protein": 28,
                    "carbohydrates": 15,
                    "fat": 18,
                    "fiber": 2,
                    "sugar": 3,
                    "sodium": 500
                },
                "spiciness": 2,
                "category": "肉类",
                "tags": ["高蛋白", "家常"]
            }
        elif "vegetable" in dish_name.lower() or "蔬菜" in dish_name:
            return {
                "name": dish_name,
                "ingredients": ["西兰花", "胡萝卜", "玉米", "植物油", "盐", "胡椒"],
                "nutrition_info": {
                    "calories": 120,
                    "protein": 5,
                    "carbohydrates": 18,
                    "fat": 5,
                    "fiber": 6,
                    "sugar": 4,
                    "sodium": 200
                },
                "spiciness": 0,
                "category": "蔬菜",
                "tags": ["低热量", "健康"]
            }
        else:
            # 默认模拟数据
            return {
                "name": dish_name,
                "ingredients": ["未知食材1", "未知食材2", "未知食材3"],
                "nutrition_info": {
                    "calories": 250,
                    "protein": 15,
                    "carbohydrates": 20,
                    "fat": 10,
                    "fiber": 3,
                    "sugar": 5,
                    "sodium": 300
                },
                "spiciness": 1,
                "category": "其他",
                "tags": ["家常"]
            }
    
    def add_dish(self, dish_data: Dict) -> Optional[Dish]:
        """添加新菜品到数据库"""
        try:
            # 创建菜品对象
            dish = Dish(
                name=dish_data.get("name", ""),
                description=dish_data.get("description", ""),
                ingredients=dish_data.get("ingredients", []),
                nutrition_info=dish_data.get("nutrition_info", {}),
                category=dish_data.get("category", ""),
                price=dish_data.get("price", 0.0),
                spiciness=dish_data.get("spiciness", 0),
                tags=dish_data.get("tags", []),
                image_path=dish_data.get("image_path", "")
            )
            
            # 保存到数据库
            self.db.dishes.insert_one(dish.to_dict())
            return dish
        except Exception as e:
            print(f"添加菜品失败: {e}")
            return None
    
    def get_dish_by_id(self, dish_id: str) -> Optional[Dish]:
        """通过ID获取菜品信息"""
        try:
            dish_data = self.db.dishes.find_one({"dish_id": dish_id})
            if dish_data:
                return Dish.from_dict(dish_data)
            return None
        except Exception as e:
            print(f"获取菜品失败: {e}")
            return None
    
    def get_all_dishes(self, filters: Dict = None) -> List[Dish]:
        """获取所有菜品，可以带过滤条件"""
        try:
            query = filters or {}
            dishes_data = self.db.dishes.find(query)
            return [Dish.from_dict(dish) for dish in dishes_data]
        except Exception as e:
            print(f"获取所有菜品失败: {e}")
            return []
    
    def update_dish(self, dish_id: str, update_data: Dict) -> bool:
        """更新菜品信息"""
        try:
            update_data["updated_at"] = datetime.now()
            result = self.db.dishes.update_one(
                {"dish_id": dish_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"更新菜品失败: {e}")
            return False
    
    def delete_dish(self, dish_id: str) -> bool:
        """删除菜品"""
        try:
            result = self.db.dishes.delete_one({"dish_id": dish_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"删除菜品失败: {e}")
            return False
    
    def update_dish_availability(self, dish_id: str, is_available: bool) -> bool:
        """更新菜品的可用性状态"""
        try:
            result = self.db.dishes.update_one(
                {"dish_id": dish_id},
                {"$set": {
                    "is_available": is_available,
                    "updated_at": datetime.now()
                }}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"更新菜品可用性失败: {e}")
            return False
    
    def analyze_dish_by_text(self, dish_description: str) -> Dict:
        """通过文本描述分析菜品信息"""
        try:
            # 调用ZhipuAI的glm-4.6模型进行文本分析
            response = self.zhipu_client.chat.completions.create(
                model="glm-4.6",
                messages=[
                    {
                        "role": "user",
                        "content": f"请根据以下描述分析菜品信息：{dish_description}\n\n请提供以下信息：\n1. 菜品名称\n2. 主要食材列表\n3. 营养信息（热量、蛋白质、碳水化合物、脂肪、纤维、糖分、钠含量）\n4. 辣度（0-5级）\n5. 菜品类别（如：主食、肉类、蔬菜、汤品等）\n6. 标签（如：健康、家常、油腻等）\n\n请以JSON格式返回结果，不要包含其他文本。"
                    }
                ]
            )
            
            # 解析返回的JSON结果
            import json
            result = json.loads(response.choices[0].message.content)
            
            # 确保返回的数据结构完整
            required_fields = ["name", "ingredients", "nutrition_info", "spiciness", "category", "tags"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            # 确保nutrition_info包含所有必需的子字段
            required_nutrition_fields = ["calories", "protein", "carbohydrates", "fat", "fiber", "sugar", "sodium"]
            for field in required_nutrition_fields:
                if field not in result["nutrition_info"]:
                    result["nutrition_info"][field] = 0  # 设置默认值
            
            return result
        except Exception as e:
            print(f"文本分析失败: {e}")
            return {"error": str(e)}