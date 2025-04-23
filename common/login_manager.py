import os
import sys
import requests
from urllib.parse import quote
from loguru import logger

# 动态获取项目根目录（兼容不同调用方式）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from common.config_manager import ConfigManager
from utils.MockUtil import MockData

class LoginManager:
    """登录管理类"""
    
    def __init__(self):
        """初始化登录管理器"""
        logger.info("初始化登录管理器")
        self.session = requests.Session()
        self.config = ConfigManager()
        self.iam_url = self.config.get_iam_url()
        self.api_url = self.config.get_base_url()
        logger.info(f"IAM URL: {self.iam_url}")
        logger.info(f"API URL: {self.api_url}")
        
        # 基础headers配置
        self.base_headers = {
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
        
        # IAM登录headers
        self.iam_headers = {
            **self.base_headers,
            'Origin': self.iam_url,
            'Referer': f"{self.iam_url}/TERP_PORTAL-TERP-tpf_umwrhzbg/login"
        }
        
        # API请求headers
        self.api_headers = {
            **self.base_headers,
            'Origin': self.api_url,
            'Referer': f"{self.api_url}/TERP_PORTAL-TERP/TERP_PORTAL/TERP_PORTAL$4f94e448-6fcd-497b-8357-66a90c82a3f9/page"
        }
        
        # 设置默认headers
        self.session.headers.update(self.base_headers)
        logger.info("登录管理器初始化完成")
        
    def login(self, account: str = None, password: str = None) -> requests.Session:
        """
        登录系统
        
        参数:
            account: 账号，如果未传则使用配置文件中的默认账号
            password: 密码，如果未传则使用配置文件中的默认密码
            
        返回:
            登录后的session对象
        """
        logger.info("开始登录流程")
        # 如果未传账号密码，使用配置文件中的默认值
        if account is None or password is None:
            logger.info("使用配置文件中的默认账号密码")
            auth_config = self.config.get_auth_config()
            account = account or auth_config["username"]
            password = password or auth_config["password"]
            logger.info(f"使用账号: {account}")
        else:
            logger.info(f"使用传入的账号: {account}")
        
        # 1. 登录 IAM
        login_url = f"{self.iam_url}/iam/api/v1/user/login/account"
        login_data = {
            "account": account,
            "password": password
        }
        logger.info(f"登录URL: {login_url}")
        
        try:
            # 使用IAM登录headers
            self.session.headers.update(self.iam_headers)
            response = self.session.post(login_url, json=login_data)
            logger.info(f"登录响应状态码: {response.status_code}")

            
            if response.status_code != 200:
                logger.error(f"登录失败: {response.status_code} - {response.text}")
                raise Exception(f"Login failed: {response.text}")
                
            # 2. 获取重定向 URL
            redirect_url = f"{self.api_url}/TERP_PORTAL-TERP-tpf_umwrhzbg/login"
            logger.info(f"重定向URL: {redirect_url}")
            
            # 3. 访问重定向 URL 以切换到正确的应用系统
            # 使用API请求headers
            self.session.headers.update(self.api_headers)
            response = self.session.get(redirect_url, allow_redirects=True)
            
            if response.status_code != 200:
                logger.error(f"重定向失败: {response.status_code} - {response.text}")
                raise Exception(f"Follow redirect URL failed: {response.text}")
                
            # 4. 获取当前用户信息作为登录成功的标志
            user_info = self.get_current_user()
            logger.info(f"登录成功，用户信息: {user_info}")
            
            return self.session
            
        except Exception as e:
            logger.error(f"登录过程发生错误: {str(e)}")
            raise
        
    def get_current_user(self) -> dict:
        """
        获取当前用户信息
        
        返回:
            当前用户信息
        """
        url = f"{self.api_url}/api/trantor/portal/user/current"
        logger.info(f"获取用户信息URL: {url}")
        
        try:
            # 使用API请求headers
            self.session.headers.update(self.api_headers)
            response = self.session.get(url)
            logger.info(f"获取用户信息响应状态码: {response.status_code}")

            
            if response.status_code != 200:
                logger.error(f"获取用户信息失败: {response.status_code} - {response.text}")
                raise Exception(f"Get current user failed: {response.text}")
                
            return response.json()
            
        except Exception as e:
            logger.error(f"获取用户信息过程发生错误: {str(e)}")
            raise
        
    def get_session(self) -> requests.Session:
        """
        获取会话对象
        
        返回:
            会话对象
        """
        return self.session 
    
    
if __name__ == "__main__":
    logger.info("开始执行登录测试")
    login_manager = LoginManager()
    # 使用默认账号密码登录
    session = login_manager.login()
    
    # 使用指定账号密码登录
    # account, password = "your_account", "your_password"
    # session = login_manager.login(account=account, password=password)