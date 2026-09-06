# Phase 3.5 — Semantic-rewrite table `hankel_v3`

Status: **INPUTS FROZEN. STATISTICS AND PREDICTIONS FROZEN BEFORE ANY OUTPUT IS READ.**

## Question

`Specification.lean` separates two recognizers: one that factors through
the set of clauses (invariant under permutation and repetition by
construction) and the ideal one that factors through the consequences
(invariant under all of `≡_L`). Set-LLM proves the first and stops
(`docs/NOVELTY.md`, N4). This table measures the gap: does a recognizer
identify clause sets that are logically identical but syntactically
different?

## Rows

For each of the eight classes with base serialization `123`:

| Kind | Rows | Relation to base | Surface | Logic | Certification |
|---|---:|---|---|---|---|
| `perm` | 24 | permutation | all clauses move | same | `Horn.logicalEquiv_of_perm` |
| `red` | 14 | base + one derivable single-atom clause | +1 clause | same | `Horn.logicalEquiv_append_derivable` |
| `red_i` vs `red_j` | 9 pairs (3 classes) | two derivable extensions | one clause differs, same count | same | `Horn.logicalEquiv_derivable_extensions` |
| `flip` | 20 | one arrow reversed in place | one clause differs, same count | changed | validator: gold row changes |

The `red_i`/`red_j` pairs and the `flip` rows are the two length-matched
one-clause edits: identical surface budget, different logical status.
Columns: the depth-≤1 family, 80 Boolean tests per renderer, two
renderers, 4224 prompts.

## Frozen statistics (pooled over renderers)

```text
T = median over classes of d_red  / d_flip        semantic +1-clause rewrite vs logical change
U = median over the 3 classes with >=2 red rows of d_swap / d_flip   length-matched
V = median over classes of d_red_free / d_flip_free                  free columns only
E = identical full profiles: (base, red) pairs of 14; (red_i, red_j) pairs of 9
```

Free columns are preference tests whose gold is a tie for both rows;
there the ideal recognizer is exactly identical and accuracy imposes
nothing, so `V` measures identification beyond correctness.

- **Gate T (semantic identity outweighs a logical change):** `T < 1` and
  at least 6 of 8 classes with `d_red < d_flip`.
- **Gate U (length-matched):** `U < 1` in all 3 classes.
- `E` is reported as counts; no gate.

## Recorded predictions (before data)

- `pythia70m` (control): `T` and `U` near 1; `E = 0`.
- `qwen05b`: `T > 1` (the added clause is a surface change comparable to
  a flip; predicted 1.0–1.6), `U` near 1, `E = 0`. Gates fail.
- `set` (constructed, permutation-invariant by architecture): `d_perm = 0`
  exactly; `T` below 1 (predicted 0.3–0.8) because flips change gold
  decisions the model tracks; **`V` is the informative number**: predicted
  between 0.5 and 1, i.e. partial identification at best; `E` small but
  possibly nonzero (0–3 of 14).
- `seq_aug`: like `set` but with `d_perm > 0`; `T` between 0.5 and 1.
- `seq_fixed`: like `qwen05b`.

The result this project wants to know is `V` and `E` for `set`: whether a
recognizer that is syntactically invariant by construction becomes, under
training on entailment, semantically invariant. If `V` is near 0 and `E`
is large, training supplies the semantic half; if `V` is near 1, it does
not, and permutation invariance is not logical invariance.

## Calibration on a synthetic recognizer

Before any model run, the analysis was applied to a synthetic recognizer
that outputs the gold label plus symmetric Gaussian noise (no
identification beyond correctness). It gives `T = 0.51 (8/8)`,
`U = 0.53 (3/3)`, `V = 1.40`, `E = 0`. So `T` and `U` are passed by mere
accuracy and are **not** evidence of identification; only `V` near 0 and
`E > 0` are. Gates T and U remain as stated, but the interpretation is
fixed here: they measure accuracy-driven proximity; `V` measures
identification.

## Confounds

`red` rows are one clause longer than the base; `T` therefore mixes a
length effect with the semantic rewrite. `U` and `V` are the controls for
that: `U` is length-matched, `V` removes columns where accuracy forces
agreement.
