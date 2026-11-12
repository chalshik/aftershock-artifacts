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
of later turns <= allmiss_reuse_max) and busy (requests waiting in at least busy_min of the scrapes): an engine that
idles in part of W does less work for a reason that is not its capacity.

Judged (thresholds registered before r is computed on any run):
  J2  load (batch 1 only): max - min of the medians of r over the load groups with at least min_group_runs judged runs
      <= tol_spread
  J1  level: |median of r - 1| <= tol_level. The median pools loads only when J2 is inside (the pooling assumption is
      J2's statement, rule H); otherwise J1 is given per load group and the pooled label is "not_pooled".
r needs no model of the queue, of the turn mix or of how long a request stays in the running batch; the earlier
drafts' fitted capacities (analysis/k3.py: mu_k, mu_X) did, and are not computed.

Reported, never judged: U by t_end; r against the reference without its lam = 2.0 run; the slope of r on the load; per
group n, min, max, SD and the runs' dates; Valse and Jannesari's trap rule read per run (token part within 0.15, backlog
slope above half the excess); the request rates, the mean served prompt, the mean turn index and first-turn share,
sessions completed over started, the median time from first token to end, running batch, KV, waiting and preemptions
in W (and the same gauges for each reference run), Huang and Liu's rule, the burst's size, model F's long-run values,
and model F's replay on the run's own schedule at 1.681 with and without that residence.
"""
from __future__ import annotations

import math

import numpy as np

from analysis import k3, modelf_sim, withheld
from analysis.gate import burst_end, shock_size
from analysis.k1 import cold_backlogged, reuse
from analysis.load import find_runs
from analysis.margin import is_burst_request

REG21 = {
    "batch1": k3.REG21["batch1"],                       # the 13 closed-loop L1 burst runs at 350 W before REG-19
    "batch2_pattern": k3.REG21["batch2_pattern"],       # REG-19's burst runs, only after REG-19's [RESULT]
    "batch2_seeds": (15, 16, 17, 18, 19),               # in REG-19's run order; batch 2 is a prefix of them
    "batch2_heading": "[RESULT] REG-19",
    "offset_s": 600.0,                                  # W starts 600 s after the burst's end
    "allmiss_reuse_max": 0.05,                          # judged only if later turns reuse at most this in W
    "busy_min": 0.99,                                   # judged only if requests wait in at least this share of W's scrapes
    # REG-8's floor runs (lam_sat 2.0; decisions.md 2026-11-07 [RESULT] REG-8): exactly these five, each valid
    "ref_runs": ("20261107-083730_sweep_l1pl350_pc_off_r2", "20261107-085650_sweep_l1pl350_pc_off_r2.5",
                 "20261107-091752_sweep_l1pl350_pc_off_r3", "20261107-093854_sweep_l1pl350_pc_off_r3.5",
                 "20261107-095958_sweep_l1pl350_pc_off_r4"),
    "ref_pattern": "*_sweep_l1pl350_pc_off_r*",
    "mu_off": 1.681,                                    # req/s, the open-loop cache-off floor (REG-8)
    "turns": 8,
    "tol_level": 0.05,                                  # J1
    "tol_spread": 0.05,                                 # J2
    "min_runs": 3,                                      # J1 needs this many judged runs
    "min_group_runs": 3,                                # J2 uses a load group only with this many judged runs
    "vj_token_tol": 0.15, "vj_slope_frac": 0.5,         # Valse and Jannesari's trap rule (their Table 1), reported only
    "grid_s": 10.0,
    "costs": k3.REG21["costs"],
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
    """Share of the scrapes in [a, b) with at least one request waiting; NaN without scrapes."""
    m = run["metrics"]
    if not len(m) or "vllm:num_requests_waiting" not in m:
        return math.nan
    w = m[(m.t >= a) & (m.t < b)]["vllm:num_requests_waiting"].dropna()
    return float((w > 0).mean()) if len(w) else math.nan


def reference(runs: list[dict] | None = None) -> dict:
    """U_off: U of each of REG-8's five saturated cache-off runs over its measured window (warm-up to the end of
    arrivals), with their mean, SD and spread, the mean without the lam = 2.0 run, and each run's own gauges. Raises
    unless exactly the five pinned runs are there and valid: a missing run or a second valid run at a rate would
    change the reference silently."""
    if runs is None:
        found = {r["dir"].name: r for r in find_runs(REG21["ref_pattern"])}
        missing = [i for i in REG21["ref_runs"] if i not in found]
        extra = [n for n in found if n not in REG21["ref_runs"] and found[n]["cfg"]["workload"]["rate"] >= 2.0]
        if missing or extra:
            raise ValueError(f"the reference needs exactly REG-8's five runs: missing {missing}, unexpected {extra}")
        runs = [found[i] for i in REG21["ref_runs"]]
    rows = {}
    for r in runs:
        a, b = float(r["cfg"]["workload"]["warmup_s"]), float(r["cfg"]["workload"]["duration_s"])
        u = work_rate(r, a, b)
        pre = k3.counter_rate(r, "vllm:num_preemptions_total", a, b)
        ok = _ok_in(r, a, b, "t_first_token")
        mp = float(ok.prompt_tokens.mean()) if len(ok) else math.nan
        rows[r["dir"].name] = {"rate": float(r["cfg"]["workload"]["rate"]), "U": u, "U_by_end": work_rate(r, a, b, "t_end"),
                               "busy": busy_share(r, a, b), "running": _metric_mean(r, "vllm:num_requests_running", a, b),
                               "waiting": _metric_mean(r, "vllm:num_requests_waiting", a, b),
                               "kv": _metric_mean(r, "vllm:kv_cache_usage_perc", a, b), "preempt_per_s": pre,
                               "mean_prompt": mp, "redo_share": pre * mp / u if u else math.nan}
    v = np.array([x["U"] for x in rows.values()], float)
    hi = np.array([x["U"] for x in rows.values() if x["rate"] >= 2.5], float)
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
           "running": _metric_mean(run, "vllm:num_requests_running", a, b),
           "waiting": _metric_mean(run, "vllm:num_requests_waiting", a, b),
           "kv": _metric_mean(run, "vllm:kv_cache_usage_perc", a, b),
           "preempt_per_s": k3.counter_rate(run, "vllm:num_preemptions_total", a, b),
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
    tok = None if math.isnan(r) else bool(abs(r - 1) <= REG21["vj_token_tol"] + EPS)
    return {"token_part": tok, "backlog_slope": slope, "slope_needed": need, "slope_part": bool(slope > need),
            "trapped": bool(tok and slope > need)}


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
    out["why_not"] = (None if out["allmiss"] and out["busy"] and not math.isnan(r) else
                      "no later turn in W" if math.isnan(ru) else "not all-miss in W" if not out["allmiss"] else
                      "idle in W" if not out["busy"] else "no work rate")
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
    if n < REG21["min_runs"]:
        return "undefined", None
    if abs(med - 1) <= REG21["tol_level"] + EPS:
        return "inside", None
    return "outside", "high" if med > 1 else "low"


def judge(rows: list[dict], loads: bool = True) -> dict:
    """J2, then J1. Rows left out are listed with the reason. A statement whose inputs are too few is "undefined",
    never rounded. With `loads` (batch 1): J1 pools the loads only if J2 is inside; otherwise it is given per load group
    and the pooled label is "not_pooled". Without it (batch 2, one load): J1 alone."""
    use = [r for r in rows if r["why_not"] is None]
    left = [{"run": r["run"], "why": r["why_not"]} for r in rows if r["why_not"] is not None]
    out = {"n": len(use), "left_out": left, "per_run": {r["run"]: r["r"] for r in use}}
    groups: dict[str, list[dict]] = {}
    for r in use:
        groups.setdefault(f"{r['lam']:.1f}", []).append(r)
    out["groups"] = {g: {"n": len(v), "median": _median([x["r"] for x in v]), "min": min(x["r"] for x in v),
                         "max": max(x["r"] for x in v),
                         "sd": float(np.std([x["r"] for x in v], ddof=1)) if len(v) > 1 else math.nan,
                         "dates": sorted({x["date"] for x in v}),
                         "J1": _level(_median([x["r"] for x in v]), len(v))[0]} for g, v in sorted(groups.items())}
    if len(use) >= 2 and len({r["lam"] for r in use}) >= 2:
        out["slope_r_per_reqs"] = float(np.polyfit([r["lam"] for r in use], [r["r"] for r in use], 1)[0])
    med = _median([r["r"] for r in use])
    if not loads:
        out["median_r"] = med
        out["J1"], out["J1_side"] = _level(med, len(use))
        return out
    meds = {g: v["median"] for g, v in out["groups"].items() if v["n"] >= REG21["min_group_runs"]}
    spread = max(meds.values()) - min(meds.values()) if len(meds) >= 2 else math.nan
    out.update(judged_groups=sorted(meds), spread=spread,
               J2="undefined" if math.isnan(spread) else ("inside" if spread <= REG21["tol_spread"] + EPS else "outside"))
    if out["J2"] == "inside":
        out["median_r"] = med
        out["J1"], out["J1_side"] = _level(med, len(use))
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
    runs of a seed, and on a gap in the seeds."""
    if not withheld.lifted(REG21["batch2_heading"]):
        raise RuntimeError("REG-21 batch 2 is computed only after REG-19's [RESULT] is in docs/decisions.md")
    runs = find_runs(REG21["batch2_pattern"])
    by_seed: dict[int, list[dict]] = {}
    for r in runs:
        by_seed.setdefault(int(r["cfg"]["seed"]), []).append(r)
    dup = sorted(s for s, v in by_seed.items() if len(v) > 1)
    seeds = sorted(by_seed)
    if dup or tuple(seeds) != REG21["batch2_seeds"][:len(seeds)] or not seeds:
        raise ValueError(f"batch 2 needs one valid burst run per seed, the seeds a prefix of {REG21['batch2_seeds']}: "
                         f"found {seeds}, two valid runs for {dup}")
    return [by_seed[s][0] for s in seeds]


def reg21_table(batch: int = 1) -> dict:
    """REG-21's table. Batch 1 once after the registration is approved; batch 2 once after REG-19's [RESULT]."""
    if batch == 1:
        found = {r["dir"].name: r for r in find_runs("*_l1pl350cl_*")}
        missing = [i for i in REG21["batch1"] if i not in found]
        runs = [found[i] for i in REG21["batch1"] if i in found]
    else:
        runs, missing = batch2_runs(), []
    ref = reference()
    entered, left = select(runs)
    rows = [row(r, ref, with_readouts=False) for r in entered]
    judged = judge(rows, loads=(batch == 1))                      # judged before any reported readout is computed
    rows = [row(r, ref) for r in entered]
    return {"batch": batch, "missing_or_invalid": missing, "not_cold_backlogged": left, "reference": ref,
            "judged": judged, "rows": rows}


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "reg21":
        print(json.dumps(reg21_table(int(sys.argv[2]) if len(sys.argv) > 2 else 1), indent=1, default=str))
    else:
        raise SystemExit("usage: python -m analysis.k3w reg21 [1|2]")
