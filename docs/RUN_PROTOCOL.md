# Run Protocol

The benchmark input is frozen independently of any model provider. A model run
is identified by a run manifest plus an append-only raw result JSONL file.

## Before collection

Copy `experiments/runs/manifest.template.json` to a new run-specific file and
replace every `FILL-BEFORE-RUN` value.

Freeze at minimum:

- provider;
- exact model identifier exposed by the provider;
- observed version or snapshot identifier if available;
- UTC access date;
- decoding parameters;
- repeats per prompt;
- response constraint;
- runner commit;
- system prompt, including an explicit `null` if none is used.

The manifest must reference the frozen paired-prompt SHA-256:

`63ab9a22ef8d77b22d6e9c4538cf94efa00a7f143d7ac4a23391eeb950ae9e1e`.

## Raw results

Never overwrite raw outputs. Store one JSON object per model call.

The primary scorer uses only `raw_text` after mechanical normalization:

1. trim surrounding whitespace;
2. uppercase;
3. accept only exactly `YES` or `NO`;
4. otherwise mark `INVALID`.

No semantic repair, regex rescue, or human adjudication is allowed for the
confirmatory primary outcome.

## Repeated sampling

If `repeats_per_prompt = r`, every one of 512 prompts must have exactly
`r` rows with sample indices `0 ... r-1`.

Do not stop early after surprising answers.

## Provider drift

If a provider silently changes the served model, or the exposed model
identifier/version changes during collection, stop the run and start a new
`run_id`. Do not merge the two runs into one confirmatory dataset.

## Failure handling

Transport/API failures may be retried, but the retry policy must be fixed before
collection and recorded in the runner or manifest notes. A failed request is not
a logical `INVALID` response; it is an execution failure and should not be
silently scored as model output.

## Validation

Before analysis:

`python3 scripts/validate_run_artifacts.py RUN_MANIFEST.json --results RAW_RESULTS.jsonl`

Only validated runs should be passed to `scripts/score_flips.py`.
