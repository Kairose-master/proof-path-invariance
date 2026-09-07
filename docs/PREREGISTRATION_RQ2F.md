# Preregistration — RQ2f (dose–response in clause count and in thinking budget)

Written and committed before any request of this table was sent. Builds
on RQ2e (held): for `gemini-3.1-flash-lite` without thinking, a
depth-shortening redundant clause helps (+0.155) and a depth-preserving
redundant clause hurts (−0.070), and both vanish with a thinking budget
of 1024. Two questions follow. Is the cost a cost of *redundancy* or of
*clause count*? And is the vanishing gradual in the budget?

Table `rq2/table_c/rq2f_dose.jsonl` (`LOCK_rq2f_dose`), fresh-seed cases
(RQ2c), target query only. Conditions at B0 (no thinking): D, C1 (the
RQ2c C clause), C2 and C3 (C1 plus the next one or two sorted-first
depth-preserving derivable clauses; available in 155 and 106 cases), N1
(one irrelevant clause x → y with y not derivable from x and x not
derivable from a: it changes the meaning of the theory but not any query
from a; 198 cases), F, F1. Conditions at B256 (thinking budget 256, about
140 tokens actually used; the model uses the same amount for 512): D, F,
F1, C1, L. Pilot facts: budgets below 256 produce no thinking and 1024
and 2048 produce the same ~300 tokens, so the model exposes three
effective budget levels, 0 / ~140 / ~300.

Readout as in RQ2d/e (first generated token YES/NO; unparseable → NO).
Net effect of a condition = fixes − breaks relative to D on the same
budget (gold YES). Paired case bootstrap 95 % CI, B = 5000.

## P7 — what the cost is a cost of (B0)

* **P7a (dose in count):** on the 106 cases having C1, C2, C3, net(C3) <
  net(C1) with the paired CI of the difference excluding 0.
* **P7b (count vs redundancy), a three-way discrimination on all cases
  having N1:** let δ = net(N1) − net(C1).
  - |δ| ≤ 0.05 → *count hypothesis*: an added clause costs the same
    whether or not it is redundant. (Expected.)
  - δ > 0.05 with CI excluding 0 → *redundancy hypothesis*: the derivable
    clause costs more than an irrelevant one.
  - δ < −0.05 with CI excluding 0 → *distraction hypothesis*: the
    irrelevant clause costs more.
  Whichever cell the CI falls in is reported; a CI straddling two cells is
  reported as undecided.

## P8 — the budget response (B0 vs B256 vs B1024)

Using the RQ2e B0 and B1024 results for D, F, F1, C1 (same cases, same
model, same prompts; B0 rows are rerun here and the rerun is used for
the B0 side to keep the pairing within one batch) and the new B256 rows:

* **P8a:** net F(B0) − net F(B256) > 0 with CI excluding 0 (the benefit of
  shortening shrinks with a small budget).
* **P8b:** net C1(B256) − net C1(B0) > 0 with CI excluding 0 (the cost of
  redundancy shrinks).
* **P8c:** at B256 neither effect reverses sign: net F(B256) ≥ −0.02 and
  net C1(B256) ≤ +0.02.

P8 holds iff all three hold. Also reported: accuracy on D at B256, dis_L at
B256 (gate), net F1(B256), and the B0 rerun agreement with the RQ2e B0
decisions (temperature 0; disagreement rate reported).

## Failure sentences

P7a: "Adding more depth-preserving redundant clauses did not hurt the
model more than adding one (net C3 − net C1 = …, CI …)."
P8: "The effects of shortening and redundancy did not shrink monotonically
with the thinking budget (…); the budget is not a grade for this model."
