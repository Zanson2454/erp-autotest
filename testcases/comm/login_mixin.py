"""登录策略 Mixin — 从 BaseTest 拆分，提供三种门户登录策略。

策略选择由 ``LOGIN_STRATEGY`` 类变量驱动：
- ``"single"`` / ``"default"`` — 单门户登录（默认 TERP_PORTAL）
- ``"admin_with_cust"`` — Admin 登录 + 客户门户 Headers
- ``"multi"`` — 多门户登录（每个门户独立 session）

所有方法要求 ``cls.env_config`` 已就绪（由 BaseTest._initialize_config 保证）。
"""

from typing import Any, Dict, Optional

from testcases.comm.auth_context import AuthContext
from testcases.comm.login_service import LoginResult, LoginService, LoginStatus
from utils.log_util import Loggers
from utils.request_util import HttpUtil


class LoginMixin:
    """门户登录策略方法集，通过多继承注入 BaseTest。"""

    # 子类覆盖以选择登录策略
    LOGIN_STRATEGY: str = "default"
    TENANT_KEY: str = "terp"
    _PORTAL_TYPE_KEYS: Dict[str, str] = {"admin": "TERP_PORTAL"}

    # 由 _login_* 方法设置的属性（类型注解供 IDE）
    env_config: Dict[str, Any]
    http: Any
    auth_context: Optional[AuthContext]
    user_info: Optional[Dict[str, Any]]
    session: Any

    # ─── 单门户 ───

    @classmethod
    def _login_single_portal(
        cls, portal_key: str = "TERP_PORTAL", tenant_key: str = "terp"
    ) -> LoginResult:
        login_service = LoginService(cls.env_config)
        result = login_service.login(portal_key=portal_key, tenant_key=tenant_key)
        if result.status != LoginStatus.SUCCESS:
            raise RuntimeError(f"{portal_key} 登录失败: {result.error_message}")

        cls.http = HttpUtil(
            url=result.portal_url,
            session=result.session,
            headers=result.portal_headers,
        )
        cls.auth_context = AuthContext.from_login_result(result)
        cls.user_info = cls.auth_context.user_info
        cls.session = cls.auth_context.session
        cls.admin_session = result.session
        cls.admin_user_info = result.user_info
        cls.admin_headers = result.portal_headers
        return result

    # ─── Admin + 客户 Headers ───

    @classmethod
    def _login_admin_with_cust_headers(
        cls,
        admin_portal_key: str = "TERP_PORTAL",
        cust_portal_key: str = "TERP_CUST_PC",
        tenant_key: str = "terp",
    ) -> LoginResult:
        result = cls._login_single_portal(
            portal_key=admin_portal_key, tenant_key=tenant_key
        )
        cls.cust_portal_headers = cls.admin_headers.copy() if cls.admin_headers else {}
        cust_portal_referer = (
            cls.env_config
            .get("portal_config", {})
            .get(tenant_key, {})
            .get(cust_portal_key, {})
            .get("portal_referer")
        )
        cls.cust_portal_headers["Referer"] = cust_portal_referer
        Loggers.info(f"cust_portal_headers 已设置: Referer={cust_portal_referer}")
        return result

    # ─── 多门户 ───

    @classmethod
    def _login_multi_portal(
        cls, portal_type_keys: Dict[str, str], tenant_key: str = "terp"
    ) -> Dict[str, HttpUtil]:
        login_service = LoginService(cls.env_config)
        cls.sessions: Dict[str, Any] = {}
        cls.user_infos: Dict[str, Any] = {}
        cls.http_clients: Dict[str, HttpUtil] = {}
        cls.portal_urls: Dict[str, str] = {}
        cls.portal_headers: Dict[str, Dict[str, str]] = {}

        first_result: Optional[LoginResult] = None

        for role, portal_key in portal_type_keys.items():
            result = login_service.login(portal_key=portal_key, tenant_key=tenant_key)
            if result.status != LoginStatus.SUCCESS:
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
                headers=result.portal_headers,
            )

            if first_result is None:
                first_result = result

        # 设置 admin 兼容属性
        if "admin" in cls.http_clients and first_result is not None:
            cls.http = cls.http_clients["admin"]
            cls.auth_context = AuthContext.from_login_result(first_result)
            cls.user_info = first_result.user_info
            cls.session = first_result.session
            cls.admin_session = cls.sessions.get("admin")
            cls.admin_user_info = cls.user_infos.get("admin")
            cls.admin_headers = cls.portal_headers.get("admin")

        # 设置 cust 兼容属性
        if "cust" in cls.http_clients:
            cls.http_cust = cls.http_clients["cust"]
            cls.cust_session = cls.sessions.get("cust")
            cls.cust_user_info = cls.user_infos.get("cust")
            cls.cust_headers = cls.portal_headers.get("cust")

        return cls.http_clients

    # ─── 统一入口（由 BaseTest._initialize_auth 调用）───

    @classmethod
    def _do_login(cls) -> None:
        """根据 LOGIN_STRATEGY + _PORTAL_TYPE_KEYS 执行唯一一次登录。"""
        strategy = cls.LOGIN_STRATEGY
        portal_keys = cls._PORTAL_TYPE_KEYS
        tenant_key = getattr(cls, "TENANT_KEY", "terp") or "terp"

        if strategy == "multi":
            cls._login_multi_portal(portal_keys, tenant_key=tenant_key)
        elif strategy == "admin_with_cust":
            admin_key = portal_keys.get("admin", "TERP_PORTAL")
            cust_key = portal_keys.get("cust", "TERP_CUST_PC")
            cls._login_admin_with_cust_headers(admin_key, cust_key, tenant_key=tenant_key)
        else:  # "default" / "single"
            admin_key = portal_keys.get("admin", "TERP_PORTAL")
            cls._login_single_portal(admin_key, tenant_key=tenant_key)
