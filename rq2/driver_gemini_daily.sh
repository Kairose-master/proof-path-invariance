#!/bin/bash
# Free-tier daily loop: relaunch the resumable runner shortly after the quota reset (00:00 PT = 07:00 UTC) each day
# until it prints DONE.  Stop this script (kill by PID) once billing is enabled and a single run finishes.
cd /home/user/proof-path-invariance
while true; do
  until [ "$(date -u +%H%M)" -ge 0705 ] && [ "$(date -u +%H%M)" -le 0720 ]; do sleep 120; done
  python3 rq2/run_gemini.py --model gemini-3.1-flash-lite --budgets none 1024 --max-consecutive-failures 12 \
    --out experiments/rq2/results_d/flash_lite.jsonl >> experiments/rq2/logs/gemini_flash_lite.log 2>&1
  grep -q "^DONE" experiments/rq2/logs/gemini_flash_lite.log && { echo "GEMINI_ALL_DONE $(date -u +%T)" >> experiments/rq2/logs/status.log; exit 0; }
  echo "daily quota exhausted $(date -u +%FT%T)" >> experiments/rq2/logs/status.log
  sleep 1200
done
