# -*- coding: utf-8 -*-
"""
ERP财务模块的测试初始化
提供配置加载等通用功能，为fin_ap, fin_ar, fin_iv等子模块提供基础支持
"""

import sys
from pathlib import Path
import json
import requests

# 获取项目根目录
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from typing import Any, Dict
from testcases.comm.base_test import BaseTest,LoginService
# 移除非必要导入，使用父类或utils中的LoginService
from data_factory.base import DataFactory
from utils.cache_util import CacheUtil
from utils.request_util import HttpUtil
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a  # Allure reporting utility (a.json, a.text)
from utils.yaml_util import YamlUtil  # yaml_util for loading configs

class FinBaseTest(BaseTest):
    """ERP财务模块的基础测试类，负责加载财务通用配置和提供API访问方法"""
    
    # 类型提示：继承的动态属性
    yaml_util: Any
    
    # 门户配置（仅admin）
    _ADMIN_PORTAL_KEY = "TERP_PORTAL"
    
    # Mock单例
    _mock_instance = None
    
    @classmethod
    def setup_class(cls):
        """
        测试类初始化 - 加载财务通用配置
        1. 调用父类初始化方法 (包括数据库连接、环境配置等)
        2. 仅登录admin门户，获取 session/user_info/headers
        3. 初始化财务配置文件路径 (erp_fin specific)
        4. 加载API路径和参数配置 (from fin_api_path.yaml / fin_api_params.yaml)
        5. 初始化 http 工具，自动带上admin门户请求头
        6. DataFactory和缓存初始化 (fin specific, fallback to md)
        7. 设置路径参数和用户信息
        """
        super().setup_class()
        
        # Mock单例初始化 (兼容子模块如 fin_iv 的 self.mock_util)
        if cls._mock_instance is None:
            cls._mock_instance = MockData()
        cls.mock_util = cls._mock_instance
        
        # 登录服务初始化 (使用utils中的LoginService)
        cls.login_service = LoginService(cls.env_config)
        
        # 仅登录admin门户
        tenant_key = "terp"
        admin_result = cls.login_service.login(portal_key=cls._ADMIN_PORTAL_KEY, tenant_key=tenant_key)
        if admin_result.status != admin_result.status.SUCCESS:
            raise RuntimeError(f"admin 登录失败: {admin_result.error_message}")
        
        # 检查portal_url
        portal_url = admin_result.portal_url or ""
        if not isinstance(portal_url, str) or not portal_url:
            raise ValueError("admin portal_url 不能为空且必须为字符串")
        
        # 保存admin相关变量
        cls.session = admin_result.session
        cls.user_info = admin_result.user_info
        cls.portal_url = portal_url
        cls.portal_headers = admin_result.portal_headers
        
        # 初始化 http (仅admin)
        cls.http = HttpUtil(
            url=portal_url,
            session=admin_result.session,
            headers=admin_result.portal_headers
        )
        
        # 初始化配置文件路径 (erp_fin specific)
        cls.fin_api_path = Path(project_root) / "testdata" / "erp_fin" / "fin_api_path.yaml"
        cls.fin_api_params = Path(project_root) / "testdata" / "erp_fin" / "fin_api_params.yaml"
        
        # 加载API配置
        cls.yaml_util = YamlUtil()  # or inherit from super if available
        cls.apis = cls.yaml_util.read_yaml(cls.fin_api_path).get("apis", {})
        cls.api_params = cls.yaml_util.read_yaml(cls.fin_api_params).get("api_params", {})
        
        # DataFactory init (env=test)
        DataFactory.__init__(env_name="test")
        
        # 缓存加载：财务主数据依赖 (use md_init_sql.yaml or fin specific like pur/sls_init_sql.yaml)
        # Fallback to md cache for org/currency, etc.
        DataFactory.init_sql_cache(
            sql_config_path=str(project_root / "config" / "erp" / "base_init_sql.yaml"),  # base or fin specific
            db_config_name="erp_db",
            cache_key="fin_init_cache",  # fin specific cache key
            cache_dir="testdata/cache"
        )
        cls.fin_cache_data = CacheUtil.get('fin_init_cache')
        
        # MD cache reuse (for org_info, currency, etc. - shared with gen_md)
        cls.md_cache_data = CacheUtil.get('md_init_cache')  # fallback if not in fin_cache
        
        # 初始化配置数据 (from init_data, e.g., currency)
        if cls.init_data:
            cls.curr_id = cls.init_data.get("currency_info",[])[0].get("curr_id")
        
        # 初始化MD (org, partner, etc.)
        if cls.md_cache_data:
            cls.com_org_id = cls.md_cache_data.get("org_info",{}).get("gr_come_org_info",[])[0].get("id")
            cls.sls_org_id = cls.md_cache_data.get("org_info",{}).get("sls_org_info",[])[0].get("id")
            cls.inv_org_id = cls.md_cache_data.get("org_info",{}).get("inv_org_info",[])[0].get("id")
            cls.cust_id = cls.md_cache_data.get("partner_info",{}).get("cust_info",[])[0].get("id")
        
        # 设置路径参数和用户信息
        cls.path_params = {"tmodule": "FIN"}  # erp_fin module
        cls.nickname = cls.init_data["user_info"]['user_info']["nickname"] if cls.init_data and "user_info" in cls.init_data else "test_user"
        cls.user_id = cls.init_data["user_info"]['user_info']["id"] if cls.init_data and "user_info" in cls.init_data else 1
    
    def get_api_path(self, api_key):
        """
        获取API路径 (erp_fin specific, using ParamUtil)
        """
        return ParamUtil.get_api_path(self.apis, api_key)
    
    def get_api_params(self, api_path, with_query_params=None):
        """
        获取API请求参数和完整URL (erp_fin specific)
        """
        return ParamUtil.get_api_params(self.api_params, api_path, with_query_params)
    
    @classmethod
    def teardown_class(cls):
        """测试类清理 (beyond super)"""
        super().teardown_class()
        # fin specific cleanup if needed (e.g., clear fin_cache)
        cls.logger.info("ERP财务模块测试类清理完成")


if __name__ == "__main__":
    FinBaseTest.setup_class()
    print(FinBaseTest.nickname)
    print(f"FIN APIs loaded: {len(FinBaseTest.apis)}")
    # Test cache
    if hasattr(FinBaseTest, 'fin_cache_data'):
        print(f"FIN Cache keys: {list(FinBaseTest.fin_cache_data.keys())}")
    if hasattr(FinBaseTest, 'md_cache_data'):
        print(f"MD Cache keys: {list(FinBaseTest.md_cache_data.keys())}")
