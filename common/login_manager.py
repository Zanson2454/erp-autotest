import os
import sys
import requests
from urllib.parse import quote
from loguru import logger

# 动态获取项目根目录（兼容不同调用方式）
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(BASE_DIR)

from config.config import Config

class LoginManager:
    """登录管理类"""
    
    def __init__(self):
        """初始化登录管理器"""
        self.session = requests.Session()
        self.iam_base_url = Config.get_iam_base_url()
        self.api_base_url = Config.get_api_base_url()
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
            'Origin': self.iam_base_url,
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'referer': self.iam_base_url + "/TERP_PORTAL-TERP-tpf_umwrhzbg/login?redirectUrl=" + self.api_base_url
        }
        self.session.headers.update(self.headers)
        
    def login(self, account: str = None, password: str = None) -> requests.Session:
        """
        登录系统
        
        参数:
            account: 账号，如果未传则使用配置文件中的默认账号
            password: 密码，如果未传则使用配置文件中的默认密码
            
        返回:
            登录后的session对象
        """
        # 如果未传账号密码，使用配置文件中的默认值
        if account is None or password is None:
            default_account, default_password = Config.get_auth_info()
            account = account or default_account
            password = password or default_password
            logger.debug(f"使用默认账号: {account}")
        
        # 1. 登录 IAM
        url = f"{self.iam_base_url}/iam/api/v1/user/login/account"
        data = {
            "account": account,
            "password": password
        }
        
        response = self.session.post(url, json=data)
        if response.status_code != 200:
            raise Exception(f"Login failed: {response.text}")
            
        # 2. 获取重定向 URL
        redirect_url = f"{self.api_base_url}/TERP_PORTAL-TERP-tpf_umwrhzbg/login"
        
        # 3. 访问重定向 URL 以切换到正确的应用系统
        response = self.session.get(redirect_url, allow_redirects=True)
        if response.status_code != 200:
            raise Exception(f"Follow redirect URL failed: {response.text}")
            
        # 4. 获取当前用户信息作为登录成功的标志
        user_info = self.get_current_user()
        logger.debug(f"登录成功")
        
        return self.session
        
    def get_current_user(self) -> dict:
        """
        获取当前用户信息
        
        返回:
            当前用户信息
        """
        url = f"{self.api_base_url}/api/trantor/portal/user/current"
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Referer': f"{self.api_base_url}/TERP_PORTAL-TERP/TERP_PORTAL/TERP_PORTAL$4f94e448-6fcd-497b-8357-66a90c82a3f9/page",
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        }
        self.session.headers.update(headers)
        
        response = self.session.get(url)
        if response.status_code != 200:
            raise Exception(f"Get current user failed: {response.text}")
            
        return response.json()
        
    def get_session(self) -> requests.Session:
        """
        获取会话对象
        
        返回:
            会话对象
        """
        return self.session 
    
    
if __name__ == "__main__":
    login_manager = LoginManager()
    # 使用默认账号密码登录
    session = login_manager.login()
    
    # 使用指定账号密码登录
    # account, password = "your_account", "your_password"
    # session = login_manager.login(account=account, password=password)