#!/usr/bin/env python3
"""Analyze a Phase 3 Hankel table run according to the frozen v0 plan.

Sections follow `docs/PHASE3_HANKEL_DESIGN.md`:

  A. invariance defect on logically identical rows;
  B. separation between logically distinct classes;
  C. numerical rank of the table and its nested sub-tables;
  D. gold-conditioned readout (AUROC of pos - neg);
  E. closure defect at the direct-query level, with refinement witness.

All quantities are computed on the raw observation pairs in R^2 with the
Euclidean metric.  Nothing here is a test of a structural hypothesis; the
output is descriptive at the level of the finite table.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np


CLASS_ORDER = ["chain", "fork_join", "chain_gap", "branch", "reversed", "fragments", "gated", "skip"]
SERIALIZATIONS = ["123", "231", "312", "321"]
CONTINUATIONS = ["none", "d_e", "c_e", "b_d", "e_a", "a_d", "e_d", "b_c"]
QUERIES = ["ad", "ae", "bd", "ce"]
ROW_IDS = [f"{c}-{s}" for c in CLASS_ORDER for s in SERIALIZATIONS]
COL_IDS = [f"{z}-{q}" for z in CONTINUATIONS for q in QUERIES]
ROW_INDEX = {r: i for i, r in enumerate(ROW_IDS)}
COL_INDEX = {c: i for i, c in enumerate(COL_IDS)}


def load(path: Path):
    tables = {}
    gold = np.zeros((len(ROW_IDS), len(COL_IDS)), dtype=bool)
    n = 0
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            n += 1
            key = (r["relabeling"], r["renderer"], r["answer_map"])
            H = tables.setdefault(key, np.full((len(ROW_IDS), len(COL_IDS), 2), np.nan))
            i, j = ROW_INDEX[r["row_id"]], COL_INDEX[r["col_id"]]
            H[i, j] = r["observation"]
            gold[i, j] = r["gold"]
    for key, H in tables.items():
        if np.isnan(H).any():
            raise SystemExit(f"incomplete table for {key}")
    return tables, gold, n


def pair_dist(H, i, j):
    """max over columns of the Euclidean distance between rows i and j."""
    return float(np.max(np.linalg.norm(H[i] - H[j], axis=1)))


def section_a(H):
    per_class = {}
    all_pair_means = []
    for c in CLASS_ORDER:
        rows = [ROW_INDEX[f"{c}-{s}"] for s in SERIALIZATIONS]
        maxes, means = [], []
        for i, j in combinations(rows, 2):
            d = np.linalg.norm(H[i] - H[j], axis=1)
            maxes.append(float(d.max()))
            means.append(float(d.mean()))
        per_class[c] = {"max": max(maxes), "mean": float(np.mean(means))}
        all_pair_means.extend(means)
    return {
        "delta_inv": max(v["max"] for v in per_class.values()),
        "mean_over_pairs_and_columns": float(np.mean(all_pair_means)),
        "per_class": per_class,
    }


def section_b(H, delta_inv):
    sep = {}
    for c1, c2 in combinations(CLASS_ORDER, 2):
        r1 = [ROW_INDEX[f"{c1}-{s}"] for s in SERIALIZATIONS]
        r2 = [ROW_INDEX[f"{c2}-{s}"] for s in SERIALIZATIONS]
        sep[f"{c1}|{c2}"] = min(pair_dist(H, i, j) for i in r1 for j in r2)
    vals = np.array(list(sep.values()))
    return {
        "min": float(vals.min()),
        "median": float(np.median(vals)),
        "max": float(vals.max()),
        "class_pairs_separated_at_delta_inv": int((vals > delta_inv).sum()),
        "class_pairs_total": len(sep),
        "per_class_pair": sep,
    }


def numerical_rank(M):
    s = np.linalg.svd(M, compute_uv=False)
    s1 = s[0]
    return {
        "sigma_1": float(s1),
        "rank_1e-3": int((s > 1e-3 * s1).sum()),
        "rank_1e-2": int((s > 1e-2 * s1).sum()),
        "singular_values": [float(x) for x in s[:12]],
    }


def section_c(H):
    flat = H.reshape(H.shape[0], -1)
    out = {"rows_32": numerical_rank(flat)}
    for k, n_classes in (("rows_16", 4), ("rows_24", 6)):
        out[k] = numerical_rank(flat[: n_classes * len(SERIALIZATIONS)])
    centered = flat - flat.mean(axis=0, keepdims=True)
    out["rows_32_column_centered_exploratory"] = numerical_rank(centered)
    return out


def auroc(scores, labels):
    scores = np.asarray(scores, dtype=float)
    labels = np.asarray(labels, dtype=bool)
    pos, neg = scores[labels], scores[~labels]
    if len(pos) == 0 or len(neg) == 0:
        return None
    order = np.argsort(scores)
    ranks = np.empty(len(scores))
    sorted_scores = scores[order]
    i = 0
    while i < len(scores):
        j = i
        while j + 1 < len(scores) and sorted_scores[j + 1] == sorted_scores[i]:
            j += 1
        ranks[order[i : j + 1]] = (i + j) / 2 + 1
        i = j + 1
    u = ranks[labels].sum() - len(pos) * (len(pos) + 1) / 2
    return float(u / (len(pos) * len(neg)))


def section_d(H, gold):
    margin = H[:, :, 0] - H[:, :, 1]
    pred_pos = int((margin > 0).sum())
    return {
        "auroc_margin_vs_gold": auroc(margin.ravel(), gold.ravel()),
        "predicted_positive": pred_pos,
        "predicted_negative": int((margin < 0).sum()),
        "cells": int(margin.size),
        "accuracy_sign": float(((margin > 0) == gold).mean()),
        "mean_margin": float(margin.mean()),
    }


def section_e(H, eps):
    direct = [COL_INDEX[f"none-{q}"] for q in QUERIES]
    ext = {a: [COL_INDEX[f"{a}-{q}"] for q in QUERIES] for a in CONTINUATIONS if a != "none"}
    d0 = {}
    for i, j in combinations(range(len(ROW_IDS)), 2):
        d0[(i, j)] = float(np.max(np.linalg.norm(H[i, direct] - H[j, direct], axis=1)))
    agreeing = [p for p, d in d0.items() if d <= eps]
    best = None
    for i, j in agreeing:
        for a, cols in ext.items():
            dist = np.linalg.norm(H[i, cols] - H[j, cols], axis=1)
            k = int(dist.argmax())
            if best is None or dist[k] > best["closure_defect"]:
                best = {
                    "closure_defect": float(dist[k]),
                    "witness_rows": [ROW_IDS[i], ROW_IDS[j]],
                    "witness_column": f"{a}-{QUERIES[k]}",
                    "d0_of_witness_pair": d0[(i, j)],
                }
    within = sum(1 for i, j in agreeing if ROW_IDS[i].split("-")[0] == ROW_IDS[j].split("-")[0])
    return {
        "epsilon": eps,
        "row_pairs_agreeing_on_direct_queries": len(agreeing),
        "of_which_same_logical_class": within,
        "row_pairs_total": len(d0),
        "d0_quantiles": {
            "p10": float(np.quantile(list(d0.values()), 0.1)),
            "p50": float(np.quantile(list(d0.values()), 0.5)),
            "p90": float(np.quantile(list(d0.values()), 0.9)),
        },
        "worst": best,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    raw = Path(args.raw)
    tables, gold, n = load(raw)
    sha = hashlib.sha256(raw.read_bytes()).hexdigest()

    per_control = {}
    for key in sorted(tables):
        H = tables[key]
        a = section_a(H)
        per_control["/".join(key)] = {
            "A_invariance": a,
            "B_separation": section_b(H, a["delta_inv"]),
            "C_rank": section_c(H),
            "D_readout": section_d(H, gold),
            "E_closure": section_e(H, a["delta_inv"]),
        }

    pooled = np.concatenate([tables[k].reshape(len(ROW_IDS), -1) for k in sorted(tables)], axis=1)
    pooled_rank = numerical_rank(pooled)
    pooled_centered = numerical_rank(pooled - pooled.mean(axis=0, keepdims=True))

    def agg(path):
        vals = []
        for v in per_control.values():
            x = v
            for p in path:
                x = x[p]
            vals.append(x)
        return {"min": float(min(vals)), "median": float(np.median(vals)), "max": float(max(vals))}

    summary = {
        "benchmark": "hankel_v0",
        "analysis_status": "descriptive_frozen_plan_v0",
        "raw_result_sha256": sha,
        "prompt_rows": n,
        "control_combinations": len(tables),
        "aggregate": {
            "delta_inv": agg(["A_invariance", "delta_inv"]),
            "separation_min": agg(["B_separation", "min"]),
            "separation_median": agg(["B_separation", "median"]),
            "class_pairs_separated_at_delta_inv": agg(["B_separation", "class_pairs_separated_at_delta_inv"]),
            "rank_1e-2_rows_32": agg(["C_rank", "rows_32", "rank_1e-2"]),
            "rank_1e-3_rows_32": agg(["C_rank", "rows_32", "rank_1e-3"]),
            "auroc": agg(["D_readout", "auroc_margin_vs_gold"]),
            "closure_defect": agg(["E_closure", "worst", "closure_defect"]),
        },
        "pooled_rank_raw": pooled_rank,
        "pooled_rank_column_centered_exploratory": pooled_centered,
        "per_control": per_control,
        "interpretation_limit": (
            "Descriptive statistics on a finite 32x32 table under 16 presentation controls. "
            "Rows agreeing on all columns are 'not separated by T', not identical under the "
            "recognition congruence. No structural claim about the model is made."
        ),
    }
    Path(args.out).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({k: v for k, v in summary.items() if k in ("raw_result_sha256", "prompt_rows", "aggregate", "pooled_rank_raw")}, indent=2))


if __name__ == "__main__":
    main()
