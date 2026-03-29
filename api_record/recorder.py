# -*- coding: utf-8 -*-
"""
Mitmproxy recorder for the ERP autotest project.

Usage:
    mitmdump -s api_record/recorder.py

生成用例与「正式用例」的关系：
- 第一遍录制默认不做 sanitize_recorded_payload，避免丢字段导致回放失败；迁入正式用例时再按项目规范剔除 sceneKey、改 mock。
- resolve_api_config_names 为 true 时，从 config/api 反查与 YAML apis 键一致的名称，便于对照 md_api_path / common_api_path。
"""

import copy
import hashlib
import importlib.util
import json
import re
import textwrap
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Set, Tuple
from urllib.parse import parse_qsl, urlsplit

from mitmproxy import ctx, http

API_RECORD_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = API_RECORD_ROOT.parent


def _load_get_execute_path_to_api_name() -> Callable[[str], Dict[str, str]]:
    """mitmdump 仅保证脚本目录在 path 上；用文件路径加载，避免误捕子依赖的 ImportError。"""
    reg_path = API_RECORD_ROOT / "api_config_path_registry.py"
    spec = importlib.util.spec_from_file_location("erp_api_config_path_registry", reg_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"无法加载 API 注册表: {reg_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, "get_execute_path_to_api_name")


get_execute_path_to_api_name = _load_get_execute_path_to_api_name()
DEFAULT_CASE_FILE = PROJECT_ROOT / "api_record" / "generated_cases" / "test_manual_flow.py"
DEFAULT_DATA_DIR = PROJECT_ROOT / "api_record" / "testdata" / "recorded"
DEFAULT_CONFIG_FILE = PROJECT_ROOT / "api_record" / "recorder_config.json"
DEFAULT_DEDUPE_INDEX_FILE = PROJECT_ROOT / "api_record" / "generated_cases" / ".recorder_index.json"
BODY_FILE_THRESHOLD = 200
HEADER_MARKER = "class RecordedFlowMixin:"
RECORDED_QUERY_KEY = "__recorded_query_params__"
RECORDED_BODY_KEY = "__recorded_body__"

DEFAULT_CONFIG = {
    "allowed_hosts": ["t-erp-huoshan-portal-test.app.duandian.com"],
    "blocked_hosts": [],
    "allowed_path_prefixes": ["/api/trantor/"],
    "blocked_path_prefixes": [],
    "body_threshold": BODY_FILE_THRESHOLD,
    "case_file": "api_record/generated_cases/test_manual_flow.py",
    "data_dir": "api_record/testdata/recorded",
    "dedupe_index_file": "api_record/generated_cases/.recorder_index.json",
    # 默认关闭清洗字段，避免回放因缺参失败；需要贴近手写用例规范时再打开
    "sanitize_recorded_payload": False,
    # 在默认清洗键之外追加（与 DEFAULT_SANITIZE_REMOVE_KEYS 合并）
    "sanitize_remove_keys": [],
    # 对 engine/execute 类 POST：无 params 包壳且非典型信封字段时，包一层 params.request
    "auto_wrap_trantor_body": True,
    # 生成用例时根据 config/api/** 下 YAML 把 path 解析为与正式用例一致的 apis 键名（如 GEN-合作伙伴-查询详情服务）
    "resolve_api_config_names": True,
    # 第一遍录制是否剔除 sceneKey 等：正式用例迁移时还会再洗，默认 false 保持回放与浏览器一致
    # none=允许同指纹多次出现；fingerprint=同指纹只记一次（适合瘦身）
    # record_dedupe_persist=false 时仅本次 mitmdump 进程内去重；true 时使用 dedupe_index_file 跨次启动累积
    "record_dedupe_mode": "fingerprint",
    "record_dedupe_persist": False,
    # request=按浏览器发起顺序写文件；response=按响应返回先后（旧行为）
    "record_order_mode": "request",
    # true 时仅当 recording_state_file 中 armed=true 才打序号/落盘（需配合 recorder_control_server）
    "recording_arm_switch": False,
    "recording_state_file": "api_record/runtime/recording_armed.json",
    "recorded_scene_epic": "场景录制",
    "recorded_scene_feature": "Mitmproxy 页面链路",
    "recorded_scene_story": "页面场景录制",
    # GenMdBaseTest | BaseTest | FinBaseTest
    "recorded_scene_base_class": "GenMdBaseTest",
}

# 与项目 .cursor 用例规范对齐的可选剔除键（仅 sanitize_recorded_payload=true 时生效）
DEFAULT_SANITIZE_REMOVE_KEYS: Set[str] = {
    "sceneKey",
    "serviceKey",
    "viewTitle",
    "buttonKey",
    "appId",
    "teamId",
    "uiKey",
    "version",
    "deleted",
    "tenantId",
    "requestId",
    "createdAt",
    "createdBy",
    "updatedAt",
    "updatedBy",
}

DEFAULT_REDACT_JSON_KEYS: Set[str] = {
    "password",
    "token",
    "accessToken",
    "refreshToken",
    "access_token",
    "refresh_token",
    "secret",
    "authorization",
    "oldPassword",
    "newPassword",
}

# 若请求体已含这些顶层键之一，则视为已有 Trantor 信封，不再 auto-wrap
TRANTOR_ENVELOPE_TOP_KEYS: Set[str] = {
    "sceneKey",
    "serviceKey",
    "viewKey",
    "viewTitle",
    "appId",
    "teamId",
    "params",
    "buttonKey",
    "uiKey",
    "containerKey",
}


def _redact_mapping(obj: Any, redact_keys_lower: Set[str]) -> Any:
    if not redact_keys_lower:
        return obj
    if isinstance(obj, dict):
        out: Dict[str, Any] = {}
        for key, val in obj.items():
            if str(key).lower() in redact_keys_lower:
                out[key] = "***REDACTED***"
            else:
                out[key] = _redact_mapping(val, redact_keys_lower)
        return out
    if isinstance(obj, list):
        return [_redact_mapping(item, redact_keys_lower) for item in obj]
    return obj


def _sanitize_remove_keys(obj: Any, keys_to_remove: Set[str]) -> Any:
    if not keys_to_remove:
        return obj
    if isinstance(obj, dict):
        return {
            k: _sanitize_remove_keys(v, keys_to_remove)
            for k, v in obj.items()
            if k not in keys_to_remove
        }
    if isinstance(obj, list):
        return [_sanitize_remove_keys(item, keys_to_remove) for item in obj]
    return obj

SKIP_METHODS = {"CONNECT", "HEAD", "OPTIONS"}
FLOW_META_RECORD_SEQ = "erp_record_seq"

SKIP_EXTENSIONS = {
    ".css",
    ".gif",
    ".ico",
    ".jpeg",
    ".jpg",
    ".js",
    ".map",
    ".png",
    ".svg",
    ".ttf",
    ".txt",
    ".woff",
    ".woff2",
}


@dataclass
class RecordDraft:
    host: str
    api_path: str
    method: str
    query_params: Dict[str, Any]
    body_payload: Any
    merged_payload: Dict[str, Any]
    response_status: int
    service_slug: str
    fingerprint: str
    request: http.Request


class RecordedCase:
    def __init__(
        self,
        host: str,
        api_path: str,
        method: str,
        query_params: Dict[str, Any],
        body_payload: Any,
        merged_payload: Dict[str, Any],
        response_status: int,
        test_name: str,
        payload_file: Optional[Path],
        service_slug: str,
        fingerprint: str,
        output_seq: int,
        browser_request_seq: Optional[int] = None,
        api_config_name: Optional[str] = None,
    ) -> None:
        self.host = host
        self.api_path = api_path
        self.method = method
        self.query_params = query_params
        self.body_payload = body_payload
        self.merged_payload = merged_payload
        self.response_status = response_status
        self.test_name = test_name
        self.payload_file = payload_file
        self.service_slug = service_slug
        self.fingerprint = fingerprint
        self.output_seq = output_seq
        self.browser_request_seq = browser_request_seq
        self.api_config_name = api_config_name


class ErpFlowRecorder:
    def __init__(self) -> None:
        self.config_file = DEFAULT_CONFIG_FILE
        self.case_file = DEFAULT_CASE_FILE
        self.data_dir = DEFAULT_DATA_DIR
        self.dedupe_index_file = DEFAULT_DEDUPE_INDEX_FILE
        self.body_threshold = BODY_FILE_THRESHOLD
        self.allowed_hosts = list(DEFAULT_CONFIG["allowed_hosts"])
        self.blocked_hosts = list(DEFAULT_CONFIG["blocked_hosts"])
        self.allowed_path_prefixes = list(DEFAULT_CONFIG["allowed_path_prefixes"])
        self.blocked_path_prefixes = list(DEFAULT_CONFIG["blocked_path_prefixes"])
        self.session_ts = int(time.time())
        self.case_index = 0
        self.fingerprints: set[str] = set()
        self.sanitize_recorded_payload = bool(DEFAULT_CONFIG["sanitize_recorded_payload"])
        self.sanitize_remove_keys: Set[str] = set(DEFAULT_SANITIZE_REMOVE_KEYS)
        self.redact_json_keys_lower: Set[str] = {k.lower() for k in DEFAULT_REDACT_JSON_KEYS}
        self.auto_wrap_trantor_body = bool(DEFAULT_CONFIG["auto_wrap_trantor_body"])
        self.record_dedupe_mode = str(DEFAULT_CONFIG["record_dedupe_mode"])
        self.record_dedupe_persist = bool(DEFAULT_CONFIG.get("record_dedupe_persist", False))
        self.record_order_mode = str(DEFAULT_CONFIG["record_order_mode"])
        self._request_order_seq = 0
        self._next_flush_seq = 1
        self._pending_cases: Dict[int, RecordDraft] = {}
        self._skipped_seqs: Set[int] = set()
        self.recording_arm_switch = bool(DEFAULT_CONFIG.get("recording_arm_switch", False))
        self.recording_state_path = PROJECT_ROOT / str(
            DEFAULT_CONFIG.get("recording_state_file", "api_record/runtime/recording_armed.json")
        )
        self._armed_cache_mtime: float = -1.0
        self._armed_cache_value: bool = False
        self.resolve_api_config_names = bool(DEFAULT_CONFIG.get("resolve_api_config_names", True))
        self._path_to_api_config_name: Optional[Dict[str, str]] = None
        self.recorded_scene_epic = str(DEFAULT_CONFIG.get("recorded_scene_epic", "场景录制"))
        self.recorded_scene_feature = str(DEFAULT_CONFIG.get("recorded_scene_feature", "Mitmproxy 页面链路"))
        self.recorded_scene_story = str(DEFAULT_CONFIG.get("recorded_scene_story", "页面场景录制"))
        self.recorded_scene_base_class = str(
            DEFAULT_CONFIG.get("recorded_scene_base_class", "GenMdBaseTest")
        )
        self._scene_class_opened = False

    def _use_fingerprint_dedupe(self) -> bool:
        return str(self.record_dedupe_mode).strip().lower() == "fingerprint"

    def _use_request_order(self) -> bool:
        return str(self.record_order_mode).strip().lower() == "request"

    def _recording_enabled_for_capture(self) -> bool:
        if not self.recording_arm_switch:
            return True
        path = self.recording_state_path
        try:
            st_mtime = path.stat().st_mtime
        except OSError:
            self._armed_cache_mtime = -1.0
            self._armed_cache_value = False
            return False
        if st_mtime != self._armed_cache_mtime:
            self._armed_cache_mtime = st_mtime
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                self._armed_cache_value = bool(raw.get("armed", False))
            except (json.JSONDecodeError, OSError):
                self._armed_cache_value = False
        return self._armed_cache_value

    def load(self, loader) -> None:
        loader.add_option(
            name="erp_recorder_config_file",
            typespec=str,
            default=str(DEFAULT_CONFIG_FILE),
            help="JSON config file for whitelist and recorder behavior.",
        )
        loader.add_option(
            name="erp_recorder_case_file",
            typespec=str,
            default=str(DEFAULT_CASE_FILE),
            help="Generated pytest buffer file.",
        )
        loader.add_option(
            name="erp_recorder_data_dir",
            typespec=str,
            default=str(DEFAULT_DATA_DIR),
            help="Directory for large recorded payloads.",
        )
        loader.add_option(
            name="erp_recorder_body_threshold",
            typespec=int,
            default=BODY_FILE_THRESHOLD,
            help="Store request payload in JSON when request body length exceeds this threshold.",
        )

    def configure(self, updated) -> None:
        option_config_file = Path(ctx.options.erp_recorder_config_file).expanduser()
        self.config_file = option_config_file if option_config_file.is_absolute() else PROJECT_ROOT / option_config_file
        config_data = self._load_config()

        self.case_file = self._resolve_path_from_config(
            ctx.options.erp_recorder_case_file,
            str(DEFAULT_CASE_FILE),
            config_data.get("case_file"),
            DEFAULT_CASE_FILE,
        )
        self.data_dir = self._resolve_path_from_config(
            ctx.options.erp_recorder_data_dir,
            str(DEFAULT_DATA_DIR),
            config_data.get("data_dir"),
            DEFAULT_DATA_DIR,
        )
        self.dedupe_index_file = self._resolve_path_from_config(
            str(DEFAULT_DEDUPE_INDEX_FILE),
            str(DEFAULT_DEDUPE_INDEX_FILE),
            config_data.get("dedupe_index_file"),
            DEFAULT_DEDUPE_INDEX_FILE,
        )
        self.body_threshold = self._resolve_threshold(config_data)
        self.allowed_hosts = list(config_data.get("allowed_hosts", []))
        self.blocked_hosts = list(config_data.get("blocked_hosts", []))
        self.allowed_path_prefixes = list(config_data.get("allowed_path_prefixes", []))
        self.blocked_path_prefixes = list(config_data.get("blocked_path_prefixes", []))

        self.sanitize_recorded_payload = bool(config_data.get("sanitize_recorded_payload", False))
        self.sanitize_remove_keys = set(DEFAULT_SANITIZE_REMOVE_KEYS)
        self.sanitize_remove_keys.update(str(k) for k in (config_data.get("sanitize_remove_keys") or []))
        if "redact_json_keys" in config_data:
            self.redact_json_keys_lower = {str(k).lower() for k in (config_data.get("redact_json_keys") or [])}
        else:
            self.redact_json_keys_lower = {k.lower() for k in DEFAULT_REDACT_JSON_KEYS}
        self.auto_wrap_trantor_body = bool(config_data.get("auto_wrap_trantor_body", True))
        self.record_dedupe_mode = str(config_data.get("record_dedupe_mode", "none"))
        self.record_dedupe_persist = bool(
            config_data.get("record_dedupe_persist", DEFAULT_CONFIG.get("record_dedupe_persist", False))
        )
        self.record_order_mode = str(config_data.get("record_order_mode", "request"))
        self.recording_arm_switch = bool(config_data.get("recording_arm_switch", False))
        state_rel = config_data.get("recording_state_file", "api_record/runtime/recording_armed.json")
        state_path = Path(str(state_rel)).expanduser()
        self.recording_state_path = state_path if state_path.is_absolute() else PROJECT_ROOT / state_path
        self._armed_cache_mtime = -1.0
        self._armed_cache_value = False

        self.resolve_api_config_names = bool(config_data.get("resolve_api_config_names", True))
        self._path_to_api_config_name = None

        self.recorded_scene_epic = str(
            config_data.get("recorded_scene_epic", DEFAULT_CONFIG.get("recorded_scene_epic", "场景录制"))
        )
        self.recorded_scene_feature = str(
            config_data.get(
                "recorded_scene_feature", DEFAULT_CONFIG.get("recorded_scene_feature", "Mitmproxy 页面链路")
            )
        )
        self.recorded_scene_story = str(
            config_data.get("recorded_scene_story", DEFAULT_CONFIG.get("recorded_scene_story", "页面场景录制"))
        )
        self.recorded_scene_base_class = str(
            config_data.get(
                "recorded_scene_base_class", DEFAULT_CONFIG.get("recorded_scene_base_class", "GenMdBaseTest")
            )
        )
        self._scene_class_opened = False

        self._request_order_seq = 0
        self._next_flush_seq = 1
        self._pending_cases = {}
        self._skipped_seqs = set()

        self._ensure_runtime_paths()
        self._load_dedupe_index()

    def request(self, flow: http.HTTPFlow) -> None:
        if not self._use_request_order():
            return
        if not self._recording_enabled_for_capture():
            return
        if not self._should_tag_request_order(flow):
            return
        self._request_order_seq += 1
        flow.metadata[FLOW_META_RECORD_SEQ] = self._request_order_seq

    def response(self, flow: http.HTTPFlow) -> None:
        seq_meta = flow.metadata.get(FLOW_META_RECORD_SEQ) if self._use_request_order() else None
        if seq_meta is not None and not isinstance(seq_meta, int):
            try:
                seq_meta = int(seq_meta)
            except (TypeError, ValueError):
                seq_meta = None

        if not self._recording_enabled_for_capture():
            if seq_meta is not None:
                self._skipped_seqs.add(seq_meta)
                self._flush_order_queue()
            return

        if seq_meta is not None and seq_meta in self._skipped_seqs:
            # error 钩子已跳过该序号，忽略迟到的 response
            return

        draft = self._draft_from_flow(flow)

        if seq_meta is not None:
            if draft is None:
                self._skipped_seqs.add(seq_meta)
            elif self._use_fingerprint_dedupe() and draft.fingerprint in self.fingerprints:
                self._skipped_seqs.add(seq_meta)
            else:
                self._pending_cases[seq_meta] = draft
            self._flush_order_queue()
            return

        if self._use_request_order() and draft is not None:
            ctx.log.warn(
                f"[erp_recorder] 跳过未打 request 序号的录制（请检查 request/response 钩子） "
                f"{draft.method} https://{draft.host}{draft.api_path}"
            )
            return

        if not draft:
            return
        if self._use_fingerprint_dedupe() and draft.fingerprint in self.fingerprints:
            return
        recorded = self._materialize_draft(draft, browser_request_seq=None)
        self._append_case(recorded)
        ctx.log.info(
            "[erp_recorder] captured "
            f"{recorded.method} https://{recorded.host}{recorded.api_path} "
            f"-> {self._display_path(self.case_file)}"
        )

    def _should_tag_request_order(self, flow: http.HTTPFlow) -> bool:
        request = flow.request
        method = (request.method or "").upper()
        if method in SKIP_METHODS:
            return False
        host = (request.host or "").lower()
        split_result = urlsplit(request.pretty_url)
        api_path = split_result.path or "/"
        if self._should_skip_path(api_path):
            return False
        if not self._is_allowed_host(host):
            return False
        if not self._is_allowed_path(api_path):
            return False
        return self._looks_like_api_request(request)

    def _looks_like_api_request(self, request: http.Request) -> bool:
        path = (request.path or "").lower()
        req_content_type = request.headers.get("content-type", "").lower()
        accept = request.headers.get("accept", "").lower()
        if any(token in path for token in ("/api/", "/execute/", "/service/", "/openapi/")):
            return True
        if "json" in req_content_type or "json" in accept:
            return True
        if any(key in request.query for key in ("modelKey", "serviceKey", "tmodule")):
            return True
        if request.headers.get("x-requested-with", "").lower() == "xmlhttprequest":
            return True
        return False

    def _draft_from_flow(self, flow: http.HTTPFlow) -> Optional[RecordDraft]:
        request = flow.request
        response = flow.response
        if response is None:
            return None

        method = (request.method or "").upper()
        if method in SKIP_METHODS:
            return None

        host = (request.host or "").lower()
        split_result = urlsplit(request.pretty_url)
        api_path = split_result.path or "/"
        if self._should_skip_path(api_path):
            return None
        if not self._is_allowed_host(host):
            return None
        if not self._is_allowed_path(api_path):
            return None
        if not self._looks_like_api(flow):
            return None

        query_params = self._normalize_mapping(parse_qsl(split_result.query, keep_blank_values=True))
        body_payload = self._parse_request_body(request)
        body_payload, query_params = self._apply_recording_policies(api_path, method, body_payload, query_params)
        merged_payload = self._merge_payload(query_params, body_payload)
        fingerprint = self._build_fingerprint(host, method, api_path, query_params, body_payload)

        service_slug = self._build_service_slug(api_path)
        return RecordDraft(
            host=host,
            api_path=api_path,
            method=method,
            query_params=query_params,
            body_payload=body_payload,
            merged_payload=merged_payload,
            response_status=response.status_code,
            service_slug=service_slug,
            fingerprint=fingerprint,
            request=request,
        )

    def _lookup_api_config_name(self, api_path: str) -> Optional[str]:
        if not self.resolve_api_config_names:
            return None
        if self._path_to_api_config_name is None:
            self._path_to_api_config_name = get_execute_path_to_api_name(str(PROJECT_ROOT.resolve()))
        return self._path_to_api_config_name.get(api_path)

    @staticmethod
    def _slugify_for_test_segment(label: Optional[str], fallback_slug: str) -> str:
        raw = (label or "").strip() or fallback_slug
        s = raw.replace("-", "_").replace(" ", "_").replace("$", "_").replace(".", "_")
        s = re.sub(r"[^\w\u4e00-\u9fff]", "_", s)
        s = re.sub(r"_+", "_", s).strip("_")
        if not s:
            s = fallback_slug
        if s[:1].isdigit():
            s = f"n_{s}"
        if len(s) > 100:
            s = s[:100].rstrip("_")
        return s

    def _format_recorded_test_name(
        self,
        *,
        method: str,
        service_slug: str,
        output_seq: int,
        api_config_name: Optional[str],
    ) -> str:
        seg = self._slugify_for_test_segment(api_config_name, service_slug)
        m = (method or "POST").lower()
        return f"test_{m}_{seg}_{output_seq:03d}"

    def _materialize_draft(self, draft: RecordDraft, browser_request_seq: Optional[int]) -> RecordedCase:
        self.case_index += 1
        output_seq = self.case_index
        api_config_name = self._lookup_api_config_name(draft.api_path)
        test_name = self._format_recorded_test_name(
            method=draft.method,
            service_slug=draft.service_slug,
            output_seq=output_seq,
            api_config_name=api_config_name,
        )
        payload_file = self._persist_large_payload(draft.service_slug, draft.merged_payload, draft.request)

        return RecordedCase(
            host=draft.host,
            api_path=draft.api_path,
            method=draft.method,
            query_params=draft.query_params,
            body_payload=draft.body_payload,
            merged_payload=draft.merged_payload,
            response_status=draft.response_status,
            test_name=test_name,
            payload_file=payload_file,
            service_slug=draft.service_slug,
            fingerprint=draft.fingerprint,
            output_seq=output_seq,
            browser_request_seq=browser_request_seq,
            api_config_name=api_config_name,
        )

    def _flush_order_queue(self) -> None:
        while True:
            if self._next_flush_seq in self._pending_cases:
                draft = self._pending_cases.pop(self._next_flush_seq)
                recorded = self._materialize_draft(draft, browser_request_seq=self._next_flush_seq)
                self._append_case(recorded)
                ctx.log.info(
                    "[erp_recorder] captured "
                    f"{recorded.method} https://{recorded.host}{recorded.api_path} "
                    f"(browser_seq={self._next_flush_seq}) -> {self._display_path(self.case_file)}"
                )
                self._next_flush_seq += 1
            elif self._next_flush_seq in self._skipped_seqs:
                self._skipped_seqs.discard(self._next_flush_seq)
                self._next_flush_seq += 1
            else:
                break

    def error(self, flow: http.HTTPFlow) -> None:
        """无正常 response（如 Client disconnected、上游失败）时补 skipped，避免 request 序号永远等不到而堵死队列。"""
        if not self._use_request_order():
            return
        seq_meta = flow.metadata.get(FLOW_META_RECORD_SEQ)
        if seq_meta is not None and not isinstance(seq_meta, int):
            try:
                seq_meta = int(seq_meta)
            except (TypeError, ValueError):
                seq_meta = None
        if seq_meta is None:
            return

        if not self._recording_enabled_for_capture():
            self._skipped_seqs.add(seq_meta)
            self._flush_order_queue()
            return

        self._pending_cases.pop(seq_meta, None)
        self._skipped_seqs.add(seq_meta)
        req = flow.request
        ctx.log.warn(
            "[erp_recorder] flow error, skip queue seq=%s %s https://%s%s",
            seq_meta,
            getattr(req, "method", "?"),
            getattr(req, "host", ""),
            getattr(req, "path", ""),
        )
        self._flush_order_queue()

    def _append_case(self, recorded: RecordedCase) -> None:
        self._ensure_runtime_paths()
        self._bootstrap_case_file()
        if self._use_fingerprint_dedupe():
            self.fingerprints.add(recorded.fingerprint)
            if self.record_dedupe_persist:
                self._save_dedupe_index()

        chunks = []
        if not self._scene_class_opened:
            chunks.append(self._render_scene_class_opening())
            self._scene_class_opened = True
        chunks.append(self._render_scene_method(recorded))
        case_block = "".join(chunks)
        with open(self.case_file, "a", encoding="utf-8") as file_obj:
            file_obj.write(case_block)

    def _ensure_runtime_paths(self) -> None:
        self.case_file.parent.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.dedupe_index_file.parent.mkdir(parents=True, exist_ok=True)
        if self.recording_arm_switch:
            self.recording_state_path.parent.mkdir(parents=True, exist_ok=True)

        init_file = self.case_file.parent / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# -*- coding: utf-8 -*-\n", encoding="utf-8")

    def _bootstrap_case_file(self) -> None:
        if not self.case_file.exists():
            self.case_file.write_text(self._render_module_header(), encoding="utf-8")
            return

        current_text = self.case_file.read_text(encoding="utf-8")
        if HEADER_MARKER in current_text:
            return

        self.case_file.write_text(self._render_module_header() + "\n\n" + current_text, encoding="utf-8")

    def _persist_large_payload(
        self,
        service_slug: str,
        merged_payload: Dict[str, Any],
        request: http.Request,
    ) -> Optional[Path]:
        body_text = self._get_request_text(request)
        if len(body_text) <= self.body_threshold:
            return None

        file_name = f"{service_slug}_{self.session_ts}_{self.case_index:03d}.json"
        target_file = self.data_dir / file_name
        with open(target_file, "w", encoding="utf-8") as file_obj:
            json.dump(merged_payload, file_obj, ensure_ascii=False, indent=2)
        return target_file

    def _render_module_header(self) -> str:
        return textwrap.dedent(
            """\
            # -*- coding: utf-8 -*-
            \"\"\"Generated by api_record/recorder.py（场景骨架对齐 .cursor/rules/testcase_temp.mdc）。\"\"\"

            import copy
            import json
            from pathlib import Path

            import allure
            import pytest

            from testcases.comm.base_test import BaseTest
            from testcases.erp_fin import FinBaseTest
            from testcases.gen_md import GenMdBaseTest
            from utils.report_util import a, case_decorator


            # 本目录为 api_record/（非仓库根目录），仅用于定位 testdata/recorded 等录制资产
            API_RECORD_ROOT = Path(__file__).resolve().parents[1]


            class RecordedFlowMixin:
                @classmethod
                def _register_direct_api(cls, api_path, method, body_template=None):
                    if getattr(cls, "apis", None) is None:
                        cls.apis = {}
                    if getattr(cls, "api_params", None) is None:
                        cls.api_params = {}

                    cls.apis[api_path] = {"path": api_path, "method": method}
                    if method in {"POST", "PUT", "PATCH"}:
                        cls.api_params[api_path] = copy.deepcopy(body_template) if body_template is not None else {}
                    else:
                        cls.api_params.setdefault(api_path, {})

                def _replay_recorded_api(self, api_path, method, request_body, query_params=None):
                    \"\"\"与 test_business_partner_management._execute_direct_api 对齐的录制回放入口。\"\"\"
                    method = (method or "POST").upper()
                    if method in {"GET", "DELETE"}:
                        self._register_direct_api(api_path, method, body_template=request_body)
                        return self.standard_api_call(
                            api_key=api_path,
                            set_dict=request_body,
                            use_param_util=False,
                            method=method,
                            query_params=query_params,
                        )

                    inner = None
                    if isinstance(request_body, dict):
                        params_obj = request_body.get("params")
                        if isinstance(params_obj, dict) and "request" in params_obj:
                            inner = params_obj.get("request")

                    if inner is not None:
                        self._register_direct_api(api_path, method, body_template=request_body)
                        return self.standard_api_call(
                            api_key=api_path,
                            set_dict=inner,
                            use_param_util=False,
                            param_path=["params", "request"],
                            method=method,
                            query_params=query_params,
                        )

                    self._register_direct_api(api_path, method, body_template=request_body)
                    return self.standard_api_call(
                        api_key=api_path,
                        set_dict=request_body,
                        use_param_util=False,
                        param_path=[],
                        method=method,
                        query_params=query_params,
                    )

                @staticmethod
                def _split_recorded_payload(set_dict):
                    if isinstance(set_dict, dict):
                        query_params = copy.deepcopy(set_dict.get("{RECORDED_QUERY_KEY}", {}))
                        body_payload = copy.deepcopy(set_dict.get("{RECORDED_BODY_KEY}", {}))
                        if "{RECORDED_QUERY_KEY}" in set_dict or "{RECORDED_BODY_KEY}" in set_dict:
                            return query_params or None, body_payload
                    return None, copy.deepcopy(set_dict)
            """
        ).replace("{RECORDED_QUERY_KEY}", RECORDED_QUERY_KEY).replace(
            "{RECORDED_BODY_KEY}", RECORDED_BODY_KEY
        ).rstrip()

    def _scene_base_class_normalized(self) -> str:
        b = (self.recorded_scene_base_class or "GenMdBaseTest").strip()
        if b not in ("GenMdBaseTest", "BaseTest", "FinBaseTest"):
            return "GenMdBaseTest"
        return b

    def _render_scene_class_opening(self) -> str:
        base = self._scene_base_class_normalized()
        lines = [
            "",
            "",
            f"@allure.epic({self.recorded_scene_epic!r})",
            f"@allure.feature({self.recorded_scene_feature!r})",
            f"class TestRecordedScene_{self.session_ts}(RecordedFlowMixin, {base}):",
            '    """Mitmproxy 录制场景（第一版），类骨架对齐 .cursor/rules/testcase_temp.mdc。"""',
            "",
            "    @classmethod",
            "    def setup_class(cls):",
            '        """安全初始化 init_data / md_cache_data（与 testcase_temp 一致）。"""',
            "        super().setup_class()",
            '        cls.logger.info("录制场景测试类初始化完成")',
            "        if cls.init_data:",
            '            cls.curr_id = cls.init_data["currency_info"][0]["curr_id"] if cls.init_data.get("currency_info") else None',
            '            cls.coun_id = cls.init_data["country_info"][0]["coun_id"] if cls.init_data.get("country_info") else None',
            '            cls.addr_id = cls.init_data["addr_info"][0]["id"] if cls.init_data.get("addr_info") else None',
            '            cls.bank_id = cls.init_data["bank_info"][0]["bank_id"] if cls.init_data.get("bank_info") else None',
            '            cls.gen_wc_head_id = cls.init_data["gen_wc_head_info"][0]["gen_wc_head_id"] if cls.init_data.get("gen_wc_head_info") else None',  # noqa: E501
            '            cls.calender_id = cls.init_data["calender_info"][0]["id"] if cls.init_data.get("calender_info") else None',
            "        else:",
            "            cls.curr_id = cls.coun_id = cls.addr_id = None",
            "            cls.bank_id = cls.gen_wc_head_id = cls.calender_id = None",
            '        if getattr(cls, "md_cache_data", None):',
            '            cust_info = cls.md_cache_data.get("partner_info", {}).get("cust_info", [])',
            '            cls.cust_id = cust_info[0].get("id") if cust_info else None',
            '            gr_come_org_info = cls.md_cache_data.get("org_info", {}).get("gr_come_org_info", [])',
            '            cls.com_org_id = gr_come_org_info[0].get("id") if gr_come_org_info else None',
            '            sls_org_info = cls.md_cache_data.get("org_info", {}).get("sls_org_info", [])',
            '            cls.sls_org_id = sls_org_info[0].get("id") if sls_org_info else None',
            '            inv_org_info = cls.md_cache_data.get("org_info", {}).get("inv_org_info", [])',
            '            cls.inv_org_id = inv_org_info[0].get("id") if inv_org_info else None',
            '            cls.org_business_type_ids = cls.md_cache_data.get("org_info", {}).get("org_biz_type_cf", [])',
            '            sls_dc_md = cls.md_cache_data.get("org_info", {}).get("sls_dc_md", [])',
            '            cls.sls_dc_id = sls_dc_md[0].get("id") if sls_dc_md else None',
            '            inv_wh_md = cls.md_cache_data.get("org_info", {}).get("inv_wh_md", [])',
            '            cls.wh_id = inv_wh_md[0].get("id") if inv_wh_md else None',
            '            mat_md = cls.md_cache_data.get("mat_info", {}).get("mat_md", {})',
            '            finp_list = mat_md.get("FINP", [])',
            '            cls.mat_id = finp_list[0].get("id") if finp_list else None',
            "        else:",
            "            cls.cust_id = cls.com_org_id = cls.sls_org_id = cls.inv_org_id = None",
            "            cls.org_business_type_ids = []",
            "            cls.sls_dc_id = cls.wh_id = cls.mat_id = None",
            "",
            "    @classmethod",
            "    def teardown_class(cls):",
            '        """转正后按业务逐表清理（禁止 for 循环表名）；录制阶段默认不删数据。"""',
            "        try:",
            '            cls.logger.info("录制场景 teardown_class：跳过库表清理")',
            "        except Exception as e:",
            '            cls.logger.error("teardown_class 失败: %s", str(e))',
            "",
        ]
        return "\n".join(lines)

    def _assert_call_for_scene_step(self, recorded: RecordedCase) -> str:
        blob = f"{recorded.api_path} {recorded.api_config_name or ''} {recorded.service_slug}".lower()
        if any(
            token in blob
            for token in (
                "query_page",
                "paging",
                "分页",
                "page_action",
                "paging_data",
                "station/paging",
            )
        ):
            return "self.assert_util.assert_response_data(response)"
        return "self.assert_util.assert_response_success(response)"

    def _scene_tags(self, recorded: RecordedCase) -> list:
        tags = ["录制场景", "mitmproxy"]
        if recorded.api_config_name:
            tags.append("接口已映射")
        if "gen_md" in recorded.api_path.lower():
            tags.append("GEN_MD")
        if "sys_common" in recorded.api_path.lower():
            tags.append("sys_common")
        return tags

    def _render_scene_method(self, recorded: RecordedCase) -> str:
        method_title = (
            f"步骤{recorded.output_seq:03d} {recorded.api_config_name}"
            if recorded.api_config_name
            else f"步骤{recorded.output_seq:03d} ({recorded.service_slug})"
        )
        step_desc = (
            f"录制回放第 {recorded.output_seq} 步；YAML 服务名: {recorded.api_config_name}"
            if recorded.api_config_name
            else f"录制回放第 {recorded.output_seq} 步（未映射 YAML 路径名）"
        )
        assert_line = self._assert_call_for_scene_step(recorded)
        tags_repr = repr(self._scene_tags(recorded))
        return self._render_scene_method_body(
            recorded, method_title, step_desc, assert_line, tags_repr
        )

    def _render_scene_method_body(
        self,
        recorded: RecordedCase,
        method_title: str,
        step_desc: str,
        assert_line: str,
        tags_repr: str,
    ) -> str:
        if recorded.payload_file:
            payload_literal = self._display_api_record_path(recorded.payload_file)
            payload_loader = (
                f"            with open(API_RECORD_ROOT / {payload_literal!r}, \"r\", encoding=\"utf-8\") as file_obj:\n"
                f"                set_dict = json.load(file_obj)"
            )
        else:
            payload_loader = "set_dict = " + self._to_pretty_json(recorded.merged_payload, indent=0)
            payload_loader = textwrap.indent(payload_loader, "            ")

        parts = [
            "",
            f"    @case_decorator(",
            f"        story={self.recorded_scene_story!r},",
            f"        title={method_title!r},",
            f"        description={step_desc!r},",
            '        severity="normal",',
            f"        file_level_order={recorded.output_seq},",
            f"        tags={tags_repr},",
            "    )",
            f"    def {recorded.test_name}(self):",
            f'        """录制步骤 {recorded.output_seq}（禁止调用其他 test_*；转正时抽 helper）。"""',
            "        try:",
            "            # 1. 准备 / 加载请求体",
            payload_loader,
            "            # 2. 拆分 query 与 body（见 RecordedFlowMixin._split_recorded_payload）",
            "            query_params, request_body = self._split_recorded_payload(set_dict)",
            "            # 3. 调用接口；转正后优先 standard_api_call(api_key=YAML服务名, …)",
            "            response, _ = self._replay_recorded_api(",
            f"                api_path={recorded.api_path!r},",
            f"                method={recorded.method!r},",
            "                request_body=request_body,",
            "                query_params=query_params,",
            "            )",
            "            # 4. 断言（分页/列表类可按需改为更强的业务校验）",
            f"            {assert_line}",
            '            a.json(set_dict, "录制请求体")',
            '            a.json(response, "响应数据")',
            "        except Exception as e:",
            '            a.text(str(e), "失败原因")',
            "            raise",
            "",
        ]
        return "\n".join(parts)

    def _looks_like_api(self, flow: http.HTTPFlow) -> bool:
        request = flow.request
        response = flow.response
        path = (request.path or "").lower()
        req_content_type = request.headers.get("content-type", "").lower()
        resp_content_type = response.headers.get("content-type", "").lower() if response else ""

        if any(token in path for token in ("/api/", "/execute/", "/service/", "/openapi/")):
            return True
        if "json" in req_content_type or "json" in resp_content_type:
            return True
        if any(key in request.query for key in ("modelKey", "serviceKey", "tmodule")):
            return True
        if request.headers.get("x-requested-with", "").lower() == "xmlhttprequest":
            return True
        return False

    def _should_skip_path(self, api_path: str) -> bool:
        lowered_path = api_path.lower()
        if not lowered_path or lowered_path == "/":
            return True
        return any(lowered_path.endswith(ext) for ext in SKIP_EXTENSIONS)

    def _is_allowed_host(self, host: str) -> bool:
        if self._matches_host_patterns(host, self.blocked_hosts):
            return False
        if not self.allowed_hosts:
            return True
        return self._matches_host_patterns(host, self.allowed_hosts)

    def _is_allowed_path(self, api_path: str) -> bool:
        if self.blocked_path_prefixes and any(api_path.startswith(prefix) for prefix in self.blocked_path_prefixes):
            return False
        if not self.allowed_path_prefixes:
            return True
        return any(api_path.startswith(prefix) for prefix in self.allowed_path_prefixes)

    def _matches_host_patterns(self, host: str, patterns) -> bool:
        for pattern in patterns:
            normalized = str(pattern).lower().strip()
            if not normalized:
                continue
            if normalized.startswith(".") and host.endswith(normalized):
                return True
            if host == normalized or host.endswith(f".{normalized}"):
                return True
        return False

    def _build_fingerprint(
        self,
        host: str,
        method: str,
        api_path: str,
        query_params: Dict[str, Any],
        body_payload: Any,
    ) -> str:
        payload = {
            "host": host,
            "method": method,
            "path": api_path,
            "query": self._normalize_for_hash(query_params),
            "body": self._normalize_for_hash(body_payload),
        }
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()

    def _normalize_for_hash(self, payload: Any) -> Any:
        if isinstance(payload, dict):
            return {key: self._normalize_for_hash(payload[key]) for key in sorted(payload)}
        if isinstance(payload, list):
            return [self._normalize_for_hash(item) for item in payload]
        return payload

    def _parse_request_body(self, request: http.Request) -> Any:
        body_text = self._get_request_text(request)
        if not body_text:
            return {}

        content_type = request.headers.get("content-type", "").lower()
        if "application/json" in content_type or self._looks_like_json(body_text):
            try:
                return json.loads(body_text)
            except json.JSONDecodeError:
                return {"raw_body": body_text}

        if "application/x-www-form-urlencoded" in content_type:
            return self._normalize_mapping(parse_qsl(body_text, keep_blank_values=True))

        return {"raw_body": body_text}

    def _maybe_wrap_trantor_body(self, api_path: str, method: str, body_payload: Any) -> Any:
        if not self.auto_wrap_trantor_body or method not in {"POST", "PUT", "PATCH"}:
            return body_payload
        if not isinstance(body_payload, dict) or not body_payload:
            return body_payload
        if "raw_body" in body_payload and len(body_payload) == 1:
            return body_payload

        lower_path = api_path.lower()
        if "engine/execute" not in lower_path and "/execute/" not in lower_path:
            return body_payload

        if isinstance(body_payload.get("params"), dict):
            return body_payload

        if TRANTOR_ENVELOPE_TOP_KEYS.intersection(body_payload.keys()):
            return body_payload

        return {"params": {"request": copy.deepcopy(body_payload)}}

    def _apply_recording_policies(
        self,
        api_path: str,
        method: str,
        body_payload: Any,
        query_params: Dict[str, Any],
    ) -> Tuple[Any, Dict[str, Any]]:
        redact_keys = self.redact_json_keys_lower
        qp = _redact_mapping(copy.deepcopy(query_params), redact_keys)
        if isinstance(body_payload, dict):
            bp: Any = _redact_mapping(copy.deepcopy(body_payload), redact_keys)
        else:
            bp = copy.deepcopy(body_payload)

        if self.sanitize_recorded_payload:
            qp = _sanitize_remove_keys(qp, self.sanitize_remove_keys)
            if isinstance(bp, dict):
                bp = _sanitize_remove_keys(bp, self.sanitize_remove_keys)

        bp = self._maybe_wrap_trantor_body(api_path, method, bp)
        return bp, qp

    def _merge_payload(self, query_params: Dict[str, Any], body_payload: Any) -> Dict[str, Any]:
        merged: Dict[str, Any] = {}
        if isinstance(body_payload, dict):
            merged.update(body_payload)

        for key, value in query_params.items():
            if key not in merged:
                merged[key] = value
                continue
            if merged[key] == value:
                continue
            merged[f"query_{key}"] = value

        merged[RECORDED_QUERY_KEY] = query_params
        merged[RECORDED_BODY_KEY] = body_payload
        return merged

    def _get_request_text(self, request: http.Request) -> str:
        try:
            return request.get_text(strict=False) or ""
        except TypeError:
            return request.get_text() or ""
        except ValueError:
            raw_content = request.raw_content or b""
            return raw_content.decode("utf-8", errors="ignore")

    def _looks_like_json(self, body_text: str) -> bool:
        body_text = body_text.strip()
        return (body_text.startswith("{") and body_text.endswith("}")) or (
            body_text.startswith("[") and body_text.endswith("]")
        )

    def _normalize_mapping(self, items) -> Dict[str, Any]:
        normalized: Dict[str, Any] = {}
        for key, value in items:
            if key in normalized:
                if not isinstance(normalized[key], list):
                    normalized[key] = [normalized[key]]
                normalized[key].append(value)
                continue
            normalized[key] = value
        return normalized

    def _build_service_slug(self, api_path: str) -> str:
        parts = [part for part in api_path.split("/") if part]
        candidate = parts[-1] if parts else "root"
        candidate = candidate or "root"
        slug = re.sub(r"[^0-9A-Za-z_]+", "_", candidate)
        slug = re.sub(r"_+", "_", slug).strip("_")
        return (slug or "manual_flow").lower()

    def _display_path(self, path_obj: Path) -> str:
        try:
            return str(path_obj.relative_to(PROJECT_ROOT)).replace("\\", "/")
        except ValueError:
            return str(path_obj).replace("\\", "/")

    def _display_api_record_path(self, path_obj: Path) -> str:
        try:
            return str(path_obj.relative_to(API_RECORD_ROOT)).replace("\\", "/")
        except ValueError:
            return self._display_path(path_obj)

    def _to_pretty_json(self, payload: Dict[str, Any], indent: int = 4) -> str:
        pretty = json.dumps(payload, ensure_ascii=False, indent=2)
        if indent <= 0:
            return pretty
        padding = " " * indent
        return pretty.replace("\n", f"\n{padding}")

    def _load_config(self) -> Dict[str, Any]:
        config = dict(DEFAULT_CONFIG)
        if not self.config_file.exists():
            return config

        with open(self.config_file, "r", encoding="utf-8") as file_obj:
            loaded = json.load(file_obj)
        config.update(loaded)
        return config

    def _load_dedupe_index(self) -> None:
        if not self._use_fingerprint_dedupe():
            self.fingerprints = set()
            return
        if not self.record_dedupe_persist:
            self.fingerprints = set()
            return
        if not self.dedupe_index_file.exists():
            self.fingerprints = set()
            return

        with open(self.dedupe_index_file, "r", encoding="utf-8") as file_obj:
            data = json.load(file_obj)
        self.fingerprints = set(data if isinstance(data, list) else [])

    def _save_dedupe_index(self) -> None:
        with open(self.dedupe_index_file, "w", encoding="utf-8") as file_obj:
            json.dump(sorted(self.fingerprints), file_obj, ensure_ascii=False, indent=2)

    def _resolve_path_from_config(
        self,
        option_value: str,
        default_option_value: str,
        config_value: Optional[str],
        default_path: Path,
    ) -> Path:
        if option_value != default_option_value:
            path_obj = Path(option_value).expanduser()
            return path_obj if path_obj.is_absolute() else PROJECT_ROOT / path_obj

        if config_value:
            path_obj = Path(config_value).expanduser()
            return path_obj if path_obj.is_absolute() else PROJECT_ROOT / path_obj

        return default_path

    def _resolve_threshold(self, config_data: Dict[str, Any]) -> int:
        option_value = int(ctx.options.erp_recorder_body_threshold)
        if option_value != BODY_FILE_THRESHOLD:
            return option_value
        return int(config_data.get("body_threshold", BODY_FILE_THRESHOLD))


addons = [ErpFlowRecorder()]
