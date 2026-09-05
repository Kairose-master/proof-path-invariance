# Phase 3.0 Result — Hankel observation table `hankel_v0` on Pythia-70M

Status: **DESCRIPTIVE RESULT UNDER THE FROZEN v0 PLAN. NO CONFIRMATORY ENDPOINT.**

Model `EleutherAI/pythia-70m`, revision `step143000`, CPU, float32, one
forward pass per prompt, both answer logits recorded. 16384 prompts, 16
presentation controls, one 32 × 32 table per control. Raw rows:
`experiments/runs/hankel_v0_pythia70m.jsonl.gz` (uncompressed SHA-256
`d5090d97…603e34`). Summary: `experiments/results/phase3_hankel_v0_summary.json`.

## Headline

**OBSERVED:** premise serialization moves the answer-logit pair more than
changing the logical class does. In every one of the 16 controls the
invariance defect on logically identical rows exceeds the separation between
every pair of logically distinct classes.

| Quantity (per control; min / median / max over 16 controls) | Value |
|---|---|
| A. `Δ_inv`: max distance between serializations of one logical class | 0.394 / 0.947 / 1.432 |
| B. min class separation (closest pair of distinct classes) | 0.030 / 0.123 / 0.185 |
| B. median class separation | 0.159 / 0.270 / 0.399 |
| B. class pairs separated at tolerance `Δ_inv` (of 28) | 0 / 0 / 0 |
| C. numerical rank of the raw table at `10⁻³·σ₁` | 1 / 1 / 1 |
| D. AUROC of `pos − neg` against gold | 0.357 / 0.519 / 0.574 |
| E. closure defect at `ε = Δ_inv` | 0.519 / 1.133 / 1.533 |

Distances are Euclidean on the raw logit pair in ℝ².

## Reading the table against the theory

The Recognition Factorization Theorem compares two quotients of `Σ*`. On the
finite family `T` of this table:

- **`≡_L ⊆ ≈_{ρ,T}` fails at every tolerance at which classes are
  separable.** Rows that are logically identical (Lean-certified,
  `Horn.logicalEquiv_of_perm`) sit 3–10 times farther apart than the closest
  logically distinct rows. There is no `ε` at which the canonical path
  `F : L → B` is approximately well-defined and non-trivial.
- **`≈_{ρ,T} ⊆ ≡_L` also fails at that scale.** At tolerance `Δ_inv`,
  between 358 and 496 of the 496 row pairs "agree" on the direct queries,
  including pairs from different logical classes. Logical meaning is not
  recoverable from behavior on this table.
- **Closure (Section E).** The closure defect equals the overall
  order-sensitivity scale; a typical refinement witness is the pair
  `branch-231` / `skip-321` separated by column `b_d-ce`. Since `ε = Δ_inv`
  is already larger than the class structure, the diagnostic is
  uninformative here beyond confirming that the direct queries do not
  determine one-step extensions. It becomes meaningful only for a recognizer
  whose `Δ_inv` is below its class separation.

## Rank

The raw table has numerical rank 1 at both thresholds in every control and
pooled (`σ₁ ≈ 4.9·10⁴` per control, `σ₂ ≈ 1.9`): the logit pair carries a
large common offset (≈ 1076 for both candidates) that dominates every
singular value. This is the frozen quantity and it is reported as such.

**EXPLORATORY (not in the frozen plan):** after removing the column means,
the 32-row table has rank 15–26 at `10⁻²·σ₁` and full rank 31 at `10⁻³·σ₁`
in every control; the pooled centered table is also full rank 31. There is
no low-dimensional structure at these thresholds: rows differ in ways that
the singular-value spectrum does not compress. Nested sub-tables of 16 and
24 rows are rank 1 raw, as expected from the offset.

## Readout

AUROC of the margin against gold is at chance (median 0.519; range
0.357–0.574). With the YES/NO map every one of the 1024 cells per control is
predicted positive; with the True/False map between 823 and 1024 are. This
matches Phases 1–2.6: the binary observable is saturated by response bias.

## Presentation controls

| Control | Effect on `Δ_inv` |
|---|---|
| relabeling `sym4` (`X1…X5`) | smallest order sensitivity (0.39–0.53) |
| relabelings `sym1`–`sym3` | 0.68–1.43 |
| renderer, answer map | no consistent direction |

**CONFOUND:** the atom-label family changes the magnitude of order
sensitivity by about a factor of three. Any future quantitative comparison
across tables must hold the relabeling fixed or report it as a factor.

Within a class, the serialization pair `312`/`321` is the closest (median
0.20) and pairs involving `123` are the farthest (0.36–0.40), consistent
with the position effects recorded in Phase 2.7.

## What this result is and is not

It is: a measurement, on a Lean-grounded finite table, that Pythia-70M's
behavioral quotient on three-premise Horn prefixes is dominated by
serialization and carries no detectable logical structure, with the
invariance defect and class separation both quantified.

It is not: evidence about any larger model, a test of the identifiability
theorem's hypotheses (the recognizer must first have `Δ_inv` below class
separation), or a statement about internal representations.

## Next

The theory side of this project only bites once a recognizer separates
logical classes more than it separates serializations. The next run should
repeat `hankel_v0` unchanged on a model with above-chance accuracy on the
same prompts, and report the same seven quantities. `hankel_v1` (depth-two
continuations for the full closure check) is worth building only after that.
