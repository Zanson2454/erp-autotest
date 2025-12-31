# 测试基类
import sys
import os
import time
import pytest
import requests
from functools import wraps
from dataclasses import dataclass
from typing import Dict, Any, Optional, Union
from enum import Enum
from pathlib import Path
import json



project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from utils.log_util import Loggers
from utils.assert_util import AssertHelper
from utils.mock_util import MockData
from utils.cache_util import CacheUtil
from utils.yaml_util import YamlUtil
from utils.request_util import HttpUtil
from utils.exception_util import safe_api_call
from utils.param_util import ParamUtil
from utils.async_wait_util import AsyncWaitUtil, WaitStatus
from data_factory.base import DataFactory 
from utils.mysql_util import DBManager


class ConfigManager:
    """配置管理器 - 集中管理所有配置相关操作"""
    
    # 配置缓存
    _config_cache: Dict[str, Dict[str, Any]] = {}
    
    # 配置默认值
    DEFAULT_CONFIG = {
        "database": {
            "erp_db": {},
            "iam_db": {}
        },
        "portal_config": {
            "terp": {}
        }
    }
    
    @classmethod
    def get_config(cls, env: str = "test", refresh: bool = False) -> Dict[str, Any]:
        """
        获取配置，支持缓存
        
        :param env: 环境名称
        :param refresh: 是否强制刷新缓存
        :return: 配置字典
        """
        # 检查缓存
        if env in cls._config_cache and not refresh:
            Loggers.info(f"从缓存加载配置 [env={env}]")
            return cls._config_cache[env]
        
        # 加载新配置
        Loggers.info(f"加载新配置 [env={env}]")
        try:
            data_factory = DataFactory(env_name=env)
            config = data_factory.get_env_config()
            
            if config is None:
                Loggers.warning(f"配置加载失败，使用默认配置 [env={env}]")
                config = cls.DEFAULT_CONFIG.copy()
            else:
                # 合并默认配置
                config = cls._merge_configs(cls.DEFAULT_CONFIG, config)
            
            # 验证配置
            cls.validate_config(config)
            
            # 缓存配置
            cls._config_cache[env] = config
            
            Loggers.info(f"配置加载成功 [env={env}]")
            return config
            
        except Exception as e:
            Loggers.error(f"配置加载异常 [env={env}]: {str(e)}")
            raise RuntimeError(f"配置加载失败: {str(e)}") from e
    
    @staticmethod
    def _merge_configs(default: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        递归合并配置字典
        
        :param default: 默认配置
        :param override: 覆盖配置
        :return: 合并后的配置
        """
        result = default.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigManager._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> None:
        """
        验证配置完整性
        
        :param config: 配置字典
        :raises ValueError: 配置验证失败时抛出
        """
        # 验证基础配置结构
        required_structures = [
            ("portal_config", dict),
            ("database", dict)
        ]
        
        for key, expected_type in required_structures:
            if key not in config or not isinstance(config[key], expected_type):
                raise ValueError(f"配置缺少必要结构: {key} (类型应为 {expected_type.__name__})")
        
        # 验证 portal_config 结构
        portal_config = config.get("portal_config", {})
        if "terp" in portal_config:
            terp_config = portal_config["terp"]
            # 验证常用的 portal_key 配置
            common_portal_keys = ["TERP_PORTAL", "TERP_CUST_PC"]
            for portal_key in common_portal_keys:
                if portal_key in terp_config:
                    portal = terp_config[portal_key]
                    required_keys = ["portal_url", "iam_url"]
                    missing_keys = [k for k in required_keys if not portal.get(k)]
                    if missing_keys:
                        Loggers.warning(f"Portal 配置 [{portal_key}] 缺少可选字段: {missing_keys}")
        
        # 验证数据库配置
        db_config = config.get("database", {})
        for db_name in ["erp_db", "iam_db"]:
            if db_name in db_config:
                db = db_config[db_name]
                required_db_keys = ["host", "port", "database", "username", "password"]
                missing_keys = [k for k in required_db_keys if not db.get(k)]
                if missing_keys:
                    Loggers.warning(f"数据库配置 [{db_name}] 缺少字段: {missing_keys}")
    
    @classmethod
    def get_safe_config(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取安全的配置副本（隐藏敏感信息）
        
        :param config: 原始配置
        :return: 安全的配置副本
        """
        safe_config = json.loads(json.dumps(config))  # 深拷贝
        
        # 隐藏密码
        def mask_passwords(data: Any) -> Any:
            if isinstance(data, dict):
                return {
                    k: ("******" if k.lower() == "password" else mask_passwords(v))
                    for k, v in data.items()
                }
            elif isinstance(data, list):
                return [mask_passwords(item) for item in data]
            else:
                return data
        
        return mask_passwords(safe_config)
    
    @classmethod
    def clear_cache(cls) -> None:
        """清空配置缓存"""
        cls._config_cache.clear()
        Loggers.info("配置缓存已清空")
    
    @classmethod
    def get_portal_config(cls, config: Dict[str, Any], portal_key: str, tenant_key: str = "terp") -> Dict[str, Any]:
        """
        获取特定门户的配置
        
        :param config: 完整配置
        :param portal_key: 门户键名
        :param tenant_key: 租户键名
        :return: 门户配置
        """
        return config.get("portal_config", {}).get(tenant_key, {}).get(portal_key, {})


class ConfigError(Exception):
    """配置相关异常"""
    pass


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
    """会话管理器 - 专门负责HTTP会话，支持多进程隔离"""
    
    _process_sessions: Dict[int, requests.Session] = {}
    
    def __init__(self, base_headers: Dict[str, str]):
        self.base_headers = base_headers
        # 为当前进程创建独立会话
        self._ensure_session_for_current_process()
    
    def _ensure_session_for_current_process(self) -> None:
        """确保当前进程有独立的会话实例"""
        import os
        process_id = os.getpid()
        
        if process_id not in self._process_sessions:
            Loggers.info(f"为进程 {process_id} 创建新的会话实例")
            session = requests.Session()
            session.headers.update(self.base_headers)
            self._process_sessions[process_id] = session
    
    def update_headers(self, headers: Dict[str, str]):
        """更新请求头"""
        import os
        process_id = os.getpid()
        session = self._process_sessions.get(process_id)
        if session:
            session.headers.update(headers)
    
    def get_session(self) -> requests.Session:
        """获取当前进程的会话对象"""
        import os
        process_id = os.getpid()
        
        # 确保会话存在
        self._ensure_session_for_current_process()
        
        return self._process_sessions[process_id]
    
    def clear_session(self) -> None:
        """清除当前进程的会话"""
        import os
        process_id = os.getpid()
        
        if process_id in self._process_sessions:
            Loggers.info(f"清除进程 {process_id} 的会话实例")
            del self._process_sessions[process_id]
    
    @classmethod
    def clear_all_sessions(cls) -> None:
        """清除所有进程的会话（仅在单进程模式下使用）"""
        cls._process_sessions.clear()
        Loggers.info("已清除所有会话实例")

    

class LoginService:
    """登录服务 - 专门负责登录逻辑"""
    
    # 常量定义
    LOGIN_SUCCESS_CODE = 200
    LOGIN_ENDPOINT = "/iam/api/v1/user/login/account"
    USER_INFO_ENDPOINT = "/api/trantor/portal/user/current"
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session_manager = SessionManager(self.build_headers())
        # 使用 ConfigManager 获取安全配置用于日志
        self.safe_config = ConfigManager.get_safe_config(config)
        
    @staticmethod
    def build_headers(origin: Optional[str] = None, referer: Optional[str] = None, cookie: Optional[str] = None) -> Dict[str, str]:
        """获取基础请求头"""
        mock_data = MockData() 
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': mock_data.get_mock_user_agent(),
            'Accpt-Language': 'zh-CN,zh;q=0.9',
            'Referer': referer,
            'Origin': origin
        }
        # 只有明确提供了 cookie 时才添加 Cookie header
        # 避免 None 值覆盖 session 中已有的 cookie
        if cookie:
            headers['Cookie'] = cookie
        return headers
    def login(self, portal_key, tenant_key="terp") -> LoginResult:
        """
        执行登录 - 支持两种方式：
        1. 配置了 cookie：直接使用 cookie 登录（快捷方式）
        2. 未配置 cookie：使用账号密码登录（原有方式）
        """
        try:
            # 1. 准备登录数据,从配置中读取
            auth_config = ConfigManager.get_portal_config(self.config, portal_key, tenant_key)
            
            if not auth_config:
                Loggers.error(f"未找到门户配置: tenant_key={tenant_key}, portal_key={portal_key}")
                return LoginResult(
                    status=LoginStatus.FAILED,
                    error_message=f"未找到门户配置: {tenant_key}/{portal_key}"
                )
            
            # 检查是否配置了 cookie（支持直接使用 cookie 登录）
            cookie = auth_config.get("cookie", "")
            
            if cookie:
                # ============ 方式1：使用 cookie 快捷登录 ============
                Loggers.info(f"检测到配置了 cookie，使用 cookie 快捷登录")
                Loggers.info(f"Cookie 前50个字符: {cookie[:50]}...")
                
                # 设置 cookie 到 session，后续所有请求都会自动带上
                self.session_manager.get_session().headers.update({"Cookie": cookie})
                
            else:
                # ============ 方式2：使用账号密码登录（原有逻辑，完整保留） ============
                Loggers.info(f"未配置 cookie，使用账号密码登录")
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
                # 隐藏密码后打印登录数据
                safe_login_data = login_data.copy()
                if 'password' in safe_login_data:
                    safe_login_data['password'] = '******'
                Loggers.info(f"登录数据: {safe_login_data}")
                self.session_manager.update_headers(iam_headers)
                login_response = self.session_manager.get_session().post(
                    login_url, 
                    json=login_data, 
                    headers=iam_headers
                )
                
                # 3. 验证登录结果
                if not self._is_login_successful(login_response):
                    return LoginResult(
                        status=LoginStatus.FAILED,
                        error_message=f"登录失败: {login_response.text}"
                    )
                
                # 4. 获取登录返回的 cookie（用于构建返回的 headers）
                cookie = login_response.headers.get("Set-Cookie", "")
                # 注意：requests.Session 会自动管理 cookie，无需手动设置
            
            # 5. 获取用户信息（两种登录方式都需要）
            user_info = self._get_user_info(portal_key, tenant_key)
            if not user_info:
                return LoginResult(
                    status=LoginStatus.FAILED,
                    error_message="获取用户信息失败"
                )
            
            # 6. 返回登录结果
            return LoginResult(
                status=LoginStatus.SUCCESS,
                user_info=user_info,
                portal_url=auth_config.get("portal_url", ""),
                iam_url=auth_config.get("iam_url", ""),
                portal_headers=self.build_headers(
                    auth_config.get("portal_url", ""),
                    auth_config.get("portal_referer", ""),
                    cookie=cookie  # 传入 cookie 用于构建外部 headers
                ),
                iam_headers=self.build_headers(
                    auth_config.get("iam_url", ""),
                    auth_config.get("iam_referer", "")
                ),
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
        """
        获取用户信息
        注意：cookie 已经在 session 中管理，无需重复设置
        - cookie 登录：cookie 在 login 方法中已设置到 session.headers
        - 账号密码登录：cookie 由 requests.Session 自动管理
        """
        portal_config = ConfigManager.get_portal_config(self.config, portal_key, tenant_key)
        portal_url = portal_config.get("portal_url", "")
        portal_referer = portal_config.get("portal_referer", "")
        
        Loggers.info(f"获取用户信息 - portal_referer: {portal_referer}")
        if not portal_url:
            Loggers.error("portal_url 配置缺失，请检查配置文件！")
            return None
        
        # 构建 headers（不传 cookie，让 session 自动管理）
        portal_headers = self.build_headers(portal_url, portal_referer) 
        url = f"{portal_url}{self.USER_INFO_ENDPOINT}"
        Loggers.info(f"获取用户信息URL: {url}")
        Loggers.info(f"获取用户信息请求头: {portal_headers}")
        
        # 更新 headers（只更新 Origin、Referer 等，不影响 Cookie）
        self.session_manager.update_headers(portal_headers)
        
        try:
            session = self.session_manager.get_session()
            # Loggers.info(f"Session headers: {session.headers}")
            Loggers.info(f"Session cookies: {session.cookies.get_dict()}")
            
            response = session.get(url)
            Loggers.info(f"获取用户信息响应状态码: {response.status_code}")
            
            if response.status_code == self.LOGIN_SUCCESS_CODE:
                response_data = response.json()
                # Loggers.info(f"获取用户信息响应: {response_data}")
                return response_data.get("data")
            else:
                Loggers.error(f"获取用户信息失败 - 状态码: {response.status_code}")
                Loggers.error(f"响应内容: {response.text}")
                return None
        except Exception as e:
            Loggers.error(f"获取用户信息异常: {str(e)}")
            import traceback
            Loggers.error(f"异常堆栈: {traceback.format_exc()}")
            return None



class BaseTestInitializer:
    """测试基类初始化器 - 专门负责初始化逻辑"""
    
    def __init__(self, env_name: str):
        self.env_name = env_name
    
    def initialize_environment(self) -> Dict[str, Any]:
        """初始化环境配置"""
        Loggers.info(f"初始化环境: {self.env_name}")
        # 使用 ConfigManager 获取配置
        config = ConfigManager.get_config(env=self.env_name)
        
        # 打印安全的配置信息
        safe_config = ConfigManager.get_safe_config(config)
        Loggers.info(f"环境配置加载成功，配置摘要: {json.dumps(safe_config, ensure_ascii=False, indent=2)[:500]}...")
        
        return config
    
    def initialize_base_data(self) -> Dict[str, Any]:
        """初始化基础数据"""
        # 创建 DataFactory 实例
        data_factory = DataFactory(env_name=self.env_name)
        raw_data = data_factory.get_base_data(project="erp")
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
    
    def initialize_database(self, env_config: Dict[str, Any],db_name="erp_db") -> DBManager:
        """初始化数据库连接"""
        db_config = env_config.get("database", {}).get(db_name)
        if not db_config:
            raise RuntimeError(f"数据库配置未找到: {db_name}，请检查环境配置文件")

        # 创建独立的数据库连接实例
        try:
            return DBManager(**db_config)
        except Exception as e:
            host = db_config.get("host", "unknown")
            port = db_config.get("port", "unknown")
            database = db_config.get("database", "unknown")
            raise RuntimeError(
                f"数据库连接失败 [{db_name}]:\n"
                f"  - 主机: {host}:{port}\n"
                f"  - 数据库: {database}\n"
                f"  - 错误: {str(e)}\n"
                f"请检查:\n"
                f"  1. 数据库服务是否已启动\n"
                f"  2. 网络连接是否正常\n"
                f"  3. 防火墙是否允许连接\n"
                f"  4. 数据库配置是否正确"
            ) from e
    
    def initialize_utilities(self) -> Dict[str, Any]:
        """初始化工具类"""
        return {
            "logger": Loggers(),
            "assert_util": AssertHelper(),
            "mock_util": MockData(),
            "cache": CacheUtil(),
            "yaml_util": YamlUtil(),
            "async_wait_util": AsyncWaitUtil,
            "wait_status": WaitStatus,
            "safe_api_call": safe_api_call
        }

class BaseTest:
    """重构后的测试基类"""
    
    # 类型提示：动态设置的属性
    # type: ignore[attr-defined]
    logger: Any
    assert_util: Any
    env_config: Any
    init_data: Any
    user_info: Any
    session: Any
    http: Any
    db: Any
    iam_db: Any
    mock_util: Any
    cache: Any
    yaml_util: Any
    
    @classmethod
    def setup_class(cls) -> None:
        """测试类初始化 - 模板方法模式优化"""
        try:
            # 获取环境
            env = os.getenv("TEST_ENV", "test")
            Loggers.info(f"开始初始化测试基类 [env={env}]")

            # 使用初始化器
            initializer = BaseTestInitializer(env)

            # 模板方法：按顺序执行初始化步骤
            cls._initialize_config(initializer)      # 1. 配置初始化
            cls._initialize_data(initializer)        # 2. 数据初始化
            cls._initialize_auth(initializer)        # 3. 认证初始化
            cls._initialize_database(initializer)    # 4. 数据库初始化
            cls._initialize_utilities(initializer)   # 5. 工具类初始化
            cls._post_initialize()                   # 6. 后处理

            Loggers.info("测试基类初始化完成")

        except Exception as e:
            Loggers.error(f"BaseTest初始化失败: {str(e)}")
            raise

    @classmethod
    def _initialize_config(cls, initializer: BaseTestInitializer) -> None:
        """配置初始化 - 可被子类重写"""
        cls.env_config = initializer.initialize_environment()

    @classmethod
    def _initialize_data(cls, initializer: BaseTestInitializer) -> None:
        """数据初始化 - 可被子类重写"""
        cls.init_data = initializer.initialize_base_data()

    @classmethod
    def _initialize_auth(cls, initializer: BaseTestInitializer) -> None:
        """认证初始化 - 可被子类重写"""
        login_result = initializer.initialize_authentication(cls.env_config)
        cls.user_info = login_result.user_info
        cls.session = login_result.session
        cls.http = HttpUtil(
            url=login_result.portal_url,
            session=login_result.session,
            headers=login_result.portal_headers
        )

    @classmethod
    def _initialize_database(cls, initializer: BaseTestInitializer) -> None:
        """数据库初始化 - 可被子类重写"""
        cls.db = initializer.initialize_database(cls.env_config, db_name="erp_db")
        cls.iam_db = initializer.initialize_database(cls.env_config, db_name="iam_db")

    @classmethod
    def _initialize_utilities(cls, initializer: BaseTestInitializer) -> None:
        """工具类初始化 - 可被子类重写"""
        utilities = initializer.initialize_utilities()
        for name, util in utilities.items():
            setattr(cls, name, util)

    @classmethod
    def _post_initialize(cls) -> None:
        """后处理 - 可被子类重写"""
        # 更新初始化数据
        cls.init_data["user_info"] = {"user_info": cls.user_info}
    
    @classmethod
    def teardown_class(cls) -> None:
        """测试类结束后关闭资源
        
        注意：子类重写时必须调用 super().teardown_class() 以确保资源正确释放
        """
        try:
            # 关闭数据库连接
            if hasattr(cls, 'db') and cls.db:
                try:
                    cls.db.close()
                    Loggers.info("ERP数据库连接已关闭")
                except Exception as e:
                    Loggers.error(f"关闭ERP数据库连接失败: {str(e)}")
            
            if hasattr(cls, 'iam_db') and cls.iam_db:
                try:
                    cls.iam_db.close()
                    Loggers.info("IAM数据库连接已关闭")
                except Exception as e:
                    Loggers.error(f"关闭IAM数据库连接失败: {str(e)}")
        except Exception as e:
            Loggers.error(f"teardown_class执行失败: {str(e)}")
    
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
        
        # 清理断言上下文（避免上下文污染）
        if hasattr(self, 'assert_util') and hasattr(self.assert_util, 'clear_request_context'):
            self.assert_util.clear_request_context()

    def set_request_param(self, params, key, value):
        """设置请求参数"""
        if 'params' not in params:
            params['params'] = {}
        if 'request' not in params['params']:
            params['params']['request'] = {}
        params['params']['request'][key] = value
        return params

    def set_request_params(self, params, param_dict):
        """批量设置请求参数"""
        if 'params' not in params:
            params['params'] = {}
        if 'request' not in params['params']:
            params['params']['request'] = {}
        for key, value in param_dict.items():
            params['params']['request'][key] = value
        return params
    
    def get_api_path(self, api_key, apis_dict):
        """
        获取API路径
        Args:
            api_key: API键名
            apis_dict: API配置字典
        Returns:
            str: API路径
        """
        return ParamUtil.get_api_path(apis_dict, api_key)
    
    def get_api_params(self, api_path, api_params_dict, with_query_params=None):
        """
        获取API请求参数和完整URL
        Args:
            api_path: API路径
            api_params_dict: API参数配置字典
            with_query_params: 查询参数
        Returns:
            tuple: (参数模板, 完整URL)
        """
        return ParamUtil.get_api_params(api_params_dict, api_path, with_query_params)
    
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

    # 新增统一调用模板，不影响老用例
    def standard_api_call(self, api_key, set_dict=None, fields_to_filter=None, store_id_as=None, use_param_util=True, param_path=None, method="POST", query_params=None):
        """
        标准化API调用模板 - 纯执行和报告工具，无断言逻辑
        统一返回响应数据（无论成功还是失败），由业务断言来判断响应是否正确
        
        :param api_key: API服务名称键
        :param set_dict: 要设置的参数字典
        :param fields_to_filter: 需要过滤的字段列表
            - 如果为 None（未指定），会自动从 set_dict.keys() 获取字段列表（兼容原有用例）
            - 如果已指定（如 ["id"] 或 ["pageable"]），使用指定的值（优先使用指定值）
            - 这样既支持自动推断，也支持显式指定，完全兼容原有用例
        :param store_id_as: ID存储属性名（用于自动保存self.xxx_id）
        :param use_param_util: 是否使用ParamUtil过滤/设置（默认True）；False时可以手动构造完整结构
        :param param_path: 参数路径，默认为["params", "request"]，支持自定义路径如["params"]（手动构造时）或["params", "reuqest"]（处理拼写错误）
        :param method: HTTP请求方法，支持 "GET", "POST", "PUT", "DELETE", "PATCH"（默认"POST"）
            - GET/DELETE: 参数通过 query string 传递（params参数）
            - POST/PUT/PATCH: 参数通过 JSON body 传递（json参数）
        :param query_params: URL查询参数，支持字符串（如"tmodule=SCM_PUR&modelKey=XXX"）或字典（如{"tmodule": "SCM_PUR", "modelKey": "XXX"}）
        :return: (response, extracted_id) - response包含成功或失败的响应数据，extracted_id在成功时提取，失败时为None
        """
        import json
        
        # 规范化HTTP方法名（转大写）
        method = method.upper() if method else "POST"
        
        # 验证HTTP方法
        supported_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        if method not in supported_methods:
            raise ValueError(f"不支持的HTTP方法: {method}，支持的方法: {supported_methods}")
        
        try:
            # 1. 获取API路径和基础参数 - 使用模块特定的方法签名
            api_path = self.get_api_path(api_key)
            if api_path is None:
                raise ValueError(
                    f"未找到API配置: {api_key}\n"
                    f"请检查:\n"
                    f"1. API key是否正确: '{api_key}'\n"
                    f"2. 配置文件是否正确加载 (apis配置是否存在)\n"
                    f"3. 配置文件路径是否正确"
                )
            
            # 1.5 处理 query_params（可以是字符串或字典）
            query_params_str = None
            if query_params:
                if isinstance(query_params, dict):
                    from urllib.parse import urlencode
                    query_params_str = urlencode(query_params)
                else:
                    query_params_str = query_params
            
            # 2. 根据HTTP方法选择参数传递方式
            if method in ["GET", "DELETE"]:
                # GET/DELETE: 使用 query parameters
                params, url = self.get_api_params(api_path, with_query_params=query_params_str)
                if url is None:
                    raise ValueError(
                        f"API路径配置错误: api_path={api_path}\n"
                        f"请检查API参数配置文件中的路径配置"
                    )
                
                # GET/DELETE 请求：使用 params 参数（query string）
                request_kwargs = {"params": set_dict} if set_dict else {}
                
            else:
                # POST/PUT/PATCH: 使用 JSON body
                params, url = self.get_api_params(api_path, with_query_params=query_params_str)
                if url is None:
                    raise ValueError(
                        f"API路径配置错误: api_path={api_path}\n"
                        f"请检查API参数配置文件中的路径配置"
                    )
                
                # 3. 参数处理 - 分支逻辑（仅用于POST/PUT/PATCH）
                if use_param_util:
                    # 标准流程：使用ParamUtil过滤和设置
                    # fields_to_filter 处理逻辑：
                    # 1. 如果已指定（不是 None），使用指定的值（优先使用指定值，完全兼容原有用例）
                    # 2. 如果未指定（为 None）且有 set_dict，自动从 set_dict.keys() 获取字段列表（方便新用例）
                    # 这样既支持自动推断，也支持显式指定，完全兼容原有用例
                    if fields_to_filter is None:
                        if set_dict:
                            fields_to_filter = list(set_dict.keys())
                        else:
                            fields_to_filter = []
                    # 如果 fields_to_filter 已指定，直接使用指定的值，不会覆盖
                    # 使用自定义路径或默认路径
                    if param_path is None:
                        param_path = ["params", "request"]
                    filtered_params = ParamUtil.filter_post_body_fields(
                        params, fields_to_filter, param_path
                    )
                    if set_dict:
                        ParamUtil.set_request_params(filtered_params, set_dict, path=param_path)
                else:
                    # 特殊流程：直接使用set_dict作为params内容，无过滤/设置
                    # 注意：保留原始params中的其他字段（如serviceKey等），避免丢失必要的顶层字段
                    if set_dict is None:
                        set_dict = {}
                    # 如果指定了param_path，使用自定义路径；否则使用默认路径
                    if param_path is None:
                        param_path = ["params", "request"]
                    
                    # 从原始params开始，保留其他字段（兼容原有逻辑）
                    import copy
                    filtered_params = copy.deepcopy(params) if params else {}
                    
                    # 构造嵌套路径并设置值
                    current = filtered_params
                    for i, p in enumerate(param_path):
                        if i == len(param_path) - 1:
                            # 到达目标路径，设置值
                            current[p] = set_dict
                        else:
                            # 中间路径，确保存在
                            if p not in current:
                                current[p] = {}
                            current = current[p]
                
                # POST/PUT/PATCH 请求：使用 json 参数（body）
                request_kwargs = {"json": filtered_params} if filtered_params else {}
            
            # 4. 设置请求上下文（供断言失败时使用）
            from urllib.parse import urljoin
            full_url = urljoin(self.http.url, url.lstrip('/')) if hasattr(self.http, 'url') else url
            
            if method in ["GET", "DELETE"]:
                self.assert_util.set_request_context(
                    api_key=api_key,
                    url=full_url,
                    method=method,
                    params=request_kwargs.get("params")
                )
            else:
                self.assert_util.set_request_context(
                    api_key=api_key,
                    url=full_url,
                    method=method,
                    body=request_kwargs.get("json")
                )
            
            # 5. 发送请求（请求信息由 http 方法内部打印完整URL）
            # 根据方法调用对应的 HTTP 方法
            if method == "GET":
                response = self.http.get(url, **request_kwargs)
            elif method == "POST":
                response = self.http.post(url, **request_kwargs)
            elif method == "PUT":
                response = self.http.put(url, **request_kwargs)
            elif method == "DELETE":
                response = self.http.delete(url, **request_kwargs)
            elif method == "PATCH":
                # PATCH 方法，如果 HttpUtil 没有 patch 方法，使用 put
                if hasattr(self.http, "patch"):
                    response = self.http.patch(url, **request_kwargs)
                else:
                    response = self.http.put(url, **request_kwargs)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            # 6. 记录响应
            Loggers.info(f"接口请求响应，状态码: 200")
            Loggers.info(f"响应数据: {json.dumps(response, ensure_ascii=False, indent=2)}")
            
            # 7. ID提取和存储
            # 兼容响应为字典或列表的情况，以及嵌套的列表结构
            extracted_id = None
            if isinstance(response, dict):
                # 安全地获取 data 字段
                data = response.get("data")
                if isinstance(data, dict):
                    # 继续获取嵌套的 data 字段
                    data_obj = data.get("data", {})
                    # 优先提取 id 字段，如果不存在则使用整个对象（兼容不同响应结构）
                    extracted_id = data_obj.get("id") if isinstance(data_obj, dict) and "id" in data_obj else data_obj
                elif isinstance(data, list):
                    # 如果 data 是列表，不提取 id
                    extracted_id = None
                else:
                    # data 是其他类型，尝试提取 id
                    extracted_id = data.get("id") if isinstance(data, dict) and "id" in data else data
            elif isinstance(response, list):
                # 如果响应是列表，不提取 id，返回 None
                extracted_id = None
            else:
                # 其他类型（如字符串、数字等），不提取 id
                extracted_id = None
            
            if store_id_as:
                setattr(self, f"{store_id_as}_id", extracted_id)
            
            return response, extracted_id
            
        except requests.exceptions.HTTPError as e:
            # 统一处理HTTP错误：从异常中提取响应数据并返回，由业务断言来判断是否正确
            if hasattr(e, 'response') and e.response is not None:
                try:
                    response = e.response.json()
                    self.logger.info(f"接口请求响应，状态码: {e.response.status_code}")
                    self.logger.info(f"响应数据: {json.dumps(response, ensure_ascii=False, indent=2)}")
                    Loggers.info(f"接口请求响应，状态码: {e.response.status_code}")
                    Loggers.info(f"响应数据: {json.dumps(response, ensure_ascii=False, indent=2)}")
                    # 错误响应时，extracted_id 为 None
                    return response, None
                except ValueError:
                    # 如果响应不是JSON格式，记录文本内容并抛出异常
                    self.logger.error(f"错误响应不是JSON格式: {e.response.text}")
                    Loggers.error(f"错误响应不是JSON格式: {e.response.text}")
                    raise
            else:
                # 如果没有响应对象，抛出异常
                self.logger.error(f"standard_api_call HTTP请求失败 [{api_key}]: {str(e)}")
                Loggers.error(f"HTTP请求失败: {str(e)}")
                raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f"standard_api_call HTTP请求失败 [{api_key}]: {str(e)}")
            Loggers.error(f"HTTP请求失败: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"standard_api_call 执行失败 [{api_key}]: {str(e)}")
            # Assuming 'a' is an instance of AllureReport or similar, which is not imported.
            # For now, we'll just log the report.
            Loggers.error(f"执行失败: {str(e)}")
            raise


class ConfigValidator:
    """配置验证器（保留向后兼容）"""
    
    @classmethod
    def validate_env_config(cls, config: Dict[str, Any]) -> None:
        """验证环境配置（向后兼容方法）"""
        ConfigManager.validate_config(config)
    
    @classmethod
    def validate_database_config(cls, config: Dict[str, Any]) -> None:
        """验证数据库配置（向后兼容方法）"""
        ConfigManager.validate_config(config)



if __name__ == "__main__":
    try:
        # 测试配置管理器
        print("=== 测试配置管理器 ===")
        config = ConfigManager.get_config()
        safe_config = ConfigManager.get_safe_config(config)
        print("配置加载成功！")
        print(f"配置包含 portal_config: {'portal_config' in config}")
        print(f"配置包含 database: {'database' in config}")
        
        # 测试测试基类
        print("\n=== 测试测试基类 ===")
        BaseTest.setup_class()
        
        # 打印安全的配置信息
        safe_env_config = ConfigManager.get_safe_config(BaseTest.env_config)
        print("环境配置摘要:")
        print(json.dumps(safe_env_config, ensure_ascii=False, indent=2)[:500] + "...")
        
        print("\n基础数据加载状态:", "成功" if BaseTest.init_data else "失败")
        
        if BaseTest.user_info:
            print("\n用户信息:")
            print(f"昵称: {BaseTest.user_info.get('nickname', '未知')}")
            print(f"用户名: {BaseTest.user_info.get('username', '未知')}")
        
        # 测试缓存功能
        print("\n=== 测试配置缓存 ===")
        config_from_cache = ConfigManager.get_config()
        print(f"缓存命中: {config is config_from_cache}")
        
        # 清理缓存
        ConfigManager.clear_cache()
        print("配置缓存已清理")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()