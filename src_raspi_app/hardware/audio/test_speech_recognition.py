#!/usr/bin/env python3
"""
语音识别功能测试脚本
测试 speech_recognition_module 的各种功能
"""

import sys
import time
from hardware.audio.speech_recognition import recognize_speech, recognize_speech_continuous, init_recognizer

def test_simple_recognition():
    """测试1: 简单的单次识别"""
    print("\n" + "="*60)
    print("测试1: 简单单次识别")
    print("="*60)
    print("请说一句话（10秒超时，2秒静音自动结束）...")
    
    result = recognize_speech(timeout=10, silence_threshold=2.0)
    
    print("\n" + "-"*60)
    if result:
        print(f"✓ 识别成功！")
        print(f"  结果: '{result}'")
        print(f"  长度: {len(result)} 字符")
    else:
        print("✗ 未识别到任何内容")
    print("-"*60)
    
    return result

def test_streaming_recognition():
    """测试2: 带流式回调的识别"""
    print("\n" + "="*60)
    print("测试2: 流式识别（实时显示）")
    print("="*60)
    
    partial_results = []
    final_results = []
    
    def on_partial(text):
        partial_results.append(text)
        print(f"\r💬 [实时] {text}                    ", end='', flush=True)
    
    def on_final(text):
        final_results.append(text)
        print(f"\n✓ [完成] {text}")
    
    print("请说一句话...")
    result = recognize_speech(
        timeout=10,
        silence_threshold=2.0,
        on_partial=on_partial,
        on_final=on_final
    )
    
    print("\n" + "-"*60)
    print(f"最终返回结果: '{result}'")
    print(f"部分结果数量: {len(partial_results)}")
    print(f"完整结果数量: {len(final_results)}")
    if partial_results:
        print(f"最后的部分结果: '{partial_results[-1]}'")
    print("-"*60)
    
    return result

def test_multiple_rounds():
    """测试3: 多轮对话测试"""
    print("\n" + "="*60)
    print("测试3: 多轮识别测试")
    print("="*60)
    
    rounds = 3
    results = []
    
    for i in range(rounds):
        print(f"\n第 {i+1}/{rounds} 轮:")
        print("请说话...")
        
        result = recognize_speech(timeout=8, silence_threshold=1.5)
        results.append(result)
        
        if result:
            print(f"✓ 第{i+1}轮识别: '{result}'")
        else:
            print(f"✗ 第{i+1}轮未识别到内容")
        
        if i < rounds - 1:
            print("准备下一轮...")
            time.sleep(1)
    
    print("\n" + "-"*60)
    print("所有轮次结果:")
    for i, result in enumerate(results, 1):
        print(f"  第{i}轮: '{result}'")
    print("-"*60)
    
    return results

def test_custom_timeout():
    """测试4: 自定义超时时间"""
    print("\n" + "="*60)
    print("测试4: 短超时测试（5秒）")
    print("="*60)
    print("请在5秒内说话...")
    
    start_time = time.time()
    result = recognize_speech(timeout=5, silence_threshold=1.0)
    elapsed = time.time() - start_time
    
    print("\n" + "-"*60)
    print(f"识别结果: '{result}'")
    print(f"实际用时: {elapsed:.2f} 秒")
    print("-"*60)
    
    return result

def test_continuous_mode():
    """测试5: 持续监听模式（可选）"""
    print("\n" + "="*60)
    print("测试5: 持续监听模式")
    print("="*60)
    print("将持续监听10秒，每说一句话都会识别...")
    print("(你也可以按 Ctrl+C 提前结束)")
    
    recognized_texts = []
    start_time = time.time()
    
    def on_speech(text):
        recognized_texts.append(text)
        print(f"\n✓ 识别到第{len(recognized_texts)}句: '{text}'")
    
    def should_stop():
        return time.time() - start_time > 10
    
    try:
        recognize_speech_continuous(on_speech, stop_callback=should_stop)
    except KeyboardInterrupt:
        print("\n用户中断")
    
    print("\n" + "-"*60)
    print(f"共识别到 {len(recognized_texts)} 句话:")
    for i, text in enumerate(recognized_texts, 1):
        print(f"  {i}. '{text}'")
    print("-"*60)
    
    return recognized_texts

def test_with_live_feedback():
    """测试6: 实时反馈测试"""
    print("\n" + "="*60)
    print("测试6: 实时反馈（可视化）")
    print("="*60)
    
    last_partial = ""
    
    def on_partial(text):
        nonlocal last_partial
        # 清除上一行
        print(f"\r{' ' * (len(last_partial) + 20)}", end='')
        # 显示新内容
        print(f"\r💭 正在识别: {text}", end='', flush=True)
        last_partial = text
    
    def on_final(text):
        print(f"\n✅ 识别完成: {text}")
    
    print("请说话，你会看到实时的识别过程...")
    result = recognize_speech(
        timeout=10,
        silence_threshold=2.0,
        on_partial=on_partial,
        on_final=on_final
    )
    
    print("\n" + "-"*60)
    print(f"最终结果: '{result}'")
    print("-"*60)
    
    return result

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print(" 语音识别功能测试套件")
    print("="*60)
    
    # 预加载模型
    print("\n正在初始化语音识别模型...")
    init_recognizer()
    print("✓ 模型加载完成！\n")
    
    # 测试菜单
    tests = {
        '1': ('简单单次识别', test_simple_recognition),
        '2': ('流式识别（实时显示）', test_streaming_recognition),
        '3': ('多轮识别测试', test_multiple_rounds),
        '4': ('短超时测试', test_custom_timeout),
        '5': ('持续监听模式', test_continuous_mode),
        '6': ('实时反馈测试', test_with_live_feedback),
        'a': ('运行所有测试', None),
    }
    
    print("请选择要运行的测试:")
    for key, (name, _) in tests.items():
        print(f"  {key}. {name}")
    print("  q. 退出")
    
    while True:
        choice = input("\n请输入选项: ").strip().lower()
        
        if choice == 'q':
            print("退出测试")
            break
        elif choice == 'a':
            # 运行所有测试
            for key in ['1', '2', '3', '4', '6']:  # 跳过持续模式
                tests[key][1]()
                time.sleep(1)
            print("\n✓ 所有测试完成！")
            break
        elif choice in tests and choice != 'a':
            # 运行单个测试
            tests[choice][1]()
            
            # 询问是否继续
            cont = input("\n继续测试其他功能? (y/n): ").strip().lower()
            if cont != 'y':
                break
        else:
            print("无效选项，请重新选择")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)