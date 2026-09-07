# RQ2f result — dose–response in clause count and in thinking budget

Status: **RUN AS PREREGISTERED (`docs/PREREGISTRATION_RQ2F.md`).** Model
`gemini-3.1-flash-lite`; table `rq2/table_c/rq2f_dose.jsonl` (2259
requests); results `experiments/rq2/results_f/flash_lite_all.jsonl`,
analysis `analysis.json` (`rq2/analyze_dose.py`). The B0 rerun of D, F,
F1, C1 agreed with the RQ2e decisions on 100 % of rows (temperature 0).

## P7a holds: more redundant clauses hurt more

On the 106 cases having all three doses (net effect on the target, B0):
C1 −0.057, C2 −0.217, C3 −0.283; C3 − C1 = −0.226 [−0.311, −0.151].
On all cases: C1 −0.070 [−0.120, −0.020] (n = 200), C2 −0.206 (n = 155),
C3 −0.283 (n = 106).

## P7b: the distraction hypothesis, not the expected count hypothesis

N1 (one irrelevant clause, not derivable, invisible from the hypothesis)
−0.217 [−0.278, −0.157] against C1 −0.071 (n = 198);
δ = N1 − C1 = −0.146 [−0.212, −0.081]. The CI lies entirely in the
*distraction* cell: an irrelevant clause costs about three times as much
as a redundant one, and about as much as two redundant ones. The
preregistered expectation (count hypothesis, |δ| ≤ 0.05) was wrong. The
cost of an added clause is therefore not a cost of length: a clause that
is derivable from the theory is cheap and a clause that is not is
expensive, even when neither touches the target's derivation.

## P8 fails: the budget response is a step, not a slope

| budget (tokens actually used) | acc(D) | net F | net F1 | net C1 | net L / dis_L |
|---|---:|---:|---:|---:|---:|
| B0 (0) | 0.78 | +0.155 [0.110, 0.210] | +0.220 | −0.070 [−0.120, −0.020] | — |
| B256 (~140) | 0.80 | +0.140 [0.090, 0.195] | +0.200 | −0.070 [−0.125, −0.015] | −0.80 / 0.80 |
| B1024 (~300) | 1.00 | 0.000 | 0.000 | 0.000 | −1.00 / 1.00 |

P8a: F(B0) − F(B256) = 0.015 [−0.030, 0.055], fails. P8b: C1(B256) −
C1(B0) = 0.000 [−0.050, 0.050], fails. P8c (no reversal) holds. As
preregistered: "the effects of shortening and redundancy did not shrink
monotonically with the thinking budget (F +0.155 → +0.140 → 0; C −0.070 →
−0.070 → 0); the budget is not a grade for this model." About 140
thinking tokens change nothing measurable; about 300 make the model the
oracle.

## Reading

Three things are now known about this model at zero budget. (i) A
derivable clause that shortens the target's derivation helps, and the
direct clause helps most (+0.16, +0.22). (ii) Any added clause that does
not shorten it hurts, in proportion to how many are added (−0.06, −0.22,
−0.28 for one, two, three redundant clauses), and an irrelevant clause
hurts three times as much as a redundant one (−0.22 vs −0.07): the model
is *less* disturbed by a clause it could have derived than by one it
could not, so the cost depends on the clause's relation to the theory,
not on its presence. (iii) The thinking budget removes all of this in a
single step between roughly 140 and 300 tokens. For the graded account,
(i) is the predicted term, (ii) is a second term the account does not
have, with a structure (derivable < irrelevant) that is logical rather
than lexical, and (iii) says that this recognizer's budget behaves like a
threshold rather than a grade: the graded description applies to the
constructed reasoners, whose budget is in rounds, and not to this model's
tokens.
