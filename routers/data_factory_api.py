import os

from fastapi import APIRouter
from loguru import logger

from erp_data_factory.compat.base import DataFactory

router = APIRouter(prefix="/data-factory", tags=["数据工厂"])


@router.get("/get_base_data")
async def get_base_data():
    """
    获取基础数据接口示例：根据类型获取基础数据
    后续可对接具体的组织信息获取逻辑
    """
    env = os.getenv("TEST_ENV", "test")
    project = os.getenv("TEST_PROJECT")
    DataFactory.__init__(env_name=env, project=project)
    data = DataFactory.get_base_data(project="erp")
    logger.info(f"获取基础数据：{data}")
    return data


# 可根据需要扩展更多造数相关接口
