import requests
from utils.LogUtil import Loggers

class HttpUtil:
    """HTTP 工具类，提供基本的 HTTP 请求功能"""
    
    def __init__(self):
        """初始化 HTTP 工具类"""
        self.logger = Loggers()
        self.session = requests.Session()
    
    def get(self, url, params=None, headers=None, **kwargs):
        """发送 GET 请求
        
        Args:
            url: 请求 URL
            params: 请求参数
            headers: 请求头
            **kwargs: 其他参数
            
        Returns:
            响应对象
        """
        self.logger.info(f"发送 GET 请求: {url}")
        self.logger.debug(f"请求参数: {params}")
        self.logger.debug(f"请求头: {headers}")
        
        response = self.session.get(url, params=params, headers=headers, **kwargs)
        
        self.logger.info(f"响应状态码: {response.status_code}")
        self.logger.debug(f"响应内容: {response.text}")
        
        return response
    
    def post(self, url, data=None, json=None, params=None, headers=None, **kwargs):
        """发送 POST 请求
        
        Args:
            url: 请求 URL
            data: 请求数据
            json: JSON 格式的请求数据
            params: 请求参数
            headers: 请求头
            **kwargs: 其他参数
            
        Returns:
            响应对象
        """
        self.logger.info(f"发送 POST 请求: {url}")
        self.logger.debug(f"请求参数: {params}")
        self.logger.debug(f"请求数据: {data}")
        self.logger.debug(f"JSON 数据: {json}")
        self.logger.debug(f"请求头: {headers}")
        
        response = self.session.post(url, data=data, json=json, params=params, headers=headers, **kwargs)
        
        self.logger.info(f"响应状态码: {response.status_code}")
        self.logger.debug(f"响应内容: {response.text}")
        
        return response
    
    def put(self, url, data=None, json=None, params=None, headers=None, **kwargs):
        """发送 PUT 请求
        
        Args:
            url: 请求 URL
            data: 请求数据
            json: JSON 格式的请求数据
            params: 请求参数
            headers: 请求头
            **kwargs: 其他参数
            
        Returns:
            响应对象
        """
        self.logger.info(f"发送 PUT 请求: {url}")
        self.logger.debug(f"请求参数: {params}")
        self.logger.debug(f"请求数据: {data}")
        self.logger.debug(f"JSON 数据: {json}")
        self.logger.debug(f"请求头: {headers}")
        
        response = self.session.put(url, data=data, json=json, params=params, headers=headers, **kwargs)
        
        self.logger.info(f"响应状态码: {response.status_code}")
        self.logger.debug(f"响应内容: {response.text}")
        
        return response
    
    def delete(self, url, params=None, headers=None, **kwargs):
        """发送 DELETE 请求
        
        Args:
            url: 请求 URL
            params: 请求参数
            headers: 请求头
            **kwargs: 其他参数
            
        Returns:
            响应对象
        """
        self.logger.info(f"发送 DELETE 请求: {url}")
        self.logger.debug(f"请求参数: {params}")
        self.logger.debug(f"请求头: {headers}")
        
        response = self.session.delete(url, params=params, headers=headers, **kwargs)
        
        self.logger.info(f"响应状态码: {response.status_code}")
        self.logger.debug(f"响应内容: {response.text}")
        
        return response 