#!/usr/bin/env python3
"""
RFID 读卡器测试脚本
"""

from hardware.rfid.rfid_reader import read_uid, read_uid_wait
import sys

def test_single_read():
    """测试单次读取"""
    print("=" * 50)
    print("测试 1: 单次读取")
    print("=" * 50)
    print("请将卡片靠近读卡器...")
    
    uid = read_uid(timeout=5, verbose=True)
    
    if uid:
        print(f"\n✅ 成功! UID = {uid}")
        print(f"UID 长度: {len(uid)} 字符")
        return True
    else:
        print("\n❌ 未检测到卡片")
        return False


def test_wait_read():
    """测试等待读取模式"""
    print("\n" + "=" * 50)
    print("测试 2: 等待读取模式 (最多尝试 5 次)")
    print("=" * 50)
    print("请在 5 次尝试内将卡片靠近读卡器...\n")
    
    uid = read_uid_wait(max_attempts=5, interval=1, verbose=True)
    
    if uid:
        print(f"\n✅ 成功! UID = {uid}")
        return True
    else:
        print("\n❌ 5次尝试后仍未检测到卡片")
        return False


def test_continuous_read():
    """测试连续读取模式"""
    print("\n" + "=" * 50)
    print("测试 3: 连续读取 3 张卡片")
    print("=" * 50)
    
    cards = []
    for i in range(3):
        print(f"\n请刷第 {i+1} 张卡片...")
        uid = read_uid_wait(verbose=True)
        if uid:
            cards.append(uid)
            print(f"✅ 第 {i+1} 张卡片记录成功")
        else:
            print(f"❌ 第 {i+1} 张卡片读取失败")
    
    print("\n" + "-" * 50)
    print("读取结果汇总:")
    for idx, uid in enumerate(cards, 1):
        print(f"  卡片 {idx}: {uid}")
    print(f"总计成功读取: {len(cards)}/3 张卡片")
    
    return len(cards) > 0


def interactive_menu():
    """交互式菜单"""
    while True:
        print("\n" + "=" * 50)
        print("RFID 读卡器测试菜单")
        print("=" * 50)
        print("1. 单次读取测试")
        print("2. 等待读取测试 (最多5次)")
        print("3. 连续读取3张卡片")
        print("4. 快速测试 (静默模式)")
        print("0. 退出")
        print("=" * 50)
        
        choice = input("\n请选择测试项目 (0-4): ").strip()
        
        if choice == "1":
            test_single_read()
        elif choice == "2":
            test_wait_read()
        elif choice == "3":
            test_continuous_read()
        elif choice == "4":
            print("\n快速测试...")
            uid = read_uid(verbose=False)
            if uid:
                print(f"✅ UID: {uid}")
            else:
                print("❌ 未检测到卡片")
        elif choice == "0":
            print("\n感谢使用，再见! 👋")
            break
        else:
            print("❌ 无效选择，请重试")


def main():
    """主函数"""
    print("🔍 RFID 读卡器测试程序")
    print("请确保:")
    print("  1. 已安装 libnfc (sudo apt-get install libnfc-bin)")
    print("  2. 读卡器已正确连接")
    print("  3. 有足够的权限访问设备\n")
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--single":
            test_single_read()
        elif arg == "--wait":
            test_wait_read()
        elif arg == "--continuous":
            test_continuous_read()
        elif arg == "--quick":
            uid = read_uid(verbose=False)
            if uid:
                print(uid)
                sys.exit(0)
            else:
                sys.exit(1)
        else:
            print(f"未知参数: {arg}")
            print("可用参数: --single, --wait, --continuous, --quick")
            sys.exit(1)
    else:
        # 无参数则进入交互模式
        interactive_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断，程序退出")
        sys.exit(0)
