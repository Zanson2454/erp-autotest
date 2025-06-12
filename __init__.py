"""
ERP自动化测试框架

提供完整的ERP系统自动化测试能力，包括：
1. 测试用例管理
2. 数据驱动测试
3. 环境配置管理
4. 测试报告生成
5. 性能测试支持
"""

import os
import sys
from pathlib import Path


# 获取项目根目录
def _get_project_root() -> Path:
    """获取项目根目录
    
    Returns:
        Path: 项目根目录路径
    """
    # 获取当前文件所在目录（项目根目录）
    project_root = Path(os.path.dirname(os.path.abspath(__file__)))
    # 添加到Python路径
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    return project_root


# 初始化项目根目录
PROJECT_ROOT = _get_project_root()

# 导出常用路径
def get_module_path(module_name: str) -> Path:
    """获取模块路径
    
    Args:
        module_name: 模块名称，如 'utils', 'testcases' 等
        
    Returns:
        Path: 模块路径
    """
    return PROJECT_ROOT / module_name


def get_data_path() -> Path:
    """获取数据目录路径
    
    Returns:
        Path: 数据目录路径
    """
    return PROJECT_ROOT / "data"


def get_config_path() -> Path:
    """获取配置目录路径
    
    Returns:
        Path: 配置目录路径
    """
    return PROJECT_ROOT / "config"


def get_log_path() -> Path:
    """获取日志目录路径
    
    Returns:
        Path: 日志目录路径
    """
    return PROJECT_ROOT / "logs"

# 包版本信息
__version__ = "1.0.0"

# 确保必要的目录在Python路径中
for subdir in ['common', 'utils', 'testcases']:
    subdir_path = PROJECT_ROOT / subdir
    if subdir_path.exists() and str(subdir_path) not in sys.path:
        sys.path.insert(0, str(subdir_path)) 