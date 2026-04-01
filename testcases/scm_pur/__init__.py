"""
采购模块的测试初始化
提供配置加载等通用功能
"""

import sys
import os
from pathlib import Path
from typing import Any

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from testcases.comm.base_test import BaseTest
from testcases.comm.cleanup_registry import register_cleanup
from testcases.comm.test_data_context import TestDataContext
from data_factory.base import DataFactory
from utils.mysql_util import DBManager


def _cleanup_scm_pur() -> None:
    """SCM_PUR 统一清理入口：由 cleanup_registry 在 session 末尾执行。"""
    db = None
    try:
        env = os.getenv("TEST_ENV", "test")
        project = os.getenv("TEST_PROJECT")
        data_factory = DataFactory(env_name=env, project=project)
        env_config = data_factory.get_env_config()
        db_config = (env_config or {}).get("database", {}).get("erp_db")
        if not db_config:
            return

        db = DBManager(**db_config)

        # 清理采购订单
        db.delete(table="pur_po_head_tr", where="pur_remark like %s", params=["%AUTOTEST%"])
        db.delete(table="pur_po_item_tr", where="note like %s", params=["%AUTOTEST%"])

        # 清理采购申请
        db.delete(table="pur_pr_head_tr", where="pur_remark like %s", params=["%AUTOTEST%"])
        db.delete(table="pur_pr_item_tr", where="note like %s", params=["%AUTOTEST%"])

        # 清理采购计划
        db.delete(table="pur_po_schl_tr", where="pur_remark like %s", params=["%AUTOTEST%"])

        # 清理配置表
        db.delete(table="pur_po_item_type_cf", where="po_item_type like %s", params=["AUTOTEST_ITEM_%"])
        db.delete(table="pur_po_type_cf", where="po_type like %s", params=["AUTOTEST_PO_%"])
        db.delete(table="pur_pr_head_type_cf", where="pr_type_code like %s", params=["AUTOTEST_PR_%"])
        db.delete(table="pur_pr_item_type_cf", where="pr_item_type_code like %s", params=["AUTOTEST_PRI_%"])
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


register_cleanup("scm_pur_cleanup", _cleanup_scm_pur, order=230)

class ScmPurBaseTest(BaseTest):
    """采购模块的基础测试类，负责加载采购配置和提供API访问方法"""
    # 类型注解
    yaml_util: Any
    
    # 模块常量
    MODULE_NAME = "SCM_PUR"  # 采购模块名称，用于 query params

    DEFAULT_CACHE_MAPPINGS = {
        **BaseTest.DEFAULT_CACHE_MAPPINGS,
        "po_type_id": "pur_config.po_type_info.id",
        "po_item_type_id": "pur_config.po_item_type_info.id",
    }
    REQUIRED_CACHE_KEYS = (
        "curr_id",
        "cust_id",
        "pur_org_id",
        "po_type_id",
        "po_item_type_id",
    )
    
    # 登录两个门户，分别保存 session/user_info 并初始化 http 工具
    _PORTAL_TYPE_KEYS = {
        "admin": "TERP_PORTAL",
        "cust": "TERP_CUST_PC"
    }

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
        cls.load_api_configs()
        cls.load_cache_data()
        cls.bind_context()

    @classmethod
    def load_api_configs(cls):
        """加载采购模块 API 配置与门户上下文。"""
        cls.module_login_admin_with_cust_headers(
            admin_portal_key=cls._PORTAL_TYPE_KEYS["admin"],
            cust_portal_key=cls._PORTAL_TYPE_KEYS["cust"],
            tenant_key="terp",
        )

        # 初始化采购模块配置文件路径
        cls.pur_api_path = Path(project_root) / "config" / "api" / "scm_pur" / "pur_api_path.yaml"
        cls.pur_api_params_path = Path(project_root) / "config" / "api" / "scm_pur" / "pur_api_params.yaml"
        # 加载API路径配置和参数配置
        cls.load_module_api_configs(cls.pur_api_path, cls.pur_api_params_path)

    @classmethod
    def load_cache_data(cls):
        """加载采购模块依赖缓存。"""
        TestDataContext.register_source("pur_config", "pur_cache_data")
        # 加载主数据缓存（采购依赖物料、组织等主数据）
        cls.md_cache_data = cls.load_sql_cache(
            sql_config_path=project_root / "config" / "erp" / "md_init_sql.yaml",
            cache_key="md_init_cache",
            db_config_name="erp_db",
            cache_dir="testdata/cache",
        )

        # 加载采购配置数据
        cls.pur_cache_data = cls.load_sql_cache(
            sql_config_path=project_root / "config" / "erp" / "pur_init_sql.yaml",
            cache_key="pur_init_cache",
            db_config_name="erp_db",
            cache_dir="testdata/cache",
        )

    @classmethod
    def bind_context(cls):
        """绑定采购模块上下文。"""
        cls.bind_cache_data()
        cls.bind_module_user_context("SCM_PUR", strict=True)

        cls.logger.info(f"✅ md_cache_data 加载完成: {cls.md_cache_data is not None}")
        cls.logger.info(f"✅ pur_cache_data 加载完成: {cls.pur_cache_data is not None}")
        cls.logger.info(f"✅ init_data 加载完成: {cls.init_data is not None}")
        
        
    @classmethod
    def teardown_class(cls):
        """
        测试类清理
        采购模块清理已迁移至 cleanup_registry（session 末尾统一执行）。
        """
        try:
            cls.logger.info("SCM_PUR 清理已交由 cleanup_registry 统一执行")
        except Exception as e:
            cls.logger.error(f"❌ 采购模块测试数据清理失败: {str(e)}")
        finally:
            super().teardown_class()


if __name__ == "__main__":
    ScmPurBaseTest.setup_class()
    print(ScmPurBaseTest.nickname)
    # print(ScmPurBaseTest.cust_user_info)
