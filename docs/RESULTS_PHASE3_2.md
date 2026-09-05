# Phase 3.2 Result — Boolean Hankel table `hankel_v1` on Qwen2.5-0.5B-Instruct

Status: **FROZEN v1 GATES EVALUATED (`docs/PHASE3_HANKEL_V1_DESIGN.md`). DESCRIPTIVE OTHERWISE.**

Table SHA-256 `53028d8b…d1fa`, 18240 prompts, one forward pass each, CPU
float32. Raw rows `experiments/runs/hankel_v1_qwen05b.jsonl.gz`
(uncompressed SHA-256 `b7e574e7…e23f`). Summary
`experiments/results/phase3_2_hankel_v1_qwen05b_summary.json`.

Every cell is read only through order relations (decision `pos > neg`,
preference `margin(q1) > margin(q2)`): 570 Boolean tests per row per
renderer, 1140 pooled. Distances are Hamming counts of separating tests.

## Frozen gates (pooled, 1140 columns)

| Gate | Rule | Value | Outcome |
|---|---|---:|:---:|
| R (reads the task) | comparative accuracy > 0.55 | 0.867 | **pass** |
| I (identifies logical equivalents) | within-class median Hamming / between-class median Hamming < 1 | 94 / 167.5 = 0.561 | **pass** |

Per renderer: bullets 0.918 / 0.576, prose 0.816 / 0.688. Both pass both
gates.

This is the first recognizer and readout in the project under which
logically identical traces are closer to each other than logically
distinct classes are to each other. The Euclidean readout of Phase 3.1 on
the same recognizer gave `R = 1.35` (fail); the two statistics are not the
same quantity (sup-based metric versus median count of Boolean tests), so
this is a change of readout, not a contradiction, and it is the change the
Boolean design was built to test.

## What the exact statements say

- **A. Exact invariance fails.** No logical class has identical profiles
  across its four serializations (0 of 8). All 40 rows are pairwise
  distinct. The canonical map `F : L → B` does not exist exactly on this
  table; it exists only approximately, at the median.
- **Decision columns are trivial.** With the bullet renderer the decision
  `pos > neg` is positive on every cell (positive rate 1.000, accuracy
  equals the gold base rate 0.572); within-class decision Hamming is 0
  everywhere. All information is in the preference columns. The
  comparative readout raises accuracy from 0.57 to 0.92 on the same logits.
- **B. Separation.** Between-class minimum Hamming ranges 43–252 pooled;
  no class pair is separated beyond the largest within-class distance
  (0 of 28), because one class (`skip`) has an outlying within-class
  spread (median 218 of 1140, against 78–122 for the other seven).
- **C. Collapse.** 40 of 40 rows distinct; 467 of 1140 columns distinct
  (the rest are constant or duplicate tests); 8 logical rows.

## Closure (E)

Exactly one row pair is identical on all 80 depth-≤1 columns:
`fork_join-312` and `fork_join-321`. It is separated by depth-2 columns
(8 pooled), e.g. `P-b_c.e_d-ae-ce` (bullets). The depth-one family is
therefore **not closed** for this recognizer, and the witness is a
logically identical pair: the two serializations agree on every one-step
test and disagree two steps ahead. By `Identification.lean` this is the
column a depth-three table would need; it is not an error.

## Idempotence (F)

| Probe | Result | Reference |
|---|---:|---:|
| repeated continuation `a.a` vs `a` (Boolean agreement) | 0.957 | serialization agreement 1 − 94/1140 = 0.918 |
| doubled prefix `u.u` vs `u` (Hamming, median over classes) | 84 | serialization Hamming median 94 |

Repeating a continuation clause is nearly invisible (96% of tests agree),
more so than permuting the prefix. Doubling the whole prefix costs about as
much as permuting it. The idempotence consequence `ww ≈_ρ w` of
`Recognition.lean` fails exactly, like permutation invariance, and to a
similar degree.

## Renderer

The Phase 3.1 exploratory split (bullets pass, prose fail) does not
reproduce in Boolean form: both renderers pass Gate I, bullets more
strongly (0.576 vs 0.688). The metric-based split was partly a scale
effect of the prose logits.

## What this result is and is not

It is: on a threshold-free, metric-free readout, an instruction-tuned 0.5B
recognizer whose behavioral table is closer to the logical quotient than to
its own serialization noise at the median, with the invariance defect, the
closure witness, and the idempotence defect all stated as exact Boolean
facts.

It is not: exact invariance (0 of 8 classes), a closed test family, or
evidence beyond this recognizer and this table. Identical profiles would
mean "not separated by these tests", and none occurred except the one
closure witness.

## Next

Two runs are now justified by the gates: (1) the same table on a larger
instruction-tuned recognizer to see whether the ratio and the exact-identity
count move with scale; (2) a depth-three column family around the closure
witness. The `skip` class outlier should be inspected before either.
