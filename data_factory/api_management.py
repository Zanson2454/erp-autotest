from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import subprocess
import asyncio
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from data_factory.base import DataFactory
from loguru import logger
app = FastAPI(title="数据工厂API管理")

# 造数相关接口示例
@app.post("/generate-data")
async def generate_data(data_type: str, count: int = 1):
    """
    造数接口示例：根据类型和数量生成测试数据
    后续可对接具体的造数逻辑
    """
    # TODO: 对接具体造数逻辑
    return {"message": f"已生成 {count} 条类型为 {data_type} 的测试数据（示例）"}


@app.get("/data-factory/get_base_data")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)