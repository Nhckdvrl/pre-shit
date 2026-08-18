#!/usr/bin/env bash
# LRE factual relations (Hernandez et al., "Linearity of Relation Decoding").
# Not redistributed here.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data/raw
API="https://api.github.com/repos/evandez/relations/git/trees/main?recursive=1"
RAW="https://raw.githubusercontent.com/evandez/relations/main"
curl -sSfL "$API" | python3 -c "
import json,sys
for e in json.load(sys.stdin)['tree']:
    p=e['path']
    if p.startswith('data/factual') and p.endswith('.json'): print(p)
" | while read -r f; do
  curl -sSfL -o "data/raw/$(basename "$f")" "$RAW/$f"
done
echo "fetched $(ls data/raw | wc -l) factual relation files"
