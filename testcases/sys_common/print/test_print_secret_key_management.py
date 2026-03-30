import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.sys_common import SysCommonBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("系统通用模块")
@allure.feature("打印密钥管理")
@pytest.mark.skip(reason="接口配置缺失或已漂移，暂时跳过")
class TestPrintSecretKeyManagement(SysCommonBaseTest):
    """打印密钥管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.logger.info("打印密钥管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 获取公钥通常不产生持久化数据，无需清理
            cls.logger.info("打印密钥测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
        super().teardown_class()
    @case_decorator(
        story="打印密钥管理",
        title="测试获取公钥",
        description="验证API_PRINT_PRINT_SECRET_KEY_GET_PUBLIC_SECRET_KEY_POST功能 - 获取公钥",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["sys_common", "print", "secret_key", "get_public"]
    )
    def test_print_secret_key_get_public_post(self):
        """测试获取公钥 - API_PRINT_PRINT_SECRET_KEY_GET_PUBLIC_SECRET_KEY_POST"""
        try:
            # 1. 准备测试数据（获取公钥通常无需输入参数）
            # 如果需要特定参数，如密钥类型或场景ID，可在此添加
            
            # 2. 调用API
            api_path = self.get_api_path("打印密钥-获取公钥")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理（假设无特定输入参数，或使用默认）
            filtered_params = ParamUtil.filter_post_body_fields(
                params, [],  # 无需过滤特定字段
                ["params", "request"]
            )
            # 如果需要设置参数，如密钥用途，可在此添加set_dict
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="打印密钥-获取公钥",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 5. 验证公钥数据
            key_data = response.get("data", {}).get("data", {})
            public_key = key_data.get("publicKey") or key_data.get("secretKey")
            self.assert_util.assert_by_operator(public_key, "not_empty", "公钥不应为空")
            self.assert_util.assert_by_operator(
                isinstance(public_key, str) and len(public_key) > 50, 
                "=", True, "公钥应为有效字符串（长度>50）"
            )
            
            # 保存公钥供后续使用（可选）
            if hasattr(self, 'public_key_cache'):
                self.public_key_cache = public_key
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"获取公钥: {public_key[:50]}...", "公钥摘要（前50字符）")
            self.logger.info("成功获取打印公钥")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
