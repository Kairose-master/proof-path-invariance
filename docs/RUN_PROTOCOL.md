# Run Protocol — Pythia-70M Logit Margin

The confirmatory v0 run does not generate text. It records two next-token logits for each frozen prompt.

## Frozen model and measurement

- model: `EleutherAI/pythia-70m`
- revision: `step143000`
- interface: Hugging Face Transformers causal LM
- device: CPU
- dtype: float32
- YES candidate: `" YES"`
- NO candidate: `" NO"`
- measurement: `YES_logit - NO_logit`
- repeats: 1

The runner refuses to continue unless both candidate strings are exactly one tokenizer token.

## Prepare prompts

Generate the already-frozen benchmark artifacts:

```bash
python3 scripts/generate_symbolic_cases.py --out /tmp/symbolic_v0.jsonl
python3 scripts/generate_paired_benchmark.py --cases /tmp/symbolic_v0.jsonl --out /tmp/ppi-paired.jsonl
python3 scripts/verify_benchmark_lock.py /tmp/symbolic_v0.jsonl /tmp/ppi-paired.jsonl
```

## Prepare environment

```bash
python3 -m pip install -r requirements-runner.txt   # torch, numpy, transformers, safetensors, huggingface_hub
```

Before the confirmatory run, fill the remaining `FILL-BEFORE-RUN` values in
`experiments/runs/manifest.template.json`, especially access date and runner commit.

Record the exact installed PyTorch and Transformers versions after the runner reports them.

## Execute

```bash
python3 scripts/run_hf_logit_margin.py \
  --prompts /tmp/ppi-paired.jsonl \
  --out results/pythia70m-step143000-symbolic-v0.jsonl \
  --run-id pythia70m-step143000-symbolic-v0
```

The output path is opened in exclusive-create mode. Existing raw results are never overwritten.

## Validate

```bash
python3 scripts/validate_run_artifacts.py \
  experiments/runs/manifest.template.json \
  --results results/pythia70m-step143000-symbolic-v0.jsonl
```

Only a validated run should be scored.

## Score

```bash
python3 scripts/score_flips.py results/pythia70m-step143000-symbolic-v0.jsonl
```

The confirmatory statistic is the sign-flip rate. Continuous logit-margin displacement is secondary.

## What is not measured

This run does not claim that Pythia follows instructions, generates a proof, represents propositions categorically, or has a proof-path semantics. It measures only a frozen next-token preference under a frozen renderer intervention.
