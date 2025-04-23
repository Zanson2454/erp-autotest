import os
import sys

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 将项目根目录添加到Python路径
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

__version__ = "0.1" 