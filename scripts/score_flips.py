#!/usr/bin/env python3
"""Score observable answer flips from validated raw result JSONL.

Rows are paired by (pair_id, sample_index). The scorer consumes
`normalized_answer`; raw-text normalization must already have been validated by
`validate_run_artifacts.py`.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


VALID = {"YES", "NO", "INVALID"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results")
    args = parser.parse_args()

    pairs: dict[tuple[str, int], dict[str, str]] = defaultdict(dict)
    golds: dict[tuple[str, int], bool] = {}

    with Path(args.results).open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            pid = row["pair_id"]
            sample = row.get("sample_index", 0)
            variant = row["variant"]
            answer = row["normalized_answer"]
            if answer not in VALID:
                raise SystemExit(f"line {line_no}: invalid normalized_answer")

            key = (pid, sample)
            if variant in pairs[key]:
                raise SystemExit(f"{key}: duplicate variant {variant}")
            pairs[key][variant] = answer

            gold = row["gold"]
            if key in golds and golds[key] != gold:
                raise SystemExit(f"{key}: inconsistent gold label")
            golds[key] = gold

    valid_pairs = 0
    flips = 0
    invalid_pairs = 0
    base_correct = 0
    reverse_correct = 0
    yes_to_no = 0
    no_to_yes = 0

    for key, variants in sorted(pairs.items()):
        if set(variants) != {"base", "premise_reverse"}:
            raise SystemExit(f"{key}: incomplete pair")

        a = variants["base"]
        b = variants["premise_reverse"]
        if "INVALID" in {a, b}:
            invalid_pairs += 1
            continue

        valid_pairs += 1
        flips += int(a != b)
        yes_to_no += int(a == "YES" and b == "NO")
        no_to_yes += int(a == "NO" and b == "YES")

        expected = "YES" if golds[key] else "NO"
        base_correct += int(a == expected)
        reverse_correct += int(b == expected)

    def ratio(x: int, n: int):
        return (x / n) if n else None

    print(json.dumps({
        "valid_pairs": valid_pairs,
        "flips": flips,
        "flip_rate": ratio(flips, valid_pairs),
        "invalid_pairs": invalid_pairs,
        "directional_flips": {
            "YES_to_NO": yes_to_no,
            "NO_to_YES": no_to_yes
        },
        "accuracy": {
            "base": ratio(base_correct, valid_pairs),
            "premise_reverse": ratio(reverse_correct, valid_pairs)
        }
    }, indent=2))


if __name__ == "__main__":
    main()
