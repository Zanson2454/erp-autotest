from typing import Any, Dict, Optional, Tuple

from utils.param_util import ParamUtil


class ApiClientFacade:
    """
    API 调用辅助门面（兼容层）。
    先承接路径/参数解析逻辑，后续可逐步承接 standard_api_call 细节。
    """

    @staticmethod
    def resolve_api_path(apis_dict: Dict[str, Any], api_key: str, logger: Any = None) -> Optional[str]:
        api_path = ParamUtil.get_api_path(apis_dict, api_key)
        if api_path:
            return api_path
        if logger:
            normalized = str(api_key).strip()
            candidates = [
                key for key, meta in apis_dict.items() if isinstance(meta, dict) and normalized in str(key)
            ][:5]
            if candidates:
                logger.error(
                    f"API key严格匹配失败: '{normalized}'。可能想要: {candidates}"
                )
            else:
                logger.error(f"API key严格匹配失败: '{normalized}'。未找到候选项。")
        return None

    @staticmethod
    def resolve_api_params(
        api_params_dict: Dict[str, Any],
        api_path: str,
        with_query_params: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], str]:
        return ParamUtil.get_api_params(api_params_dict, api_path, with_query_params)
