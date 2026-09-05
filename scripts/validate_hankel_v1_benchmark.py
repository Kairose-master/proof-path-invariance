#!/usr/bin/env python3
"""Validate `hankel_v1`: structure, independent gold re-derivation, gold
constancy across serializations and doubled prefixes, and renderer pairing."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


EXPECTED_ROWS = 40
EXPECTED_CONTS = 57
EXPECTED_QUERIES = 4
EXPECTED_RENDERERS = 2


def fail(msg: str) -> None:
    raise SystemExit(msg)


def forward_chain(clauses, hyp, goal):
    known = {hyp}
    changed = True
    while changed:
        changed = False
        for body, head in clauses:
            if set(body) <= known and not set(head) <= known:
                known |= set(head)
                changed = True
    return goal in known


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("benchmark")
    args = parser.parse_args()

    cells = defaultdict(set)
    gold = {}
    rows = {}
    conts = set()
    n = 0
    with Path(args.benchmark).open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            r = json.loads(line)
            n += 1
            if r["table"] != "hankel_v1":
                fail(f"line {line_no}: unexpected table")
            if r["relabeling"] != "sym1" or r["answer_map"] != "yesno":
                fail(f"line {line_no}: controls must be fixed to sym1 / yesno")
            clauses = [(tuple(b), tuple(h)) for b, h in r["prefix_clauses"] + r["continuation_clauses"]]
            if forward_chain(clauses, r["query_hyp"], r["query_goal"]) != r["gold"]:
                fail(f"line {line_no}: gold disagrees with forward chaining")
            if len(r["continuation_clauses"]) != r["continuation_depth"] or r["continuation_depth"] > 2:
                fail(f"line {line_no}: continuation depth mismatch")
            if not r["prompt"].endswith("Answer:"):
                fail(f"line {line_no}: prompt must end at the answer position")
            key = (r["row_id"], r["col_id"])
            cells[key].add(r["renderer"])
            if key in gold and gold[key] != r["gold"]:
                fail(f"{key}: gold changed across renderers")
            gold[key] = r["gold"]
            rows[r["row_id"]] = (r["logical_class"], r["serialization"], r["doubled_prefix"],
                                 tuple(sorted(json.dumps(c) for c in r["prefix_clauses"])))
            conts.add(r["continuation"])

    if len(rows) != EXPECTED_ROWS:
        fail(f"expected {EXPECTED_ROWS} rows, found {len(rows)}")
    if len(conts) != EXPECTED_CONTS:
        fail(f"expected {EXPECTED_CONTS} continuations, found {len(conts)}")
    cols = {k[1] for k in cells}
    if len(cols) != EXPECTED_CONTS * EXPECTED_QUERIES:
        fail("column count mismatch")
    for key, rends in cells.items():
        if len(rends) != EXPECTED_RENDERERS:
            fail(f"{key}: expected {EXPECTED_RENDERERS} renderers")
    if n != EXPECTED_ROWS * EXPECTED_CONTS * EXPECTED_QUERIES * EXPECTED_RENDERERS:
        fail(f"unexpected prompt count {n}")

    # Gold must agree across all rows of one logical class (serializations and
    # the doubled prefix are Lean-certified logically identical).
    by_class = defaultdict(list)
    for rid, (cls, ser, dbl, ms) in rows.items():
        by_class[cls].append(rid)
    if len(by_class) != 8:
        fail("expected 8 logical classes")
    profiles = {}
    for cls, rids in by_class.items():
        if len(rids) != 5:
            fail(f"{cls}: expected 4 serializations + 1 doubled prefix")
        vecs = {tuple(gold[(rid, c)] for c in sorted(cols)) for rid in rids}
        if len(vecs) != 1:
            fail(f"{cls}: gold differs across logically identical rows")
        profiles[cls] = next(iter(vecs))
        ms = {rows[r][3] for r in rids if not rows[r][2]}
        if len(ms) != 1:
            fail(f"{cls}: serializations do not share one clause multiset")
    if len(set(profiles.values())) != 8:
        fail("logical classes must have pairwise distinct gold rows")

    yes = sum(sum(v) for v in profiles.values())
    print(
        f"validated hankel_v1: {n} prompts, {len(rows)} rows, {len(cols)} columns, "
        f"8 classes with distinct gold rows, class-level YES rate {yes}/{8 * len(cols)}"
    )


if __name__ == "__main__":
    main()
