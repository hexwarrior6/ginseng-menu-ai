# main.py - 无延迟终极版

import sensor
import image
import time
import pyb
import gc

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.VGA)
sensor.skip_frames(time=2000)
sensor.set_auto_exposure(False, exposure_us=50000)

red_led = pyb.LED(1)
green_led = pyb.LED(2)
blue_led = pyb.LED(3)

for i in range(3):
    green_led.on()
    time.sleep_ms(100)
    green_led.off()
    time.sleep_ms(100)

usb = pyb.USB_VCP()

while not usb.isconnected():
    time.sleep_ms(100)

print("USB OK")
green_led.on()

def clear_buffer():
    while usb.any():
        usb.read(usb.any())

clear_buffer()

def send_image(img):
    try:
        blue_led.on()

        jpeg_data = img.compress(quality=80)
        size = jpeg_data.size()

        print(f"Size: {size}")

        # 发送开始标记和大小
        usb.write(b"IMG_START\n")
        usb.write(size.to_bytes(4, 'big'))

        # ✅ 关键：一次性写入，完全不延迟
        usb.write(jpeg_data)

        # 立即发送结束标记
        usb.write(b"\nIMG_END\n")

        print("Sent")

        blue_led.off()
        del jpeg_data
        gc.collect()
        return True

    except Exception as e:
        print(f"Err: {e}")
        blue_led.off()
        red_led.on()
        time.sleep_ms(200)
        red_led.off()
        gc.collect()
        return False

print("Ready")
loop_count = 0

while True:
    try:
        loop_count += 1

        if not usb.isconnected():
            red_led.on()
            while not usb.isconnected():
                time.sleep_ms(500)
            red_led.off()
            green_led.on()
            clear_buffer()

        img = sensor.snapshot()

        if loop_count % 2000 == 0:
            gc.collect()

        if usb.any():
            data = usb.readline()
            if data:
                cmd = data.decode('utf-8', 'ignore').strip()

                if cmd == "CAPTURE":
                    green_led.off()
                    send_image(img)
                    green_led.on()
                    clear_buffer()

                elif cmd == "PING":
                    usb.write(b"PONG\n")

                elif cmd == "STATUS":
                    usb.write(f"OK:{gc.mem_free()}\n".encode())

    except KeyboardInterrupt:
        red_led.off()
        green_led.off()
        blue_led.off()
        break
    except:
        pass