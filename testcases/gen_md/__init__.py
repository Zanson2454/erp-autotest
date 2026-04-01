"""
通用基础模块的测试初始化
提供配置加载等通用功能
"""
import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from typing import Any, Dict
from testcases.comm.base_test import BaseTest
from testcases.comm.test_data_context import TestDataContext

class GenMdBaseTest(BaseTest):
    """通用基础模块的基础测试类，负责加载通用配置和提供API访问方法"""
    
    # 类型提示：继承的动态属性
    yaml_util: Any

    REQUIRED_CACHE_KEYS = ("curr_id", "cust_id", "com_org_id")
    
    
    # 登录两个门户，分别保存 session/user_info 并初始化 http 工具
    _PORTAL_TYPE_KEYS: Dict[str, str] = {
    "admin": "TERP_PORTAL",
    "cust": "TERP_CUST_PC"
    }
    
    # 添加单例实例持有者，作为类变量
    _mock_instance = None
    
    @classmethod
    def setup_class(cls):
        """
        测试类初始化 - 加载通用配置
        1. 调用父类初始化方法 (包括登录、数据库连接等)
        2. 多门户多用户登录，获取 session
        3. 初始化通用配置文件路径
        4. 加载API路径和参数配置
        5. 初始化 http 工具，自动带上门户请求头
        """
        super().setup_class()
        cls.load_api_configs()
        cls.load_cache_data()
        cls.bind_context()

    @classmethod
    def load_api_configs(cls):
        """加载 gen_md 模块 API 配置与门户上下文。"""
        admin_result = cls.module_login_single_portal(
            portal_key=cls._PORTAL_TYPE_KEYS["admin"],
            tenant_key="terp"
        )
        cls.admin_headers = admin_result.portal_headers

        # 初始化配置文件路径
        cls.md_api_path = Path(project_root) / "config" / "api" / "gen_md" / "md_api_path.yaml"
        cls.md_api_params = Path(project_root) / "config" / "api" / "gen_md" / "md_api_params.yaml"

        cls.load_module_api_configs(cls.md_api_path, cls.md_api_params)

    @classmethod
    def load_cache_data(cls):
        """加载 gen_md 模块依赖缓存。"""
        TestDataContext.register_source("partner_info", "md_cache_data")
        TestDataContext.register_source("org_info", "md_cache_data")
        TestDataContext.register_source("mat_info", "md_cache_data")
        for _key in (
            "calender_info",
            "sett_doc_info",
            "sett_item_info",
            "sb_type_info",
            "ar_type_info",
            "ap_type_info",
        ):
            TestDataContext.register_source(_key, "fin_cache_data")
        # BaseTest.setup_class 已通过 DataFactory 拉取 init_data；此处加载 md + 财务日历（组织保存等用 def12 日历头）
        cls.md_cache_data = cls.load_sql_cache(
            sql_config_path=project_root / "config" / "erp" / "md_init_sql.yaml",
            cache_key="md_init_cache",
            db_config_name="erp_db",
            cache_dir="testdata/cache",
        )
        cls.fin_cache_data = cls.load_sql_cache(
            sql_config_path=project_root / "config" / "erp" / "fin_init_sql.yaml",
            cache_key="fin_init_cache",
            db_config_name="erp_db",
            cache_dir="testdata/cache",
        )

    @classmethod
    def _calendar_head_id_from_fin_cache(cls):
        """财务日历头 ID 来自 fin_init_sql（calender_info），不在 base_init_sql。"""
        fin = getattr(cls, "fin_cache_data", None) or {}
        ci = fin.get("calender_info") or {}
        rows = ci.get("calender_head_info") or []
        return rows[0]["id"] if rows else None

    @classmethod
    def bind_context(cls):
        """绑定 gen_md 模块上下文。"""
        cls.bind_cache_data()
        cls.bind_mock_util_singleton()
        cls.calenderId = cls._calendar_head_id_from_fin_cache()

        # 设置路径参数和用户信息（安全访问）
        cls.bind_module_user_context("GEN_MD", strict=False)
    
if __name__ == "__main__":
    GenMdBaseTest.setup_class()
    print(GenMdBaseTest.nickname)
    # print(GenMdBaseTest.cust_user_info)
