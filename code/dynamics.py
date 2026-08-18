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


def build_arrays(items, suite, mode, strict3=False):
    """Returns seeds, itemlist, C[s,t,i], G[s,t,i,k].

    Note G, not B: PREREG.md defines B = mean_k max(G_k(t), 0) where G_k(t) is the
    *population* interaction at checkpoint t, so the rectification has to happen
    after averaging over items, not per item. Keeping G here is what makes that
    possible.
    """
    sub = items[(items.suite == suite) & (items["mode"] == mode) & (items.step.isin(STEPS))]
    if strict3:
        k = sub.groupby("item")["K"].min()
        sub = sub[sub.item.isin(set(k[k >= 3].index))]
    seeds = sorted(sub.seed.unique())
    itemlist = sorted(sub.item.unique())
    si = {v: k for k, v in enumerate(seeds)}
    ii = {v: k for k, v in enumerate(itemlist)}
    C = np.full((len(seeds), len(STEPS), len(itemlist)), np.nan)
    G = np.full((len(seeds), len(STEPS), len(itemlist), 3), np.nan)
    for r in sub.itertuples():
        a, b = si[r.seed], STEPS.index(r.step)
        C[a, b, ii[r.item]] = r.C
        G[a, b, ii[r.item]] = [r.G1, r.G2, r.G3]
    return np.array(seeds), np.array(itemlist), C, G


def burden(Gsub, variant="rect_pop"):
    """Gsub: [step, item, k] -> per-step burden.

    rect_pop is the pre-registered definition. The others exist so the audit can
    show the conclusion does not hinge on the choice.
    """
    with np.errstate(invalid="ignore"):
        if variant == "rect_item":       # the defective Phase 1 version
            return np.nanmean(np.nanmean(np.clip(Gsub, 0, None), axis=2), axis=1)
        gk = np.nanmean(Gsub, axis=1)
        if variant == "rect_pop":
            return np.nanmean(np.clip(gk, 0, None), axis=1)
        if variant == "signed":
            return np.nanmean(gk, axis=1)
        if variant == "auc":
            return np.nansum(gk, axis=1)
        if variant == "g1":
            return gk[:, 0]
    raise ValueError(variant)


def ci_gate(C_seed, n=2000, rng=None):
    """Per-checkpoint item-level paired bootstrap; True where the 95% CI excludes 0.

    This is clause 1 of the commitment gate. It was specified in PREREG.md and
    described in DEVIATIONS.md D6 as applied on real data, but the Phase 1 report
    path never called it.
    """
    rng = rng or np.random.default_rng(7)
    T = C_seed.shape[0]
    ok = np.zeros(T, bool)
    for t in range(T):
        v = C_seed[t][~np.isnan(C_seed[t])]
        if len(v) == 0:
            continue
        idx = rng.integers(0, len(v), size=(n, len(v)))
        ok[t] = np.percentile(v[idx].mean(axis=1), 2.5) > 0
    return ok


def _first_sustained(flags):
    """Index of the first True starting a *full* SUSTAIN-long run of Trues.

    An earlier version clipped the window at the end of the grid, so the final
    checkpoint needed only one True to count as "sustained over 3". That made
    late acquisition times easier to define than the pre-registration allows.
    """
    n = len(flags)
    for i in range(n - SUSTAIN + 1):
        if all(flags[i:i + SUSTAIN]):
            return i
    return None


def times_from_curves(c, b, ci_ok=None):
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
    if ci_ok is not None:
        ok = ok & ci_ok
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
    j = _first_sustained([np.isfinite(R[i]) and R[i] <= thresh for i in valid])
    if j is None:
        return out
    out["T_recover"] = STEPS[valid[j]]
    out["D"] = np.log2(out["T_recover"] / out["T_commit"])
    return out


def observed(C, G, variant="rect_pop", use_ci_gate=True):
    """Per-seed acquisition times on the real data, with the full gate."""
    rows = []
    for s in range(C.shape[0]):
        c = np.nanmean(C[s], axis=1)
        b = burden(G[s], variant)
        gate = ci_gate(C[s], rng=np.random.default_rng(100 + s)) if use_ci_gate else None
        r = times_from_curves(c, b, gate)
        r["seed_index"] = s
        rows.append(r)
    return pd.DataFrame(rows)


def hierarchical_bootstrap(C, G, n_boot=10000, rng=None, variant="rect_pop"):
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
            b = burden(G[s][:, ib], variant)
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


def crossed_bootstrap_mean(vals, seed_idx, item_idx=None, n=10000, rng=None):
    """Crossed seed x item bootstrap of a mean.

    Pooling seeds x items into one item-level bootstrap treats 10 training runs
    x 24 items as 240 independent observations, which is the pseudo-replication
    the pre-registration explicitly warns against.
    """
    rng = rng or np.random.default_rng(11)
    vals = np.asarray(vals, float)
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
        draws[b] = np.mean([by[keys[j]][rng.integers(0, len(by[keys[j]]), len(by[keys[j]]))].mean()
                            for j in sb])
    return (np.mean([v.mean() for v in by.values()]),
            np.percentile(draws, 2.5), np.percentile(draws, 97.5))
