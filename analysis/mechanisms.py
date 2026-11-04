"""Mechanism analyses of existing runs: the dips in two no-trigger controls (A3, registration REG-2). Never writes into
runs/. Every threshold is an argument; the registered values are in REG2, fixed before any run was analyzed with this code.
"""
import numpy as np
import pandas as pd

from analysis.load import _level


# ---------------------------------------------------------------- A3: dips in no-trigger controls

def bin_series(run: dict, bin_s: float, lead_s: float) -> pd.DataFrame:
    """One row per bin [a, a + bin_s) from warm-up to the end of arrivals: planned arrival rate in the bin, and over
    the `lead_s` before it **plus the bin itself** ([a - lead_s, a + bin_s)), since percent fast is counted by arrival and
    a dip lands in the excess bin (REG-2 review, trace A); the `_level` values; KV max; preemptions; mean planned prompt
    tokens; unfinished requests; mean busy SM clock."""
    wl, r, m = run["cfg"]["workload"], run["requests"], run["metrics"]
    order = np.argsort(r.t_planned.to_numpy())
    tp = r.t_planned.to_numpy()[order]
    plen = (r.prompt_tokens_planned.to_numpy()[order] if "prompt_tokens_planned" in r else np.full(len(tp), np.nan))
    unfinished = (r.status.to_numpy()[order] == "unfinished")
    idx = lambda a, b: (np.searchsorted(tp, a, "left"), np.searchsorted(tp, b, "left"))
    pre = m["vllm:num_preemptions_total"]
    g = run.get("gpu")
    rows = []
    for a in np.arange(wl["warmup_s"], wl["duration_s"] - bin_s + 1e-9, bin_s):
        b = a + bin_s
        i, j = idx(a, b)
        li, _ = idx(max(0.0, a - lead_s), b)
        w = (m.t >= a) & (m.t < b)
        row = {"a": float(a), "arrivals": (j - i) / bin_s, "lead_arrivals": (j - li) / (b - max(0.0, a - lead_s)),
               **_level(run, a, b), "kv_max": float(m["vllm:kv_cache_usage_perc"][w].max()),
               "preemptions": float(np.interp(b, m.t, pre) - np.interp(a, m.t, pre)),
               "prompt_mean": float(np.mean(plen[i:j])) if j > i and not np.isnan(plen[i:j]).all() else np.nan, "unfinished": int(unfinished[i:j].sum())}
        if g is not None and len(g) and "sm_clock_mhz" in g:
            gw = g[(g.t >= a) & (g.t < b) & (g.util_pct >= 50)]
            row["sm_clock"] = float(gw.sm_clock_mhz.mean()) if len(gw) else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def episodes(bins: pd.DataFrame, pf_limit: float, merge_gap_bins: int) -> list[tuple[int, int]]:
    """Runs of bins with percent fast below `pf_limit`, as (first, last) positions. Runs separated by at most
    `merge_gap_bins` healthy bins are one episode, so one slump flickering across the limit is not several (review, B)."""
    low = np.flatnonzero((bins.pf < pf_limit).to_numpy())
    out = []
    for i in low:
        if out and i - out[-1][1] - 1 <= merge_gap_bins:
            out[-1] = (out[-1][0], int(i))
        else:
            out.append((int(i), int(i)))
    return out


def cv(starts) -> float:
    """Sample coefficient of variation (ddof = 1) of the intervals between episode starts; NaN below 2 intervals."""
    d = np.diff(np.asarray(starts, float))
    return float(d.std(ddof=1) / d.mean()) if len(d) >= 2 and d.mean() > 0 else np.nan


def cv_chance(n_episodes: int, n_bins: int, cv_obs: float, draws: int, seed: int) -> float:
    """Chance that `n_episodes` starts placed uniformly at random among `n_bins` bins (distinct) have a CV at or below
    `cv_obs`: the null for "regular spacing" (review, C). Seeded, so the value is reproducible."""
    if n_episodes < 3 or np.isnan(cv_obs):
        return np.nan
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(draws):
        s = np.sort(rng.choice(n_bins, n_episodes, replace=False))
        c = cv(s)
        hits += (not np.isnan(c)) and c <= cv_obs
    return hits / draws


def classify_dips(run: dict, bin_s: float, lead_s: float, pf_limit: float, merge_gap_bins: int, high_arrivals: float,
                  min_episodes_cycle: int, max_chance: float, min_preempt_share: float, min_arrival_share: float,
                  min_arrival_excess: float, draws: int, seed: int) -> dict:
    """Label a control's dips. In order:
    - too_few_episodes: fewer than 2 episodes (after merging);
    - ao_like_cycle: >= min_episodes_cycle episodes, spacing more regular than chance (cv_chance <= max_chance),
      preemptions in or in the bin before >= min_preempt_share of episodes, and a weak arrival link
      (arrival_share - base_share < min_arrival_excess);
    - arrival_driven: arrival_share >= min_arrival_share and arrival_share - base_share >= min_arrival_excess;
    - unclassified otherwise.
    arrival_share: share of episodes with a high lead (rate over [a - lead_s, a + bin_s) >= high_arrivals x lambda)
    at any of their bins; base_share: share of all bins with a high lead."""
    lam = float(run["cfg"]["workload"]["rate"])
    bins = bin_series(run, bin_s, lead_s)
    eps = episodes(bins, pf_limit, merge_gap_bins)
    high = (bins.lead_arrivals >= high_arrivals * lam).to_numpy()
    pre = bins.preemptions.to_numpy()
    starts = [float(bins.a.iloc[s]) for s, _ in eps]
    res = {"n_bins": len(bins), "n_episodes": len(eps), "episode_bins": int(sum(e - s + 1 for s, e in eps)),
           "arrival_share": float(np.mean([high[s:e + 1].any() for s, e in eps])) if eps else np.nan,
           "base_share": float(high.mean()) if len(high) else np.nan,
           "preempt_share": float(np.mean([pre[max(0, s - 1):e + 1].sum() > 0 for s, e in eps])) if eps else np.nan,
           "interval_cv": cv(starts), "episode_starts": starts,
           "preemptions_in_episodes": float(sum(pre[s:e + 1].sum() for s, e in eps)), "preemptions_total": float(pre.sum()),
           "unfinished_total": int(bins.unfinished.sum())}
    res["cv_chance"] = cv_chance(len(eps), len(bins), res["interval_cv"], draws, seed)
    excess = res["arrival_share"] - res["base_share"] if eps else np.nan
    if len(eps) < 2:
        label = "too_few_episodes"
    elif (len(eps) >= min_episodes_cycle and res["cv_chance"] <= max_chance
          and res["preempt_share"] >= min_preempt_share and excess < min_arrival_excess):
        label = "ao_like_cycle"
    elif res["arrival_share"] >= min_arrival_share and excess >= min_arrival_excess:
        label = "arrival_driven"
    else:
        label = "unclassified"
    return {"label": label, **res, "bins": bins}


# ---------------------------------------------------------------- registered settings (REG-2)

REG2 = {"runs": ["20261101-202808_stage2_control_cap_r4", "20261102-225146_stage2_control_kv72k_r3.5"],
        "bin_s": 60, "lead_s": 180, "pf_limit": 0.98, "merge_gap_bins": 2, "high_arrivals": 1.05,
        "min_episodes_cycle": 4, "max_chance": 0.05, "min_preempt_share": 2 / 3, "min_arrival_share": 2 / 3,
        "min_arrival_excess": 0.3, "draws": 20000, "seed": 0}

def _load(rid: str) -> dict:
    from analysis.load import RUNS, _jsonl, load_run
    run = load_run(RUNS / rid)
    if not (run["checks"] and run["checks"]["valid"]):
        raise ValueError(f"{rid} is not valid")
    return run, _jsonl(RUNS / rid / "metrics.jsonl")


def reg2_table() -> pd.DataFrame:
    keys = [k for k in REG2 if k != "runs"]
    rows = []
    for rid in REG2["runs"]:
        run, _ = _load(rid)
        res = classify_dips(run, **{k: REG2[k] for k in keys})
        res.pop("bins")
        rows.append({"run": rid, **res})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    import sys
    pd.set_option("display.width", 250, "display.max_columns", 40)
    if sys.argv[1:] == ["reg2"]:
        print(reg2_table().round(3).to_string(index=False))
    else:
        raise SystemExit("usage: python -m analysis.mechanisms reg2")
