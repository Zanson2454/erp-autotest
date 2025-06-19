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
from datetime import datetime
from typing import Generator, Callable, Any
from pathlib import Path
from functools import wraps
import inspect
import re

from utils.log_util import Loggers
from utils.yaml_util import YamlUtil
from utils.report_util import ReportEnhancer, TestStatus

# 获取项目根目录
project_root = Path(__file__).resolve().parent.parent

# 确保必要的目录存在
REQUIRED_DIRS = ["reports/allure-results", "reports/allure-report","logs", "testdata", "testcases"]
for dir_name in REQUIRED_DIRS:
    os.makedirs(project_root / dir_name, exist_ok=True)

def pytest_addoption(parser: pytest.Parser) -> None:
    """添加命令行参数"""
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
        default=None,
        help="Trantor版本号"
    )

def load_env_config(env: str) -> dict:
    """加载环境配置
    
    Args:
        env: 环境名称
        
    Returns:
        dict: 环境配置
    """
    config_path = project_root / "config" / "env" / f"{env}.yaml"
    if not config_path.exists():
        Loggers.warning(f"环境配置文件不存在: {config_path}")
        return {}
        
    yaml_util = YamlUtil()
    return yaml_util.read_yaml(config_path)

def pytest_configure(config: pytest.Config) -> None:
    """配置测试环境"""
    # 设置测试环境
    env = config.getoption("--env")
    Loggers.info(f"当前测试环境: {env}")
    os.environ["TEST_ENV"] = env
    
    # 加载环境配置
    env_config = load_env_config(env)
    
    # 设置 Trantor 版本，优先级：命令行参数 > 配置文件 > 硬编码默认值
    trantor_version = (
        config.getoption("--trantor_version")
        or env_config.get("trantor_version")
        or "2.5.25.0330.0-SNAPSHOT"
    )
    os.environ["TRANTOR_VERSION"] = trantor_version
    Loggers.info(f"Trantor版本: {trantor_version}")
    
    # 注册自定义标记
    for marker, desc in {
        "critical": "标记为关键测试用例",
        "high": "标记为高优先级测试用例",
        "medium": "标记为中优先级测试用例",
        "low": "标记为低优先级测试用例"
    }.items():
        config.addinivalue_line("markers", f"{marker}: {desc}")
    
    # 创建 Allure 环境信息
    create_allure_environment(config)

def create_allure_environment(config: pytest.Config) -> None:
    """创建 Allure 环境配置文件"""
    try:
        results_dir = config.getoption("--alluredir") or project_root / "reports/allure-results"
        os.makedirs(results_dir, exist_ok=True)
        
        env_info = {
            "Environment": os.getenv("TEST_ENV", "test"),
            "Trantor_Version": os.getenv("TRANTOR_VERSION", ""),
            "Python_Version": sys.version.split()[0],
            "Platform": sys.platform,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        env_file = Path(results_dir) / "environment.properties"
        with open(env_file, "w", encoding="utf-8") as f:
            for key, value in env_info.items():
                f.write(f"{key}={value}\n")
                
    except Exception as e:
        Loggers.error(f"创建 Allure 环境配置文件失败: {str(e)}")

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment() -> Generator[None, None, None]:
    """测试环境设置"""
    Loggers.info("开始测试会话")
    yield
    Loggers.info("测试会话结束")

@pytest.fixture(scope="function")
def report_enhancer() -> ReportEnhancer:
    """报告增强器"""
    return ReportEnhancer()

def business_case(epic: str, feature: str, story: str, severity: allure.severity_level = allure.severity_level.NORMAL) -> Callable:
    """业务测试用例装饰器"""
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
    """测试报告生成钩子"""
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":
        if hasattr(item, "funcargs"):
            # 尝试获取自定义标题
            custom_title = get_custom_title(item)
            
            # 如果找到自定义标题，则设置它；否则使用默认标题
            if custom_title:
                allure.dynamic.title(custom_title)
            else:
                allure.dynamic.title(item.name)
            
            # 添加测试用例文档
            if item.function.__doc__:
                allure.dynamic.description(item.function.__doc__)
        
        # 处理测试失败
        if report.failed:
            handle_test_failure(item, report)
            
def get_custom_title(item):
    """从测试函数中提取自定义标题
    
    优先级:
    1. 函数中使用的allure.dynamic.title
    2. @allure.title装饰器
    3. case_decorator中的title参数
    """
    if not hasattr(item.function, "__code__"):
        return None
    
    try:
        # 一次性获取函数源代码
        import inspect
        func_source = inspect.getsource(item.function)
        
        # 使用正则表达式匹配各种标题设置方式
        import re
        
        # 先检查函数体中的动态设置
        dynamic_match = re.search(r'allure\.dynamic\.title\([\'"](.+?)[\'"]\)', func_source)
        if dynamic_match:
            return dynamic_match.group(1)
            
        # 然后检查装饰器
        decorator_match = re.search(r'@allure\.title\([\'"](.+?)[\'"]\)', func_source)
        if decorator_match:
            return decorator_match.group(1)
            
        # 最后检查case_decorator中的title参数
        case_decorator_match = re.search(r'@case_decorator\(.*?title=[\'"](.+?)[\'"]', func_source, re.DOTALL)
        if case_decorator_match:
            return case_decorator_match.group(1)
            
    except Exception as e:
        Loggers.warning(f"无法解析测试函数标题: {e}")
    
    return None

def handle_test_failure(item: pytest.Item, report: pytest.TestReport) -> None:
    """处理测试失败"""
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
                    name=f"failure_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as e:
                Loggers.error(f"截图失败: {e}") 