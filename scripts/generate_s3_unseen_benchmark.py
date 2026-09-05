#!/usr/bin/env python3
"""Generate the confirmatory unseen-family S3 benchmark.

Eight formal families are used: four positive and four negative. Each family
contributes 16 neutral-symbol cases, and each case is rendered under all six
premise permutations. Total: 128 cases / 768 prompts.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path


PERMS = list(itertools.permutations((0, 1, 2)))

FAMILIES = [
    {
        "family": "direct_anchor_positive",
        "gold": True,
        "certificate": {
            "lean_file": "PPI/ConfirmatoryUnseen.lean",
            "theorem": "PPI.confirmDirectAnchor",
        },
        "premises": lambda a, b, c, d: [
            f"If {a} holds, then {d} holds.",
            f"If {b} holds, then {c} holds.",
            f"If {c} holds, then {b} holds.",
        ],
    },
    {
        "family": "fork_join_positive",
        "gold": True,
        "certificate": {
            "lean_file": "PPI/ConfirmatoryUnseen.lean",
            "theorem": "PPI.confirmForkJoin",
        },
        "premises": lambda a, b, c, d: [
            f"If {a} holds, then {b} holds.",
            f"If {a} holds, then {c} holds.",
            f"If both {b} and {c} hold, then {d} holds.",
        ],
    },
    {
        "family": "conjunction_source_positive",
        "gold": True,
        "certificate": {
            "lean_file": "PPI/ConfirmatoryUnseen.lean",
            "theorem": "PPI.confirmConjunctionSource",
        },
        "premises": lambda a, b, c, d: [
            f"If {a} holds, then {b} holds.",
            f"If both {a} and {b} hold, then {c} holds.",
            f"If {c} holds, then {d} holds.",
        ],
    },
    {
        "family": "branch_to_conjunction_positive",
        "gold": True,
        "certificate": {
            "lean_file": "PPI/ConfirmatoryUnseen.lean",
            "theorem": "PPI.confirmBranchToConjunction",
        },
        "premises": lambda a, b, c, d: [
            f"If {a} holds, then both {b} and {c} hold.",
            f"If {b} holds, then {d} holds.",
            f"If {c} holds, then {d} holds.",
        ],
    },
    {
        "family": "fork_missing_join_negative",
        "gold": False,
        "certificate": {
            "lean_file": "PPI/ConfirmatoryUnseen.lean",
            "theorem": "PPI.confirmForkMissingJoinCountermodel",
        },
        "premises": lambda a, b, c, d: [
            f"If {a} holds, then {b} holds.",
            f"If {a} holds, then {c} holds.",
            f"If both {b} and {d} hold, then {c} holds.",
        ],
    },
    {
        "family": "reverse_join_negative",
        "gold": False,
        "certificate": {
            "lean_file": "PPI/ConfirmatoryUnseen.lean",
            "theorem": "PPI.confirmReverseJoinCountermodel",
        },
        "premises": lambda a, b, c, d: [
            f"If {b} holds, then {a} holds.",
            f"If {c} holds, then {b} holds.",
            f"If both {b} and {c} hold, then {d} holds.",
        ],
    },
    {
        "family": "conjunction_gate_negative",
        "gold": False,
        "certificate": {
            "lean_file": "PPI/ConfirmatoryUnseen.lean",
            "theorem": "PPI.confirmConjunctionGateCountermodel",
        },
        "premises": lambda a, b, c, d: [
            f"If {a} holds, then {b} holds.",
            f"If both {b} and {c} hold, then {d} holds.",
            f"If {d} holds, then {c} holds.",
        ],
    },
    {
        "family": "downstream_cycle_negative",
        "gold": False,
        "certificate": {
            "lean_file": "PPI/ConfirmatoryUnseen.lean",
            "theorem": "PPI.confirmDownstreamCycleCountermodel",
        },
        "premises": lambda a, b, c, d: [
            f"If {a} holds, then {b} holds.",
            f"If {b} holds, then {c} holds.",
            f"If both {c} and {d} hold, then {b} holds.",
        ],
    },
]


def atom(prefix: str, i: int) -> str:
    return f"{prefix}{i:04d}"


def render_prompt(statements: list[str], query: str) -> str:
    body = "\n".join(f"- {s}" for s in statements)
    return (
        "Determine whether the conclusion logically follows from the statements.\n"
        "Use only the information given. Answer exactly YES or NO.\n\n"
        f"Statements:\n{body}\n\nConclusion:\n{query}\n\nAnswer:"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-family", type=int, default=16)
    parser.add_argument("--out", default="experiments/cases/s3_unseen_v0.jsonl")
    args = parser.parse_args()

    if args.per_family != 16:
        raise SystemExit("confirmatory v0 is frozen to --per-family 16")

    rows = []
    case_counter = 0

    for fam in FAMILIES:
        for i in range(1, args.per_family + 1):
            case_counter += 1
            a = atom("P", case_counter)
            b = atom("Q", case_counter)
            c = atom("R", case_counter)
            d = atom("S", case_counter)
            premises = fam["premises"](a, b, c, d)
            query = f"If {a} holds, then {d} holds."

            for perm in PERMS:
                perm_id = "".join(str(j + 1) for j in perm)
                ordered = [premises[j] for j in perm]
                rows.append({
                    "case_id": f"unseen-{fam['family']}-{i:04d}",
                    "family": fam["family"],
                    "gold": fam["gold"],
                    "certificate": fam["certificate"],
                    "permutation": perm_id,
                    "permutation_indices": [j + 1 for j in perm],
                    "formal_status": "same_formal_problem",
                    "premise_multiset": premises,
                    "query": query,
                    "prompt": render_prompt(ordered, query),
                })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    print(
        f"wrote {len(rows)} prompts from {case_counter} cases "
        f"across {len(FAMILIES)} unseen families to {out}"
    )


if __name__ == "__main__":
    main()
