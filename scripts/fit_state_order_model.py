#!/usr/bin/env python3
"""Exploratory Phase 2.9: surface-position baseline vs finite-state update.

All responses are centered within each complete S3 orbit. Outer evaluation is
leave-one-formal-family-out. Hyperparameters are selected only inside the outer
training families. This reuses Phase 2.6 data and is not confirmatory evidence.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

PERMS = ["123", "132", "213", "231", "312", "321"]
GRID = [(r, k, v) for r in (0.5, 0.75, 1.0)
        for k in (0.0, 0.25, 0.5) for v in (0.0, 0.1, 0.25)]
RIDGES = (0.0, 0.01, 0.1, 1.0, 10.0)


def atoms(text):
    return re.findall(r"[A-Za-z]+\d+", text)


def parse_query(text):
    xs = atoms(text)
    if len(xs) != 2:
        raise ValueError(f"unexpected query: {text!r}")
    return xs[0], xs[1]


def parse_rule(text):
    left, right = text.removeprefix("If ").removesuffix(".").split(", then ")
    return tuple(atoms(left)), tuple(atoms(right))


def load_benchmark(path):
    out = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        out.setdefault(row["case_id"], {
            "family": row["family"], "premises": row["premise_multiset"],
            "query": row["query"],
        })
    return out


def load_results(path):
    out = defaultdict(dict)
    fam = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        out[row["case_id"]][row["permutation"]] = float(row["margin"])
        fam[row["case_id"]] = row["family"]
    for cid, vals in out.items():
        if set(vals) != set(PERMS):
            raise ValueError(f"{cid}: incomplete S3 orbit")
    return out, fam


def surface(case, perm):
    source, target = parse_query(case["query"])
    prem = case["premises"]
    lengths = np.array([len(re.findall(r"\w+", x)) for x in prem], float)
    lengths /= lengths.sum()
    value = np.zeros(8)
    for pos, digit in enumerate(perm):
        i = int(digit) - 1
        u = pos / (len(perm) - 1)
        l1, l2 = 2 * u - 1, 6 * u * u - 6 * u + 1
        aa = atoms(prem[i])
        s = np.array([
            aa.count(source), aa.count(target), lengths[i],
            float("both " in prem[i]),
        ])
        value[:4] += s * l1
        value[4:] += s * l2
    return value


def update(z, body, head, rho, kappa, nu):
    t = np.eye(len(z)) + rho * (z - np.eye(len(z)))
    gate = ((1 - kappa) * np.prod(t[:, body], axis=1)
            + kappa * np.mean(t[:, body], axis=1))
    reverse = np.mean(t[:, head], axis=1)
    f, r = np.zeros_like(t), np.zeros_like(t)
    f[:, head] = gate[:, None]
    r[:, body] = reverse[:, None]
    return t + (1 - t) * (1 - (1 - f) * (1 - nu * r))


def state_score(case, perm, params):
    source, target = parse_query(case["query"])
    names = sorted(set(sum((atoms(x) for x in case["premises"]), []))
                   | {source, target})
    ix = {x: i for i, x in enumerate(names)}
    rules = [(tuple(ix[x] for x in b), tuple(ix[x] for x in h))
             for b, h in map(parse_rule, case["premises"])]
    z = np.eye(len(names))
    for digit in perm:
        z = update(z, *rules[int(digit) - 1], *params)
    return float(z[ix[source], ix[target]])


def make_rows(bench, results, fam_of):
    rows = []
    for cid, vals in results.items():
        y = np.array([vals[p] for p in PERMS])
        y -= y.mean()
        s = np.stack([surface(bench[cid], p) for p in PERMS])
        s -= s.mean(axis=0)
        states = {}
        for params in GRID:
            z = np.array([state_score(bench[cid], p, params) for p in PERMS])
            states[params] = z - z.mean()
        for j, p in enumerate(PERMS):
            rows.append({"case_id": cid, "family": fam_of[cid], "perm": p,
                         "y": y[j], "surface": s[j],
                         "states": {k: v[j] for k, v in states.items()}})
    return rows


def fit_predict(train, test, params, ridge, state):
    def x(row):
        base = row["surface"]
        return np.r_[base, row["states"][params]] if state else base
    a = np.stack([x(r) for r in train]); y = np.array([r["y"] for r in train])
    b = np.stack([x(r) for r in test])
    reg = ridge * np.eye(a.shape[1])
    coef = np.linalg.solve(a.T @ a + reg + 1e-12 * np.eye(a.shape[1]), a.T @ y)
    return b @ coef, coef


def sse(rows, pred):
    y = np.array([r["y"] for r in rows])
    return float(np.sum((y - pred) ** 2))


def select(train, state):
    families = sorted({r["family"] for r in train})
    candidates = itertools.product(GRID if state else [GRID[0]], RIDGES)
    scored = []
    for params, ridge in candidates:
        total = 0.0
        for held in families:
            tr = [r for r in train if r["family"] != held]
            va = [r for r in train if r["family"] == held]
            pred, _ = fit_predict(tr, va, params, ridge, state)
            total += sse(va, pred) / len(va)
        scored.append((total / len(families), params, ridge))
    return min(scored, key=lambda x: (x[0], x[1], x[2]))


def metric(rows, pred, baseline=None):
    y = np.array([r["y"] for r in rows]); err = y - pred
    out = {"n": len(rows), "sse": float(err @ err),
           "rmse": float(np.sqrt(np.mean(err ** 2))),
           "mae": float(np.mean(np.abs(err))),
           "zero_sse": float(y @ y)}
    out["skill_vs_zero"] = 1 - out["sse"] / out["zero_sse"]
    if baseline is not None:
        out["skill_vs_surface"] = 1 - out["sse"] / baseline
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--benchmark", required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--out")
    args = ap.parse_args()
    bench = load_benchmark(args.benchmark)
    results, fam_of = load_results(args.results)
    if set(bench) != set(results):
        raise ValueError("benchmark/result case sets differ")
    rows = make_rows(bench, results, fam_of)
    families = sorted(set(fam_of.values()))
    folds, all_y, all_m0, all_m1, all_m2 = {}, [], [], [], []
    for held in families:
        train = [r for r in rows if r["family"] != held]
        test = [r for r in rows if r["family"] == held]
        cv0, params0, ridge0 = select(train, False)
        cv2, params2, ridge2 = select(train, True)
        pred0, _ = fit_predict(train, test, params0, ridge0, False)
        strict = (1.0, 0.0, 0.0)
        strict_scored = []
        train_families = sorted({r["family"] for r in train})
        for ridge1 in RIDGES:
            inner = 0.0
            for inner_held in train_families:
                tr = [r for r in train if r["family"] != inner_held]
                va = [r for r in train if r["family"] == inner_held]
                pv, _ = fit_predict(tr, va, strict, ridge1, True)
                inner += sse(va, pv) / len(va)
            strict_scored.append((inner / len(train_families), ridge1))
        cv1, ridge1 = min(strict_scored)
        pred1, coef1 = fit_predict(train, test, strict, ridge1, True)
        pred2, coef2 = fit_predict(train, test, params2, ridge2, True)
        m0 = metric(test, pred0)
        m1 = metric(test, pred1, m0["sse"])
        m2 = metric(test, pred2, m0["sse"])
        folds[held] = {"surface": m0, "strict_state": m1, "soft_state": m2,
                       "selected": {"rho": params2[0], "kappa": params2[1],
                                    "nu": params2[2], "ridge": ridge2,
                                    "inner_mse": cv2, "surface_ridge": ridge0,
                                    "surface_inner_mse": cv0,
                                    "strict_ridge": ridge1,
                                    "strict_inner_mse": cv1,
                                    "strict_state_readout": float(coef1[-1]),
                                    "state_readout": float(coef2[-1])}}
        all_y.extend(test); all_m0.extend(pred0); all_m1.extend(pred1); all_m2.extend(pred2)
    m0 = metric(all_y, np.array(all_m0))
    m1 = metric(all_y, np.array(all_m1), m0["sse"])
    m2 = metric(all_y, np.array(all_m2), m0["sse"])
    result = {"analysis_status": "exploratory_posthoc_after_phase2_6",
              "target": "within-case S3-orbit-centered margin",
              "outer_split": "leave-one-formal-family-out",
              "inner_selection": "training-families-only LOFO",
              "models": {"M0": "surface-position",
                         "M1": "M0 + strict one-pass finite-state support",
                         "M2": "M0 + soft one-pass finite-state support"},
              "aggregate": {"surface": m0, "strict_state": m1, "soft_state": m2}, "folds": folds,
              "decision": {"advance_to_confirmation": bool(m2["skill_vs_surface"] > 0
                  and sum(f["soft_state"]["skill_vs_surface"] > 0 for f in folds.values()) >= 6),
                  "rule": "state aggregate skill_vs_surface > 0 and at least 6/8 positive folds"},
              "interpretation_boundary": "Reuses observed Phase 2.6 data; cannot confirm a new law."}
    text = json.dumps(result, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
