# Novelty statement (after full-text reading, 2026-09-06)

Full texts read: LGMT ([2605.23965](https://arxiv.org/html/2605.23965)),
CRTBench ([2607.14528](https://arxiv.org/html/2607.14528)), Parameterized
Logical Problems ([2602.12665](https://arxiv.org/html/2602.12665v1)),
Set-LLM ([2505.15433](https://arxiv.org/html/2505.15433)), Order-Centric
Augmentation ([2502.19907](https://arxiv.org/html/2502.19907)). Abstracts
only: Chen et al. 2024, Lacroce et al. 2021, *An Algebraic View of the
Expressivity of Recurrent Language Models* ([2606.01765](https://arxiv.org/abs/2606.01765)).

## What the five papers do (facts that matter for us)

| | LGMT | CRTBench | Param. SAT | Set-LLM | Order-Centric |
|---|---|---|---|---|---|
| Equivalence relations | 20 metamorphic relations incl. **premise reordering (MR-P1), duplication (MR-P2), redundancy elimination, irrelevant extension**, renaming, formula rewrites | contrapositive, double negation, De Morgan, quantifier rewrite, passive voice | clause reordering, filler clauses, variable renaming | permutation of set elements only | premise and reasoning-step permutation |
| How guaranteed | FOL skeleton mutated; NL translation by an LLM; **no proof assistant** | manual audit | generator construction | theorem (equivariance of attention under set permutation) | DAG of step dependencies |
| Readout | **discrete labels only** | **answers only** (regex) | **accuracy only** | accuracy | accuracy |
| Statistic | violation rate; identity of labels | family consistency; accuracy–consistency gap | accuracy under perturbation | random-order vs adversarial-order accuracy | accuracy on shuffled sets |
| Surface-vs-logic control | none | passive voice as observational surface control; **no minimal-logic-change contrast** | none | n/a | none |
| Exact identity of outputs, equivalence classes, quotients | no | no | no | no (equivariance theorem, but no measured quotient) | no |
| What a finite test set can conclude (closure, identifiability) | no | no | no | no | no |
| Consequence-equivalent but syntactically different sets | partly, as separate MRs, label-level | no | no | **no** | no |
| Models | frontier (GPT-5.2, Claude 4.5, Llama-70B…) | frontier | 15–120B | 1–8B, LoRA | 7–70B, full FT |

Key numbers: LGMT violation rate 21–29%, with premise-level relations the
*least* violated (16%); CRTBench accuracy–consistency gap up to 38.6 pp;
Set-LLM removes the adversarial-order gap entirely (ARC 55→24% for the
baseline).

## What is therefore not new in this project

- That LLMs are sensitive to premise order and to logic-preserving
  rewrites (Chen 2024; LGMT; Param. SAT).
- That a model can be accurate on each version and inconsistent across
  versions (CRTBench's accuracy–consistency gap; our Gate R / Gate I
  split is the same phenomenon at small scale).
- Reordering and duplication as test relations (LGMT MR-P1, MR-P2).
- Permutation-invariant architecture with a proof (Set-LLM) and
  permutation augmentation (Order-Centric) as remedies.
- The algebraic language of syntactic monoids applied to neural sequence
  models (2606.01765, for expressivity of RNNs).

Our Phases 1–3.4 are, as empirical findings, small-scale replications
and must be labelled so.

## What survives as a contribution

**N1. The framework, machine-checked.** None of the five states the
object being tested. We define logical identity and behavioral identity
as two congruences on the same free monoid and prove, in Lean: the
canonical map exists iff one congruence refines the other; that map is a
monoid morphism; **premise reordering and duplication are not two
independent test relations but consequences of one inclusion**
(LGMT's MR-P1 and MR-P2 are theorems `contextEquiv_of_perm_of_invariant`
and `contextEquiv_dup_of_invariant`); a finite test family induces the
full behavioral identity iff it is closed under one-symbol extension, and
a closure failure names the next test; the biextensional collapse of the
observation table. This turns "which metamorphic relations should we
test" into a lattice question with a proof obligation, and "when have we
tested enough" into a checkable condition. No prior work in the set does
either.

**N2. Exact versus approximate identity from logits.** All five read
discrete answers. We read the logit pair through order relations only
(decision and pairwise preference), which is threshold-free and
offset-invariant, and we count exactly identical profiles and the sizes
of the row and column collapses. The finding that *no two* logically
identical traces are ever behaviorally identical, for any recognizer,
including one that reads the task, is a statement none of the five can
make or refute with their readouts. The comparative readout also removes
the answer-bias saturation that discrete readouts inherit.

**N3. A designed surface-versus-logic statistic with a validity control.**
CRTBench uses passive voice as an observational surface control; nobody
contrasts a maximal logic-preserving rewrite with a minimal logic-changing
one on the same instance. `S = d_perm / d_flip`, with a non-reading
recognizer as the control that sits at the noise value, is new. Its
result, that for the reader `S > 1`, sharpens CRTBench's gap: the
inconsistency is not only present, it outweighs a logical change.

**N4. Permutation invariance versus logical invariance.** Set-LLM proves
and measures permutation equivariance and stops there. The gap between a
theory-factoring recognizer (invariant under the syntactic part of `≡_L`
by construction) and the ideal recognizer (invariant under all of `≡_L`)
is stated in `Specification.lean` and has not been measured by anyone in
this set. The experiment that measures it, a table of
consequence-equivalent but syntactically different clause sets applied to
a set-encoder recognizer, is the one this project should own
(`hankel_v3`, Phase 4).

**N5.** Measured LLMs and constructed recognizers on one frozen table with
one statistic. Minor, but it is what makes N4 comparable to N3.

## The claim, sized to the evidence

> We give a machine-checked account of what it means for a recognizer to
> respect logical identity, of which invariance tests follow from which,
> and of when a finite test family has decided the question; a readout
> that makes the question exact; and a controlled contrast showing that,
> for small readers of Horn entailment, surface rewrites outweigh logical
> ones. On this instrument, permutation-invariant architectures answer
> only the syntactic half of the question; the semantic half is open and
> measurable.

## Still to check

- 2602.12665's "symmetry/duplication variants" in detail against N3.
- LGMT's appendix on PNNF completeness against N1 (their completeness is
  about normalization, not about test sufficiency; confirm).
- Whether any L*-style work applies closure to LLM prompts (search found
  none; 2606.01765 is about RNN expressivity, not testing).
