#!/usr/bin/env bash
# Fetch the third-party stimuli. Nothing here is redistributed in this repo;
# each set is pulled from its original source.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data/raw data/processed

# SyntaxGym test suites (Hu et al. 2020), cpllab/syntactic-generalization
SG=https://raw.githubusercontent.com/cpllab/syntactic-generalization/master/test_suites/json
for f in npz_ambig mvrr; do
  curl -sSfL -o "data/raw/$f.json" "$SG/$f.json"
  echo "fetched data/raw/$f.json"
done

# Classic garden-path stimuli as released in microsoft/turing-experiments
MS=https://raw.githubusercontent.com/microsoft/turing-experiments/main/data/external/garden_path
for f in Christianson_2001 Alternates_2022; do
  curl -sSfL -o "data/raw/$f.tsv" "$MS/$f.tsv"
  echo "fetched data/raw/$f.tsv"
done

echo
echo "Now build the region-aligned stimulus file:"
echo "  ./env/bin/python code/build_stimuli.py"
