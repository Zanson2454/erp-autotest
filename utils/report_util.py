import allure
from typing import Dict, Any, List, Optional
from loguru import logger
from datetime import datetime
from enum import Enum
import json
import re
from pathlib import Path
from contextlib import contextmanager
import pytest
import functools


class TestStatus(Enum):
    """测试状态枚举"""
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class ReportEnhancer:
    """测试报告增强类，用于丰富测试报告内容
    
    提供测试步骤记录、截图管理、性能指标收集等功能。
    支持业务语义化的测试报告生成，并与 Allure 报告系统集成。
    
    使用示例：
    ```python
    # 在测试用例中使用
    @allure.epic("进销存管理")
    @allure.feature("订单管理")
    class TestOrder:
        def test_create_order(self):
            report = ReportEnhancer()
            with allure.step("前置条件：登录系统"):
                report.add_test_step("登录系统", {"user": "admin"})
            with allure.step("创建订单"):
                report.add_test_step("创建订单", {"order_type": "SO"})
    ```
    """
    
    def __init__(self):
        """初始化报告增强器"""
        self.report_data: Dict[str, Any] = {
            "business_domain": None,  # 业务域
            "feature": None,         # 功能模块
            "story": None,           # 用户场景
            "requirement_id": None,  # 需求ID
            "test_case_id": None,    # 测试用例ID
            "status": None,          # 测试状态
            "start_time": None,      # 开始时间
            "end_time": None,        # 结束时间
            "duration": None,        # 执行时长
            "metrics": {},           # 性能指标
            "steps": [],            # 测试步骤
            "attachments": []       # 附件列表
        }
        self._steps: List[Dict[str, Any]] = []
        self.start_time = datetime.now()
    
    def set_business_context(
        self,
        business_domain: str,
        feature: str,
        story: str,
        requirement_id: Optional[str] = None,
        test_case_id: Optional[str] = None
    ):
        """设置业务上下文
        
        Args:
            business_domain: 业务域
            feature: 功能模块
            story: 用户场景
            requirement_id: 需求ID
            test_case_id: 测试用例ID
        """
        self.report_data.update({
            "business_domain": business_domain,
            "feature": feature,
            "story": story,
            "requirement_id": requirement_id,
            "test_case_id": test_case_id
        })
        # 设置 Allure 标签
        allure.dynamic.epic(business_domain)
        allure.dynamic.feature(feature)
        allure.dynamic.story(story)
        if requirement_id:
            allure.dynamic.link(requirement_id, name="需求链接")
        if test_case_id:
            allure.dynamic.link(test_case_id, name="测试用例链接")
    
    @allure.step("添加测试步骤")
    def add_test_step(
        self,
        step_name: str,
        details: Dict[str, Any] = None,
        status: TestStatus = TestStatus.PASSED
    ):
        """添加测试步骤
        
        Args:
            step_name: 步骤名称
            details: 步骤详情
            status: 步骤状态
        """
        step = {
            "name": step_name,
            "time": datetime.now().isoformat(),
            "details": details or {},
            "status": status.value
        }
        self._steps.append(step)
        logger.info(f"步骤: {step_name} [{status.value}]")
        if details:
            logger.debug(f"详情: {details}")
    
    @allure.step("添加截图")
    def add_screenshot(
        self,
        name: str,
        image_data: bytes,
        description: Optional[str] = None
    ):
        """添加截图
        
        Args:
            name: 截图名称
            image_data: 图片数据
            description: 截图描述
        """
        allure.attach(
            image_data,
            name=name,
            description=description,
            attachment_type=allure.attachment_type.PNG
        )
        self.report_data["attachments"].append({
            "type": "screenshot",
            "name": name,
            "description": description,
            "time": datetime.now().isoformat()
        })
    
    @allure.step("添加性能指标")
    def add_metrics(self, metrics: Dict[str, Any]):
        """添加性能指标
        
        Args:
            metrics: 性能指标字典
        """
        self.report_data["metrics"].update(metrics)
        allure.attach(
            str(metrics),
            name="性能指标",
            attachment_type=allure.attachment_type.TEXT
        )
    
    def set_test_status(self, status: TestStatus):
        """设置测试状态
        
        Args:
            status: 测试状态
        """
        self.report_data["status"] = status.value
        self.end_time = datetime.now()
        self.report_data["duration"] = (self.end_time - self.start_time).total_seconds()
    
    def get_report_data(self) -> Dict[str, Any]:
        """获取报告数据
        
        Returns:
            报告数据字典
        """
        return {
            **self.report_data,
            "steps": self._steps
        }


def fix_report_title(report_dir: str, title: str = "ERP-AUTOTEST"):
    """修改 Allure 报告标题
    
    Args:
        report_dir: 报告目录路径
        title: 报告标题，默认为 "ERP-AUTOTEST"
    """
    report_path = Path(report_dir)
    
    # 修改 summary.json
    summary_file = report_path / 'widgets' / 'summary.json'
    if summary_file.exists():
        with open(summary_file, 'r+', encoding='utf-8') as f:
            data = json.load(f)
            data['reportName'] = title
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.truncate()
    
    # 修改 index.html
    index_file = report_path / 'index.html'
    if index_file.exists():
        with open(index_file, 'r+', encoding='utf-8') as f:
            content = f.read()
            content = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', content)
            f.seek(0)
            f.write(content)
            f.truncate()


class AllureSimple:
    """
    极简的Allure辅助类，提供最基本的功能封装
    
    主要功能：
    1. 简化JSON附件添加
    2. 简化文本附件添加
    3. 提供更简洁的步骤上下文管理器
    
    使用示例:
        from utils.report_util import a
        
        # 添加JSON附件
        a.json(data, "请求数据")
        
        # 添加文本附件
        a.text("一些文本信息", "文本数据")
        
        # 使用步骤上下文管理器
        with a.step("执行某个步骤"):
            # 步骤内的代码
            result = do_something()
            # 添加步骤结果作为附件
            a.json(result, "步骤结果")
    """
    
    @staticmethod
    def json(data: Dict[str, Any], name: str = "数据") -> None:
        """
        添加JSON数据作为附件
        
        Args:
            data: 要添加的JSON数据(字典对象)
            name: 附件名称，默认为"数据"
        
        说明:
            自动将字典转换为格式化的JSON字符串，并设置正确的附件类型
        """
        allure.attach(
            json.dumps(data, ensure_ascii=False, indent=2),
            name=name,
            attachment_type=allure.attachment_type.JSON
        )
    
    @staticmethod
    def text(text: str, name: str = "文本") -> None:
        """
        添加文本数据作为附件
        
        Args:
            text: 要添加的文本数据
            name: 附件名称，默认为"文本"
        
        说明:
            将文本内容直接添加为附件，并设置正确的附件类型
        """
        allure.attach(
            text,
            name=name,
            attachment_type=allure.attachment_type.TEXT
        )
    
    @staticmethod
    @contextmanager
    def step(name: str):
        """
        步骤上下文管理器，简化步骤的创建
        
        Args:
            name: 步骤名称
        
        使用示例:
            with a.step("步骤1: 准备数据"):
                data = prepare_data()
        
        说明:
            使用Python的上下文管理器(with语句)实现步骤的自动开始和结束
        """
        with allure.step(name):
            yield
    
    @staticmethod
    def add_description(description: str) -> None:
        """
        动态添加测试描述
        
        Args:
            description: Markdown格式的描述文本
        
        说明:
            在测试运行时动态添加或修改测试描述
        """
        allure.dynamic.description(description)
    
    @staticmethod
    def add_title(title: str) -> None:
        """
        动态添加测试标题
        
        Args:
            title: 测试标题
        
        说明:
            在测试运行时动态添加或修改测试标题
        """
        allure.dynamic.title(title)


# 创建一个全局实例方便导入
a = AllureSimple()


def case_decorator(title="", story="", description="", severity="normal", order=0, file_level_order=None, smoke=False, tags=None):
    """
    统一的测试用例装饰器 - 支持两种排序模式
    
    Args:
        title: 测试用例标题，必填
        story: 所属故事/模块，必填
        description: 详细描述，可选
        severity: 严重级别，支持：blocker/critical/normal/minor/trivial，默认normal
        order: 全局执行顺序（兼容老代码），使用pytest-ordering插件，默认0
        file_level_order: 文件级执行顺序（新功能），先按文件串行，再按此值排序，默认None
        smoke: 是否为冒烟测试，默认False
        tags: 标签列表，用于分类和过滤，默认为空
        
    使用说明：
        - 如果使用 order：全局排序，所有文件的测试用例按order值统一排序（可能交叉执行）
        - 如果使用 file_level_order：文件级串行，先执行完文件1的所有测试，再执行文件2
        - 两个参数不要同时使用，优先使用 file_level_order
    """
    severity_map = {
        "blocker": allure.severity_level.BLOCKER,
        "critical": allure.severity_level.CRITICAL,
        "normal": allure.severity_level.NORMAL,
        "minor": allure.severity_level.MINOR,
        "trivial": allure.severity_level.TRIVIAL,
    }
    
    def decorator(func):
        # 使用functools.wraps保留原始函数的元数据
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 只在运行时设置allure信息，不在装饰时重复设置
            if title:
                allure.dynamic.title(title)
            if story:
                allure.dynamic.story(story)
            if description:
                allure.dynamic.description(description)
            if severity:
                allure.dynamic.severity(severity_map.get(severity, allure.severity_level.NORMAL))
            if tags:
                for tag in tags:
                    allure.dynamic.tag(tag)
            
            # 调用原始函数
            return func(*args, **kwargs)
        
        # 根据排序模式选择不同的处理方式
        if file_level_order is not None:
            # 新模式：文件级排序，保存到 _file_level_order 属性
            wrapper._file_level_order = file_level_order
        elif order:
            # 兼容模式：全局排序，使用 pytest-ordering 插件
            wrapper = pytest.mark.run(order=order)(wrapper)
        
        # 应用pytest装饰器
        if smoke:
            wrapper = pytest.mark.smoke(wrapper)
        
        return wrapper
    return decorator


if __name__ == '__main__':
    import os
    import sys
    
    # 支持命令行参数
    report_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), 'reports/allure-report')
    title = sys.argv[2] if len(sys.argv) > 2 else "ERP-AUTOTEST"
    
    fix_report_title(report_dir, title)