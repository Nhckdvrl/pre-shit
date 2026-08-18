"""Entrainment measures and the crossed seed x item bootstrap."""
import glob, os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHASE_B_STEPS = [1000, 4000, 16000, 64000, 143000]
FULL_STEPS = [128, 512, 1000, 2000, 4000, 8000, 16000, 32000, 64000, 96000, 128000, 143000]


def load(dirpath=None):
    files = sorted(glob.glob(os.path.join(dirpath or os.path.join(ROOT, "results", "scores"),
                                          "*.parquet")))
    if not files:
        raise SystemExit("no score files")
    return pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)


def measures(df):
    """One row per (seed, step, item) with every derived quantity."""
    out = []
    for (seed, step), g in df.groupby(["seed", "step"]):
        p = g.pivot_table(index=["item", "relation"], columns=["condition", "role"],
                          values="logp")
        idx = p.index
        get = lambda c, r: p[(c, r)].values
        none_g, none_d, none_c = get("none", "gold"), get("none", "distractor"), get("none", "control")
        rec = dict(
            seed=seed, step=step,
            item=[i[0] for i in idx], relation=[i[1] for i in idx],
            # mechanical copying: the context token, minus an unseen random word
            E_copy=(get("random", "distractor") - none_d) - (get("random", "control") - none_c),
            D_rand_seen=get("random", "distractor") - none_d,
            D_rand_unseen=get("random", "control") - none_c,
            # semantic conditions
            D_cf_d=get("counterfactual", "distractor") - none_d,
            D_cf_g=get("counterfactual", "gold") - none_g,
            D_irr_d=get("counterfactual", "distractor") * 0
                    + (get("irrelevant", "distractor") - none_d),
            # parametric knowledge margin (the confound)
            K=none_g - none_d,
            # margin after the false context: >0 means the model resisted
            margin_cf=get("counterfactual", "gold") - get("counterfactual", "distractor"),
        )
        rec["F_prereg"] = rec["D_cf_g"] - rec["D_cf_d"]
        out.append(pd.DataFrame(rec))
    return pd.concat(out, ignore_index=True)


def crossed_bootstrap(vals, seed_idx, n=10000, rng=None, stat=np.mean):
    """Resample seeds, then items within each resampled seed."""
    rng = rng or np.random.default_rng(20260819)
    vals = np.asarray(vals, float)
    seed_idx = np.asarray(seed_idx)
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
