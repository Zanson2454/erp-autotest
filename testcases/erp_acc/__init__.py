"""
ERP账户模块的测试初始化
提供配置加载等通用功能
"""
import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from typing import Any, Dict
from testcases.comm.base_test import BaseTest

class ErpAccBaseTest(BaseTest):
    """ERP账户模块的基础测试类，负责加载通用配置和提供API访问方法"""
    
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
        """加载 erp_acc 模块 API 配置与门户上下文。"""
        cls.module_login_single_portal(
            portal_key=cls._PORTAL_TYPE_KEYS["admin"],
            tenant_key="terp"
        )

        # 初始化配置文件路径 - 针对erp_acc模块
        cls.acc_api_path = Path(project_root) / "config" / "api" / "erp_acc" / "acc_api_path.yaml"
        cls.acc_api_params = Path(project_root) / "config" / "api" / "erp_acc" / "acc_api_params.yaml"

        cls.load_module_api_configs(
            cls.acc_api_path,
            cls.acc_api_params,
            api_params_optional=True
        )

    @classmethod
    def load_cache_data(cls):
        """加载 erp_acc 模块依赖缓存。"""
        # 加载缓存数据：账户模块依赖的初始化SQL (如果存在)
        # 注意：如果没有专门的acc_init_sql.yaml，可以复用md_init_sql或创建新的
        sql_config_path = str(project_root / "config" / "erp" / "acc_init_sql.yaml")
        if Path(sql_config_path).exists():
            cls.acc_cache_data = cls.load_sql_cache(
                sql_config_path=sql_config_path,
                cache_key="acc_init_cache",
                db_config_name="erp_db",
                cache_dir="testdata/cache",
            )
        else:
            # 复用主数据缓存
            cls.acc_cache_data = cls.md_cache_data if hasattr(cls, "md_cache_data") else {}

    @classmethod
    def bind_context(cls):
        """绑定 erp_acc 模块上下文。"""
        cls.bind_mock_util_singleton()

        # 设置路径参数和用户信息 - 针对ERP_ACC模块
        cls.bind_module_user_context("ERP_ACC", strict=True)
    
if __name__ == "__main__":
    ErpAccBaseTest.setup_class()
    print(ErpAccBaseTest.nickname)
    # print(ErpAccBaseTest.cust_user_info)
