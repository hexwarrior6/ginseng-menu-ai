import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"


def ask_llm(prompt: str) -> str:
    """
    调用 DeepSeek 文本对话模型（deepseek-chat）
    输入：prompt 文本
    输出：模型回复文本
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    resp = requests.post(DEEPSEEK_URL, headers=headers, json=payload)

    # 错误处理
    if resp.status_code != 200:
        raise RuntimeError(f"DeepSeek API 错误：{resp.text}")

    data = resp.json()

    # 提取模型回复
    return data["choices"][0]["message"]["content"]
