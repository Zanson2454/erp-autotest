from fastapi import APIRouter, BackgroundTasks, Request
from pydantic import BaseModel, Field
from enum import Enum
from fastapi.responses import JSONResponse
import subprocess
import os
import uuid
import shutil
from utils.report_util import fix_report_title
import threading
from utils.dingtalk_util import send_dingtalk_msg
import datetime
from typing import Optional

def get_dingtalk_webhook() -> str:
    """获取钉钉机器人 webhook（仅从环境变量读取，禁止硬编码）"""
    return (
        os.getenv("DINGTALK_WEBHOOK")
        or os.getenv("AUTOTEST_DINGTALK_WEBHOOK")
        or ""
    ).strip()

class ExecType(str, Enum):
    all = "all"
    module = "module"
    file = "file"

class RunTestRequest(BaseModel):
    type: ExecType = Field(..., description="执行类型: all/module/file")
    module: Optional[str] = Field(None, description="模块名，如 gen")
    file: Optional[str] = Field(None, description="文件名，不带 .py")
    env: str = Field("test", description="环境配置")
    workers: int = Field(4, description="并行工作进程数")

router = APIRouter(prefix="/executor", tags=["用例执行"])

tasks = {}

def run_tests_background(task_id, target, req):
    try:
        # 1. 复制上一次报告的 history 到 allure-results/history
        report_history = "reports/allure-report/history"
        results_history = "reports/allure-results/history"
        if os.path.exists(report_history):
            shutil.rmtree(results_history, ignore_errors=True)
            shutil.copytree(report_history, results_history)

        # 2. 执行 pytest 按文件并行执行
        pytest_cmd = [
            "pytest", 
            target, 
            "-s", 
            "--log-cli-level=INFO",
            f"--env={req.get('env', 'test')}",
            f"-n={req.get('workers', 4)}",
            "--dist=loadfile",
            "--alluredir=reports/allure-results", 
            "--disable-warnings"
        ]
        pytest_proc = subprocess.run(pytest_cmd, capture_output=True, text=True, timeout=1200)
        tasks[task_id]["pytest"] = pytest_proc.stdout + pytest_proc.stderr
        tasks[task_id]["pytest_returncode"] = pytest_proc.returncode

        # 3. 执行 allure generate 到临时目录
        allure_cmd = ["allure", "generate", "reports/allure-results", "-o", "reports/allure-report-tmp", "--clean", "--report-language", "zh"]
        allure_proc = subprocess.run(allure_cmd, capture_output=True, text=True, timeout=300)
        tasks[task_id]["allure"] = allure_proc.stdout + allure_proc.stderr
        tasks[task_id]["allure_returncode"] = allure_proc.returncode

        # 4. 修改报告标题
        fix_report_title("reports/allure-report-tmp")

        # 5. 原子替换报告目录
        shutil.rmtree("reports/allure-report", ignore_errors=True)
        shutil.move("reports/allure-report-tmp", "reports/allure-report")

        tasks[task_id]["status"] = "success" if pytest_proc.returncode == 0 else "failed"
    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["error"] = str(e)
    finally:
        tasks[task_id]["end_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

@router.post("/run")
async def run_tests(req: RunTestRequest):
    # 1. 生成任务ID
    task_id = str(uuid.uuid4())
    now = datetime.datetime.now()
    tasks[task_id] = {"status": "running", "start_time": now.strftime('%Y-%m-%d %H:%M:%S')}
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
    task = tasks[task_id]
    # 只要任务结束且未通知时，发送钉钉
    if task["status"] in ("success", "failed", "error") and not task.get("notified"):
        msg = (
            f"[自动化测试任务通知]\n"
            f"任务ID: {task_id}\n"
            f"执行状态: {task['status']}\n"
            f"报告入口: https://erp-autotest.app.terminus.io/allure/index.html\n"
            f"开始时间: {task.get('start_time', '-')}, 结束时间: {task.get('end_time', '-')}\n"
        )
        webhook = get_dingtalk_webhook()
        if not webhook:
            task["notified"] = True
            task["notify_skipped"] = "DINGTALK_WEBHOOK 未配置，已跳过钉钉通知"
            return task
        try:
            send_dingtalk_msg(webhook, msg)
            task["notified"] = True
        except Exception as e:
            task["notified"] = False
            task["notify_error"] = str(e)
    return task

if __name__ == "__main__":
    """Todo: 测试用例执行"""
    pass
