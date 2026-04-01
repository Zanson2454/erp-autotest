"""
交货单模块的测试初始化
提供配置加载等通用功能
"""

import sys
from pathlib import Path
from typing import Any

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from testcases.comm.base_test import BaseTest
from testcases.comm.test_data_context import TestDataContext


class ScmDelBaseTest(BaseTest):
    """交货单模块的基础测试类，负责加载交货单配置和提供API访问方法"""
    
    # 类型注解
    yaml_util: Any

    DEFAULT_CACHE_MAPPINGS = {
        **BaseTest.DEFAULT_CACHE_MAPPINGS,
        "dn_type_id": "scm_del_config.dn_type_info.id",
        "dn_item_type_id": "scm_del_config.dn_item_type_info.id",
    }
    REQUIRED_CACHE_KEYS = (
        "curr_id",
        "cust_id",
        "dn_type_id",
        "dn_item_type_id",
    )
    
    # 登录两个门户，分别保存 session/user_info 并初始化 http 工具
    _PORTAL_TYPE_KEYS = {
        "admin": "TERP_PORTAL",
        "cust": "TERP_CUST_PC"
    }

    @classmethod
    def setup_class(cls):
        """
        测试类初始化 - 加载交货单配置
        1. 调用父类初始化方法 (包括登录、数据库连接等)
        2. 多门户多用户登录，获取 session
        3. 初始化交货单配置文件路径
        4. 加载API配置
        5. 初始化 http 工具，自动带上门户请求头
        """
        super().setup_class()
        cls.load_api_configs()
        cls.load_cache_data()
        cls.bind_context()

    @classmethod
    def load_api_configs(cls):
        """加载交货模块 API 配置与门户上下文。"""
        cls.module_login_admin_with_cust_headers(
            admin_portal_key=cls._PORTAL_TYPE_KEYS["admin"],
            cust_portal_key=cls._PORTAL_TYPE_KEYS["cust"],
            tenant_key="terp",
        )

        # 初始化交货单模块配置文件路径
        cls.del_api_path = Path(project_root) / "config" / "api" / "scm_del" / "del_api_path.yaml"
        cls.del_api_params_path = Path(project_root) / "config" / "api" / "scm_del" / "del_api_params.yaml"
        cls.load_module_api_configs(cls.del_api_path, cls.del_api_params_path)

    @classmethod
    def load_cache_data(cls):
        """加载交货模块依赖缓存。"""
        TestDataContext.register_source("scm_del_config", "del_cache_data")
        # 加载主数据缓存（交货单依赖物料、组织等主数据）
        cls.md_cache_data = cls.load_sql_cache(
            sql_config_path=project_root / "config" / "erp" / "md_init_sql.yaml",
            cache_key="md_init_cache",
            db_config_name="erp_db",
            cache_dir="testdata/cache",
        )

        # 加载交货单配置数据
        cls.del_cache_data = cls.load_sql_cache(
            sql_config_path=project_root / "config" / "erp" / "del_init_sql.yaml",
            cache_key="del_init_cache",
            db_config_name="erp_db",
            cache_dir="testdata/cache",
        )

    @classmethod
    def bind_context(cls):
        """绑定交货模块上下文。"""
        cls.bind_cache_data()
        cls.bind_module_user_context("SCM_DEL", strict=True)

        cls.logger.info(f"✅ md_cache_data 加载完成: {cls.md_cache_data is not None}")
        cls.logger.info(f"✅ del_cache_data 加载完成: {cls.del_cache_data is not None}")
        cls.logger.info(f"✅ init_data 加载完成: {cls.init_data is not None}")
        
        
if __name__ == "__main__":
    ScmDelBaseTest.setup_class()
    print(ScmDelBaseTest.nickname)
    # print(ScmDelBaseTest.cust_user_info)
