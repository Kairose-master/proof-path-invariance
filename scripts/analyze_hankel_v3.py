#!/usr/bin/env python3
"""Semantic-rewrite analysis of a `hankel_v3` run (frozen plan v3).

Boolean profiles as in `analyze_hankel_v2.py` (80 tests per renderer on the
depth-<=1 family).  For each class with base `123`:

  d_perm : median Hamming(base, permutation)        syntactic identity
  d_red  : median Hamming(base, red_k)              semantic identity, +1 clause
  d_swap : median Hamming(red_i, red_j), i<j        semantic identity, length-matched
  d_flip : median Hamming(base, flip_k)             logical change, length-matched

Free-column versions (`_free`) restrict to preference tests whose gold is a
tie for both rows of the pair, where an ideal recognizer is identical and
accuracy imposes nothing.

Frozen statistics (pooled over renderers):

  T = median over classes of d_red / d_flip          (all classes)
  U = median over classes with >=2 red rows of d_swap / d_flip
  V = median over classes of d_red_free / d_flip_free
  E = number of (base, red) pairs with identical full profiles, and of (red_i, red_j) pairs
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


CLASS_ORDER = ["chain", "fork_join", "chain_gap", "branch", "reversed", "fragments", "gated", "skip"]
QUERIES = ["ad", "ae", "bd", "ce"]
QPAIRS = list(itertools.combinations(QUERIES, 2))


def load(path):
    obs = defaultdict(dict); gold = {}; kind = {}; conts = set(); n = 0
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line); n += 1
            c, q = r["col_id"].rsplit("-", 1)
            obs[r["renderer"]][(r["row_id"], c, q)] = tuple(r["observation"])
            gold[(r["row_id"], c, q)] = bool(r["gold"])
            kind[r["row_id"]] = (r["logical_class"], r["kind"])
            conts.add(c)
    return obs, gold, kind, sorted(conts), n


def profiles(obs_r, gold, rows, conts):
    prof, free = {}, {}
    for u in rows:
        v, fmask = [], []
        for c in conts:
            m = {q: obs_r[(u, c, q)][0] - obs_r[(u, c, q)][1] for q in QUERIES}
            for q in QUERIES:
                v.append(m[q] > 0); fmask.append(False)
            for a, b in QPAIRS:
                v.append(m[a] > m[b]); fmask.append(gold[(u, c, a)] == gold[(u, c, b)])
        prof[u] = np.array(v); free[u] = np.array(fmask)
    return prof, free


def ham(a, b):
    return int(np.count_nonzero(a != b))


def ham_free(prof, free, u, v):
    m = free[u] & free[v]
    return int(np.count_nonzero(prof[u][m] != prof[v][m])), int(m.sum())


def med(xs):
    return float(np.median(xs)) if xs else None


def ratio(a, b):
    if a is None or b is None:
        return None
    return a / b if b > 0 else float("inf")


def analyze(prof, free, kind, rows):
    per_class = {}
    T, U, V = [], [], []
    ident_red = ident_swap = pairs_red = pairs_swap = 0
    for cls in CLASS_ORDER:
        base = f"{cls}-123"
        perms = [r for r in rows if kind[r] == (cls, "perm")]
        reds = [r for r in rows if kind[r] == (cls, "red")]
        flips = [r for r in rows if kind[r] == (cls, "flip")]
        d_perm = med([ham(prof[base], prof[r]) for r in perms])
        d_red = med([ham(prof[base], prof[r]) for r in reds])
        d_swap = med([ham(prof[a], prof[b]) for a, b in itertools.combinations(reds, 2)])
        d_flip = med([ham(prof[base], prof[r]) for r in flips])
        d_red_free = med([ham_free(prof, free, base, r)[0] for r in reds])
        d_flip_free = med([ham_free(prof, free, base, r)[0] for r in flips])
        d_swap_free = med([ham_free(prof, free, a, b)[0] for a, b in itertools.combinations(reds, 2)])
        ident_red += sum(ham(prof[base], prof[r]) == 0 for r in reds); pairs_red += len(reds)
        ident_swap += sum(ham(prof[a], prof[b]) == 0 for a, b in itertools.combinations(reds, 2))
        pairs_swap += len(list(itertools.combinations(reds, 2)))
        t, u, v = ratio(d_red, d_flip), ratio(d_swap, d_flip), ratio(d_red_free, d_flip_free)
        if t is not None: T.append(t)
        if u is not None: U.append(u)
        if v is not None: V.append(v)
        per_class[cls] = {"d_perm": d_perm, "d_red": d_red, "d_swap": d_swap, "d_flip": d_flip,
                          "d_red_free": d_red_free, "d_swap_free": d_swap_free, "d_flip_free": d_flip_free,
                          "T": t, "U": u, "V": v, "n_red": len(reds), "n_flip": len(flips)}
    fin = lambda xs: [x for x in xs if x is not None and np.isfinite(x)]
    return {"T_median_red_over_flip": med(fin(T)), "classes_red_closer_than_flip": sum(x < 1 for x in fin(T)),
            "U_median_swap_over_flip": med(fin(U)), "U_classes": len(fin(U)), "classes_swap_closer_than_flip": sum(x < 1 for x in fin(U)),
            "V_median_free_red_over_flip": med(fin(V)), "classes_free_red_closer": sum(x < 1 for x in fin(V)),
            "identical_base_red_pairs": ident_red, "base_red_pairs": pairs_red,
            "identical_swap_pairs": ident_swap, "swap_pairs": pairs_swap,
            "d_perm_median_over_classes": med([v["d_perm"] for v in per_class.values()]),
            "d_red_median_over_classes": med([v["d_red"] for v in per_class.values()]),
            "per_class": per_class}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--raw", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(); raw = Path(a.raw)
    obs, gold, kind, conts, n = load(raw); rows = sorted(kind)
    res = {"benchmark": "hankel_v3", "analysis_status": "semantic_rewrite_frozen_plan_v3",
           "raw_result_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(), "prompt_rows": n,
           "per_renderer": {}, "pooled": None}
    tabs = {}
    for rend in sorted(obs):
        prof, free = profiles(obs[rend], gold, rows, conts); tabs[rend] = (prof, free)
        res["per_renderer"][rend] = analyze(prof, free, kind, rows)
    if len(tabs) > 1:
        rs = sorted(tabs)
        prof = {u: np.concatenate([tabs[r][0][u] for r in rs]) for u in rows}
        free = {u: np.concatenate([tabs[r][1][u] for r in rs]) for u in rows}
        res["pooled"] = analyze(prof, free, kind, rows)
    res["interpretation_limit"] = ("Compares semantic rewrites (same consequences, different clauses) with a length-matched "
                                   "logical change on a finite Boolean table; identical profiles mean 'not separated by these tests'.")
    Path(a.out).write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8")
    for name in list(res["per_renderer"]) + (["pooled"] if res["pooled"] else []):
        r = res["per_renderer"].get(name) or res["pooled"]
        print(f"{name:8s} T={r['T_median_red_over_flip']:.2f} ({r['classes_red_closer_than_flip']}/8) "
              f"U={r['U_median_swap_over_flip']} ({r['classes_swap_closer_than_flip']}/{r['U_classes']}) "
              f"V={r['V_median_free_red_over_flip']} | ident base-red {r['identical_base_red_pairs']}/{r['base_red_pairs']} "
              f"swap {r['identical_swap_pairs']}/{r['swap_pairs']} | d_perm {r['d_perm_median_over_classes']} d_red {r['d_red_median_over_classes']}")


if __name__ == "__main__":
    main()
