# Research questions (2026-09-06)

Central question:

> Inputs that are formally identical in meaning are distinguished by a
> recognizer. How does that distinction depend on the observation, on the
> range of contexts, and on the computational resources, and under which
> conditions does it disappear?

The question does not contain the conclusion "the model implements a
closure operator or a monad". Labels follow `AGENTS.md`; decision rules are
fixed before each new experiment.

## RQ1. In which observation does the distinction of logically equivalent inputs appear?

Two observations of the same pair of inputs:

- **decision observation** `o_dec`: YES/NO per query;
- **extended observation** `o_ext`: YES/NO plus the preference order of
  margins between queries.

With an explicit context family `T`, "recognized as the same" is
restricted to

    u ≡_{ρ,o,T} v  iff  ∀ t ∈ T, o(ρ(u t)) = o(ρ(v t)).

HYPOTHESIS: pairs that are not distinguished under `o_dec` are
distinguished under `o_ext`, and this appears on a fresh benchmark.

Measure: the fraction of equivalent pairs with decision agreement and
extended disagreement, with uncertainty; accuracy and constant-response
checks alongside. That `o_ext` distinguishes at least as much as `o_dec` is
true by construction; the object of study is how large the difference is
and where it replicates. A preference disagreement is not called an
absence of logical understanding.

Refutation / reduction: the difference does not replicate, or is explained
by numerical ties or run-to-run variation.

## RQ2. Is the effect of adding a derivable clause related to a shortening of derivation depth?

*Status: run; see `docs/PREREGISTRATION_RQ2.md` and `docs/RESULTS_RQ2.md`.*

Three conditions on one base theory:

| condition | change to the input | preserved / controlled |
|---|---|---|
| D | base theory | reference |
| F | add an already-derivable clause that shortens the derivation of the target | full logical meaning |
| C | add a derivable clause that does not shorten the target's derivation | meaning; length, clause count, lexical overlap matched to F as far as possible |

Depth is the minimal number of parallel derivation rounds under a fixed
rule set. Exclusion rules for cases without a matched C are fixed before
results are seen.

HYPOTHESIS: under limited computation the F effect exceeds the C effect,
and the gap shrinks as computation increases.

Measure: decision-disagreement and accuracy differences D–F and D–C per
computation budget. The primary analysis is one condition × budget
interaction between two pre-chosen budgets.

Refutation / reduction: the effect disappears under surface controls, is
independent of budget, or unrelated to depth shortening; then the
"limited-inference shortcut" explanation is not supported. Reproducing the
expected pattern on a k-round symbolic reasoner is control validation;
whether the prediction transfers to learned recognizers is the empirical
question. Monotone decrease across all budgets is not assumed.

## RQ3. Which implementation keeps semantic invariance on new logical structures?

| candidate | purpose |
|---|---|
| exact semantic-closure oracle | the instrument detects guaranteed invariance |
| k-round symbolic reasoner | differences that arise from computation limits alone |
| iterative learned reasoner | whether iterated computation transfers to new structures |
| set encoder (existing) | baseline that supplies syntactic invariance only |

HYPOTHESIS: the iterative learned reasoner is less sensitive to
meaning-preserving rewrites than the set encoder on new depths and
branch/join structures.

Measure: disagreement rate on equivalent pairs over fresh structures as
the primary index, with accuracy and separation of logically distinct
pairs, so that a constant recognizer is never scored as "invariant".

Refutation / reduction: no difference, or a difference explained by
accuracy, training budget, or parameter count. Invariance enforced by
architecture is not counted as a finding of learning.

## RQ4 (OPEN, mathematical). Under which assumptions does a finite observation decide full-context identity?

Which of finite-state realization, state reachability, transition
coverage, or query coverage makes stability of a finite table imply
full-context equivalence? State and prove sufficient conditions; construct
counterexamples when a condition is dropped; separate assumptions the
instrument can check from those it cannot. "No counterexample in the
inspected table" and "identical in all contexts" must be connected, not
identified (`recognition-paths/Identification.lean` states the global
condition; a sampled table checks only refinement).

The monad question comes after: on the states and operations
reconstructed from observation, does a well-defined closure operation
exist, and is it extensive, monotone, idempotent? (OPEN.) Describing the
closure of the formal semantics and obtaining such an operation from the
recognizer's observation structure are different things.

## First experiment

RQ2 with RQ1's observation split. Fixed before running: the equivalence
relation and certification scope, D/F/C generation and exclusion rules,
models, budgets, output mode and tie handling, one primary comparison with
its effect criterion and uncertainty estimate, sample-size rationale in
units of logical structures and a fresh holdout, the exact oracle, the
non-reading control and the logic-change control, and the sentence that
will be reported if the prediction fails.

The first goal is one prediction, about what makes equal-meaning inputs
distinguishable, that holds on new cases. The operations and laws that
prediction requires will determine the next mathematical object.
