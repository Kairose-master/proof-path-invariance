#!/usr/bin/env python3
"""Score observable answer flips in paired benchmark outputs.

Input JSONL rows require: pair_id, variant, answer.
Answers are normalized only if they are exactly YES or NO after stripping/casefold.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def norm(x: object) -> str:
    if not isinstance(x, str):
        return "INVALID"
    y = x.strip().upper()
    return y if y in {"YES", "NO"} else "INVALID"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results")
    args = parser.parse_args()

    pairs = defaultdict(dict)
    with Path(args.results).open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            pid = row["pair_id"]
            variant = row["variant"]
            if variant in pairs[pid]:
                raise SystemExit(f"{pid}: duplicate variant {variant}")
            pairs[pid][variant] = norm(row.get("answer"))

    n = 0
    flips = 0
    invalid = 0
    for pid, variants in sorted(pairs.items()):
        if set(variants) != {"base", "premise_reverse"}:
            raise SystemExit(f"{pid}: expected base and premise_reverse, got {sorted(variants)}")
        a, b = variants["base"], variants["premise_reverse"]
        if "INVALID" in {a, b}:
            invalid += 1
            continue
        n += 1
        flips += int(a != b)

    rate = (flips / n) if n else float("nan")
    print(json.dumps({
        "valid_pairs": n,
        "flips": flips,
        "flip_rate": rate,
        "invalid_pairs": invalid,
    }, indent=2))


if __name__ == "__main__":
    main()
