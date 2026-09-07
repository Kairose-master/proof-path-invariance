# Preregistration — RQ2c (the one-round sandwich law on a fresh seed)

Written and committed before the learned reasoners were run on the fresh
table. Motivation: on the RQ2b table every violation of the composition
law by the 4-round reasoner was a lost derivation, and a post-hoc check
found that its hypothesis-set decisions were sandwiched between two
symbolic budgets on every pair (1.000). That check was not preregistered;
this document turns it into a prediction on new cases.

Fresh table: `rq2/table_c/` (seed 20260907, 200 cases, `LOCK`), and
`rq2/table_c/rq2c_presat.jsonl` (`LOCK_rq2c_presat`); the cases are
disjoint from the training-time holdout only by seed (they were not
excluded from training up to relabelling; overlap with training is
possible but was not inspected), and were never seen by any analysis.

## Law

For a recognizer R with budget k and hypothesis set H_j = T_j({a}):

    T_{j+k-1}{a} ∋ g  ⟹  R(H_j, g; k) = YES,   and   R(H_j, g; k) = YES  ⟹  T_{j+k}{a} ∋ g.   (S)

(S) is the composition law weakened by at most one round on the lower
side; the symbolic reasoner satisfies it with equality.

## Prediction P4

For the 4-round reasoner (`experiments/rq2/iter_r4.pt`, unchanged), the
per-case rate at which (S) holds (mean over queries t and n) has bootstrap
95 % lower bound ≥ 0.95 on every pair (j, k) with j ∈ {1, 2}, k ∈ {1, 2, 3, 4}.
Also reported: the exact composition-law agreement on the same pairs
(expected to fail again at (1, 2) and (2, 1)); the 2-round model on the same
statistics (secondary).

Failure sentence: "On 200 fresh cases the 4-round reasoner's hypothesis-set
decisions were not sandwiched between the symbolic budgets j+k−1 and j+k
(rate …, CI …); the lax one-round description of RQ2b does not generalise."
