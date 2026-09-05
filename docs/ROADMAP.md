# Research Roadmap

## Phase 0 — Formal certification

Use Lean to certify positive and negative logical cases. Keep the formal layer independent of model APIs.

Exit criterion: all logical case families compile in Lean and every empirical case has traceable certificate provenance.

## Phase 1 — Minimal paired stability measurement

Start with transformations that do not alter the formal problem at all. Benchmark v0 uses only premise-order reversal at the renderer layer.

For each certified case, generate a base prompt and a reversed-premise prompt. Measure binary answer flips.

Exit criterion: deterministic paired generator, positive and negative gold cases, frozen scoring rule, CI validation, and a preregistered model-evaluation protocol.

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
