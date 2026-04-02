"""标准 API 调用适配层。

作用：
1. 在不依赖 BaseTest 的场景下复用 ``standard_api_call`` 机制。
2. 负责配置加载、登录会话准备、API 路径与参数解析。
3. 对外提供统一 ``call`` 方法，供场景层直接调用。
"""

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from testcases.comm.api_call_service import ApiCallService
from testcases.comm.config_manager import ConfigManager
from testcases.comm.login_service import LoginService, LoginStatus
from utils.request_util import HttpUtil
from utils.yaml_util import YamlUtil


class _SilentLogger:
    """最小日志占位实现，用于兼容共享 API 组件接口。"""

    def info(self, *_args, **_kwargs):
        return None

    def warning(self, *_args, **_kwargs):
        return None

    def error(self, *_args, **_kwargs):
        return None


class _SilentAssertUtil:
    """断言工具占位实现（空操作），用于兼容调用链。"""

    def set_request_context(self, **_kwargs):
        return None


@dataclass
class _ApiCallContext:
    """API 调用上下文对象，模拟 BaseTest 中被依赖的字段。"""

    http: HttpUtil
    apis: Dict[str, Any]
    api_params: Dict[str, Any]

    def __post_init__(self):
        self.logger = _SilentLogger()
        self.assert_util = _SilentAssertUtil()

    def get_api_path(self, api_key, apis_dict=None):
        """根据 API key 从 YAML 映射中解析接口路径。"""
        target = apis_dict if apis_dict is not None else self.apis
        from testcases.comm.api_client_facade import ApiClientFacade

        return ApiClientFacade.resolve_api_path(target, api_key, logger=self.logger)

    def get_api_params(self, api_path, api_params_dict=None, with_query_params=None):
        """根据接口路径解析参数模板与 URL。"""
        target = api_params_dict if api_params_dict is not None else self.api_params
        from testcases.comm.api_client_facade import ApiClientFacade

        return ApiClientFacade.resolve_api_params(target, api_path, with_query_params)


class StandardApiCaller:
    """标准 API 调用器。

    这是一个薄适配器，核心目标是把测试框架内的 API 调用能力复用于
    数据工厂场景执行流程。
    """

    def __init__(self, env: str = "test", project: Optional[str] = None, no_api_login: bool = False):
        self.env = env
        self.project = project
        self.no_api_login = no_api_login
        self._ctx = self._build_context()

    def _build_context(self) -> _ApiCallContext:
        """构建调用上下文（环境配置、登录态、API 元数据）。"""
        os.environ.setdefault("TEST_ENV", self.env)
        if self.project:
            os.environ["TEST_PROJECT"] = self.project

        config = ConfigManager.get_config(env=self.env, project=self.project)
        YamlUtil.init("config")
        apis = YamlUtil.read_yaml("api/gen_md/md_api_path.yaml")
        api_params = YamlUtil.read_yaml("api/gen_md/md_api_params.yaml")

        if self.no_api_login:
            portal_url = self._portal_url(config)
            http = HttpUtil(url=portal_url)
            return _ApiCallContext(http=http, apis=apis, api_params=api_params)

        login_service = LoginService(config)
        login_result = login_service.login("TERP_PORTAL", tenant_key="terp")
        if login_result.status != LoginStatus.SUCCESS or login_result.session is None:
            raise RuntimeError(f"login failed: {login_result.error_message or 'unknown error'}")

        portal_url = login_result.portal_url or self._portal_url(config)
        http = HttpUtil(url=portal_url, session=login_result.session, headers=login_result.portal_headers)
        return _ApiCallContext(http=http, apis=apis, api_params=api_params)

    @staticmethod
    def _portal_url(config: Dict[str, Any]) -> str:
        """从环境配置中读取 portal_url，并校验非空。"""
        url = config.get("portal_config", {}).get("terp", {}).get("TERP_PORTAL", {}).get("portal_url", "").rstrip("/")
        if not url:
            raise RuntimeError("portal_url is missing in config/env")
        return url

    def call(
        self,
        api_key: str,
        set_dict: Dict[str, Any],
        fields_to_filter: Optional[list] = None,
        method: str = "POST",
    ) -> Tuple[Dict[str, Any], Any]:
        """按共享 ``ApiCallService`` 协议执行一次 API 调用。"""
        return ApiCallService.execute(
            self._ctx,
            api_key=api_key,
            set_dict=set_dict,
            fields_to_filter=fields_to_filter,
            method=method,
        )
