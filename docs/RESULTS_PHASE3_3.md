# Phase 3.3 Result — Control and scale on the Boolean table

Status: **CONTROL COMPLETED; SCALE RUN IN PROGRESS.** Gates and predictions
were frozen in `docs/PREREGISTRATION_PHASE3_3.md` before any output was read.

## Control: Pythia-70M on `hankel_v1`

Raw rows `experiments/runs/hankel_v1_pythia70m.jsonl.gz` (uncompressed
SHA-256 `49bf32f9…1d6a`), summary
`experiments/results/phase3_3_hankel_v1_pythia70m_summary.json`.

| Gate | Rule | `pythia70m` | `qwen05b` (Phase 3.2) |
|---|---|---:|---:|
| R | comparative accuracy > 0.55 (pooled) | 0.456 **fail** | 0.867 pass |
| I | within / between median Hamming < 1 (pooled) | 72.5 / 51.0 = 1.422 **fail** | 0.561 pass |

**The Boolean Gate I is valid.** A recognizer that does not read the task
does not pass it. The prediction "fails both gates" holds; the predicted
ratio range (0.9–1.1) was too low: for the non-reading recognizer
logically identical rows are *farther* apart than logically distinct
classes (ratio 1.42), the same ordering as under the Euclidean readout of
Phase 3.0. Its columns are also far less informative (276 distinct of
1140, against 467 for `qwen05b`), so both Hamming medians are smaller in
absolute terms; only the ratio is comparable across recognizers.

## What the control corrects in the Phase 3.2 reading

- **Repeated continuations.** `pythia70m` agrees with itself on `a.a`
  versus `a` on 95.0% of tests, essentially the same as `qwen05b`
  (95.7%). High agreement on repeated continuations is therefore a
  generic property of these prompts, not evidence of logical idempotence.
  The Phase 3.2 sentence "repeating a continuation clause is nearly
  invisible" stands as an observation but carries no logical weight.
- **Doubled prefixes.** `pythia70m`: `u.u` versus `u` Hamming median 55
  against serialization median 72.5; `qwen05b`: 84 against 94. In both,
  doubling the prefix costs slightly less than permuting it. Same reading:
  generic, not logical.
- **Closure.** `pythia70m` has 1 row pair identical on the depth-≤1
  columns pooled (9 and 26 per renderer), all separated at depth 2. The
  depth-one family is not closed for either recognizer; closure failure
  by itself does not discriminate between them.

Per renderer the control ratios are 2.05 (bullets) and 1.82 (prose),
against 0.58 and 0.69 for `qwen05b`.

## EXPLORATORY — what Gate I does and does not measure

Two robustness checks on the Boolean tables, not preregistered.

**Matched statistic.** The frozen Gate I compares the within-class median
with the between-class median of *minimum* row-pair distances. Replacing
the minimum by the median over all cross-class row pairs gives
`qwen05b` 0.43 and `pythia70m` 0.72: under the matched statistic the
non-reading control is also below 1. The frozen gate discriminates the
two recognizers; the ordering "same class closer than different class"
by itself does not.

**Nearest classes.** For `qwen05b`, `chain` (`a→b, b→c, c→d`) and
`reversed` (`b→a, c→b, d→c`), which share every atom and every clause
shape and differ in nothing but the direction of all three arrows, are at
Hamming 73, *below* the within-class serialization distance of `chain`
(78). Likewise `fragments`/`gated` at 43 against within-class 122 and
100. The logically most different pairs with the most similar surface are
not separated beyond serialization noise.

Reading: part of the within-class proximity that Gate I rewards is shared
surface content (the same clause multiset), not logical identity. The
gate is valid as a discriminator between recognizers but does not by
itself show that the proximity is logical. Phase 3.4 (`hankel_v2`)
separates the two by contrasting single-arrow flips (minimal surface
edit, logical change) with permutations (maximal surface edit, no logical
change).

## Scale: Qwen2.5-1.5B-Instruct on `hankel_v1`

Running as a single 4-thread float32 process (memory does not allow
sharding). Results are appended here when it completes.
