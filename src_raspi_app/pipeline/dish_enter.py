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
    """从AI响应中提取完整的JSON数据，处理特殊标记"""
    print("🔍 Extracting JSON from AI response...")
    
    # 首先清理特殊标记
    cleaned_text = text.replace('<|begin_of_box|>', '').replace('<|end_of_box|>', '').strip()
    print("✅ Removed special markers")
    
    # 尝试直接解析清理后的文本
    try:
        json_data = json.loads(cleaned_text)
        print("✅ Direct JSON parse successful after cleaning")
        return json_data
    except json.JSONDecodeError as e:
        print(f"⚠️ Direct parse failed: {e}")
    
    # 如果直接解析失败，使用改进的正则表达式
    try:
        # 匹配完整的dishes数组结构
        pattern = r'"dishes"\s*:\s*\[.*\]'
        match = re.search(pattern, cleaned_text, re.DOTALL)
        
        if match:
            # 提取dishes数组部分
            dishes_part = match.group(0)
            # 构建完整的JSON对象
            full_json_str = '{' + dishes_part + '}'
            json_data = json.loads(full_json_str)
            print("✅ Regex extraction successful")
            return json_data
    except Exception as e:
        print(f"⚠️ Regex extraction failed: {e}")
    
    # 最后尝试：手动解析
    return manual_json_extraction(cleaned_text)

def manual_json_extraction(text):
    """手动解析JSON数据"""
    print("🔄 Trying manual JSON parsing...")
    
    try:
        # 查找dishes数组的开始
        dishes_start = text.find('"dishes":')
        if dishes_start == -1:
            print("❌ 'dishes' field not found")
            return None
        
        # 找到数组开始位置
        array_start = text.find('[', dishes_start)
        if array_start == -1:
            print("❌ Array start not found")
            return None
        
        # 手动解析数组
        bracket_count = 1
        i = array_start + 1
        while i < len(text) and bracket_count > 0:
            if text[i] == '[':
                bracket_count += 1
            elif text[i] == ']':
                bracket_count -= 1
            i += 1
        
        if bracket_count == 0:
            # 提取完整的dishes数组部分
            dishes_array_str = text[array_start:i]
            full_json_str = '{"dishes": ' + dishes_array_str + '}'
            
            # 验证和修复可能的JSON格式问题
            full_json_str = full_json_str.replace('\\n', '').replace('\\t', '').strip()
            
            json_data = json.loads(full_json_str)
            print("✅ Manual extraction successful")
            return json_data
        else:
            print("❌ Unbalanced brackets in manual extraction")
            
    except Exception as e:
        print(f"❌ Manual extraction failed: {e}")
        import traceback
        traceback.print_exc()
    
    return None

def check_existing_dish(name):
    """检查当天是否已经存在相同名称的菜品（MongoDB 版）"""
    try:
        db = get_db_connection()
        dishes = db["dishes"]

        # 使用时区感知的当前时间
        local_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(local_tz)

        # 获取当天的开始和结束时间（时区感知）
        start_of_day = local_tz.localize(datetime(now.year, now.month, now.day))
        end_of_day = start_of_day + timedelta(days=1)

        result = dishes.find_one({
            "name": name,
            "timestamp": {"$gte": start_of_day.astimezone(pytz.UTC), "$lt": end_of_day.astimezone(pytz.UTC)}
        })

        return result["_id"] if result else None

    except Exception as e:
        print(f"❌ Error checking existing dish: {e}")
        return None
    
def save_dishes_to_database(dishes_data):
    try:
        db = get_db_connection()
        dishes_col = db["dishes"]

        saved_ids = []
        dishes_list = dishes_data.get('dishes', [])

        # 使用时区感知的当前时间
        local_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(local_tz)

        for dish in dishes_list:
            name = dish.get('name')
            existing_id = check_existing_dish(name)

            # 构建要保存的数据
            record = {
                "name": name,
                "category": dish.get("category"),
                "timestamp": now,  # 这里会被db_connection.py中的convert_datetime_to_utc函数转换为UTC
                "calories": int(float(dish.get("calories", 0))),
                "nutrition": {
                    "protein_g": float(dish.get("nutrition", {}).get("protein_g", 0)),
                    "carbs_g": float(dish.get("nutrition", {}).get("carbs_g", 0)),
                    "fat_g": float(dish.get("nutrition", {}).get("fat_g", 0)),
                    "fiber_g": float(dish.get("nutrition", {}).get("fiber_g", 0)),
                },
            }

            if existing_id:
                # === 已存在：先删掉旧记录，再插入新记录 ===
                dishes_col.delete_one({"_id": ObjectId(existing_id)})
                print(f"  🔄 Deleted old dish ID {existing_id}")

            # 插入新记录 - 使用封装的insert_data函数，会自动处理时区转换
            from database.db_connection import insert_data
            result_id = insert_data("dishes", record)
            if result_id:
                print(f"  ✅ Inserted new dish '{name}' with ID {result_id}")
                saved_ids.append(result_id)
            else:
                print(f"  ❌ Failed to insert dish '{name}'")

        return saved_ids

    except Exception as e:
        print(f"❌ Error saving dishes: {e}")
        return []
    
def capture_and_analyze_dishes():
    """拍照并分析多个菜品，返回JSON格式的结构化数据并自动保存到数据库"""

    # Log the start of dish capture and analysis
    interaction_logger.log_user_action("system", "dish_capture_start", "dish_enter", {
        "process": "dish_capture_analysis"
    })

    # 1. 调用相机拍照
    print("Starting camera capture...")
    result = capture_image()

    if not result:
        print("Photo capture failed!")
        # Log the failure
        interaction_logger.log_user_action("system", "dish_capture_failed", "dish_enter", {
            "error": "Camera capture failed",
            "image_path": result
        })
        return None

    print(f"Photo captured successfully! File saved at: {result}")

    # Log the successful photo capture
    interaction_logger.log_user_action("system", "dish_capture_success", "dish_enter", {
        "image_path": result
    })

    # 2. 分析图片
    client = ZhipuAI(api_key=ZHIPUAI_API_KEY)

    # 读取拍摄的图片
    with open(result, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    
    # 修改后的系统提示词，添加菜品名称标准化要求
    system_prompt = f"""You are a professional food nutrition analysis system. Analyze ALL visible dishes in the image and return STRICT JSON format.

CRITICAL REQUIREMENTS:
1. You MUST identify MULTIPLE dishes if present
2. Use STANDARDIZED dish names from the reference list below
3. If a dish matches multiple names, choose the MOST SPECIFIC and STANDARD name
4. Return EXACTLY this format without any additional text or markers:

REFERENCE DISH NAMES (use these EXACT names when matching):
{CANTEEN_DISHES_PROMPT}

STANDARDIZATION RULES:
- For "Scrambled Eggs with Tomatoes", NOT "Tomato Scrambled Eggs" or "Eggs with Tomato"
- For "Yu-Shiang Shredded Pork", NOT "Yuxiang Pork" or "Fish-Flavored Shredded Pork"  
- For "Braised Pork Chop", NOT "Stewed Pork Chop" or "Red-Cooked Pork Chop"
- Use the EXACT names from the reference list above

RETURN FORMAT:
{{
    "dishes": [
        {{
            "name": "Standardized dish name from reference list",
            "category": "Cuisine type",
            "calories": 400,
            "nutrition": {{
                "protein_g": 25,
                "carbs_g": 45,
                "fat_g": 15,
                "fiber_g": 5
            }},
            "ingredients": ["ingredient1", "ingredient2"],
            "confidence": 0.9
        }}
    ]
}}

IMPORTANT:
- Do NOT include <|begin_of_box|> or <|end_of_box|> markers
- Return PURE JSON only, no other text
- Include ALL dishes you see in the image
- Use STANDARDIZED names to ensure consistency across multiple recordings"""

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
                            "text": "Analyze this food image. Identify EVERY dish you see using STANDARDIZED names from the reference list. Return only PURE JSON with all dishes in the 'dishes' array. Do not include any markers or additional text. CRITICAL: Use exact standardized names to avoid duplicate entries for the same dish."
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
            "system",
            "dish_enter",
            "ai_response_received",
            {"image_path": result},
            {"raw_response_length": len(result_text)},
            success=True
        )

        # 使用改进的JSON提取
        analysis_result = extract_json_from_text(result_text)

        if analysis_result is None:
            print("❌ Failed to extract JSON from response")
            # 保存原始响应以便调试
            with open("debug_raw_response.txt", "w", encoding="utf-8") as f:
                f.write(result_text)
            print("💾 Raw response saved to debug_raw_response.txt for analysis")

            # Log the failure to extract JSON
            interaction_logger.log_pipeline_operation(
                "system",
                "dish_enter",
                "json_extraction_failed",
                {"raw_response_length": len(result_text)},
                success=False
            )

            return None
        
        # 调试：打印提取的结果结构
        print("🔍 Extracted JSON structure:")
        print(json.dumps(analysis_result, ensure_ascii=False, indent=2))
        
        # 验证数据结构
        if 'dishes' not in analysis_result:
            print("❌ Invalid structure: missing 'dishes' field")
            return None
        
        if not isinstance(analysis_result['dishes'], list):
            print("❌ Invalid structure: 'dishes' is not a list")
            return None
        
        # 验证和清理数据
        valid_dishes = []
        for i, dish in enumerate(analysis_result['dishes']):
            if isinstance(dish, dict) and dish.get('name'):
                # 确保数值字段格式正确
                try:
                    dish['calories'] = int(float(dish.get('calories', 0)))
                    if 'nutrition' not in dish:
                        dish['nutrition'] = {}
                    for nutrient in ['protein_g', 'carbs_g', 'fat_g', 'fiber_g']:
                        dish['nutrition'][nutrient] = round(float(dish['nutrition'].get(nutrient, 0)), 1)
                    valid_dishes.append(dish)
                    print(f"✅ Validated dish {i+1}: {dish.get('name')}")
                except (ValueError, TypeError) as e:
                    print(f"⚠️ Skipped dish {i+1} due to data error: {e}")
            else:
                print(f"⚠️ Skipped invalid dish {i+1}: {dish}")
        
        analysis_result['dishes'] = valid_dishes
        
        print(f"\n✅ Dish analysis completed! Found {len(valid_dishes)} valid dishes")
        
        # 3. 自动保存到数据库（包含重复检查逻辑）
        if valid_dishes:
            # Log the dish analysis result before saving
            interaction_logger.log_pipeline_operation(
                "system",
                "dish_enter",
                "dishes_analyzed",
                {"image_path": result, "valid_dishes_count": len(valid_dishes)},
                {"dishes": [dish.get('name', 'Unknown') for dish in valid_dishes]},
                success=True
            )

            saved_ids = save_dishes_to_database(analysis_result)
            if saved_ids:
                print(f"🎉 Successfully processed {len(saved_ids)} dishes to database!")
                # Log the successful database save
                interaction_logger.log_pipeline_operation(
                    "system",
                    "dish_enter",
                    "dishes_saved_to_db",
                    {"dishes_count": len(valid_dishes)},
                    {"saved_ids": saved_ids},
                    success=True
                )
            else:
                print("⚠️ Analysis completed but failed to save any dishes to database")
                # Log the failure to save to database
                interaction_logger.log_pipeline_operation(
                    "system",
                    "dish_enter",
                    "dishes_save_to_db_failed",
                    {"dishes_count": len(valid_dishes)},
                    success=False
                )
        else:
            print("❌ No valid dishes found to save")
            # Log that no valid dishes were found
            interaction_logger.log_user_action("system", "no_valid_dishes_found", "dish_enter", {
                "image_path": result,
                "total_dishes_found": len(analysis_result.get('dishes', [])),
                "valid_dishes_count": 0
            })

        # Log the completion of the dish capture and analysis process
        interaction_logger.log_user_action("system", "dish_capture_analysis_completed", "dish_enter", {
            "image_path": result,
            "valid_dishes_count": len(valid_dishes),
            "dishes_saved_count": len(saved_ids) if saved_ids else 0
        })

        # Send telemetry
        send_telemetry(CAMERA_TOKEN, analysis_result)

        return analysis_result

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

        # Log the error during analysis
        interaction_logger.log_user_action("system", "dish_capture_analysis_error", "dish_enter", {
            "error": str(e),
            "error_type": type(e).__name__,
            "image_path": result if 'result' in locals() else "unknown"
        })

        return None

# 使用示例
if __name__ == "__main__":
    print("=== Multi-Dish Food Recognition System ===")
    
    try:
        # 检查数据库连接
        db = get_db_connection()
        print(f"✅ Connected to database: {db.name}")
        
        # 拍照、分析并自动保存到数据库
        result = capture_and_analyze_dishes()
        
        if result and result.get('dishes'):
            print(f"\n🎉 Success! Analyzed {len(result.get('dishes', []))} dishes:")
            
            for i, dish in enumerate(result['dishes']):
                print(f"\nDish {i+1}:")
                print(f"  Name: {dish.get('name', 'Unknown')}")
                print(f"  Category: {dish.get('category', 'Unknown')}")
                print(f"  Calories: {dish.get('calories', 0)}")
                print(f"  Protein: {dish['nutrition'].get('protein_g', 0)}g")
                print(f"  Carbs: {dish['nutrition'].get('carbs_g', 0)}g")
                print(f"  Fat: {dish['nutrition'].get('fat_g', 0)}g")
                print(f"  Fiber: {dish['nutrition'].get('fiber_g', 0)}g")
                
        else:
            print("\n❌ Analysis failed or no dishes found!")
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")