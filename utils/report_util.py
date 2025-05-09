import allure
from typing import Dict, Any, List
from loguru import logger
from datetime import datetime

class ReportEnhancer:
    """测试报告增强类，用于丰富测试报告内容"""
    
    def __init__(self):
        self.report_data: Dict[str, Any] = {}
        self._steps: List[Dict[str, Any]] = []
    
    @allure.step("添加测试步骤")
    def add_test_step(self, step_name: str, details: Dict[str, Any] = None):
        """添加测试步骤
        
        Args:
            step_name: 步骤名称
            details: 步骤详情
        """
        step = {
            "name": step_name,
            "time": datetime.now().isoformat(),
            "details": details or {}
        }
        self._steps.append(step)
        logger.info(f"步骤: {step_name}")
        if details:
            logger.debug(f"详情: {details}")
    
    @allure.step("添加截图")
    def add_screenshot(self, name: str, image_data: bytes):
        """添加截图
        
        Args:
            name: 截图名称
            image_data: 图片数据
        """
        allure.attach(
            image_data,
            name=name,
            attachment_type=allure.attachment_type.PNG
        )
    
    @allure.step("添加性能指标")
    def add_metrics(self, metrics: Dict[str, Any]):
        """添加性能指标
        
        Args:
            metrics: 性能指标字典
        """
        self.report_data["metrics"] = metrics
        allure.attach(
            str(metrics),
            name="性能指标",
            attachment_type=allure.attachment_type.TEXT
        )
    
    def get_report_data(self) -> Dict[str, Any]:
        """获取报告数据
        
        Returns:
            报告数据字典
        """
        return {
            "steps": self._steps,
            **self.report_data
        } 