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

# 摄像头初始化一次
def init_sensor_once():
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QQVGA2)  # 128x160 LCD
    sensor.skip_frames(time=800)

init_sensor_once()

def send_image(img):
    jpeg = img.compress(quality=80)
    size = jpeg.size()

    usb.write(b"IMG_START\n")
    usb.write(size.to_bytes(4, "big"))
    usb.write(jpeg)
    usb.write(b"\nIMG_END\n")

    del jpeg
    gc.collect()

# =====================================================
#                    非阻塞流畅倒计时
# =====================================================
def countdown_smooth(sec=3):
    start_time = time.ticks_ms()
    remain = sec

    while remain > 0:
        now = time.ticks_ms()
        elapsed = time.ticks_diff(now, start_time)

        # 每次循环都实时刷新摄像头画面
        frame = sensor.snapshot()

        # 画倒计时数字
        frame.draw_string(50, 60, str(remain), color=(255, 0, 0), scale=4)
        lcd.write(frame)

        # 每秒减少一次倒计时
        if elapsed >= 1000:
            remain -= 1
            start_time = now  # 重置计时

        # 不要 sleep 太久，否则刷新卡顿
        time.sleep_ms(10)

# =====================================================
#                     主循环
# =====================================================
while True:
    if usb.any():
        cmd = usb.readline().decode().strip()

        if cmd == "CAPTURE":

            # ---------- 流畅倒计时 ----------
            countdown_smooth(3)

            # ---------- 拍照 ----------
            final_img = sensor.snapshot()

            # ---------- 显示 "Saved" ----------
            captured_img = image.Image(128, 160, sensor.RGB565)
            captured_img.draw_string(5, 60, "Saved", color=(0, 255, 0), scale=3)
            lcd.write(captured_img)
            time.sleep_ms(1000)

            # ---------- 黑屏 ----------
            lcd.write(black)

            # ---------- USB 发送 ----------
            send_image(final_img)
            clear_buffer()

        elif cmd == "PING":
            usb.write(b"PONG\n")

        elif cmd == "STATUS":
            usb.write(f"OK:{gc.mem_free()}\n".encode())

    time.sleep_ms(10)
