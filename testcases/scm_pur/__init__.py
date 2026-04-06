"""采购模块的测试初始化 — 声明式配置。"""

import os

from erp_data_factory.compat.base import DataFactory
from testcases.comm.base_test import BaseTest
from testcases.comm.cleanup_registry import register_cleanup
from testcases.comm.utility_mixins import MockUtilMixin
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

        db.delete(table="pur_po_head_tr", where="pur_remark like %s", params=["%AUTOTEST%"])
        db.delete(table="pur_po_item_tr", where="note like %s", params=["%AUTOTEST%"])
        db.delete(table="pur_pr_item_tr", where="note like %s", params=["%AUTOTEST%"])
        db.delete(table="pur_po_item_type_cf", where="po_item_type like %s", params=["AUTOTEST_ITEM_%"])
        db.delete(table="pur_po_type_cf", where="po_type like %s", params=["AUTOTEST_PO_%"])
        db.delete(table="pur_pr_head_type_cf", where="pr_type_code like %s", params=["AUTOTEST_PR_%"])
        db.delete(table="pur_pr_item_type_cf", where="pr_item_type_code like %s", params=["AUTOTEST_PRI_%"])
        try:
            db.delete(table="pur_po_schl_tr", where="po_head_id IN "
                      "(SELECT id FROM pur_po_head_tr WHERE pur_remark LIKE %s)", params=["%AUTOTEST%"])
        except Exception:
            pass
        try:
            db.delete(table="pur_pr_head_tr", where="remark like %s", params=["%AUTOTEST%"])
        except Exception:
            pass
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


register_cleanup("scm_pur_cleanup", _cleanup_scm_pur, order=230)


class ScmPurBaseTest(MockUtilMixin, BaseTest):
    """采购模块基础测试类 — 声明式注册。"""

    MODULE_NAME = "SCM_PUR"
    LOGIN_STRATEGY = "admin_with_cust"

    _PORTAL_TYPE_KEYS = {
        "admin": "TERP_PORTAL",
        "cust": "TERP_CUST_PC",
    }

    API_PATH_FILE = "config/api/scm_pur/pur_api_path.yaml"
    API_PARAMS_FILE = "config/api/scm_pur/pur_api_params.yaml"

    SQL_CACHES = [
        {"path": "config/erp/md_init_sql.yaml", "key": "md_init_cache", "attr": "md_cache_data"},
        {"path": "config/erp/pur_init_sql.yaml", "key": "pur_init_cache", "attr": "pur_cache_data"},
    ]

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

    @classmethod
    def teardown_class(cls):
        """采购模块清理已迁移至 cleanup_registry（session 末尾统一执行）。"""
        try:
            cls.logger.info("SCM_PUR 清理已交由 cleanup_registry 统一执行")
        except Exception as e:
            cls.logger.error(f"❌ 采购模块测试数据清理失败: {str(e)}")
        finally:
            super().teardown_class()
