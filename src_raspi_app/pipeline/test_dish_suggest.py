#!/usr/bin/env python3
"""
测试语音识别结果处理模块
"""

from pipeline.dish_suggest import process_speech_to_llm, process_command_speech_to_llm


def test_basic_speech_to_llm():
    """测试基本的语音识别结果处理功能"""
    print("🔍 测试基本语音识别结果处理功能...")
    
    # 测试正常情况
    test_text = "今天天气怎么样？"
    result = process_speech_to_llm(test_text)
    print(f"输入: {test_text}")
    print(f"大模型回复: {result}")
    print()
    
    # 测试空输入情况
    empty_text = ""
    result = process_speech_to_llm(empty_text)
    print(f"输入: '{empty_text}' (空输入)")
    print(f"大模型回复: {result}")
    print()
    
    # 测试只有空格的情况
    whitespace_text = "   "
    result = process_speech_to_llm(whitespace_text)
    print(f"输入: '{whitespace_text}' (只有空格)")
    print(f"大模型回复: {result}")
    print()


def test_command_speech_to_llm():
    """测试带命令上下文的语音识别结果处理功能"""
    print("🔍 测试带命令上下文的语音识别结果处理功能...")
    
    test_text = "帮我点一份宫保鸡丁"
    context = "点餐"
    result = process_command_speech_to_llm(test_text, context)
    print(f"上下文: {context}")
    print(f"输入: {test_text}")
    print(f"大模型回复: {result}")
    print()


def test_error_handling():
    """测试错误处理功能"""
    print("🔍 测试错误处理功能...")
    
    # 测试包含特殊字符的输入
    test_text = '你好"世界"！'
    result = process_speech_to_llm(test_text)
    print(f"输入: {test_text}")
    print(f"大模型回复: {result}")
    print()


if __name__ == "__main__":
    print("🧪 开始测试 speech_to_llm 模块\n")
    
    test_basic_speech_to_llm()
    test_command_speech_to_llm()
    test_error_handling()
    
    print("🎉 测试完成！")