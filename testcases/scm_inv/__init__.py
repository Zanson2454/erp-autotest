"""SCM 库存模块的测试初始化 — 声明式配置。"""

from testcases.comm.base_test import BaseTest


class ScmInvBaseTest(BaseTest):
    """SCM 库存模块基础测试类 — 声明式注册。"""

    MODULE_NAME = "SCM_INV"
    LOGIN_STRATEGY = "admin_with_cust"

    _PORTAL_TYPE_KEYS = {
        "admin": "TERP_PORTAL",
        "cust": "TERP_CUST_PC",
    }

    API_PATH_FILE = "config/api/scm_inv/inv_api_path.yaml"
    API_PARAMS_FILE = "config/api/scm_inv/inv_api_params.yaml"

    SQL_CACHES = [
        {"path": "config/erp/md_init_sql.yaml", "key": "inv_init_cache", "attr": "inv_cache_data"},
    ]

    @classmethod
    def teardown_class(cls):
        """SCM_INV 清理已迁移至 cleanup_registry（session 末尾统一执行）。"""
        try:
            cls.logger.info("SCM_INV 清理已交由 cleanup_registry 统一执行")
        except Exception as e:
            cls.logger.error(f"❌ 库存模块 teardown 异常: {str(e)}")
        finally:
            super().teardown_class()
