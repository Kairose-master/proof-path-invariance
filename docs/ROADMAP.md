# Research Roadmap

## Phase 0 — Formal certification

Use Lean to certify only the logical relations underlying experimental cases. Start with implication transitivity and conjunction. Keep the formal layer independent of any LLM API.

Exit criterion: all experimental logical relations compile in Lean and every empirical case has a traceable certificate family.

## Phase 1 — Controlled behavioral measurement

Compare direct (`D`), valid-intermediate (`F`), and matched-control (`C`) presentations while holding the target entailment fixed. Measure final binary entailment accuracy and disagreement rates. Do not interpret differences as categorical failures.

Exit criterion: preregistered analysis with enough cases and repeated runs to estimate uncertainty, plus matched controls for presentation length and format.

## Phase 2 — Robustness

Vary proposition names, natural-language realizations, ordering, distractors, depth, and model family. Test whether any Phase 1 effect survives these perturbations.

Exit criterion: replicated effect that cannot be explained by obvious presentation confounds.

## Phase 3 — Compositional behavioral hypothesis

Only after Phases 1–2, test whether behavior across 2-, 3-, and n-step certified decompositions admits a stable compositional description.

## Phase 4 — Categorical model candidate

Only if multiple independently tested composition/equivalence laws are behaviorally preserved, ask whether an approximate structure-preserving categorical model is useful. Category theory enters here as a model candidate, not as a Phase 1 assumption.

## Phase 5 — Optional geometry

Only if the empirical object at Phase 4 provides a justified probabilistic structure, investigate whether a chosen metric or spectral construction yields explanatory geometry. Do not call it intrinsic or semantic without separate evidence.
