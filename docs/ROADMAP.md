# Research Roadmap

## Phase 0 — Formal certification

Use Lean to certify positive and negative logical cases. Keep the formal layer independent of model APIs.

Exit criterion: all logical case families compile in Lean and every empirical case has traceable certificate provenance.

## Phase 1 — Minimal paired stability measurement

Start with transformations that do not alter the formal problem at all. Benchmark v0 uses only premise-order reversal at the renderer layer.

For each certified case, generate a base prompt and a reversed-premise prompt. Measure binary answer flips.

Exit criterion: deterministic paired generator, positive and negative gold cases, frozen scoring rule, CI validation, and a preregistered model-evaluation protocol.

**Status:** first Pythia-70M run completed. Binary sign-flip rate was 0/256,
while both base and reversed accuracy were 0.5. Continuous margin displacement
was nonzero. Phase 1 now moves to secondary diagnosis of response bias and
sub-threshold label separation before adding new transformations.

## Phase 1.5 — Diagnose the continuous signal

Before expanding the transformation family, measure whether the observed
logit margin contains gold-label information despite chance threshold accuracy.

Required diagnostics:

- prediction counts by variant;
- positive/negative gold-conditioned margin distributions;
- AUROC of the margin before and after premise reversal;
- distribution of paired margin displacement.

Exit criterion: determine whether Phase 1's zero flips are best explained by a
one-sided answer bias or by a stable but miscalibrated continuous signal.

**Status:** completed. All 256 base judgments and all 256 reversed judgments
were YES. Base-margin AUROC was 0.4781 and reversed-margin AUROC was 0.2282.
The zero-flip result is therefore response-bias stability, not evidence of
correct logical invariance. Gold-conditioned effects remain confounded with
formal family in v0.

## Phase 2 — Additional certified or audited transformations

Add one transformation family at a time. Each must state exactly what is preserved, what changes, and whether that fact is Lean-checked or only generator-validated.

The first Phase 2 transform family is the full six-element premise-permutation
family on three-premise problems (`S3`). This gives an exact input-side identity
and composition law while keeping the formal problem fixed. The empirical goal
is to test whether response effects generalize across multiple positive and
negative formal families, not to assume that the model itself represents
`S3`.

See `docs/PREREGISTRATION_PHASE2.md`.

**Status:** completed. Phase 2 observed nonzero within-case margin variation
under S3 premise permutations, while all 768 binary judgments remained YES.
Permutation effects differed by formal family.

## Phase 2.5 — Held-out scalar generalization

Run an exploratory post-hoc test on the already-collected Phase 2 raw results.
Estimate permutation effects on training cases/families and evaluate prediction
on held-out cases/families against a zero-effect null.

Exit criterion: determine whether a family-blind scalar permutation law has
positive out-of-sample skill, and whether family-specific interaction materially
improves held-out case prediction.

This phase does not test an S3 representation or compositionality. See
`docs/ANALYSIS_PHASE2_5.md`.

**Status:** completed. Exploratory aggregate leave-one-family-out skill was
positive, but one held-out family failed badly and family-specific effects
improved within-family prediction.

## Phase 2.6 — Confirmatory unseen-family replication

Freeze the Phase 2 pooled permutation coefficients and evaluate them, without
refitting, on eight new Lean-certified formal families.

Primary endpoint:

`skill = 1 - SSE_frozen / SSE_zero`

Confirmatory success criterion:

`aggregate skill > 0`.

See `docs/PREREGISTRATION_PHASE2_6.md`.

**Status:** completed; confirmatory endpoint failed. The frozen pooled scalar
permutation law had aggregate skill -0.1188 versus the zero-effect null on eight
unseen formal families. The previously positive 321 effect reversed sign.

## Phase 2.7 — Explain interaction before adding structure

Do not refit the failed pooled scalar law on the confirmatory holdout.

Use the accumulated Phase 2/2.6 data only for exploratory mechanism diagnosis:
separate permutation effects associated with formal-family structure, local
syntax, conjunction placement, and positional/token context.

The next confirmatory model must be specified from that diagnosis and then
evaluated on a fresh set of unseen formal families.

Exit criterion: identify a compact interaction hypothesis that explains the
sign reversals and yields a new frozen out-of-family prediction. No group,
representation, equivariance, or categorical claim enters before that fresh
replication succeeds.

**Current exploratory clue:** simple single-feature movement summaries are not
enough. A family-specific pairwise premise-precedence decomposition explains a
substantial fraction of the six-point S3 response surface in many Phase 2.6
families (mean family R2 about 0.60), but the coefficients are not yet known to
generalize. See `docs/RESULTS_PHASE2_7_PRELIM.md`.

## Phase 3 — Derivation-sensitive experiments

Only if simpler renderer-level effects are understood, introduce explicit derivations as data and same-context alternative derivations. Test decomposition-specific effects without assuming composition failure.

## Phase 4 — Minimal structural model

Only after robust regularities across multiple transformation families should the project fit a mathematical structure to the behavior.

Category theory is a candidate only if identity/composition/equivalence laws are independently motivated by data.

## Phase 5 — Optional richer structure

Probabilistic geometry, Markov structure, HoTT, or higher categories are not milestones by default. They enter only when a precise empirical object and testable prediction require them.
