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
from utils.response_util import ResponseUtil

logger = Loggers()
logger
class AssertHelper:
    """断言辅助类，提供通用的断言方法"""
    
    @staticmethod
    def assert_id_exists(id_value: Union[int, str], field_name: str = "id") -> None:
        """断言 ID 存在且有效"""
        assert id_value, f"{field_name} 不能为空"

    @staticmethod
    def assert_eq(actual: Any, expected: Any, message: str = None) -> None:
        """断言相等"""
        assert actual == expected, message or f"实际值 {actual} 不等于预期值 {expected}"

    @staticmethod
    def assert_not_eq(actual: Any, expected: Any, message: str = None) -> None:
        """断言不相等"""
        assert actual != expected, message or f"实际值 {actual} 等于预期值 {expected}"

    @staticmethod
    def assert_response_success(response: Dict[str, Any], message: str = None) -> None:
        """
        断言响应成功
        
        Args:
            response: 响应数据字典
            message: 自定义错误消息
        """
        assert response.get("success", False), message or "响应未成功"

    @staticmethod
    def assert_response_data(response: Dict[str, Any], message: str = None) -> Any:
        """
        断言响应成功
        支持处理Response对象和字典类型的响应数据
        """
        # 1. 首先验证响应成功
        AssertHelper.assert_response_success(response)
        # 2. 使用 ResponseUtil 提取数据
        result = ResponseUtil.get_response_data(response)
        
        # 3. 验证结果不为 None
        assert result is not None, message or "未找到有效的响应数据"
        
        return result

    @staticmethod
    def assert_contains(container: Union[List, str], item: Any, message: str = None) -> None:
        """断言包含"""
        assert item in container, message or f"元素 {item} 不在容器中（容器类型：{type(container).__name__}）"

    @staticmethod
    def assert_not_contains(container: Union[List, str], item: Any, message: str = None) -> None:
        """断言不包含"""
        assert item not in container, message or f"元素 {item} 在容器中找到（容器类型：{type(container).__name__}）"

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

    @staticmethod
    def assert_not_empty(value: Any, message: str = None) -> None:
        """
        断言值不为空（None/空列表/空字典/空字符串等）
        
        Args:
            value: 要检查的值
            message: 自定义错误消息
        """
        if message is None:
            message = f"期望值不为空，但实际值为: {value}"
        assert value, message
        if isinstance(value, (list, dict, str)):
            assert len(value) > 0, message
            
            
            
if __name__ == "__main__":
    assert_helper = AssertHelper()
    assert_helper.assert_id_exists(1, "id")
    assert_helper.assert_eq(1, 1)
    assert_helper.assert_not_eq(1, 2)
    # assert_helper.assert_response_success({"status_code": 200, "json": {"success": True}})
    assert_helper.assert_contains([1, 2, 3], 2)
    assert_helper.assert_not_contains([1, 2, 3], 4)
    # assert_helper.assert_response_time({"elapsed": 1000})