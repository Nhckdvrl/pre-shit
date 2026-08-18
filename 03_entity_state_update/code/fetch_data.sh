#!/usr/bin/env bash
# Key-value inventory from PI-LLM (Wang & Sun, "Unable to Forget", ICML 2025 workshop).
# 46 semantic categories x 400 values. Not redistributed here.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data/raw
curl -sSfL -o data/raw/pi_dict.json \
  "https://raw.githubusercontent.com/zhuangziGiantfish/Unable-to-Forget/main/testing_data/dict_category_double-word_46-400_v1-1.json"
echo "fetched data/raw/pi_dict.json"
