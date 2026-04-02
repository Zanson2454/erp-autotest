"""ERP 数据工厂 SDK 入口。

作用：
1. 为测试代码/服务代码提供统一 Python 调用接口。
2. 统一同步执行、异步执行、能力查询、任务查询。
3. 通过 facade 提供 ``client.master.xxx.run(...)`` 快捷调用。
"""

from typing import Any, Dict, Optional

from erp_data_factory.application.bootstrap import build_runner
from erp_data_factory.application.task_manager import get_task_manager
from erp_data_factory.core.context import ExecutionContext


class _MasterFacade:
    """master 场景快捷门面。

    让调用方可以使用 ``client.master.org.run(...)`` 风格调用，
    不需要每次显式传入 ``scenario_key``。
    """

    def __init__(self, client):
        self._client = client
        self.org = _ScenarioFacade(client, "master.org.run")
        self.material = _ScenarioFacade(client, "master.material.run")
        self.partner = _ScenarioFacade(client, "master.partner.run")


class _ScenarioFacade:
    """单场景门面。

    将固定 ``scenario_key`` 绑定到 ``run``，对外暴露更短的调用路径。
    """

    def __init__(self, client, scenario_key: str):
        self._client = client
        self._scenario_key = scenario_key

    def run(self, payload: Optional[Dict[str, Any]] = None, profile: Optional[str] = None):
        """同步执行当前门面绑定的场景。"""
        return self._client.run(self._scenario_key, payload or {}, profile=profile)


class ERPDataFactoryClient:
    """统一数据工厂客户端。

    对外提供：
    - run: 同步执行场景
    - run_async: 异步执行场景
    - list_capabilities: 查询能力列表
    - get_task: 查询异步任务状态
    """

    def __init__(
        self,
        env: str = "test",
        project: Optional[str] = None,
        profile: str = "default",
        runner=None,
        registry=None,
        no_api_login: bool = False,
    ):
        """初始化客户端并构建运行器。

        参数说明：
        - env/project/profile: 默认执行上下文。
        - runner/registry: 允许注入自定义执行器（测试或扩展场景常用）。
        - no_api_login: 跳过 API 登录，优先走缓存回退链路。
        """
        self.env = env
        self.project = project
        self.profile = profile

        if runner is not None:
            self.runner = runner
        elif registry is not None:
            from erp_data_factory.application.runner import ScenarioRunner

            self.runner = ScenarioRunner(registry)
        else:
            self.runner = build_runner(env=env, project=project, no_api_login=no_api_login)

        self.master = _MasterFacade(self)

    def run(self, scenario_key: str, payload: Optional[Dict[str, Any]] = None, profile: Optional[str] = None):
        """同步执行指定场景并返回 ``ScenarioResult``。"""
        ctx = ExecutionContext(
            env=self.env,
            project=self.project,
            profile=profile or self.profile,
        )
        return self.runner.run(scenario_key=scenario_key, payload=payload or {}, context=ctx)

    def list_capabilities(self):
        """返回已注册场景能力元数据列表。"""
        if not hasattr(self.runner, "registry"):
            return []
        return self.runner.registry.list_capabilities()

    def run_async(
        self, scenario_key: str, payload: Optional[Dict[str, Any]] = None, profile: Optional[str] = None
    ) -> str:
        """异步提交场景执行任务，返回 ``task_id``。"""
        ctx = ExecutionContext(
            env=self.env,
            project=self.project,
            profile=profile or self.profile,
        )
        task_manager = get_task_manager()
        return task_manager.submit(
            run_fn=self.runner.run,
            scenario_key=scenario_key,
            payload=payload or {},
            context=ctx,
        )

    def get_task(self, task_id: str):
        """按 ``task_id`` 查询异步任务快照。"""
        return get_task_manager().get(task_id)
