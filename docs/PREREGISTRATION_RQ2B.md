# Preregistration — RQ2b (the composition law: a hint buys exactly its depth)

Written and committed before any learned recognizer was run on the RQ2b
table. The symbolic control was run first (deterministic).

Frozen table: `rq2/table/rq2b_presat.jsonl`, sha256
`5e42376dd5e01a7f4f6b04856a74a4596f8378ea6579786acce489928456a910`,
1200 rows = 200 RQ2 base theories × 2 queries (target t, non-derivable n)
× 3 hypothesis sets H_j = T_j({a}), j ∈ {0, 1, 2}. Generator
`rq2/build_presat.py`; |H_1| ∈ {2: 137, 3: 60, 4: 3}, |H_2| ∈ {3: 89,
4: 80, 5: 31}.

## 1. The law being tested

`RecognitionPaths/Graded.lean`, `entailsK_presaturate`: for the graded
closure, T_k(T_j S) = T_{j+k} S. Read on a budgeted recognizer R:

    R(H_j, goal; k) = R(H_0, goal; j + k)        (★)

i.e. pre-saturating the hypotheses by j rounds and reading with budget k
gives the answer of budget j + k from the bare hypothesis. This is an
equation *between budgets*, so it is testable only on recognizers with a
budget knob; it is the first prediction that follows from the graded
structure rather than from the closure alone.

## 2. Recognizers

| recognizer | budgets k | hypothesis input | role |
|---|---|---|---|
| symbolic k-round reasoner | 0–6 | set | control: (★) holds exactly by `rounds_add` |
| IterReasoner trained at 4 rounds, single-atom hypotheses (`experiments/rq2/iter_r4.pt`, unchanged) | 0–6 | multi-hot hypothesis flag; readout = max over hypothesis-atom states (one atom: identical to the trained readout, verified to 1e-4) | **primary** |
| IterReasoner trained at 2 rounds (`iter_r2.pt`) | 0–6 | same | secondary |

The primary model has never seen a multi-atom hypothesis set: (★) is
tested out of the training format, on the same weights that gave the RQ2
result. Decisions = argmax, ties → NO.

## 3. Primary comparison

For each pair (j, k) the agreement rate agree(j, k) = fraction of cases
(mean over the two queries) with R(H_j; k) = R(H_0; j + k), with a paired
case bootstrap 95 % CI (B = 5000, seed 0).

Primary pairs are those where the symbolic yes-rate on the target changes
between budget k and budget j + k, so that agreement is not achievable by
a constant answer: (j, k) ∈ {(1, 2), (2, 1), (2, 2), (1, 3)}; symbolic
yes-rates on t: (H_0, 2) 0.00 → (H_0, 3) 0.885 → (H_0, 4) 1.00.

**Prediction P3**: for the primary model, every primary pair has
agree(j, k) with CI lower bound ≥ 0.95.

Effect criterion: P3 holds iff all four lower bounds are ≥ 0.95. Also
reported: agreement on t and n separately, yes-rates on both sides, the
median |margin difference| on t, and accuracy at every (j, k).

Sample size: 200 structures; at agreement 0.97 the CI half-width is about
0.025, so 0.95 is resolvable. Rows come from the RQ2 holdout, never used
in training (theories excluded up to relabelling).

## 4. Secondary

* S1 The 2-round model: same pairs; does (★) hold beyond its training
  budget?
* S2 Budget 0 (never trained): R(H_j; 0) should equal R(H_0; j), i.e. the
  model must answer "goal ∈ hypotheses" at zero rounds; reported, not
  predicted.
* S3 Failure mode analysis if P3 fails: whether disagreement is located at
  cases with |H_j| ≥ 4 (multi-hot magnitude) or at depth-4 cases.

## 5. Failure sentence

If P3 fails: "On 200 fresh Horn cases the learned reasoner did not satisfy
the composition law T_k ∘ T_j = T_{j+k} out of its training format
(agreement …, CI …); the graded-monad description fits its budget
behaviour (RQ2) but not its hypothesis-set behaviour, and the law is a
property of the symbolic reasoner that the learned one does not inherit."

## 6. Not claimed

No claim about LLMs: a single forward pass has no budget knob, so (★)
cannot be tested on them here. The LLM version of (★) requires a budget
(e.g. chain-of-thought length) and is future work.
