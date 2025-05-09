from typing import Dict, Any, List
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
        """
        assert "data" in response_data, "响应中缺少data字段"
        data = response_data["data"]
        
        # 处理嵌套的data字段
        for key in data_path.split('.'):
            assert key in data, f"响应中缺少{key}字段"
            data = data[key]
            
        return data
    
    @staticmethod
    def assert_fields_exist(data: Dict[str, Any], expected_fields: List[str], field_descriptions: Dict[str, str] = None) -> None:
        """
        断言数据包含指定的字段
        
        Args:
            data: 数据对象
            expected_fields: 期望的字段列表
            field_descriptions: 字段描述字典，用于错误提示
        """
        for field in expected_fields:
            assert field in data, f"数据中缺少{field_descriptions.get(field, field)}字段"
    
    @staticmethod
    def assert_list_not_empty(data_list: List[Any], list_name: str) -> None:
        """
        断言列表不为空
        
        Args:
            data_list: 数据列表
            list_name: 列表名称，用于错误提示
        """
        assert isinstance(data_list, list), f"{list_name}不是列表类型"
        assert len(data_list) > 0, f"{list_name}为空"
    
    @staticmethod
    def assert_list_length(data_list: List[Any], min_length: int, list_name: str) -> None:
        """
        断言列表长度符合预期
        
        Args:
            data_list: 数据列表
            min_length: 最小长度
            list_name: 列表名称，用于错误提示
        """
        assert isinstance(data_list, list), f"{list_name}不是列表类型"
        assert len(data_list) >= min_length, f"{list_name}长度不足，当前只有{len(data_list)}条记录"
    
    @staticmethod
    def assert_http_status(response, expected_status: int = 200) -> None:
        """
        断言HTTP响应状态码
        
        Args:
            response: HTTP响应对象
            expected_status: 期望的状态码，默认为200
        """
        assert response.status_code == expected_status, f"HTTP请求失败: {response.status_code}"
    
    @staticmethod
    def assert_id_exists(id_value: Any, id_name: str) -> None:
        """
        断言ID存在
        
        Args:
            id_value: ID值
            id_name: ID名称，用于错误提示
        """
        assert id_value is not None, f"未能获取到{id_name}"
