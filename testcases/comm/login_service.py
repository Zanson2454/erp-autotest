"""登录服务 — 负责门户认证、会话管理与用户信息获取。

从 base_test.py 拆分而来。包含 LoginStatus / LoginResult / SessionManager / LoginService
以及 AuthenticationError。
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Union

import requests
import urllib3

from testcases.comm.config_manager import ConfigManager
from utils.log_util import Loggers

_DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)


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


class SessionManager:
    """会话管理器 - 专门负责HTTP会话，支持多进程隔离"""

    _process_sessions: Dict[int, requests.Session] = {}

    def __init__(self, base_headers: Dict[str, str]):
        self.base_headers = base_headers
        self._ensure_session_for_current_process()

    def _ensure_session_for_current_process(self) -> None:
        process_id = os.getpid()
        if process_id not in self._process_sessions:
            Loggers.info(f"为进程 {process_id} 创建新的会话实例")
            session = requests.Session()
            session.headers.update(self.base_headers)
            self._process_sessions[process_id] = session

    def update_headers(self, headers: Dict[str, str]):
        process_id = os.getpid()
        session = self._process_sessions.get(process_id)
        if session:
            session.headers.update(headers)

    def get_session(self) -> requests.Session:
        process_id = os.getpid()
        self._ensure_session_for_current_process()
        return self._process_sessions[process_id]

    def clear_session(self) -> None:
        process_id = os.getpid()
        if process_id in self._process_sessions:
            Loggers.info(f"清除进程 {process_id} 的会话实例")
            del self._process_sessions[process_id]

    @classmethod
    def clear_all_sessions(cls) -> None:
        cls._process_sessions.clear()
        Loggers.info("已清除所有会话实例")


class LoginService:
    """登录服务 - 专门负责登录逻辑"""

    LOGIN_SUCCESS_CODE = 200
    LOGIN_ENDPOINT = "/iam/api/v1/user/login/account"
    USER_INFO_ENDPOINT = "/api/trantor/portal/user/current"

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session_manager = SessionManager(self.build_headers())
        self.safe_config = ConfigManager.get_safe_config(config)

    @staticmethod
    def build_headers(
        origin: Optional[str] = None,
        referer: Optional[str] = None,
        cookie: Optional[str] = None,
    ) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": _DEFAULT_USER_AGENT,
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": referer,
            "Origin": origin,
        }
        if cookie:
            headers["Cookie"] = cookie
        return headers

    @staticmethod
    def _is_unresolved_env_placeholder(value: str) -> bool:
        return isinstance(value, str) and value.startswith("${") and value.endswith("}")

    @staticmethod
    def _resolve_cookie_from_env(portal_key: str, tenant_key: str = "terp") -> tuple:
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
        ca_bundle = (
            auth_config.get("ca_bundle")
            or os.getenv("TEST_CA_BUNDLE", "").strip()
            or os.getenv("REQUESTS_CA_BUNDLE", "").strip()
        )
        if ca_bundle:
            return ca_bundle

        return self._to_bool(
            auth_config.get("verify_ssl", os.getenv("TEST_VERIFY_SSL")),
            default=True,
        )

    def _configure_session_transport(self, auth_config: Dict[str, Any]) -> None:
        session = self.session_manager.get_session()
        verify = self._resolve_ssl_verify(auth_config)
        session.verify = verify

        if verify is False:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            Loggers.warning("当前 Session 已关闭 HTTPS 证书校验，仅建议测试环境使用")
        else:
            Loggers.info(f"当前 Session HTTPS 校验配置: {verify}")

    def login(self, portal_key, tenant_key="terp") -> LoginResult:
        try:
            auth_config = ConfigManager.get_portal_config(self.config, portal_key, tenant_key)

            if not auth_config:
                Loggers.error(f"未找到门户配置: tenant_key={tenant_key}, portal_key={portal_key}")
                return LoginResult(
                    status=LoginStatus.FAILED,
                    error_message=f"未找到门户配置: {tenant_key}/{portal_key}",
                )

            self._configure_session_transport(auth_config)

            cookie = auth_config.get("cookie", "")

            if self._is_unresolved_env_placeholder(cookie):
                cookie = ""

            if not cookie:
                env_cookie, env_cookie_key = self._resolve_cookie_from_env(portal_key, tenant_key)
                if env_cookie:
                    cookie = env_cookie
                    Loggers.info(f"从环境变量读取 cookie: {env_cookie_key}")

            if cookie:
                Loggers.info("检测到配置了 cookie，使用 cookie 快捷登录")
                Loggers.info(f"Cookie 前50个字符: {cookie[:50]}...")
                self.session_manager.get_session().headers.update({"Cookie": cookie})
            else:
                Loggers.info("未配置 cookie，使用账号密码登录")
                login_url = f"{auth_config.get('iam_url', '').rstrip('/')}{self.LOGIN_ENDPOINT}"
                login_data = {
                    "account": auth_config.get("username", ""),
                    "password": auth_config.get("password", ""),
                    "iam_url": auth_config.get("iam_url", ""),
                    "iam_referer": auth_config.get("iam_referer", ""),
                    "portal_url": auth_config.get("portal_url", ""),
                    "portal_referer": auth_config.get("portal_referer", ""),
                    "description": auth_config.get("description", ""),
                }
                iam_headers = self.build_headers(
                    origin=auth_config.get("iam_url", ""),
                    referer=auth_config.get("iam_referer", ""),
                )
                Loggers.info(f"登录URL: {login_url}")
                Loggers.info(f"登录账号: {login_data['account']}")
                Loggers.info(f"登录请求头: {iam_headers}")
                safe_login_data = login_data.copy()
                if "password" in safe_login_data:
                    safe_login_data["password"] = "******"
                Loggers.info(f"登录数据: {safe_login_data}")
                self.session_manager.update_headers(iam_headers)
                login_response = self.session_manager.get_session().post(
                    login_url, json=login_data, headers=iam_headers
                )

                if not self._is_login_successful(login_response):
                    return LoginResult(
                        status=LoginStatus.FAILED,
                        error_message=f"登录失败: {login_response.text}",
                    )

                cookie = login_response.headers.get("Set-Cookie", "")

            user_info = self._get_user_info(portal_key, tenant_key)
            if not user_info:
                return LoginResult(
                    status=LoginStatus.FAILED,
                    error_message="获取用户信息失败",
                )

            return LoginResult(
                status=LoginStatus.SUCCESS,
                user_info=user_info,
                portal_url=auth_config.get("portal_url", ""),
                iam_url=auth_config.get("iam_url", ""),
                portal_headers=self.build_headers(
                    auth_config.get("portal_url", ""),
                    auth_config.get("portal_referer", ""),
                    cookie=cookie,
                ),
                iam_headers=self.build_headers(
                    auth_config.get("iam_url", ""),
                    auth_config.get("iam_referer", ""),
                ),
                session=self.session_manager.get_session(),
            )
        except Exception as e:
            Loggers.error(f"登录过程异常: {str(e)}")
            return LoginResult(
                status=LoginStatus.FAILED,
                error_message=str(e),
            )

    def _is_login_successful(self, response: requests.Response) -> bool:
        return response.status_code == self.LOGIN_SUCCESS_CODE

    def _get_user_info(self, portal_key, tenant_key="terp") -> Optional[Dict[str, Any]]:
        portal_config = ConfigManager.get_portal_config(self.config, portal_key, tenant_key)
        portal_url = portal_config.get("portal_url", "")
        portal_referer = portal_config.get("portal_referer", "")

        Loggers.info(f"获取用户信息 - portal_referer: {portal_referer}")
        if not portal_url:
            Loggers.error("portal_url 配置缺失，请检查配置文件！")
            return None

        portal_headers = self.build_headers(portal_url, portal_referer)
        url = f"{portal_url}{self.USER_INFO_ENDPOINT}"
        Loggers.info(f"获取用户信息URL: {url}")
        Loggers.info(f"获取用户信息请求头: {portal_headers}")

        self.session_manager.update_headers(portal_headers)

        try:
            session = self.session_manager.get_session()
            Loggers.info(f"Session cookies: {session.cookies.get_dict()}")

            response = session.get(url)
            Loggers.info(f"获取用户信息响应状态码: {response.status_code}")

            if response.status_code == self.LOGIN_SUCCESS_CODE:
                response_data = response.json()
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
