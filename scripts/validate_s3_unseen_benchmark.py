#!/usr/bin/env python3
"""Validate the frozen confirmatory unseen-family S3 benchmark."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


EXPECTED_PERMS = {"123", "132", "213", "231", "312", "321"}
EXPECTED_FAMILIES = {
    "direct_anchor_positive": True,
    "fork_join_positive": True,
    "conjunction_source_positive": True,
    "branch_to_conjunction_positive": True,
    "fork_missing_join_negative": False,
    "reverse_join_negative": False,
    "conjunction_gate_negative": False,
    "downstream_cycle_negative": False,
}


def fail(msg: str) -> None:
    raise SystemExit(msg)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("benchmark")
    args = parser.parse_args()

    per_case = defaultdict(list)
    family_counts = Counter()

    with Path(args.benchmark).open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            fam = row["family"]
            if fam not in EXPECTED_FAMILIES:
                fail(f"line {line_no}: unexpected family {fam}")
            if bool(row["gold"]) != EXPECTED_FAMILIES[fam]:
                fail(f"line {line_no}: wrong gold for {fam}")
            family_counts[fam] += 1
            per_case[row["case_id"]].append(row)

    if len(per_case) != 128:
        fail(f"expected 128 cases, found {len(per_case)}")

    for fam in EXPECTED_FAMILIES:
        if family_counts[fam] != 16 * 6:
            fail(f"{fam}: expected 96 rows, found {family_counts[fam]}")

    for cid, rows in per_case.items():
        if len(rows) != 6:
            fail(f"{cid}: expected 6 permutations, found {len(rows)}")
        if {r["permutation"] for r in rows} != EXPECTED_PERMS:
            fail(f"{cid}: permutation set mismatch")
        first = rows[0]
        base_multiset = sorted(first["premise_multiset"])
        for row in rows:
            if row["family"] != first["family"]:
                fail(f"{cid}: family changed")
            if row["gold"] != first["gold"]:
                fail(f"{cid}: gold changed")
            if row["certificate"] != first["certificate"]:
                fail(f"{cid}: certificate changed")
            if row["query"] != first["query"]:
                fail(f"{cid}: query changed")
            if row["formal_status"] != "same_formal_problem":
                fail(f"{cid}: bad formal status")
            if sorted(row["premise_multiset"]) != base_multiset:
                fail(f"{cid}: premise multiset changed")

    print("validated 128 unseen-family cases / 768 S3 prompts")


if __name__ == "__main__":
    main()
