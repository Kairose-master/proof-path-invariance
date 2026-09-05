# Phase 2.6 Result — Confirmatory unseen-family replication

Status: **CONFIRMATORY RESULT — PRIMARY ENDPOINT FAILED.**

## Frozen setup

The test used the pre-frozen Phase 2 scalar permutation coefficients without
refitting on the confirmatory benchmark.

Primary success rule:

`aggregate skill_vs_zero > 0`.

The benchmark contained 128 cases from eight unseen Lean-certified formal
families, with six premise permutations per case (768 prompts).

## Primary result

```text
n                 = 640 non-identity effects
MAE               = 0.060371392965316774
RMSE              = 0.08014615213316811
SSE_frozen        = 4.110979649121873
SSE_zero          = 3.674517810344696
skill_vs_zero     = -0.11878071118567624
confirmatory pass = false
```

The frozen scalar permutation predictor performed worse than predicting no
permutation effect at all.

Therefore the confirmatory hypothesis

> a family-blind scalar permutation-response law learned from Phase 2 predicts
> entirely new formal families better than a zero-effect null

is **not supported**.

## Binary behavior

All 768 prompts were again predicted `YES`.

This confirms that the binary observable remains saturated by the same strong
response bias and cannot be interpreted as logical competence.

## Observed mean effects in the unseen benchmark

```text
132  -0.0160675048828125
213  -0.028473854064941406
231  -0.0063915252685546875
312  -0.05844306945800781
321  -0.032113075256347656
```

The most important change is `321`.

Phase 2 estimated:

`321 = +0.05498981475830078`.

The unseen-family confirmatory benchmark observed:

`321 = -0.032113075256347656`.

So the strongest apparent shared effect from Phase 2 not only weakened but
reversed sign out of family.

## Interpretation

**PROVED / frozen design:** the benchmark, coefficients, and success rule were
fixed before confirmatory model collection.

**OBSERVED:** the primary confirmatory endpoint failed.

**REJECTED narrow hypothesis:** a single family-blind additive scalar
permutation law is not a reliable cross-family description for this
Pythia-70M renderer setup.

**NOT rejected:** the broader possibility that response transformations have
structure conditional on formal family, local syntax, token positions, or a
richer response state.

The correct next move is not to rescue the scalar law by refitting on this
confirmatory data. This dataset should remain a failed confirmatory holdout.

Any next structural model must explain why transformation effects reverse
across formal families and must be tested on a fresh holdout.
