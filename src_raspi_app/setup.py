# src_raspi_app/setup.py
from setuptools import setup, find_packages
import os

# 读取requirements.txt中的依赖
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = f.read().splitlines()
        # 过滤掉空行和注释
        return [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="ginseng_menu_ai_raspi_app",
    version="0.1.0",
    description="Ginseng Menu Ai - Raspberry Pi Application",
    
    # 当前目录的所有包
    packages=find_packages(),
    
    # 从requirements.txt读取依赖
    install_requires=read_requirements(),
    
    include_package_data=True,
    python_requires=">=3.8",
    
    # 可选：入口点
    entry_points={
        'console_scripts': [
            'ginseng-raspi=main:main',
        ],
    },
)