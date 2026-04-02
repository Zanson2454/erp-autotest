"""场景执行链路的结构化业务异常定义。"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ErrorCategory(str, Enum):
    """错误分类枚举，用于失败分桶和诊断归因。"""

    PARAM_ERROR = "PARAM_ERROR"
    CONFIG_ERROR = "CONFIG_ERROR"
    UPSTREAM_API_ERROR = "UPSTREAM_API_ERROR"
    DATA_NOT_FOUND = "DATA_NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"


@dataclass
class ScenarioError(Exception):
    """业务异常模型，会被 runner 转换成结构化错误结果。"""

    code: str
    message: str
    category: ErrorCategory
    details: Optional[dict] = None

    def __str__(self) -> str:
        """返回紧凑错误文本，便于日志输出。"""
        return f"[{self.category}] {self.code}: {self.message}"
