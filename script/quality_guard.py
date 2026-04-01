#!/usr/bin/env python3
"""仓库质量守卫（P1 治理）。

检查项：
1) 密钥或 webhook/token 硬编码检测。
2) teardown_class 必须调用 super().teardown_class()。
3) 测试用例之间禁止相互调用（self.test_xxx）。
"""

from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable

# 仓库根目录：当前脚本所在目录的上一级
REPO_ROOT = Path(__file__).resolve().parent.parent

# 需要排除的目录标记（扫描时跳过这些目录下的文件）
EXCLUDED_DIR_MARKERS = {
    ".git",
    ".venv",
    ".pytest_cache",
    "logs",
    "reports",
    "outputs",
    "__pycache__",
}

# 需要排除的路径前缀
EXCLUDED_PREFIXES = {
    "static/",
}

# 密钥硬编码检测的正则模式（保持严格以减少误报）
SECRET_PATTERNS = [
    re.compile(r"oapi\.dingtalk\.com/robot/send\?access_token=", re.IGNORECASE),  # 钉钉机器人 webhook
    re.compile(r"access_token=[A-Za-z0-9_\-]{16,}", re.IGNORECASE),  # 长 access_token
    re.compile(r"BEGIN\s+PRIVATE\s+KEY", re.IGNORECASE),  # 私钥文件标记
]

# 测试用例间相互调用的检测模式（如 self.test_001_xxx）
TEST_INTERDEPENDENCY_PATTERN = re.compile(r"\bself\.test_\d+_")


def to_rel(path: Path) -> str:
    """将绝对路径转换为相对于仓库根目录的 POSIX 路径字符串。"""
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def is_excluded(path: Path) -> bool:
    """判断文件是否位于需要排除的目录或路径前缀下。"""
    rel = to_rel(path)
    if any(rel.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
        return True
    parts = set(path.parts)
    return any(marker in parts for marker in EXCLUDED_DIR_MARKERS)


def tracked_files_from_git() -> list[Path]:
    """通过 git ls-files 获取仓库中所有被跟踪的文件列表。"""
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
    """规范化输入的文件路径列表；若未提供则回退到 git 跟踪的文件。"""
    files = []
    for item in args_files:
        p = (REPO_ROOT / item).resolve() if not Path(item).is_absolute() else Path(item).resolve()
        if p.is_file():
            files.append(p)
    if files:
        return files
    return tracked_files_from_git()


def scan_secret_hardcoding(path: Path) -> list[str]:
    """扫描文件是否存在密钥硬编码问题。"""
    if is_excluded(path):
        return []
    # 仅扫描特定后缀的文件
    if path.suffix.lower() not in {".py", ".md", ".yaml", ".yml", ".toml", ".env", ".ini"}:
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # 非 UTF-8 编码文件跳过
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
    """检查函数体内是否包含 super().teardown_class() 调用。"""
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
    """扫描 Python 文件中的 teardown_class 方法是否调用了 super()。"""
    if is_excluded(path) or path.suffix != ".py":
        return []
    text = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError:
        # 语法错误应由常规 lint/compile 捕获，此处跳过
        return []

    errors = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        if node.name == "BaseTest":
            # 基类本身不需要调用 super()
            continue
        for child in node.body:
            if isinstance(child, ast.FunctionDef) and child.name == "teardown_class":
                if not _has_super_teardown_call(child):
                    rel = to_rel(path)
                    errors.append(f"{rel}:{child.lineno}: teardown_class missing super().teardown_class()")
    return errors


def scan_test_interdependency(path: Path) -> list[str]:
    """禁止测试方法之间直接相互调用（如 self.test_xxx）。"""
    if is_excluded(path) or path.suffix != ".py":
        return []
    rel = to_rel(path)
    # 仅扫描 testcases/ 目录下的文件
    if not rel.startswith("testcases/"):
        return []
    text = path.read_text(encoding="utf-8")
    errors = []
    for idx, line in enumerate(text.splitlines(), start=1):
        if TEST_INTERDEPENDENCY_PATTERN.search(line):
            errors.append(f"{rel}:{idx}: avoid test interdependency call: {line.strip()}")
    return errors


def main() -> int:
    """主入口函数：解析参数、收集文件、执行扫描并输出结果。"""
    parser = argparse.ArgumentParser(description="ERP autotest 仓库质量守卫。")
    parser.add_argument("files", nargs="*", help="可选的文件列表。若为空则扫描所有 git 跟踪的文件。")
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
