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

## Replication and one exploratory run (added 2026-09-06, before running)

- **Seed 1** for `set`, `seq_aug`, `seq_fixed` with the identical
  protocol: a replication of the seed-0 numbers. Predictions: same
  qualitative pattern; `set` `V` in 0.4–0.9, `E` 0–3; `seq_fixed` Gate I
  ratio below 1 again.
- **`seq_aug` for 18000 steps, seed 0** (three times the budget):
  EXPLORATORY, not part of the frozen design. It asks whether the
  seed-0 failure (`S` 1.37) is under-convergence. Prediction: validation
  accuracy above 0.93 and `S` below 1; if `S` stays above 1 at high
  accuracy, augmentation does not yield permutation invariance on this
  contrast.

## Phase 4.1 — objective aimed at the quotient (added 2026-09-06, before running)

`set` seeds 2 and 3 (replication of the central `V`/`E` numbers) and a new
arm **`set_contrast`**: the same set encoder trained with the same data
plus a symmetric-KL loss (weight 1.0) between its outputs on pairs
(trace, trace + one derivable clause) with the same query, i.e. an
objective that targets the semantic part of `≡_L` directly. Two seeds.

Predictions: `set` s2/s3 `V` in 0.4–0.9, `E` 0–3. `set_contrast`: `V`
below 0.4 and `E` at least 4 of 14 on `hankel_v3`, comparative accuracy
still above 0.9; `S` 0 by construction. If `V` does not fall below the
plain `set` range, an objective on derivable extensions does not
generalise to the held-out classes' extensions, and the semantic half is
not reachable this way either.

## Re-centring after the literature check

Set-LLM (2025) and order-centric augmentation (2025) already realise the
`set` and `seq_aug` ideas at LLM scale (`docs/RELATED_WORK.md`). The
question this phase can still own is the gap between the two
specifications in `Specification.lean`: a permutation-invariant recognizer
is invariant under the syntactic part of `≡_L` by construction; does
training make it identify consequence-equivalent but syntactically
different clause sets? Answering it needs a table of such rewrites
(`hankel_v3`: redundant derivable clauses, alternative axiomatisations of
the same closure), on which `d_perm = 0` is trivial and the informative
distance is between consequence-equivalent rows. The predictions above
stand for the tables that exist; the `hankel_v3` design is the next step.

## What this cannot show

These are task-specific models of ~10⁵ parameters, not language models.
The comparison separates what the property requires from what pretraining
provides; it says nothing about which of the two an LLM at scale is doing.
