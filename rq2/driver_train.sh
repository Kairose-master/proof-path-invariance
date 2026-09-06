#!/bin/bash
# Secondary constructed models; waits for the primary iter_r4 training to finish.
cd /home/user/proof-path-invariance
S=experiments/rq2/logs/status.log
until [ -f experiments/rq2/iter_r4.pt ]; do sleep 30; done
echo "TRAIN_DONE iter_r4 $(date -u +%T)" >> $S
python3 rq2/train_rq2.py --kind iter --rounds 2 --threads 1 --out experiments/rq2/iter_r2.pt > experiments/rq2/logs/train_iter_r2.log 2>&1 \
  && echo "TRAIN_DONE iter_r2 $(date -u +%T)" >> $S || echo "TRAIN_FAIL iter_r2" >> $S
python3 rq2/train_rq2.py --kind set --threads 1 --out experiments/rq2/set7.pt > experiments/rq2/logs/train_set7.log 2>&1 \
  && echo "TRAIN_DONE set7 $(date -u +%T)" >> $S || echo "TRAIN_FAIL set7" >> $S
echo "TRAIN_ALL_DONE $(date -u +%T)" >> $S
