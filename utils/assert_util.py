"""
断言工具模块

提供了一系列用于API响应和数据处理断言的辅助方法。
主要用于测试用例中的结果验证。
"""

from typing import Dict, Any, List, Optional, Union
from loguru import logger

class AssertHelper:
    """断言辅助类，提供通用的断言方法"""
    
    @staticmethod
    def assert_response_status(response_data: Dict[str, Any], expected_success: bool = True) -> None:
        """
        断言响应状态
        
        Args:
            response_data: 响应数据
            expected_success: 期望的成功状态，默认为True
            
        Raises:
            AssertionError: 当响应状态不符合预期时抛出
        """
        assert response_data["success"] is expected_success, f"响应状态不符合预期: {response_data}"
    
    @staticmethod
    def assert_response_has_data(response_data: Dict[str, Any], data_path: str = "data") -> Dict[str, Any]:
        """
        断言响应包含数据字段
        
        Args:
            response_data: 响应数据
            data_path: 数据字段路径，默认为"data"
            
        Returns:
            Dict[str, Any]: 数据字段的值
            
        Raises:
            AssertionError: 当响应中缺少指定字段时抛出
        """
        assert "data" in response_data, f"响应中缺少data字段: {response_data}"
        data = response_data["data"]
        
        # 处理嵌套的data字段
        for key in data_path.split('.'):
            assert key in data, f"响应中缺少{key}字段: {data}"
            data = data[key]
            
        return data
    
    @staticmethod
    def assert_fields_exist(data: Dict[str, Any], expected_fields: List[str], field_descriptions: Optional[Dict[str, str]] = None) -> None:
        """
        断言数据包含指定的字段
        
        Args:
            data: 数据对象
            expected_fields: 期望的字段列表
            field_descriptions: 字段描述字典，用于错误提示
            
        Raises:
            AssertionError: 当数据中缺少指定字段时抛出
        """
        for field in expected_fields:
            assert field in data, f"数据中缺少{field_descriptions.get(field, field)}字段: {data}"
    
    @staticmethod
    def assert_list_not_empty(data_list: List[Any], list_name: str) -> None:
        """
        断言列表不为空
        
        Args:
            data_list: 数据列表
            list_name: 列表名称，用于错误提示
            
        Raises:
            AssertionError: 当列表为空或不是列表类型时抛出
        """
        assert isinstance(data_list, list), f"{list_name}不是列表类型: {type(data_list)}"
        assert len(data_list) > 0, f"{list_name}为空"
    
    @staticmethod
    def assert_list_length(data_list: List[Any], min_length: int, list_name: str) -> None:
        """
        断言列表长度符合预期
        
        Args:
            data_list: 数据列表
            min_length: 最小长度
            list_name: 列表名称，用于错误提示
            
        Raises:
            AssertionError: 当列表长度不足或不是列表类型时抛出
        """
        assert isinstance(data_list, list), f"{list_name}不是列表类型: {type(data_list)}"
        assert len(data_list) >= min_length, f"{list_name}长度不足，当前只有{len(data_list)}条记录，期望至少{min_length}条"
    
    @staticmethod
    def assert_http_status(response: Any, expected_status: int = 200) -> None:
        """
        断言HTTP响应状态码
        
        Args:
            response: HTTP响应对象
            expected_status: 期望的状态码，默认为200
            
        Raises:
            AssertionError: 当HTTP状态码不符合预期时抛出
        """
        assert response.status_code == expected_status, f"HTTP请求失败: 状态码 {response.status_code}，响应内容: {response.text}"
    
    @staticmethod
    def assert_id_exists(id_value: Any, id_name: str) -> None:
        """
        断言ID存在
        
        Args:
            id_value: ID值
            id_name: ID名称，用于错误提示
            
        Raises:
            AssertionError: 当ID不存在时抛出
        """
        assert id_value is not None, f"未能获取到{id_name}"
    
    @staticmethod
    def assert_response_code(response_data: Dict[str, Any], expected_code: str) -> None:
        """
        断言响应码
        
        Args:
            response_data: 响应数据
            expected_code: 期望的响应码
            
        Raises:
            AssertionError: 当响应码不符合预期时抛出
        """
        assert response_data.get("code") == expected_code, f"响应码不符合预期: 期望 {expected_code}，实际 {response_data.get('code')}"
    
    @staticmethod
    def assert_response_message(response_data: Dict[str, Any], expected_message: str) -> None:
        """
        断言响应消息
        
        Args:
            response_data: 响应数据
            expected_message: 期望的响应消息
            
        Raises:
            AssertionError: 当响应消息不符合预期时抛出
        """
        assert response_data.get("message") == expected_message, f"响应消息不符合预期: 期望 {expected_message}，实际 {response_data.get('message')}"
    
    @staticmethod
    def assert_value_in_range(value: Union[int, float], min_value: Union[int, float], max_value: Union[int, float], value_name: str) -> None:
        """
        断言数值在指定范围内
        
        Args:
            value: 要检查的数值
            min_value: 最小值
            max_value: 最大值
            value_name: 数值名称，用于错误提示
            
        Raises:
            AssertionError: 当数值不在指定范围内时抛出
        """
        assert min_value <= value <= max_value, f"{value_name}不在有效范围内: 期望 {min_value} <= {value} <= {max_value}"
    
    @staticmethod
    def assert_string_contains(text: str, substring: str, description: str = "文本") -> None:
        """
        断言字符串包含指定子串
        
        Args:
            text: 要检查的文本
            substring: 期望包含的子串
            description: 文本描述，用于错误提示
            
        Raises:
            AssertionError: 当文本不包含指定子串时抛出
        """
        assert substring in text, f"{description}不包含预期内容: 期望包含 '{substring}'，实际内容: '{text}'"
