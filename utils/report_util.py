import allure
from typing import Dict, Any, List, Optional
from loguru import logger
from datetime import datetime
from enum import Enum


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