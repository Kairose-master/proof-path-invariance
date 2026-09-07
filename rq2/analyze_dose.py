#!/usr/bin/env python3
"""Preregistered analysis for RQ2f (docs/PREREGISTRATION_RQ2F.md).

  python3 rq2/analyze_dose.py --results experiments/rq2/results_f/flash_lite_all.jsonl \
      --b1024 experiments/rq2/results_e/flash_lite_all.jsonl --out experiments/rq2/results_f/analysis.json
Uses only rows whose budget equals the row's planned budget (none / 256); B1024 rows for
D, F, F1, C1 come from the RQ2e results (condition C there = C1 here).
"""

from __future__ import annotations

import argparse
import json

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True); ap.add_argument("--b1024"); ap.add_argument("--b0-prev")
    ap.add_argument("--out")
    a = ap.parse_args()
    d = {}
    for l in open(a.results):
        if l.strip():
            r = json.loads(l)
            if r["budget"] in ("none", "256"):
                d[(r["case_id"], r["condition"], r["budget"])] = r["decision"] == "YES"
    if a.b1024:
        for l in open(a.b1024):
            if l.strip():
                r = json.loads(l)
                if r["budget"] == "1024" and r["query_kind"] == "t" and r["row_id"].startswith("A_"):
                    d[(r["case_id"], "C1" if r["condition"] == "C" else r["condition"], "1024")] = r["decision"] == "YES"
    cases = sorted({k[0] for k in d})
    def net(cond, b, cs):
        return np.array([float(d[(c, cond, b)]) - float(d[(c, "D", b)]) for c in cs])
    def ci(v, seed=0):
        rng = np.random.default_rng(seed); idx = rng.integers(0, len(v), (5000, len(v)))
        s = np.sort(v[idx].mean(1)); return [float(s[125]), float(s[4875])]
    rep = {"n_cases": len(cases), "net": {}, "acc_D": {}}
    for b in ("none", "256", "1024"):
        cs = [c for c in cases if (c, "D", b) in d]
        if cs:
            rep["acc_D"][b] = float(np.mean([d[(c, "D", b)] for c in cs]))
        for cond in ("C1", "C2", "C3", "N1", "F", "F1", "L"):
            cs = [c for c in cases if (c, cond, b) in d and (c, "D", b) in d]
            if len(cs) >= 20:
                v = net(cond, b, cs); rep["net"][f"{cond}@{b}"] = {"n": len(cs), "net": float(v.mean()), "ci95": ci(v)}
    if "L@256" in rep["net"]:
        cs = [c for c in cases if (c, "L", "256") in d and (c, "D", "256") in d]
        rep["dis_L@256"] = float(np.mean([d[(c, "L", "256")] != d[(c, "D", "256")] for c in cs]))
    # P7a: C3 vs C1 on cases with all three
    cs3 = [c for c in cases if all((c, k, "none") in d for k in ("D", "C1", "C2", "C3"))]
    if cs3:
        diff = net("C3", "none", cs3) - net("C1", "none", cs3)
        rep["P7a"] = {"n": len(cs3), "net_C1": float(net("C1", "none", cs3).mean()), "net_C2": float(net("C2", "none", cs3).mean()),
                      "net_C3": float(net("C3", "none", cs3).mean()), "C3_minus_C1": float(diff.mean()), "ci95": ci(diff), "holds": bool(ci(diff)[1] < 0)}
    csN = [c for c in cases if all((c, k, "none") in d for k in ("D", "C1", "N1"))]
    if csN:
        delta = net("N1", "none", csN) - net("C1", "none", csN); lo, hi = ci(delta)
        verdict = "count" if (abs(delta.mean()) <= 0.05 and lo > -0.05 and hi < 0.05) else ("redundancy" if (delta.mean() > 0.05 and lo > 0) else ("distraction" if (delta.mean() < -0.05 and hi < 0) else "undecided"))
        rep["P7b"] = {"n": len(csN), "net_N1": float(net("N1", "none", csN).mean()), "net_C1": float(net("C1", "none", csN).mean()),
                      "delta_N1_minus_C1": float(delta.mean()), "ci95": [lo, hi], "verdict": verdict}
    # P8: budget response
    if all(f"{k}@{b}" in rep["net"] for k in ("F", "C1") for b in ("none", "256")):
        cs = [c for c in cases if all((c, k, b) in d for k in ("D", "F", "C1") for b in ("none", "256"))]
        dF = net("F", "none", cs) - net("F", "256", cs); dC = net("C1", "256", cs) - net("C1", "none", cs)
        nF256 = float(net("F", "256", cs).mean()); nC256 = float(net("C1", "256", cs).mean())
        rep["P8"] = {"n": len(cs), "a_F_shrinks": {"diff": float(dF.mean()), "ci95": ci(dF), "holds": bool(ci(dF)[0] > 0)},
                     "b_C_shrinks": {"diff": float(dC.mean()), "ci95": ci(dC), "holds": bool(ci(dC)[0] > 0)},
                     "c_no_reversal": {"net_F@256": nF256, "net_C1@256": nC256, "holds": bool(nF256 >= -0.02 and nC256 <= 0.02)}}
        rep["P8"]["holds"] = all(rep["P8"][k]["holds"] for k in ("a_F_shrinks", "b_C_shrinks", "c_no_reversal"))
    if a.b0_prev:
        prev = {}
        for l in open(a.b0_prev):
            r = json.loads(l)
            if r["budget"] == "none" and r["query_kind"] == "t" and r["row_id"].startswith("A_"):
                prev[(r["case_id"], "C1" if r["condition"] == "C" else r["condition"])] = r["decision"] == "YES"
        pairs = [(k, prev[k]) for k in prev if (k[0], k[1], "none") in d]
        rep["B0_rerun_disagreement"] = float(np.mean([d[(c, cond, "none")] != v for (c, cond), v in pairs])) if pairs else None
    txt = json.dumps(rep, indent=1)
    if a.out:
        open(a.out, "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
