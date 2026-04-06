"""Flow DSL 基类。

职责：
1. 统一封装 Flow 动作中常用的 API 调用入口；
2. Flow 成功后自动注册 cleanup_registry 运行时清理动作；
3. 在测试方法 teardown 阶段触发“谁创建谁清理”。
"""

from typing import Any, Callable, Iterable, Optional

from testcases.comm.cleanup_registry import register_runtime_cleanup


class BaseFlow:
    """所有业务 Flow 的基础能力。"""

    def __init__(self, test_obj: Any):
        self.test = test_obj

    def call_api(self, *args, **kwargs):
        """透传至 BaseTest.standard_api_call，统一保留调用习惯。"""
        return self.test.standard_api_call(*args, **kwargs)

    def register_cleanup_action(self, name: str, action: Callable[[], None], order: int = 500) -> None:
        """注册运行时清理动作。"""
        register_runtime_cleanup(name=name, func=action, order=order)

    def register_db_cleanup(
        self,
        *,
        name: str,
        table: str,
        where: str,
        params: Optional[Iterable[Any]] = None,
        order: int = 500,
        db_attr: str = "db",
    ) -> None:
        """注册数据库删除动作（用于 Flow 创建成功后的回滚/冲销）。"""
        delete_params = list(params or [])

        def _cleanup() -> None:
            db = getattr(self.test, db_attr, None)
            if db is None:
                raise RuntimeError(f"未找到数据库连接属性: {db_attr}")
            db.delete(table=table, where=where, params=delete_params)

        self.register_cleanup_action(name=name, action=_cleanup, order=order)
