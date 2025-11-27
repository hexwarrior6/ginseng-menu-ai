import serial
import time
from threading import Thread, Lock
from typing import Callable, Optional

class ScreenDriver:
    """串口通信助手（按自定义协议 55 XX 0D0A 解析）"""
    
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 0.1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_port: Optional[serial.Serial] = None
        self.is_listening = False
        self.listen_thread: Optional[Thread] = None
        self.lock = Lock()
        self.receive_callback: Optional[Callable] = None
        
    def open(self) -> bool:
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
        self.stop_listen()
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print("🔌 串口已关闭")
    
    def send(self, data: bytes) -> bool:
        if not self.serial_port or not self.serial_port.is_open:
            print("⚠️  串口未打开，无法发送")
            return False

        try:
            with self.lock:
                bytes_written = self.serial_port.write(data)
                self.serial_port.flush()
            print(f"📤 发送 {bytes_written} 字节: {data}")
            return True
        except Exception as e:
            print(f"❌ 发送失败：{e}")
            return False
    
    def send_nextion_cmd(self, cmd: str) -> bool:
        data = cmd.encode() + bytes.fromhex('ff ff ff')
        return self.send(data)
    
    def start_listen(self, callback: Callable[[bytes], None]):
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
        """
        解析协议：
        帧头：0x55
        指令：1 字节
        尾部：0x0D 0x0A
        完整帧格式：55 XX 0D 0A
        """
        buffer = b''
        while self.is_listening:
            try:
                with self.lock:
                    if self.serial_port.in_waiting > 0:
                        data = self.serial_port.read(self.serial_port.in_waiting)
                    else:
                        data = b''

                if data:
                    buffer += data
                    print(f"📥 收到原始数据: {data.hex()}")

                    # 解析多帧和粘包
                    while True:
                        start = buffer.find(b'\x55')
                        if start == -1:
                            buffer = b''  # 没头就清空
                            break

                        # 至少要 4 字节：55 XX 0D 0A
                        if len(buffer) < start + 4:
                            # 等更多字节
                            buffer = buffer[start:]
                            break

                        frame = buffer[start:start+4]

                        # 判断是否是完整帧
                        if frame[0] == 0x55 and frame[2] == 0x0D and frame[3] == 0x0A:
                            cmd = bytes([frame[1]])  # 只取指令码
                            print(f"📌 解析指令码: {cmd.hex()}")

                            if self.receive_callback:
                                self.receive_callback(cmd)

                            buffer = buffer[start+4:]  # 移除已处理帧
                        else:
                            # 不是完整帧，丢弃当前头，从下一个字节继续找
                            buffer = buffer[start+1:]
                            continue

            except Exception as e:
                print(f"⚠️ 监听异常：{e}")

            time.sleep(0.02)

    def stop_listen(self):
        if self.is_listening:
            self.is_listening = False
            if self.listen_thread:
                self.listen_thread.join(timeout=1)
            print("🛑 串口监听已停止")
    
    def receive_once(self, size: int = 1024, timeout: float = 1.0) -> Optional[bytes]:
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
