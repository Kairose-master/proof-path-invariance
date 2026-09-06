#!/usr/bin/env python3
"""Generate the Phase 3.5 semantic-rewrite table `hankel_v3`.

Question: does a recognizer identify clause sets that are logically
identical but syntactically different, beyond permutation?

For each of the eight logical classes with base serialization `123`:

- `perm`  : the three non-identity serializations (syntactic identity;
            Lean `Horn.logicalEquiv_of_perm`);
- `red_k` : the base plus one *derivable* single-atom clause `x -> y`
            (y in the closure of x, clause not already present), up to three
            per class in a fixed order (semantic identity; Lean
            `Horn.logicalEquiv_append_derivable`);
- `flip_k`: the single-arrow flips of `hankel_v2` (logical change).

Two `red` rows of one class differ in exactly one clause and have the same
clause count: the **length-matched semantic rewrite** (Lean
`Horn.logicalEquiv_derivable_extensions`).  A `flip` row differs from the
base in exactly one clause and changes the logic: the length-matched
logical change.  The contrast between these two is the frozen statistic.

Columns: the depth-<=1 family (8 continuations x 4 queries), two renderers,
relabeling `sym1`, answer map YES/NO.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from generate_hankel_benchmark import (
    ANSWER_MAPS, ATOMS, LOGICAL_CLASSES, QUERIES, RENDERERS, SERIALIZATIONS,
    closure, entails, label, relabel, render_clause_bullets, render_clause_prose, render_prompt,
)
from generate_hankel_v1_benchmark import SINGLE
from generate_hankel_v2_benchmark import gold_row

RELABELING = "sym1"
ANSWER_MAP = "yesno"
MAX_RED = 3


def continuations():
    out = {"none": []}
    for k, c in SINGLE.items():
        out[k] = [c]
    return out


def derivable_singles(base):
    """Single-atom clauses x -> y derivable from base and not already present."""
    present = {(tuple(b), tuple(h)) for b, h in base}
    out = []
    for x in ATOMS:
        cl = closure(base, [x])
        for y in ATOMS:
            if y != x and y in cl and ((x,), (y,)) not in present:
                out.append(((x,), (y,)))
    return out


def rows():
    out = {}
    for class_id, clauses in LOGICAL_CLASSES.items():
        base = [clauses[i] for i in SERIALIZATIONS["123"]]
        base_gold = gold_row(base)
        for perm_id, perm in SERIALIZATIONS.items():
            out[f"{class_id}-{perm_id}"] = {
                "logical_class": class_id, "variant": perm_id,
                "kind": "base" if perm_id == "123" else "perm",
                "prefix": [clauses[i] for i in perm], "added_clause": None, "flipped_clause": None,
            }
        for k, c in enumerate(derivable_singles(base)[:MAX_RED]):
            ext = base + [c]
            assert gold_row(ext) == base_gold, (class_id, c)
            out[f"{class_id}-red{k + 1}"] = {
                "logical_class": class_id, "variant": f"red{k + 1}", "kind": "red",
                "prefix": ext, "added_clause": [list(c[0]), list(c[1])], "flipped_clause": None,
            }
        for i, (body, head) in enumerate(base):
            if len(body) != 1 or len(head) != 1:
                continue
            flipped = list(base)
            flipped[i] = (head, body)
            if gold_row(flipped) == base_gold:
                continue
            out[f"{class_id}-f{i + 1}"] = {
                "logical_class": class_id, "variant": f"f{i + 1}", "kind": "flip",
                "prefix": flipped, "added_clause": None, "flipped_clause": i + 1,
            }
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="experiments/cases/hankel_v3.jsonl")
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
                        "table": "hankel_v3", "row_id": row_id, "logical_class": r["logical_class"],
                        "variant": r["variant"], "kind": r["kind"],
                        "added_clause": r["added_clause"], "flipped_clause": r["flipped_clause"],
                        "col_id": f"{cont_id}-{query_id}", "continuation": cont_id, "query": query_id,
                        "query_hyp": hyp, "query_goal": goal,
                        "relabeling": RELABELING, "renderer": renderer, "answer_map": ANSWER_MAP,
                        "candidates": {"pos": amap["pos"], "neg": amap["neg"]},
                        "prefix_clauses": [[list(b), list(h)] for b, h in prefix],
                        "continuation_clauses": [[list(b), list(h)] for b, h in cont],
                        "gold": golds[query_id], "gold_all_queries": golds,
                        "gold_status": "generator_forward_chaining_not_lean_certified",
                        "row_equivalence_status": (
                            "perm: Horn.logicalEquiv_of_perm; red: Horn.logicalEquiv_append_derivable "
                            "(derivability checked by forward chaining); red-red: "
                            "Horn.logicalEquiv_derivable_extensions; flip: different theory"
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
