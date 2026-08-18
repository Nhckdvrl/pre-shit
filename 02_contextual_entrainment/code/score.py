"""Score gold and distractor log-probabilities for one Pythia checkpoint.

For every item x condition we need log P(candidate | context + query). The
candidate is appended to the prompt and its sub-token log-probs are summed, so a
multi-token object is one measurement unit. Entrainment is later taken as a
difference against the no-context condition, in which the token count cancels.
"""
import argparse, json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)
os.environ.setdefault("HF_HOME", os.path.join(REPO, "models", "hf_cache"))

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

LN2 = math.log(2.0)
CONDITIONS = ["none", "related", "irrelevant", "random", "counterfactual"]


@torch.no_grad()
def score_batch(model, tok, pairs, device, batch_size=64):
    """pairs: list of (prompt, candidate). Returns summed log2 P(candidate|prompt)."""
    out = []
    bos = tok.eos_token_id
    for s in range(0, len(pairs), batch_size):
        chunk = pairs[s:s + batch_size]
        seqs, nc = [], []
        for prompt, cand in chunk:
            p = tok(prompt, add_special_tokens=False)["input_ids"]
            c = tok(" " + cand, add_special_tokens=False)["input_ids"]
            seqs.append([bos] + p + c)
            nc.append(len(c))
        maxlen = max(len(x) for x in seqs)
        inp = torch.full((len(seqs), maxlen), bos, dtype=torch.long)
        mask = torch.zeros((len(seqs), maxlen), dtype=torch.long)
        for i, x in enumerate(seqs):
            inp[i, :len(x)] = torch.tensor(x)
            mask[i, :len(x)] = 1
        inp, mask = inp.to(device), mask.to(device)
        logits = model(input_ids=inp, attention_mask=mask).logits.float()
        logp = torch.log_softmax(logits, dim=-1)
        for i, x in enumerate(seqs):
            n, k = len(x), nc[i]
            tgt = inp[i, n - k:n]
            lp = logp[i, n - k - 1:n - 1].gather(-1, tgt.unsqueeze(-1)).squeeze(-1)
            out.append((lp.sum() / LN2).item())
    return out


def run(repo, revision, stim, device, batch_size):
    tok = AutoTokenizer.from_pretrained(repo, revision=revision)
    model = AutoModelForCausalLM.from_pretrained(
        repo, revision=revision, dtype=torch.float32).to(device).eval()

    jobs, keys = [], []
    for it in stim:
        for cond in CONDITIONS:
            ctx = it["contexts"][cond]
            prompt = (ctx + " " + it["query"]).strip() if ctx else it["query"]
            cands = {"gold": it["gold"]}
            if cond in it["distractors"]:
                cands["distractor"] = it["distractors"][cond]
            else:                      # `none` still needs the counterfactual
                cands["distractor"] = it["distractors"]["counterfactual"]
            # the unseen-random control, scored in every condition: without it a
            # rise in D_d could just mean random nouns became likelier overall
            cands["control"] = it["control"]
            for role, cand in cands.items():
                jobs.append((prompt, cand))
                keys.append((it["item"], it["relation"], cond, role))
    vals = score_batch(model, tok, jobs, device, batch_size)
    del model
    torch.cuda.empty_cache()
    return keys, vals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="0")
    ap.add_argument("--steps", default="143000")
    ap.add_argument("--size", default="410m")
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "scores"))
    args = ap.parse_args()

    stim = [json.loads(l) for l in
            open(os.path.join(ROOT, "data", "processed", "stimuli.jsonl"))]
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
            keys, vals = run(repo, f"step{step}", stim, args.device, args.batch_size)
            df = pd.DataFrame(keys, columns=["item", "relation", "condition", "role"])
            df["logp"] = vals
            df["seed"], df["step"] = seed, step
            tmp = path + f".tmp{os.getpid()}"
            df.to_parquet(tmp, index=False)
            os.replace(tmp, path)
            print("  ->", path, flush=True)


if __name__ == "__main__":
    main()
