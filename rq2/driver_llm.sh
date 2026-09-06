#!/bin/bash
# RQ2 LLM runs; waits for Audit 2 (recognition-audit) to release the CPU.
cd /home/user/proof-path-invariance
export TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=3 MKL_NUM_THREADS=3
S=experiments/rq2/logs/status.log
until grep -q AUDIT2_DONE /home/user/recognition-audit/runs/driver.log 2>/dev/null; do sleep 30; done
echo "llm driver start $(date -u +%T)" >> $S
run(){ tag=$1; model=$2; rev=$3
  python3 scripts/run_hf_hankel.py --prompts rq2/table/rq2_prompts.jsonl --out experiments/rq2/results/$tag.jsonl \
    --run-id $tag --model-id $model --revision $rev --expected-rows 4000 > experiments/rq2/logs/$tag.log 2>&1 \
    && echo "LLM_DONE $tag $(date -u +%T)" >> $S || echo "LLM_FAIL $tag $(date -u +%T)" >> $S; }
run pythia70m EleutherAI/pythia-70m step143000
run qwen05b Qwen/Qwen2.5-0.5B-Instruct main
run qwen15b Qwen/Qwen2.5-1.5B-Instruct main
echo "LLM_ALL_DONE $(date -u +%T)" >> $S
