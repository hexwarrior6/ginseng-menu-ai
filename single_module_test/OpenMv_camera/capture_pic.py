# test_camera.py - 最终版

import serial
import time
import os  

SAVE_DIR = "src_raspi_app/temp/captured_dish"  # ← 相对路径
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200

def test_capture():
    print("连接串口...")
    
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    
    # 测试 PING
    print("\n测试 PING...")
    ser.reset_input_buffer()
    ser.write(b"PING\n")
    ser.flush()
    time.sleep(0.3)
    
    if ser.in_waiting > 0:
        print(f"✓ {ser.readline().decode().strip()}")
    
    # 测试 CAPTURE
    print("\n测试 CAPTURE...")
    ser.reset_input_buffer()
    ser.write(b"CAPTURE\n")
    ser.flush()
    
    # 等待 IMG_START
    start_time = time.time()
    while time.time() - start_time < 10:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', 'ignore').strip()
            if "Size:" in line:
                print(f"  {line}")
            if line == "IMG_START":
                print("  ✓ IMG_START")
                break
        time.sleep(0.01)
    else:
        print("  ✗ 超时")
        ser.close()
        return
    
    # 读取大小
    size_data = ser.read(4)
    if len(size_data) != 4:
        print(f"  ✗ 大小错误")
        ser.close()
        return
    
    size = int.from_bytes(size_data, 'big')
    print(f"  图片: {size} 字节")
    
    # 接收数据
    print("  接收中...")
    data = bytearray()
    
    start_time = time.time()
    last_print = 0
    
    # 持续读取直到收完
    while len(data) < size:
        elapsed = time.time() - start_time
        
        # 20秒超时
        if elapsed > 20:
            print(f"  ✗ 超时")
            break
        
        # 读取所有可用数据
        if ser.in_waiting > 0:
            chunk = ser.read(ser.in_waiting)
            data.extend(chunk)
            
            # 打印进度
            progress = len(data) * 100 // size
            if progress >= last_print + 20:
                print(f"  {progress}%...")
                last_print = progress
        else:
            time.sleep(0.001)
    
    elapsed = time.time() - start_time
    
    if len(data) >= size:
        speed = size / elapsed / 1024
        print(f"  ✓ 完成!")
        print(f"  用时: {elapsed:.2f}秒")
        print(f"  速度: {speed:.2f} KB/s")
        
        # 保存
        os.makedirs(SAVE_DIR, exist_ok=True)

        filename = os.path.join(SAVE_DIR, f"capture_{int(time.time())}.jpg")
        with open(filename, "wb") as f:
            f.write(data[:size])  # 只保存实际大小
        print(f"  ✓ 已保存: {filename}")
    else:
        print(f"  ✗ 不完整: {len(data)}/{size}")
        print(f"  速度: {len(data)/elapsed/1024:.2f} KB/s")
        
    
    ser.close()

if __name__ == "__main__":
    test_capture()