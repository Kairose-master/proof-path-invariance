#!/usr/bin/env python3
"""Exploratory Phase 2.7 interaction diagnosis.

This script is intentionally descriptive/post-hoc. It joins a frozen S3
benchmark with its raw model results and asks which simple renderer-local
features co-vary with the permutation effect relative to identity order 123.

Features are derived mechanically from the benchmark text:
- movement of premises mentioning the query antecedent;
- movement of premises mentioning the query consequent;
- movement of a conjunction-bearing premise ("both"), when present;
- movement of a direct query-edge premise containing both query atoms;
- whether the final serialized premise mentions those features.

No structural claim follows from these summaries. Any compact hypothesis
suggested here must be frozen and tested on a fresh holdout.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path


PERMS = ["132", "213", "231", "312", "321"]
BASE = "123"


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    if not n:
        return None
    m = n // 2
    return xs[m] if n % 2 else (xs[m - 1] + xs[m]) / 2


def summarize(xs):
    return {
        "n": len(xs),
        "mean": mean(xs),
        "median": median(xs),
        "min": min(xs) if xs else None,
        "max": max(xs) if xs else None,
    }


def pearson(xs, ys):
    if len(xs) != len(ys) or len(xs) < 2:
        return None
    mx = mean(xs)
    my = mean(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx == 0 or vy == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(vx * vy)


def parse_query_atoms(query):
    m = re.fullmatch(r"If (\S+) holds, then (\S+) holds\.", query)
    if not m:
        raise SystemExit(f"unexpected query format: {query!r}")
    return m.group(1), m.group(2)


def position_map(perm):
    return {int(orig): pos for pos, orig in enumerate(perm, start=1)}


def center_position(indices, posmap):
    if not indices:
        return None
    return sum(posmap[i] for i in indices) / len(indices)


def load_benchmark(path):
    by_case = {}
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            cid = r["case_id"]
            if cid not in by_case:
                by_case[cid] = {
                    "family": r["family"],
                    "gold": bool(r["gold"]),
                    "premises": list(r["premise_multiset"]),
                    "query": r["query"],
                }
            else:
                x = by_case[cid]
                if (
                    x["family"] != r["family"]
                    or x["gold"] != bool(r["gold"])
                    or x["premises"] != list(r["premise_multiset"])
                    or x["query"] != r["query"]
                ):
                    raise SystemExit(f"{cid}: benchmark metadata changed across permutations")
    return by_case


def load_results(path):
    cases = defaultdict(dict)
    family = {}
    prompt_tokens = {}
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            cid = r["case_id"]
            p = r["permutation"]
            if p in cases[cid]:
                raise SystemExit(f"{cid}: duplicate permutation {p}")
            cases[cid][p] = float(r["margin"])
            family[cid] = r["family"]
            prompt_tokens[(cid, p)] = int(r["prompt_token_count"])
    expected = set(PERMS + [BASE])
    for cid, vals in cases.items():
        if set(vals) != expected:
            raise SystemExit(f"{cid}: incomplete S3 orbit")
    return cases, family, prompt_tokens


def premise_flags(case):
    a, d = parse_query_atoms(case["query"])
    flags = []
    for i, text in enumerate(case["premises"], start=1):
        flags.append({
            "index": i,
            "mentions_source": a in text,
            "mentions_target": d in text,
            "has_conjunction": "both " in text,
            "direct_query_edge": (a in text and d in text),
            "char_len": len(text),
            "word_len": len(text.split()),
        })
    return flags


def movement(indices, perm):
    if not indices:
        return None
    base = position_map(BASE)
    now = position_map(perm)
    return center_position(indices, now) - center_position(indices, base)


def bucket(x):
    if x is None:
        return "NA"
    if abs(x) < 1e-12:
        return "0"
    # half steps can occur when two premises carry the same query atom.
    return f"{x:+g}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", required=True)
    parser.add_argument("--results", required=True)
    parser.add_argument(
        "--phase2-summary",
        default="experiments/results/phase2_pythia70m_s3_summary.json",
    )
    args = parser.parse_args()

    bench = load_benchmark(args.benchmark)
    cases, result_family, prompt_tokens = load_results(args.results)

    if set(cases) != set(bench):
        missing_results = sorted(set(bench) - set(cases))
        missing_bench = sorted(set(cases) - set(bench))
        raise SystemExit(
            f"case mismatch: benchmark-only={missing_results[:3]}, "
            f"results-only={missing_bench[:3]}"
        )

    records = []
    signatures = {}
    family_perm = defaultdict(lambda: defaultdict(list))
    grouped = {
        "source_center_move": defaultdict(list),
        "target_center_move": defaultdict(list),
        "conjunction_move": defaultdict(list),
        "direct_edge_move": defaultdict(list),
        "last_mentions_source": defaultdict(list),
        "last_mentions_target": defaultdict(list),
        "last_has_conjunction": defaultdict(list),
        "last_is_direct_edge": defaultdict(list),
    }
    correlation_data = defaultdict(lambda: [[], []])

    for cid, vals in cases.items():
        case = bench[cid]
        if result_family[cid] != case["family"]:
            raise SystemExit(f"{cid}: family mismatch between benchmark and result")
        flags = premise_flags(case)

        src = [f["index"] for f in flags if f["mentions_source"]]
        tgt = [f["index"] for f in flags if f["mentions_target"]]
        conj = [f["index"] for f in flags if f["has_conjunction"]]
        direct = [f["index"] for f in flags if f["direct_query_edge"]]

        sig = {
            "gold": case["gold"],
            "source_premise_indices": src,
            "target_premise_indices": tgt,
            "conjunction_premise_indices": conj,
            "direct_query_edge_indices": direct,
            "baseline_prompt_tokens": prompt_tokens[(cid, BASE)],
        }
        signatures.setdefault(case["family"], sig)

        base_margin = vals[BASE]
        for p in PERMS:
            effect = vals[p] - base_margin
            posmap = position_map(p)
            last_orig = int(p[-1])
            last_flag = flags[last_orig - 1]

            feats = {
                "source_center_move": movement(src, p),
                "target_center_move": movement(tgt, p),
                "conjunction_move": movement(conj, p),
                "direct_edge_move": movement(direct, p),
                "last_mentions_source": bool(last_flag["mentions_source"]),
                "last_mentions_target": bool(last_flag["mentions_target"]),
                "last_has_conjunction": bool(last_flag["has_conjunction"]),
                "last_is_direct_edge": bool(last_flag["direct_query_edge"]),
            }

            family_perm[case["family"]][p].append(effect)
            for name, value in feats.items():
                if isinstance(value, bool):
                    grouped[name][str(value).lower()].append(effect)
                else:
                    grouped[name][bucket(value)].append(effect)
                    if value is not None:
                        correlation_data[name][0].append(float(value))
                        correlation_data[name][1].append(effect)

            records.append({
                "case_id": cid,
                "family": case["family"],
                "permutation": p,
                "effect": effect,
                **feats,
            })

    family_perm_summary = {
        fam: {
            p: summarize(vals)
            for p, vals in sorted(perms.items())
        }
        for fam, perms in sorted(family_perm.items())
    }

    grouped_summary = {
        name: {
            key: summarize(vals)
            for key, vals in sorted(groups.items())
        }
        for name, groups in grouped.items()
    }

    correlations = {
        name: pearson(xs, ys)
        for name, (xs, ys) in correlation_data.items()
    }

    current_perm_means = {
        p: mean([
            r["effect"] for r in records if r["permutation"] == p
        ])
        for p in PERMS
    }

    phase2_compare = None
    phase2_path = Path(args.phase2_summary)
    if phase2_path.exists():
        old = json.loads(phase2_path.read_text(encoding="utf-8"))
        old_means = {
            p: old["permutation_effect_vs_123"][p]["mean"]
            for p in PERMS
        }
        phase2_compare = {
            p: {
                "phase2_mean": old_means[p],
                "phase2_6_mean": current_perm_means[p],
                "difference": current_perm_means[p] - old_means[p],
                "sign_reversal": (
                    old_means[p] != 0
                    and current_perm_means[p] != 0
                    and (old_means[p] > 0) != (current_perm_means[p] > 0)
                ),
            }
            for p in PERMS
        }

    out = {
        "analysis_status": "exploratory_posthoc_after_failed_confirmatory",
        "cases": len(cases),
        "nonidentity_effect_rows": len(records),
        "family_signatures": dict(sorted(signatures.items())),
        "family_permutation_effects": family_perm_summary,
        "grouped_effects": grouped_summary,
        "feature_effect_pearson": correlations,
        "current_mean_effect_by_permutation": current_perm_means,
        "phase2_vs_phase2_6": phase2_compare,
        "interpretation_boundary": (
            "These summaries diagnose renderer-local interactions after a failed "
            "confirmatory test. They may generate a compact next hypothesis, but "
            "cannot validate it. Any proposed interaction law must be frozen and "
            "tested on a fresh unseen-family benchmark."
        ),
    }

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
