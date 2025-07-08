"""
通用基础模块的测试初始化
提供配置加载等通用功能
"""
import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from typing import Any
from testcases.comm.base_test import BaseTest
from data_factory.base import DataFactory
from utils.cache_util import CacheUtil

class GenMdBaseTest(BaseTest):
    """通用基础模块的基础测试类，负责加载通用配置和提供API访问方法"""
    
    # 类型提示：继承的动态属性
    yaml_util: Any
    
    @classmethod
    def setup_class(cls):
        """
        测试类初始化 - 加载通用配置
        完成以下工作:
        1. 调用父类初始化方法 (包括登录、数据库连接等)
        2. 初始化通用配置文件路径
        3. 加载API路径和参数配置
        """
        # 调用父类初始化方法 (完成登录、获取用户信息、建立数据库连接等)
        super().setup_class()
        
        # 初始化配置文件路径
        cls.md_api_path = Path(project_root) / "testdata" / "gen_md" / "md_api_path.yaml"
        cls.md_api_params = Path(project_root) / "testdata" / "gen_md" / "md_api_params.yaml"
        
        # 加载API路径配置和参数配置
        cls.apis = cls.yaml_util.read_yaml(cls.md_api_path).get("apis", {})
        cls.api_params = cls.yaml_util.read_yaml(cls.md_api_params).get("api_params", {})
        
        
        # 加载缓存数据
        DataFactory.init_sql_cache(
        sql_config_path=str(project_root / "config" / "erp" / "md_init_sql.yaml"), # 主数据依赖的初始化sql 存放路径
        db_config_name="erp_db", # 数据库配置名称
        cache_key="md_init_cache", # 缓存key
        cache_dir="testdata/cache" # 缓存目录
        )
        cls.md_cache_data = CacheUtil.get('md_init_cache')
        
        cls.path_params = {"tmodule":"GEN_MD"}
        cls.nickname = cls.init_data["user_info"]['user_info']["nickname"]
        cls.user_id = cls.init_data["user_info"]['user_info']["id"]
    
    def get_api_path(self, api_key):
        """
        获取API路径
        """
        return self.apis.get(api_key, {}).get("path")
    
    def get_api_params(self, api_path, with_query_params=None):
        """
        获取API请求参数和完整URL
        """
        # 准备URL
        url = api_path
        if with_query_params:
            url = f"{api_path}?{with_query_params}"
        
        # 获取请求参数 (从api_params字典中获取对应api_path的参数模板)
        params = self.api_params.get(api_path, {})
        return params, url
      
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
