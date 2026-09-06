#!/usr/bin/env python3
"""Verify the frozen `hankel_v3` hash."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("benchmark"); p.add_argument("--lock", default="experiments/hankel_v3.lock.json")
    a = p.parse_args()
    lock = json.loads(Path(a.lock).read_text(encoding="utf-8")); data = Path(a.benchmark).read_bytes()
    got = hashlib.sha256(data).hexdigest()
    if got != lock["sha256"]:
        raise SystemExit(f"hankel_v3 hash mismatch: expected {lock['sha256']}, got {got}")
    rows = sum(1 for l in data.splitlines() if l.strip())
    if rows != lock["prompts"]:
        raise SystemExit(f"expected {lock['prompts']} rows, found {rows}")
    print("hankel_v3 benchmark lock verified")

if __name__ == "__main__":
    main()
