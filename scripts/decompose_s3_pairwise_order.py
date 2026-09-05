#!/usr/bin/env python3
"""Exploratory pairwise-order decomposition of S3 response surfaces.

For each formal family, average the margin effect over neutral-symbol cases and
fit the six S3 values with a pairwise precedence model:

    effect(pi) ~= a + t12*z12(pi) + t13*z13(pi) + t23*z23(pi)

where zij(pi) is +1 when original premise i precedes j and -1 otherwise.

This is a descriptive decomposition, not a group representation. The fitted
coefficients are family-specific and cannot be used as confirmatory evidence.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


PERMS = ["123", "132", "213", "231", "312", "321"]


def pair_features(perm):
    pos = {int(x): i for i, x in enumerate(perm)}
    return [
        1.0,
        1.0 if pos[1] < pos[2] else -1.0,
        1.0 if pos[1] < pos[3] else -1.0,
        1.0 if pos[2] < pos[3] else -1.0,
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("results")
    args = parser.parse_args()

    cases = defaultdict(dict)
    family = {}

    with Path(args.results).open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            cid = r["case_id"]
            p = r["permutation"]
            cases[cid][p] = float(r["margin"])
            family[cid] = r["family"]

    expected = set(PERMS)
    for cid, vals in cases.items():
        if set(vals) != expected:
            raise SystemExit(f"{cid}: incomplete S3 orbit")

    family_effects = defaultdict(lambda: defaultdict(list))
    for cid, vals in cases.items():
        base = vals["123"]
        for p in PERMS:
            family_effects[family[cid]][p].append(vals[p] - base)

    X = np.array([pair_features(p) for p in PERMS], dtype=float)

    output = {}
    r2s = []

    for fam, per_perm in sorted(family_effects.items()):
        y = np.array(
            [sum(per_perm[p]) / len(per_perm[p]) for p in PERMS],
            dtype=float,
        )
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        pred = X @ beta
        residual = y - pred
        sse = float(np.sum(residual ** 2))
        centered = y - float(np.mean(y))
        sst = float(np.sum(centered ** 2))
        r2 = None if sst == 0 else 1.0 - sse / sst
        if r2 is not None:
            r2s.append(r2)

        output[fam] = {
            "observed_effects": {
                p: float(y[i]) for i, p in enumerate(PERMS)
            },
            "pairwise_precedence_fit": {
                "intercept": float(beta[0]),
                "theta_12": float(beta[1]),
                "theta_13": float(beta[2]),
                "theta_23": float(beta[3]),
            },
            "predicted_effects": {
                p: float(pred[i]) for i, p in enumerate(PERMS)
            },
            "residuals": {
                p: float(residual[i]) for i, p in enumerate(PERMS)
            },
            "sse": sse,
            "r2": r2,
        }

    result = {
        "analysis_status": "exploratory_posthoc",
        "model": (
            "effect(pi) ~= intercept + theta_12*z12(pi) + "
            "theta_13*z13(pi) + theta_23*z23(pi)"
        ),
        "families": output,
        "r2_summary": {
            "n": len(r2s),
            "mean": float(sum(r2s) / len(r2s)) if r2s else None,
            "min": float(min(r2s)) if r2s else None,
            "max": float(max(r2s)) if r2s else None,
        },
        "interpretation_boundary": (
            "High within-family R2 means pairwise premise precedence compresses "
            "that family's six-point S3 response surface. It does not show that "
            "the coefficients generalize across families or form an S3 "
            "representation."
        ),
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
