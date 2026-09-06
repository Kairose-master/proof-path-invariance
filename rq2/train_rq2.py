#!/usr/bin/env python3
"""Train a 7-atom constructed recognizer (set or iter) for RQ2, excluding the
holdout table's theories up to relabelling.

  python3 rq2/train_rq2.py --kind iter --rounds 4 --out experiments/rq2/iter_r4.pt
  python3 rq2/train_rq2.py --kind set --out experiments/rq2/set7.pt
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

import torch
import torch.nn.functional as F

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "constructed"))
import data7  # noqa: E402
from models import IterReasoner, SetRecognizer  # noqa: E402


def build(kind, rounds):
    return SetRecognizer(vocab_size=len(data7.VOCAB)) if kind == "set" else IterReasoner(rounds=rounds, n_atoms=7)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=["set", "iter"], required=True)
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--holdout", default=str(HERE / "table" / "rq2_cases.json"))
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--multi-hyp", action="store_true", help="hypothesis sets of 1-3 atoms (iter only)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    torch.manual_seed(a.seed); rng = random.Random(a.seed)
    cases = json.load(open(a.holdout))["cases"]
    holdout = data7.Holdout([[(tuple(b), tuple(h)) for b, h in t] for c in cases for t in c["theories"].values()])
    model = build(a.kind, a.rounds)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.01)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=1e-3, total_steps=a.steps)
    t0 = time.time(); log = []
    for step in range(1, a.steps + 1):
        inp, y = data7.batch(rng, a.batch, a.kind, holdout, a.multi_hyp)
        loss = F.cross_entropy(model(*inp), y)
        opt.zero_grad(); loss.backward(); opt.step(); sched.step()
        if step % 200 == 0:
            model.eval()
            with torch.no_grad():
                inp, y = data7.batch(random.Random(10_000 + step), 1024, a.kind, None, a.multi_hyp)
                acc = (model(*inp).argmax(-1) == y).float().mean().item()
            model.train()
            log.append({"step": step, "loss": loss.item(), "val_acc": acc, "sec": time.time() - t0})
            print(json.dumps(log[-1]), flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    torch.save({"kind": a.kind, "rounds": a.rounds, "n_atoms": 7, "multi_hyp": a.multi_hyp, "state": model.state_dict(), "log": log, "seed": a.seed,
                "steps": a.steps, "batch": a.batch, "holdout": a.holdout,
                "params": sum(p.numel() for p in model.parameters())}, a.out)
    print(json.dumps({"saved": a.out, "params": sum(p.numel() for p in model.parameters()), "final_val_acc": log[-1]["val_acc"]}))


if __name__ == "__main__":
    main()
