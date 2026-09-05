# Phase 2 Preregistration Draft — S3 premise permutations

Status: **DRAFT — design specified before Phase 2 model collection.**

## Motivation

Phase 1 found a complete YES response bias in Pythia-70M. Premise reversal did
not change the binary sign but did move the continuous YES-vs-NO margin. The
gold-conditioned effect was confounded with formal family.

Phase 2 therefore asks a narrower structural question without relying on binary
correctness:

> For the same certified three-premise formal problem, how does the continuous
> model response vary across all six premise-order permutations?

## Transformation family

For ordered premise positions `(1,2,3)`, use every element of the symmetric
group `S3`:

```text
123, 132, 213, 231, 312, 321
```

Each variant contains exactly the same premise multiset, query, gold label, and
formal certificate. Only serialization order changes.

The group structure is known **on the input transformations**. This does not
imply that the model response forms a representation of `S3`.

## Formal families

Phase 2 must include more than one positive and more than one negative schema so
that gold label is not identical to schema identity. The benchmark generator
must record both `gold` and `family` explicitly.

No model run begins until those families and their Lean certificates are frozen.

## Observable

Primary continuous observable remains

`m(x) = logit(" YES" | x) - logit(" NO" | x)`.

Binary sign is retained descriptively but is not the central Phase 2 endpoint,
because Phase 1 showed a large one-sided response bias.

For case `q` and permutation `pi`, record `m_pi(q)`.

## Primary Phase 2 questions

1. **Permutation sensitivity**: how much within-case variance is induced by
   premise permutation?
2. **Permutation-specific effect**: after controlling for case/family, do
   particular permutations produce reproducible margin shifts?
3. **Family interaction**: do permutation effects generalize across formal
   families with the same gold label?
4. **Composition test**: can a response transformation law estimated on some
   permutations predict responses to composed permutations better than a null
   model?

The composition analysis must use held-out cases or families. A tautological
identity such as scalar telescoping is not evidence of compositional structure.

## Minimal structural criterion

Do not claim an `S3` representation merely because the input transformations
form `S3`.

A structural claim requires an independently fitted response map `A_pi` on a
response representation `R(q)` and an out-of-sample test of

`A_(sigma o pi) R(q) ~= A_sigma A_pi R(q)`.

With scalar margin alone, only permutation effects are measured. Richer logit
or hidden-state representations may be introduced later, but must be frozen
before testing representation laws.

## Interpretation boundary

Phase 2 can establish systematic transformation-response structure. It cannot,
by itself, establish proof identity, semantic equivalence inside the model,
categorical reasoning, or a functor from syntax to model states.
