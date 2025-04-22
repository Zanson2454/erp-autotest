import pytest
import allure
import os
import json
from datetime import datetime
from loguru import logger


# 添加项目根目录到 Python 路径
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.insert(0, project_root)

from testcases.SCM.base_test import DecimalEncoder



@pytest.fixture(scope="session", autouse=True)
def env_setup(request):
    """测试环境设置"""
    env = request.config.getoption("--env")
    logger.info(f"当前测试环境: {env}")
    return env

def pytest_addoption(parser):
    """添加命令行参数"""
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        help="测试环境：dev/test/prod"
    )

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    用于向测试用例中添加用例的开始时间、内部注释，和失败截图等
    """
    outcome = yield
    report = outcome.get_result()
    
    # 添加测试用例的注释信息
    extra = getattr(report, "extra", [])
    if report.when == "call":
        # 获取测试用例的注释信息
        allure_notes = getattr(item, "_testcase_notes", None)
        if allure_notes:
            extra.append(allure.attach(
                allure_notes,
                "测试用例注释",
                allure.attachment_type.TEXT
            ))
        
        # 如果测试失败，添加失败信息
        if report.failed:
            # 添加失败信息
            if hasattr(item, "_testcase_failure_info"):
                extra.append(allure.attach(
                    item._testcase_failure_info,
                    "失败信息",
                    allure.attachment_type.TEXT
                ))
            
            # 添加请求和响应信息
            if hasattr(item, "_request_info"):
                extra.append(allure.attach(
                    json.dumps(item._request_info, ensure_ascii=False, indent=2, cls=DecimalEncoder),
                    "请求信息",
                    allure.attachment_type.JSON
                ))
            
            if hasattr(item, "_response_info"):
                extra.append(allure.attach(
                    json.dumps(item._response_info, ensure_ascii=False, indent=2, cls=DecimalEncoder),
                    "响应信息",
                    allure.attachment_type.JSON
                ))
            
            # 添加异常堆栈信息
            if hasattr(item, "_exception_info"):
                extra.append(allure.attach(
                    item._exception_info,
                    "异常堆栈",
                    allure.attachment_type.TEXT
                ))
    
    # 添加测试用例的开始时间
    if report.when == "setup":
        item._testcase_start_time = datetime.now()
    
    # 添加测试用例的结束时间和执行时间
    if report.when == "teardown":
        start_time = getattr(item, "_testcase_start_time", None)
        if start_time:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            extra.append(allure.attach(
                f"开始时间: {start_time}\n结束时间: {end_time}\n执行时间: {duration}秒",
                "执行时间",
                allure.attachment_type.TEXT
            ))
    
    report.extra = extra

@pytest.fixture(autouse=True)
def allure_env_info(request):
    """添加环境信息到Allure报告"""
    # 使用 allure.environment 的正确方式
    env_info = {
        "Environment": request.config.getoption("--env"),
        "Python Version": os.popen("python3 --version").read().strip(),
        "Pytest Version": pytest.__version__,
        "Allure Version": "2.13.2"  # 使用已知的版本号
    }
    
    # 确保目录存在
    os.makedirs("allure-results", exist_ok=True)
    
    # 将环境信息写入文件
    with open("allure-results/environment.properties", "w") as f:
        for key, value in env_info.items():
            f.write(f"{key}={value}\n") 