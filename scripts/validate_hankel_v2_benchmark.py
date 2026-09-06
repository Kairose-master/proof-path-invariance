#!/usr/bin/env python3
"""Validate `hankel_v2`: structure, gold re-derivation, permutations keep the
gold row, every flip changes it, and no flip coincides with another row's
clause multiset."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def fail(msg: str) -> None:
    raise SystemExit(msg)


def forward_chain(clauses, hyp, goal):
    known = {hyp}
    changed = True
    while changed:
        changed = False
        for body, head in clauses:
            if set(body) <= known and not set(head) <= known:
                known |= set(head); changed = True
    return goal in known


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("benchmark")
    args = parser.parse_args()
    gold, rows, cells = {}, {}, defaultdict(set)
    n = 0
    with Path(args.benchmark).open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            r = json.loads(line); n += 1
            if r["table"] != "hankel_v2":
                fail(f"line {line_no}: unexpected table")
            clauses = [(tuple(b), tuple(h)) for b, h in r["prefix_clauses"] + r["continuation_clauses"]]
            if forward_chain(clauses, r["query_hyp"], r["query_goal"]) != r["gold"]:
                fail(f"line {line_no}: gold disagrees with forward chaining")
            if len(r["continuation_clauses"]) > 1:
                fail(f"line {line_no}: depth must be <= 1")
            if not r["prompt"].endswith("Answer:"):
                fail(f"line {line_no}: prompt must end at the answer position")
            key = (r["row_id"], r["col_id"])
            cells[key].add(r["renderer"])
            if key in gold and gold[key] != r["gold"]:
                fail(f"{key}: gold changed across renderers")
            gold[key] = r["gold"]
            rows[r["row_id"]] = (r["logical_class"], r["kind"],
                                 tuple(sorted(json.dumps(c) for c in r["prefix_clauses"])))
    cols = sorted({k[1] for k in cells})
    if len(cols) != 32:
        fail(f"expected 32 columns, found {len(cols)}")
    for key, rends in cells.items():
        if len(rends) != 2:
            fail(f"{key}: expected 2 renderers")
    by_class = defaultdict(dict)
    for rid, (cls, kind, ms) in rows.items():
        by_class[cls][rid] = (kind, ms, tuple(gold[(rid, c)] for c in cols))
    if len(by_class) != 8:
        fail("expected 8 classes")
    multisets = {}
    nflip = 0
    for cls, d in by_class.items():
        base = d[f"{cls}-123"]
        perms = [v for k, v in d.items() if v[0] == "perm"]
        flips = [v for k, v in d.items() if v[0] == "flip"]
        if len(perms) != 3:
            fail(f"{cls}: expected 3 permutations")
        if not flips:
            fail(f"{cls}: expected at least one flip")
        for kind, ms, g in perms:
            if ms != base[1] or g != base[2]:
                fail(f"{cls}: permutation changed multiset or gold")
        for kind, ms, g in flips:
            if g == base[2]:
                fail(f"{cls}: a flip did not change the gold row")
            if ms in multisets:
                fail(f"{cls}: flip coincides with {multisets[ms]}")
            nflip += 1
        multisets[base[1]] = cls
    if n != len(rows) * 32 * 2:
        fail(f"unexpected prompt count {n}")
    print(f"validated hankel_v2: {n} prompts, {len(rows)} rows (8 base, 24 perm, {nflip} flip), 32 columns")


if __name__ == "__main__":
    main()
