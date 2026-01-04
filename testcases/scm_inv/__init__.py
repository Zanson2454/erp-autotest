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
from testcases.comm.base_test import BaseTest,LoginService
from data_factory.base import DataFactory
from utils.cache_util import CacheUtil
from utils.request_util import HttpUtil

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

        cls.login_service = LoginService(cls.env_config)  # 初始化一次登录服务，避免重复创建
        # 登录 admin
        admin_result = cls.login_service.login(portal_key=cls._PORTAL_TYPE_KEYS["admin"])
        if admin_result.status != admin_result.status.SUCCESS:
            raise RuntimeError(f"admin 登录失败: {admin_result.error_message}")
        
        # 初始化 cust 的 headers
        cls.admin_headers = admin_result.portal_headers
        if cls.admin_headers:
            cls.cust_portal_headers = cls.admin_headers.copy()  
        cust_portal_referer = cls.env_config.get("portal_config",{}).get('terp',{}).get("TERP_CUST_PC",{}).get("portal_referer")
        cls.cust_portal_headers["Referer"] = cust_portal_referer
        cls.logger.info(f"cust_portal_headers: {cls.cust_portal_headers}")
  
        # 初始化 http 实例
        cls.http = HttpUtil(
            url=admin_result.portal_url,
            session=admin_result.session,
            headers=admin_result.portal_headers
        )
     

        # 初始化库存模块配置文件路径
        cls.inv_api_path = Path(project_root) / "config" / "api" / "scm_inv" / "inv_api_path.yaml"
        cls.inv_api_params = Path(project_root) / "config" / "api" / "scm_inv" / "inv_api_params.yaml"
        # 加载库存API路径配置和参数配置
        cls.apis = cls.yaml_util.read_yaml(cls.inv_api_path).get("apis", {})
        cls.api_params = cls.yaml_util.read_yaml(cls.inv_api_params).get("api_params", {})
        # 初始化DataFactory（必须在init_sql_cache之前调用）
        DataFactory.__init__(env_name="test")
        # 加载缓存数据（库存模块依赖主数据）
        DataFactory.init_sql_cache(
            sql_config_path=str(project_root / "config" / "erp" / "md_init_sql.yaml"), # 主数据依赖的初始化sql存放路径
            db_config_name="erp_db", # 数据库配置名称
            cache_key="inv_init_cache", # 缓存key
            cache_dir="testdata/cache" # 缓存目录
        )
        cls.inv_cache_data = CacheUtil.get('inv_init_cache')
        cls.path_params = {"tmodule":"SCM_INV"}
        cls.nickname = cls.init_data["user_info"]['user_info']["nickname"]
        cls.user_id = cls.init_data["user_info"]['user_info']["id"]

    
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
        测试类清理 - 删除库存模块的测试数据
        在所有 scm_inv 模块的测试完成后执行
        """
        try:
            # 清理库存类型配置相关表
            # inv_inv_type_cf 需要清理关联的翻译表
            try:
                cls.db.execute("""
                    DELETE FROM inv_inv_type_trans_cf 
                    WHERE created_by IN (
                        SELECT DISTINCT created_by FROM inv_inv_type_cf WHERE code LIKE %s
                    )
                """, ["AT_%"])
            except Exception as e:
                cls.logger.warning(f"清理 inv_inv_type_trans_cf 失败: {str(e)}")
            
            try:
                cls.db.delete(
                    table="inv_inv_type_cf",
                    where="code like %s",
                    params=["AT_%"]
                )
            except Exception as e:
                cls.logger.warning(f"清理 inv_inv_type_cf 失败: {str(e)}")
            
            # 清理移动类型配置
            try:
                cls.db.delete(
                    table="inv_mvm_type_cf",
                    where="remark = %s",
                    params=["AUTOMATION_TEST"]
                )
            except Exception as e:
                cls.logger.warning(f"清理 inv_mvm_type_cf 失败: {str(e)}")
            
            # 清理特殊库存类型配置
            try:
                cls.db.delete(
                    table="inv_spc_stk_type_cf",
                    where="code like %s",
                    params=["AT_%"]
                )
            except Exception as e:
                cls.logger.warning(f"清理 inv_spc_stk_type_cf 失败: {str(e)}")
            
            # 清理其他移动配置表
            try:
                cls.db.delete(
                    table="inv_fb_type_cf",
                    where="code like %s",
                    params=["AT_%"]
                )
            except Exception as e:
                cls.logger.warning(f"清理 inv_fb_type_cf 失败: {str(e)}")
            
            try:
                cls.db.delete(
                    table="inv_mvm_ext_type_cf",
                    where="code like %s",
                    params=["AT_%"]
                )
            except Exception as e:
                cls.logger.warning(f"清理 inv_mvm_ext_type_cf 失败: {str(e)}")
            
            try:
                cls.db.delete(
                    table="inv_bs_type_cf",
                    where="name like %s",
                    params=["%AT%"]
                )
            except Exception as e:
                cls.logger.warning(f"清理 inv_bs_type_cf 失败: {str(e)}")
            
            # 清理ATP相关表
            try:
                cls.db.delete(
                    table="inv_atp_rule_cf",
                    where="code like %s",
                    params=["AUTOTEST_%"]
                )
            except Exception as e:
                cls.logger.warning(f"清理 inv_atp_rule_cf 失败: {str(e)}")
            
            try:
                cls.db.delete(
                    table="inv_atp_group_md",
                    where="code like %s",
                    params=["AUTOTEST_ATP_%"]
                )
            except Exception as e:
                cls.logger.warning(f"清理 inv_atp_group_md 失败: {str(e)}")
            
            # 清理移动单据相关表（可选，如果表存在）
            try:
                cls.db.delete(
                    table="inv_move_doc_head",
                    where="doc_code like %s",
                    params=["AUTOTEST_%"]
                )
            except Exception as e:
                cls.logger.warning(f"清理 inv_move_doc_head 失败: {str(e)}")
            
            try:
                cls.db.delete(
                    table="inv_move_doc_item",
                    where="note like %s",
                    params=["%AUTOTEST%"]
                )
            except Exception as e:
                cls.logger.warning(f"清理 inv_move_doc_item 失败: {str(e)}")
            
            cls.logger.info("✅ 库存模块测试数据清理完成")
            
        except Exception as e:
            cls.logger.error(f"❌ 库存模块测试数据清理出现严重错误: {str(e)}")


if __name__ == "__main__":
    ScmInvBaseTest.setup_class()
    print(ScmInvBaseTest.nickname)
    # print(ScmInvBaseTest.cust_user_info)