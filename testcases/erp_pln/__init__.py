"""ERP 计划模块的测试初始化 — 声明式配置。"""

from testcases.comm.base_test import BaseTest
from testcases.comm.utility_mixins import MockUtilMixin, QueryServiceMixin, YamlUtilMixin


class ErpPlnBaseTest(QueryServiceMixin, YamlUtilMixin, MockUtilMixin, BaseTest):
    """ERP 计划模块基础测试类。"""

    MODULE_NAME = "ERP_PLN"
    LOGIN_STRATEGY = "single"

    API_PATH_FILE = "config/api/erp_pln/pln_api_path.yaml"
    API_PARAMS_FILE = "config/api/erp_pln/pln_api_params.yaml"
    API_PARAMS_OPTIONAL = False
