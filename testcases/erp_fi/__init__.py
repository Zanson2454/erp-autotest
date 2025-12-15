"""
基础财务模块的测试初始化
提供配置加载等通用功能
"""
import sys
from pathlib import Path
import json
import requests

# 获取项目根目录
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from typing import Any, Dict
from testcases.comm.base_test import BaseTest, LoginService
from data_factory.base import DataFactory
from utils.cache_util import CacheUtil
from utils.request_util import HttpUtil
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a  # Allure reporting utility (a.json, a.text)

class FiBaseTest(BaseTest):
    """基础财务模块的基础测试类，负责加载通用配置和提供API访问方法"""
    
    # 类型提示：继承的动态属性
    yaml_util: Any
    
    # 登录两个门户，分别保存 session/user_info/headers/url
    _PORTAL_TYPE_KEYS: Dict[str, str] = {
        "admin": "TERP_PORTAL",
        "cust": "TERP_CUST_PC"
    }
    _mock_instance = None

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
        
        # 优化单例创建：仅在 super().setup_class() 后执行
        # 确保环境就绪，不干扰 pytest 测试收集过程
        if cls._mock_instance is None:
            cls._mock_instance = MockData()
        
        # 设置类级 mock_util 以兼容现有代码 (cls.mock_util)
        # 现有测试类可继续使用 cls.mock_data 或迁移到 cls.mock_util
        cls.mock_util = cls._mock_instance
        
        # 初始化登录服务，避免重复创建
        cls.login_service = LoginService(cls.env_config)
        
        # 登录两个门户，分别保存 session/user_info/headers/url
        cls.sessions = {}
        cls.user_infos = {}
        cls.http_clients = {}
        cls.portal_urls = {}
        cls.portal_headers = {}

        for role, portal_key in cls._PORTAL_TYPE_KEYS.items():
            result = cls.login_service.login(portal_key=portal_key, tenant_key="terp")
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
        cls.http_cust = cls.http_clients["cust"]
        cls.admin_session = cls.sessions["admin"]
        cls.cust_session = cls.sessions["cust"]
        cls.admin_user_info = cls.user_infos["admin"]
        cls.cust_user_info = cls.user_infos["cust"]
        cls.admin_headers = cls.portal_headers["admin"]
        cls.cust_headers = cls.portal_headers["cust"]
     
        # 初始化配置文件路径 - 针对erp_fi模块
        cls.fi_api_path = Path(project_root) / "testdata" / "erp_fi" / "fi_api_path.yaml"
        cls.fi_api_params = Path(project_root) / "testdata" / "erp_fi" / "fi_api_params.yaml"
        
        # 加载API路径配置和参数配置
        cls.apis = cls.yaml_util.read_yaml(cls.fi_api_path).get("apis", {})
        cls.api_params = cls.yaml_util.read_yaml(cls.fi_api_params).get("api_params", {}) if Path(cls.fi_api_params).exists() else {}
        
        # 初始化DataFactory（必须在init_sql_cache之前调用）
        DataFactory.__init__(env_name="test")
        
        # 加载缓存数据：财务模块依赖的初始化SQL (如果存在)
        sql_config_path = str(project_root / "config" / "erp" / "fi_init_sql.yaml")
        if Path(sql_config_path).exists():
            DataFactory.init_sql_cache(
                sql_config_path=sql_config_path,
                db_config_name="erp_db",  # 数据库配置名称
                cache_key="fi_init_cache",  # 缓存key
                cache_dir="testdata/cache"  # 缓存目录
            )
            cls.fi_cache_data = CacheUtil.get('fi_init_cache')
        else:
            # 复用主数据缓存
            cls.fi_cache_data = cls.md_cache_data if hasattr(cls, 'md_cache_data') else {}
        
        # 设置路径参数和用户信息 - 针对ERP_FI模块
        cls.path_params = {"tmodule":"ERP_FI"}
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

    def set_request_param(self, params, key, value):
        """
        设置请求参数中的值，简化嵌套访问
        
        参数:
            params: 请求参数字典
            key: 参数键名
            value: 参数值
        
        返回:
            更新后的参数字典
        """
        if 'params' not in params:
            params['params'] = {}
        if 'request' not in params['params']:
            params['params']['request'] = {}
            
        params['params']['request'][key] = value
        return params
    
    def set_request_params(self, params, param_dict):
        """
        批量设置请求参数，简化嵌套访问
        
        参数:
            params: 请求参数字典
            param_dict: 要设置的参数字典 {key: value, ...}
        
        返回:
            更新后的参数字典
        """
        if 'params' not in params:
            params['params'] = {}
        if 'request' not in params['params']:
            params['params']['request'] = {}
            
        for key, value in param_dict.items():
            params['params']['request'][key] = value
        return params
    

if __name__ == "__main__":
    FiBaseTest.setup_class()
    print(FiBaseTest.nickname)
    # print(FiBaseTest.cust_user_info)
    
    