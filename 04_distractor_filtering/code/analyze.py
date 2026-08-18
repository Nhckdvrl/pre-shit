"""Measures and the crossed seed x item bootstrap for distractor filtering."""
import glob, os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHASE_B_STEPS = [1000, 4000, 16000, 64000, 143000]
FULL_STEPS = [128, 512, 1000, 2000, 4000, 8000, 16000, 32000, 64000, 96000, 128000, 143000]


def load(dirpath=None):
    fs = sorted(glob.glob(os.path.join(dirpath or os.path.join(ROOT, "results", "scores"),
                                       "*.parquet")))
    if not fs:
        raise SystemExit("no score files")
    return pd.concat([pd.read_parquet(f) for f in fs], ignore_index=True)


def margins(df):
    """One row per (seed, step, item, condition, position) with M = correct - best wrong."""
    d = df[df.condition != "decoy_probe"]
    p = d.pivot_table(index=["seed", "step", "idx", "item", "relation", "condition", "position"],
                      columns="role", values="logp", aggfunc="max").reset_index()
    p["M"] = p["correct"] - p[["decoy", "other"]].max(axis=1)
    p["acc"] = p["M"] > 0
    return p


def decoy_strength(df):
    """A_decoy: the model's own grasp of the decoy relation, from a clean prompt."""
    d = df[df.condition == "decoy_probe"]
    return d.groupby(["seed", "step"]).logp.mean().rename("A_decoy").reset_index()


def eligible(p, min_seeds=8):
    """Items whose base condition is correct in >= min_seeds seeds, at the final step.
    Selection uses the base condition only and never looks at any distractor."""
    b = p[(p.condition == "base") & (p.step == p.step.max())]
    n = b.groupby("item").acc.sum()
    return set(n[n >= min_seeds].index)


def crossed_bootstrap(vals, seed_idx, n=10000, rng=None, stat=np.mean):
    rng = rng or np.random.default_rng(20260819)
    vals, seed_idx = np.asarray(vals, float), np.asarray(seed_idx)
    by = {}
    for s in np.unique(seed_idx):
        v = vals[(seed_idx == s) & np.isfinite(vals)]
        if len(v):
            by[s] = v
    if not by:
        return np.nan, np.nan, np.nan
    keys = list(by)
    draws = np.empty(n)
    for b in range(n):
        sb = rng.integers(0, len(keys), len(keys))
        draws[b] = np.mean([stat(by[keys[j]][rng.integers(0, len(by[keys[j]]), len(by[keys[j]]))])
                            for j in sb])
    return (np.mean([stat(v) for v in by.values()]),
            np.percentile(draws, 2.5), np.percentile(draws, 97.5))


def dstar(p, elig, position=None, kind="semantic", step=None):
    """D* = M_unrelated - M_<kind>, paired by (seed, item)."""
    q = p[p.item.isin(elig)]
    if step is not None:
        q = q[q.step == step]
    if position:
        q = q[q.position == position]
    u = q[q.condition == "unrelated"].set_index(["seed", "item", "position"]).M
    s = q[q.condition == kind].set_index(["seed", "item", "position"]).M
    j = u.index.intersection(s.index)
    d = (u[j] - s[j])
    return d.values, np.array([i[0] for i in j])
