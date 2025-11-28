from services.dish_analyze import capture_and_analyze_dishes

if __name__ == "__main__":
    print("🔍 开始分析菜品...\n")
    result = capture_and_analyze_dishes()
    print(f"{result}\n🎉 分析完成！")
