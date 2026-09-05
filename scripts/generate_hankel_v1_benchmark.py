#!/usr/bin/env python3
"""Generate the Phase 3.2 Hankel table `hankel_v1`.

Changes relative to `hankel_v0`, each motivated by a theorem in
`recognition-paths`:

1. **Comparative (Boolean) columns.**  Every cell still records the answer
   logit pair, but the analysis reads only order relations: the decision
   `pos > neg` and, for two queries after the same continuation, the
   preference `margin(q1) > margin(q2)`.  No threshold, no metric, and
   automatic invariance to the common logit offset.  The table becomes a
   Boolean Chu space, the same kind of object as the logical table, so the
   canonical map `F : L -> B` is checked by exact equality of row profiles.
2. **Depth-two continuations.**  `Identification.lean` shows that a test
   family identifies `≡_ρ` iff its induced identity is closed under one-symbol
   extension.  Checking closure of the depth-one family needs depth-two
   columns `(a z, q)`.  All ordered pairs of the seven single clauses are
   included.
3. **Idempotence probes.**  `Recognition.lean` proves that logical invariance
   forces `ww ≈_ρ w`.  Repeated continuations `a a` and doubled prefixes
   `u u` (serialization 123 of each class) test that consequence directly.

Controls are reduced to two renderers with one relabeling (`sym1`) and one
answer map (YES/NO), because Phase 3.0 found the label family to change the
scale of order sensitivity by about 3x.

Gold labels are computed by Horn forward chaining (not Lean-certified per
cell).  Logical identity of serializations and of `u u` versus `u` is
Lean-certified in `recognition-paths` (`Horn.logicalEquiv_of_perm`,
`Horn.logicalEquiv_dup`).
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from generate_hankel_benchmark import (
    ANSWER_MAPS,
    LOGICAL_CLASSES,
    QUERIES,
    RENDERERS,
    SERIALIZATIONS,
    entails,
    label,
    relabel,
    render_clause_bullets,
    render_clause_prose,
    render_prompt,
)

RELABELING = "sym1"
ANSWER_MAP = "yesno"

SINGLE = {
    "d_e": (("d",), ("e",)),
    "c_e": (("c",), ("e",)),
    "b_d": (("b",), ("d",)),
    "e_a": (("e",), ("a",)),
    "a_d": (("a",), ("d",)),
    "e_d": (("e",), ("d",)),
    "b_c": (("b",), ("c",)),
}


def continuations():
    out = {"none": []}
    for k, c in SINGLE.items():
        out[k] = [c]
    for k1, k2 in itertools.product(SINGLE, repeat=2):
        out[f"{k1}.{k2}"] = [SINGLE[k1], SINGLE[k2]]
    return out


def rows():
    out = {}
    for class_id, clauses in LOGICAL_CLASSES.items():
        for perm_id, perm in SERIALIZATIONS.items():
            out[f"{class_id}-{perm_id}"] = {
                "logical_class": class_id,
                "serialization": perm_id,
                "prefix": [clauses[i] for i in perm],
                "doubled": False,
            }
    for class_id, clauses in LOGICAL_CLASSES.items():
        base = [clauses[i] for i in SERIALIZATIONS["123"]]
        out[f"{class_id}-123x2"] = {
            "logical_class": class_id,
            "serialization": "123x2",
            "prefix": base + base,
            "doubled": True,
        }
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="experiments/cases/hankel_v1.jsonl")
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
                        "table": "hankel_v1",
                        "row_id": row_id,
                        "logical_class": r["logical_class"],
                        "serialization": r["serialization"],
                        "doubled_prefix": r["doubled"],
                        "col_id": f"{cont_id}-{query_id}",
                        "continuation": cont_id,
                        "continuation_depth": len(cont),
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
                            "serializations: Horn.logicalEquiv_of_perm; doubled prefix: "
                            "Horn.logicalEquiv_dup (recognition-paths)"
                        ),
                        "prompt": render_prompt(renderer, statements, query, amap["instruction"]),
                    })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in out_rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    print(
        f"wrote {len(out_rows)} prompts: {len(rws)} rows x {len(conts)} continuations x "
        f"{len(QUERIES)} queries x {len(RENDERERS)} renderers to {out}"
    )


if __name__ == "__main__":
    main()
