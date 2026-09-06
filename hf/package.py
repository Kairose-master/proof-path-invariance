#!/usr/bin/env python3
"""Package the constructed recognizers and the frozen Hankel tables for the
Hugging Face Hub, and optionally upload them.

  python3 hf/package.py --weights-dir <dir with set.pt seq_aug.pt seq_fixed.pt> \
      --eval-dir <dir with <tag>_v{1,2,3}_summary.json> --out hf/build
  python3 hf/package.py ... --upload            # needs HF_TOKEN with write role

Model repo   : jinu0633/recognition-paths-recognizers   (folders set/, seq_aug/, seq_fixed/)
Dataset repo : jinu0633/hankel-tables                   (tables, locks, raw runs, summaries)

Model cards are generated from the summary JSON files; no number is typed
by hand.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

import torch
from safetensors.torch import save_file

ROOT = Path(__file__).resolve().parent.parent
MODEL_REPO = "jinu0633/recognition-paths-recognizers"
DATA_REPO = "jinu0633/hankel-tables"
TAGS = ["set", "seq_aug", "seq_fixed"]
DESC = {
    "set": "clause encoder + max-pool + query encoder; permutation- and repetition-invariant by architecture",
    "seq_aug": "causal transformer over the token sequence, trained with permutation/repetition augmentation",
    "seq_fixed": "causal transformer over the token sequence, trained on fixed-order traces only",
}


def summary_numbers(eval_dir: Path, tag: str) -> dict:
    out = {}
    v1 = json.loads((eval_dir / f"{tag}_v1_summary.json").read_text())["per_renderer"]["tokens"]
    v2 = json.loads((eval_dir / f"{tag}_v2_summary.json").read_text())["per_renderer"]["tokens"]
    v3 = json.loads((eval_dir / f"{tag}_v3_summary.json").read_text())["per_renderer"]["tokens"]
    out["v1_comparative_accuracy"] = v1["D_readout"]["comparative_accuracy"]
    out["v1_gate_I_ratio"] = v1["B_separation"]["ratio_within_median_over_between_median"]
    out["v1_identical_classes"] = f'{v1["A_invariance"]["classes_with_identical_profiles"]}/8'
    out["v1_distinct_rows"] = f'{v1["C_collapse"]["distinct_row_profiles"]}/40'
    out["v1_depth1_closed"] = v1["E_closure"]["closed"]
    out["v2_S"] = v2["S_median_ratio_perm_over_flip"]
    out["v2_classes_perm_closer"] = f'{v2["classes_with_perm_closer_than_flip"]}/8'
    out["v3_T"] = v3["T_median_red_over_flip"]
    out["v3_U"] = v3["U_median_swap_over_flip"]
    out["v3_V"] = v3["V_median_free_red_over_flip"]
    out["v3_E_base_red"] = f'{v3["identical_base_red_pairs"]}/{v3["base_red_pairs"]}'
    out["v3_E_swap"] = f'{v3["identical_swap_pairs"]}/{v3["swap_pairs"]}'
    return out


def model_card(tag: str, ck: dict, nums: dict) -> str:
    rows = "\n".join(f"| `{k}` | {v if not isinstance(v, float) else f'{v:.3f}'} |" for k, v in nums.items())
    return f"""---
license: mit
tags: [recognition-paths, horn-logic, permutation-invariance, logical-invariance]
---

# `{tag}` — a constructed recognizer for Horn entailment

Part of `{MODEL_REPO}`. {DESC[tag]}. Parameters: {ck['params']}. Trained
{ck['steps']} steps of batch 128 on synthetic Horn traces (2–4 clauses, five
atoms, random relabelling, balanced labels), seed {ck['seed']}, with the eight
evaluation classes of the Hankel tables held out up to atom relabelling.
Final validation accuracy {ck['log'][-1]['val_acc']:.3f}.

This is **not a language model**. It is a task-specific recognizer built to
satisfy, or to fail, the specifications in
`RecognitionPaths/Specification.lean` (repository `recognition-paths`):
a theory-factoring recognizer is invariant under permutation and repetition
of clauses by construction; the ideal recognizer is invariant under all
logically identical rewrites.

## Evaluation on the frozen tables (`{DATA_REPO}`)

| statistic | value |
|---|---|
{rows}

`S` compares permutations with single-arrow flips (`hankel_v2`); `T`, `U`,
`V` compare derivable-clause extensions with flips (`hankel_v3`), `V` on
columns where accuracy imposes nothing; `E` counts exactly identical
profiles. See `docs/PHASE3_HANKEL_V2_DESIGN.md`, `docs/PHASE3_HANKEL_V3_DESIGN.md`,
`docs/PHASE4_CONSTRUCTED_DESIGN.md` in `proof-path-invariance`.

## Loading

```python
import torch, sys
sys.path.insert(0, "code")           # models.py and horn_data.py are in this folder
from models import SetRecognizer, SeqRecognizer
from safetensors.torch import load_file
cfg = json.load(open("config.json"))
model = SetRecognizer() if cfg["kind"] == "set" else SeqRecognizer()
model.load_state_dict(load_file("model.safetensors")); model.eval()
```

Inputs are token ids over the vocabulary in `horn_data.VOCAB`; see
`constructed/evaluate.py` in `proof-path-invariance` for rendering a Hankel
table row.
"""


def build(weights_dir: Path, eval_dir: Path, out: Path) -> None:
    if out.exists():
        shutil.rmtree(out)
    mroot = out / "models"; droot = out / "dataset"
    for tag in TAGS:
        d = mroot / tag; d.mkdir(parents=True)
        ck = torch.load(weights_dir / f"{tag}.pt", map_location="cpu")
        save_file({k: v.contiguous() for k, v in ck["state"].items()}, str(d / "model.safetensors"))
        (d / "config.json").write_text(json.dumps({k: ck[k] for k in ("kind", "augment", "params", "seed", "steps")}, indent=2))
        (d / "training_log.json").write_text(json.dumps(ck["log"], indent=1))
        (d / "code").mkdir()
        for f in ("models.py", "horn_data.py"):
            shutil.copy(ROOT / "constructed" / f, d / "code" / f)
        (d / "README.md").write_text(model_card(tag, ck, summary_numbers(eval_dir, tag)))
        for v in ("v1", "v2", "v3"):
            shutil.copy(eval_dir / f"{tag}_{v}_summary.json", d / f"eval_hankel_{v}_summary.json")
    (mroot / "README.md").write_text(f"""---
license: mit
---
# Recognition-paths constructed recognizers

Three small recognizers for Horn entailment, trained on the same synthetic
distribution and evaluated on the same frozen Hankel tables
(`{DATA_REPO}`): `set/` (invariance by architecture), `seq_aug/`
(invariance by data augmentation), `seq_fixed/` (neither). Each folder has
its own model card with the evaluation numbers. Source and theory:
github.com/Kairose-master/proof-path-invariance and
github.com/Kairose-master/recognition-paths.
""")
    droot.mkdir(parents=True)
    (droot / "tables").mkdir()
    for v, gen in (("v0", "generate_hankel_benchmark.py"), ("v1", "generate_hankel_v1_benchmark.py"),
                   ("v2", "generate_hankel_v2_benchmark.py"), ("v3", "generate_hankel_v3_benchmark.py")):
        subprocess.run(["python3", str(ROOT / "scripts" / gen), "--out", str(droot / "tables" / f"hankel_{v}.jsonl")],
                       check=True, cwd=ROOT, capture_output=True)
        shutil.copy(ROOT / "experiments" / f"hankel_{v}.lock.json", droot / "tables" / f"hankel_{v}.lock.json")
    (droot / "runs").mkdir(); (droot / "results").mkdir()
    for f in (ROOT / "experiments" / "runs").glob("hankel_*"):
        shutil.copy(f, droot / "runs" / f.name)
    for f in (ROOT / "experiments" / "results").glob("phase3*"):
        shutil.copy(f, droot / "results" / f.name)
    for f in (ROOT / "docs").glob("PHASE3_HANKEL*"):
        shutil.copy(f, droot / f.name)
    (droot / "README.md").write_text(f"""---
license: cc-by-4.0
---
# Hankel tables for recognition-path experiments

Frozen observation tables of Horn premise traces against continuation-query
tests, with SHA-256 lock files, raw runs of several recognizers (answer
logit pairs), and summary statistics. Rows inside a logical class are
Lean-certified logically identical (`recognition-paths`). Designs and frozen
analysis plans are the `PHASE3_HANKEL*` documents. Every raw run file is
gzip-compressed JSONL with one row per prompt: `row_id`, `col_id`,
`renderer`, `gold`, `observation = [positive logit, negative logit]`.
Source: github.com/Kairose-master/proof-path-invariance.
""")
    print(f"built {out}")


def upload(out: Path, private: bool) -> None:
    from huggingface_hub import HfApi
    api = HfApi()
    api.create_repo(MODEL_REPO, repo_type="model", private=private, exist_ok=True)
    api.upload_folder(folder_path=str(out / "models"), repo_id=MODEL_REPO, repo_type="model")
    api.create_repo(DATA_REPO, repo_type="dataset", private=private, exist_ok=True)
    api.upload_folder(folder_path=str(out / "dataset"), repo_id=DATA_REPO, repo_type="dataset")
    print(f"uploaded to https://huggingface.co/{MODEL_REPO} and https://huggingface.co/datasets/{DATA_REPO}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights-dir", default="experiments/constructed")
    ap.add_argument("--eval-dir", default="experiments/results/constructed")
    ap.add_argument("--out", default="hf/build")
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--private", action="store_true")
    a = ap.parse_args()
    build(Path(a.weights_dir), Path(a.eval_dir), Path(a.out))
    if a.upload:
        upload(Path(a.out), a.private)


if __name__ == "__main__":
    main()
