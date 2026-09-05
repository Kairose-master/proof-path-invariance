#!/usr/bin/env python3
"""Validate the frozen PPI logit-margin run manifest and raw results.

Only Python standard library is used. The confirmatory v0 contract is narrow:
Pythia-70M step143000, CPU float32, one deterministic next-token forward pass
per frozen prompt, comparing exactly the single-token candidates " YES" and
" NO".
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path


VARIANTS = {"base", "premise_reverse"}
PREDICTIONS = {"YES", "NO", "TIE"}
PLACEHOLDER = "FILL-BEFORE-RUN"


def fail(msg: str) -> None:
    raise SystemExit(msg)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{path}: {exc}")


def validate_manifest(m: dict, allow_placeholders: bool) -> None:
    required = {"run_id", "benchmark", "model", "measurement", "execution"}
    missing = required - set(m)
    if missing:
        fail(f"manifest missing fields: {sorted(missing)}")

    b = m["benchmark"]
    if b.get("name") != "symbolic_v0":
        fail("benchmark.name must be symbolic_v0")
    lock_path = Path(b.get("lock_file", ""))
    if not lock_path.is_file():
        fail(f"benchmark lock file not found: {lock_path}")
    lock = load_json(lock_path)
    expected_hash = lock.get("sha256", {}).get("paired_prompts_jsonl")
    if b.get("paired_prompts_sha256") != expected_hash:
        fail("paired prompt hash does not match benchmark lock file")
    if b.get("prompt_count") != 512:
        fail("prompt_count must be 512")

    model = m["model"]
    if model.get("provider") != "huggingface-local":
        fail("confirmatory v0 provider must be huggingface-local")
    if model.get("model_id") != "EleutherAI/pythia-70m":
        fail("confirmatory v0 model_id must be EleutherAI/pythia-70m")
    if model.get("revision") != "step143000":
        fail("confirmatory v0 revision must be step143000")
    if model.get("interface") != "transformers.AutoModelForCausalLM":
        fail("unexpected model interface")

    measurement = m["measurement"]
    expected_measurement = {
        "mode": "next_token_logit_margin",
        "yes_candidate": " YES",
        "no_candidate": " NO",
        "require_single_token_candidates": True,
        "repeats_per_prompt": 1,
    }
    for key, value in expected_measurement.items():
        if measurement.get(key) != value:
            fail(f"measurement.{key} must be {value!r}")

    execution = m["execution"]
    if execution.get("device") != "cpu":
        fail("confirmatory v0 device must be cpu")
    if execution.get("dtype") != "float32":
        fail("confirmatory v0 dtype must be float32")

    if not allow_placeholders:
        if PLACEHOLDER in json.dumps(m):
            fail("manifest still contains FILL-BEFORE-RUN placeholders")
        if not model.get("access_date_utc"):
            fail("model.access_date_utc must be recorded")
        if not execution.get("runner_commit"):
            fail("execution.runner_commit must be recorded")


def expected_prediction(margin: float) -> str:
    if margin > 0:
        return "YES"
    if margin < 0:
        return "NO"
    return "TIE"


def validate_results(path: Path, manifest: dict) -> None:
    run_id = manifest["run_id"]
    seen = set()
    per_pair = defaultdict(set)
    yes_token_id = None
    no_token_id = None
    rows = 0

    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                fail(f"{path}:{line_no}: invalid JSON: {exc}")

            if row.get("run_id") != run_id:
                fail(f"line {line_no}: run_id mismatch")

            pid = row.get("pair_id")
            variant = row.get("variant")
            if not isinstance(pid, str) or not pid:
                fail(f"line {line_no}: invalid pair_id")
            if variant not in VARIANTS:
                fail(f"line {line_no}: invalid variant")

            key = (pid, variant)
            if key in seen:
                fail(f"line {line_no}: duplicate result key {key}")
            seen.add(key)
            per_pair[pid].add(variant)

            if not isinstance(row.get("gold"), bool):
                fail(f"line {line_no}: gold must be boolean")

            yid = row.get("yes_token_id")
            nid = row.get("no_token_id")
            if not isinstance(yid, int) or not isinstance(nid, int) or yid < 0 or nid < 0:
                fail(f"line {line_no}: token ids must be nonnegative integers")
            if yid == nid:
                fail(f"line {line_no}: YES and NO token ids are identical")

            if yes_token_id is None:
                yes_token_id, no_token_id = yid, nid
            elif (yid, nid) != (yes_token_id, no_token_id):
                fail(f"line {line_no}: candidate token ids changed within run")

            try:
                yes_logit = float(row["yes_logit"])
                no_logit = float(row["no_logit"])
                margin = float(row["margin"])
            except (KeyError, TypeError, ValueError):
                fail(f"line {line_no}: logits and margin must be numeric")

            if not all(math.isfinite(x) for x in (yes_logit, no_logit, margin)):
                fail(f"line {line_no}: non-finite logit or margin")
            if abs((yes_logit - no_logit) - margin) > 1e-6:
                fail(f"line {line_no}: margin != yes_logit - no_logit")

            prediction = row.get("predicted_answer")
            if prediction not in PREDICTIONS:
                fail(f"line {line_no}: invalid predicted_answer")
            if prediction != expected_prediction(margin):
                fail(f"line {line_no}: predicted_answer inconsistent with margin sign")

            token_count = row.get("prompt_token_count")
            if not isinstance(token_count, int) or token_count < 1:
                fail(f"line {line_no}: invalid prompt_token_count")

            rows += 1

    if rows != 512:
        fail(f"expected 512 result rows, found {rows}")
    if len(per_pair) != 256:
        fail(f"expected 256 pair_ids, found {len(per_pair)}")
    for pid, variants in per_pair.items():
        if variants != VARIANTS:
            fail(f"{pid}: incomplete variant pair")

    print(
        f"validated {rows} logit rows across {len(per_pair)} pairs; "
        f"YES token={yes_token_id}, NO token={no_token_id}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    parser.add_argument("--results")
    parser.add_argument("--allow-placeholders", action="store_true")
    args = parser.parse_args()

    manifest = load_json(Path(args.manifest))
    validate_manifest(manifest, args.allow_placeholders)

    if args.results:
        validate_results(Path(args.results), manifest)
    else:
        print("manifest validated")


if __name__ == "__main__":
    main()
