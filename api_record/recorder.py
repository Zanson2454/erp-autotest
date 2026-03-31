# -*- coding: utf-8 -*-
"""
Mitmproxy recorder for the ERP autotest project (cURL Markdown 输出版).

中文说明（设计目标）：
- 录制阶段只做两件事：**过滤噪音** + **把请求导出为可读的 cURL（Markdown）**
- “重构/参数化/断言/清理”交给 AI + 人工迁移到 `testcases/**`
- 录制产物默认不进 Git（避免敏感信息与噪音污染）

Usage:
    mitmdump -s api_record/recorder.py
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlsplit

from mitmproxy import ctx, http

API_RECORD_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = API_RECORD_ROOT.parent

DEFAULT_CONFIG_FILE = PROJECT_ROOT / "api_record" / "recorder_config.json"
DEFAULT_CONFIG = {
    "allowed_hosts": [],
    "allowed_path_prefixes": ["/api/trantor/"],
    "blocked_paths": [],
    "blocked_path_prefixes": ["/api/trantor/runtime/scene/"],
    "blocked_path_contains": [],
    "output_dir": "api_record/raw_curls",
    "output_file": "api_record/raw_curls/recorded_flow.md",
    "max_curls_per_file": 100,
    "redact_header_keys": ["cookie", "authorization", "content-length"],
    "skip_path_contains": ["/metrics"],
    "skip_extensions": [".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".map"],
}


def _should_skip_by_extension(path: str, extensions: List[str]) -> bool:
    lowered = (path or "").lower()
    return any(lowered.endswith(ext.lower()) for ext in extensions)


def _should_skip_by_contains(path: str, tokens: List[str]) -> bool:
    if not path:
        return True
    lowered = path.lower()
    return any(str(t).lower() in lowered for t in tokens)


def _normalize_path(path: str) -> str:
    return (path or "").strip() or "/"


def _format_curl(flow: http.HTTPFlow, *, redact_header_keys: List[str]) -> str:
    request = flow.request
    method = (request.method or "GET").upper()
    url = request.pretty_url

    # 中文说明：录制阶段不采集 Cookie/Authorization 等敏感头；其它头只做“尽量可回放”的参考。
    redact = {k.lower() for k in (redact_header_keys or [])}
    header_parts: List[str] = []
    for k, v in request.headers.items():
        if str(k).lower() in redact:
            continue
        header_parts.append(f'-H \"{k}: {v}\"')

    curl = f"curl -X {method} '{url}'"
    if header_parts:
        curl += " " + " ".join(header_parts)

    body = request.get_text(strict=False) if request.content else ""
    if body:
        # 说明：这里不做 JSON 美化，仅保留原始文本，避免转义/格式化导致 AI 丢字段。
        curl += f" -d '{body}'"
    return curl


class CurlRecorder:
    """mitmproxy addon：把命中的请求写成 cURL Markdown。"""

    def __init__(self) -> None:
        self.config_file = DEFAULT_CONFIG_FILE
        self.config: Dict[str, object] = dict(DEFAULT_CONFIG)
        self.output_file: Path = PROJECT_ROOT / "api_record/raw_curls/recorded_flow.md"
        self.output_dir: Path = self.output_file.parent
        self.output_base_stem: str = self.output_file.stem
        self.output_suffix: str = self.output_file.suffix or ".md"
        self.max_curls_per_file: int = int(DEFAULT_CONFIG["max_curls_per_file"])
        self._file_index: int = 1
        self._curl_count_in_current_file: int = 0
        self._configured = False

    def _count_curls_in_file(self, path: Path) -> int:
        """统计文件里已有 curl 条数（按 Step 标题计数）。"""
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            return 0
        return content.count("\n### Step: ") + (1 if content.startswith("### Step: ") else 0)

    def _resolve_output_file_by_index(self, index: int) -> Path:
        """根据索引生成分片文件名，如 recorded_flow_001.md。"""
        return self.output_dir / f"{self.output_base_stem}_{index:03d}{self.output_suffix}"

    def _init_file_rotation_state(self) -> None:
        """初始化当前写入分片与计数，支持重启后续写。"""
        if self.max_curls_per_file <= 0:
            self.max_curls_per_file = 100

        index = 1
        while True:
            current = self._resolve_output_file_by_index(index)
            if not current.exists():
                break
            count = self._count_curls_in_file(current)
            if count < self.max_curls_per_file:
                self._file_index = index
                self.output_file = current
                self._curl_count_in_current_file = count
                return
            index += 1

        self._file_index = index
        self.output_file = self._resolve_output_file_by_index(index)
        self._curl_count_in_current_file = 0

    def _rotate_if_needed(self) -> None:
        """达到上限后切换到下一分片文件。"""
        if self._curl_count_in_current_file < self.max_curls_per_file:
            return
        self._file_index += 1
        self.output_file = self._resolve_output_file_by_index(self._file_index)
        self._curl_count_in_current_file = self._count_curls_in_file(self.output_file)

    def _load_config(self) -> None:
        """加载 recorder_config.json，并确保输出路径可写（尽量在首次 request 前完成）。"""
        if self._configured:
            return
        try:
            raw = json.loads(Path(self.config_file).read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                self.config.update(raw)
        except OSError:
            pass
        except json.JSONDecodeError:
            ctx.log.warn("[curl_recorder] recorder_config.json 解析失败，使用默认配置")

        output_file = str(self.config.get("output_file") or DEFAULT_CONFIG["output_file"])
        out_path = Path(output_file).expanduser()
        self.output_file = out_path if out_path.is_absolute() else PROJECT_ROOT / out_path
        self.output_dir = self.output_file.parent
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_base_stem = self.output_file.stem
        self.output_suffix = self.output_file.suffix or ".md"
        max_curls = self.config.get("max_curls_per_file", DEFAULT_CONFIG["max_curls_per_file"])
        try:
            self.max_curls_per_file = int(max_curls)
        except (TypeError, ValueError):
            self.max_curls_per_file = int(DEFAULT_CONFIG["max_curls_per_file"])
        self._init_file_rotation_state()
        self._configured = True

    def configure(self, updated) -> None:
        # 中文说明：mitm 运行中若配置发生变化，configure 会被调用；极简实现选择“重新加载一次”。
        self._configured = False
        self._load_config()

    def request(self, flow: http.HTTPFlow) -> None:
        # 中文说明：部分 mitm 启动路径下 configure 可能不会先于 request 触发；
        # 为保证可用性，这里做一次懒加载。
        self._load_config()

        req = flow.request
        host = (req.pretty_host or "").lower()
        path = urlsplit(req.pretty_url).path or ""

        allowed_hosts = [str(x).lower() for x in (self.config.get("allowed_hosts") or [])]
        if allowed_hosts and host not in allowed_hosts:
            return

        allowed_prefixes = [str(x) for x in (self.config.get("allowed_path_prefixes") or [])]
        if allowed_prefixes and not any(path.startswith(p) for p in allowed_prefixes):
            return

        blocked_paths = [_normalize_path(str(x)) for x in (self.config.get("blocked_paths") or [])]
        if blocked_paths and _normalize_path(path) in blocked_paths:
            return

        blocked_prefixes = [str(x) for x in (self.config.get("blocked_path_prefixes") or [])]
        if blocked_prefixes and any(path.startswith(p) for p in blocked_prefixes):
            return

        blocked_contains = [str(x) for x in (self.config.get("blocked_path_contains") or [])]
        if blocked_contains and _should_skip_by_contains(path, blocked_contains):
            return

        if _should_skip_by_extension(path, [str(x) for x in (self.config.get("skip_extensions") or [])]):
            return

        if _should_skip_by_contains(path, [str(x) for x in (self.config.get("skip_path_contains") or [])]):
            return

        curl = _format_curl(flow, redact_header_keys=[str(x) for x in (self.config.get("redact_header_keys") or [])])

        self._rotate_if_needed()
        # 中文说明：用 Markdown 组织每一步，便于 AI 在 Cursor 里“整块复制 + 重构生成用例”。
        with open(self.output_file, "a", encoding="utf-8") as f:
            f.write(f"### Step: {path}\n")
            f.write(f"```bash\n{curl}\n```\n\n")
        self._curl_count_in_current_file += 1


addons = [CurlRecorder()]
