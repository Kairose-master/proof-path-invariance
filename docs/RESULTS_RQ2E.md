# RQ2e result — signed extension effects without thinking hold on a fresh seed

Status: **RUN AS PREREGISTERED (`docs/PREREGISTRATION_RQ2E.md`).** Model
`gemini-3.1-flash-lite`, budgets B0 (no thinking) and B1 (thinking 1024),
fresh table `rq2/table_c/rq2e_llm.jsonl` (sha256 `211e2a7f…`, 5600
requests; 3 unparseable at B0, counted NO). Results
`experiments/rq2/results_e/flash_lite_all.jsonl`, analysis
`analysis_flash_lite.json`.

Gate: B0 acc(D) 0.89, dis_L 0.78; B1 acc(D) 1.00, dis_L 1.00. Both read.

## P6 holds

| clause | criterion | fresh seed (RQ2e) | first seed (RQ2d, exploratory) |
|---|---|---|---|
| P6a shortening helps at B0 | net F ≥ +0.05, CI > 0 | **+0.155 [0.110, 0.210]** | +0.135 [0.085, 0.190] |
| P6b redundancy hurts at B0 | net C ≤ −0.05, CI < 0 | **−0.070 [−0.120, −0.020]** | −0.090 [−0.140, −0.040] |
| P6c the budget removes both | dis_F, dis_C ≤ 0.02 at B1 | **0.000, 0.000** | 0.000, 0.000 |

All three clauses hold. Secondary: F1 net +0.220 [0.165, 0.280]; signed
F − C at B0 +0.225 [0.170, 0.285] (first seed: +0.225 [0.165, 0.285]);
the unsigned Δ is again null (0.015 [−0.050, 0.080]). Pre-saturation at
B0: H_0 0.78, H_1 0.71, H_2 0.925 (first seed 0.80 / 0.71 / 0.945): the
non-monotonicity recurs. At B1 the model is again the oracle on every
row. Thinking tokens at B1 relative to D: F1 −34, F +19, C +39, L −9; the
F1 saving and the C cost recur, the L cost of the first seed (+112) does
not.

## Reading

For a language model without thinking, a redundant clause is not neutral:
one that shortens the target derivation raises the answer rate by about
0.15, and one that preserves depth lowers it by about 0.07, on two
independent sets of 200 cases with the same signed difference (0.225).
With thinking the model identifies both and reads every logic change.
The graded account predicted the direction of the shortening effect and
its disappearance with budget; it did not predict the cost of a
depth-preserving clause, which is a property of this recognizer and not
of the closure. For this model the variable that makes equal-meaning
inputs distinguishable at zero budget is therefore two-sided: derivation
depth (helps when shortened) and clause count (hurts when merely added),
and both vanish once the model can spend tokens.
