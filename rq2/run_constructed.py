#!/usr/bin/env python3
"""Evaluate symbolic and constructed recognizers on the frozen RQ2 table.

Writes one result file per recognizer in the schema of scripts/run_hf_hankel.py
(observation = [pos, neg]; decision = pos > neg, ties -> NO).

  python3 rq2/run_constructed.py --out-dir experiments/rq2/results \
      --model experiments/rq2/iter_r4.pt --rounds 1 2 3 4 6
  python3 rq2/run_constructed.py --out-dir experiments/rq2/results --symbolic
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "constructed"))
import data7  # noqa: E402
from dfc import ATOMS, exact_oracle, k_round_reasoner  # noqa: E402
from models import IterReasoner, SetRecognizer  # noqa: E402


def rows(prompts):
    with open(prompts) as f:
        return [json.loads(l) for l in f if l.strip()]


def write(out_dir, run_id, results):
    p = Path(out_dir) / f"{run_id}.jsonl"
    with p.open("w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(run_id, len(results), "->", p)


def base(r, run_id):
    return {k: r[k] for k in ("table", "row_id", "logical_class", "col_id", "gold", "condition", "case_id", "query_kind", "depth")} | {"run_id": run_id, "renderer": "tokens"}


def run_symbolic(table, out_dir):
    fns = {"oracle": exact_oracle, "constant_no": lambda c, h, g: False}
    for k in (1, 2, 3, 4, 6):
        fns[f"symbolic_k{k}"] = k_round_reasoner(k)
    for name, fn in fns.items():
        res = []
        for r in table:
            cl = [(tuple(b), tuple(h)) for b, h in r["clauses"]]
            yes = fn(cl, r["query_hyp"], r["query_goal"])
            res.append(base(r, name) | {"observation": [1.0, 0.0] if yes else [0.0, 1.0]})
        write(out_dir, name, res)


def run_model(table, out_dir, path, rounds_list, tag):
    ck = torch.load(path, map_location="cpu")
    kind = ck["kind"]
    model = SetRecognizer(vocab_size=len(data7.VOCAB)) if kind == "set" else IterReasoner(rounds=ck["rounds"], n_atoms=7)
    model.load_state_dict(ck["state"]); model.eval()
    relabel = {x: f"A{i}" for i, x in enumerate(ATOMS)}
    cs = [[(tuple(b), tuple(h)) for b, h in r["clauses"]] for r in table]
    hyps = [r["query_hyp"] for r in table]; goals = [r["query_goal"] for r in table]
    rl = [relabel] * len(table)
    budgets = rounds_list if kind == "iter" else [None]
    for k in budgets:
        run_id = f"{tag}_k{k}" if k is not None else tag
        res = []
        with torch.no_grad():
            for i in range(0, len(table), 256):
                sl = slice(i, i + 256)
                inp = data7.tensors(kind, cs[sl], hyps[sl], goals[sl], rl[sl])
                logits = model(*inp, rounds=k) if kind == "iter" else model(*inp)
                for j, r in enumerate(table[sl]):
                    res.append(base(r, run_id) | {"observation": [float(logits[j, 1]), float(logits[j, 0])]})
        write(out_dir, run_id, res)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts", default=str(HERE / "table" / "rq2_prompts.jsonl"))
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--symbolic", action="store_true")
    ap.add_argument("--model")
    ap.add_argument("--tag")
    ap.add_argument("--rounds", type=int, nargs="*", default=[1, 2, 3, 4, 6])
    a = ap.parse_args()
    Path(a.out_dir).mkdir(parents=True, exist_ok=True)
    table = rows(a.prompts)
    if a.symbolic:
        run_symbolic(table, a.out_dir)
    if a.model:
        run_model(table, a.out_dir, a.model, a.rounds, a.tag or Path(a.model).stem)


if __name__ == "__main__":
    main()
