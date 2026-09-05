# Phase 2.7 Analysis Plan — Explain the failed scalar law

Status: **EXPLORATORY / POST-HOC AFTER FAILED CONFIRMATORY TEST.**

Phase 2.6 rejected the current family-blind additive scalar permutation law.
The purpose of Phase 2.7 is not to rescue that law by refitting it. It is to
identify a compact renderer-local interaction hypothesis that could explain why
permutation effects change magnitude or sign across formal families.

## Data status

The Phase 2.6 benchmark remains a failed confirmatory holdout. Phase 2.7 may use
it for exploratory diagnosis only.

## Mechanical features

For each formal case, derive from the frozen benchmark text:

- which premise positions mention the query antecedent;
- which premise positions mention the query consequent;
- whether a premise contains a conjunction marker (`both`);
- whether a premise directly contains both query atoms;
- how those premise roles move under each non-identity permutation;
- whether the final serialized premise contains each role.

These are renderer-local observables. They are not claims about internal model
state.

## Primary exploratory questions

1. Does moving a conjunction-bearing premise earlier or later systematically
   change the YES-vs-NO margin?
2. Does the position of a premise mentioning the query antecedent or consequent
   explain sign reversals?
3. Is the Phase 2 -> Phase 2.6 reversal concentrated in particular syntactic
   roles rather than in permutation identity itself?
4. Can one compact interaction hypothesis be stated without using family names
   as free categorical parameters?

## Guardrails

Do not:

- refit the failed Phase 2 pooled coefficients and call the result confirmatory;
- use family ID itself as the final explanatory mechanism;
- claim an S3 representation, equivariance, or categorical semantics;
- select only favorable families.

A useful Phase 2.7 output is a small hypothesis such as

`effect = f(permutation, conjunction-position movement, query-role position)`

that can be frozen before another fresh unseen-family benchmark.

## Exit criterion

Advance only if the exploratory summaries suggest a compact, falsifiable
interaction rule whose coefficients/features can be frozen before new model
collection.
