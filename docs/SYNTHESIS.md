# Synthesis — what the project can currently say

Status: working draft, updated as phases complete. Every sentence carries
one of the labels of `AGENTS.md`: PROVED (machine-checked in
`recognition-paths`), OBSERVED (measured here, with the file that holds the
number), HYPOTHESIS, OPEN, or CONFOUND. Novelty: not established; see the
last section.

## The objects

PROVED. Fix a Horn signature `Σ`, ordered premise traces `Σ*`, queries
`Q`, and a recognizer `ρ : Σ* × Q → O`. Logical identity `u ≡_L v` (same
consequences for every query) is a two-sided congruence, commutative and
idempotent, so `L = Σ*/≡_L` is a commutative idempotent monoid. Two-sided
behavioral identity `u ≈_ρ v` is a congruence, so `B = Σ*/≈_ρ` is a
monoid. Right-context identity `≡_ρ` gives the Nerode quotient, which is
the extensional collapse of the prefix realization, and `B` acts on it as
its transition monoid. (`Horn.lean`, `Recognition.lean`, `Nerode.lean`.)

PROVED. `≡_L ⊆ ≈_ρ` holds iff a unique representative-preserving
`F : L → B` exists; `F` is then a monoid morphism. `≈_ρ ⊆ ≡_L` holds iff
`G : B → L` exists; both give `L ≃ B`. Under `≡_L ⊆ ≈_ρ`, every
permutation, every swap of blocks, and every repetition of a block is
behaviorally invisible in every context. (`Recognition.lean`,
`Factorization.lean`.)

PROVED. A test family containing the direct queries induces exactly `≡_ρ`
iff the identity it induces is closed under one-symbol extension; a
closure failure yields a separating test one symbol longer. The
biextensional collapse of an observation system makes tests separate
states and states separate tests. (`Identification.lean`,
`Biextensional.lean`.)

OPEN. The counting bound (`n` Nerode classes force stabilisation by
continuation length `n − 1`); the quantitative (metric or bisimulation
pseudometric) version of all of the above; per-cell Lean certification of
gold labels.

## The measurements

All on the frozen tables `hankel_v0` (metric readout on `ℝ²`) and
`hankel_v1` (order-relation readout, Boolean), one forward pass per prompt.

OBSERVED (`RESULTS_PHASE3_HANKEL.md`, `RESULTS_PHASE3_1.md`). Under the
metric readout, for Pythia-70M and Pythia-410M, serialization of logically
identical premises moves the answer-logit pair 2–5× farther than changing
the logical class does, in every presentation control; readout is at
chance. Scale from 70M to 410M halves both quantities and leaves the ratio
unchanged. Qwen2.5-0.5B-Instruct reads the task (AUROC 0.77) but its ratio
is still 1.35.

OBSERVED (`RESULTS_PHASE3_2.md`, `RESULTS_PHASE3_3.md`). Under the Boolean
readout, Qwen2.5-0.5B-Instruct passes both preregistered gates
(comparative accuracy 0.867; within-class over between-class median
Hamming 0.561), and the non-reading control Pythia-70M fails both (0.456;
1.42), so the gate is valid. Exact invariance fails for every recognizer
(0 of 8 classes with identical serialization profiles; all 40 rows
distinct). The depth-one test family is not closed for any recognizer;
for Qwen the witness is a logically identical pair separated only at
depth two.

OBSERVED, qualifying the above (`RESULTS_PHASE3_3.md`). Under a matched
between-class statistic (median over all cross-class pairs) the control
also falls below 1 (0.72 against Qwen's 0.43), and for Qwen the class
pair that differs only in the direction of all three arrows (`chain`
versus `reversed`) is closer than `chain` is to its own serializations.
Part of the proximity Gate I rewards is shared surface content. Whether
any of it is logical is the question of Phase 3.4.

OBSERVED. Decision columns (`pos > neg`) are constant under the bullet
renderer for every recognizer tested; the comparative readout lifts
Qwen's accuracy from the base rate 0.57 to 0.92 on the same logits.

OBSERVED, generic. Repeated continuations agree with their single
versions on about 95% of tests for reader and non-reader alike; doubling
the prefix costs slightly less than permuting it for both. Neither
carries logical weight.

CONFOUND. The atom-label family changes the metric invariance defect by
about 3×. A first-premise primacy effect on the query mentioned first is
the largest single source of within-class distance in the Boolean table.

OBSERVED (`RESULTS_PHASE3_4.md`). On the surface-controlled contrast,
Qwen2.5-0.5B moves more under a permutation of its three premises than
under a flip of one arrow (`S` 1.27 pooled; 3 of 8 classes favour logic;
bullets 0.75, prose 1.80). The Boolean Gate I proximity is predominantly
surface. The non-reading control sits at the noise value.

## The sentence the paper can currently defend

> For every recognizer tested on a Lean-certified Horn benchmark,
> including an instruction-tuned model that reads the task at 0.84–0.87
> comparative accuracy, a maximal logic-preserving rewrite (permuting the
> premises) moves behavior at least as much as a minimal logic-changing
> rewrite (flipping one arrow). No two logically identical traces are
> behaviorally identical for any recognizer. Reading the task and
> respecting logical identity are distinct properties; the second is
> absent at the pooled level and present only as a weak,
> renderer-dependent tendency.

HYPOTHESIS (Phase 3.3 scale run, preregistered). Within the
instruction-tuned family the Gate I ratio falls with scale while exact
identity remains absent. HYPOTHESIS (Phase 3.4): the bullet-renderer
logic signal on the surface-controlled contrast strengthens with scale.

## Novelty

Settled after full-text reading in `docs/NOVELTY.md`. Not new: order
sensitivity, accuracy–consistency gaps, reordering/duplication as test
relations, permutation-invariant architectures and augmentation. New on
the evidence read: the machine-checked framework (which test relations
follow from which; when a finite family has decided the question), the
exact-versus-approximate identity readout, the surface-versus-logic
statistic with a validity control, and the unmeasured gap between
permutation invariance and logical invariance, which `hankel_v3` is to
measure.
