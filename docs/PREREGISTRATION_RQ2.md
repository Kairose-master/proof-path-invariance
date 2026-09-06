# Preregistration — RQ2 (derivation-depth shortening vs computation budget)

Written and committed before any learned recognizer or LLM was run on the
RQ2 table. The symbolic k-round reasoner and the exact oracle were run
first as control validation (their outputs are deterministic functions of
the table and contain no empirical content about learned recognizers).

Frozen table: `rq2/table/rq2_prompts.jsonl`,
sha256 `39a82a17f9aae4027586339c58942a0114439bf0f978cf12724e754479676510`,
4000 rows = 200 cases × 5 conditions × 4 queries, seed 20260906,
264 draws (64 dropped by the exclusion rules below).
Generator: `rq2/build_table.py` on top of `rq2/dfc.py`.

## 1. Question

Under a limited computation budget, does adding a clause that *shortens the
derivation* of the target (F) change a recognizer's decision more than
adding a clause that is equally redundant but does *not* shorten it (C),
and does that gap close as the budget grows?

The hypothesis is one instance of the RQ1 programme: the surface property
that makes two equal-meaning inputs distinguishable is, here, the *depth of
the shortest derivation relative to the recognizer's budget*. If it holds,
the observed non-identification of derivable extensions in Phase 3.5 and
Phase 4 has a structural reading (budget-relative depth) rather than being
an unexplained sensitivity.

## 2. Equivalence relation and certification scope

* Logical identity ≡_L is theory equivalence on all single-hypothesis
  queries: two clause lists are identical iff `closure(T,{x})` agrees for
  every atom x. The builder asserts this for D, F, F1, C of every case
  (exact certification; Lean counterpart
  `Horn.logicalEquiv_append_derivable`).
* L is certified to differ from D on the target query (`goal ∉ closure(L,{a})`).
* Observation split (RQ1): o_dec = the Boolean decision on the target
  query (pos logit > neg logit; ties → NO); o_ext = the real margin on the
  target query and the 4-query decision vector. The primary analysis uses
  o_dec on the target query only.

## 3. Case generation and exclusion rules (fixed)

* 7 atoms `a..g`; base D = 5 random Horn clauses (70 % single→single,
  15 % two-body, 15 % two-head); target hypothesis is always `a`; goal =
  the derivable atom with maximal depth, ties broken by name; cases with
  maximal depth < 3 are redrawn. Depth = minimal number of parallel
  forward-chaining rounds from {a}.
* Derivable single-atom clause candidates x→y: y ∈ closure(D,{x}), x ≠ y,
  not already a (sub-)clause of D (x→(y,z) counts as present).
* F = sorted-first candidate among those that reduce depth by the *least*
  amount (minimal shortening).
* F1 = the direct clause a→goal (maximal shortening and maximal lexical
  overlap with the query; secondary condition, always exists).
* C = sorted-first depth-preserving candidate with the same overlap with
  {a, goal} as F, falling back to any depth-preserving candidate
  (overlap matched in 181/200 cases, recorded per case).
* L = D minus the sorted-first clause whose deletion makes the target
  non-derivable (logic-change control; 4 clauses).
* Queries per case: t = (a, goal); d1 = (a, y), y sorted-first depth-1
  atom; n = (a, z), z sorted-first atom not derivable from a; r = (goal, a).
* Exclusion: no F candidate, no C candidate, no L deletion, no depth-1 atom,
  or no non-derivable atom → case dropped; the next draw is used.
* Realised distribution: depth_D {3: 177, 4: 23}; depth_F {2: 176, 3: 23,
  1: 1}; depth_C = depth_D. Gold on t and d1 is always YES, on n always NO,
  on r NO in 190/200.
* Surface confounds shared by F, F1, C: one appended clause at the end,
  same clause shape (single→single). F and C differ in the atoms they
  mention; F contains `a` in 198/200 cases and C in 131/200 (recorded).
  The F1–F contrast separates "mentions both query atoms" from "shortens".

## 4. Recognizers, budgets, output mode, ties

| recognizer | budget knob | budgets | role |
|---|---|---|---|
| exact closure oracle | none | – | ceiling; must give dis = 0 on F, F1, C and 1 on L |
| k-round symbolic reasoner | k | 1, 2, 3, 4, 6 | control validation (run before this document) |
| constant-NO recognizer | none | – | non-reading control (dis = 0 everywhere, acc_D_t = 0) |
| Pythia-70M (step143000) | none | – | empirical non-reading control (chance in Phases 3–4) |
| IterReasoner, 7 atoms, trained at 4 rounds, seed 0 | evaluation rounds k | 1, 2, 3, 4, 6 | **primary** |
| IterReasoner trained at 2 rounds, seed 0 | evaluation rounds k | 2, 4 | secondary (training-time budget) |
| SetRecognizer, 7 atoms, seed 0 | none | – | secondary (no budget knob) |
| Qwen2.5-0.5B-Instruct, 1.5B-Instruct | model size (confounded) | 0.5B, 1.5B | secondary transfer test |

Constructed models: `rq2/train_rq2.py`, 6000 steps, batch 128, AdamW +
OneCycle, training distribution = random 2–6-clause theories over 7 atoms
with balanced labels; every D, F, F1, C, L theory of the table is excluded
from training up to atom relabelling (`data7.Holdout`). Output = 2 logits;
decision = argmax with ties → NO. LLMs: raw prompt (bullets renderer,
YES/NO answer map, single forward pass, float32 CPU); decision =
logit(" YES") > logit(" NO"), ties → NO. Names are `p000…v000` per case.

Architectural note, stated in advance: in the IterReasoner information
flows body→head one hop per round, so at k < depth the goal state cannot
depend on the hypothesis flag. A *correct* model must therefore say NO on D
at k = 2 and YES on F (depth 2) at k = 2. The empirical content of the
primary test is (i) whether the trained model actually behaves like this
rather than through shortcuts (e.g. answering YES from clause statistics),
(ii) whether the gap closes at k = 4 (identification at sufficient
budget), and (iii) whether the same pattern transfers to recognizers
without an explicit round structure (set model, LLMs).

## 5. Primary comparison

For a recognizer R at budget k, over the 200 cases:

* dis_X(k) = fraction of cases whose target decision differs between D and X;
* Δ(k) = dis_F(k) − dis_C(k).

**Primary**: IterReasoner (trained at 4 rounds) at k = 2 vs k = 4.
Interaction I = Δ(2) − Δ(4).

**Prediction P1**: I > 0 with the paired case-bootstrap 95 % CI (B = 5000,
seed 0) excluding 0, and Δ(2) ≥ 0.10.

Effect criterion: the prediction *holds* iff both clauses of P1 hold.
Any other outcome is a failure of P1.

Sample-size rationale: 200 logical structures. For a proportion difference
around 0.15 the paired bootstrap half-width is about 0.05 (SE ≈
√(0.15·0.85/200) ≈ 0.025), so an interaction of 0.10 is resolvable; the
symbolic control on the same table gives I = 0.885 as the ceiling if the
learned model behaves like the k-round reasoner. Cases come from one seed
never used for training (training data are drawn from a different
generator with the table excluded up to relabelling); no case was
inspected against any learned recognizer before this commit.

## 6. Secondary analyses (reported, not confirmatory)

* S1 Direction: among D–F disagreements at k = 2, the share where F is
  correct and D wrong (`F_fixes`) vs the reverse (`F_breaks`); P1's
  mechanism predicts F_fixes ≫ F_breaks.
* S2 F1 vs F at each k: if dis_F1 ≫ dis_F at k = 4 (where depth no longer
  matters), lexical overlap, not shortening, drives the effect.
* S3 Logic-change control: dis_L ≥ dis_F for every reading recognizer at
  every budget; a recognizer with dis_L ≈ 0 is not reading.
* S4 Set model (no knob): Δ reported with CI; no budget prediction.
* S5 IterReasoner trained at 2 rounds: Δ(2) and Δ(4); does a model that
  never saw depth-3 derivations still close the gap at k = 4?
* S6 LLM transfer: Δ(0.5B) and Δ(1.5B) with CIs, and I = Δ(0.5B) −
  Δ(1.5B). Prediction P2 (secondary): I > 0 with CI excluding 0. Size is
  not a pure budget, so P2 failing does not refute P1.
* S7 Extended observation: median |margin_D − margin_X| for X ∈ {F, C};
  and 4-query Hamming distance dis4_X. Reported for the o_dec/o_ext split.
* Non-target queries d1, n, r: dis reported per condition (F/C should not
  change them for a correct recognizer; L changes only t by construction).

## 7. Failure sentence

If P1 fails, the report will state verbatim:

> "On 200 fresh Horn cases, the learned iterative reasoner did not show a
> larger decision change for depth-shortening extensions than for
> depth-preserving extensions at the low budget relative to the high
> budget (I = …, 95 % CI […]); the budget-relative-depth account of
> non-identification is not supported by this test."

If P1 holds but S2 shows dis_F1 ≫ dis_F at k = 4, the report will add that
lexical overlap contributes an effect beyond depth shortening.

## 8. What is *not* claimed

No claim that the learned reasoner "has" a monad, a quotient, or any
algebraic object; no claim about LLMs beyond the two sizes run; no claim of
monotone decrease across all budgets (only the two pre-chosen budgets are
confirmatory).
