from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, Field
from enum import Enum
from fastapi.responses import JSONResponse
import subprocess
import os
import uuid
import requests

# 钉钉机器人Webhook（请替换为你的真实token）
DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN_HERE"

class ExecType(str, Enum):
    all = "all"
    module = "module"
    file = "file"

class RunTestRequest(BaseModel):
    type: ExecType = Field(..., description="执行类型: all/module/file")
    module: str = Field(None, description="模块名，如 gen")
    file: str = Field(None, description="文件名，不带 .py")

router = APIRouter(prefix="/executor", tags=["用例管理"])

def send_dingtalk_msg(content: str):
    requests.post(DINGTALK_WEBHOOK, json={
        "msgtype": "text",
        "text": {"content": content}
    })

def run_pytest_background(target: str, task_id: str):
    try:
        result = subprocess.run(
            ["pytest", target, "--maxfail=3", "--disable-warnings", "-q"],
            capture_output=True, text=True, timeout=600
        )
        msg = f"[自动化测试完成]\n任务ID: {task_id}\nReturnCode: {result.returncode}\nStdout:\n{result.stdout[-1000:]}\nStderr:\n{result.stderr[-1000:]}"
    except Exception as e:
        msg = f"[自动化测试异常]\n任务ID: {task_id}\nError: {str(e)}"
    send_dingtalk_msg(msg)

@router.post("/run")
async def run_tests(req: RunTestRequest, background_tasks: BackgroundTasks):
    # 构建 pytest 路径
    if req.type == ExecType.all:
        target = "testcases"
    elif req.type == ExecType.module:
        if not req.module:
            return JSONResponse(status_code=400, content={"error": "module 必填"})
        target = f"testcases/{req.module}"
    elif req.type == ExecType.file:
        if not req.module or not req.file:
            return JSONResponse(status_code=400, content={"error": "module 和 file 必填"})
        target = f"testcases/{req.module}/{req.file}.py"
    else:
        return JSONResponse(status_code=400, content={"error": "未知的执行类型"})

    if not os.path.exists(target):
        return JSONResponse(status_code=400, content={"error": f"目标不存在: {target}"})

    task_id = str(uuid.uuid4())
    background_tasks.add_task(run_pytest_background, target, task_id)
    return {"msg": "用例执行已提交", "task_id": task_id} 


if __name__ == "__main__":
    """Todo: 测试用例执行"""
    pass