"""
通用基础模块的测试初始化
提供配置加载等通用功能
"""
import sys
from pathlib import Path
import json
import requests

# 获取项目根目录
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from typing import Any,Dict
from testcases.comm.base_test import BaseTest,LoginService
from data_factory.base import DataFactory
from utils.cache_util import CacheUtil
from utils.request_util import HttpUtil
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a  # Allure reporting utility (a.json, a.text)

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
        
        # 优化单例创建：仅在 super().setup_class() 后执行
        # 确保环境就绪，不干扰 pytest 测试收集过程
        if cls._mock_instance is None:
            cls._mock_instance = MockData()
        
        # 设置类级 mock_util 以兼容现有代码 (cls.mock_util)
        # 现有测试类可继续使用 cls.mock_data 或迁移到 cls.mock_util
        cls.mock_util = cls._mock_instance
        
        # 初始化登录服务，避免重复创建
        cls.login_service = LoginService(cls.env_config)
        
        # 登录 admin 门户
        admin_result = cls.login_service.login(portal_key=cls._PORTAL_TYPE_KEYS["admin"])
        if admin_result.status != admin_result.status.SUCCESS:
            raise RuntimeError(f"admin 登录失败: {admin_result.error_message}")
        
        # 初始化 cust 门户的 headers
        cls.admin_headers = admin_result.portal_headers
        if cls.admin_headers:
            cls.cust_portal_headers = cls.admin_headers.copy()  
        # 从配置获取 cust 门户的 referer
        cust_portal_referer = cls.env_config.get("portal_config",{}).get('terp',{}).get("TERP_CUST_PC",{}).get("portal_referer")
        cls.cust_portal_headers["Referer"] = cust_portal_referer
        cls.logger.info(f"cust_portal_headers: {cls.cust_portal_headers}")
        # cls.logger.info(f"cust_portal_headers: {cls.cust_portal_headers}")
  
        # 初始化 http 实例，绑定 admin 门户的 url、session 和 headers
        cls.http = HttpUtil(
            url=admin_result.portal_url,
            session=admin_result.session,
            headers=admin_result.portal_headers
        )
     
        # 初始化配置文件路径
        cls.md_api_path = Path(project_root) / "testdata" / "gen_md" / "md_api_path.yaml"
        cls.md_api_params = Path(project_root) / "testdata" / "gen_md" / "md_api_params.yaml"
        
        # 加载API路径配置和参数配置
        cls.apis = cls.yaml_util.read_yaml(cls.md_api_path).get("apis", {})
        cls.api_params = cls.yaml_util.read_yaml(cls.md_api_params).get("api_params", {})
        
        # 初始化DataFactory（必须在init_sql_cache之前调用）
        DataFactory.__init__(env_name="test")
        
        # 加载缓存数据：主数据依赖的初始化SQL
        DataFactory.init_sql_cache(
            sql_config_path=str(project_root / "config" / "erp" / "md_init_sql.yaml"),  # 主数据依赖的初始化sql 存放路径
            db_config_name="erp_db",  # 数据库配置名称
            cache_key="md_init_cache",  # 缓存key
            cache_dir="testdata/cache"  # 缓存目录
        )
        cls.md_cache_data = CacheUtil.get('md_init_cache')
        
        # 设置路径参数和用户信息
        cls.path_params = {"tmodule":"GEN_MD"}
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

    def standard_api_call(self, api_key, set_dict=None, fields_to_filter=None, store_id_as=None, use_param_util=True):
        """
        标准化API调用模板 - 纯执行和报告工具，无断言逻辑
        :param api_key: API服务名称键
        :param set_dict: 要设置的参数字典
        :param fields_to_filter: 需要过滤的字段列表
        :param store_id_as: ID存储属性名（用于自动保存self.xxx_id）
        :param use_param_util: 是否使用ParamUtil过滤/设置（默认True）；False时直接使用set_dict作为params
        :return: (response, extracted_id)
        """
        try:
            # 1. 获取API路径和基础参数
            api_path = self.get_api_path(api_key)
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理 - 分支逻辑
            if use_param_util:
                # 标准流程：使用ParamUtil过滤和设置
                if fields_to_filter is None:
                    fields_to_filter = []
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, fields_to_filter, ["params", "request"]
                )
                if set_dict:
                    ParamUtil.set_request_params(filtered_params, set_dict)
            else:
                # 特殊流程：直接使用set_dict作为params内容，无过滤/设置
                if set_dict is None:
                    set_dict = {}
                filtered_params = {"params": set_dict}
            
            # 3. 发送请求
            self.logger.info(f"接口请求的地址>>>{url}")
            self.logger.info(f"接口请求的方法>>>POST")
            self.logger.info(f"接口请求的json参数>>>{json.dumps(filtered_params, ensure_ascii=False, indent=2)}")
            
            response = self.http.post(url, json=filtered_params)
            
            # 4. Allure报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
            # 5. ID提取和存储
            extracted_id = response.get("data", {}).get("data", {})
            if store_id_as:
                setattr(self, f"{store_id_as}_id", extracted_id)
            
            return response, extracted_id
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"standard_api_call HTTP请求失败 [{api_key}]: {str(e)}")
            a.text(f"HTTP请求失败: {str(e)}", "请求失败")
            raise
        except Exception as e:
            self.logger.error(f"standard_api_call 执行失败 [{api_key}]: {str(e)}")
            a.text(f"执行失败: {str(e)}", "执行异常")
            raise


if __name__ == "__main__":
    GenMdBaseTest.setup_class()
    print(GenMdBaseTest.nickname)
    # print(GenMdBaseTest.cust_user_info)