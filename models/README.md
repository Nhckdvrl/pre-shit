# Model weights

Deliberately absent from git. All Pythia-410M and PolyPythia checkpoints are
downloaded here at run time by `code/score.py`, which sets

    HF_HOME = <repo>/models/hf_cache

**before** importing `transformers` — the cache root is read at import time, so
the order matters. The full grid is 10 seeds x 13 checkpoints x ~1.6 GB ≈ 190 GB,
which is why `models/hf_cache/` is git-ignored.

Repos used:
* `EleutherAI/pythia-410m` — seed 0
* `EleutherAI/pythia-410m-seed1` … `-seed9` — PolyPythias, 9 further training runs

Each checkpoint is a git branch on the model repo, e.g. `revision="step8000"`.
Downloads authenticate via `models/hf_cache/token` (not committed); without it
the Hub throttles and the grid takes noticeably longer.
