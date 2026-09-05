# Dependency Audit — Logic and Categorical Infrastructure

Status: initial audit, 2026-09-05. This document records what should be reused before PPI implements new formal machinery.

## Decision summary

**Phase 1 does not need a custom proof calculus or syntactic category.** The current shallow Lean certificates are sufficient for the first D/F/C behavioral pilot.

For later proof-path and categorical phases, do **not** build the logical stack from scratch. Existing libraries already cover substantial pieces. The likely local gap is the research bridge from machine-checked derivational structure to reproducible experimental interventions, not basic logic itself.

## 1. Lean core

Use Lean core for the current proposition-level certificates. Curry–Howard gives us ordinary propositions and proof terms, so elementary implication/conjunction certificates need no extra dependency.

Limit: two Lean terms inhabiting the same proposition do not by themselves provide the explicit object-language proof identity/equivalence relation needed for later proof-path claims.

Decision: **REUSE for Phase 1.**

## 2. mathlib model theory

Relevant existing modules include:

- `Mathlib.ModelTheory.Syntax`
  - first-order `Term`, `BoundedFormula`, `Formula`, `Sentence`, `Theory`;
  - relabeling and substitution operations;
  - language maps acting on syntax.
- `Mathlib.ModelTheory.Semantics`
  - realization of terms/formulas/sentences;
  - `M ⊨ φ` and theory models;
  - theorems showing syntactic operations such as substitution/relabeling commute appropriately with realization.
- `Mathlib.ModelTheory.Equivalence`
  - semantic implication `φ ⟹[T] ψ`;
  - semantic equivalence `φ ⇔[T] ψ`;
  - reflexivity/transitivity-style infrastructure.

Important upstream signal: `Mathlib.ModelTheory.Equivalence` currently documents a TODO to define the quotient of formulas modulo `⇔[T]` and its Boolean algebra structure. This is relevant to future quotient-based syntax, but PPI must not assume that implementing this TODO is automatically our job or automatically upstream-worthy.

Decision: **REUSE/AUDIT MORE before any local FOL syntax or semantic-equivalence implementation.**

## 3. mathlib category theory

mathlib already provides the general category-theory infrastructure we would need later: categories, functors, natural transformations, functor categories, products, categories of types, etc.

Decision: **REUSE. Never implement a generic category/functor layer locally.**

Open question: whether there is already a maintained construction matching the exact syntactic category required by our chosen logical calculus. Do not infer absence from the initial search; perform a targeted audit before Gate 4.

## 4. FormalMathematicsLab/lean4-logic

Repository: `FormalMathematicsLab/lean4-logic` (fork lineage from FormalizedFormalLogic/Foundation).

The project explicitly formalizes logic in Lean 4 and depends on mathlib. Its documented surface includes:

- classical propositional derivations in a Tait calculus with cut;
- soundness and completeness;
- intuitionistic propositional deduction plus Kripke semantics;
- first-order derivations in Tait calculus with cut;
- first-order Tarski semantics;
- cut elimination;
- theory interpretation;
- arithmetic and incompleteness infrastructure;
- modal logic.

This means PPI should not create a substantial custom derivation calculus merely to obtain "derivations as data" without first checking whether this library's derivation objects and APIs fit the experiment.

Caution: suitability is not established merely because the concepts exist. Before adding it as a dependency, check version compatibility, maintenance status, API stability, license, and whether its proof representation supports the exact transformations we need.

Decision: **CANDIDATE REUSE; targeted compatibility spike required.**

## 5. What is actually missing for PPI right now?

The current experimentally relevant gap is not a theorem such as implication transitivity. It is the bridge:

`formal certificate -> case provenance -> controlled D/F/C realization -> frozen prompt -> raw model output -> analysis`

PPI already owns the beginning of this bridge through certificate metadata, case validation, deterministic prompt generation, and CI.

The next formal gap is narrower: negative and control cases should be certified strongly enough that the benchmark does not rely on an informal claim of irrelevance.

## 6. Immediate implementation decision

Before adding mathlib or lean4-logic as dependencies:

1. Keep the current proposition-level Lean core for the pilot.
2. Replace pilot-only informal `C` controls with a formally specified control construction.
3. Add formally certified negative cases so a constant-YES policy cannot score well.
4. Freeze a benchmark v0 only after positive, negative, and control provenance is machine-auditable.
5. Separately run a small compatibility spike for `lean4-logic` before Gate 3/4 work.

## 7. Upstream decision rule

No Lean-core PR is justified by current needs.

No mathlib PR is justified yet.

An upstream PR becomes a candidate only if local work reveals a general missing lemma/construction that:

- naturally belongs to an existing upstream namespace/API;
- is independent of PPI's LLM experiment;
- is not already present under another formulation;
- has a reusable statement and tests;
- is accepted in principle by upstream maintainers/style expectations.

The formula-quotient TODO in mathlib is a **lead**, not an assignment.

## 8. Gate map

- Gate 0 / Phase 1: Lean core is sufficient.
- Negative/control certification: local small formalization is appropriate.
- Explicit derivations/proof transformations: audit `lean4-logic` first.
- FOL syntax/semantics/equivalence: audit/reuse mathlib first.
- Generic category theory: reuse mathlib.
- Syntactic category: targeted audit; implement locally only if genuinely missing and empirically motivated.
- Upstream contribution: only after local use demonstrates a general gap.

## References checked

- mathlib: `Mathlib.ModelTheory.Syntax`
- mathlib: `Mathlib.ModelTheory.Semantics`
- mathlib: `Mathlib.ModelTheory.Equivalence`
- mathlib category-theory documentation
- `FormalMathematicsLab/lean4-logic` README and package configuration

This audit should be updated whenever a dependency decision changes.
