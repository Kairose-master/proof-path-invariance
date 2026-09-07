#!/usr/bin/env python3
"""Resumable Gemini runner for the RQ2d table (decision readout = generated text).

  python3 rq2/run_gemini.py --model gemini-3.1-flash-lite --budgets none 1024 --out experiments/rq2/results_d/flash_lite.jsonl

Budget "none": no thinking_config (the model emits the answer directly);
an integer: thinking_budget.  Rate-limited (free tier: 15 requests/min);
on 429 waits and retries; appends one line per (row, budget); skips rows
already present in --out; stops after --max-consecutive-failures.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

from google import genai
from google.genai import types

HERE = Path(__file__).parent


def decision(text):
    m = re.match(r"\s*\**\s*(YES|NO)\b", text or "", re.I)
    return (m.group(1).upper() if m else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", default=str(HERE / "table" / "rq2d_llm.jsonl"))
    ap.add_argument("--model", default="gemini-3.1-flash-lite")
    ap.add_argument("--budgets", nargs="+", default=["none", "1024"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--rpm", type=float, default=14.0)
    ap.add_argument("--max-consecutive-failures", type=int, default=30)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--shard", default="0/1", help="i/n: process rows i, i+n, ... (separate --out per shard)")
    ap.add_argument("--done-from", nargs="*", default=[], help="other result files whose (row, budget) pairs are skipped")
    a = ap.parse_args()
    client = genai.Client()
    rows = [json.loads(l) for l in open(a.table) if l.strip()]
    si, sn = (int(x) for x in a.shard.split("/"))
    rows = rows[si::sn]
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    for f in ([out] if out.exists() else []) + [Path(x) for x in a.done_from if Path(x).exists()]:
        for l in open(f):
            if l.strip():
                r = json.loads(l); done.add((r["row_id"], r["budget"]))
    todo = [(r, b) for r in rows for b in a.budgets if (r["row_id"], b) not in done]
    if a.limit:
        todo = todo[: a.limit]
    print(f"{len(done)} done, {len(todo)} to do", flush=True)
    fails = 0; t_last = 0.0
    with out.open("a") as f:
        for r, b in todo:
            wait = 60.0 / a.rpm - (time.time() - t_last)
            if wait > 0:
                time.sleep(wait)
            cfg = {"max_output_tokens": 8 if b == "none" else 4000, "temperature": 0}
            if b != "none":
                cfg["thinking_config"] = types.ThinkingConfig(thinking_budget=int(b))
            try:
                t_last = time.time()
                resp = client.models.generate_content(model=a.model, contents=r["prompt"], config=types.GenerateContentConfig(**cfg))
                u = resp.usage_metadata
                text = resp.text or ""
                rec = {"row_id": r["row_id"], "budget": b, "model": a.model, "case_id": r["case_id"], "condition": r["condition"],
                       "query_kind": r["query_kind"], "j": r["j"], "gold": r["gold"], "text": text[:80], "decision": decision(text),
                       "thoughts_tokens": getattr(u, "thoughts_token_count", None), "out_tokens": u.candidates_token_count}
                f.write(json.dumps(rec) + "\n"); f.flush(); fails = 0
            except Exception as e:
                msg = str(e)
                fails += 1
                m = re.search(r"retry in ([0-9.]+)s", msg, re.I)
                delay = float(m.group(1)) + 1 if m else 20.0
                print(f"error ({fails}): {msg[:160]} -> sleep {delay:.0f}s", flush=True)
                if fails >= a.max_consecutive_failures:
                    print("too many consecutive failures; stopping (resume later)", flush=True); sys.exit(2)
                time.sleep(min(delay, 300))
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
