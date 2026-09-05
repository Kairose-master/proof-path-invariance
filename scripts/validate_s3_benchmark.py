#!/usr/bin/env python3
"""Validate the Phase 2 S3 benchmark."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


EXPECTED_PERMS = {"123", "132", "213", "231", "312", "321"}


def fail(msg: str) -> None:
    raise SystemExit(msg)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("benchmark")
    parser.add_argument("--expected-cases", type=int, default=128)
    args = parser.parse_args()

    per_case = defaultdict(list)
    families = Counter()
    gold_by_family = {}

    with Path(args.benchmark).open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            cid = row["case_id"]
            per_case[cid].append(row)
            families[row["family"]] += 1
            gold = row["gold"]
            if row["family"] in gold_by_family and gold_by_family[row["family"]] != gold:
                fail(f"line {line_no}: inconsistent gold within family")
            gold_by_family[row["family"]] = gold

    if len(per_case) != args.expected_cases:
        fail(f"expected {args.expected_cases} cases, found {len(per_case)}")

    for cid, rows in per_case.items():
        if len(rows) != 6:
            fail(f"{cid}: expected 6 permutations, found {len(rows)}")
        perms = {r["permutation"] for r in rows}
        if perms != EXPECTED_PERMS:
            fail(f"{cid}: permutation set mismatch")

        first = rows[0]
        base_multiset = sorted(first["premise_multiset"])
        for row in rows:
            if row["gold"] != first["gold"]:
                fail(f"{cid}: gold changed across permutations")
            if row["family"] != first["family"]:
                fail(f"{cid}: family changed across permutations")
            if row["certificate"] != first["certificate"]:
                fail(f"{cid}: certificate changed across permutations")
            if row["query"] != first["query"]:
                fail(f"{cid}: query changed across permutations")
            if row["formal_status"] != "same_formal_problem":
                fail(f"{cid}: unexpected formal_status")
            if sorted(row["premise_multiset"]) != base_multiset:
                fail(f"{cid}: premise multiset changed")

    positives = sum(1 for g in gold_by_family.values() if g)
    negatives = sum(1 for g in gold_by_family.values() if not g)
    if positives < 2 or negatives < 2:
        fail("need at least two positive and two negative families")

    print(
        f"validated {len(per_case)} cases, {sum(len(v) for v in per_case.values())} prompts, "
        f"{positives} positive families, {negatives} negative families"
    )


if __name__ == "__main__":
    main()
