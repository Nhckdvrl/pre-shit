#!/usr/bin/env bash
# Phase 1: the 12-checkpoint analysis grid (+ step0 sanity) on all 10 seeds,
# sharded across the four local GPUs.
set -u
cd "$(dirname "$0")/.."
STEPS="0,128,512,1000,2000,4000,8000,16000,32000,64000,96000,128000,143000"
SHARDS=("0,1,2" "3,4,5" "6,7" "8,9")
for i in "${!SHARDS[@]}"; do
  nohup ./env/bin/python code/score.py \
      --seeds "${SHARDS[$i]}" --steps "$STEPS" --device "cuda:$i" \
      > "logs/phase1_gpu$i.log" 2>&1 &
  echo "gpu$i <- seeds ${SHARDS[$i]} (pid $!)"
done
wait
