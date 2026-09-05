#!/usr/bin/env python3
"""Verify the frozen `hankel_v1` hash."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("benchmark")
    parser.add_argument("--lock", default="experiments/hankel_v1.lock.json")
    args = parser.parse_args()
    lock = json.loads(Path(args.lock).read_text(encoding="utf-8"))
    data = Path(args.benchmark).read_bytes()
    got = hashlib.sha256(data).hexdigest()
    if got != lock["sha256"]:
        raise SystemExit(f"hankel_v1 hash mismatch: expected {lock['sha256']}, got {got}")
    rows = sum(1 for line in data.splitlines() if line.strip())
    if rows != lock["prompts"]:
        raise SystemExit(f"expected {lock['prompts']} rows, found {rows}")
    print("hankel_v1 benchmark lock verified")


if __name__ == "__main__":
    main()
