"""场景执行上下文模型。"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ExecutionContext:
    """执行链路共享上下文。

    字段说明：
    - env: 运行环境（test/dev/staging/prod 等）
    - profile: 运行配置分组
    - project: 项目标识（多项目模式）
    - request_id: 调用请求 ID（用于审计追踪）
    """

    env: str = "test"
    profile: str = "default"
    project: Optional[str] = None
    request_id: Optional[str] = None
