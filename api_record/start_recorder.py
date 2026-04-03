#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用主项目 .venv 中的 mitmdump 启动录制脚本（与根目录 requirements.txt 一次安装）。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

API_RECORD_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = API_RECORD_ROOT.parent
RECORDER_SCRIPT = API_RECORD_ROOT / "recorder.py"


def _mitmdump_candidates() -> list[Path]:
    """定位 mitmdump 可执行文件（优先使用当前 Python 环境同目录）。"""
    exe = Path(sys.executable).resolve()
    parent = exe.parent
    if sys.platform == "win32":
        return [parent / "mitmdump.exe"]
    return [parent / "mitmdump"]


def _fallback_venv_mitmdump() -> Path | None:
    """兜底：尝试从主项目 `.venv/` 找 mitmdump（兼容“未激活 venv 但想直接跑脚本”的场景）。"""
    venv_dir = PROJECT_ROOT / ".venv"
    if sys.platform == "win32":
        p = venv_dir / "Scripts" / "mitmdump.exe"
    else:
        p = venv_dir / "bin" / "mitmdump"
    return p if p.exists() else None


def main() -> int:
    # 录制器必须依赖 mitmproxy；这里做“可执行文件探测”，让使用者少踩环境坑。
    mitmdump: Path | None = None
    for candidate in _mitmdump_candidates():
        if candidate.exists():
            mitmdump = candidate
            break
    if mitmdump is None:
        mitmdump = _fallback_venv_mitmdump()

    if mitmdump is None or not mitmdump.exists():
        # 失败时给出明确修复命令，避免“找不到 mitmdump”导致新手卡住。
        root_req = PROJECT_ROOT / "requirements.txt"
        print(
            "未找到 mitmdump，请先安装主项目依赖（含 mitmproxy）：\n"
            f"  {PROJECT_ROOT / '.venv' / 'bin' / 'python'} -m pip install -r {root_req}\n"
            "若使用其它虚拟环境，请激活该环境后再运行本脚本（将使用当前 Python 同目录下的 mitmdump）。",
            file=sys.stderr,
        )
        return 1

    # 关键点：使用 execv 直接把当前进程替换成 mitmdump，信号/退出码更贴近原生 mitm 行为。
    # 同时转发 CLI 参数，便于临时调试（例如加日志级别、改端口等）。
    command = [str(mitmdump), "-s", str(RECORDER_SCRIPT), *sys.argv[1:]]
    os.execv(command[0], command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
