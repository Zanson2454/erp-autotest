#!/usr/bin/env python3
"""Validate key repository structure used by README and onboarding.

This script is intentionally strict on high-value paths to catch
"doc vs implementation" drift early in pre-commit/CI.
"""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

# Keep this list short and high-signal.
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
]


def main() -> int:
    missing: list[str] = []
    for rel in REQUIRED_PATHS:
        path = REPO_ROOT / rel
        if not path.exists():
            missing.append(rel)

    if missing:
        print("validate_project_structure: FAILED")
        print("Missing required paths:")
        for rel in missing:
            print(f"- {rel}")
        return 1

    print("validate_project_structure: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

