#!/usr/bin/env python3
"""Generate Phase 2 S3 premise-permutation prompts.

The benchmark uses four three-premise formal families: two positive and two
negative. Gold label is therefore not identical to family identity.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path


PERMS = list(itertools.permutations((0, 1, 2)))

FAMILIES = [
    {
        "family": "chain3_positive",
        "gold": True,
        "certificate": {
            "lean_file": "PPI/Phase2.lean",
            "theorem": "PPI.phase2Chain3",
        },
        "premises": lambda a, b, c, d: [
            f"If {a} holds, then {b} holds.",
            f"If {b} holds, then {c} holds.",
            f"If {c} holds, then {d} holds.",
        ],
    },
    {
        "family": "shortcut_positive",
        "gold": True,
        "certificate": {
            "lean_file": "PPI/Phase2.lean",
            "theorem": "PPI.phase2Shortcut",
        },
        "premises": lambda a, b, c, d: [
            f"If {a} holds, then {b} holds.",
            f"If {b} holds, then {d} holds.",
            f"If {c} holds, then {d} holds.",
        ],
    },
    {
        "family": "collider_negative",
        "gold": False,
        "certificate": {
            "lean_file": "PPI/Phase2.lean",
            "theorem": "PPI.phase2ColliderCountermodel",
        },
        "premises": lambda a, b, c, d: [
            f"If {a} holds, then {b} holds.",
            f"If {c} holds, then {b} holds.",
            f"If {c} holds, then {d} holds.",
        ],
    },
    {
        "family": "reverse_start_negative",
        "gold": False,
        "certificate": {
            "lean_file": "PPI/Phase2.lean",
            "theorem": "PPI.phase2ReverseStartCountermodel",
        },
        "premises": lambda a, b, c, d: [
            f"If {b} holds, then {a} holds.",
            f"If {b} holds, then {c} holds.",
            f"If {c} holds, then {d} holds.",
        ],
    },
]


def atom(prefix: str, i: int) -> str:
    return f"{prefix}{i:04d}"


def prompt(statements: list[str], query: str) -> str:
    body = "\n".join(f"- {s}" for s in statements)
    return (
        "Determine whether the conclusion logically follows from the statements.\n"
        "Use only the information given. Answer exactly YES or NO.\n\n"
        f"Statements:\n{body}\n\nConclusion:\n{query}\n\nAnswer:"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-family", type=int, default=32)
    parser.add_argument("--out", default="experiments/cases/s3_v0.jsonl")
    args = parser.parse_args()

    if args.per_family <= 0:
        raise SystemExit("--per-family must be positive")

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
                    "case_id": f"s3-{fam['family']}-{i:04d}",
                    "family": fam["family"],
                    "gold": fam["gold"],
                    "certificate": fam["certificate"],
                    "permutation": perm_id,
                    "permutation_indices": [j + 1 for j in perm],
                    "formal_status": "same_formal_problem",
                    "premise_multiset": premises,
                    "query": query,
                    "prompt": prompt(ordered, query),
                })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    print(
        f"wrote {len(rows)} prompts from {case_counter} cases "
        f"across {len(FAMILIES)} families to {out}"
    )


if __name__ == "__main__":
    main()
