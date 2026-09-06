#!/usr/bin/env python3
"""Evaluate the composition law on the RQ2b table.

For a recognizer R with budget k and hypothesis set H_j:
  agree(j, k) = fraction of rows where R(H_j, goal; k) = R(H_0, goal; j + k).
Symbolic k-round reasoner: agree = 1 exactly (control).  Learned
IterReasoner: the preregistered prediction (docs/PREREGISTRATION_RQ2B.md).

  python3 rq2/run_presat.py --model experiments/rq2/iter_r4.pt --out experiments/rq2/results_b/iter_r4.json
  python3 rq2/run_presat.py --symbolic --out experiments/rq2/results_b/symbolic.json
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
from dfc import ATOMS  # noqa: E402
from build_presat import t_rounds  # noqa: E402
from models import IterReasoner  # noqa: E402

BUDGETS = [0, 1, 2, 3, 4, 5, 6]
PRIMARY = [(1, 2), (2, 1), (2, 2), (1, 3)]   # pairs where the symbolic yes-rate changes between budgets k and j+k


def rows():
    with open(HERE / "table" / "rq2b_presat.jsonl") as f:
        return [json.loads(l) for l in f if l.strip()]


def symbolic_decisions(table):
    dec = {}
    for r in table:
        cl = [(tuple(b), tuple(h)) for b, h in r["clauses"]]
        for k in BUDGETS:
            dec[(r["case_id"], r["query_kind"], r["j"], k)] = r["goal"] in t_rounds(cl, r["hyps"], k)
    return dec, {}


def model_decisions(table, path):
    ck = torch.load(path, map_location="cpu")
    model = IterReasoner(rounds=ck["rounds"], n_atoms=7); model.load_state_dict(ck["state"]); model.eval()
    relabel = {x: f"A{i}" for i, x in enumerate(ATOMS)}
    cs = [[(tuple(b), tuple(h)) for b, h in r["clauses"]] for r in table]
    hyps = [r["hyps"] for r in table]; goals = [r["goal"] for r in table]
    inp = data7.iter_tensors(cs, hyps, goals, [relabel] * len(table))
    dec, margin = {}, {}
    with torch.no_grad():
        for k in BUDGETS:
            logits = model(*inp, rounds=k)
            for i, r in enumerate(table):
                key = (r["case_id"], r["query_kind"], r["j"], k)
                dec[key] = bool(logits[i, 1] > logits[i, 0]); margin[key] = float(logits[i, 1] - logits[i, 0])
    return dec, margin


def analyze(table, dec, margin):
    cases = sorted({r["case_id"] for r in table})
    rng = np.random.default_rng(0); idx = rng.integers(0, len(cases), (5000, len(cases)))
    def ci(v):
        s = np.sort(v[idx].mean(1)); return [float(s[125]), float(s[4875])]
    out = {"pairs": {}, "accuracy": {}}
    for j in (1, 2):
        for k in BUDGETS:
            if j + k > max(BUDGETS):
                continue
            per_case = np.array([np.mean([dec[(c, q, j, k)] == dec[(c, q, 0, j + k)] for q in ("t", "n")]) for c in cases])
            e = {"agree": float(per_case.mean()), "ci95": ci(per_case),
                 "agree_t": float(np.mean([dec[(c, "t", j, k)] == dec[(c, "t", 0, j + k)] for c in cases])),
                 "agree_n": float(np.mean([dec[(c, "n", j, k)] == dec[(c, "n", 0, j + k)] for c in cases])),
                 "yes_rate_Hj_k": float(np.mean([dec[(c, "t", j, k)] for c in cases])),
                 "yes_rate_H0_jk": float(np.mean([dec[(c, "t", 0, j + k)] for c in cases]))}
            if margin:
                e["median_abs_margin_diff_t"] = float(np.median([abs(margin[(c, "t", j, k)] - margin[(c, "t", 0, j + k)]) for c in cases]))
            out["pairs"][f"j{j}_k{k}"] = e
    gold = {(r["case_id"], r["query_kind"]): r["gold"] == "pos" for r in table}
    for k in BUDGETS:
        for j in (0, 1, 2):
            out["accuracy"][f"j{j}_k{k}"] = float(np.mean([dec[(c, q, j, k)] == gold[(c, q)] for c in cases for q in ("t", "n")]))
    out["primary"] = {f"j{j}_k{k}": out["pairs"][f"j{j}_k{k}"] for j, k in PRIMARY}
    out["prediction_holds"] = all(out["pairs"][f"j{j}_k{k}"]["ci95"][0] >= 0.95 for j, k in PRIMARY)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--symbolic", action="store_true"); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    table = rows()
    dec, margin = symbolic_decisions(table) if a.symbolic else model_decisions(table, a.model)
    rep = analyze(table, dec, margin)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(rep, indent=1))
    print(f"{'pair':8s} {'agree':>6s} {'CI':>14s} {'agr_t':>6s} {'agr_n':>6s} {'yesHjk':>7s} {'yesH0':>7s}")
    for name, e in rep["pairs"].items():
        flag = "*" if name in rep["primary"] else " "
        print(f"{name:7s}{flag} {e['agree']:6.3f} [{e['ci95'][0]:5.3f},{e['ci95'][1]:5.3f}] {e['agree_t']:6.3f} {e['agree_n']:6.3f} {e['yes_rate_Hj_k']:7.3f} {e['yes_rate_H0_jk']:7.3f}")
    print("accuracy", {k: round(v, 3) for k, v in rep["accuracy"].items()})
    print("PREDICTION_HOLDS", rep["prediction_holds"])


if __name__ == "__main__":
    main()
