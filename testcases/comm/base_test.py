"""测试框架基础模块

提供测试用例的基础功能，包括：
1. 环境初始化：配置加载、日志设置
2. 数据库操作：连接池管理、SQL执行
3. HTTP 请求处理：会话管理、请求封装
4. 断言工具：通用断言方法
5. 日志记录：统一日志格式
6. 测试数据管理：数据初始化、缓存机制
"""

import pytest
from typing import Dict, Any, Optional
from pathlib import Path
from loguru import logger
import sys
import time
import requests
import os

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.assert_util import AssertHelper
from utils.log_util import Loggers
from utils.request_util import HttpUtil
from utils.mock_util import MockData
from utils.cache_util import CacheUtil
from data_factory.base import DataFactory
from utils.yaml_util import YamlUtil
from utils.exception_util import safe_api_call
from utils.mysql_util import DBManager


class Login:
    """
    登录类，依赖DataFactory获取环境配置。
    """
    def __init__(self, env_name: str = "test"):
        """
        初始化登录类
        :param env_name: 环境名称，如 test/dev/prod
        """
        Loggers.info(f"初始化登录类，环境: {env_name}")
        self.config = DataFactory(env_name=env_name).get_env_config()
        self.iam_url = self.config.get("iam_url")
        self.portal_url = self.config.get("portal_url")
        self.admin_url = self.config.get("admin_url")
        self.iam_referer = self.config.get("iam_referer")
        self.portal_referer = self.config.get("portal_referer")
        self.admin_referer = self.config.get("admin_referer")
        self.base_headers = self._get_base_headers()
        self.iam_headers = self._get_iam_headers()
        self.portal_headers = self._get_portal_headers()
        self.session = requests.Session()
        self.session.headers.update(self.base_headers)
        self.user_info = None  # 初始化 user_info 属性
        self.login()
    
    def _get_base_headers(self) -> Dict[str, str]:
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
        return {
            **self.base_headers,
            'Origin': self.iam_url,
            'Referer': self.iam_referer
        }
    
    def _get_portal_headers(self) -> Dict[str, str]:
        return {
            **self.base_headers,
            'Origin': self.portal_url,
            'Referer': self.portal_referer
        }   
    
    def login(self):
        try:
            login_data = {
                "account": self.config.get("tenants", {}).get("terp", {}).get("auth", {}).get("username", ""),
                "password": self.config.get("tenants", {}).get("terp", {}).get("auth", {}).get("password", "")          
            }
            logger.info(f"使用账号: {login_data['account']}")
            login_url = f"{self.iam_url}/iam/api/v1/user/login/account"
            self.session.headers.update(self.iam_headers)
            response = self.session.post(login_url, json=login_data, headers=self.iam_headers)
            logger.info(f"登录响应状态码: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"登录失败: {response.text}")
                raise Exception("登录失败")
            user_info = self.get_current_user()
            logger.info(f"获取用户信息: {user_info}")
            if not user_info:
                raise Exception("获取用户信息失败")
            logger.info("登录成功")
        except Exception as e:
            logger.error(f"登录过程发生错误: {str(e)}")
            raise
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        url = f"{self.portal_url}/api/trantor/portal/user/current"
        logger.info(f"获取用户信息URL: {url}")
        try:
            self.session.headers.update(self.portal_headers)
            response = self.session.get(url)
            if response.status_code != 200:
                logger.error(f"获取用户信息失败: {response.text}")
                return None
            user_info = response.json().get("data")
            return user_info
        except Exception as e:
            logger.error(f"获取用户信息过程发生错误: {str(e)}")
            return None
    
class BaseTest:
    """
    测试基类，统一依赖DataFactory进行环境初始化和基础数据获取。
    提供断言、日志、HTTP等通用能力。
    """
    @classmethod
    def setup_class(cls) -> None:
        """
        测试类初始化：
        1. 初始化数据工厂（环境、配置、数据库、缓存）
        2. 获取结构化基础数据
        3. 提取常用ID
        4. 初始化断言、日志、HTTP等工具
        """
        try:
            # 获取当前环境
            env = os.getenv("TEST_ENV", "test")
            Loggers.info(f"使用环境: {env}")
            
            # 初始化数据工厂
            data_factory = DataFactory(env_name=env)
            cls.init_data = data_factory.get_base_data(module="gen") # 获取结构化基础数据
            cls.env_config = data_factory.get_env_config() # 获取环境基础配置
            
            # 登录 并保存 userId
            cls.login = Login(env)
            logger.info(f"登录成功: {cls.login}")
            cls.user_info = cls.login.get_current_user() # 获取当前用户信息
            if not cls.user_info or "id" not in cls.user_info:
                raise RuntimeError("user_info 未正确初始化或缺少 id 字段")
 
            cls.base_headers = cls.login.base_headers
            cls.session = cls.login.session 
            cls.init_data["user_info"] = {"user_info": cls.user_info}
            if not cls.init_data: # 如果基础数据获取失败，则抛出异常
                raise RuntimeError("基础数据获取失败，请检查数据工厂配置和数据库连接！")
            
            cls.ids = DataFactory.extract_ids(cls.init_data) # 提取常用ID   
            logger.info(f"ids: {cls.ids}")
            cls.logger = Loggers() # 初始化日志
            cls.assert_util = AssertHelper() # 初始化断言工具
            cls.mock_util = MockData() # 初始化Mock工具
            cls.cache = CacheUtil() # 初始化缓存工具
            cls.yaml_util = YamlUtil() # 初始化Yaml工具
            
            _db_config = cls.env_config.get("database", {}).get("erp_db")
            if not _db_config:
                raise RuntimeError("数据库配置未找到，请检查环境配置文件")
            DBManager.init(_db_config)
            cls.db=DBManager()
            cls.safe_api_call = safe_api_call # 初始化安全API调用工具
        
           
            cls.http = HttpUtil(
                url=cls.env_config.get("portal_url"),
                session=cls.session,
                headers=cls.base_headers
            ) # 初始化HTTP工具

            
            logger.info("测试基类初始化完成")
        except Exception as e:
            logger.error(f"BaseTest.setup_class 初始化失败: {str(e)}")
            raise
    
    def setup_method(self, method: Optional[pytest.Function] = None) -> None:
        """
        测试方法开始前的设置
        """
        if method and hasattr(method, '__name__'):
            self.logger.info(f"开始测试: {method.__name__}")
        else:
            self.logger.info("开始测试方法")
        self.test_data = {}

    def teardown_method(self):
        """
        测试方法清理
        """
        pass

    @classmethod
    def teardown_class(cls):
        """
        测试类清理
        """
        pass
    
    def timer(func):
        """装饰器，用于记录函数执行时间"""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                logger.info(f"函数 {func.__name__} 执行时间: {end_time - start_time:.3f} 秒")
                return result
            except Exception as e:
                end_time = time.time()
                logger.error(f"函数 {func.__name__} 执行失败，耗时: {end_time - start_time:.3f} 秒，错误: {str(e)}")
                raise
        return wrapper



if __name__ == "__main__":
    # 测试环境初始化
    test = BaseTest()
    test.setup_class()
    # test = Login(env_name="test")
    # test.login()
