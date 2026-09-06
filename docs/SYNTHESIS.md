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

OBSERVED (`RESULTS_PHASE3_5.md`). Qwen2.5-0.5B does not identify
consequence-equivalent clause sets: a Lean-certified derivable-clause
extension moves it as much as a one-arrow logical change (`T` 1.11) and
more on accuracy-free columns (`V` 1.5); no pair of logically identical
rows is identical (`E` 0).

OBSERVED (`RESULTS_PHASE3_5.md`, scale). Qwen2.5-1.5B on the same table:
`T` 0.62, `V` 1.01 pooled (0.67 under bullets, 1.10 under prose), `E` 0.
Scale moves the accuracy-free statistic toward, not past, identification.

OBSERVED (`RESULTS_PHASE4.md`). A recognizer that is permutation- and
repetition-invariant by construction and 99% accurate on held-out classes
has a behavioral quotient equal to the syntactic quotient (8 distinct rows
of 40, `S` 0, closed depth-one family) and only partly the semantic one
(`V` 0.63, `E` 0). A fixed-order recognizer passes Gate I (0.74) without
ever seeing a permutation: Gate I rewards shared surface content.

CORRECTION (recorded in `RESULTS_PHASE3_4.md`, `RESULTS_PHASE4.md`). The
surface-versus-logic statistic `S` is one-sided: a synthetic accurate
recognizer with no invariance reaches 0.5–0.6, and fixed-order toy
recognizers reach 0.4–0.8. `S > 1` (Qwen-0.5B pooled, prose at both
scales) shows surface dominance beyond accuracy; `S < 1` shows nothing
further. The beyond-accuracy statistic is `V`: above 1 for every LLM, the
control, and seven of eight causal toy runs; below 1 only for the
architecturally invariant recognizer (0.62, 0.80; two seeds).

OBSERVED (`RESULTS_PHASE4.md`, Phase 4.1). The set recognizer's partial
semantic identification holds at four seeds (`V` 0.48–0.80). Training the
same recognizer with an equivalence loss on derivable-extension pairs
(the semantic rewrite itself) leaves `V` and `E` unchanged (0.53, 0.80; 1,
0 of 14): the objective closes the gap on simple classes and not on
classes with disconnected or gated clauses. Accuracy, architectural
invariance, and an objective on the equivalence all fail to supply the
semantic half; none computes the closure.

## The sentence the paper can currently defend

> On a Lean-certified Horn benchmark read through order relations at the
> answer position, no recognizer tested, measured or constructed, treats
> two logically identical traces identically. For small instruction-tuned
> language models that read the task, permuting the premises and appending
> a derivable clause each move behavior at least as much as reversing one
> arrow. A recognizer built to be permutation-invariant and trained to 99%
> accuracy is exactly the syntactic quotient and only partly the semantic
> one, and an objective that names the semantic equivalence on the
> training distribution does not change that. Reading the task, permutation
> invariance, and logical invariance are three distinct properties, in that
> order of difficulty; accuracy, architectural invariance, and an
> equivalence objective each fail to supply the third.

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
