"""Trantor 框架模块的测试初始化 — 声明式配置。"""

from testcases.comm.base_test import BaseTest
from testcases.comm.utility_mixins import MockUtilMixin, QueryServiceMixin, YamlUtilMixin


class TrantorBaseTest(QueryServiceMixin, YamlUtilMixin, MockUtilMixin, BaseTest):
    """Trantor 框架模块基础测试类 — 声明式注册。"""

    API_PATH_FILE = "config/api/trantor/api_api_path.yaml"
    API_PARAMS_FILE = "config/api/trantor/api_api_params.yaml"
