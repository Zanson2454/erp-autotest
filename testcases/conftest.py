"""Test-specific pytest configuration."""
import os
import sys
import pytest
from datetime import datetime
from utils.LogUtil import Loggers
from common.config_manager import ConfigManager
import allure
import json

project_root = os.path.dirname(os.path.abspath(__file__))

def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="test", help="测试环境：dev/test/staging/prod")
    parser.addoption("--trantor_version", action="store", default="2.5.25.0130.0-SNAPSHOT", help="Trantor版本号")

def pytest_configure(config):
    env = config.getoption("--env")
    Loggers.info(f"当前测试环境: {env}")
    if env:
        os.environ["TEST_ENV"] = env
    # 确保必要目录存在
    for dir_name in ["reports/allure-results", "logs"]:
        try:
            os.makedirs(os.path.join(project_root, dir_name), exist_ok=True)
        except Exception as e:
            Loggers.error(f"创建目录失败: {dir_name}, {e}")
    # 设置 Trantor 版本
    config_manager = ConfigManager()
    env_config = config_manager.load_env_config(env)
    trantor_version = config.getoption("--trantor_version", env_config.get("trantor_version", ""))
    os.environ["TRANTOR_VERSION"] = trantor_version

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
        allure_notes = getattr(item, "_testcase_notes", None)
        if allure_notes:
            extra.append(allure.attach(
                allure_notes,
                "测试用例注释",
                allure.attachment_type.TEXT
            ))
        if report.failed:
            if hasattr(item, "_testcase_failure_info"):
                extra.append(allure.attach(
                    item._testcase_failure_info,
                    "失败信息",
                    allure.attachment_type.TEXT
                ))
            if hasattr(item, "_request_info"):
                extra.append(allure.attach(
                    json.dumps(item._request_info, ensure_ascii=False, indent=2),
                    "请求信息",
                    allure.attachment_type.JSON
                ))
            if hasattr(item, "_response_info"):
                extra.append(allure.attach(
                    json.dumps(item._response_info, ensure_ascii=False, indent=2),
                    "响应信息",
                    allure.attachment_type.JSON
                ))
            if hasattr(item, "_exception_info"):
                extra.append(allure.attach(
                    item._exception_info,
                    "异常堆栈",
                    allure.attachment_type.TEXT
                ))
    if report.when == "setup":
        item._testcase_start_time = datetime.now()
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