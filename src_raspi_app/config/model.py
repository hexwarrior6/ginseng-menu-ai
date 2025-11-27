"""
Model configuration loader
"""

import yaml
from pathlib import Path

# Load configuration from YAML file
CONFIG_PATH = Path(__file__).parent / "model.yaml"

with open(CONFIG_PATH, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

# Extract configuration sections
local_model = config.get('local_model', {})
vision_model = config.get('vision_model', {})
text_model = config.get('text_model', {})
preference_system = config.get('preference_system', {})