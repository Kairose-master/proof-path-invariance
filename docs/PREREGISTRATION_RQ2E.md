# Preregistration — RQ2e (signed extension effects for a budget-less language model, fresh seed)

Written and committed before any Gemini result on the fresh table was
obtained. Motivation: RQ2d's preregistered unsigned test failed while an
exploratory directional analysis showed the shortening clause helping and
the depth-preserving clause hurting the no-thinking model by similar
amounts. This document turns that observation into predictions on new
cases.

Table: `rq2/table_c/rq2e_llm.jsonl` (`LOCK_rq2e_llm`), built from the
fresh RQ2c cases (seed 20260907; never used with any language model):
part A = 200 cases × {D, F, F1, C, L} × {t, n}; part B = the pre-saturated
rows for j ∈ {1, 2}. Same model, budgets, prompt and readout as RQ2d
(`gemini-3.1-flash-lite`; B0 no thinking, B1 thinking budget 1024; first
token YES/NO; unparseable → NO).

Gate as in RQ2d (acc(D) ≥ 0.75 over t and n and dis_L ≥ 0.50 at a budget).

## Predictions (target query t, gold YES; net accuracy change = fixes − breaks)

* **P6a (shortening helps at B0):** net change for F at B0 ≥ +0.05 with
  paired case-bootstrap 95 % CI excluding 0.
* **P6b (redundancy hurts at B0):** net change for C at B0 ≤ −0.05 with
  CI excluding 0.
* **P6c (the budget removes both):** at B1, dis_F ≤ 0.02 and dis_C ≤ 0.02.

Primary criterion: P6 holds iff P6a, P6b and P6c all hold. Each clause is
also reported separately.

Secondary (reported): F1 net change at B0; the signed difference F − C at
B0 with CI; pre-saturation accuracies from H_1 and H_2 at B0 (the RQ2d
non-monotonicity, 0.71 < 0.80 < 0.945, is expected to recur if it is
real); paired thinking-token differences at B1 (F1 − D negative, C − D and
L − D positive, as in RQ2d).

Failure sentence: "On a second set of 200 fresh Horn cases,
gemini-3.1-flash-lite without thinking did not show the opposite-signed
effects of a shortening and a depth-preserving redundant clause found on
the first set (F …, C …); the RQ2d directional pattern does not
generalise."
