import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from typing import Optional, Dict, Any, Union, Callable
from urllib.parse import urljoin
import json
import os
import sys
from datetime import datetime
from pathlib import Path


# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from utils.exception_util import safe_api_call, APIException
from utils.log_util import Loggers
from utils.response_util import DecimalEncoder
from decimal import Decimal

class HttpUtil:
    """HTTP 工具类，提供增强的 HTTP 请求功能
    
    主要功能：
    1. 支持 GET、POST、PUT、DELETE 等基本请求方法
    2. 支持请求重试和超时设置
    3. 支持请求/响应拦截器
    4. 支持会话管理
    5. 支持响应状态码检查
    6. 支持请求/响应数据的序列化处理
    7. 支持默认登录和自定义请求头
    """
    
    def __init__(
        self,
        url: str,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        """初始化HTTP工具类
        
        Args:
            url: API根路径
            session: 可选的现有会话对象
            headers: 可选的请求头
        """
        self.url = url
        self.session = session or requests.Session()
        if headers:
            self.session.headers.update(headers)

    def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """发送GET请求"""
        return self.request(url, "GET", **kwargs)

    def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """发送POST请求"""
        return self.request(url, "POST", **kwargs)

    def put(self, url: str, **kwargs) -> Dict[str, Any]:
        """发送PUT请求"""
        return self.request(url, "PUT", **kwargs)

    def delete(self, url: str, **kwargs) -> Dict[str, Any]:
        """发送DELETE请求"""
        return self.request(url, "DELETE", **kwargs)

    def request(self, url: str, method: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求
        
        Args:
            url: 请求URL（相对路径，不需要包含域名）
            method: 请求方法
            **kwargs: 请求参数
            
        Returns:
            Dict[str, Any]: 响应数据
        """
        # 构建完整URL
        full_url = urljoin(self.url, url.lstrip('/'))
        
        # 记录请求信息
        self.request_log(full_url, method, **kwargs)
        
        # 从kwargs中移除description参数，因为requests不支持这个参数
        description = kwargs.pop('description', None)
        if description:
            Loggers.info(f"请求描述: {description}", depth=4)
        
        # 转换kwargs中的Decimal类型为float（requests库不支持Decimal类型）
        def convert_decimal_to_float(obj):
            """递归转换字典和列表中的Decimal类型为float"""
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_decimal_to_float(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_decimal_to_float(item) for item in obj]
            return obj
        
        # 转换json参数中的Decimal类型
        if 'json' in kwargs and kwargs['json'] is not None:
            kwargs['json'] = convert_decimal_to_float(kwargs['json'])
        # 转换data参数中的Decimal类型（如果data是字典或列表）
        if 'data' in kwargs and kwargs['data'] is not None and isinstance(kwargs['data'], (dict, list)):
            kwargs['data'] = convert_decimal_to_float(kwargs['data'])
        
        # 发送请求
        try:
            response = self.session.request(method, full_url, **kwargs)
            # 记录响应信息
            Loggers.info(f"响应状态码: {response.status_code}", depth=4)
            
            try:
                response_json = response.json()
                Loggers.info(f"响应内容: {json.dumps(response_json, ensure_ascii=False, indent=2, cls=DecimalEncoder)}", depth=4)
            except ValueError:
                Loggers.info(f"响应内容: {response.text}", depth=4)
            
            response.raise_for_status()  # 抛出HTTP错误
            return response.json()
        except requests.exceptions.RequestException as e:
            Loggers.error(f"请求失败: {str(e)}", depth=4)
            if description:
                Loggers.error(f"失败的请求: {description}", depth=4)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    Loggers.error(f"错误详情: {json.dumps(error_detail, ensure_ascii=False, indent=2, cls=DecimalEncoder)}", depth=4)
                except ValueError:
                    Loggers.error(f"错误响应: {e.response.text}", depth=4)
            raise

    def request_log(self, full_url, method, **kwargs):
        """记录请求信息
        
        Args:
            full_url: 完整的请求URL
            method: 请求方法
            **kwargs: 请求参数
        """
        data = dict(**kwargs).get("data")
        json_data = dict(**kwargs).get("json")
        params = dict(**kwargs).get("params")
        headers = dict(**kwargs).get("headers")
        
        # 使用depth=4来跳过整个调用链，直接显示测试用例位置
        Loggers.info("接口请求的地址>>>{}", full_url, depth=4)
        Loggers.info("接口请求的方法>>>{}", method, depth=4)
        
        if data is not None:
            Loggers.info("接口请求的data参数>>>\n{}", json.dumps(data, ensure_ascii=False, indent=2, cls=DecimalEncoder), depth=4)
        if json_data is not None:
            Loggers.info("接口请求的json参数>>>\n{}", json.dumps(json_data, ensure_ascii=False, indent=2, cls=DecimalEncoder), depth=4)
        if params is not None:
            Loggers.info("接口请求的params参数>>>\n{}", json.dumps(params, ensure_ascii=False, indent=2, cls=DecimalEncoder), depth=4)
        if headers is not None:
            Loggers.info("接口请求的headers参数>>>\n{}", json.dumps(headers, ensure_ascii=False, indent=2, cls=DecimalEncoder), depth=4)

