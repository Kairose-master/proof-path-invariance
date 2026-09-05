# Google Colab execution

This is the easiest path for the first Pythia-70M run. GPU is not required; use a standard CPU runtime.

## 1. Open Colab

Create a new notebook at Google Colab. The repository also includes
`notebooks/pythia70m_colab.ipynb`, which contains the same commands.

## 2. Clone the repository

```bash
!git clone https://github.com/Kairose-master/proof-path-invariance.git
%cd proof-path-invariance
```

## 3. Install runner dependencies

```bash
!python3 -m pip install -q -r requirements-runner.txt
```

Do not manually change the model, revision, device, dtype, YES/NO candidates, or benchmark files for the confirmatory v0 run.

## 4. Rebuild and verify the frozen benchmark

```bash
!python3 scripts/generate_symbolic_cases.py --out /tmp/symbolic_v0.jsonl
!python3 scripts/generate_paired_benchmark.py --cases /tmp/symbolic_v0.jsonl --out /tmp/ppi-paired.jsonl
!python3 scripts/verify_benchmark_lock.py /tmp/symbolic_v0.jsonl /tmp/ppi-paired.jsonl
```

Expected final line:

```text
benchmark lock verified
```

## 5. Create the environment-specific manifest

```bash
!mkdir -p results
!python3 scripts/create_run_manifest.py \
  --out results/pythia70m-step143000-symbolic-v0.manifest.json
```

This records the Hugging Face resolved model commit, access time, exact PyTorch
and Transformers versions, and the commit that last changed the runner.

Validate it before running:

```bash
!python3 scripts/validate_run_artifacts.py \
  results/pythia70m-step143000-symbolic-v0.manifest.json
```

## 6. Execute all 512 prompts

```bash
!python3 scripts/run_hf_logit_margin.py \
  --prompts /tmp/ppi-paired.jsonl \
  --out results/pythia70m-step143000-symbolic-v0.jsonl \
  --run-id pythia70m-step143000-symbolic-v0
```

On the first run, Hugging Face downloads the Pythia weights and tokenizer. The
runner then checks that `" YES"` and `" NO"` are each exactly one token. If
that check fails, the run stops instead of changing the measurement rule.

Do not rerun this cell against the same output path: raw results are deliberately
opened in exclusive-create mode. Delete the exploratory file only if no
confirmatory analysis has been performed; otherwise create a new run ID.

## 7. Validate the raw results

```bash
!python3 scripts/validate_run_artifacts.py \
  results/pythia70m-step143000-symbolic-v0.manifest.json \
  --results results/pythia70m-step143000-symbolic-v0.jsonl
```

A successful validation should report 512 rows across 256 pairs.

## 8. Score

```bash
!python3 scripts/score_flips.py \
  results/pythia70m-step143000-symbolic-v0.jsonl
```

The primary number is `flip_rate`. The margin displacement fields are secondary.

## 9. Save the artifacts

Colab storage is temporary. Download or commit the following before closing the runtime:

- the run-specific manifest;
- the raw result JSONL;
- the scorer output if desired.

Do not replace or hand-edit raw result rows after collection.
