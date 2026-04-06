"""ERP 账户模块的测试初始化 — 声明式配置。"""

from testcases.comm.base_test import BaseTest
from testcases.comm.utility_mixins import MockUtilMixin, QueryServiceMixin, YamlUtilMixin


class ErpAccBaseTest(QueryServiceMixin, YamlUtilMixin, MockUtilMixin, BaseTest):
    """ERP 账户模块基础测试类 — 声明式注册。"""

    MODULE_NAME = "ERP_ACC"
    LOGIN_STRATEGY = "single"

    API_PATH_FILE = "config/api/erp_acc/acc_api_path.yaml"
    API_PARAMS_FILE = "config/api/erp_acc/acc_api_params.yaml"
    API_PARAMS_OPTIONAL = True

    SQL_CACHES = [
        {
            "path": "config/erp/acc_init_sql.yaml",
            "key": "acc_init_cache",
            "attr": "acc_cache_data",
            "optional": True,
        },
    ]
