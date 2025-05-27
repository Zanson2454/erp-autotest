from fastapi import APIRouter, BackgroundTasks, Request
from pydantic import BaseModel, Field
from enum import Enum
from fastapi.responses import JSONResponse
import subprocess
import os
import uuid
import requests
import shutil
from utils.fix_report import fix_report_title
import threading

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

router = APIRouter(prefix="/executor", tags=["用例执行"])

tasks = {}

def send_dingtalk_msg(content: str):
    requests.post(DINGTALK_WEBHOOK, json={
        "msgtype": "text",
        "text": {"content": content}
    })

def run_tests_background(task_id, target, req):
    try:
        # 1. 执行 pytest
        pytest_cmd = ["pytest", target, "--alluredir=reports/allure-results", "--disable-warnings", "-q"]
        pytest_proc = subprocess.run(pytest_cmd, capture_output=True, text=True, timeout=1200)
        tasks[task_id]["pytest"] = pytest_proc.stdout + pytest_proc.stderr
        tasks[task_id]["pytest_returncode"] = pytest_proc.returncode

        # 2. 执行 allure generate 到临时目录
        allure_cmd = ["allure", "generate", "reports/allure-results", "-o", "reports/allure-report-tmp", "--clean"]
        allure_proc = subprocess.run(allure_cmd, capture_output=True, text=True, timeout=300)
        tasks[task_id]["allure"] = allure_proc.stdout + allure_proc.stderr
        tasks[task_id]["allure_returncode"] = allure_proc.returncode

        # 3. 原子替换报告目录
        shutil.rmtree("reports/allure-report", ignore_errors=True)
        shutil.move("reports/allure-report-tmp", "reports/allure-report")

        tasks[task_id]["status"] = "success" if pytest_proc.returncode == 0 else "failed"
    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["error"] = str(e)

@router.post("/run")
async def run_tests(req: RunTestRequest):
    # 1. 生成任务ID
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "running"}
    # 2. 解析目标
    if req.type == ExecType.all:
        target = "testcases"
    elif req.type == ExecType.module:
        if not req.module:
            return JSONResponse(status_code=400, content={"error": "module 必填"})
        target = f"testcases/{req.module}"
    elif req.type == ExecType.file:
        if not req.module or not req.file:
            return JSONResponse(status_code=400, content={"error": "module 和 file 必填"})
        target = f"testcases/{req.module}/{req.file}"
    else:
        return JSONResponse(status_code=400, content={"error": "type参数非法"})
    # 3. 启动后台线程
    thread = threading.Thread(target=run_tests_background, args=(task_id, target, req.dict()))
    thread.start()
    # 4. 立即返回
    return {"task_id": task_id, "status": "started"}

@router.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks:
        return JSONResponse(status_code=404, content={"error": "任务不存在"})
    return tasks[task_id]

if __name__ == "__main__":
    """Todo: 测试用例执行"""
    pass