import allure
import pytest
from testcases.gen_md import GenMdBaseTest


@allure.epic("通用基础数据")
@allure.feature("调试 - 验证 pytest 发现机制")
class TestSimpleDebug(GenMdBaseTest):
    """纯净测试文件 - 验证 pytest 能否正常发现 GenMdBaseTest 的测试方法"""
    
    def test_simple_method(self):
        """最简单的测试方法 - 无装饰器、无复杂逻辑"""
        self.logger.info("这是一个纯净的测试方法")
        assert True
    
    def test_standard_api_call(self):
        """验证 standard_api_call 方法可用性"""
        try:
            # 测试方法签名
            set_dict = {"test": "value"}
            # 由于没有实际 API，这里只是验证方法存在
            # response, id = self.standard_api_call("TEST_API", set_dict)
            self.logger.info("standard_api_call 方法签名验证通过")
            assert hasattr(self, 'standard_api_call')
            assert hasattr(self, 'mock_util')
        except Exception as e:
            self.logger.error(f"方法验证失败: {e}")
            raise
    
    def test_mock_util(self):
        """验证 mock_util 单例可用性"""
        try:
            code = self.mock_util.generate_unique_code(tag="DEBUG")
            timestamp = self.mock_util.get_timestamp()
            self.logger.info(f"MockData 生成成功: code={code}, timestamp={timestamp}")
            assert code.startswith("AT_")  # 验证唯一码格式
            assert isinstance(timestamp, int)  # 验证时间戳格式
        except Exception as e:
            self.logger.error(f"MockData 测试失败: {e}")
            raise
