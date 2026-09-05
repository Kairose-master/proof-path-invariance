#!/usr/bin/env python3
"""Score paired next-token logit margins.

Primary outcome: sign flip rate between base and premise-reversed renderings.
Secondary summaries: accuracy and continuous margin displacement.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results")
    args = parser.parse_args()

    pairs = defaultdict(dict)
    golds = {}

    with Path(args.results).open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            pid = row["pair_id"]
            variant = row["variant"]
            if variant in pairs[pid]:
                raise SystemExit(f"{pid}: duplicate variant {variant}")
            pairs[pid][variant] = {
                "prediction": row["predicted_answer"],
                "margin": float(row["margin"]),
            }
            gold = row["gold"]
            if pid in golds and golds[pid] != gold:
                raise SystemExit(f"{pid}: inconsistent gold label")
            golds[pid] = gold

    valid_pairs = 0
    tie_pairs = 0
    flips = 0
    yes_to_no = 0
    no_to_yes = 0
    base_correct = 0
    reverse_correct = 0
    margin_shifts = []

    for pid, variants in sorted(pairs.items()):
        if set(variants) != {"base", "premise_reverse"}:
            raise SystemExit(f"{pid}: incomplete pair")

        base = variants["base"]
        rev = variants["premise_reverse"]
        margin_shifts.append(rev["margin"] - base["margin"])

        a, b = base["prediction"], rev["prediction"]
        if "TIE" in {a, b}:
            tie_pairs += 1
            continue

        valid_pairs += 1
        flips += int(a != b)
        yes_to_no += int(a == "YES" and b == "NO")
        no_to_yes += int(a == "NO" and b == "YES")

        expected = "YES" if golds[pid] else "NO"
        base_correct += int(a == expected)
        reverse_correct += int(b == expected)

    def ratio(x: int, n: int):
        return (x / n) if n else None

    mean_shift = sum(margin_shifts) / len(margin_shifts) if margin_shifts else None
    mean_abs_shift = (
        sum(abs(x) for x in margin_shifts) / len(margin_shifts)
        if margin_shifts
        else None
    )

    print(json.dumps({
        "pairs_total": len(pairs),
        "valid_binary_pairs": valid_pairs,
        "tie_pairs": tie_pairs,
        "flips": flips,
        "flip_rate": ratio(flips, valid_pairs),
        "directional_flips": {
            "YES_to_NO": yes_to_no,
            "NO_to_YES": no_to_yes
        },
        "accuracy": {
            "base": ratio(base_correct, valid_pairs),
            "premise_reverse": ratio(reverse_correct, valid_pairs)
        },
        "margin_shift": {
            "mean_reverse_minus_base": mean_shift,
            "mean_absolute_shift": mean_abs_shift
        }
    }, indent=2))


if __name__ == "__main__":
    main()
