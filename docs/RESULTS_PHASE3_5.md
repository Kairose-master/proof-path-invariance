# Phase 3.5 Result — Semantic rewrites `hankel_v3` on Pythia-70M and Qwen2.5-0.5B

Status: **FROZEN STATISTICS EVALUATED (`docs/PHASE3_HANKEL_V3_DESIGN.md`).**

Table SHA-256 `59fed91c…5a4b`, 4224 prompts, 66 rows (8 base, 24
permutations, 14 derivable-clause extensions, 20 flips), 80 Boolean tests
per renderer.

| Run | Raw (compressed) | Summary |
|---|---|---|
| `qwen05b` | `experiments/runs/hankel_v3_qwen05b.jsonl.gz` (`7024f1a5…`) | `experiments/results/phase3_5_hankel_v3_qwen05b_summary.json` |
| `pythia70m` | `experiments/runs/hankel_v3_pythia70m.jsonl.gz` (`b550a306…`) | `experiments/results/phase3_5_hankel_v3_pythia70m_summary.json` |

## Frozen statistics, pooled over renderers

| Recognizer | `T` (red/flip) | classes red < flip | `U` (swap/flip) | `V` (free columns) | `E` base–red | `E` swap |
|---|---:|---:|---:|---:|---:|---:|
| `qwen05b` | **1.11** | 3 / 8 | 1.45 (1/3) | **1.50** | 0 / 14 | 0 / 9 |
| `pythia70m` (control) | 1.00 | 3 / 8 | 0.64 (3/3) | 1.50 | 0 / 14 | 0 / 9 |
| synthetic gold + noise (calibration) | 0.51 | 8 / 8 | 0.53 | 1.40 | 0 | 0 |

Predictions: `qwen05b` `T` 1.0–1.6 and gates failing, `E = 0`: observed
1.11, fail, 0. Control near 1, `E = 0`: observed 1.00, 0. Both as recorded.

## Reading

For Qwen2.5-0.5B, appending a clause that is derivable from the trace
(logically invisible, Lean-certified schema) moves behavior as much as
reversing one arrow (`T` 1.11), and two such extensions of the same base
are as far apart as a base is from its flip (`U` 1.45). On the columns
where accuracy imposes nothing, `V` = 1.5: the semantic rewrite is *more*
disruptive than the logical change. No pair of logically identical rows is
behaviorally identical. The recognizer does not identify
consequence-equivalent clause sets at all; it does not even reach the
synthetic accuracy-only calibration on `T`.

Per renderer: bullets `T` 1.14, `V` 1.5; prose `T` 2.33, `V` 2.0.

The control sits at the noise value on `T` and `V`, as designed. Its
prose-renderer identical pairs (4/14, 3/9) are an artefact of near-constant
columns and vanish pooled.

## Scale: Qwen2.5-1.5B-Instruct on the same table

Raw `experiments/runs/hankel_v3_qwen15b.jsonl.gz` (`9b0d4eff…`), summary
`experiments/results/phase3_5_hankel_v3_qwen15b_summary.json`. No prediction
was recorded for this run; it is reported as observed.

| Recognizer | `T` | classes red < flip | `U` | `V` | `E` |
|---|---:|---:|---:|---:|---:|
| Qwen2.5-0.5B | 1.11 | 3 / 8 | 1.45 | 1.50 | 0, 0 |
| Qwen2.5-1.5B pooled | **0.62** | 5 / 8 | 0.82 | **1.01** | 0, 0 |
| Qwen2.5-1.5B bullets | 0.54 | 6 / 8 | 0.53 | 0.67 | 0, 0 |
| Qwen2.5-1.5B prose | 0.92 | 4 / 8 | 1.10 | 1.10 | 0, 1 |

From 0.5B to 1.5B, `T` falls from 1.11 to 0.62 and `V` from 1.50 to 1.01.
`T` below 1 is reached by accuracy (calibration in the design document),
so the informative movement is in `V`: pooled it reaches exactly the
no-identification value, under the bullet renderer it falls to 0.67, the
range of the architecturally invariant recognizer (0.62–0.80), under prose
it stays above 1. Exact identification remains absent (`E` 0 of 14).
HYPOTHESIS: within the family, identification of consequence-equivalent
sets on the accuracy-free columns begins to appear with scale, first under
the list renderer.

## What this settles

Phase 3.4 showed that permutations outweigh a logical change for this
recognizer. Phase 3.5 shows that the semantic part of `≡_L` fares no
better than the syntactic part: the recognizer's behavioral quotient does
not contain the consequence relation at any level the table can see. The
constructed recognizers of Phase 4 ask what training on entailment
supplies when the syntactic part is removed by architecture.
