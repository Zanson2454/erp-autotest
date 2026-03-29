#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scan and optionally delete orphan payload files in testdata/recorded."""

import argparse
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CASE_ROOT = PROJECT_ROOT / "testcases"
PAYLOAD_ROOT = PROJECT_ROOT / "testdata" / "recorded"
PAYLOAD_REF_PATTERN = re.compile(r"(testdata/recorded/[^'\"\s)]+\.json)")


def collect_referenced_payloads():
    referenced = set()
    for py_file in CASE_ROOT.rglob("test_*.py"):
        text = py_file.read_text(encoding="utf-8")
        for match in PAYLOAD_REF_PATTERN.findall(text):
            referenced.add(match)
    return referenced


def collect_existing_payloads():
    if not PAYLOAD_ROOT.exists():
        return set()
    return {
        str(path.relative_to(PROJECT_ROOT))
        for path in PAYLOAD_ROOT.rglob("*.json")
    }


def main():
    parser = argparse.ArgumentParser(description="Clean orphan recorded payloads.")
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete orphan payload files instead of only printing them.",
    )
    args = parser.parse_args()

    referenced = collect_referenced_payloads()
    existing = collect_existing_payloads()
    orphaned = sorted(existing - referenced)

    print(f"referenced_payloads={len(referenced)}")
    print(f"existing_payloads={len(existing)}")
    print(f"orphaned_payloads={len(orphaned)}")

    for item in orphaned:
        print(item)

    if args.delete:
        for item in orphaned:
            (PROJECT_ROOT / item).unlink(missing_ok=True)
        print(f"deleted_payloads={len(orphaned)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
