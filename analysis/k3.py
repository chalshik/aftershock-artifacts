"""K3, model transfer, step B: registration REG-21 (draft, docs/decisions.md 2026-11-12 [REG]; docs/claims.md K3).
Never writes into runs/.

Redrafted after the rule F review of the first draft (it judged long-run values of model F on 900 s windows: the
burst and the turn gaps move those windows away from the long run, and the served-turn mix had been partly seen).
This draft replays model F on each run's own schedule (`analysis/modelf_sim.py`) and judges *floors*, not mixes:
  mu_k   the all-miss capacity at which the replay reproduces the run's mean served turn index in W
  mu_X   the all-miss capacity at which the replay reproduces the run's session-turn completion rate in W
Model F (BELIEF as to the model) has one all-miss capacity for a server, whatever the turn semantics and the load, so:
  J1  the medians of mu_k by load (2.0, 2.2, 2.4; REG-15 apart) agree;
  J2  mu_k and mu_X agree (the mix and the throughput imply the same floor);
  J3  mu_k agrees with the open-loop cache-off floor 1.681 (REG-8): under model F a saturated open-loop sweep serves
      the planned, stationary mix, so its throughput is the all-miss capacity itself;
  J4  blind: E1's closed-loop cache-off floor statistic equals the replay of E1's own configs at the pooled mu_k
      (judged when E1 reports; E1's statistic is the one it registers, by default `gate.cold_floor`'s).
Only runs that are all-miss in W enter J1-J3 (reuse of later turns in W <= allmiss_reuse_max).
Observed readouts on W = [burst end + offset_s, burst end + watch_s), session requests only:
  kbar_obs  mean turn index (1..8) of session turns completed ok in W (by t_end)
  X_obs     session turns completed ok in W per second
  d_obs     sessions whose last turn completed in W / sessions whose turn 0 is planned in W
Reported, never judged: kbar_obs, d_obs and X_obs against the replay at 1.681 and at mu_k (the first draft's Q1, Q2',
Q2), the long-run values of `analysis/modelf.py`, uncached prompt tokens per second against REG-8's saturated sweeps,
Huang and Liu's rule (arXiv 2611.13412 §3), preemptions per second, kbar_obs per half of W, the burst requests in W,
`gate.shock_size`.
"""
from __future__ import annotations

import math

import numpy as np

from analysis import modelf, modelf_sim
from analysis.gate import REG8, burst_end, shock_size
from analysis.k1 import cold_backlogged, reuse
from analysis.load import find_runs
from analysis.margin import is_burst_request

REG21 = {
    # Batch 1: every valid closed-loop L1 burst run at 350 W made before REG-19 (REG-11, REG-12 seeds 2-6, REG-14,
    # REG-15, REG-17, REG-18 seeds 3-6); a run enters only if `k1.cold_backlogged` holds in its own end window.
    "batch1": ("20261109-042828_burst_l1pl350cl_r2.4_s1", "20261109-080203_burst_l1pl350cl_r2.4_s2",
               "20261109-093609_burst_l1pl350cl_r2.4_s3", "20261109-111316_burst_l1pl350cl_r2.4_s4",
               "20261109-125300_burst_l1pl350cl_r2.4_s5", "20261109-151300_burst_l1pl350cl_r2.4_s6",
               "20261110-063647_burst_l1pl350cl_r2.2_s2", "20261110-085730_confirm_l1pl350cl_r2.2_s12",
               "20261110-182920_burst_l1pl350cl_r2.0_s2", "20261111-101805_burst_l1pl350cl_r2.0_s4",
               "20261111-115409_burst_l1pl350cl_r2.0_s3", "20261111-133019_burst_l1pl350cl_r2.0_s5",
               "20261111-150642_burst_l1pl350cl_r2.0_s6"),
    "apart": ("20261110-085730_confirm_l1pl350cl_r2.2_s12",),   # REG-15: 3900 s W, its own group in J1
    # Batch 2, reported separately and only after REG-19's [RESULT]: REG-19's burst runs (not the drift rerun).
    "batch2_pattern": "*_burst_l1pl350cl_r2.0_w3000_s1[5-9]",
    "offset_s": 600.0,          # W starts 600 s after the burst's end (REG-19's counting window starts there too)
    "turns": 8,
    "mu_off": 1.681,            # req/s, the open-loop cache-off floor (REG-8; docs/model.md M2)
    "costs": {"prop": (0.0, 1.0), "fixed": (0.18, 0.000135)},   # turn cost a + b L (docs/model.md M5)
    "mu_grid": (1.30, 2.40, 0.01),   # req/s: where mu_k and mu_X are searched
    "local_half": 0.10,         # req/s: half-width of the stretch `local_fit` fits a line to
    "allmiss_reuse_max": 0.05,  # a run enters J1-J3 only if later turns reuse at most this in W
    "hl_window_s": 300.0, "hl_degraded_hit": 0.5,
    "cacheoff_pattern": "*_sweep_l1pl350_pc_off_r*", "cacheoff_min_rate": 2.0,   # REG-8's floor runs (lam_sat 2.0)
    # Tolerances (registered before mu_k, mu_X or any readout here is computed on a real run):
    "tol_groups": 0.10,         # J1: max - min of the group medians of mu_k
    "tol_kx": 0.08,             # J2: median over runs of mu_k - mu_X
    "tol_floor": 0.08,          # J3: median mu_k - 1.681
    "tol_e1": 0.08,             # J4: |E1's statistic - the replay's| for either cost model
}


# ---------------------------------------------------------------- observed readouts

def window(run: dict) -> tuple[float, float]:
    e = burst_end(run)
    return e + REG21["offset_s"], e + float(run["cfg"]["verdict"]["watch_s"])


def session_turns(run: dict):
    q = run["requests"]
    return q[~is_burst_request(run)]


def completed(run: dict, a: float, b: float):
    q = session_turns(run)
    return q[(q.status == "ok") & (q.t_end >= a) & (q.t_end < b)]


def lam_w(run: dict, a: float, b: float, turns: int | None = None) -> float:
    """Planned request rate of the sessions starting in [a, b): turns x sessions with turn 0 planned there / (b - a)."""
    q, T = session_turns(run), turns or REG21["turns"]
    return T * int(((q.turn == 0) & (q.t_planned >= a) & (q.t_planned < b)).sum()) / (b - a)


def kbar_obs(run: dict, a: float, b: float) -> float:
    w = completed(run, a, b)
    return float((w.turn + 1).mean()) if len(w) else math.nan


def x_obs(run: dict, a: float, b: float) -> float:
    return len(completed(run, a, b)) / (b - a)


def d_obs(run: dict, a: float, b: float, turns: int | None = None) -> float:
    T, q = turns or REG21["turns"], session_turns(run)
    starts = int(((q.turn == 0) & (q.t_planned >= a) & (q.t_planned < b)).sum())
    w = completed(run, a, b)
    return int((w.turn == T - 1).sum()) / starts if starts else math.nan


def kbar_of_z(z: float, turns: int) -> float:
    nu = [z ** -(k + 1) for k in range(turns)]
    return sum((k + 1) * v for k, v in enumerate(nu)) / sum(nu)


def uncached_rate(run: dict, a: float, b: float) -> float:
    """Uncached prompt tokens per second over every request (burst ones too) completed ok in [a, b)."""
    q = run["requests"]
    w = q[(q.status == "ok") & (q.t_end >= a) & (q.t_end < b)]
    return float((w.prompt_tokens - w.cached_tokens.fillna(0)).clip(lower=0).sum() / (b - a))


def cacheoff_uncached() -> dict:
    """Reference for `uncached_tok_s`: the same rate on REG-8's saturated cache-off sweeps (the five runs at rate >=
    lam_sat = 2.0 that give mu_off = 1.681), each over its measured window (`load.window`: warm-up to end of
    arrivals). Reported, never judged."""
    runs = [r for r in find_runs(REG21["cacheoff_pattern"]) if r["cfg"]["workload"]["rate"] >= REG21["cacheoff_min_rate"]]
    vals = {r["dir"].name: uncached_rate(r, r["cfg"]["workload"]["warmup_s"], r["cfg"]["workload"]["duration_s"])
            for r in runs}
    return {"runs": vals, "mean": float(np.mean(list(vals.values()))) if vals else math.nan}


def hl_rule(run: dict) -> dict:
    """Huang and Liu's persistent-degradation rule on session turns, token-weighted hit by t_end, windows aligned to
    the burst's end through the end of the watch."""
    e, (_, b), step = burst_end(run), window(run), REG21["hl_window_s"]
    hits = []
    for t in np.arange(e, b - step + 1e-9, step):
        w = completed(run, t, t + step)
        den = w.prompt_tokens.sum()
        hits.append(float(w.cached_tokens.fillna(0).sum() / den) if den > 0 else math.nan)
    low = [h < REG21["hl_degraded_hit"] for h in hits]
    first = next((i for i, x in enumerate(low) if x), None)
    persistent = first is not None and all(low[first:]) and not any(math.isnan(h) for h in hits[first:])
    return {"hits": hits, "first_degraded": first, "persistently_degraded": persistent}


def counter_rate(run: dict, col: str, a: float, b: float) -> float:
    """Increase of a raw counter over [a, b) per second, from the first and last scrape inside; NaN if missing or if
    the counter went down anywhere inside (a restart: flagged, not hidden)."""
    m = run["metrics"]
    if not len(m) or col not in m:
        return math.nan
    w = m[(m.t >= a) & (m.t < b)]
    if len(w) < 2 or (w[col].diff().dropna() < 0).any():
        return math.nan
    return float((w[col].iloc[-1] - w[col].iloc[0]) / (w.t.iloc[-1] - w.t.iloc[0]))


def observed(run: dict) -> dict:
    a, b = window(run)
    mid = 0.5 * (a + b)
    q = run["requests"]
    br = q[is_burst_request(run) & (q.status == "ok") & (q.t_end >= a) & (q.t_end < b)]
    return {"W": (a, b), "lam_W": lam_w(run, a, b), "kbar": kbar_obs(run, a, b), "X": x_obs(run, a, b),
            "d": d_obs(run, a, b), "n_turns": len(completed(run, a, b)), "reuse_W": reuse(run, a, b),
            "kbar_halves": (kbar_obs(run, a, mid), kbar_obs(run, mid, b)), "burst_in_W": len(br),
            "uncached_tok_s": uncached_rate(run, a, b), "hl": hl_rule(run),
            "preempt_per_s": counter_rate(run, "vllm:num_preemptions_total", a, b)}


# ---------------------------------------------------------------- the replay and the fitted floors

def replay(cfg: dict, mu: float, cost: tuple[float, float], sched=None) -> dict:
    """The k3 readouts in W on model F's replay of the run's schedule at all-miss capacity mu."""
    run = modelf_sim.as_run(cfg, modelf_sim.simulate(cfg, mu, cost, sched=sched))
    a, b = window(run)
    return {"kbar": kbar_obs(run, a, b), "X": x_obs(run, a, b), "d": d_obs(run, a, b)}


def crossing(grid: np.ndarray, vals: np.ndarray, target: float) -> dict:
    """mu where vals(mu) - target changes sign (linear interpolation), if it does so exactly once on the grid.
    Otherwise NaN with the reason: "target_above_grid_values", "target_below_grid_values", "flat" or "multiple".
    Used for curves that are smooth on the grid; the replay's kbar is not (see `local_fit`)."""
    if math.isnan(target):
        return {"mu": math.nan, "status": "nan"}
    f = np.asarray(vals, float) - target
    ok = ~np.isnan(f)
    idx = [i for i in range(len(f) - 1) if ok[i] and ok[i + 1] and (f[i] == 0 or f[i] * f[i + 1] < 0)]
    if ok[-1] and f[-1] == 0:
        idx.append(len(f) - 1)
    if len(idx) == 1:
        i = idx[0]
        if f[i] == 0:
            return {"mu": float(grid[i]), "status": "ok"}
        return {"mu": float(grid[i] - f[i] * (grid[i + 1] - grid[i]) / (f[i + 1] - f[i])), "status": "ok"}
    if not idx:
        if np.nanmax(f) < 0:
            return {"mu": math.nan, "status": "target_above_grid_values"}
        if np.nanmin(f) > 0:
            return {"mu": math.nan, "status": "target_below_grid_values"}
        return {"mu": math.nan, "status": "flat"}
    return {"mu": math.nan, "status": "multiple"}


def local_fit(grid: np.ndarray, vals: np.ndarray, target: float, half: float | None = None) -> dict:
    """mu at which a least-squares line through the replay's values reaches the target. The replay is discrete, so its
    kbar(mu) jitters by about 0.005-0.01 and is not monotone; a sign-change search then finds several crossings.
    Procedure (registered): start at the grid point whose value is nearest the target; fit a line to the values
    within +- half of it; solve; if the solution falls outside that stretch, re-centre once on it and refit. Status
    "ok" with the line's residual SD (`jitter`), or "no_slope" (slope <= 0), "edge" (the solution is outside the grid
    or still outside the stretch after re-centring), "nan"."""
    h = REG21["local_half"] if half is None else half
    v = np.asarray(vals, float)
    if math.isnan(target) or np.isnan(v).all():
        return {"mu": math.nan, "status": "nan", "jitter": math.nan, "slope": math.nan}
    centre = float(grid[int(np.nanargmin(np.abs(v - target)))])
    for _ in range(2):
        m = (np.abs(grid - centre) <= h + 1e-9) & ~np.isnan(v)
        if m.sum() < 3:
            return {"mu": math.nan, "status": "nan", "jitter": math.nan, "slope": math.nan}
        slope, icpt = np.polyfit(grid[m], v[m], 1)
        if slope <= 0:
            return {"mu": math.nan, "status": "no_slope", "jitter": math.nan, "slope": float(slope)}
        mu = (target - icpt) / slope
        jitter = float(np.std(v[m] - (slope * grid[m] + icpt), ddof=2))
        if abs(mu - centre) <= h:
            if mu < grid[0] or mu > grid[-1]:
                break
            return {"mu": float(mu), "status": "ok", "jitter": jitter, "slope": float(slope)}
        centre = float(np.clip(mu, grid[0], grid[-1]))
    return {"mu": math.nan, "status": "edge", "jitter": math.nan, "slope": math.nan}


def grid() -> np.ndarray:
    lo, hi, step = REG21["mu_grid"]
    return np.round(np.arange(lo, hi + step / 2, step), 6)


def fit(run: dict, obs: dict | None = None) -> dict:
    """mu_k and mu_X for each cost model, and the replay's readouts at 1.681 and at mu_k (reported)."""
    obs = obs or observed(run)
    cfg, g = run["cfg"], grid()
    sched = modelf_sim.schedule(cfg)
    out = {}
    for name, cost in REG21["costs"].items():
        reps = [replay(cfg, float(m), cost, sched) for m in g]
        k = local_fit(g, np.array([r["kbar"] for r in reps]), obs["kbar"])
        x = local_fit(g, np.array([r["X"] for r in reps]), obs["X"])
        at_floor = replay(cfg, REG21["mu_off"], cost, sched)
        at_k = replay(cfg, k["mu"], cost, sched) if not math.isnan(k["mu"]) else None
        out[name] = {"mu_k": k["mu"], "mu_k_status": k["status"], "mu_k_jitter": k["jitter"], "mu_k_slope": k["slope"],
                     "mu_X": x["mu"], "mu_X_status": x["status"], "mu_X_jitter": x["jitter"],
                     "at_floor": at_floor, "at_mu_k": at_k}
    return out


def long_run(lam: float) -> dict:
    """The first draft's yardstick, reported only: model F's long-run values at rho = lam / 1.681."""
    T, rho = REG21["turns"], lam / REG21["mu_off"]
    if rho <= 1:
        return {"kbar": math.nan, "d": math.nan, "X": math.nan}
    t = modelf.l1(lam, REG21["mu_off"], T)
    return {"kbar": kbar_of_z(t.z, T), "d": t.z ** -T, "X": t.requests * REG21["mu_off"]}


def row(run: dict) -> dict:
    obs = observed(run)
    return {"run": run["dir"].name, "lam": float(run["cfg"]["workload"]["rate"]), "obs": obs, "fit": fit(run, obs),
            "long_run": long_run(obs["lam_W"]), "shock": shock_size(run),
            "allmiss": (not math.isnan(obs["reuse_W"])) and obs["reuse_W"] <= REG21["allmiss_reuse_max"]}


# ---------------------------------------------------------------- judging

def _median(xs) -> float:
    xs = [x for x in xs if not math.isnan(x)]
    return float(np.median(xs)) if xs else math.nan


def group(r: dict) -> str:
    return "apart:" + r["run"] if r["run"] in REG21["apart"] else f"{r['lam']:.1f}"


def judge(rows: list[dict], cost: str = "prop") -> dict:
    """J1-J3 on the all-miss rows for one cost model. Rows left out (not all-miss) and rows without a fitted value
    are listed with their reason, never dropped silently. Labels: "inside" / "outside", or "nan"."""
    R = REG21
    use = [r for r in rows if r["allmiss"]]
    mk = {r["run"]: r["fit"][cost]["mu_k"] for r in use}
    mx = {r["run"]: r["fit"][cost]["mu_X"] for r in use}
    groups: dict[str, list[float]] = {}
    for r in use:
        groups.setdefault(group(r), []).append(mk[r["run"]])
    gmed = {g: _median(v) for g, v in groups.items()}
    fin = [v for v in gmed.values() if not math.isnan(v)]
    spread = max(fin) - min(fin) if len(fin) >= 2 else math.nan
    kx = _median([mk[i] - mx[i] for i in mk])
    pooled = _median(list(mk.values()))
    lab = lambda x, tol: "nan" if math.isnan(x) else ("inside" if abs(x) <= tol else "outside")
    return {
        "cost": cost, "n_rows": len(rows), "n_allmiss": len(use),
        "not_allmiss": [r["run"] for r in rows if not r["allmiss"]],
        "unfitted": {r["run"]: (r["fit"][cost]["mu_k_status"], r["fit"][cost]["mu_X_status"]) for r in use
                     if math.isnan(mk[r["run"]]) or math.isnan(mx[r["run"]])},
        "J1": {"group_medians": gmed, "spread": spread,
               "label": "nan" if math.isnan(spread) else ("inside" if spread <= R["tol_groups"] else "outside")},
        "J2": {"median_mu_k_minus_mu_X": kx, "label": lab(kx, R["tol_kx"])},
        "J3": {"pooled_mu_k": pooled, "minus_floor": pooled - R["mu_off"],
               "label": lab(pooled - R["mu_off"], R["tol_floor"])},
    }


def overall(judged: dict[str, dict]) -> dict:
    """One label per J item from the per-cost-model judges: "inside" if inside under at least one cost model (as J4),
    "outside" if outside under every model that has a label, "nan" if none has one. Per-model labels stay reported."""
    out = {}
    for j in ("J1", "J2", "J3"):
        labs = [judged[c][j]["label"] for c in judged]
        out[j] = "inside" if "inside" in labs else ("outside" if "outside" in labs else "nan")
    return out


# ---------------------------------------------------------------- E1 (blind)

def e1_statistic(cfgs: list[dict], mu: float, cost: tuple[float, float], sat_frac: float | None = None) -> dict:
    """The replay of E1's sweep at all-miss capacity mu (caching off: every request misses from t = 0), read with
    `gate.cold_floor`'s rule without the KV condition (the replay has no KV): throughput = requests completed ok in
    [warm-up, end of arrivals) per second; lam_sat = the lowest rate whose throughput < sat_frac x planned rate; the
    statistic is the mean throughput at rates >= lam_sat. E1's [REG] may register another statistic; then this
    function is replaced before E1 runs, never after."""
    sf = REG8["sat_frac"] if sat_frac is None else sat_frac
    rows = []
    for cfg in cfgs:
        wl = cfg["workload"]
        reqs = modelf_sim.simulate(cfg, mu, cost, all_miss_from=0.0)
        a, b = wl["warmup_s"], wl["duration_s"]
        thr = float(((reqs.status == "ok") & (reqs.t_end >= a) & (reqs.t_end < b)).sum() / (b - a))
        planned = float(((reqs.t_planned >= a) & (reqs.t_planned < b)).sum() / (b - a))
        rows.append({"rate": float(wl["rate"]), "throughput": thr, "planned_rate": planned})
    rows.sort(key=lambda r: r["rate"])
    sat = [r for r in rows if r["throughput"] < sf * r["planned_rate"]]
    if not sat:
        return {"rows": rows, "lam_sat": math.nan, "statistic": math.nan, "status": "unsaturated"}
    lam_sat = sat[0]["rate"]
    use = [r for r in rows if r["rate"] >= lam_sat]
    return {"rows": rows, "lam_sat": lam_sat, "statistic": float(np.mean([r["throughput"] for r in use])),
            "status": "ok"}


def e1_prediction(cfgs: list[dict], judged: dict[str, dict]) -> dict:
    """For each cost model: the replay of E1 at that model's pooled mu_k, and at 1.681, so that one can see whether
    E1 can tell the two apart (`separates`: the two statistics differ by more than tol_e1)."""
    out = {}
    for name, cost in REG21["costs"].items():
        mu = judged[name]["J3"]["pooled_mu_k"]
        at_mu = e1_statistic(cfgs, mu, cost) if not math.isnan(mu) else None
        at_floor = e1_statistic(cfgs, REG21["mu_off"], cost)
        out[name] = {"mu": mu, "predicted": at_mu["statistic"] if at_mu else math.nan,
                     "at_open_loop_floor": at_floor["statistic"],
                     "separates": bool(at_mu) and abs(at_mu["statistic"] - at_floor["statistic"]) > REG21["tol_e1"]}
    return out


def e1_hit(pred: dict, measured: float) -> bool:
    return any(not math.isnan(p["predicted"]) and abs(p["predicted"] - measured) <= REG21["tol_e1"]
               for p in pred.values())


# ---------------------------------------------------------------- the table

def select(runs: list[dict]) -> tuple[list[dict], list[dict]]:
    """(entered, left out): a run enters when `k1.cold_backlogged` holds in its own end window."""
    keep, out = [], []
    for r in runs:
        st = cold_backlogged(r)
        (keep if st["cold_backlogged"] else out).append({"run": r, "state": st})
    return [x["run"] for x in keep], [{"run": x["run"]["dir"].name, "cold_backlogged": x["state"]["cold_backlogged"]}
                                      for x in out]


def reg21_table(batch: int = 1) -> dict:
    """Never call before the owner approves REG-21; batch 2 never before REG-19's [RESULT]."""
    if batch == 1:
        found = {r["dir"].name: r for r in find_runs("*_l1pl350cl_*")}
        missing = [i for i in REG21["batch1"] if i not in found]
        runs = [found[i] for i in REG21["batch1"] if i in found]
    else:
        runs, missing = [r for r in find_runs(REG21["batch2_pattern"]) if not r["dir"].name.endswith("_drift")], []
    entered, left = select(runs)
    rows = [row(r) for r in entered]
    return {"batch": batch, "missing_or_invalid": missing, "left_out": left, "rows": rows,
            "judged": (j := {c: judge(rows, c) for c in REG21["costs"]}), "overall": overall(j),
            "uncached_reference": cacheoff_uncached()}


def reg21_e1(e1_config_paths: list[str], table: dict) -> dict:
    """E1's prediction, computed once from E1's configs before E1 runs and recorded in docs/model.md's ledger."""
    from harness.run import load_config
    from pathlib import Path
    return e1_prediction([load_config(Path(p)) for p in e1_config_paths], table["judged"])


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "reg21":
        b = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        print(json.dumps(reg21_table(b), indent=1, default=str))
