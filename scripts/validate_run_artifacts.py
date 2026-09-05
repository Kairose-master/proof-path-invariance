#!/usr/bin/env python3
"""Validate provider-agnostic PPI run manifests and raw result JSONL.

This validator intentionally uses only the Python standard library.
It checks cross-file invariants needed for reproducible paired analysis.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


VARIANTS = {"base", "premise_reverse"}
ANSWERS = {"YES", "NO", "INVALID"}
PLACEHOLDER = "FILL-BEFORE-RUN"


def fail(msg: str) -> None:
    raise SystemExit(msg)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{path}: {exc}")


def validate_manifest(m: dict, allow_placeholders: bool) -> None:
    required = {"run_id", "benchmark", "model", "decoding", "sampling", "execution"}
    missing = required - set(m)
    if missing:
        fail(f"manifest missing fields: {sorted(missing)}")

    b = m["benchmark"]
    if b.get("name") != "symbolic_v0":
        fail("manifest benchmark.name must be symbolic_v0")
    if b.get("paired_prompts_sha256") != "63ab9a22ef8d77b22d6e9c4538cf94efa00a7f143d7ac4a23391eeb950ae9e1e":
        fail("manifest paired prompt hash does not match frozen benchmark")
    if b.get("prompt_count") != 512:
        fail("manifest prompt_count must be 512 for symbolic_v0")

    repeats = m["sampling"].get("repeats_per_prompt")
    expected = m["sampling"].get("expected_result_rows")
    if not isinstance(repeats, int) or repeats < 1:
        fail("repeats_per_prompt must be a positive integer")
    if expected != 512 * repeats:
        fail("expected_result_rows must equal 512 * repeats_per_prompt")

    if not allow_placeholders:
        serialized = json.dumps(m)
        if PLACEHOLDER in serialized:
            fail("manifest still contains FILL-BEFORE-RUN placeholders")

        for k in ("provider", "model_id", "access_date_utc"):
            if not m["model"].get(k):
                fail(f"model.{k} must be frozen before collection")
        if not m["execution"].get("runner_commit"):
            fail("execution.runner_commit must be frozen before collection")


def normalize(raw: object) -> str:
    if not isinstance(raw, str):
        return "INVALID"
    x = raw.strip().upper()
    return x if x in {"YES", "NO"} else "INVALID"


def validate_results(path: Path, manifest: dict) -> None:
    run_id = manifest["run_id"]
    repeats = manifest["sampling"]["repeats_per_prompt"]
    expected_rows = manifest["sampling"]["expected_result_rows"]

    seen = set()
    per_pair = defaultdict(set)
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
            sample = row.get("sample_index")
            if not isinstance(pid, str) or not pid:
                fail(f"line {line_no}: invalid pair_id")
            if variant not in VARIANTS:
                fail(f"line {line_no}: invalid variant")
            if not isinstance(sample, int) or not (0 <= sample < repeats):
                fail(f"line {line_no}: sample_index out of range")

            key = (pid, variant, sample)
            if key in seen:
                fail(f"line {line_no}: duplicate result key {key}")
            seen.add(key)
            per_pair[pid].add((variant, sample))

            raw = row.get("raw_text")
            normalized = row.get("normalized_answer")
            expected_norm = normalize(raw)
            if normalized != expected_norm:
                fail(f"line {line_no}: normalized_answer does not match raw_text")

            if normalized not in ANSWERS:
                fail(f"line {line_no}: invalid normalized_answer")
            if row.get("valid_format") != (normalized != "INVALID"):
                fail(f"line {line_no}: valid_format inconsistent with normalized_answer")
            if not isinstance(row.get("gold"), bool):
                fail(f"line {line_no}: gold must be boolean")

            rows += 1

    if rows != expected_rows:
        fail(f"expected {expected_rows} result rows, found {rows}")

    expected_keys = {(v, i) for v in VARIANTS for i in range(repeats)}
    for pid, keys in per_pair.items():
        if keys != expected_keys:
            fail(f"{pid}: incomplete variant/sample grid")

    if len(per_pair) != 256:
        fail(f"expected 256 pair_ids, found {len(per_pair)}")

    print(f"validated {rows} raw result rows across {len(per_pair)} pairs")


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
