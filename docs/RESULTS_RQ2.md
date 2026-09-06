# RQ2 results — derivation-depth shortening vs computation budget

Status: **PRIMARY ANALYSIS RUN AS PREREGISTERED** (`docs/PREREGISTRATION_RQ2.md`).
Secondary recognizers still running are marked *pending*. Table
`rq2/table/rq2_prompts.jsonl` (sha256 `39a82a17…`), 200 cases × {D, F, F1,
C, L} × 4 queries. Analysis: `rq2/analyze.py`; report
`experiments/rq2/analysis.json` (partial: `analysis_partial.json`).

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

## Secondary: LLM transfer (S6) — Qwen2.5-0.5B; 1.5B *pending*

On this table Qwen2.5-0.5B answers YES on every target query of every
condition (minimum margin 1.23), so its o_dec is uninformative: dis_F =
dis_C = dis_L = 0.00 and accuracy over the four queries is 0.51. The
decision-level test of P2 cannot be evaluated at 0.5B; the failure sentence
does not apply because the model does not read at the decision level on
this rendering (7 atoms, 5–6 clauses; the Gate R condition of the audit
protocol).

Exploratory extended observation (preregistered as o_ext, analysis not
confirmatory): comparative accuracy [margin(t) > margin(n)] on D is 0.79,
so the margins carry partial reading. Mean signed margin shift on the
target query: F +0.12, F1 +0.21, C +0.08, L −0.41 (in logit units;
median |shift| F 0.17, C 0.14). The ordering F1 > F > C > 0 > L is the
depth-shortening ordering, but the F–C gap is small relative to the L
shift and no CI has been computed for it; it is reported as a lead for a
margin-level test, not as a result.

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

### S4 — 7-atom SetRecognizer (no budget knob) — *pending*

## One-sentence conclusion (so far)

For a recognizer with an explicit computation budget, "which equal-meaning
inputs it distinguishes" is predicted exactly by whether the input change
moves the shortest derivation across the budget; whether the same
quantity predicts LLM behaviour is not decided by this table at 0.5B
(decision-level non-reading) and awaits the 1.5B run and a margin-level
test.
