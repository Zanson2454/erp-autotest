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
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.exception_util import safe_api_call, APIException
from testcases.comm.login import LoginManager

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
        api_root_url: str,
        use_default_login: bool = True
    ):
        self.api_root_url = api_root_url
        self.session = requests.Session()
    def get(self, url, **kwargs):
        return self.request(url, "GET", **kwargs)

    def post(self, url, **kwargs):
        return self.request(url, "POST", **kwargs)

    def put(self, url, **kwargs):
        return self.request(url, "PUT", **kwargs)

    def delete(self, url, **kwargs):
        return self.request(url, "DELETE", **kwargs)

    def request(self, url, method, **kwargs):
        self.request_log(url, method, **kwargs)
        if method == "GET":
            return self.session.get(self.api_root_url + url, **kwargs)
        if method == "POST":
            return self.session.post(self.api_root_url + url, **kwargs)
        if method == "PUT":
            return self.session.put(self.api_root_url + url, **kwargs)
        if method == "DELETE":
            return self.session.delete(self.api_root_url + url, **kwargs)

    def request_log(self, url, method, **kwargs):
        data = dict(**kwargs).get("data")
        json_data = dict(**kwargs).get("json")
        params = dict(**kwargs).get("params")
        headers = dict(**kwargs).get("headers")

        self.log.info("接口请求的地址>>>{}".format(self.api_root_url + url))
        self.log.info("接口请求的方法>>>{}".format(method))
        if data is not None:
            self.log.info("接口请求的data参数>>>\n{}".format(json.dumps(data, ensure_ascii=False, indent=2)))
        if json_data is not None:
            self.log.info("接口请求的json参数>>>\n{}".format(json.dumps(json_data, ensure_ascii=False, indent=2)))
        if params is not None:
            self.log.info("接口请求的params参数>>>\n{}".format(json.dumps(params, ensure_ascii=False, indent=2)))
        if headers is not None:
            self.log.info("接口请求的headers参数>>>\n{}".format(json.dumps(headers, ensure_ascii=False, indent=2)))

