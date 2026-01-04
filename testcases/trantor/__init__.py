"""
Trantor框架模块的测试初始化
提供配置加载等通用功能
"""
import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from typing import Any
from testcases.comm.base_test import BaseTest


class TrantorBaseTest(BaseTest):
    """Trantor框架模块的基础测试类，负责加载Trantor配置和提供API访问方法"""
    
    # 类型提示：继承的动态属性
    yaml_util: Any
    
    @classmethod
    def setup_class(cls):
        """
        测试类初始化 - 加载Trantor配置
        1. 调用父类初始化方法 (包括登录、数据库连接等)
        2. 初始化Trantor配置文件路径
        3. 加载API路径和参数配置
        """
        super().setup_class()

        # 初始化配置文件路径
        cls.trantor_api_path = Path(project_root) / "config" / "api" / "trantor" / "api_api_path.yaml"
        cls.trantor_api_params = Path(project_root) / "config" / "api" / "trantor" / "api_api_params.yaml"
        
        # 加载API路径配置和参数配置
        cls.apis = cls.yaml_util.read_yaml(cls.trantor_api_path).get("apis", {})
        cls.api_params = cls.yaml_util.read_yaml(cls.trantor_api_params).get("api_params", {})
        
        cls.logger.info("TrantorBaseTest初始化完成")

    def get_api_path(self, api_key):
        """
        获取API路径
        """
        return super().get_api_path(api_key, self.apis)
    
    def get_api_params(self, api_path, with_query_params=None):
        """
        获取API请求参数和完整URL
        """
        return super().get_api_params(api_path, self.api_params, with_query_params)


if __name__ == "__main__":
    TrantorBaseTest.setup_class()

