# Phase 2.5 Analysis Plan — Held-out permutation generalization

Status: **EXPLORATORY / POST-HOC.**

This analysis was designed after observing the Phase 2 aggregate S3 results.
It is therefore not confirmatory evidence. Its purpose is to decide whether the
next confirmatory experiment is worth running.

## Question

Does a scalar permutation effect learned from some cases or formal families
predict the effect on unseen cases/families better than a zero-effect null?

For each case `q` and non-identity permutation `pi`, define

`d_pi(q) = m_pi(q) - m_123(q)`.

## Test A — leave-one-family-out

For each held-out formal family:

1. estimate `beta_pi = mean d_pi(q)` on the other three families;
2. predict `d_pi(q) = beta_pi` for the held-out family;
3. compare MAE/RMSE against predicting zero effect.

The aggregate skill score is

`1 - SSE_permutation_model / SSE_zero_null`.

Positive skill means the pooled permutation law predicts unseen-family effects
better than assuming premise order has no effect.

## Test B — within-family alternating split

Within each family, sort case IDs and alternate cases into train/test sets.

Compare:

- zero-effect null;
- pooled permutation-only effects;
- family-specific permutation effects.

This diagnoses whether family interaction materially improves prediction once
new cases are held out.

## Interpretation boundary

This analysis concerns only the scalar next-token margin effect.

Even strong held-out prediction does not establish an `S3` representation.
A nontrivial exact group representation on a richer response state requires
separate frozen measurements and composition tests. Scalar margin differences
alone are insufficient for that claim.
