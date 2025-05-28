"""
通用基础模块的测试初始化
提供配置加载等通用功能
"""
import yaml
from pathlib import Path
from testcases.comm.base_test import BaseTest
from utils.yaml_util import YamlUtil

# 获取项目根目录 (例如: /Users/shengqiaowei/Desktop/erp-autotest)
project_root = Path(__file__).resolve().parent.parent.parent

class GenBaseTest(BaseTest):
    """通用基础模块的基础测试类，负责加载通用配置和提供API访问方法"""
    
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
        # base_api_path: API路径配置文件 (例如: /Users/shengqiaowei/Desktop/erp-autotest/testdata/gen/gen_api_path.yaml)
        # 包含各API的路径信息 {"apis": {"物料主数据定义表-分页数据服务": {"path": "/api/trantor/service/engine/execute/ERP_GEN$gen_mat_md_PAGING_DATA_SERVICE"}}}
        cls.base_api_path = Path(project_root) / "testdata" / "gen" / "gen_api_path.yaml"
        
        # base_api_params: API参数配置文件 (例如: /Users/shengqiaowei/Desktop/erp-autotest/testdata/gen/gen_api_params.yaml)
        # 包含各API的参数模板 {"api_params": {"/api/trantor/service/engine/execute/ERP_GEN$gen_mat_md_PAGING_DATA_SERVICE": {...参数模板...}}}
        cls.base_api_params = Path(project_root) / "testdata" / "gen" / "gen_api_params.yaml"
        
        # 初始化YAML工具类，用于读取YAML配置文件
        cls.yaml_util = YamlUtil()
        
        # 加载API路径配置
        # apis: 存储所有API路径信息的字典，格式为 {"物料主数据定义表-分页数据服务": {"path": "/api/..."}, ...}
        cls.apis = cls.yaml_util.read_yaml(cls.base_api_path).get("apis", {})
        
        # 加载API参数配置
        # api_params: 存储所有API参数模板的字典，格式为 {"/api/...": {...参数模板...}, ...}
        cls.api_params = cls.yaml_util.read_yaml(cls.base_api_params).get("api_params", {})
        
        cls.logger.info("GenBaseTest初始化完成")
    
    def get_api_path(self, api_key):
        """
        获取API路径
        
        参数:
            api_key (str): API的名称键值，如"物料主数据定义表-分页数据服务"
            
        返回:
            str: 对应的API路径，如"/api/trantor/service/engine/execute/ERP_GEN$gen_mat_md_PAGING_DATA_SERVICE"
                 如果找不到对应的API，则返回None
        """
        return self.apis.get(api_key, {}).get("path")
    
    def get_api_params(self, api_path, with_query_params=None):
        """
        获取API请求参数和完整URL
        
        参数:
            api_path (str): API路径，如"/api/trantor/service/engine/execute/ERP_GEN$gen_mat_md_PAGING_DATA_SERVICE"
            with_query_params (str, optional): 查询参数字符串，如"param1=value1&param2=value2"
            
        返回:
            tuple: (params, url)
                params (dict): 对应API的请求参数模板，如{"params": {"request": {...}}}
                url (str): 完整的API URL，如果提供了with_query_params，则会附加到路径后
                           例如: "/api/..." 或 "/api/...?param1=value1"
        """
        # 准备URL
        url = api_path
        if with_query_params:
            url = f"{api_path}?{with_query_params}"
        
        # 获取请求参数 (从api_params字典中获取对应api_path的参数模板)
        params = self.api_params.get(api_path, {})
        return params, url
