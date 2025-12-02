import requests
import json
import time
from typing import Dict, Any

THINGSBOARD_HOST = "http://thingsboard.cloud"

def send_telemetry(token: str, data: Dict[str, Any]) -> bool:
    """
    Send telemetry data to ThingsBoard.

    Args:
        token: Device access token
        data: Dictionary containing telemetry data

    Returns:
        bool: True if successful, False otherwise
    """
    url = f"{THINGSBOARD_HOST}/api/v1/{token}/telemetry"
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=5)
        if response.status_code == 200:
            # print(f"✅ Telemetry sent to {token[:5]}...: {data}")
            return True
        else:
            print(f"❌ Failed to send telemetry. Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending telemetry: {e}")
        return False
