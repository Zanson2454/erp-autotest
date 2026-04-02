"""ERP 数据工厂 FastAPI 路由层。

作用：
1. 暴露能力列表接口。
2. 暴露场景同步/异步执行接口。
3. 暴露异步任务状态查询接口。
"""

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from erp_data_factory.client import ERPDataFactoryClient

router = APIRouter(prefix="/erp-data-factory/v1", tags=["ERP Data Factory"])


class ScenarioRunRequest(BaseModel):
    """场景执行请求体（同步/异步通用）。"""

    env: str = Field(default="test")
    project: Optional[str] = Field(default=None)
    profile: str = Field(default="default")
    payload: dict = Field(default_factory=dict)
    no_api_login: bool = Field(default=False)


@router.get("/capabilities")
async def list_capabilities():
    """返回当前注册的全部场景能力。"""
    client = ERPDataFactoryClient(no_api_login=True)
    return {"capabilities": client.list_capabilities()}


@router.post("/scenarios/{scenario_key}:run")
async def run_scenario(scenario_key: str, req: ScenarioRunRequest):
    """同步执行场景并返回序列化结果。"""
    client = ERPDataFactoryClient(
        env=req.env,
        project=req.project,
        profile=req.profile,
        no_api_login=req.no_api_login,
    )
    result = client.run(scenario_key=scenario_key, payload=req.payload, profile=req.profile)
    return result.to_dict()


@router.post("/tasks/scenarios/{scenario_key}:run")
async def run_scenario_async(scenario_key: str, req: ScenarioRunRequest):
    """异步执行场景并返回任务 ID。"""
    client = ERPDataFactoryClient(
        env=req.env,
        project=req.project,
        profile=req.profile,
        no_api_login=req.no_api_login,
    )
    task_id = client.run_async(scenario_key=scenario_key, payload=req.payload, profile=req.profile)
    return {"task_id": task_id, "status": "PENDING"}


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """按任务 ID 查询异步执行状态。"""
    client = ERPDataFactoryClient(no_api_login=True)
    task = client.get_task(task_id)
    if task is None:
        return {"task_id": task_id, "status": "NOT_FOUND"}
    return task
