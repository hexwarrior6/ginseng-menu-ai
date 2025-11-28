# test_meal_analysis.py
from pipeline.plate_analyze import capture_and_identify_dishes_for_user


if __name__ == "__main__":
    uid = "a1b2c3d4" # Example user ID
    response = capture_and_identify_dishes_for_user(uid)
    print(response)