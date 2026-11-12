"""K3, step B, as registered: REG-21 (docs/decisions.md 2026-11-13 [REG]; docs/claims.md K3). Never writes into runs/.

Question: is the stuck (cold, backlogged) server the all-miss server? Model F (Valse and Jannesari, arXiv 2611.08902
§3; BELIEF as to the model) gives the trapped server one capacity, its all-miss capacity, whatever the load. In
tokens that is a statement with no queue in it: the stuck server prefills uncached prompt tokens at the rate of the
saturated cache-off server, at every load.

  U      uncached prompt tokens per second: Σ (prompt_tokens - cached_tokens) over ok requests, session and burst,
         whose first token falls in the window (the first token ends a request's prefill)
  U_off  the mean of U over REG-8's saturated cache-off runs (the runs at rate >= lam_sat = 2.0 that give the floor
         1.681 req/s), each over its measured window
  r      U over W / U_off, per stuck run; W = [burst end + 600 s, burst end + watch)

Judged (thresholds registered before r is computed on any run):
  J1  level:  |median of r over the all-miss runs - 1| <= tol_level
  J2  load:   max - min of the load groups' medians of r <= tol_spread   (batch 1 only; batch 2 has one load)
A run enters when `k1.cold_backlogged` holds in its own end window and it is all-miss in W (reuse of later turns in
W <= allmiss_reuse_max). r needs no model of the queue, of the turn mix or of how long a request stays in the
running batch; the earlier drafts' fitted capacities (analysis/k3.py: mu_k, mu_X) did, and are not computed.

Reported, never judged: U by t_end, the request rates, the mean served prompt, the mean turn index and first-turn
share, sessions completed over started, the median time from first token to end (the residence in the running
batch), running batch, KV, waiting and preemptions in W, Huang and Liu's rule, the burst's size, model F's long-run
values, and model F's replay on the run's own schedule at 1.681 with and without that residence.
"""
from __future__ import annotations

import math

import numpy as np

from analysis import k3, modelf_sim
from analysis.gate import burst_end, shock_size
from analysis.k1 import cold_backlogged, reuse
from analysis.load import find_runs
from analysis.margin import is_burst_request

REG21 = {
    "batch1": k3.REG21["batch1"],                       # the 13 closed-loop L1 burst runs at 350 W before REG-19
    "batch2_pattern": k3.REG21["batch2_pattern"],       # REG-19's burst runs, only after REG-19's [RESULT]
    "offset_s": 600.0,                                  # W starts 600 s after the burst's end
    "allmiss_reuse_max": 0.05,                          # a run is judged only if later turns reuse at most this in W
    "ref_pattern": "*_sweep_l1pl350_pc_off_r*", "ref_min_rate": 2.0,   # REG-8's floor runs (lam_sat 2.0)
    "mu_off": 1.681,                                    # req/s, the open-loop cache-off floor (REG-8)
    "tol_level": 0.05,                                  # J1
    "tol_spread": 0.05,                                 # J2
    "min_runs": 3,                                      # J1 needs this many all-miss runs
    "min_group_runs": 2,                                # J2 uses a load group only with this many all-miss runs
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
    w = _ok_in(run, a, b, by)
    if not len(w):
        return math.nan
    cached = w.cached_tokens.fillna(0) if "cached_tokens" in w else 0
    return float((w.prompt_tokens - cached).clip(lower=0).sum() / (b - a))


def reference() -> dict:
    """U_off: U of each REG-8 saturated cache-off run over its measured window (warm-up to the end of arrivals), with
    their mean, SD and the spread max/min - 1."""
    runs = [r for r in find_runs(REG21["ref_pattern"]) if r["cfg"]["workload"]["rate"] >= REG21["ref_min_rate"]]
    vals = {r["dir"].name: work_rate(r, r["cfg"]["workload"]["warmup_s"], r["cfg"]["workload"]["duration_s"])
            for r in runs}
    v = np.array(list(vals.values()), float)
    return {"runs": vals, "n": len(v), "mean": float(v.mean()) if len(v) else math.nan,
            "sd": float(v.std(ddof=1)) if len(v) > 1 else math.nan,
            "spread": float(v.max() / v.min() - 1) if len(v) else math.nan}


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


def row(run: dict, u_off: float, with_readouts: bool = True) -> dict:
    a, b = window(run)
    ru, u = reuse(run, a, b), work_rate(run, a, b)
    r = {"run": run["dir"].name, "lam": float(run["cfg"]["workload"]["rate"]), "seed": run["cfg"].get("seed"),
         "reuse_W": ru, "allmiss": (not math.isnan(ru)) and ru <= REG21["allmiss_reuse_max"],
         "U": u, "r": u / u_off if u_off and not math.isnan(u) else math.nan}
    if with_readouts:
        r["readouts"] = readouts(run)
    return r


def _median(xs) -> float:
    xs = [x for x in xs if x is not None and not math.isnan(x)]
    return float(np.median(xs)) if xs else math.nan


def judge(rows: list[dict], loads: bool = True) -> dict:
    """J1 and J2 on the all-miss rows. Rows left out are listed with the reason. A statement whose inputs are too few
    is "undefined", never rounded to inside or outside."""
    use = [r for r in rows if r["allmiss"] and not math.isnan(r["r"])]
    left = [{"run": r["run"], "why": "not all-miss in W" if not r["allmiss"] else "no work rate"}
            for r in rows if r not in use]
    med = _median([r["r"] for r in use])
    j1 = "undefined" if len(use) < REG21["min_runs"] else ("inside" if abs(med - 1) <= REG21["tol_level"] + EPS else "outside")
    out = {"n": len(use), "left_out": left, "median_r": med, "J1": j1,
           "J1_side": None if j1 != "outside" else ("high" if med > 1 else "low"),
           "per_run": {r["run"]: r["r"] for r in use}}
    if loads:
        groups: dict[str, list[float]] = {}
        for r in use:
            groups.setdefault(f"{r['lam']:.1f}", []).append(r["r"])
        meds = {g: _median(v) for g, v in groups.items() if len(v) >= REG21["min_group_runs"]}
        spread = max(meds.values()) - min(meds.values()) if len(meds) >= 2 else math.nan
        out.update(group_n={g: len(v) for g, v in groups.items()}, group_medians=meds, spread=spread,
                   J2="undefined" if math.isnan(spread) else ("inside" if spread <= REG21["tol_spread"] + EPS else "outside"))
    return out


def select(runs: list[dict]) -> tuple[list[dict], list[dict]]:
    """(entered, left out): a run enters when `k1.cold_backlogged` holds in its own end window."""
    keep, out = [], []
    for r in runs:
        st = cold_backlogged(r)["cold_backlogged"]
        (keep if st else out).append(r if st else {"run": r["dir"].name, "cold_backlogged": st})
    return keep, out


def reg21_table(batch: int = 1) -> dict:
    """REG-21's table. Batch 1 once after the registration is approved; batch 2 once after REG-19's [RESULT]."""
    if batch == 1:
        found = {r["dir"].name: r for r in find_runs("*_l1pl350cl_*")}
        missing = [i for i in REG21["batch1"] if i not in found]
        runs = [found[i] for i in REG21["batch1"] if i in found]
    else:
        runs, missing = [r for r in find_runs(REG21["batch2_pattern"])], []
    ref = reference()
    entered, left = select(runs)
    rows = [row(r, ref["mean"]) for r in entered]
    return {"batch": batch, "missing_or_invalid": missing, "not_cold_backlogged": left, "reference": ref,
            "rows": rows, "judged": judge(rows, loads=(batch == 1))}


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "reg21":
        print(json.dumps(reg21_table(int(sys.argv[2]) if len(sys.argv) > 2 else 1), indent=1, default=str))
    else:
        raise SystemExit("usage: python -m analysis.k3w reg21 [1|2]")
