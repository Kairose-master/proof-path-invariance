#!/usr/bin/env python3
"""Boolean Chu-space analysis of a `hankel_v1` run (frozen plan v1).

Every cell's logit pair is read only through order relations:

  decision   D(u; z, q)      = [pos > neg]
  preference P(u; z, q1, q2) = [margin(z, q1) > margin(z, q2)],  q1 < q2

giving 228 + 342 = 570 bits per row per renderer.  No threshold and no
metric are used; the common logit offset cancels.  Distances below are
Hamming counts of disagreeing tests, i.e. numbers of separating columns.

Sections (see docs/PHASE3_HANKEL_V1_DESIGN.md):
  A. exact invariance on logically identical rows;
  B. separation between logical classes;
  C. biextensional collapse (distinct rows / distinct columns);
  D. readout: decision accuracy and bias-free comparative accuracy;
  E. exact closure check of the depth-one family;
  F. idempotence: repeated continuations and doubled prefixes.
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
SERIALIZATIONS = ["123", "231", "312", "321"]
QUERIES = ["ad", "ae", "bd", "ce"]
QPAIRS = list(itertools.combinations(QUERIES, 2))


def load(path: Path):
    obs = defaultdict(dict)        # renderer -> (row_id, cont, q) -> (pos, neg)
    gold = {}                      # (row_id, cont, q) -> bool
    rows, conts = set(), set()
    n = 0
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            n += 1
            cont, q = r["col_id"].rsplit("-", 1)
            obs[r["renderer"]][(r["row_id"], cont, q)] = tuple(r["observation"])
            gold[(r["row_id"], cont, q)] = bool(r["gold"])
            rows.add(r["row_id"])
            conts.add(cont)
    return obs, gold, sorted(rows), sorted(conts), n


def boolean_table(obs_r, gold, rows, conts):
    """Return (profiles, col_ids, col_depth, dec_gold, pref_gold)."""
    col_ids, depth = [], []
    for c in conts:
        d = 0 if c == "none" else c.count(".") + 1
        for q in QUERIES:
            col_ids.append(("D", c, q)); depth.append(d)
        for q1, q2 in QPAIRS:
            col_ids.append(("P", c, q1, q2)); depth.append(d)
    prof = np.zeros((len(rows), len(col_ids)), dtype=bool)
    dgold = np.zeros_like(prof)
    pgold = np.zeros(prof.shape, dtype=np.int8)   # +1 prefer q1, -1 prefer q2, 0 tie
    for i, u in enumerate(rows):
        j = 0
        for c in conts:
            m = {q: obs_r[(u, c, q)][0] - obs_r[(u, c, q)][1] for q in QUERIES}
            for q in QUERIES:
                prof[i, j] = m[q] > 0
                dgold[i, j] = gold[(u, c, q)]
                j += 1
            for q1, q2 in QPAIRS:
                prof[i, j] = m[q1] > m[q2]
                g1, g2 = gold[(u, c, q1)], gold[(u, c, q2)]
                pgold[i, j] = 0 if g1 == g2 else (1 if g1 else -1)
                j += 1
    return prof, col_ids, np.array(depth), dgold, pgold


def hamming(a, b):
    return int(np.count_nonzero(a != b))


def analyze_one(prof, col_ids, depth, dgold, pgold, rows):
    idx = {r: i for i, r in enumerate(rows)}
    kind = np.array([c[0] for c in col_ids])
    ncol = prof.shape[1]

    # A. exact invariance across serializations
    per_class, within_all = {}, []
    exact_classes = 0
    for c in CLASS_ORDER:
        ids = [idx[f"{c}-{s}"] for s in SERIALIZATIONS]
        hs = [hamming(prof[i], prof[j]) for i, j in itertools.combinations(ids, 2)]
        hd = [hamming(prof[i][kind == "D"], prof[j][kind == "D"]) for i, j in itertools.combinations(ids, 2)]
        hp = [hamming(prof[i][kind == "P"], prof[j][kind == "P"]) for i, j in itertools.combinations(ids, 2)]
        identical = len({prof[i].tobytes() for i in ids}) == 1
        exact_classes += identical
        per_class[c] = {"max_hamming": max(hs), "median_hamming": float(np.median(hs)),
                        "median_hamming_decision": float(np.median(hd)),
                        "median_hamming_preference": float(np.median(hp)),
                        "all_serializations_identical": identical}
        within_all.extend(hs)
    A = {"classes_with_identical_profiles": exact_classes, "classes": 8,
         "within_class_hamming_median": float(np.median(within_all)),
         "within_class_hamming_max": int(max(within_all)),
         "columns": int(ncol), "per_class": per_class}

    # B. separation between classes
    sep = {}
    for c1, c2 in itertools.combinations(CLASS_ORDER, 2):
        i1 = [idx[f"{c1}-{s}"] for s in SERIALIZATIONS]
        i2 = [idx[f"{c2}-{s}"] for s in SERIALIZATIONS]
        sep[f"{c1}|{c2}"] = min(hamming(prof[i], prof[j]) for i in i1 for j in i2)
    sv = np.array(list(sep.values()))
    # Exploratory robustness statistic (not a frozen gate): between-class
    # distance as the median over all cross-class row pairs, matching the
    # within-class statistic, instead of the minimum.
    cross = []
    for c1, c2 in itertools.combinations(CLASS_ORDER, 2):
        i1 = [idx[f"{c1}-{s}"] for s in SERIALIZATIONS]
        i2 = [idx[f"{c2}-{s}"] for s in SERIALIZATIONS]
        cross.extend(hamming(prof[i], prof[j]) for i in i1 for j in i2)
    cross_median = float(np.median(cross))
    B = {"min": int(sv.min()), "median": float(np.median(sv)), "max": int(sv.max()),
         "exploratory_cross_pair_median": cross_median,
         "exploratory_ratio_within_median_over_cross_pair_median": float(A["within_class_hamming_median"] / max(cross_median, 1e-9)),
         "class_pairs_with_min_separation_above_within_max": int((sv > A["within_class_hamming_max"]).sum()),
         "class_pairs_total": len(sep),
         "ratio_within_median_over_between_median": float(A["within_class_hamming_median"] / max(np.median(sv), 1e-9)),
         "per_class_pair": sep}

    # C. biextensional collapse
    C = {"distinct_row_profiles": len({prof[i].tobytes() for i in range(len(rows))}), "rows": len(rows),
         "distinct_column_profiles": len({prof[:, j].tobytes() for j in range(ncol)}), "columns": int(ncol),
         "logical_distinct_rows": len({dgold[i].tobytes() for i in range(len(rows))})}

    # D. readout
    dmask = kind == "D"
    pmask = (kind == "P") & (pgold != 0).any(axis=0)
    pdef = (kind == "P")[None, :] & (pgold != 0)
    pcorrect = ((prof == (pgold > 0)) & pdef)
    D = {"decision_accuracy": float((prof[:, dmask] == dgold[:, dmask]).mean()),
         "decision_positive_rate": float(prof[:, dmask].mean()),
         "decision_gold_positive_rate": float(dgold[:, dmask].mean()),
         "comparative_accuracy": float(pcorrect.sum() / pdef.sum()),
         "comparative_cells_defined": int(pdef.sum())}

    # E. exact closure of the depth-one family
    t1 = depth <= 1
    t2 = depth == 2
    agree_t1, violations, witness = 0, 0, None
    for i, j in itertools.combinations(range(len(rows)), 2):
        if hamming(prof[i][t1], prof[j][t1]) == 0:
            agree_t1 += 1
            h2 = hamming(prof[i][t2], prof[j][t2])
            if h2 > 0:
                violations += 1
                if witness is None or h2 > witness["separating_depth2_columns"]:
                    k = int(np.argmax(prof[i][t2] != prof[j][t2]))
                    witness = {"rows": [rows[i], rows[j]], "separating_depth2_columns": h2,
                               "example_column": "-".join(map(str, np.array(col_ids, dtype=object)[t2][k]))}
    E = {"row_pairs_identical_on_depth_le_1": agree_t1, "of_which_separated_at_depth_2": violations,
         "closed": violations == 0, "witness": witness, "depth_le_1_columns": int(t1.sum())}

    # F. idempotence
    singles = sorted({c[1] for c in col_ids if c[1] != "none" and "." not in c[1]})
    cont_eq, cont_tot = 0, 0
    for i in range(len(rows)):
        for a in singles:
            for k, c in enumerate(col_ids):
                if c[1] == a:
                    kk = col_ids.index((c[0], f"{a}.{a}") + c[2:])
                    cont_tot += 1
                    cont_eq += prof[i, k] == prof[i, kk]
    pre = {}
    for c in CLASS_ORDER:
        pre[c] = hamming(prof[idx[f"{c}-123"]], prof[idx[f"{c}-123x2"]])
    F = {"continuation_zz_vs_z_agreement": cont_eq / cont_tot, "continuation_cells": cont_tot,
         "prefix_uu_vs_u_hamming": pre, "prefix_uu_vs_u_hamming_median": float(np.median(list(pre.values()))),
         "serialization_hamming_median_for_reference": A["within_class_hamming_median"]}
    return {"A_invariance": A, "B_separation": B, "C_collapse": C, "D_readout": D, "E_closure": E, "F_idempotence": F}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    raw = Path(args.raw)
    obs, gold, rows, conts, n = load(raw)
    result = {"benchmark": "hankel_v1", "analysis_status": "boolean_chu_frozen_plan_v1",
              "raw_result_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(), "prompt_rows": n,
              "per_renderer": {}, "pooled": None}
    tables = {}
    for rend in sorted(obs):
        prof, col_ids, depth, dgold, pgold = boolean_table(obs[rend], gold, rows, conts)
        tables[rend] = (prof, col_ids, depth, dgold, pgold)
        result["per_renderer"][rend] = analyze_one(prof, col_ids, depth, dgold, pgold, rows)
    if len(tables) > 1:
        prof = np.concatenate([tables[r][0] for r in sorted(tables)], axis=1)
        col_ids = sum(([c + (r,) for c in tables[r][1]] for r in sorted(tables)), [])
        depth = np.concatenate([tables[r][2] for r in sorted(tables)])
        dgold = np.concatenate([tables[r][3] for r in sorted(tables)], axis=1)
        pgold = np.concatenate([tables[r][4] for r in sorted(tables)], axis=1)
        result["pooled"] = analyze_one(prof, col_ids, depth, dgold, pgold, rows)
    result["interpretation_limit"] = ("Exact Boolean statements about a finite table. Identical profiles mean "
                                      "'not separated by these tests', not identity under the recognition congruence.")
    Path(args.out).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    brief = {r: {k: {kk: vv for kk, vv in v.items() if kk not in ("per_class", "per_class_pair", "prefix_uu_vs_u_hamming")}
                 for k, v in res.items()} for r, res in result["per_renderer"].items()}
    print(json.dumps(brief, indent=1))


if __name__ == "__main__":
    main()
