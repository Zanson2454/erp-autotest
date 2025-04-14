import pytest
import allure

@pytest.fixture(scope="session", autouse=True)
def env_setup():
    """
    测试环境初始化
    """
    pass

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
            if hasattr(item, "_testcase_failure_info"):
                extra.append(allure.attach(
                    item._testcase_failure_info,
                    "失败信息",
                    allure.attachment_type.TEXT
                ))
    
    report.extra = extra 