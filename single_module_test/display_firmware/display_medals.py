# 使用前请安装 pyserial 库（pip install pyserial）
import serial
import time
from threading import Timer, Thread
import threading

# 配置参数
PORT = "/dev/ttyUSB1"  # 端口（Linux:/dev/ttyUSBx，Windows:COMx）
BAUD = 115200          # 波特率（与串口屏一致）
SYNC_INTERVAL = 1      # 1秒与屏幕同步一次
BRONZE_INTERVAL = 2    # 铜牌每2秒+1
SILVER_INTERVAL = 3   # 银牌每3秒+1
GOLD_INTERVAL = 5     # 金牌每5秒+1

# 复位指令定义（与串口屏一致）
RESET_CMD = b'\x55\x03\x0D\x0A'  # 帧头55 + 指令码03 + 帧尾0D0A

# 全局变量（奖牌数 + 线程控制）
gold = 0
silver = 0
bronze = 0
last_bronze_time = time.time()
last_silver_time = time.time()
last_gold_time = time.time()
serial_port = None  # 全局串口对象（避免重复打开）
is_running = True   # 程序运行标志

def init_serial():
    """初始化串口（全局唯一）"""
    global serial_port
    try:
        serial_port = serial.Serial(
            port=PORT,
            baudrate=BAUD,
            timeout=0.1,  # 读超时0.1秒，避免阻塞
            write_timeout=2
        )
        print(f"✅ 串口初始化成功：{PORT}（波特率：{BAUD}）")
        return True
    except Exception as e:
        print(f"❌ 串口初始化失败：{str(e)}")
        return False

def reset_medals():
    """清零所有奖牌数"""
    global gold, silver, bronze, last_bronze_time, last_silver_time, last_gold_time
    gold = 0
    silver = 0
    bronze = 0
    # 重置增长计时器（避免复位后立即增长）
    last_bronze_time = time.time()
    last_silver_time = time.time()
    last_gold_time = time.time()
    print("🔴 收到复位指令！所有奖牌已清零")

def listen_serial():
    """监听串口屏指令（独立线程，避免阻塞同步任务）"""
    global is_running
    buffer = b''  # 接收缓冲区（处理粘包/断包）
    while is_running:
        if serial_port and serial_port.is_open:
            try:
                # 读取串口数据（非阻塞）
                data = serial_port.read(1024)
                if data:
                    buffer += data
                    # 检查缓冲区是否包含完整的复位指令
                    if RESET_CMD in buffer:
                        reset_medals()
                        # 清空缓冲区（避免重复触发）
                        buffer = buffer.replace(RESET_CMD, b'')
            except Exception as e:
                print(f"⚠️  串口监听异常：{str(e)}")
        time.sleep(0.05)  # 降低CPU占用

def update_medals():
    """更新奖牌数量（按设定频率增长）"""
    global gold, silver, bronze, last_bronze_time, last_silver_time, last_gold_time
    current_time = time.time()
    
    # 铜牌增长
    if current_time - last_bronze_time >= BRONZE_INTERVAL:
        bronze += 1
        last_bronze_time = current_time
        print(f"🔵 铜牌+1 → 当前：{bronze}")
    
    # 银牌增长
    if current_time - last_silver_time >= SILVER_INTERVAL:
        silver += 1
        last_silver_time = current_time
        print(f"⚪ 银牌+1 → 当前：{silver}")
    
    # 金牌增长
    if current_time - last_gold_time >= GOLD_INTERVAL:
        gold += 1
        last_gold_time = current_time
        print(f"🟡 金牌+1 → 当前：{gold}")

def sync_with_screen():
    """每秒同步数据到串口屏"""
    global is_running
    if not is_running:
        return
    
    # 先更新奖牌数，再同步
    update_medals()
    
    try:
        if serial_port and serial_port.is_open:
            # 发送金牌数据（格式：gold.val=%d + 结束符FF FF FF）
            gold_cmd = f"gold.val={gold}".encode()
            serial_port.write(gold_cmd)
            serial_port.write(bytes.fromhex('ff ff ff'))
            
            # 发送银牌数据
            silver_cmd = f"silver.val={silver}".encode()
            serial_port.write(silver_cmd)
            serial_port.write(bytes.fromhex('ff ff ff'))
            
            # 发送铜牌数据
            bronze_cmd = f"bronze.val={bronze}".encode()
            serial_port.write(bronze_cmd)
            serial_port.write(bytes.fromhex('ff ff ff'))
            
            # 可选：打印同步日志
            # print(f"✅ 同步：金牌{gold} | 银牌{silver} | 铜牌{bronze}")
    except Exception as e:
        print(f"⚠️  同步失败：{str(e)}")
    
    # 1秒后继续同步
    Timer(SYNC_INTERVAL, sync_with_screen).start()

def main():
    global is_running
    # 初始化串口
    if not init_serial():
        return
    
    # 启动串口监听线程
    listen_thread = Thread(target=listen_serial, daemon=True)
    listen_thread.start()
    print("📻 串口监听线程已启动")
    
    # 启动同步任务
    print("=" * 50)
    print("🏅 奖牌自动增长同步程序")
    print(f"📅 同步频率：{SYNC_INTERVAL}秒/次")
    print(f"📈 增长规则：铜牌{BRONZE_INTERVAL}秒+1 | 银牌{SILVER_INTERVAL}秒+1 | 金牌{GOLD_INTERVAL}秒+1")
    print(f"🔌 串口配置：{PORT} | {BAUD}")
    print("🖱️  点击串口屏'reset_button'可清零复位")
    print("=" * 50)
    sync_with_screen()
    
    # 保持程序运行（捕获Ctrl+C退出）
    try:
        while is_running:
            time.sleep(1)
    except KeyboardInterrupt:
        is_running = False
        print("\n🛑 程序正在退出...")
        if serial_port and serial_port.is_open:
            serial_port.close()
        print("✅ 程序已退出")

if __name__ == '__main__':
    main()