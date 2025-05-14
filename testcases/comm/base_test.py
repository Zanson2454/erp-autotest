"""测试框架基础模块

提供测试用例的基础功能，包括：
1. 环境初始化：配置加载、日志设置
2. 数据库操作：连接池管理、SQL执行
3. HTTP 请求处理：会话管理、请求封装
4. 断言工具：通用断言方法
5. 日志记录：统一日志格式
6. 测试数据管理：数据初始化、缓存机制
"""

import json
import pytest
import allure
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from loguru import logger
import sys
import os
import time
import requests
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from testcases.comm.login import LoginManager
from utils.yaml_util import YamlUtil
from utils.assert_util import AssertHelper
from utils.log_util import Loggers
from utils.mysql_util import DBManager
from utils.request_util import HttpUtil
from utils.exception_util import handle_exception, safe_api_call, handle_class_method_exception
from utils.mock_util import MockData
from utils.cache_util import CacheUtil

class EnvInit:
    """环境初始化类"""
    
    def __init__(self, env: str = "test"):
        """初始化环境配置
        
        Args:
            env: 环境名称，默认为test
        """
        self.env = env
        self.project_root = Path(__file__).parent.parent.parent
        self.env_file = self.project_root / '.env'
        self.yaml_file = self.project_root / 'config' / 'env' / f'{env}.yaml'
        
        # 加载配置
        self._load_env()
        self._load_yaml()
        logger.info(f"初始化环境配置: {self.env}")
    
    def _load_env(self):
        """加载.env文件中的环境变量"""
        if self.env_file.exists():
            load_dotenv(self.env_file)
            logger.info(f"已加载环境变量文件: {self.env_file}")
        else:
            logger.warning(f"环境变量文件不存在: {self.env_file}")
    
    def _load_yaml(self):
        """加载YAML配置文件并替换环境变量"""
        if self.yaml_file.exists():
            yaml_util = YamlUtil()
            self.config = yaml_util.read_yaml(f"env/{self.env}.yaml")
            logger.info(f"已加载YAML配置文件: {self.yaml_file}")
            
            # 替换环境变量
            self._replace_env_vars(self.config)
        else:
            logger.warning(f"YAML配置文件不存在: {self.yaml_file}")
            self.config = {}
    
    def _replace_env_vars(self, config: Dict[str, Any]):
        """递归替换配置中的环境变量
        
        Args:
            config: 配置字典
        """
        for key, value in config.items():
            if isinstance(value, dict):
                self._replace_env_vars(value)
            elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                # 提取环境变量名
                env_var = value[2:-1]
                # 获取环境变量值
                env_value = os.getenv(env_var)
                if env_value is not None:
                    config[key] = env_value
                    logger.debug(f"替换环境变量: {env_var} -> {env_value}")
                else:
                    logger.warning(f"环境变量未定义: {env_var}")
    
    def get_config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return self.config

class Login:
    """登录类"""
    def __init__(self, env: str = "test"):
        """初始化登录类
        
        Args:
            env: 环境名称，默认为test
        """
        self.config = EnvInit(env).get_config()
        self.iam_url = self.config.get("iam_url")
        self.api_url = self.config.get("base_url")
        self.base_headers = self._get_base_headers()  # 获取基础请求头
        self.iam_headers = self._get_iam_headers()  # 获取 IAM 登录请求头
        self.api_headers = self._get_api_headers()  # 获取 API 请求头
        self.session = requests.Session()
        self.session.headers.update(self.base_headers)
        
        # 初始化时执行登录
        self.login()
    
    def _get_base_headers(self) -> Dict[str, str]:
        """获取基础请求头"""
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
        """获取IAM登录请求头"""
        return {
            **self.base_headers,
            'Origin': self.iam_url,
            'Referer': f"{self.iam_url}/TERP_PORTAL-TERP-tpf_umwrhzbg/login"
        }
    
    def _get_api_headers(self) -> Dict[str, str]:
        """获取API请求头"""
        return {
            **self.base_headers,
            'Origin': self.api_url,
            'Referer': f"{self.api_url}/TERP_PORTAL-TERP/TERP_PORTAL/TERP_PORTAL$4f94e448-6fcd-497b-8357-66a90c82a3f9/page"
        }   
    
    def login(self):
        """执行登录流程"""
        try:
            # 获取登录信息
            login_data = {
                "username": self.config.get("tenants", {}).get("terp", {}).get("auth", {}).get("username", ""),
                "password": self.config.get("tenants", {}).get("terp", {}).get("auth", {}).get("password", "")          
            }
            logger.info(f"使用账号: {login_data['username']}")
            
            # 执行IAM登录
            login_url = f"{self.iam_url}/iam/api/v1/user/login/account"
            self.session.headers.update(self.iam_headers)
            response = self.session.post(login_url, json=login_data)
            logger.info(f"登录响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                raise Exception(f"登录失败: {response.text}")
            
            # 处理重定向
            redirect_url = f"{self.api_url}/TERP_PORTAL-TERP-tpf_umwrhzbg/login"
            self.session.headers.update(self.api_headers)
            response = self.session.get(redirect_url, allow_redirects=True)
            
            if response.status_code != 200:
                raise Exception(f"重定向失败: {response.text}")
            
            # 获取用户信息验证登录状态
            user_info = self.get_current_user()
            if not user_info:
                raise Exception("获取用户信息失败")
            
            logger.info("登录成功")
            
        except Exception as e:
            logger.error(f"登录过程发生错误: {str(e)}")
            raise
    
    def get_current_user(self) -> Dict[str, Any]:
        """获取当前登录用户的信息"""
        logger.info(f"api_url: {self.api_url}")
        url = f"{self.api_url}/api/trantor/portal/user/current"
        logger.info(f"获取用户信息URL: {url}")
        
        try:
            self.session.headers.update(self.api_headers)
            response = self.session.get(url)
            logger.info(f"获取用户信息响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"获取用户信息失败: {response.text}")
                return None
                
            return response.json()
        except Exception as e:
            logger.error(f"获取用户信息过程发生错误: {str(e)}")
            return None
    
    
class SQLInitializer:
    """SQL初始化器
    
    负责执行和验证数据库初始化SQL，支持缓存机制。
    """
    def __init__(self, config_path: Path, cache: CacheUtil, db_config: Dict[str, Any], logger: Loggers): # 初始化SQL初始化器
        self.config_path = config_path # 配置文件路径
        self.cache = cache # 缓存管理器
        self.log = logger # 日志工具
        self.db = self._init_db(db_config) # 初始化数据库连接
    
    def _init_db(self, db_config: Dict[str, Any]) -> DBManager:
        """初始化数据库连接
        
        Args:
            db_config: 数据库配置
            
        Returns:
            DBManager: 数据库管理器实例
        """
        # 重命名配置键以匹配 PyMySQL 参数
        db_config = {
            'host': db_config.get('host'),
            'port': int(db_config.get('port', 3306)),
            'user': db_config.get('user'),
            'password': db_config.get('password'),
            'database': db_config.get('name'),
            'charset': db_config.get('charset', 'utf8mb4')
        }
        
        logger.info(f"db_config: {db_config}")
        return DBManager(db_config)
    
    def init_sql(self) -> Dict[str, Any]:
        """初始化SQL数据
        
        Returns:
            Dict[str, Any]: 初始化数据
        """
        try:
            # 尝试从缓存获取数据
            cache_data = self.cache.get()
            if cache_data:
                self.log.info("从缓存获取数据成功")
                return cache_data
            
            # 缓存不存在或已过期，重新初始化数据
            self.log.info("缓存数据不存在或已过期，开始初始化数据")
            init_data = self._init_sql_impl()
            
            # 写入缓存
            self.cache.set(init_data)
            self.log.info("数据初始化完成并写入缓存")
            
            return init_data
        except Exception as e:
            self.log.error(f"初始化SQL时出错: {str(e)}")
            raise
    
    def _init_sql_impl(self) -> Dict[str, Any]:
        """实际的SQL初始化实现"""
        # 读取配置文件
        yaml_util = YamlUtil()
        config = yaml_util.read_yaml(self.config_path)
        if not config:
            raise ValueError(f"配置文件为空: {self.config_path}")
        
        # 初始化返回结果
        init_data = {
            "user_info": {},
            "base_info": {},
            "org_info": {},
            "partner_info": {},
            "material_info": {}
        }
        
        # 执行配置的SQL查询
        for query_key, query_config in config.get('base_info', {}).items():
            try:
                sql = query_config.get('sql', '')
                if not sql:
                    continue
                
                # 使用新的 query 方法
                result = self.db.query(sql)
                formatted_result = self._format_result(result)
                
                # 根据查询类型分类存储结果
                category = self._get_result_category(query_key)
                init_data[category][query_key] = formatted_result[0] if formatted_result else None
                
            except Exception as e:
                self.log.error(f"执行查询 {query_key} 时出错: {str(e)}")
                raise
        
        return init_data
    
    def _format_result(self, result: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """格式化查询结果"""
        if not result:
            return []
        
        return [{
            key: float(value) if isinstance(value, Decimal) # 将 Decimal 转换为 float
            else value.isoformat() if isinstance(value, datetime) # 将 datetime 转换为 ISO 格式字符串
            else value # 其他类型保持不变
            for key, value in row.items() # 遍历每一行数据
        } for row in result] # 返回格式化后的结果
    
    def _get_result_category(self, query_key: str) -> str:
        """根据查询键获取结果分类"""
        if 'org' in query_key:
            return 'org_info' # 返回组织信息分类
        elif any(x in query_key for x in ['partner', 'vend', 'cust']):
            return 'partner_info' # 返回合作伙伴信息分类
        elif any(x in query_key for x in ['mat', 'atp', 'inv']):
            return 'material_info' # 返回物料信息分类
        return 'base_info'

class BaseTest:
    """测试基类
    
    提供测试用例的公共功能，包括环境初始化、数据库操作、HTTP请求处理等。
    """
    
    @classmethod
    @handle_class_method_exception(log_level="ERROR")
    def setup_class(cls) -> None:
        """测试类初始化
        
        1. 初始化日志
        2. 初始化缓存管理器
        3. 初始化SQL工具
        4. 初始化HTTP工具和断言工具
        """
        # 初始化日志
        cls.logger = Loggers()
        
        # 初始化缓存管理器
        cache_dir = Path(__file__).parent.parent.parent / "testdata" / "cache"
        cls.cache = CacheUtil(cache_dir)
        
        # 初始化环境配置
        cls.env = EnvInit()
        logger.info("测试环境初始化完成")
        
        # 初始化SQL工具
        config_path = project_root / "testdata" / "init" / "gen.yaml" # 配置文件路径
        env_config = cls.env.get_config()
        
        # 获取数据库配置
        db_config = env_config.get("database", {}).get("erp_db", {})
        if not db_config:
            raise ValueError(f"数据库配置不存在: config/env/{cls.env.env}.yaml")
            
        cls.init_sql = SQLInitializer(config_path, cls.cache, db_config, cls.logger) # SQL初始化器
        cls.db = cls.init_sql.db  # 获取数据库管理器实例
        
        # 初始化其他组件
        cls.http = HttpUtil() # HTTP 工具
        cls.assert_util = AssertHelper() # 断言工具
        
        # 获取初始化数据
        init_data = cls.init_sql.init_sql() # 获取初始化数据
        cls._process_init_data(init_data) # 处理初始化数据
        
        # 初始化测试数据
        cls.test_data = {}
    
    @classmethod
    def _process_init_data(cls, init_data: Dict[str, Any]) -> None:
        """处理初始化数据"""
        cls.init_data = {
            "user_info": {"user_info": init_data.get("base_info", {}).get("user_info", {})},
            "base_info": {
                "so_type_info": init_data.get("base_info", {}).get("so_type_info", {}),
                "sales_channel_info": init_data.get("base_info", {}).get("sales_channel_info", {}),
                "exchange_rate_type_info": init_data.get("base_info", {}).get("exchange_rate_type_info", {}),
                "currency_info": init_data.get("base_info", {}).get("currency_info", {})
            },
            "org_info": {
                "sls_org_info": init_data.get("org_info", {}).get("sls_org_info", {}),
                "pur_org_info": init_data.get("org_info", {}).get("pur_org_info", {}),
                "inv_org_info": init_data.get("org_info", {}).get("inv_org_info", {}),
                "com_org_info": init_data.get("org_info", {}).get("com_org_info", {})
            },
            "partner_info": {
                "cust_info": init_data.get("partner_info", {}).get("cust_info", {})
            },
            "material_info": {
                "inv_loc_info": init_data.get("material_info", {}).get("inv_loc_info", {})
            }
        }
        
        cls._extract_ids()
    
    @classmethod
    def _extract_ids(cls) -> None:
        """提取必要的ID并验证"""
        id_mappings = {
            'user_id': ('user_info', 'user_info', 'id'),
            'cust_id': ('partner_info', 'cust_info', 'id'),
            'so_type_id': ('base_info', 'so_type_info', 'id'),
            'sls_org_id': ('org_info', 'sls_org_info', 'id'),
            'pur_org_id': ('org_info', 'pur_org_info', 'id'),
            'inv_org_id': ('org_info', 'inv_org_info', 'id'),
            'com_org_id': ('org_info', 'com_org_info', 'id'),
            'sls_dc_id': ('base_info', 'sales_channel_info', 'id'),
            'inv_loc_id': ('material_info', 'inv_loc_info', 'id'),
            'exchange_rate_type_id': ('base_info', 'exchange_rate_type_info', 'exchange_rate_type_id'),
            'base_curr_id': ('base_info', 'currency_info', 'curr_id'),
            'sls_curr_id': ('base_info', 'currency_info', 'curr_id')
        }
        
        for attr_name, path in id_mappings.items():
            value = cls.init_data
            for key in path:
                value = value.get(key, {})
            setattr(cls, attr_name, value)
            cls.assert_util.assert_id_exists(value, f"{attr_name.replace('_', ' ').title()}")
    
    def setup_method(self, method: Optional[pytest.Function] = None) -> None:
        """测试方法开始前的设置"""
        if method and hasattr(method, '__name__'):
            self.log.info(f"开始测试: {method.__name__}")
        else:
            self.log.info("开始测试方法")
        self.test_data = {}

    def teardown_method(self):
        """测试方法清理"""
        pass

    @classmethod
    def teardown_class(cls):
        """测试类清理"""
        pass

if __name__ == "__main__":
    # 测试环境初始化
    env = EnvInit()
    logger.info(f"环境配置: {env.get_config()}")
    login = Login()
    logger.info(f"当前登录用户: {login.get_current_user()}")
