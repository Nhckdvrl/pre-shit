"""Acquisition times and the hierarchical bootstrap over them (K2-K5).

Everything works off two arrays per (suite, mode):
    Carr[seed, step, item]   commitment interaction at the disambiguator
    Barr[seed, step, item]   residual burden over the recovery window
so that a bootstrap draw is just an index into the item axis.
"""
import os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import (ROOT, STEPS, LATE_STEPS, SUSTAIN, RECOVERY_IMPROVEMENT_MIN,
                     RECOVERY_REACH_FRAC)

LATE_IDX = [STEPS.index(s) for s in LATE_STEPS]


def build_arrays(items, suite, mode):
    sub = items[(items.suite == suite) & (items["mode"] == mode) & (items.step.isin(STEPS))]
    seeds = sorted(sub.seed.unique())
    itemlist = sorted(sub.item.unique())
    ii = {v: k for k, v in enumerate(itemlist)}
    C = np.full((len(seeds), len(STEPS), len(itemlist)), np.nan)
    B = np.full_like(C, np.nan)
    for r in sub.itertuples():
        C[seeds.index(r.seed), STEPS.index(r.step), ii[r.item]] = r.C
        B[seeds.index(r.seed), STEPS.index(r.step), ii[r.item]] = r.B
    return np.array(seeds), np.array(itemlist), C, B


def _first_sustained(flags):
    """Index of the first True with SUSTAIN consecutive Trues (clipped at the end)."""
    n = len(flags)
    for i in range(n):
        if all(flags[j] for j in range(i, min(i + SUSTAIN, n))):
            return i
    return None


def times_from_curves(c, b):
    """c, b: length-len(STEPS) curves for one training run.
    Returns dict with T_commit, T_recover, R_early, R_late, improvement, D."""
    out = dict(T_commit=np.nan, T_recover=np.nan, R_early=np.nan,
               R_late=np.nan, improvement=np.nan, D=np.nan)
    late = c[LATE_IDX]
    if not np.all(np.isfinite(late)):
        return out
    C_late = np.median(late)
    if C_late <= 0:
        return out
    ok = (c > 0) & (c >= 0.5 * C_late) & np.isfinite(c)
    i0 = _first_sustained(ok)
    if i0 is None:
        return out
    out["T_commit"] = STEPS[i0]

    R = np.full(len(STEPS), np.nan)
    m = np.arange(len(STEPS)) >= i0
    good = m & (c > 0) & np.isfinite(b)
    R[good] = b[good] / c[good]
    valid = np.where(np.isfinite(R))[0]
    if len(valid) < SUSTAIN:
        return out
    R_early = np.median(R[valid[:SUSTAIN]])
    late_r = [R[i] for i in LATE_IDX if np.isfinite(R[i])]
    if not late_r or R_early <= 0:
        return out
    R_late = np.median(late_r)
    imp = (R_early - R_late) / R_early
    out.update(R_early=R_early, R_late=R_late, improvement=imp)
    if imp < RECOVERY_IMPROVEMENT_MIN:
        return out
    thresh = R_late + (1 - RECOVERY_REACH_FRAC) * (R_early - R_late)
    reached = [np.isfinite(R[i]) and R[i] <= thresh for i in valid]
    j = _first_sustained(reached)
    if j is None:
        return out
    out["T_recover"] = STEPS[valid[j]]
    out["D"] = np.log2(out["T_recover"] / out["T_commit"])
    return out


def observed(C, B):
    """Per-seed acquisition times on the real data."""
    rows = []
    for s in range(C.shape[0]):
        c = np.nanmean(C[s], axis=1)
        with np.errstate(invalid="ignore"):
            b = np.nanmean(B[s], axis=1)
        r = times_from_curves(c, b)
        r["seed_index"] = s
        rows.append(r)
    return pd.DataFrame(rows)


def hierarchical_bootstrap(C, B, n_boot=10000, rng=None):
    """Resample seeds, then items within each resampled seed; recompute everything.

    Inside the bootstrap the commitment gate uses the point criterion C>0 rather
    than a nested CI (see DEVIATIONS.md D6) -- the outer resampling already
    carries the uncertainty that the nested interval would express.
    """
    rng = rng or np.random.default_rng(20260819)
    S, T, I = C.shape
    med_D, med_imp, frac_later, med_tc, med_tr = [], [], [], [], []
    for _ in range(n_boot):
        sb = rng.integers(0, S, S)
        Ds, imps, later, tcs, trs = [], [], [], [], []
        for s in sb:
            ib = rng.integers(0, I, I)
            c = np.nanmean(C[s][:, ib], axis=1)
            with np.errstate(invalid="ignore"):
                b = np.nanmean(B[s][:, ib], axis=1)
            r = times_from_curves(c, b)
            Ds.append(r["D"]); imps.append(r["improvement"])
            tcs.append(r["T_commit"]); trs.append(r["T_recover"])
            later.append(1.0 if (np.isfinite(r["T_recover"]) and np.isfinite(r["T_commit"])
                                 and r["T_recover"] > r["T_commit"]) else 0.0)
        with np.errstate(invalid="ignore"):
            med_D.append(np.nanmedian(Ds) if np.any(np.isfinite(Ds)) else np.nan)
            med_imp.append(np.nanmedian(imps) if np.any(np.isfinite(imps)) else np.nan)
            med_tc.append(np.nanmedian(tcs) if np.any(np.isfinite(tcs)) else np.nan)
            med_tr.append(np.nanmedian(trs) if np.any(np.isfinite(trs)) else np.nan)
        frac_later.append(np.mean(later))
    def ci(x):
        x = np.asarray(x, float)
        f = x[np.isfinite(x)]
        if len(f) == 0:
            return (np.nan, np.nan, np.nan, 0.0)
        return (np.median(f), np.percentile(f, 2.5), np.percentile(f, 97.5),
                len(f) / len(x))
    return dict(D=ci(med_D), improvement=ci(med_imp), frac_later=ci(frac_later),
                T_commit=ci(med_tc), T_recover=ci(med_tr))
