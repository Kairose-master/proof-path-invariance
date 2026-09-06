#!/usr/bin/env python3
"""RQ2b table: pre-saturated hypothesis sets for the composition law.

For each RQ2 base theory D (200 cases, target (a, goal) of depth >= 3) and
each j in {0, 1, 2}, the hypothesis set H_j = T_j({a}) (atoms known after j
rounds from a), for the target goal and for the non-derivable atom n of the
RQ2 table.  The composition law T_k ∘ T_j = T_{j+k} predicts, for the
budgeted recognizer, decision(H_j, goal; k) = decision(H_0, goal; j + k).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dfc import rounds_to_derive  # noqa: E402

HERE = Path(__file__).parent


def t_rounds(clauses, facts, j):
    known = set(facts)
    for _ in range(j):
        new = set(known)
        for body, head in clauses:
            if all(x in known for x in body):
                new |= set(head)
        known = new
    return sorted(known)


def main():
    cases = json.load(open(HERE / "table" / "rq2_cases.json"))["cases"]
    rows = []
    for c in cases:
        D = [(tuple(b), tuple(h)) for b, h in c["theories"]["D"]]
        a = c["hyp"]
        for qk in ("t", "n"):
            _, goal = c["queries"][qk]
            for j in (0, 1, 2):
                H = t_rounds(D, [a], j)
                rows.append({"table": "rq2b", "case_id": c["case_id"], "query_kind": qk, "j": j,
                             "hyps": H, "goal": goal, "clauses": c["theories"]["D"],
                             "gold": "pos" if goal in t_rounds(D, [a], 20) else "neg",
                             "depth_from_a": rounds_to_derive(D, a, goal),
                             "depth_from_H": min((rounds_to_derive(D, h, goal) for h in H if rounds_to_derive(D, h, goal) is not None), default=None) if goal not in H else 0})
    out = HERE / "table" / "rq2b_presat.jsonl"
    with out.open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    (HERE / "table" / "LOCK_rq2b").write_text(f"rq2b_presat.jsonl sha256 {sha} rows {len(rows)}\n")
    from collections import Counter
    print(json.dumps({"rows": len(rows), "sha256": sha,
                      "H_size_by_j": {j: dict(Counter(len(r["hyps"]) for r in rows if r["j"] == j and r["query_kind"] == "t")) for j in (0, 1, 2)},
                      "gold_t": dict(Counter(r["gold"] for r in rows if r["query_kind"] == "t")),
                      "gold_n": dict(Counter(r["gold"] for r in rows if r["query_kind"] == "n"))}))


if __name__ == "__main__":
    main()
