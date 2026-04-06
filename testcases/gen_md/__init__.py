"""通用基础模块的测试初始化 — 声明式配置 + 自定义日历绑定。"""

from testcases.comm.base_test import BaseTest
from testcases.comm.utility_mixins import MockUtilMixin, QueryServiceMixin, YamlUtilMixin


class GenMdBaseTest(QueryServiceMixin, YamlUtilMixin, MockUtilMixin, BaseTest):
    """通用基础模块基础测试类 — 声明式注册，覆盖 _bind_module_context 添加日历绑定。"""

    MODULE_NAME = "GEN_MD"
    LOGIN_STRATEGY = "single"
    STRICT_USER_CONTEXT = False

    API_PATH_FILE = "config/api/gen_md/md_api_path.yaml"
    API_PARAMS_FILE = "config/api/gen_md/md_api_params.yaml"

    SQL_CACHES = [
        {"path": "config/erp/md_init_sql.yaml", "key": "md_init_cache", "attr": "md_cache_data"},
        {"path": "config/erp/fin_init_sql.yaml", "key": "fin_init_cache", "attr": "fin_cache_data"},
    ]

    REQUIRED_CACHE_KEYS = ("curr_id", "cust_id", "com_org_id")

    # ─── 自定义上下文绑定 ───

    @classmethod
    def _bind_module_context(cls) -> None:
        """在标准绑定基础上，额外绑定财务日历头 ID。"""
        super()._bind_module_context()
        cls.calenderId = cls._calendar_head_id_from_fin_cache()

    @classmethod
    def _calendar_head_id_from_fin_cache(cls):
        """财务日历头 ID 来自 fin_init_sql（calender_info），不在 base_init_sql。"""
        fin = getattr(cls, "fin_cache_data", None) or {}
        ci = fin.get("calender_info") or {}
        rows = ci.get("calender_head_info") or []
        return rows[0]["id"] if rows else None
