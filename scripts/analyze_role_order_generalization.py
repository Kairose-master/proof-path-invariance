#!/usr/bin/env python3
"""Exploratory Phase 2.8 formal-role generalization test.

Goal:
  Replace family-name-specific pairwise coefficients with a compact model whose
  predictors are derived mechanically from premise roles.

For every case/permutation, build order features from the original three
premises and the query:

- source_order: whether source-bearing premises are earlier than non-source ones
- target_order: whether target-bearing premises are earlier than non-target ones
- conjunction_order: whether conjunction-bearing premises are earlier
- direct_edge_order: whether a direct query-edge premise is earlier
- source_vs_target: pairwise precedence between source-bearing and target-bearing
  premises when those roles occur on distinct premises
- last-role indicators for the serialized final premise

Then perform leave-one-family-out prediction of
    effect = margin(permutation) - margin(123)

using ordinary least squares fit on the other families.

This is exploratory/post-hoc. Any useful feature set or coefficient pattern must
be frozen and tested on a fresh confirmatory benchmark.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import numpy as np


PERMS = ["132", "213", "231", "312", "321"]
BASE = "123"


def parse_query_atoms(query):
    m = re.fullmatch(r"If (\S+) holds, then (\S+) holds\.", query)
    if not m:
        raise SystemExit(f"unexpected query format: {query!r}")
    return m.group(1), m.group(2)


def load_benchmark(path):
    by_case = {}
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            cid = r["case_id"]
            if cid not in by_case:
                by_case[cid] = {
                    "family": r["family"],
                    "premises": list(r["premise_multiset"]),
                    "query": r["query"],
                }
    return by_case


def load_results(path):
    cases = defaultdict(dict)
    family = {}
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            cid = r["case_id"]
            cases[cid][r["permutation"]] = float(r["margin"])
            family[cid] = r["family"]
    expected = set(PERMS + [BASE])
    for cid, vals in cases.items():
        if set(vals) != expected:
            raise SystemExit(f"{cid}: incomplete S3 orbit")
    return cases, family


def premise_roles(case):
    source, target = parse_query_atoms(case["query"])
    out = []
    for text in case["premises"]:
        out.append({
            "source": source in text,
            "target": target in text,
            "conjunction": "both " in text,
            "direct_edge": (source in text and target in text),
        })
    return out


def precedes_score(perm, positive_mask):
    """Sum +1 when positive-role premise precedes negative-role premise, else -1.

    Normalize by number of cross-role comparisons so the feature stays in [-1,1].
    Returns 0 when there is no role contrast.
    """
    pos = {int(orig) - 1: rank for rank, orig in enumerate(perm)}
    yes = [i for i, v in enumerate(positive_mask) if v]
    no = [i for i, v in enumerate(positive_mask) if not v]
    if not yes or not no:
        return 0.0
    vals = []
    for i in yes:
        for j in no:
            vals.append(1.0 if pos[i] < pos[j] else -1.0)
    return sum(vals) / len(vals)


def cross_role_precedence(perm, mask_a, mask_b):
    """Pairwise precedence A vs B, ignoring premises carrying both roles."""
    pos = {int(orig) - 1: rank for rank, orig in enumerate(perm)}
    aa = [i for i, v in enumerate(mask_a) if v and not mask_b[i]]
    bb = [i for i, v in enumerate(mask_b) if v and not mask_a[i]]
    if not aa or not bb:
        return 0.0
    vals = []
    for i in aa:
        for j in bb:
            vals.append(1.0 if pos[i] < pos[j] else -1.0)
    return sum(vals) / len(vals)


FEATURE_NAMES = [
    "source_order",
    "target_order",
    "conjunction_order",
    "direct_edge_order",
    "source_vs_target",
    "last_source",
    "last_target",
    "last_conjunction",
    "last_direct_edge",
]


def features(case, perm):
    roles = premise_roles(case)
    masks = {
        key: [bool(r[key]) for r in roles]
        for key in ["source", "target", "conjunction", "direct_edge"]
    }
    last = roles[int(perm[-1]) - 1]
    return np.array([
        precedes_score(perm, masks["source"]),
        precedes_score(perm, masks["target"]),
        precedes_score(perm, masks["conjunction"]),
        precedes_score(perm, masks["direct_edge"]),
        cross_role_precedence(perm, masks["source"], masks["target"]),
        float(last["source"]),
        float(last["target"]),
        float(last["conjunction"]),
        float(last["direct_edge"]),
    ], dtype=float)


def metric(y, pred):
    err = pred - y
    sse = float(np.sum(err ** 2))
    zero = float(np.sum(y ** 2))
    return {
        "n": int(len(y)),
        "mae": float(np.mean(np.abs(err))),
        "rmse": float(math.sqrt(np.mean(err ** 2))),
        "sse": sse,
        "zero_null_sse": zero,
        "skill_vs_zero": None if zero == 0 else float(1.0 - sse / zero),
    }


def design_rows(bench, cases, fam_of):
    rows = []
    for cid, vals in cases.items():
        base = vals[BASE]
        fam = fam_of[cid]
        case = bench[cid]
        for p in PERMS:
            rows.append({
                "case_id": cid,
                "family": fam,
                "permutation": p,
                "x": features(case, p),
                "y": vals[p] - base,
            })
    return rows


def fit_ols(rows):
    X = np.stack([np.concatenate(([1.0], r["x"])) for r in rows])
    y = np.array([r["y"] for r in rows], dtype=float)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


def predict(beta, rows):
    X = np.stack([np.concatenate(([1.0], r["x"])) for r in rows])
    return X @ beta


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", required=True)
    parser.add_argument("--results", required=True)
    args = parser.parse_args()

    bench = load_benchmark(args.benchmark)
    cases, fam_of = load_results(args.results)

    if set(bench) != set(cases):
        raise SystemExit("benchmark/results case sets differ")

    rows = design_rows(bench, cases, fam_of)
    families = sorted(set(r["family"] for r in rows))

    folds = {}
    all_y = []
    all_pred = []

    for held in families:
        train = [r for r in rows if r["family"] != held]
        test = [r for r in rows if r["family"] == held]
        beta = fit_ols(train)
        y = np.array([r["y"] for r in test], dtype=float)
        pred = predict(beta, test)

        folds[held] = {
            "train_rows": len(train),
            "test_rows": len(test),
            "coefficients": {
                "intercept": float(beta[0]),
                **{
                    name: float(beta[i + 1])
                    for i, name in enumerate(FEATURE_NAMES)
                },
            },
            "metrics": metric(y, pred),
        }
        all_y.extend(y.tolist())
        all_pred.extend(pred.tolist())

    all_y = np.array(all_y, dtype=float)
    all_pred = np.array(all_pred, dtype=float)

    beta_all = fit_ols(rows)
    result = {
        "analysis_status": "exploratory_posthoc_after_failed_confirmatory",
        "model": "formal-role order features -> scalar permutation effect",
        "feature_names": FEATURE_NAMES,
        "families": families,
        "leave_one_family_out": {
            "folds": folds,
            "aggregate": metric(all_y, all_pred),
        },
        "full_data_descriptive_fit": {
            "coefficients": {
                "intercept": float(beta_all[0]),
                **{
                    name: float(beta_all[i + 1])
                    for i, name in enumerate(FEATURE_NAMES)
                },
            },
            "metrics": metric(
                np.array([r["y"] for r in rows], dtype=float),
                predict(beta_all, rows),
            ),
        },
        "interpretation_boundary": (
            "Positive LOFO skill would show that this fixed exploratory feature "
            "class predicts unseen families within the already-observed Phase 2.6 "
            "dataset. It remains post-hoc and cannot validate a new law. Any next "
            "confirmatory claim requires freezing the feature set/model and using "
            "fresh unseen families."
        ),
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
