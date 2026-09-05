# Benchmark v0 Sampling Note

## Purpose

Increase the number of paired observations without introducing additional
logical families.

## Frozen generator

`scripts/generate_symbolic_cases.py` deterministically creates:

- 128 positive transitivity instances;
- 128 negative non-entailment instances;
- 256 certified case records total;
- 512 prompts after base/reversed pairing.

No random seed is required. Case identifiers and atom labels are deterministic.

## What varies

Only neutral symbol labels vary across case records:

`P0001, Q0001, R0001`, ..., `P0128, Q0128, R0128`.

Within each pair, Phase 1 varies only premise serialization order.

## What does not vary

The benchmark contains only two formal certificate schemas:

1. implication transitivity;
2. the existing non-entailment countermodel schema.

Therefore 256 case records must **not** be described as 256 independent logical
structures. They are repeated symbolic instantiations of two formal families.

The sample size increases precision for the measured renderer sensitivity under
these schemas. It does not by itself establish generalization to arbitrary
logical reasoning.

## Confirmatory use

Only condition `D` from each generated case is consumed by
`generate_paired_benchmark.py`.

Generated `F` and `C` fields exist only to satisfy the legacy case schema.
They are explicitly disabled for Phase 1 and must not be analyzed as
confirmatory interventions.
