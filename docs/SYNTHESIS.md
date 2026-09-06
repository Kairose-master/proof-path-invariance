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

## The sentence the paper can currently defend

> (Provisional, pending Phase 3.4.) For a small instruction-tuned language model read through order
> relations at the answer position, traces that are logically identical
> in a Lean-certified Horn semantics are, at the median, separated by
> fewer behavioral tests than traces from distinct logical classes,
> while no two logically identical traces are behaviorally identical;
> for base models of the same or larger size the ordering is reversed.
> Reading the task and identifying logical equivalents are therefore
> distinct properties, the second weaker than the first and present only
> approximately.

HYPOTHESIS (Phase 3.3 scale run, preregistered). Within the
instruction-tuned family the ratio falls with scale while exact identity
remains absent.

## Novelty: not established

Adjacent prior work: premise-order sensitivity of LLM reasoning (Chen et
al. 2024); automata and weighted-automata extraction from recurrent
networks via L* and Hankel matrices (Weiss et al. 2018; Okudono et al.
2020; Ayache et al. 2018); probabilistic bisimulation (Larsen–Skou) and
its pseudometrics; Chu spaces (Pratt). The narrowest defensible
difference: the behavioral quotient is compared, on a machine-checked
logical quotient, by a preregistered gate with a validity control, using
a threshold-free readout that makes the comparison an exact statement
about a finite Boolean table. Whether that difference is publishable
novelty is not yet assessed against a full literature search.
