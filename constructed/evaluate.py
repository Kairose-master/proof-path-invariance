#!/usr/bin/env python3
"""Evaluate a constructed recognizer on a frozen Hankel table.

Renders each prompt row of the table (hankel_v1 or hankel_v2) into the
model's token format from its `prefix_clauses`, `continuation_clauses`,
`query_hyp`, `query_goal`, and writes a raw result file in the same schema
as `scripts/run_hf_hankel.py` (renderer = "tokens"), so that
`scripts/analyze_hankel_v1.py` and `scripts/analyze_hankel_v2.py` apply
unchanged.  Only one renderer exists for a constructed model, so the
"pooled" analysis equals the per-renderer one.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).parent))
from horn_data import ATOMS, TOK, encode, encode_clauses  # noqa: E402
from models import SeqRecognizer, SetRecognizer  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--prompts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--run-id", required=True)
    a = ap.parse_args()
    ck = torch.load(a.model, map_location="cpu")
    model = SetRecognizer() if ck["kind"] == "set" else SeqRecognizer()
    model.load_state_dict(ck["state"]); model.eval()
    relabel = {x: f"A{i}" for i, x in enumerate(ATOMS)}
    seen = set(); n = 0
    with Path(a.prompts).open(encoding="utf-8") as f, Path(a.out).open("w", encoding="utf-8") as g:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            key = (r["row_id"], r["col_id"])
            if key in seen:          # the table has one row per renderer; the model has one rendering
                continue
            seen.add(key)
            clauses = [(tuple(b), tuple(h)) for b, h in r["prefix_clauses"] + r["continuation_clauses"]]
            with torch.no_grad():
                if ck["kind"] == "seq":
                    ids = torch.tensor([encode(clauses, r["query_hyp"], r["query_goal"], relabel)])
                    logits = model(ids)[0]
                else:
                    cid = torch.tensor([encode_clauses(clauses, relabel)])
                    q = torch.tensor([[TOK["?"], TOK[relabel[r["query_hyp"]]], TOK["=>"], TOK[relabel[r["query_goal"]]]]])
                    logits = model(cid, q)[0]
            out = {k: r[k] for k in ("table", "row_id", "logical_class", "col_id", "gold") if k in r}
            for k in ("serialization", "variant", "kind", "flipped_clause", "doubled_prefix"):
                if k in r:
                    out[k] = r[k]
            out.update({"run_id": a.run_id, "renderer": "tokens", "relabeling": "A0-A4", "answer_map": "logits",
                        "observation": [float(logits[1]), float(logits[0])]})   # [pos, neg]
            g.write(json.dumps(out) + "\n"); n += 1
    print(json.dumps({"rows": n, "kind": ck["kind"], "augment": ck.get("augment"), "params": ck.get("params")}))


if __name__ == "__main__":
    main()
