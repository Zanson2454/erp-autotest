"""场景执行编排器。

作用：
1. 根据 ``scenario_key`` 路由到对应场景处理器。
2. 统一封装执行结果，确保调用方始终收到 ``ScenarioResult``。
3. 统一处理场景不存在、业务异常、未知异常三类失败路径。
"""

import uuid
from typing import Any, Dict, Optional

from erp_data_factory.core.context import ExecutionContext
from erp_data_factory.core.error_codes import (
    SCENARIO_NOT_FOUND,
    UNEXPECTED_ERROR,
)
from erp_data_factory.core.errors import ErrorCategory, ScenarioError
from erp_data_factory.core.models import ErrorInfo, ScenarioResult


class ScenarioRunner:
    """场景执行器：负责分发与结果规范化。"""

    def __init__(self, registry):
        """初始化执行器。

        参数：
        - registry: 场景注册中心，维护 ``scenario_key -> handler`` 映射关系。
        """
        self.registry = registry

    def run(
        self,
        scenario_key: str,
        payload: Optional[Dict[str, Any]] = None,
        context: Optional[ExecutionContext] = None,
    ) -> ScenarioResult:
        """执行单个场景并返回统一结果对象。

        返回语义：
        - 成功：``success=True``，``data`` 为场景产出。
        - 失败：``success=False``，``error`` 包含结构化错误信息。
        """
        trace_id = str(uuid.uuid4())
        context = context or ExecutionContext()
        payload = payload or {}
        request_id = context.request_id or str(uuid.uuid4())
        audit = {
            "request_id": request_id,
            "scenario_key": scenario_key,
            "profile": context.profile,
            "env": context.env,
        }

        handler = self.registry.get(scenario_key)
        if handler is None:
            return ScenarioResult(
                success=False,
                scenario_key=scenario_key,
                data=None,
                trace_id=trace_id,
                audit=audit,
                error=ErrorInfo(
                    code=SCENARIO_NOT_FOUND,
                    message=f"Unknown scenario_key: {scenario_key}",
                    category=ErrorCategory.PARAM_ERROR.value,
                ),
            )

        try:
            data = handler.run(payload, context=context)
            return ScenarioResult(
                success=True,
                scenario_key=scenario_key,
                data=data,
                trace_id=trace_id,
                audit=audit,
            )
        except ScenarioError as e:
            return ScenarioResult(
                success=False,
                scenario_key=scenario_key,
                data=None,
                trace_id=trace_id,
                audit=audit,
                error=ErrorInfo(
                    code=e.code,
                    message=e.message,
                    category=e.category.value,
                    details=e.details,
                ),
            )
        except Exception as e:  # pragma: no cover
            return ScenarioResult(
                success=False,
                scenario_key=scenario_key,
                data=None,
                trace_id=trace_id,
                audit=audit,
                error=ErrorInfo(
                    code=UNEXPECTED_ERROR,
                    message=str(e),
                    category=ErrorCategory.INTERNAL_ERROR.value,
                ),
            )
