"""
通用基础模块的测试初始化
提供配置加载等通用功能
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

    def standard_api_call(self, api_key, set_dict=None, fields_to_filter=None, 
                         store_id_as=None):
        """
        标准化API调用方法，替换20+行重复的CRUD调用逻辑（纯执行，无断言）
        
        参数:
            api_key: API键名，如 "GEN-地址库-保存服务"
            set_dict: 要设置的参数字典，默认为None
            fields_to_filter: 需要过滤的字段列表，默认为None（使用通用字段）
            store_id_as: ID存储属性名，默认为None（返回extracted_id）
        
        返回:
            tuple: (response, extracted_id) - 响应对象和提取的ID
            
        功能:
            1. 获取API路径和参数模板
            2. 过滤POST body字段
            3. 设置请求参数
            4. 发送POST请求
            5. 提取并存储响应ID
            6. 记录Allure报告
            注意：不包含任何断言逻辑，验证由调用方负责
        """
        try:
            # 1. 获取API路径和参数模板
            api_path = self.get_api_path(api_key)
            params, url = self.get_api_params(api_path)
            
            # 2. 确定要过滤的字段（使用默认或传入的）
            if fields_to_filter is None:
                # 通用CRUD字段，根据API类型智能选择
                if "保存" in api_key or "新增" in api_key or "创建" in api_key:
                    fields_to_filter = ["id"]  # 保存操作通常过滤id
                elif "查询" in api_key or "列表" in api_key:
                    fields_to_filter = ["pageable", "fields", "conditionItems"]
                elif "详情" in api_key or "获取" in api_key:
                    fields_to_filter = ["id"]
                elif "删除" in api_key or "禁用" in api_key:
                    fields_to_filter = ["id"]
                else:
                    fields_to_filter = []
            
            # 3. 过滤POST body字段
            filtered_params = ParamUtil.filter_post_body_fields(
                params, fields_to_filter, ["params", "request"]
            )
            
            # 4. 设置请求参数（如果提供了set_dict）
            if set_dict:
                ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 5. 发送POST请求
            response = self.http.post(url, json=filtered_params)
            
            # 6. 提取响应ID（CRUD操作通常在 data.data 或 data.id）
            extracted_id = None
            if "保存" in api_key or "新增" in api_key or "创建" in api_key:
                # 保存操作返回新创建的ID
                extracted_id = response.get("data", {}).get("data", {})
                if isinstance(extracted_id, dict):
                    extracted_id = extracted_id.get("id", extracted_id)
            elif "详情" in api_key or "获取" in api_key:
                # 详情操作返回对象ID
                extracted_id = response.get("data", {}).get("data", {}).get("id")
            
            # 7. 存储ID到实例属性（如果指定了store_id_as）
            if store_id_as and extracted_id:
                setattr(self, f"{store_id_as}_id", extracted_id)
                self.logger.info(f"自动存储 {store_id_as}_id: {extracted_id}")
            
            # 8. 记录Allure报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
            # 9. 返回响应和提取的ID
            return response, extracted_id
            
        except Exception as e:
            # 异常时记录Allure报告并重新抛出
            a.text(str(e), "API调用失败原因")
            self.logger.error(f"standard_api_call 失败 [{api_key}]: {str(e)}")
            raise


if __name__ == "__main__":
    GenMdBaseTest.setup_class()
    print(GenMdBaseTest.nickname)
    # print(GenMdBaseTest.cust_user_info)