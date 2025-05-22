"""
YAML数据处理工具类
用于处理YAML配置文件中的数据，支持复杂嵌套结构和动态参数替换
"""

import copy
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Union, Optional, Tuple

from utils.yaml_util import YamlUtil


class YamlDataProcessor:
    """
    YAML数据处理类
    用于读取YAML配置文件，并处理其中的动态参数替换
    
    支持的功能：
    1. 加载YAML配置文件
    2. 处理复杂的嵌套YAML结构
    3. 替换YAML中的动态参数（支持多种格式）
    4. 错误处理和日志记录
    """

    def __init__(self, logger=None):
        """
        初始化YAML数据处理器
        
        参数:
            logger: 日志记录器，如果为None则创建新的日志记录器
        """
        # 初始化日志记录器
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        # 初始化YAML工具
        self.yaml_util = YamlUtil()
        
    def load_config(self, api_path_file: Union[Path, str], api_params_file: Union[Path, str]) -> Tuple[Dict, Dict]:
        """
        加载API路径和参数配置文件
        
        参数:
            api_path_file (Path|str): API路径配置文件路径
            api_params_file (Path|str): API参数配置文件路径
            
        返回:
            tuple: (api_paths, api_params) API路径和参数配置
        """
        try:
            # 读取API路径配置
            api_paths = self.yaml_util.read_yaml(api_path_file)
            # 读取API参数配置
            api_params = self.yaml_util.read_yaml(api_params_file).get("api_params", {})
            
            return api_paths, api_params
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {str(e)}")
            return {}, {}

    def load_module_paths(self, api_paths: Dict, module_name: str, sub_module_name: Optional[str] = None) -> Dict:
        """
        从API路径配置中加载指定模块的路径
        
        参数:
            api_paths (Dict): API路径配置
            module_name (str): 模块名称，例如：通用基础
            sub_module_name (str, optional): 子模块名称，例如：合作伙伴
            
        返回:
            Dict: 指定模块的API路径配置
        """
        try:
            # 获取模块路径
            module_paths = api_paths.get(module_name, {})
            
            # 如果指定了子模块，则返回子模块的路径
            if sub_module_name and sub_module_name in module_paths:
                return module_paths[sub_module_name]
                
            return module_paths
        except Exception as e:
            self.logger.error(f"加载模块路径失败: {str(e)}")
            return {}
    
    def get_request_data(self, api_url: str, api_params: Dict, **kwargs) -> Dict:
        """
        从YAML配置中获取请求数据，并替换动态参数
        
        参数:
            api_url (str): API接口路径
            api_params (dict): API参数配置字典
            **kwargs: 动态参数，用于替换YAML中的占位符
            
        返回:
            dict: 处理后的请求数据对象
            
        示例:
            processor = YamlDataProcessor()
            api_paths, api_params = processor.load_config(path_file, params_file)
            data = processor.get_request_data(
                "/api/example/endpoint", 
                api_params,
                param1="value1", 
                param2="value2"
            )
        """
        try:
            api_config = api_params.get(api_url, {})
            if not api_config:
                self.logger.error(f"未找到API配置: {api_url}")
                return {}
                
            request_data = copy.deepcopy(api_config)
            
            if "params" in request_data and "request" in request_data["params"]:
                self._replace_values(request_data["params"]["request"], kwargs)
            
            return request_data
        except Exception as e:
            self.logger.error(f"处理请求数据出错: {str(e)}")
            return {}
    
    def _replace_values(self, obj, kwargs):
        """替换数据结构中的占位符"""
        if isinstance(obj, dict):
            for key, value in list(obj.items()):
                if isinstance(value, (dict, list)):
                    self._replace_values(value, kwargs)
                elif isinstance(value, str) and "${" in value and "}" in value:
                    if value.startswith("${") and value.endswith("}"):
                        var_name = value[2:-1]
                        if var_name in kwargs:
                            obj[key] = kwargs[var_name]
                    else:
                        # 部分替换逻辑可以根据需要添加
                        pass
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, (dict, list)):
                    self._replace_values(item, kwargs)
                elif isinstance(item, str) and "${" in item and "}" in item:
                    if item.startswith("${") and item.endswith("}"):
                        var_name = item[2:-1]
                        if var_name in kwargs:
                            obj[i] = kwargs[var_name]
    
    def find_and_merge(self, api_params: Dict, api_key_part: str) -> Dict:
        """
        根据部分API路径查找和合并相关配置
        
        参数:
            api_params (Dict): API参数配置字典
            api_key_part (str): API路径的部分关键字
            
        返回:
            Dict: 合并后的参数配置
        """
        result = {}
        
        # 查找包含指定关键字的所有API配置
        for api_key, config in api_params.items():
            if api_key_part in api_key:
                # 合并配置
                if not result:
                    result = copy.deepcopy(config)
                else:
                    # 合并params.request部分
                    if "params" in config and "request" in config["params"]:
                        if "params" not in result:
                            result["params"] = {"request": {}}
                        elif "request" not in result["params"]:
                            result["params"]["request"] = {}
                            
                        result["params"]["request"].update(config["params"]["request"])
        
        return result 