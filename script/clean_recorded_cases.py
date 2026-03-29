#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Clean recorded cases using recorder_config.json."""

import json
import re
from pathlib import Path
from urllib.parse import urlsplit


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_ROOT / "config" / "recorder_config.json"

DEFAULT_CONFIG = {
    "allowed_hosts": [],
    "blocked_hosts": [],
    "allowed_path_prefixes": [],
    "blocked_path_prefixes": [],
    "clean_dedupe_mode": "api_path",
    "case_file": "testcases/generated_cases/test_manual_flow.py",
    "data_dir": "testdata/recorded",
    "dedupe_index_file": "testcases/generated_cases/.recorder_index.json",
}

BLOCK_SPLIT_PATTERN = re.compile(
    r'(?=^@allure\.epic\("Manual Recorded Flow"\)\n@allure\.feature\("Mitmproxy Recorder"\)\nclass )',
    re.M,
)
RECORDED_FROM_PATTERN = re.compile(r"Recorded from (\w+) (.+?) \(status=")
HOST_PATTERN = re.compile(r"RECORDED_HOST = '([^']+)'")
FINGERPRINT_PATTERN = re.compile(r"RECORDED_FINGERPRINT = '([^']+)'")
PAYLOAD_FILE_PATTERN = re.compile(r"with open\(PROJECT_ROOT / '([^']+)'")


def load_config():
    config = dict(DEFAULT_CONFIG)
    if CONFIG_FILE.exists():
        config.update(json.loads(CONFIG_FILE.read_text(encoding="utf-8")))
    config["case_file"] = resolve_path(config["case_file"])
    config["data_dir"] = resolve_path(config["data_dir"])
    config["dedupe_index_file"] = resolve_path(config["dedupe_index_file"])
    return config


def resolve_path(path_text):
    path_obj = Path(path_text)
    return path_obj if path_obj.is_absolute() else PROJECT_ROOT / path_obj


def matches_host_patterns(host, patterns):
    for pattern in patterns:
        normalized = str(pattern).lower().strip()
        if not normalized:
            continue
        if normalized.startswith(".") and host.endswith(normalized):
            return True
        if host == normalized or host.endswith(f".{normalized}"):
            return True
    return False


def is_allowed_host(host, config):
    if not host:
        return True
    if matches_host_patterns(host, config["blocked_hosts"]):
        return False
    if not config["allowed_hosts"]:
        return True
    return matches_host_patterns(host, config["allowed_hosts"])


def is_allowed_path(path, config):
    if config["blocked_path_prefixes"] and any(path.startswith(prefix) for prefix in config["blocked_path_prefixes"]):
        return False
    if not config["allowed_path_prefixes"]:
        return True
    return any(path.startswith(prefix) for prefix in config["allowed_path_prefixes"])


def split_case_blocks(text):
    parts = BLOCK_SPLIT_PATTERN.split(text)
    header = parts[0]
    blocks = [part.strip() for part in parts[1:] if part.strip()]
    return header.rstrip(), blocks


def extract_block_meta(block):
    recorded_match = RECORDED_FROM_PATTERN.search(block)
    if not recorded_match:
        return None

    method = recorded_match.group(1)
    target = recorded_match.group(2)
    host_match = HOST_PATTERN.search(block)
    host = host_match.group(1).lower() if host_match else ""
    if target.startswith("http://") or target.startswith("https://"):
        split_result = urlsplit(target)
        path = split_result.path or "/"
        host = host or split_result.hostname or ""
    else:
        path = target

    fingerprint_match = FINGERPRINT_PATTERN.search(block)
    payload_file_match = PAYLOAD_FILE_PATTERN.search(block)
    return {
        "method": method,
        "path": path,
        "host": host,
        "fingerprint": fingerprint_match.group(1) if fingerprint_match else "",
        "payload_file": payload_file_match.group(1) if payload_file_match else "",
        "block": block.strip(),
    }


def payload_exists(payload_file):
    if not payload_file:
        return True
    return (PROJECT_ROOT / payload_file).exists()


def main():
    config = load_config()
    case_file = Path(config["case_file"])
    if not case_file.exists():
        print(f"case file not found: {case_file}")
        return 1

    text = case_file.read_text(encoding="utf-8")
    header, raw_blocks = split_case_blocks(text)

    kept_blocks = []
    seen = set()
    kept_fingerprints = []

    removed_count = 0
    duplicate_count = 0
    filtered_count = 0
    missing_payload_count = 0

    dedupe_mode = str(config.get("clean_dedupe_mode", "api_path")).strip().lower()
    for raw_block in raw_blocks:
        meta = extract_block_meta(raw_block)
        if not meta:
            removed_count += 1
            continue

        if not is_allowed_host(meta["host"], config) or not is_allowed_path(meta["path"], config):
            filtered_count += 1
            continue

        if not payload_exists(meta["payload_file"]):
            missing_payload_count += 1
            continue

        if dedupe_mode == "fingerprint":
            dedupe_key = meta["fingerprint"] or f"{meta['method']}::{meta['host']}::{meta['path']}"
        else:
            dedupe_key = f"{meta['method']}::{meta['host']}::{meta['path']}"
        if dedupe_key in seen:
            duplicate_count += 1
            continue

        seen.add(dedupe_key)
        if meta["fingerprint"]:
            kept_fingerprints.append(meta["fingerprint"])
        kept_blocks.append(meta["block"])

    new_text = header
    if kept_blocks:
        new_text = header + "\n\n\n" + "\n\n\n".join(kept_blocks) + "\n"
    else:
        new_text = header + "\n"
    case_file.write_text(new_text, encoding="utf-8")

    dedupe_index_file = Path(config["dedupe_index_file"])
    dedupe_index_file.parent.mkdir(parents=True, exist_ok=True)
    dedupe_index_file.write_text(json.dumps(sorted(set(kept_fingerprints)), ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"kept_blocks={len(kept_blocks)}")
    print(f"filtered_blocks={filtered_count}")
    print(f"duplicate_blocks={duplicate_count}")
    print(f"missing_payload_blocks={missing_payload_count}")
    print("removed_payload_files=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
