"""交货单模块的测试初始化 — 声明式配置。"""

from testcases.comm.base_test import BaseTest


class ScmDelBaseTest(BaseTest):
    """交货单模块基础测试类 — 声明式注册，无需覆盖 setup_class。"""

    MODULE_NAME = "SCM_DEL"
    LOGIN_STRATEGY = "admin_with_cust"

    _PORTAL_TYPE_KEYS = {
        "admin": "TERP_PORTAL",
        "cust": "TERP_CUST_PC",
    }

    API_PATH_FILE = "config/api/scm_del/del_api_path.yaml"
    API_PARAMS_FILE = "config/api/scm_del/del_api_params.yaml"

    SQL_CACHES = [
        {"path": "config/erp/md_init_sql.yaml", "key": "md_init_cache", "attr": "md_cache_data"},
        {"path": "config/erp/del_init_sql.yaml", "key": "del_init_cache", "attr": "del_cache_data"},
    ]

    DEFAULT_CACHE_MAPPINGS = {
        **BaseTest.DEFAULT_CACHE_MAPPINGS,
        "dn_type_id": "del_config.dn_type_info.id",
        "dn_item_type_id": "del_config.dn_item_type_info.id",
    }

    REQUIRED_CACHE_KEYS = ("curr_id", "cust_id")
