# Phase 4 Result — Recognizers by construction

Status: **DESIGN AND PREDICTIONS FROZEN BEFORE TRAINING (`docs/PHASE4_CONSTRUCTED_DESIGN.md`). SEED 0 ONLY.**

Three recognizers trained on the same synthetic Horn distribution with the
eight evaluation classes held out up to atom relabelling, 6000 steps of
batch 128, seed 0, evaluated on the frozen tables through
`constructed/evaluate.py`. Weights `experiments/constructed/*.pt`,
evaluations `experiments/results/constructed/`, manifest there.

| Tag | Invariance source | Params | Final val. acc. |
|---|---|---:|---:|
| `set` | architecture (max-pooled clause encodings) | 168k | 0.993 |
| `seq_aug` | data (permutation/repetition augmentation) | 104k | 0.814 |
| `seq_fixed` | none | 104k | 0.945 |

`seq_aug` did not converge in the budget; augmentation makes the sequence
task harder. Its numbers are reported but its comparisons are weak.

## Same statistics as the measured recognizers

| | `set` | `seq_aug` | `seq_fixed` | `qwen05b` | `qwen15b` | `pythia70m` |
|---|---:|---:|---:|---:|---:|---:|
| `hankel_v1` comparative acc. | 0.996 | 0.703 | 0.737 | 0.867 | — | 0.456 |
| `hankel_v1` Gate I ratio | **0.000** | 0.288 | 0.739 | 0.561 | — | 1.42 |
| `hankel_v1` identical classes | **8 / 8** | 0 / 8 | 0 / 8 | 0 / 8 | — | 0 / 8 |
| `hankel_v1` distinct rows (of 40) | **8** | 39 | 40 | 40 | — | 40 |
| `hankel_v1` depth-1 family closed | **yes** (80 pairs, 0 separated) | no (4/3) | trivially (0 pairs) | no (1/1) | — | no (1/1) |
| `hankel_v2` `S` | **0.00** (8/8) | 1.37 (3/8) | 1.16 (3/8) | 1.27 (3/8) | 0.99 (4/8) | 0.97 (4/8) |
| `hankel_v3` `T` | 0.27 (7/8) | 0.68 (4/8) | 2.45 (2/8) | 1.11 (3/8) | — | 1.00 (3/8) |
| `hankel_v3` `U` | 0.27 (3/3) | 0.13 (2/2) | 0.50 (3/3) | 1.45 (1/3) | — | 0.64 (3/3) |
| `hankel_v3` `V` (free columns) | **0.63** | 1.54 | 6.0 | 1.50 | — | 1.50 |
| `hankel_v3` `E` base–red / swap | 0/14, 0/9 | 0/14, 2/9 | 0/14, 1/9 | 0/14, 0/9 | — | 0/14, 0/9 |

## The central experiment: `set` on `hankel_v3`

The `set` recognizer is exactly invariant under the syntactic part of
`≡_L`: on `hankel_v1` its 40 rows collapse to exactly the 8 logical
classes, `S = 0`, and its depth-one family is closed. It is 99% accurate
on classes it never saw. On `hankel_v3`:

- **`E` = 0 / 14.** Not one derivable-clause extension has the same
  profile as its base; no two extensions of one base coincide. Exact
  identification of consequence-equivalent clause sets: none.
- **`V` = 0.63.** On the columns where accuracy imposes nothing, a
  semantic rewrite moves the recognizer 0.63 times as far as a logical
  flip. Partial identification, within the recorded prediction (0.5–1).
- `T` = 0.27 and `U` = 0.27 pass their gates, but the calibration in the
  design document shows these are passed by accuracy alone (synthetic
  gold-plus-noise: 0.51 / 0.53); they are not evidence of identification.

**Conclusion (OBSERVED).** Permutation invariance by construction plus
training to 99% accuracy on Horn entailment yields a recognizer whose
behavioral quotient is exactly the syntactic quotient and only partly the
semantic one. Training supplies part of the semantic half (`V` 0.63
against 1.5 for the LLMs and the control) but not all of it, and none of
it exactly. Permutation invariance is not logical invariance, and
accuracy does not close the gap.

## Prediction check

| Prediction | Outcome |
|---|---|
| `set`: comparative acc. > 0.85; `S = 0`; Gate I pass | 0.996; 0; ratio 0.000 — held |
| `set`: depth-one family still not closed | **wrong**: closed on `hankel_v1` (whose rows are all syntactic rewrites) |
| `set`: `V` in 0.5–1; `E` 0–3 | 0.63; 0 — held |
| `seq_aug`: `S` in 0.3–0.8, Gate I pass, no identical classes | `S` **1.37 (wrong)**; 0.288 pass; 0/8 — model under-converged |
| `seq_fixed`: `S > 1`, Gate I fail | 1.16 held; Gate I **0.739 pass (wrong)** |
| Ordering `set < seq_aug < 1 < seq_fixed` on `S` | `set` 0 < `seq_fixed` 1.16 < `seq_aug` 1.37 — **wrong in the middle** |

Two of the wrong predictions carry information. `seq_fixed` passes Gate I
at 0.739 although it never saw a permuted trace: Gate I rewards shared
surface content, as Phases 3.3–3.4 concluded, and a fixed-order model
shares it. And `seq_fixed` collapses under the doubled prefix
(`u.u` versus `u` Hamming 278 of 1140) because six-clause traces are
outside its training lengths: a length-generalization failure that the
set encoder does not have (`u.u` Hamming 0).

## Seed 1 replication (added 2026-09-06; predictions recorded in the design document before training)

| | `set` s0 | `set` s1 | `seq_aug` s0 | `seq_aug` s1 | `seq_fixed` s0 | `seq_fixed` s1 |
|---|---:|---:|---:|---:|---:|---:|
| final val. acc. | 0.993 | 0.990 | 0.814 | 0.895 | 0.945 | 0.950 |
| `hankel_v1` identical classes / distinct rows | 8/8, 8 | 8/8, 8 | 0/8, 39 | 0/8, 40 | 0/8, 40 | 0/8, 40 |
| `hankel_v1` Gate I ratio | 0.000 | 0.000 | 0.288 | 0.437 | 0.739 | 0.342 |
| `hankel_v2` `S` | 0.00 (8/8) | 0.00 (8/8) | 1.37 (3/8) | **0.51 (7/8)** | 1.16 (3/8) | **0.58 (5/8)** |
| `hankel_v3` `V` | 0.62 | 0.80 | 1.54 | 0.75 | 6.0 | 2.42 |
| `hankel_v3` `E` base–red, swap | 0/14, 0/9 | 2/14, 0/9 | 0/14, 2/9 | 0/14, 5/9 | 0/14, 1/9 | 0/14, 2/9 |

**`set` replicates.** Exactly the syntactic quotient again (8/8, `S` 0,
closed), and partial semantic identification again: `V` 0.80 (seed 0:
0.62), `E` 2 of 14 extensions exactly identical to their base (seed 0: 0).
Both inside the recorded ranges (`V` 0.4–0.9, `E` 0–3). The central
conclusion stands: permutation invariance plus accuracy gives part, not
all, of the semantic half, and almost none of it exactly.

**The sequence recognizers do not replicate on `S`.** With a
better-converged seed (val 0.895) `seq_aug` passes Gate S at 0.51 (7/8);
the seed-0 failure was under-convergence, as suspected. But `seq_fixed`,
which never sees a permutation, also drops from 1.16 to 0.58 across seeds.
On an 80-test table with 10⁵-parameter models, `S` for the causal
recognizers moves by a factor of two between seeds. Two consequences:
the recorded ordering `set < seq_aug < 1 < seq_fixed` is not established
in either direction, and any claim about augmentation versus fixed order
needs several seeds (seeds 2–3 queued). The `set` recognizer's numbers are
stable because most of them are forced by construction.

## Limits

One seed; toy models of ~10⁵ parameters; `seq_aug` under-trained; the
held-out classes are held out only up to atom relabelling; five atoms.
These models say what the property requires, not what an LLM does.

## Next

A longer `seq_aug` run (exploratory, not preregistered) to separate
"augmentation cannot reach `S < 1`" from "6000 steps were not enough";
a second seed for all three; and the same `hankel_v3` on `qwen15b`.
