# Phase 3.2 — Boolean Hankel table `hankel_v1`

Status: **INPUTS FROZEN. ANALYSIS PLAN v1 FROZEN. NO MODEL DATA COLLECTED.**

## Why a second table

Phase 3.0 read the table through a Euclidean metric on the raw logit pair.
That choice is not part of the theory: `≡_L`, `≈_ρ`, `L`, `B`, the Nerode
quotient and the closure criterion are all defined by exact equalities of
test outcomes, with no metric. The metric entered only to compare real
numbers, and it brought an artefact with it (the common logit offset that
made the raw table rank 1).

`hankel_v1` removes the metric. Each cell still records the logit pair, but
the analysis reads it only through **order relations**:

```text
decision    D(u; z, q)       = [ pos > neg ]
preference  P(u; z, q1, q2)  = [ margin(z, q1) > margin(z, q2) ]
```

Both are threshold-free and invariant to the common offset. The table
becomes a **Boolean Chu space**: rows are prefixes, columns are Boolean
tests. The logical table (gold) is a Chu space of the same kind, so the
canonical map `F : L → B` of the Recognition Factorization Theorem is
checked by exact equality of row profiles, not by a tolerance.

The preference columns also give a readout that the YES bias cannot
saturate: comparative accuracy is defined on query pairs whose gold labels
differ, and a model that always says YES scores at chance on it rather than
at the base rate.

## Structure

| Axis | Size | Content |
|---|---:|---|
| rows | 40 | 8 logical classes × (4 serializations `123, 231, 312, 321` + doubled prefix `123x2`) |
| continuations | 57 | empty; 7 single clauses; all 49 ordered pairs, including the 7 repeats `a.a` |
| queries | 4 | `ad, ae, bd, ce` |
| logit cells | 228 per row per renderer | |
| Boolean columns | 570 per renderer | 228 decision + 342 preference |
| controls | 2 renderers | relabeling `sym1`, answer map YES/NO fixed |
| prompts | 18240 | |

Continuation depth two makes the depth-one family's closure checkable
(`Identification.lean`: a direct family identifies `≡_ρ` iff it is closed
under one-symbol extension). Repeated continuations `a.a` and doubled
prefixes `u.u` test the idempotence consequence `ww ≈_ρ w`
(`Recognition.lean`, `contextEquiv_dup_of_invariant`).

Controls are reduced because Phase 3.0 found the atom-label family to
change the scale of order sensitivity by about 3×; `sym1` is kept.

## Certification status

- PROVED (Lean, `recognition-paths`): serializations of one class are
  logically identical (`Horn.logicalEquiv_of_perm`); `u.u ≡_L u`
  (`Horn.logicalEquiv_dup`); the closure criterion and the idempotence
  consequence.
- Generator-validated, not Lean-certified per cell: every gold label.
- Not certified: renderer irrelevance.

## Frozen analysis plan (v1)

All distances are Hamming counts: the number of Boolean tests on which two
rows differ. Reported per renderer and pooled (1140 columns).

- **A. Exact invariance.** For each class, whether all four serializations
  have identical profiles; within-class Hamming distances, split by
  decision and preference columns. `F` exists exactly on the table iff all
  eight classes are identical.
- **B. Separation.** Minimum Hamming distance between rows of distinct
  classes, per class pair; number of class pairs whose separation exceeds
  the largest within-class distance; ratio of within-class median to
  between-class median (the Boolean analogue of Phase 3.1's `R`).
- **C. Biextensional collapse.** Number of distinct row profiles (of 40)
  and distinct column profiles (of 570), against 8 distinct logical rows.
- **D. Readout.** Decision accuracy and positive rate; comparative accuracy
  on defined query pairs.
- **E. Exact closure.** Among row pairs with identical profiles on the
  depth-≤1 columns, how many are separated by a depth-2 column; the
  witness pair and column.
- **F. Idempotence.** Agreement rate of `a.a` with `a` columns across rows;
  Hamming distance between `u` and `u.u` rows, against the serialization
  distances for reference.

### Pre-specified decision language

- Gate R (Boolean): comparative accuracy `> 0.55` pooled.
- Gate I (Boolean): within-class median Hamming / between-class median
  Hamming `< 1`, pooled.
- Identical profiles are reported as "not separated by these tests", never
  as identity under `≈_ρ`.
- A closure violation is reported with its witness as the column that a
  depth-three table would need; it is not an error.

## Run protocol

```bash
python3 scripts/generate_hankel_v1_benchmark.py --out hankel_v1.jsonl
python3 scripts/validate_hankel_v1_benchmark.py hankel_v1.jsonl
python3 scripts/verify_hankel_v1_lock.py hankel_v1.jsonl
python3 scripts/run_hf_hankel.py --prompts hankel_v1.jsonl --out <raw> \
    --run-id <id> --model-id <model> --revision <rev> --expected-rows 18240
python3 scripts/analyze_hankel_v1.py --raw <raw> --out <summary>
```

Planned recognizers: the Phase 3.1 set (`pythia-70m`, `pythia-410m`,
`Qwen2.5-0.5B-Instruct`), unchanged runner.
