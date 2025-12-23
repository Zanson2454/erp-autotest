import allure
import pytest
from testcases.trantor import TrantorBaseTest
from utils.report_util import a, case_decorator


@allure.epic("Trantor框架模块")
@allure.feature("门户管理")
class TestTrantorPortal(TrantorBaseTest):
    """Trantor门户管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.logger.info("Trantor门户管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 此测试类不涉及数据库操作，无需清理
            cls.logger.info("Trantor门户管理测试类清理完成")
        except Exception as e:
            cls.logger.error(f"测试类清理失败: {str(e)}")
    
    @case_decorator(
        story="门户版本信息",
        title="测试获取最新版本信息",
        description="验证Trantor门户最新版本信息接口功能 - 获取latest.json",
        severity="normal",
        file_level_order=1,
        tags=["trantor", "portal", "version"]
    )
    def test_get_latest_version(self):
        """测试获取最新版本信息"""
        try:
            # 使用标准化API调用
            # GET请求，无需参数
            response, _ = self.standard_api_call(
                api_key="获取最新版本信息",
                set_dict=None,
                method="GET"
            )
            
            # 验证 HTTP 状态码为 200
            # standard_api_call 在状态码非 2xx 时会抛出异常，成功返回即表示状态码为 200
            # 通过验证响应不为空来间接验证状态码为 200
            self.assert_util.assert_by_operator(response, "not_empty", message="HTTP 状态码验证失败：响应为空，期望状态码为 200")
            
            # 记录响应数据
            a.json(response, "最新版本信息响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="门户信息",
        title="测试获取当前门户信息",
        description="验证Trantor门户当前门户信息接口功能 - 获取/api/trantor/portal/current",
        severity="normal",
        file_level_order=2,
        tags=["trantor", "portal", "current"]
    )
    def test_get_current_portal(self):
        """测试获取当前门户信息"""
        try:
            # 使用标准化API调用
            # GET请求，无需参数
            response, _ = self.standard_api_call(
                api_key="获取当前门户信息",
                set_dict=None,
                method="GET"
            )
            
            # 业务断言：验证响应数据
            self.assert_util.assert_response_data(response)
            
            # 记录响应数据
            a.json(response, "当前门户信息响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="门户功能引导",
        title="测试获取功能引导信息",
        description="验证Trantor门户功能引导信息接口功能 - 获取/api/trantor/portal/feature-guide",
        severity="normal",
        file_level_order=3,
        tags=["trantor", "portal", "feature-guide"]
    )
    def test_get_feature_guide(self):
        """测试获取功能引导信息"""
        try:
            # 使用标准化API调用
            # GET请求，无需参数
            response, _ = self.standard_api_call(
                api_key="查询功能引导配置",
                set_dict=None,
                method="GET"
            )
            
            # 业务断言：验证响应数据
            self.assert_util.assert_by_operator(response, "not_empty", message="HTTP 状态码验证失败：响应为空，期望状态码为 200")
            
            # 记录响应数据
            a.json(response, "功能引导信息响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

