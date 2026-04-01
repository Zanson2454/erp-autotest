"""基础财务模块的测试初始化 — 声明式配置。"""

from testcases.comm.base_test import BaseTest


class FiBaseTest(BaseTest):
    """基础财务模块基础测试类 — 声明式注册（多门户）。"""

    MODULE_NAME = "ERP_FI"
    LOGIN_STRATEGY = "multi"

    _PORTAL_TYPE_KEYS = {
        "admin": "TERP_PORTAL",
        "cust": "TERP_CUST_PC",
    }

    API_PATH_FILE = "config/api/erp_fi/fi_api_path.yaml"
    API_PARAMS_FILE = "config/api/erp_fi/fi_api_params.yaml"
    API_PARAMS_OPTIONAL = True

    SQL_CACHES = [
        {
            "path": "config/erp/fi_init_sql.yaml",
            "key": "fi_init_cache",
            "attr": "fi_cache_data",
            "optional": True,
        },
    ]
