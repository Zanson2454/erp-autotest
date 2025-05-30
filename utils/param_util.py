"""
参数处理工具包

功能：
- 提供 post 请求 body 字段过滤方法，便于用例只传递需要的字段。
"""
from typing import Dict, List, Any

class ParamUtil:
    @staticmethod
    def filter_post_body_fields(body: Dict[str, Any], fields: List[str], path: List[str] = None) -> Dict[str, Any]:
        """
        支持指定嵌套路径的字段过滤，并将过滤结果嵌套回原路径
        :param body: 原始请求体 dict
        :param fields: 需要保留的字段名列表
        :param path: 需要过滤的嵌套路径（如 ["params", "request"]）
        :return: 只包含指定字段的新 dict，嵌套回 path
        """
        if path and len(path) > 0:
            p = path[0]
            sub_body = body.get(p, {})
            filtered = ParamUtil.filter_post_body_fields(sub_body, fields, path[1:])
            return {p: filtered}
        else:
            result = {}
            for k, v in body.items():
                if k in fields:
                    # 如果字段值是一个字典，保留其所有内容
                    if isinstance(v, dict):
                        result[k] = v
                    else:
                        result[k] = v
            return result

    @staticmethod
    def convert_param_type(body: Dict[str, Any], path: List[str], target_type: str = "array", **kwargs) -> Dict[str, Any]:
        """
        转换参数类型，支持多种类型转换
        :param body: 原始请求体 dict
        :param path: 需要转换的嵌套路径（如 ["params", "request"]）
        :param target_type: 目标类型，支持以下类型：
            - "array": 转换为数组
            - "object": 转换为对象
            - "string": 转换为字符串
            - "number": 转换为数字
            - "boolean": 转换为布尔值
            - "date": 转换为日期字符串
            - "timestamp": 转换为时间戳
        :param kwargs: 额外参数
            - format: 日期格式（当target_type为date时使用）
            - decimal_places: 小数位数（当target_type为number时使用）
        :return: 转换后的 dict
        """
        if not path or len(path) == 0:
            return body
            
        result = body.copy()
        current = result
        # 遍历路径直到倒数第二个元素
        for i in range(len(path) - 1):
            if path[i] not in current:
                return result
            current = current[path[i]]
            
        # 获取最后一个路径元素
        last_key = path[-1]
        if last_key not in current:
            return result
            
        # 根据目标类型进行转换
        if target_type == "array":
            # 如果当前值不是数组，将其转换为数组
            if not isinstance(current[last_key], list):
                current[last_key] = [current[last_key]]
        elif target_type == "object":
            # 如果当前值是数组且只有一个元素，将其转换为对象
            if isinstance(current[last_key], list) and len(current[last_key]) == 1:
                current[last_key] = current[last_key][0]
        elif target_type == "string":
            # 转换为字符串
            if not isinstance(current[last_key], str):
                current[last_key] = str(current[last_key])
        elif target_type == "number":
            # 转换为数字
            try:
                decimal_places = kwargs.get('decimal_places', 2)
                if isinstance(current[last_key], str):
                    current[last_key] = round(float(current[last_key]), decimal_places)
                elif isinstance(current[last_key], (int, float)):
                    current[last_key] = round(float(current[last_key]), decimal_places)
            except (ValueError, TypeError):
                pass
        elif target_type == "boolean":
            # 转换为布尔值
            if isinstance(current[last_key], str):
                current[last_key] = current[last_key].lower() in ('true', '1', 'yes', 'y')
            elif isinstance(current[last_key], (int, float)):
                current[last_key] = bool(current[last_key])
        elif target_type == "date":
            # 转换为日期字符串
            try:
                date_format = kwargs.get('format', '%Y-%m-%d')
                if isinstance(current[last_key], (int, float)):
                    # 假设是时间戳
                    from datetime import datetime
                    current[last_key] = datetime.fromtimestamp(current[last_key]/1000).strftime(date_format)
                elif isinstance(current[last_key], str):
                    # 尝试解析日期字符串
                    from datetime import datetime
                    parsed_date = datetime.strptime(current[last_key], '%Y-%m-%d %H:%M:%S')
                    current[last_key] = parsed_date.strftime(date_format)
            except (ValueError, TypeError):
                pass
        elif target_type == "timestamp":
            # 转换为时间戳（毫秒）
            try:
                from datetime import datetime
                if isinstance(current[last_key], str):
                    # 尝试解析日期字符串
                    parsed_date = datetime.strptime(current[last_key], '%Y-%m-%d %H:%M:%S')
                    current[last_key] = int(parsed_date.timestamp() * 1000)
                elif isinstance(current[last_key], datetime):
                    current[last_key] = int(current[last_key].timestamp() * 1000)
            except (ValueError, TypeError):
                pass
                
        return result

# 示例用例
def _demo():
    swagger_body = {
        "params": {
            "request": {
                "id": 1,
                "name": "test",
                "desc": "desc",
                "object": {
                    "id": 1,
                    "name": "test",
                    "desc": "desc"
                }
            }
        }
    }
    
    # 测试各种类型转换
    print("原始数据:", swagger_body)
    
    # 转换为数组
    array_data = ParamUtil.convert_param_type(swagger_body, ["params", "request"], "array")
    print("\n转换为数组:", array_data)
    
    # 转换为对象
    object_data = ParamUtil.convert_param_type(array_data, ["params", "request"], "object")
    print("\n转换为对象:", object_data)
    
    # 转换为字符串
    string_data = ParamUtil.convert_param_type(swagger_body, ["params", "request", "id"], "string")
    print("\n转换为字符串:", string_data)
    
    # 转换为数字
    number_data = ParamUtil.convert_param_type(swagger_body, ["params", "request", "id"], "number", decimal_places=2)
    print("\n转换为数字:", number_data)
    
    # 转换为日期
    date_data = {
        "params": {
            "request": {
                "date": "2024-03-20 10:00:00"
            }
        }
    }
    date_converted = ParamUtil.convert_param_type(date_data, ["params", "request", "date"], "date", format="%Y-%m-%d")
    print("\n转换为日期:", date_converted)
    
    # 转换为时间戳
    timestamp_data = {
        "params": {
            "request": {
                "date": "2024-03-20 10:00:00"
            }
        }
    }
    timestamp_converted = ParamUtil.convert_param_type(timestamp_data, ["params", "request", "date"], "timestamp")
    print("\n转换为时间戳:", timestamp_converted)

if __name__ == "__main__":
    _demo() 
    