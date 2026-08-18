"""Pre-registered analysis for the garden-path acquisition-dynamics study.

Metrics (all region-aligned, all in bits):

  commitment      C(t) = [(A,cue-absent) - (A,cue-present)]
                       - [(U,cue-absent) - (U,cue-present)]   at the disambiguator
  residual burden B(t) = mean_k max(G_k(t), 0) over the recovery window,
                         G_k = the same 2x2 interaction at post-disambiguator word k
  recovery ratio  R(t) = B(t) / C(t)

For the two-condition external sets the interaction collapses to the simple
garden-path contrast (GP - comma control).

Nothing here is allowed to depend on the outcome: the checkpoint grid, the
recovery window, the gates and their thresholds are fixed in PREREG.md.
"""
import argparse, glob, json, os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEPS = [128, 512, 1000, 2000, 4000, 8000, 16000, 32000, 64000, 96000, 128000, 143000]
LATE_STEPS = [96000, 128000, 143000]
SG_SUITES = ["npz_ambig", "mvrr"]
EXT_SUITES = ["Christianson_2001", "Alternates_2022"]
N_BOOT = 10000
RECOVERY_IMPROVEMENT_MIN = 0.30
RECOVERY_REACH_FRAC = 0.75
SUSTAIN = 3
RNG = np.random.default_rng(20260819)


# ---------------------------------------------------------------- item tables
def load_surprisals(dirpath):
    files = sorted(glob.glob(os.path.join(dirpath, "*.parquet")))
    if not files:
        raise SystemExit("no surprisal files in " + dirpath)
    return pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)


def item_effects(df):
    """Collapse a long surprisal table to one row per
    (seed, step, suite, mode, item) with C and G1..G3."""
    out = []
    posc = ["S_post1", "S_post2", "S_post3"]
    for (seed, step, suite, mode), g in df.groupby(["seed", "step", "suite", "mode"]):
        if suite in SG_SUITES:
            piv = g.pivot_table(index="item", columns=["ambiguity", "cue"],
                                values=["S_crit"] + posc)
            npost = g.groupby("item")["n_post"].min()
            for it in piv.index:
                r = piv.loc[it]
                def inter(col):
                    try:
                        return ((r[(col, "ambig", "absent")] - r[(col, "ambig", "present")])
                                - (r[(col, "unambig", "absent")] - r[(col, "unambig", "present")]))
                    except KeyError:
                        return np.nan
                rec = dict(seed=seed, step=step, suite=suite, mode=mode, item=it,
                           C=inter("S_crit"), K=int(min(3, npost.loc[it])))
                for k in range(3):
                    rec[f"G{k+1}"] = inter(posc[k]) if k < rec["K"] else np.nan
                out.append(rec)
        else:
            g = g.copy()
            g["base"] = g["condition"].str.lstrip("D")
            piv = g.pivot_table(index=["base", "item"], columns="cue",
                                values=["S_crit"] + posc)
            npost = g.groupby(["base", "item"])["n_post"].min()
            for key in piv.index:
                r = piv.loc[key]
                def diff(col):
                    try:
                        return r[(col, "absent")] - r[(col, "present")]
                    except KeyError:
                        return np.nan
                rec = dict(seed=seed, step=step, suite=suite, mode=mode,
                           item=f"{key[0]}-{key[1]}", C=diff("S_crit"),
                           K=int(min(3, npost.loc[key])))
                for k in range(3):
                    rec[f"G{k+1}"] = diff(posc[k]) if k < rec["K"] else np.nan
                out.append(rec)
    t = pd.DataFrame(out)
    gg = t[["G1", "G2", "G3"]].clip(lower=0)
    t["B"] = gg.mean(axis=1, skipna=True)
    return t


# ------------------------------------------------------------------ bootstrap
def paired_bootstrap_mean(x, n=N_BOOT, rng=RNG):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    idx = rng.integers(0, len(x), size=(n, len(x)))
    b = x[idx].mean(axis=1)
    return x.mean(), np.percentile(b, 2.5), np.percentile(b, 97.5)


# ------------------------------------------------ curve -> acquisition times
def curves_from_items(sub, steps):
    """sub: item-level rows for one (seed, suite, mode). Returns dict step->(C,B,R)."""
    C, B = {}, {}
    for st in steps:
        s = sub[sub.step == st]
        if len(s) == 0:
            continue
        C[st] = np.nanmean(s["C"].values)
        b = s["B"].values
        B[st] = np.nanmean(b) if np.any(~np.isnan(b)) else np.nan
    return C, B


def commitment_time(C, ci_ok, steps):
    """Earliest step with C>0, CI excluding 0, C >= 0.5*C_late, sustained."""
    avail = [s for s in steps if s in C]
    if not avail:
        return None, np.nan
    C_late = np.median([C[s] for s in LATE_STEPS if s in C])
    ok = {s: (C[s] > 0 and ci_ok.get(s, False) and C[s] >= 0.5 * C_late) for s in avail}
    for i, s in enumerate(avail):
        if all(ok[avail[j]] for j in range(i, min(i + SUSTAIN, len(avail)))):
            return s, C_late
    return None, C_late


def recovery_time(R, steps, t_commit):
    """R must already be restricted to commitment-passing checkpoints."""
    valid = [s for s in steps if s in R and s >= t_commit and np.isfinite(R[s])]
    if len(valid) < SUSTAIN:
        return None, np.nan, np.nan, np.nan
    R_early = np.median([R[s] for s in valid[:SUSTAIN]])
    late = [R[s] for s in LATE_STEPS if s in R and np.isfinite(R[s])]
    if not late:
        return None, R_early, np.nan, np.nan
    R_late = np.median(late)
    improvement = (R_early - R_late) / R_early if R_early > 0 else np.nan
    if not np.isfinite(improvement) or improvement < RECOVERY_IMPROVEMENT_MIN:
        return None, R_early, R_late, improvement
    thresh = R_late + (1 - RECOVERY_REACH_FRAC) * (R_early - R_late)
    for i, s in enumerate(valid):
        if all(R[valid[j]] <= thresh for j in range(i, min(i + SUSTAIN, len(valid)))):
            return s, R_early, R_late, improvement
    return None, R_early, R_late, improvement


def seed_trajectory(items, seed, suite, mode, steps=STEPS, rng=RNG, do_ci=True):
    sub = items[(items.seed == seed) & (items.suite == suite) & (items["mode"] == mode)]
    C, B = curves_from_items(sub, steps)
    ci_ok = {}
    for st in C:
        if do_ci:
            _, lo, _ = paired_bootstrap_mean(sub[sub.step == st]["C"].values, 2000, rng)
            ci_ok[st] = lo > 0
        else:
            ci_ok[st] = C[st] > 0
    t_commit, C_late = commitment_time(C, ci_ok, steps)
    R = {}
    if t_commit is not None:
        for st in C:
            if st >= t_commit and C[st] > 0:
                R[st] = B[st] / C[st]
    t_rec, R_early, R_late, improvement = (
        recovery_time(R, steps, t_commit) if t_commit is not None else (None, np.nan, np.nan, np.nan))
    D = np.log2(t_rec / t_commit) if (t_rec and t_commit) else np.nan
    return dict(seed=seed, suite=suite, mode=mode, C=C, B=B, R=R, C_late=C_late,
                T_commit=t_commit, T_recover=t_rec, R_early=R_early, R_late=R_late,
                improvement=improvement, D=D)


# ---------------------------------------------------------------------- gates
def gate_K0_K1(items, mode="full", suites=SG_SUITES, step=143000):
    print(f"\n=== K0 / K1  (mode={mode}, step={step}) ===")
    res = {}
    for suite in suites:
        sub = items[(items.suite == suite) & (items["mode"] == mode) & (items.step == step)]
        per_seed = []
        for seed, g in sub.groupby("seed"):
            m, lo, hi = paired_bootstrap_mean(g["C"].values)
            frac = float(np.mean(g["C"].values > 0))
            per_seed.append(dict(seed=seed, C=m, lo=lo, hi=hi, frac_pos=frac,
                                 pass_=bool(lo > 0 and frac >= 0.65)))
        t = pd.DataFrame(per_seed).sort_values("seed")
        res[suite] = t
        print(f"\n-- {suite}")
        print(t.to_string(index=False,
              formatters={"C": "{:.3f}".format, "lo": "{:.3f}".format,
                          "hi": "{:.3f}".format, "frac_pos": "{:.2f}".format}))
        n_ok = int(t["pass_"].sum())
        print(f"   seeds passing (C>0, CI excl. 0, >=65% items positive): {n_ok}/{len(t)}")
    k0 = all(bool(t[t.seed == 0]["pass_"].iloc[0]) for t in res.values()) \
        if all((t.seed == 0).any() for t in res.values()) else None
    k1 = all(int(t["pass_"].sum()) >= 8 for t in res.values())
    print(f"\nK0 (original pythia-410m passes on both suites): {k0}")
    print(f"K1 (>=8/10 seeds pass on both suites):          {k1}")
    return res, k0, k1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="0")
    ap.add_argument("--dir", default=os.path.join(ROOT, "results", "surprisals"))
    ap.add_argument("--mode", default="full")
    args = ap.parse_args()

    df = load_surprisals(args.dir)
    items = item_effects(df)
    items.to_parquet(os.path.join(ROOT, "results", "item_effects.parquet"), index=False)
    print("loaded", df.shape, "-> item effects", items.shape)
    print("steps present:", sorted(items.step.unique()))
    print("seeds present:", sorted(items.seed.unique()))

    if args.phase == "0":
        gate_K0_K1(items, mode=args.mode)
        gate_K0_K1(items, mode=args.mode, suites=EXT_SUITES)


if __name__ == "__main__":
    main()
