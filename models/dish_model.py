from typing import List, Dict, Optional
from datetime import datetime
import uuid

class Dish:
    """菜品模型类，用于表示食堂中的菜品信息"""
    
    def __init__(self,
                 name: str,
                 description: str = "",
                 ingredients: List[str] = None,
                 nutrition_info: Dict = None,
                 category: str = "",
                 price: float = 0.0,
                 spiciness: int = 0,  # 0-5表示辣度
                 tags: List[str] = None,
                 image_path: str = "",
                 is_available: bool = True,
                 created_at: datetime = None,
                 updated_at: datetime = None,
                 dish_id: str = None):
        
        # 基本信息
        self.dish_id = dish_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.category = category
        self.price = price
        self.is_available = is_available
        
        # 成分和营养信息
        self.ingredients = ingredients or []
        self.nutrition_info = nutrition_info or {
            "calories": 0,
            "protein": 0,
            "carbohydrates": 0,
            "fat": 0,
            "fiber": 0,
            "sugar": 0,
            "sodium": 0
        }
        
        # 其他属性
        self.spiciness = spiciness  # 0-5表示辣度
        self.tags = tags or []
        self.image_path = image_path
        
        # 时间戳
        current_time = created_at or datetime.now()
        self.created_at = current_time
        self.updated_at = updated_at or current_time
    
    def to_dict(self) -> Dict:
        """将对象转换为字典格式，用于存储到数据库"""
        return {
            "dish_id": self.dish_id,
            "name": self.name,
            "description": self.description,
            "ingredients": self.ingredients,
            "nutrition_info": self.nutrition_info,
            "category": self.category,
            "price": self.price,
            "spiciness": self.spiciness,
            "tags": self.tags,
            "image_path": self.image_path,
            "is_available": self.is_available,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Dish':
        """从字典创建对象，用于从数据库读取数据"""
        return cls(
            dish_id=data.get("dish_id"),
            name=data.get("name"),
            description=data.get("description", ""),
            ingredients=data.get("ingredients", []),
            nutrition_info=data.get("nutrition_info", {}),
            category=data.get("category", ""),
            price=data.get("price", 0.0),
            spiciness=data.get("spiciness", 0),
            tags=data.get("tags", []),
            image_path=data.get("image_path", ""),
            is_available=data.get("is_available", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    
    def update_nutrition_info(self, nutrition_data: Dict):
        """更新菜品的营养信息"""
        self.nutrition_info.update(nutrition_data)
        self.updated_at = datetime.now()
    
    def update_availability(self, is_available: bool):
        """更新菜品的可用性"""
        self.is_available = is_available
        self.updated_at = datetime.now()