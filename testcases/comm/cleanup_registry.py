"""测试清理注册中心。

目标：
1. 聚合分散在各模块 conftest/teardown 的清理逻辑；
2. 在主进程 session 末尾统一执行，减少并发冲突。
"""

import os
from typing import Any, Callable, Dict, List, Optional, Tuple

_cleanups: List[Tuple[int, str, Callable[[], None]]] = []
_registered_names = set()
_has_run = False


def get_module_db_config(db_name: str = "erp_db") -> Optional[Dict[str, Any]]:
    """各模块 conftest 共用的数据库配置获取。

    避免每个模块重复 DataFactory 初始化逻辑。
    """
    from data_factory.base import DataFactory

    env = os.getenv("TEST_ENV", "test")
    project = os.getenv("TEST_PROJECT")
    DataFactory(env_name=env, project=project)
    env_config = DataFactory.get_env_config() or {}
    return env_config.get("database", {}).get(db_name)


def register_cleanup(name: str, func: Callable[[], None], order: int = 100) -> None:
    if name in _registered_names:
        return
    _registered_names.add(name)
    _cleanups.append((order, name, func))
    _cleanups.sort(key=lambda item: (item[0], item[1]))


def run_cleanups(logger) -> None:
    global _has_run
    if _has_run:
        logger.info("cleanup_registry: 清理已执行过，跳过重复执行")
        return

    for _order, name, func in _cleanups:
        try:
            logger.info(f"cleanup_registry: 开始执行清理任务 -> {name}")
            func()
            logger.info(f"cleanup_registry: 清理任务完成 -> {name}")
        except Exception as exc:
            logger.error(f"cleanup_registry: 清理任务失败 -> {name}, 错误: {exc}")
    _has_run = True


def reset_run_state() -> None:
    """重置执行标记，允许在同一进程内再次执行清理。"""
    global _has_run
    _has_run = False
