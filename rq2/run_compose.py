#!/usr/bin/env python3
"""RQ2g: the learned reader's own composition (Kleisli-style), monotonicity and unit.

For each fresh case with hypothesis atom a and budgets j, k:
  R_k{a}  = {a} ∪ {g' ≠ a : model(hyps={a}, goal=g'; k) = YES}
  composite decision = model(hyps=R_k{a}, goal=g; j)          for g = target t and non-derivable n
compared with the symbolic closure T_m{a} for m = j+k-2, j+k-1, j+k.
Monotonicity: S = {a} ⊆ S' = {a, y}; violation iff YES on S and NO on S' for some goal.
Unit: R_0 S ∋ g  iff  g ∈ S, tested on S = {a} and S = T_1{a}.

  python3 rq2/run_compose.py --model experiments/rq2/iter_r4.pt --out experiments/rq2/results_g/iter_r4.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "constructed"))
import data7  # noqa: E402
from build_presat import t_rounds  # noqa: E402
from dfc import ATOMS, closure  # noqa: E402
from models import IterReasoner  # noqa: E402

BUDGETS = [1, 2, 3]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True); ap.add_argument("--cases", default=str(HERE / "table_c" / "rq2_cases.json")); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    ck = torch.load(a.model, map_location="cpu"); model = IterReasoner(rounds=ck["rounds"], n_atoms=7); model.load_state_dict(ck["state"]); model.eval()
    cases = json.load(open(a.cases))["cases"]
    relabel = {x: f"A{i}" for i, x in enumerate(ATOMS)}

    def decide(items, k):
        """items: list of (clauses, hyps(list), goal) -> list of bool."""
        out = []
        with torch.no_grad():
            for i in range(0, len(items), 512):
                cs, hs, gs = zip(*items[i:i + 512])
                inp = data7.iter_tensors(list(cs), list(hs), list(gs), [relabel] * len(cs))
                lg = model(*inp, rounds=k)
                out += [bool(lg[t, 1] > lg[t, 0]) for t in range(len(cs))]
        return out

    D = {c["case_id"]: [(tuple(b), tuple(h)) for b, h in c["theories"]["D"]] for c in cases}
    rng = np.random.default_rng(0); idx = rng.integers(0, len(cases), (5000, len(cases)))
    def ci(v):
        s = np.sort(v[idx].mean(1)); return [float(s[125]), float(s[4875])]
    rep = {"model": a.model, "composite": {}, "monotonicity": {}, "unit": {}}
    # R_k{a} for every case and k
    Rk = {}
    for k in BUDGETS:
        items = [(D[c["case_id"]], [c["hyp"]], g) for c in cases for g in ATOMS if g != c["hyp"]]
        dec = decide(items, k); t = 0
        for c in cases:
            s = {c["hyp"]}
            for g in ATOMS:
                if g != c["hyp"]:
                    if dec[t]:
                        s.add(g)
                    t += 1
            Rk[(c["case_id"], k)] = sorted(s)
    for j in BUDGETS:
        for k in BUDGETS:
            items = [(D[c["case_id"]], Rk[(c["case_id"], k)], c["queries"][q][1]) for c in cases for q in ("t", "n")]
            dec = decide(items, j)
            per = {m: [] for m in ("l2", "l1", "up", "s2", "s1", "exact")}
            t = 0
            for c in cases:
                vals = {m: [] for m in per}
                for q in ("t", "n"):
                    g = c["queries"][q][1]; y = dec[t]; t += 1
                    T = {m: g in t_rounds(D[c["case_id"]], [c["hyp"]], m) for m in (max(j + k - 2, 0), max(j + k - 1, 0), j + k)}
                    l2 = (not T[max(j + k - 2, 0)]) or y; l1 = (not T[max(j + k - 1, 0)]) or y; up = (not y) or T[j + k]
                    vals["l2"].append(l2); vals["l1"].append(l1); vals["up"].append(up); vals["s2"].append(l2 and up); vals["s1"].append(l1 and up); vals["exact"].append(y == T[j + k])
                for m in per:
                    per[m].append(np.mean(vals[m]))
            rep["composite"][f"j{j}_k{k}"] = {m: {"rate": float(np.mean(per[m])), "ci95": ci(np.array(per[m]))} for m in per}
    # monotonicity: S={a} vs S'={a,y}, y = sorted-first atom not derivable from a (else sorted-first != a)
    for k in BUDGETS:
        base, ext, meta = [], [], []
        for c in cases:
            reach = closure(D[c["case_id"]], [c["hyp"]])
            ys = [x for x in ATOMS if x != c["hyp"] and x not in reach] or [x for x in ATOMS if x != c["hyp"]]
            y = sorted(ys)[0]
            for g in ATOMS:
                if g != c["hyp"] and g != y:
                    base.append((D[c["case_id"]], [c["hyp"]], g)); ext.append((D[c["case_id"]], sorted([c["hyp"], y]), g)); meta.append(c["case_id"])
        db, de = decide(base, k), decide(ext, k)
        viol = {}
        for cid, b_, e_ in zip(meta, db, de):
            viol.setdefault(cid, []).append(b_ and not e_)
        v = np.array([np.mean(viol[c["case_id"]]) for c in cases])
        rep["monotonicity"][f"k{k}"] = {"violation_rate": float(v.mean()), "ci95": ci(v), "cases_with_violation": float(np.mean([any(viol[c["case_id"]]) for c in cases]))}
    # unit: R_0
    for name, hyps_of in (("S=a", lambda c: [c["hyp"]]), ("S=T1a", lambda c: t_rounds(D[c["case_id"]], [c["hyp"]], 1))):
        items = [(D[c["case_id"]], hyps_of(c), g) for c in cases for g in ATOMS]
        dec = decide(items, 0); t = 0; ok = []
        for c in cases:
            H = set(hyps_of(c)); vals = []
            for g in ATOMS:
                vals.append(dec[t] == (g in H)); t += 1
            ok.append(np.mean(vals))
        rep["unit"][name] = {"agreement_with_identity": float(np.mean(ok)), "ci95": ci(np.array(ok))}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True); Path(a.out).write_text(json.dumps(rep, indent=1))
    print(f"{'pair':7s} {'slack2':>14s} {'slack1':>14s} {'upper':>7s} {'lower2':>7s} {'lower1':>7s} {'exact':>6s}")
    for name, e in rep["composite"].items():
        print(f"{name:7s} {e['s2']['rate']:.3f} [{e['s2']['ci95'][0]:.3f},{e['s2']['ci95'][1]:.3f}] {e['s1']['rate']:.3f} [{e['s1']['ci95'][0]:.3f},{e['s1']['ci95'][1]:.3f}] {e['up']['rate']:7.3f} {e['l2']['rate']:7.3f} {e['l1']['rate']:7.3f} {e['exact']['rate']:6.3f}")
    print("monotonicity:", {k: (round(v["violation_rate"], 4), v["ci95"], round(v["cases_with_violation"], 3)) for k, v in rep["monotonicity"].items()})
    print("unit R_0 = id:", {k: (round(v["agreement_with_identity"], 3), v["ci95"]) for k, v in rep["unit"].items()})
    print("P9_holds", all(e["s2"]["ci95"][0] >= 0.95 for e in rep["composite"].values()), "P10_holds", all(v["violation_rate"] <= 0.05 for v in rep["monotonicity"].values()))


if __name__ == "__main__":
    main()
