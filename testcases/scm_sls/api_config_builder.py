from typing import Any, Callable, Dict, Iterable, Tuple

YamlLoader = Callable[[Any], Dict[str, Any]]
PathPair = Tuple[Any, Any]


def _read_section(load_yaml: YamlLoader, path: Any, section: str) -> Dict[str, Any]:
    data = load_yaml(path) or {}
    value = data.get(section, {})
    if isinstance(value, dict):
        return value
    return {}


def merge_module_api_configs(
    load_yaml: YamlLoader,
    base_api_path: Any,
    base_api_params: Any,
    extension_pairs: Iterable[PathPair],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    apis = dict(_read_section(load_yaml, base_api_path, "apis"))
    api_params = dict(_read_section(load_yaml, base_api_params, "api_params"))

    for api_path, params_path in extension_pairs:
        apis.update(_read_section(load_yaml, api_path, "apis"))
        api_params.update(_read_section(load_yaml, params_path, "api_params"))

    return apis, api_params
