#!/usr/bin/env python3
"""Repository quality guard for P1 governance.

Checks:
1) Secrets or webhook/token hardcoding.
2) teardown_class must call super().teardown_class().
"""

from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parent.parent
EXCLUDED_DIR_MARKERS = {
    ".git",
    ".venv",
    ".pytest_cache",
    "logs",
    "reports",
    "outputs",
    "__pycache__",
}
EXCLUDED_PREFIXES = {
    "static/",
}

# Keep patterns strict to reduce false positives.
SECRET_PATTERNS = [
    re.compile(r"oapi\.dingtalk\.com/robot/send\?access_token=", re.IGNORECASE),
    re.compile(r"access_token=[A-Za-z0-9_\-]{16,}", re.IGNORECASE),
    re.compile(r"BEGIN\s+PRIVATE\s+KEY", re.IGNORECASE),
]
TEST_INTERDEPENDENCY_PATTERN = re.compile(r"\bself\.test_\d+_")


def to_rel(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def is_excluded(path: Path) -> bool:
    rel = to_rel(path)
    if any(rel.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
        return True
    parts = set(path.parts)
    return any(marker in parts for marker in EXCLUDED_DIR_MARKERS)


def tracked_files_from_git() -> list[Path]:
    cmd = ["git", "ls-files"]
    out = subprocess.check_output(cmd, cwd=REPO_ROOT, text=True)
    files = []
    for line in out.splitlines():
        if not line.strip():
            continue
        p = REPO_ROOT / line.strip()
        if p.is_file():
            files.append(p)
    return files


def normalize_paths(args_files: Iterable[str]) -> list[Path]:
    files = []
    for item in args_files:
        p = (REPO_ROOT / item).resolve() if not Path(item).is_absolute() else Path(item).resolve()
        if p.is_file():
            files.append(p)
    if files:
        return files
    return tracked_files_from_git()


def scan_secret_hardcoding(path: Path) -> list[str]:
    if is_excluded(path):
        return []
    if path.suffix.lower() not in {".py", ".md", ".yaml", ".yml", ".toml", ".env", ".ini"}:
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []

    errors = []
    lines = text.splitlines()
    for idx, line in enumerate(lines, start=1):
        for pattern in SECRET_PATTERNS:
            if pattern.search(line):
                errors.append(f"{to_rel(path)}:{idx}: potential secret hardcoding detected")
                break
    return errors


def _has_super_teardown_call(fn: ast.FunctionDef) -> bool:
    for node in ast.walk(fn):
        if not isinstance(node, ast.Call):
            continue
        attr = node.func
        if not isinstance(attr, ast.Attribute):
            continue
        if attr.attr != "teardown_class":
            continue
        super_call = attr.value
        if not isinstance(super_call, ast.Call):
            continue
        if isinstance(super_call.func, ast.Name) and super_call.func.id == "super":
            return True
    return False


def scan_teardown_contract(path: Path) -> list[str]:
    if is_excluded(path) or path.suffix != ".py":
        return []
    text = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError:
        # Syntax should be caught by normal lint/compile; skip here.
        return []

    errors = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        if node.name == "BaseTest":
            continue
        for child in node.body:
            if isinstance(child, ast.FunctionDef) and child.name == "teardown_class":
                if not _has_super_teardown_call(child):
                    rel = to_rel(path)
                    errors.append(
                        f"{rel}:{child.lineno}: teardown_class missing super().teardown_class()"
                    )
    return errors


def scan_test_interdependency(path: Path) -> list[str]:
    """Disallow test-method-to-test-method direct calls (self.test_xxx)."""
    if is_excluded(path) or path.suffix != ".py":
        return []
    rel = to_rel(path)
    if not rel.startswith("testcases/"):
        return []
    text = path.read_text(encoding="utf-8")
    errors = []
    for idx, line in enumerate(text.splitlines(), start=1):
        if TEST_INTERDEPENDENCY_PATTERN.search(line):
            errors.append(f"{rel}:{idx}: avoid test interdependency call: {line.strip()}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Quality guard for ERP autotest repository.")
    parser.add_argument("files", nargs="*", help="Optional file list. If empty, scan tracked files.")
    args = parser.parse_args()

    files = normalize_paths(args.files)
    files = [f for f in files if f.exists() and f.is_file()]

    violations = []
    for path in files:
        violations.extend(scan_secret_hardcoding(path))
        violations.extend(scan_teardown_contract(path))
        violations.extend(scan_test_interdependency(path))

    if violations:
        print("quality_guard: FAILED")
        for item in violations:
            print(item)
        return 1

    print("quality_guard: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
