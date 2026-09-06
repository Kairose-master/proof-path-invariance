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

