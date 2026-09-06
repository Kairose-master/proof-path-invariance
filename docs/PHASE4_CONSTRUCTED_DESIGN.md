# Phase 4 — Recognizers by construction

Status: **DESIGN AND PREDICTIONS FROZEN BEFORE TRAINING THE REPORTED MODELS.**
(Smoke runs of a few hundred steps were used only to check that the code
executes; their outputs are not reported.)

## Question

The theory defines the target property (`Specification.lean`): a
recognizer that factors through the set of clauses is permutation- and
repetition-invariant by construction; the ideal recognizer factors through
the consequence operator and has `L ≃ B`. Measured LLMs satisfy neither.
What does training supply when the surface quotient is removed by
architecture, and what does it supply when it is not?

## Recognizers

All are trained on the same synthetic Horn distribution (`constructed/horn_data.py`):
2–4 clauses over five atoms, atoms relabelled at random per sample, balanced
labels by rejection, and the eight evaluation classes of `hankel_v0` held
out up to atom relabelling (isomorphism under the 120 atom permutations).

| Tag | Model | Invariance source | Params |
|---|---|---|---|
| `set` | clause encoder + max-pool + query encoder (`SetRecognizer`) | architecture: exact for permutation and repetition | ~170k |
| `seq_aug` | causal transformer, last position (`SeqRecognizer`) | data: permutation + repetition augmentation | ~100k |
| `seq_fixed` | same transformer | none (fixed generation order) | ~100k |

Each is trained for 6000 steps of batch 128 (768k samples), AdamW,
one-cycle schedule, seed 0. A second seed is run for each if time allows;
the primary numbers are seed 0.

## Evaluation

Each model is applied to the frozen tables through
`constructed/evaluate.py`, which renders the table's clause lists into the
model's tokens and writes runner-schema output, so the existing
`analyze_hankel_v1.py` and `analyze_hankel_v2.py` run unchanged. There is
one rendering, so "pooled" equals per-renderer.

Primary statistics, same as Phases 3.2–3.4:

- `hankel_v2`: `S` (median over classes of `d_perm / d_flip`), classes with
  `d_perm < d_flip`, comparative accuracy.
- `hankel_v1`: Gate R (comparative accuracy), Gate I (within/between
  median Hamming), classes with identical serialization profiles, closure,
  idempotence.

For `set`, `d_perm = 0` and identical serialization profiles in 8/8
classes are guaranteed; the code checks that this holds numerically (a
failure would be a bug, not a result).

## Recorded predictions (before training)

- `set`: comparative accuracy on the held-out classes above 0.85;
  `S = 0` by construction; Gate I passes; closure of the depth-one family
  still fails (consequence-equivalent but syntactically different
  extensions are not identified by the architecture).
- `seq_aug`: `S` below 1 (prediction 0.3–0.8), Gate I passes, but no class
  with exactly identical serialization profiles.
- `seq_fixed`: `S` above 1, Gate I fails: the same ordering as the measured
  LLMs.
- Ordering of `S`: `set` (0) < `seq_aug` < 1 < `seq_fixed`.

The interesting comparison is `set` against `seq_aug`: if `seq_aug`
reaches `S` near 0 with near-identical profiles, data alone recovers what
architecture guarantees; if it does not, the surface quotient survives
augmentation.

## What this cannot show

These are task-specific models of ~10⁵ parameters, not language models.
The comparison separates what the property requires from what pretraining
provides; it says nothing about which of the two an LLM at scale is doing.
