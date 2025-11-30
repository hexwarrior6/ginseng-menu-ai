#!/usr/bin/env python3
"""
语音识别结果处理模块
将语音识别结果传递给大模型进行处理
"""

import logging
import re
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, date
import pytz
from services.llm_service import ask_llm
from database.db_connection import get_db_connection


def process_speech_to_llm(speech_text: str, uid: Optional[str] = None) -> Optional[str]:
    """
    处理语音识别结果并传递给大模型

    Args:
        speech_text: 语音识别得到的文本
        uid: 用户的唯一标识符（可选），用于获取用户资料

    Returns:
        str: 大模型处理结果，如果处理失败则返回 None
    """
    if not speech_text or not speech_text.strip():
        logging.warning("语音识别结果为空，跳过大模型处理")
        return None

    try:
        # 获取用户资料（如果提供了uid）
        user_profile = None
        if uid:
            user_profile = _get_user_profile_by_uid(uid)

        # 获取当天菜单
        today_menu = _get_today_menu()
        menu_info_str = _format_menu_info(today_menu)

        # 构造提示词，包含用户资料和菜单信息（如果可用）
        if user_profile:
            # 将用户资料转换为文本格式
            user_info_str = _format_user_profile(user_profile)
            prompt = f"Today's menu information: {menu_info_str}\n\nUser profile information: {user_info_str}\n\nUser voice input:{speech_text}\n\nBased on today's menu, user's profile and voice input, please provide appropriate responses or perform corresponding actions. Also, extract relevant information from the user's input and return it in JSON format at the end of your response. Format: {{\"dietary_restrictions\": [], \"favorite_cuisines\": [], \"favorite_foods\": [], \"allergies\": [], \"preferences\": []}} (Do not exceed 50 words except for JSON)"
        else:
            prompt = f"Today's menu information: {menu_info_str}\n\nUser voice input:{speech_text}\n\nPlease provide appropriate responses or perform corresponding actions based on today's menu and user's voice input. Also, extract relevant information from the user's input and return it in JSON format at the end of your response. Format: {{\"dietary_restrictions\": [], \"favorite_cuisines\": [], \"favorite_foods\": [], \"allergies\": [], \"preferences\": []}} (Do not exceed 50 words total)"

        logging.info(f"向大模型发送请求: {speech_text}")

        # 调用大模型服务
        result = ask_llm(prompt)
        logging.info(f"大模型返回结果: {result}")

        if result:
            # 提取JSON数据并更新用户偏好
            extracted_preferences = _extract_json_from_response(result)
            if extracted_preferences and uid:
                _update_user_preferences(uid, extracted_preferences)

            # 使用正则表达式提取并移除JSON部分
            result_without_json = _remove_json_from_response(result)
            return result_without_json

        return result
    except Exception as e:
        logging.error(f"处理语音识别结果时发生错误: {e}")
        return None


def _get_user_profile_by_uid(uid: str) -> Optional[dict]:
    """
    根据uid从数据库中获取用户资料

    Args:
        uid: 用户的唯一标识符

    Returns:
        dict: 用户资料，如果未找到则返回None
    """
    try:
        db = get_db_connection()
        users_collection = db['users']

        # 根据uid查找用户
        user = users_collection.find_one({"uid": uid})
        return user
    except Exception as e:
        logging.error(f"从数据库获取用户资料时发生错误: {e}")
        return None


def _get_today_menu() -> List[Dict[str, Any]]:
    """
    获取当天的所有菜单

    Returns:
        list: 当天菜单列表，如果获取失败则返回空列表
    """
    try:
        db = get_db_connection()
        dishes_collection = db['dishes']

        # 使用时区感知的当前时间
        local_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(local_tz)
        today = now.date()

        # 获取当天的开始和结束时间（时区感知）
        start_of_day = local_tz.localize(datetime.combine(today, datetime.min.time()))
        end_of_day = local_tz.localize(datetime.combine(today, datetime.max.time()))

        # 查询当天的所有菜单，转换为UTC时间进行查询
        today_menu = list(dishes_collection.find({
            "timestamp": {
                "$gte": start_of_day.astimezone(pytz.UTC),
                "$lte": end_of_day.astimezone(pytz.UTC)
            }
        }))

        logging.info(f"获取到 {len(today_menu)} 个今日菜品")
        return today_menu

    except Exception as e:
        logging.error(f"获取当天菜单时发生错误: {e}")
        return []


def _format_menu_info(menu_items: List[Dict[str, Any]]) -> str:
    """
    将菜单信息格式化为文本字符串

    Args:
        menu_items: 菜单项列表

    Returns:
        str: 格式化后的菜单信息文本
    """
    if not menu_items:
        return "No menu available for today."
    
    menu_str = "Today's menu includes: "
    dish_descriptions = []
    
    for dish in menu_items:
        name = dish.get('name', 'Unknown dish')
        category = dish.get('category', 'Unknown category')
        calories = dish.get('calories', 0)
        
        # 构建营养信息
        nutrition = dish.get('nutrition', {})
        nutrition_info = []
        if 'protein_g' in nutrition:
            nutrition_info.append(f"{nutrition['protein_g']}g protein")
        if 'carbs_g' in nutrition:
            nutrition_info.append(f"{nutrition['carbs_g']}g carbs")
        if 'fat_g' in nutrition:
            nutrition_info.append(f"{nutrition['fat_g']}g fat")
        
        dish_desc = f"{name} ({category}, {calories} calories"
        if nutrition_info:
            dish_desc += f", {', '.join(nutrition_info)}"
        dish_desc += ")"
        
        dish_descriptions.append(dish_desc)
    
    menu_str += "; ".join(dish_descriptions)
    return menu_str


def _format_user_profile(user_profile: dict) -> str:
    """
    将用户资料格式化为文本字符串

    Args:
        user_profile: 用户资料字典

    Returns:
        str: 格式化后的用户资料文本
    """
    if not user_profile:
        return ""

    profile_str = f"UID: {user_profile.get('uid', 'N/A')}"

    preferences = user_profile.get('preferences', {})
    if preferences:
        dietary = preferences.get('dietary_restrictions', [])
        if dietary:
            profile_str += f", Dietary Restrictions: {', '.join(dietary)}"

        cuisines = preferences.get('favorite_cuisines', [])
        if cuisines:
            profile_str += f", Favorite Cuisines: {', '.join(cuisines)}"

        foods = preferences.get('favorite_foods', [])
        if foods:
            profile_str += f", Favorite Foods: {', '.join(foods)}"

        allergies = preferences.get('allergies', [])
        if allergies:
            profile_str += f", Allergies: {', '.join(allergies)}"

    return profile_str


def _extract_json_from_response(response: str) -> Optional[Dict[str, Any]]:
    """
    从大模型响应中提取JSON数据

    Args:
        response: 大模型的原始响应

    Returns:
        dict: 提取的JSON数据，如果提取失败则返回None
    """
    try:
        # 使用正则表达式匹配JSON对象
        json_pattern = r'\{[^{}]*\}(?:\s*\{[^{}]*\})*'
        json_matches = re.findall(json_pattern, response)
        
        if not json_matches:
            return None
            
        # 尝试解析最后一个JSON对象（通常是最新的）
        for json_str in reversed(json_matches):
            try:
                data = json.loads(json_str)
                # 验证是否包含预期的字段
                expected_fields = ['dietary_restrictions', 'favorite_cuisines', 'favorite_foods', 'allergies', 'preferences']
                if any(key in data for key in expected_fields):
                    return data
            except json.JSONDecodeError:
                continue
                
        return None
    except Exception as e:
        logging.error(f"提取JSON数据时发生错误: {e}")
        return None


def _update_user_preferences(uid: str, preferences_data: Dict[str, Any]) -> bool:
    """
    更新用户偏好信息到数据库，按照示例的文档结构存储

    Args:
        uid: 用户ID
        preferences_data: 从大模型响应中提取的偏好数据

    Returns:
        bool: 更新成功返回True，否则返回False
    """
    try:
        db = get_db_connection()
        users_collection = db['users']
        
        # 检查用户是否存在
        existing_user = users_collection.find_one({"uid": uid})
        
        # 构建preferences对象，按照示例的结构
        preferences_update = {}
        
        # 处理饮食限制
        dietary_restrictions = _extract_preference_list(preferences_data, 'dietary_restrictions')
        if dietary_restrictions:
            preferences_update['dietary_restrictions'] = dietary_restrictions
        
        # 处理喜欢的菜系
        favorite_cuisines = _extract_preference_list(preferences_data, 'favorite_cuisines')
        if favorite_cuisines:
            preferences_update['favorite_cuisines'] = favorite_cuisines
        
        # 处理喜欢的菜品（新增）
        favorite_foods = _extract_preference_list(preferences_data, 'favorite_foods')
        if favorite_foods:
            preferences_update['favorite_foods'] = favorite_foods
        
        # 处理过敏信息
        allergies = _extract_preference_list(preferences_data, 'allergies')
        if allergies:
            preferences_update['allergies'] = allergies
        
        # 处理偏好信息
        preferences = _extract_preference_list(preferences_data, 'preferences')
        if preferences:
            preferences_update['preferences'] = preferences
        
        if existing_user:
            # 更新现有用户 - 合并偏好信息
            current_preferences = existing_user.get('preferences', {})
            
            # 合并每个偏好类别
            for key, new_values in preferences_update.items():
                if isinstance(new_values, list) and new_values:
                    current_values = current_preferences.get(key, [])
                    # 添加新值并去重
                    for value in new_values:
                        if value and value not in current_values:
                            current_values.append(value)
                    current_preferences[key] = current_values
            
            # 使用时区感知的当前时间
            local_tz = pytz.timezone('Asia/Shanghai')
            current_time = datetime.now(local_tz)

            update_data = {
                "preferences": current_preferences,
                "last_active": current_time
            }
            
            result = users_collection.update_one(
                {"uid": uid},
                {"$set": update_data}
            )
            success = result.modified_count > 0
            
            if success:
                logging.info(f"✅ 用户 {uid} 偏好更新成功")
                logging.info(f"📊 更新后的偏好: {current_preferences}")
            else:
                logging.info(f"ℹ️ 用户 {uid} 偏好无变化或已是最新")
                
        else:
            # 使用时区感知的当前时间
            local_tz = pytz.timezone('Asia/Shanghai')
            current_time = datetime.now(local_tz)

            # 创建新用户 - 按照示例的文档结构
            user_data = {
                "uid": uid,
                "preferences": preferences_update,
                "created_at": current_time,
                "last_active": current_time
            }

            result = users_collection.insert_one(user_data)
            success = result.inserted_id is not None
            
            if success:
                logging.info(f"✅ 新用户 {uid} 创建成功，偏好信息已保存")
                logging.info(f"📊 用户偏好: {preferences_update}")
            else:
                logging.error(f"❌ 创建新用户 {uid} 失败")
        
        return success
        
    except Exception as e:
        logging.error(f"更新用户偏好时发生错误: {e}")
        return False


def _extract_preference_list(data: Dict[str, Any], key: str) -> List[str]:
    """
    从数据中提取偏好列表，支持嵌套结构

    Args:
        data: 原始数据
        key: 要提取的键名

    Returns:
        list: 提取的偏好列表
    """
    result = []
    
    # 首先检查preferences字段内
    if 'preferences' in data and isinstance(data['preferences'], dict):
        if key in data['preferences'] and isinstance(data['preferences'][key], list):
            result.extend([item for item in data['preferences'][key] if item])
    
    # 然后检查根级别
    if key in data and isinstance(data[key], list):
        result.extend([item for item in data[key] if item])
    
    return result


def _remove_json_from_response(response: str) -> str:
    """
    从大模型响应中移除JSON部分

    Args:
        response: 大模型的原始响应

    Returns:
        str: 移除了JSON部分的响应
    """
    # 使用正则表达式匹配JSON对象
    json_pattern = r'\{[^{}]*\}(?:\s*\{[^{}]*\})*'

    # 查找所有JSON对象
    json_matches = re.findall(json_pattern, response)

    # 如果找到JSON对象，则从响应中移除它们
    result = response
    for json_match in json_matches:
        result = result.replace(json_match, '').strip()

    # 清理多余的空行和空格
    result = re.sub(r'\n\s*\n', '\n', result)  # 替换多个空行为单个换行
    result = result.strip()

    return result


def process_command_speech_to_llm(speech_text: str, command_context: Optional[str] = None, uid: Optional[str] = None) -> Optional[str]:
    """
    处理语音识别结果并传递给大模型，支持命令上下文

    Args:
        speech_text: 语音识别得到的文本
        command_context: 命令上下文（可选）
        uid: 用户的唯一标识符（可选），用于获取用户资料

    Returns:
        str: 大模型处理结果，如果处理失败则返回 None
    """
    if not speech_text or not speech_text.strip():
        logging.warning("语音识别结果为空，跳过大模型处理")
        return None

    try:
        # 获取用户资料（如果提供了uid）
        user_profile = None
        if uid:
            user_profile = _get_user_profile_by_uid(uid)

        # 获取当天菜单
        today_menu = _get_today_menu()
        menu_info_str = _format_menu_info(today_menu)

        # 构造提示词，包含用户资料和菜单信息（如果可用）
        if user_profile:
            user_info_str = _format_user_profile(user_profile)
            if command_context:
                prompt = f"Today's menu information: {menu_info_str}\n\nUser profile information: {user_info_str}\n\nIn the context of {command_context}, user voice input: {speech_text}\n\nBased on today's menu, user's profile and input, provide an appropriate response or perform the corresponding action. Also, extract relevant information from the user's input and return it in JSON format at the end of your response. Format: {{\"dietary_restrictions\": [], \"favorite_cuisines\": [], \"favorite_foods\": [], \"allergies\": [], \"preferences\": []}}"
            else:
                prompt = f"Today's menu information: {menu_info_str}\n\nUser profile information: {user_info_str}\n\nUser voice input: {speech_text}\n\nBased on today's menu, user's profile and input, provide an appropriate response or perform the corresponding action. Also, extract relevant information from the user's input and return it in JSON format at the end of your response. Format: {{\"dietary_restrictions\": [], \"favorite_cuisines\": [], \"favorite_foods\": [], \"allergies\": [], \"preferences\": []}}"
        else:
            if command_context:
                prompt = f"Today's menu information: {menu_info_str}\n\nIn the context of {command_context}, user voice input: {speech_text}\n\nProvide an appropriate response or perform the corresponding action based on today's menu. Also, extract relevant information from the user's input and return it in JSON format at the end of your response. Format: {{\"dietary_restrictions\": [], \"favorite_cuisines\": [], \"favorite_foods\": [], \"allergies\": [], \"preferences\": []}}"
            else:
                prompt = f"Today's menu information: {menu_info_str}\n\nUser voice input: {speech_text}\n\nProvide an appropriate response or perform the corresponding action based on today's menu. Also, extract relevant information from the user's input and return it in JSON format at the end of your response. Format: {{\"dietary_restrictions\": [], \"favorite_cuisines\": [], \"favorite_foods\": [], \"allergies\": [], \"preferences\": []}}"

        # 调用大模型服务
        result = ask_llm(prompt)
        logging.info(f"大模型返回结果: {result}")

        if result:
            # 提取JSON数据并更新用户偏好
            extracted_preferences = _extract_json_from_response(result)
            if extracted_preferences and uid:
                _update_user_preferences(uid, extracted_preferences)

            # 使用正则表达式提取并移除JSON部分
            result_without_json = _remove_json_from_response(result)
            return result_without_json

        return result
    except Exception as e:
        logging.error(f"处理语音识别结果时发生错误: {e}")
        return None


# 示例函数，展示完整的文档结构
def example_insert_dish():
    """
    示例：插入菜品数据
    """
    print("=== Insert Dish Example ===")
    
    dish_data = {
        "name": "Pad Thai",
        "category": "Thai",
        "timestamp": datetime.now(),
        "calories": 490,
        "nutrition": {
            "protein_g": 15, 
            "carbs_g": 70, 
            "fat_g": 18
        }
    }
    
    print(f"✅ 示例菜品数据: {dish_data}")
    return dish_data