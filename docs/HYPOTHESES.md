# Hypotheses

## Scope discipline

This project does **not** assume that LLM reasoning is categorical, functorial, geometric, Markovian, or proof-theoretically identical to Lean derivations.

Lean is used only to certify formal logical relations used to construct controlled interventions.

## Phase 1 research question

Holding the target entailment fixed, does exposing a formally valid intermediate entailment alter an LLM's final entailment accuracy beyond matched presentation controls?

Let:

- `D` = direct presentation of a certified target entailment;
- `F` = presentation exposing a formally valid intermediate entailment;
- `C` = length/format-matched control that does not supply the valid decomposition.

Primary null hypothesis:

`H0: e_D = e_F`

Two-sided alternative:

`H1: e_D ≠ e_F`

The direction of the effect is not assumed in Phase 1.

## Not yet hypotheses

The following are explicitly deferred:

1. LLM behavior preserves composition laws.
2. LLM behavior admits an approximate functorial model.
3. Predictive distributions induce a useful semantic geometry.
4. HoTT or higher-categorical structure is required.

These claims may only be promoted after preregistered lower-level evidence warrants them.
