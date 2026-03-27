"""
基础财务模块的测试初始化
提供配置加载等通用功能
"""
import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from typing import Any, Dict
from testcases.comm.base_test import BaseTest
from data_factory.base import DataFactory

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
        cls.load_api_configs()
        cls.load_cache_data()
        cls.bind_context()

    @classmethod
    def load_api_configs(cls):
        """加载 erp_fi 模块 API 配置与门户上下文。"""
        cls.module_login_multi_portal(cls._PORTAL_TYPE_KEYS, tenant_key="terp")

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
        cls.fi_api_path = Path(project_root) / "config" / "api" / "erp_fi" / "fi_api_path.yaml"
        cls.fi_api_params = Path(project_root) / "config" / "api" / "erp_fi" / "fi_api_params.yaml"

        cls.load_module_api_configs(
            cls.fi_api_path,
            cls.fi_api_params,
            api_params_optional=True
        )

    @classmethod
    def load_cache_data(cls):
        """加载 erp_fi 模块依赖缓存。"""
        # 初始化DataFactory（必须在init_sql_cache之前调用）
        DataFactory.__init__(env_name="test")

        # 加载缓存数据：财务模块依赖的初始化SQL (如果存在)
        sql_config_path = str(project_root / "config" / "erp" / "fi_init_sql.yaml")
        if Path(sql_config_path).exists():
            cls.fi_cache_data = cls.load_sql_cache(
                sql_config_path=sql_config_path,
                cache_key="fi_init_cache",
                db_config_name="erp_db",
                cache_dir="testdata/cache",
            )
        else:
            # 复用主数据缓存
            cls.fi_cache_data = cls.md_cache_data if hasattr(cls, "md_cache_data") else {}

    @classmethod
    def bind_context(cls):
        """绑定 erp_fi 模块上下文。"""
        cls.bind_mock_util_singleton()

        # 设置路径参数和用户信息 - 针对ERP_FI模块
        cls.bind_module_user_context("ERP_FI", strict=True)
    
if __name__ == "__main__":
    FiBaseTest.setup_class()
    print(FiBaseTest.nickname)
    # print(FiBaseTest.cust_user_info)
    
    
