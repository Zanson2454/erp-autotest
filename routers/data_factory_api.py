from fastapi import APIRouter, HTTPException
from data_factory.base import DataFactory
from loguru import logger

router = APIRouter(prefix="/data-factory", tags=["数据工厂"])

# 造数相关接口示例
@router.post("/generate-data")
async def generate_data(data_type: str, count: int = 1):
    """
    造数接口示例：根据类型和数量生成测试数据
    后续可对接具体造数逻辑
    """
    # TODO: 对接具体造数逻辑
    return {"message": f"已生成 {count} 条类型为 {data_type} 的测试数据（示例）"}


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