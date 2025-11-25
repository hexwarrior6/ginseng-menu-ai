#!/usr/bin/env python3
"""
NFC读卡器部署和使用指南 - PCR532 (CH340) + 树莓派

项目概述:
本脚本用于通过PCR532 NFC读卡器读取IC卡的UID，适用于树莓派环境下的菜单系统用户识别。

硬件设备:
- PCR532 NFC读卡器 (基于PN532芯片，CH340 USB转串口)
- 树莓派 (测试环境: Raspberry Pi OS Bullseye)

部署时间线:
========================================================================
1. 硬件识别阶段
========================================================================
在树莓派上连接PCR532设备后，通过以下命令识别设备:

$ lsusb
输出: Bus 001 Device 008: ID 1a86:7523 QinHeng Electronics CH340 serial converter

$ ls -la /dev/ttyUSB*
输出: crw-rw---- 1 root dialout 188, 0 Nov 25 10:30 /dev/ttyUSB0

确认设备被正确识别为CH340串口设备。

========================================================================
2. 软件环境准备
========================================================================
安装必要的NFC库和工具:

$ sudo apt update
$ sudo apt install libnfc-dev libnfc-bin

========================================================================
3. 驱动配置 (如果需要)
========================================================================

创建配置文件 /etc/nfc/libnfc.conf:
----------------------------------------
# 创建配置目录
sudo mkdir -p /etc/nfc

# 创建配置文件
sudo tee /etc/nfc/libnfc.conf > /dev/null <<'EOF'
# libnfc configuration file
allow_intrusive_scan = true
allow_autoscan = true
log_level = 1

# 自动检测设备（推荐先尝试这个）
# device.connstring = "pn532_uart:/dev/ttyUSB0"

# 如果自动检测不行，取消注释下面一行，并确认你的设备路径
# device.connstring = "pn532_uart:/dev/ttyUSB0"
EOF
----------------------------------------

权限设置:
$ sudo usermod -a -G dialout $USER  # 重新登录生效
或临时: $ sudo chmod 666 /dev/ttyUSB0

========================================================================
4. 命令行测试阶段
========================================================================
测试设备识别:
$ nfc-list
正常输出: NFC device: pn532_uart:/dev/ttyUSB0 opened

测试卡片读取:
$ nfc-list
当卡片靠近时显示UID信息。

遇到的问题和解决方案:
- 初始出现I2C错误: 这是libnfc自动探测的正常过程，可忽略
- nfc-relay-picc命令会进入模拟模式，需要用Ctrl+C退出
- 最终确定使用nfc-list命令进行简单读取

========================================================================
5. Python集成阶段
========================================================================
基于nfc-list命令开发Python脚本，实现自动化读取。
本脚本即为最终可用的读取工具。

使用说明:
1. 确保PCR532设备已连接
2. 运行脚本: python3 nfc_reader.py
3. 将IC卡靠近读卡器
4. 脚本自动读取并显示UID后退出

返回信息说明:
- UID (NFCID1): 卡片的唯一标识符，如"89 ee 77 3c"
- ATQA (SENS_RES): 答案请求，标识卡片类型
- SAK (SEL_RES): 选择确认，标识卡片功能
- ATS: 卡片的其他属性信息

典型应用场景:
- 用户身份识别 (门禁系统)
- 会员卡识别 (点餐系统)
- 设备控制 (刷卡启动)

作者: HexWarrior6
创建日期: 2025/11/25
版本: 1.0
"""

import subprocess
import time

print("开始读取卡片，请将卡片靠近读卡器...")

# 使用nfc-list读取，读取后立即退出
result = subprocess.run(['nfc-list'], capture_output=True, text=True)

if 'UID' in result.stdout:
    for line in result.stdout.split('\n'):
        if 'UID' in line:
            print(f"读取成功: {line.strip()}")
            break
else:
    print("未检测到卡片")

print("程序自动退出")