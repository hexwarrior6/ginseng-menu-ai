import os
import base64
from zhipuai import ZhipuAI

ZHIPUAI_API_KEY = "e62abd4ebbba488ea4a96771929b6c6d.41RwSM4Nd0Y92AEN"
IMG_DIR = "src_raspi_app/temp/captured_dish"


def get_latest_image(folder):
    """获取指定目录下最新的图片文件"""
    imgs = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    if not imgs:
        raise FileNotFoundError("❌ 未找到任何图片")

    return max(imgs, key=os.path.getmtime)


def analyze_latest_dish():
    """封装好的函数：分析最新图片中的菜品并返回结果文本"""

    client = ZhipuAI(api_key=ZHIPUAI_API_KEY)

    # 读取最新图片
    img_path = get_latest_image(IMG_DIR)
    print(f"📸 使用最新图片进行分析：{img_path}")

    # 图片转 base64
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    # 调用 GLM-4.5V 多模态模型
    response = client.chat.completions.create(
        model="glm-4.5v",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "请识别这道菜，并分析其主要食材、营养特点以及可能的烹饪方式。"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_b64}"
                        }
                    }
                ]
            }
        ]
    )

    result = response.choices[0].message.content

    print("\n🧾 菜品分析结果：\n")
    print(result)

    return result
