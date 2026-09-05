#!/usr/bin/env python3
"""Generate deterministic symbolic Phase 1 cases.

These cases deliberately add surface instances without adding new logical
families. Half instantiate implication transitivity (gold YES); half instantiate
the existing non-entailment countermodel family (gold NO).

The generated labels are neutral symbols, not natural-language world knowledge.
This reduces lexical-semantic confounding but does not create independent formal
structures: all cases share one of two certificate schemas.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


POS_CERT = {
    "lean_file": "PPI/Transitivity.lean",
    "theorem": "PPI.direct₂ / PPI.factored₂",
    "family": "implication_transitivity",
}

NEG_CERT = {
    "lean_file": "PPI/Controls.lean",
    "theorem": "PPI.negativeCountermodel / PPI.negativeCountermodelWithExtra",
    "family": "non_entailment_countermodel",
}


def atom(prefix: str, i: int) -> str:
    return f"{prefix}{i:04d}"


def make_case(i: int, gold: bool) -> dict:
    a = atom("P", i)
    b = atom("Q", i)
    c = atom("R", i)

    if gold:
        premises = [
            f"If {a} holds, then {b} holds.",
            f"If {b} holds, then {c} holds.",
        ]
        cert = POS_CERT
        cid = f"sym-pos-{i:04d}"
    else:
        premises = [
            f"If {a} holds, then {b} holds.",
            f"If {c} holds, then {b} holds.",
        ]
        cert = NEG_CERT
        cid = f"sym-neg-{i:04d}"

    query = f"Does it follow that if {a} holds, then {c} holds?"

    # D is the only condition used by the minimal paired benchmark.
    # F/C remain present solely for compatibility with the legacy case schema
    # and are not part of the confirmatory Phase 1 analysis.
    return {
        "case_id": cid,
        "certificate": cert,
        "atoms": {"A": a, "B": b, "C": c},
        "premises": premises,
        "target": f"If {a} holds, then {c} holds.",
        "gold": gold,
        "conditions": {
            "D": {
                "statements": premises,
                "query": query,
            },
            "F": {
                "statements": premises + [f"{b} is listed as an auxiliary symbol."],
                "query": query,
                "control_note": "Legacy-schema placeholder; disabled in confirmatory Phase 1.",
            },
            "C": {
                "statements": premises + [f"S{i:04d} is listed as an auxiliary symbol."],
                "query": query,
                "control_note": "Legacy-schema placeholder; disabled in confirmatory Phase 1.",
            },
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-label", type=int, default=128)
    parser.add_argument("--out", default="experiments/cases/symbolic_v0.jsonl")
    args = parser.parse_args()

    if args.per_label <= 0:
        raise SystemExit("--per-label must be positive")

    rows = []
    for i in range(1, args.per_label + 1):
        rows.append(make_case(i, True))
        rows.append(make_case(i, False))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    print(f"wrote {len(rows)} deterministic symbolic cases to {out}")


if __name__ == "__main__":
    main()
