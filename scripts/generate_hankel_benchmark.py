#!/usr/bin/env python3
"""Generate the Phase 3 Hankel observation table `hankel_v0`.

The table realises the observation pairing

    H_rho(u, t) = rho(u, t),   t = (z, q),

demanded by the Recognition Factorization Theorem
(`recognition-paths`, `RecognitionPaths/Recognition.lean`):

- rows `u`     : 32 prefix traces = 8 Horn logical classes x 4 serializations;
- columns `t`  : 32 tests = 8 continuation traces `z` x 4 queries `q`;
- controls     : 4 atom relabelings x 2 renderers x 2 answer-token maps.

Each cell is rendered as one prompt; the runner records BOTH answer logits so
the observation space is R^2, not a single margin.

Formal status of the ingredients:

- Rows inside one logical class are permutations of one clause multiset.
  Their theory-level logical identity is Lean-certified in `recognition-paths`
  by `RecognitionPaths.Horn.logicalEquiv_of_perm`.
- Cell gold labels are computed by Horn forward chaining in this script.  They
  are generator-validated, NOT Lean-certified per cell.
- Atom relabeling, renderer choice, and answer-token map are presentation
  controls; they are NOT Lean-certified as logically irrelevant.

Nothing in this file assumes that the model respects any of this structure.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


# --------------------------------------------------------------------------
# Small Horn world over five abstract atoms.  A clause is (body, head), both
# conjunctions of atoms.  The signature contains A -> B, A /\ B -> C and
# A -> B /\ C, exactly the signature fixed in the Lean development.
# --------------------------------------------------------------------------

ATOMS = ["a", "b", "c", "d", "e"]


def clause(body: list[str], head: list[str]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return (tuple(body), tuple(head))


# Eight logical classes.  Each is a multiset of three clauses.  They were
# chosen so that the 8 x 32 gold matrix has full row rank 8, all eight rows are
# distinct, and the overall YES rate is close to one half.
LOGICAL_CLASSES = {
    "chain": [clause(["a"], ["b"]), clause(["b"], ["c"]), clause(["c"], ["d"])],
    "fork_join": [clause(["a"], ["b"]), clause(["a"], ["c"]), clause(["b", "c"], ["d"])],
    "chain_gap": [clause(["a"], ["b"]), clause(["b"], ["c"]), clause(["d"], ["e"])],
    "branch": [clause(["a"], ["b", "c"]), clause(["c"], ["d"]), clause(["e"], ["b"])],
    "reversed": [clause(["b"], ["a"]), clause(["c"], ["b"]), clause(["d"], ["c"])],
    "fragments": [clause(["a"], ["b"]), clause(["c"], ["d"]), clause(["d"], ["e"])],
    "gated": [clause(["a", "b"], ["c"]), clause(["c"], ["d"]), clause(["d"], ["e"])],
    "skip": [clause(["a"], ["c"]), clause(["c"], ["e"]), clause(["b"], ["d"])],
}

# Four serializations per class: the cyclic rotations (closed under
# composition) plus the full reversal used in Phase 1.
SERIALIZATIONS = {
    "123": (0, 1, 2),
    "231": (1, 2, 0),
    "312": (2, 0, 1),
    "321": (2, 1, 0),
}

# Eight continuation traces, appended after the prefix.
CONTINUATIONS = {
    "none": [],
    "d_e": [clause(["d"], ["e"])],
    "c_e": [clause(["c"], ["e"])],
    "b_d": [clause(["b"], ["d"])],
    "e_a": [clause(["e"], ["a"])],
    "a_d": [clause(["a"], ["d"])],
    "e_d": [clause(["e"], ["d"])],
    "b_c": [clause(["b"], ["c"])],
}

# Four queries (hypothesis atom, goal atom).
QUERIES = {
    "ad": ("a", "d"),
    "ae": ("a", "e"),
    "bd": ("b", "d"),
    "ce": ("c", "e"),
}

# Four atom relabelings: neutral symbol families, indexed by relabeling id.
RELABELINGS = {
    "sym1": ["P", "Q", "R", "S", "T"],
    "sym2": ["K", "M", "N", "W", "Z"],
    "sym3": ["T", "S", "R", "Q", "P"],
    "sym4": ["X1", "X2", "X3", "X4", "X5"],
}

# Two answer-token maps.  Candidates must each be a single tokenizer token;
# the runner checks this and refuses to run otherwise.
ANSWER_MAPS = {
    "yesno": {"pos": " YES", "neg": " NO", "instruction": "Answer exactly YES or NO."},
    "truefalse": {"pos": " True", "neg": " False", "instruction": "Answer exactly True or False."},
}

RENDERERS = ["bullets", "prose"]


# --------------------------------------------------------------------------
# Horn forward chaining: the standard decision procedure for propositional
# Horn entailment.  Gold = goal is in the closure of {hyp} under the clauses.
# --------------------------------------------------------------------------

def closure(theory, facts):
    known = set(facts)
    changed = True
    while changed:
        changed = False
        for body, head in theory:
            if all(x in known for x in body):
                for y in head:
                    if y not in known:
                        known.add(y)
                        changed = True
    return known


def entails(theory, hyp: str, goal: str) -> bool:
    return goal in closure(theory, [hyp])


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def label(atom: str, relabeling: str, case_index: int) -> str:
    base = RELABELINGS[relabeling][ATOMS.index(atom)]
    return f"{base}{case_index:04d}"


def render_clause_bullets(body: list[str], head: list[str]) -> str:
    if len(body) == 1:
        ante = f"If {body[0]} holds"
    else:
        ante = f"If both {body[0]} and {body[1]} hold"
    if len(head) == 1:
        cons = f"then {head[0]} holds."
    else:
        cons = f"then both {head[0]} and {head[1]} hold."
    return f"{ante}, {cons}"


def render_clause_prose(body: list[str], head: list[str]) -> str:
    ante = body[0] if len(body) == 1 else f"{body[0]} together with {body[1]}"
    cons = head[0] if len(head) == 1 else f"{head[0]} and also {head[1]}"
    return f"{ante} implies {cons}."


def render_prompt(renderer: str, statements: list[str], query: str, instruction: str) -> str:
    if renderer == "bullets":
        body = "\n".join(f"- {s}" for s in statements)
        return (
            "Determine whether the conclusion logically follows from the statements.\n"
            f"Use only the information given. {instruction}\n\n"
            f"Statements:\n{body}\n\nConclusion:\n{query}\n\nAnswer:"
        )
    if renderer == "prose":
        body = " ".join(statements)
        return (
            f"Consider the following facts. {body}\n"
            f"Question: does it follow that {query[:-1]}? "
            f"Use only the facts above. {instruction}\n"
            "Answer:"
        )
    raise ValueError(renderer)


def relabel(clauses, relabeling: str, case_index: int):
    return [
        ([label(x, relabeling, case_index) for x in body],
         [label(y, relabeling, case_index) for y in head])
        for body, head in clauses
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="experiments/cases/hankel_v0.jsonl")
    parser.add_argument("--case-index", type=int, default=1,
                        help="numeric suffix shared by all atom labels")
    args = parser.parse_args()

    rows = []
    row_ids = []
    col_ids = []

    for class_id, clauses in LOGICAL_CLASSES.items():
        for perm_id in SERIALIZATIONS:
            row_ids.append(f"{class_id}-{perm_id}")
    for cont_id in CONTINUATIONS:
        for query_id in QUERIES:
            col_ids.append(f"{cont_id}-{query_id}")

    for class_id, clauses in LOGICAL_CLASSES.items():
        for perm_id, perm in SERIALIZATIONS.items():
            prefix = [clauses[i] for i in perm]
            row_id = f"{class_id}-{perm_id}"
            for cont_id, cont in CONTINUATIONS.items():
                for query_id, (hyp, goal) in QUERIES.items():
                    col_id = f"{cont_id}-{query_id}"
                    gold = entails(prefix + cont, hyp, goal)
                    gold_prefix_only = entails(prefix, hyp, goal)
                    direct_control = entails(cont, hyp, goal)
                    for relabeling in RELABELINGS:
                        for renderer in RENDERERS:
                            for answer_map, amap in ANSWER_MAPS.items():
                                trace = relabel(prefix + cont, relabeling, args.case_index)
                                render = render_clause_bullets if renderer == "bullets" else render_clause_prose
                                statements = [render(b, h) for b, h in trace]
                                h_lab = label(hyp, relabeling, args.case_index)
                                g_lab = label(goal, relabeling, args.case_index)
                                if renderer == "bullets":
                                    query = f"If {h_lab} holds, then {g_lab} holds."
                                else:
                                    query = f"{h_lab} implies {g_lab}."
                                prompt = render_prompt(renderer, statements, query, amap["instruction"])
                                rows.append({
                                    "table": "hankel_v0",
                                    "row_id": row_id,
                                    "logical_class": class_id,
                                    "serialization": perm_id,
                                    "col_id": col_id,
                                    "continuation": cont_id,
                                    "query": query_id,
                                    "query_hyp": hyp,
                                    "query_goal": goal,
                                    "relabeling": relabeling,
                                    "renderer": renderer,
                                    "answer_map": answer_map,
                                    "candidates": {"pos": amap["pos"], "neg": amap["neg"]},
                                    "prefix_clauses": [[list(b), list(h)] for b, h in prefix],
                                    "continuation_clauses": [[list(b), list(h)] for b, h in cont],
                                    "gold": gold,
                                    "gold_prefix_only": gold_prefix_only,
                                    "direct_answer_control": direct_control,
                                    "gold_status": "generator_forward_chaining_not_lean_certified",
                                    "row_equivalence_status": (
                                        "same_clause_multiset; logical identity Lean-certified by "
                                        "RecognitionPaths.Horn.logicalEquiv_of_perm (recognition-paths)"
                                    ),
                                    "control_status": "relabeling_renderer_answer_map_not_lean_certified",
                                    "prompt": prompt,
                                })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    print(
        f"wrote {len(rows)} prompts: {len(row_ids)} rows x {len(col_ids)} columns x "
        f"{len(RELABELINGS)} relabelings x {len(RENDERERS)} renderers x "
        f"{len(ANSWER_MAPS)} answer maps to {out}"
    )


if __name__ == "__main__":
    main()
