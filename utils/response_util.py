import json
from datetime import datetime
from decimal import Decimal
from typing import Any

from utils.log_util import Loggers

logger = Loggers()

class DecimalEncoder(json.JSONEncoder):
    """自定义 JSON 编码器
    
    支持以下类型的序列化：
    - Decimal: 转换为 float
    - datetime: 转换为 ISO 格式字符串
    """
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return float(obj)  # 将 Decimal 转换为 float 
        if isinstance(obj, datetime):
            return obj.isoformat()  # 将 datetime 转换为 ISO 格式字符串
        return super().default(obj)  # 调用父类默认的序列化方法

class ResponseUtil:
    def process_response(self, response):
        if response.status_code == 200 or response.status_code == 201:
            response.success = True
            response.body = response.json()
        else:
            response.success = False
            logger.info("接口状态码不是2开头，请检查")
            logger.info("接口的返回内容>>>：" + json.dumps(response.json(), ensure_ascii=False, cls=DecimalEncoder))
        return response

