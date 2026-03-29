# -*- coding: utf-8 -*-
"""
扫描 config/api 下各模块的 *_api_path.yaml / common_api_path.yaml，
建立「完整 execute 路径 -> YAML apis 键名」映射，与正式用例里 api_key 一致。

仅用于 mitm 录制生成时的可读命名；运行时仍可用完整 path + _register_direct_api。
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict

import yaml

_EXECUTE_PREFIX = "/api/trantor/service/engine/execute"


def _iter_api_path_files(config_api_root: Path):
    if not config_api_root.is_dir():
        return
    yield from config_api_root.rglob("*_api_path.yaml")
    yield from config_api_root.rglob("common_api_path.yaml")


def build_execute_path_to_api_name(project_root: Path) -> Dict[str, str]:
    """首次命中路径优先；重复 path 一般不跨文件出现。"""
    root = project_root.resolve()
    config_api = root / "config" / "api"
    out: Dict[str, str] = {}
    for yaml_path in _iter_api_path_files(config_api):
        try:
            raw = yaml_path.read_text(encoding="utf-8")
        except OSError:
            continue
        try:
            data = yaml.safe_load(raw)
        except yaml.YAMLError:
            continue
        apis = (data or {}).get("apis") or {}
        if not isinstance(apis, dict):
            continue
        for api_name, spec in apis.items():
            if not isinstance(spec, dict):
                continue
            path = spec.get("path")
            if not isinstance(path, str):
                continue
            if not path.startswith(_EXECUTE_PREFIX):
                continue
            if path not in out:
                out[path] = str(api_name)
    return out


@lru_cache(maxsize=4)
def get_execute_path_to_api_name(project_root: str) -> Dict[str, str]:
    """project_root 用 str 以便 lru_cache；传 PROJECT_ROOT 的 resolve 路径字符串。"""
    return build_execute_path_to_api_name(Path(project_root))


def clear_registry_cache() -> None:
    get_execute_path_to_api_name.cache_clear()
