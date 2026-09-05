#!/usr/bin/env python3
"""Conservative structural validation for PPI case files.

This is not a substitute for Lean. It rejects malformed empirical records and
requires each record to point to an allow-listed Lean certificate family.
CI separately runs `lake build` to check the proofs themselves.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ALLOWED = {
    ("PPI/Transitivity.lean", "PPI.direct₂ / PPI.factored₂", "implication_transitivity"),
    ("PPI/Controls.lean", "PPI.negativeCountermodel / PPI.negativeCountermodelWithExtra", "non_entailment_countermodel"),
}


def fail(case_id: str, message: str) -> None:
    raise SystemExit(f"{case_id}: {message}")


def validate(path: Path, seen: set[str]) -> int:
    count = 0
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            case = json.loads(line)
            cid = case.get("case_id", f"{path}:line-{line_no}")
            if cid in seen:
                fail(cid, "duplicate case_id across benchmark")
            seen.add(cid)

            cert = case.get("certificate", {})
            key = (cert.get("lean_file"), cert.get("theorem"), cert.get("family"))
            if key not in ALLOWED:
                fail(cid, f"certificate is not allow-listed: {key}")

            if not isinstance(case.get("gold"), bool):
                fail(cid, "gold must be boolean")

            conditions = case.get("conditions", {})
            if set(conditions) != {"D", "F", "C"}:
                fail(cid, "conditions must be exactly D, F, C")

            queries = {conditions[k].get("query") for k in ("D", "F", "C")}
            if len(queries) != 1:
                fail(cid, "target query must be identical across D/F/C")

            d_n = len(conditions["D"].get("statements", []))
            f_n = len(conditions["F"].get("statements", []))
            c_n = len(conditions["C"].get("statements", []))
            if f_n <= d_n:
                fail(cid, "F must expose at least one additional statement")
            if c_n != f_n:
                fail(cid, "C and F must have the same statement count in benchmark v0")

            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", default=[
        "experiments/cases/transitivity_v0.jsonl",
        "experiments/cases/negative_v0.jsonl",
    ])
    args = parser.parse_args()

    seen: set[str] = set()
    count = sum(validate(Path(p), seen) for p in args.paths)
    print(f"validated {count} case(s) across {len(args.paths)} file(s); Lean checked separately")


if __name__ == "__main__":
    main()
