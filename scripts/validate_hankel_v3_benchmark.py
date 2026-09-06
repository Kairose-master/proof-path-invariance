#!/usr/bin/env python3
"""Validate `hankel_v3`: structure, gold re-derivation, every red row's added
clause is derivable from the base and its gold row equals the base's, every
flip changes the gold row, perms keep multiset and gold."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def fail(msg):
    raise SystemExit(msg)


def closure(theory, facts):
    known = set(facts); changed = True
    while changed:
        changed = False
        for b, h in theory:
            if set(b) <= known and not set(h) <= known:
                known |= set(h); changed = True
    return known


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("benchmark"); a = ap.parse_args()
    gold, rows, cells = {}, {}, defaultdict(set); n = 0
    with Path(a.benchmark).open(encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            if not line.strip():
                continue
            r = json.loads(line); n += 1
            if r["table"] != "hankel_v3":
                fail(f"line {ln}: table")
            cl = [(tuple(b), tuple(h)) for b, h in r["prefix_clauses"] + r["continuation_clauses"]]
            if (r["query_goal"] in closure(cl, [r["query_hyp"]])) != r["gold"]:
                fail(f"line {ln}: gold mismatch")
            if not r["prompt"].endswith("Answer:"):
                fail(f"line {ln}: prompt end")
            key = (r["row_id"], r["col_id"]); cells[key].add(r["renderer"])
            if key in gold and gold[key] != r["gold"]:
                fail(f"{key}: gold across renderers")
            gold[key] = r["gold"]
            rows[r["row_id"]] = (r["logical_class"], r["kind"], [(tuple(b), tuple(h)) for b, h in r["prefix_clauses"]],
                                 r["added_clause"])
    cols = sorted({k[1] for k in cells})
    if len(cols) != 32:
        fail("columns")
    if any(len(v) != 2 for v in cells.values()):
        fail("renderers")
    by = defaultdict(dict)
    for rid, v in rows.items():
        by[v[0]][rid] = v
    if len(by) != 8:
        fail("classes")
    nred = nflip = 0
    for cls, d in by.items():
        base = d[f"{cls}-123"]; bg = tuple(gold[(f"{cls}-123", c)] for c in cols)
        bms = sorted(base[2])
        for rid, (c_, kind, prefix, added) in d.items():
            g = tuple(gold[(rid, c)] for c in cols)
            if kind == "perm":
                if sorted(prefix) != bms or g != bg:
                    fail(f"{rid}: perm changed multiset or gold")
            elif kind == "red":
                if prefix[:-1] != base[2] or [list(prefix[-1][0]), list(prefix[-1][1])] != added:
                    fail(f"{rid}: red must be base plus the added clause")
                (bx,), (hy,) = prefix[-1]
                if hy not in closure(base[2], [bx]):
                    fail(f"{rid}: added clause not derivable")
                if prefix[-1] in base[2] or g != bg:
                    fail(f"{rid}: red changed gold or duplicates a clause")
                nred += 1
            elif kind == "flip":
                if g == bg:
                    fail(f"{rid}: flip did not change gold")
                nflip += 1
        if sum(1 for v in d.values() if v[1] == "red") < 1:
            fail(f"{cls}: needs at least one red row")
    if n != len(rows) * 32 * 2:
        fail("count")
    print(f"validated hankel_v3: {n} prompts, {len(rows)} rows (8 base, 24 perm, {nred} red, {nflip} flip), 32 columns")


if __name__ == "__main__":
    main()
