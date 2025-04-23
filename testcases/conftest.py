"""Test-specific pytest configuration."""
import os
import json
import pytest
import allure
from datetime import datetime
from loguru import logger

from testcases.SCM.base_test import DecimalEncoder

@pytest.fixture(scope="session", autouse=True)
def env_setup(request):
    """测试环境设置
    作用：设置测试环境（dev/test/prod）
    范围：session级别，整个测试会话只执行一次
    自动执行：autouse=True，无需显式调用
    """
    env = request.config.getoption("--env")
    logger.info(f"当前测试环境: {env}")
    return env

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    测试报告钩子函数
    作用：增强测试报告，添加额外信息
    功能：
    1. 添加测试用例注释
    2. 记录失败信息
    3. 记录请求和响应信息
    4. 记录异常堆栈
    5. 记录测试执行时间
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
def allure_env_info(request, set_test_dir):
    """Allure环境信息
    作用：添加环境信息到Allure报告
    功能：
    1. 记录测试环境
    2. 记录Python版本
    3. 记录Pytest版本
    4. 记录Allure版本
    自动执行：autouse=True，无需显式调用
    """
    # 使用 allure.environment 的正确方式
    env_info = {
        "Environment": request.config.getoption("--env"),
        "Trantor Version": request.config.getoption("--trantor_version")
    }
    
    # 确保 reports/allure-results 目录存在
    reports_dir = os.path.join(set_test_dir, "reports", "allure-results")
    os.makedirs(reports_dir, exist_ok=True)
    
    # 将环境信息写入文件
    env_file = os.path.join(reports_dir, "environment.properties")
    with open(env_file, "w") as f:
        for key, value in env_info.items():
            f.write(f"{key}={value}\n") 