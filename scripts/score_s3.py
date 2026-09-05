#!/usr/bin/env python3
"""Score Phase 2 S3 premise-permutation responses."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path


PERMS = ["123", "132", "213", "231", "312", "321"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results")
    args = parser.parse_args()

    cases = defaultdict(dict)
    family = {}
    gold = {}

    with Path(args.results).open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            cid = r["case_id"]
            p = r["permutation"]
            if p in cases[cid]:
                raise SystemExit(f"{cid}: duplicate permutation {p}")
            cases[cid][p] = float(r["margin"])
            family[cid] = r["family"]
            gold[cid] = bool(r["gold"])

    for cid, vals in cases.items():
        if set(vals) != set(PERMS):
            raise SystemExit(f"{cid}: incomplete S3 orbit")

    base = "123"
    effects = {p: [] for p in PERMS}
    effects_by_family = defaultdict(lambda: {p: [] for p in PERMS})
    within_ranges = []
    within_sd = []
    predictions = Counter()

    with Path(args.results).open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                predictions[r["predicted_answer"]] += 1

    for cid, vals in cases.items():
        b = vals[base]
        xs = [vals[p] for p in PERMS]
        within_ranges.append(max(xs) - min(xs))
        within_sd.append(statistics.pstdev(xs))
        for p in PERMS:
            d = vals[p] - b
            effects[p].append(d)
            effects_by_family[family[cid]][p].append(d)

    def mean(xs):
        return sum(xs) / len(xs) if xs else None

    out = {
        "cases": len(cases),
        "prompt_rows": len(cases) * 6,
        "prediction_counts": dict(predictions),
        "within_case": {
            "mean_range": mean(within_ranges),
            "median_range": statistics.median(within_ranges),
            "mean_population_sd": mean(within_sd),
        },
        "permutation_effect_vs_123": {
            p: {
                "mean": mean(effects[p]),
                "median": statistics.median(effects[p]),
            }
            for p in PERMS
        },
        "permutation_effect_by_family": {
            fam: {
                p: {
                    "mean": mean(vals[p]),
                    "median": statistics.median(vals[p]),
                }
                for p in PERMS
            }
            for fam, vals in sorted(effects_by_family.items())
        },
    }

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
