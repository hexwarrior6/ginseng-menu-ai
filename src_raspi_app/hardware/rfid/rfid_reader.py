import subprocess
import re

def read_uid(timeout=5, verbose=False):
    """
    读取 RFID 卡片的 UID

    ！！！注意：
    确保已按照 single_module_test/PCR532_nfcreader.py 中的步骤配置libnfc。
    
    参数:
        timeout: 超时时间(秒)，默认5秒
        verbose: 是否打印详细信息，默认False
    
    返回:
        str: 成功时返回 UID 字符串（例如: "04a3b2c1"，无空格）
        None: 未检测到卡片或读取失败
    """
    if verbose:
        print("开始读取卡片，请将卡片靠近读卡器...")
    
    try:
        # 使用 nfc-list 读取卡片信息
        result = subprocess.run(
            ['nfc-list'], 
            capture_output=True, 
            text=True,
            timeout=timeout
        )
        
        # 在输出中查找 UID
        if 'UID' in result.stdout:
            for line in result.stdout.split('\n'):
                if 'UID' in line:
                    # 提取 UID 值并去除所有空格
                    uid_match = re.search(r'UID[^:]*:\s*([0-9a-fA-F\s]+)', line)
                    if uid_match:
                        uid = uid_match.group(1).strip().replace(' ', '')
                        if verbose:
                            print(f"读取成功: {uid}")
                        return uid
                    else:
                        # 如果正则匹配失败，返回整行并去除空格
                        uid = line.split(':', 1)[-1].strip().replace(' ', '')
                        if verbose:
                            print(f"读取成功: {uid}")
                        return uid
        
        if verbose:
            print("未检测到卡片")
        return None
        
    except subprocess.TimeoutExpired:
        if verbose:
            print(f"读取超时（{timeout}秒）")
        return None
    except FileNotFoundError:
        if verbose:
            print("错误: 未找到 nfc-list 命令，请确保已安装 libnfc")
        return None
    except Exception as e:
        if verbose:
            print(f"读取出错: {e}")
        return None


def read_uid_wait(max_attempts=None, interval=1, verbose=False):
    """
    持续尝试读取 UID，直到读取成功
    
    参数:
        max_attempts: 最大尝试次数，None 表示无限尝试
        interval: 每次尝试之间的间隔(秒)
        verbose: 是否打印详细信息
    
    返回:
        str: UID 字符串
    """
    attempts = 0
    while max_attempts is None or attempts < max_attempts:
        uid = read_uid(verbose=verbose)
        if uid:
            return uid
        attempts += 1
        if max_attempts is None or attempts < max_attempts:
            if verbose:
                print(f"重试中... ({attempts})")
            import time
            time.sleep(interval)
    
    return None