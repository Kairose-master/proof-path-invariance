#!/usr/bin/env python3
"""Run the Phase 3 Hankel table and record both answer logits per cell.

The observation space is R^2: for every prompt the runner stores the logit of
the positive candidate and the logit of the negative candidate as given by
the row's own answer map.  No margin is taken here; derived quantities are
computed downstream from the raw pair.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


EXPECTED_ROWS = 16384


def fail(msg: str) -> None:
    raise SystemExit(msg)


def one_token_id(tokenizer, text: str, cache: dict[str, int]) -> int:
    if text not in cache:
        ids = tokenizer(text, add_special_tokens=False)["input_ids"]
        if len(ids) != 1:
            fail(f"candidate {text!r} tokenized to {ids}; expected one token")
        cache[text] = int(ids[0])
    return cache[text]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--model-id", default="EleutherAI/pythia-70m")
    parser.add_argument("--revision", default="step143000")
    parser.add_argument("--expected-rows", type=int, default=EXPECTED_ROWS)
    args = parser.parse_args()

    tok = AutoTokenizer.from_pretrained(args.model_id, revision=args.revision)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, revision=args.revision, torch_dtype=torch.float32
    )
    model.to("cpu")
    model.eval()

    cache: dict[str, int] = {}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with Path(args.prompts).open(encoding="utf-8") as inp, out.open("x", encoding="utf-8") as f:
        with torch.inference_mode():
            for line in inp:
                if not line.strip():
                    continue
                row = json.loads(line)
                pos_id = one_token_id(tok, row["candidates"]["pos"], cache)
                neg_id = one_token_id(tok, row["candidates"]["neg"], cache)
                if pos_id == neg_id:
                    fail("positive and negative candidate ids coincide")
                enc = tok(row["prompt"], add_special_tokens=False, return_tensors="pt")
                ids = enc["input_ids"]
                logits = model(input_ids=ids).logits[0, -1].float().cpu()
                p = float(logits[pos_id].item())
                q = float(logits[neg_id].item())
                f.write(json.dumps({
                    "run_id": args.run_id,
                    "table": row["table"],
                    "row_id": row["row_id"],
                    "logical_class": row["logical_class"],
                    "serialization": row["serialization"],
                    "col_id": row["col_id"],
                    "relabeling": row["relabeling"],
                    "renderer": row["renderer"],
                    "answer_map": row["answer_map"],
                    "gold": row["gold"],
                    "pos_token_id": pos_id,
                    "neg_token_id": neg_id,
                    "observation": [p, q],
                    "prompt_token_count": int(ids.shape[1]),
                }, ensure_ascii=False) + "\n")
                count += 1

    if count != args.expected_rows:
        fail(f"expected {args.expected_rows} prompt rows, wrote {count}")

    print(json.dumps({
        "rows": count,
        "model_id": args.model_id,
        "revision": args.revision,
        "candidate_token_ids": cache,
        "observation_space": "R^2 (positive logit, negative logit)",
        "device": "cpu",
        "dtype": "float32",
    }, indent=2))


if __name__ == "__main__":
    main()
