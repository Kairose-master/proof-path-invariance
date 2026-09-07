# Preregistration — RQ2d (a language model with a thinking budget)

Written and committed before any Gemini result was read beyond the
following pilot: one RQ2 prompt was sent to three Gemini models to test
the API (logprobs unavailable; `gemini-3.1-flash-lite` answers "YES"/"NO"
directly with thinking off and uses ~300 thinking tokens with a budget of
1024; the free tier allows 15 requests per minute).

Table: `rq2/table/rq2d_llm.jsonl` (`LOCK_rq2d`), 2800 rows: part A = the
RQ2 rows for queries t and n (200 cases × {D, F, F1, C, L} × 2), part B =
the RQ2b pre-saturated rows for j ∈ {1, 2} (200 × 2 × 2), rendered with a
multi-atom hypothesis. Each row is run at two budgets.

## Recognizer and budgets

`gemini-3.1-flash-lite`, temperature 0, raw prompt (same bullet rendering
as RQ2). Budget B0: no thinking (`thinking_config` absent; max 8 output
tokens). Budget B1: `thinking_budget = 1024`. Readout: the first token of
the generated text, YES or NO; anything else is recorded as unparseable
and counted as NO. This is a decision-level readout only; no margins.

## Gate

The model reads the table at a budget iff on D its accuracy over t and n
is ≥ 0.75 and dis_L ≥ 0.50 at that budget. Predictions below are
evaluated only at budgets that pass the gate; a budget that fails the
gate is reported as not evaluable.

## Primary prediction P5 (identification interaction)

Δ(B) = dis_F(B) − dis_C(B) on the target query t.
P5: I = Δ(B0) − Δ(B1) > 0 with paired case-bootstrap 95 % CI (B = 5000)
excluding 0, and Δ(B0) ≥ 0.10.

This is P1 read on a language model whose budget is thinking tokens rather
than rounds. If thinking off already suffices for depth 3–4 (Δ(B0) ≈ 0 with
acc ≈ 1), P5 is not evaluable in this budget range and will be reported as
"budget too large at B0".

## Secondary

* S1 F1 vs F at each budget: if dis_F1 ≫ dis_F at B1, lexical overlap
  drives the residual (as for Qwen margins).
* S2 Pre-saturation (part B): accuracy on t from H_1 and H_2 at B0 versus
  from H_0 (= D, t) at B0; the lax law predicts acc(H_2) ≥ acc(H_1) ≥
  acc(H_0) at B0 and equality at B1. No exact composition test is possible
  (thinking tokens are not rounds).
* S3 Thinking tokens used per condition at B1: if the model "spends" less
  on F than on D and C (the shortcut is used), reported descriptively.

## Sample size and quota

200 cases; the free-tier rate (15/min) means about 3.3 hours per budget
for part A; the run proceeds in priority order (t rows, n rows, part B)
and resumes across days if a daily quota intervenes. Analysis is run only
on complete parts.

## Failure sentence

"On 200 fresh Horn cases, gemini-3.1-flash-lite did not show a larger
decision change for depth-shortening extensions than for depth-preserving
ones at the low thinking budget relative to the high one (I = …, CI …);
the budget-relative-depth account does not transfer to this language
model's thinking budget."
