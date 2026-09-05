#!/usr/bin/env python3
"""Confirmatory scorer for unseen-family S3 replication.

The permutation effects below were frozen from the full Phase 2 s3_v0 result
before any unseen-family model run. They are NOT refit on confirmatory data.

Primary endpoint:
    skill_vs_zero = 1 - SSE_frozen / SSE_zero

Success criterion:
    aggregate skill_vs_zero > 0

This establishes only predictive scalar permutation-response structure.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


BASE = "123"
PERMS = ["132", "213", "231", "312", "321"]

FROZEN_BETA = {
    "132": -0.032772064208984375,
    "213": -0.032546043395996094,
    "231": -0.016511917114257812,
    "312": -0.027113914489746094,
    "321": 0.05498981475830078,
}


def metrics(y_true, y_pred):
    errors = [p - y for y, p in zip(y_true, y_pred)]
    sse = sum(e * e for e in errors)
    mae = sum(abs(e) for e in errors) / len(errors)
    rmse = math.sqrt(sse / len(errors))
    zero_sse = sum(y * y for y in y_true)
    skill = None if zero_sse == 0 else 1.0 - sse / zero_sse
    return {
        "n": len(y_true),
        "mae": mae,
        "rmse": rmse,
        "sse": sse,
        "zero_null_sse": zero_sse,
        "skill_vs_zero": skill,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results")
    args = parser.parse_args()

    cases = defaultdict(dict)
    family = {}
    predictions = Counter()

    with Path(args.results).open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            cid = row["case_id"]
            p = row["permutation"]
            if p in cases[cid]:
                raise SystemExit(f"{cid}: duplicate permutation {p}")
            cases[cid][p] = float(row["margin"])
            family[cid] = row["family"]
            predictions[row["predicted_answer"]] += 1

    if len(cases) != 128:
        raise SystemExit(f"expected 128 cases, found {len(cases)}")

    expected = set(PERMS + [BASE])
    for cid, vals in cases.items():
        if set(vals) != expected:
            raise SystemExit(f"{cid}: incomplete S3 orbit")

    all_y = []
    all_pred = []
    by_family_y = defaultdict(list)
    by_family_pred = defaultdict(list)
    observed_by_perm = defaultdict(list)

    for cid, vals in cases.items():
        b = vals[BASE]
        fam = family[cid]
        for p in PERMS:
            d = vals[p] - b
            pred = FROZEN_BETA[p]
            all_y.append(d)
            all_pred.append(pred)
            by_family_y[fam].append(d)
            by_family_pred[fam].append(pred)
            observed_by_perm[p].append(d)

    aggregate = metrics(all_y, all_pred)
    result = {
        "analysis_status": "confirmatory_pre_frozen",
        "cases": len(cases),
        "prompt_rows": len(cases) * 6,
        "prediction_counts": dict(predictions),
        "effect_definition": "margin(permutation) - margin(123)",
        "frozen_beta_from_phase2": FROZEN_BETA,
        "primary_endpoint": {
            "name": "aggregate_skill_vs_zero",
            "success_rule": "skill_vs_zero > 0",
            "result": aggregate,
            "success": bool(
                aggregate["skill_vs_zero"] is not None
                and aggregate["skill_vs_zero"] > 0
            ),
        },
        "by_family": {
            fam: metrics(by_family_y[fam], by_family_pred[fam])
            for fam in sorted(by_family_y)
        },
        "observed_mean_effect_by_permutation": {
            p: sum(observed_by_perm[p]) / len(observed_by_perm[p])
            for p in PERMS
        },
        "interpretation_boundary": (
            "Success supports out-of-sample prediction by a frozen scalar "
            "permutation-response law. It does not establish logical competence, "
            "an S3 representation, equivariance, compositionality, or functoriality."
        ),
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
