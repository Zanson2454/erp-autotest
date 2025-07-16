"""
采购模块的测试初始化
提供配置加载等通用功能
"""

import sys
from pathlib import Path
from typing import Any

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from testcases.comm.base_test import BaseTest, LoginService
from data_factory.base import DataFactory
from utils.cache_util import CacheUtil
from utils.request_util import HttpUtil

class ScmPurBaseTest(BaseTest):
    """采购模块的基础测试类，负责加载采购配置和提供API访问方法"""
    
    # 类型注解
    yaml_util: Any
    apis: Any
    pur_unified_api_path: Any
    md_cache_data: Any
    path_params: Any
    nickname: Any
    user_id: Any
    admin_session: Any
    admin_user_info: Any
    admin_headers: Any

    @classmethod
    def setup_class(cls):
        """
        测试类初始化 - 加载采购配置
        1. 调用父类初始化方法 (包括登录、数据库连接等)
        2. 多门户多用户登录，获取 session
        3. 初始化采购配置文件路径
        4. 加载API配置
        5. 初始化 http 工具，自动带上门户请求头
        """
        super().setup_class()

        portal_keys = {
            "admin": "TERP_PORTAL",
            # "cust": "TERP_CUST_PC"
        }
        tenant_key = "terp"
        login_service = LoginService(cls.env_config)

        # 登录 admin
        admin_result = login_service.login(portal_key=portal_keys["admin"], tenant_key=tenant_key)
        if admin_result.status != admin_result.status.SUCCESS:
            raise RuntimeError(f"admin 登录失败: {admin_result.error_message}")
        cls.admin_session = admin_result.session
        cls.admin_user_info = admin_result.user_info
        cls.http = HttpUtil(
            url=admin_result.portal_url,
            session=admin_result.session,
            headers=admin_result.portal_headers
        )
        cls.admin_headers = admin_result.portal_headers

        # # 登录 cust（如需多门户测试可放开）
        # cust_result = login_service.login(portal_key=portal_keys["cust"], tenant_key=tenant_key)
        # if cust_result.status != cust_result.status.SUCCESS:
        #     raise RuntimeError(f"cust 登录失败: {cust_result.error_message}")
        # cls.cust_session = cust_result.session
        # cls.cust_user_info = cust_result.user_info
        # cls.http_cust = HttpUtil(
        #     url=cust_result.portal_url,
        #     session=cust_result.session,
        #     headers=cust_result.portal_headers
        # )

        # 初始化配置文件路径
        cls.pur_unified_api_path = Path(project_root) / "testdata" / "scm_pur" / "pur_api_info.yaml"
        
        # 从缓存加载统一API配置（性能优化）

        cls.apis =cls.yaml_util.read_yaml(str(cls.pur_unified_api_path)) or {}
        
        # 加载缓存数据
        DataFactory.init_sql_cache(
            sql_config_path=str(project_root / "config" / "erp" / "md_init_sql.yaml"), # 主数据依赖的初始化sql 存放路径
            db_config_name="erp_db", # 数据库配置名称
            cache_key="md_init_cache", # 缓存key
            cache_dir="testdata/cache" # 缓存目录
        )
        cls.md_cache_data = CacheUtil.get('md_init_cache')
        cls.path_params = {"tmodule": "SCM_PUR"}
        cls.nickname = cls.init_data["user_info"]['user_info']["nickname"]
        cls.user_id = cls.init_data["user_info"]['user_info']["id"]

    def get_api_info(self, api_key):
        """
        获取API路径
        """
        api_info = self.apis.get(api_key, {})
        if not api_info:
            raise ValueError(f"API服务名 {api_key} 未找到")
        api_path = api_info.get("path")
        api_method = api_info.get("method","POST")
        if not api_path:
            raise ValueError(f"API服务名 {api_key} 未找到对应的路径")
        api_params = api_info.get("body", {}).copy() if api_info.get("body") else {}
        return {"path":api_path,"method":api_method,"body":api_params}




if __name__ == "__main__":
    ScmPurBaseTest.setup_class()
    print(ScmPurBaseTest.admin_user_info)
    # print(ScmPurBaseTest.cust_user_info)
