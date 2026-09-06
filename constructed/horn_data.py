"""Synthetic Horn data for constructed recognizers.

Tokens: atoms `A0..A4` (relabelled at random per sample), `->`, `&`, `;`
(clause separator), `?` (query marker), `=>` (inside the query).  A sample
is a trace of 2-4 clauses plus one query; the label is Horn entailment by
forward chaining.  The eight evaluation classes of `hankel_v0` are held out
of training up to atom relabelling (graph isomorphism under the 120 atom
permutations).
"""

from __future__ import annotations

import itertools
import random

ATOMS = ["a", "b", "c", "d", "e"]
VOCAB = ["<pad>", "<bos>", "A0", "A1", "A2", "A3", "A4", "->", "&", ";", "?", "=>"]
TOK = {t: i for i, t in enumerate(VOCAB)}
NEG, POS = 0, 1

HELD_OUT = {
    "chain": [(("a",), ("b",)), (("b",), ("c",)), (("c",), ("d",))],
    "fork_join": [(("a",), ("b",)), (("a",), ("c",)), (("b", "c"), ("d",))],
    "chain_gap": [(("a",), ("b",)), (("b",), ("c",)), (("d",), ("e",))],
    "branch": [(("a",), ("b", "c")), (("c",), ("d",)), (("e",), ("b",))],
    "reversed": [(("b",), ("a",)), (("c",), ("b",)), (("d",), ("c",))],
    "fragments": [(("a",), ("b",)), (("c",), ("d",)), (("d",), ("e",))],
    "gated": [(("a", "b"), ("c",)), (("c",), ("d",)), (("d",), ("e",))],
    "skip": [(("a",), ("c",)), (("c",), ("e",)), (("b",), ("d",))],
}


def canonical(clauses):
    """Canonical form of a clause multiset under atom relabelling."""
    best = None
    for perm in itertools.permutations(ATOMS):
        m = dict(zip(ATOMS, perm))
        key = tuple(sorted((tuple(sorted(m[x] for x in b)), tuple(sorted(m[y] for y in h))) for b, h in clauses))
        if best is None or key < best:
            best = key
    return best


HELD_OUT_CANON = {canonical(v) for v in HELD_OUT.values()}


def closure(theory, facts):
    known = set(facts)
    changed = True
    while changed:
        changed = False
        for b, h in theory:
            if all(x in known for x in b) and not all(y in known for y in h):
                known |= set(h)
                changed = True
    return known


def entails(theory, hyp, goal):
    return goal in closure(theory, [hyp])


def random_clause(rng):
    k = rng.random()
    if k < 0.6:
        b, h = rng.sample(ATOMS, 2)
        return ((b,), (h,))
    if k < 0.8:
        x, y, z = rng.sample(ATOMS, 3)
        return ((x, y), (z,))
    x, y, z = rng.sample(ATOMS, 3)
    return ((x,), (y, z))


def random_trace(rng, n_clauses):
    while True:
        clauses = [random_clause(rng) for _ in range(n_clauses)]
        if n_clauses == 3 and canonical(clauses) in HELD_OUT_CANON:
            continue
        return clauses


def encode(clauses, hyp, goal, relabel):
    """Token ids for a trace + query, with atom relabelling map `relabel`."""
    ids = [TOK["<bos>"]]
    for b, h in clauses:
        for i, x in enumerate(b):
            if i:
                ids.append(TOK["&"])
            ids.append(TOK[relabel[x]])
        ids.append(TOK["->"])
        for i, y in enumerate(h):
            if i:
                ids.append(TOK["&"])
            ids.append(TOK[relabel[y]])
        ids.append(TOK[";"])
    ids += [TOK["?"], TOK[relabel[hyp]], TOK["=>"], TOK[relabel[goal]]]
    return ids


def encode_clauses(clauses, relabel, max_len=6):
    """Per-clause token lists (for the set encoder), padded."""
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


def sample(rng, augment: bool):
    """Balanced sample: the target label is drawn first, then a trace and
    query with that label are found by rejection."""
    target = rng.choice([NEG, POS])
    while True:
        n = rng.choice([2, 3, 3, 4])
        clauses = random_trace(rng, n)
        hyp, goal = rng.sample(ATOMS, 2)
        label = POS if entails(clauses, hyp, goal) else NEG
        if label == target:
            break
    perm = ATOMS[:]
    rng.shuffle(perm)
    relabel = {a: f"A{i}" for a, i in zip(ATOMS, [ATOMS.index(p) for p in perm])}
    if augment:
        rng.shuffle(clauses)
        if rng.random() < 0.3:
            clauses = clauses + [rng.choice(clauses)]
    return clauses, hyp, goal, relabel, label
