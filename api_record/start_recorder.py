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
    exe = Path(sys.executable).resolve()
    parent = exe.parent
    if sys.platform == "win32":
        return [parent / "mitmdump.exe"]
    return [parent / "mitmdump"]


def _fallback_venv_mitmdump() -> Path | None:
    venv_dir = PROJECT_ROOT / ".venv"
    if sys.platform == "win32":
        p = venv_dir / "Scripts" / "mitmdump.exe"
    else:
        p = venv_dir / "bin" / "mitmdump"
    return p if p.exists() else None


def main() -> int:
    mitmdump: Path | None = None
    for candidate in _mitmdump_candidates():
        if candidate.exists():
            mitmdump = candidate
            break
    if mitmdump is None:
        mitmdump = _fallback_venv_mitmdump()

    if mitmdump is None or not mitmdump.exists():
        root_req = PROJECT_ROOT / "requirements.txt"
        print(
            "未找到 mitmdump，请先安装主项目依赖（含 mitmproxy）：\n"
            f"  {PROJECT_ROOT / '.venv' / 'bin' / 'python'} -m pip install -r {root_req}\n"
            "若使用其它虚拟环境，请激活该环境后再运行本脚本（将使用当前 Python 同目录下的 mitmdump）。",
            file=sys.stderr,
        )
        return 1

    command = [str(mitmdump), "-s", str(RECORDER_SCRIPT), *sys.argv[1:]]
    os.execv(command[0], command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
