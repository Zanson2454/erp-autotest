"""
参数处理工具包

功能：
- 提供 post 请求 body 字段过滤方法，便于用例只传递需要的字段。
- 提供统一的测试用例装饰器，简化测试用例的装饰器使用
"""
from typing import Dict, List, Any, Optional, Union
import re
import inspect
import sys
import uuid


class ParamUtil:
    @staticmethod
    def _sanitize_pageable(pageable: Dict[str, Any]) -> Dict[str, Any]:
        """清洗 pageable 结构，避免无效排序/筛选结构触发后端参数校验错误。"""
        if not isinstance(pageable, dict):
            return pageable

        sort_orders = pageable.get("sortOrders")
        if sort_orders is None:
            pageable["sortOrders"] = []
        elif isinstance(sort_orders, list):
            valid_orders = []
            field_keys = {"field", "property", "orderBy", "column", "name", "key"}
            for item in sort_orders:
                if not isinstance(item, dict):
                    continue
                if not any(item.get(k) for k in field_keys):
                    continue
                valid_orders.append(item)
            pageable["sortOrders"] = valid_orders

        if pageable.get("conditionItems") is None:
            pageable["conditionItems"] = {}
        if pageable.get("conditionGroup") is None:
            pageable["conditionGroup"] = {}
        return pageable

    @staticmethod
    def sanitize_payload(payload: Any) -> Any:
        """
        递归清洗 payload 中的 pageable 结构。
        主要用于 use_param_util=False 的场景，避免模板残留空排序对象。
        """
        if isinstance(payload, dict):
            for key, value in payload.items():
                if key == "pageable" and isinstance(value, dict):
                    ParamUtil._sanitize_pageable(value)
                else:
                    ParamUtil.sanitize_payload(value)
        elif isinstance(payload, list):
            for item in payload:
                ParamUtil.sanitize_payload(item)
        return payload

    @staticmethod
    def filter_post_body_fields(body: Dict[str, Any], fields: List[str], path: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        支持指定嵌套路径的字段过滤，并将过滤结果嵌套回原路径，保留同级其它字段
        :param body: 原始请求体 dict
        :param fields: 需要保留的字段名列表
        :param path: 需要过滤的嵌套路径（如 ["params", "request"]）
        :return: 只包含指定字段的新 dict，嵌套回 path，保留同级其它字段
        """
        if not isinstance(body, dict):
            # 兼容参数模板中 request 为 list 的场景，交由后续 set_request_params 重建目标结构
            return {}

        if path and len(path) > 0:
            p = path[0]
            # 递归过滤目标路径
            filtered = ParamUtil.filter_post_body_fields(body.get(p, {}), fields, path[1:])
            # 保留同级其它字段
            result = {}
            for k, v in body.items():
                if k == p:
                    result[k] = filtered
                else:
                    result[k] = v
            return result
        else:
            result = {}
            for k, v in body.items():
                if k in fields:
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

    @staticmethod
    def get_api_path(apis_dict: Dict[str, Any], api_key: str) -> str:
        """
        获取API路径
        
        参数:
            apis_dict (dict): API路径配置字典
            api_key (str): API的名称键值，如"物料主数据定义表-分页数据服务"
            
        返回:
            str: 对应的API路径，如"/api/trantor/service/engine/execute/ERP_GEN$gen_mat_md_PAGING_DATA_SERVICE"
                 如果找不到对应的API，则返回None
        """
        return apis_dict.get(api_key, {}).get("path")
    
    @staticmethod
    def get_api_params(api_params_dict: Dict[str, Any], api_path: str, with_query_params: Optional[str] = None) -> tuple:
        """
        获取API请求参数和完整URL
        
        参数:
            api_params_dict (dict): API参数配置字典
            api_path (str): API路径，如"/api/trantor/service/engine/execute/ERP_GEN$gen_mat_md_PAGING_DATA_SERVICE"
            with_query_params (str, optional): 查询参数字符串，如"param1=value1&param2=value2"
        
        返回:
            tuple: (params, url)
                params (dict): 对应API的请求参数模板，如{"params": {"request": {...}}}
                url (str): 完整的API URL，如果提供了with_query_params，则会附加到路径后
                           例如: "/api/..." 或 "/api/...?param1=value1"
        """
        # 准备URL
        url = api_path
        if with_query_params:
            url = f"{api_path}?{with_query_params}"
        
        # 获取请求参数 (从api_params字典中获取对应api_path的参数模板)
        params = api_params_dict.get(api_path, {})
        return params, url
    
    @staticmethod
    def set_request_param(params: Dict[str, Any], key: str, value: Any) -> Dict[str, Any]:
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
    
    @staticmethod
    def set_request_params(params: Dict[str, Any], param_dict: Dict[str, Any], path: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        批量设置请求参数，简化嵌套访问
        
        参数:
            params: 请求参数字典
            param_dict: 要设置的参数字典 {key: value, ...}
            path: 参数路径，默认为 ["params", "request"]，支持自定义路径如 ["params", "reuqest"]
        
        返回:
            更新后的参数字典
        """
        if path is None:
            path = ["params", "request"]

        # 顶层直写：例如 standard_api_call(param_path=[]) 的场景
        if len(path) == 0:
            if isinstance(param_dict, dict):
                params.update(param_dict)
                return params
            if isinstance(param_dict, list):
                raise TypeError("path=[] 时 param_dict 必须为 dict，不能为 list")
            raise TypeError(f"param_dict 必须是 dict 或 list，当前类型: {type(param_dict).__name__}")
        
        # 确保路径存在
        current = params
        for p in path[:-1]:
            if p not in current or not isinstance(current[p], dict):
                current[p] = {}
            current = current[p]

        last_key = path[-1]
        if last_key not in current or not isinstance(current[last_key], dict):
            current[last_key] = {}

        # 兼容批量接口参数直接为 list 的模板
        if isinstance(param_dict, list):
            current[last_key] = param_dict
            return params

        if not isinstance(param_dict, dict):
            raise TypeError(f"param_dict 必须是 dict 或 list，当前类型: {type(param_dict).__name__}")

        # dataList 语义兼容：大量批量接口模板 request 实际为 list
        if set(param_dict.keys()) == {"dataList"} and isinstance(param_dict.get("dataList"), list):
            current[last_key] = param_dict["dataList"]
            return params

        # 设置参数值
        for key, value in param_dict.items():
            # 容错：上游把整对象当作 id 传入时，自动提取 id
            if isinstance(value, dict) and key.lower().endswith("id") and "id" in value:
                value = value.get("id")
            if isinstance(value, dict) and isinstance(value.get("pageable"), dict):
                ParamUtil._sanitize_pageable(value["pageable"])
            if isinstance(value, list) and (key.lower() == "ids" or key.lower().endswith("ids")):
                value = [item.get("id") if isinstance(item, dict) and "id" in item else item for item in value]
            current[last_key][key] = value
        ParamUtil.sanitize_payload(params)
        return params
    
    @staticmethod
    def extract_id(result: dict, path: str = "data.data.id"):
        """
        从API响应中提取ID
        
        参数:
            result: API响应结果
            path: ID在响应中的路径，默认为 "data.data.id"
            
        返回:
            提取到的ID值
        """
        data = result
        for key in path.split("."):
            data = data.get(key, {})
        return data
    






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
    
