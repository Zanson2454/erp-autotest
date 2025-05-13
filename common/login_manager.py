"""
登录管理模块

该模块提供了系统登录相关的功能，包括：
1. 用户认证和登录
2. 会话管理
3. 用户信息获取

主要组件：
- LoginManager: 登录管理主类
- AuthConfig: 认证配置管理类
- HeadersManager: 请求头管理类
- LoginError: 登录相关异常类

使用示例：
    login_manager = LoginManager()
    session = login_manager.login()  # 使用默认账号密码登录
    # 或
    session = login_manager.login(account="your_account", password="your_password")
"""

import os
import sys
import requests
from urllib.parse import quote
from loguru import logger
from typing import Optional, Dict, Any

# 动态获取项目根目录（兼容不同调用方式）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils.yaml_util import YamlUtil
from utils.mock_util import MockData

class LoginError(Exception):
    """登录相关异常类
    
    用于处理登录过程中可能出现的各种错误，包括：
    - 认证失败
    - 网络错误
    - 服务器错误
    - 会话过期
    """
    pass

class AuthConfig:
    """认证配置管理类
    
    负责管理和提供认证相关的配置信息，包括：
    - IAM URL
    - API URL
    - 认证信息（用户名/密码）
    
    Attributes:
        config (YamlUtil): 配置工具实例
        iam_url (str): IAM服务地址
        api_url (str): API服务地址
        auth_config (dict): 认证配置信息
    """
    
    def __init__(self, config: YamlUtil):
        """
        初始化认证配置
        
        Args:
            config: 配置工具实例，用于读取配置信息
        """
        self.config = config 
        self.iam_url = config.get_iam_url()  # 获取 IAM 服务地址
        self.api_url = config.get_base_url()  # 获取 API 服务地址
        self.auth_config = config.get_auth_config()  # 获取认证配置
    
    def get_default_credentials(self) -> Dict[str, str]: 
        """
        获取默认认证信息
        
        Returns:
            Dict[str, str]: 包含用户名和密码的字典
        """
        return {
            "username": self.auth_config["username"],
            "password": self.auth_config["password"]
        }

class HeadersManager:
    """请求头管理类
    
    负责管理和提供不同场景下的HTTP请求头，包括：
    - 基础请求头
    - IAM登录请求头
    - API请求头
    
    Attributes:
        iam_url (str): IAM服务地址
        api_url (str): API服务地址
        base_headers (dict): 基础请求头
        iam_headers (dict): IAM登录请求头
        api_headers (dict): API请求头
    """
    
    def __init__(self, iam_url: str, api_url: str):
        """
        初始化请求头管理器
        
        Args:
            iam_url: IAM服务地址
            api_url: API服务地址
        """
        self.iam_url = iam_url
        self.api_url = api_url
        self.base_headers = self._get_base_headers()  # 获取基础请求头
        self.iam_headers = self._get_iam_headers()  # 获取 IAM 登录请求头
        self.api_headers = self._get_api_headers()  # 获取 API 请求头
    
    def _get_base_headers(self) -> Dict[str, str]:
        """
        获取基础请求头
        
        Returns:
            Dict[str, str]: 基础请求头字典
        """
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': MockData().get_mock_user_agent(),
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty'
        }
    
    def _get_iam_headers(self) -> Dict[str, str]:
        """
        获取IAM登录请求头
        
        Returns:
            Dict[str, str]: IAM登录请求头字典
        """
        return {
            **self.base_headers,
            'Origin': self.iam_url,
            'Referer': f"{self.iam_url}/TERP_PORTAL-TERP-tpf_umwrhzbg/login"
        }
    
    def _get_api_headers(self) -> Dict[str, str]:
        """
        获取API请求头
        
        Returns:
            Dict[str, str]: API请求头字典
        """
        return {
            **self.base_headers,
            'Origin': self.api_url,
            'Referer': f"{self.api_url}/TERP_PORTAL-TERP/TERP_PORTAL/TERP_PORTAL$4f94e448-6fcd-497b-8357-66a90c82a3f9/page"
        }

class LoginManager:
    """登录管理类
    
    负责处理系统登录相关的所有操作，包括：
    - 用户认证
    - 会话管理
    - 用户信息获取
    
    Attributes:
        session (requests.Session): HTTP会话对象
        config (YamlUtil): 配置工具实例
        auth_config (AuthConfig): 认证配置管理器
        headers_manager (HeadersManager): 请求头管理器
    """
    
    def __init__(self):
        """
        初始化登录管理器
        
        初始化过程包括：
        1. 创建HTTP会话
        2. 加载配置
        3. 初始化认证配置
        4. 初始化请求头管理器
        """
        logger.info("初始化登录管理器")
        self.session = requests.Session() 
        self.config = YamlUtil() # 加载配置
        self.auth_config = AuthConfig(self.config) # 初始化认证配置
        self.headers_manager = HeadersManager(
            self.config.get_iam_url(), 
            self.config.get_base_url()
        )
        self.session.headers.update(self.headers_manager.base_headers)  # 更新请求头    
        logger.info("登录管理器初始化完成")
    
    def login(self, account: Optional[str] = None, password: Optional[str] = None) -> requests.Session:
        """
        执行登录流程
        
        登录流程包括：
        1. 获取认证信息（使用默认或指定的账号密码）
        2. 执行IAM登录
        3. 处理重定向
        4. 获取用户信息
        
        Args:
            account: 账号，如果未传则使用配置文件中的默认账号
            password: 密码，如果未传则使用配置文件中的默认密码
            
        Returns:
            requests.Session: 登录成功后的会话对象
            
        Raises:
            LoginError: 登录失败时抛出，包含详细的错误信息
        """
        logger.info("开始登录流程")
        credentials = self._get_credentials(account, password)
        
        try:
            self._login_iam(credentials)
            self._handle_redirect()
            user_info = self.get_current_user()
            logger.info(f"登录成功，用户信息: {user_info}")
            return self.session
        except Exception as e:
            logger.error(f"登录过程发生错误: {str(e)}")
            raise LoginError(f"Login failed: {str(e)}")
    
    def _get_credentials(self, account: Optional[str], password: Optional[str]) -> Dict[str, str]:
        """
        获取认证信息
        
        如果未提供账号密码，则使用配置文件中的默认值
        
        Args:
            account: 账号
            password: 密码
            
        Returns:
            Dict[str, str]: 包含账号和密码的字典
        """
        if account is None or password is None:
            logger.info("使用配置文件中的默认账号密码")
            credentials = self.auth_config.get_default_credentials()
            account = account or credentials["username"]
            password = password or credentials["password"]
            logger.info(f"使用账号: {account}")
        else:
            logger.info(f"使用传入的账号: {account}")
        return {"account": account, "password": password}
    
    def _login_iam(self, credentials: Dict[str, str]) -> None:
        """
        执行IAM登录
        
        Args:
            credentials: 包含账号和密码的字典
            
        Raises:
            LoginError: IAM登录失败时抛出
        """
        login_url = f"{self.auth_config.iam_url}/iam/api/v1/user/login/account"
        self.session.headers.update(self.headers_manager.iam_headers)
        response = self.session.post(login_url, json=credentials)
        logger.info(f"登录响应状态码: {response.status_code}")
        
        if response.status_code != 200:
            raise LoginError(f"Login failed: {response.text}")
    
    def _handle_redirect(self) -> None:
        """
        处理登录后的重定向
        
        重定向过程包括：
        1. 获取重定向URL
        2. 更新请求头
        3. 执行重定向请求
        
        Raises:
            LoginError: 重定向失败时抛出
        """
        redirect_url = f"{self.auth_config.api_url}/TERP_PORTAL-TERP-tpf_umwrhzbg/login"
        logger.info(f"重定向URL: {redirect_url}")
        
        self.session.headers.update(self.headers_manager.api_headers)
        response = self.session.get(redirect_url, allow_redirects=True)
        
        if response.status_code != 200:
            raise LoginError(f"Follow redirect URL failed: {response.text}")
    
    def get_current_user(self) -> Dict[str, Any]:
        """
        获取当前登录用户的信息
        
        获取的信息包括：
        - 用户ID
        - 用户名
        - 用户角色
        - 其他用户相关信息
        
        Returns:
            Dict[str, Any]: 用户信息字典
            
        Raises:
            LoginError: 获取用户信息失败时抛出
        """
        url = f"{self.auth_config.api_url}/api/trantor/portal/user/current"
        logger.info(f"获取用户信息URL: {url}")
        
        try:
            self.session.headers.update(self.headers_manager.api_headers)
            response = self.session.get(url)
            logger.info(f"获取用户信息响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                raise LoginError(f"Get current user failed: {response.text}")
            
            return response.json()
        except Exception as e:
            logger.error(f"获取用户信息过程发生错误: {str(e)}")
            raise LoginError(f"Get current user failed: {str(e)}")
    
    def get_session(self) -> requests.Session:
        """
        获取当前会话对象
        
        Returns:
            requests.Session: 当前HTTP会话对象
        """
        return self.session

if __name__ == "__main__":
    logger.info("开始执行登录测试")
    login_manager = LoginManager()
    session = login_manager.login()