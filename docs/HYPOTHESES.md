# Hypotheses

## Scope discipline

This project does **not** assume that LLM reasoning is categorical, functorial, geometric, Markovian, or proof-theoretically identical to Lean derivations.

Lean certifies formal logical cases. Deterministic renderers create stimuli. Model responses are empirical observations.

## Minimal Phase 1 question

For a fixed formally certified problem, does a deterministic renderer-level transformation that preserves the formal problem change the model's binary judgment?

For benchmark v0 the only confirmatory transformation is:

- `premise_reverse`: reverse the order of the same premises.

Let `q` be a certified case, `E(q)` its base rendering, and `E_rev(q)` the rendering with premise order reversed.

The gold label is identical because the underlying formal problem is identical.

Observed pairwise instability is:

`I_rev(q) = 1[M(E(q)) != M(E_rev(q))]`

and the primary descriptive statistic is the mean flip rate across paired cases.

No claim about proof paths, composition, categories, or internal semantics follows from a nonzero flip rate.

## Deferred transformations

- atom renaming / aliasing;
- redundant valid information;
- explicit valid intermediates;
- derivation factorization;
- composition-sensitive interventions.

These require separate control arguments or stronger formal representations before confirmatory use.

## Not yet hypotheses

1. LLM behavior preserves composition laws.
2. LLM behavior admits an approximate functorial model.
3. Predictive distributions induce a useful semantic geometry.
4. HoTT or higher-categorical structure is required.

Stronger structure is introduced only if lower-level measurements independently motivate it.
