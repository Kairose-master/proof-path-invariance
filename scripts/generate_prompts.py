#!/usr/bin/env python3
"""Render D/F/C experiment prompts from certified case records.

This script deliberately does not call any model API. It freezes the stimulus
construction layer before data collection.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

LABELS = ("D", "F", "C")


def load_cases(path: Path):
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise SystemExit(f"invalid JSON on line {line_no}: {exc}") from exc


def render(case: dict, condition: str) -> str:
    block = case["conditions"][condition]
    statements = "\n".join(f"- {s}" for s in block["statements"])
    return (
        "Determine whether the conclusion logically follows from the statements.\n"
        "Use only the information given. Answer exactly YES or NO.\n\n"
        f"Statements:\n{statements}\n\n"
        f"Question: {block['query']}\n"
        "Answer:"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="experiments/cases/transitivity_v0.jsonl")
    parser.add_argument("--out", default="experiments/prompts/transitivity_v0.jsonl")
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for case in load_cases(Path(args.cases)):
        for condition in LABELS:
            rows.append({
                "case_id": case["case_id"],
                "condition": condition,
                "gold": case["gold"],
                "certificate": case["certificate"],
                "prompt": render(case, condition),
            })

    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"wrote {len(rows)} prompts to {out}")


if __name__ == "__main__":
    main()
