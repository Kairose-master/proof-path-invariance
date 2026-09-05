# Phase 3.1 Result — Cross-recognizer replication of `hankel_v0`

Status: **PREREGISTERED GATES EVALUATED (`docs/PREREGISTRATION_PHASE3_1.md`). DESCRIPTIVE OTHERWISE.**

The frozen table (SHA-256 `9491e21e…3dcf`) was run unchanged on two further
recognizers with the same runner. Raw rows, manifests and summaries:

| Tag | Model | Raw (compressed) | Summary |
|---|---|---|---|
| `pythia70m` | `EleutherAI/pythia-70m` @ `step143000` | `experiments/runs/hankel_v0_pythia70m.jsonl.gz` | `experiments/results/phase3_hankel_v0_summary.json` |
| `pythia410m` | `EleutherAI/pythia-410m` @ `step143000` | `experiments/runs/hankel_v0_pythia410m.jsonl.gz` | `experiments/results/phase3_1_pythia410m_summary.json` |
| `qwen05b` | `Qwen/Qwen2.5-0.5B-Instruct` @ `main` | `experiments/runs/hankel_v0_qwen05b.jsonl.gz` | `experiments/results/phase3_1_qwen05b_summary.json` |

## Preregistered gates (median over the 16 controls)

| Recognizer | AUROC | Gate R (`> 0.55`) | `R = Δ_inv / median sep.` | Gate I (`< 1`) |
|---|---:|:---:|---:|:---:|
| `pythia70m` | 0.519 | fail | 3.01 | fail |
| `pythia410m` | 0.468 | fail | 2.95 | fail |
| `qwen05b` | 0.770 | **pass** | 1.35 | fail |

**Recorded prediction:** `pythia410m` fails both; `qwen05b` passes Gate R
and fails Gate I. **Outcome:** the prediction holds on the preregistered
criteria. The "malfunctioning machine" reading, which expects a recognizer
that reads the task to also identify logical equivalents, is not supported
at the pooled level.

## All seven frozen quantities (min / median / max over controls)

| Quantity | `pythia70m` | `pythia410m` | `qwen05b` |
|---|---|---|---|
| `Δ_inv` | 0.394 / 0.947 / 1.432 | 0.291 / 0.525 / 0.780 | 0.263 / 0.423 / 0.739 |
| min class separation | 0.030 / 0.123 / 0.185 | 0.052 / 0.084 / 0.131 | 0.114 / 0.135 / 0.225 |
| median class separation | 0.159 / 0.270 / 0.399 | 0.090 / 0.177 / 0.289 | 0.261 / 0.341 / 0.490 |
| class pairs separated at `Δ_inv` (of 28) | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 8.5 / 17 |
| raw rank at `10⁻³·σ₁` | 1 / 1 / 1 | 2 / 4.5 / 6 | 3 / 5 / 7 |
| AUROC | 0.357 / 0.519 / 0.574 | 0.368 / 0.468 / 0.637 | 0.656 / 0.770 / 0.851 |
| closure defect at `ε = Δ_inv` | 0.519 / 1.133 / 1.533 | 0.342 / 0.639 / 1.135 | 0.388 / 0.563 / 0.863 |

## Observations

- **OBSERVED (scale alone):** from 70M to 410M in the same family, absolute
  order sensitivity halves, but class separation halves with it. The ratio
  `R` is unchanged (3.01 → 2.95) and the readout stays at chance. Scale did
  not move the recognizer toward the logical quotient.
- **OBSERVED (instruction-tuned family):** `qwen05b` reads the task (AUROC
  0.77) and is the first recognizer for which some class pairs are separated
  by more than the invariance defect (up to 17 of 28 in one control). Its
  `R` is still above 1 at the median.
- **OBSERVED (threshold miscalibration):** although the ranking is
  informative, the sign of the margin is not: with the bullet renderer
  `qwen05b` predicts positive on essentially every cell (accuracy at the
  base rate 0.44), and with the prose renderer and the True/False map it
  predicts negative on essentially every cell. This is the concrete case for
  the threshold-free comparative readout of `hankel_v1`.

## EXPLORATORY — not preregistered: the renderer decides Gate I

Splitting `qwen05b` by renderer:

| Renderer | `R` median (range) | controls with `R < 1` | AUROC median |
|---|---:|---:|---:|
| bullets | 0.88 (0.63–1.20) | 6 of 8 | 0.84 |
| prose | 1.68 (1.50–2.18) | 0 of 8 | 0.72 |

With the bullet-list renderer, logically identical rows are closer than the
typical pair of logically distinct classes in six of eight controls; with
the prose renderer they never are. The recognizer's approximate invariance
is a property of the presentation format, not of the recognizer alone.
This split was not preregistered and is reported as a hypothesis for the
Phase 3.2 table, which uses both renderers with a threshold-free readout.

## What this result is and is not

It is: the first measurement in this project of a recognizer whose behavior
carries logical signal, with the invariance defect and class separation on
the same scale, and the separation of "reads the task" from "identifies
logical equivalents" on preregistered criteria.

It is not: a demonstration that any recognizer realises the logical
quotient (no `R < 1` at the pooled level), or evidence about the relative
roles of tuning and scale beyond these three models.

## Next

Run `hankel_v1` on `qwen05b` (both renderers, comparative readout, depth-two
continuations, idempotence probes). Its Boolean gates test the renderer
hypothesis above with exact equalities and no threshold, and its closure
check becomes meaningful for the first time on a recognizer with `R` near 1.
