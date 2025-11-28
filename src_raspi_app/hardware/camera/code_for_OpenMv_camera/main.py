import sensor, image, time, pyb, gc, display

# 初始化 LCD
lcd = display.SPIDisplay()

# 上电立即黑屏
black = image.Image(128, 160, sensor.RGB565)
lcd.write(black)

usb = pyb.USB_VCP()

red_led = pyb.LED(1)
green_led = pyb.LED(2)
blue_led = pyb.LED(3)

while not usb.isconnected():
    time.sleep_ms(100)

print("USB Ready")
green_led.on()

def clear_buffer():
    while usb.any():
        usb.read(usb.any())

# 摄像头初始化（LCD 用 QQVGA2）
def init_sensor_preview():
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QQVGA2)  # 128x160
    sensor.skip_frames(time=800)

init_sensor_preview()

def crop_to_4_5_vertical(img):
    """
    将VGA(640x480)照片裁切成4:5竖屏比例
    保持高度480，计算宽度：480 * 4/5 = 384
    从水平居中位置裁切
    """
    original_width = img.width()   # 640
    original_height = img.height() # 480
    
    # 计算4:5竖屏的宽度 (高度保持480不变)
    target_width = int(original_height * 4 / 5)  # 480 * 0.8 = 384
    
    # 计算裁切区域的x起始位置（水平居中）
    start_x = (original_width - target_width) // 2  # (640-384)/2 = 128
    
    # 裁切区域: (x, y, width, height)
    crop_roi = (start_x, 0, target_width, original_height)
    
    # 进行裁切
    cropped_img = img.copy(roi=crop_roi)
    
    return cropped_img

def send_image(img):
    # 先强制垃圾回收释放内存
    gc.collect()
    
    # 压缩前再检查一次内存
    if gc.mem_free() < 100000:  # 如果内存不足100KB
        gc.collect()
        time.sleep_ms(50)
    
    jpeg = img.compress(quality=80)
    size = jpeg.size()

    usb.write(b"IMG_START\n")
    usb.write(size.to_bytes(4, "big"))
    usb.write(jpeg)
    usb.write(b"\nIMG_END\n")

    del jpeg
    gc.collect()

# 切换到高分辨率拍照模式
def switch_to_high_res():
    # 先释放一些内存
    gc.collect()
    time.sleep_ms(100)
    
    sensor.set_framesize(sensor.VGA)  # 640x480
    # 增加跳帧数量，确保图像稳定
    sensor.skip_frames(time=500)  # 从300增加到500ms
    
    # 额外等待确保传感器稳定
    time.sleep_ms(200)

# 切换回预览模式
def switch_to_preview():
    # 先释放内存
    gc.collect()
    time.sleep_ms(100)
    
    sensor.set_framesize(sensor.QQVGA2)  # 128x160
    sensor.skip_frames(time=200)
    
    # 额外等待
    time.sleep_ms(100)

# =====================================================
#                    非阻塞流畅倒计时
# =====================================================
def countdown_smooth(sec=3):
    start_time = time.ticks_ms()
    remain = sec

    while remain > 0:
        now = time.ticks_ms()
        elapsed = time.ticks_diff(now, start_time)

        # 实时预览
        frame = sensor.snapshot()

        # 画数字
        frame.draw_string(50, 60, str(remain), color=(255, 0, 0), scale=4)
        lcd.write(frame)

        if elapsed >= 1000:
            remain -= 1
            start_time = now

        time.sleep_ms(10)

# =====================================================
#                     主循环
# =====================================================
while True:
    if usb.any():
        cmd = usb.readline().decode().strip()

        if cmd == "CAPTURE":
            countdown_smooth(3)

            # ---------- 切换到 VGA 拍照 ----------
            try:
                switch_to_high_res()
                
                # 多拍几张，取最后一张确保稳定
                for i in range(3):
                    final_img = sensor.snapshot()  # 高清照片
                    time.sleep_ms(100)
                
                # ---------- 裁切成4:5竖屏比例 ----------
                cropped_img = crop_to_4_5_vertical(final_img)
                
                # 立即释放原始图像内存
                del final_img
                gc.collect()
                
                # ---------- 拍照完立即切回预览模式 ----------
                switch_to_preview()

                # ---------- 显示 "Saved" ----------
                saved_img = image.Image(128, 160, sensor.RGB565)
                saved_img.draw_string(5, 60, "Saved", color=(0, 255, 0), scale=3)
                lcd.write(saved_img)
                time.sleep_ms(800)

                # ---------- 黑屏 ----------
                lcd.write(black)

                # ---------- USB 发送裁切后的照片 ----------
                send_image(cropped_img)
                clear_buffer()
                
                # 释放裁切图像内存
                del cropped_img
                gc.collect()
                
            except Exception as e:
                # 出错时确保切回预览模式
                try:
                    switch_to_preview()
                except:
                    init_sensor_preview()  # 完全重新初始化
                
                usb.write(f"ERROR:{str(e)}\n".encode())

        elif cmd == "PING":
            usb.write(b"PONG\n")

        elif cmd == "STATUS":
            usb.write(f"OK:{gc.mem_free()}\n".encode())

    time.sleep_ms(10)