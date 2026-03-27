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
from data_factory.base import DataFactory

class GenMdBaseTest(BaseTest):
    """通用基础模块的基础测试类，负责加载通用配置和提供API访问方法"""
    
    # 类型提示：继承的动态属性
    yaml_util: Any
    
    
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
        # 初始化DataFactory（必须在init_sql_cache之前调用）
        # 从环境变量获取 env 和 project，支持多项目模式
        import os
        env_name = os.getenv("TEST_ENV", "test")
        project = os.getenv("TEST_PROJECT")
        DataFactory.__init__(env_name=env_name, project=project)

        # 加载缓存数据：主数据依赖的初始化SQL
        # 保持向后兼容，所有项目共享缓存；切换项目时自动清除缓存
        cls.md_cache_data = cls.load_sql_cache(
            sql_config_path=project_root / "config" / "erp" / "md_init_sql.yaml",
            cache_key="md_init_cache",
            db_config_name="erp_db",
            cache_dir="testdata/cache",
        )

    @classmethod
    def bind_context(cls):
        """绑定 gen_md 模块上下文。"""
        cls.bind_mock_util_singleton()

        # 设置路径参数和用户信息（安全访问）
        cls.bind_module_user_context("GEN_MD", strict=False)
    
if __name__ == "__main__":
    GenMdBaseTest.setup_class()
    print(GenMdBaseTest.nickname)
    # print(GenMdBaseTest.cust_user_info)
