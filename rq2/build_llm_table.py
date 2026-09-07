#!/usr/bin/env python3
"""RQ2d table for a language model with a thinking budget.

Rows (all from the frozen RQ2 tables, seed 20260906):
  part A: rq2_prompts.jsonl rows with query_kind in {t, n}   (200 x 5 conditions x 2 = 2000)
  part B: rq2b_presat.jsonl rows with j in {1, 2}, rendered with a multi-atom
          hypothesis ("given that p, q and r hold")             (200 x 2 x 2 = 800)
Each row is run at every budget in BUDGETS.  Priority order for a
rate-limited run: A-t, A-n, B.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_table import NAMES, render_clause, render_prompt  # noqa: E402
from dfc import ATOMS  # noqa: E402

HERE = Path(__file__).parent


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--table-dir", default=str(HERE / "table"))
    ap.add_argument("--presat", default="rq2b_presat.jsonl")
    ap.add_argument("--out", default="rq2d_llm.jsonl")
    a = ap.parse_args()
    tdir = Path(a.table_dir)
    rows = []
    for l in open(tdir / "rq2_prompts.jsonl"):
        r = json.loads(l)
        if r["query_kind"] in ("t", "n"):
            rows.append({"part": "A", "priority": 0 if r["query_kind"] == "t" else 1, "case_id": r["case_id"], "condition": r["condition"],
                         "query_kind": r["query_kind"], "j": 0, "gold": r["gold"], "depth": r["depth"], "prompt": r["prompt"]})
    for l in open(tdir / a.presat):
        r = json.loads(l)
        if r["j"] == 0:
            continue
        ci = int(r["case_id"][4:])
        names = {x: f"{NAMES[i]}{ci:03d}" for i, x in enumerate(ATOMS)}
        stmts = [render_clause([names[x] for x in b], [names[y] for y in h]) for b, h in r["clauses"]]
        hs = [names[h] for h in r["hyps"]]
        given = hs[0] if len(hs) == 1 else ", ".join(hs[:-1]) + " and " + hs[-1]
        rows.append({"part": "B", "priority": 2, "case_id": r["case_id"], "condition": "D", "query_kind": r["query_kind"], "j": r["j"],
                     "gold": r["gold"], "depth": r["depth_from_H"], "hyps": r["hyps"],
                     "prompt": render_prompt(stmts, f"{names[r['goal']]} holds, given that {given} hold.")})
    rows.sort(key=lambda r: (r["priority"], r["case_id"]))
    for i, r in enumerate(rows):
        r["row_id"] = f"{r['part']}_{r['case_id']}_{r['condition']}_{r['query_kind']}_j{r['j']}"
    out = tdir / a.out
    with out.open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    (tdir / f"LOCK_{out.stem}").write_text(f"{out.name} sha256 {sha} rows {len(rows)}\n")
    print(json.dumps({"rows": len(rows), "sha256": sha}))


if __name__ == "__main__":
    main()
