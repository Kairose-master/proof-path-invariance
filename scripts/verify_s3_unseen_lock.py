#!/usr/bin/env python3
"""Verify the frozen unseen-family confirmatory benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("benchmark")
    parser.add_argument("--lock", default="experiments/s3_unseen_v0.lock.json")
    args = parser.parse_args()

    lock = json.loads(Path(args.lock).read_text(encoding="utf-8"))
    data = Path(args.benchmark).read_bytes()
    got = hashlib.sha256(data).hexdigest()
    expected = lock["sha256"]

    if got != expected:
        raise SystemExit(
            f"unseen-family benchmark hash mismatch: expected {expected}, got {got}"
        )

    rows = sum(1 for line in data.splitlines() if line.strip())
    if rows != lock["prompts"]:
        raise SystemExit(f"expected {lock['prompts']} rows, found {rows}")

    print("unseen-family benchmark lock verified")


if __name__ == "__main__":
    main()
