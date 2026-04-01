#!/usr/bin/env python3
"""扫描 YAML 映射中的重复 key（同一块内重复定义，非 merge << 场景）。

PyYAML 默认对重复 key 静默覆盖；本脚本使用自定义 Loader 在遇到重复 key 时抛错。

用法：
  python script/scan_yaml_duplicate_keys.py
  python script/scan_yaml_duplicate_keys.py --config config/erp

退出码：0 无重复；1 发现重复；2 参数/读文件错误。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class DuplicateKeyLoader(yaml.SafeLoader):
    """遇到重复 key 时抛出 ConstructorError。"""


def _construct_mapping_no_duplicate(loader: DuplicateKeyLoader, node: MappingNode) -> Dict[Any, Any]:
    if not isinstance(node, MappingNode):
        raise ConstructorError(None, None, "expected a mapping node", node.start_mark)
    mapping: Dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        if key in mapping:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=True)
    return mapping


DuplicateKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping_no_duplicate,
)


def scan_file(path: Path) -> List[str]:
    """返回该文件内重复 key 的报错信息列表（若解析失败则返回单条错误）。"""
    errors: List[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return [f"{path}: 无法读取: {e}"]
    try:
        yaml.load(text, Loader=DuplicateKeyLoader)
    except ConstructorError as e:
        line = getattr(e.problem_mark, "line", None)
        line_hint = f" line ~{line + 1}" if line is not None else ""
        errors.append(f"{path}{line_hint}: {e.problem}")
    except yaml.YAMLError as e:
        errors.append(f"{path}: YAML 解析失败: {e}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="扫描 YAML 重复 key")
    parser.add_argument(
        "--config",
        type=Path,
        default=PROJECT_ROOT / "config",
        help="要扫描的根目录（默认 config/）",
    )
    parser.add_argument(
        "--glob",
        default="**/*.yaml",
        help="相对 config 的 glob（默认 **/*.yaml）",
    )
    args = parser.parse_args()
    root = args.config.resolve()
    if not root.exists():
        print(f"路径不存在: {root}", file=sys.stderr)
        return 2

    all_errors: List[str] = []
    for path in sorted(root.glob(args.glob)):
        if not path.is_file():
            continue
        errs = scan_file(path)
        all_errors.extend(errs)

    if all_errors:
        print("scan_yaml_duplicate_keys: FAILED")
        for msg in all_errors:
            print(f"  - {msg}")
        return 1

    print(f"scan_yaml_duplicate_keys: OK (已扫描 {root} / {args.glob})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
