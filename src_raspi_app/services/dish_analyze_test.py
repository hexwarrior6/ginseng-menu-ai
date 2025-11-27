from services.dish_analyze import analyze_latest_dish

if __name__ == "__main__":
    print("🔍 开始分析菜品...\n")
    result = analyze_latest_dish()
    print(f"{result}\n🎉 分析完成！")
