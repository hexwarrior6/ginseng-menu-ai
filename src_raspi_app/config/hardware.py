"""
Hardware configuration loader
"""

import yaml
from pathlib import Path

# Load configuration from YAML file
CONFIG_PATH = Path(__file__).parent / "hardware.yaml"

with open(CONFIG_PATH, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

# Extract configuration sections
ultrasonic = config.get('ultrasonic', {})