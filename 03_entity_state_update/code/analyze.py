"""Trial-level measures for the entity state-update study."""
import glob, os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHASE_B_STEPS = [1000, 4000, 16000, 64000, 143000]
FULL_STEPS = [128, 512, 1000, 2000, 4000, 8000, 16000, 32000, 64000, 96000, 128000, 143000]
CONDS = ["update_1", "update_2", "update_3", "control_2", "control_3"]


def load(dirpath=None):
    files = sorted(glob.glob(os.path.join(dirpath or os.path.join(ROOT, "results", "scores"),
                                          "*.parquet")))
    if not files:
        raise SystemExit("no score files")
    return pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)


def trial_measures(df):
    """One row per (seed, step, trial, condition)."""
    df = df.copy()
    top = df.loc[df.groupby(["seed", "step", "idx"]).logp.idxmax()]
    top = top.set_index(["seed", "step", "idx"])[["role"]].rename(columns={"role": "top_role"})
    piv = df.pivot_table(index=["seed", "step", "idx", "trial", "category",
                                "condition", "n_states"],
                         columns="role", values="logp", aggfunc="max").reset_index()
    piv = piv.merge(top, left_on=["seed", "step", "idx"], right_index=True, how="left")
    piv["correct"] = piv.top_role == "current"
    piv["M_interf"] = piv["current"] - piv.get("interferer")
    piv["M_unment"] = piv["current"] - piv.get("unmentioned")
    return piv


def crossed_bootstrap(vals, seed_idx, n=10000, rng=None, stat=np.mean):
    """Resample seeds, then trials within each resampled seed."""
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
