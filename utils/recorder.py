# -*- coding: utf-8 -*-
"""
Mitmproxy recorder for the ERP autotest project.

Usage:
    mitmdump -s utils/recorder.py
"""

import hashlib
import json
import re
import textwrap
import time
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import parse_qsl, urlsplit

from mitmproxy import ctx, http


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CASE_FILE = PROJECT_ROOT / "testcases" / "generated_cases" / "test_manual_flow.py"
DEFAULT_DATA_DIR = PROJECT_ROOT / "testdata" / "recorded"
DEFAULT_CONFIG_FILE = PROJECT_ROOT / "config" / "recorder_config.json"
DEFAULT_DEDUPE_INDEX_FILE = PROJECT_ROOT / "testcases" / "generated_cases" / ".recorder_index.json"
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
    "case_file": "testcases/generated_cases/test_manual_flow.py",
    "data_dir": "testdata/recorded",
    "dedupe_index_file": "testcases/generated_cases/.recorder_index.json",
}

SKIP_METHODS = {"CONNECT", "HEAD", "OPTIONS"}
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


class RecordedCase:
    def __init__(
        self,
        host: str,
        api_path: str,
        base_class: str,
        method: str,
        query_params: Dict[str, Any],
        body_payload: Any,
        merged_payload: Dict[str, Any],
        response_status: int,
        class_name: str,
        test_name: str,
        payload_file: Optional[Path],
        service_slug: str,
        fingerprint: str,
    ) -> None:
        self.host = host
        self.api_path = api_path
        self.base_class = base_class
        self.method = method
        self.query_params = query_params
        self.body_payload = body_payload
        self.merged_payload = merged_payload
        self.response_status = response_status
        self.class_name = class_name
        self.test_name = test_name
        self.payload_file = payload_file
        self.service_slug = service_slug
        self.fingerprint = fingerprint


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

        self._ensure_runtime_paths()
        self._load_dedupe_index()

    def response(self, flow: http.HTTPFlow) -> None:
        recorded = self._build_recorded_case(flow)
        if not recorded:
            return

        self._append_case(recorded)
        ctx.log.info(
            "[erp_recorder] captured "
            f"{recorded.method} https://{recorded.host}{recorded.api_path} "
            f"-> {self._display_path(self.case_file)}"
        )

    def _build_recorded_case(self, flow: http.HTTPFlow) -> Optional[RecordedCase]:
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
        merged_payload = self._merge_payload(query_params, body_payload)
        fingerprint = self._build_fingerprint(host, method, api_path, query_params, body_payload)
        if fingerprint in self.fingerprints:
            return None

        self.case_index += 1
        service_slug = self._build_service_slug(api_path)
        class_name = f"TestFlow_{self.session_ts}_{self.case_index:03d}"
        test_name = f"test_{method.lower()}_{service_slug}_{self.case_index:03d}"
        payload_file = self._persist_large_payload(service_slug, merged_payload, request)

        return RecordedCase(
            host=host,
            api_path=api_path,
            base_class=self._resolve_base_class(api_path),
            method=method,
            query_params=query_params,
            body_payload=body_payload,
            merged_payload=merged_payload,
            response_status=response.status_code,
            class_name=class_name,
            test_name=test_name,
            payload_file=payload_file,
            service_slug=service_slug,
            fingerprint=fingerprint,
        )

    def _append_case(self, recorded: RecordedCase) -> None:
        self._ensure_runtime_paths()
        self._bootstrap_case_file()
        self.fingerprints.add(recorded.fingerprint)
        self._save_dedupe_index()

        case_block = self._render_case_block(recorded)
        with open(self.case_file, "a", encoding="utf-8") as file_obj:
            file_obj.write(case_block)

    def _ensure_runtime_paths(self) -> None:
        self.case_file.parent.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.dedupe_index_file.parent.mkdir(parents=True, exist_ok=True)

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
            \"\"\"Generated by utils/recorder.py.\"\"\"

            import copy
            import json
            from pathlib import Path

            import allure

            from testcases.comm.base_test import BaseTest
            from testcases.erp_fin import FinBaseTest
            from testcases.gen_md import GenMdBaseTest
            from utils.report_util import a


            PROJECT_ROOT = Path(__file__).resolve().parents[2]


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

    def _render_case_block(self, recorded: RecordedCase) -> str:
        if recorded.payload_file:
            payload_literal = self._display_path(recorded.payload_file)
            payload_loader = textwrap.dedent(
                f"""\
                with open(PROJECT_ROOT / {payload_literal!r}, "r", encoding="utf-8") as file_obj:
                    set_dict = json.load(file_obj)
                """
            ).rstrip()
        else:
            payload_loader = f"set_dict = {self._to_pretty_json(recorded.merged_payload, indent=0)}"

        payload_loader = textwrap.indent(payload_loader, " " * 12)

        case_source = f"""


@allure.epic("Manual Recorded Flow")
@allure.feature("Mitmproxy Recorder")
class {recorded.class_name}(RecordedFlowMixin, {recorded.base_class}):
    \"\"\"Recorded from {recorded.method} https://{recorded.host}{recorded.api_path} (status={recorded.response_status}).\"\"\"

    RECORDED_HOST = {recorded.host!r}
    RECORDED_FINGERPRINT = {recorded.fingerprint!r}

    def {recorded.test_name}(self):
        try:
{payload_loader}
            query_params, request_body = self._split_recorded_payload(set_dict)
            self._register_direct_api(
                api_path={recorded.api_path!r},
                method={recorded.method!r},
                body_template=request_body,
            )

            response, _ = self.standard_api_call(
                api_key={recorded.api_path!r},
                set_dict=request_body,
                use_param_util=False,
                param_path=[],
                method={recorded.method!r},
                query_params=query_params,
            )
            self.assert_util.assert_response_success(response)
            a.json(set_dict, "recorded_set_dict")
            a.json(response, "response_data")
        except Exception as exc:
            a.text(str(exc), "failure_reason")
            raise
"""
        return textwrap.dedent(case_source)

    def _resolve_base_class(self, api_path: str) -> str:
        lowered_path = api_path.lower()
        if "gen_md" in lowered_path:
            return "GenMdBaseTest"
        if "erp_fin" in lowered_path:
            return "FinBaseTest"
        return "BaseTest"

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
