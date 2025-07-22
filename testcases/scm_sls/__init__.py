"""
销售管理模块的测试初始化
提供配置加载等通用功能
"""
import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from typing import Any, Dict
from testcases.comm.base_test import BaseTest, LoginService
from data_factory.base import DataFactory
from utils.cache_util import CacheUtil
from utils.request_util import HttpUtil

class SlsBase(BaseTest):
    """销售管理模块的基础测试类，负责加载销售配置和提供API访问方法"""
    
    # 类型提示：继承的动态属性
    yaml_util: Any
    
    # 登录两个门户，分别保存 session/user_info 并初始化 http 工具
    _PORTAL_TYPE_KEYS: Dict[str, str] = {
        "admin": "TERP_PORTAL",
        "cust": "TERP_CUST_PC"
    }
    
    @classmethod
    def setup_class(cls):
        """
        测试类初始化 - 加载销售配置
        1. 调用父类初始化方法 (包括登录、数据库连接等)
        2. 多门户多用户登录，获取 session
        3. 初始化销售配置文件路径
        4. 加载API路径和参数配置
        5. 初始化 http 工具，自动带上门户请求头
        6. 加载销售缓存数据
        """
        super().setup_class()

        cls.login_service = LoginService(cls.env_config)  # 初始化一次登录服务，避免重复创建
        # 登录 admin
        admin_result = cls.login_service.login(portal_key=cls._PORTAL_TYPE_KEYS["admin"])
        if admin_result.status != admin_result.status.SUCCESS:
            raise RuntimeError(f"admin 登录失败: {admin_result.error_message}")
        
        # 初始化 cust 的 headers
        cls.admin_headers = admin_result.portal_headers
        if cls.admin_headers:
            cls.cust_portal_headers = cls.admin_headers.copy()  
        cust_portal_referer = cls.env_config.get("portal_config",{}).get('terp',{}).get("TERP_CUST_PC",{}).get("portal_referer")
        cls.cust_portal_headers["Referer"] = cust_portal_referer
        cls.logger.info(f"cust_portal_headers: {cls.cust_portal_headers}")
  
        # 初始化 http 实例
        cls.http = HttpUtil(
            url=admin_result.portal_url,
            session=admin_result.session,
            headers=admin_result.portal_headers
        )
     
        # 初始化配置文件路径
        cls.sls_api_path = Path(project_root) / "testdata" / "scm_sls" / "sls_api_path.yaml"
        cls.sls_api_params = Path(project_root) / "testdata" / "scm_sls" / "sls_api_params.yaml"
        
        # 加载API路径配置和参数配置
        cls.apis = cls.yaml_util.read_yaml(cls.sls_api_path).get("apis", {})
        cls.api_params = cls.yaml_util.read_yaml(cls.sls_api_params).get("api_params", {})
        
        # 初始化DataFactory（必须在init_sql_cache之前调用）
        DataFactory.__init__(env_name="test")
        
             # 加载缓存数据
        DataFactory.init_sql_cache(
            sql_config_path=str(project_root / "config" / "erp" / "md_init_sql.yaml"), # 主数据依赖的初始化sql 存放路径
            db_config_name="erp_db", # 数据库配置名称
            cache_key="md_init_cache", # 缓存key
            cache_dir="testdata/cache" # 缓存目录
        )
        cls.md_cache_data = CacheUtil.get('md_init_cache')
        
        
        DataFactory.init_sql_cache(
            sql_config_path=str(project_root / "config" / "erp" / "sls_init_sql.yaml"), # 销售管理依赖的初始化sql 存放路径
            db_config_name="erp_db", # 数据库配置名称
            cache_key="sls_init_cache", # 缓存key
            cache_dir="testdata/cache" # 缓存目录
        )
        cls.sls_cache_data = CacheUtil.get('sls_init_cache')

        cls.path_params = {"tmodule": "SCM_SLS"}
        cls.nickname = cls.init_data["user_info"]['user_info']["nickname"]
        cls.user_id = cls.init_data["user_info"]['user_info']["id"]

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
    SlsBase.setup_class()
    print(SlsBase.nickname)
    print(SlsBase.ORDER_TYPES)
    print(SlsBase.ORDER_LINE_TYPES)
    print(SlsBase.ORDER_TYPE_LINE_COMBINATIONS)