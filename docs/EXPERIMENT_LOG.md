# Experiment Log

## 2026-09-05 — Phase 1 Pythia-70M premise reversal

**Status:** completed; scorer output recorded. Raw manifest/result JSONL are not
yet committed to the repository.

Frozen setup:

- model: `EleutherAI/pythia-70m`
- revision: `step143000`
- benchmark: `symbolic_v0`
- cases: 256 paired items
- transform: `premise_reverse`
- observable: `logit(" YES") - logit(" NO")`

Primary result:

```text
valid_binary_pairs = 256
ties               = 0
flips              = 0
flip_rate           = 0.0
```

Extended diagnosis:

```text
base predictions:             YES 256
premise-reverse predictions:  YES 256
base accuracy:                0.5
reverse accuracy:             0.5
base AUROC:                   0.478057861328125
reverse AUROC:                0.228179931640625
mean margin shift:            0.02717304229736328
mean absolute margin shift:   0.07551097869873047
```

Gold/family-conditioned mean shifts:

```text
positive family: -0.025316238403320312
negative family:  0.07966232299804688
```

Interpretation:

- **OBSERVED:** premise reversal changed continuous logit margins but never
  crossed the YES/NO sign boundary.
- **OBSERVED:** every prompt was classified YES, so zero flips are response-bias
  stability rather than evidence of correct logical invariance.
- **OBSERVED:** base AUROC is approximately chance and reversed AUROC is below
  chance.
- **LIMIT:** gold label is confounded with formal family in `symbolic_v0`, so
  gold-conditioned differences cannot be identified as logical-truth effects.

Machine-readable records:

- `experiments/results/phase1_pythia70m_summary.json`
- `experiments/results/phase1_pythia70m_extended_score.json`
- `docs/RESULTS_PHASE1.md`

Next experiment:

- Phase 2 benchmark: `s3_v0`
- four formal families: two positive, two negative
- 128 formal cases
- all six `S3` premise permutations
- 768 model prompts
- separate notebook: `notebooks/phase2_s3_colab.ipynb`
