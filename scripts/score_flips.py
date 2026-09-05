#!/usr/bin/env python3
"""Score paired next-token logit margins.

Primary outcome: sign flip rate between base and premise-reversed renderings.
Secondary summaries: accuracy, prediction counts, label-conditioned margins,
AUROC, and continuous margin displacement.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path


def auc(labels: list[bool], scores: list[float]) -> float | None:
    pos = [(s, i) for i, (y, s) in enumerate(zip(labels, scores)) if y]
    neg = [(s, i) for i, (y, s) in enumerate(zip(labels, scores)) if not y]
    if not pos or not neg:
        return None

    wins = 0.0
    total = len(pos) * len(neg)
    for ps, _ in pos:
        for ns, _ in neg:
            if ps > ns:
                wins += 1.0
            elif ps == ns:
                wins += 0.5
    return wins / total


def summarize(xs: list[float]) -> dict:
    if not xs:
        return {
            "n": 0,
            "mean": None,
            "median": None,
            "min": None,
            "max": None,
        }
    return {
        "n": len(xs),
        "mean": sum(xs) / len(xs),
        "median": statistics.median(xs),
        "min": min(xs),
        "max": max(xs),
    }


def quantiles(xs: list[float]) -> dict:
    if not xs:
        return {"q05": None, "q25": None, "q50": None, "q75": None, "q95": None}
    ys = sorted(xs)

    def q(p: float) -> float:
        if len(ys) == 1:
            return ys[0]
        pos = p * (len(ys) - 1)
        lo = math.floor(pos)
        hi = math.ceil(pos)
        if lo == hi:
            return ys[lo]
        frac = pos - lo
        return ys[lo] * (1 - frac) + ys[hi] * frac

    return {
        "q05": q(0.05),
        "q25": q(0.25),
        "q50": q(0.50),
        "q75": q(0.75),
        "q95": q(0.95),
    }


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
    prediction_counts = {
        "base": Counter(),
        "premise_reverse": Counter(),
    }

    base_labels = []
    reverse_labels = []
    base_scores = []
    reverse_scores = []
    base_by_gold = {True: [], False: []}
    reverse_by_gold = {True: [], False: []}
    shift_by_gold = {True: [], False: []}

    for pid, variants in sorted(pairs.items()):
        if set(variants) != {"base", "premise_reverse"}:
            raise SystemExit(f"{pid}: incomplete pair")

        base = variants["base"]
        rev = variants["premise_reverse"]
        shift = rev["margin"] - base["margin"]
        margin_shifts.append(shift)

        gold = golds[pid]
        base_labels.append(gold)
        reverse_labels.append(gold)
        base_scores.append(base["margin"])
        reverse_scores.append(rev["margin"])
        base_by_gold[gold].append(base["margin"])
        reverse_by_gold[gold].append(rev["margin"])
        shift_by_gold[gold].append(shift)

        a, b = base["prediction"], rev["prediction"]
        prediction_counts["base"][a] += 1
        prediction_counts["premise_reverse"][b] += 1

        if "TIE" in {a, b}:
            tie_pairs += 1
            continue

        valid_pairs += 1
        flips += int(a != b)
        yes_to_no += int(a == "YES" and b == "NO")
        no_to_yes += int(a == "NO" and b == "YES")

        expected = "YES" if gold else "NO"
        base_correct += int(a == expected)
        reverse_correct += int(b == expected)

    def ratio(x: int, n: int):
        return (x / n) if n else None

    out = {
        "pairs_total": len(pairs),
        "valid_binary_pairs": valid_pairs,
        "tie_pairs": tie_pairs,
        "flips": flips,
        "flip_rate": ratio(flips, valid_pairs),
        "directional_flips": {
            "YES_to_NO": yes_to_no,
            "NO_to_YES": no_to_yes
        },
        "prediction_counts": {
            "base": dict(prediction_counts["base"]),
            "premise_reverse": dict(prediction_counts["premise_reverse"]),
        },
        "accuracy": {
            "base": ratio(base_correct, valid_pairs),
            "premise_reverse": ratio(reverse_correct, valid_pairs)
        },
        "auroc": {
            "base_margin": auc(base_labels, base_scores),
            "premise_reverse_margin": auc(reverse_labels, reverse_scores),
        },
        "margin_by_gold": {
            "base": {
                "positive": summarize(base_by_gold[True]),
                "negative": summarize(base_by_gold[False]),
            },
            "premise_reverse": {
                "positive": summarize(reverse_by_gold[True]),
                "negative": summarize(reverse_by_gold[False]),
            },
        },
        "margin_shift": {
            "mean_reverse_minus_base": (
                sum(margin_shifts) / len(margin_shifts) if margin_shifts else None
            ),
            "mean_absolute_shift": (
                sum(abs(x) for x in margin_shifts) / len(margin_shifts)
                if margin_shifts else None
            ),
            "quantiles": quantiles(margin_shifts),
            "by_gold": {
                "positive": summarize(shift_by_gold[True]),
                "negative": summarize(shift_by_gold[False]),
            },
        },
    }

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
