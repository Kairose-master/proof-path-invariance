# Phase 3.4 Result — Surface-controlled contrast `hankel_v2`

Status: **FROZEN GATE S EVALUATED (`docs/PHASE3_HANKEL_V2_DESIGN.md`). DESCRIPTIVE OTHERWISE.**

Table SHA-256 `81695c3e…43b8`, 3328 prompts, one forward pass each.
Each of eight classes: base serialization, three permutations (maximal
surface change, no logical change), and two or three single-arrow flips
(minimal surface change, logical change). Depth-≤1 columns read as 80
Boolean tests per renderer.

| Run | Raw (compressed) | Summary |
|---|---|---|
| `qwen05b` | `experiments/runs/hankel_v2_qwen05b.jsonl.gz` (`5f6879ee…9ba4`) | `experiments/results/phase3_4_hankel_v2_qwen05b_summary.json` |
| `pythia70m` | `experiments/runs/hankel_v2_pythia70m.jsonl.gz` (`a35350b0…85c5`) | `experiments/results/phase3_4_hankel_v2_pythia70m_summary.json` |

## Gate S: `S = median over classes of d_perm / d_flip`, pass if `S < 1` and ≥ 6/8 classes

| Recognizer | Renderer | `S` | classes with `d_perm < d_flip` | comparative acc. | Outcome |
|---|---|---:|---:|---:|:---:|
| `qwen05b` | pooled | **1.27** | 3 / 8 | 0.842 | **fail** (predicted) |
| `qwen05b` | bullets | 0.75 | 5 / 8 | 0.904 | fail (5 < 6) |
| `qwen05b` | prose | 1.80 | 0 / 8 | 0.779 | fail |
| `pythia70m` | pooled | 0.97 | 4 / 8 | 0.480 | fail |

**Prediction check.** `qwen05b` was predicted at 0.8–1.5 and failing:
observed 1.27, fail. `pythia70m` was predicted "well above 1": observed
0.97. That prediction was wrong. The non-reading recognizer is not
surface-dominated on this contrast; both its permutation and its flip
distances are small (4–15 of 160 tests) and uncorrelated with anything,
so `S` sits at the noise value 1. The contrast is informative only for a
recognizer whose columns carry information.

## Per class, `qwen05b` pooled

| Class | `d_perm` | `d_flip` | ratio |
|---|---:|---:|---:|
| chain | 8 | 11 | 0.73 |
| fork_join | 17 | 11 | 1.55 |
| chain_gap | 16 | 18 | 0.89 |
| branch | 14 | 21 | 0.67 |
| reversed | 11 | 9 | 1.22 |
| fragments | 21 | 9 | 2.33 |
| gated | 23 | 17.5 | 1.31 |
| skip | 24 | 11 | 2.18 |

The classes where a one-arrow flip moves behavior more than reordering
are the simplest ones (`chain`, `branch`, `chain_gap`); in the classes
with a disconnected or gated clause (`fragments`, `skip`, `gated`)
reordering moves behavior two to three times more than a logical change.

EXPLORATORY: across the 20 flips, the Spearman correlation between the
size of a flip's logical change (gold-row Hamming) and its behavioral
distance is −0.11 for `qwen05b` and −0.38 for the control. How much
logic a flip changes does not predict how much behavior it changes.

## Reading

For Qwen2.5-0.5B-Instruct on this table, reordering the same three
premises moves behavior more than changing the direction of one arrow.
The within-class proximity that passed the Boolean Gate I in Phase 3.2
is therefore, at the pooled level, **predominantly surface**: shared
clause content, not shared logical content. Under the bullet renderer
there is a weak logic-favouring signal (5 of 8 classes, `S` 0.75) that
does not reach the gate; under the prose renderer there is none.

This closes the question opened in Phase 3.3. Gate I discriminates a
reader from a non-reader, but what it measures in the reader is mostly
the words.

## Scale: Qwen2.5-1.5B-Instruct on the same table

Raw `experiments/runs/hankel_v2_qwen15b.jsonl.gz` (`d8e8313b…3b6f`),
summary `experiments/results/phase3_4_hankel_v2_qwen15b_summary.json`.

| Recognizer | Renderer | `S` | classes `d_perm < d_flip` | comparative acc. | Gate S |
|---|---|---:|---:|---:|:---:|
| `qwen15b` | pooled | **0.99** | 4 / 8 | 0.889 | fail (class count) |
| `qwen15b` | bullets | 0.80 | 6 / 8 | 0.915 | **pass** |
| `qwen15b` | prose | 1.25 | 1 / 8 | 0.863 | fail |
| `qwen05b` | pooled | 1.27 | 3 / 8 | 0.842 | fail |

The recorded prediction was "`S` lower than for `qwen05b`, pass not
predicted": observed 1.27 → 0.99 pooled, with prose moving most
(1.80 → 1.25) and bullets flat (0.75 → 0.80). Under the bullet renderer
the 1.5B model passes Gate S: a one-arrow logical change now moves
behavior more than reordering in six of eight classes. Pooled it sits at
the boundary. Per class the largest moves are `branch` (0.67 → 0.48),
`reversed` (1.22 → 0.52), `fragments` (2.33 → 0.95) and `skip`
(2.18 → 1.38).

Two cautions. The 1.5B model has the opposite answer bias (positive on
7.9% of cells; decision accuracy 0.70), so its decision columns are no
longer constant and contribute to both distances. And two points do not
make a trend; the direction is consistent with "logic rises over surface
with scale within one family" (HYPOTHESIS) and nothing more.

## Calibration (post hoc, see the design document)

A synthetic gold-plus-noise recognizer with no invariance reaches `S`
0.5–0.6 with 8 of 8 classes. `S < 1` is therefore consistent with mere
accuracy; only `S > 1` is diagnostic. Read this way: `qwen05b` pooled
(1.27) and prose (1.80), and the 1.5B prose (1.25), are surface-dominated
beyond what accuracy explains; the passes (0.75–0.80 under bullets) are
what an accurate recognizer produces and say nothing further.

## What this does to the project's claim

The defensible sentence retreats from Phase 3.2 to:

> For every recognizer tested, including an instruction-tuned model that
> reads the task at 0.84–0.87 comparative accuracy, a maximal
> logic-preserving rewrite (permuting the premises) moves behavior at
> least as much as a minimal logic-changing rewrite (flipping one arrow),
> at the pooled level. The behavioral quotient of these recognizers on
> Horn traces is organised by surface content first and by logical
> content, if at all, second.

HYPOTHESIS for the scale run (`qwen15b`, `hankel_v1`, in progress; a
`hankel_v2` run on it is now the more informative follow-up): the
bullet-renderer signal (`S` 0.75, 5/8) strengthens with scale.
