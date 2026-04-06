"""测试基类 — 框架主编排中心。

负责环境初始化、登录上下文、数据库、缓存绑定、标准 API 调用入口。
辅助类（ConfigManager / LoginService / BaseTestInitializer / LoginMixin）
已拆分至同目录独立模块。
"""

import os
import re
import time
import warnings
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pytest

from erp_data_factory.compat.base import DataFactory
from testcases.comm.api_call_service import ApiCallService
from testcases.comm.api_client_facade import ApiClientFacade
from testcases.comm.auth_context import AuthContext
from testcases.comm.base_test_initializer import BaseTestInitializer
from testcases.comm.cleanup_registry import register_runtime_cleanup, reset_runtime_cleanups, run_runtime_cleanups
from testcases.comm.config_manager import ConfigError, ConfigManager
from testcases.comm.data_context import TestDataContext
from testcases.comm.login_mixin import LoginMixin
from testcases.comm.login_service import (
    AuthenticationError,
    LoginResult,
    LoginService,
    LoginStatus,
    SessionManager,
)
from testcases.comm.query_service import QueryService
from testcases.comm.test_context import TestContext
from utils.assert_util import AssertHelper
from utils.cache_util import CacheUtil
from utils.exception_util import safe_api_call
from utils.log_util import Loggers
from utils.mysql_util import DBManager
from utils.request_util import HttpUtil
from utils.yaml_util import YamlUtil

__all__ = [
    "BaseTest",
    "ConfigManager",
    "ConfigError",
    "LoginService",
    "LoginStatus",
    "LoginResult",
    "SessionManager",
    "AuthenticationError",
    "BaseTestInitializer",
]

# 项目根目录（base_test.py → testcases/comm/ → testcases/ → project root）
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class BaseTest(LoginMixin):
    """测试基类 — 支持声明式模块注册与策略化登录。

    子类有两种使用方式：

    **声明式**（推荐）— 设置类变量，无需覆盖 ``setup_class``::

        class ScmDelBaseTest(BaseTest):
            MODULE_NAME = "SCM_DEL"
            LOGIN_STRATEGY = "admin_with_cust"
            API_PATH_FILE = "config/api/scm_del/del_api_path.yaml"
            API_PARAMS_FILE = "config/api/scm_del/del_api_params.yaml"
            SQL_CACHES = [...]

    **命令式**（复杂场景）— 仅设 ``LOGIN_STRATEGY``，其余手动::

        class FinBaseTest(BaseTest):
            LOGIN_STRATEGY = "single"

            @classmethod
            def setup_class(cls):
                super().setup_class()
                cls.load_api_configs()
                cls.load_cache_data()
                cls.bind_context()
    """

    # ─── 声明式模块配置（子类覆盖） ───
    MODULE_NAME: Optional[str] = None
    API_PATH_FILE: Optional[str] = None
    API_PARAMS_FILE: Optional[str] = None
    API_PARAMS_OPTIONAL: bool = False
    SQL_CACHES: List[Dict[str, str]] = []
    STRICT_USER_CONTEXT: bool = True
    TENANT_KEY: str = "terp"

    # ─── 缓存绑定映射 ───
    DEFAULT_CACHE_MAPPINGS: Dict[str, str] = {
        "curr_id": "currency_info.curr_id",
        "coun_id": "country_info.coun_id",
        "addr_id": "addr_info.id",
        "bank_id": "bank_info.bank_id",
        "gen_wc_head_id": "gen_wc_head_info.gen_wc_head_id",
        "cust_id": "partner_info.cust_info.id",
        "sup_id": "partner_info.sup_info.id",
        "com_org_id": "org_info.gr_come_org_info.id",
        "sls_org_id": "org_info.sls_org_info.id",
        "inv_org_id": "org_info.inv_org_info.id",
        "pur_org_id": "org_info.pur_org_info.id",
        "sls_dc_id": "org_info.sls_dc_md.id",
        "wh_id": "org_info.inv_wh_md.id",
        "mat_id": "mat_info.mat_md.FINP.id",
    }
    REQUIRED_CACHE_KEYS: Tuple[str, ...] = ()

    # ─── 类型注解（IDE 可跳转 / 自动补全） ───
    logger: Loggers
    assert_util: AssertHelper
    env_config: Dict[str, Any]
    init_data: Dict[str, Any]
    user_info: Optional[Dict[str, Any]]
    session: Any
    http: HttpUtil
    db: DBManager
    iam_db: DBManager
    mock_util: Any
    cache: CacheUtil
    yaml_util: YamlUtil
    query_service: QueryService
    auth_context: Optional[AuthContext]
    _base_teardown_called: bool = False

    _CAMEL_TO_SNAKE_PATTERN = re.compile(r"(?<!^)(?=[A-Z])")

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

    def __getattr__(self, name: str):
        """兼容路由：将 ``_ensure_xxx`` 映射到已有 ``test_xxx`` 实现。"""
        if name.startswith("_ensure_"):
            test_name = f"test_{name[len('_ensure_'):]}"
            try:
                target = object.__getattribute__(self, test_name)
            except AttributeError as exc:
                raise AttributeError(name) from exc
            if callable(target):

                def _ensure_wrapper(*args, **kwargs):
                    # 同一测试方法上下文内，重复 ensure 调用只执行一次，降低重复造数副作用。
                    sentinel = object()
                    cache_key = f"ensure::{name}::{repr(args)}::{repr(sorted(kwargs.keys()))}"
                    cached = TestDataContext.get_runtime_value(cache_key, sentinel)
                    if cached is not sentinel:
                        return cached
                    result = target(*args, **kwargs)
                    TestDataContext.set_runtime_value(cache_key, result)
                    return result

                return _ensure_wrapper
        raise AttributeError(name)

    def __getattribute__(self, name: str):
        """优先读取当前测试运行时上下文中的动态 ID，降低类属性状态污染风险。"""
        if isinstance(name, str) and not name.startswith("__") and (name.endswith("_id") or name.endswith("Id")):
            sentinel = object()
            runtime_value = TestDataContext.get_runtime_value(name, sentinel)
            if runtime_value is not sentinel:
                return runtime_value

            if name.endswith("_id"):
                base_key = name[:-3]
                runtime_value = TestDataContext.get_runtime_value(base_key, sentinel)
                if runtime_value is not sentinel:
                    return runtime_value
            elif name.endswith("Id"):
                snake_name = self._CAMEL_TO_SNAKE_PATTERN.sub("_", name).lower()
                runtime_value = TestDataContext.get_runtime_value(snake_name, sentinel)
                if runtime_value is not sentinel:
                    return runtime_value
                if snake_name.endswith("_id"):
                    base_key = snake_name[:-3]
                    runtime_value = TestDataContext.get_runtime_value(base_key, sentinel)
                    if runtime_value is not sentinel:
                        return runtime_value

        return object.__getattribute__(self, name)

    # ─────────────────────────────────────────────
    #  setup_class  —  模板方法模式
    # ─────────────────────────────────────────────

    @classmethod
    def setup_class(cls) -> None:
        """测试类初始化 — 模板方法 + 声明式模块注册。

        执行顺序:
            1. 配置  2. 基础数据  3. 数据库  4. 工具类
            5. 认证（策略由 ``LOGIN_STRATEGY`` 决定）
            6. 模块初始化（声明式：API/缓存/上下文自动处理）
            7. 后处理
        """
        try:
            cls._base_teardown_called = False
            env = os.getenv("TEST_ENV", "test")
            project = os.getenv("TEST_PROJECT")
            Loggers.info(
                f"开始初始化测试基类 [env={env}"
                + (f", project={project}" if project else "")
                + f", strategy={cls.LOGIN_STRATEGY}]"
            )

            initializer = BaseTestInitializer(env, project)

            cls._initialize_config(initializer)  # 1. 环境配置
            cls._initialize_data(initializer)  # 2. 基础数据（SQL）
            cls._initialize_database(initializer)  # 3. 数据库连接
            cls._initialize_utilities()  # 4. 工具类
            cls._initialize_auth()  # 5. 登录（策略驱动，单次）
            cls._initialize_module()  # 6. 模块 API / 缓存 / 上下文
            cls._post_initialize()  # 7. 后处理

            Loggers.info("测试基类初始化完成")

        except Exception as e:
            Loggers.error(f"BaseTest初始化失败: {str(e)}")
            raise

    @classmethod
    def _initialize_config(cls, initializer: BaseTestInitializer) -> None:
        cls.env_config = initializer.initialize_environment()

    @classmethod
    def _initialize_data(cls, initializer: BaseTestInitializer) -> None:
        cls.init_data = initializer.initialize_base_data()

    @classmethod
    def _initialize_database(cls, initializer: BaseTestInitializer) -> None:
        cls.db = initializer.initialize_database(cls.env_config, db_name="erp_db")
        cls.iam_db = initializer.initialize_database(cls.env_config, db_name="iam_db")
        # 兼容历史直接调用 DBManager.query(sql) 的写法：同步初始化类级连接配置。
        try:
            erp_db_config = dict((cls.env_config or {}).get("database", {}).get("erp_db", {}) or {})
            if erp_db_config:
                if "user" not in erp_db_config and "username" in erp_db_config:
                    erp_db_config["user"] = erp_db_config.get("username")
                DBManager.init(erp_db_config)
        except Exception as exc:
            Loggers.warning(f"初始化 DBManager 类级配置失败（不影响实例连接）: {exc}")

    @classmethod
    def _initialize_utilities(cls) -> None:
        """工具类初始化 — 核心依赖内建，扩展依赖通过 mixin 注入。"""
        cls.logger = Loggers()
        cls.assert_util = AssertHelper()
        cls.cache = CacheUtil()
        cls.yaml_util = YamlUtil()
        cls.safe_api_call = safe_api_call
        cls.query_service = QueryService(cls.db)
        cls._initialize_optional_utilities()

    @classmethod
    def _initialize_optional_utilities(cls) -> None:
        """按需工具注入扩展点（由 mixin 覆盖）。"""

    @classmethod
    def _initialize_auth(cls) -> None:
        """策略驱动的单次登录 — 由 LoginMixin._do_login 执行。"""
        cls._do_login()
        cls.init_data["user_info"] = {"user_info": cls.user_info}

    # ─── 声明式模块初始化（子类可覆盖各 hook） ───

    @classmethod
    def _initialize_module(cls) -> None:
        """自动处理声明式模块配置。仅当声明式类变量已设置时才执行。

        若子类未设置任何声明式变量且覆盖了 ``setup_class``，视为命令式用法，
        发出迁移建议（DeprecationWarning）以引导统一至声明式路径。
        """
        has_declarative = bool(cls.API_PATH_FILE or cls.SQL_CACHES or cls.MODULE_NAME)
        if not has_declarative:
            for klass in cls.__mro__:
                if "setup_class" in klass.__dict__ and klass is not BaseTest:
                    warnings.warn(
                        f"{klass.__name__} 使用命令式 setup_class 且未设置声明式配置 "
                        "(API_PATH_FILE / SQL_CACHES / MODULE_NAME)。"
                        "建议迁移至声明式模块注册以降低维护成本，"
                        "详见 BaseTest 类文档字符串。",
                        DeprecationWarning,
                        stacklevel=2,
                    )
                    break
            return

        cls._load_module_apis()
        cls._load_module_caches()
        cls._bind_module_context()

    @classmethod
    def _load_module_apis(cls) -> None:
        """Hook: 加载模块 API 路径与参数 YAML。"""
        if not cls.API_PATH_FILE or not cls.API_PARAMS_FILE:
            return
        cls.load_module_api_configs(
            _PROJECT_ROOT / cls.API_PATH_FILE,
            _PROJECT_ROOT / cls.API_PARAMS_FILE,
            api_params_optional=cls.API_PARAMS_OPTIONAL,
        )

    @classmethod
    def _load_module_caches(cls) -> None:
        """Hook: 加载声明式 SQL 缓存。"""
        for cfg in cls.SQL_CACHES:
            sql_path = _PROJECT_ROOT / cfg["path"]
            if cfg.get("optional") and not sql_path.exists():
                setattr(cls, cfg["attr"], {})
                continue
            data = cls.load_sql_cache(
                sql_config_path=sql_path,
                cache_key=cfg["key"],
                db_config_name=cfg.get("db", "erp_db"),
                cache_dir=cfg.get("dir", "testdata/cache"),
            )
            setattr(cls, cfg["attr"], data)

    @classmethod
    def _bind_module_context(cls) -> None:
        """Hook: 绑定缓存数据与用户上下文。子类覆盖此方法以添加自定义绑定逻辑。"""
        if cls.SQL_CACHES:
            cls.bind_cache_data()
        if cls.MODULE_NAME:
            cls.bind_module_user_context(cls.MODULE_NAME, strict=cls.STRICT_USER_CONTEXT)

    @classmethod
    def _post_initialize(cls) -> None:
        if not hasattr(cls, "md_cache_data") or cls.md_cache_data is None:
            cls.md_cache_data = {}

    # ─── 向后兼容 ───

    @classmethod
    def bind_context(cls) -> None:
        """向后兼容：子类 ``bind_context`` 调用 ``super().bind_context()`` 时的安全着陆点。

        实际的缓存绑定和用户上下文已在 ``_bind_module_context`` 中完成（声明式路径），
        或由命令式子类（如 ``FinBaseTest``）自行处理。此方法仅作为链式调用终点。
        """

    @classmethod
    def module_login_single_portal(cls, portal_key: str = "TERP_PORTAL", tenant_key: str = "terp") -> LoginResult:
        """.. deprecated:: 请直接设置 ``LOGIN_STRATEGY`` 类变量。"""
        return cls._login_single_portal(portal_key=portal_key, tenant_key=tenant_key)

    @classmethod
    def module_login_multi_portal(
        cls, portal_type_keys: Dict[str, str], tenant_key: str = "terp"
    ) -> Dict[str, HttpUtil]:
        """.. deprecated:: 请直接设置 ``LOGIN_STRATEGY = 'multi'``。"""
        return cls._login_multi_portal(portal_type_keys, tenant_key=tenant_key)

    @classmethod
    def module_login_admin_with_cust_headers(
        cls,
        admin_portal_key: str = "TERP_PORTAL",
        cust_portal_key: str = "TERP_CUST_PC",
        tenant_key: str = "terp",
    ) -> LoginResult:
        """.. deprecated:: 请直接设置 ``LOGIN_STRATEGY = 'admin_with_cust'``。"""
        return cls._login_admin_with_cust_headers(admin_portal_key, cust_portal_key, tenant_key)

    # ─────────────────────────────────────────────
    #  模块配置 / 缓存 / 用户上下文 辅助
    # ─────────────────────────────────────────────

    @classmethod
    def load_module_api_configs(
        cls,
        api_path_file: Union[str, Path],
        api_params_file: Union[str, Path],
        *,
        api_params_optional: bool = False,
    ) -> None:
        path_file = Path(api_path_file)
        params_file = Path(api_params_file)
        cls.apis = cls.yaml_util.read_yaml(path_file).get("apis", {})
        if api_params_optional and not params_file.exists():
            cls.api_params = {}
        else:
            cls.api_params = cls.yaml_util.read_yaml(params_file).get("api_params", {})

    @classmethod
    def bind_module_user_context(cls, tmodule: str, strict: bool = True) -> None:
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
    def load_sql_cache(
        cls,
        sql_config_path: Union[str, Path],
        cache_key: str,
        db_config_name: str = "erp_db",
        cache_dir: str = "testdata/cache",
    ) -> Any:
        DataFactory.init_sql_cache(
            sql_config_path=str(sql_config_path),
            db_config_name=db_config_name,
            cache_key=cache_key,
            cache_dir=cache_dir,
        )
        return CacheUtil.get(cache_key)

    # ─────────────────────────────────────────────
    #  缓存绑定
    # ─────────────────────────────────────────────

    @classmethod
    def bind_cache_data(
        cls,
        mappings: Dict[str, str] = None,
        required: Optional[List[str]] = None,
        *,
        strict_resolve: bool = False,
    ) -> None:
        """将缓存中的常用 ID 绑定到类属性（见 ``DEFAULT_CACHE_MAPPINGS``）。"""
        mappings = mappings if mappings is not None else cls.DEFAULT_CACHE_MAPPINGS
        if required is None:
            required = list(getattr(cls, "REQUIRED_CACHE_KEYS", ()) or ())
        if os.getenv("TEST_RELAX_CACHE_REQUIREMENTS", "").strip().lower() in ("1", "true", "yes"):
            required = []

        missing: list = []
        for attr_name, path in mappings.items():
            value = cls._resolve_cache_path(path, strict_resolve=strict_resolve)
            setattr(cls, attr_name, value)
            if value is not None:
                cls.logger.debug(f"绑定数据: {attr_name} = {value}")
            elif attr_name in required:
                missing.append(f"{attr_name} ← {path}")

        if missing:
            raise RuntimeError(
                "以下缓存绑定失败（值为 None），请检查 config/erp 中 SQL、库内 AUTOTEST_* 主数据及 .env：\n  - "
                + "\n  - ".join(missing)
                + "\n若仅为本地调试缺少数据，可设置 TEST_RELAX_CACHE_REQUIREMENTS=1 跳过必填校验。"
            )

    @classmethod
    def _resolve_cache_path(cls, path: str, *, strict_resolve: bool = True) -> Any:
        context = TestDataContext.from_class(cls)
        return context.resolve_cache_path(path, logger=cls.logger, strict=strict_resolve)

    # ─────────────────────────────────────────────
    #  teardown
    # ─────────────────────────────────────────────

    @classmethod
    def teardown_class(cls) -> None:
        """测试类结束后关闭资源"""
        try:
            if hasattr(cls, "db") and cls.db:
                try:
                    cls.db.close()
                    Loggers.info("ERP数据库连接已关闭")
                    cls.db = None
                except Exception as e:
                    Loggers.error(f"关闭ERP数据库连接失败: {str(e)}")

            if hasattr(cls, "iam_db") and cls.iam_db:
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

    # ─────────────────────────────────────────────
    #  per-method hooks
    # ─────────────────────────────────────────────

    def setup_method(self, method: Optional[pytest.Function] = None) -> None:
        method_name = getattr(method, "__name__", "unknown_method")
        self.logger.info(f"开始测试方法: {method_name}")
        current_test = os.getenv("PYTEST_CURRENT_TEST", "")
        nodeid = current_test.split(" ", 1)[0] if current_test else None
        if not nodeid:
            nodeid = f"{self.__class__.__module__}::{self.__class__.__name__}::{method_name}"
        tenant_key = getattr(self.__class__, "TENANT_KEY", "terp") or "terp"
        os.environ["TEST_TENANT"] = tenant_key
        TestContext.activate(nodeid=nodeid, tenant_key=tenant_key)
        reset_runtime_cleanups()
        TestDataContext.clear_runtime_values()
        self.test_data = {}
        self.test_start_time = time.time()

    def teardown_method(self, method: Optional[pytest.Function] = None) -> None:
        if hasattr(self, "test_start_time"):
            duration = time.time() - self.test_start_time
            method_name = getattr(method, "__name__", "unknown_method")
            self.logger.info(f"测试方法 {method_name} 执行完成，耗时: {duration:.3f}秒")

        run_runtime_cleanups(self.logger)
        TestDataContext.clear_runtime_values()

        if hasattr(self, "assert_util") and hasattr(self.assert_util, "clear_request_context"):
            self.assert_util.clear_request_context()

    def _async_delay(self, seconds: float, reason: str = "") -> None:
        """统一异步等待封装，替代测试代码中的固定 sleep。"""
        if not hasattr(self, "async_wait_util") or not hasattr(self, "wait_status"):
            raise RuntimeError(
                f"{self.__class__.__name__} 未注入异步等待工具。"
                "请继承 AsyncWaitMixin，或避免调用 _async_delay。"
            )
        start = time.time()

        def check_func():
            elapsed = time.time() - start
            return elapsed >= seconds, {"elapsed": round(elapsed, 3)}, None

        result = self.async_wait_util.wait_for_condition(
            check_func=check_func,
            max_wait=max(seconds + 1.0, 1.0),
            interval=min(max(seconds / 5, 0.2), 1.0),
            timeout_message=f"异步等待超时: {reason or seconds}",
            enable_polling_log=False,
        )
        if result.status != self.wait_status.SUCCESS:
            self.logger.warning(
                f"异步等待未成功: reason={reason or 'delay'}, "
                f"status={result.status.value}, detail={result.error_message}"
            )

    # ─────────────────────────────────────────────
    #  API 解析 / 调用
    # ─────────────────────────────────────────────

    def get_api_path(self, api_key, apis_dict=None):
        if apis_dict is None:
            apis_dict = getattr(self, "apis", None)
        if apis_dict is None:
            raise ValueError("未找到 apis 配置，请检查模块基类是否已加载 API 路径配置")
        return ApiClientFacade.resolve_api_path(apis_dict, api_key, logger=self.logger)

    def set_runtime_id(self, key: str, value: Any) -> Any:
        """写入当前测试方法上下文中的业务 ID，并同步实例属性。"""
        if not key:
            return value
        snake_attr = f"{key}_id"
        camel_attr = f"{key}Id"
        TestDataContext.set_runtime_value(key, value)
        TestDataContext.set_runtime_value(snake_attr, value)
        TestDataContext.set_runtime_value(camel_attr, value)
        setattr(self, snake_attr, value)
        setattr(self, camel_attr, value)
        if hasattr(self, "test_data") and isinstance(self.test_data, dict):
            self.test_data[snake_attr] = value
            self.test_data[camel_attr] = value
        return value

    def get_runtime_id(self, key: str, default: Any = None) -> Any:
        """读取当前测试方法上下文中的业务 ID。"""
        if not key:
            return default
        sentinel = object()
        snake_attr = f"{key}_id"
        camel_attr = f"{key}Id"
        for candidate in (key, snake_attr, camel_attr):
            value = TestDataContext.get_runtime_value(candidate, sentinel)
            if value is not sentinel:
                return value
        return default

    def register_cleanup_action(self, name: str, action, order: int = 500) -> None:
        """注册当前测试方法生命周期内的动态清理动作。"""
        register_runtime_cleanup(name=name, func=action, order=order)

    def get_api_url(self, api_path, with_query_params=None):
        _, url = self.get_api_params(api_path, with_query_params=with_query_params)
        return url

    def get_api_params(self, api_path, api_params_dict=None, with_query_params=None):
        if api_params_dict is None:
            api_params_dict = getattr(self, "api_params", None)
        if api_params_dict is None:
            raise ValueError("未找到 api_params 配置，请检查模块基类是否已加载 API 参数配置")
        return ApiClientFacade.resolve_api_params(api_params_dict, api_path, with_query_params)

    def standard_api_call(
        self,
        api_key,
        set_dict=None,
        fields_to_filter=None,
        store_id_as=None,
        use_param_util=True,
        param_path=None,
        method="POST",
        query_params=None,
        cross_module_name=None,
    ):
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
