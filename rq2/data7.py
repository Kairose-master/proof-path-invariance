"""Seven-atom Horn data for the RQ2 constructed recognizers.

Same token format as `constructed/horn_data.py` (atoms `A0..A6` relabelled
at random per sample, `->`, `&`, `;`, `?`, `=>`), but over seven atoms and
traces of 2-6 clauses, so that the RQ2 table (5-clause bases, 6-clause F/C
extensions, 4-clause L deletions over 7 atoms) lies inside the training
format.  Every evaluation theory (D, F, C, L of every holdout case) is
excluded from training up to atom relabelling.
"""

from __future__ import annotations

import itertools
import random
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).parent))
from dfc import ATOMS, closure  # noqa: E402

VOCAB = ["<pad>", "<bos>"] + [f"A{i}" for i in range(7)] + ["->", "&", ";", "?", "=>"]
TOK = {t: i for i, t in enumerate(VOCAB)}
NEG, POS = 0, 1
PERMS = list(itertools.permutations(ATOMS))


def entails(theory, hyp, goal):
    return goal in closure(theory, [hyp])


def signature(clauses):
    """Cheap relabelling-invariant: per clause the sorted atom-role profiles."""
    prof = {x: [0, 0, 0, 0] for x in ATOMS}
    for b, h in clauses:
        for x in b:
            prof[x][0 if len(b) == 1 else 1] += 1
        for y in h:
            prof[y][2 if len(h) == 1 else 3] += 1
    key = lambda x: tuple(prof[x])  # noqa: E731
    return tuple(sorted((tuple(sorted(key(x) for x in b)), tuple(sorted(key(y) for y in h))) for b, h in clauses))


def canonical(clauses):
    best = None
    for perm in PERMS:
        m = dict(zip(ATOMS, perm))
        key = tuple(sorted((tuple(sorted(m[x] for x in b)), tuple(sorted(m[y] for y in h))) for b, h in clauses))
        if best is None or key < best:
            best = key
    return best


class Holdout:
    """Set of theories excluded from training, matched up to relabelling."""

    def __init__(self, theories):
        self.sigs = {}
        for t in theories:
            self.sigs.setdefault(signature(t), set()).add(canonical(t))

    def contains(self, clauses):
        s = signature(clauses)
        if s not in self.sigs:
            return False
        return canonical(clauses) in self.sigs[s]


def random_clause(rng):
    k = rng.random()
    if k < 0.7:
        b, h = rng.sample(ATOMS, 2)
        return ((b,), (h,))
    if k < 0.85:
        x, y, z = rng.sample(ATOMS, 3)
        return ((x, y), (z,))
    x, y, z = rng.sample(ATOMS, 3)
    return ((x,), (y, z))


def sample(rng, holdout: Holdout | None = None):
    """Balanced sample over 2-6 clauses; theories in `holdout` are rejected."""
    target = rng.choice([NEG, POS])
    while True:
        n = rng.choice([2, 3, 4, 5, 5, 6])
        clauses = [random_clause(rng) for _ in range(n)]
        if holdout is not None and holdout.contains(clauses):
            continue
        hyp, goal = rng.sample(ATOMS, 2)
        label = POS if entails(clauses, hyp, goal) else NEG
        if label == target:
            break
    perm = ATOMS[:]
    rng.shuffle(perm)
    relabel = {a: f"A{ATOMS.index(p)}" for a, p in zip(ATOMS, perm)}
    return clauses, hyp, goal, relabel, label


def encode_clauses(clauses, relabel, max_len=6):
    out = []
    for b, h in clauses:
        ids = []
        for i, x in enumerate(b):
            if i:
                ids.append(TOK["&"])
            ids.append(TOK[relabel[x]])
        ids.append(TOK["->"])
        for i, y in enumerate(h):
            if i:
                ids.append(TOK["&"])
            ids.append(TOK[relabel[y]])
        out.append(ids + [TOK["<pad>"]] * (max_len - len(ids)))
    return out


def set_tensors(cs, hyps, goals, relabels):
    n = len(cs); C = max(len(c) for c in cs)
    cid = torch.full((n, C, 6), TOK["<pad>"], dtype=torch.long)
    qs = []
    for i, c in enumerate(cs):
        enc = encode_clauses(c, relabels[i])
        cid[i, : len(enc)] = torch.tensor(enc)
        qs.append([TOK["?"], TOK[relabels[i][hyps[i]]], TOK["=>"], TOK[relabels[i][goals[i]]]])
    return cid, torch.tensor(qs)


def iter_tensors(cs, hyps, goals, relabels):
    n = len(cs); C = max(len(c) for c in cs)
    bodies = torch.full((n, C, 2), -1, dtype=torch.long); heads = torch.full((n, C, 2), -1, dtype=torch.long)
    for i, c in enumerate(cs):
        rl = relabels[i]
        for j, (b, h) in enumerate(c):
            for k, x in enumerate(b[:2]):
                bodies[i, j, k] = int(rl[x][1:])
            for k, y in enumerate(h[:2]):
                heads[i, j, k] = int(rl[y][1:])
    hyp = torch.tensor([int(relabels[i][hyps[i]][1:]) for i in range(n)])
    goal = torch.tensor([int(relabels[i][goals[i]][1:]) for i in range(n)])
    return bodies, heads, None, hyp, goal


def tensors(kind, cs, hyps, goals, relabels):
    return set_tensors(cs, hyps, goals, relabels) if kind == "set" else iter_tensors(cs, hyps, goals, relabels)


def batch(rng, n, kind, holdout=None):
    raw, ys = [], []
    for _ in range(n):
        clauses, hyp, goal, relabel, label = sample(rng, holdout)
        raw.append((clauses, hyp, goal, relabel)); ys.append(label)
    return tensors(kind, *zip(*raw)), torch.tensor(ys)
