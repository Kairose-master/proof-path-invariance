# RQ2c result — the one-round sandwich law holds on a fresh seed

Status: **RUN AS PREREGISTERED (`docs/PREREGISTRATION_RQ2C.md`).** Fresh
table `rq2/table_c/` (seed 20260907; cases sha256 `a65f577a…`, presat
`346ea642…`), reports in `experiments/rq2/results_c/*.json`.

Law (S): T_{j+k−1}{a} ∋ g ⟹ R(H_j, g; k) = YES, and R(H_j, g; k) = YES ⟹
T_{j+k}{a} ∋ g. The composition law is the case where both bounds coincide.

## P4 holds

| pair (j, k) | (S) holds, 4-round model [95 % CI] | exact composition law, 4-round model | (S) holds, 2-round model | exact law, 2-round model |
|---|---|---|---|---|
| (1, 1) | 1.000 [1.000, 1.000] | 1.000 | 0.993 [0.983, 1.000] | 0.892 |
| (1, 2) | 1.000 [1.000, 1.000] | **0.895** [0.868, 0.922] | 0.993 [0.983, 1.000] | 0.993 |
| (1, 3) | 1.000 [1.000, 1.000] | 0.983 | 0.998 [0.993, 1.000] | 0.998 |
| (1, 4) | 1.000 [1.000, 1.000] | 1.000 | 0.998 [0.993, 1.000] | 0.998 |
| (2, 1) | 1.000 [1.000, 1.000] | **0.818** [0.782, 0.850] | 1.000 [1.000, 1.000] | 0.990 |
| (2, 2) | 1.000 [1.000, 1.000] | 0.990 | 0.998 [0.993, 1.000] | 0.998 |
| (2, 3) | 1.000 [1.000, 1.000] | 0.998 | 1.000 [1.000, 1.000] | 1.000 |
| (2, 4) | 1.000 [1.000, 1.000] | 1.000 | 0.998 [0.993, 1.000] | 0.998 |

Every pair has lower bound ≥ 0.95 for the 4-round model; **P4 holds**, with
(S) satisfied on every case and every pair. The exact composition law
fails again at (1, 2) and (2, 1), as expected from RQ2b, with almost the
same rates (0.895 vs 0.897; 0.818 vs 0.830). The 2-round model satisfies
(S) at ≥ 0.993 and the exact law at ≥ 0.990 on the primary pairs.

## Reading

The 4-round learned reasoner's behaviour on hypothesis sets is now a law,
not a failure report: its decision from H_j at budget k lies between the
symbolic reasoner's decisions at budgets j+k−1 and j+k, on 200 fresh cases
without exception. It is a *lax* graded reader: it never derives more than
the algebra allows, and never less than the algebra allows with one round
of slack. The composition equation is the special case in which the slack
is zero; the model trained under a smaller budget is within 0.01 of that
case.
