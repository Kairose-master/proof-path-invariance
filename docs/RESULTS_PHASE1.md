# Phase 1 Result — Pythia-70M / premise reversal

Status: **OBSERVED RESULT, raw artifacts pending repository import.**

The following summary was produced by the Phase 1 scorer after the first
Pythia-70M run and supplied for repository recording.

## Frozen setup

- model: `EleutherAI/pythia-70m`
- revision: `step143000`
- benchmark: `symbolic_v0`
- paired cases: 256
- confirmatory transform: `premise_reverse`
- primary observable: sign of `logit(" YES") - logit(" NO")`

## Primary result

```text
valid_binary_pairs = 256
tie_pairs          = 0
flips              = 0
flip_rate          = 0.0
```

No tested pair crossed the YES/NO decision boundary under premise reversal.

This supports only the narrow statement that, under this protocol and these two
formal case families, premise reversal did not change the induced binary
judgment.

## Accuracy

```text
base accuracy             = 0.5
premise_reverse accuracy  = 0.5
```

This prevents a stronger interpretation such as "the model preserved a correct
logical judgment." A 0.5 accuracy on the balanced benchmark is compatible with
a strong one-sided response bias. Prediction counts and label-conditioned
margins must be inspected before any competence claim.

## Continuous response displacement

```text
mean(reverse - base) margin = 0.02717304229736328
mean absolute margin shift  = 0.07551097869873047
```

Therefore the renderer intervention was not behaviorally null at the continuous
logit-margin level even though it produced zero sign flips.

## Current interpretation

PROVED by the benchmark/formal layer:

- each paired item preserves the same formal problem;
- only premise serialization order changes.

OBSERVED in the first run:

- zero binary sign flips across 256 pairs;
- nonzero average continuous margin displacement;
- 0.5 accuracy in both variants.

NOT ESTABLISHED:

- correct logical invariance;
- proof-path invariance;
- compositionality;
- a categorical representation;
- an internal semantic mechanism.

## Next analysis

Before adding a richer structural theory, inspect whether the continuous margin
contains label information below the zero threshold. The next scorer reports:

- YES/NO/TIE counts;
- positive/negative gold-conditioned margin summaries;
- base and reversed AUROC;
- margin-shift quantiles.

If AUROC is near 0.5 and predictions are one-sided, the Phase 1 stability result
is best understood as response-bias stability. If margins separate the gold
classes despite poor threshold accuracy, that is a distinct sub-threshold signal
worth testing across additional formally preserving transformations.


## Phase 1.5 diagnosis

The extended scorer showed a complete one-sided response bias:

```text
base:             YES = 256
premise_reverse:  YES = 256
```

Therefore the zero sign-flip result is best interpreted as **response-bias
stability**, not preservation of correct logical judgments.

The continuous margin did not show useful positive-vs-negative separation in the
base rendering:

```text
base AUROC             = 0.478057861328125
premise_reverse AUROC  = 0.228179931640625
```

Because higher margin means stronger YES preference, the reversed rendering
actually ranks negative-family items above positive-family items substantially
more often than chance.

Gold-conditioned mean margins were:

```text
base positive mean = 1.5353775024414062
base negative mean = 1.5621347427368164

reverse positive mean = 1.510061264038086
reverse negative mean = 1.6417970657348633
```

The paired margin shift was also family-dependent:

```text
positive-family mean shift = -0.025316238403320312
negative-family mean shift =  0.07966232299804688
```

This is an interesting continuous renderer effect, but it must not be called a
gold-sensitive logical signal. In `symbolic_v0`, gold label is perfectly
confounded with formal family: all positive items instantiate one schema and all
negative items another. Thus a label-conditioned shift can equally be a
schema-conditioned shift.

### Consequence for the larger program

The first run does **not** support the claim that Pythia-70M has a meaningful
binary logical invariant under premise reversal. It does support a weaker and
more useful empirical observation:

> a formally preserving renderer transformation can induce systematic continuous
> changes in model preference even when the binary decision is frozen by a large
> response bias.

The next experiment must therefore separate transformation structure from both
gold label and schema identity.
