"""系统公共模块的测试初始化 — 声明式配置。"""

from testcases.comm.base_test import BaseTest
from testcases.comm.utility_mixins import MockUtilMixin


class SysCommonBaseTest(MockUtilMixin, BaseTest):
    """系统公共模块基础测试类 — 声明式注册（多门户，仅 admin）。"""

    MODULE_NAME = "SYS_COMMON"
    LOGIN_STRATEGY = "multi"

    _PORTAL_TYPE_KEYS = {
        "admin": "TERP_PORTAL",
    }

    API_PATH_FILE = "config/api/sys_common/common_api_path.yaml"
    API_PARAMS_FILE = "config/api/sys_common/common_api_params.yaml"

    def get_api_params(self, api_path, with_query_params=None):
        """自动附加 tmodule 查询参数。"""
        tmodule_part = f"tmodule={self.path_params['tmodule'].lower()}"

        if with_query_params:
            existing = str(with_query_params)
            if "tmodule=" in existing:
                query_str = existing
            else:
                query_str = f"{existing}&{tmodule_part}"
        else:
            query_str = tmodule_part

        return super().get_api_params(api_path, self.api_params, query_str)
