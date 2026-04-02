"""场景执行返回模型定义（SDK/CLI/API 统一）。"""

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass
class ErrorInfo:
    """失败场景中的错误信息载体（可序列化）。"""

    code: str
    message: str
    category: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class ScenarioResult:
    """场景统一结果模型（同步/异步共用）。"""

    success: bool
    scenario_key: str
    data: Optional[Dict[str, Any]]
    trace_id: str
    audit: Optional[Dict[str, Any]] = None
    error: Optional[ErrorInfo] = None

    def to_dict(self) -> Dict[str, Any]:
        """将 dataclass 结果转换为普通 dict，便于接口层序列化。"""
        payload = asdict(self)
        if self.error is None:
            payload["error"] = None
        return payload
