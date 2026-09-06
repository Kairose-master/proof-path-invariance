# RQ2b result — the composition law (a hint buys exactly its depth)

Status: **RUN AS PREREGISTERED (`docs/PREREGISTRATION_RQ2B.md`).**
Table `rq2/table/rq2b_presat.jsonl` (sha256 `5e42376d…`), reports in
`experiments/rq2/results_b/*.json`, runner `rq2/run_presat.py`.

Law under test (`Graded.lean`, `entailsK_presaturate`):
R(H_j, goal; k) = R(H_0, goal; j + k), with H_j = T_j({a}).

## Primary: P3 fails for the 4-round model

Agreement between R(H_j; k) and R(H_0; j + k), 200 cases × 2 queries,
paired case bootstrap 95 % CI. Primary pairs marked *.

| pair | symbolic | IterReasoner trained at 4 rounds (**primary**) | IterReasoner trained at 2 rounds (secondary) |
|---|---:|---|---|
| j=1, k=2 * | 1.000 | **0.897 [0.870, 0.925]** | 0.990 [0.980, 0.998] |
| j=2, k=1 * | 1.000 | **0.830 [0.797, 0.863]** | 0.975 [0.960, 0.990] |
| j=2, k=2 * | 1.000 | 0.995 [0.988, 1.000] | 0.998 [0.993, 1.000] |
| j=1, k=3 * | 1.000 | 0.983 [0.970, 0.995] | 1.000 [1.000, 1.000] |
| j=1, k=1 | 1.000 | 1.000 (trivial: both NO) | 0.922 |
| j=1, k=0 | 1.000 | 0.630 | 1.000 |
| j=2, k=0 | 1.000 | 0.630 | 0.920 |
| j ≥ 1, k ≥ 4 | 1.000 | 1.000 | 0.995–1.000 |

Two of the four primary pairs have CI lower bounds below 0.95, so **P3
fails** for the primary model. The failure sentence, as preregistered:

> "On 200 fresh Horn cases the learned reasoner did not satisfy the
> composition law T_k ∘ T_j = T_{j+k} out of its training format
> (agreement 0.897 [0.870, 0.925] at j=1, k=2 and 0.830 [0.797, 0.863] at
> j=2, k=1); the graded-monad description fits its budget behaviour (RQ2)
> but not its hypothesis-set behaviour, and the law is a property of the
> symbolic reasoner that the learned one does not inherit."

The secondary model, trained at 2 rounds, satisfies all four primary pairs
(lower bounds 0.980, 0.960, 0.993, 1.000). P3 was not preregistered for it,
so this is an observation, not a confirmed prediction.

## Failure mode (S3)

Every disagreement of the primary model is in one direction: R(H_j; k) =
NO where R(H_0; j + k) = YES (41 of 41 at j=1, k=2; 68 of 68 at j=2, k=1).
The model reads multi-atom hypothesis sets correctly when given slack
(accuracy 1.000 at k = 4 with H_1 and with H_2), but at the exact budget
the hint under-delivers: yes-rate 0.685 at (H_1, 2) against 0.890 at
(H_0, 3); 0.550 at (H_2, 1) against 0.890 at (H_0, 3). Agreement falls with
the size of the hint (j=2, k=1: |H_2| = 3: 0.73, 4: 0.63, 5: 0.55) and is
near-perfect on the depth-4 cases (0.957), where the extra round of slack
exists. The learned operator therefore satisfies T_k ∘ T_j ⊆ T_{j+k} with
strict inclusion on 20–35 % of cases at the tight budgets: it needs about
one round more than the law grants when the derivation starts from a set
rather than a single atom. The 2-round model, which had to learn to
propagate from whatever it is given within two rounds, does not show this
loss.

## Reading

RQ2 showed that the budgeted reasoner's *identification* of extensions is
exactly graded (it separates a trace from a redundant extension iff the
extension crosses its budget). RQ2b shows that the same reasoner is not
exactly a graded monad: the grade composition law holds for its symbolic
counterpart and, empirically, for the 2-round model, but the 4-round model
loses part of a round when the budget is exhausted from a multi-atom
start. The graded structure is therefore the right description of *what
is distinguished*; whether a given learned reasoner also obeys the
*composition* law is a property of its training, not of its architecture.
This is the first equation from the mathematical object that a
constructed recognizer failed, and it was found by testing the law rather
than by assuming it.

## Not claimed

Nothing about LLMs (no budget knob in a single forward pass); nothing
about the 2-round model beyond the observation above.
