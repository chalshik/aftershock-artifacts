"""K3, step B, as registered: REG-21 (docs/decisions.md 2026-11-13 [REG]; docs/claims.md K3). Never writes into runs/.

Question: does the stuck (cold, backlogged) server do the work of the all-miss server? Model F (Valse and Jannesari,
arXiv 2611.08902 §3; BELIEF as to the model) gives the trapped server one capacity, its all-miss capacity, whatever the
load, and their registered trap rule (their Table 1) asks for an "uncached prefill token rate within ±15% of the
all-miss rate". In tokens the statement needs no model of the queue.

  U      uncached prompt tokens per second: Σ (prompt_tokens - cached_tokens) over ok requests, session and burst,
         whose first token falls in the window (the first token ends a request's prefill)
  U_off  the mean of U over REG-8's five saturated cache-off runs (the pinned ids of REG21["ref_runs"]: the runs at
         rate >= lam_sat = 2.0 that give the floor 1.681 req/s), each over its measured window
  r      U over W / U_off, per stuck run; W = [burst end + 600 s, burst end + watch)

A run enters when `k1.cold_backlogged` holds in its own end window. It is judged only if, in W, it is all-miss (reuse
of later turns <= allmiss_reuse_max) and busy (requests waiting in at least busy_min of the scrapes, the gauge covering
W with no gap above gauge_max_gap_s): an engine that idles in part of W does less work for a reason that is not its
capacity. The gauge `vllm:num_requests_waiting` counts the scheduler's waiting queues without the deferred requests
and no request of the running set (SOURCE(vLLM 0.32.0 vllm/v1/core/sched/scheduler.py:Scheduler.make_stats,
Scheduler.get_request_counts)), so an engine that holds every request in its running set reads 0 and is left out.

Judged (thresholds registered before r is computed on any run):
  J2  load (batch 1 only): max - min of the medians of r over the load groups with at least min_group_runs judged runs
      <= tol_spread
  J1  level: |median of r - 1| <= tol_level. The median pools loads only when J2 is inside, and only the runs of the
      load groups J2 judged (the pooling assumption is J2's statement, rule H; a group of fewer than min_group_runs
      runs is covered by no such statement, so its runs are reported and not pooled). Otherwise J1 is given per load
      group and the pooled label is "not_pooled".
r needs no model of the queue, of the turn mix or of how long a request stays in the running batch; the earlier
drafts' fitted capacities (analysis/k3.py: mu_k, mu_X) did, and are not computed.

Reported, never judged: U by t_end; r against the reference without its lam = 2.0 run; the slope of r on the load; per
group n, min, max, SD, the runs' dates and the side of the group's own level; the same table with busy_min_reported
in place of busy_min; batch 2's median minus batch 1's lam = 2.0 group median (the same load on other days); Valse
and Jannesari's trap rule read per run (token part within 0.15, backlog slope above half the excess); the request
rates, the mean served prompt, the mean turn index and first-turn share, sessions completed over started, the median
time from first token to end, running batch, KV, waiting, preemptions and the redo proxy (preemptions per second x
mean prompt / U) in W (and the same for each reference run), Huang and Liu's rule, the burst's size, model F's
long-run values, and model F's replay on the run's own schedule at 1.681 with and without that residence.
"""
from __future__ import annotations

import math

import numpy as np

from analysis import k3, modelf_sim, withheld
from analysis.gate import burst_end, shock_size
from analysis.k1 import cold_backlogged, reuse
from analysis.load import _covered, find_runs
from analysis.margin import is_burst_request

REG21 = {
    # Batch 1: the 13 closed-loop L1 burst runs at 350 W made before REG-19 (REG-11, REG-12, REG-14, REG-15, REG-17,
    # REG-18). Every one must be there and valid.
    "batch1": ("20261109-042828_burst_l1pl350cl_r2.4_s1", "20261109-080203_burst_l1pl350cl_r2.4_s2",
               "20261109-093609_burst_l1pl350cl_r2.4_s3", "20261109-111316_burst_l1pl350cl_r2.4_s4",
               "20261109-125300_burst_l1pl350cl_r2.4_s5", "20261109-151300_burst_l1pl350cl_r2.4_s6",
               "20261110-063647_burst_l1pl350cl_r2.2_s2", "20261110-085730_confirm_l1pl350cl_r2.2_s12",
               "20261110-182920_burst_l1pl350cl_r2.0_s2", "20261111-101805_burst_l1pl350cl_r2.0_s4",
               "20261111-115409_burst_l1pl350cl_r2.0_s3", "20261111-133019_burst_l1pl350cl_r2.0_s5",
               "20261111-150642_burst_l1pl350cl_r2.0_s6"),
    "batch2_pattern": "*_burst_l1pl350cl_r2.0_w3000_s1[5-9]",   # REG-19's burst runs, only after REG-19's [RESULT]
    "batch2_seeds": (15, 16, 17, 18, 19),               # in REG-19's run order; batch 2 is a prefix of them
    "batch2_heading": "[RESULT] REG-19",
    "offset_s": 600.0,                                  # W starts 600 s after the burst's end
    "allmiss_reuse_max": 0.05,                          # judged only if later turns reuse at most this in W
    "busy_min": 0.99,                                   # judged only if requests wait in at least this share of W's scrapes
    "gauge_max_gap_s": 10.0,                            # ... and the waiting gauge covers W with no gap above this
    "busy_min_reported": 0.95,                          # a second table at this share is reported, never judged
    # REG-8's floor runs (lam_sat 2.0; decisions.md 2026-11-07 [RESULT] REG-8): exactly these five, each valid
    "ref_runs": ("20261107-083730_sweep_l1pl350_pc_off_r2", "20261107-085650_sweep_l1pl350_pc_off_r2.5",
                 "20261107-091752_sweep_l1pl350_pc_off_r3", "20261107-093854_sweep_l1pl350_pc_off_r3.5",
                 "20261107-095958_sweep_l1pl350_pc_off_r4"),
    "ref_pattern": "*_sweep_l1pl350_pc_off_r*",
    "ref_min_rate": 2.0,                                # lam_sat of REG-8: a valid run at or above it belongs to the floor
    "ref_alt_min_rate": 2.5,                            # the reported second reference leaves the lam = 2.0 run out
    "contrast_group": "2.0",                            # batch 2's load, for the reported fixed-load contrast
    "mu_off": 1.681,                                    # req/s, the open-loop cache-off floor (REG-8)
    "turns": 8,
    "tol_level": 0.05,                                  # J1
    "tol_spread": 0.05,                                 # J2
    "min_runs": 3,                                      # J1 needs this many judged runs
    "min_group_runs": 3,                                # J2 uses a load group only with this many judged runs
    "vj_token_tol": 0.15, "vj_slope_frac": 0.5,         # Valse and Jannesari's trap rule (their Table 1), reported only
    "grid_s": 10.0,
    "costs": {"prop": (0.0, 1.0), "fixed": (0.18, 0.000135)},   # turn cost a + b L (docs/model.md M5), replays only
}
EPS = 1e-9   # a value exactly at a tolerance is inside, whatever the float rounding


def window(run: dict) -> tuple[float, float]:
    e = burst_end(run)
    return e + REG21["offset_s"], e + float(run["cfg"]["verdict"]["watch_s"])


def _ok_in(run: dict, a: float, b: float, by: str):
    q = run["requests"]
    return q[(q.status == "ok") & (q[by] >= a) & (q[by] < b)]


def work_rate(run: dict, a: float, b: float, by: str = "t_first_token") -> float:
    """U: uncached prompt tokens per second over ok requests (burst ones too) whose `by` time falls in [a, b)."""
    q = run["requests"]
    ok = q[q.status == "ok"]
    if ok[by].isna().any() or ok.prompt_tokens.isna().any():
        raise ValueError(f"an ok request without {by} or prompt_tokens: the work rate would silently leave it out")
    w = _ok_in(run, a, b, by)
    if not len(w):
        return math.nan
    cached = w.cached_tokens.fillna(0) if "cached_tokens" in w else 0
    return float((w.prompt_tokens - cached).clip(lower=0).sum() / (b - a))


def busy_share(run: dict, a: float, b: float) -> float:
    """Share of the scrapes in [a, b) with at least one request waiting. NaN when the gauge does not cover [a, b):
    no scrapes, no such column, or a gap between its values above gauge_max_gap_s (`load._covered`, the test every
    level in `load._level` passes through). A share over the few scrapes that happen to exist is not a share of W."""
    m, col = run["metrics"], "vllm:num_requests_waiting"
    if not len(m) or col not in m:
        return math.nan
    g = m[["t", col]].dropna()
    if not _covered(g.t.to_numpy(float), a, b, REG21["gauge_max_gap_s"]):
        return math.nan
    w = g[(g.t >= a) & (g.t < b)][col]
    return float((w > 0).mean()) if len(w) else math.nan


def reference(runs: list[dict] | None = None) -> dict:
    """U_off: U of each of REG-8's five saturated cache-off runs over its measured window (warm-up to the end of
    arrivals), with their mean, SD and spread, the mean without the lam = 2.0 run, and each run's own gauges. Raises
    unless exactly the five pinned runs are there and valid: a missing run or a second valid run at a rate would
    change the reference silently."""
    if runs is None:
        found = {r["dir"].name: r for r in find_runs(REG21["ref_pattern"])}
        missing = [i for i in REG21["ref_runs"] if i not in found]
        extra = [n for n in found if n not in REG21["ref_runs"]
                 and found[n]["cfg"]["workload"]["rate"] >= REG21["ref_min_rate"]]
        if missing or extra:
            raise ValueError(f"the reference needs exactly REG-8's five runs: missing {missing}, unexpected {extra}")
        runs = [found[i] for i in REG21["ref_runs"]]
    rows = {}
    for r in runs:
        a, b = float(r["cfg"]["workload"]["warmup_s"]), float(r["cfg"]["workload"]["duration_s"])
        u = work_rate(r, a, b)
        rows[r["dir"].name] = {"rate": float(r["cfg"]["workload"]["rate"]), "U": u}
        try:                                               # reported gauges never take the reference with them
            rows[r["dir"].name].update(U_by_end=work_rate(r, a, b, "t_end"), busy=busy_share(r, a, b), **_gauges(r, a, b, u))
        except Exception as e:
            rows[r["dir"].name]["gauges_error"] = f"{type(e).__name__}: {e}"[:200]
    v = np.array([x["U"] for x in rows.values()], float)
    hi = np.array([x["U"] for x in rows.values() if x["rate"] >= REG21["ref_alt_min_rate"]], float)
    return {"runs": rows, "n": len(v), "mean": float(v.mean()) if len(v) else math.nan,
            "sd": float(v.std(ddof=1)) if len(v) > 1 else math.nan,
            "spread": float(v.max() / v.min() - 1) if len(v) else math.nan,
            "mean_without_2.0": float(hi.mean()) if len(hi) else math.nan}


def _metric_mean(run: dict, col: str, a: float, b: float) -> float:
    m = run["metrics"]
    if not len(m) or col not in m:
        return math.nan
    w = m[(m.t >= a) & (m.t < b)]
    return float(w[col].mean()) if len(w) else math.nan


def _gauges(run: dict, a: float, b: float, u: float) -> dict:
    """Reported for a stuck run and for a reference run alike: the running batch, the waiting line, KV, preemptions per
    second, the mean prompt of the ok requests by first token, and the redo proxy, preemptions per second x mean
    prompt / U: the share of the counted work that preempted requests may have had to do a second time."""
    pre = k3.counter_rate(run, "vllm:num_preemptions_total", a, b)
    ok = _ok_in(run, a, b, "t_first_token")
    mp = float(ok.prompt_tokens.mean()) if len(ok) else math.nan
    return {"running": _metric_mean(run, "vllm:num_requests_running", a, b),
            "waiting": _metric_mean(run, "vllm:num_requests_waiting", a, b),
            "kv": _metric_mean(run, "vllm:kv_cache_usage_perc", a, b), "preempt_per_s": pre, "mean_prompt_all": mp,
            "redo_share": pre * mp / u if u and not math.isnan(u) else math.nan}


def readouts(run: dict) -> dict:
    """Everything reported for one run in W; nothing here is judged."""
    a, b = window(run)
    q = run["requests"]
    ok = _ok_in(run, a, b, "t_first_token")
    sess = ok[~is_burst_request(run).reindex(ok.index)]
    done = k3.completed(run, a, b)
    res = float((sess.t_end - sess.t_first_token).median()) if len(sess) else math.nan
    out = {"W": (a, b), "lam_W": k3.lam_w(run, a, b), "n_requests": int(len(ok)), "burst_in_W": int(len(ok) - len(sess)),
           "U_by_end": work_rate(run, a, b, "t_end"),
           "X_all": float(len(_ok_in(run, a, b, "t_end")) / (b - a)), "X_session": k3.x_obs(run, a, b),
           "mean_prompt": float(sess.prompt_tokens.mean()) if len(sess) else math.nan,
           "kbar": k3.kbar_obs(run, a, b), "turn0_share": float((done.turn == 0).mean()) if len(done) else math.nan,
           "d": k3.d_obs(run, a, b), "residence_s": res,
           **_gauges(run, a, b, work_rate(run, a, b)),
           "hl": k3.hl_rule(run), "shock": shock_size(run) if len(run["metrics"]) else None,
           "long_run": k3.long_run(k3.lam_w(run, a, b))}
    rep = {}
    for name, cost in REG21["costs"].items():      # model F on the run's schedule at the open-loop floor
        for label, dec in (("plain", 0.0), ("residence", res)):
            if math.isnan(dec):
                continue
            sim = modelf_sim.as_run(run["cfg"], modelf_sim.simulate(run["cfg"], REG21["mu_off"], cost, decode_s=dec))
            rep[f"{name}_{label}"] = {"kbar": k3.kbar_obs(sim, a, b), "X_session": k3.x_obs(sim, a, b),
                                      "d": k3.d_obs(sim, a, b), "U": work_rate(sim, a, b)}
    out["replay_at_floor"] = rep
    return out


def sessions_slope(run: dict, a: float, b: float) -> float:
    """Least-squares slope (sessions per second) over [a, b) of the sessions in the system: turn 0 planned by t and
    the last turn not ended by t. Valse and Jannesari's backlog, counted from the plan so that sessions still waiting
    to be sent count too."""
    q = run["requests"]
    q = q[~is_burst_request(run)]
    start = q[q.turn == 0].set_index("session_id").t_planned
    last = q[q.turn == REG21["turns"] - 1]
    end = last[last.status == "ok"].set_index("session_id").t_end.reindex(start.index)
    grid = np.arange(a, b + 1e-9, REG21["grid_s"])
    s, e = np.sort(start.to_numpy(float)), np.sort(end.dropna().to_numpy(float))
    n = np.searchsorted(s, grid, side="right") - np.searchsorted(e, grid, side="right")
    return float(np.polyfit(grid, n, 1)[0]) if len(grid) >= 2 else math.nan


def vj_rule(run: dict, r: float, a: float, b: float) -> dict:
    """Valse and Jannesari's registered trap rule read on one run (reported only): the uncached token rate within
    vj_token_tol of the all-miss rate, and the session backlog growing faster than vj_slope_frac of the excess of the
    planned session rate in W over the all-miss session capacity mu_off / turns."""
    lam_s = k3.lam_w(run, a, b) / REG21["turns"]
    slope, need = sessions_slope(run, a, b), REG21["vj_slope_frac"] * (lam_s - REG21["mu_off"] / REG21["turns"])
    need_cfg = REG21["vj_slope_frac"] * (float(run["cfg"]["workload"]["rate"]) - REG21["mu_off"]) / REG21["turns"]
    tok = None if math.isnan(r) else bool(abs(r - 1) <= REG21["vj_token_tol"] + EPS)
    return {"token_part": tok, "backlog_slope": slope, "slope_needed": need, "slope_needed_at_configured_rate": need_cfg,
            "slope_part": bool(slope > need), "trapped": bool(tok and slope > need)}


def _why(ru: float, busy: float, r: float, busy_min: float) -> str | None:
    """Why a run is not judged: every reason that applies, or None. A missing gauge is not called idleness."""
    why = []
    if math.isnan(ru):
        why.append("no later turn in W")
    elif ru > REG21["allmiss_reuse_max"]:
        why.append("not all-miss in W")
    if math.isnan(busy):
        why.append("no waiting gauge in W")
    elif busy < busy_min:
        why.append("idle in W")
    if not why and math.isnan(r):
        why.append("no work rate")
    return "; ".join(why) or None


def row(run: dict, ref: dict, with_readouts: bool = True) -> dict:
    """One run's judged values first; its reported readouts after, each failure of a readout kept as its message so
    that it cannot take the judged table with it."""
    a, b = window(run)
    ru, u, busy = reuse(run, a, b), work_rate(run, a, b), busy_share(run, a, b)
    u_off = ref["mean"]
    r = u / u_off if u_off and not math.isnan(u) else math.nan
    name = run["dir"].name
    out = {"run": name, "date": name[:8], "lam": float(run["cfg"]["workload"]["rate"]), "seed": run["cfg"].get("seed"),
           "reuse_W": ru, "allmiss": (not math.isnan(ru)) and ru <= REG21["allmiss_reuse_max"],
           "busy_W": busy, "busy": (not math.isnan(busy)) and busy >= REG21["busy_min"], "U": u, "r": r}
    out["why_not"] = _why(ru, busy, r, REG21["busy_min"])
    out["why_not_reported"] = _why(ru, busy, r, REG21["busy_min_reported"])
    alt = ref.get("mean_without_2.0", math.nan)
    out["r_without_2.0"] = u / alt if alt and not math.isnan(alt) and not math.isnan(u) else math.nan
    if with_readouts:
        for key, f in (("vj_rule", lambda: vj_rule(run, r, a, b)), ("readouts", lambda: readouts(run))):
            try:
                out[key] = f()
            except Exception as e:   # a reported readout never aborts the judged table
                out[key] = {"error": f"{type(e).__name__}: {e}"[:200]}
    return out


def _median(xs) -> float:
    xs = [x for x in xs if x is not None and not math.isnan(x)]
    return float(np.median(xs)) if xs else math.nan


def _level(med: float, n: int) -> tuple[str, str | None]:
    if n < REG21["min_runs"] or math.isnan(med):
        return "undefined", None
    if abs(med - 1) <= REG21["tol_level"] + EPS:
        return "inside", None
    return "outside", "high" if med > 1 else "low"


def judge(rows: list[dict], loads: bool = True, why: str = "why_not") -> dict:
    """J2, then J1. Rows left out are listed with the reason. A statement whose inputs are too few is "undefined",
    never rounded. With `loads` (batch 1): J1 pools the loads only if J2 is inside, and then only the runs of the
    groups J2 judged; otherwise it is given per load group and the pooled label is "not_pooled". Without it (batch 2,
    one load): J1 alone. `why` names the column holding the reason a run is left out (the reported second table uses
    the one computed at busy_min_reported)."""
    use = [r for r in rows if r[why] is None]
    left = [{"run": r["run"], "why": r[why]} for r in rows if r[why] is not None]
    out = {"n": len(use), "left_out": left, "per_run": {r["run"]: r["r"] for r in use}}
    groups: dict[str, list[dict]] = {}
    for r in use:
        groups.setdefault(f"{r['lam']:.1f}", []).append(r)
    out["groups"] = {}
    for g, v in sorted(groups.items()):
        lab, side = _level(_median([x["r"] for x in v]), len(v))
        out["groups"][g] = {"n": len(v), "median": _median([x["r"] for x in v]), "min": min(x["r"] for x in v),
                            "max": max(x["r"] for x in v),
                            "sd": float(np.std([x["r"] for x in v], ddof=1)) if len(v) > 1 else math.nan,
                            "dates": sorted({x["date"] for x in v}), "J1": lab, "J1_side": side}
    if len(use) >= 2 and len({r["lam"] for r in use}) >= 2:
        out["slope_r_per_reqs"] = float(np.polyfit([r["lam"] for r in use], [r["r"] for r in use], 1)[0])
    med = _median([r["r"] for r in use])
    if not loads:
        out["median_r"] = med
        out["J1"], out["J1_side"] = _level(med, len(use))
        return out
    meds = {g: v["median"] for g, v in out["groups"].items() if v["n"] >= REG21["min_group_runs"]}
    spread = max(meds.values()) - min(meds.values()) if len(meds) >= 2 else math.nan
    pool = [r for r in use if f"{r['lam']:.1f}" in meds]            # a group J2 did not judge is not pooled
    out.update(judged_groups=sorted(meds), spread=spread, pooled_n=len(pool),
               reported_not_pooled=[r["run"] for r in use if f"{r['lam']:.1f}" not in meds],
               all_judged_groups_inside=bool(meds) and all(out["groups"][g]["J1"] == "inside" for g in meds),
               J2="undefined" if math.isnan(spread) else ("inside" if spread <= REG21["tol_spread"] + EPS else "outside"))
    if out["J2"] == "inside":
        out["median_r"] = _median([r["r"] for r in pool])
        out["J1"], out["J1_side"] = _level(out["median_r"], len(pool))
    else:
        out["median_r"], out["J1"], out["J1_side"] = math.nan, "not_pooled", None
    return out


def select(runs: list[dict]) -> tuple[list[dict], list[dict]]:
    """(entered, left out): a run enters when `k1.cold_backlogged` holds in its own end window."""
    keep, out = [], []
    for r in runs:
        st = cold_backlogged(r)["cold_backlogged"]
        (keep if st else out).append(r if st else {"run": r["dir"].name, "cold_backlogged": st})
    return keep, out


def batch2_runs() -> list[dict]:
    """REG-19's burst runs, one valid run per seed, the seeds a prefix of REG-19's order. Raises before REG-19's
    [RESULT] is in decisions.md (the runs are sealed until then and the table would come out empty), on two valid
    runs of a seed, on a gap in the seeds, and on fewer than min_runs seeds."""
    if not withheld.lifted(REG21["batch2_heading"]):
        raise RuntimeError("REG-21 batch 2 is computed only after REG-19's [RESULT] is in docs/decisions.md")
    runs = find_runs(REG21["batch2_pattern"])
    by_seed: dict[int, list[dict]] = {}
    for r in runs:
        by_seed.setdefault(int(r["cfg"]["seed"]), []).append(r)
    dup = sorted(s for s, v in by_seed.items() if len(v) > 1)
    seeds = sorted(by_seed)
    if dup or tuple(seeds) != REG21["batch2_seeds"][:len(seeds)] or len(seeds) < REG21["min_runs"]:
        raise ValueError(f"batch 2 needs one valid burst run per seed, the seeds a prefix of {REG21['batch2_seeds']} "
                         f"and at least {REG21['min_runs']} of them (fewer would spend the one computation on an "
                         f"undefined table): found {seeds}, two valid runs for {dup}")
    return [by_seed[s][0] for s in seeds]


def batch1_runs() -> list[dict]:
    """The 13 registered runs, each valid. Raises if one is missing or invalid: a table on fewer would be another
    table than the one registered."""
    found = {i: find_runs(i) for i in REG21["batch1"]}
    missing = [i for i, v in found.items() if len(v) != 1]
    if missing:
        raise ValueError(f"batch 1 needs the {len(REG21['batch1'])} registered runs, each valid: not so for {missing}")
    return [found[i][0] for i in REG21["batch1"]]


def _judged(runs: list[dict], ref: dict, loads: bool) -> tuple[list[dict], list[dict], dict]:
    entered, left = select(runs)
    rows = [row(r, ref, with_readouts=False) for r in entered]
    return entered, left, judge(rows, loads=loads) | {"at_busy_min_reported": judge(rows, loads=loads, why="why_not_reported")}


def reg21_table(batch: int = 1) -> dict:
    """REG-21's table. Batch 1 once after the registration is approved; batch 2 once after REG-19's final [RESULT].
    The judged values are computed before any reported readout. Reported with batch 2: its median minus batch 1's
    median at the same load (the fixed-load contrast: the same load on other days and with another window)."""
    if batch not in (1, 2):
        raise ValueError("REG-21 has batch 1 and batch 2")
    runs = batch1_runs() if batch == 1 else batch2_runs()
    ref = reference()
    entered, left, judged = _judged(runs, ref, loads=(batch == 1))
    out = {"batch": batch, "not_cold_backlogged": left, "reference": ref, "judged": judged}
    if batch == 2:
        g = _judged(batch1_runs(), ref, loads=True)[2]["groups"].get(REG21["contrast_group"])
        b1 = g["median"] if g and g["n"] >= REG21["min_group_runs"] else math.nan
        b2 = judged["median_r"] if judged["J1"] != "undefined" else math.nan
        out["fixed_load_contrast"] = {"batch1_group": REG21["contrast_group"], "batch1_median": b1, "batch2_median": b2,
                                      "difference": b2 - b1}
    out["rows"] = [row(r, ref) for r in entered]
    return out


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "reg21":
        print(json.dumps(reg21_table(int(sys.argv[2]) if len(sys.argv) > 2 else 1), indent=1, default=str))
    else:
        raise SystemExit("usage: python -m analysis.k3w reg21 [1|2]")
