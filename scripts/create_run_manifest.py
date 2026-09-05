#!/usr/bin/env python3
"""Create a run-specific manifest from the frozen template and live environment."""

from __future__ import annotations

import argparse
import json
import subprocess
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import torch
import transformers
from huggingface_hub import HfApi


def git_last_commit(path: str) -> str:
    return subprocess.check_output(
        ["git", "log", "-1", "--format=%H", "--", path],
        text=True,
    ).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--template",
        default="experiments/runs/manifest.template.json",
    )
    parser.add_argument(
        "--out",
        default="results/pythia70m-step143000-symbolic-v0.manifest.json",
    )
    args = parser.parse_args()

    template = json.loads(Path(args.template).read_text(encoding="utf-8"))
    manifest = deepcopy(template)

    model_id = manifest["model"]["model_id"]
    revision = manifest["model"]["revision"]
    resolved = HfApi().model_info(model_id, revision=revision).sha

    manifest["model"]["resolved_commit"] = resolved
    manifest["model"]["access_date_utc"] = datetime.now(timezone.utc).isoformat()

    manifest["execution"]["runner_commit"] = git_last_commit(
        "scripts/run_hf_logit_margin.py"
    )
    manifest["execution"]["torch_version"] = torch.__version__
    manifest["execution"]["transformers_version"] = transformers.__version__

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        raise SystemExit(f"refusing to overwrite existing manifest: {out}")
    out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "manifest": str(out),
        "resolved_commit": resolved,
        "runner_commit": manifest["execution"]["runner_commit"],
        "torch_version": torch.__version__,
        "transformers_version": transformers.__version__,
        "access_date_utc": manifest["model"]["access_date_utc"],
    }, indent=2))


if __name__ == "__main__":
    main()
