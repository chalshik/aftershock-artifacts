"""E1 (draft, not registered): the closed-loop cache-off sweep of setup L1 (configs/sweep_l1pl350cl_pc_off.yaml), and
the blind K3 test it carries (REG-21 round-2 review, recommendation 3: J4 as drafted could not change a decision).

Model F (Valse and Jannesari §3; BELIEF as to the model) says a saturated all-miss server with closed-loop turns serves a
mix tilted toward a session's early, short turns, and the tilt grows with the backlog, so its completion rate rises
with the offered rate; with open-loop turns the server serves the planned mix whatever the backlog, so its rate is
flat. The test statistic is the *tilt* d = slope(closed loop) - slope(open loop), each the least-squares slope of
throughput on rate over the rows `gate.cold_floor` counts as saturated: E1's own rows against REG-8's open-loop
cache-off rows at the same rates and seed. Engine effects that change throughput with the rate (batch size,
preemption) enter both slopes and cancel to the extent they act alike in the two loops.

The prediction is the replay of the two sweeps' own configs through model F's server (`analysis/modelf_sim.py`) at
the open-loop floor mu = 1.681: d_F on seed 0 (the runs' seed), and the spread of d over replay seeds. No run folder
is read by the prediction; `observed` reads E1's and REG-8's rows through `gate.sweep_rows`, after E1 has run.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

from analysis import modelf_sim
from analysis.gate import REG8, cold_floor, sweep_rows

REPO = Path(__file__).resolve().parent.parent
E1 = {
    "configs": {"cl": "configs/sweep_l1pl350cl_pc_off.yaml", "ol": "configs/sweep_l1pl350_pc_off_b.yaml"},
    "sweeps": {"cl": "sweep_l1pl350cl_pc_off", "ol": "sweep_l1pl350_pc_off"},
    "mu": 1.681,                                         # req/s, REG-8's open-loop floor (docs/model.md M2)
    "costs": {"prop": (0.0, 1.0), "fixed": (0.18, 0.000135)},   # as k3.REG21["costs"]; `fixed` = k2.calibrate_fixed
    "replay_seeds": tuple(range(20)),                    # the spread of d over trajectories
    "floor_min_kv": REG8["floor_min_kv"], "floor_min_runs": REG8["floor_min_runs"], "sat_frac": REG8["sat_frac"],
}


def _cfgs(path: str, seed: int | None = None) -> list[dict]:
    from harness.config import with_defaults
    from harness.run import expand, load_config
    out = []
    for c in expand(with_defaults(load_config(REPO / path))):
        if seed is not None:
            c = {**c, "seed": seed}
        out.append(c)
    return out


def replay_rows(path: str, mu: float, cost: tuple[float, float], seed: int | None = None) -> pd.DataFrame:
    """One sweep replayed with caching off (every request misses from t = 0): per rate, throughput and planned rate
    as `load.summarize` counts them (ok completions with t_end in [warmup, duration), planned arrivals there, over the
    span), and kv_mean set to 1 on rows that fell behind (throughput < sat_frac x planned) and 0 otherwise, so that
    `gate.cold_floor` applies unchanged (the replay has no KV pool; saturation stands in for full)."""
    rows = []
    for c in _cfgs(path, seed):
        wl = c["workload"]
        q = modelf_sim.simulate(c, mu, cost, all_miss_from=0.0)
        a, b = wl["warmup_s"], wl["duration_s"]
        span = b - a
        done = q[(q.status == "ok") & (q.t_end >= a) & (q.t_end < b)]
        thr, planned = len(done) / span, float(((q.t_planned >= a) & (q.t_planned < b)).sum() / span)
        rows.append({"rate": float(wl["rate"]), "throughput": thr, "planned_rate": planned,
                     "kv_mean": 1.0 if thr < E1["sat_frac"] * planned else 0.0,
                     "kbar": float((done.turn + 1).mean()) if len(done) else math.nan})
    return pd.DataFrame(rows).sort_values("rate").reset_index(drop=True)


def saturated(rows: pd.DataFrame) -> dict:
    """`gate.cold_floor` on a sweep's rows: status, lam_sat (the onset of saturation) and the floor."""
    return cold_floor(rows, E1["floor_min_kv"], E1["floor_min_runs"], E1["sat_frac"])


def onset(cl: pd.DataFrame, ol: pd.DataFrame) -> float:
    """The lowest rate at which both sweeps are saturated by cold_floor's rule (NaN unless both are 'ok'). The tilt is
    fitted over the rates from there up, the same set in both sweeps."""
    a, b = saturated(cl), saturated(ol)
    return max(a["lam_sat"], b["lam_sat"]) if a["status"] == b["status"] == "ok" else math.nan


def fit(rows: pd.DataFrame, col: str, lo: float) -> dict:
    """Least-squares slope of `col` on rate over rates >= lo, and its standard error from the residuals."""
    use = rows[(rows.rate >= lo - 1e-9) & np.isfinite(rows[col])]
    if len(use) < 2:
        return {"slope": math.nan, "se": math.nan, "n": len(use)}
    x, y = use.rate.to_numpy(float), use[col].to_numpy(float)
    k, c = np.polyfit(x, y, 1)
    sxx = float(((x - x.mean()) ** 2).sum())
    se = float(np.sqrt(((y - (k * x + c)) ** 2).sum() / (len(x) - 2) / sxx)) if len(x) > 2 else math.nan
    return {"slope": float(k), "se": se, "n": len(use)}


def tilt(cl: pd.DataFrame, ol: pd.DataFrame, col: str, lo: float) -> dict:
    """d = slope(closed) - slope(open) of `col` over rates >= lo; se combines the two fits' residual SEs."""
    a, b = fit(cl, col, lo), fit(ol, col, lo)
    return {"d": a["slope"] - b["slope"], "se": math.hypot(a["se"], b["se"]), "cl": a, "ol": b}


READOUTS = ("kbar", "throughput")   # kbar first: the served mix, which no token rate of the engine enters


def prediction(seeds: tuple | None = None) -> dict:
    """For each cost model and each possible onset (every grid rate from REG-8's onset 2.0 up to the third-highest, so
    at least three rows remain): d_F of each readout on seed 0, and the SD of d over replay seeds. The threshold between
    'tilted' (as model F) and 'flat' is half of the d_F nearer zero of the two cost models."""
    seeds = E1["replay_seeds"] if seeds is None else seeds
    reps = {name: {s: (replay_rows(E1["configs"]["cl"], E1["mu"], cost, s),
                       replay_rows(E1["configs"]["ol"], E1["mu"], cost, s)) for s in {0, *seeds}}
            for name, cost in E1["costs"].items()}
    rates = sorted(reps["prop"][0][0].rate)
    out = {}
    for lo in [r for r in rates if r >= 2.0][:-2]:
        per = {}
        for col in READOUTS:
            m = {}
            for name in E1["costs"]:
                d0 = tilt(*reps[name][0], col, lo)["d"]
                ds = [tilt(*reps[name][s], col, lo)["d"] for s in seeds]
                m[name] = {"d_F": d0, "d_sd": float(np.std(ds, ddof=1)) if len(ds) > 1 else math.nan}
            near = min((v["d_F"] for v in m.values()), key=abs)
            per[col] = {"models": m, "threshold": near / 2}
        out[lo] = per
    return {"by_onset": out, "rows_seed0": {n: {k: v.to_dict("records") for k, v in zip(("cl", "ol"), reps[n][0])}
                                            for n in reps}}


def judge(t: dict, threshold: float) -> str:
    """'tilted' or 'flat' by the side of the threshold d falls on; 'unresolved' if it lies within 2 SE of it (the SE
    from the two fits' residuals, so the engine's own run-to-run noise sets it, not the replay's)."""
    d, se = t["d"], t["se"]
    if math.isnan(d):
        return "nan"
    if not math.isnan(se) and abs(d - threshold) < 2 * se:
        return "unresolved"
    sign = 1 if threshold > 0 else -1
    return "tilted" if sign * (d - threshold) >= 0 else "flat"


def observed(pred: dict) -> dict:
    """E1's and REG-8's real rows (valid runs only) judged against the registered prediction. Never call before E1
    has run under an approved [REG]."""
    cl, ol = sweep_rows(E1["sweeps"]["cl"]), sweep_rows(E1["sweeps"]["ol"])
    cl, ol = cl.assign(kbar=[_kbar(r) for r in cl.run]), ol.assign(kbar=[_kbar(r) for r in ol.run])
    lo = onset(cl, ol)
    res = {"floor_cl": saturated(cl), "floor_ol": saturated(ol), "onset": lo}
    if math.isnan(lo) or lo not in pred["by_onset"]:
        return {**res, "status": "no_prediction_for_this_onset"}
    for col in READOUTS:
        t = tilt(cl, ol, col, lo)
        res[col] = {**t, "threshold": pred["by_onset"][lo][col]["threshold"],
                    "label": judge(t, pred["by_onset"][lo][col]["threshold"])}
    return {**res, "status": "ok"}


def _kbar(run_name: str) -> float:
    """Mean turn index (1-based) of the session turns completed ok in [warmup, duration) of one real run."""
    from analysis.load import RUNS, load_run
    r = load_run(RUNS / run_name)
    q, wl = r["requests"], r["cfg"]["workload"]
    done = q[(q.status == "ok") & (q.t_end >= wl["warmup_s"]) & (q.t_end < wl["duration_s"])]
    return float((done.turn + 1).mean()) if len(done) else math.nan
