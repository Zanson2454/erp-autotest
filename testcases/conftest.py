"""Pytest 配置文件

此文件包含 pytest 的全局配置、钩子函数和通用 fixture。
主要功能：
1. 环境配置管理
2. Allure 报告集成
3. 测试前置和后置处理
4. 失败用例截图
5. 测试用例装饰器支持

使用示例：
```bash
# 运行测试并指定环境
pytest --env=test --alluredir=./reports/allure-results

# 运行测试并指定 Trantor 版本
pytest --trantor_version=2.5.25.0130.0-SNAPSHOT

# 运行指定优先级的测试
pytest -m "critical"
```
"""

import os
import sys
import pytest
import allure
import shutil
from datetime import datetime
from typing import Generator, Callable, Any
from pathlib import Path
from functools import wraps

from utils.log_util import Loggers
from utils.yaml_util import YamlUtil
from utils.report_util import ReportEnhancer, TestStatus
from utils.path_util import PathUtil


# 确保必要的目录存在
project_root = PathUtil.get_project_root()
for dir_name in ["reports/allure-results", "logs", "data"]:
    os.makedirs(project_root / dir_name, exist_ok=True)

# 清理测试用例目录下的日志
testcases_logs = project_root / "logs"
if testcases_logs.exists():
    shutil.rmtree(testcases_logs)


def pytest_addoption(parser: pytest.Parser) -> None:
    """添加命令行参数
    
    Args:
        parser: pytest 参数解析器
    """
    parser.addoption(
        "--env",
        action="store",
        default="test",
        choices=["dev", "test", "staging", "prod"],
        help="执行环境：dev/test/staging/prod"
    )
    parser.addoption(
        "--trantor_version",
        action="store",
        default="2.5.25.0130.0-SNAPSHOT",
        help="Trantor版本号:查看配置文件config/env/xxx.yaml"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="是否使用无头模式运行浏览器"
    )


def pytest_configure(config: pytest.Config) -> None:
    """配置测试环境
    
    Args:
        config: pytest 配置对象
    """
    # 设置测试环境
    env = config.getoption("--env")
    Loggers.info(f"当前测试环境: {env}")
    os.environ["TEST_ENV"] = env
    
    # 设置 Trantor 版本
    config_manager = YamlUtil()
    env_config = config_manager.load_env_config(env)
    trantor_version = config.getoption("--trantor_version") or env_config.get("trantor_version", "")
    os.environ["TRANTOR_VERSION"] = trantor_version
    
    # 注册自定义标记
    config.addinivalue_line("markers", "critical: 标记为关键测试用例")
    config.addinivalue_line("markers", "high: 标记为高优先级测试用例")
    config.addinivalue_line("markers", "medium: 标记为中优先级测试用例")
    config.addinivalue_line("markers", "low: 标记为低优先级测试用例")
    
    # 创建 Allure 环境信息文件
    _create_allure_env_file(config)


def _create_allure_env_file(config):
    """创建 Allure 环境配置文件"""
    try:
        # 获取 Allure 结果目录
        results_dir = config.getoption("--alluredir") or "allure-results"
        
        # 确保结果目录存在
        os.makedirs(results_dir, exist_ok=True)
        
        # 创建环境配置文件
        env_file = os.path.join(results_dir, "environment.properties")
        
        # 获取环境信息
        env_info = {
            "Environment": os.getenv("ENV", "test"),
            "Python.Version": sys.version,
            "Platform": sys.platform
        }
        
        # 写入环境信息
        with open(env_file, "w", encoding="utf-8") as f:
            for key, value in env_info.items():
                f.write(f"{key}={value}\n")
                
    except Exception as e:
        print(f"创建 Allure 环境配置文件失败: {str(e)}")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    """测试环境设置 fixture
    
    在测试会话开始时设置环境，结束时清理环境。
    
    Args:
        request: pytest fixture 请求对象
        
    Yields:
        None
    """
    Loggers.info("开始测试会话")
    yield
    Loggers.info("测试会话结束")


@pytest.fixture(scope="function")
def report_enhancer() -> ReportEnhancer:
    """报告增强器 fixture
    
    为每个测试用例提供报告增强器实例。
    
    Returns:
        ReportEnhancer: 报告增强器实例
    """
    return ReportEnhancer()


def business_case(epic: str, feature: str, story: str, severity: allure.severity_level = allure.severity_level.NORMAL) -> Callable:
    """业务测试用例装饰器
    
    用于标记测试用例的业务属性和优先级。
    
    Args:
        epic: 一级业务域
        feature: 二级功能模块
        story: 用户场景
        severity: 用例优先级
        
    Returns:
        Callable: 装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @allure.epic(epic)
        @allure.feature(feature)
        @allure.story(story)
        @allure.severity(severity)
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)
        return wrapper
    return decorator


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> Generator[None, pytest.TestReport, None]:
    """测试报告生成钩子
    
    在测试执行过程中收集信息并生成报告。
    
    Args:
        item: 测试项
        call: 测试调用信息
        
    Yields:
        None
    """
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":
        # 设置测试标题
        if hasattr(item, "funcargs"):
            test_name = item.name
            allure.dynamic.title(f"Test: {test_name}")
            
            # 添加测试用例文档
            if item.function.__doc__:
                allure.dynamic.description(item.function.__doc__)
        
        # 处理测试失败
        if report.failed:
            _handle_test_failure(item, report)
    
    # 添加测试阶段信息
    if report.when == "setup":
        allure.dynamic.description("Test Setup")
    elif report.when == "teardown":
        allure.dynamic.description("Test Cleanup")


def _handle_test_failure(item: pytest.Item, report: pytest.TestReport) -> None:
    """处理测试失败
    
    Args:
        item: 测试项
        report: 测试报告
    """
    if hasattr(item, "funcargs"):
        # 获取报告增强器
        report_enhancer = item.funcargs.get("report_enhancer")
        if report_enhancer:
            report_enhancer.set_test_status(TestStatus.FAILED)
        
        # 获取浏览器驱动并截图
        driver = item.funcargs.get("driver")
        if driver:
            try:
                screenshot = driver.get_screenshot_as_png()
                allure.attach(
                    screenshot,
                    name="failure_screenshot",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as e:
                Loggers.error(f"截图失败: {e}") 