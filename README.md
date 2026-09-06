# Proof-Path Invariance

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22495706.svg)](https://doi.org/10.5281/zenodo.22495706)

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
python3 -m pip install -r requirements-runner.txt   # torch, numpy, transformers, safetensors, huggingface_hub
```

See `docs/RUN_PROTOCOL.md` for the model execution procedure.

## Research escalation

Stronger claims are downstream only:

`formal transformation -> measured instability -> robustness -> minimal structural model`

Composition or category theory enters only if later measurements independently justify those structures.

## First empirical result

The first Pythia-70M / premise-reversal run produced:

- 256 / 256 valid binary pairs;
- 0 sign flips;
- 0.0 flip rate;
- 0.5 base accuracy;
- 0.5 reversed accuracy;
- mean absolute logit-margin shift of 0.07551097869873047.

This is not evidence of correct logical invariance because accuracy is at chance
on the balanced benchmark. It is evidence only that premise reversal did not
cross the YES/NO decision boundary in this run, while still moving the continuous
logit margin.

See `docs/RESULTS_PHASE1.md`.

## Phase 3.0 Hankel table

`hankel_v0` renders 32 Horn prefix traces against 32 continuation-query tests
under 16 presentation controls and records both answer logits. On Pythia-70M,
serialization of logically identical premises moves the logit pair farther
than changing the logical class does, in every control; the readout is at
chance. See `docs/RESULTS_PHASE3_HANKEL.md`.

Phase 3.1 ran the same table on Pythia-410M and Qwen2.5-0.5B-Instruct under
preregistered gates. Scale alone changed nothing; the instruction-tuned model
reads the task (AUROC 0.77) but still does not identify logical equivalents
at the pooled level (`Δ_inv` / class separation 1.35). See
`docs/RESULTS_PHASE3_1.md`.

Phase 3.2 replaced the metric readout with order relations only
(`hankel_v1`). On that Boolean table Qwen2.5-0.5B-Instruct passes both
gates: comparative accuracy 0.87 and logically identical rows closer than
logically distinct classes at the median (ratio 0.56), while exact
invariance still fails in every class. See `docs/RESULTS_PHASE3_2.md`.

## Phase 3.4–3.5 and Phase 4

`hankel_v2` contrasts permutations (maximal surface change, no logical
change) with single-arrow flips (minimal surface change, logical change).
Qwen2.5-0.5B moves more under permutation (`S` 1.27); Qwen2.5-1.5B sits at
the boundary (0.99; 0.80 under the bullet renderer). `hankel_v3` adds
derivable-clause extensions (Lean-certified schema) to measure
identification of consequence-equivalent clause sets; Phase 4 trains
recognizers with invariance by architecture, by data, or neither, and
evaluates them on the same tables. See `docs/NOVELTY.md`,
`docs/DRAFT_OUTLINE.md`.

## Status

The formal framework, frozen benchmark families, raw model runs, constructed
recognizer checkpoints, and analysis summaries are committed. The submission
manuscript and arXiv-ready source are in `arxiv/`; claims are scoped to the
small-model and synthetic settings documented there.

## Citation

Concept DOI (all versions): [10.5281/zenodo.22495706](https://doi.org/10.5281/zenodo.22495706). Version v0.1.1: [10.5281/zenodo.22495707](https://doi.org/10.5281/zenodo.22495707).

```
Jang, Jinu (2026). proof-path-invariance. Zenodo. https://doi.org/10.5281/zenodo.22495706
```
