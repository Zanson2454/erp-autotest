# 测试基类
import sys
import os
import time
import pytest
import requests
import urllib3
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
from utils.async_wait_util import AsyncWaitUtil, WaitStatus
from data_factory.base import DataFactory 
from utils.mysql_util import DBManager
from testcases.comm.auth_context import AuthContext
from testcases.comm.api_client_facade import ApiClientFacade
from testcases.comm.api_call_service import ApiCallService
from testcases.comm.test_data_context import TestDataContext


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
    def get_config(cls, env: str = "test", project: str = None, refresh: bool = False) -> Dict[str, Any]:
        """
        获取配置，支持缓存和多项目
        
        :param env: 环境名称
        :param project: 项目名称（可选），如果指定则从 config/env/{project}/{env}.yaml 加载
        :param refresh: 是否强制刷新缓存
        :return: 配置字典
        """
        # 从环境变量获取项目名称（如果未通过参数传入）
        if project is None:
            project = os.getenv("TEST_PROJECT")
        
        # 构建缓存键（包含项目信息以支持多项目）
        cache_key = f"{env}" if project is None else f"{project}:{env}"
        
        # 检查缓存
        if cache_key in cls._config_cache and not refresh:
            Loggers.info(f"从缓存加载配置 [env={env}" + (f", project={project}" if project else "") + "]")
            return cls._config_cache[cache_key]
        
        # 加载新配置
        Loggers.info(f"加载新配置 [env={env}" + (f", project={project}" if project else "") + "]")
        try:
            data_factory = DataFactory(env_name=env, project=project)
            config = data_factory.get_env_config()
            
            if config is None:
                Loggers.warning(f"配置加载失败，使用默认配置 [env={env}" + (f", project={project}" if project else "") + "]")
                config = cls.DEFAULT_CONFIG.copy()
            else:
                # 合并默认配置
                config = cls._merge_configs(cls.DEFAULT_CONFIG, config)
            
            # 验证配置
            cls.validate_config(config)
            
            # 缓存配置（使用包含项目的键）
            cls._config_cache[cache_key] = config
            
            Loggers.info(f"配置加载成功 [env={env}" + (f", project={project}" if project else "") + "]")
            return config
            
        except Exception as e:
            Loggers.error(f"配置加载异常 [env={env}" + (f", project={project}" if project else "") + f"]: {str(e)}")
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
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': referer,
            'Origin': origin
        }
        # 只有明确提供了 cookie 时才添加 Cookie header
        # 避免 None 值覆盖 session 中已有的 cookie
        if cookie:
            headers['Cookie'] = cookie
        return headers

    @staticmethod
    def _is_unresolved_env_placeholder(value: str) -> bool:
        """判断配置值是否仍是未替换的环境变量占位符，例如 ${TEST_COOKIE}。"""
        return isinstance(value, str) and value.startswith("${") and value.endswith("}")

    @staticmethod
    def _resolve_cookie_from_env(portal_key: str, tenant_key: str = "terp") -> tuple:
        """
        从环境变量解析 cookie（按优先级）：
        1. TEST_{PORTAL_KEY}_COOKIE（例如 TEST_TERP_PORTAL_COOKIE）
        2. 语义别名：admin/cust
        3. 全局 TEST_COOKIE
        """
        normalized_portal = (portal_key or "").upper()
        normalized_tenant = (tenant_key or "").upper()
        portal_cookie_key = f"TEST_{normalized_portal}_COOKIE" if normalized_portal else ""
        tenant_portal_cookie_key = (
            f"TEST_{normalized_tenant}_{normalized_portal}_COOKIE"
            if normalized_tenant and normalized_portal
            else ""
        )

        alias_map = {
            "TERP_PORTAL": "TEST_ADMIN_COOKIE",
            "TERP_CUST_PC": "TEST_CUST_COOKIE",
        }
        candidates = [
            tenant_portal_cookie_key,
            portal_cookie_key,
            alias_map.get(normalized_portal, ""),
            "TEST_COOKIE",
        ]

        for env_key in candidates:
            if not env_key:
                continue
            env_val = os.getenv(env_key, "").strip()
            if env_val:
                return env_val, env_key

        return "", ""

    @staticmethod
    def _to_bool(value: Any, default: bool = True) -> bool:
        """将环境变量/配置中的布尔值转为 bool。"""
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "y", "on"}:
                return True
            if normalized in {"0", "false", "no", "n", "off"}:
                return False
        return bool(value)

    def _resolve_ssl_verify(self, auth_config: Dict[str, Any]) -> Union[bool, str]:
        """
        解析 requests Session 的 verify 配置。
        优先级：
        1. portal 配置中的 ca_bundle / verify_ssl
        2. TEST_CA_BUNDLE / REQUESTS_CA_BUNDLE
        3. TEST_VERIFY_SSL
        4. 默认 True
        """
        ca_bundle = (
            auth_config.get("ca_bundle")
            or os.getenv("TEST_CA_BUNDLE", "").strip()
            or os.getenv("REQUESTS_CA_BUNDLE", "").strip()
        )
        if ca_bundle:
            return ca_bundle

        return self._to_bool(
            auth_config.get("verify_ssl", os.getenv("TEST_VERIFY_SSL")),
            default=True
        )

    def _configure_session_transport(self, auth_config: Dict[str, Any]) -> None:
        """根据环境配置初始化 Session 的 TLS 校验策略。"""
        session = self.session_manager.get_session()
        verify = self._resolve_ssl_verify(auth_config)
        session.verify = verify

        if verify is False:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            Loggers.warning("当前 Session 已关闭 HTTPS 证书校验，仅建议测试环境使用")
        else:
            Loggers.info(f"当前 Session HTTPS 校验配置: {verify}")

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

            self._configure_session_transport(auth_config)
            
            # 检查是否配置了 cookie（支持直接使用 cookie 登录）
            cookie = auth_config.get("cookie", "")

            # 若配置值仍是占位符（如 ${TEST_TERP_PORTAL_COOKIE}），视为未配置
            if self._is_unresolved_env_placeholder(cookie):
                cookie = ""

            # 支持直接从环境变量兜底获取 cookie（含 TEST_COOKIE）
            if not cookie:
                env_cookie, env_cookie_key = self._resolve_cookie_from_env(portal_key, tenant_key)
                if env_cookie:
                    cookie = env_cookie
                    Loggers.info(f"从环境变量读取 cookie: {env_cookie_key}")
            
            if cookie:
                # ============ 方式1：使用 cookie 快捷登录 ============
                Loggers.info("检测到配置了 cookie，使用 cookie 快捷登录")
                Loggers.info(f"Cookie 前50个字符: {cookie[:50]}...")
                
                # 设置 cookie 到 session，后续所有请求都会自动带上
                self.session_manager.get_session().headers.update({"Cookie": cookie})
                
            else:
                # ============ 方式2：使用账号密码登录（原有逻辑，完整保留） ============
                Loggers.info("未配置 cookie，使用账号密码登录")
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
    
    def __init__(self, env_name: str, project: str = None):
        """
        初始化测试基类初始化器
        
        :param env_name: 环境名称
        :param project: 项目名称（可选），如果未指定则从环境变量 TEST_PROJECT 获取
        """
        self.env_name = env_name
        # 从环境变量获取项目名称（如果未通过参数传入）
        self.project = project or os.getenv("TEST_PROJECT")
    
    def initialize_environment(self) -> Dict[str, Any]:
        """初始化环境配置"""
        Loggers.info(f"初始化环境: {self.env_name}" + (f", 项目: {self.project}" if self.project else ""))
        # 使用 ConfigManager 获取配置
        config = ConfigManager.get_config(env=self.env_name, project=self.project)
        
        # 打印安全的配置信息
        safe_config = ConfigManager.get_safe_config(config)
        Loggers.info(f"环境配置加载成功，配置摘要: {json.dumps(safe_config, ensure_ascii=False, indent=2)[:500]}...")
        
        return config
    
    def initialize_base_data(self) -> Dict[str, Any]:
        """初始化基础数据"""
        # 创建 DataFactory 实例（传递项目参数）
        data_factory = DataFactory(env_name=self.env_name, project=self.project)
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

    # 默认缓存绑定映射：attr_name → 点分路径
    # 子类可整体替换或调用 bind_cache_data(custom_mappings) 覆盖，无需改此处
    DEFAULT_CACHE_MAPPINGS: Dict[str, str] = {
        # init_data
        "curr_id":        "currency_info.curr_id",
        "coun_id":        "country_info.coun_id",
        "addr_id":        "addr_info.id",
        "bank_id":        "bank_info.bank_id",
        "gen_wc_head_id": "gen_wc_head_info.gen_wc_head_id",
        "calender_id":    "calender_info.id",
        # md_cache_data
        "cust_id":        "partner_info.cust_info.id",
        "sup_id":         "partner_info.sup_info.id",
        "com_org_id":     "org_info.gr_come_org_info.id",
        "sls_org_id":     "org_info.sls_org_info.id",
        "inv_org_id":     "org_info.inv_org_info.id",
        "pur_org_id":     "org_info.pur_org_info.id",
        "sls_dc_id":      "org_info.sls_dc_md.id",
        "wh_id":          "org_info.inv_wh_md.id",
        "mat_id":         "mat_info.mat_md.FINP.id",
    }

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
    auth_context: Any
    _base_teardown_called: bool = False

    def __init_subclass__(cls, **kwargs):
        """兜底保障：子类即便未显式调用 super().teardown_class()，也会执行基类资源清理。"""
        super().__init_subclass__(**kwargs)

        raw_teardown = cls.__dict__.get("teardown_class")
        if raw_teardown is None:
            return

        original = raw_teardown.__func__ if isinstance(raw_teardown, classmethod) else raw_teardown
        if getattr(original, "_base_teardown_wrapped", False):
            return

        @wraps(original)
        def wrapped(sub_cls, *args, **kwargs):
            try:
                return original(sub_cls, *args, **kwargs)
            finally:
                if not getattr(sub_cls, "_base_teardown_called", False):
                    BaseTest.teardown_class.__func__(sub_cls)

        wrapped._base_teardown_wrapped = True
        cls.teardown_class = classmethod(wrapped)
    
    @classmethod
    def setup_class(cls) -> None:
        """测试类初始化 - 模板方法模式优化"""
        try:
            cls._base_teardown_called = False
            # 获取环境和项目
            env = os.getenv("TEST_ENV", "test")
            project = os.getenv("TEST_PROJECT")
            Loggers.info(f"开始初始化测试基类 [env={env}" + (f", project={project}" if project else "") + "]")

            # 使用初始化器（传递项目参数）
            initializer = BaseTestInitializer(env, project)

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
        cls.auth_context = AuthContext.from_login_result(login_result)
        cls.user_info = cls.auth_context.user_info
        cls.session = cls.auth_context.session
        cls.http = HttpUtil(
            url=cls.auth_context.portal_url,
            session=cls.auth_context.session,
            headers=cls.auth_context.portal_headers
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
        # 兜底初始化，避免部分模块直接访问该属性时报 AttributeError
        if not hasattr(cls, "md_cache_data") or cls.md_cache_data is None:
            cls.md_cache_data = {}

    @classmethod
    def module_login_single_portal(cls, portal_key: str = "TERP_PORTAL", tenant_key: str = "terp"):
        """
        模块基类通用：登录单门户并初始化 http（最小封装，保持现有结构）
        """
        cls.login_service = LoginService(cls.env_config)
        result = cls.login_service.login(portal_key=portal_key, tenant_key=tenant_key)
        if result.status != result.status.SUCCESS:
            raise RuntimeError(f"{portal_key} 登录失败: {result.error_message}")

        cls.http = HttpUtil(
            url=result.portal_url,
            session=result.session,
            headers=result.portal_headers
        )
        cls.admin_session = result.session
        cls.admin_user_info = result.user_info
        cls.admin_headers = result.portal_headers
        return result

    @classmethod
    def module_login_multi_portal(cls, portal_type_keys: Dict[str, str], tenant_key: str = "terp"):
        """
        模块基类通用：多门户登录并初始化 sessions/user_infos/http_clients
        """
        cls.login_service = LoginService(cls.env_config)
        cls.sessions = {}
        cls.user_infos = {}
        cls.http_clients = {}
        cls.portal_urls = {}
        cls.portal_headers = {}

        for role, portal_key in portal_type_keys.items():
            result = cls.login_service.login(portal_key=portal_key, tenant_key=tenant_key)
            if result.status != result.status.SUCCESS:
                raise RuntimeError(f"{role} 登录失败: {result.error_message}")

            portal_url = result.portal_url or ""
            if not isinstance(portal_url, str) or not portal_url:
                raise ValueError(f"{role} portal_url 不能为空且必须为字符串")

            cls.sessions[role] = result.session
            cls.user_infos[role] = result.user_info
            cls.portal_urls[role] = portal_url
            cls.portal_headers[role] = result.portal_headers
            cls.http_clients[role] = HttpUtil(
                url=portal_url,
                session=result.session,
                headers=result.portal_headers
            )

        return cls.http_clients

    @classmethod
    def module_login_admin_with_cust_headers(
        cls,
        admin_portal_key: str = "TERP_PORTAL",
        cust_portal_key: str = "TERP_CUST_PC",
        tenant_key: str = "terp",
    ) -> LoginResult:
        """
        模块基类通用：登录 admin 门户，并初始化 admin/cust headers。
        """
        admin_result = cls.module_login_single_portal(
            portal_key=admin_portal_key,
            tenant_key=tenant_key,
        )
        cls.admin_headers = admin_result.portal_headers
        cls.cust_portal_headers = cls.admin_headers.copy() if cls.admin_headers else {}
        cust_portal_referer = (
            cls.env_config
            .get("portal_config", {})
            .get(tenant_key, {})
            .get(cust_portal_key, {})
            .get("portal_referer")
        )
        cls.cust_portal_headers["Referer"] = cust_portal_referer
        cls.logger.info(f"cust_portal_headers: {cls.cust_portal_headers}")
        return admin_result

    @classmethod
    def load_module_api_configs(
        cls,
        api_path_file: Union[str, Path],
        api_params_file: Union[str, Path],
        *,
        api_params_optional: bool = False
    ) -> None:
        """
        模块基类通用：加载 apis/api_params
        """
        path_file = Path(api_path_file)
        params_file = Path(api_params_file)
        cls.apis = cls.yaml_util.read_yaml(path_file).get("apis", {})
        if api_params_optional and not params_file.exists():
            cls.api_params = {}
        else:
            cls.api_params = cls.yaml_util.read_yaml(params_file).get("api_params", {})

    @classmethod
    def bind_module_user_context(cls, tmodule: str, strict: bool = True) -> None:
        """
        模块基类通用：设置 path_params/nickname/user_id
        """
        cls.path_params = {"tmodule": tmodule}
        if strict:
            user_info = cls.init_data["user_info"]["user_info"]
            cls.nickname = user_info["nickname"]
            cls.user_id = user_info["id"]
            return

        user_info = (cls.init_data or {}).get("user_info", {}).get("user_info", {})
        cls.nickname = user_info.get("nickname")
        cls.user_id = user_info.get("id")
        if cls.nickname is None or cls.user_id is None:
            cls.logger.warning("init_data 中未找到完整 user_info，nickname 或 user_id 为 None")

    @classmethod
    def bind_mock_util_singleton(cls) -> None:
        """
        模块基类通用：绑定 mock_util 单例。
        """
        if getattr(cls, "_mock_instance", None) is None:
            cls._mock_instance = MockData()
        cls.mock_util = cls._mock_instance

    @classmethod
    def load_sql_cache(
        cls,
        sql_config_path: Union[str, Path],
        cache_key: str,
        db_config_name: str = "erp_db",
        cache_dir: str = "testdata/cache",
    ) -> Any:
        """
        模块基类通用：执行 SQL 缓存初始化并返回缓存数据。
        """
        DataFactory.init_sql_cache(
            sql_config_path=str(sql_config_path),
            db_config_name=db_config_name,
            cache_key=cache_key,
            cache_dir=cache_dir,
        )
        return CacheUtil.get(cache_key)

    @classmethod
    def bind_cache_data(cls, mappings: Dict[str, str] = None) -> None:
        """简化数据绑定 - 一行代码获取常用数据。

        不传参时使用 cls.DEFAULT_CACHE_MAPPINGS（子类可整体替换）。
        传参时使用传入的 mappings（支持增量扩展）。

        路径格式：
            "currency_info.curr_id"     → init_data["currency_info"][0]["curr_id"]
            "partner_info.cust_info.id" → md_cache_data["partner_info"]["cust_info"][0]["id"]
            "pur_cache_data.xxx.id"     → pur_cache_data["xxx"][0]["id"]
                                          （需先调用 TestDataContext.register_source(...)）
        """
        mappings = mappings if mappings is not None else cls.DEFAULT_CACHE_MAPPINGS
        
        for attr_name, path in mappings.items():
            value = cls._resolve_cache_path(path)
            setattr(cls, attr_name, value)
            if value is not None:
                cls.logger.debug(f"绑定数据: {attr_name} = {value}")
    
    @classmethod
    def _resolve_cache_path(cls, path: str) -> Any:
        """
        解析缓存路径，支持 init_data 和 md_cache_data
        
        Args:
            path: 路径字符串，如 "currency_info.curr_id" 或 "partner_info.cust_info.id"
            
        Returns:
            解析后的值，路径无效返回 None
        """
        context = TestDataContext.from_class(cls)
        return context.resolve_cache_path(path, logger=cls.logger)
    
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
                    cls.db = None
                except Exception as e:
                    Loggers.error(f"关闭ERP数据库连接失败: {str(e)}")
            
            if hasattr(cls, 'iam_db') and cls.iam_db:
                try:
                    cls.iam_db.close()
                    Loggers.info("IAM数据库连接已关闭")
                    cls.iam_db = None
                except Exception as e:
                    Loggers.error(f"关闭IAM数据库连接失败: {str(e)}")
        except Exception as e:
            Loggers.error(f"teardown_class执行失败: {str(e)}")
        finally:
            cls._base_teardown_called = True
    
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

    def get_api_path(self, api_key, apis_dict=None):
        """
        获取API路径
        Args:
            api_key: API键名
            apis_dict: API配置字典（可选，不传时默认读取 self.apis）
        Returns:
            str: API路径
        """
        if apis_dict is None:
            apis_dict = getattr(self, "apis", None)
        if apis_dict is None:
            raise ValueError("未找到 apis 配置，请检查模块基类是否已加载 API 路径配置")
        return ApiClientFacade.resolve_api_path(apis_dict, api_key, logger=self.logger)

    def get_api_url(self, api_path, with_query_params=None):
        """
        根据API路径返回请求URL（相对路径，交由 HttpUtil 拼接 base_url）。
        """
        _, url = self.get_api_params(api_path, with_query_params=with_query_params)
        return url
    
    def get_api_params(self, api_path, api_params_dict=None, with_query_params=None):
        """
        获取API请求参数和完整URL
        Args:
            api_path: API路径
            api_params_dict: API参数配置字典（可选，不传时默认读取 self.api_params）
            with_query_params: 查询参数
        Returns:
            tuple: (参数模板, 完整URL)
        """
        if api_params_dict is None:
            api_params_dict = getattr(self, "api_params", None)
        if api_params_dict is None:
            raise ValueError("未找到 api_params 配置，请检查模块基类是否已加载 API 参数配置")
        return ApiClientFacade.resolve_api_params(api_params_dict, api_path, with_query_params)
    
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
    def standard_api_call(self, api_key, set_dict=None, fields_to_filter=None, store_id_as=None, use_param_util=True, param_path=None, method="POST", query_params=None, cross_module_name=None):
        return ApiCallService.execute(
            self,
            api_key=api_key,
            set_dict=set_dict,
            fields_to_filter=fields_to_filter,
            store_id_as=store_id_as,
            use_param_util=use_param_util,
            param_path=param_path,
            method=method,
            query_params=query_params,
            cross_module_name=cross_module_name,
        )

