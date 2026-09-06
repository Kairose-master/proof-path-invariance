# Experiment Log

## 2026-09-05 — Phase 1 Pythia-70M premise reversal

**Status:** completed; scorer output recorded. Raw manifest/result JSONL are not
yet committed to the repository.

Frozen setup:

- model: `EleutherAI/pythia-70m`
- revision: `step143000`
- benchmark: `symbolic_v0`
- cases: 256 paired items
- transform: `premise_reverse`
- observable: `logit(" YES") - logit(" NO")`

Primary result:

```text
valid_binary_pairs = 256
ties               = 0
flips              = 0
flip_rate           = 0.0
```

Extended diagnosis:

```text
base predictions:             YES 256
premise-reverse predictions:  YES 256
base accuracy:                0.5
reverse accuracy:             0.5
base AUROC:                   0.478057861328125
reverse AUROC:                0.228179931640625
mean margin shift:            0.02717304229736328
mean absolute margin shift:   0.07551097869873047
```

Gold/family-conditioned mean shifts:

```text
positive family: -0.025316238403320312
negative family:  0.07966232299804688
```

Interpretation:

- **OBSERVED:** premise reversal changed continuous logit margins but never
  crossed the YES/NO sign boundary.
- **OBSERVED:** every prompt was classified YES, so zero flips are response-bias
  stability rather than evidence of correct logical invariance.
- **OBSERVED:** base AUROC is approximately chance and reversed AUROC is below
  chance.
- **LIMIT:** gold label is confounded with formal family in `symbolic_v0`, so
  gold-conditioned differences cannot be identified as logical-truth effects.

Machine-readable records:

- `experiments/results/phase1_pythia70m_summary.json`
- `experiments/results/phase1_pythia70m_extended_score.json`
- `docs/RESULTS_PHASE1.md`

Next experiment:

- Phase 2 benchmark: `s3_v0`
- four formal families: two positive, two negative
- 128 formal cases
- all six `S3` premise permutations
- 768 model prompts
- separate notebook: `notebooks/phase2_s3_colab.ipynb`


## 2026-09-05 — Phase 2 Pythia-70M S3 premise permutations

**Status:** completed; scorer output recorded. Raw result JSONL is not yet
committed.

- cases: 128
- prompt rows: 768
- all six premise permutations per case
- predictions: YES 768 / 768
- mean within-case margin range: 0.11499595642089844
- median within-case margin range: 0.102294921875
- mean within-case population SD: 0.039450170786057795
- strongest positive mean permutation effect vs 123: 321 = +0.05498981475830078
- strongest negative mean effect vs 123: 132 = -0.032772064208984375

Interpretation: continuous permutation sensitivity is present, while binary
behavior remains saturated by a YES bias. Effects vary by formal family, so the
next step is held-out prediction rather than a representation claim.

See `docs/RESULTS_PHASE2.md` and
`experiments/results/phase2_pythia70m_s3_summary.json`.


## 2026-09-05 — Phase 2.6 confirmatory unseen-family replication

**Status:** completed; primary confirmatory endpoint failed.

Frozen predictor was evaluated without refitting on eight new Lean-certified
formal families.

```text
cases              = 128
prompt rows        = 768
binary predictions = YES 768 / 768
skill_vs_zero      = -0.11878071118567624
success            = false
```

The frozen model had SSE 4.110979649121873 versus zero-effect-null SSE
3.674517810344696.

Most importantly, the previously positive `321` mean effect
(+0.05498981475830078 in Phase 2) reversed sign on the unseen benchmark
(-0.032113075256347656).

Conclusion: the family-blind additive scalar permutation law did not replicate.
Do not refit it and relabel the result as confirmatory. Preserve this benchmark
as a failed holdout and move to models that explicitly allow family/syntax
interaction or richer response states.

Raw result SHA-256:
`25d970bb9c376583c415c9af227be699469571fab1ce842d76fb2a69d50d5e6d`.

See `docs/RESULTS_PHASE2_6.md`.


## 2026-09-05 — Phase 3.0 Pythia-70M Hankel observation table

**Status:** completed; descriptive under the frozen v0 plan.

- benchmark: `hankel_v0` (32 prefixes × 32 continuation-query tests × 16 controls)
- prompt rows: 16384
- observation: answer-logit pair in ℝ²
- run time: 2026-09-05T17:10:03Z → 17:16:36Z, CPU, 4 single-thread shards

```text
delta_inv (min/median/max over controls)   = 0.394 / 0.947 / 1.432
min class separation                       = 0.030 / 0.123 / 0.185
class pairs separated at delta_inv (of 28) = 0 / 0 / 0
raw numerical rank at 1e-3                 = 1 in every control
AUROC margin vs gold                       = 0.357 / 0.519 / 0.574
closure defect at eps = delta_inv          = 0.519 / 1.133 / 1.533
```

- **OBSERVED:** serialization of logically identical premises moves the logit
  pair farther than changing the logical class does, in every control.
- **OBSERVED:** raw table rank is 1 (common logit offset). Exploratory
  column-centered rank is full (31) at 1e-3 in every control.
- **OBSERVED:** readout at chance; YES/NO map predicts positive on every cell.
- **CONFOUND:** the atom-label family changes `Δ_inv` by about 3×.
- **LIMIT:** `Δ_inv` above class separation means the identifiability
  criterion is not yet testable on this recognizer.

Raw result SHA-256 (uncompressed):
`d5090d9792fe00477fcddcce67b12c52196bc6bfa166445400baf69e7e603e34`.

See `docs/RESULTS_PHASE3_HANKEL.md`.


## 2026-09-05 — Phase 3.1 cross-recognizer replication of `hankel_v0`

**Status:** completed; preregistered gates evaluated.

```text
recognizer   AUROC(med)  Gate R   R=dinv/sep(med)  Gate I
pythia70m    0.519       fail     3.01             fail
pythia410m   0.468       fail     2.95             fail
qwen05b      0.770       pass     1.35             fail
```

- **PREDICTED → OBSERVED:** `pythia410m` fails both gates; `qwen05b` passes
  Gate R and fails Gate I. Reading the task and identifying logical
  equivalents come apart, as recorded before the runs.
- **OBSERVED:** scale alone (70M → 410M) halves absolute order sensitivity
  and class separation together; `R` is unchanged.
- **OBSERVED:** `qwen05b` is the first recognizer separating some class
  pairs beyond `Δ_inv` (up to 17/28 in one control).
- **OBSERVED:** margin sign is miscalibrated in opposite directions by
  renderer/answer map while AUROC is informative.
- **EXPLORATORY:** by renderer, `qwen05b` has `R` median 0.88 (bullets,
  6/8 controls below 1) versus 1.69 (prose, 0/8). Not preregistered.

Raw SHA-256 (uncompressed): `pythia410m`
`aba44f5fc7976361878393f90c61f2a1da041009562d4b4fd861d5a2b6922c3f`;
`qwen05b` `502b8e2750f8480c32f34df1283f22ab013a3bd0d66c8823120db1dcf4546a31`.

See `docs/RESULTS_PHASE3_1.md`.


## 2026-09-05 — Phase 3.2 Boolean Hankel table `hankel_v1` on Qwen2.5-0.5B-Instruct

**Status:** completed; frozen v1 gates evaluated.

```text
Gate R  comparative accuracy (pooled)              = 0.867   pass
Gate I  within/between median Hamming (pooled)     = 0.561   pass
exact   classes with identical serializations      = 0 / 8
closure depth<=1 identical pairs / separated at 2  = 1 / 1  (fork_join-312 vs 321)
idem    a.a vs a agreement 0.957 ; u.u vs u Hamming 84 (serialization 94)
```

- **OBSERVED:** first recognizer/readout pair passing both gates.
- **OBSERVED:** exact invariance fails (0/8); all 40 rows distinct.
- **OBSERVED:** decision columns are constant (all positive) under bullets;
  the comparative readout lifts accuracy 0.57 → 0.92 on the same logits.
- **OBSERVED:** depth-one family not closed; witness is a logically
  identical pair separated only at depth two.
- **OBSERVED:** repeated continuation nearly invisible (96%); doubled
  prefix costs about as much as permutation.
- **LIMIT:** the Boolean ratio and the Phase 3.1 Euclidean ratio are
  different statistics; the gate change is a readout change.

Raw SHA-256 (uncompressed):
`b7e574e7f29c07b1def8aa62955a63f30b18712f57c179e0f8619ad7ba09e23f`.

See `docs/RESULTS_PHASE3_2.md`.


## 2026-09-06 — Phase 3.3 control: Pythia-70M on `hankel_v1`

**Status:** completed; preregistered gates evaluated.

```text
Gate R  comparative accuracy (pooled)          = 0.456   fail (predicted)
Gate I  within/between median Hamming (pooled) = 1.422   fail (predicted; range predicted 0.9-1.1 was too low)
```

- **OBSERVED:** the Boolean Gate I is valid; a non-reading recognizer fails it.
- **OBSERVED:** repeated-continuation agreement 0.950 for the control versus
  0.957 for `qwen05b`: generic, not logical. The Phase 3.2 idempotence
  reading is downgraded accordingly.
- **OBSERVED:** depth-one closure fails for the control as well.

Raw SHA-256 (uncompressed):
`49bf32f90bb2b8aae77887b7a9e2cab7b7eb30a6ca44e16d281249ebc8ca1d6a`.
Scale run (Qwen2.5-1.5B-Instruct) in progress. See `docs/RESULTS_PHASE3_3.md`.


## 2026-09-06 — Phase 3.4 surface-controlled contrast `hankel_v2`

**Status:** completed; frozen Gate S evaluated.

```text
recognizer  S(pooled)  classes perm<flip  compacc   Gate S
qwen05b     1.27       3/8                0.842     fail (predicted)
pythia70m   0.97       4/8                0.480     fail (predicted 'well above 1': wrong; noise value)
qwen05b bullets 0.75 (5/8) ; prose 1.80 (0/8)
```

- **OBSERVED:** for Qwen, permuting the premises moves behavior more than
  flipping one arrow, pooled. The Phase 3.2 Gate I proximity is
  predominantly surface.
- **OBSERVED:** the non-reading control sits at the noise value; the
  contrast is uninformative for it.
- **EXPLORATORY:** across the 20 flips, Spearman correlation between the
  size of the logical change (gold-row Hamming) and the behavioral
  distance is -0.11 for Qwen and -0.38 for the control: a flip's
  behavioral effect does not track how much logic it changes.
- **HYPOTHESIS:** the weak bullet-renderer logic signal grows with scale.
- Scheduling: the 1.5B `hankel_v1` run was restarted so that `hankel_v2`
  on 1.5B runs first (the more informative follow-up); 738 partial rows
  discarded.

Raw SHA-256 (uncompressed): `qwen05b`
`5f6879ee777f44455db6b8de29ea90130d5248f08a67e49bb9c5b671e8999ba4`;
`pythia70m` `a35350b033ca410d476d7f63eac5878857d971aecb1d17223127bd6468ed85c5`.

See `docs/RESULTS_PHASE3_4.md`.


## 2026-09-06 — EXPLORATORY: is the premise-by-premise margin change a diffusion?

Not preregistered. On the `hankel_v1` raw margins (`pos − neg`), treat
appending one clause as one time step and look at the increments.

```text
qwen05b bullets  depth0->1 increments: mean +0.230 sd 0.240 skew +1.06 excess kurtosis +1.00
                 depth1->2 increments: mean +0.306 sd 0.193 skew +1.24 excess kurtosis +3.11
                 R^2 of increment on appended-clause identity: 0.08
                 within-class dispersion across serializations by depth: 0.065, 0.055, 0.052
                 corr(|increment|, level): -0.49
qwen05b prose    same pattern: skew +1.4/+1.7, kurtosis +1.3/+3.5, dispersion flat (0.081, 0.083, 0.079), corr -0.53
pythia70m        increments near zero drift, dispersion flat or falling, corr -0.26/-0.35
```

- **OBSERVED:** increments are right-skewed and heavy-tailed, not Gaussian.
- **OBSERVED:** increments have a positive drift toward the positive
  answer for the reader (about +0.2 to +0.3 logit per appended clause),
  almost independent of which clause is appended.
- **OBSERVED:** dispersion across serializations does not grow with depth;
  a Brownian model predicts growth like the square root of depth.
- **OBSERVED:** larger margins receive smaller increments (negative
  correlation of magnitude with level): saturation, the opposite of a
  geometric (multiplicative) process.
- **HYPOTHESIS:** if a process model is wanted, the first candidate is a
  saturating accumulator with a positive drift (mean reversion toward a
  ceiling), not Brownian or geometric Brownian motion. No stochastic
  layer is required yet: the measured variation is structured (position,
  renderer) and does not accumulate. Actual randomness would need
  sampled outputs, which this project has not collected.


## 2026-09-06 — Phase 3.4 scale: Qwen2.5-1.5B on `hankel_v2`

```text
qwen15b  S pooled 0.99 (4/8) ; bullets 0.80 (6/8, Gate S pass) ; prose 1.25 (1/8) ; compacc 0.889
qwen05b  S pooled 1.27 (3/8) ; bullets 0.75 (5/8)               ; prose 1.80 (0/8) ; compacc 0.842
```

- **PREDICTED → OBSERVED:** `S` lower at 1.5B (1.27 → 0.99). Pass not
  predicted; bullets passes, pooled fails on the class count.
- **OBSERVED:** answer bias reverses (positive rate 0.08).
- **HYPOTHESIS:** logic rises over surface with scale within the family.

Raw SHA-256 (uncompressed):
`d8e8313b42d4b06614a6d23ef272212556c7594da2f20260c22fd2e82c7e3b6f`.


## 2026-09-06 — Phase 3.5 `hankel_v3` (Pythia-70M control, Qwen2.5-0.5B) and Phase 4 constructed recognizers

```text
hankel_v3 pooled      T      U      V     E(base-red, swap)
qwen05b               1.11   1.45   1.50  0/14, 0/9      (predicted T 1.0-1.6, fail, E 0: held)
pythia70m (control)   1.00   0.64   1.50  0/14, 0/9      (predicted near 1, E 0: held)

constructed (seed 0)  val   v2 S         v1 Gate I  v1 identical  v3 V    v3 E
set                   0.993 0.00 (8/8)   0.000      8/8           0.63    0/14, 0/9
seq_aug               0.814 1.37 (3/8)   0.288      0/8           1.54    0/14, 2/9
seq_fixed             0.945 1.16 (3/8)   0.739      0/8           6.0     0/14, 1/9
```

- **OBSERVED:** Qwen2.5-0.5B does not identify consequence-equivalent
  clause sets: a derivable-clause extension moves it as much as a logical
  flip, and more on the accuracy-free columns.
- **OBSERVED:** the set recognizer is exactly the syntactic quotient
  (8 distinct rows of 40, closed depth-one family, S = 0) and only partly
  the semantic quotient (V 0.63, E 0). Permutation invariance plus 99%
  accuracy does not yield logical invariance.
- **PREDICTION FAILURES:** seq_aug S 1.37 (predicted < 1; model
  under-converged at 0.81); seq_fixed passes Gate I at 0.74 (surface
  sharing, as in Phase 3.4); the set recognizer's depth-one family is
  closed on hankel_v1 (predicted not).
- **LIMIT:** one seed; toy models.

Raw SHA-256 (uncompressed): `qwen05b` v3
`7024f1a53869fa80…`; weights and evaluation hashes in
`experiments/results/constructed/manifest.json`.

See `docs/RESULTS_PHASE3_5.md`, `docs/RESULTS_PHASE4.md`.


## 2026-09-06 — Phase 4 seed-1 replication

```text
set       s1: val 0.990 | ident 8/8 rows 8 closed | S 0.00 | V 0.80 E 2/14   (predicted V 0.4-0.9, E 0-3: held)
seq_aug   s1: val 0.895 | ident 0/8 | S 0.51 (7/8) | V 0.75 E 0/14, swap 5/9
seq_fixed s1: val 0.950 | ident 0/8 | S 0.58 (5/8) | V 2.42
```

- **OBSERVED:** the set recognizer replicates; partial semantic
  identification (V 0.6-0.8), near-zero exact identification.
- **OBSERVED:** S for the causal recognizers varies by 2x across seeds
  (seq_aug 1.37 -> 0.51; seq_fixed 1.16 -> 0.58). Seed-0 augmentation
  failure was under-convergence; the fixed-order model's drop shows S is
  noisy for these models on 80 tests. Seeds 2-3 queued.


## 2026-09-06 — EXPLORATORY: seq_aug at 18000 steps

```text
val 0.981 | S 0.49 (7/8) | Gate I 0.307, identical classes 0/8, rows 40/40 | V 1.17, E 0/14
```

- **PREDICTED → OBSERVED:** converged augmentation passes Gate S.
- **OBSERVED:** approximate permutation invariance only (no exact
  identities); no semantic identification (V 1.17), unlike the set
  recognizer (V 0.62–0.80).


## 2026-09-06 — Phase 4 seeds 2–3; S calibration recorded

```text
seq_aug   S over 4 seeds: 1.37 0.51 1.12 0.61 (median 0.87) | V: 1.54 0.75 3.00 1.92
seq_fixed S over 4 seeds: 1.16 0.58 0.81 0.43 (median 0.69) | V: 6.0 2.42 2.25 1.26
set       S 0, 0 | V 0.62 0.80
synthetic gold+noise (no invariance): S 0.60 pooled, 8/8
```

- **CORRECTION (recorded):** S is one-sided; accuracy alone reaches S 0.5-0.6.
  S > 1 is diagnostic; S < 1 is not evidence of invariance. Phase 3.4 and
  NOVELTY N3 amended.
- **OBSERVED:** no causal recognizer has an exactly identical class at any
  seed; V above 1 in 7 of 8 causal runs, below 1 in both set runs.


## 2026-09-06 — Phase 3.5 scale: Qwen2.5-1.5B on `hankel_v3`

```text
qwen15b  T 0.62 (5/8)  U 0.82  V 1.01 (bullets 0.67, prose 1.10)  E 0/14, 0/9
qwen05b  T 1.11 (3/8)  U 1.45  V 1.50                             E 0/14, 0/9
```

- **OBSERVED (no prediction recorded):** T and V fall with scale; V pooled
  sits at the no-identification value, bullets 0.67; E stays 0.
- Raw SHA-256 (uncompressed): `9b0d4effd058adf79416eaf56a211d92fa131c42d2f63f974eceaafdd2dbc640`.


## 2026-09-06 — Phase 4.1: set seeds 2-3; equivalence objective

```text
set s2, s3            V 0.48, 0.57  E 1/14, 1/14   (predicted V 0.4-0.9, E 0-3: held)
set_contrast s0, s1   V 0.53, 0.80  E 1/14, 0/14   (predicted V < 0.4, E >= 4: FAILED)
```

- **OBSERVED:** the central set result holds at four seeds (V 0.48-0.80).
- **PREDICTION FAILED:** a symmetric-KL objective on derivable-extension
  pairs does not lower V or raise E on held-out classes; it closes the gap
  on simple classes only. The semantic half is not supplied by an
  objective that names it on the training distribution.

