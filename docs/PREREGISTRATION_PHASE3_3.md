# Phase 3.3 Preregistration — Control and scale on the Boolean table

Status: **FROZEN BEFORE INSPECTING ANY RESULT OF THESE RUNS.** The control
run was launched at 2026-09-06T00:0xZ; this document is committed while it
runs and before any of its output is read. The scale run starts after it.

## Purpose

Phase 3.2 found that `qwen05b` passes both Boolean gates on `hankel_v1`.
Two questions must be answered before that result carries weight.

1. **Is the Boolean Gate I too easy?** A recognizer that does not read the
   prefix at all would have within-class and between-class Hamming
   distances that are both noise, hence a ratio near 1. If a non-reading
   recognizer passes Gate I, the gate is invalid.
2. **Does scale inside the instruction-tuned family move the ratio and
   the exact-identity count?**

## Held fixed

`hankel_v1` unchanged (SHA-256 `53028d8b…d1fa`), runner unchanged,
analysis `scripts/analyze_hankel_v1.py` unchanged, gates as in
`docs/PHASE3_HANKEL_V1_DESIGN.md`:

- Gate R: pooled comparative accuracy `> 0.55`;
- Gate I: pooled within-class median Hamming / between-class median
  Hamming `< 1`.

## Recognizers

| Tag | Model | Role |
|---|---|---|
| `pythia70m` | `EleutherAI/pythia-70m` @ `step143000` | control: known not to read the task |
| `qwen15b` | `Qwen/Qwen2.5-1.5B-Instruct` @ `main` | scale: same family as `qwen05b`, 3× parameters |

If memory forces it, the scale run uses 2 shards instead of 4; the
per-prompt computation is unchanged.

## Recorded predictions (before data)

- `pythia70m`: fails Gate R (comparative accuracy 0.45–0.55) and fails
  Gate I (ratio 0.9–1.1). If it passes Gate I, Gate I is declared invalid
  and the Phase 3.2 pass is withdrawn pending a corrected statistic.
- `qwen15b`: passes Gate R (comparative accuracy above 0.90); passes
  Gate I with a lower ratio than `qwen05b` (below 0.5); the number of
  classes with exactly identical serialization profiles stays 0 or 1 of 8;
  the depth-one family remains not closed; repeated-continuation agreement
  stays above 0.95.

## Interpretation boundary

A valid control plus a scale trend supports, and only supports, the
statement that approximate logical invariance under the Boolean readout
increases with scale within one instruction-tuned family. Exact invariance
and closure remain separate questions.
