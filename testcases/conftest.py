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

# 运行测试并指定项目（多项目模式）
pytest --project=project1 --env=test --alluredir=./reports/allure-results

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
        "--project",
        action="store",
        default=None,
        help="项目名称（对应 config/env/{project}/ 目录），不指定时使用默认配置（config/env/{env}.yaml）"
    )
    parser.addoption(
        "--trantor_version",
        action="store",
        default=None,
        help="Trantor版本号"
    )

def load_env_config(env: str, project: str = None) -> dict:
    """加载环境配置
    
    Args:
        env: 环境名称
        project: 项目名称（可选），如果指定则从 config/env/{project}/{env}.yaml 加载，
                 否则从 config/env/{env}.yaml 加载（向后兼容）
        
    Returns:
        dict: 环境配置
    """
    if project:
        # 多项目模式：从项目目录加载配置
        config_path = project_root / "config" / "env" / project / f"{env}.yaml"
        if not config_path.exists():
            Loggers.warning(f"项目配置文件不存在: {config_path}，尝试使用默认配置")
            # 如果项目配置不存在，尝试使用默认配置
            config_path = project_root / "config" / "env" / f"{env}.yaml"
    else:
        # 默认模式：从根目录加载配置（向后兼容）
        config_path = project_root / "config" / "env" / f"{env}.yaml"
    
    if not config_path.exists():
        Loggers.warning(f"环境配置文件不存在: {config_path}")
        return {}
        
    yaml_util = YamlUtil()
    if project:
        # 多项目模式：需要使用相对路径
        relative_path = f"env/{project}/{env}.yaml"
    else:
        relative_path = f"env/{env}.yaml"
    
    return yaml_util.read_yaml(relative_path)

def pytest_configure(config: pytest.Config) -> None:
    """配置测试环境"""
    # 设置测试环境
    env = config.getoption("--env")
    project = config.getoption("--project")
    Loggers.info(f"当前测试环境: {env}" + (f", 项目: {project}" if project else ""))
    os.environ["TEST_ENV"] = env
    if project:
        os.environ["TEST_PROJECT"] = project
    
    # 加载环境配置
    env_config = load_env_config(env, project)
    
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
            "Project": os.getenv("TEST_PROJECT", "default"),
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
@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(session, config, items):
    """
    智能排序方案：支持两种模式
    
    模式1 - 全局排序（兼容老代码）：
        - 使用 order 参数的测试用例，由 pytest-ordering 插件处理
        - 所有文件的测试用例按 order 值统一排序（可能交叉执行）
    
    模式2 - 文件级串行（新功能）：
        - 使用 file_level_order 参数的测试用例，由本函数处理
        - 先按文件路径排序，文件内按 file_level_order 排序
        - 确保先执行完文件1的所有测试，再执行文件2
    
    原理：给每个文件分配编号，排序键 = 文件编号*1000 + file_level_order
    这样可以确保文件1的order=999也会排在文件2的order=1之前
    
    注意：使用 trylast=True 确保在 pytest-ordering 之后执行，覆盖其排序结果
    """
    def get_file_level_order(item):
        """从函数的 _file_level_order 属性中获取排序值"""
        # 检查函数本身和 __wrapped__ 属性
        func = item.function
        order = getattr(func, '_file_level_order', None)
        if order is None and hasattr(func, '__wrapped__'):
            order = getattr(func.__wrapped__, '_file_level_order', None)
        return order
    
    # 分离两种模式的测试用例
    file_level_items = [item for item in items if get_file_level_order(item) is not None]
    other_items = [item for item in items if get_file_level_order(item) is None]
    
    # 对使用 file_level_order 的测试用例进行文件级排序
    if file_level_items:
        # 为每个文件分配唯一编号（按字母顺序）
        file_paths = sorted(set(item.location[0] for item in file_level_items))
        file_index = {path: idx for idx, path in enumerate(file_paths)}
        
        # 排序键 = 文件编号*1000 + file_level_order
        file_level_items.sort(key=lambda x: file_index[x.location[0]] * 1000 + get_file_level_order(x))
    
    # 重新组合：file_level_order 的测试用例排在前面
    # 这样可以优先执行需要文件级串行的测试
    items[:] = file_level_items + other_items