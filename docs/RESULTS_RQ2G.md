# RQ2g result — the learned reader composes with itself, is monotone, and has no unit

Status: **RUN AS PREREGISTERED (`docs/PREREGISTRATION_RQ2G.md`).** Fresh
cases (`rq2/table_c/rq2_cases.json`); results
`experiments/rq2/results_g/{iter_r4,iter_r2}.json`; script `rq2/run_compose.py`.

## P9 holds: self-composition is sandwiched with slack ≤ 2, and mostly with slack 1

4-round model, composite decision model(hyps = R_k{a}, goal; j) against
T_m{a}, mean over the target and the non-derivable atom, 200 cases:

| (j, k) | slack-2 sandwich [CI] | slack-1 sandwich [CI] | upper bound | exact = T_{j+k} |
|---|---|---|---:|---:|
| (1,1) | 1.000 [1, 1] | 1.000 | 1.000 | 1.000 |
| (1,2) | 1.000 [1, 1] | 1.000 | 1.000 | 0.818 |
| (1,3) | 1.000 [1, 1] | **0.890 [0.860, 0.917]** | 1.000 | 0.870 |
| (2,1) | 1.000 [1, 1] | 1.000 | 1.000 | 0.895 |
| (2,2) | 1.000 [1, 1] | 1.000 | 1.000 | 0.990 |
| (2,3) | 1.000 [1, 1] | 1.000 | 1.000 | 1.000 |
| (3,1) | 1.000 [1, 1] | 1.000 | 1.000 | 0.983 |
| (3,2) | 1.000 [1, 1] | 1.000 | 1.000 | 0.998 |
| (3,3) | 1.000 [1, 1] | 1.000 | 1.000 | 1.000 |

The theorem's bound (slack 2, `LaxGraded.comp_sandwich`) holds on every
case of every pair. The composite is in fact within one round of slack on
eight of nine pairs; only (j, k) = (1, 3), one round applied to a
three-round output, loses a second round on 11 % of cases. The upper
bound (never more than the closure) holds without exception. The 2-round
model's self-composition agrees exactly with T_{j+k} on ≥ 0.990 of cases
on every pair (slack-1 and slack-2 rates ≥ 0.990).

## P10 holds: the 4-round reader is monotone

Violations (YES on {a}, NO on {a, y}) at k = 1, 2, 3: 0.000, 0.000, 0.000
(2-round model: 0.000, 0.013 [0.006, 0.021], 0.000). So the hypothesis of
`LaxGraded` holds empirically for the primary model on this test, and the
theorem's conclusion is not a coincidence.

## The unit law fails

R_0 = id would mean: at zero rounds the reader answers YES exactly for the
hypothesis atoms. Agreement with the identity: 0.571 on S = {a} (that is
4/7: a constant answer) and 0.545 on S = T_1{a}; 2-round model 0.714 and
0.686. Zero rounds was never trained, and the readout at zero rounds does
not read the hypothesis flag. The learned family therefore satisfies the
composition laws of a lax graded monad on budgets k ≥ 1 and does not
satisfy its unit law.

## Reading

The learned 4-round reader, fed its own output, behaves as the lax graded
theory says it must (slack adds to at most 2), and better than it must
(slack 1 on eight of nine pairs). It is monotone. It has no unit. In the
programme's terms: the operations and equations observed on this
recognizer are those of an ℕ-graded family of monotone operators with a
lax multiplication T_{j+k−1} ⊆ R_j ∘ R_k ⊆ T_{j+k} (occasionally
T_{j+k−2}) and no unit, sitting inside the graded closure monad, which is
what remains of that monad after training. The 2-round model is within
0.01 of the monad itself on multiplication, and equally unitless.
