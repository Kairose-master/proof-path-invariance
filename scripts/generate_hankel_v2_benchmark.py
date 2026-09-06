#!/usr/bin/env python3
"""Generate the Phase 3.4 surface-controlled table `hankel_v2`.

Question: is the within-class proximity rewarded by the Boolean Gate I
logical, or is it shared surface content?

Design: for each of the eight logical classes, two kinds of neighbours of
the base serialization `123`.

- **Permutations** (`231`, `312`, `321`): maximal surface change (all three
  clauses move), no logical change (Lean: `Horn.logicalEquiv_of_perm`).
- **Single-arrow flips** (`f1`, `f2`, `f3`): the body and head of one
  single-atom clause are exchanged in place; minimal surface change (two
  atoms swap inside one clause), logical change (the validator requires the
  gold row to change).  Conjunction clauses are never flipped; a class with
  a conjunction clause contributes only the flips of its single-atom
  clauses.

Columns are the depth-<=1 family of `hankel_v1` (8 continuations x 4
queries = 32 logit cells, 80 Boolean tests per renderer).  Controls:
relabeling `sym1`, answer map YES/NO, two renderers.

A recognizer whose behavior tracks logic puts flips farther than
permutations; a recognizer that tracks surface puts permutations farther
than flips.  The ratio of the two median distances is the preregistered
statistic (see docs/PHASE3_HANKEL_V2_DESIGN.md).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from generate_hankel_benchmark import (
    ANSWER_MAPS, LOGICAL_CLASSES, QUERIES, RENDERERS, SERIALIZATIONS,
    entails, label, relabel, render_clause_bullets, render_clause_prose, render_prompt,
)
from generate_hankel_v1_benchmark import SINGLE

RELABELING = "sym1"
ANSWER_MAP = "yesno"


def continuations():
    out = {"none": []}
    for k, c in SINGLE.items():
        out[k] = [c]
    return out


def gold_row(prefix):
    return tuple(entails(prefix + cont, h, g)
                 for cont in continuations().values() for (h, g) in QUERIES.values())


def rows():
    out = {}
    for class_id, clauses in LOGICAL_CLASSES.items():
        base = [clauses[i] for i in SERIALIZATIONS["123"]]
        for perm_id, perm in SERIALIZATIONS.items():
            out[f"{class_id}-{perm_id}"] = {
                "logical_class": class_id, "variant": perm_id, "kind": "base" if perm_id == "123" else "perm",
                "prefix": [clauses[i] for i in perm], "flipped_clause": None,
            }
        base_gold = gold_row(base)
        for i, (body, head) in enumerate(base):
            if len(body) != 1 or len(head) != 1:
                continue
            flipped = list(base)
            flipped[i] = (head, body)
            if gold_row(flipped) == base_gold:
                continue   # not a logical change on this column family
            out[f"{class_id}-f{i + 1}"] = {
                "logical_class": class_id, "variant": f"f{i + 1}", "kind": "flip",
                "prefix": flipped, "flipped_clause": i + 1,
            }
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="experiments/cases/hankel_v2.jsonl")
    parser.add_argument("--case-index", type=int, default=1)
    args = parser.parse_args()

    conts = continuations()
    rws = rows()
    amap = ANSWER_MAPS[ANSWER_MAP]
    out_rows = []
    for row_id, r in rws.items():
        prefix = r["prefix"]
        for cont_id, cont in conts.items():
            theory = prefix + cont
            golds = {qid: entails(theory, h, g) for qid, (h, g) in QUERIES.items()}
            for query_id, (hyp, goal) in QUERIES.items():
                for renderer in RENDERERS:
                    trace = relabel(theory, RELABELING, args.case_index)
                    render = render_clause_bullets if renderer == "bullets" else render_clause_prose
                    statements = [render(b, h) for b, h in trace]
                    h_lab = label(hyp, RELABELING, args.case_index)
                    g_lab = label(goal, RELABELING, args.case_index)
                    query = (f"If {h_lab} holds, then {g_lab} holds." if renderer == "bullets"
                             else f"{h_lab} implies {g_lab}.")
                    out_rows.append({
                        "table": "hankel_v2",
                        "row_id": row_id,
                        "logical_class": r["logical_class"],
                        "variant": r["variant"],
                        "kind": r["kind"],
                        "flipped_clause": r["flipped_clause"],
                        "col_id": f"{cont_id}-{query_id}",
                        "continuation": cont_id,
                        "query": query_id,
                        "query_hyp": hyp,
                        "query_goal": goal,
                        "relabeling": RELABELING,
                        "renderer": renderer,
                        "answer_map": ANSWER_MAP,
                        "candidates": {"pos": amap["pos"], "neg": amap["neg"]},
                        "prefix_clauses": [[list(b), list(h)] for b, h in prefix],
                        "continuation_clauses": [[list(b), list(h)] for b, h in cont],
                        "gold": golds[query_id],
                        "gold_all_queries": golds,
                        "gold_status": "generator_forward_chaining_not_lean_certified",
                        "row_equivalence_status": (
                            "perm: same theory, Horn.logicalEquiv_of_perm; flip: different theory "
                            "(validator checks the gold row changes)"
                        ),
                        "prompt": render_prompt(renderer, statements, query, amap["instruction"]),
                    })
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in out_rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    kinds = {}
    for r in rws.values():
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    print(f"wrote {len(out_rows)} prompts: {len(rws)} rows {kinds} x {len(conts)} continuations x "
          f"{len(QUERIES)} queries x {len(RENDERERS)} renderers to {out}")


if __name__ == "__main__":
    main()
