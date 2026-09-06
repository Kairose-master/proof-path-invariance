#!/usr/bin/env python3
"""RQ2 analysis on the frozen table (docs/PREREGISTRATION_RQ2.md).

Per recognizer (result file):
  acc_D      accuracy on D over all 4 queries; acc_D_t on the target query
  dis(X)     fraction of cases whose target decision differs between D and X
  delta      dis(F) - dis(C)
  dis4(X)    mean Hamming distance over the 4-query decision vector D vs X
  ext(X)     median |margin_D - margin_X| on the target query (extended observation)
Primary comparison: interaction I = delta(low budget) - delta(high budget)
with a paired case bootstrap 95% CI (B = 5000, seed 0).

  python3 rq2/analyze.py --results experiments/rq2/results --primary iter_r4_k2 iter_r4_k4
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

CONDS = ["F", "F1", "C", "L"]
QUERIES = ["t", "d1", "n", "r"]


def load(path):
    d = {}
    with open(path) as f:
        for l in f:
            if l.strip():
                r = json.loads(l)
                d[(r["case_id"], r["condition"], r["query_kind"])] = r
    return d


def dec(r):
    p, n = r["observation"]
    return p > n


def per_case(d, cases):
    """Per case: target decisions/margins by condition and 4-query vectors."""
    out = {}
    for c in cases:
        e = {}
        for cond in ["D"] + CONDS:
            rs = [d[(c, cond, q)] for q in QUERIES]
            e[cond] = {"dec_t": dec(rs[0]), "m_t": rs[0]["observation"][0] - rs[0]["observation"][1],
                       "vec": [dec(r) for r in rs], "correct": [dec(r) == (r["gold"] == "pos") for r in rs]}
        out[c] = e
    return out


def stats(pc, cases):
    n = len(cases)
    s = {"n": n, "acc_D": sum(sum(pc[c]["D"]["correct"]) for c in cases) / (4 * n),
         "acc_D_t": sum(pc[c]["D"]["correct"][0] for c in cases) / n}
    for cond in CONDS:
        s[f"dis_{cond}"] = sum(pc[c]["D"]["dec_t"] != pc[c][cond]["dec_t"] for c in cases) / n
        s[f"dis4_{cond}"] = sum(sum(x != y for x, y in zip(pc[c]["D"]["vec"], pc[c][cond]["vec"])) for c in cases) / (4 * n)
        s[f"ext_{cond}"] = sorted(abs(pc[c]["D"]["m_t"] - pc[c][cond]["m_t"]) for c in cases)[n // 2]
        s[f"acc_{cond}_t"] = sum(pc[c][cond]["correct"][0] for c in cases) / n
    s["delta"] = s["dis_F"] - s["dis_C"]
    s["delta1"] = s["dis_F1"] - s["dis_C"]
    # direction of D-F disagreement: F correct & D wrong vs the reverse
    s["F_fixes"] = sum(pc[c]["F"]["correct"][0] and not pc[c]["D"]["correct"][0] for c in cases) / n
    s["F_breaks"] = sum(pc[c]["D"]["correct"][0] and not pc[c]["F"]["correct"][0] for c in cases) / n
    return s


def bootstrap(arrays, fn, B=5000, seed=0):
    """Paired case bootstrap: `arrays` are per-case numpy arrays (same case
    order); fn(resampled arrays) -> statistic.  Returns the 2.5/97.5 % points."""
    import numpy as np
    rng = np.random.default_rng(seed)
    n = len(arrays[0])
    idx = rng.integers(0, n, size=(B, n))
    vals = np.sort(np.array([fn(*[a[i] for a in arrays]) for i in idx]))
    return float(vals[int(0.025 * B)]), float(vals[int(0.975 * B)])


def indicators(pc, cases):
    import numpy as np
    dF = np.array([pc[c]["D"]["dec_t"] != pc[c]["F"]["dec_t"] for c in cases], dtype=float)
    dC = np.array([pc[c]["D"]["dec_t"] != pc[c]["C"]["dec_t"] for c in cases], dtype=float)
    return dF, dC


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--primary", nargs=2, metavar=("LOW", "HIGH"), action="append", default=[])
    ap.add_argument("--out")
    a = ap.parse_args()
    files = sorted(Path(a.results).glob("*.jsonl"))
    tables = {f.stem: load(f) for f in files}
    full = max(len(t) for t in tables.values())
    for name in [n for n, t in tables.items() if len(t) < full]:
        print(f"skipping {name}: {len(tables[name])} of {full} rows (incomplete)")
        del tables[name]
    cases = sorted({k[0] for k in next(iter(tables.values()))})
    report = {"n_cases": len(cases), "recognizers": {}, "primary": []}
    pcs, ind = {}, {}
    for name, d in tables.items():
        pcs[name] = per_case(d, cases)
        ind[name] = indicators(pcs[name], cases)
        s = stats(pcs[name], cases)
        s["delta_ci"] = bootstrap(ind[name], lambda f, c: f.mean() - c.mean())
        report["recognizers"][name] = s
    for low, high in a.primary:
        if low not in pcs or high not in pcs:
            report["primary"].append({"low": low, "high": high, "missing": True}); continue
        fl, cl = ind[low]; fh, ch = ind[high]
        I = float((fl - cl).mean() - (fh - ch).mean())
        ci = bootstrap((fl, cl, fh, ch), lambda a, b, c, d: (a - b).mean() - (c - d).mean())
        dl, dh = report["recognizers"][low]["delta"], report["recognizers"][high]["delta"]
        report["primary"].append({"low": low, "high": high, "delta_low": dl, "delta_high": dh, "interaction": I, "ci95": ci,
                                  "prediction_holds": bool(ci[0] > 0 and dl >= 0.10)})
    txt = json.dumps(report, indent=1)
    if a.out:
        Path(a.out).write_text(txt)
    hdr = f"{'recognizer':22s} {'acc_D':>6s} {'accDt':>6s} {'disF':>6s} {'disF1':>6s} {'disC':>6s} {'disL':>6s} {'delta':>6s} {'CI':>16s} {'extF':>7s} {'extC':>7s} {'Ffix':>5s} {'Fbrk':>5s}"
    print(hdr)
    for name, s in report["recognizers"].items():
        print(f"{name:22s} {s['acc_D']:6.2f} {s['acc_D_t']:6.2f} {s['dis_F']:6.2f} {s['dis_F1']:6.2f} {s['dis_C']:6.2f} {s['dis_L']:6.2f} {s['delta']:6.2f} "
              f"[{s['delta_ci'][0]:5.2f},{s['delta_ci'][1]:5.2f}] {s['ext_F']:7.3f} {s['ext_C']:7.3f} {s['F_fixes']:5.2f} {s['F_breaks']:5.2f}")
    for p in report["primary"]:
        print("PRIMARY", json.dumps(p))


if __name__ == "__main__":
    main()
