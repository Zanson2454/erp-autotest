"""测试清理注册中心。

目标：
1. 聚合分散在各模块 conftest/teardown 的清理逻辑；
2. 在主进程 session 末尾统一执行，减少并发冲突。
"""

import os
from contextvars import ContextVar
from itertools import count
from typing import Any, Callable, Dict, List, Optional, Tuple

_cleanups: List[Tuple[int, str, Callable[[], None]]] = []
_registered_names = set()
_has_run = False
_runtime_cleanup_seq = count(1)
_runtime_cleanups: ContextVar[Optional[List[Tuple[int, int, str, Callable[[], None]]]]] = ContextVar(
    "cleanup_registry_runtime_cleanups", default=None
)


def get_module_db_config(db_name: str = "erp_db") -> Optional[Dict[str, Any]]:
    """各模块 conftest 共用的数据库配置获取。

    避免每个模块重复 DataFactory 初始化逻辑。
    """
    from erp_data_factory.compat.base import DataFactory

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


def reset_runtime_cleanups() -> None:
    """重置当前运行上下文中的动态清理队列（通常在每个测试方法 setup 调用）。"""
    _runtime_cleanups.set([])


def register_runtime_cleanup(name: str, func: Callable[[], None], order: int = 500) -> None:
    """注册当前测试方法生命周期内的动态清理动作。"""
    if not callable(func):
        raise TypeError("register_runtime_cleanup 仅支持可调用对象")
    queue = _runtime_cleanups.get() or []
    queue = list(queue)
    queue.append((order, next(_runtime_cleanup_seq), name, func))
    _runtime_cleanups.set(queue)


def run_runtime_cleanups(logger) -> None:
    """执行当前上下文中的动态清理动作（LIFO + order 优先）。"""
    queue = list(_runtime_cleanups.get() or [])
    if not queue:
        return

    # order 越大优先级越高；同优先级后注册先执行（LIFO）
    queue.sort(key=lambda item: (item[0], item[1]), reverse=True)
    for _order, _seq, name, func in queue:
        try:
            logger.info(f"cleanup_registry(runtime): 开始执行 -> {name}")
            func()
            logger.info(f"cleanup_registry(runtime): 清理完成 -> {name}")
        except Exception as exc:
            logger.warning(f"cleanup_registry(runtime): 清理失败 -> {name}, 错误: {exc}")

    _runtime_cleanups.set([])


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
            logger.warning(f"cleanup_registry: 清理任务失败 -> {name}, 错误: {exc}")
    _has_run = True


def reset_run_state() -> None:
    """重置执行标记，允许在同一进程内再次执行清理。"""
    global _has_run
    _has_run = False
