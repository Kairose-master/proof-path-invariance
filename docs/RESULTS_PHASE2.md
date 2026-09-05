# Phase 2 Result — Pythia-70M / S3 premise permutations

Status: **OBSERVED RESULT, raw JSONL pending repository import.**

## Setup

- model: `EleutherAI/pythia-70m`
- revision: `step143000`
- benchmark: `s3_v0`
- 128 formal cases
- 4 formal families
- 6 premise permutations per case
- 768 prompts total
- observable: next-token margin `logit(" YES") - logit(" NO")`

## Binary behavior

All 768 prompts induced `YES`.

```text
YES = 768
NO  = 0
TIE = 0
```

So Phase 2 still cannot support a logical-competence claim at the decision level.
The useful signal remains continuous.

## Within-case permutation sensitivity

```text
mean range             = 0.11499595642089844
median range           = 0.102294921875
mean population stddev = 0.039450170786057795
```

Thus the same formal problem, with the same premises and query, exhibits a
nontrivial spread in YES-vs-NO margin solely from premise serialization order.

## Mean effect relative to identity ordering 123

```text
123   0.000000
132  -0.032772
213  -0.032546
231  -0.016512
312  -0.027114
321  +0.054990
```

The six input permutations therefore do not act as a behaviorally null family.
In particular, full reversal `321` has the opposite signed average effect from
the other four non-identity permutations.

## Family interaction

The effect is not uniform across formal families.

For `321` relative to `123`:

```text
chain3_positive          +0.107265
collider_negative        +0.036686
reverse_start_negative   +0.048237
shortcut_positive        +0.027771
```

This is evidence for a **family-dependent renderer response**, not yet a
family-independent representation of `S3`.

## Interpretation

OBSERVED:

- all binary judgments remain YES;
- premise permutations systematically perturb the continuous margin;
- within-case variation is substantial relative to Phase 1's single-reversal
  mean absolute shift;
- permutation effects differ by formal family;
- `321` has a reproducible positive mean shift across all four current families.

NOT ESTABLISHED:

- logical competence;
- an `S3` representation in model state;
- equivariance;
- compositionality;
- a functorial or categorical semantics.

The next discriminating test is out-of-sample prediction: estimate a
permutation-response law on some cases/families and ask whether it predicts
held-out responses better than family-specific or permutation-agnostic null
models.
