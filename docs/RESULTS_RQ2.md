# RQ2 results — derivation-depth shortening vs computation budget

Status: **RUN AS PREREGISTERED** (`docs/PREREGISTRATION_RQ2.md`); all
recognizers complete. Table
`rq2/table/rq2_prompts.jsonl` (sha256 `39a82a17…`), 200 cases × {D, F, F1,
C, L} × 4 queries. Analysis: `rq2/analyze.py`; report
`experiments/rq2/analysis.json`.

## Primary result: P1 holds

IterReasoner (7 atoms, trained at 4 rounds, seed 0, 75 202 parameters, in-distribution val acc 0.996), decision on the target query:

| budget k | acc(D, all 4 queries) | acc(D, target) | dis_F | dis_F1 | dis_C | dis_L | Δ = dis_F − dis_C [95 % CI] |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 0.75 | 0.00 | 0.01 | 1.00 | 0.00 | 0.00 | 0.01 [0.00, 0.01] |
| **2** | 0.75 | 0.00 | **0.89** | 1.00 | **0.00** | 0.00 | **0.89 [0.84, 0.93]** |
| 3 | 0.97 | 0.89 | 0.11 | 0.11 | 0.01 | 0.89 | 0.10 [0.06, 0.15] |
| **4** | 1.00 | 1.00 | **0.00** | 0.00 | **0.00** | 1.00 | **0.00 [0.00, 0.00]** |
| 6 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 [0.00, 0.00] |

Interaction I = Δ(2) − Δ(4) = **0.885, 95 % CI [0.84, 0.93]**; Δ(2) ≥ 0.10.
Both clauses of P1 hold.

The learned reasoner's decision table coincides with the k-round symbolic
reasoner's at every budget (compare `symbolic_k*` rows in
`analysis.json`): at k = 2 the 177 depth-3 cases are NO on D and YES on F
(depth 2), the 23 depth-4 cases are NO on both; at k = 4 all are YES. Every
D–F disagreement is F correct and D wrong (`F_fixes` 0.89, `F_breaks` 0).
The logic-change control L is invisible below k = 3 (both NO) and fully
visible from k = 4 (dis_L = 1.00), as it must be for a budgeted reader.

So on this recognizer the answer to RQ2 is exact: a derivable extension is
distinguishable from its base iff it moves the target's derivation depth
across the budget; extensions that keep the depth (C) are identified at
every budget, and every extension is identified once the budget covers the
base depth. The architectural caveat stated in the preregistration
applies: one hop per round makes this pattern *available* to the model;
the empirical content is that training at k = 4 produced exactly this
reader and no shortcut (in-distribution accuracy 0.996 with no clause-count
or lexical heuristic surviving at k = 2, where dis_F1 = 1.00 comes from the
direct clause a→goal being read as a depth-1 derivation, not from lexical
overlap: dis_F1 = dis_F at k = 3 and 0 at k = 4).

## Controls

| recognizer | acc(D) | dis_F | dis_F1 | dis_C | dis_L | Δ [CI] |
|---|---:|---:|---:|---:|---:|---|
| exact oracle | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 |
| constant NO | 0.49 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Pythia-70M | 0.51 | 0.02 | 0.01 | 0.04 | 0.04 | −0.02 [−0.04, 0.01] |
| symbolic k = 2 / 4 | 0.75 / 1.00 | 0.89 / 0.00 | 1.00 / 0.00 | 0.00 / 0.00 | 0.00 / 1.00 | 0.89 / 0.00 |

Pythia-70M does not read (dis_L 0.04, accuracy at chance) and shows no
condition effect, as required of the non-reading control.

## Secondary: LLM transfer (S6) — P2 not evaluable at the decision level

| recognizer | acc(D, all) | YES on D target | dis_F | dis_F1 | dis_C | dis_L | compacc [m_t > m_n] |
|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen2.5-0.5B | 0.51 | 200 / 200 | 0.00 | 0.00 | 0.00 | 0.00 | 0.79 |
| Qwen2.5-1.5B | 0.49 | 0 / 200 | 0.00 | 0.04 | 0.00 | 0.00 | 0.89 |

On this rendering (7 atoms, 5–6 clauses) Qwen2.5-0.5B answers YES on every
query of every condition (minimum margin 1.23) and Qwen2.5-1.5B answers NO
on every query (maximum margin below 0): neither model reads at the
decision level, so the interaction I = Δ(0.5B) − Δ(1.5B) is 0 − 0 with a
degenerate CI and P2 is **not evaluable**, not refuted. This is the Gate R
outcome of the audit protocol (a recognizer that does not read cannot be
scored for identification) and is recorded as such. The margins do carry
partial reading (comparative accuracy 0.79 and 0.89), so the extended
observation is the only channel on which the LLMs can be examined here.

Exploratory (o_ext, not confirmatory; paired case bootstrap, B = 5000):
mean signed margin shift on the target query relative to D, logit units.

| recognizer | F | C | F − C [95 % CI] | F1 − F [95 % CI] | L [95 % CI] |
|---|---:|---:|---|---|---|
| Pythia-70M (non-reader) | −0.087 | −0.097 | 0.010 [0.005, 0.014] | 0.004 [−0.001, 0.009] | −0.080 [−0.099, −0.061] |
| Qwen2.5-0.5B | 0.116 | 0.083 | 0.033 [0.026, 0.040] | 0.098 [0.091, 0.104] | −0.406 [−0.437, −0.374] |
| Qwen2.5-1.5B | 0.300 | 0.251 | 0.048 [0.030, 0.067] | 0.285 [0.268, 0.302] | −0.207 [−0.237, −0.177] |
| SetRecognizer (7 atoms) | 0.646 | 0.229 | 0.417 [0.289, 0.540] | 1.264 [1.124, 1.407] | −9.32 [−9.76, −8.88] |

Restricted to the 181 cases where F and C mention the same number of query
atoms, F − C is 0.025 (0.5B), 0.029 (1.5B), 0.007 (Pythia), 0.372 (set).

Reading. For both Qwen models the shortening clause moves the target
margin more than the depth-preserving clause, and the CI excludes 0, but
the effect is about 0.03–0.05 logits: three to five times the non-reader's
surface residual (0.010, which exists because F mentions the hypothesis
atom in 198/200 cases and C in 131/200) and an order of magnitude below
the effect of the direct clause a→goal (F1 − F: 0.10 and 0.29). For the
LLMs, what makes a derivable extension distinguishable on this table is
overwhelmingly *lexical overlap with the query*, with a small residual in
the depth direction. For the set model the same ordering holds at ten
times the scale (F − C 0.42, F1 − F 1.26), i.e. a recognizer that
identifies the extensions at the decision level still orders them by
depth shortening in its margins.

## Secondary: constructed models

### S5 — IterReasoner trained at 2 rounds (never trained on a depth-3 derivation)

In-distribution val acc 0.960 (vs 0.996 for the 4-round model: 2 rounds
cannot derive the depth-3/4 positives in the training distribution).

| budget k | acc(D, all) | acc(D, target) | dis_F | dis_F1 | dis_C | dis_L | Δ [95 % CI] |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 0.75 | 0.00 | 0.01 | 1.00 | 0.00 | 0.00 | 0.01 [0.00, 0.01] |
| **2** (training budget) | 0.79 | 0.16 | 0.77 | 0.84 | 0.10 | 0.16 | **0.67 [0.60, 0.74]** |
| 3 | 0.98 | 0.94 | 0.07 | 0.07 | 0.01 | 0.94 | 0.06 [0.03, 0.10] |
| **4** | 0.99 | 0.99 | 0.01 | 0.01 | 0.00 | 0.86 | **0.01 [0.00, 0.01]** |
| 6 | 0.90 | 0.99 | 0.01 | 0.01 | 0.00 | 0.70 | 0.01 [0.00, 0.01] |

I = Δ(2) − Δ(4) = 0.665 [0.60, 0.74]: the same pattern, and the gap closes
at k = 4 although the model was never trained with 4 rounds (its rounds
extrapolate; at k = 6 accuracy starts to degrade, 0.90, and the
logic-change control becomes partly invisible, dis_L 0.70). Two
differences from the 4-round model are informative: at its own budget the
2-round model says YES on 16 % of the depth-3 bases it cannot derive, and
its decision moves on 10 % of the depth-preserving extensions C, i.e. a
model trained under a budget too small for its data acquires a shortcut
component that a merely redundant clause can trigger. The budget-relative
depth account still explains 0.67 of the 0.77 F effect; the residual 0.10
is not depth.

### S4 — 7-atom SetRecognizer (no budget knob)

168 386 parameters, in-distribution val acc 0.951. On the table:
acc(D, all) 0.98, acc(D, target) 1.00, dis_F 0.01, dis_F1 0.00, dis_C
0.00, dis_L 0.94, Δ 0.01 [0.00, 0.01]. At the decision level the set
model identifies almost every extension and reads the logic change, so
here it behaves like the oracle; there is no budget to vary. Exploratory
margins: signed shift on the target F +0.65, F1 +1.91, C +0.23, L −9.3.
The extended observation orders the conditions F1 > F > C > 0 > L, the
same ordering as the reasoner's margins and as Qwen-0.5B's, although the
set model has no round structure: a shortening clause moves the margin
about three times as much as a depth-preserving one. This is the
margin-level lead for a recognizer without an explicit budget.

## Predictions against outcomes

- P1 (primary, 4-round reasoner, k = 2 vs 4): **held** (I 0.885 [0.84, 0.93]).
- S1 direction: held (F_fixes 0.89, F_breaks 0.00).
- S2 F1 vs F: at k = 4 both 0.00 for the reasoner; lexical overlap does
  not drive its effect. For the LLMs the reverse: F1 ≫ F on margins.
- S3 logic-change control: held for every reading recognizer with a
  sufficient budget (dis_L 0.86–1.00); Pythia 0.04 (non-reader).
- S4 set model: Δ 0.01, no decision-level effect; margin ordering F1 > F > C.
- S5 2-round reasoner: held (I 0.665 [0.60, 0.74]) with a 0.10 shortcut
  residual on C.
- P2 (LLM sizes): not evaluable at the decision level (neither model
  reads this rendering); margin-level F − C small but nonzero.

## One-sentence conclusion

For a recognizer with an explicit computation budget, which equal-meaning
inputs it distinguishes is predicted exactly by whether the change moves
the shortest derivation across the budget, on 200 fresh cases; for LLMs
at 0.5–1.5B the same quantity accounts for only a small residual of the
margin movement, whose bulk is lexical overlap between the added clause
and the query. The prediction obtained is therefore: *budget-relative
derivation depth predicts distinguishability for budgeted reasoners;
query overlap predicts it for these LLMs.* Whether a larger or
chain-of-thought LLM behaves like the budgeted reasoner is the next test.
