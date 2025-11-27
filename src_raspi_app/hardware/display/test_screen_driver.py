#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单串口测试
"""

import time
from hardware.display import ScreenDriver

# 配置
PORT = "/dev/ttyUSB1"
BAUDRATE = 9600

def main():
    # 创建串口对象
    serial = ScreenDriver(port=PORT, baudrate=BAUDRATE)
    
    # 打开串口
    if not serial.open():
        print("串口打开失败")
        return
    
    # ========== 在这里修改你的测试代码 ==========
    
    # 示例1: 发送Nextion指令
    # serial.send_nextion_cmd("page 0")
    serial.send_nextion_cmd("reco_result.txt=\"Hello World\"")

    # 示例2: 发送原始字节
    # serial.send(b'\x55\xAA\x01\x02')
    
    # 示例3: 设置数值
    # serial.send_nextion_cmd("gold.val=100")
    
    # 示例4: 单次接收
    # data = serial.receive_once(timeout=1.0)
    # if data:
    #     print(f"收到: {data.hex(' ').upper()}")
    
    # 示例5: 持续监听
    # def on_receive(data):
    #     print(f"收到: {data.hex(' ').upper()}")
    # serial.start_listen(on_receive)
    # time.sleep(15)  # 监听15秒
    
    # ============================================
    
    # 关闭串口
    serial.close()
    print("测试完成")


if __name__ == '__main__':
    main()