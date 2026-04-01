"""ERP 条件模块的测试初始化 — 声明式配置。"""

from testcases.comm.base_test import BaseTest


class ErpCondBaseTest(BaseTest):
    """ERP 条件模块基础测试类 — 声明式注册。"""

    MODULE_NAME = "ERP_COND"
    LOGIN_STRATEGY = "single"

    API_PATH_FILE = "config/api/erp_cond/cond_api_path.yaml"
    API_PARAMS_FILE = "config/api/erp_cond/cond_api_params.yaml"
    API_PARAMS_OPTIONAL = True

    SQL_CACHES = [
        {
            "path": "config/erp/cond_init_sql.yaml",
            "key": "cond_init_cache",
            "attr": "cond_cache_data",
            "optional": True,
        },
    ]
