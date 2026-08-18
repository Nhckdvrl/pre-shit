"""Score word-level surprisal for one Pythia checkpoint over all stimuli.

Surprisal of a word is the summed NLL (base 2) of its sub-tokens. Alignment is
done through character offsets, so a word that splits into several BPE pieces is
still one measurement unit and regions stay aligned across conditions.

Two context modes are always produced:
  full    -- the whole sentence as context
  local4  -- only the 4 preceding words as context (K7 baseline)
"""
import argparse, json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Must precede the transformers import: the cache root is read at import time.
os.environ.setdefault("HF_HOME", os.path.join(ROOT, "models", "hf_cache"))

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
LOCAL_CTX_WORDS = 4
LN2 = math.log(2.0)


def load_stimuli(path):
    return [json.loads(l) for l in open(path)]


def token_word_map(tok, text, spans):
    """Map each BPE token to the index of the word it starts inside."""
    enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
    ids = enc["input_ids"]
    owner = []
    wi = 0
    for (a, b) in enc["offset_mapping"]:
        while a < b and text[a].isspace():
            a += 1
        while wi < len(spans) and spans[wi][1] <= a:
            wi += 1
        assert wi < len(spans) and spans[wi][0] <= a < spans[wi][1], (text, a, spans[wi])
        owner.append(wi)
    return ids, owner


@torch.no_grad()
def batch_surprisal(model, bos_id, seqs, device, batch_size=32):
    """seqs: list of token-id lists. Returns per-sequence list of per-token
    surprisal in bits, aligned to the input tokens (context [BOS] prepended)."""
    out = []
    for s in range(0, len(seqs), batch_size):
        chunk = seqs[s:s + batch_size]
        maxlen = max(len(c) for c in chunk) + 1
        inp = torch.full((len(chunk), maxlen), bos_id, dtype=torch.long)
        mask = torch.zeros((len(chunk), maxlen), dtype=torch.long)
        for i, c in enumerate(chunk):
            inp[i, 1:1 + len(c)] = torch.tensor(c, dtype=torch.long)
            mask[i, :1 + len(c)] = 1
        inp, mask = inp.to(device), mask.to(device)
        logits = model(input_ids=inp, attention_mask=mask).logits.float()
        logp = torch.log_softmax(logits, dim=-1)
        for i, c in enumerate(chunk):
            n = len(c)
            tgt = inp[i, 1:1 + n]
            lp = logp[i, 0:n].gather(-1, tgt.unsqueeze(-1)).squeeze(-1)
            out.append((-lp / LN2).tolist())
    return out


def run(model_repo, revision, stim, device, batch_size):
    tok = AutoTokenizer.from_pretrained(model_repo, revision=revision)
    model = AutoModelForCausalLM.from_pretrained(
        model_repo, revision=revision, dtype=torch.float32).to(device).eval()
    bos_id = tok.eos_token_id

    rows = []

    # ---------------- full-context pass ----------------
    prepared = []
    for s in stim:
        spans = [tuple(x) for x in s["word_char_spans"]]
        ids, owner = token_word_map(tok, s["text"], spans)
        prepared.append((s, ids, owner))
    sups = batch_surprisal(model, bos_id, [p[1] for p in prepared], device, batch_size)
    for (s, ids, owner), sup in zip(prepared, sups):
        per_word = [0.0] * len(s["words"])
        for o, v in zip(owner, sup):
            per_word[o] += v
        rows.append((s, "full", per_word))

    # ---------------- local-4-word-context pass ----------------
    jobs = []   # (stim_index, target_word_index, token_ids, target_token_slice)
    for si, s in enumerate(stim):
        targets = list(s["crit_idx"]) + list(s["post_idx"])
        for t in targets:
            lo = max(0, t - LOCAL_CTX_WORDS)
            sub = " ".join(s["words"][lo:t + 1])
            # rebuild spans for the truncated string
            spans, pos = [], 0
            for w in s["words"][lo:t + 1]:
                spans.append((pos, pos + len(w)))
                pos += len(w) + 1
            ids, owner = token_word_map(tok, sub, spans)
            jobs.append((si, t, ids, owner, t - lo))
    sups = batch_surprisal(model, bos_id, [j[2] for j in jobs], device, batch_size)
    local = {}
    for (si, t, ids, owner, wpos), sup in zip(jobs, sups):
        v = sum(x for o, x in zip(owner, sup) if o == wpos)
        local.setdefault(si, {})[t] = v
    for si, s in enumerate(stim):
        per_word = [float("nan")] * len(s["words"])
        for t, v in local.get(si, {}).items():
            per_word[t] = v
        rows.append((s, "local4", per_word))

    del model
    torch.cuda.empty_cache()
    return rows


def to_records(rows, seed, step):
    recs = []
    for s, mode, per_word in rows:
        crit = sum(per_word[i] for i in s["crit_idx"])
        rec = dict(seed=seed, step=step, suite=s["suite"], item=s["item"],
                   condition=s["condition"], ambiguity=s["ambiguity"], cue=s["cue"],
                   mode=mode, n_post=s["n_post"], S_crit=crit)
        for k in range(3):
            rec[f"S_post{k+1}"] = (per_word[s["post_idx"][k]]
                                   if k < len(s["post_idx"]) else float("nan"))
        recs.append(rec)
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="0", help="comma list; 0 = original pythia-410m")
    ap.add_argument("--steps", default="143000", help="comma list of training steps")
    ap.add_argument("--size", default="410m")
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "surprisals"))
    args = ap.parse_args()

    stim = load_stimuli(os.path.join(ROOT, "data", "processed", "stimuli.jsonl"))
    os.makedirs(args.out, exist_ok=True)
    import pandas as pd

    for seed in [int(x) for x in args.seeds.split(",")]:
        repo = (f"EleutherAI/pythia-{args.size}" if seed == 0
                else f"EleutherAI/pythia-{args.size}-seed{seed}")
        for step in [int(x) for x in args.steps.split(",")]:
            path = os.path.join(args.out, f"{args.size}_seed{seed}_step{step}.parquet")
            if os.path.exists(path):
                print("skip (exists)", path, flush=True)
                continue
            print(f"[scoring] {repo} @ step{step}", flush=True)
            rows = run(repo, f"step{step}", stim, args.device, args.batch_size)
            pd.DataFrame(to_records(rows, seed, step)).to_parquet(path, index=False)
            print("  ->", path, flush=True)


if __name__ == "__main__":
    main()
