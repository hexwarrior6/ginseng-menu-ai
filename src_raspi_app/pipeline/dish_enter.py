import os
import base64
import json
import re
from datetime import datetime
from hardware.camera.raspberry_camera import capture_image
from zhipuai import ZhipuAI

# 导入数据库模块
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from database import insert_data, get_db_connection

ZHIPUAI_API_KEY = "e62abd4ebbba488ea4a96771929b6c6d.41RwSM4Nd0Y92AEN"
IMG_DIR = "src_raspi_app/temp/captured_dish"

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

def save_dishes_to_database(dishes_data):
    """将菜品数据逐个保存到数据库"""
    try:
        saved_ids = []
        dishes_list = dishes_data.get('dishes', [])
        
        if not dishes_list:
            print("⚠️ No dishes found to save")
            return []
        
        print(f"💾 Saving {len(dishes_list)} dishes to database...")
        
        for i, dish in enumerate(dishes_list):
            # 准备单个菜品的数据结构
            dish_record = {
                "name": dish.get('name', 'Unknown Dish'),
                "category": dish.get('category', 'Unknown'),
                "timestamp": datetime.now(),
                "calories": int(float(dish.get('calories', 0))),
                "nutrition": {
                    "protein_g": round(float(dish.get('nutrition', {}).get('protein_g', 0)), 1),
                    "carbs_g": round(float(dish.get('nutrition', {}).get('carbs_g', 0)), 1),
                    "fat_g": round(float(dish.get('nutrition', {}).get('fat_g', 0)), 1),
                    "fiber_g": round(float(dish.get('nutrition', {}).get('fiber_g', 0)), 1)
                }
            }
            
            # 使用insert_data逐个插入
            result_id = insert_data("dishes", dish_record)
            if result_id:
                saved_ids.append(result_id)
                print(f"  ✅ Dish {i+1}: '{dish_record['name']}' saved with ID: {result_id}")
            else:
                print(f"  ❌ Failed to save dish {i+1}: '{dish_record['name']}'")
        
        print(f"💾 Database operation completed: {len(saved_ids)}/{len(dishes_list)} dishes saved successfully")
        return saved_ids
                
    except Exception as e:
        print(f"❌ Error saving to database: {e}")
        import traceback
        traceback.print_exc()
        return []

def capture_and_analyze_dishes():
    """拍照并分析多个菜品，返回JSON格式的结构化数据并自动保存到数据库"""
    
    # 1. 调用相机拍照
    print("Starting camera capture...")
    result = capture_image()
    
    if not result:
        print("Photo capture failed!")
        return None
    
    print(f"Photo captured successfully! File saved at: {result}")
    
    # 2. 分析图片
    client = ZhipuAI(api_key=ZHIPUAI_API_KEY)
    
    # 读取拍摄的图片
    with open(result, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    
    # 更严格的英文系统提示词
    system_prompt = """You are a professional food nutrition analysis system. Analyze ALL visible dishes in the image and return STRICT JSON format.

CRITICAL: You MUST identify MULTIPLE dishes if present. Return EXACTLY this format without any additional text or markers:

{
    "dishes": [
        {
            "name": "Dish name 1",
            "category": "Cuisine type",
            "calories": 400,
            "nutrition": {
                "protein_g": 25,
                "carbs_g": 45,
                "fat_g": 15,
                "fiber_g": 5
            },
            "ingredients": ["ingredient1", "ingredient2"],
            "confidence": 0.9
        },
        {
            "name": "Dish name 2", 
            "category": "Cuisine type",
            "calories": 350,
            "nutrition": {
                "protein_g": 20,
                "carbs_g": 40,
                "fat_g": 12,
                "fiber_g": 4
            },
            "ingredients": ["ingredient3", "ingredient4"],
            "confidence": 0.8
        }
    ]
}

IMPORTANT:
- Do NOT include <|begin_of_box|> or <|end_of_box|> markers
- Return PURE JSON only, no other text
- Include ALL dishes you see in the image"""

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
                            "text": "Analyze this food image. Identify EVERY dish you see. Return only PURE JSON with all dishes in the 'dishes' array. Do not include any markers or additional text."
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
        
        # 使用改进的JSON提取
        analysis_result = extract_json_from_text(result_text)
        
        if analysis_result is None:
            print("❌ Failed to extract JSON from response")
            # 保存原始响应以便调试
            with open("debug_raw_response.txt", "w", encoding="utf-8") as f:
                f.write(result_text)
            print("💾 Raw response saved to debug_raw_response.txt for analysis")
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
        
        # 3. 自动保存到数据库
        if valid_dishes:
            saved_ids = save_dishes_to_database(analysis_result)
            if saved_ids:
                print(f"🎉 Successfully saved {len(saved_ids)} dishes to database!")
            else:
                print("⚠️ Analysis completed but failed to save any dishes to database")
        else:
            print("❌ No valid dishes found to save")
        
        return analysis_result
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
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