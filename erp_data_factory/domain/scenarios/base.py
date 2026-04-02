"""主数据场景基类。

执行策略：
1. 有 payload 且可用 API 调用器时，优先走 API 造数。
2. API 不可用或无结果时，走 cache_loader / _run_by_cache 回退。
3. 统一以 ``ScenarioError`` 抛出业务失败语义。
"""

from typing import Any, Callable, Dict, Optional

from erp_data_factory.core.error_codes import DATA_NOT_FOUND, UPSTREAM_API_FAILED
from erp_data_factory.core.errors import ErrorCategory, ScenarioError


class BaseMasterScenario:
    """主数据场景公共执行流程。"""

    api_key: str = ""

    def __init__(self, api_caller=None, cache_loader: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None):
        self.api_caller = api_caller
        self.cache_loader = cache_loader

    def run(self, payload: Dict[str, Any], context=None) -> Dict[str, Any]:
        """执行场景主流程：API 优先，缓存回退。"""
        payload = payload or {}

        if payload and self.api_caller is not None:
            data = self._run_by_api(payload)
            if data:
                return data

        if self.cache_loader is not None:
            data = self.cache_loader(payload)
            if data:
                return data

        data = self._run_by_cache(payload, context=context)
        if data:
            return data

        raise ScenarioError(
            code=DATA_NOT_FOUND,
            message="No data was created or resolved for scenario",
            category=ErrorCategory.DATA_NOT_FOUND,
        )

    def _run_by_api(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """调用场景配置的 API，并校验统一上游响应契约。"""
        try:
            response, extracted_id = self.api_caller.call(
                api_key=self.api_key,
                set_dict=payload,
                fields_to_filter=list(payload.keys()),
            )
        except Exception as e:
            raise ScenarioError(
                code=UPSTREAM_API_FAILED,
                message=str(e),
                category=ErrorCategory.UPSTREAM_API_ERROR,
            ) from e

        if not isinstance(response, dict) or not response.get("success"):
            message = (
                response.get("message", "upstream api call failed")
                if isinstance(response, dict)
                else "invalid api response"
            )
            raise ScenarioError(
                code=UPSTREAM_API_FAILED,
                message=message,
                category=ErrorCategory.UPSTREAM_API_ERROR,
            )

        return self._extract_data_from_response(response, extracted_id, payload)

    def _extract_data_from_response(
        self, response: Dict[str, Any], extracted_id: Any, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """将上游响应映射为稳定的场景输出结构。"""
        return {"id": extracted_id} if extracted_id is not None else response.get("data", {})

    def _run_by_cache(self, payload: Dict[str, Any], context=None) -> Dict[str, Any]:
        """当 API 路径不可用时，从缓存/数据库解析数据。"""
        raise NotImplementedError
