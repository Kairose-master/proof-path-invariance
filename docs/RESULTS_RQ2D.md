# RQ2d result — a language model with a thinking budget

Status: **RUN AS PREREGISTERED (`docs/PREREGISTRATION_RQ2D.md`).** Model
`gemini-3.1-flash-lite` (temperature 0, raw prompt), budgets B0 = no
thinking, B1 = thinking budget 1024 (mean ≈ 400 thinking tokens used).
Table `rq2/table/rq2d_llm.jsonl` (5600 requests, all parsed as YES/NO).
Results `experiments/rq2/results_d/flash_lite_all.jsonl`, analysis
`analysis_flash_lite.json` (`rq2/analyze_llm.py`).

## Gate

| budget | acc(D) over t and n | acc(D, t) | dis_L | reads? |
|---|---:|---:|---:|---|
| B0 (no thinking) | 0.90 | 0.80 | 0.80 | yes |
| B1 (thinking 1024) | 1.00 | 1.00 | 1.00 | yes |

Both budgets pass the gate. At B1 the model is the oracle on this table:
accuracy 1.000 on every condition and query, dis_F = dis_F1 = dis_C = 0,
dis_L = 1. It identifies every redundant extension and reads every logic
change. This is the first recognizer in the programme, other than the
constructed ones at sufficient budget, with an exactly logical decision
profile on a table.

## Primary P5: fails

Decision-change rates on the target at B0: dis_F 0.155 [0.105, 0.205],
dis_F1 0.200, dis_C 0.140 [0.095, 0.190], dis_L 0.80.
Δ(B0) = dis_F − dis_C = 0.015 [−0.055, 0.080]; Δ(B1) = 0.
I = 0.015 [−0.055, 0.080]. **P5 fails** on both clauses (CI includes 0;
Δ(B0) < 0.10). As preregistered:

> "On 200 fresh Horn cases, gemini-3.1-flash-lite did not show a larger
> decision change for depth-shortening extensions than for depth-preserving
> ones at the low thinking budget relative to the high one (I = 0.015,
> CI [−0.055, 0.080]); the budget-relative-depth account does not transfer
> to this language model's thinking budget."

## Exploratory: the changes have opposite signs

The unsigned rate hides a directional pattern. At B0, with D at 0.80
accuracy on the target (all gold YES):

| extension | fixes (D wrong → X right) | breaks (D right → X wrong) | net accuracy change [95 % CI] |
|---|---:|---:|---|
| F (minimal shortening) | 0.145 | 0.010 | **+0.135 [0.085, 0.190]** |
| F1 (direct clause) | 0.200 | 0.000 | +0.200 [0.145, 0.255] |
| C (depth-preserving) | 0.025 | 0.115 | **−0.090 [−0.140, −0.040]** |

Signed difference F − C: +0.225 [0.165, 0.285] at B0 and 0 at B1. The
shortening clause makes the budget-less model *more* often right and the
equally redundant depth-preserving clause makes it *less* often right;
both move about 15 % of decisions, which is why the unsigned Δ is null.
The preregistered statistic assumed, from the constructed reasoners, that
C would change nothing; for this model a redundant clause has a cost.
This is an observation for a follow-up preregistration (RQ2e, fresh
seed), not a result.

Pre-saturation at B0 (part B): accuracy on t from H_0 0.80, H_1 0.71,
H_2 0.945 (|H_1| = 2: 0.67, 3: 0.80; |H_2| = 3: 0.92, 4: 0.95, 5: 1.00); at
B1 all 1.00. Not monotone in j: a one-round hint of two atoms hurts, a
two-round hint helps. Thinking tokens at B1 relative to D (paired): F
+6 [−6, +18], F1 −78 [−94, −62], C +31 [+21, +42], L +112 [+89, +135]. The
direct clause saves thinking, the minimal shortening saves none, the
redundant preserving clause costs some, and the logic change costs most.

## Reading

With thinking, the model behaves as the ideal recognizer on this table,
so the graded description has nothing to separate at B1 and the
interesting budget is B0. There the depth-shortening clause and the
depth-preserving clause are both visible, in opposite directions. The
graded account predicted the sign of F and the invisibility of C; the
first held, the second did not: for this language model, redundancy
itself is a cost when no thinking is spent, and the cost is of the same
size as the benefit of shortening. Whether "redundant clause hurts,
shortening clause helps" is a stable law is the next preregistered test.
