"""
通用基础模块的测试初始化
提供配置加载等通用功能
"""
from pathlib import Path
from typing import Dict, Tuple
from testcases.comm.base_test import BaseTest
from utils.yaml_data_util import YamlDataProcessor
# 获取项目根目录
project_root = Path(__file__).resolve().parent.parent.parent


class GenBaseTest(BaseTest):
    """通用基础模块的基础测试类"""
    
    @classmethod
    def setup_class(cls):
        """
        测试类初始化 - 加载通用配置
        这个方法会在BaseTest.setup_class之后执行，初始化通用的配置
        """
        # 调用父类初始化方法
        super().setup_class()
        
        # 加载API路径和参数配置，设置yaml处理器
        cls.setup_config()
    
    @classmethod
    def setup_config(cls):
        """设置配置和处理器"""
        # 1. 配置文件路径
        api_path_file = Path(project_root) / "testdata" / "gen" / "mat.yaml"  # API路径配置文件
        api_params_file = Path(project_root) / "testdata" / "gen" / "mat_api_params.yaml"  # API参数配置文件
        
        # 2. 创建YAML处理器
        cls.yaml_processor = YamlDataProcessor(logger=cls.logger)
        
        # 3. 加载配置文件
        api_paths, api_params = cls.yaml_processor.load_config(api_path_file, api_params_file)
        
        # 4. 保存配置到类变量
        cls.api_paths = api_paths  # 所有API路径配置
        cls.api_params = api_params  # 所有API参数配置
    
    @classmethod
    def get_module_paths(cls, module_name, sub_module_name=None):
        """
        获取指定模块的API路径
        
        参数:
            module_name: 模块名称，如"通用基础"
            sub_module_name: 子模块名称，如"合作伙伴"
            
        返回:
            module_paths: 该模块的API路径字典
        """
        # 获取模块路径
        if sub_module_name:
            # 获取子模块路径，例如："通用基础"模块下的"合作伙伴"子模块
            module_paths = cls.api_paths.get(module_name, {}).get(sub_module_name, {})
            if not module_paths:
                cls.logger.warning(f"未找到[{module_name}]模块下的[{sub_module_name}]子模块配置")
        else:
            # 获取整个模块的路径
            module_paths = cls.api_paths.get(module_name, {})
            if not module_paths:
                cls.logger.warning(f"未找到[{module_name}]模块配置")
        
        return module_paths
    
    def get_request_data(self, api_url, **kwargs):
        """
        获取请求数据并替换参数
        
        参数:
            api_url: API接口路径，如"/api/xxx/yyy"
            **kwargs: 要替换的参数，如partner_id="123"
            
        返回:
            request_data: 替换参数后的请求数据
        """
        # 调用工具类方法，从api_params中获取数据并替换参数
        return self.yaml_processor.get_request_data(api_url, self.api_params, **kwargs)
