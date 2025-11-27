import serial
import time
from threading import Thread, Lock
from typing import Callable, Optional

class ScreenDriver:
    """串口通信助手类（推荐方案）"""
    
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 0.1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_port: Optional[serial.Serial] = None
        self.is_listening = False
        self.listen_thread: Optional[Thread] = None
        self.lock = Lock()  # 线程锁，保护串口读写
        self.receive_callback: Optional[Callable] = None
        
    def open(self) -> bool:
        """打开串口"""
        try:
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                write_timeout=2
            )
            print(f"✅ 串口已打开：{self.port} ({self.baudrate}bps)")
            return True
        except Exception as e:
            print(f"❌ 串口打开失败：{e}")
            return False
    
    def close(self):
        """关闭串口"""
        self.stop_listen()  # 先停止监听
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print("🔌 串口已关闭")
    
    def send(self, data: bytes) -> bool:
        """
        发送数据
        Args:
            data: 要发送的字节数据
        Returns:
            bool: 发送是否成功
        """
        if not self.serial_port or not self.serial_port.is_open:
            print("⚠️  串口未打开，无法发送")
            return False

        try:
            with self.lock:  # 加锁保护
                bytes_written = self.serial_port.write(data)
                self.serial_port.flush()  # 确保数据发送完成
            print(f"📤 发送 {bytes_written} 字节: {data}")
            return True
        except Exception as e:
            print(f"❌ 发送失败：{e}")
            return False
    
    def send_nextion_cmd(self, cmd: str) -> bool:
        """
        发送Nextion串口屏指令（自动添加结束符FF FF FF）
        Args:
            cmd: 指令字符串，如 "gold.val=10"
        """
        data = cmd.encode() + bytes.fromhex('ff ff ff')
        return self.send(data)
    
    def start_listen(self, callback: Callable[[bytes], None]):
        """
        启动后台监听线程（推荐方式）
        Args:
            callback: 接收到数据时的回调函数，参数为接收到的字节数据
        """
        if self.is_listening:
            print("⚠️  监听线程已在运行")
            return
        
        if not self.serial_port or not self.serial_port.is_open:
            print("⚠️  串口未打开，无法启动监听")
            return
        
        self.receive_callback = callback
        self.is_listening = True
        self.listen_thread = Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        print("📻 串口监听已启动")
    
    def _listen_loop(self):
        """监听循环（内部方法）"""
        buffer = b''
        while self.is_listening:
            try:
                with self.lock:
                    # 检查串口是否有数据可读
                    if self.serial_port.in_waiting > 0:
                        data = self.serial_port.read(self.serial_port.in_waiting)
                    else:
                        data = b''

                if data:
                    buffer += data
                    print(f"📥 收到数据: {data.hex()}")

                    # 尝试处理完整的指令（根据结束符 ff ff ff 分割）
                    while b'\xff\xff\xff' in buffer:
                        # 找到一个完整的指令
                        parts = buffer.split(b'\xff\xff\xff', 1)
                        complete_cmd = parts[0]

                        if self.receive_callback:
                            self.receive_callback(complete_cmd)

                        # 保留剩余数据
                        buffer = parts[1] if len(parts) > 1 else b''

                    # 处理没有结束符的数据或粘包
                    # 如果buffer太长，可能需要其他策略

            except Exception as e:
                print(f"⚠️  监听异常：{e}")

            time.sleep(0.05)  # 降低CPU占用，50ms轮询
    
    def stop_listen(self):
        """停止监听"""
        if self.is_listening:
            self.is_listening = False
            if self.listen_thread:
                self.listen_thread.join(timeout=1)
            print("🛑 串口监听已停止")
    
    def receive_once(self, size: int = 1024, timeout: float = 1.0) -> Optional[bytes]:
        """
        单次接收数据（阻塞方式）
        Args:
            size: 读取字节数
            timeout: 超时时间（秒）
        Returns:
            接收到的数据，超时返回None
        """
        if not self.serial_port or not self.serial_port.is_open:
            print("⚠️  串口未打开")
            return None
        
        try:
            old_timeout = self.serial_port.timeout
            self.serial_port.timeout = timeout
            
            with self.lock:
                data = self.serial_port.read(size)
            
            self.serial_port.timeout = old_timeout
            return data if data else None
        except Exception as e:
            print(f"❌ 接收失败：{e}")
            return None


# ============ 使用示例 ============

def example_usage():
    """演示如何使用ScreenDriver"""
    
    # 1. 创建串口助手
    serial = ScreenDriver(port="/dev/ttyUSB1", baudrate=115200)
    
    # 2. 打开串口
    if not serial.open():
        return
    
    # 3. 定义接收回调函数
    def on_receive(data: bytes):
        """收到数据时的处理"""
        print(f"📩 收到数据：{data.hex()} | {data}")
        
        # 示例：检测复位指令
        if b'\x55\x03\x0D\x0A' in data:
            print("🔴 检测到复位指令！")
    
    # 4. 启动后台监听
    serial.start_listen(callback=on_receive)
    
    # 5. 发送数据
    try:
        while True:
            # 发送Nextion指令
            serial.send_nextion_cmd("gold.val=100")
            serial.send_nextion_cmd("silver.val=50")
            
            # 或直接发送字节
            serial.send(b'\x55\xAA')
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n退出中...")
    
    finally:
        # 6. 关闭串口（自动停止监听）
        serial.close()


def example_single_receive():
    """演示单次接收模式（不推荐用于实时监听）"""
    serial = ScreenDriver(port="/dev/ttyUSB1")
    
    if serial.open():
        # 发送指令
        serial.send_nextion_cmd("page 0")
        
        # 等待接收响应（阻塞1秒）
        response = serial.receive_once(timeout=1.0)
        if response:
            print(f"收到响应：{response}")
        
        serial.close()


# ============ 简化版：纯函数式（不推荐长时间运行）============

def simple_send(port: str, data: bytes, baudrate: int = 115200) -> bool:
    """
    简单发送函数（适合偶尔发送，不适合频繁调用）
    每次都打开/关闭串口，性能较差
    """
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            ser.write(data)
            return True
    except Exception as e:
        print(f"发送失败：{e}")
        return False


def simple_receive(port: str, size: int = 1024, timeout: float = 1.0, 
                   baudrate: int = 115200) -> Optional[bytes]:
    """
    简单接收函数（适合单次接收，不适合持续监听）
    """
    try:
        with serial.Serial(port, baudrate, timeout=timeout) as ser:
            return ser.read(size)
    except Exception as e:
        print(f"接收失败：{e}")
        return None


if __name__ == '__main__':
    # 运行示例
    print("推荐使用 ScreenDriver 类进行持续通信")
    example_usage()