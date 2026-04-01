#!/usr/bin/env python3
"""验证仓库关键目录结构（供 README 和入职指引使用）。

本脚本对高价值路径进行严格检查，以便在 pre-commit/CI 阶段尽早发现
“文档与实际实现不一致”的偏差。
"""

from __future__ import annotations

import sys
from pathlib import Path

# 仓库根目录：当前脚本所在目录的上一级
REPO_ROOT = Path(__file__).resolve().parent.parent

# 必须存在的关键路径列表（保持精简且高信噪比）
REQUIRED_PATHS = [
    "README.md",
    "requirements.txt",
    "pytest.ini",
    "pipeline.yml",
    "api_record/recorder.py",
    "api_record/start_recorder.py",
    "api_record/recorder_config.json",
    "testcases/conftest.py",
    "testcases/comm/base_test.py",
    "testcases/comm/api_client_facade.py",
    "testcases/comm/auth_context.py",
    "testcases/comm/test_data_context.py",
    "utils/mysql_util.py",
    "config/api",
    "config/env",
    "config/erp",
    "script/quality_guard.py",
    "script/scan_yaml_duplicate_keys.py",
    "script/seed_test_data.py",
    "docs/cache_data_dependency.md",
]


def main() -> int:
    """主入口函数：检查 REQUIRED_PATHS 中的路径是否全部存在。"""
    missing: list[str] = []
    for rel in REQUIRED_PATHS:
        path = REPO_ROOT / rel
        if not path.exists():
            missing.append(rel)

    if missing:
        print("validate_project_structure: FAILED")
        print("缺失的必需路径：")
        for rel in missing:
            print(f"- {rel}")
        return 1

    print("validate_project_structure: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
