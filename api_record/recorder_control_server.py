#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地「录制武装」控制台（与 mitmproxy 中的 recorder.py 通过 recording_state_file 联动）。

在浏览器中打开（建议固定标签页与 ERP 并排）：
  python api_record/recorder_control_server.py

需在 recorder_config.json 中设置 recording_arm_switch: true，且路径与 recording_state_file 一致。
业务系统为远程 HTTPS 页面时无法直接内嵌本机 UI；可用并排标签、书签或 Tampermonkey + GM_xmlhttpRequest 调 /api/*。
"""

from __future__ import annotations

import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

API_RECORD_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = API_RECORD_ROOT.parent
DEFAULT_STATE_FILE = API_RECORD_ROOT / "runtime" / "recording_armed.json"
DEFAULT_PORT = 18765

HTML_PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>ERP 录制开关</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 360px; margin: 2rem auto; padding: 0 1rem; }
    h1 { font-size: 1.1rem; }
    .pill { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 999px; font-size: 0.85rem; }
    .on { background: #d4edda; color: #155724; }
    .off { background: #f8d7da; color: #721c24; }
    button { width: 100%; margin: 0.5rem 0; padding: 0.75rem; font-size: 1rem; cursor: pointer;
             border-radius: 8px; border: 1px solid #ccc; }
    .arm { background: #28a745; color: #fff; border-color: #218838; }
    .disarm { background: #6c757d; color: #fff; border-color: #5a6268; }
    small { color: #666; word-break: break-all; }
  </style>
</head>
<body>
  <h1>API 录制武装</h1>
  <p>状态：<span id="st" class="pill off">…</span></p>
  <p><button type="button" class="arm" id="btnArm">开始录制</button></p>
  <p><button type="button" class="disarm" id="btnDisarm">停止录制</button></p>
  <p><button type="button" id="btnToggle">切换</button></p>
  <p><small id="path"></small></p>
  <script>
    const st = document.getElementById("st");
    const pathEl = document.getElementById("path");
    async function refresh() {
      const r = await fetch("/api/status");
      const j = await r.json();
      pathEl.textContent = j.state_file || "";
      const armed = j.armed === true;
      st.textContent = armed ? "录制中" : "已停止";
      st.className = "pill " + (armed ? "on" : "off");
    }
    async function post(url) {
      await fetch(url, { method: "POST" });
      await refresh();
    }
    document.getElementById("btnArm").onclick = () => post("/api/arm");
    document.getElementById("btnDisarm").onclick = () => post("/api/disarm");
    document.getElementById("btnToggle").onclick = () => post("/api/toggle");
    refresh();
    setInterval(refresh, 2000);
  </script>
</body>
</html>
"""


def resolve_state_path(cli_path: Path | None) -> Path:
    env = os.environ.get("ERP_RECORD_STATE_FILE", "").strip()
    if cli_path is not None:
        p = cli_path.expanduser()
        return p if p.is_absolute() else PROJECT_ROOT / p
    if env:
        p = Path(env).expanduser()
        return p if p.is_absolute() else PROJECT_ROOT / p
    return DEFAULT_STATE_FILE


def read_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"armed": False}
    try:
        return dict(json.loads(path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, OSError):
        return {"armed": False}


def write_state(path: Path, armed: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps({"armed": armed}, ensure_ascii=False, indent=2) + "\n"
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(payload, encoding="utf-8")
    tmp.replace(path)


def make_handler(state_path: Path):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: Any) -> None:
            return

        def _cors(self) -> None:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

        def do_OPTIONS(self) -> None:
            self.send_response(204)
            self._cors()
            self.end_headers()

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path in ("/", "/index.html"):
                body = HTML_PAGE.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self._cors()
                self.end_headers()
                self.wfile.write(body)
                return
            if parsed.path == "/api/status":
                data = read_state(state_path)
                armed = bool(data.get("armed", False))
                out = json.dumps(
                    {"armed": armed, "state_file": str(state_path)},
                    ensure_ascii=False,
                ).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(out)))
                self._cors()
                self.end_headers()
                self.wfile.write(out)
                return
            self.send_error(404)

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            path_only = parsed.path.rstrip("/") or "/"
            if path_only == "/api/arm":
                write_state(state_path, True)
            elif path_only == "/api/disarm":
                write_state(state_path, False)
            elif path_only == "/api/toggle":
                cur = bool(read_state(state_path).get("armed", False))
                write_state(state_path, not cur)
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._cors()
            self.end_headers()
            self.wfile.write(b"{}\n")

    return Handler


def main() -> int:
    parser = argparse.ArgumentParser(description="ERP autotest recording arm switch UI")
    parser.add_argument(
        "--state-file",
        type=Path,
        default=None,
        help="与 recorder_config.json 中 recording_state_file 一致（可设环境变量 ERP_RECORD_STATE_FILE）",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    state_path = resolve_state_path(args.state_file)
    handler = make_handler(state_path)
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(
        f"录制控制台 http://{args.host}:{args.port}/  state_file={state_path}\n"
        "请确保 mitmproxy 已启用 recording_arm_switch 且路径一致。"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已退出")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
