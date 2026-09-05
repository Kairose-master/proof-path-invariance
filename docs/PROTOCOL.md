# Phase 1 Protocol (draft; not preregistered yet)

## Unit of analysis

A case consists of a target entailment plus three controlled presentations:

- `D`: direct presentation;
- `F`: presentation with a Lean-certified valid intermediate entailment;
- `C`: matched control.

The target question and gold truth value are held fixed within a case.

## Primary outcome

Final entailment judgment accuracy. The first implementation should constrain answers to a binary label so scoring does not require semantic interpretation of free-form text.

## Secondary outcomes

- within-case D/F disagreement;
- D/C disagreement;
- model-reported token probability for the binary answer, when the evaluated API exposes comparable log probabilities.

Log probabilities are secondary because API support and calibration differ across model providers.

## Controls

At minimum, balance or record:

- token/character length;
- proposition naming;
- premise order;
- number of statements;
- lexical overlap;
- target truth value;
- inference family;
- decomposition depth.

`C` must not introduce a new valid route to the target. This should be checked formally where possible.

## Analysis discipline

Phase 1 is descriptive/confirmatory only for D versus F after the protocol is frozen. Do not relabel a significant D/F difference as evidence of categorical non-functoriality. Any categorical interpretation is deferred to later phases.

## Before data collection

1. Freeze case generator and control construction.
2. Freeze primary metric and exclusion rules.
3. Choose sample size/power plan.
4. Record model IDs, versions, decoding parameters, and date.
5. Preregister the Phase 1 comparison before inspecting final outcomes.
