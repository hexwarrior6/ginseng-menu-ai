import os
import requests

DEEPSEEK_API_KEY = "sk-522bd7700c8b4e239b9a888e62498418"
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
