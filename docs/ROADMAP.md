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

## Phase 2 — Additional certified or audited transformations

Add one transformation family at a time. Each must state exactly what is preserved, what changes, and whether that fact is Lean-checked or only generator-validated.

Candidates include atom aliases, alternative serializations, and carefully controlled redundant information.

## Phase 3 — Derivation-sensitive experiments

Only if simpler renderer-level effects are understood, introduce explicit derivations as data and same-context alternative derivations. Test decomposition-specific effects without assuming composition failure.

## Phase 4 — Minimal structural model

Only after robust regularities across multiple transformation families should the project fit a mathematical structure to the behavior.

Category theory is a candidate only if identity/composition/equivalence laws are independently motivated by data.

## Phase 5 — Optional richer structure

Probabilistic geometry, Markov structure, HoTT, or higher categories are not milestones by default. They enter only when a precise empirical object and testable prediction require them.
