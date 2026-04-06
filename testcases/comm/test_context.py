"""测试运行时上下文（支持 worker/nodeid/tenant 三维隔离）。"""

import os
from contextvars import ContextVar
from typing import Any, Dict, Optional

__test__ = False


class TestContext:
    """用例级运行时上下文。

    命名空间格式：``{worker_id}:{nodeid}:{tenant_key}``
    """

    _STORE: ContextVar[Optional[Dict[str, Dict[str, Any]]]] = ContextVar("test_context_store", default=None)
    _ACTIVE_NS: ContextVar[str] = ContextVar("test_context_active_namespace", default="master:global:terp")

    @classmethod
    def _current_test_nodeid(cls) -> str:
        current = os.getenv("PYTEST_CURRENT_TEST", "")
        if not current:
            return "global"
        return current.split(" ", 1)[0] or "global"

    @classmethod
    def compose_namespace(
        cls,
        *,
        worker_id: Optional[str] = None,
        nodeid: Optional[str] = None,
        tenant_key: Optional[str] = None,
    ) -> str:
        worker = (worker_id or os.getenv("PYTEST_XDIST_WORKER") or "master").strip()
        node = (nodeid or cls._current_test_nodeid() or "global").strip()
        tenant = (tenant_key or os.getenv("TEST_TENANT") or "terp").strip()
        return f"{worker}:{node}:{tenant}"

    @classmethod
    def activate(
        cls,
        *,
        worker_id: Optional[str] = None,
        nodeid: Optional[str] = None,
        tenant_key: Optional[str] = None,
    ) -> str:
        namespace = cls.compose_namespace(worker_id=worker_id, nodeid=nodeid, tenant_key=tenant_key)
        store = dict(cls._STORE.get() or {})
        if namespace not in store:
            store[namespace] = {}
        cls._STORE.set(store)
        cls._ACTIVE_NS.set(namespace)
        return namespace

    @classmethod
    def current_namespace(cls) -> str:
        return cls._ACTIVE_NS.get()

    @classmethod
    def clear(cls) -> None:
        namespace = cls.current_namespace()
        store = dict(cls._STORE.get() or {})
        store[namespace] = {}
        cls._STORE.set(store)

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        if not key:
            return
        namespace = cls.current_namespace()
        store = dict(cls._STORE.get() or {})
        bucket = dict(store.get(namespace, {}))
        bucket[key] = value
        store[namespace] = bucket
        cls._STORE.set(store)

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        namespace = cls.current_namespace()
        store = cls._STORE.get() or {}
        return (store.get(namespace) or {}).get(key, default)

    @classmethod
    def snapshot(cls) -> Dict[str, Any]:
        namespace = cls.current_namespace()
        store = cls._STORE.get() or {}
        return dict(store.get(namespace) or {})
