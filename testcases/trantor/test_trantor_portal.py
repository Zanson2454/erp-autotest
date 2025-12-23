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
    
    @case_decorator(
        story="WebSocket连接",
        title="测试获取WebSocket Token",
        description="验证Trantor门户WebSocket Token接口功能 - 获取/api/mw/websocket/getToken",
        severity="normal",
        file_level_order=4,
        tags=["trantor", "websocket", "token"]
    )
    def test_get_websocket_token(self):
        """测试获取WebSocket Token"""
        try:
            # 使用标准化API调用
            # POST请求，请求体为空
            response, _ = self.standard_api_call(
                api_key="获取WebSocket Token",
                set_dict=None,
                method="POST"
            )
            
            # 业务断言：验证响应数据
            self.assert_util.assert_response_data(response)
            
            # 记录响应数据
            a.json(response, "WebSocket Token响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="用户信息",
        title="测试获取当前登录用户信息",
        description="验证Trantor门户当前登录用户信息接口功能 - 获取/api/trantor/portal/user/current",
        severity="normal",
        file_level_order=5,
        tags=["trantor", "portal", "user", "current"]
    )
    def test_get_current_user(self):
        """测试获取当前登录用户信息"""
        try:
            # 使用标准化API调用
            # GET请求，无需参数
            response, _ = self.standard_api_call(
                api_key="获取当前登陆用户",
                set_dict=None,
                method="GET"
            )
            
            # 业务断言：验证响应数据
            self.assert_util.assert_response_data(response)
            
            # 记录响应数据
            a.json(response, "当前登录用户信息响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="工作台应用",
        title="测试获取工作台应用列表",
        description="验证Trantor门户工作台应用列表接口功能 - 获取/api/trantor/portal/application/list",
        severity="normal",
        file_level_order=6,
        tags=["trantor", "portal", "application", "list"]
    )
    def test_get_application_list(self):
        """测试获取工作台应用列表"""
        try:
            # 使用标准化API调用
            # GET请求，无需参数
            response, _ = self.standard_api_call(
                api_key="获取工作台应用",
                set_dict=None,
                method="GET"
            )
            
            # 业务断言：验证响应数据
            self.assert_util.assert_response_data(response)
            
            # 记录响应数据
            a.json(response, "工作台应用列表响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="图标信息",
        title="测试查询图标信息",
        description="验证Trantor门户图标信息接口功能 - 获取/api/trantor/portal/icon",
        severity="normal",
        file_level_order=7,
        tags=["trantor", "portal", "icon"]
    )
    def test_get_icon(self):
        """测试查询图标信息"""
        try:
            # 使用标准化API调用
            # GET请求，无需参数
            response, _ = self.standard_api_call(
                api_key="查询图标",
                set_dict=None,
                method="GET"
            )
            
            # 业务断言：验证响应数据
            self.assert_util.assert_response_data(response)
            
            # 记录响应数据
            a.json(response, "图标信息响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="AI通知连接",
        title="测试获取AI通知连接",
        description="验证Trantor AI通知连接接口功能 - 获取/api/trantor/ai/notice-connection",
        severity="normal",
        file_level_order=8,
        tags=["trantor", "ai", "notice", "connection"]
    )
    @pytest.mark.skip(reason="这是一个SSE流式响应接口，暂时跳过")
    def test_get_ai_notice_connection(self):
        """测试获取AI通知连接"""
        try:
            # 使用标准化API调用
            # GET请求，无需参数（SSE流式响应接口）
            response, _ = self.standard_api_call(
                api_key="notice-connection",
                set_dict=None,
                method="GET"
            )
            
            # 业务断言：验证响应数据
            # 注意：这是一个SSE流式响应接口，响应可能是文本格式
            self.assert_util.assert_by_operator(response, "not_empty", message="HTTP 状态码验证失败：响应为空，期望状态码为 200")
            
            # 记录响应数据
            a.json(response, "AI通知连接响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="AI会话管理",
        title="测试创建新的AI会话",
        description="验证Trantor AI新建会话接口功能 - 创建/api/trantor/ai/new-session",
        severity="normal",
        file_level_order=9,
        tags=["trantor", "ai", "session", "new"]
    )
    def test_create_ai_new_session(self):
        """测试创建新的AI会话"""
        try:
            # 准备测试数据
            # 使用标准化API调用
            set_dict = {
                "agentKey": "AI$erp_main_agent",
                "greetings": f"{self.mock_util.get_mock_name()} 您好！\n当前有待办任务 0 件，风险项目 0 条\n您想详细展开哪个方面？",
                "greetingsRelatedTools": []
            }
            
            response, _ = self.standard_api_call(
                api_key="new-session",
                set_dict=set_dict,
                method="POST"
            )
            
            # 业务断言：验证响应数据
            self.assert_util.assert_response_data(response)
            
            # 记录响应数据
            a.json(response, "新建AI会话响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

