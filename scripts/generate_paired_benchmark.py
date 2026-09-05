#!/usr/bin/env python3
"""Generate paired prompts for the minimal Phase 1 invariance test.

The confirmatory v0 transform is renderer-level premise reversal only.
It leaves the formal case, premises-as-a-set, query, certificate, and gold label
unchanged. No categorical or proof-path interpretation is made.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_cases(paths):
    for raw in paths:
        path = Path(raw)
        with path.open(encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    yield path, json.loads(line)
                except json.JSONDecodeError as exc:
                    raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}") from exc


def render(statements: list[str], query: str) -> str:
    block = "\n".join(f"- {s}" for s in statements)
    return (
        "Determine whether the conclusion logically follows from the statements.\n"
        "Use only the information given. Answer exactly YES or NO.\n\n"
        f"Statements:\n{block}\n\n"
        f"Question: {query}\n"
        "Answer:"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cases",
        nargs="+",
        default=["experiments/cases/symbolic_v0.jsonl"],
    )
    parser.add_argument("--out", default="experiments/prompts/paired_v0.jsonl")
    args = parser.parse_args()

    rows = []
    for source, case in load_cases(args.cases):
        d = case["conditions"]["D"]
        statements = list(d["statements"])
        query = d["query"]

        variants = {
            "base": statements,
            "premise_reverse": list(reversed(statements)),
        }

        for variant, rendered_statements in variants.items():
            rows.append(
                {
                    "pair_id": case["case_id"],
                    "variant": variant,
                    "transform": None if variant == "base" else "premise_reverse",
                    "gold": case["gold"],
                    "certificate": case["certificate"],
                    "source_case_file": str(source),
                    "formal_status": "same_formal_problem",
                    "prompt": render(rendered_statements, query),
                }
            )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"wrote {len(rows)} paired prompts to {out}")


if __name__ == "__main__":
    main()
