#!/usr/bin/env python3
"""Conservative structural validation for PPI case files.

This is not a substitute for Lean. It rejects malformed empirical records and
requires each record to point to the currently allow-listed Lean certificate
families. The CI separately runs `lake build` to check those proofs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ALLOWED = {
    ("PPI/Transitivity.lean", "PPI.direct₂ / PPI.factored₂", "implication_transitivity"),
}


def fail(case_id: str, message: str) -> None:
    raise SystemExit(f"{case_id}: {message}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="experiments/cases/transitivity_v0.jsonl")
    args = parser.parse_args()

    seen = set()
    count = 0
    with Path(args.path).open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            case = json.loads(line)
            cid = case.get("case_id", f"line-{line_no}")
            if cid in seen:
                fail(cid, "duplicate case_id")
            seen.add(cid)

            cert = case.get("certificate", {})
            key = (cert.get("lean_file"), cert.get("theorem"), cert.get("family"))
            if key not in ALLOWED:
                fail(cid, f"certificate is not allow-listed: {key}")

            conditions = case.get("conditions", {})
            if set(conditions) != {"D", "F", "C"}:
                fail(cid, "conditions must be exactly D, F, C")

            queries = {conditions[k].get("query") for k in ("D", "F", "C")}
            if len(queries) != 1:
                fail(cid, "target query must be identical across D/F/C")

            if len(conditions["D"].get("statements", [])) >= len(conditions["F"].get("statements", [])):
                fail(cid, "F must expose at least one additional intermediate statement")

            count += 1

    print(f"validated {count} case(s); Lean certificates are checked separately by lake build")


if __name__ == "__main__":
    main()
