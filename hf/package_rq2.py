#!/usr/bin/env python3
"""Package the RQ2 constructed recognizers (7 atoms) for the Hugging Face model
repo `jinu0633/recognition-paths-recognizers`, folder `rq2/`.

  python3 hf/package_rq2.py --out hf/build_rq2 [--upload]
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import torch
from safetensors.torch import save_file

ROOT = Path(__file__).resolve().parent.parent
MODEL_REPO = "jinu0633/recognition-paths-recognizers"
W = ROOT / "experiments" / "rq2"

DESC = {
    "iter_r4": "iterative learned reasoner (atom-state message passing, GRU update, max aggregation), trained with a budget of 4 rounds; the RQ2 primary model",
    "iter_r2": "the same architecture trained with a budget of 2 rounds; RQ2 secondary (S5) and the model that satisfies the RQ2b composition law",
    "set7": "clause encoder + max-pool + query encoder over seven atoms; permutation- and repetition-invariant by architecture",
}

RQ2 = {
    "iter_r4": {"acc_D(k=4)": 1.000, "delta(k=2)": "0.89 [0.84, 0.93]", "delta(k=4)": "0.00", "interaction I": "0.885 [0.84, 0.93] (P1 holds)",
                "RQ2b composition law": "fails at (j=1,k=2) 0.897 and (j=2,k=1) 0.830"},
    "iter_r2": {"acc_D(k=4)": 0.99, "delta(k=2)": "0.67 [0.60, 0.74]", "delta(k=4)": "0.01", "interaction I": "0.665 [0.60, 0.74]",
                "RQ2b composition law": "holds on all four primary pairs (lower bounds 0.98, 0.96, 0.99, 1.00)"},
    "set7": {"acc_D": 0.98, "dis_F": 0.01, "dis_C": 0.00, "dis_L": 0.94, "margin shift F / C / F1": "+0.65 / +0.23 / +1.91"},
}


def card(tag, ck):
    rows = "\n".join(f"| `{k}` | {v} |" for k, v in RQ2[tag].items())
    load = ("IterReasoner(rounds=%d, n_atoms=7)" % ck["rounds"]) if ck["kind"] == "iter" else "SetRecognizer(vocab_size=len(data7.VOCAB))"
    return f"""---
license: mit
tags: [recognition-paths, horn-logic, graded-monad, computation-budget]
---

# `rq2/{tag}` — {DESC[tag].split(';')[0]}

Part of `{MODEL_REPO}`. {DESC[tag]}. Parameters {ck['params']}; {ck['steps']} steps
of batch {ck['batch']} on synthetic Horn traces (2–6 clauses, seven atoms,
random relabelling, balanced labels), seed {ck['seed']}; the 200 RQ2 evaluation
theories (and their F, F1, C, L variants) are excluded from training up to
atom relabelling. Final validation accuracy {ck['log'][-1]['val_acc']:.3f}.

This is **not a language model.** It is a budgeted recognizer: the number
of message-passing rounds is a computation budget `k`, and the theory
(`RecognitionPaths/Graded.lean` in `recognition-paths`) predicts which
logically identical inputs it distinguishes at each `k`.

## Results on the frozen RQ2 tables (`proof-path-invariance/rq2/table`)

| statistic | value |
|---|---|
{rows}

`delta(k)` = decision-change rate for a depth-shortening derivable clause
minus that for a depth-preserving one; `I` = delta(2) − delta(4). See
`docs/RESULTS_RQ2.md` and `docs/RESULTS_RQ2B.md` in `proof-path-invariance`.

## Loading

```python
import json, sys, torch
sys.path.insert(0, "code")
from models import IterReasoner, SetRecognizer
import data7
from safetensors.torch import load_file
cfg = json.load(open("config.json"))
model = {load}
model.load_state_dict(load_file("model.safetensors")); model.eval()
# inputs: data7.iter_tensors(clauses, hyps, goals, relabels) / data7.set_tensors(...)
```
"""


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="hf/build_rq2"); ap.add_argument("--upload", action="store_true")
    a = ap.parse_args()
    out = ROOT / a.out
    if out.exists():
        shutil.rmtree(out)
    for tag in ("iter_r4", "iter_r2", "set7"):
        d = out / tag; d.mkdir(parents=True)
        ck = torch.load(W / f"{tag}.pt", map_location="cpu")
        save_file({k: v.contiguous() for k, v in ck["state"].items()}, str(d / "model.safetensors"))
        (d / "config.json").write_text(json.dumps({k: ck[k] for k in ("kind", "rounds", "n_atoms", "params", "seed", "steps", "batch")}, indent=2))
        (d / "training_log.json").write_text(json.dumps(ck["log"], indent=1))
        (d / "code").mkdir()
        shutil.copy(ROOT / "constructed" / "models.py", d / "code" / "models.py")
        for f in ("data7.py", "dfc.py"):
            shutil.copy(ROOT / "rq2" / f, d / "code" / f)
        (d / "README.md").write_text(card(tag, ck))
    (out / "README.md").write_text("""# rq2/ — budgeted recognizers over seven atoms

`iter_r4/`, `iter_r2/`: iterative learned reasoners (budget = rounds), `set7/`:
seven-atom set recognizer. Tables, preregistrations and results:
`Kairose-master/proof-path-invariance` (`rq2/`, `docs/PREREGISTRATION_RQ2*.md`,
`docs/RESULTS_RQ2*.md`); theory: `Kairose-master/recognition-paths`
(`RecognitionPaths/Graded.lean`).
""")
    print("built", [p.name for p in out.iterdir()])
    if a.upload:
        from huggingface_hub import HfApi
        api = HfApi()
        api.upload_folder(folder_path=str(out), repo_id=MODEL_REPO, repo_type="model", path_in_repo="rq2",
                          commit_message="Add RQ2 budgeted recognizers (iter_r4, iter_r2, set7)")
        print("uploaded to", MODEL_REPO, "rq2/")


if __name__ == "__main__":
    main()
