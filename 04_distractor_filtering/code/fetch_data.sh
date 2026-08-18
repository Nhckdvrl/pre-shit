#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data/raw
RAW="https://raw.githubusercontent.com/evandez/relations/main/data/factual"
for f in country_capital_city country_currency country_language country_largest_city; do
  curl -sSfL -o "data/raw/$f.json" "$RAW/$f.json"
done
echo "fetched $(ls data/raw | wc -l) relation files"
