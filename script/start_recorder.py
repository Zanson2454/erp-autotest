#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Start the mitmproxy recorder from an isolated virtual environment."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RECORDER_VENV = PROJECT_ROOT / ".venv_mitmproxy"
MITMDUMP = RECORDER_VENV / "bin" / "mitmdump"
RECORDER_SCRIPT = PROJECT_ROOT / "utils" / "recorder.py"
RECORDER_REQUIREMENTS = PROJECT_ROOT / "requirements-recorder.txt"


def main() -> int:
    if not MITMDUMP.exists():
        print(
            "Isolated recorder environment not found.\n"
            f"Create it with:\n"
            f"  python3 -m venv {RECORDER_VENV.name}\n"
            f"  {RECORDER_VENV / 'bin' / 'python'} -m pip install -r {RECORDER_REQUIREMENTS.name}",
            file=sys.stderr,
        )
        return 1

    command = [str(MITMDUMP), "-s", str(RECORDER_SCRIPT), *sys.argv[1:]]
    os.execv(command[0], command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
