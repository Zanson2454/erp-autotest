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
from datetime import datetime
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
    "deduplicate_requests": True,
    "reset_output_on_start": False,
    "flush_gap_threshold": 20,
    "redact_header_keys": ["cookie", "authorization", "content-length"],
    "skip_path_contains": ["/metrics"],
    "skip_extensions": [".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".map"],
    "capture_http_error_requests": True,
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
    raw = (path or "").strip()
    if not raw:
        return "/"
    return raw if raw.startswith("/") else f"/{raw}"


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
        self._request_sequence: int = 0
        self._written_step_count: int = 0
        self._next_flush_request_seq: int = 1
        self._pending_records: dict[int, Optional[dict]] = {}
        self._max_assigned_request_seq: int = 0
        self._recorded_signatures: set[str] = set()
        self._configured = False
        self._bootstrapped = False
        self._session_started_at: str = ""

    @staticmethod
    def _build_signature(flow: http.HTTPFlow) -> str:
        """接口去重签名：按 method + path 去重（忽略 query/body）。"""
        req = flow.request
        method = (req.method or "GET").upper()
        path = _normalize_path(urlsplit(req.pretty_url).path or "")
        return f"{method} {path}"

    def _collect_existing_signatures(self) -> None:
        """重启录制时从历史分片读取已写入接口签名，避免重复追加。"""
        self._recorded_signatures = set()
        pattern = f"{self.output_base_stem}_*{self.output_suffix}"
        for p in sorted(self.output_dir.glob(pattern)):
            try:
                content = p.read_text(encoding="utf-8")
            except OSError:
                continue
            # 逐行扫描 curl，避免复杂 Markdown 解析。
            for line in content.splitlines():
                line = line.strip()
                if not line.startswith("curl -X "):
                    continue
                # 形如：curl -X POST 'https://host/path?...' ...
                method = "GET"
                if line.startswith("curl -X "):
                    rest = line[len("curl -X "):]
                    method = rest.split(" ", 1)[0].upper()
                first_quote = line.find("'")
                second_quote = line.find("'", first_quote + 1) if first_quote >= 0 else -1
                if first_quote < 0 or second_quote <= first_quote:
                    continue
                url = line[first_quote + 1:second_quote]
                path = _normalize_path(urlsplit(url).path or "")
                self._recorded_signatures.add(f"{method} {path}")

    def _count_curls_in_file(self, path: Path) -> int:
        """统计文件里已有 curl 条数（按 Step 标题计数）。"""
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            return 0
        return sum(1 for line in content.splitlines() if line.startswith("### Step"))

    def _init_request_sequence_state(self) -> None:
        """按当前已写入条数初始化序号，重启后保持 Step 递增。"""
        total = 0
        index = 1
        while True:
            p = self._resolve_output_file_by_index(index)
            if not p.exists():
                break
            total += self._count_curls_in_file(p)
            index += 1
        self._request_sequence = total
        self._written_step_count = total
        self._next_flush_request_seq = 1
        self._pending_records = {}
        self._max_assigned_request_seq = total

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
        if not self._bootstrapped and bool(self.config.get("reset_output_on_start", False)):
            pattern = f"{self.output_base_stem}_*{self.output_suffix}"
            for p in self.output_dir.glob(pattern):
                try:
                    p.unlink()
                except OSError:
                    pass

        max_curls = self.config.get("max_curls_per_file", DEFAULT_CONFIG["max_curls_per_file"])
        try:
            self.max_curls_per_file = int(max_curls)
        except (TypeError, ValueError):
            self.max_curls_per_file = int(DEFAULT_CONFIG["max_curls_per_file"])
        self._init_file_rotation_state()
        self._init_request_sequence_state()
        if bool(self.config.get("deduplicate_requests", True)):
            self._collect_existing_signatures()
        if not self._bootstrapped:
            self._session_started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(f"<!-- Recorder Session Start: {self._session_started_at} -->\n\n")
        self._bootstrapped = True
        self._configured = True

    def configure(self, updated) -> None:
        # 中文说明：mitm 运行中若配置发生变化，configure 会被调用；极简实现选择“重新加载一次”。
        self._configured = False
        self._load_config()

    def _should_record_flow(self, flow: http.HTTPFlow, *, bypass_allowed_prefix: bool = False) -> bool:
        req = flow.request
        host = (req.pretty_host or "").lower()
        path = urlsplit(req.pretty_url).path or ""

        allowed_hosts = [str(x).lower() for x in (self.config.get("allowed_hosts") or [])]
        if allowed_hosts and host not in allowed_hosts:
            return False

        allowed_prefixes = [str(x) for x in (self.config.get("allowed_path_prefixes") or [])]
        if not bypass_allowed_prefix and allowed_prefixes and not any(path.startswith(p) for p in allowed_prefixes):
            return False

        blocked_paths = [_normalize_path(str(x)) for x in (self.config.get("blocked_paths") or [])]
        if blocked_paths and _normalize_path(path) in blocked_paths:
            return False

        blocked_prefixes = [str(x) for x in (self.config.get("blocked_path_prefixes") or [])]
        if blocked_prefixes and any(path.startswith(p) for p in blocked_prefixes):
            return False

        blocked_contains = [str(x) for x in (self.config.get("blocked_path_contains") or [])]
        if blocked_contains and _should_skip_by_contains(path, blocked_contains):
            return False

        if _should_skip_by_extension(path, [str(x) for x in (self.config.get("skip_extensions") or [])]):
            return False

        if _should_skip_by_contains(path, [str(x) for x in (self.config.get("skip_path_contains") or [])]):
            return False

        return True

    def request(self, flow: http.HTTPFlow) -> None:
        # 中文说明：在 request 阶段打序号，确保 Step 按“前端发起顺序”编号。
        self._load_config()
        self._request_sequence += 1
        self._max_assigned_request_seq = max(self._max_assigned_request_seq, self._request_sequence)
        flow.metadata["request_seq"] = self._request_sequence

    def response(self, flow: http.HTTPFlow) -> None:
        # 中文说明：改为在 response 阶段写入，便于识别状态码（尤其是 4xx/5xx）。
        self._load_config()
        response = flow.response
        status_code = int(response.status_code) if response is not None else 0
        capture_error = bool(self.config.get("capture_http_error_requests", True))
        bypass_allowed_prefix = capture_error and status_code >= 400

        request_seq = int(flow.metadata.get("request_seq") or 0)
        if request_seq <= 0:
            self._request_sequence += 1
            request_seq = self._request_sequence
            self._max_assigned_request_seq = max(self._max_assigned_request_seq, self._request_sequence)

        if not self._should_record_flow(flow, bypass_allowed_prefix=bypass_allowed_prefix):
            self._pending_records[request_seq] = None
            self._flush_pending_records()
            return

        self._pending_records[request_seq] = {
            "signature": self._build_signature(flow),
            "curl": _format_curl(
                flow, redact_header_keys=[str(x) for x in (self.config.get("redact_header_keys") or [])]
            ),
            "path": urlsplit(flow.request.pretty_url).path or "",
            "status_code": status_code,
        }
        self._flush_pending_records()

    def _flush_pending_records(self) -> None:
        """按请求发起顺序刷盘；过滤/去重项不占 Step 编号。"""
        gap_threshold_raw = self.config.get("flush_gap_threshold", 20)
        try:
            gap_threshold = int(gap_threshold_raw)
        except (TypeError, ValueError):
            gap_threshold = 20
        if gap_threshold < 1:
            gap_threshold = 1

        # 若某些请求长期没有 response，避免阻塞后续全部写入。
        while (
            self._next_flush_request_seq not in self._pending_records
            and (self._max_assigned_request_seq - self._next_flush_request_seq) >= gap_threshold
        ):
            self._next_flush_request_seq += 1

        while self._next_flush_request_seq in self._pending_records:
            item = self._pending_records.pop(self._next_flush_request_seq)
            self._next_flush_request_seq += 1
            if not item:
                continue

            signature = str(item["signature"])
            if bool(self.config.get("deduplicate_requests", True)) and signature in self._recorded_signatures:
                continue

            self._rotate_if_needed()
            self._written_step_count += 1
            path = str(item["path"])
            status_code = int(item["status_code"])
            curl = str(item["curl"])
            with open(self.output_file, "a", encoding="utf-8") as f:
                if status_code:
                    f.write(f"### Step{self._written_step_count}: {path} [HTTP {status_code}]\n")
                else:
                    f.write(f"### Step{self._written_step_count}: {path}\n")
                f.write(f"```bash\n{curl}\n```\n\n")
            self._curl_count_in_current_file += 1
            self._recorded_signatures.add(signature)


addons = [CurlRecorder()]
