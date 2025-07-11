# 改进后的登录管理

from math import log
import sys
import os
import time
import pytest
import requests
from functools import wraps
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum
from pathlib import Path



project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from utils.log_util import Loggers
from utils.assert_util import AssertHelper
from utils.mock_util import MockData
from utils.cache_util import CacheUtil
from utils.yaml_util import YamlUtil
from utils.request_util import HttpUtil
from utils.exception_util import safe_api_call
from data_factory.base import DataFactory, DBManager


class LoginStatus(Enum):
    """登录状态枚举"""
    SUCCESS = "success"
    FAILED = "failed"
    EXPIRED = "expired"
    UNAUTHORIZED = "unauthorized"

@dataclass
class LoginResult:
    """登录结果数据类"""
    status: LoginStatus
    user_info: Optional[Dict[str, Any]] = None
    session: Optional[requests.Session] = None
    error_message: Optional[str] = None
    portal_url: Optional[str] = None
    portal_headers: Optional[Dict[str, str]] = None
    iam_url: Optional[str] = None
    iam_headers: Optional[Dict[str, str]] = None

class AuthenticationError(Exception):
    """认证相关异常"""
    pass

class SessionManager:
    """会话管理器 - 专门负责HTTP会话"""
    
    def __init__(self, base_headers: Dict[str, str]):
        self.session = requests.Session()
        self.session.headers.update(base_headers)
    
    def update_headers(self, headers: Dict[str, str]):
        """更新请求头"""
        self.session.headers.update(headers)
    
    def get_session(self) -> requests.Session:
        """获取会话对象"""
        return self.session

    

class LoginService:
    """登录服务 - 专门负责登录逻辑"""
    
    # 常量定义
    LOGIN_SUCCESS_CODE = 200
    LOGIN_ENDPOINT = "/iam/api/v1/user/login/account"
    USER_INFO_ENDPOINT = "/api/trantor/portal/user/current"
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session_manager = SessionManager(self.build_headers())
        
    @staticmethod
    def build_headers(origin: Optional[str] = None, referer: Optional[str] = None) -> Dict[str, str]:
        """获取基础请求头"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': MockData().get_mock_user_agent(),
            'Referer': referer,
            'Origin': origin
        }
        return headers
    def login(self, portal_key, tenant_key="terp") -> LoginResult:
        """执行登录"""
        try:
            # 1. 准备登录数据,从配置中读取
            auth_config = self.config.get("portal_config", {}).get(tenant_key, {}).get(portal_key, {})
            login_url = f"{auth_config.get('iam_url', '').rstrip('/')}{self.LOGIN_ENDPOINT}"
            login_data = {
            "account": auth_config.get("username", ""),
            "password": auth_config.get("password", ""),
            "iam_url": auth_config.get("iam_url", ""),
            "iam_referer": auth_config.get("iam_referer", ""),
            "portal_url": auth_config.get("portal_url", ""),
            "portal_referer": auth_config.get("portal_referer", ""),
            "description": auth_config.get("description", "")
        }
            # 2. 执行登录请求
            iam_headers = self.build_headers(
                origin=auth_config.get("iam_url", ""),
                referer=auth_config.get("iam_referer", "")
            )
            Loggers.info(f"登录URL: {login_url}")
            Loggers.info(f"登录账号: {login_data['account']}")
            Loggers.info(f"登录请求头: {iam_headers}")
            Loggers.info(f"登录数据: {login_data}")
            self.session_manager.update_headers(iam_headers)
            login_response = self.session_manager.get_session().post(
                login_url, 
                json=login_data, 
                headers=iam_headers
            )
    
            
            # 4. 验证登录结果
            if not self._is_login_successful(login_response):
                return LoginResult(
                    status=LoginStatus.FAILED,
                    error_message=f"登录失败: {login_response.text}"
                )
            
            # 5. 获取用户信息
            user_info = self._get_user_info(portal_key, tenant_key)
            if not user_info:
                return LoginResult(
                    status=LoginStatus.FAILED,
                    error_message="获取用户信息失败"
                )
            
            return LoginResult(
                status=LoginStatus.SUCCESS,
                user_info=user_info,
                portal_url=auth_config.get("portal_url", ""),
                iam_url=auth_config.get("iam_url", ""),
                portal_headers=self.build_headers(auth_config.get("portal_url", ""),auth_config.get("portal_referer", "")),
                iam_headers=self.build_headers(auth_config.get("iam_url", ""),auth_config.get("iam_referer", "")),
                session=self.session_manager.get_session()
            )
        except Exception as e:
            Loggers.error(f"登录过程异常: {str(e)}")
            return LoginResult(
                status=LoginStatus.FAILED,
                error_message=str(e)
            )
    

    
    def _is_login_successful(self, response: requests.Response) -> bool:
        """判断登录是否成功"""
        return response.status_code == self.LOGIN_SUCCESS_CODE
    
    def _get_user_info(self, portal_key, tenant_key="terp") -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        portal_config = self.config.get("portal_config", {}).get(tenant_key, {}).get(portal_key, {})
        portal_url = portal_config.get("portal_url", "")
        portal_referer = portal_config.get("portal_referer", "")
        Loggers.info(f"portal_config: {portal_config}")
        Loggers.info(f"portal_referer: {portal_referer}")
        if not portal_url:
            Loggers.error("portal_url 配置缺失，请检查配置文件！")
            return None
        portal_headers = self.build_headers(portal_url, portal_referer) 
        url = f"{portal_url}{self.USER_INFO_ENDPOINT}"
        Loggers.info(f"获取用户信息URL: {url}")
        Loggers.info(f"获取用户信息请求头: {portal_headers}")
        self.session_manager.update_headers(portal_headers)
        
        
        try:
            response = self.session_manager.get_session().get(url)
            if response.status_code == self.LOGIN_SUCCESS_CODE:
                return response.json().get("data")
            else:
                Loggers.error(f"获取用户信息失败: {response.text}")
                return None
        except Exception as e:
            Loggers.error(f"获取用户信息异常: {str(e)}")
            return None



class BaseTestInitializer:
    """测试基类初始化器 - 专门负责初始化逻辑"""
    
    def __init__(self, env_name: str):
        self.env_name = env_name
        self.data_factory = DataFactory(env_name=env_name)
    
    def initialize_environment(self) -> Dict[str, Any]:
        """初始化环境配置"""
        Loggers.info(f"初始化环境: {self.env_name}")
        config = self.data_factory.get_env_config()
        if config is None:
            raise RuntimeError(f"环境配置获取失败: {self.env_name}")
        return config
    
    def initialize_base_data(self) -> Dict[str, Any]:
        """初始化基础数据"""
        raw_data = self.data_factory.get_base_data(project="erp")
        if not raw_data:
            raise RuntimeError("基础数据获取失败，请检查数据工厂配置和数据库连接！")
        return raw_data
    
    def initialize_authentication(self, env_config: Dict[str, Any]) -> LoginResult:
        """初始化认证"""
        login_service = LoginService(env_config)
        login_result = login_service.login(portal_key="TERP_PORTAL",tenant_key="terp")
        
        if login_result.status != LoginStatus.SUCCESS:
            raise AuthenticationError(f"登录失败: {login_result.error_message}")
        
        return login_result
    
    def initialize_database(self, env_config: Dict[str, Any]) -> DBManager:
        """初始化数据库连接"""
        db_config = env_config.get("database", {}).get("erp_db")
        if not db_config:
            raise RuntimeError("数据库配置未找到，请检查环境配置文件")
        
        DBManager.init(db_config)
        return DBManager()
    
    def initialize_utilities(self) -> Dict[str, Any]:
        """初始化工具类"""
        return {
            "logger": Loggers(),
            "assert_util": AssertHelper(),
            "mock_util": MockData(),
            "cache": CacheUtil(),
            "yaml_util": YamlUtil(),
            "safe_api_call": safe_api_call
        }

class BaseTest:
    """重构后的测试基类"""
    
    # 类型提示：动态设置的属性
    logger: Any
    assert_util: Any
    
    @classmethod
    def setup_class(cls) -> None:
        """测试类初始化 - 简化版"""
        try:
            # 获取环境
            env = os.getenv("TEST_ENV", "test")
            
            # 使用初始化器
            initializer = BaseTestInitializer(env)
            
            # 分步初始化
            cls.env_config = initializer.initialize_environment() # 获取环境基础配置
            cls.init_data = initializer.initialize_base_data() # 获取基础数据
            
            # 认证初始化
            login_result = initializer.initialize_authentication(cls.env_config)
            cls.user_info = login_result.user_info # 获取用户信息
            cls.session = login_result.session # 获取会话
            cls.http = HttpUtil(
                url=login_result.portal_url,
                session=login_result.session,
                headers=login_result.portal_headers
            )
            
            # 数据库初始化
            cls.db = initializer.initialize_database(cls.env_config) # 获取数据库连接
            
            # mock工具初始化
            cls.mock_util = MockData() # 获取mock工具类
            
            # 缓存工具初始化
            cls.cache = CacheUtil() # 获取缓存工具类
            
            # 工具类初始化
            utilities = initializer.initialize_utilities() # 获取工具类
            for name, util in utilities.items(): # 设置工具类
                setattr(cls, name, util) # 设置工具类
            
            
      
            
            # 更新初始化数据
            cls.init_data["user_info"] = {"user_info": cls.user_info}
            
            Loggers.info("测试基类初始化完成")
            
        except Exception as e:
            Loggers.error(f"BaseTest初始化失败: {str(e)}")
            raise
    
    def setup_method(self, method: Optional[pytest.Function] = None) -> None:
        """测试方法前置设置"""
        method_name = getattr(method, '__name__', 'unknown_method')
        self.logger.info(f"开始测试方法: {method_name}")
        self.test_data = {}
        self.test_start_time = time.time()
    
    def teardown_method(self, method: Optional[pytest.Function] = None) -> None:
        """测试方法后置清理"""
        if hasattr(self, 'test_start_time'):
            duration = time.time() - self.test_start_time
            method_name = getattr(method, '__name__', 'unknown_method')
            self.logger.info(f"测试方法 {method_name} 执行完成，耗时: {duration:.3f}秒")
    
    @staticmethod
    def timer(func):
        """改进的计时装饰器"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                Loggers.info(f"函数 {func_name} 执行成功，耗时: {duration:.3f}秒")
                return result
            except Exception as e:
                duration = time.time() - start_time
                Loggers.error(f"函数 {func_name} 执行失败，耗时: {duration:.3f}秒，错误: {str(e)}")
                raise
        return wrapper


class ConfigValidator:
    """配置验证器"""
    
    REQUIRED_CONFIG_KEYS = [
        "iam_url", "portal_url", "admin_url",
        "iam_referer", "portal_referer", "admin_referer"
    ]
    
    REQUIRED_AUTH_KEYS = ["username", "password"]
    
    @classmethod
    def validate_env_config(cls, config: Dict[str, Any]) -> None:
        """验证环境配置"""
        # 验证基础配置
        missing_keys = [key for key in cls.REQUIRED_CONFIG_KEYS if not config.get(key)]
        if missing_keys:
            raise ValueError(f"环境配置缺少必要字段: {missing_keys}")
        
        # 验证认证配置
        auth_config = config.get("tenants", {}).get("terp", {}).get("auth", {})
        missing_auth_keys = [key for key in cls.REQUIRED_AUTH_KEYS if not auth_config.get(key)]
        if missing_auth_keys:
            raise ValueError(f"认证配置缺少必要字段: {missing_auth_keys}")
    
    @classmethod
    def validate_database_config(cls, config: Dict[str, Any]) -> None:
        """验证数据库配置"""
        db_config = config.get("database", {}).get("erp_db", {})
        required_db_keys = ["host", "port", "database", "username", "password"]
        missing_db_keys = [key for key in required_db_keys if not db_config.get(key)]
        if missing_db_keys:
            raise ValueError(f"数据库配置缺少必要字段: {missing_db_keys}")



if __name__ == "__main__":
    BaseTest.setup_class()
    print(BaseTest.env_config)
    print(BaseTest.init_data)
    if BaseTest.user_info:
        print(BaseTest.user_info['nickname'])
   
   
    # login_result = LoginService(BaseTest.env_config).login(portal_key="TERP_CUST_PC",tenant_key="terp")
    # print(login_result)