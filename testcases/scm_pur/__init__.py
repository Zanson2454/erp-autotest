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

        cls.pur_api_path = Path(project_root) / "testdata" / "scm_pur" / "pur_api_path.yaml"
        cls.pur_api_params_path = Path(project_root) / "testdata" / "scm_pur" / "pur_api_params.yaml"
        # 加载API路径配置和参数配置
        cls.apis = cls.yaml_util.read_yaml(cls.pur_api_path).get("apis", {})
        cls.api_params = cls.yaml_util.read_yaml(cls.pur_api_params_path).get("api_params", {})
        
        # 加载主数据缓存数据
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
    ScmPurBaseTest.setup_class()
    print(ScmPurBaseTest.nickname)
    # print(ScmPurBaseTest.cust_user_info)
