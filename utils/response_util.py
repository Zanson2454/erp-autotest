import json
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict

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
    """响应处理工具类"""
    
    @staticmethod
    def extract_data(response: Dict[str, Any], max_depth: int = 10) -> Any:
        """
        从响应中提取嵌套的 data 字段值
        """
        def _extract(data: Any, depth: int = 0) -> Any:
            # 防止无限递归
            if depth >= max_depth:
                return data
                
            # 如果不是字典类型，直接返回
            if not isinstance(data, dict):
                return data
                
            # 如果有 data 字段且不为 None
            if "data" in data and data["data"] is not None:
                return _extract(data["data"], depth + 1)
                
            return data
            
        # 如果响应成功且有 data 字段
        if response.get("success") and "data" in response:
            return _extract(response["data"])
            
        return None

    def process_response(self, response):
        """处理 HTTP 响应"""
        if response.status_code == 200 or response.status_code == 201:
            response.success = True
            response.body = response.json()
        else:
            response.success = False
            logger.info("接口状态码不是2开头，请检查")
            logger.info("接口的返回内容>>>：" + json.dumps(response.json(), ensure_ascii=False, cls=DecimalEncoder))
        return response

    @staticmethod
    def get_response_data(response: Dict[str, Any], default: Any = None) -> Any:
        """
        获取响应中的数据，支持处理多层嵌套的 data 字段
        """
        try:
            # 验证响应成功
            if not response.get("success", False):
                logger.warning("Response is not successful")
                return default
                
            # 提取数据
            result = ResponseUtil.extract_data(response)
            return result if result is not None else default
            
        except Exception as e:
            logger.error(f"Failed to extract data from response: {str(e)}")
            return default

