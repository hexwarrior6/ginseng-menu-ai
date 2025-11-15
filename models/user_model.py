from typing import List, Dict, Optional
from datetime import datetime
import uuid

class User:
    """用户模型类，用于表示系统中的用户信息"""
    
    def __init__(self,
                 user_id: str = None,
                 username: str = "",
                 user_type: str = "guest",  # guest, registered, admin
                 preferences: Dict = None,
                 dietary_restrictions: List[str] = None,
                 favorite_dishes: List[str] = None,
                 created_at: datetime = None,
                 updated_at: datetime = None):
        
        # 基本信息
        self.user_id = user_id or str(uuid.uuid4())
        self.username = username
        self.user_type = user_type  # 访客、注册用户、管理员
        
        # 用户偏好和限制
        self.preferences = preferences or {
            "preferred_categories": [],
            "disliked_ingredients": [],
            "max_spiciness": 5,
            "budget_range": [0, 100],
            "meal_type_preference": "all"  # breakfast, lunch, dinner, all
        }
        
        self.dietary_restrictions = dietary_restrictions or []  # 如vegetarian, vegan, gluten-free等
        self.favorite_dishes = favorite_dishes or []  # 存储dish_id列表
        
        # 时间戳
        current_time = created_at or datetime.now()
        self.created_at = current_time
        self.updated_at = updated_at or current_time
    
    def to_dict(self) -> Dict:
        """将对象转换为字典格式，用于存储到数据库"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "user_type": self.user_type,
            "preferences": self.preferences,
            "dietary_restrictions": self.dietary_restrictions,
            "favorite_dishes": self.favorite_dishes,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """从字典创建对象，用于从数据库读取数据"""
        return cls(
            user_id=data.get("user_id"),
            username=data.get("username", ""),
            user_type=data.get("user_type", "guest"),
            preferences=data.get("preferences", {}),
            dietary_restrictions=data.get("dietary_restrictions", []),
            favorite_dishes=data.get("favorite_dishes", []),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    
    def update_preferences(self, preferences: Dict):
        """更新用户偏好"""
        self.preferences.update(preferences)
        self.updated_at = datetime.now()
    
    def add_dietary_restriction(self, restriction: str):
        """添加饮食限制"""
        if restriction not in self.dietary_restrictions:
            self.dietary_restrictions.append(restriction)
            self.updated_at = datetime.now()
    
    def remove_dietary_restriction(self, restriction: str):
        """移除饮食限制"""
        if restriction in self.dietary_restrictions:
            self.dietary_restrictions.remove(restriction)
            self.updated_at = datetime.now()
    
    def add_favorite_dish(self, dish_id: str):
        """添加喜爱的菜品"""
        if dish_id not in self.favorite_dishes:
            self.favorite_dishes.append(dish_id)
            self.updated_at = datetime.now()
    
    def remove_favorite_dish(self, dish_id: str):
        """移除喜爱的菜品"""
        if dish_id in self.favorite_dishes:
            self.favorite_dishes.remove(dish_id)
            self.updated_at = datetime.now()

class OrderHistory:
    """订单历史模型类，用于记录用户的订单信息"""
    
    def __init__(self,
                 order_id: str = None,
                 user_id: str = None,
                 dish_ids: List[str] = None,
                 order_time: datetime = None,
                 total_amount: float = 0.0,
                 special_requests: str = ""):
        
        self.order_id = order_id or str(uuid.uuid4())
        self.user_id = user_id
        self.dish_ids = dish_ids or []
        self.order_time = order_time or datetime.now()
        self.total_amount = total_amount
        self.special_requests = special_requests
    
    def to_dict(self) -> Dict:
        """将对象转换为字典格式"""
        return {
            "order_id": self.order_id,
            "user_id": self.user_id,
            "dish_ids": self.dish_ids,
            "order_time": self.order_time,
            "total_amount": self.total_amount,
            "special_requests": self.special_requests
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'OrderHistory':
        """从字典创建对象"""
        return cls(
            order_id=data.get("order_id"),
            user_id=data.get("user_id"),
            dish_ids=data.get("dish_ids", []),
            order_time=data.get("order_time"),
            total_amount=data.get("total_amount", 0.0),
            special_requests=data.get("special_requests", "")
        )