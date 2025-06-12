from fastapi import APIRouter, HTTPException
from data_factory.base import DataFactory
from loguru import logger

router = APIRouter(prefix="/data-factory", tags=["数据工厂"])


@router.get("/get_base_data")
async def get_base_data():
    """
    获取基础数据接口示例：根据类型获取基础数据
    后续可对接具体的组织信息获取逻辑
    """
    data = DataFactory()
    data = data.get_base_data()
    logger.info(f"获取基础数据：{data}")
    return data

# 可根据需要扩展更多造数相关接口