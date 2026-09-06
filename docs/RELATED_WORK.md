# Related work — what already exists, and the narrowest defensible difference

Status: first pass from abstracts, then full-text reading of the starred
items (2026-09-06). The novelty statement that results is in
`docs/NOVELTY.md`.

## Directly overlapping

| Work | What it does | Overlap with this project |
|---|---|---|
| Chen et al. 2024, *Premise Order Matters* ([2402.08939](https://arxiv.org/abs/2402.08939)) | Permuting premise order drops GPT-4-class accuracy by >30% on deduction and math | Our Phase 1–3 finding that serialization moves behavior is a small-model replication, not new |
| ★ LGMT 2026, *Logic-Grounded Metamorphic Testing* ([2605.23965](https://arxiv.org/abs/2605.23965)) | Metamorphic relations derived from first-order logical equivalences (formula-, symbol-, premise-, conclusion-level, including predicate renaming); cross-case consistency on six frontier LLMs | The idea "logically equivalent inputs must get the same judgement, so test invariance" is theirs at scale. Our `≡_L` test family is a special case |
| ★ CRTBench 2026, *Controlled Reformulation Testing* ([2607.14528](https://arxiv.org/html/2607.14528)) | 350 question families; contrapositive, double negation, negation flip, passive; reports accuracy–consistency gaps in frontier models | "Reads the task but is not invariant" (our Gate R pass / Gate I fail) already exists as the accuracy–consistency gap |
| ★ *Robustness on Parameterized Logical Problems* 2026 ([2602.12665](https://arxiv.org/html/2602.12665)) | 2-SAT families with controlled structure; clause reordering, filler clauses, variable renaming; explicitly separates surface difficulty from structural phenomena | Closest in spirit to our surface-controlled contrast; they hold surface fixed and vary structure, we vary surface maximally while holding logic fixed against a minimal logic change |
| Set-LLM 2025 ([2505.15433](https://arxiv.org/abs/2505.15433)) | Permutation-invariant LLM via attention mask and positional encoding, with a proof of invariance; removes option-order bias | Our Phase 4 arm `set` is this idea at toy scale |
| *Order-Centric Augmentation* 2025 ([2502.19907](https://arxiv.org/abs/2502.19907)) | Trains LLMs with premise and reasoning-step reorderings | Our Phase 4 arm `seq_aug` at toy scale |
| Lacroce et al. 2021 ([2106.02965](https://arxiv.org/abs/2106.02965)); Weiss et al. 2018; Okudono et al. 2020; *Automata Extraction from Transformers* 2024 ([2406.05564](https://arxiv.org/pdf/2406.05564)) | Extract (weighted) automata from black-box sequence models; Hankel matrices, spectral norm, AAK theory | Our Hankel-table framing and Nerode quotient are this literature's objects |
| Angluin 1987; Myhill–Nerode; Larsen–Skou; Pratt (Chu spaces) | Classical | Every theorem in `recognition-paths` is an instance or restatement |

## What, on this evidence, is not already done

These are candidates, each to be checked against the full texts.

1. **A machine-checked quotient framework for the comparison.** Logical
   and behavioral identity as two congruences on one free monoid, the
   factorization criterion, the equational consequences of invariance
   (commutativity, idempotence), the finite-test identification criterion
   with its refinement witness, and the biextensional collapse, all in
   Lean. The metamorphic-testing papers state relations; they do not
   state what a finite test family can and cannot conclude.
2. **Exact versus approximate identity on a Boolean table**, with the
   count of exactly identical profiles and the collapse sizes, and a
   non-reading validity control for the approximate statistic. The
   consistency literature reports agreement rates; whether any two
   equivalent inputs are ever *exactly* identified appears not to be
   asked.
3. **The flip-versus-permutation contrast** as a single dimensionless
   statistic `S` with a validity control. 2602.12665 is the nearest and
   must be read in full.
4. **The theory-factoring versus ideal distinction.** A permutation-
   invariant recognizer (Set-LLM, our `set`) is invariant under the
   syntactic part of `≡_L` by construction. Whether it identifies
   consequence-equivalent but syntactically different clause sets is a
   different question, and it is the one the specification in
   `Specification.lean` isolates. Neither Set-LLM nor the augmentation
   paper appears to ask it. This needs a table of consequence-equivalent
   rewrites (redundant clauses, alternative axiomatisations), not yet
   built (`hankel_v3`).
5. Measured LLMs and constructed recognizers evaluated on the **same
   frozen table** with the same statistics.

## What this changes

- The empirical headline "small models are order-sensitive and read the
  task without respecting equivalence" is known. It is a replication and
  should be presented as one.
- The contribution, if any, is the instrument (1–3) and the question in
  (4). Phase 4 should be re-centred on (4): the difference between
  permutation invariance and logical invariance, which the constructed
  `set` model makes testable in isolation.
- The paper sentence in `SYNTHESIS.md` is downgraded accordingly.

## To read in full before writing

LGMT (2605.23965), CRTBench (2607.14528), Parameterized Logical Problems
(2602.12665), Set-LLM (2505.15433), Order-Centric Augmentation
(2502.19907), *Do LLMs Game Formalization?* (2604.19459), and the
inconsistency survey literature ([2505.18658](https://arxiv.org/pdf/2505.18658)).
