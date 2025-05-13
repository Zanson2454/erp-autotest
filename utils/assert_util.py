"""
断言工具模块

提供了一系列用于API响应和数据处理断言的辅助方法。
主要用于测试用例中的结果验证。
"""

import os
import sys
from pathlib import  Path
from typing import Dict, Any, List, Optional, Union


# 添加项目根目录到 Python 路径
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))



from utils.log_util import Loggers

logger = Loggers()
logger
class AssertHelper:
    """断言辅助类，提供通用的断言方法"""
    
    @staticmethod
    def assert_id_exists(id_value: Any, id_name: str) -> None:
        """
        断言ID存在
        """
        assert id_value is not None, f"未能获取到{id_name}"
    @staticmethod
    def assert_response_success(response: Union[Dict[str, Any], Any], error_message: str = "请求失败") -> None:
        """
        断言响应成功
        支持处理Response对象和字典类型的响应数据
        """
        # 如果是Response对象
        if hasattr(response, 'status_code'):
            assert response.status_code == 200, f"{error_message}: {response.get('errorMsg', f'接口请求非200，状态码为{response.status_code}')}"
            response_data = response.json() if hasattr(response, 'json') else response
        else:
            # 如果是字典类型
            response_data = response
            
        assert response_data.get("success", False), f"{error_message}: {response_data.get('errorMsg', '接口请求成功，但返回数据失败')}"
        
    @staticmethod
    def assert_contains(container: Union[List, Dict, str], item: Any):
        """验证元素存在于容器"""
        assert item in container, f"元素 {item} 未在容器中找到（容器类型：{type(container).__name__}）"
    
    @staticmethod
    def assert_not_contains(container: Union[List, Dict, str], item: Any):
        """验证元素不存在于容器"""
        assert item not in container, f"元素 {item} 在容器中找到（容器类型：{type(container).__name__}）"


    @staticmethod
    def assert_response_time(response: Union[Dict[str, Any], Any], max_time: int = 1000, unit: str = 'ms'):
        """
        验证接口响应时间
        支持处理Response对象和字典类型的响应数据
        
        Args:
            response: 响应对象或响应数据
            max_time: 最大允许时间
            unit: 时间单位，支持 's'(秒) 或 'ms'(毫秒)
        """
        if hasattr(response, 'elapsed'):
            elapsed = response.elapsed.total_seconds()
            # 如果单位是毫秒，进行转换
            if unit.lower() == 'ms':
                elapsed = elapsed * 1000
                max_time = max_time * 1000
                
            assert elapsed <= max_time, f"响应时间 {elapsed:.2f}{unit} 超过阈值 {max_time:.2f}{unit}"
            logger.info(f"接口响应时间：{elapsed:.2f}{unit}")
        else:
            logger.warning("响应对象中没有elapsed属性，无法验证响应时间")