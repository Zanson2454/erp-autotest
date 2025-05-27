from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, Field
from enum import Enum
from fastapi.responses import JSONResponse
import subprocess
import os
import uuid
import requests
import shutil

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

def send_dingtalk_msg(content: str):
    requests.post(DINGTALK_WEBHOOK, json={
        "msgtype": "text",
        "text": {"content": content}
    })

def run_pytest_background(target: str, task_id: str):
    try:
        results_dir = "reports/allure-results"
        report_dir = "reports/allure-report"
        history_dir = os.path.join(report_dir, "history")
        results_history_dir = os.path.join(results_dir, "history")

        # 0. 清空 allure-results 目录
        if os.path.exists(results_dir):
            shutil.rmtree(results_dir)
        os.makedirs(results_dir, exist_ok=True)

        # 1. 复制上一次报告的 history 到 allure-results/history
        if os.path.exists(history_dir):
            shutil.copytree(history_dir, results_history_dir, dirs_exist_ok=True)

        # 2. 运行 pytest，生成 allure-results
        result = subprocess.run(
            ["pytest", target, "--alluredir=reports/allure-results", "--maxfail=3", "--disable-warnings", "-q"],
            capture_output=True, text=True, timeout=600
        )
        # 3. 生成 Allure HTML 报告
        gen_result = subprocess.run(
            ["allure", "generate", "reports/allure-results", "-o", "reports/allure-report", "--clean"],
            capture_output=True, text=True, timeout=120
        )
        msg = (
            f"[自动化测试完成]\n任务ID: {task_id}\n"
            f"ReturnCode: {result.returncode}\n"
            f"AllureGenCode: {gen_result.returncode}\n"
            f"AllureGenOut: {gen_result.stdout[-1000:]}\n"
            f"AllureGenErr: {gen_result.stderr[-1000:]}\n"
            f"Stdout:\n{result.stdout[-1000:]}\nStderr:\n{result.stderr[-1000:]}"
        )
    except Exception as e:
        msg = f"[自动化测试异常]\n任务ID: {task_id}\nError: {str(e)}"
    send_dingtalk_msg(msg)

@router.post("/run")
async def run_tests(req: RunTestRequest):
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

    results_dir = "reports/allure-results"
    report_dir = "reports/allure-report"
    history_dir = os.path.join(report_dir, "history")
    results_history_dir = os.path.join(results_dir, "history")

    # 0. 清空 allure-results 目录
    if os.path.exists(results_dir):
        shutil.rmtree(results_dir)
    os.makedirs(results_dir, exist_ok=True)

    # 1. 复制上一次报告的 history 到 allure-results/history
    if os.path.exists(history_dir):
        shutil.copytree(history_dir, results_history_dir, dirs_exist_ok=True)

    # 2. 运行 pytest，生成 allure-results
    try:
        result = subprocess.run(
            ["pytest", target, "--alluredir=reports/allure-results", "--maxfail=3", "--disable-warnings", "-q"],
            capture_output=True, text=True, timeout=600
        )
    except Exception as e:
        send_dingtalk_msg(f"[自动化测试异常]\nError: {str(e)}")
        return JSONResponse(status_code=500, content={"error": f"pytest 执行异常: {str(e)}"})

    # 3. 生成 Allure HTML 报告
    try:
        gen_result = subprocess.run(
            ["allure", "generate", "reports/allure-results", "-o", "reports/allure-report", "--clean"],
            capture_output=True, text=True, timeout=120
        )
    except Exception as e:
        send_dingtalk_msg(f"[Allure 报告生成异常]\nError: {str(e)}")
        return JSONResponse(status_code=500, content={"error": f"allure generate 执行异常: {str(e)}"})

    task_id = str(uuid.uuid4())
    msg = (
        f"[自动化测试完成]\n任务ID: {task_id}\n"
        f"ReturnCode: {result.returncode}\n"
        f"AllureGenCode: {gen_result.returncode}\n"
        f"AllureGenOut: {gen_result.stdout[-1000:]}\n"
        f"AllureGenErr: {gen_result.stderr[-1000:]}\n"
        f"Stdout:\n{result.stdout[-1000:]}\nStderr:\n{result.stderr[-1000:]}"
    )
    send_dingtalk_msg(msg)

    return {
        "msg": "用例执行完成",
        "task_id": task_id,
        "pytest_returncode": result.returncode,
        "pytest_stdout": result.stdout[-1000:],
        "pytest_stderr": result.stderr[-1000:],
        "allure_returncode": gen_result.returncode,
        "allure_stdout": gen_result.stdout[-1000:],
        "allure_stderr": gen_result.stderr[-1000:]
    }


if __name__ == "__main__":
    """Todo: 测试用例执行"""
    pass