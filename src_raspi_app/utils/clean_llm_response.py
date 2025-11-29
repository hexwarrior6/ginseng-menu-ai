def clean_llm_response(text: str) -> str:
    """
    清理LLM响应文本，去除星号和多余空格
    
    Args:
        text (str): 需要清理的原始文本
        
    Returns:
        str: 清理后的文本
    """
    if not text or not isinstance(text, str):
        return text
    
    # 去除文本开头的星号（如果有的话）
    text = text.lstrip('*')
    
    # 使用正则表达式替换多个连续星号为单个空格
    import re
    text = re.sub(r'\*+', ' ', text)
    
    # 替换多个连续空格为单个空格
    text = re.sub(r'\s+', ' ', text)
    
    # 去除首尾空格
    text = text.strip()
    
    return text

# 测试示例
if __name__ == "__main__":
    test_cases = [
        "**这是一段**带有星号的文本**",
        "* 开头有星号 中间有 多余空格  ",
        "正常文本没有特殊字符",
        "多个***星号***和   空格",
        "",
        "   ",
        None
    ]
    
    for i, test in enumerate(test_cases):
        result = clean_llm_response(test)
        print(f"测试 {i+1}:")
        print(f"原始: '{test}'")
        print(f"清理后: '{result}'\n")