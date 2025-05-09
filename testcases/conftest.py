"""Test-specific pytest configuration."""
import os
import sys
import pytest
from datetime import datetime
from utils.log_util import Loggers
from utils.yaml_util import YamlUtil
import allure
import json
from typing import Dict, Any

# 获取项目根目录
def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 确保必要的目录存在
project_root = get_project_root()
for dir_name in ["reports/allure-results", "logs"]:
    os.makedirs(os.path.join(project_root, dir_name), exist_ok=True)

# 确保testcases目录下没有logs目录
testcases_logs = os.path.join(project_root, "testcases", "logs")
if os.path.exists(testcases_logs):
    import shutil
    shutil.rmtree(testcases_logs)

def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="test", help="测试环境：dev/test/staging/prod")
    parser.addoption("--trantor_version", action="store", default="2.5.25.0130.0-SNAPSHOT", help="Trantor版本号")

def pytest_configure(config):
    env = config.getoption("--env")
    Loggers.info(f"当前测试环境: {env}")
    if env:
        os.environ["TEST_ENV"] = env
    # 设置 Trantor 版本
    config_manager = YamlUtil()
    env_config = config_manager.load_env_config(env)
    trantor_version = config.getoption("--trantor_version", env_config.get("trantor_version", ""))
    os.environ["TRANTOR_VERSION"] = trantor_version

    reports_dir = os.path.join(project_root, "reports", "allure-results")
    env_file = os.path.join(reports_dir, "environment.properties")
    
    with open(env_file, "w") as f:
        f.write(f"Browser=Chrome\n")
        f.write(f"Browser.Version=Latest\n")
        f.write(f"Platform=MacOS\n")
        f.write(f"Python.Version=3.8+\n")
        f.write(f"Timestamp={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

@pytest.fixture(autouse=True, scope="session")
def allure_env_info(request):
    env_info = {
        "Environment": request.config.getoption("--env"),
        "Trantor Version": request.config.getoption("--trantor_version"),
        "Python Version": sys.version.replace('\n', ' '),
        "Pytest Version": pytest.__version__,
    }
    reports_dir = os.path.join(project_root, "reports", "allure-results")
    env_file = os.path.join(reports_dir, "environment.properties")
    try:
        with open(env_file, "w") as f:
            for key, value in env_info.items():
                f.write(f"{key}={value}\n")
    except Exception as e:
        Loggers.error(f"写入 Allure 环境信息失败: {e}")

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, "extra", [])
    
    if report.when == "call":
        # 添加测试步骤
        if hasattr(item, "funcargs"):
            test_name = item.name
            allure.dynamic.title(f"Test: {test_name}")
            
        # 添加失败截图
        if report.failed:
            if hasattr(item, "funcargs"):
                driver = item.funcargs.get("driver")
                if driver:
                    screenshot = driver.get_screenshot_as_png()
                    allure.attach(
                        screenshot,
                        name="failure_screenshot",
                        attachment_type=allure.attachment_type.PNG
                    )
    
    # 添加设置和清理步骤
    if report.when == "setup":
        allure.dynamic.description("Test Setup")
    if report.when == "teardown":
        allure.dynamic.description("Test Cleanup")
    
    report.extra = extra 