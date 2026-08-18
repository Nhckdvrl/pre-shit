# Pretraining dynamics of Pythia-410M

A series of small, pre-registered training-dynamics studies sharing one asset:
**Pythia-410M x 10 independent pretraining runs x 13 checkpoints**
(`EleutherAI/pythia-410m` plus PolyPythias `-seed1..9`).

Each topic gets its own folder, its own locked protocol, and its own kill gates.
Topics are killed on their own evidence and the negative result is kept, not
deleted — a killed topic with a clean audit trail is a result.

| # | topic | question | status |
|---|---|---|---|
| [01](01_garden_path/) | garden-path reanalysis | does susceptibility to a garden path emerge before recovery from it? | **killed** at Phase 1 |

## Shared infrastructure

```
env/            uv virtualenv (torch 2.11+cu128, transformers 5.15)
models/         HF cache for all checkpoints, shared across topics (~190 GB, not in git)
NN_topic/       one folder per research question
```

Every topic follows the same three-stage protocol:

* **Phase A** — final checkpoint only, 10 seeds. Does the phenomenon exist at all
  in a mature 410M? If not, the topic dies the same day.
* **Phase B** — 5 sparse checkpoints (1k, 4k, 16k, 64k, 143k). Do the two
  behaviours under study actually have different trajectories, and does the most
  dangerous confound explain them away? If it does, the topic dies.
* **Phase C** — the full 12-checkpoint grid, and only then acquisition times,
  phase transitions and any mechanistic work.

Never in the other order.

## What is not in this repository

Model weights, stimuli (fetched by each topic's `fetch_data.sh`), the virtualenv,
and run logs. Code, protocols, per-checkpoint measurements and reports are all here.
