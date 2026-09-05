#!/usr/bin/env python3
"""Exploratory held-out generalization analysis for Phase 2 S3 effects.

This script does not test an S3 representation. It asks whether the scalar
permutation effect relative to identity ordering 123 generalizes across unseen
cases and unseen formal families better than a zero-effect null.

Two evaluations are reported:

1. leave-one-family-out (LOFO):
   estimate one mean effect per permutation on three families and predict the
   held-out fourth family;

2. within-family alternating split:
   estimate effects from one half of cases and predict the other half, comparing
   a pooled permutation-only model with a family-specific permutation model.

Primary error summaries are MAE and RMSE. A skill score relative to the
zero-effect null is also reported:

    skill = 1 - SSE_model / SSE_null

Positive skill means better than predicting no permutation effect.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

PERMS = ["132", "213", "231", "312", "321"]
BASE = "123"


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def metrics(y_true, y_pred):
    if len(y_true) != len(y_pred) or not y_true:
        raise ValueError("nonempty aligned vectors required")
    errors = [p - y for y, p in zip(y_true, y_pred)]
    sse = sum(e * e for e in errors)
    mae = sum(abs(e) for e in errors) / len(errors)
    rmse = math.sqrt(sse / len(errors))
    null_sse = sum(y * y for y in y_true)
    skill = None if null_sse == 0 else 1.0 - sse / null_sse
    return {
        "n": len(y_true),
        "mae": mae,
        "rmse": rmse,
        "sse": sse,
        "zero_null_sse": null_sse,
        "skill_vs_zero": skill,
    }


def load_effects(path: Path):
    cases = defaultdict(dict)
    family = {}
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            r = json.loads(line)
            cid = r["case_id"]
            p = r["permutation"]
            if p in cases[cid]:
                raise SystemExit(f"{cid}: duplicate permutation {p}")
            cases[cid][p] = float(r["margin"])
            if cid in family and family[cid] != r["family"]:
                raise SystemExit(f"{cid}: inconsistent family")
            family[cid] = r["family"]

    effects = {}
    for cid, vals in cases.items():
        expected = set(PERMS + [BASE])
        if set(vals) != expected:
            raise SystemExit(f"{cid}: incomplete S3 orbit")
        b = vals[BASE]
        effects[cid] = {p: vals[p] - b for p in PERMS}
    return effects, family


def estimate_permutation_means(case_ids, effects):
    return {
        p: mean([effects[cid][p] for cid in case_ids])
        for p in PERMS
    }


def flatten_predictions(case_ids, effects, predictor):
    y = []
    pred = []
    for cid in case_ids:
        for p in PERMS:
            y.append(effects[cid][p])
            pred.append(predictor(cid, p))
    return y, pred


def lofo(effects, family):
    fams = sorted(set(family.values()))
    out = {}
    all_y = []
    all_pred = []
    all_zero = []

    for held in fams:
        train = [cid for cid in effects if family[cid] != held]
        test = [cid for cid in effects if family[cid] == held]
        beta = estimate_permutation_means(train, effects)

        y, pred = flatten_predictions(
            test, effects, lambda _cid, p: beta[p]
        )
        zero = [0.0] * len(y)
        out[held] = {
            "train_cases": len(train),
            "test_cases": len(test),
            "estimated_effects": beta,
            "permutation_model": metrics(y, pred),
            "zero_effect_null": metrics(y, zero),
        }
        all_y.extend(y)
        all_pred.extend(pred)
        all_zero.extend(zero)

    return {
        "folds": out,
        "aggregate": {
            "permutation_model": metrics(all_y, all_pred),
            "zero_effect_null": metrics(all_y, all_zero),
        },
    }


def alternating_split(effects, family):
    train = []
    test = []
    for fam in sorted(set(family.values())):
        ids = sorted(cid for cid in effects if family[cid] == fam)
        for i, cid in enumerate(ids):
            (train if i % 2 == 0 else test).append(cid)

    pooled = estimate_permutation_means(train, effects)
    family_beta = {}
    for fam in sorted(set(family.values())):
        fam_train = [cid for cid in train if family[cid] == fam]
        family_beta[fam] = estimate_permutation_means(fam_train, effects)

    y, pooled_pred = flatten_predictions(
        test, effects, lambda _cid, p: pooled[p]
    )
    _, family_pred = flatten_predictions(
        test, effects, lambda cid, p: family_beta[family[cid]][p]
    )
    zero = [0.0] * len(y)

    return {
        "train_cases": len(train),
        "test_cases": len(test),
        "pooled_estimated_effects": pooled,
        "family_estimated_effects": family_beta,
        "pooled_permutation_model": metrics(y, pooled_pred),
        "family_specific_permutation_model": metrics(y, family_pred),
        "zero_effect_null": metrics(y, zero),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("results")
    args = parser.parse_args()

    effects, family = load_effects(Path(args.results))
    fam_counts = defaultdict(int)
    for cid in effects:
        fam_counts[family[cid]] += 1

    out = {
        "analysis_status": "exploratory_posthoc",
        "cases": len(effects),
        "families": dict(sorted(fam_counts.items())),
        "effect_definition": "margin(permutation) - margin(123)",
        "leave_one_family_out": lofo(effects, family),
        "within_family_alternating_split": alternating_split(effects, family),
        "interpretation_boundary": (
            "Positive out-of-sample skill supports a reproducible scalar "
            "permutation-response law. It does not establish an S3 representation, "
            "equivariance, compositionality, or logical competence."
        ),
    }

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
