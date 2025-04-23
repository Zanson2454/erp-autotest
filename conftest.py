"""Global pytest configuration."""
import os
import sys
import pytest

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))

def pytest_configure(config):
    """pytest 配置钩子函数"""
    # 添加项目根目录到 PYTHONPATH
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # 确保 reports 目录存在
    reports_dir = os.path.join(project_root, "reports", "allure-results")
    os.makedirs(reports_dir, exist_ok=True)

def pytest_addoption(parser):
    """添加命令行参数"""
    parser.addoption(
        "--env",
        action="store",
        default="test",
        help="测试环境：dev/test/prod"
    )
    
    # 添加 Trantor 版本参数
    parser.addoption(
        "--trantor_version",
        action="store",
        default="2.5.25.0130.0-SNAPSHOT",
        help="Trantor版本号"
    )
  

@pytest.fixture(scope="session", autouse=True)
def set_test_dir():
    """设置测试目录"""
    # 设置工作目录为项目根目录
    os.chdir(project_root)
    return project_root 