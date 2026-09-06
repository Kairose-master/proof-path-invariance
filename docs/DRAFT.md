# Recognition paths: when does a recognizer respect logical identity, and how would we know?

Working draft (2026-09-06). All sections written and all runs in. Labels follow `AGENTS.md`: PROVED, OBSERVED,
HYPOTHESIS, OPEN, CONFOUND. Source and data: github.com/Kairose-master/
{recognition-paths, proof-path-invariance}; huggingface.co/jinu0633.

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

## 4. Measured recognizers (OBSERVED)

Recognizers: Pythia-70M and Pythia-410M (base, `step143000`),
Qwen2.5-0.5B-Instruct and Qwen2.5-1.5B-Instruct (raw prompts, no chat
template), one forward pass per prompt in float32 on CPU, both answer
logits recorded.

### 4.1 Reading is not identifying

On the Boolean table (`hankel_v1`), Gate R and Gate I with their controls:

| recognizer | comparative acc. (Gate R > 0.55) | within/between median Hamming (Gate I < 1) |
|---|---:|---:|
| Pythia-70M | 0.456 | 1.42 |
| Qwen2.5-0.5B | 0.867 | 0.561 |

Qwen reads the task and passes Gate I; the control fails both, so the gate
discriminates. But no recognizer has a single logical class whose
serializations have identical profiles (0 of 8 for every recognizer, all
40 rows distinct), and under a matched between-class statistic the control
also falls below 1. Gate I rewards shared surface content: for Qwen the
class pair differing only in the direction of all three arrows is closer
than a class to its own serializations. This is CRTBench's accuracy–
consistency gap at small scale, with the addition that the readout is
exact: identity never occurs.

### 4.2 Surface outweighs logic, and scale moves it

On the surface-controlled table (`hankel_v2`), `S` = median over classes
of d_perm / d_flip:

| recognizer | `S` pooled | bullets | prose | comparative acc. |
|---|---:|---:|---:|---:|
| Pythia-70M (control) | 0.97 | 1.20 | 1.11 | 0.48 |
| Qwen2.5-0.5B | 1.27 | 0.75 | 1.80 | 0.84 |
| Qwen2.5-1.5B | 0.99 | 0.80 | 1.25 | 0.89 |

The statistic is one-sided: an accurate recognizer with no invariance
reaches 0.5–0.6 because flips change gold decisions it tracks. So the
diagnostic values are the ones above 1: for the 0.5B reader, and under the
prose renderer at both scales, reordering the same three premises moves
behavior more than reversing one arrow. From 0.5B to 1.5B the pooled value
falls from 1.27 to 0.99 (HYPOTHESIS: logic rises over surface with scale
within the family; two points).

### 4.3 Semantic rewrites are not identified

On the semantic-rewrite table (`hankel_v3`), a derivable-clause extension
(Lean-certified logically invisible) against a flip:

| recognizer | `T` red/flip | `V` free columns | `E` exact identities |
|---|---:|---:|---:|
| Pythia-70M (control) | 1.00 | 1.50 | 0 / 14 |
| Qwen2.5-0.5B | 1.11 | 1.50 | 0 / 14 |
| Qwen2.5-1.5B | 0.62 | 1.01 (bullets 0.67, prose 1.10) | 0 / 14 |

For the 0.5B reader a logically invisible extension moves behavior as much
as a logical change, and more where accuracy imposes nothing (`V` 1.5,
equal to the control). At 1.5B `V` falls to the no-identification value
pooled and to 0.67 under the list renderer, with no exact identification
(HYPOTHESIS: identification on accuracy-free columns begins with scale,
renderer first). The behavioral quotient of the 0.5B model does not
contain the consequence relation at any level the table sees.

### 4.4 Closure, idempotence, and what is generic

The depth-one test family is not closed for any measured recognizer; for
Qwen the witness pair is logically identical and separated only at depth
two, the situation the identification theorem describes. Repeated
continuations agree with their single versions on about 95% of tests for
reader and control alike, so this is a property of the prompts, not of
logic. The largest single source of within-class distance is a
first-premise primacy effect on the query mentioned first (CONFOUND), and
the atom-label family changes the metric invariance defect by about 3×
(CONFOUND). Premise-by-premise margin increments are right-skewed,
heavy-tailed, drift toward the positive answer, do not accumulate with
depth, and shrink with level: not a diffusion (EXPLORATORY).

## 5. Constructed recognizers

Three recognizers trained on synthetic Horn traces with the eight
evaluation classes held out up to atom relabelling, 6000 steps, batch 128:
`set` (max-pooled clause encodings: permutation- and repetition-invariant
by construction, ~170k parameters), `seq_aug` (causal transformer with
permutation/repetition augmentation, ~100k) and `seq_fixed` (the same
without augmentation). Evaluated on the same tables through the same
statistics; one rendering, so no renderer split.

### 5.1 The syntactic half, exactly

The `set` recognizer is, on `hankel_v1`, exactly the syntactic quotient:
its 40 rows collapse to the 8 logical classes, all eight classes have
identical serialization profiles, `S` = 0 on `hankel_v2`, and the
depth-one family is closed. Both seeds. No causal recognizer, at any of
four seeds or at three times the budget (validation accuracy 0.98), has
one class with identical profiles or fewer than 39 distinct rows.
Augmentation buys approximate permutation invariance (`S` 0.49 at
convergence); architecture buys exact invariance; accuracy buys neither.

### 5.2 The semantic half, partly

On `hankel_v3` the `set` recognizer, 99% accurate on classes it never saw,
identifies none of the 14 derivable-clause extensions exactly in one seed
and two in the other; on the columns where accuracy imposes nothing it
moves 0.62–0.80 times as far under a semantic rewrite as under a logical
flip. Every LLM, the control, and seven of eight causal toy runs have `V`
above 1 (medians 1.5–2.3). So the architecturally invariant recognizer is
the only one in which a semantic rewrite is detectably less disruptive
than a logical change, and even there most of the semantic half is
missing and almost none of it is exact. (Two seeds; suggestive.)

### 5.3 What the constructed recognizers add

They separate three properties that the LLM measurements conflate:
reading the task (all accurate recognizers), permutation invariance
(exact only by architecture, approximate by augmentation), and logical
invariance (present partly, and only where the syntactic half was
exact). They also show that `S < 1` and Gate I are reached by accuracy
and surface alone, which fixes the reading of Section 4.

## 6. Discussion

**Three properties, ordered.** Reading the task, respecting the syntactic
part of logical identity, and respecting its semantic part are distinct,
and every recognizer we measured or built sits on that ladder at a
different rung. Accuracy does not climb it; architecture climbs one rung
exactly; nothing we tried climbs the last.

**What a finite table can conclude.** By the identification theorem, a
test family decides `≡_ρ` when it is closed. On the measured recognizers
the depth-one family is not closed, and the theorem names the column a
deeper table needs. On the `set` recognizer the same family is closed,
which is the theorem working as intended: the recognizer's quotient is
coarse enough for the family to capture it.

**Exact versus approximate.** A statistical recognizer never produces two
identical profiles for logically identical inputs; the exceptions here are
forced by construction. The right long-run object is a canonical distance
with a certified tolerance, not an equality (OPEN).

**Metric and duality.** Metric geometry on the logits misled twice
(offset, scale); the Boolean readout keeps only the point–test duality of
the Chu space, and every exact statement in this paper lives there.

**Limitations.** One Horn fragment, five atoms, eight classes; models up to
1.5B without chat templates; no sampling; toy constructed models at one
or four seeds; gold labels by forward chaining, not certified per cell.

**Related work and novelty.** `RELATED_WORK.md`, `NOVELTY.md`: the empirical
phenomena are known; the framework, the exact readout, the one-sided
surface statistic with its control, and the separation of permutation from
logical invariance are, on the texts read, not.
