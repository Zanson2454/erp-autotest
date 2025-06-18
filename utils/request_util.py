import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from typing import Optional, Dict, Any, Union, Callable
from urllib.parse import urljoin
import json
import os
import sys
from datetime import datetime
from loguru import logger
from pathlib import Path


# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent
logger.info(f"project_root: {project_root}")
sys.path.insert(0, str(project_root))

from utils.exception_util import safe_api_call, APIException

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
            logger.info(f"请求描述: {description}")
        
        # 发送请求
        try:
            response = self.session.request(method, full_url, **kwargs)
            # 记录响应信息
            logger.info(f"响应状态码: {response.status_code}")
            
            try:
                response_json = response.json()
                logger.info(f"响应内容: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
            except ValueError:
                logger.info(f"响应内容: {response.text}")
            
            response.raise_for_status()  # 抛出HTTP错误
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {str(e)}")
            if description:
                logger.error(f"失败的请求: {description}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    logger.error(f"错误详情: {json.dumps(error_detail, ensure_ascii=False, indent=2)}")
                except ValueError:
                    logger.error(f"错误响应: {e.response.text}")
            raise

    def request_log(self, full_url, method, **kwargs):
        data = dict(**kwargs).get("data")
        json_data = dict(**kwargs).get("json")
        params = dict(**kwargs).get("params")
        headers = dict(**kwargs).get("headers")
        logger.info("接口请求的地址>>>{}", full_url, stacklevel=3)
        logger.info("接口请求的方法>>>{}", method, stacklevel=3)
        if data is not None:
            logger.info("接口请求的data参数>>>\n{}", json.dumps(data, ensure_ascii=False, indent=2), stacklevel=3)
        if json_data is not None:
            logger.info("接口请求的json参数>>>\n{}", json.dumps(json_data, ensure_ascii=False, indent=2), stacklevel=3)
        if params is not None:
            logger.info("接口请求的params参数>>>\n{}", json.dumps(params, ensure_ascii=False, indent=2), stacklevel=3)
        if headers is not None:
            logger.info("接口请求的headers参数>>>\n{}", json.dumps(headers, ensure_ascii=False, indent=2), stacklevel=3)

