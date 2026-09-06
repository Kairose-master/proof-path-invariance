#!/usr/bin/env python3
"""Surface-controlled analysis of a `hankel_v2` run (frozen plan v2).

Boolean profiles as in `analyze_hankel_v1.py` (decision and preference
bits; 80 per renderer for the depth-<=1 family).  For each logical class
with base row `123`:

  d_perm  = median over the 3 permutations of Hamming(base, perm)
  d_flip  = median over the flips       of Hamming(base, flip)

Preregistered statistic (pooled over renderers):

  S = median over classes of d_perm / d_flip

S < 1: logically identical rewrites move behavior less than a one-arrow
logical change (logic outweighs surface).  S > 1: the opposite (surface
outweighs logic).  Also reported: the count of classes with d_perm <
d_flip, gold-row Hamming of each flip (how big the logical change is), and
the comparative/decision accuracies.
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
    obs = defaultdict(dict); gold = {}; kind = {}; conts = set()
    n = 0
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
    prof, dg, pg = {}, {}, {}
    for u in rows:
        v, g, p = [], [], []
        for c in conts:
            m = {q: obs_r[(u, c, q)][0] - obs_r[(u, c, q)][1] for q in QUERIES}
            for q in QUERIES:
                v.append(m[q] > 0); g.append(gold[(u, c, q)])
            for a, b in QPAIRS:
                v.append(m[a] > m[b]); ga, gb = gold[(u, c, a)], gold[(u, c, b)]
                p.append(0 if ga == gb else (1 if ga else -1))
        prof[u] = np.array(v); dg[u] = np.array(g); pg[u] = np.array(p)
    return prof, dg, pg


def ham(a, b):
    return int(np.count_nonzero(a != b))


def analyze(prof, dg, pg, kind, rows):
    per_class = {}
    ratios, wins = [], 0
    for cls in CLASS_ORDER:
        base = f"{cls}-123"
        perms = [r for r in rows if kind[r] == (cls, "perm")]
        flips = [r for r in rows if kind[r] == (cls, "flip")]
        dp = [ham(prof[base], prof[r]) for r in perms]
        df = [ham(prof[base], prof[r]) for r in flips]
        gf = [ham(dg[base], dg[r]) for r in flips]
        d_perm, d_flip = float(np.median(dp)), float(np.median(df))
        ratio = d_perm / d_flip if d_flip > 0 else float("inf")
        ratios.append(ratio); wins += d_perm < d_flip
        per_class[cls] = {"d_perm": d_perm, "d_flip": d_flip, "ratio": ratio,
                          "perm_distances": dp, "flip_distances": df,
                          "flip_gold_changes_decision_bits": gf, "n_flips": len(flips)}
    ncol = len(next(iter(prof.values())))
    dmask = np.array([i % 10 < 4 for i in range(ncol)])  # per continuation: 4 D then 6 P
    dec_acc = float(np.mean([np.mean(prof[u][dmask] == dg[u]) for u in rows]))
    pos = float(np.mean([np.mean(prof[u][dmask]) for u in rows]))
    corr = tot = 0
    for u in rows:
        p = prof[u][~dmask]; g = pg[u]; m = g != 0
        corr += int(((p == (g > 0)) & m).sum()); tot += int(m.sum())
    finite = [r for r in ratios if np.isfinite(r)]
    return {"S_median_ratio_perm_over_flip": float(np.median(finite)) if finite else None,
            "classes_with_perm_closer_than_flip": wins, "classes": len(CLASS_ORDER),
            "decision_accuracy": dec_acc, "decision_positive_rate": pos,
            "comparative_accuracy": corr / tot if tot else None, "columns": ncol,
            "per_class": per_class}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--raw", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(); raw = Path(a.raw)
    obs, gold, kind, conts, n = load(raw)
    rows = sorted(kind)
    res = {"benchmark": "hankel_v2", "analysis_status": "surface_controlled_frozen_plan_v2",
           "raw_result_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(), "prompt_rows": n,
           "per_renderer": {}, "pooled": None}
    tabs = {}
    for rend in sorted(obs):
        prof, dg, pg = profiles(obs[rend], gold, rows, conts)
        tabs[rend] = (prof, dg, pg)
        res["per_renderer"][rend] = analyze(prof, dg, pg, kind, rows)
    if len(tabs) > 1:
        rs = sorted(tabs)
        prof = {u: np.concatenate([tabs[r][0][u] for r in rs]) for u in rows}
        dg = {u: np.concatenate([tabs[r][1][u] for r in rs]) for u in rows}
        pg = {u: np.concatenate([tabs[r][2][u] for r in rs]) for u in rows}
        res["pooled"] = analyze(prof, dg, pg, kind, rows)
    res["interpretation_limit"] = ("S compares two kinds of rewrites of the same base trace on a finite Boolean table. "
                                   "It says which of surface reordering or a one-arrow logical change moves behavior more; "
                                   "it does not establish logical invariance.")
    Path(a.out).write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8")
    for name in list(res["per_renderer"]) + (["pooled"] if res["pooled"] else []):
        r = res["per_renderer"].get(name) or res["pooled"]
        print(f"{name:8s} S={r['S_median_ratio_perm_over_flip']:.3f} perm<flip in {r['classes_with_perm_closer_than_flip']}/8 "
              f"| compacc {r['comparative_accuracy']:.3f} decacc {r['decision_accuracy']:.3f} pos {r['decision_positive_rate']:.3f}")


if __name__ == "__main__":
    main()
