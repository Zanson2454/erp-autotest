from fastapi import APIRouter
from fastapi.responses import RedirectResponse
import os

router = APIRouter(prefix="/reports", tags=["Allure报告"])

@router.get("/allure")
async def allure_index():
    """
    跳转到 Allure 报告首页
    """
    return RedirectResponse(url="/allure/index.html") 