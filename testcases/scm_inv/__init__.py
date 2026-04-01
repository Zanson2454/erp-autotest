"""
SCM库存模块的测试初始化
提供库存相关配置加载等通用功能
"""
import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from typing import Any,Dict
from testcases.comm.base_test import BaseTest

class ScmInvBaseTest(BaseTest):
    """SCM库存模块的基础测试类，负责加载库存相关配置和提供API访问方法"""
    
    # 类型提示：继承的动态属性
    yaml_util: Any
    
    
    # 登录两个门户，分别保存 session/user_info 并初始化 http 工具
    _PORTAL_TYPE_KEYS: Dict[str, str] = {
    "admin": "TERP_PORTAL",
    "cust": "TERP_CUST_PC"
    }   
    
    
    @classmethod
    def setup_class(cls):
        """
        测试类初始化 - 加载库存模块配置
        1. 调用父类初始化方法 (包括登录、数据库连接等)
        2. 多门户多用户登录，获取 session
        3. 初始化库存模块配置文件路径
        4. 加载库存API路径和参数配置
        5. 初始化 http 工具，自动带上门户请求头
        """
        super().setup_class()
        cls.load_api_configs()
        cls.load_cache_data()
        cls.bind_context()

    @classmethod
    def load_api_configs(cls):
        """加载库存模块 API 配置与门户上下文。"""
        cls.module_login_admin_with_cust_headers(
            admin_portal_key=cls._PORTAL_TYPE_KEYS["admin"],
            cust_portal_key=cls._PORTAL_TYPE_KEYS["cust"],
            tenant_key="terp",
        )

        # 初始化库存模块配置文件路径
        cls.inv_api_path = Path(project_root) / "config" / "api" / "scm_inv" / "inv_api_path.yaml"
        cls.inv_api_params = Path(project_root) / "config" / "api" / "scm_inv" / "inv_api_params.yaml"
        cls.load_module_api_configs(cls.inv_api_path, cls.inv_api_params)

    @classmethod
    def load_cache_data(cls):
        """加载库存模块依赖缓存。"""
        # 加载缓存数据（库存模块依赖主数据）
        cls.inv_cache_data = cls.load_sql_cache(
            sql_config_path=project_root / "config" / "erp" / "md_init_sql.yaml",
            cache_key="inv_init_cache",
            db_config_name="erp_db",
            cache_dir="testdata/cache",
        )

    @classmethod
    def bind_context(cls):
        """绑定库存模块上下文。"""
        cls.bind_module_user_context("SCM_INV", strict=True)

    
    @classmethod
    def teardown_class(cls):
        """SCM_INV 清理已迁移至 scm_inv/conftest.py → cleanup_registry（session 末尾统一执行）。"""
        try:
            cls.logger.info("SCM_INV 清理已交由 cleanup_registry 统一执行")
        except Exception as e:
            cls.logger.error(f"❌ 库存模块 teardown 异常: {str(e)}")
        finally:
            super().teardown_class()


if __name__ == "__main__":
    ScmInvBaseTest.setup_class()
    print(ScmInvBaseTest.nickname)
    # print(ScmInvBaseTest.cust_user_info)
