# Phase 3 — Hankel observation table `hankel_v0`

Status: **INPUTS FROZEN. ANALYSIS PLAN v0 FROZEN. Pythia-70M run completed: see `docs/RESULTS_PHASE3_HANKEL.md`.**

This benchmark is designed from the definitions in the `recognition-paths`
repository (`RecognitionPaths/Recognition.lean`). It collects the observations
that the Recognition Factorization Theorem asks about, and nothing else.

## Mathematical objects being estimated

Fix the Horn signature `Σ` (clauses `A → B`, `A ∧ B → C`, `A → B ∧ C`), the
query set `Q` of pairs (hypothesis atom, goal atom), and the observation space
`O = ℝ²` holding both answer logits.

The recognizer is `ρ : Σ* × Q → O`, read at the answer position.

| Symbol | Definition | Status |
|---|---|---|
| `u ≡_L v` | `∀ q, Entails(Γ(u), q) ⇔ Entails(Γ(v), q)` | PROVED as a setoid; permutation invariance PROVED (`Horn.logicalEquiv_of_perm`) |
| `u ≡_ρ v` | `∀ z, q, ρ(uz, q) = ρ(vz, q)` | definition |
| `u ≈_ρ v` | `∀ x, z, q, ρ(xuz, q) = ρ(xvz, q)` | definition; congruence PROVED |
| `≈_{ρ,T}` | the same restricted to a finite test family `T` | definition; `≈_ρ ⊆ ≈_{ρ,T}` PROVED |

The theorem: `≡_L ⊆ ≈_ρ` holds iff a unique representative-preserving
`F : L → B` exists. An experiment can only measure a finite restriction, so
the experimental object is the **Hankel table**

```text
H_ρ(u, t) = ρ(u, t),   t = (z, q),
```

whose rows are prefix traces and whose columns are continuation-query tests.
Its row-equality relation is the finite restriction `≡_{ρ,T}` with
`T = {([], z, q)}`.

## Table structure

| Axis | Size | Content |
|---|---:|---|
| rows `u` | 32 | 8 Horn logical classes × 4 serializations (123, 231, 312, 321) |
| columns `t` | 32 | 8 continuation traces × 4 queries |
| relabelings | 4 | neutral atom label families |
| renderers | 2 | bullet list vs. prose |
| answer maps | 2 | YES/NO vs. True/False |
| prompts | 16384 | one per cell per control combination |

The eight logical classes were chosen so that the class-level 8 × 32 gold
matrix has full row rank 8, pairwise distinct rows, and 112/256 YES cells.
Three columns are answered directly by the continuation alone; they are kept
as `direct_answer_control = true` sanity cells.

The four serializations are the three cyclic rotations, which are closed under
composition, plus the full reversal used in Phase 1.

## What is certified and what is not

- **PROVED (Lean, `recognition-paths`):** rows inside one logical class are
  logically identical for every query, by `Horn.logicalEquiv_of_perm`.
- **OBSERVED-BY-GENERATOR, not Lean-certified:** every cell's gold label,
  computed by Horn forward chaining and independently re-derived by
  `validate_hankel_benchmark.py`.
- **NOT certified:** that atom relabeling, renderer choice, and answer map are
  logically irrelevant. They are presentation controls and are reported as
  such.
- **OPEN:** per-cell Lean certification via a decidable Horn closure.

## Frozen analysis plan (v0)

All quantities are computed on the raw `observation = [pos_logit, neg_logit]`
pairs. Distances use the Euclidean metric on `ℝ²` unless stated.

### A. Invariance defect (primary descriptive quantity)

For each control combination `κ` and each logical class, the empirical
two-sided invariance defect over the finite test set `T`:

```text
Δ_inv(κ) = max over classes, over serialization pairs (u, v) in the class,
           of max over t in T of ‖H(u, t) − H(v, t)‖₂.
```

Also report the mean over pairs and columns, and the per-class values.

### B. Separation (does behavior distinguish logically distinct rows?)

For each pair of logical classes `(c, c')`, the minimum over serializations
of the maximum over `t` of `‖H(u, t) − H(v, t)‖₂`. A pair is *behaviorally
separated at tolerance ε* when this exceeds ε.

The comparison that the theorem's two directions require is:

- `Δ_inv` small relative to between-class separation supports (but does not
  prove) `≡_L ⊆ ≈_{ρ,T}`;
- every logically distinct pair separated supports `≈_{ρ,T} ⊆ ≡_L` on `T`.

### C. Numerical rank of the table

Singular values of the 32 × 64 real matrix obtained by flattening each `ℝ²`
cell, per control combination, and of the pooled 32 × (64·16) matrix. Report
the number of singular values above `10⁻³ · σ₁` and above `10⁻² · σ₁`.
Rank is reported for the sub-tables of 16 and 24 rows (nested by class) to
check whether it stabilises as rows are added.

### D. Gold-conditioned readout

AUROC of `pos_logit − neg_logit` against gold, per control combination.
This is reported so that Phase 1's chance-level accuracy is not silently
assumed away; it is not a primary endpoint.

### E. Closure diagnostic (what the finite table can and cannot conclude)

`RecognitionPaths/Identification.lean` proves that a test family containing
the direct queries induces exactly `≡_ρ` if and only if the induced identity
is closed under appending one symbol. `hankel_v0` has continuations of depth
at most one, so only the lowest level of that criterion is checkable:

- Let `T₀ = {([], q)}` be the four direct-query columns. Two rows `u`, `v`
  agree on `T₀` at tolerance ε when `‖H(u,([],q)) − H(v,([],q))‖₂ ≤ ε` for
  all four `q`.
- For each of the seven single-clause continuations `a`, the row `ua`
  restricted to `T₀` is available as the four columns `(a, q)`.
- The closure defect at ε is the maximum, over row pairs that agree on `T₀`
  and over `a`, of `max_q ‖H(u,(a,q)) − H(v,(a,q))‖₂`.

A large closure defect is a concrete refinement witness: it names the
column `(a, q)` that separates rows the direct queries could not. Checking
closure of the full 32-column family would require depth-two continuations
`(a z, q)` and is deferred to a `hankel_v1` table. Rows that agree on all
32 columns are therefore reported as "not separated by `T`", never as
`≡_ρ`-identical.

### Pre-specified decision language

- No result on this table is described as evidence that the model "has" a
  logical quotient, a monoid, or a monad.
- Small `Δ_inv` with poor separation is reported as "the finite test family
  does not separate logical classes", not as invariance.
- `Δ_inv` comparable to separation is reported as failure of the finite
  restriction of `≡_L ⊆ ≈_ρ` on `T`.

## Run protocol

```bash
python3 scripts/generate_hankel_benchmark.py --out hankel_v0.jsonl
python3 scripts/validate_hankel_benchmark.py hankel_v0.jsonl
python3 scripts/verify_hankel_lock.py hankel_v0.jsonl
python3 scripts/run_hf_hankel.py --prompts hankel_v0.jsonl \
    --out runs/hankel_v0_pythia70m.jsonl --run-id <run-id>
```

Model: `EleutherAI/pythia-70m`, revision `step143000`, CPU, float32, no
generation. Candidate tokens `" YES"`, `" NO"`, `" True"`, `" False"` are
single tokens in this tokenizer (ids recorded in the lock file).

Raw observation rows must be stored unmodified; derived statistics go in a
separate file.
