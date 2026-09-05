# Phase 3.1 Preregistration — Cross-recognizer replication of `hankel_v0`

Status: **FROZEN BEFORE INSPECTING ANY RESULT OF THESE RUNS.** Runs were
launched at 2026-09-05T17:27Z; this document was committed at 17:29Z while
they were in progress (184 of 32768 rows written, none read).

## Question

Is the Phase 3.0 null result a property of the table or of the recognizer?
The "malfunctioning machine" reading of Phase 3.0 says Pythia-70M simply
cannot read the task, and a recognizer that can would identify logically
identical traces. Phase 3.1 tests that reading by changing only `ρ`.

## What is held fixed

- benchmark: `hankel_v0`, unchanged, SHA-256
  `9491e21e82e00b3fab20bbcb6bf6cced10285edbad47d0851cbc61d017513cdf`;
- runner: `scripts/run_hf_hankel.py`, one forward pass per prompt, float32,
  CPU, both answer logits recorded;
- analysis: `scripts/analyze_hankel.py`, frozen plan sections A–E, plus the
  dimensionless ratio below;
- answer candidates `" YES"`, `" NO"`, `" True"`, `" False"`, each verified
  to be a single token in both tokenizers.

## Recognizers

| Tag | Model | Revision | What it separates |
|---|---|---|---|
| `pythia410m` | `EleutherAI/pythia-410m` | `step143000` | same family, ~6× parameters: scale alone |
| `qwen05b` | `Qwen/Qwen2.5-0.5B-Instruct` | `main` (resolved commit recorded in manifest) | different family, instruction-tuned |

## Pre-specified statistics

Because logit scale and offset differ across models, the cross-model
comparison uses a dimensionless quantity:

```text
R = Δ_inv / median class separation        (per control; report min/median/max)
```

together with the seven frozen quantities of Phase 3.0.

Phase 3.0 baseline (Pythia-70M): `R` min / median / max over controls =
see `experiments/results/phase3_hankel_v0_summary.json`
(`aggregate.ratio_delta_inv_over_median_separation`); every value exceeds 1.

## Pre-specified decision rules

Two independent gates, evaluated per recognizer on the median over the 16
controls:

- **Gate R (reads the task):** `AUROC > 0.55`.
- **Gate I (identifies logical equivalents):** `R < 1`, i.e. logically
  identical rows are closer than the typical pair of logically distinct
  classes.

The "malfunctioning machine" reading predicts that a recognizer passing
Gate R also passes Gate I.

## Recorded predictions (before data)

- `pythia410m`: fails Gate R (AUROC near 0.5) and fails Gate I (`R > 1`).
- `qwen05b`: passes Gate R (AUROC roughly 0.6–0.75) and **fails** Gate I
  (`R` roughly 0.7–1.5, median above 1).

Prediction summarised: reading the task and identifying logical equivalents
come apart. If `qwen05b` passes Gate I with `R < 0.5`, or fails Gate R, the
prediction is wrong and is reported as such.

## Interpretation boundary

Passing both gates on one recognizer would justify, and only then, running
the idempotence test `ww ≈_ρ w` and building `hankel_v1`. It would not
establish that the recognizer realises the logical quotient; it would make
the identifiability criterion testable.
