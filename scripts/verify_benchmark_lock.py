#!/usr/bin/env python3
"""Verify frozen benchmark hashes.

Usage:
  python3 scripts/verify_benchmark_lock.py CASES_JSONL PAIRED_JSONL
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cases")
    parser.add_argument("paired")
    parser.add_argument("--lock", default="experiments/benchmark_v0.lock.json")
    args = parser.parse_args()

    lock = json.loads(Path(args.lock).read_text(encoding="utf-8"))
    expected = lock["sha256"]

    actual_cases = sha256(Path(args.cases))
    actual_paired = sha256(Path(args.paired))

    if actual_cases != expected["symbolic_cases_jsonl"]:
        raise SystemExit(
            f"case hash mismatch: expected {expected['symbolic_cases_jsonl']}, got {actual_cases}"
        )
    if actual_paired != expected["paired_prompts_jsonl"]:
        raise SystemExit(
            f"paired hash mismatch: expected {expected['paired_prompts_jsonl']}, got {actual_paired}"
        )

    print("benchmark lock verified")


if __name__ == "__main__":
    main()
