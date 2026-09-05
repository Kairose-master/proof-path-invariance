# Proof-Path Invariance

A Lean-grounded project for measuring behavioral stability under formally controlled input transformations.

> The project does **not** assume that LLM reasoning is categorical, compositional, geometric, or proof-theoretically identical to Lean derivations.

## Phase 1

The initial confirmatory question is deliberately small:

> For the same certified entailment problem, does reversing premise serialization order change a model's YES-vs-NO judgment?

The formal problem is unchanged. Only the premise list order changes.

For the first model, the project uses the small pretrained base model `EleutherAI/pythia-70m` at revision `step143000`.

No text is generated. For each prompt `x` the runner measures

```text
margin(x) = logit(" YES" | x) - logit(" NO" | x)
```

and converts the sign into an induced YES/NO judgment. The primary statistic is the paired sign-flip rate under premise reversal.

## Formal core

Lean certifies the logical case families used by the benchmark. Current v0 uses:

- implication transitivity for positive cases;
- a countermodel-backed non-entailment family for negative cases.

The benchmark contains 256 deterministic symbolic records, but these are repeated instantiations of two formal schemas, not 256 independent logical structures.

## Reproducibility

CI checks:

1. Lean certificates build;
2. symbolic case generation;
3. case validation;
4. paired prompt generation;
5. exact benchmark hashes;
6. run-schema and manifest structure.

The frozen paired-prompt SHA-256 is recorded in `experiments/benchmark_v0.lock.json`.

## Run locally

```bash
lake build
python3 -m pip install -r requirements-runner.txt
```

See `docs/RUN_PROTOCOL.md` for the model execution procedure.

## Research escalation

Stronger claims are downstream only:

`formal transformation -> measured instability -> robustness -> minimal structural model`

Composition or category theory enters only if later measurements independently justify those structures.

## Status

Research scaffold. No empirical result or novelty claim is made yet.
