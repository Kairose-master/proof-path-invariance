# Recognition paths: when does a recognizer respect logical identity, and how would we know?

Working draft. Sections 1–3 are written from settled material; Sections 4–6
are placeholders to be filled from the results documents once the seed-1
replication and the 1.5B semantic-rewrite run are in. Labels follow
`AGENTS.md`: PROVED, OBSERVED, HYPOTHESIS, OPEN, CONFOUND.

## Abstract (draft)

Whether a language model "respects logic" has no answer until three things
are fixed: which logical identity, which behavioral identity, and which
finite family of tests decides between them. We fix all three. Logical
identity is theory-level Horn entailment on ordered premise traces;
behavioral identity is two-sided contextual indistinguishability at the
answer position; both are congruences on the same free monoid, and the
model respects logic exactly when the first refines the second. We prove in
Lean, without Mathlib, that this refinement is equivalent to the existence
of a unique canonical monoid morphism from the logical quotient to the
behavioral one; that premise reordering, repetition, and derivable-clause
extension are consequences of that single inclusion rather than independent
test relations; that a finite test family decides the question exactly when
the identity it induces is closed under one-symbol extension, a closure
failure naming the next test; and that the observation table's
biextensional collapse is the identifiable object. We then build an
instrument: frozen tables of prefix traces against continuation–query tests,
read through order relations on the answer logits so that identity is
exact, with preregistered statistics, a non-reading validity control, and a
surface-controlled contrast between a maximal logic-preserving rewrite and a
minimal logic-changing one. On three base and instruction-tuned models up
to 1.5B parameters, no two logically identical traces are ever behaviorally
identical; models that read the task are moved as much by permuting or
redundantly extending the premises as by reversing one arrow. A recognizer
built to be permutation-invariant by architecture and trained to 99%
accuracy is exactly the syntactic quotient and only partly the semantic
one. Reading the task, permutation invariance, and logical invariance are
three distinct properties, in that order of difficulty; neither accuracy
nor architectural invariance supplies the third.

## 1. Introduction

**The question.** Language models are sensitive to the order of premises
(Chen et al. 2024), inconsistent across logically equivalent reformulations
(LGMT 2026; CRTBench 2026), and their accuracy and their consistency come
apart. These findings share a form: a set of inputs that a logic declares
identical, and a model that treats them differently. What is missing is a
statement of the object being tested. Which identity on inputs? Which
identity on outputs? And since only finitely many inputs are ever tried,
when has the test family decided the question rather than sampled it?

**What we do.** We give the three definitions, prove what follows from them,
build an instrument that measures exactly what the definitions name, and
use it on measured and constructed recognizers.

**Contributions.** (i) A machine-checked framework in which "respects
logical identity" is the refinement of one congruence by another on a free
monoid, with the equational consequences, the finite-test identification
criterion, and the collapse of the observation table all proved
(`recognition-paths`, Lean 4 core, no Mathlib). (ii) A readout of answer
logits through order relations only, threshold-free and offset-invariant,
which makes identity exact and immune to answer bias, together with counts
of exactly identical profiles and collapse sizes. (iii) A surface-controlled
statistic, permutation against single-arrow flip, with a non-reading
validity control and a synthetic calibration. (iv) Constructed recognizers
that realise the syntactic half of logical identity by architecture, on
which the semantic half is measured in isolation.

**What we do not claim.** Order sensitivity and accuracy–consistency gaps
are known; our small-model findings replicate them. The mathematics is
classical (Myhill–Nerode, Angluin, Chu spaces); we assemble it and check it.
Nothing here concerns frontier models.

## 2. Framework (PROVED)

### 2.1 Traces, queries, logical identity

Fix a type of atoms. A Horn clause is a pair of atom lists (body, head); a
trace is a list of clauses; a query is a list of hypothesis atoms and a goal
atom. The theory of a trace, Γ(w), is its set of clauses. Entailment is
semantic: every valuation modelling Γ(w) and the hypotheses makes the goal
true. Two traces are logically identical, u ≡_L v, when they entail the same
queries. This is an equivalence and a two-sided congruence for
concatenation; since Γ forgets order and repetition it is commutative and
idempotent, so L = Σ*/≡_L is a commutative idempotent monoid. Permutations
are logically identical; appending a derivable clause is logically
invisible (`Horn.lean`).

### 2.2 Recognizers and behavioral identity

A recognizer is ρ : Σ* × Q → O. Right-context identity u ≡_ρ v asks that no
continuation and query separate u from v; two-sided identity u ≈_ρ v asks
the same in every left and right context. The latter is a congruence, so
B = Σ*/≈_ρ is a monoid. The Nerode quotient Σ*/≡_ρ is the extensional
collapse of the prefix realization (states = traces, tests = continuation–
query pairs), and B acts on it as its transition monoid; every state is
reached from the empty trace (`Recognition.lean`, `Nerode.lean`).

### 2.3 The factorization theorem and its consequences

≡_L ⊆ ≈_ρ holds iff there is a unique representative-preserving F : L → B;
F is then a monoid morphism. The reverse inclusion gives G : B → L; both
give L ≃ B. Under ≡_L ⊆ ≈_ρ, swapping two blocks of premises, repeating a
block, permuting a block, and appending a derivable clause are all
behaviorally invisible in every context. In the vocabulary of metamorphic
testing: reordering, duplication, and redundancy relations are not
independent; they are theorems of one inclusion (`Factorization.lean`,
`Recognition.lean`).

### 2.4 When a finite test family has decided

Let T be a family of tests (z, q) containing the direct queries ([], q).
The identity it induces, ≡_{ρ,T}, equals ≡_ρ if and only if it is closed:
u ≡_{ρ,T} v implies ua ≡_{ρ,T} va for every symbol a. When T is not closed
there exist u ≡_{ρ,T} v and a test (a·z, q) with (z, q) ∈ T separating them,
so the criterion is constructive. For length-bounded families, one more
level of continuation is one more symbol of prefix, and a stable level
identifies ≡_ρ. Two-sided versions hold for ≈_ρ (`Identification.lean`).
The counting bound (n Nerode classes force stabilisation by length n−1)
is standard and not formalised (OPEN).

### 2.5 The table as a Chu space

Quotienting tests by equal state profiles, dually to the state collapse,
gives the biextensional collapse, in which tests separate states and states
separate tests; silent extensions do not change it (`Biextensional.lean`).
The counts "distinct rows" and "distinct columns" of an observation table
are the sizes of these quotients. Under the broadest reading of "geometry",
this point–test duality is the geometry that cannot be removed; metric
structure is a further choice.

### 2.6 Specifications for constructed recognizers

A theory-factoring recognizer ρ(w, q) = f(Γ(w), q) is invariant under
permutation and repetition of blocks by construction; the ideal recognizer
ρ(w, q) = Entails(Γ(w), q) is logically invariant and recoverable, so
L ≃ B. The gap between them, identification of consequence-equivalent but
syntactically different clause sets, is what training must supply
(`Specification.lean`).

## 3. Instrument

### 3.1 Tables

Eight Horn logical classes over five atoms, chosen so that the class-level
gold matrix has full rank and half of its cells are positive. Rows are
prefix traces (serializations, and in later tables doubled prefixes,
single-arrow flips, derivable-clause extensions); columns are
continuation–query pairs. Four frozen tables (`hankel_v0`–`v3`), each with
a generator, an independent validator that re-derives every gold label, a
SHA-256 lock, and CI. Row equivalences inside a class are Lean-certified;
cell gold labels are forward-chaining, not Lean-certified per cell.

### 3.2 Readout

Each cell records the logit pair (positive candidate, negative candidate)
at the answer position, one forward pass, float32, no sampling. The
analysis reads only order relations: the decision [pos > neg] and, for two
queries after the same continuation, the preference [margin(q1) > margin(q2)].
This is threshold-free and invariant to the common logit offset, which had
made the raw metric table rank one, and it is immune to the answer-bias
saturation that discrete readouts inherit. Distances are Hamming counts of
separating tests: the number of columns of the Chu space that distinguish
two rows.

### 3.3 Statistics

All preregistered before the corresponding runs, with predictions recorded.
Gate R: comparative accuracy on query pairs whose gold labels differ. Gate
I: within-class median Hamming over between-class median. S: median over
classes of d_perm / d_flip on the surface-controlled table. T, U, V: on the
semantic-rewrite table, derivable extension against flip, length-matched
swap against flip, and the same on columns where gold ties so that accuracy
imposes nothing. E: counts of exactly identical profiles. A non-reading
recognizer (Pythia-70M) is the validity control; a synthetic
gold-plus-noise recognizer is the calibration showing that T and U are
passed by accuracy alone while V is not.

### 3.4 Three corrections

The instrument corrected itself three times, each recorded. A Euclidean
readout was dominated by a logit offset (rank one) and by scale differences
across renderers; the Boolean readout replaced it. Gate I, valid against
the control, was found to reward shared surface content: the class pair
differing only in the direction of all three arrows was closer than a class
to its own serializations; the surface-controlled contrast replaced it as
the primary statistic. The apparent invisibility of repeated continuations
was found in the control at the same rate and downgraded to a property of
the prompts.

## 4. Measured recognizers (OBSERVED) — to be filled from RESULTS_PHASE3_*.md

## 5. Constructed recognizers — to be filled from RESULTS_PHASE4.md after seed 1

## 6. Discussion, limitations, related work — see SYNTHESIS.md, NOVELTY.md, RELATED_WORK.md
