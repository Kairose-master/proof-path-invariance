# Phase 2.8 Analysis Plan — Formal-role order model

Status: **EXPLORATORY / POST-HOC.**

Phase 2.7 showed that family-specific pairwise precedence terms compress many
within-family S3 response surfaces, but family-specific coefficients are not an
acceptable explanation.

Phase 2.8 asks whether those effects can be predicted from mechanically derived
premise roles rather than family identity.

## Fixed exploratory feature class

For each permutation, derive:

- source-premise order;
- target-premise order;
- conjunction-premise order;
- direct-query-edge order;
- source-vs-target precedence;
- whether the final premise carries each of those roles.

No family ID is used as a predictor.

## Evaluation

Use leave-one-family-out ordinary least squares.

For each held-out family:

1. fit the role-order model on the other seven families;
2. predict all five non-identity effects in the held-out family;
3. compare SSE with the zero-effect null.

Aggregate skill:

`1 - SSE_role_model / SSE_zero`.

This analysis is still post-hoc because the feature class was chosen after
observing the failed Phase 2.6 result and the Phase 2.7 decomposition.

## Decision rule for research progression

- If aggregate LOFO skill <= 0: do not build a fresh confirmatory benchmark from
  this role model.
- If aggregate LOFO skill > 0 but unstable across folds: refine the mechanism
  only descriptively; do not confirm yet.
- If aggregate LOFO skill is positive and reasonably distributed across folds:
  freeze this exact feature class and coefficients from existing data, then
  construct a fresh unseen-family benchmark for the next confirmatory phase.

No representation, equivariance, or categorical claim is permitted at this
stage.
