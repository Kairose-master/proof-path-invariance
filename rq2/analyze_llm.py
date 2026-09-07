#!/usr/bin/env python3
"""Preregistered analysis for RQ2d (docs/PREREGISTRATION_RQ2D.md).

  python3 rq2/analyze_llm.py --results experiments/rq2/results_d/flash_lite.jsonl --low none --high 1024
Runs only on complete parts (all 200 cases present for the rows needed).
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict

import numpy as np

CONDS = ["F", "F1", "C", "L"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True); ap.add_argument("--low", default="none"); ap.add_argument("--high", default="1024")
    ap.add_argument("--out")
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.results) if l.strip()]
    d = {}
    for r in rows:
        d[(r["row_id"], r["budget"])] = r
    cases = sorted({r["case_id"] for r in rows})
    rng = np.random.default_rng(0); idx = rng.integers(0, len(cases), (5000, len(cases)))
    def ci(v):
        s = np.sort(v[idx].mean(1)); return [float(s[125]), float(s[4875])]
    def dec(rid, b):
        r = d.get((rid, b)); return None if r is None else (r["decision"] == "YES")
    rep = {"n_rows": len(rows), "budgets": {}}
    ind = {}
    for b in (a.low, a.high):
        # part A completeness
        needA = [(f"A_{c}_{cond}_{q}_j0", b) for c in cases for cond in ["D"] + CONDS for q in ("t", "n")]
        complete_t = all((f"A_{c}_{cond}_t_j0", b) in d for c in cases for cond in ["D"] + CONDS)
        complete_n = all((f"A_{c}_{cond}_n_j0", b) in d for c in cases for cond in ["D"] + CONDS)
        e = {"complete_t": complete_t, "complete_n": complete_n,
             "unparseable": sum(1 for r in rows if r["budget"] == b and r["decision"] is None),
             "mean_thoughts_by_condition": {cond: float(np.mean([r["thoughts_tokens"] or 0 for r in rows if r["budget"] == b and r["condition"] == cond and r["part"] == "A"] or [0])) for cond in ["D"] + CONDS} if b != "none" else None}
        if complete_t:
            accD_t = np.array([dec(f"A_{c}_D_t_j0", b) == True for c in cases], dtype=float)
            e["acc_D_t"] = float(accD_t.mean())
            for cond in CONDS:
                v = np.array([dec(f"A_{c}_D_t_j0", b) != dec(f"A_{c}_{cond}_t_j0", b) for c in cases], dtype=float)
                e[f"dis_{cond}"] = float(v.mean()); e[f"dis_{cond}_ci"] = ci(v)
                e[f"acc_{cond}_t"] = float(np.mean([dec(f"A_{c}_{cond}_t_j0", b) == (cond != "L") for c in cases]))
            dF = np.array([dec(f"A_{c}_D_t_j0", b) != dec(f"A_{c}_F_t_j0", b) for c in cases], dtype=float)
            dC = np.array([dec(f"A_{c}_D_t_j0", b) != dec(f"A_{c}_C_t_j0", b) for c in cases], dtype=float)
            ind[b] = (dF, dC); e["delta"] = float((dF - dC).mean()); e["delta_ci"] = ci(dF - dC)
        if complete_n:
            e["acc_D_n"] = float(np.mean([dec(f"A_{c}_D_n_j0", b) == False for c in cases]))
        if complete_t and complete_n:
            e["acc_D"] = (e["acc_D_t"] + e["acc_D_n"]) / 2
            e["gate_reads"] = bool(e["acc_D"] >= 0.75 and e["dis_L"] >= 0.5)
        # part B
        for j in (1, 2):
            if all((f"B_{c}_D_t_j{j}", b) in d for c in cases):
                e[f"acc_t_H{j}"] = float(np.mean([dec(f"B_{c}_D_t_j{j}", b) == True for c in cases]))
            if all((f"B_{c}_D_n_j{j}", b) in d for c in cases):
                e[f"acc_n_H{j}"] = float(np.mean([dec(f"B_{c}_D_n_j{j}", b) == False for c in cases]))
        rep["budgets"][b] = e
    if a.low in ind and a.high in ind:
        (fl, cl), (fh, ch) = ind[a.low], ind[a.high]
        I = float((fl - cl).mean() - (fh - ch).mean()); v = (fl - cl) - (fh - ch)
        rep["primary"] = {"interaction": I, "ci95": ci(v), "delta_low": rep["budgets"][a.low]["delta"], "delta_high": rep["budgets"][a.high]["delta"],
                          "prediction_holds": bool(ci(v)[0] > 0 and rep["budgets"][a.low]["delta"] >= 0.10)}
    txt = json.dumps(rep, indent=1)
    if a.out:
        open(a.out, "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
