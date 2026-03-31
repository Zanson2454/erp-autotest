import re
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

        api_key_str = str(api_key).strip()
        matched_keys = []

        if api_key_str.startswith("/"):
            normalized_path = api_key_str.split("#", 1)[0]
            for key, meta in apis_dict.items():
                if not isinstance(meta, dict):
                    continue
                if key == api_key_str or key.startswith(f"{normalized_path}#"):
                    matched_keys.append(key)
        else:
            for key, meta in apis_dict.items():
                if not isinstance(meta, dict):
                    continue
                if key.startswith(f"{api_key_str}("):
                    matched_keys.append(key)

            if not matched_keys:
                signature_match = re.search(r"\(([^()]+)\)", api_key_str)
                if signature_match:
                    signature = signature_match.group(1).strip()
                    for key, meta in apis_dict.items():
                        if not isinstance(meta, dict):
                            continue
                        if f"({signature})" in key:
                            matched_keys.append(key)

        if not matched_keys:
            return None

        matched_keys.sort(key=lambda k: ("direct" in k.lower(), len(k)))
        best_key = matched_keys[0]
        best_path = ParamUtil.get_api_path(apis_dict, best_key)
        if best_path and logger:
            logger.warning(f"API key未精确命中，已使用近似匹配: '{api_key_str}' -> '{best_key}'")
        return best_path

    @staticmethod
    def resolve_api_params(
        api_params_dict: Dict[str, Any],
        api_path: str,
        with_query_params: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], str]:
        return ParamUtil.get_api_params(api_params_dict, api_path, with_query_params)
