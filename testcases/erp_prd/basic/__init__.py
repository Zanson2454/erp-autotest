# -*- coding: utf-8 -*-
"""
生产管理基础测试模块
定义生产管理模块的基础测试类，提供测试用例需要的公共方法

主要功能：
1. 提供测试基础设施
2. 提供测试工具方法
3. 管理配置初始化
4. 集成 Allure 报告
"""
import allure
from testcases.comm.base_test import BaseTest
from utils.param_util import ParamUtil
from utils.report_util import a
from .init_config import PrdConfigInitializer

@allure.epic("生产管理")
@allure.feature("基础数据配置")
class PrdBasicBaseTest(BaseTest):
    """生产管理基础测试类
    
    提供:
    1. 配置管理
    2. 测试数据生成
    3. 测试步骤记录
    4. 响应验证
    5. API配置获取
    """
    
    @classmethod
    def setup_class(cls):
        """测试类初始化
        1. 初始化基类
        2. 创建配置管理器实例
        """
        super().setup_class()
        cls.config_manager = PrdConfigInitializer()
        cls.logger.info("生产基础测试类初始化完成")
    
    def setup_method(self, method):
        """测试方法初始化
        1. 初始化基类方法
        2. 确保配置数据存在
        """
        super().setup_method(method)
        self.config_manager.ensure_configs_exist()
    
    def generate_test_data(self, prefix="TEST"):
        """生成测试数据
        
        Args:
            prefix (str): 编码前缀
            
        Returns:
            dict: 包含编码和名称的字典
        """
        return {
            "code": ParamUtil.generate_unique_code(prefix),
            "name": ParamUtil.generate_test_name(prefix),
            "remark": ParamUtil.generate_remark()
        }
    
    def add_allure_step(self, title, content):
        """添加测试步骤到Allure报告
        
        Args:
            title (str): 步骤标题
            content (str/dict): 步骤内容
        """
        with a.step(title):
            if isinstance(content, dict):
                a.json(content, title)
            else:
                a.text(str(content), title)
    
    def verify_response(self, response, error_msg=""):
        """验证响应结果
        
        Args:
            response (dict): 响应结果
            error_msg (str): 错误信息
            
        Raises:
            AssertionError: 响应验证失败
        """
        try:
            self.assert_util.assert_response_success(response)
            self.add_allure_step("验证结果", "成功")
        except Exception as e:
            self.add_allure_step("错误信息", f"{error_msg}: {str(e)}")
            raise
    
    def get_api_config(self, api_key):
        """获取API配置
        
        Args:
            api_key (str): API键名
            
        Returns:
            tuple: (api_path, url, params)
        """
        api_path = ParamUtil.get_api_path(self.apis, api_key)
        params, url = ParamUtil.get_api_params(self.api_params, api_path)
        return api_path, url, params
    
    def get_config(self, config_type):
        """统一的配置获取方法
        
        Args:
            config_type (str): 配置类型名称
            
        Returns:
            dict: 配置信息
            
        Example:
            >>> self.get_config('issue_types')
            >>> self.get_config('wo_types')
            >>> self.get_config('routing_types')
        """
        method = getattr(self.config_manager, f"get_{config_type}")
        if not method:
            raise AttributeError(f"配置类型 {config_type} 不存在")
        return method()

class PrdBaseTest(PrdBasicBaseTest):
    """生产测试基类
    
    继承自 PrdBasicBaseTest,用于生产模块的具体测试用例
    """
    pass 