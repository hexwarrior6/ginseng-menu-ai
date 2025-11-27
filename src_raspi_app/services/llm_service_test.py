from llm_service import ask_llm

if __name__ == "__main__":
    print("🔍 LLM 测试开始\n")

    prompt = "周子涵爱吃炸鸡还是wu"

    reply = ask_llm(prompt)

    print("🤖 模型回复：\n")
    print(reply)
