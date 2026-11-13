"""E1 (registration: docs/decisions.md 2026-11-13 [REG] E1): the closed-loop cache-off sweep of setup L1
(configs/sweep_l1pl350cl_pc_off.yaml).

Judged: nothing. E1 *measures* K2's 8-turn closed-loop cold floor (`floor`, `gate.cold_floor` with REG-8's settings,
with the registered fallback `floor_tail` when that rule returns "not_monotone"). Owner, 2026-11-12: "Floor only".

Reported only, never judged: the served-mix tilt. Model F (Valse and Jannesari §3; BELIEF as to the model) says a
saturated all-miss server with closed-loop turns serves a mix tilted toward a session's early turns, more so as the
load rises; with open-loop turns it serves the planned mix. The E0/E1 rule F review showed (synthetic replays) that the
tilt follows from within-session precedence and work conservation alone, for FIFO, many slots, residence, superlinear
cost and LIFO alike (d_k -0.36 to -0.39 per req/s against model F's -0.39), so it cannot tell model F from other
servers and no decision may rest on it. `tilt` and `prediction` stay for the description: d = slope(closed) -
slope(open) of k-bar or throughput on rate, over the rates both sweeps have from the common onset up, E1's rows against
REG-8's open-loop cache-off rows at the same rates and seed; the prediction is the replay of both configs through
model F's server (`analysis/modelf_sim.py`) at mu = 1.681. No run folder is read by the prediction.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

from analysis import modelf_sim, withheld
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
    """d = slope(closed) - slope(open) of `col` over the rates >= lo that both sweeps have (a rate valid in one sweep
    only is left out of both); se combines the two fits' residual SEs. Reported only."""
    common = set(cl.rate) & set(ol.rate)
    cl, ol = cl[cl.rate.isin(common)], ol[ol.rate.isin(common)]
    a, b = fit(cl, col, lo), fit(ol, col, lo)
    return {"d": a["slope"] - b["slope"], "se": math.hypot(a["se"], b["se"]), "cl": a, "ol": b}


READOUTS = ("kbar", "throughput")   # kbar first: the served mix, which no token rate of the engine enters


def prediction(seeds: tuple | None = None) -> dict:
    """For each cost model and each possible onset (every grid rate from REG-8's onset 2.0 up to the third-highest, so
    at least three rows remain): d_F of each readout on seed 0, and the SD of d over replay seeds. Reported only; the
    `threshold` (half the d_F nearer zero) is kept as a description of where model F sits, not as a decision rule."""
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


def floor_tail(rows: pd.DataFrame) -> dict:
    """Registered fallback for `gate.cold_floor`'s "not_monotone" (a row at or above its lam_sat kept up or was not
    full): lam_sat becomes the lowest rate from which *every* row is saturated (KV >= min_kv and throughput < sat_frac
    x planned), and the floor is their mean, with at least min_runs rows ("too_few" otherwise). Its status carries the
    prefix "tail_" so a fallback floor is never mistaken for cold_floor's own."""
    s = rows[np.isfinite(rows[["rate", "throughput", "planned_rate", "kv_mean"]]).all(axis=1)].sort_values("rate")
    sat = ((s.kv_mean >= E1["floor_min_kv"]) & (s.throughput < E1["sat_frac"] * s.planned_rate)).to_numpy()
    out = {"mu_sat_off": math.nan, "lam_sat": math.nan, "n": 0}
    k = len(sat)
    while k > 0 and sat[k - 1]:
        k -= 1                                        # rows k.. are the saturated tail
    tail = s.iloc[k:]
    if not len(tail):
        return {**out, "status": "tail_unsaturated"}
    out.update(lam_sat=float(tail.rate.min()), n=len(tail))
    if len(tail) < E1["floor_min_runs"]:
        return {**out, "status": "tail_too_few"}
    return {**out, "mu_sat_off": float(tail.throughput.mean()), "status": "tail_ok"}


def floor(rows: pd.DataFrame, swept: tuple | list | None = None) -> dict:
    """E1's floor: `gate.cold_floor`; if and only if that returns "not_monotone", `floor_tail`. Two statuses of its
    own, neither a floor: "no_rows" when the sweep has no valid run at all (a sweep that was not read is not a sweep
    that did not saturate), and, when the swept rates are given, "holes" when a swept rate at or above the floor's
    lam_sat has no valid run (the floor would average over a gap)."""
    if not len(rows):
        return {"mu_sat_off": math.nan, "lam_sat": math.nan, "n": 0, "status": "no_rows"}
    f = saturated(rows)
    f = floor_tail(rows) if f["status"] == "not_monotone" else f
    if swept is not None and f["status"] in ("ok", "tail_ok"):
        have = set(np.round(rows.rate.to_numpy(float), 6))
        missing = [float(x) for x in swept if x >= f["lam_sat"] - 1e-9 and round(float(x), 6) not in have]
        if missing:
            return {**f, "mu_sat_off": math.nan, "status": "holes", "missing_rates": missing}
    return f


def first_valid(rows: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Registered rule for two valid runs at one rate (a rate launched again by mistake): the earliest run counts
    (run ids start with their launch time); the later ones are returned by name and reported."""
    s = rows.sort_values("run")
    keep = s.drop_duplicates("rate", keep="first")
    return keep.sort_values("rate").reset_index(drop=True), sorted(set(s.run) - set(keep.run))


def swept_rates(parent: str) -> tuple:
    """The rates the sweep's own config lists (`sweep.rates`), read from configs/<parent>.yaml."""
    from harness.run import load_config
    return tuple(float(x) for x in load_config(REPO / "configs" / f"{parent}.yaml")["sweep"]["rates"])


def observed() -> dict:
    """E1's floor (judged as a measurement, feeds E0) and the reported tilt against REG-8 (valid runs only). Never
    call before E1 has run under an approved [REG]."""
    cl, ol = sweep_rows(E1["sweeps"]["cl"]), sweep_rows(E1["sweeps"]["ol"])
    if not len(cl) or not len(ol):
        raise RuntimeError(f"no valid run of {E1['sweeps']['cl'] if not len(cl) else E1['sweeps']['ol']} can be read "
                           "(not run yet, or still sealed: set AFTERSHOCK_UNSEAL=E1)")
    cl, dropped = first_valid(cl)
    cl, ol = cl.assign(kbar=[_kbar(r) for r in cl.run]), ol.assign(kbar=[_kbar(r) for r in ol.run])
    res = {"floor": floor(cl, swept_rates(E1["sweeps"]["cl"])), "floor_ol": saturated(ol), "onset": onset(cl, ol),
           "rows_cl": cl.to_dict("records"), "later_valid_runs_not_counted": dropped}
    if not math.isnan(res["onset"]):
        res["tilt_reported"] = {col: tilt(cl, ol, col, res["onset"]) for col in READOUTS}
    return res


def _kbar(run_name: str) -> float:
    """Mean turn index (1-based) of the session turns completed ok in [warmup, duration) of one real run."""
    from analysis.load import RUNS, load_run
    r = load_run(RUNS / run_name)
    q, wl = r["requests"], r["cfg"]["workload"]
    done = q[(q.status == "ok") & (q.t_end >= wl["warmup_s"]) & (q.t_end < wl["duration_s"])]
    return float((done.turn + 1).mean()) if len(done) else math.nan


def work_rates(rows: pd.DataFrame, lam_sat: float) -> dict:
    """Reported only: REG-21's statistic U (`k3w.work_rate`, uncached prompt tokens per second by first token) of each
    row at rate >= lam_sat, over its measured window [warm-up, end of arrivals), with the gauges REG-21 reports for a
    reference run (running batch, waiting line, KV, preemptions per second, the redo proxy): a closed-loop server
    may differ from an open-loop one in its running batch and its preemptions, not only in its served mix."""
    from analysis import k3w
    from analysis.load import RUNS, load_run
    out = {}
    if math.isnan(lam_sat):
        return out
    for name in rows[rows.rate >= lam_sat - 1e-9].run:
        r = load_run(RUNS / name)
        wl = r["cfg"]["workload"]
        u = k3w.work_rate(r, wl["warmup_s"], wl["duration_s"])
        out[name] = {"U": u}
        try:
            out[name].update(k3w._gauges(r, float(wl["warmup_s"]), float(wl["duration_s"]), u))
        except Exception as e:   # a reported gauge never takes the work rate with it
            out[name]["gauges_error"] = f"{type(e).__name__}: {e}"[:200]
    return out


def floor_status(parent: str) -> str:
    """Only the status of `floor` on one sweep parent: the one flag E2 reads between its two sweeps. Raises when no
    valid run of the parent can be read, so that a forgotten AFTERSHOCK_UNSEAL is an error and not a status."""
    rows = sweep_rows(parent)
    if not len(rows):
        raise RuntimeError(f"no valid run of {parent} can be read (not run yet, or still sealed)")
    return floor(first_valid(rows)[0], swept_rates(parent))["status"]


def report() -> dict:
    """E1's registered result: `observed`, plus the work rates of both sweeps' saturated rows (reported only).
    The work rate is REG-21's statistic, and on REG-8's runs it is REG-21's reference: so this waits for REG-21's
    first [RESULT] and raises before it."""
    if not withheld.lifted("[RESULT] REG-21"):
        raise RuntimeError("E1's report computes REG-21's statistic on REG-8's runs: it waits for REG-21's [RESULT]")
    res = observed()
    cl, ol = sweep_rows(E1["sweeps"]["cl"]), sweep_rows(E1["sweeps"]["ol"])
    res["work_cl"] = work_rates(cl, res["floor"]["lam_sat"])
    res["work_ol"] = work_rates(ol, res["floor_ol"]["lam_sat"])
    return res


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) == 2 and sys.argv[1] == "floor":
        print(json.dumps(report(), indent=1, default=str))
    elif len(sys.argv) == 3 and sys.argv[1] == "status":
        print(json.dumps({"parent": sys.argv[2], "status": floor_status(sys.argv[2])}))
    else:
        raise SystemExit("usage: python -m analysis.e1 floor | status <sweep parent>")
