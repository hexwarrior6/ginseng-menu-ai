import os
import random
from datetime import datetime
from typing import List, Dict, Optional
import os
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
# LLMChain已弃用，使用RunnableSequence替代
from dotenv import load_dotenv

from database import get_db
from models.dish_model import Dish
from models.user_model import User

# 加载环境变量
load_dotenv()

class RecommendationService:
    """推荐服务类，处理菜品推荐相关的业务逻辑"""
    
    def __init__(self):
        # 初始化DeepSeek LLM (通过OpenAI兼容接口)
        self.llm = OpenAI(
            api_key=os.getenv('DEEPSEEK_API_KEY'),
            model_name="deepseek-chat",
            base_url="https://api.deepseek.com/v1"
        )
        
        # 初始化数据库连接
        self.db = get_db()
        
        # 初始化推荐的Prompt模板
        self.recommendation_prompt = PromptTemplate(
            input_variables=["user_request", "available_dishes", "user_preferences", "sensor_data", "weather_info"],
            template="""你是一个智能菜单推荐助手，根据用户需求、可用菜品、用户偏好和环境信息，为用户推荐合适的菜品。
            
            用户需求: {user_request}
            可用菜品: {available_dishes}
            用户偏好: {user_preferences}
            传感器信息: {sensor_data}
            天气信息: {weather_info}
            
            请根据以上信息，推荐3-5道适合的菜品，并解释推荐理由。
            请以JSON格式输出，包含以下字段：
            - recommendations: 推荐菜品列表，每道菜品包含id、name、reason
            - total_count: 推荐菜品总数
            """
        )
        
        # 使用RunnableSequence替代LLMChain
        self.recommendation_chain = self.recommendation_prompt | self.llm
    
    def get_guest_recommendations(self, user_request: str, sensor_data: Dict = None) -> Dict:
        """访客模式下的菜品推荐"""
        try:
            # 获取所有可用的菜品
            available_dishes = self._get_available_dishes()
            
            # 准备菜品信息字符串
            dishes_str = self._format_dishes_for_llm(available_dishes)
            
            # 模拟用户偏好（访客模式下为通用偏好）
            user_preferences = "通用偏好，适合大多数人"
            
            # 获取模拟天气信息
            weather_info = self._get_mock_weather_info()
            
            # 准备完整的prompt文本
            prompt_text = self.recommendation_prompt.format(
                user_request=user_request,
                available_dishes=dishes_str,
                user_preferences=user_preferences,
                sensor_data=sensor_data or {"temperature": 25, "humidity": 50},
                weather_info=weather_info
            )
            
            # 直接调用LLM进行推荐
            result = self.llm.predict(prompt_text)
            
            # 解析JSON结果
            import json
            recommendations = json.loads(result)
            
            # 如果LLM返回的是空推荐，生成一些随机推荐
            if len(recommendations.get("recommendations", [])) == 0:
                recommendations = self._generate_fallback_recommendations(available_dishes)
            
            return recommendations
        except Exception as e:
            print(f"访客模式推荐失败: {e}")
            # 如果推荐失败，返回备用推荐
            available_dishes = self._get_available_dishes()
            return self._generate_fallback_recommendations(available_dishes)
    
    def get_user_recommendations(self, user_id: str, user_request: str, sensor_data: Dict = None) -> Dict:
        """用户模式下的菜品推荐（预留功能）"""
        try:
            # 获取用户信息
            user = self._get_user_by_id(user_id)
            if not user:
                # 如果用户不存在，回退到访客模式
                return self.get_guest_recommendations(user_request, sensor_data)
            
            # 获取所有可用的菜品
            available_dishes = self._get_available_dishes()
            
            # 准备菜品信息字符串
            dishes_str = self._format_dishes_for_llm(available_dishes)
            
            # 格式化用户偏好信息
            user_preferences = self._format_user_preferences(user)
            
            # 获取模拟天气信息
            weather_info = self._get_mock_weather_info()
            
            # 准备完整的prompt文本
            prompt_text = self.recommendation_prompt.format(
                user_request=user_request,
                available_dishes=dishes_str,
                user_preferences=user_preferences,
                sensor_data=sensor_data or {"temperature": 25, "humidity": 50},
                weather_info=weather_info
            )
            
            # 直接调用LLM进行推荐
            result = self.llm.predict(prompt_text)
            
            # 解析JSON结果
            import json
            recommendations = json.loads(result)
            
            # 如果LLM返回的是空推荐，生成一些基于用户偏好的推荐
            if len(recommendations.get("recommendations", [])) == 0:
                recommendations = self._generate_user_based_fallback_recommendations(available_dishes, user)
            
            return recommendations
        except Exception as e:
            print(f"用户模式推荐失败: {e}")
            # 如果推荐失败，返回备用推荐
            available_dishes = self._get_available_dishes()
            user = self._get_user_by_id(user_id) if user_id else None
            if user:
                return self._generate_user_based_fallback_recommendations(available_dishes, user)
            else:
                return self._generate_fallback_recommendations(available_dishes)
    
    def _get_available_dishes(self) -> List[Dish]:
        """获取所有可用的菜品"""
        try:
            dishes_data = self.db.dishes.find({"is_available": True})
            return [Dish.from_dict(dish) for dish in dishes_data]
        except Exception as e:
            print(f"获取可用菜品失败: {e}")
            # 返回模拟菜品数据（用于演示）
            return self._get_mock_dishes()
    
    def _get_mock_dishes(self) -> List[Dish]:
        """获取模拟菜品数据（用于演示）"""
        mock_dishes = [
            {
                "name": "宫保鸡丁",
                "description": "经典川菜，鸡肉搭配花生米和干辣椒",
                "ingredients": ["鸡肉", "花生米", "干辣椒", "黄瓜", "葱姜蒜"],
                "nutrition_info": {"calories": 350, "protein": 25, "carbohydrates": 15, "fat": 20},
                "category": "肉类",
                "spiciness": 3,
                "tags": ["川菜", "高蛋白"]
            },
            {
                "name": "清炒时蔬",
                "description": "新鲜蔬菜清炒，健康营养",
                "ingredients": ["青菜", "胡萝卜", "植物油", "盐"],
                "nutrition_info": {"calories": 80, "protein": 3, "carbohydrates": 10, "fat": 3},
                "category": "蔬菜",
                "spiciness": 0,
                "tags": ["健康", "素食"]
            },
            {
                "name": "番茄鸡蛋汤",
                "description": "家常汤品，酸甜可口",
                "ingredients": ["番茄", "鸡蛋", "葱花", "盐"],
                "nutrition_info": {"calories": 120, "protein": 8, "carbohydrates": 15, "fat": 3},
                "category": "汤品",
                "spiciness": 0,
                "tags": ["清淡", "家常"]
            },
            {
                "name": "麻婆豆腐",
                "description": "川菜名品，豆腐搭配肉末和豆瓣酱",
                "ingredients": ["豆腐", "肉末", "豆瓣酱", "干辣椒", "葱姜蒜"],
                "nutrition_info": {"calories": 280, "protein": 15, "carbohydrates": 10, "fat": 20},
                "category": "豆制品",
                "spiciness": 4,
                "tags": ["川菜", "高蛋白"]
            },
            {
                "name": "扬州炒饭",
                "description": "经典炒饭，配料丰富",
                "ingredients": ["米饭", "火腿", "虾仁", "豌豆", "鸡蛋"],
                "nutrition_info": {"calories": 420, "protein": 15, "carbohydrates": 50, "fat": 15},
                "category": "主食",
                "spiciness": 0,
                "tags": ["主食", "饱腹"]
            }
        ]
        
        return [Dish(**dish) for dish in mock_dishes]
    
    def _format_dishes_for_llm(self, dishes: List[Dish]) -> str:
        """格式化菜品信息，使其适合传递给LLM"""
        formatted_dishes = []
        for dish in dishes:
            dish_info = f"{dish.name}: {dish.description}, 类别: {dish.category}, 辣度: {dish.spiciness}, 热量: {dish.nutrition_info.get('calories', 0)}大卡"
            formatted_dishes.append(dish_info)
        return "\n".join(formatted_dishes)
    
    def _get_user_by_id(self, user_id: str) -> Optional[User]:
        """通过用户ID获取用户信息"""
        try:
            user_data = self.db.users.find_one({"user_id": user_id})
            if user_data:
                return User.from_dict(user_data)
            return None
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return None
    
    def _format_user_preferences(self, user: User) -> str:
        """格式化用户偏好信息"""
        preferences = []
        
        # 饮食限制
        if user.dietary_restrictions:
            preferences.append(f"饮食限制: {', '.join(user.dietary_restrictions)}")
        
        # 喜爱的菜品
        if user.favorite_dishes:
            preferences.append(f"喜爱的菜品ID: {', '.join(user.favorite_dishes)}")
        
        # 其他偏好
        if user.preferences.get("preferred_categories"):
            preferences.append(f"偏好类别: {', '.join(user.preferences['preferred_categories'])}")
        
        if user.preferences.get("disliked_ingredients"):
            preferences.append(f"不喜欢的食材: {', '.join(user.preferences['disliked_ingredients'])}")
        
        if user.preferences.get("max_spiciness") is not None:
            preferences.append(f"最大接受辣度: {user.preferences['max_spiciness']}")
        
        if not preferences:
            return "无特殊偏好"
        
        return "\n".join(preferences)
    
    def _get_mock_weather_info(self) -> str:
        """获取模拟天气信息"""
        # 根据当前时间简单模拟天气
        hour = datetime.now().hour
        if 6 <= hour < 12:
            return "早晨，天气晴朗，温度适宜"
        elif 12 <= hour < 18:
            return "下午，天气较热，可能有些闷热"
        else:
            return "晚上，天气凉爽"
    
    def _generate_fallback_recommendations(self, dishes: List[Dish]) -> Dict:
        """生成备用推荐（当LLM推荐失败时使用）"""
        if not dishes:
            return {"recommendations": [], "total_count": 0}
        
        # 随机选择3-5道菜品
        num_recommendations = min(random.randint(3, 5), len(dishes))
        selected_dishes = random.sample(dishes, num_recommendations)
        
        recommendations = []
        for dish in selected_dishes:
            # 为每道菜品生成一个简单的推荐理由
            reason = f"这道{self._get_category_cn_name(dish.category)}色香味俱全，是今天的人气选择"
            recommendations.append({
                "id": dish.dish_id,
                "name": dish.name,
                "reason": reason
            })
        
        return {"recommendations": recommendations, "total_count": len(recommendations)}
    
    def _generate_user_based_fallback_recommendations(self, dishes: List[Dish], user: User) -> Dict:
        """生成基于用户偏好的备用推荐"""
        if not dishes:
            return {"recommendations": [], "total_count": 0}
        
        # 根据用户偏好过滤菜品
        filtered_dishes = []
        for dish in dishes:
            # 检查辣度
            max_spiciness = user.preferences.get("max_spiciness", 5)
            if dish.spiciness > max_spiciness:
                continue
            
            # 检查饮食限制
            if not self._check_dietary_restrictions(dish, user.dietary_restrictions):
                continue
            
            # 检查不喜欢的食材
            if not self._check_disliked_ingredients(dish, user.preferences.get("disliked_ingredients", [])):
                continue
            
            filtered_dishes.append(dish)
        
        # 如果没有符合条件的菜品，回退到普通随机推荐
        if not filtered_dishes:
            return self._generate_fallback_recommendations(dishes)
        
        # 从符合条件的菜品中选择
        num_recommendations = min(random.randint(3, 5), len(filtered_dishes))
        selected_dishes = random.sample(filtered_dishes, num_recommendations)
        
        recommendations = []
        for dish in selected_dishes:
            reason = f"这道{self._get_category_cn_name(dish.category)}符合您的饮食偏好"
            recommendations.append({
                "id": dish.dish_id,
                "name": dish.name,
                "reason": reason
            })
        
        return {"recommendations": recommendations, "total_count": len(recommendations)}
    
    def _get_category_cn_name(self, category: str) -> str:
        """获取菜品类别的中文名称"""
        category_map = {
            "肉类": "肉类",
            "vegetable": "蔬菜",
            "蔬菜": "蔬菜",
            "主食": "主食",
            "汤品": "汤品",
            "豆制品": "豆制品",
            "其他": "菜品"
        }
        return category_map.get(category, "菜品")
    
    def _check_dietary_restrictions(self, dish: Dish, restrictions: List[str]) -> bool:
        """检查菜品是否符合饮食限制"""
        # 简化实现，实际应用中需要更复杂的检查逻辑
        if not restrictions:
            return True
        
        # 这里只是简单示例，实际应用中需要更精确的食材分析
        for restriction in restrictions:
            if restriction == "vegetarian" or restriction == "素食":
                # 检查是否包含肉类（简化版）
                if "肉类" in dish.category or "chicken" in dish.name.lower() or "beef" in dish.name.lower():
                    return False
            elif restriction == "vegan" or restriction == "纯素":
                # 检查是否包含动物制品
                if "肉类" in dish.category or "鸡蛋" in dish.ingredients or "牛奶" in dish.ingredients:
                    return False
        
        return True
    
    def _check_disliked_ingredients(self, dish: Dish, disliked: List[str]) -> bool:
        """检查菜品是否包含不喜欢的食材"""
        if not disliked:
            return True
        
        for ingredient in dish.ingredients:
            for dislike in disliked:
                if dislike.lower() in ingredient.lower():
                    return False
        
        return True