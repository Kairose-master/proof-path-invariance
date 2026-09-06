#!/usr/bin/env python3
"""Build the frozen RQ2 table: cases x conditions {D, F, C, L} x 4 queries.

Fixed rules (see docs/PREREGISTRATION_RQ2.md):
  * base D: 5 random Horn clauses over 7 atoms, target (a, goal) with
    depth_D >= 3 (goal = the deepest derivable atom, ties by name);
  * F: D + one derivable single-atom clause that reduces depth_D by the
    least amount (sorted-first among those);
  * F1: D + the direct clause a -> goal (maximal shortening, maximal
    lexical overlap with the target query; secondary condition);
  * C: D + one derivable single-atom clause that keeps depth_D, with the
    same overlap with {a, goal} as F when possible (sorted-first);
  * L: D minus one clause, the sorted-first whose deletion makes the target
    non-derivable (logic-change control);
  * queries: t = (a, goal); d1 = (a, y) with y the sorted-first depth-1 atom;
    n = (a, z) with z the sorted-first atom not derivable from a in D;
    r = (goal, a);
  * exclusion: no F, no C, no L, or no non-derivable atom -> case dropped;
  * certification: closure(T, {x}) equal for T in {D, F, C} and all atoms x.
Every case is generated from one seed; cases are taken in order.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dfc import ATOMS, closure, dfc, random_base, rounds_to_derive  # noqa: E402

NAMES = ["p", "q", "r", "s", "t", "u", "v"]
CONDITIONS = ["D", "F", "F1", "C", "L"]
INSTRUCTION = "Answer exactly YES or NO."
CANDIDATES = {"pos": " YES", "neg": " NO"}


def render_clause(body, head):
    ante = f"If {body[0]} holds" if len(body) == 1 else f"If both {body[0]} and {body[1]} hold"
    cons = f"then {head[0]} holds." if len(head) == 1 else f"then both {head[0]} and {head[1]} hold."
    return f"{ante}, {cons}"


def render_prompt(statements, query):
    body = "\n".join(f"- {s}" for s in statements)
    return ("Determine whether the conclusion logically follows from the statements.\n"
            f"Use only the information given. {INSTRUCTION}\n\n"
            f"Statements:\n{body}\n\nConclusion:\n{query}\n\nAnswer:")


def logic_change(clauses, hyp, goal):
    for i in sorted(range(len(clauses)), key=lambda i: clauses[i]):
        rest = clauses[:i] + clauses[i + 1:]
        if goal not in closure(rest, [hyp]):
            return rest, clauses[i]
    return None


def queries(clauses, hyp, goal):
    depth = {x: rounds_to_derive(clauses, hyp, x) for x in ATOMS if x != hyp}
    d1 = sorted(x for x, d in depth.items() if d == 1)
    nd = sorted(x for x, d in depth.items() if d is None)
    if not d1 or not nd:
        return None
    return {"t": (hyp, goal), "d1": (hyp, d1[0]), "n": (hyp, nd[0]), "r": (goal, hyp)}


def make_cases(n, seed):
    rng = random.Random(seed)
    cases, tried = [], 0
    while len(cases) < n and tried < 50000:
        tried += 1
        b = random_base(rng, 5, 3)
        if b is None:
            continue
        clauses, hyp, goal = b
        fc = dfc(clauses, hyp, goal)
        lc = logic_change(clauses, hyp, goal)
        qs = queries(clauses, hyp, goal)
        if fc is None or lc is None or qs is None:
            continue
        Fc, Cc = fc
        F1 = ((hyp,), (goal,))
        theories = {"D": clauses, "F": clauses + [Fc], "F1": clauses + [F1], "C": clauses + [Cc], "L": lc[0]}
        for x in ATOMS:   # certification of full logical identity D = F = C
            assert closure(theories["D"], [x]) == closure(theories["F"], [x]) == closure(theories["C"], [x]) == closure(theories["F1"], [x])
        assert goal not in closure(theories["L"], [hyp])
        cases.append({"case_id": f"case{len(cases):03d}", "hyp": hyp, "goal": goal,
                      "theories": theories, "F_clause": Fc, "C_clause": Cc, "L_deleted": lc[1],
                      "overlap": {"F": len(set(Fc[0] + Fc[1]) & {hyp, goal}), "C": len(set(Cc[0] + Cc[1]) & {hyp, goal})},
                      "depth": {k: rounds_to_derive(t, hyp, goal) for k, t in theories.items()},
                      "queries": qs})
    return cases, tried


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20260906)
    ap.add_argument("--out-dir", default="rq2/table")
    a = ap.parse_args()
    cases, tried = make_cases(a.n, a.seed)
    if len(cases) < a.n:
        sys.exit(f"only {len(cases)} cases after {tried} draws")
    out = Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
    rows = []
    for ci, c in enumerate(cases):
        names = {x: f"{NAMES[i]}{ci:03d}" for i, x in enumerate(ATOMS)}
        for cond in CONDITIONS:
            th = c["theories"][cond]
            stmts = [render_clause([names[x] for x in b], [names[y] for y in h]) for b, h in th]
            for qk, (h, g) in c["queries"].items():
                gold = "pos" if g in closure(th, [h]) else "neg"
                rows.append({"table": "rq2", "row_id": f"{c['case_id']}_{cond}", "logical_class": c["case_id"],
                             "col_id": qk, "relabeling": "R0", "renderer": "bullets", "answer_map": "yesno",
                             "condition": cond, "case_id": c["case_id"], "query_kind": qk,
                             "query_hyp": h, "query_goal": g, "clauses": th, "gold": gold,
                             "depth": rounds_to_derive(th, h, g),
                             "prompt": render_prompt(stmts, f"{names[g]} holds, given that {names[h]} holds."),
                             "candidates": CANDIDATES})
    (out / "rq2_cases.json").write_text(json.dumps({"seed": a.seed, "n": a.n, "draws": tried, "cases": cases}, indent=1))
    with (out / "rq2_prompts.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    sha = hashlib.sha256((out / "rq2_prompts.jsonl").read_bytes()).hexdigest()
    (out / "LOCK").write_text(f"rq2_prompts.jsonl sha256 {sha} rows {len(rows)} cases {len(cases)} seed {a.seed}\n")
    from collections import Counter
    print(json.dumps({"cases": len(cases), "draws": tried, "rows": len(rows), "sha256": sha,
                      "depth_D": Counter(c["depth"]["D"] for c in cases), "depth_F": Counter(c["depth"]["F"] for c in cases),
                      "depth_C": Counter(c["depth"]["C"] for c in cases),
                      "gold_by_query": {qk: Counter(r["gold"] for r in rows if r["query_kind"] == qk and r["condition"] == "D") for qk in ("t", "d1", "n", "r")}}, default=dict))


if __name__ == "__main__":
    main()
