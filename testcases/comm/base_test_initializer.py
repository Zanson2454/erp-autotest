"""测试基类初始化器 — 负责 BaseTest 中"环境 / 基础数据 / 数据库"阶段。

认证（登录）已迁移至 ``LoginMixin``，由 ``BaseTest._initialize_auth`` 驱动。
"""

import json
import os
from typing import Any, Dict

from erp_data_factory.compat.base import DataFactory
from testcases.comm.config_manager import ConfigManager
from utils.log_util import Loggers
from utils.mysql_util import DBManager


class BaseTestInitializer:
    """测试基类初始化器 — 配置 / 数据 / 数据库。"""

    def __init__(self, env_name: str, project: str = None):
        self.env_name = env_name
        self.project = project or os.getenv("TEST_PROJECT")

    def initialize_environment(self) -> Dict[str, Any]:
        Loggers.info(
            f"初始化环境: {self.env_name}"
            + (f", 项目: {self.project}" if self.project else "")
        )
        config = ConfigManager.get_config(env=self.env_name, project=self.project)

        safe_config = ConfigManager.get_safe_config(config)
        Loggers.info(
            f"环境配置加载成功，配置摘要: "
            f"{json.dumps(safe_config, ensure_ascii=False, indent=2)[:500]}..."
        )

        return config

    def initialize_base_data(self) -> Dict[str, Any]:
        data_factory = DataFactory(env_name=self.env_name, project=self.project)
        raw_data = data_factory.get_base_data(project="erp")
        if not raw_data:
            raise RuntimeError("基础数据获取失败，请检查数据工厂配置和数据库连接！")
        return raw_data

    def initialize_database(self, env_config: Dict[str, Any], db_name: str = "erp_db") -> DBManager:
        db_config = env_config.get("database", {}).get(db_name)
        if not db_config:
            raise RuntimeError(f"数据库配置未找到: {db_name}，请检查环境配置文件")

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
