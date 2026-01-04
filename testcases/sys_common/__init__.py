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
from testcases.comm.base_test import BaseTest, LoginService
from utils.request_util import HttpUtil


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

        # 初始化登录服务，避免重复创建
        cls.login_service = LoginService(cls.env_config)
        
        # 登录门户，分别保存 session/user_info/headers/url
        cls.sessions = {}
        cls.user_infos = {}
        cls.http_clients = {}
        cls.portal_urls = {}
        cls.portal_headers = {}
        
        tenant_key = "terp"
        for role, portal_key in cls._PORTAL_TYPE_KEYS.items():
            result = cls.login_service.login(portal_key=portal_key, tenant_key=tenant_key)
            if result.status != result.status.SUCCESS:
                raise RuntimeError(f"{role} 登录失败: {result.error_message}")
            portal_url = result.portal_url or ""
            if not isinstance(portal_url, str) or not portal_url:
                raise ValueError(f"{role} portal_url 不能为空且必须为字符串")
            cls.sessions[role] = result.session
            cls.user_infos[role] = result.user_info
            cls.portal_urls[role] = portal_url
            cls.portal_headers[role] = result.portal_headers
            cls.http_clients[role] = HttpUtil(
                url=portal_url,
                session=result.session,
                headers=result.portal_headers
            )

        # 兼容原有写法
        cls.http = cls.http_clients["admin"]
        cls.admin_session = cls.sessions["admin"]
        cls.admin_user_info = cls.user_infos["admin"]
        cls.admin_headers = cls.portal_headers["admin"]

        # 初始化配置文件路径
        cls.common_api_path = Path(project_root) / "config" / "api" / "sys_common" / "common_api_path.yaml"
        cls.common_api_params = Path(project_root) / "config" / "api" / "sys_common" / "common_api_params.yaml"
        
        # 加载API路径配置和参数配置
        cls.apis = cls.yaml_util.read_yaml(cls.common_api_path).get("apis", {})
        cls.api_params = cls.yaml_util.read_yaml(cls.common_api_params).get("api_params", {})
        
        # 初始化路径参数
        cls.path_params = {"tmodule": "SYS_COMMON"}
        cls.nickname = cls.init_data["user_info"]['user_info']["nickname"]
        cls.user_id = cls.init_data["user_info"]['user_info']["id"]
        cls.logger.debug(f"SysCommonBaseTest初始化完成: nickname: {cls.nickname}, user_id: {cls.user_id}")

    def get_api_path(self, api_key):
        """
        获取API路径
        """
        return super().get_api_path(api_key, self.apis)
    
    def get_api_params(self, api_path, with_query_params=None):
        """
        获取API请求参数和完整URL
        自动添加 tmodule 查询参数
        """
        # 构建查询参数字符串
        if with_query_params:
            query_str = f"{with_query_params}&tmodule={self.path_params['tmodule'].lower()}"
        else:
            query_str = f"tmodule={self.path_params['tmodule'].lower()}"
        
        return super().get_api_params(api_path, self.api_params, query_str)
      
   


if __name__ == "__main__":
    SysCommonBaseTest.setup_class()

