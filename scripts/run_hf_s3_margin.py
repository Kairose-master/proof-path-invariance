#!/usr/bin/env python3
"""Run Phase 2 S3 benchmark with Pythia-70M next-token logit margins."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def fail(msg: str) -> None:
    raise SystemExit(msg)


def one_token_id(tokenizer, text: str) -> int:
    ids = tokenizer(text, add_special_tokens=False)["input_ids"]
    if len(ids) != 1:
        fail(f"candidate {text!r} tokenized to {ids}; expected one token")
    return int(ids[0])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--model-id", default="EleutherAI/pythia-70m")
    parser.add_argument("--revision", default="step143000")
    args = parser.parse_args()

    tok = AutoTokenizer.from_pretrained(args.model_id, revision=args.revision)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, revision=args.revision, torch_dtype=torch.float32
    )
    model.to("cpu")
    model.eval()

    yes_id = one_token_id(tok, " YES")
    no_id = one_token_id(tok, " NO")
    if yes_id == no_id:
        fail("YES and NO token ids are identical")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with Path(args.prompts).open(encoding="utf-8") as inp, out.open("x", encoding="utf-8") as f:
        with torch.inference_mode():
            for line_no, line in enumerate(inp, 1):
                if not line.strip():
                    continue
                row = json.loads(line)
                enc = tok(row["prompt"], add_special_tokens=False, return_tensors="pt")
                ids = enc["input_ids"]
                logits = model(input_ids=ids).logits[0, -1].float().cpu()
                y = float(logits[yes_id].item())
                n = float(logits[no_id].item())
                margin = y - n
                pred = "YES" if margin > 0 else "NO" if margin < 0 else "TIE"

                result = {
                    "run_id": args.run_id,
                    "case_id": row["case_id"],
                    "family": row["family"],
                    "gold": row["gold"],
                    "permutation": row["permutation"],
                    "yes_token_id": yes_id,
                    "no_token_id": no_id,
                    "yes_logit": y,
                    "no_logit": n,
                    "margin": margin,
                    "predicted_answer": pred,
                    "prompt_token_count": int(ids.shape[1]),
                }
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
                count += 1

    if count != 768:
        fail(f"expected 768 prompt rows, wrote {count}")

    print(json.dumps({
        "rows": count,
        "model_id": args.model_id,
        "revision": args.revision,
        "yes_token_id": yes_id,
        "no_token_id": no_id,
        "device": "cpu",
        "dtype": "float32",
    }, indent=2))


if __name__ == "__main__":
    main()
