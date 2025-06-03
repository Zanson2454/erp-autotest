"""
生产模块的测试初始化
提供配置加载等通用功能
"""
import yaml
from pathlib import Path
from testcases.comm.base_test import BaseTest
from utils.yaml_util import YamlUtil
from utils.mysql_util import DBManager
import allure

# 获取项目根目录
project_root = Path(__file__).resolve().parent.parent.parent

class PrdBaseTest(BaseTest):
    """生产模块的基础测试类，负责加载通用配置和提供API访问方法"""
    
    # 保存基础配置信息的类变量
    base_info = {}
    
    @classmethod
    def setup_class(cls):
        """
        测试类初始化 - 加载通用配置
        完成以下工作:
        1. 调用父类初始化方法 (包括登录、数据库连接等)
        2. 初始化通用配置文件路径
        3. 加载API路径和参数配置
        """
        # 调用父类初始化方法
        super().setup_class()
        
        # 初始化配置文件路径
        cls.base_api_path = Path(project_root) / "testdata" / "prd" / "prd_api_path.yaml"
        cls.base_api_params = Path(project_root) / "testdata" / "prd" / "prd_api_params.yaml"
        
        # 初始化YAML工具类
        cls.yaml_util = YamlUtil()
        
        # 加载API路径配置
        cls.apis = cls.yaml_util.read_yaml(cls.base_api_path).get("apis", {})
        
        # 加载API参数配置
        cls.api_params = cls.yaml_util.read_yaml(cls.base_api_params).get("api_params", {})
        
        # 初始化基础配置数据
        cls._init_base_info()
        
        cls.logger.info("PrdBaseTest初始化完成")
    
    @classmethod
    def _init_base_info(cls):
        """初始化基础配置数据"""
        try:
            # 1. 查询工单类型配置
            wo_type_sql = """
                SELECT id, type_code, type_name 
                FROM prd_wo_type_cf 
                WHERE deleted = 0 AND type_name = '量产生产订单'
                LIMIT 1
            """
            wo_type_result = DBManager.query(wo_type_sql)
            if not wo_type_result:
                raise Exception("未找到量产生产订单工单类型配置")
            
            # 2. 查询库存组织配置
            inv_org_sql = """
                SELECT id, org_code, org_name 
                FROM org_struct_md 
                WHERE org_status='ENABLED' 
                AND org_dimension_code='SCM_ORG_GRP' 
                AND org_code LIKE 'C100%' 
                AND org_business_type_codes = '["INV_ORG"]' 
                AND deleted=0 
                LIMIT 1
            """
            inv_org_result = DBManager.query(inv_org_sql)
            if not inv_org_result:
                raise Exception("未找到C100开头的库存组织配置")
            
            # 3. 保存查询结果
            cls.base_info.update({
                "wo_type_info": {
                    "id": wo_type_result[0]["id"],
                    "type_code": wo_type_result[0]["type_code"],
                    "type_name": wo_type_result[0]["type_name"]
                },
                "inv_org_info": {
                    "id": inv_org_result[0]["id"],
                    "org_code": inv_org_result[0]["org_code"],
                    "org_name": inv_org_result[0]["org_name"]
                }
            })
            
            cls.logger.info(f"基础配置数据初始化成功: {cls.base_info}")
            
        except Exception as e:
            cls.logger.error(f"基础配置数据初始化失败: {str(e)}")
            raise
    
    def get_api_path(self, api_key):
        """
        获取API路径
        
        参数:
            api_key (str): API的名称键值
            
        返回:
            str: 对应的API路径，如果找不到对应的API，则返回None
        """
        return self.apis.get(api_key, {}).get("path")
    
    def get_api_params(self, api_path, with_query_params=None):
        """
        获取API请求参数和完整URL
        
        参数:
            api_path (str): API路径
            with_query_params (str, optional): 查询参数字符串
            
        返回:
            tuple: (params, url)
                params (dict): 对应API的请求参数模板
                url (str): 完整的API URL
        """
        url = api_path
        if with_query_params:
            url = f"{api_path}?{with_query_params}"
        
        params = self.api_params.get(api_path, {})
        return params, url 