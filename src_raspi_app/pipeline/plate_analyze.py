import os
import base64
import json
import re
from datetime import datetime, timedelta
import pytz
from bson import ObjectId
from hardware.camera.raspberry_camera import capture_image
from zhipuai import ZhipuAI

# 导入数据库模块
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from database import insert_data, get_db_connection
from utils.user_interaction_logger import interaction_logger
import sys
import os

# Add parent directory to path to import services
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from services.telemetry import send_telemetry

CAMERA_TOKEN = "c1zm08l5c2ko91v785eh"

ZHIPUAI_API_KEY = "e62abd4ebbba488ea4a96771929b6c6d.41RwSM4Nd0Y92AEN"
IMG_DIR = "src_raspi_app/temp/captured_dish"

# 菜品列表提示词
CANTEEN_DISHES_PROMPT = """
Main Dishes (Meat/Poultry):
Braised Pork Chop, Stir-fried Diced Chicken in Soy Bean Paste, Yu-Shiang Shredded Pork, Sweet and Sour Pork Tenderloin, Deep-Fried Pork Strips with Spicy Salt, Braised Chicken Chunks, Chicken Curry, Diced Chicken with Chili Peppers, Kung Pao Chicken, Beef with Black Pepper Sauce, Scallion Beef, Poached Sliced Pork in Hot Chili Oil, Twice-Cooked Pork Slices, Shredded Pork in Beijing Sauce, Steamed Pork with Preserved Mustard Greens, Braised Pork Meatballs (Lion's Head Meatballs), Sweet and Sour Spare Ribs, Fried Shrimp with Spicy Salt, Steamed Fish Fillets, Braised Ribbon Fish
Vegetable Dishes:
Hot and Sour Shredded Potatoes, Mapo Tofu, Scrambled Eggs with Tomatoes, Shredded Potatoes with Green Pepper, Stir-fried Greens with Garlic, Stir-fried Lettuce in Oyster Sauce, Stir-fried Cabbage, Hand-Torn Cabbage Stir-fry, Sautéed Potato, Green Pepper & Eggplant, Pan-Seared Green Peppers, Yu-Shiang Eggplant, Dry-Fried Green Beans, Stir-fried Bean Sprouts, Stir-fried Water Spinach with Garlic, Spinach in Superior Broth
Meat & Vegetable Combos:
Shredded Pork with Green Pepper, Shredded Pork with Celery, Shredded Pork with Garlic Sprouts, Stir-fried Pork with Green Beans, Stir-fried Pork Slices with Wood Ear Mushrooms, Stir-fried Pork Slices with Cauliflower, Stir-fried Pork Slices with Lettuce, Stir-fried Pork Slices with Chinese Yam, Stir-fried Pork Slices with Zucchini, Scrambled Eggs with Cucumber, Scrambled Eggs with Chinese Chives, Stir-fried Beef with Onion, Stir-fried Beef with Green Pepper, Stir-fried Pork Slices with Potato, Stir-fried Pork Slices with Radish
Egg Dishes:
Scrambled Eggs with Tomatoes, Scrambled Eggs with Chinese Chives, Scrambled Eggs with Scallions, Scrambled Eggs with Shrimp, Scrambled Eggs with Wood Ear Mushrooms, Scrambled Eggs with Green Pepper, Scrambled Eggs with Cucumber, Scrambled Eggs with Ham, Steamed Egg Custard, Pan-Fried Sunny-Side-Up Egg
Soups:
Tomato and Egg Drop Soup, Seaweed and Egg Drop Soup, Green Vegetable and Tofu Soup, Winter Melon Soup, Radish Soup, Hot and Sour Soup, Three Delicacies Soup, Pork Rib Soup, Chicken Soup, Fish Head and Tofu Soup
Staples:
Steamed Rice, Steamed Buns, Twisted Steamed Buns, Noodles, Dumplings, Wontons, Fried Rice, Fried Noodles, Fried Rice Noodles, Congee
Cold Dishes:
Smashed Cucumber Salad, Cold Tossed Cucumber, Cold Tossed Wood Ear Mushrooms, Cold Tossed Shredded Kelp, Cold Tossed Tofu Skin, Cold Tossed Three Shreds, Tofu with Century Egg, Pickled Radish in Soy Dressing, Kimchi/Pickled Vegetables, Cold Tossed Bean Thread Noodles"""

def extract_json_from_text(text):
    """从AI响应中提取完整的JSON数据"""
    print("🔍 Extracting JSON from AI response...")
    
    # 清理特殊标记
    cleaned_text = text.replace('<|begin_of_box|>', '').replace('<|end_of_box|>', '').strip()
    print("✅ Removed special markers")
    
    # 尝试直接解析清理后的文本
    try:
        json_data = json.loads(cleaned_text)
        print("✅ Direct JSON parse successful after cleaning")
        return json_data
    except json.JSONDecodeError as e:
        print(f"⚠️ Direct parse failed: {e}")
    
    # 如果直接解析失败，使用正则表达式
    try:
        # 匹配完整的JSON结构
        pattern = r'\{.*\}'
        match = re.search(pattern, cleaned_text, re.DOTALL)
        
        if match:
            json_str = match.group(0)
            json_data = json.loads(json_str)
            print("✅ Regex extraction successful")
            return json_data
    except Exception as e:
        print(f"⚠️ Regex extraction failed: {e}")
    
    return None

def save_user_dish_record(uid, dish_name, timestamp):
    """保存用户菜品记录到MongoDB"""
    try:
        db = get_db_connection()
        user_dishes_col = db["user_dishes"]

        record = {
            "uid": uid,
            "dish_name": dish_name,
            "timestamp": timestamp
        }

        result = user_dishes_col.insert_one(record)
        print(f"✅ Saved user dish record: {uid} - {dish_name}")
        return str(result.inserted_id)

    except Exception as e:
        print(f"❌ Error saving user dish record: {e}")
        return None

def process_ai_response(raw_response, uid):
    """处理AI返回的响应，分离文本和JSON数据"""
    print("🔄 Processing AI response...")
    
    # 清理特殊标记
    cleaned_response = raw_response.replace('<|begin_of_box|>', '').replace('<|end_of_box|>', '').strip()
    
    # 方法1: 尝试找到JSON部分（使用更精确的匹配）
    json_patterns = [
        r'```json\s*(\{.*\})\s*```',  # 匹配 ```json {内容} ```
        r'```\s*(\{.*\})\s*```',      # 匹配 ``` {内容} ```
        r'(\{.*\})'                    # 直接匹配 {内容}
    ]
    
    json_data = None
    user_text_response = cleaned_response
    
    for pattern in json_patterns:
        match = re.search(pattern, cleaned_response, re.DOTALL)
        if match:
            json_str = match.group(1).strip()
            try:
                json_data = json.loads(json_str)
                print("✅ JSON data extracted successfully")
                # 从原始文本中移除JSON部分
                user_text_response = cleaned_response.replace(match.group(0), "").strip()
                break
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parse failed with pattern {pattern}: {e}")
                continue
    
    # 如果没找到有效的JSON，尝试手动解析文本
    if json_data is None:
        print("🔄 Trying to extract dish names from text response...")
        # 从文本响应中提取菜品名称
        dish_names = extract_dish_names_from_text(user_text_response)
        if dish_names:
            json_data = {
                "identified_dishes": [{"name": name, "confidence": 0.9, "description": ""} for name in dish_names]
            }
            print(f"✅ Extracted {len(dish_names)} dishes from text")
    
    # 保存到数据库
    if json_data and 'identified_dishes' in json_data:
        identified_dishes = json_data['identified_dishes']
        # 使用时区感知的当前时间
        local_tz = pytz.timezone('Asia/Shanghai')
        current_time = datetime.now(local_tz)

        saved_count = 0
        for dish in identified_dishes:
            dish_name = dish.get('name')
            if dish_name:
                save_user_dish_record(uid, dish_name, current_time)
                saved_count += 1
        
        print(f"✅ Saved {saved_count} dish records for user {uid}")
    
    # 清理文本响应（移除多余的空行）
    user_text_response = re.sub(r'\n\s*\n', '\n\n', user_text_response).strip()
    
    return user_text_response

def extract_dish_names_from_text(text):
    """从文本响应中提取菜品名称"""
    # 匹配数字列表格式：1. 菜品名 - 描述
    pattern = r'\d+\.\s*([^-—–]+?)(?:\s*[-—–]|\n|$)'
    matches = re.findall(pattern, text)
    
    dish_names = []
    for match in matches:
        dish_name = match.strip()
        if dish_name and len(dish_name) > 1:  # 过滤掉太短的匹配
            dish_names.append(dish_name)
    
    return dish_names

def capture_and_identify_dishes_for_user(uid):
    """为用户拍照识别菜品并保存记录"""

    # Log the start of user dish identification
    interaction_logger.log_user_action(uid, "user_dish_identification_start", "plate_analyze", {
        "process": "user_dish_identification"
    })

    # 1. 调用相机拍照
    print("Starting camera capture...")
    result = capture_image()

    if not result:
        print("Photo capture failed!")
        # Log the failure
        interaction_logger.log_user_action(uid, "user_dish_capture_failed", "plate_analyze", {
            "error": "Camera capture failed"
        })
        return "抱歉，拍照失败，请重试。"

    print(f"Photo captured successfully! File saved at: {result}")

    # Log the successful photo capture
    interaction_logger.log_user_action(uid, "user_dish_capture_success", "plate_analyze", {
        "image_path": result
    })
    
    # 2. 分析图片
    client = ZhipuAI(api_key=ZHIPUAI_API_KEY)
    
    # 读取拍摄的图片
    with open(result, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    
    # 改进的系统提示词（英文）
    system_prompt = f"""You are a helpful food identification assistant. Analyze the food image and identify ALL dishes on the plate.

CRITICAL REQUIREMENTS:
1. You MUST return ONLY valid JSON format, no additional text
2. Use STANDARDIZED dish names from the reference list below
3. The JSON must contain BOTH the structured data AND a user-friendly text response

REFERENCE DISH NAMES (use these EXACT names):
{CANTEEN_DISHES_PROMPT}

STRICT JSON FORMAT (you must return EXACTLY this structure):
{{
    "user_response": "Hello! I've identified the following dishes on your plate:\\n\\n1. Dish Name 1 - Brief introduction\\n2. Dish Name 2 - Brief introduction\\n\\nEnjoy your meal!",
    "dishes": [
        {{
            "name": "Standardized dish name from reference list",
            "confidence": 0.95,
            "description": "Brief description"
        }}
    ]
}}

TEXT RESPONSE GUIDELINES (for the user_response field):
- List all identified dishes clearly with numbers
- Provide brief interesting facts about each dish
- Keep it concise but informative
- Use this exact format with line breaks

IMPORTANT:
- Return ONLY the JSON object, no other text
- No <|begin_of_box|> or <|end_of_box|> markers"""

    try:
        response = client.chat.completions.create(
            model="glm-4.5v",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": "Please analyze this food image and identify all dishes. Return ONLY the JSON object with both the user response in English and the structured dish data. Use exact standardized names from the reference list."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_b64}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.1
        )
        
        result_text = response.choices[0].message.content
        print("📄 Raw AI response received.")
        print("=" * 50)
        print("RAW RESPONSE:")
        print(result_text)
        print("=" * 50)

        # Log the AI response
        interaction_logger.log_pipeline_operation(
            uid,
            "plate_analyze",
            "ai_response_received",
            {"image_path": result},
            {"raw_response_length": len(result_text)},
            success=True
        )

        # 3. 提取和解析JSON数据
        analysis_result = extract_json_from_text(result_text)

        if analysis_result is None:
            print("❌ Failed to extract JSON from response")
            # Log the failure to extract JSON
            interaction_logger.log_pipeline_operation(
                uid,
                "plate_analyze",
                "json_extraction_failed",
                {"raw_response_length": len(result_text)},
                success=False
            )

            # 如果JSON解析失败，尝试从原始文本中处理
            user_response = process_ai_response(result_text, uid)

            # Log the fallback processing
            interaction_logger.log_pipeline_operation(
                uid,
                "plate_analyze",
                "fallback_processing_completed",
                {"raw_response_length": len(result_text)},
                {"user_response_length": len(user_response) if user_response else 0},
                success=True
            )

            return user_response
        
        # 4. 验证数据结构
        if 'user_response' not in analysis_result or 'dishes' not in analysis_result:
            print("❌ Invalid JSON structure")
            # Log the invalid structure
            interaction_logger.log_pipeline_operation(
                uid,
                "plate_analyze",
                "invalid_json_structure",
                {"raw_response_length": len(result_text)},
                {"analysis_result_keys": list(analysis_result.keys()) if analysis_result else []},
                success=False
            )

            user_response = process_ai_response(result_text, uid)
            return user_response

        # 5. 保存菜品记录到数据库
        identified_dishes = analysis_result['dishes']
        # 使用时区感知的当前时间
        local_tz = pytz.timezone('Asia/Shanghai')
        current_time = datetime.now(local_tz)

        saved_count = 0
        for dish in identified_dishes:
            dish_name = dish.get('name')
            if dish_name:
                save_user_dish_record(uid, dish_name, current_time)
                saved_count += 1

        print(f"✅ Saved {saved_count} dish records for user {uid}")

        # Log the successful saving of dish records
        interaction_logger.log_user_dish_analysis(
            uid,
            result,
            {
                "dishes_count": len(identified_dishes),
                "dishes_saved": saved_count,
                "dishes": [dish.get('name') for dish in identified_dishes]
            }
        )

        # Send telemetry for each dish individually
        for dish in identified_dishes:
            telemetry_data = {
                "dish_name": dish.get('name'),
                "confidence": dish.get('confidence'),
                "description": dish.get('description')
            }
            send_telemetry(CAMERA_TOKEN, telemetry_data)
            # Small delay to ensure order if needed, though requests are synchronous
            import time
            time.sleep(0.1)

        # 6. 返回用户文本回复
        user_response = analysis_result['user_response']
        print("📤 Returning text response to user:")
        print(user_response)
        print("=" * 50)

        # Log the successful completion of the process
        interaction_logger.log_user_action(uid, "user_dish_identification_completed", "plate_analyze", {
            "image_path": result,
            "dishes_identified": len(identified_dishes),
            "dishes_saved": saved_count,
            "user_response_length": len(user_response) if user_response else 0
        })

        return user_response

    except Exception as e:
        error_msg = "抱歉，菜品识别暂时不可用，请稍后重试。"
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

        # Log the error during analysis
        interaction_logger.log_user_action(uid, "user_dish_identification_error", "plate_analyze", {
            "error": str(e),
            "error_type": type(e).__name__,
            "image_path": result if 'result' in locals() else "unknown"
        })

        return error_msg

# 使用示例
if __name__ == "__main__":
    print("=== User Dish Identification System ===")
    
    try:
        # 检查数据库连接
        db = get_db_connection()
        print(f"✅ Connected to database: {db.name}")
        
        # 示例UID（8位16进制字符串）
        test_uid = "a1b2c3d4"
        
        # 拍照、识别菜品并返回用户回复
        user_response = capture_and_identify_dishes_for_user(test_uid)
        
        print(f"\n🎉 Final response to user:")
        print("=" * 50)
        print(user_response)
        print("=" * 50)
            
    except Exception as e:
        print(f"❌ System error: {e}")