# Phase 2.6 Preregistration — Confirmatory unseen-family replication

Status: **FROZEN BEFORE MODEL COLLECTION.**

## Purpose

Phase 2 observed systematic continuous margin changes under all six premise
permutations. Phase 2.5, explicitly post-hoc, found positive aggregate
leave-one-family-out skill but substantial family interaction.

Phase 2.6 converts that exploratory signal into a confirmatory test.

## Fixed hypothesis

A scalar permutation-response law estimated from Phase 2 will predict
permutation-induced margin changes on entirely new formal families better than
a zero-effect null.

For non-identity permutation `pi`:

`d_pi(q) = m_pi(q) - m_123(q)`.

The frozen Phase 2 predictor is:

```text
132  -0.032772064208984375
213  -0.032546043395996094
231  -0.016511917114257812
312  -0.027113914489746094
321  +0.05498981475830078
```

These coefficients MUST NOT be refit on Phase 2.6 data.

## Confirmatory benchmark

- benchmark: `s3_unseen_v0`
- formal families: 8 total
- positive families: 4
- negative families: 4
- neutral-symbol cases per family: 16
- formal cases total: 128
- S3 variants per case: 6
- prompts total: 768

The eight families are new relative to the four families used in `s3_v0`.
Some introduce conjunction inside premises to make the replication materially
harder than renaming or duplicating prior implication-graph schemas.

## Frozen model protocol

- model: `EleutherAI/pythia-70m`
- revision: `step143000`
- device: CPU
- dtype: float32
- candidates: `" YES"`, `" NO"`
- observable: next-token logit margin
- no generation

## Primary endpoint

Let `y_i` be observed non-identity permutation effects and `p_i` the frozen
Phase 2 predictions.

`skill = 1 - SSE_frozen / SSE_zero`

where the zero-effect null predicts `d_pi(q)=0`.

### Confirmatory success rule

`aggregate skill_vs_zero > 0`.

No per-family cherry-picking is allowed for the primary conclusion.

## Secondary diagnostics

Report:

- MAE and RMSE of the frozen predictor;
- per-family skill;
- observed mean effect for each permutation;
- binary prediction counts.

These are descriptive and do not replace the aggregate primary endpoint.

## Interpretation boundary

A successful replication supports:

> a partially shared scalar response law for formally preserving premise
> permutations that predicts unseen formal families better than a zero-effect
> null.

It does NOT establish:

- logical competence;
- an internal semantic representation;
- an `S3` representation;
- equivariance;
- composition laws;
- categorical or functorial semantics.
