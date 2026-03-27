"""
采购模块的测试初始化
提供配置加载等通用功能
"""

import sys
from pathlib import Path
from typing import Any

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from testcases.comm.base_test import BaseTest
from data_factory.base import DataFactory

class ScmPurBaseTest(BaseTest):
    """采购模块的基础测试类，负责加载采购配置和提供API访问方法"""
    # 类型注解
    yaml_util: Any
    
    # 模块常量
    MODULE_NAME = "SCM_PUR"  # 采购模块名称，用于 query params
    
    # 登录两个门户，分别保存 session/user_info 并初始化 http 工具
    _PORTAL_TYPE_KEYS = {
        "admin": "TERP_PORTAL",
        "cust": "TERP_CUST_PC"
    }

    @classmethod
    def setup_class(cls):
        """
        测试类初始化 - 加载采购配置
        1. 调用父类初始化方法 (包括登录、数据库连接等)
        2. 多门户多用户登录，获取 session
        3. 初始化采购配置文件路径
        4. 加载API配置
        5. 初始化 http 工具，自动带上门户请求头
        """
        super().setup_class()
        cls.load_api_configs()
        cls.load_cache_data()
        cls.bind_context()

    @classmethod
    def load_api_configs(cls):
        """加载采购模块 API 配置与门户上下文。"""
        cls.module_login_admin_with_cust_headers(
            admin_portal_key=cls._PORTAL_TYPE_KEYS["admin"],
            cust_portal_key=cls._PORTAL_TYPE_KEYS["cust"],
            tenant_key="terp",
        )

        # 初始化采购模块配置文件路径
        cls.pur_api_path = Path(project_root) / "config" / "api" / "scm_pur" / "pur_api_path.yaml"
        cls.pur_api_params_path = Path(project_root) / "config" / "api" / "scm_pur" / "pur_api_params.yaml"
        # 加载API路径配置和参数配置
        cls.load_module_api_configs(cls.pur_api_path, cls.pur_api_params_path)

    @classmethod
    def load_cache_data(cls):
        """加载采购模块依赖缓存。"""
        # 初始化DataFactory（必须在init_sql_cache之前调用）
        DataFactory.__init__(env_name="test")

        # 加载主数据缓存（采购依赖物料、组织等主数据）
        cls.md_cache_data = cls.load_sql_cache(
            sql_config_path=project_root / "config" / "erp" / "md_init_sql.yaml",
            cache_key="md_init_cache",
            db_config_name="erp_db",
            cache_dir="testdata/cache",
        )

        # 加载采购配置数据
        cls.pur_cache_data = cls.load_sql_cache(
            sql_config_path=project_root / "config" / "erp" / "pur_init_sql.yaml",
            cache_key="pur_init_cache",
            db_config_name="erp_db",
            cache_dir="testdata/cache",
        )

    @classmethod
    def bind_context(cls):
        """绑定采购模块上下文。"""
        cls.bind_module_user_context("SCM_PUR", strict=True)

        cls.logger.info(f"✅ md_cache_data 加载完成: {cls.md_cache_data is not None}")
        cls.logger.info(f"✅ pur_cache_data 加载完成: {cls.pur_cache_data is not None}")
        cls.logger.info(f"✅ init_data 加载完成: {cls.init_data is not None}")
        
        
    @classmethod
    def teardown_class(cls):
        """
        测试类清理 - 删除采购模块的测试数据
        在所有 scm_pur 模块的测试完成后执行
        """
        try:
            # 使用从 BaseTest 继承的 cls.db 进行清理
            # 清理采购订单
            cls.db.delete(
                table="pur_po_head_tr",
                where="pur_remark like %s",
                params=["%AUTOTEST%"]
            )
            cls.db.delete(
                table="pur_po_item_tr",
                where="note like %s",
                params=["%AUTOTEST%"]
            )
            
            # 清理采购申请
            cls.db.delete(
                table="pur_pr_head_tr",
                where="pur_remark like %s",
                params=["%AUTOTEST%"]
            )
            cls.db.delete(
                table="pur_pr_item_tr",
                where="note like %s",
                params=["%AUTOTEST%"]
            )
            
            # 清理采购计划
            cls.db.delete(
                table="pur_po_schl_tr",
                where="pur_remark like %s",
                params=["%AUTOTEST%"]
            )
            
            # 清理配置表
            cls.db.delete(
                table="pur_po_item_type_cf",
                where="po_item_type like %s",
                params=["AUTOTEST_ITEM_%"]
            )
            cls.db.delete(
                table="pur_po_type_cf",
                where="po_type like %s",
                params=["AUTOTEST_PO_%"]
            )
            cls.db.delete(
                table="pur_pr_head_type_cf",
                where="pr_type_code like %s",
                params=["AUTOTEST_PR_%"]
            )
            cls.db.delete(
                table="pur_pr_item_type_cf",
                where="pr_item_type_code like %s",
                params=["AUTOTEST_PRI_%"]
            )
            
            cls.logger.info("✅ 采购模块测试数据清理完成")
            
        except Exception as e:
            cls.logger.error(f"❌ 采购模块测试数据清理失败: {str(e)}")


if __name__ == "__main__":
    ScmPurBaseTest.setup_class()
    print(ScmPurBaseTest.nickname)
    # print(ScmPurBaseTest.cust_user_info)
