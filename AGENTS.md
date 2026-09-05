# AGENTS.md — Proof-Path Invariance Research Rules

This file defines the operating rules for coding and research agents working in this repository.

## Mission

Build a reviewer-defensible, machine-checked experimental pipeline for studying whether controlled changes in the presentation of formally certified logical entailments alter LLM judgments.

The repository must earn stronger structural claims step by step. Do not assume the conclusion the project may eventually investigate.

## Core epistemic rule

Always distinguish three levels of claim:

1. **Proved** — machine-checked in Lean or established by a cited theorem under stated assumptions.
2. **Observed** — supported by a specified empirical measurement in this repository.
3. **Hypothesized** — proposed explanation or model not yet established here.

Never silently promote a hypothesis to an observation, or an observation to a theorem.

In notes and code review, prefer explicit labels such as `PROVED`, `OBSERVED`, `HYPOTHESIS`, `OPEN`, and `CONFOUND` when the status could otherwise be ambiguous.

## No analogy inflation

Do not describe LLM behavior as categorical, functorial, geometric, Markovian, proof-theoretic, or homotopical merely because a mathematical analogy is available.

In particular, Phase 1 results must not be described as evidence that an LLM is a functor or that it possesses an intrinsic logical geometry.

A mathematical structure may be introduced as an empirical model only after lower-level measurements independently motivate its defining laws.

## Formal layer versus empirical layer

Keep these layers separate.

### Formal layer

Lean certifies logical facts used to construct experiments. Examples include implication transitivity, conjunction rules, derivations, substitutions, and—if later required—explicit proof transformations.

Lean does **not** certify claims about an LLM unless such a claim has itself been given a precise formal specification and justified independently.

### Empirical layer

The empirical layer measures model behavior under frozen interventions. Model outputs, error rates, disagreement rates, log probabilities, and statistical tests belong here.

Do not encode empirical expectations as Lean theorems.

## Dependency-first formalization

Before implementing a new logical or categorical construction, perform a dependency audit in this order:

1. Lean core.
2. mathlib.
3. Relevant maintained Lean libraries, including logic/formal-methods libraries.
4. Local implementation only if the required construction is absent, unsuitable, or would introduce unacceptable assumptions.

Record the result of nontrivial dependency audits in `docs/` or an issue. Do not reimplement substantial proof-theoretic infrastructure merely because doing so is convenient.

## Upstream policy

Do not modify or propose changes to Lean core merely to support this research project.

Research-specific definitions and theorems belong in this repository.

A contribution is an upstream candidate only when all of the following hold:

- it fills a genuine gap in the upstream library;
- it is useful independently of Proof-Path Invariance;
- its statement and API are appropriately general;
- it follows upstream style and dependency expectations;
- it has been exercised locally enough to justify the abstraction.

Prefer this sequence:

`local proof -> local use -> generalize -> assess upstream value -> upstream PR`

Never reverse it to obtain external validation for a research-specific abstraction.

## Object language before proof-path claims

Lean propositions such as `A -> B` are sufficient for the initial behavioral pilot, but they are not by themselves a formal representation of proof paths.

Before making claims about derivations, proof identity, proof factorization as data, or syntactic categories, introduce or reuse an explicit object language and derivation representation.

Do not infer:

`two Lean terms prove the same Prop` => `they are the same proof`.

Proof equality must always name the exact equivalence relation, quotient, rewrite theory, or definitional equality being used.

## Categorical claims require earned structure

Do not construct a syntactic category simply to make the project categorical.

A categorical layer is justified only when the relevant objects, morphisms, equality/congruence, identity, and composition have precise definitions and the category laws are machine-checked or imported from an appropriate established formalization.

If a quotient is used, prove that composition is well-defined on equivalence classes.

Even after a syntactic category exists formally, do not assume LLM behavior respects it. That is a separate empirical question.

## Current Phase 1 scope

The current confirmatory question is intentionally weak:

> Holding the target entailment fixed, does exposing a formally valid intermediate entailment alter an LLM's final entailment accuracy beyond matched presentation controls?

Use three conditions:

- `D`: direct presentation;
- `F`: presentation exposing a formally valid intermediate entailment;
- `C`: matched presentation control.

Primary comparison: `e_D` versus `e_F`.

Do not assume the direction of the effect. Do not call a D/F difference a composition failure.

## Experimental controls

Treat presentation effects as first-class confounds. At minimum consider:

- token and character length;
- premise count;
- premise order;
- lexical overlap;
- proposition naming;
- target truth value;
- inference family;
- decomposition depth;
- distractors;
- output format;
- model/version/date;
- decoding parameters.

A control described as logically irrelevant must either be formally certified under the chosen formalization or explicitly marked as not formally certified. Never hide this distinction.

Use constrained outputs such as `YES`/`NO` for primary scoring whenever possible. Free-form semantic grading should not be the Phase 1 primary outcome.

## Case provenance

Every empirical case must be traceable to its formal certificate family.

The validation pipeline must reject malformed or unapproved certificate references. CI must check both the Lean formal layer and empirical case construction.

Generated prompts should be deterministic from frozen case records. Do not hand-edit generated prompts after freezing a protocol.

## Negative cases

Do not build a benchmark containing only valid entailments. Add formally certified negative cases before substantive model evaluation so that trivial answer policies cannot achieve high accuracy.

Negative controls should be matched to positive cases as closely as practical without accidentally introducing another valid route to the target.

## Statistics and preregistration

Before inspecting confirmatory results, freeze:

- primary outcome;
- primary comparison;
- case-generation procedure;
- exclusions;
- sample-size or power rationale;
- model identifiers;
- decoding settings;
- planned uncertainty estimates/statistical tests.

Exploratory analyses must be labeled exploratory. Do not retrofit a post-hoc pattern into the preregistered hypothesis.

## Research escalation gates

Stronger claims are permitted only after the preceding gate is passed.

**Gate 0 — Formal validity:** Lean-certified experimental relations and auditable provenance.

**Gate 1 — Behavioral effect:** controlled D/F/C measurement with uncertainty.

**Gate 2 — Robustness:** effect survives relevant surface-form, ordering, naming, depth, and model-family perturbations.

**Gate 3 — Compositional model:** multiple independently tested composition-related regularities admit a stable quantitative description.

**Gate 4 — Categorical model candidate:** enough identity/composition/equivalence laws are empirically supported to justify testing a structure-preserving categorical model.

**Gate 5 — Optional probabilistic/geometry layer:** only after a precise probabilistic object exists and a particular geometric construction yields independently testable predictions.

HoTT, higher categories, diffusion geometry, Markov semantics, and similar structures are not default milestones. Introduce them only if an empirical or formal requirement specifically demands them.

## Novelty discipline

Absence from a quick literature search is not evidence of novelty.

Before making a novelty claim, compare against at least the relevant areas of:

- logical consistency/invariance benchmarks;
- metamorphic testing of LLMs;
- theorem proving and proof transformation;
- decomposition and chain-of-thought prompting;
- formal/categorical logic;
- Lean formalizations of the required logical machinery.

State the narrowest defensible difference from prior work. If novelty is unresolved, write `novelty not established`.

## Failure is informative

The project must remain publishable or scientifically useful even if the strong structural story fails.

A null or negative result should be reported at the level actually measured, for example:

- no detectable D/F difference under the tested protocol;
- an effect disappears after length matching;
- an effect is model-specific;
- behavior is unstable across equivalent serializations.

Do not turn a failed structural hypothesis into an unsupported philosophical conclusion.

## Coding rules

- Keep the Lean formal core small and auditable.
- Prefer explicit theorem names and short proofs over tactic-heavy opacity for certificate-critical results.
- Avoid unnecessary dependencies.
- Keep experiment generation deterministic and seed stochastic utilities.
- Store raw model outputs separately from derived metrics.
- Never overwrite raw results.
- Record model/provider metadata with each run.
- CI must fail on Lean build failures, malformed cases, or invalid certificate references.
- Add tests when fixing a case-generation or scoring bug.

## Definition of done for a new experimental family

A new inference family is not ready for evaluation until:

1. its formal relation is Lean-checked;
2. positive and negative cases are defined;
3. D/F/C construction is explicit;
4. known confounds are documented;
5. certificate provenance is machine-validated;
6. prompt generation is deterministic;
7. scoring requires no discretionary semantic interpretation for the primary metric;
8. CI passes;
9. the hypothesis attached to the family is no stronger than the measurement supports.

## Default decision rule for agents

When choosing between a more impressive abstraction and a weaker directly testable statement, choose the weaker statement.

When choosing between reimplementing mathematics and reusing a maintained formalization, audit and reuse first.

When choosing between calling something an analogy and calling it an equivalence, functor, invariant, or theorem, use the stronger term only after its defining conditions have been established.

The project succeeds by progressively earning structure, not by assuming it.
