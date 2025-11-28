from hardware.camera.raspberry_camera import capture_image

print("开始拍照测试...")

result = capture_image()

if result:
    print(f"\n拍照成功！文件保存于：{result}")
else:
    print("\n拍照失败！")
