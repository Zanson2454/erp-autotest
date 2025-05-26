#!/usr/bin/env python3
# coding=utf-8
# from .dependencies import get_query_token, get_token_header
import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

# 将父目录添加到 sys.path 中，以便包含来自父目录的模块
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from routers import (
    data_factory_api,
    allure_api
)

# 定义常量用于静态文件路径
STATIC_DIR = 'static'


# 初始化FastAPI应用程序
app = FastAPI(
    swagger_ui_parameters=None,
    openapi_url="/openapi.json",
    title="自定义API",
    description="自定义的API.",
    version="1.0.0",
    openapi_version="3.1.0")

# 静态文件的目录应该和 STATIC_DIR 一致
app.mount(f"/{STATIC_DIR}", StaticFiles(directory=f"{STATIC_DIR}"), name='static')

# 挂载 Allure 报告静态目录
ALLURE_REPORT_DIR = 'reports/allure-report'
app.mount("/allure", StaticFiles(directory=ALLURE_REPORT_DIR), name="allure")



# 注册API路由
# app.include_router(autotest_api.router)
app.include_router(data_factory_api.router)
app.include_router(allure_api.router)


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    pass
