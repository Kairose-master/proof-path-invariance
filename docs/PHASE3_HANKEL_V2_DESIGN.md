# Phase 3.4 — Surface-controlled contrast `hankel_v2`

Status: **INPUTS FROZEN. ANALYSIS PLAN AND PREDICTIONS FROZEN BEFORE ANY OUTPUT IS READ.**
Runs on `qwen05b` and the `pythia70m` control were launched at
2026-09-06T01:35:43Z; this document is committed while they run and before
any output is read.

## Question

Phase 3.3 showed that the Boolean Gate I rewards proximity that is partly
shared surface content: for `qwen05b` the class pair `chain`/`reversed`,
which differs only in the direction of all three arrows, is closer than
`chain` is to its own serializations. Does anything in the within-class
proximity track logic rather than words?

## Design

Each of the eight classes has a base serialization `123` and two kinds of
neighbours of it.

| Kind | Rows | Surface change | Logical change | Certification |
|---|---:|---|---|---|
| permutation (`231`, `312`, `321`) | 24 | maximal: all three clauses move | none | `Horn.logicalEquiv_of_perm` |
| single-arrow flip (`f1`–`f3`) | 20 | minimal: two atoms swap inside one clause, in place | yes: the gold row changes | validator check, forward chaining |

Flips are made only on single-atom clauses and only kept when the gold row
over the 32 cells changes; 20 of 24 candidates survive. Columns are the
depth-≤1 family (8 continuations × 4 queries), read as 80 Boolean tests per
renderer as in `hankel_v1`; two renderers; 3328 prompts.

## Frozen statistic and gate

For each class, `d_perm` = median Hamming(base, permutation), `d_flip` =
median Hamming(base, flip). Pooled over renderers:

```text
S = median over classes of d_perm / d_flip
```

- **Gate S (logic outweighs surface): `S < 1`** and at least 6 of 8
  classes with `d_perm < d_flip`.
- `S > 1`: a one-arrow logical change moves behavior less than reordering
  the same clauses; the within-class proximity of Gate I is surface.

Also reported: per-class distances, the size of each flip's logical change
(Hamming of gold decision rows), comparative and decision accuracies.

## Recorded predictions (before data)

- `pythia70m`: `S` well above 1 (surface only).
- `qwen05b`: `S` between 0.8 and 1.5, with fewer than 6 of 8 classes
  favouring logic; Gate S fails. The Phase 3.3 `chain`/`reversed` result
  makes a pass unlikely.
- `qwen15b` (run after the Phase 3.3 scale run): `S` lower than for
  `qwen05b`; whether it passes is not predicted.

## Interpretation boundary

Gate S passing would show that, for this recognizer, a minimal logical
change is behaviorally larger than a maximal logic-preserving change. It
would not show invariance. Gate S failing would show that the Boolean Gate
I proximity is predominantly surface for this recognizer, and would move
the project's defensible claim back to the Euclidean and Boolean
measurements of serialization sensitivity.
