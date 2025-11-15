import os
import os
from datetime import datetime
from typing import List, Dict, Optional

import requests
import base64
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

from database import get_db
from models.dish_model import Dish

# 加载环境变量
load_dotenv()

class DishService:
    """菜品服务类，处理菜品相关的业务逻辑"""
    
    def __init__(self):
        # 初始化DeepSeek LLM (通过OpenAI兼容接口)
        self.llm = OpenAI(
            api_key=os.getenv('DEEPSEEK_API_KEY'),
            model_name="deepseek-chat",
            base_url="https://api.deepseek.com/v1"
        )
        
        # 初始化数据库连接
        self.db = get_db()
        
        # 初始化菜品分析的Prompt模板
        self.dish_analysis_prompt = PromptTemplate(
            input_variables=["dish_description"],
            template="""请分析以下菜品，提取其成分、营养信息、辣度等。
            菜品描述: {dish_description}
            
            请以JSON格式输出，包含以下字段：
            - ingredients: 食材列表
            - calories: 估计热量(大卡)
            - protein: 蛋白质含量(克)
            - carbohydrates: 碳水化合物含量(克)
            - fat: 脂肪含量(克)
            - fiber: 纤维含量(克)
            - sugar: 糖含量(克)
            - spiciness: 辣度(0-5)
            - category: 菜品类别(如：主食、肉类、蔬菜、汤品等)
            - tags: 标签列表(如：健康、家常、油腻等)
            """
        )
        
        # 创建LLM链
        self.dish_analysis_chain = LLMChain(
            llm=self.llm,
            prompt=self.dish_analysis_prompt,
            verbose=True
        )
    
    def analyze_dish_by_image(self, image_path: str) -> Dict:
        """通过图像分析菜品信息"""
        try:
            # 这里应该是调用图像识别API，如Cal AI
            # 由于实际环境限制，这里返回模拟数据
            return self._mock_ai_image_analysis(image_path)
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
            # 准备完整的prompt文本
            prompt_text = self.dish_analysis_prompt.format(dish_description=dish_description)
            # 直接调用LLM进行分析
            result = self.llm.predict(prompt_text)
            # 解析JSON结果
            import json
            return json.loads(result)
        except Exception as e:
            print(f"文本分析失败: {e}")
            # 返回默认模拟数据
            return {
                "ingredients": ["未知食材"],
                "calories": 200,
                "protein": 10,
                "carbohydrates": 15,
                "fat": 8,
                "fiber": 2,
                "sugar": 3,
                "spiciness": 0,
                "category": "其他",
                "tags": []
            }