#!/usr/bin/env python3
"""Validate the Phase 3 Hankel observation table `hankel_v0`.

Checks structure (32 rows x 32 columns x 16 control cells), re-derives every
gold label by an independent forward-chaining pass, and checks that gold is
constant across serializations inside one logical class (the property the
Lean-certified permutation invariance guarantees) and across all presentation
controls.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


EXPECTED_ROWS = 32
EXPECTED_COLS = 32
EXPECTED_CLASSES = 8
EXPECTED_SERIALIZATIONS = {"123", "231", "312", "321"}
EXPECTED_CONTROLS = 4 * 2 * 2


def fail(msg: str) -> None:
    raise SystemExit(msg)


def forward_chain(clauses, hyp: str, goal: str) -> bool:
    known = {hyp}
    frontier = True
    while frontier:
        frontier = False
        for body, head in clauses:
            if set(body) <= known and not set(head) <= known:
                known |= set(head)
                frontier = True
    return goal in known


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("benchmark")
    args = parser.parse_args()

    cells = defaultdict(list)
    rows_by_class = defaultdict(set)
    cols = set()
    prefix_multiset = {}
    gold_by_row_col = {}

    n = 0
    with Path(args.benchmark).open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            r = json.loads(line)
            n += 1
            if r["table"] != "hankel_v0":
                fail(f"line {line_no}: unexpected table")
            if r["serialization"] not in EXPECTED_SERIALIZATIONS:
                fail(f"line {line_no}: unexpected serialization")
            if r["gold_status"] != "generator_forward_chaining_not_lean_certified":
                fail(f"line {line_no}: gold_status must remain explicit")
            clauses = [(tuple(b), tuple(h)) for b, h in r["prefix_clauses"] + r["continuation_clauses"]]
            if forward_chain(clauses, r["query_hyp"], r["query_goal"]) != r["gold"]:
                fail(f"line {line_no}: gold disagrees with forward chaining")
            if forward_chain([(tuple(b), tuple(h)) for b, h in r["continuation_clauses"]],
                             r["query_hyp"], r["query_goal"]) != r["direct_answer_control"]:
                fail(f"line {line_no}: direct_answer_control mismatch")
            if r["candidates"]["pos"] == r["candidates"]["neg"]:
                fail(f"line {line_no}: degenerate answer map")
            if not r["prompt"].endswith("Answer:"):
                fail(f"line {line_no}: prompt must end at the answer position")

            key = (r["row_id"], r["col_id"])
            ctrl = (r["relabeling"], r["renderer"], r["answer_map"])
            cells[key].append(ctrl)
            rows_by_class[r["logical_class"]].add(r["row_id"])
            cols.add(r["col_id"])

            ms = tuple(sorted(json.dumps(c, sort_keys=True) for c in r["prefix_clauses"]))
            if r["row_id"] in prefix_multiset and prefix_multiset[r["row_id"]] != ms:
                fail(f"{r['row_id']}: prefix multiset changed across cells")
            prefix_multiset[r["row_id"]] = ms

            if key in gold_by_row_col and gold_by_row_col[key] != r["gold"]:
                fail(f"{key}: gold changed across presentation controls")
            gold_by_row_col[key] = r["gold"]

    if len(cols) != EXPECTED_COLS:
        fail(f"expected {EXPECTED_COLS} columns, found {len(cols)}")
    if len(rows_by_class) != EXPECTED_CLASSES:
        fail(f"expected {EXPECTED_CLASSES} logical classes, found {len(rows_by_class)}")
    all_rows = set().union(*rows_by_class.values())
    if len(all_rows) != EXPECTED_ROWS:
        fail(f"expected {EXPECTED_ROWS} rows, found {len(all_rows)}")
    if len(cells) != EXPECTED_ROWS * EXPECTED_COLS:
        fail(f"expected {EXPECTED_ROWS * EXPECTED_COLS} cells, found {len(cells)}")
    for key, ctrls in cells.items():
        if len(ctrls) != EXPECTED_CONTROLS or len(set(ctrls)) != EXPECTED_CONTROLS:
            fail(f"{key}: expected {EXPECTED_CONTROLS} distinct control cells")
    if n != EXPECTED_ROWS * EXPECTED_COLS * EXPECTED_CONTROLS:
        fail(f"expected {EXPECTED_ROWS * EXPECTED_COLS * EXPECTED_CONTROLS} prompts, found {n}")

    # Gold must be constant across serializations inside each logical class,
    # and the same clause multiset must underlie every serialization.
    class_gold = {}
    for cls, rids in rows_by_class.items():
        if len(rids) != len(EXPECTED_SERIALIZATIONS):
            fail(f"{cls}: expected {len(EXPECTED_SERIALIZATIONS)} serializations")
        if len({prefix_multiset[r] for r in rids}) != 1:
            fail(f"{cls}: serializations do not share one clause multiset")
        vec = None
        for rid in rids:
            v = tuple(gold_by_row_col[(rid, c)] for c in sorted(cols))
            if vec is None:
                vec = v
            elif v != vec:
                fail(f"{cls}: gold differs across serializations")
        class_gold[cls] = vec

    if len(set(class_gold.values())) != EXPECTED_CLASSES:
        fail("logical classes must have pairwise distinct gold rows")

    yes = sum(sum(v) for v in class_gold.values())
    total = EXPECTED_CLASSES * EXPECTED_COLS
    print(
        f"validated hankel_v0: {n} prompts, {len(all_rows)} rows, {len(cols)} columns, "
        f"{EXPECTED_CLASSES} logical classes with distinct gold rows, "
        f"class-level YES rate {yes}/{total}"
    )


if __name__ == "__main__":
    main()
