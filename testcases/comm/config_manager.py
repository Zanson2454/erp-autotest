"""配置管理器 — 集中管理所有配置相关操作。

从 base_test.py 拆分而来，提供环境配置加载、缓存、验证与脱敏能力。
"""

import json
import os
from typing import Any, Dict

from data_factory.base import DataFactory
from utils.log_util import Loggers


class ConfigError(Exception):
    """配置相关异常"""


class ConfigManager:
    """配置管理器 - 集中管理所有配置相关操作"""

    _config_cache: Dict[str, Dict[str, Any]] = {}

    DEFAULT_CONFIG: Dict[str, Any] = {
        "database": {
            "erp_db": {},
            "iam_db": {},
        },
        "portal_config": {
            "terp": {},
        },
    }

    @classmethod
    def get_config(
        cls, env: str = "test", project: str = None, refresh: bool = False
    ) -> Dict[str, Any]:
        if project is None:
            project = os.getenv("TEST_PROJECT")

        cache_key = f"{env}" if project is None else f"{project}:{env}"

        if cache_key in cls._config_cache and not refresh:
            Loggers.info(
                f"从缓存加载配置 [env={env}"
                + (f", project={project}" if project else "")
                + "]"
            )
            return cls._config_cache[cache_key]

        Loggers.info(
            f"加载新配置 [env={env}"
            + (f", project={project}" if project else "")
            + "]"
        )
        try:
            data_factory = DataFactory(env_name=env, project=project)
            config = data_factory.get_env_config()

            if config is None:
                Loggers.warning(
                    f"配置加载失败，使用默认配置 [env={env}"
                    + (f", project={project}" if project else "")
                    + "]"
                )
                config = cls.DEFAULT_CONFIG.copy()
            else:
                config = cls._merge_configs(cls.DEFAULT_CONFIG, config)

            cls.validate_config(config)
            cls._config_cache[cache_key] = config

            Loggers.info(
                f"配置加载成功 [env={env}"
                + (f", project={project}" if project else "")
                + "]"
            )
            return config

        except Exception as e:
            Loggers.error(
                f"配置加载异常 [env={env}"
                + (f", project={project}" if project else "")
                + f"]: {str(e)}"
            )
            raise RuntimeError(f"配置加载失败: {str(e)}") from e

    @staticmethod
    def _merge_configs(
        default: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        result = default.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigManager._merge_configs(result[key], value)
            else:
                result[key] = value
        return result

    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> None:
        required_structures = [
            ("portal_config", dict),
            ("database", dict),
        ]

        for key, expected_type in required_structures:
            if key not in config or not isinstance(config[key], expected_type):
                raise ValueError(
                    f"配置缺少必要结构: {key} (类型应为 {expected_type.__name__})"
                )

        portal_config = config.get("portal_config", {})
        if "terp" in portal_config:
            terp_config = portal_config["terp"]
            common_portal_keys = ["TERP_PORTAL", "TERP_CUST_PC"]
            for portal_key in common_portal_keys:
                if portal_key in terp_config:
                    portal = terp_config[portal_key]
                    required_keys = ["portal_url", "iam_url"]
                    missing_keys = [k for k in required_keys if not portal.get(k)]
                    if missing_keys:
                        Loggers.warning(
                            f"Portal 配置 [{portal_key}] 缺少可选字段: {missing_keys}"
                        )

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
        safe_config = json.loads(json.dumps(config))

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
        cls._config_cache.clear()
        Loggers.info("配置缓存已清空")

    @classmethod
    def get_portal_config(
        cls, config: Dict[str, Any], portal_key: str, tenant_key: str = "terp"
    ) -> Dict[str, Any]:
        return config.get("portal_config", {}).get(tenant_key, {}).get(portal_key, {})
