"""Feasibility gate for setup L1 (registration REG-7, docs/decisions.md 2026-11-05; docs/process.md §4; docs/model.md M2).
Never writes into runs/.

A stuck state at λ needs the cold, backlogged completion rate below λ while the warm server keeps up at λ:
c_b(λ) < λ <= c_warm(λ). The gate is decided by functions here, from committed code only:
  1. `cold_floor`: μ_sat,off, the cache-off completion rate of a sweep once it is saturated.
  2. `zone_check` (+ `slo_feasible`): the one test load λ_test, chosen by a fixed rule, or None.
  3. `gate_verdict`: on a control and a burst run at λ_test with the same seed and duration.
Every threshold is an argument; the registered values are in REG7. The rules were tightened after REG-7's adversarial
review, before any L1 run existed (decisions.md 2026-11-05 [REG] REG-7).
"""
import math

import numpy as np
import pandas as pd

from analysis.derived import _later_turns
from analysis.floor import sustained_capacity
from analysis.load import _level, verdict
from analysis.margin import is_burst_request, post_trigger_margin


# ---------------------------------------------------------------- 1. cold floor

def cold_floor(sweep: pd.DataFrame, min_kv: float, min_runs: int, sat_frac: float) -> dict:
    """μ_sat,off over a cache-off sweep's valid rows (columns rate, throughput, planned_rate, kv_mean).
    Rows with a non-finite value are dropped first. λ_sat is the lowest rate whose mean KV is >= min_kv. Every row at
    λ >= λ_sat must be *saturated*: KV >= min_kv and throughput < sat_frac x planned_rate (it fell behind its load);
    otherwise the floor is undefined (`status` "not_monotone"), never averaged over rows that still kept up.
    μ_sat,off = mean throughput of those rows; undefined with fewer than min_runs rows ("too_few") or no saturated
    row ("unsaturated": the grid did not reach the floor, so the floor is unmeasured, not absent)."""
    s = sweep[np.isfinite(sweep[["rate", "throughput", "planned_rate", "kv_mean"]]).all(axis=1)].sort_values("rate")
    if s.rate.duplicated().any():
        raise ValueError("two valid runs at one rate; the registration says which counts")
    out = {"mu_sat_off": math.nan, "lam_sat": math.nan, "n": 0}
    sat = s[s.kv_mean >= min_kv]
    if not len(sat):
        return {**out, "status": "unsaturated"}
    lam_sat = float(sat.rate.min())
    rows = s[s.rate >= lam_sat]
    out.update(lam_sat=lam_sat, n=len(rows))
    if not ((rows.kv_mean >= min_kv) & (rows.throughput < sat_frac * rows.planned_rate)).all():
        return {**out, "status": "not_monotone"}
    if len(rows) < min_runs:
        return {**out, "status": "too_few"}
    return {**out, "mu_sat_off": float(rows.throughput.mean()), "status": "ok"}


# ---------------------------------------------------------------- 2. test load

def zone_check(mu_warm: float, mu_sat_off: float, warm_frac: float, floor_mult: float, step: float) -> float | None:
    """λ_test: the largest multiple of `step` that is <= warm_frac x μ_warm and >= floor_mult x μ_sat,off.
    None if μ_warm or μ_sat,off is undefined, or no grid value fits."""
    if not (np.isfinite(mu_warm) and np.isfinite(mu_sat_off)):
        return None
    lam = math.floor(warm_frac * mu_warm / step + 1e-9) * step
    return float(lam) if lam > 0 and lam >= floor_mult * mu_sat_off - 1e-9 else None


def slo_feasible(sweep_on: pd.DataFrame, lam: float, min_pf: float) -> bool:
    """The cache-on sweep run at the smallest swept rate >= λ met the SLO in its measured window: pooled percent fast
    (`load._level` pf over [warm-up, end of arrivals)) >= min_pf. Columns: rate, pf. False if no such run."""
    rows = sweep_on[sweep_on.rate >= lam - 1e-9].sort_values("rate")
    return bool(len(rows) and np.isfinite(rows.pf.iloc[0]) and rows.pf.iloc[0] >= min_pf)


def choose_lambda(mu_warm: float, mu_sat_off: float, sweep_on: pd.DataFrame, c: dict) -> float | None:
    """`zone_check`, then step down by `step` until `slo_feasible` holds, staying >= floor_mult x μ_sat,off."""
    lam = zone_check(mu_warm, mu_sat_off, c["warm_frac"], c["floor_mult"], c["step"])
    while lam is not None and not slo_feasible(sweep_on, lam, c["min_pf"]):
        lam = lam - c["step"]
        if lam <= 0 or lam < c["floor_mult"] * mu_sat_off - 1e-9:
            return None
    return lam


# ---------------------------------------------------------------- 3. gate runs

def planned_session_rate(run: dict, a: float, b: float) -> float:
    """Planned session requests per second in [a, b) (burst requests left out), from the run's own requests."""
    r = run["requests"]
    s = r[~is_burst_request(run)]
    return float(((s.t_planned >= a) & (s.t_planned < b)).sum() / (b - a))


def burst_end(run: dict) -> float:
    return float(run["cfg"]["trigger"]["at_s"] + run["cfg"]["trigger"]["duration_s"])


def burst_backlog(run: dict, spans: list[tuple[float, float]], baseline_s: float, cold_hit_drop: float, conf: float) -> list[dict]:
    """`margin.post_trigger_margin` per span after the burst's end. A span `holds` when it qualifies (waiting > 0 at
    every scrape, burst-free, sessions' own cached share <= baseline - cold_hit_drop) and even the upper bound of its
    completion rate is below BOTH the configured λ and the span's planned session rate λp. Comparing with λp alone
    let a slowly draining backlog pass during a local rise of the schedule (REG-7 review, trace A)."""
    end = burst_end(run)
    rows = post_trigger_margin(run, spans, baseline_s, cold_hit_drop, conf)
    for row in rows:
        a, b = row["span"]
        row["lam_p"] = planned_session_rate(run, end + a, end + b)
        row["defined"] = bool(np.isfinite(row["share"]) and np.isfinite(row["share_base"]) and np.isfinite(row["q_min"]))
        row["holds"] = bool(row["qualifies"] and row["c_upper"] < min(row["lam"], row["lam_p"]))
    return rows


def control_backlog(control: dict, abs_spans: list[tuple[float, float]], max_gap_s: float) -> list[dict]:
    """The control at the burst run's absolute spans: waiting > 0 at every scrape (`backlogged`), and its waiting mean.
    A control backlogged where the burst run holds means the schedule, not the burst, made that backlog (review, B)."""
    m = control["metrics"]
    out = []
    for lo, hi in abs_spans:
        q = m["vllm:num_requests_waiting"][(m.t >= lo) & (m.t < hi)]
        lv = _level(control, lo, hi)
        defined = bool(len(q) and q.notna().all() and np.isfinite(lv["q"]))
        out.append({"span": (lo, hi), "q": lv["q"], "defined": defined, "backlogged": bool(defined and q.min() > 0)})
    return out


def gate_verdict(control: dict, burst: dict, spans: list[tuple[float, float]], baseline_s: float, cold_hit_drop: float,
                 conf: float) -> dict:
    """REG-7 gate on one control and one burst run at λ_test (same seed and duration, so the same session schedule;
    the control is judged with `control_t_s` at the burst's end, so both watches end at the end of arrivals).
    - inconclusive: an instrument gap: the control or the burst verdict is `unclear`, the burst run is `bad_baseline`,
      or a span needed for the decision is undefined. Rerun under the stopping rule; never read as `drains`.
    - control_not_healthy: the control is `bad_baseline`, `slow_drain` or `stuck` (anything defined but `recovered`).
    - pass: some span holds in the burst run, and the control is not backlogged at that same span.
    - inconclusive also: the burst verdict is `stuck` but no span counts (the span test could not confirm it).
    - drains: otherwise.
    Both runs must be valid; invalid or unmatched runs raise."""
    for run in (control, burst):
        if not (run["checks"] and run["checks"]["valid"]):
            raise ValueError(f"{run['dir'].name} is not valid")
    cc, bc = control["cfg"], burst["cfg"]
    if cc["seed"] != bc["seed"] or cc["workload"]["duration_s"] != bc["workload"]["duration_s"]:
        raise ValueError("control and burst run must share seed and duration, so their session schedules match")
    if float(cc["verdict"]["control_t_s"]) != burst_end(burst):
        raise ValueError("the control must be judged at the burst's end (control_t_s), so both watches end together")
    vc, vb = verdict(control)["verdict"], verdict(burst)["verdict"]
    rows = burst_backlog(burst, spans, baseline_s, cold_hit_drop, conf)
    end = burst_end(burst)
    ctrl = control_backlog(control, [(end + a, end + b) for a, b in spans], cc["checks"]["max_scrape_gap_s"])
    for row, cr in zip(rows, ctrl):
        row["control_backlogged"], row["control_defined"] = cr["backlogged"], cr["defined"]
        row["counts"] = row["holds"] and cr["defined"] and not cr["backlogged"]
    res = {"control_verdict": vc, "burst_verdict": vb, "spans": rows}
    if vc == "unclear" or vb in ("unclear", "bad_baseline"):
        return {"label": "inconclusive", **res}
    if vc != "recovered":
        return {"label": "control_not_healthy", **res}
    if any(r["counts"] for r in rows):
        return {"label": "pass", **res}
    # `stuck` by the verdict but unconfirmed by a span (e.g. burst requests still completing in every span, so none is
    # burst-free): the span test could not measure, so it is not read as a drain (pre-commit review, 2026-11-05).
    if vb == "stuck" or any(r["holds"] and not r["control_defined"] for r in rows) or not all(r["defined"] for r in rows):
        return {"label": "inconclusive", **res}
    return {"label": "drains", **res}


# ---------------------------------------------------------------- readouts (reported, never decisive except overlap)

def overlap_share(run: dict, a: float, b: float) -> float:
    """Share of the session cache hits in [a, b) (by first token) that came from a previous turn still running:
    Σ cached_tokens over ok later turns whose first token came before the previous turn's end, divided by Σ cached_tokens
    over all ok later turns. NaN if there are no cached tokens. Decides REG-7's closed-loop proposal under `drains`."""
    q = _later_turns(run)
    q = q[(q.status == "ok") & (q.t_first_token >= a) & (q.t_first_token < b)]  # later turns: never burst rows (turn 0)
    tot = q.cached_tokens.sum()
    return float(q.cached_tokens[q.t_first_token < q.prev_end].sum() / tot) if tot else math.nan


def secondary_cb(run: dict, max_gap_s: float) -> dict:
    """`floor.sustained_capacity` from the burst's end to the end of arrivals, with REG-6's stretch settings."""
    return sustained_capacity(run, burst_end(run), float(run["cfg"]["workload"]["duration_s"]), REG7["cb_min_waiting"],
                              REG7["cb_min_stretch_s"], REG7["cb_min_backlog_s"], REG7["cb_margin"], max_gap_s)


# REG-7 (docs/decisions.md 2026-11-05): registered values. Not to be changed after approval.
REG7 = {
    "sweep_on": "sweep_l1_pc_on", "sweep_off": "sweep_l1_pc_off",
    "floor_min_kv": 0.85, "floor_min_runs": 2, "sat_frac": 0.95,   # KV threshold: owner, decisions.md 2026-11-04
    "warm_frac": 0.8, "floor_mult": 1.3, "step": 0.5, "min_pf": 0.98, "slo_ttft_s": 1.0,   # SLO: configs/stage2_base.yaml
    "spans": [(600, 900), (900, 1200), (1200, 1500)],       # seconds after the burst's last planned arrival
    "baseline_s": 600, "cold_hit_drop": 0.06, "conf": 0.99,
    "overlap_limit": 0.5,
    "cb_min_waiting": 1.0, "cb_min_stretch_s": 30, "cb_min_backlog_s": 300, "cb_margin": 0.05,   # REG-6's settings
}


def sweep_rows(parent: str, slo_ttft_s: float | None = None) -> pd.DataFrame:
    """Valid runs of one sweep that have metrics: rate, throughput and planned_rate (`load.summarize`), mean KV over the
    measured window, and pooled percent fast over it (`load._level` pf) at `slo_ttft_s` (sweeps carry no SLO of
    their own; NaN without one)."""
    from analysis.load import find_runs, rates, summarize, window
    rows = []
    for r in find_runs("*"):
        if r["cfg"].get("sweep_parent") != parent or not len(r["metrics"]):
            continue
        s, wl = summarize(r), r["cfg"]["workload"]
        m = window(rates(r["metrics"]), r["cfg"])
        pf = math.nan
        if slo_ttft_s is not None:
            r["cfg"] = {**r["cfg"], "slo": {**r["cfg"]["slo"], "ttft_s": slo_ttft_s}}
            pf = _level(r, wl["warmup_s"], wl["duration_s"])["pf"]
        rows.append({"run": r["dir"].name, "rate": wl["rate"], "throughput": s["throughput"], "planned_rate": s["planned_rate"],
                     "kv_mean": float(m.kv_cache_usage_perc.mean()), "pf": pf})
    return pd.DataFrame(rows, columns=["run", "rate", "throughput", "planned_rate", "kv_mean", "pf"])


def reg7_zone() -> dict:
    """Parts 1-2 on the L1 sweeps: μ_warm (the rule in their configs), μ_sat,off, λ_test (with the SLO check)."""
    from analysis.tables import sweep_capacity
    on = sweep_rows(REG7["sweep_on"], REG7["slo_ttft_s"])
    mu_warm = sweep_capacity(REG7["sweep_on"])
    floor = cold_floor(sweep_rows(REG7["sweep_off"]), REG7["floor_min_kv"], REG7["floor_min_runs"], REG7["sat_frac"])
    return {"mu_warm": mu_warm, "mu_off": sweep_capacity(REG7["sweep_off"]), **floor,
            "lam_test": choose_lambda(mu_warm, floor["mu_sat_off"], on, REG7)}


if __name__ == "__main__":
    print(reg7_zone())
