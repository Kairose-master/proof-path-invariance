# Draft outline — "Recognition paths: when does a recognizer respect logical identity, and how would we know?"

Status: skeleton with claims mapped to evidence. Numbers marked ⟨pending⟩
come from runs not yet finished (Phase 3.5 `hankel_v3`; Phase 4
constructed recognizers). Every claim keeps its `AGENTS.md` label.

## 1. Introduction (1 page)

- The question "does a language model respect logic" has no answer until
  three things are fixed: which logical identity, which behavioral
  identity, and which finite family of tests. Prior work fixes none of
  them formally (LGMT, CRTBench, Param-SAT: `docs/NOVELTY.md`).
- Contributions: (i) a machine-checked framework that fixes all three and
  derives which invariance tests follow from which and when a finite
  family has decided the question; (ii) an order-relation readout that
  makes the question exact; (iii) a controlled contrast with a validity
  control; (iv) the separation of permutation invariance from logical
  invariance, measured on constructed recognizers.
- What is not claimed: novelty of order sensitivity or of accuracy–
  consistency gaps; anything about frontier models.

## 2. Framework (PROVED; `recognition-paths`)

- 2.1 Horn traces, queries, `≡_L`; `L` commutative idempotent monoid.
  (`Horn.lean`)
- 2.2 Recognizers, `≡_ρ`, `≈_ρ`; `B` monoid; Nerode quotient = extensional
  collapse of the prefix realization; `B` acts on it.
  (`Recognition.lean`, `Nerode.lean`)
- 2.3 Recognition Factorization Theorem; both directions; `F` a monoid
  morphism; invariance forces commutativity, idempotence, permutation
  invisibility. (`Factorization.lean`, `Recognition.lean`)
- 2.4 Finite-test identification: closed ⇔ identifies; refinement
  witness; stabilisation. (`Identification.lean`)
- 2.5 Biextensional collapse; the Hankel table as a Chu space.
  (`Biextensional.lean`)
- 2.6 Specifications: theory-factoring vs ideal recognizer; the gap.
  (`Specification.lean`)
- Remark: all mathematics classical (Myhill–Nerode, Angluin, Chu); the
  contribution is the assembly and the machine-checked map from
  metamorphic relations to one inclusion.

## 3. Instrument (`proof-path-invariance`)

- 3.1 Tables: `hankel_v0` (metric), `hankel_v1` (Boolean, depth 2,
  idempotence probes), `hankel_v2` (flip vs perm), `hankel_v3`
  (derivable extensions). Lock files, validators, CI.
- 3.2 Readout: logit pair; order relations only; why (offset artefact,
  bias saturation): `RESULTS_PHASE3_HANKEL.md`, `RESULTS_PHASE3_2.md`.
- 3.3 Statistics and gates, all preregistered: R, I, S, T, U, V, E;
  validity control (Pythia-70M) and synthetic calibration.
- 3.4 How the instrument corrected itself three times
  (`RESULTS_PHASE3_1.md`, `RESULTS_PHASE3_3.md`, `RESULTS_PHASE3_4.md`):
  a methods result in its own right.

## 4. Measured recognizers (OBSERVED)

- 4.1 Reading vs identifying: Gate R / Gate I table for 70M, 410M, 0.5B
  (`RESULTS_PHASE3_1.md`, `RESULTS_PHASE3_2.md`, `RESULTS_PHASE3_3.md`).
  Framed as a small-scale replication of CRTBench's gap with an exact
  readout: no two logically identical traces are ever behaviorally
  identical (0/8 classes, all recognizers).
- 4.2 Surface outweighs logic: `S` for 0.5B (1.27), 1.5B (0.99; bullets
  0.80 pass), control (0.97 noise). Per-class table; renderer dependence.
  (`RESULTS_PHASE3_4.md`)
- 4.3 Closure and idempotence: depth-one family not closed (witness);
  repeated continuation invisibility generic. (`RESULTS_PHASE3_2.md`,
  `RESULTS_PHASE3_3.md`)
- 4.4 Semantic rewrites on LLMs: `T`, `U`, `V`, `E` for 70M and 0.5B.
  ⟨pending: Phase 3.5⟩
- 4.5 Exploratory: primacy effect; increment statistics (not a diffusion).
  (`EXPERIMENT_LOG.md`)

## 5. Constructed recognizers (Phase 4)

- 5.1 `set`, `seq_aug`, `seq_fixed`; held-out classes; same tables.
- 5.2 `hankel_v2`: `S` for each. ⟨pending⟩
- 5.3 `hankel_v3`: `V` and `E` for `set`: does training supply the
  semantic half? ⟨pending⟩ This is the paper's central experiment.
- 5.4 Comparison with measured LLMs on the same statistics.

## 6. Discussion

- Reading, permutation invariance, logical invariance: three properties,
  ordered; where each recognizer sits.
- What a finite table can conclude (closure) and what it cannot (exact
  `≈_ρ`).
- Metric versus Boolean readouts; the duality reading of "geometry".
- Limitations: Horn fragment, five atoms, ≤ 1.5B, no sampling, no chat
  template, toy constructed models.

## 7. Related work

`docs/RELATED_WORK.md`, `docs/NOVELTY.md`.

## Appendices

Lean listing; table specifications; preregistrations verbatim; all
per-class numbers; the three corrections.

## Figures (planned)

1. The two quotients and the canonical map (diagram).
2. Gate R vs Gate I scatter, recognizers as points.
3. `S` per class and recognizer; renderer split.
4. `V`/`E` for constructed recognizers vs LLMs. ⟨pending⟩
