# Proof-Path Invariance

A Lean-grounded experimental project for measuring whether formally valid intermediate entailments change LLM entailment judgments under controlled presentation conditions.

> This repository does **not** assume that LLM reasoning is categorical or compositional. Lean is used only to certify logical relations used to construct controlled interventions.

## Phase 1 question

Holding the target entailment fixed, does exposing a formally valid intermediate entailment alter an LLM's final entailment accuracy beyond matched presentation controls?

The first experiment compares:

- **D — Direct:** target entailment presented directly.
- **F — Factored:** the same target with a Lean-certified valid intermediate entailment exposed.
- **C — Control:** a length/format-matched presentation that does not supply the valid decomposition.

Primary hypothesis is deliberately weak and two-sided: `e_D != e_F`. No categorical interpretation is attached to this result.

## Formal core

`PPI/Transitivity.lean` certifies the initial implication family:

```text
A -> B
B -> C
-----
A -> C
```

Both a compact proof and an explicitly intermediate proof are included. `PPI/Conjunction.lean` supplies a second certificate family for later robustness tests.

## Research stages

1. Lean-certified logical cases.
2. Controlled D/F/C behavioral measurement.
3. Robustness across realizations and models.
4. Only then: test a compositional behavioral hypothesis.
5. Only after independent structural evidence: consider a categorical model.
6. Geometry is optional and strictly downstream.

See `docs/HYPOTHESES.md`, `docs/PROTOCOL.md`, and `docs/ROADMAP.md`.

## Build

Install Lean via `elan`, then run:

```bash
lake build
```

## Status

Research scaffold. No empirical result or novelty claim is made yet.
