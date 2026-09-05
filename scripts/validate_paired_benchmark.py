#!/usr/bin/env python3
"""Validate the generated minimal paired benchmark.

The validator checks only generator-level invariants. Lean validity is checked
separately by `lake build` and case-certificate validation.

For benchmark v0, the sole enabled transformation is premise reversal.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def fail(message: str) -> None:
    raise SystemExit(message)


def parse_prompt(prompt: str) -> tuple[list[str], str]:
    marker_s = "Statements:\n"
    marker_q = "\n\nQuestion: "
    if marker_s not in prompt or marker_q not in prompt:
        fail("unexpected prompt format")

    body = prompt.split(marker_s, 1)[1]
    statements_block, rest = body.split(marker_q, 1)
    statements = []
    for line in statements_block.splitlines():
        if not line.startswith("- "):
            fail(f"unexpected statement line: {line!r}")
        statements.append(line[2:])

    query = rest.rsplit("\nAnswer:", 1)[0]
    return statements, query


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()

    pairs: dict[str, dict[str, dict]] = defaultdict(dict)

    with Path(args.path).open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            pid = row.get("pair_id")
            variant = row.get("variant")
            if not pid or variant not in {"base", "premise_reverse"}:
                fail(f"line {line_no}: invalid pair_id/variant")
            if variant in pairs[pid]:
                fail(f"{pid}: duplicate variant {variant}")
            pairs[pid][variant] = row

    if not pairs:
        fail("no paired rows found")

    for pid, variants in pairs.items():
        if set(variants) != {"base", "premise_reverse"}:
            fail(f"{pid}: incomplete pair")

        base = variants["base"]
        rev = variants["premise_reverse"]

        for key in ("gold", "certificate", "source_case_file", "formal_status"):
            if base.get(key) != rev.get(key):
                fail(f"{pid}: {key} differs across pair")

        if base.get("formal_status") != "same_formal_problem":
            fail(f"{pid}: unexpected formal_status")

        if base.get("transform") is not None:
            fail(f"{pid}: base transform must be null")
        if rev.get("transform") != "premise_reverse":
            fail(f"{pid}: reverse transform must be premise_reverse")

        base_statements, base_query = parse_prompt(base["prompt"])
        rev_statements, rev_query = parse_prompt(rev["prompt"])

        if base_query != rev_query:
            fail(f"{pid}: query changed")
        if rev_statements != list(reversed(base_statements)):
            fail(f"{pid}: transformed statements are not the exact reverse")
        if sorted(rev_statements) != sorted(base_statements):
            fail(f"{pid}: premise multiset changed")

    print(f"validated {len(pairs)} paired benchmark item(s)")


if __name__ == "__main__":
    main()
