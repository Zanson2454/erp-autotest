import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from typing import Optional, Dict, Any, Union, Callable
from urllib.parse import urljoin
import json
from datetime import datetime
from utils.log_util import Loggers
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
    
    使用示例：
    ```python
    # 创建 HTTP 工具实例
    http = HttpUtil(base_url="http://api.example.com")
    
    # 发送 GET 请求
    response = http.get("/users", params={"page": 1})
    
    # 发送 POST 请求
    response = http.post("/users", json={"name": "John"})
    ```
    """
    
    def __init__(
        self,
        base_url: str = "",
        timeout: int = 30,
        max_retries: int = 3,
        retry_backoff: float = 0.5,
        retry_status_codes: Optional[list] = None,
        default_headers: Optional[Dict[str, str]] = None
    ):
        """初始化 HTTP 工具类
        
        Args:
            base_url: 基础 URL
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            retry_backoff: 重试间隔时间（秒）
            retry_status_codes: 需要重试的状态码列表
            default_headers: 默认请求头
        """
        self.logger = Loggers()
        self.base_url = base_url
        self.timeout = timeout
        self.default_headers = default_headers or {}
        
        # 配置重试策略
        retry_status_codes = retry_status_codes or [500, 502, 503, 504]
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=retry_backoff,
            status_forcelist=retry_status_codes
        )
        
        # 配置会话
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 请求/响应拦截器
        self.request_interceptors: list[Callable] = []
        self.response_interceptors: list[Callable] = []
    
    def add_request_interceptor(self, interceptor: Callable) -> None:
        """添加请求拦截器
        
        Args:
            interceptor: 拦截器函数，接收 (method, url, **kwargs) 参数
        """
        self.request_interceptors.append(interceptor)
    
    def add_response_interceptor(self, interceptor: Callable) -> None:
        """添加响应拦截器
        
        Args:
            interceptor: 拦截器函数，接收 (response) 参数
        """
        self.response_interceptors.append(interceptor)
    
    def _build_url(self, url: str) -> str:
        """构建完整 URL
        
        Args:
            url: 相对或绝对 URL
            
        Returns:
            str: 完整 URL
        """
        if url.startswith(("http://", "https://")):
            return url
        return urljoin(self.base_url, url)
    
    def _prepare_request(self, method: str, url: str, **kwargs) -> tuple[str, dict]:
        """准备请求参数
        
        Args:
            method: 请求方法
            url: 请求 URL
            **kwargs: 请求参数
            
        Returns:
            tuple: (完整 URL, 请求参数)
        """
        # 构建完整 URL
        full_url = self._build_url(url)
        
        # 合并请求头
        headers = self.default_headers.copy()
        headers.update(kwargs.pop("headers", {}))
        kwargs["headers"] = headers
        
        # 设置超时
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout
        
        # 执行请求拦截器
        for interceptor in self.request_interceptors:
            interceptor(method, full_url, **kwargs)
        
        return full_url, kwargs
    
    def _handle_response(self, response: requests.Response) -> requests.Response:
        """处理响应
        
        Args:
            response: 响应对象
            
        Returns:
            Response: 处理后的响应对象
        """
        # 执行响应拦截器
        for interceptor in self.response_interceptors:
            interceptor(response)
        
        # 检查响应状态码
        if not response.ok:
            error_msg = f"请求失败: {response.status_code} - {response.reason}"
            try:
                error_detail = response.json()
                error_msg += f"\n错误详情: {json.dumps(error_detail, ensure_ascii=False)}"
            except:
                error_msg += f"\n响应内容: {response.text}"
            raise APIException(error_msg)
        
        return response
    
    @safe_api_call(error_message="GET请求失败")
    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """发送 GET 请求
        
        Args:
            url: 请求 URL
            params: 请求参数
            headers: 请求头
            **kwargs: 其他参数
            
        Returns:
            Response: 响应对象
            
        Raises:
            APIException: 请求失败时抛出异常
        """
        self.logger.info(f"发送 GET 请求: {url}")
        self.logger.debug(f"请求参数: {params}")
        self.logger.debug(f"请求头: {headers}")
        
        full_url, kwargs = self._prepare_request("GET", url, params=params, headers=headers, **kwargs)
        response = self.session.get(full_url, **kwargs)
        
        self.logger.info(f"响应状态码: {response.status_code}")
        self.logger.debug(f"响应内容: {response.text}")
        
        return self._handle_response(response)
    
    @safe_api_call(error_message="POST请求失败")
    def post(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """发送 POST 请求
        
        Args:
            url: 请求 URL
            data: 请求数据
            json: JSON 格式的请求数据
            params: 请求参数
            headers: 请求头
            **kwargs: 其他参数
            
        Returns:
            Response: 响应对象
            
        Raises:
            APIException: 请求失败时抛出异常
        """
        self.logger.info(f"发送 POST 请求: {url}")
        self.logger.debug(f"请求参数: {params}")
        self.logger.debug(f"请求数据: {data}")
        self.logger.debug(f"JSON 数据: {json}")
        self.logger.debug(f"请求头: {headers}")
        
        full_url, kwargs = self._prepare_request("POST", url, data=data, json=json, params=params, headers=headers, **kwargs)
        response = self.session.post(full_url, **kwargs)
        
        self.logger.info(f"响应状态码: {response.status_code}")
        self.logger.debug(f"响应内容: {response.text}")
        
        return self._handle_response(response)
    
    @safe_api_call(error_message="PUT请求失败")
    def put(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """发送 PUT 请求
        
        Args:
            url: 请求 URL
            data: 请求数据
            json: JSON 格式的请求数据
            params: 请求参数
            headers: 请求头
            **kwargs: 其他参数
            
        Returns:
            Response: 响应对象
            
        Raises:
            APIException: 请求失败时抛出异常
        """
        self.logger.info(f"发送 PUT 请求: {url}")
        self.logger.debug(f"请求参数: {params}")
        self.logger.debug(f"请求数据: {data}")
        self.logger.debug(f"JSON 数据: {json}")
        self.logger.debug(f"请求头: {headers}")
        
        full_url, kwargs = self._prepare_request("PUT", url, data=data, json=json, params=params, headers=headers, **kwargs)
        response = self.session.put(full_url, **kwargs)
        
        self.logger.info(f"响应状态码: {response.status_code}")
        self.logger.debug(f"响应内容: {response.text}")
        
        return self._handle_response(response)
    
    @safe_api_call(error_message="DELETE请求失败")
    def delete(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """发送 DELETE 请求
        
        Args:
            url: 请求 URL
            params: 请求参数
            headers: 请求头
            **kwargs: 其他参数
            
        Returns:
            Response: 响应对象
            
        Raises:
            APIException: 请求失败时抛出异常
        """
        self.logger.info(f"发送 DELETE 请求: {url}")
        self.logger.debug(f"请求参数: {params}")
        self.logger.debug(f"请求头: {headers}")
        
        full_url, kwargs = self._prepare_request("DELETE", url, params=params, headers=headers, **kwargs)
        response = self.session.delete(full_url, **kwargs)
        
        self.logger.info(f"响应状态码: {response.status_code}")
        self.logger.debug(f"响应内容: {response.text}")
        
        return self._handle_response(response)
    
    def close(self) -> None:
        """关闭会话"""
        self.session.close() 