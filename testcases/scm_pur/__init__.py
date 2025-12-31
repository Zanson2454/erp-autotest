"""
采购模块的测试初始化
提供配置加载等通用功能
"""

import sys
from pathlib import Path
from typing import Any

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from testcases.comm.base_test import BaseTest, LoginService
from data_factory.base import DataFactory
from utils.cache_util import CacheUtil
from utils.request_util import HttpUtil

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

        cls.login_service = LoginService(cls.env_config)
        # 登录 admin
        admin_result = cls.login_service.login(portal_key=cls._PORTAL_TYPE_KEYS["admin"])
        if admin_result.status != admin_result.status.SUCCESS:
            raise RuntimeError(f"admin 登录失败: {admin_result.error_message}")
        
        # 初始化 cust 的 headers
        cls.admin_headers = admin_result.portal_headers
        if cls.admin_headers:
            cls.cust_portal_headers = cls.admin_headers.copy()
        cust_portal_referer = cls.env_config.get("portal_config", {}).get('terp', {}).get("TERP_CUST_PC", {}).get("portal_referer")
        cls.cust_portal_headers["Referer"] = cust_portal_referer
        cls.logger.info(f"cust_portal_headers: {cls.cust_portal_headers}")
        
        # 使用 admin_result 初始化 http 实例
        cls.http = HttpUtil(
            url=admin_result.portal_url,    # admin 的 URL
            session=admin_result.session,   # admin 的 session（包含 cookie）
            headers=admin_result.portal_headers # admin 的 headers
        )

        # 初始化采购模块配置文件路径
        cls.pur_api_path = Path(project_root) / "testdata" / "scm_pur" / "pur_api_path.yaml"
        cls.pur_api_params_path = Path(project_root) / "testdata" / "scm_pur" / "pur_api_params.yaml"
        # 加载API路径配置和参数配置
        cls.apis = cls.yaml_util.read_yaml(cls.pur_api_path).get("apis", {})
        cls.api_params = cls.yaml_util.read_yaml(cls.pur_api_params_path).get("api_params", {})
        
        # 初始化DataFactory（必须在init_sql_cache之前调用）
        DataFactory.__init__(env_name="test")
        
        # 加载主数据缓存（采购依赖物料、组织等主数据）
        DataFactory.init_sql_cache(
            sql_config_path=str(project_root / "config" / "erp" / "md_init_sql.yaml"),
            db_config_name="erp_db",
            cache_key="md_init_cache",
            cache_dir="testdata/cache"
        )
        cls.md_cache_data = CacheUtil.get('md_init_cache')
        
        # 加载采购配置数据
        DataFactory.init_sql_cache(
            sql_config_path=str(project_root / "config" / "erp" / "pur_init_sql.yaml"),
            db_config_name="erp_db",
            cache_key="pur_init_cache",
            cache_dir="testdata/cache"
        )
        cls.pur_cache_data = CacheUtil.get('pur_init_cache')
        cls.path_params = {"tmodule": "SCM_PUR"}
        cls.nickname = cls.init_data["user_info"]['user_info']["nickname"]
        cls.user_id = cls.init_data["user_info"]['user_info']["id"]
        
        cls.logger.info(f"✅ md_cache_data 加载完成: {cls.md_cache_data is not None}")
        cls.logger.info(f"✅ pur_cache_data 加载完成: {cls.pur_cache_data is not None}")
        cls.logger.info(f"✅ init_data 加载完成: {cls.init_data is not None}")
        
        
    def get_api_path(self, api_key):
        """
        获取API路径
        """
        return super().get_api_path(api_key, self.apis)
    
    def get_api_params(self, api_path, with_query_params=None):
        """
        获取API请求参数和完整URL
        """
        return super().get_api_params(api_path, self.api_params, with_query_params)
    
    def set_request_param(self, params, key, value):
        """
        设置请求参数中的值，简化嵌套访问
        
        参数:
            params: 请求参数字典
            key: 参数键名
            value: 参数值
        
        返回:
            更新后的参数字典
        """
        if 'params' not in params:
            params['params'] = {}
        if 'request' not in params['params']:
            params['params']['request'] = {}
            
        params['params']['request'][key] = value
        return params
    
    def set_request_params(self, params, param_dict):
        """
        批量设置请求参数，简化嵌套访问
        
        参数:
            params: 请求参数字典
            param_dict: 要设置的参数字典 {key: value, ...}
        
        返回:
            更新后的参数字典
        """
        if 'params' not in params:
            params['params'] = {}
        if 'request' not in params['params']:
            params['params']['request'] = {}
            
        for key, value in param_dict.items():
            params['params']['request'][key] = value
        return params
    
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
