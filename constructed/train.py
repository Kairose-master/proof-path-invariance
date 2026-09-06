#!/usr/bin/env python3
"""Train one constructed recognizer and save it.

  python3 constructed/train.py --kind set  --out runs/set.pt
  python3 constructed/train.py --kind seq  --augment --out runs/seq_aug.pt
  python3 constructed/train.py --kind seq  --out runs/seq_fixed.pt
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

sys.path.insert(0, str(Path(__file__).parent))
from horn_data import TOK, encode, encode_clauses, sample, derivable_extension  # noqa: E402
from models import SeqRecognizer, SetRecognizer  # noqa: E402


def batch(rng, n, kind, augment):
    xs, cs, qs, ys = [], [], [], []
    for _ in range(n):
        clauses, hyp, goal, relabel, label = sample(rng, augment)
        ys.append(label)
        if kind == "seq":
            xs.append(encode(clauses, hyp, goal, relabel))
        else:
            cs.append(encode_clauses(clauses, relabel))
            qs.append([TOK["?"], TOK[relabel[hyp]], TOK["=>"], TOK[relabel[goal]]])
    y = torch.tensor(ys)
    if kind == "seq":
        L = max(len(x) for x in xs)
        ids = torch.full((n, L), TOK["<pad>"], dtype=torch.long)
        for i, x in enumerate(xs):
            ids[i, L - len(x):] = torch.tensor(x)   # left-pad so the last position is the query end
        return (ids,), y
    C = max(len(c) for c in cs)
    cid = torch.full((n, C, 6), TOK["<pad>"], dtype=torch.long)
    for i, c in enumerate(cs):
        cid[i, : len(c)] = torch.tensor(c)
    return (cid, torch.tensor(qs)), y


def equiv_batch(rng, n, kind):
    """Pairs (trace, trace + derivable clause) with the same query: logically
    identical inputs whose outputs an equivalence loss pulls together."""
    a, b = [], []
    while len(a) < n:
        clauses, hyp, goal, relabel, _ = sample(rng, False)
        ext = derivable_extension(rng, clauses)
        if ext is None:
            continue
        for lst, cl in ((a, clauses), (b, ext)):
            if kind == "seq":
                lst.append(encode(cl, hyp, goal, relabel))
            else:
                lst.append((encode_clauses(cl, relabel), [TOK["?"], TOK[relabel[hyp]], TOK["=>"], TOK[relabel[goal]]]))
    def pack(items):
        if kind == "seq":
            L = max(len(x) for x in items)
            ids = torch.full((n, L), TOK["<pad>"], dtype=torch.long)
            for i, x in enumerate(items):
                ids[i, L - len(x):] = torch.tensor(x)
            return (ids,)
        C = max(len(c) for c, _ in items)
        cid = torch.full((n, C, 6), TOK["<pad>"], dtype=torch.long)
        for i, (c, _) in enumerate(items):
            cid[i, : len(c)] = torch.tensor(c)
        return (cid, torch.tensor([q for _, q in items]))
    return pack(a), pack(b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=["set", "seq"], required=True)
    ap.add_argument("--augment", action="store_true")
    ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--equiv-loss", type=float, default=0.0,
                    help="weight of the symmetric-KL loss between outputs on (trace, trace + derivable clause) pairs")
    a = ap.parse_args()
    torch.manual_seed(a.seed)
    rng = random.Random(a.seed)
    model = SetRecognizer() if a.kind == "set" else SeqRecognizer()
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.01)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=1e-3, total_steps=a.steps)
    t0 = time.time()
    log = []
    for step in range(1, a.steps + 1):
        inp, y = batch(rng, a.batch, a.kind, a.augment)
        loss = F.cross_entropy(model(*inp), y)
        if a.equiv_loss > 0:
            ea, eb = equiv_batch(rng, a.batch // 2, a.kind)
            la, lb = F.log_softmax(model(*ea), -1), F.log_softmax(model(*eb), -1)
            kl = 0.5 * (F.kl_div(la, lb, log_target=True, reduction="batchmean")
                        + F.kl_div(lb, la, log_target=True, reduction="batchmean"))
            loss = loss + a.equiv_loss * kl
        opt.zero_grad(); loss.backward(); opt.step(); sched.step()
        if step % 200 == 0:
            model.eval()
            with torch.no_grad():
                inp, y = batch(random.Random(10_000 + step), 1024, a.kind, False)
                acc = (model(*inp).argmax(-1) == y).float().mean().item()
            model.train()
            log.append({"step": step, "loss": loss.item(), "val_acc": acc, "sec": time.time() - t0})
            print(json.dumps(log[-1]), flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    torch.save({"kind": a.kind, "augment": a.augment, "equiv_loss": a.equiv_loss, "state": model.state_dict(), "log": log,
                "params": sum(p.numel() for p in model.parameters()), "seed": a.seed, "steps": a.steps}, a.out)
    print(json.dumps({"saved": a.out, "params": sum(p.numel() for p in model.parameters()), "final_val_acc": log[-1]["val_acc"]}))


if __name__ == "__main__":
    main()
