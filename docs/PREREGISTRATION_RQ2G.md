# Preregistration — RQ2g (the learned reader's own composition, monotonicity and unit)

Written and committed before running. Motivation: `Graded.lean` now
defines a *lax graded reader* (a family R_k with T_{k−s} ⊆ R_k ⊆ T_k and
R_k monotone) and proves that composition inherits the sandwich with the
slack added (`LaxGraded.comp_sandwich`: T_{j+k−2s} ⊆ R_j ∘ R_k ⊆ T_{j+k}),
that slack 0 forces R = T (the graded monad), and that R_0 = id for any
slack. RQ2c established slack 1 for the 4-round learned reader on budgets
k ≥ 1 with the *symbolic* saturation as input. This test feeds the reader
its own output: the monad-style multiplication of the learned operator.

Cases: `rq2/table_c/rq2_cases.json` (fresh seed). Models: `iter_r4.pt`
(primary), `iter_r2.pt` (secondary). Script `rq2/run_compose.py`.

Definitions. R_k{a} = {a} ∪ {g′ ≠ a : model(hyps {a}, goal g′; k) = YES}.
Composite decision at (j, k): model(hyps R_k{a}, goal g; j) for the target
t and the non-derivable atom n. Bounds from the symbolic closure T_m{a}.

## Predictions

* **P9 (composite sandwich, slack 2):** for all (j, k) ∈ {1, 2, 3}², the
  per-case rate of [T_{j+k−2}{a} ∋ g ⇒ YES] ∧ [YES ⇒ T_{j+k}{a} ∋ g] (mean
  over t and n) has bootstrap lower bound ≥ 0.95 for the 4-round model.
  This is what the theorem guarantees *if* the reader is monotone and has
  slack 1 on these budgets.
* **P10 (monotonicity):** for S = {a} ⊆ S′ = {a, y} (y the sorted-first
  atom not derivable from a), the rate of goals with YES on S and NO on
  S′ is ≤ 0.05 at each k ∈ {1, 2, 3}.
* Reported, not predicted: the slack-1 sandwich rate of the composite (is
  the self-composition tighter than the theorem's bound?); the exact
  agreement with T_{j+k}; the unit law R_0 = id on S = {a} and S = T_1{a}
  (the model was never trained at 0 rounds; failure is expected and would
  mean the learned family has no unit); the 2-round model on all of the
  above.

Failure sentence for P9: "The learned reader's self-composition was not
sandwiched within two rounds of slack (rate …, CI …); the lax graded
structure established with symbolic hints does not extend to the
reader's own outputs." For P10: "The learned reader is not monotone in
its hypothesis set (violation rate …); the lax-graded theorems do not
apply to it as stated."
