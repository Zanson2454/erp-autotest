#!/usr/bin/env python3
# coding=utf-8
# from .dependencies import get_query_token, get_token_header
import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.staticfiles import StaticFiles

# main.py 位于项目根目录，将项目根加入 sys.path 以支持 utils / routers 等子包导入
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from routers import allure_api, api_manage, data_factory_api  # noqa: E402

# 初始化FastAPI应用程序
app = FastAPI(
    docs_url=None,  # 禁用默认 docs
    redoc_url=None, # 如需禁用 redoc
    swagger_ui_parameters=None,
    openapi_url="/openapi.json",
    title="ERP-AUTOTEST",
    description="ERP自动化测试平台",
    version="1.0.0",
    openapi_version="3.1.0")



# 挂载 Allure 报告静态目录
ALLURE_REPORT_DIR = 'reports/allure-report'
app.mount("/allure", StaticFiles(directory=ALLURE_REPORT_DIR), name="allure")

# 挂载 static 静态资源目录（必须有！）
app.mount("/static", StaticFiles(directory="static"), name="static")



# 注册API路由
# app.include_router(autotest_api.router)
app.include_router(data_factory_api.router)
app.include_router(allure_api.router)
app.include_router(api_manage.router)


@app.get("/",tags=["首页"])
async def root():
    return "ok"


@app.get("/docs", include_in_schema=False)
async def custom_docs():
    html_path = os.path.join("static", "swagger-ui-5.22.0", "custom_index.html")
    abs_path = os.path.abspath(html_path)
    if not os.path.exists(abs_path):
        return HTMLResponse(f"custom_index.html not found: {abs_path}", status_code=404)
    with open(abs_path, encoding="utf-8") as f:
        return HTMLResponse(f.read())


if __name__ == "__main__":
    pass
