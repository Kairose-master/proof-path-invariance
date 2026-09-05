# Phase 2.9 — Surface-position versus finite-state update

Status: **EXPLORATORY / POST-HOC AFTER PHASE 2.6.**

Phase 2.9 tests the state-order model on the already observed Phase 2.6 data.
It does not create a new confirmatory result.

## Evaluation

The target is the YES-minus-NO logit margin centered within each complete S3
orbit. The outer split holds out one formal family. Ridge and soft-state
parameters are selected using only nested leave-one-family-out splits inside
the outer training families.

Models:

- M0: eight fixed surface-position features;
- M1: M0 plus strict, one-pass Horn support;
- M2: M0 plus one-pass support with retention, partial-conjunction, and
  reverse-implication parameters selected inside training data.

No family identifier or gold label is a predictor.

## Aggregate result

| Model | RMSE | SSE | Skill vs zero | Skill vs M0 |
|---|---:|---:|---:|---:|
| M0 surface-position | 0.050506 | 1.959043 | +0.024690 | — |
| M1 strict state | 0.051937 | 2.071645 | -0.031369 | -0.057478 |
| M2 soft state | 0.052931 | 2.151712 | -0.071230 | -0.098349 |

M1 and M2 improve over M0 in only 2 of 8 held-out-family folds. The frozen
exploratory decision rule required positive aggregate skill versus M0 and at
least 6 of 8 positive folds. The decision is therefore:

**DO NOT ADVANCE THIS STATE MODEL TO A FRESH CONFIRMATORY BENCHMARK.**

## Interpretation

The tested scalar readout of a one-pass reachability state does not explain the
observed order response beyond the surface-position baseline. Allowing three
soft error parameters makes held-out prediction worse.

This result rejects only the tested readout and update class on this dataset.
It does not establish that Pythia has no state-dependent processing. The
current benchmark was designed for three-premise permutation replication, not
to identify state transitions: its neutral-symbol cases repeat the same graph
within a family, and it lacks controlled pairs that keep two exchanged
premises fixed while varying the state immediately before them.

The next justified experiment is a diagnostic intervention benchmark. It
should cross the same exchanged premise pair with reachable versus unreachable
prefix states, atom renamings, renderer variants, and answer-token mappings.
That benchmark can distinguish a state-dependent exchange effect from position,
lexical, and answer-token effects before another generalization claim is frozen.

Full numeric output is written to `phase2_9_state_order_results.json` by the
analysis notebook.
