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
    def assert_list_not_empty(data_list: List[Any], list_name: str) -> None:
        """
        断言列表非空
        
        Args:
            data_list: 要检查的列表
            list_name: 列表名称，用于错误提示
            
        Raises:
            AssertionError: 当列表为空时抛出
        """
        assert data_list is not None and len(data_list) > 0, f"{list_name}为空"
        
    @staticmethod
    def assert_status_matches(actual_status: str, expected_status: str, entity_name: str) -> None:
        """
        断言状态匹配
        
        Args:
            actual_status: 实际状态
            expected_status: 期望状态
            entity_name: 实体名称，用于错误提示
            
        Raises:
            AssertionError: 当状态不匹配时抛出
        """
        assert actual_status == expected_status, f"{entity_name}状态不匹配: 期望={expected_status}, 实际={actual_status}"
        
    @staticmethod
    def assert_field_value_matches(actual_value: Any, expected_value: Any, field_name: str) -> None:
        """
        断言字段值匹配
        
        Args:
            actual_value: 实际值
            expected_value: 期望值
            field_name: 字段名称，用于错误提示
            
        Raises:
            AssertionError: 当值不匹配时抛出
        """
        assert actual_value == expected_value, f"{field_name}值不匹配: 期望={expected_value}, 实际={actual_value}"
        
    @staticmethod
    def assert_response_success(response: Dict[str, Any], error_message: str = "请求失败") -> None:
        """
        断言响应成功
        
        Args:
            response: 响应数据
            error_message: 错误消息
            
        Raises:
            AssertionError: 当响应不成功时抛出
        """
        assert response.get("success", False), f"{error_message}: {response.get('errorMsg', '未知错误')}"
        
    @staticmethod
    def assert_all_records_match(records: List[Dict[str, Any]], field_name: str, expected_value: Any, entity_name: str) -> None:
        """
        断言所有记录都匹配指定条件
        
        Args:
            records: 记录列表
            field_name: 字段名称
            expected_value: 期望值
            entity_name: 实体名称，用于错误提示
            
        Raises:
            AssertionError: 当存在不匹配的记录时抛出
        """
        for record in records:
            actual_value = record.get(field_name)
            assert actual_value == expected_value, f"{entity_name} {field_name}不匹配: 期望={expected_value}, 实际={actual_value}"