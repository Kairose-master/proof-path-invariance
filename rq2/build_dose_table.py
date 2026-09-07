#!/usr/bin/env python3
"""RQ2f table: dose-response in clause count and in thinking budget (fresh seed cases).

Conditions on the target query t of each RQ2c case (base D, depth >= 3):
  C1 = the RQ2c C clause; C2, C3 = C1 plus the next sorted-first depth-preserving
       derivable single-atom clauses (cases lacking them are absent from C2/C3);
  N1 = one irrelevant clause x -> y: y not derivable from x, x not derivable from a,
       not a sub-clause of D (changes the meaning of (x => y), invisible from a);
  F, F1, L as in RQ2c.  Budget column: "none" (B0) or 256 (B256; ~140 thinking tokens).
Rows for B0: D, C1, C2, C3, N1, F, F1;  rows for B256: D, F, F1, C1, L.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_table import NAMES, render_clause, render_prompt  # noqa: E402
from dfc import ATOMS, closure, derivable_singles, rounds_to_derive  # noqa: E402

HERE = Path(__file__).parent


def main():
    cases = json.load(open(HERE / "table_c" / "rq2_cases.json"))["cases"]
    rows = []
    for c in cases:
        ci = int(c["case_id"][4:]); names = {x: f"{NAMES[i]}{i2:03d}" for i, x in enumerate(ATOMS) for i2 in [ci]}
        D = [(tuple(b), tuple(h)) for b, h in c["theories"]["D"]]; a, g, d = c["hyp"], c["goal"], c["depth"]["D"]
        C1 = (tuple(c["C_clause"][0]), tuple(c["C_clause"][1]))
        cands = sorted(cl for cl in derivable_singles(D) if rounds_to_derive(D + [cl], a, g) == d and cl != C1)
        conds = {"D": D, "C1": D + [C1], "F": [(tuple(b), tuple(h)) for b, h in c["theories"]["F"]],
                 "F1": [(tuple(b), tuple(h)) for b, h in c["theories"]["F1"]], "L": [(tuple(b), tuple(h)) for b, h in c["theories"]["L"]]}
        if len(cands) >= 1:
            conds["C2"] = D + [C1, cands[0]]
        if len(cands) >= 2:
            conds["C3"] = D + [C1, cands[0], cands[1]]
        reach = closure(D, [a]); present = {(b[0], y) for b, h in D if len(b) == 1 for y in h}
        N = sorted(((x,), (y,)) for x in ATOMS for y in ATOMS if x != y and y not in closure(D, [x]) and x not in reach and (x, y) not in present)
        if N:
            conds["N1"] = D + [N[0]]
            assert rounds_to_derive(conds["N1"], a, g) == d
        for cond in ("C2", "C3"):
            if cond in conds:
                assert all(closure(conds[cond], [x]) == closure(D, [x]) for x in ATOMS)
        plan = [("none", k) for k in ("D", "C1", "C2", "C3", "N1", "F", "F1") if k in conds] + [("256", k) for k in ("D", "F", "F1", "C1", "L")]
        for budget, cond in plan:
            th = conds[cond]
            stmts = [render_clause([names[x] for x in b], [names[y] for y in h]) for b, h in th]
            rows.append({"row_id": f"f_{c['case_id']}_{cond}_t", "case_id": c["case_id"], "condition": cond, "query_kind": "t", "j": 0,
                         "budget_plan": budget, "gold": "pos" if g in closure(th, [a]) else "neg", "n_clauses": len(th),
                         "prompt": render_prompt(stmts, f"{names[g]} holds, given that {names[a]} holds.")})
    out = HERE / "table_c" / "rq2f_dose.jsonl"
    with out.open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    (HERE / "table_c" / "LOCK_rq2f_dose").write_text(f"rq2f_dose.jsonl sha256 {sha} rows {len(rows)}\n")
    from collections import Counter
    print(json.dumps({"rows": len(rows), "sha256": sha, "by_condition_budget": {f"{b}:{c}": n for (b, c), n in Counter((r["budget_plan"], r["condition"]) for r in rows).items()}}))


if __name__ == "__main__":
    main()
