"""
系统公共模块的测试初始化
提供配置加载等通用功能
"""
import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from typing import Any, Dict
from testcases.comm.base_test import BaseTest


class SysCommonBaseTest(BaseTest):
    """系统公共模块的基础测试类，负责加载通用配置和提供API访问方法"""
    
    # 类型提示：继承的动态属性
    yaml_util: Any
    
    # 门户配置（仅admin）
    _PORTAL_TYPE_KEYS: Dict[str, str] = {
        "admin": "TERP_PORTAL"
    }
    
    @classmethod
    def setup_class(cls):
        """
        测试类初始化 - 加载通用配置
        1. 调用父类初始化方法 (包括登录、数据库连接等)
        2. 多门户多用户登录，获取 session
        3. 初始化通用配置文件路径
        4. 加载API路径和参数配置
        5. 初始化 http 工具，自动带上门户请求头
        """
        super().setup_class()
        cls.load_api_configs()
        cls.bind_context()

    @classmethod
    def load_api_configs(cls):
        """加载 sys_common 模块 API 配置与门户上下文。"""
        cls.module_login_multi_portal(cls._PORTAL_TYPE_KEYS, tenant_key="terp")

        # 兼容原有写法
        cls.http = cls.http_clients["admin"]
        cls.admin_session = cls.sessions["admin"]
        cls.admin_user_info = cls.user_infos["admin"]
        cls.admin_headers = cls.portal_headers["admin"]

        # 初始化配置文件路径
        cls.common_api_path = Path(project_root) / "config" / "api" / "sys_common" / "common_api_path.yaml"
        cls.common_api_params = Path(project_root) / "config" / "api" / "sys_common" / "common_api_params.yaml"
        
        cls.load_module_api_configs(cls.common_api_path, cls.common_api_params)

    @classmethod
    def bind_context(cls):
        """绑定 sys_common 模块上下文。"""
        # 初始化路径参数
        cls.bind_module_user_context("SYS_COMMON", strict=True)
        cls.logger.debug(f"SysCommonBaseTest初始化完成: nickname: {cls.nickname}, user_id: {cls.user_id}")

    def get_api_params(self, api_path, with_query_params=None):
        """
        获取API请求参数和完整URL
        自动添加 tmodule 查询参数
        """
        tmodule_part = f"tmodule={self.path_params['tmodule'].lower()}"

        # 构建查询参数字符串
        if with_query_params:
            existing = str(with_query_params)
            if "tmodule=" in existing:
                query_str = existing
            else:
                query_str = f"{existing}&{tmodule_part}"
        else:
            query_str = tmodule_part
        
        return super().get_api_params(api_path, self.api_params, query_str)
      
   


if __name__ == "__main__":
    SysCommonBaseTest.setup_class()
