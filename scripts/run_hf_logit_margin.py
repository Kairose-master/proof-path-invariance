#!/usr/bin/env python3
"""Run the frozen symbolic benchmark on a local Hugging Face causal LM.

Primary measurement:
    margin(x) = logit(" YES" | x) - logit(" NO" | x)

The runner refuses to continue unless each candidate is exactly one tokenizer
token. This keeps Phase 1 at the next-token level and avoids sequence-length
normalization choices.

No text is generated.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer


def fail(msg: str) -> None:
    raise SystemExit(msg)


def load_prompts(path: Path):
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                fail(f"{path}:{line_no}: invalid JSON: {exc}")


def one_token_id(tokenizer, text: str) -> int:
    ids = tokenizer(text, add_special_tokens=False)["input_ids"]
    if len(ids) != 1:
        fail(
            f"candidate {text!r} tokenized to {ids}; "
            "Phase 1 requires exactly one token per candidate"
        )
    return int(ids[0])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--model-id", default="EleutherAI/pythia-70m")
    parser.add_argument("--revision", default="step143000")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--yes-candidate", default=" YES")
    parser.add_argument("--no-candidate", default=" NO")
    args = parser.parse_args()

    if args.device != "cpu":
        fail("confirmatory v0 is frozen to --device cpu")

    tokenizer = AutoTokenizer.from_pretrained(
        args.model_id,
        revision=args.revision,
    )
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id,
        revision=args.revision,
        torch_dtype=torch.float32,
    )
    model.to(args.device)
    model.eval()

    yes_id = one_token_id(tokenizer, args.yes_candidate)
    no_id = one_token_id(tokenizer, args.no_candidate)
    if yes_id == no_id:
        fail("YES and NO candidates resolved to the same token id")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with out.open("x", encoding="utf-8") as f:
        with torch.inference_mode():
            for row in load_prompts(Path(args.prompts)):
                prompt = row["prompt"]
                encoded = tokenizer(
                    prompt,
                    add_special_tokens=False,
                    return_tensors="pt",
                )
                input_ids = encoded["input_ids"].to(args.device)
                if input_ids.shape[1] < 1:
                    fail(f"{row['pair_id']}: empty tokenized prompt")

                outputs = model(input_ids=input_ids)
                next_logits = outputs.logits[0, -1].float().cpu()
                yes_logit = float(next_logits[yes_id].item())
                no_logit = float(next_logits[no_id].item())
                margin = yes_logit - no_logit

                if margin > 0:
                    prediction = "YES"
                elif margin < 0:
                    prediction = "NO"
                else:
                    prediction = "TIE"

                result = {
                    "run_id": args.run_id,
                    "pair_id": row["pair_id"],
                    "variant": row["variant"],
                    "gold": row["gold"],
                    "yes_token_id": yes_id,
                    "no_token_id": no_id,
                    "yes_logit": yes_logit,
                    "no_logit": no_logit,
                    "margin": margin,
                    "predicted_answer": prediction,
                    "prompt_token_count": int(input_ids.shape[1]),
                }
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
                count += 1

    if count != 512:
        fail(f"expected 512 prompt rows, wrote {count}")

    print(json.dumps({
        "rows": count,
        "model_id": args.model_id,
        "revision": args.revision,
        "yes_candidate": args.yes_candidate,
        "yes_token_id": yes_id,
        "no_candidate": args.no_candidate,
        "no_token_id": no_id,
        "torch_version": torch.__version__,
        "transformers_version": transformers.__version__,
        "device": args.device,
        "dtype": "float32",
    }, indent=2))


if __name__ == "__main__":
    main()
