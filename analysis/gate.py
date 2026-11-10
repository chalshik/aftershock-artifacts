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
from pathlib import Path

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
    num = {k: float for k in ("rate", "throughput", "planned_rate", "kv_mean", "pf")}   # typed even with no rows
    return pd.DataFrame(rows, columns=["run", *num]).astype(num)


# REG-8 (docs/decisions.md 2026-11-06): REG-7 repeated at a 350 W power limit. Every value is REG-7's; only the sweeps
# differ. Not to be changed after approval.
REG8 = {**REG7, "sweep_on": "sweep_l1pl350_pc_on", "sweep_off": "sweep_l1pl350_pc_off",
        "power_limit_w": 350, "g1a_top": 5.0}   # the cap, and the top rate of G1' part a


def zone(reg: dict) -> dict:
    """Parts 1-2 on one pair of sweeps: μ_warm (the rule in their configs), μ_sat,off, λ_test (with the SLO check)."""
    from analysis.tables import sweep_capacity
    on = sweep_rows(reg["sweep_on"], reg["slo_ttft_s"])
    mu_warm = sweep_capacity(reg["sweep_on"])
    floor = cold_floor(sweep_rows(reg["sweep_off"]), reg["floor_min_kv"], reg["floor_min_runs"], reg["sat_frac"])
    return {"mu_warm": mu_warm, "mu_off": sweep_capacity(reg["sweep_off"]), **floor,
            "lam_test": choose_lambda(mu_warm, floor["mu_sat_off"], on, reg)}


def reg7_zone() -> dict:
    """REG-7's gate, parts 1-2, on the 420 W L1 sweeps."""
    return zone(REG7)


def reg8_zone() -> dict:
    """REG-8's gate, parts 1-2, on the 350 W L1 sweeps."""
    return zone(REG8)


# REG-8's stopping rules, as functions (after its adversarial review). They read validity, GPU throttle bits, the cold
# floor (G2' only) and the capacity chain, never a verdict or a burst outcome.
HW_THERMAL_BIT = 0x40     # NVML HW thermal slowdown


def reg8_part_a(run: dict) -> str:
    """Outcome of G2' part a (λ = 1, the heat test): `valid`; `heat` (the limit held, and the SW-thermal share is over
    the run's own limit or a sample carries the HW-thermal bit); `rerun` (any other failure, including `power_limit`:
    a run whose limit did not hold says nothing about heat at 350 W)."""
    ch = run["checks"]
    if ch is None:
        return "rerun"
    if ch["valid"]:
        return "valid"
    by = {c["name"]: c for c in ch["checks"]}
    if "power_limit" not in by or not by["power_limit"]["passed"]:
        return "rerun"
    g, c, wl = by.get("gpu_steady"), run["cfg"]["checks"], run["cfg"]["workload"]
    if g is None or g["passed"] or not isinstance(g["detail"], dict):
        return "rerun"
    gpu = pd.read_json(run["dir"] / "gpu.jsonl", lines=True)
    w = gpu[(gpu.t >= wl["warmup_s"]) & (gpu.t <= wl["duration_s"])]
    hw_thermal = bool(((w.throttle_reasons.astype(int) & HW_THERMAL_BIT) != 0).any())
    return "heat" if g["detail"]["sw_thermal_frac"] > c["max_sw_thermal_frac"] or hw_thermal else "rerun"


def reg8_g1_may_start() -> dict:
    """G1' starts only if G2' gives a cold floor with status `ok`; otherwise no λ_test is possible whatever G1' shows."""
    r = REG8
    return cold_floor(sweep_rows(r["sweep_off"]), r["floor_min_kv"], r["floor_min_runs"], r["sat_frac"])


def reg8_g1b_may_start() -> bool:
    """G1' part b (λ = 5.5, 6, 7) starts only if every part-a rate (2-5) has a valid run that passes the capacity rule,
    i.e. the monotone μ_warm over the rates swept so far is 5. Otherwise the chain has ended and b cannot change μ."""
    from analysis.tables import sweep_capacity
    return sweep_capacity(REG8["sweep_on"]) == REG8["g1a_top"]


def reg8_gate_verdict(control: dict, burst: dict) -> dict:
    """`gate_verdict` with REG-8's settings, after checking that both runs are 350 W L1 runs at the same λ."""
    for run in (control, burst):
        if run["cfg"]["checks"].get("expected_power_limit_w") != REG8["power_limit_w"]:
            raise ValueError(f"{run['dir'].name} is not a {REG8['power_limit_w']} W run")
    if control["cfg"]["workload"]["rate"] != burst["cfg"]["workload"]["rate"]:
        raise ValueError("control and burst run must have the same λ")
    return gate_verdict(control, burst, REG8["spans"], REG8["baseline_s"], REG8["cold_hit_drop"], REG8["conf"])


# REG-10 (decisions.md 2026-11-08): an exploratory G3′ pair at L1, 350 W, chosen after REG-8's data. Judged as REG-8's
# G3′. λ = 2.4 = REG-8's 0.8 μ_warm margin itself, with no grid step (owner's choice, 2026-11-08); it is ≥ 1.3 μ_sat,off.
REG10 = {"lam": 2.4, "force_close": True}   # force_close: amendment, decisions.md 2026-11-09
REG10["control"] = f"*_stage2_control_l1pl350_r{REG10['lam']:g}"
REG10["burst"] = f"*_burst_l1pl350_r{REG10['lam']:g}_s1"


def queued_miss_share(run: dict, spans: list[tuple[float, float]]) -> list[float]:
    """REG-10 readout, never decisive: per span after the burst's end, the share of ok later session turns (by first
    token) with no cached tokens whose previous turn had no first token yet at this turn's planned arrival. Such a turn
    misses even with an unlimited cache: open-loop queueing, not eviction (REG-10 review). NaN if no cold turn."""
    q = _later_turns(run)
    end, out = burst_end(run), []
    for a, b in spans:
        w = q[(q.status == "ok") & (q.t_first_token >= end + a) & (q.t_first_token < end + b) & (q.cached_tokens == 0)]
        due = w.t_released.fillna(w.t_planned).astype(float) if "t_released" in w else w.t_planned  # REG-11 review, T4
        out.append(float((w.prev_first.isna() | (w.prev_first > due)).mean()) if len(w) else math.nan)
    return out


def span_clock(run: dict, spans: list[tuple[float, float]], baseline_s: float) -> dict:
    """REG-10 readout, never decisive: median busy SM clock (util >= the run's gpu_busy_util_pct) in the baseline
    before the burst and in each span after it, to see a clock drift from heat."""
    g, c, end = run["gpu"], run["cfg"]["checks"], burst_end(run)
    busy = g[g.util_pct >= c["gpu_busy_util_pct"]]
    med = lambda a, b: float(busy[(busy.t >= a) & (busy.t < b)].sm_clock_mhz.median())
    start = float(run["cfg"]["trigger"]["at_s"])
    return {"baseline": med(start - baseline_s, start), "spans": [med(end + a, end + b) for a, b in spans]}


def reg10_pick(runs: list[dict]) -> dict:
    """The run that counts: the latest valid one by run id (a rerun is launched only after the earlier run was invalid
    or, in REG-10 and REG-11 only, its pair `inconclusive`, so the latest is the one the stopping rule allows). REG-12
    has no rerun on a verdict and pins one valid run per pattern (`reg12_only`). Raises if there is none."""
    if not runs:
        raise ValueError("no valid run")
    return sorted(runs, key=lambda r: r["dir"].name)[-1]


def release_delay(run: dict, spans: list[tuple[float, float]], end: float | None = None) -> list[float]:
    """REG-11 readout (closed-loop turns), never decisive: per span after the burst's end, the median of t_released -
    t_planned over later session turns released in the span: how far the sessions have fallen behind their schedule.
    NaN for an open-loop run or a span with no release."""
    q, out = run["requests"], []
    end = burst_end(run) if end is None else end
    if "t_released" not in q:
        return [math.nan for _ in spans]
    q = q[(q.turn > 0) & q.t_released.notna()]
    rel = q.t_released.astype(float)
    for a, b in spans:
        w = q[(rel >= end + a) & (rel < end + b)]
        out.append(float((w.t_released.astype(float) - w.t_planned).median()) if len(w) else math.nan)
    return out


def release_delay_baseline(run: dict, baseline_s: float) -> float:
    """release_delay over the baseline before the burst (REG-11 review, recommendation 6): the drift of a healthy
    closed loop, the reference for the post-burst values."""
    start = float(run["cfg"]["trigger"]["at_s"])
    return release_delay(run, [(start - baseline_s, start)], end=0.0)[0]


def shock_size(run: dict) -> dict:
    """REG-11 readout (review, recommendation 1): how big the post-burst session backlog was. `outstanding`: session
    requests (no burst rows) due by the burst's end (t_released, else t_planned) and not ended by then; `backlog_s`:
    backlogged time from the burst's end to the end of arrivals (`secondary_cb`'s stretches)."""
    q, end = run["requests"], burst_end(run)
    s = q[~is_burst_request(run)]
    due = s.t_released.fillna(s.t_planned).astype(float) if "t_released" in s else s.t_planned
    out = int(((due <= end) & (s.t_end.isna() | (s.t_end > end))).sum())
    return {"outstanding": out, "backlog_s": secondary_cb(run, run["cfg"]["checks"]["max_scrape_gap_s"])["backlog_s"]}


def turn0_share(run: dict, spans: list[tuple[float, float]]) -> list[float]:
    """REG-11 readout (review, recommendation 7): per span after the burst's end, the share of first turns among the
    session completions (by t_end). Closed loop can change the queue mix; first turns carry no session prefix."""
    q, end, out = run["requests"], burst_end(run), []
    s = q[~is_burst_request(run) & (q.status == "ok")]
    for a, b in spans:
        w = s[(s.t_end >= end + a) & (s.t_end < end + b)]
        out.append(float((w.turn == 0).mean()) if len(w) else math.nan)
    return out


def unreleased(run: dict, spans: list[tuple[float, float]]) -> list[int]:
    """REG-11 readout (review, recommendation 4): per span after the burst's end, later session turns planned in the
    span that were never sent. They count as misses in percent fast, which is binned by t_planned."""
    q, end = run["requests"], burst_end(run)
    s = q[~is_burst_request(run) & (q.turn > 0) & q.t_sent.isna()]
    return [int(((s.t_planned >= end + a) & (s.t_planned < end + b)).sum()) for a, b in spans]


def closed_loop(run: dict) -> bool:
    return bool((run["cfg"]["workload"].get("sessions") or {}).get("closed_loop"))


def reg10_gate(spec: dict | None = None) -> dict:
    """REG-10's verdict: the latest valid control and burst run at REG10's λ, judged by `reg8_gate_verdict`. The label
    `inconclusive` is split: `stuck_unconfirmed` if the burst verdict is `stuck` and the control `recovered` (the span
    test could not confirm; not rerun, the owner decides), otherwise `inconclusive` (an instrument gap; rerun).
    Readouts, never decisive except overlap under `drains`: overlap_share, secondary_cb, queued_miss_share, span_clock."""
    from analysis.load import find_runs
    spec = spec or REG10
    pair = []
    for key in ("control", "burst"):
        runs = find_runs(spec[key])  # valid runs only
        r = reg10_pick(runs)
        if r["cfg"]["workload"]["rate"] != spec["lam"]:
            raise ValueError(f"{r['dir'].name} is not at λ = {spec['lam']}")
        if r["cfg"].get("loadgen_force_close") is not spec["force_close"]:  # amendment review, trace A
            raise ValueError(f"{r['dir'].name} is not a run with a new connection per request")
        if closed_loop(r) is not spec.get("closed_loop", False):  # REG-11: the pair must be in the registered mode
            raise ValueError(f"{r['dir'].name}: closed_loop is not {spec.get('closed_loop', False)}")
        pair.append(r)
    control, burst = pair
    res = reg8_gate_verdict(control, burst)
    res["outcome"] = ("stuck_unconfirmed" if res["label"] == "inconclusive" and res["burst_verdict"] == "stuck"
                      and res["control_verdict"] == "recovered" else res["label"])
    end = burst_end(burst)
    res["overlap_share"] = overlap_share(burst, end, burst["cfg"]["workload"]["duration_s"])
    res["secondary_cb"] = secondary_cb(burst, burst["cfg"]["checks"]["max_scrape_gap_s"])
    res["queued_miss_share"] = queued_miss_share(burst, REG8["spans"])
    res["span_clock"] = span_clock(burst, REG8["spans"], REG8["baseline_s"])
    if spec.get("closed_loop"):
        res["release_delay"] = release_delay(burst, REG8["spans"])
        res["release_delay_baseline"] = release_delay_baseline(burst, REG8["baseline_s"])
        res["shock_size"] = shock_size(burst)
        res["turn0_share"] = turn0_share(burst, REG8["spans"])
        res["unreleased"] = unreleased(burst, REG8["spans"])
    res["runs"] = [control["dir"].name, burst["dir"].name]
    return res


# REG-11 draft (docs/decisions.md 2026-11-09 [REG]): REG-10's pair with closed-loop turns, the only change.
REG11 = {**REG10, "closed_loop": True}
REG11["control"] = f"*_stage2_control_l1pl350cl_r{REG11['lam']:g}"
REG11["burst"] = f"*_burst_l1pl350cl_r{REG11['lam']:g}_s1"


REG11["comparable_frac"] = 0.5   # registered before REG-10's reference was computed (REG-11 review, recommendation 1)
REG11["reference_run"] = "20261108-220248_burst_l1pl350_r2.4_s1"


def reg11_reference() -> dict:
    """REG-10's burst run's shock size, the reference for REG-11's reading of `drains`."""
    from analysis.load import RUNS, load_run
    return shock_size(load_run(RUNS / REG11["reference_run"]))


def reg11_shock_comparable(res: dict, ref: dict) -> bool:
    """REG-11's `drains` rules out overlap protection only if its shock was comparable to REG-10's: outstanding
    session requests at the burst's end and post-burst backlogged time both >= comparable_frac x REG-10's."""
    f, s = REG11["comparable_frac"], res["shock_size"]
    return s["outstanding"] >= f * ref["outstanding"] and s["backlog_s"] >= f * ref["backlog_s"]


def reg11_turn0_reference() -> list[float]:
    """REG-11's `pass` readout: `turn0_share` in REG-10's burst run's spans, against REG-11's (queue-mix alternative)."""
    from analysis.load import RUNS, load_run
    return turn0_share(load_run(RUNS / REG11["reference_run"]), REG8["spans"])


def reg11_gate() -> dict:
    """REG-11's verdict: `reg10_gate` on the closed-loop pair. overlap_share and queued_miss_share are 0 or NaN by
    construction (a later turn is released only after its previous turn ended); release_delay is added."""
    res = reg10_gate(REG11)
    res["reference"] = reg11_reference()
    res["shock_comparable"] = reg11_shock_comparable(res, res["reference"])
    return res



# REG-12 draft (docs/decisions.md 2026-11-09 [REG]): the confirmatory matrix of REG-11's cell. One burst run and one
# same-seed control per seed; REG-11's pair (seed 1) is not counted. A seed counts as stuck when the burst run's
# `load.verdict` is `stuck` and its control's is `recovered` (C1's test, docs/claims.md); every other pair counts in n,
# not in k. The gate label (span test) is reported per seed, not counted.
REG12 = {**REG11, "seeds": (2, 3, 4, 5, 6), "most": 3, "conf": 0.95}
for _k in ("comparable_frac", "reference_run"):
    REG12.pop(_k, None)


def reg12_spec(seed: int) -> dict:
    return {**REG12, "control": f"*_stage2_control_l1pl350cl_r{REG12['lam']:g}_s{seed}",
            "burst": f"*_burst_l1pl350cl_r{REG12['lam']:g}_s{seed}"}


def reg12_only(runs: list[dict], pattern: str) -> dict:
    """REG-12 pins its runs (review, recommendation 3): exactly one valid run per pattern. A rerun is made only after an
    invalid run, never on a verdict or label, so a second valid run means something outside the registration."""
    if len(runs) != 1:
        raise ValueError(f"{pattern}: {len(runs)} valid runs, REG-12 needs exactly one")
    return runs[0]


def end_window(run: dict) -> dict:
    """REG-12 readout (review, recommendation 4): what fills `load.verdict`'s end window [t_end - end_s, t_end).
    burst_first_token: burst requests whose first token came in the window (a burst backlog still draining);
    unreleased: later session turns planned in the window and never sent; unfinished_sent: later turns planned in the
    window, sent, and not finished; q, q_slope and q / -q_slope (s to empty, NaN unless draining) from the verdict."""
    v = verdict(run)
    a, b = v["t_wipe"] + run["cfg"]["verdict"]["watch_s"] - run["cfg"]["verdict"]["end_s"], v["t_wipe"] + run["cfg"]["verdict"]["watch_s"]
    q, burst = run["requests"], is_burst_request(run)
    later = q[~burst & (q.turn > 0) & (q.t_planned >= a) & (q.t_planned < b)]
    e = v["end"]
    return {"window": (a, b),
            "burst_first_token": int((burst & (q.t_first_token >= a) & (q.t_first_token < b)).sum()),
            "unreleased": int(later.t_sent.isna().sum()),
            "unfinished_sent": int((later.t_sent.notna() & (later.status == "unfinished")).sum()),
            "q": e["q"], "q_slope": e["q_slope"],
            "s_to_empty": float(e["q"] / -e["q_slope"]) if e["q_slope"] < 0 else math.nan}


def reg12_pair(seed: int) -> dict:
    """`reg10_gate` on one seed's closed-loop pair, after checking that each pattern has exactly one valid run, with
    that seed. Adds `stuck` (C1's test), `stuck_pass` (stuck and the span test's label `pass`) and the end-window
    readout of the burst run."""
    from analysis.load import find_runs
    spec = reg12_spec(seed)
    burst = None
    for key in ("control", "burst"):
        r = reg12_only(find_runs(spec[key]), spec[key])
        if r["cfg"]["seed"] != seed:
            raise ValueError(f"{r['dir'].name} has seed {r['cfg']['seed']}, not {seed}")
        burst = r
    res = reg10_gate(spec)
    res["seed"] = seed
    res["stuck"] = res["burst_verdict"] == "stuck" and res["control_verdict"] == "recovered"
    res["stuck_pass"] = res["stuck"] and res["label"] == "pass"
    res["end_window"] = end_window(burst)
    return res


def reg12_outcome(n: int, n_control_recovered: int, k: int) -> str:
    """REG-12's decision, in this order (review, recommendation 1): controls_not_healthy if two or more controls are
    not `recovered` (the matrix cannot speak to C1); else supports if k >= most; some if k >= 1; else none."""
    if n - n_control_recovered >= 2:
        return "controls_not_healthy"
    return "supports" if k >= REG12["most"] else ("some" if k >= 1 else "none")


def reg12_table(seeds: tuple[int, ...] | None = None) -> dict:
    """REG-12's result: per seed (control and burst verdict, gate label, stuck, stuck_pass), then k stuck of n with its
    one-sided Clopper–Pearson upper bound, k_pass beside it, n_control_recovered, and `outcome` (`reg12_outcome`).
    Needs exactly one valid pair for every seed."""
    from analysis.stats import cp_upper
    seeds = tuple(seeds or REG12["seeds"])
    rows = [reg12_pair(s) for s in seeds]
    k, n = sum(r["stuck"] for r in rows), len(rows)
    n_rec = sum(r["control_verdict"] == "recovered" for r in rows)
    out = reg12_outcome(n, n_rec, k)
    return {"rows": [{key: r[key] for key in ("seed", "control_verdict", "burst_verdict", "label", "stuck", "stuck_pass",
                                              "runs")} for r in rows],
            "k": k, "n": n, "cp_upper": cp_upper(k, n, REG12["conf"]), "k_pass": sum(r["stuck_pass"] for r in rows),
            "n_control_recovered": n_rec, "outcome": out, "supports": out == "supports", "details": rows}


# REG-13 (decisions.md 2026-11-09 [REG], draft): μ_warm of L1 at 350 W with closed-loop turns, REG-8's G1′ sweep with
# closed-loop turns and a new connection per request. It asks whether the cold, backlogged states of REG-11 and REG-12
# persisted at a planned load the warm server carries (metastable) or above it (overload). Revised after its review
# (rule F). Not to be changed after approval.
REG13 = {
    "sweep_on": "sweep_l1pl350cl_pc_on", "rates": (2.0, 2.4, 2.6, 2.8, 3.0), "lam": 2.4, "power_limit_w": 350,
    "slo_ttft_s": 1.0, "surge_window_s": 120,
    "max_backlog_slope": 0.01,     # req/s, on server queue + due-but-unreleased turns (review T3; the capacity rule's limit)
    "collapse_min_warm_s": 300,    # a failing run carried its load this long before its first backlog (review T1)
    "collapse_hit_drop": 0.06,     # and its hit rate then fell by this much (configs/stage2_base.yaml stuck_hit_drop)
    # REG-8's open-loop runs with the same seed and planned schedule (checked: harness.workload.build_schedule)
    "paired": {2.0: "20261107-103010_sweep_l1pl350_pc_on_r2", 3.0: "20261107-104614_sweep_l1pl350_pc_on_r3"},
    # every run of REG-11 and REG-12 whose end window was cold and backlogged, with the planned session rate it faced
    # after its trigger (gate.post_trigger_rate, computed before this registration; fixed here, review T4)
    "cold_runs": {"20261109-042828_burst_l1pl350cl_r2.4_s1": 2.3593333333333333,
                  "20261109-080203_burst_l1pl350cl_r2.4_s2": 2.3393333333333333,
                  "20261109-093609_burst_l1pl350cl_r2.4_s3": 2.222,
                  "20261109-111316_burst_l1pl350cl_r2.4_s4": 2.711333333333333,
                  "20261109-125300_burst_l1pl350cl_r2.4_s5": 2.4,
                  "20261109-151300_burst_l1pl350cl_r2.4_s6": 2.4193333333333333,
                  "20261109-120308_stage2_control_l1pl350cl_r2.4_s5": 2.287382901894504},
}
REG13["post_lam_p_max"] = max(REG13["cold_runs"].values())   # 2.711, seed 4's burst run


def post_trigger_rate(run: dict) -> dict:
    """Where a cold run's trigger ended and the planned session rate λp it faced from then to the end of arrivals.
    A burst run: from the burst's end. A run with no trigger: from the start of its first backlogged stretch
    (`floor.backlogged_stretches` after warm-up, REG-6's stretch settings); NaN if it never backlogged."""
    from analysis.floor import backlogged_stretches
    wl = run["cfg"]["workload"]
    if (run["cfg"].get("trigger") or {}).get("kind") == "burst":
        start = burst_end(run)
    else:
        st = backlogged_stretches(run["metrics"], float(wl["warmup_s"]), float(wl["duration_s"]),
                                  REG7["cb_min_waiting"], REG7["cb_min_stretch_s"])
        start = float(st[0][0]) if st else math.nan
    lam_p = planned_session_rate(run, start, float(wl["duration_s"])) if np.isfinite(start) else math.nan
    return {"run": run["dir"].name, "from": start, "lam_p": lam_p}


def surge_max(run: dict, window_s: float) -> float:
    """Readout: the highest planned session rate over consecutive `window_s` windows of the measured window."""
    wl = run["cfg"]["workload"]
    a, b = float(wl["warmup_s"]), float(wl["duration_s"])
    starts = np.arange(a, b - window_s + 1e-9, window_s)
    return max((planned_session_rate(run, t, t + window_s) for t in starts), default=math.nan)


def due_unreleased_slope(run: dict) -> float:
    """Closed loop (review T3): slope (req/s) over the measured window of later session turns already due by their plan
    (t_planned <= t) and not yet released (t_released > t or never), on a 1 s grid. Under closed loop part of a deficit
    piles up here instead of in the server's queue. 0.0 for an open-loop run (every turn released at t_planned)."""
    wl, q = run["cfg"]["workload"], run["requests"]
    if "t_released" not in q:
        return 0.0
    q = q[q.turn > 0]
    grid = np.arange(float(wl["warmup_s"]), float(wl["duration_s"]), 1.0)
    planned = np.sort(q.t_planned.to_numpy(float))
    released = np.sort(q.t_released.dropna().to_numpy(float))
    due = np.searchsorted(planned, grid, "right") - np.searchsorted(released, grid, "right")
    return float(np.polyfit(grid, due, 1)[0])


def collapsed(run: dict) -> dict:
    """A failing run that carried its load and then went cold (review T1): its first backlogged stretch after warm-up
    (REG-6's stretch settings) starts at t_b >= warm-up + collapse_min_warm_s; over [warm-up, t_b) ok completions are
    >= 0.95 x planned session requests; and the counter hit rate over [t_b, end of arrivals) is at least
    collapse_hit_drop below that over [warm-up, t_b). Never true for a run with no backlog."""
    from analysis.floor import backlogged_stretches
    wl, r, frac = run["cfg"]["workload"], run["requests"], run["cfg"]["capacity"]["min_throughput_frac"]
    a, b = float(wl["warmup_s"]), float(wl["duration_s"])
    st = backlogged_stretches(run["metrics"], a, b, REG7["cb_min_waiting"], REG7["cb_min_stretch_s"])
    out = {"t_backlog": float(st[0][0]) if st else math.nan, "collapsed": False}
    if not st or st[0][0] < a + REG13["collapse_min_warm_s"]:
        return out
    tb = float(st[0][0])
    done = int(((r.status == "ok") & (r.t_end >= a) & (r.t_end < tb)).sum())
    planned = planned_session_rate(run, a, tb) * (tb - a)
    hit_before, hit_after = _level(run, a, tb)["hit"], _level(run, tb, b)["hit"]
    out.update(carried=done / planned if planned else math.nan, hit_before=hit_before, hit_after=hit_after)
    out["collapsed"] = bool(planned and done >= frac * planned and np.isfinite(hit_before) and np.isfinite(hit_after)
                            and hit_after <= hit_before - REG13["collapse_hit_drop"])
    return out


def reg13_check(run: dict) -> None:
    """Raises unless the run is a REG-13 sweep run: its parent, closed-loop turns, a new connection per request, 350 W."""
    cfg = run["cfg"]
    if cfg.get("sweep_parent") != REG13["sweep_on"]:
        raise ValueError(f"{run['dir'].name} is not a run of {REG13['sweep_on']}")
    if not closed_loop(run) or not cfg.get("loadgen_force_close"):
        raise ValueError(f"{run['dir'].name} lacks closed-loop turns or force_close")
    if cfg["checks"].get("expected_power_limit_w") != REG13["power_limit_w"]:
        raise ValueError(f"{run['dir'].name} is not a {REG13['power_limit_w']} W run")


def reg13_outcome(complete: bool, end_collapsed: bool, mu: float, carried: float, lam: float, lam_post_max: float) -> str:
    """In this order: `incomplete` (the chain reaches a registered rate with no valid run); `below` (`carried`, the
    realized planned rate of the run at μ_warm,cl, >= the highest post-trigger λp of the cold runs; review T2);
    `collapsed` (the first failing rate carried its load, then went cold: `collapsed`; review T1); `overload` (μ_warm,cl
    undefined or below the cell's λ); `partial` (in between)."""
    if not complete:
        return "incomplete"
    if np.isfinite(carried) and carried >= lam_post_max - 1e-9:
        return "below"
    if end_collapsed:
        return "collapsed"
    if not np.isfinite(mu) or mu < lam - 1e-9:
        return "overload"
    return "partial"


def reg13_table() -> dict:
    """REG-13's result. Per rate: throughput, planned rate, server queue slope, due-but-unreleased slope, `passes`
    (throughput >= 0.95 x planned and the sum of both slopes <= max_backlog_slope), `collapsed`, and readouts. μ_warm,cl
    by the configs' monotone rule (`load.capacity`) on that pass test, over the registered rates. `outcome`
    (`reg13_outcome`). Readouts: μ by the configs' rule alone (`tables.sweep_capacity`), paired REG-8 rows, λ_test by
    REG-7's rule, each cold run's margin."""
    from analysis.load import capacity, find_runs, load_run, summarize
    from analysis.tables import sweep_capacity
    r13 = REG13
    for rid, lam_p in r13["cold_runs"].items():   # the fixed threshold still matches its runs (review T4)
        got = post_trigger_rate(load_run(f"runs/{rid}"))["lam_p"]
        if not math.isclose(got, lam_p, rel_tol=1e-9):
            raise ValueError(f"{rid}: post-trigger λp {got} differs from the registered {lam_p}")
    runs = [r for r in find_runs(f"*_{r13['sweep_on']}_r*") if r["checks"] and r["checks"]["valid"]]
    for r in runs:
        reg13_check(r)
        if not len(r["metrics"]):
            raise ValueError(f"{r['dir'].name}: a valid run with no metrics")
    names = {r["dir"].name for r in runs}
    on = sweep_rows(r13["sweep_on"], r13["slo_ttft_s"])
    on = on[on.run.isin(names)]                     # valid runs only (review T6)
    rows = []
    for r in sorted(runs, key=lambda r: r["cfg"]["workload"]["rate"]):
        s, wl, cap = summarize(r), r["cfg"]["workload"], r["cfg"]["capacity"]
        due = due_unreleased_slope(r)
        row = on[on.run == r["dir"].name].iloc[0].to_dict()
        passes = bool(s["throughput"] >= cap["min_throughput_frac"] * s["planned_rate"]
                      and s["q_slope_per_s"] + due <= r13["max_backlog_slope"])
        rows.append({**row, "q_slope": s["q_slope_per_s"], "due_slope": due, "unfinished": s["unfinished"],
                     "passes": passes, **({} if passes else collapsed(r)),
                     "release_delay": release_delay(r, [(float(wl["warmup_s"]), float(wl["duration_s"]))], end=0.0)[0],
                     "surge_max": surge_max(r, r13["surge_window_s"])})
    by = {row["rate"]: row for row in rows}
    curve = pd.DataFrame({"rate": [x["rate"] for x in rows], "throughput": [x["throughput"] for x in rows],
                          "planned_rate": [x["planned_rate"] for x in rows],
                          "q_slope_per_s": [0.0 if x["passes"] else math.inf for x in rows]})
    mu = capacity(curve, 0.0, 1.0, "planned_rate", monotone=True, swept_rates=list(r13["rates"])) if rows else math.nan
    chain_end = next((x for x in r13["rates"] if x not in by or not by[x]["passes"]), None)
    complete = chain_end is None or chain_end in by
    end_collapsed = bool(complete and chain_end is not None and by[chain_end].get("collapsed"))
    carried = by[mu]["planned_rate"] if np.isfinite(mu) else math.nan
    paired = sweep_rows("sweep_l1pl350_pc_on", r13["slo_ttft_s"])
    paired = paired[paired.run.isin(r13["paired"].values())].to_dict("records")
    floor = reg8_g1_may_start()
    return {"rows": rows, "mu_warm_cl": mu, "carried": carried, "chain_end": chain_end,
            "outcome": reg13_outcome(complete, end_collapsed, mu, carried, r13["lam"], r13["post_lam_p_max"]),
            "n_cold_below": sum(v <= carried + 1e-9 for v in r13["cold_runs"].values()) if np.isfinite(carried) else 0,
            "mu_config_rule": sweep_capacity(r13["sweep_on"]) if runs else math.nan,
            "paired_reg8": paired, "mu_sat_off": floor["mu_sat_off"],
            "lam_test_reg7_rule": choose_lambda(mu, floor["mu_sat_off"], on, REG7) if np.isfinite(mu) else None}


def reg13_inputs() -> dict:
    """REG-13's design inputs, from runs that exist before it: the cold runs' post-trigger λp."""
    from analysis.load import load_run
    cold = [post_trigger_rate(load_run(f"runs/{rid}")) for rid in REG13["cold_runs"]]
    return {"cold_runs": cold, "post_lam_p_max": max(c["lam_p"] for c in cold)}

def due_unreleased_profile(run: dict, window_s: float = 120.0) -> dict:
    """Exploratory readout ([CORR] 2026-11-10 on REG-13): why `due_unreleased_slope` grows on a healthy closed loop.
    Over the measured window: the slope it gives; the planned rate of later turns over the first and last `window_s`;
    and the median release lag (t_released - t_planned) of later turns by planned minute."""
    wl, q = run["cfg"]["workload"], run["requests"]
    a, b = float(wl["warmup_s"]), float(wl["duration_s"])
    q = q[q.turn > 0]
    rate = lambda lo, hi: float(((q.t_planned >= lo) & (q.t_planned < hi)).sum() / (hi - lo))
    lag = q.t_released.astype(float) - q.t_planned
    by_min = [float(lag[(q.t_planned >= t) & (q.t_planned < t + 60)].median()) for t in np.arange(a, b, 60.0)]
    return {"slope": due_unreleased_slope(run), "later_rate_first": rate(a, a + window_s),
            "later_rate_last": rate(b - window_s, b), "lag_by_minute": by_min}


# REG-14 draft (docs/decisions.md 2026-11-10 [REG]): REG-12's seed-2 pair at λ = 2.2 instead of 2.4, the only change
# (owner's choice of cell after the review, 2026-11-10). Judged as REG-11 (`reg10_gate`). The shock is read against
# REG-12's seed-2 burst run: the same seed and burst at λ = 2.4.
REG14 = {**REG11, "lam": 2.2, "seed": 2}
REG14["control"] = "*_stage2_control_l1pl350cl_r2.2_s2"
REG14["burst"] = "*_burst_l1pl350cl_r2.2_s2"
REG14["reference_run"] = "20261109-080203_burst_l1pl350cl_r2.4_s2"   # REG-12's seed-2 burst run (`stuck`)
REG14["cold_c_max"] = 1.84   # highest span completion rate of REG-11/12's cold runs (decisions.md 2026-11-09 [RESULT] REG-12)
REG14["seed_candidates"] = tuple(range(1, 11))
REG14["max_control_waiting"] = 0.5   # review round 2, B1: a `pass` drafts the matrix only below this (fixed before any run)
REG14["warm_runs"] = ("20261109-190221_sweep_l1pl350cl_pc_on_r2", "20261109-191845_sweep_l1pl350cl_pc_on_r2.4")


def max_holding_c(lam: float, lam_p: float, span_s: float, conf: float) -> float:
    """The highest point completion rate n / span_s whose upper bound `poisson_rate_upper(n, span_s, conf)` is still
    below min(λ, λp): the most a cold span may complete and still hold (`burst_backlog`). NaN if no n holds."""
    from analysis.stats import poisson_rate_upper
    cap, n = min(lam, lam_p), -1
    while poisson_rate_upper(n + 1, span_s, conf) < cap:
        n += 1
    return n / span_s if n >= 0 else math.nan


def _burst_cfg(name: str = "burst_l1pl350cl_r2.2_s2") -> dict:
    from harness.config import load_config, with_defaults
    from harness.run import expand
    return expand(with_defaults(load_config(Path(f"configs/{name}.yaml"))))[0]


def span_sensitivity(lam: float, seed: int) -> dict:
    """REG-14 review, recommendation 1 (design input, no run): REG-14's burst config at λ and seed, its planned λp in
    each of REG-8's spans after the burst, and the highest cold completion rate that could hold in each span."""
    from harness.workload import build_schedule
    b = _burst_cfg()
    s, _ = build_schedule({**b["workload"], "rate": lam}, seed, b["trigger"])
    s = s[~s.burst]
    end = float(b["trigger"]["at_s"] + b["trigger"]["duration_s"])
    rows = []
    for x, y in REG8["spans"]:
        lo, hi = end + x, end + y
        lp = float(((s.t_planned >= lo) & (s.t_planned < hi)).sum() / (hi - lo))
        rows.append({"span": (x, y), "lam_p": lp, "max_c": max_holding_c(lam, lp, hi - lo, REG8["conf"])})
    return {"lam": lam, "seed": seed, "spans": rows}


def reg14_seed_rule(lam: float, seeds=None, cold_c_max: float | None = None) -> int | None:
    """The seed REG-14 uses: the lowest candidate whose every span could hold a cold completion rate above
    `cold_c_max` (each span's `max_c` > the highest cold rate seen). None if no candidate qualifies."""
    seeds = REG14["seed_candidates"] if seeds is None else seeds
    c = REG14["cold_c_max"] if cold_c_max is None else cold_c_max
    for sd in seeds:
        if all(r["max_c"] > c for r in span_sensitivity(lam, sd)["spans"]):
            return sd
    return None


def reg14_sensitivity(lams=(2.0, 2.2)) -> dict:
    """Design inputs for the cell choice: every candidate seed at each λ, and the seed the rule picks."""
    return {lam: {"seeds": [span_sensitivity(lam, sd) for sd in REG14["seed_candidates"]],
                  "picked": reg14_seed_rule(lam)} for lam in lams}


def reg14_schedule_inputs() -> dict:
    """REG-14's design inputs from the configs alone (no run): λp in the baseline, from the burst's end to the end of
    arrivals and per span, the highest 120 s window, request counts, and whether the control's schedule equals the
    burst run's session rows."""
    from harness.workload import build_schedule
    c, b = _burst_cfg("stage2_control_l1pl350cl_r2.2_s2"), _burst_cfg()
    sc, _ = build_schedule(c["workload"], c["seed"], c.get("trigger"))
    sb, _ = build_schedule(b["workload"], b["seed"], b["trigger"])
    s = sb[~sb.burst].reset_index(drop=True)
    rate = lambda lo, hi: float(((s.t_planned >= lo) & (s.t_planned < hi)).sum() / (hi - lo))
    start, dur = float(b["trigger"]["at_s"]), float(b["workload"]["duration_s"])
    end = start + float(b["trigger"]["duration_s"])
    wins = [(float(t), rate(t, t + 120)) for t in np.arange(float(b["workload"]["warmup_s"]), dur - 120 + 1e-9, 120)]
    same = len(s) == len(sc) and bool((s.t_planned.values == sc.t_planned.values).all()
                                      and (s.prompt_len.values == sc.prompt_len.values).all())
    return {"lam_p_post": rate(end, dur), "lam_p_baseline": rate(start - REG8["baseline_s"], start),
            "spans": span_sensitivity(b["workload"]["rate"], b["seed"])["spans"],
            "surge_max": max(wins, key=lambda w: w[1]), "windows_above_2_4": [w for w in wins if w[1] > 2.4],
            "n_burst": int(sb.burst.sum()), "n_session": len(s), "control_schedule_same": same}


def reg14_inputs() -> dict:
    from analysis.load import RUNS, load_run, summarize
    out = reg14_schedule_inputs()
    out["warm"] = [{k: summarize(load_run(RUNS / rid))[k] for k in ("planned_rate", "throughput")} | {"run": rid}
                   for rid in REG14["warm_runs"]]
    out["reference"] = shock_size(load_run(RUNS / REG14["reference_run"]))
    out["seed_rule"] = reg14_seed_rule(REG14["lam"])
    return out


def release_rate(run: dict, spans: list[tuple[float, float]]) -> list[float]:
    """REG-14 readout (review, recommendation 4 and T5): per span after the burst's end, session requests released per
    second, first turns included (released at t_released, else t_planned), the same population as λp
    (`planned_session_rate`): under closed loop the released load falls below λp when sessions lag."""
    q, end = run["requests"], burst_end(run)
    if "t_released" not in q:
        return [math.nan for _ in spans]
    s = q[~is_burst_request(run)]
    rel = s.t_released.astype(float).fillna(s.t_planned.astype(float))
    rel = rel[s.t_sent.notna()] if "t_sent" in s else rel
    return [float(((rel >= end + a) & (rel < end + b)).sum() / (b - a)) for a, b in spans]


def control_waiting(control: dict, abs_spans: list[tuple[float, float]]) -> list[dict]:
    """REG-14 readout (review T3): per absolute span, the share of the control's scrapes with waiting > 0 and its mean."""
    m, out = control["metrics"], []
    for lo, hi in abs_spans:
        q = m["vllm:num_requests_waiting"][(m.t >= lo) & (m.t < hi)]
        out.append({"share_waiting": float((q > 0).mean()) if len(q) else math.nan,
                    "mean": float(q.mean()) if len(q) else math.nan})
    return out


def reg14_gate() -> dict:
    """REG-14's verdict: `reg10_gate` on the λ = 2.2 closed-loop pair of seed 2, with REG-11's comparability rule
    against REG-12's seed-2 burst run; readouts: post-burst λp, per-span max holding c, release rate, control waiting."""
    from analysis.load import RUNS, load_run
    res = reg10_gate(REG14)
    control, burst = (load_run(RUNS / n) for n in res["runs"])
    for r in (control, burst):
        if r["cfg"]["seed"] != REG14["seed"]:
            raise ValueError(f"{r['dir'].name} is not seed {REG14['seed']}")
    res["reference"] = shock_size(load_run(RUNS / REG14["reference_run"]))
    f, s = REG14["comparable_frac"], res["shock_size"]
    res["shock_comparable"] = s["outstanding"] >= f * res["reference"]["outstanding"] and \
        s["backlog_s"] >= f * res["reference"]["backlog_s"]
    res["post_trigger"] = post_trigger_rate(burst)
    end = burst_end(burst)
    res["max_holding_c"] = [max_holding_c(REG14["lam"], r["lam_p"], r["span"][1] - r["span"][0], REG8["conf"])
                            for r in res["spans"]]
    res["release_rate"] = release_rate(burst, REG8["spans"])
    res["control_waiting"] = control_waiting(control, [(end + a, end + b) for a, b in REG8["spans"]])
    res["outcome"] = reg14_outcome(res)
    return res


def reg14_outcome(res: dict) -> str:
    """REG-14's decision map (review round 2, B1). A `pass` is `pass_clear` if some counting span has the control
    waiting at no more than `max_control_waiting` of its scrapes, otherwise `pass_warm_edge` (the control queued in
    every counting span: overload is not excluded there). Every other outcome is `reg10_gate`'s."""
    if res["outcome"] != "pass":
        return res["outcome"]
    ok = [r["counts"] and w["share_waiting"] <= REG14["max_control_waiting"]
          for r, w in zip(res["spans"], res["control_waiting"])]
    return "pass_clear" if any(ok) else "pass_warm_edge"

# REG-15 draft (docs/decisions.md 2026-11-10 [REG]): C1's confirmation run at REG-14's cell (PROTOCOL §3, conditions 5
# and 6). One run: REG-14's burst config at seed 12 (`reg15_seed_rule`, owner 2026-11-10) with a 4500 s watch, then
# λ = 1 for 1800 s, then λ = 2.2 for 1500 s.
REG15 = {"pattern": "*_confirm_l1pl350cl_r2.2_s12", "lam": 2.2, "seed": 12, "power_limit_w": 350,
         "watch_s": 4500, "drop_rate": 1.0, "drop_s": 1800, "return_s": 1500, "return_end_s": 600,
         "timeline_s": 300, "n_cap": 256, "window_tol": 0.05}


def reg15_phases(run: dict) -> dict:
    """The run's phases from its config: baseline window, burst, watch end, drop and return (absolute seconds).
    Raises unless the config is REG-15's design (one drop to `drop_rate`, then back to λ, at the watch's end)."""
    cfg, wl, tr = run["cfg"], run["cfg"]["workload"], run["cfg"]["trigger"]
    end = float(tr["at_s"] + tr["duration_s"])
    watch_end = end + float(cfg["verdict"]["watch_s"])
    steps = wl.get("steps") or []
    ok = (len(steps) == 2 and float(steps[0]["at_s"]) == watch_end and float(steps[0]["rate"]) == REG15["drop_rate"]
          and float(steps[1]["at_s"]) == watch_end + REG15["drop_s"] and float(steps[1]["rate"]) == float(wl["rate"])
          and float(wl["duration_s"]) == watch_end + REG15["drop_s"] + REG15["return_s"]
          and float(cfg["verdict"]["watch_s"]) == REG15["watch_s"])
    if not ok:
        raise ValueError(f"{run['dir'].name} does not have REG-15's watch, drop and return")
    return {"baseline": (float(tr["at_s"]) - float(cfg["verdict"]["baseline_s"]), float(tr["at_s"])),
            "burst_end": end, "watch_end": watch_end, "drop": (watch_end, watch_end + REG15["drop_s"]),
            "return": (watch_end + REG15["drop_s"], float(wl["duration_s"])),
            "return_end": (float(wl["duration_s"]) - REG15["return_end_s"], float(wl["duration_s"]))}


def line_reached_zero(run: dict, a: float, b: float) -> bool | None:
    """Condition 6's "the line reached 0 during the drop": some scrape in [a, b) has 0 requests waiting.
    None if no scrape in the window has a value."""
    m = run["metrics"]
    q = m["vllm:num_requests_waiting"][(m.t >= a) & (m.t < b)].dropna()
    return None if not len(q) else bool((q == 0).any())


def recovered_against(run: dict, base: dict, a: float, b: float) -> bool | None:
    """`load.verdict`'s `recovered` test for the window [a, b) against a given baseline level, with the run's own
    `verdict` settings. None if a value it needs is NaN."""
    from analysis.load import _level
    c, w = run["cfg"]["verdict"], _level(run, a, b)
    if any(np.isnan(x) for x in (w["pf"], w["hit"], w["q"], base["pf"], base["hit"], base["q"])):
        return None
    return bool(w["pf"] >= base["pf"] - c["recovered_pf_drop"] and w["hit"] >= base["hit"] - c["recovered_hit_drop"]
                and w["q"] <= base["q"] + c["recovered_q_excess"])


def reg15_outcome(v5: str, line_zero: bool | None, back: bool | None, broken: bool = False) -> str:
    """REG-15's outcome from condition 5 (`load.verdict` of the 4500 s watch), persistence through the watch (review T3)
    and condition 6 (the line reached 0 in the drop; the last 600 s of the return `recovered` against the baseline).
    - bad_baseline: v5 `bad_baseline` (the owner decides);
    - not_persistent: v5 `recovered` or `slow_drain` (condition 5 fails);
    - inconclusive: v5 `unclear`, or a needed value is missing (an instrument gap; rerun);
    - reformed: stuck at the watch's end, but some 300 s window of the watch was `recovered` (`broken`): the cold
      state cleared and came back, so persistence is not shown;
    - drop_inconclusive: stuck, but the line never reached 0 in the drop (condition 6 inconclusive, PROTOCOL §3);
    - no_return: stuck, the line reached 0, but the end of the return is not `recovered`;
    - confirms: stuck through the watch, the line reached 0, and the end of the return is `recovered`."""
    if v5 == "bad_baseline":
        return "bad_baseline"
    if v5 in ("recovered", "slow_drain"):
        return "not_persistent"
    if v5 != "stuck":
        return "inconclusive"
    if broken:
        return "reformed"
    if line_zero is None:
        return "inconclusive"
    if not line_zero:
        return "drop_inconclusive"
    if back is None:
        return "inconclusive"
    return "confirms" if back else "no_return"


def watch_broken(run: dict, base: dict, burst_end_s: float, watch_end_s: float) -> dict:
    """Review T3: `recovered_against` the baseline for each 300 s window from the burst's end to the watch's end.
    `broken` is True if any window is `recovered` (a window with a missing value counts as not recovered)."""
    step = REG15["timeline_s"]
    wins = [(a, a + step) for a in np.arange(burst_end_s, watch_end_s - step + 1e-9, step)]
    rec = [recovered_against(run, base, a, b) for a, b in wins]
    lam = [planned_session_rate(run, a, b) for a, b in wins] if "requests" in run else [math.nan] * len(wins)
    return {"windows": wins, "recovered": rec, "lam_p": lam, "broken": any(x is True for x in rec)}


def reg15_timeline(run: dict) -> list[dict]:
    """Readout, never decisive: `_level` over consecutive `timeline_s` windows of the whole run, with λp per window."""
    from analysis.load import _level
    dur, step = float(run["cfg"]["workload"]["duration_s"]), REG15["timeline_s"]
    return [{"t": (a, a + step), "lam_p": planned_session_rate(run, a, a + step), **_level(run, a, a + step)}
            for a in np.arange(0.0, dur - step + 1e-9, step)]


def reg15_check(run: dict) -> None:
    c = run["cfg"]
    if not (run["checks"] and run["checks"]["valid"]):
        raise ValueError(f"{run['dir'].name} is not valid")
    if (c["seed"] != REG15["seed"] or float(c["workload"]["rate"]) != REG15["lam"] or not closed_loop(run)
            or c.get("loadgen_force_close") is not True
            or c["checks"].get("expected_power_limit_w") != REG15["power_limit_w"]):
        raise ValueError(f"{run['dir'].name} is not REG-15's seed, λ, closed loop, force_close and 350 W")


def reg15_table() -> dict:
    """REG-15's result: the latest valid confirmation run (`reg10_pick`), its outcome, and readouts (never decisive):
    the span test over the watch in 300 s spans, condition 4's loop levels over the watch's last 1500 s, release
    delay at the phase edges, the timeline."""
    from analysis.load import _level, find_runs, verdict
    run = reg10_pick(find_runs(REG15["pattern"]))
    reg15_check(run)
    ph, v = reg15_phases(run), verdict(run)
    base = v["baseline"]
    line = line_reached_zero(run, *ph["drop"])
    back = recovered_against(run, base, *ph["return_end"])
    brk = watch_broken(run, base, ph["burst_end"], ph["watch_end"])
    watch = [(a, a + 300.0) for a in np.arange(0.0, REG15["watch_s"] - 300 + 1e-9, 300.0)]
    spans = burst_backlog(run, watch, REG8["baseline_s"], REG8["cold_hit_drop"], REG8["conf"])
    loop = _level(run, ph["watch_end"] - 1500, ph["watch_end"])
    m = run["metrics"]
    n_max = float(m["vllm:num_requests_running"][(m.t >= ph["watch_end"] - 1500) & (m.t < ph["watch_end"])].max())
    return {"run": run["dir"].name, "v5": v["verdict"], "baseline": base, "watch_end_level": v["end"],
            "line_reached_zero": line, "return_end_level": _level(run, *ph["return_end"]), "return_recovered": back,
            "outcome": reg15_outcome(v["verdict"], line, back, brk["broken"]), "phases": ph, "watch_broken": brk,
            "drop_level": _level(run, ph["drop"][1] - REG15["return_end_s"], ph["drop"][1]),
            "judged_lam_p": {k: planned_session_rate(run, a, b) for k, (a, b) in
                             {"baseline": ph["baseline"], "previous": (ph["watch_end"] - 2 * run["cfg"]["verdict"]["end_s"],
                              ph["watch_end"] - run["cfg"]["verdict"]["end_s"]),
                              "end": (ph["watch_end"] - run["cfg"]["verdict"]["end_s"], ph["watch_end"]),
                              "return_end": ph["return_end"]}.items()},
            "watch_spans": [{k: r[k] for k in ("span", "c", "c_upper", "lam_p", "holds")} for r in spans],
            "loop": {"kv": loop["kv"], "n": loop["n"], "n_over_base": loop["n"] / base["n"], "n_max": n_max,
                     "n_cap": REG15["n_cap"]},
            "release_delay": release_delay(run, [(ph["watch_end"] - 300, ph["watch_end"]), (ph["drop"][1] - 300,
                                           ph["drop"][1]), (ph["return_end"][0], ph["return_end"][1])], end=0.0),
            "timeline": reg15_timeline(run)}


def reg15_judged_windows(seed: int) -> dict:
    """REG-15 review T1/T2 (design input, no run): the confirmation config at `seed`, planned λp in the windows the
    outcome judges (baseline, the verdict's previous and end windows, the return's end) and the highest 120 s window
    inside the end window and the return's end."""
    from harness.workload import build_schedule
    b = _burst_cfg("confirm_l1pl350cl_r2.2_s12")
    s, _ = build_schedule(b["workload"], seed, b["trigger"])
    s = s[~s.burst]
    rate = lambda lo, hi: float(((s.t_planned >= lo) & (s.t_planned < hi)).sum() / (hi - lo))
    v, tr = b["verdict"], b["trigger"]
    t0, we, dur = float(tr["at_s"]), float(tr["at_s"] + tr["duration_s"] + v["watch_s"]), float(b["workload"]["duration_s"])
    win = {"baseline": (t0 - v["baseline_s"], t0), "previous": (we - 2 * v["end_s"], we - v["end_s"]),
           "end": (we - v["end_s"], we), "return_end": (dur - REG15["return_end_s"], dur)}
    peak = lambda lo, hi: max(rate(t, t + 120) for t in np.arange(lo, hi - 120 + 1e-9, 60.0))
    return {"seed": seed, "windows": win, "lam_p": {k: rate(*w) for k, w in win.items()},
            "peak_end": peak(*win["end"]), "peak_return_end": peak(*win["return_end"])}


def reg15_seed_rule(seeds=range(1, 31), tol: float | None = None) -> dict:
    """The seed REG-15 uses (review recommendation 2): the lowest candidate whose four judged windows all have λp
    within `tol` x λ of λ, so the stuck test and the recovery test judge the same planned load."""
    tol = REG15["window_tol"] if tol is None else tol
    rows = [reg15_judged_windows(sd) for sd in seeds]
    ok = [r for r in rows if all(abs(x - REG15["lam"]) <= tol * REG15["lam"] for x in r["lam_p"].values())]
    return {"picked": ok[0]["seed"] if ok else None, "qualifying": [r["seed"] for r in ok], "rows": rows}


def reg15_inputs() -> dict:
    """REG-15's design inputs from the config alone (no run): planned λp per phase and the 120 s windows above λ."""
    from harness.workload import build_schedule
    b = _burst_cfg("confirm_l1pl350cl_r2.2_s12")
    s, _ = build_schedule(b["workload"], b["seed"], b["trigger"])
    n_burst = int(s.burst.sum())
    s = s[~s.burst]
    rate = lambda lo, hi: float(((s.t_planned >= lo) & (s.t_planned < hi)).sum() / (hi - lo))
    wd = float(b["trigger"]["at_s"] + b["trigger"]["duration_s"] + b["verdict"]["watch_s"])
    dur = float(b["workload"]["duration_s"])
    wins = [(float(t), rate(t, t + 120)) for t in np.arange(240.0, dur - 120 + 1e-9, 120)]
    return {"n_session": len(s), "n_burst": n_burst, "lam_p": {"baseline": rate(300, 900), "watch": rate(1080, wd),
            "watch_last_300": rate(wd - 300, wd), "drop": rate(wd, wd + 1800), "return": rate(wd + 1800, dur),
            "return_last_600": rate(dur - 600, dur),
            "drop_by_600": [rate(a, a + 600) for a in (wd, wd + 600, wd + 1200)]},
            "windows_above_lam": [w for w in wins if w[1] > float(b["workload"]["rate"])]}


# REG-16 draft (docs/decisions.md 2026-11-10 [REG]): a no-burst control at λ = 2.2 on the exact session schedule of a
# later confirmation run with a longer drop (REG-17, registered separately). The drop is sized from the total owed
# backlog (server waiting plus turns planned but not completed), calibrated on REG-15's run (reviewer, 2026-11-10).
REG16 = {"lam": 2.2, "power_limit_w": 350, "watch_s": 4500, "drop_rate": 1.0, "return_s": 1500, "return_end_s": 600,
         "timeline_s": 300, "window_tol": 0.05, "drop_candidates": (5400, 7200, 9000),
         "seeds": tuple(s for s in range(1, 31) if s not in (3, 4, 5, 6, 7)),   # 3-7 kept for the matrix (owner)
         "calib_run": "20261110-085730_confirm_l1pl350cl_r2.2_s12",
         "c_pessimism": 0.05,     # c_b 1.78-1.83 across REG-11/12/14 (decisions.md [RESULT]s): the spread of cold rates
         "calib_window_s": 600,   # review T3: the pessimistic rates start from REG-15's lowest 600 s rate per phase
         "warm_watch_s": 1200, "grid_s": 10.0,
         "control_pattern": "*_stage2_control_l1pl350cl_r2.2_long_s{seed}",
         "baseline": (300.0, 900.0),   # the burst run's baseline window (trigger at 900 s, baseline_s 600), for both runs
         "drop_s": 9000,     # chosen over the rule's 7200 s for margin (review round 2, N1; owner delegated, 2026-11-10)
         "persistent_s": 1500}   # review round 2, T1: a cold stretch this long counts as persistent: the study's watch
                                 # window, max(1200 s, 5 tau) (docs/definitions.md "watch window")


def completion_rate(run: dict, a: float, b: float) -> float:
    """Requests (session and burst) completed per second in [a, b), by t_end."""
    q = run["requests"]
    return float(((q.t_end >= a) & (q.t_end < b)).sum() / (b - a))


def owed_backlog(run: dict, t: float) -> int:
    """The total line at time t: requests planned before t and not completed by t (server waiting and running, plus
    closed-loop turns not yet released)."""
    q = run["requests"]
    return int(((q.t_planned < t) & ~(q.t_end < t)).sum())


def reg16_calibration() -> dict:
    """The drain model's inputs from REG-15's run: owed backlog at the burst's start, the watch's end and the drop's end;
    completion rates over burst-plus-watch and over the drop; the drop's released rate."""
    from analysis.load import load_run
    run = load_run(Path("runs") / REG16["calib_run"])
    ph = reg15_phases(run)
    t0, we, de = float(run["cfg"]["trigger"]["at_s"]), ph["watch_end"], ph["drop"][1]
    w = REG16["calib_window_s"]
    lowest = lambda a, b: min(completion_rate(run, x, x + w) for x in np.arange(a, b - w + 1e-9, w))
    return {"run": run["dir"].name, "owed_at_trigger": owed_backlog(run, t0), "owed_at_watch_end": owed_backlog(run, we),
            "owed_at_drop_end": owed_backlog(run, de), "c_watch": completion_rate(run, t0, we),
            "c_drop": completion_rate(run, we, de), "c_watch_min": lowest(ph["burst_end"], we),
            "c_drop_min": lowest(we, de), "released_drop": release_rate(run, [(we - ph["burst_end"],
                                                                                de - ph["burst_end"])])[0]}


def reg16_burst_cfg(seed: int, drop_s: float) -> dict:
    """The REG-17 confirmation config at `seed` and `drop_s` (resolved; REG-15's design with a longer drop)."""
    b = _burst_cfg("confirm_l1pl350cl_r2.2_s12")
    we = float(b["trigger"]["at_s"] + b["trigger"]["duration_s"] + REG16["watch_s"])
    wl = {**b["workload"], "duration_s": we + drop_s + REG16["return_s"],
          "steps": [{"at_s": we, "rate": REG16["drop_rate"]}, {"at_s": we + drop_s, "rate": REG16["lam"]}]}
    return {**b, "seed": seed, "workload": wl}


def reg16_empty_time(cfg: dict, cal: dict, pessimistic: bool = False) -> float:
    """Predicted seconds from the drop's start until the owed backlog reaches 0 (NaN if not within the drop): owed at
    the trigger, plus every request planned since, minus completions at REG-15's cold rates per phase. Pessimistic
    (review T3): REG-15's lowest 600 s rate in each phase, lowered by `c_pessimism`."""
    dc = REG16["c_pessimism"] if pessimistic else 0.0
    cw, cd = (cal["c_watch_min"], cal["c_drop_min"]) if pessimistic else (cal["c_watch"], cal["c_drop"])
    from harness.workload import build_schedule
    s, _ = build_schedule(cfg["workload"], cfg["seed"], cfg["trigger"])
    t0 = float(cfg["trigger"]["at_s"])
    we = float(cfg["workload"]["steps"][0]["at_s"])
    de = float(cfg["workload"]["steps"][1]["at_s"])
    tp = np.sort(s.t_planned.to_numpy())
    for t in np.arange(we, de + 1e-9, REG16["grid_s"]):
        planned = np.searchsorted(tp, t) - np.searchsorted(tp, t0)
        done = (cw - dc) * (we - t0) + (cd - dc) * (t - we)
        if cal["owed_at_trigger"] + planned - done <= 0:
            return float(t - we)
    return math.nan


def reg16_judged_windows(cfg: dict) -> dict:
    """λp (session requests) in the windows the outcomes judge: baseline, the verdict's previous and end windows, the
    return's end; as `reg15_judged_windows`, for any design."""
    from harness.workload import build_schedule
    s, _ = build_schedule(cfg["workload"], cfg["seed"], cfg["trigger"])
    s = s[~s.burst]
    rate = lambda lo, hi: float(((s.t_planned >= lo) & (s.t_planned < hi)).sum() / (hi - lo))
    v, tr, dur = cfg["verdict"], cfg["trigger"], float(cfg["workload"]["duration_s"])
    t0, we = float(tr["at_s"]), float(tr["at_s"] + tr["duration_s"] + REG16["watch_s"])
    win = {"baseline": (t0 - v["baseline_s"], t0), "previous": (we - 2 * v["end_s"], we - v["end_s"]),
           "end": (we - v["end_s"], we), "return_end": (dur - REG16["return_end_s"], dur)}
    return {k: rate(*w) for k, w in win.items()}


def reg16_seed_rule() -> dict:
    """REG-16's design: the shortest drop in `drop_candidates`, and in it the lowest seed in `seeds`, whose four judged
    windows have λp within `window_tol` x λ of λ and whose pessimistic predicted empty time (cold rates lowered by
    `c_pessimism` from REG-15's lowest 600 s rates) leaves `warm_watch_s` of the drop to watch the cache."""
    cal = reg16_calibration()
    rows = []
    for d in REG16["drop_candidates"]:
        for sd in REG16["seeds"]:
            cfg = reg16_burst_cfg(sd, d)
            lam = reg16_judged_windows(cfg)
            t_mid, t_pess = reg16_empty_time(cfg, cal), reg16_empty_time(cfg, cal, pessimistic=True)
            ok_w = all(abs(x - REG16["lam"]) <= REG16["window_tol"] * REG16["lam"] for x in lam.values())
            ok_d = bool(np.isfinite(t_pess) and t_pess + REG16["warm_watch_s"] <= d)
            rows.append({"drop_s": d, "seed": sd, "lam_p": lam, "empty_s": t_mid, "empty_s_pessimistic": t_pess,
                         "windows_ok": ok_w, "drop_ok": ok_d})
        ok = [r for r in rows if r["drop_s"] == d and r["windows_ok"] and r["drop_ok"]]
        if ok:
            return {"calibration": cal, "picked": {"drop_s": d, "seed": ok[0]["seed"]}, "rows": rows}
    return {"calibration": cal, "picked": None, "rows": rows}


def reg16_phases(run: dict) -> dict:
    """REG-16's control phases (absolute s): its own baseline (verdict, `control_t_s`), the burst run's watch, drop and
    return, and the return's end. Raises unless the config is REG-16's design."""
    cfg, wl = run["cfg"], run["cfg"]["workload"]
    t = float(cfg["verdict"]["control_t_s"])
    we, dur = t + REG16["watch_s"], float(wl["duration_s"])
    steps = wl.get("steps") or []
    ok = ((cfg.get("trigger") or {}).get("kind") != "burst" and float(cfg["verdict"]["watch_s"]) == REG16["watch_s"]
          and len(steps) == 2 and float(steps[0]["at_s"]) == we and float(steps[0]["rate"]) == REG16["drop_rate"]
          and float(steps[1]["rate"]) == REG16["lam"] and dur == float(steps[1]["at_s"]) + REG16["return_s"])
    if not ok:
        raise ValueError(f"{run['dir'].name} does not have REG-16's control design")
    return {"baseline": (t - float(cfg["verdict"]["baseline_s"]), t), "watch": (t, we),
            "drop": (we, float(steps[1]["at_s"])), "return": (float(steps[1]["at_s"]), dur),
            "return_end": (dur - REG16["return_end_s"], dur)}


def pf_by_sent(run: dict, a: float, b: float) -> float:
    """Percent fast of requests sent in [a, b) (review T2: under closed loop a request is served near its send time, not
    near its planned time, which lags by up to 15 min). NaN with no request."""
    r, slo = run["requests"], run["cfg"]["slo"]["ttft_s"]
    q = r[(r.t_sent >= a) & (r.t_sent < b)]
    return float(((q.status == "ok") & (q.ttft <= slo)).mean()) if len(q) else math.nan


def cold_windows(run: dict, base: dict, a: float, b: float) -> dict:
    """Per `timeline_s` window in [a, b), with no new threshold:
    - `cold`: the hit share (scrape time) and percent fast (`pf_by_sent`) both at `load.verdict`'s stuck levels against
      the baseline: hit <= base - stuck_hit_drop and pf <= base - stuck_pf_drop; None if either is NaN;
    - `hit_low_queued` (review T2): hit <= base - stuck_hit_drop with a waiting mean above base + recovered_q_excess,
      whatever pf says; None if either is NaN."""
    c, step = run["cfg"]["verdict"], REG16["timeline_s"]
    wins = [(x, x + step) for x in np.arange(a, b - step + 1e-9, step)]
    cold, low = [], []
    for lo, hi in wins:
        w, pf = _level(run, lo, hi), pf_by_sent(run, lo, hi)
        hit_low = None if np.isnan(w["hit"]) else bool(w["hit"] <= base["hit"] - c["stuck_hit_drop"])
        cold.append(None if hit_low is None or np.isnan(pf) else bool(hit_low and pf <= base["pf"] - c["stuck_pf_drop"]))
        low.append(None if hit_low is None or np.isnan(w["q"]) else
                   bool(hit_low and w["q"] > base["q"] + c["recovered_q_excess"]))
    return {"windows": wins, "cold": cold, "hit_low_queued": low}


def longest_cold_s(cw: dict) -> float:
    """The longest run of consecutive cold windows, in seconds (a None breaks a run)."""
    best = cur = 0.0
    for (lo, hi), x in zip(cw["windows"], cw["cold"]):
        cur = cur + (hi - lo) if x is True else 0.0
        best = max(best, cur)
    return best


def cold_persistent(cw: dict, phase_ends: list[float]) -> bool | None:
    """Review T1 and round 2, T1: True if some cold window is the last window of its phase (still cold when the phase
    ends), or a cold stretch lasts `persistent_s` or more. None if a phase's last window is missing right after a cold
    window (it cannot be told whether the stretch ended), unless already True. Else False."""
    pairs = list(zip(cw["windows"], cw["cold"]))
    if any(x is True and w[1] in phase_ends for w, x in pairs) or longest_cold_s(cw) >= REG16["persistent_s"]:
        return True
    if any(x is None and w[1] in phase_ends and i > 0 and pairs[i - 1][1] is True for i, (w, x) in enumerate(pairs)):
        return None
    return False


def window_mix(run: dict, a: float, b: float) -> dict:
    """Readout (review round 2, T3 and N2): requests planned in [a, b) never sent (`pf_by_sent` cannot count them), and
    the first-turn share of the session requests sent in [a, b)."""
    r = run["requests"]
    planned = r[(r.t_planned >= a) & (r.t_planned < b)]
    sent = r[(r.t_sent >= a) & (r.t_sent < b) & ~is_burst_request(run).reindex(r.index, fill_value=False)]
    return {"unsent": int(planned.t_sent.isna().sum()),
            "turn0_share": float((sent.turn == 0).mean()) if len(sent) else math.nan}


def reg16_control_outcome(base_ok: bool | None, v: str, cw: dict, persistent: bool | None, back: bool | None) -> str:
    """REG-16's outcome, in this order (the baseline is the burst run's window, `REG16["baseline"]`):
    - bad_baseline: the baseline's pf is under `min_baseline_pf` (base_ok False), or the watch verdict is `bad_baseline`
      on its own 480-1080 s baseline (review N3: fixed by the schedule, so a rerun cannot change it); the owner decides;
    - inconclusive: the baseline pf is NaN (base_ok None);
    - control_cold_persistent: `cold_persistent` is True (cold at a phase's end, or a cold stretch of `persistent_s`
      or more), or the watch verdict is `stuck`: the warm state did not last on this schedule without a burst;
    - inconclusive: `cold_persistent` is None (a phase's last window missing right after a cold window);
    - control_cold_transient: some window is cold, every cold stretch ended inside its phase and was shorter than
      `persistent_s` (review T1);
    - inconclusive: any other missing value: the watch verdict `unclear`, a window, or the return's end;
    - control_unclear: never cold, but some window has a low hit with a queue (`hit_low_queued`, review T2);
    - control_not_recovered: the watch verdict is not `recovered`, or the return's end is not `recovered_against` the
      baseline (a queue, not the cache);
    - control_warm: never cold, no low-hit queued window, the watch `recovered` and the return's end `recovered`.
    A cold window decides even if another value is missing."""
    if base_ok is False or v == "bad_baseline":
        return "bad_baseline"
    if base_ok is None:
        return "inconclusive"
    if persistent is True or v == "stuck":
        return "control_cold_persistent"
    if persistent is None:
        return "inconclusive"
    if any(x is True for x in cw["cold"]):
        return "control_cold_transient"
    if v == "unclear" or any(x is None for x in cw["cold"] + cw["hit_low_queued"]) or back is None:
        return "inconclusive"
    if any(x is True for x in cw["hit_low_queued"]):
        return "control_unclear"
    return "control_warm" if v == "recovered" and back else "control_not_recovered"


REG16_CONTROL = "stage2_control_l1pl350cl_r2.2_long_s14"


def reg16_check(run: dict) -> None:
    """Refuses a run that is not valid, or whose config differs from the registered file on any key that file sets
    (review N6: this also pins seed, λ, closed loop, force_close, 350 W and no trigger)."""
    if not (run["checks"] and run["checks"]["valid"]):
        raise ValueError(f"{run['dir'].name} is not valid")
    flat = lambda d, p="": {k2: v2 for k, v in d.items()
                            for k2, v2 in (flat(v, p + k + ".") if isinstance(v, dict) else {p + k: v}).items()}
    reg, got = flat(_burst_cfg(REG16_CONTROL)), flat(run["cfg"])
    diff = sorted(k for k in reg if got.get(k) != reg[k])
    if diff or (run["cfg"].get("trigger") or {}).get("kind") is not None:
        raise ValueError(f"{run['dir'].name} is not REG-16's registered control (differs on {diff[:5]})")


def reg16_table(seed: int = 14) -> dict:
    """REG-16's result: the latest valid control of the pattern (`reg10_pick`), its outcome, and readouts (never
    decisive): where the first cold window falls, the highest 120 s λp in the 600 s before it, both baselines,
    the timeline."""
    from analysis.load import find_runs
    run = reg10_pick(find_runs(REG16["control_pattern"].format(seed=seed)))
    reg16_check(run)
    ph, v = reg16_phases(run), verdict(run)
    base = _level(run, *REG16["baseline"])
    base_ok = None if np.isnan(base["pf"]) else bool(base["pf"] >= run["cfg"]["verdict"]["min_baseline_pf"])
    cw = cold_windows(run, base, ph["watch"][0], ph["return"][1])
    persistent = cold_persistent(cw, [ph["watch"][1], ph["drop"][1], ph["return"][1]])
    back = recovered_against(run, base, *ph["return_end"])
    first = next((w for w, x in zip(cw["windows"], cw["cold"]) if x is True), None)
    peak = None
    if first is not None:
        lo = max(0.0, first[0] - 600.0)
        peak = max(planned_session_rate(run, t, t + 120) for t in np.arange(lo, first[0] - 120 + 1e-9, 60.0))
    return {"run": run["dir"].name, "v_watch": v["verdict"], "verdict_baseline": v["baseline"], "baseline": base,
            "watch_end_level": v["end"], "return_end_level": _level(run, *ph["return_end"]), "return_recovered": back,
            "phases": ph, "cold_windows": cw, "first_cold": first, "longest_cold_s": longest_cold_s(cw),
            "window_mix": [window_mix(run, lo, hi) for lo, hi in cw["windows"]],
            "first_cold_phase": None if first is None else next(k for k in ("watch", "drop", "return")
                                                                 if ph[k][0] <= first[0] < ph[k][1]),
            "peak_120s_before_first_cold": peak,
            "outcome": reg16_control_outcome(base_ok, v["verdict"], cw, persistent, back),
            "timeline": reg15_timeline(run)}


def reg16_inputs() -> dict:
    """REG-16's design inputs from the config alone (no run): session requests, planned λp per phase, the 120 s
    windows above λ per phase, and the drain prediction for REG-17's burst run."""
    from harness.workload import build_schedule
    c = _burst_cfg("stage2_control_l1pl350cl_r2.2_long_s14")
    b = _burst_cfg("confirm_l1pl350cl_r2.2_long_s14")
    s, _ = build_schedule(c["workload"], c["seed"], c.get("trigger"))
    rate = lambda lo, hi: float(((s.t_planned >= lo) & (s.t_planned < hi)).sum() / (hi - lo))
    ph = reg16_phases({"dir": Path("x"), "cfg": c})
    peaks = {k: max(rate(t, t + 120) for t in np.arange(a, bb - 120 + 1e-9, 60.0))
             for k, (a, bb) in [("baseline", ph["baseline"]), ("watch", ph["watch"]), ("drop", ph["drop"]),
                                ("return", ph["return"])]}
    cal = reg16_calibration()
    return {"n_session": len(s), "lam_p": {"verdict_baseline": rate(*ph["baseline"]), "baseline": rate(*REG16["baseline"]),
                                           **{k: rate(*ph[k]) for k in ("watch", "drop", "return", "return_end")}},
            "peak_120s": peaks, "n_120s_above": {k: int(sum(rate(t, t + 120) > 3.0 for t in np.arange(a, bb - 120 + 1e-9, 60.0)))
                                                  for k, (a, bb) in [("watch", ph["watch"]), ("return", ph["return"])]},
            "judged_lam_p": reg16_judged_windows(b), "empty_s": reg16_empty_time(b, cal),
            "empty_s_pessimistic": reg16_empty_time(b, cal, pessimistic=True), "calibration": cal}


# ---------------------------------------------------------------- surge statistic (reviewer session, 2026-11-10)
# The reviewer session's exploratory reading (owner-approved for commit, 2026-11-10): no-burst collapses follow a short
# surge of planned arrivals, not a sustained mean above a capacity. These functions reproduce it from committed code.
# The settings below are the reviewer's, fixed as found; they were chosen with the data in view (rule A5: a readout,
# not a registered threshold, until a registration fixes it).

SURGE = {"pattern": "*_l1pl350cl_*",   # every closed-loop run at L1, 350 W (REG-11 to REG-16)
         "window_s": 120.0, "grid_s": 5.0, "start_s": 240.0,
         "kv_onset": 0.9, "kv_roll_s": 60, "kv_min_periods": 30,
         "lead_s": 60.0,      # a tipped run's warm time ends this long before its KV onset
         "tip_s": 180.0,      # the surge that tipped it: the peak in the last tip_s of its warm time
         "hazard_cfg": "stage2_control_l1pl350cl_r2.2_s2", "hazard_seeds": tuple(range(1, 41)),
         "hazard_lams": (1.8, 1.9, 2.0, 2.1, 2.2, 2.4), "hazard_s": 8000.0,
         "hazard_horizons": (2600.0, 5600.0, 8000.0), "hazard_thresholds": (3.0, 3.2, 3.4)}


def rolling_rate(t: np.ndarray, grid: np.ndarray, window_s: float) -> np.ndarray:
    """Events per second in [g - window_s, g) for each grid point g; `t` need not be sorted."""
    t = np.sort(np.asarray(t, float))
    return (np.searchsorted(t, grid) - np.searchsorted(t, grid - window_s)) / window_s


def kv_onset(run: dict) -> float:
    """The first scrape time whose trailing kv_roll_s mean KV usage is >= kv_onset (at least kv_min_periods scrapes
    in the window); NaN if never."""
    m = run["metrics"]
    if "vllm:kv_cache_usage_perc" not in m or not len(m):
        return math.nan
    k = pd.Series(m["vllm:kv_cache_usage_perc"].to_numpy(float), index=pd.to_timedelta(m.t.to_numpy(float), unit="s"))
    k = k.rolling(f"{SURGE['kv_roll_s']}s", min_periods=SURGE["kv_min_periods"]).mean()
    hit = k[k >= SURGE["kv_onset"]]
    return float(hit.index[0].total_seconds()) if len(hit) else math.nan


def surge_run(run: dict) -> dict:
    """One run's warm time and its 120 s planned-rate peaks (session requests only, by t_planned). Warm time runs from
    start_s to: the trigger's start (a burst run); KV onset - lead_s (a run with no burst that reached the onset:
    `tipped`); the end of arrivals otherwise. For a tipped run, `peak_tip` is the highest 120 s rate in the last tip_s
    of its warm time and `peak_before` the highest before that; otherwise `peak_before` covers all warm time."""
    cfg, q = run["cfg"], run["requests"]
    burst = (cfg.get("trigger") or {}).get("kind") == "burst"
    s = q[~is_burst_request(run) & q.turn.notna()]
    on = kv_onset(run)
    tipped = (not burst) and np.isfinite(on)
    end = float(cfg["trigger"]["at_s"]) if burst else (on - SURGE["lead_s"] if tipped else float(cfg["workload"]["duration_s"]))
    grid = np.arange(SURGE["start_s"], end, SURGE["grid_s"])
    x = rolling_rate(s.t_planned.to_numpy(float), grid, SURGE["window_s"])
    out = {"run": run["dir"].name, "lam": float(cfg["workload"]["rate"]), "burst": burst, "onset": on,
           "tipped": tipped, "warm_s": max(0.0, end - SURGE["start_s"]), "peak_tip": math.nan, "peak_before": math.nan}
    pre = grid >= end - SURGE["tip_s"] if tipped else np.zeros(len(grid), bool)
    if pre.any():
        out["peak_tip"] = float(x[pre].max())
    if (~pre).any():
        out["peak_before"] = float(x[~pre].max())
        out["t_peak_before"] = float(grid[~pre][x[~pre].argmax()])
    return out


def surge_table() -> dict:
    """`surge_run` on every valid closed-loop L1 350 W run, and the summary: tipped runs and the range of their tipping
    peaks; the highest peak in warm time that did not tip (and its run); total warm seconds."""
    from analysis.load import find_runs
    rows = [surge_run(r) for r in find_runs(SURGE["pattern"]) if closed_loop(r)]
    tip = [r for r in rows if r["tipped"]]
    calm = [r for r in rows if np.isfinite(r["peak_before"])]
    top = max(calm, key=lambda r: r["peak_before"]) if calm else None
    return {"runs": rows, "n_runs": len(rows), "n_tipped": len(tip),
            "tipped": [r["run"] for r in tip],
            "peak_tip_range": (min(r["peak_tip"] for r in tip), max(r["peak_tip"] for r in tip)) if tip else None,
            "max_peak_not_tipping": None if top is None else (top["peak_before"], top["run"]),
            "warm_s_total": float(sum(r["warm_s"] for r in rows))}


def schedule_peak_series(cfg: dict, lam: float, seed: int, duration_s: float) -> tuple[np.ndarray, np.ndarray]:
    """Schedule only (no run): the 120 s planned session rate on the grid from start_s, for `cfg`'s workload at
    rate `lam`, `seed` and `duration_s`, with no steps and no trigger."""
    from harness.workload import build_schedule
    s, _ = build_schedule({**cfg["workload"], "rate": lam, "duration_s": duration_s, "steps": None}, seed, None)
    grid = np.arange(SURGE["start_s"], duration_s, SURGE["grid_s"])
    return grid, rolling_rate(s.t_planned.to_numpy(float), grid, SURGE["window_s"])


def surge_hazard() -> dict:
    """Schedule only: per λ and threshold, how many of the hazard seeds reach a 120 s planned rate >= the threshold
    before each horizon, on REG-14's control workload; and the median of each seed's highest 120 s rate before the
    first horizon."""
    cfg = _burst_cfg(SURGE["hazard_cfg"])
    out = {}
    for lam in SURGE["hazard_lams"]:
        first = {thr: [] for thr in SURGE["hazard_thresholds"]}
        mx = []
        for sd in SURGE["hazard_seeds"]:
            g, x = schedule_peak_series(cfg, lam, sd, SURGE["hazard_s"])
            for thr in first:
                i = np.flatnonzero(x >= thr)
                first[thr].append(float(g[i[0]]) if len(i) else math.inf)
            mx.append(float(x[g < SURGE["hazard_horizons"][0]].max()))
        out[lam] = {"n_seeds": len(SURGE["hazard_seeds"]),
                    "counts": {thr: {h: int(sum(t < h for t in ts)) for h in SURGE["hazard_horizons"]}
                               for thr, ts in first.items()},
                    "median_peak_first_horizon": float(np.median(mx))}
    return out


def pair_schedule(lam: float, seed: int, name: str = "burst_l1pl350cl_r2.2_s2") -> dict:
    """Schedule only: REG-14's burst config at `lam` and `seed`. The highest 120 s planned session rate up to the burst's
    start and over the whole run (and when); λp in the baseline (300-900 s), over the watch (the burst's end + watch_s)
    and in its three thirds."""
    from harness.workload import build_schedule
    b = _burst_cfg(name)
    s, _ = build_schedule({**b["workload"], "rate": lam}, seed, b["trigger"])
    tp = s[~s.burst].t_planned.to_numpy(float)
    dur, at = float(b["workload"]["duration_s"]), float(b["trigger"]["at_s"])
    g = np.arange(SURGE["start_s"], dur, SURGE["grid_s"])
    x = rolling_rate(tp, g, SURGE["window_s"])
    rate = lambda a, z: float(((tp >= a) & (tp < z)).sum() / (z - a))
    te, w = at + float(b["trigger"]["duration_s"]), float(b["verdict"]["watch_s"])
    return {"lam": lam, "seed": seed, "peak_pre_burst": float(x[g <= at].max()), "peak_run": float(x.max()),
            "t_peak_run": float(g[x.argmax()]), "lam_p_baseline": rate(at - 600.0, at), "lam_p_watch": rate(te, te + w),
            "lam_p_watch_thirds": [rate(te + i * w / 3, te + (i + 1) * w / 3) for i in range(3)]}


def surge_pair_inputs(lams=(2.0, 2.1, 2.2), seeds=tuple(range(2, 8))) -> dict:
    """`pair_schedule` for seeds 2-7 at each λ (design inputs for a pair on REG-14's design; no run)."""
    return {lam: [pair_schedule(lam, sd) for sd in seeds] for lam in lams}



# REG-17 draft (docs/decisions.md 2026-11-10 [REG]): REG-14's seed-2 pair at λ = 2.0, the only change. Decided by C1's
# per-seed test (REG-12's: burst `stuck`, control `recovered`) plus a measured cold side (review T2), not by the span
# test: at λ = 2.0 a span confirms a cold rate only up to 1.81 req/s (`span_sensitivity`), inside the cold rates seen
# (1.72-1.90: REG-14 c 1.73-1.81, REG-15 span c 1.72-1.90), so the span label is a readout. The control's tip, if any,
# is read by `surge_run`.
REG17 = {**REG14, "lam": 2.0, "seed": 2,
         "control": "*_stage2_control_l1pl350cl_r2.0_s2", "burst": "*_burst_l1pl350cl_r2.0_s2",
         "surge_tip": 3.2,     # splits a control's tip by its 120 s peak; a covariate found in the data, not a tip
                               # threshold (review N2): tips 3.24-3.49 overlap untipped peaks up to 3.32 (`surge_table`)
         "max_control_waiting": 0.5}   # REG-14's: share of a span's scrapes with waiting > 0


def reg17_cold_side(burst: dict) -> dict:
    """Review T2, registered before any run: the cold state completes below the load it faces. In every REG-8 span
    after the burst's end, the point completion rate (`completion_rate`, all requests by t_end) is below min(λ, the
    span's λp); and the verdict's end-window queue slope is > 0. `holds` is None if any value is NaN."""
    end, lam = burst_end(burst), REG17["lam"]
    rows = []
    for a, b in REG8["spans"]:
        c, lp = completion_rate(burst, end + a, end + b), planned_session_rate(burst, end + a, end + b)
        rows.append({"span": (a, b), "c": c, "lam_p": lp,
                     "below": None if not (np.isfinite(c) and np.isfinite(lp)) else bool(c < min(lam, lp))})
    slope = verdict(burst)["end"]["q_slope"]
    vals = [r["below"] for r in rows] + [None if not np.isfinite(slope) else bool(slope > 0)]
    return {"spans": rows, "end_q_slope": slope, "holds": None if None in vals else all(vals)}


def reg17_outcome(cv: str, bv: str, control_surge: dict, control_waiting: list[dict],
                  cold_side: bool | None = True) -> str:
    """In this order (review T1):
    `bad_baseline` (either run);
    control not `recovered`: `control_cold_surge` if it tipped (KV onset) after a 120 s peak >= surge_tip,
    `control_cold_no_surge` if it tipped otherwise (the surge reading is wrong), `control_unclear` if it did not tip and
    its verdict is `unclear` (an instrument gap is not a refutation), `control_warm_queue` if it did not tip (queued
    without going cold);
    burst `stuck`: `stuck_draining` unless the cold side holds (`reg17_cold_side`; None gives `inconclusive`), then
    `pass_clear` if the control had waiting > 0 in at most max_control_waiting of the scrapes of every span, else
    `pass_warm_edge` (also when a share is NaN);
    `drains` (burst `recovered` or `slow_drain`); `unclear` (burst `unclear`)."""
    if "bad_baseline" in (cv, bv):
        return "bad_baseline"
    if cv != "recovered":
        if control_surge.get("tipped"):
            pk = control_surge.get("peak_tip", math.nan)
            return "control_cold_surge" if np.isfinite(pk) and pk >= REG17["surge_tip"] else "control_cold_no_surge"
        return "control_unclear" if cv == "unclear" else "control_warm_queue"
    if bv == "stuck":
        if cold_side is None:
            return "inconclusive"
        if not cold_side:
            return "stuck_draining"
        sh = [w["share_waiting"] for w in control_waiting]
        clear = bool(sh) and all(np.isfinite(x) and x <= REG17["max_control_waiting"] for x in sh)
        return "pass_clear" if clear else "pass_warm_edge"
    if bv in ("recovered", "slow_drain"):
        return "drains"
    return "unclear"


def drain_time(burst: dict, grid_s: float = 10.0) -> float:
    """REG-17 readout (review T4): seconds after the burst's end until the first scrape with 0 waiting that is followed
    by 0 waiting for 30 s; NaN if never before the end of arrivals. Read against the watch's thirds."""
    m, end = burst["metrics"], burst_end(burst)
    w = m[(m.t >= end) & (m.t < float(burst["cfg"]["workload"]["duration_s"]))]
    t, q = w.t.to_numpy(float), w["vllm:num_requests_waiting"].to_numpy(float)
    for i in np.flatnonzero(q == 0):
        if (q[(t >= t[i]) & (t < t[i] + 30.0)] == 0).all():
            return float(t[i] - end)
    return math.nan


def reg17_gate() -> dict:
    """REG-17's result: `reg10_gate` on the λ = 2.0 seed-2 pair (verdicts and the span label), REG-14's readouts, the
    surge readouts of both runs, and `reg17_outcome`."""
    from analysis.load import RUNS, load_run
    res = reg10_gate(REG17)
    control, burst = (load_run(RUNS / n) for n in res["runs"])
    for r in (control, burst):
        if r["cfg"]["seed"] != REG17["seed"]:
            raise ValueError(f"{r['dir'].name} is not seed {REG17['seed']}")
    end = burst_end(burst)
    res["post_trigger"] = post_trigger_rate(burst)
    res["max_holding_c"] = [max_holding_c(REG17["lam"], r["lam_p"], r["span"][1] - r["span"][0], REG8["conf"])
                            for r in res["spans"]]
    res["release_rate"] = release_rate(burst, REG8["spans"])
    res["control_waiting"] = control_waiting(control, [(end + a, end + b) for a, b in REG8["spans"]])
    res["reference"] = shock_size(load_run(RUNS / REG17["reference_run"]))
    res["surge_control"], res["surge_burst"] = surge_run(control), surge_run(burst)
    res["cold_side"], res["drain_time_s"] = reg17_cold_side(burst), drain_time(burst)
    res["outcome"] = reg17_outcome(res["control_verdict"], res["burst_verdict"], res["surge_control"],
                                   res["control_waiting"], res["cold_side"]["holds"])
    return res


def reg17_inputs() -> dict:
    """REG-17's design inputs from the configs alone (no run): the pair schedule, REG-14's span test limits at
    λ = 2.0, whether the control's schedule equals the burst run's session rows, and the surge hazard row at 2.0."""
    from harness.workload import build_schedule
    c, b = _burst_cfg("stage2_control_l1pl350cl_r2.0_s2"), _burst_cfg("burst_l1pl350cl_r2.0_s2")
    sc, _ = build_schedule(c["workload"], c["seed"], c.get("trigger"))
    sb, _ = build_schedule(b["workload"], b["seed"], b["trigger"])
    s = sb[~sb.burst].reset_index(drop=True)
    same = len(s) == len(sc) and bool((s.t_planned.values == sc.t_planned.values).all()
                                      and (s.prompt_len.values == sc.prompt_len.values).all())
    g, x = schedule_peak_series({"workload": {**c["workload"], "steps": None}}, REG17["lam"], c["seed"],
                                float(c["workload"]["duration_s"]))
    return {"pair": pair_schedule(REG17["lam"], REG17["seed"], "burst_l1pl350cl_r2.0_s2"),
            "spans": span_sensitivity(REG17["lam"], REG17["seed"])["spans"],
            "control_schedule_same": same, "n_session": len(s), "n_burst": int(sb.burst.sum()),
            "control_peak": float(x.max()), "lam_cfg": (c["workload"]["rate"], b["workload"]["rate"]),
            "seeds": (c["seed"], b["seed"])}


if __name__ == "__main__":
    import sys
    if sys.argv[1] in ("reg10", "reg11", "reg11_reference", "reg11_turn0_reference", "reg12", "reg13", "reg13_inputs",
                       "reg14", "reg14_inputs", "reg14_sensitivity",
                       "reg15", "reg15_inputs", "reg16", "reg16_inputs", "reg16_seed_rule",
                       "surge", "surge_hazard", "surge_pair_inputs", "reg17", "reg17_inputs"):
        print({"reg10": reg10_gate, "reg11": reg11_gate, "reg11_reference": reg11_reference,
               "reg11_turn0_reference": reg11_turn0_reference, "reg12": reg12_table, "reg13": reg13_table,
               "reg13_inputs": reg13_inputs, "reg14": reg14_gate, "reg14_inputs": reg14_inputs,
               "reg14_sensitivity": reg14_sensitivity, "reg15": reg15_table, "reg15_inputs": reg15_inputs,
               "reg16": reg16_table, "reg16_inputs": reg16_inputs, "reg16_seed_rule": reg16_seed_rule,
               "surge": surge_table, "surge_hazard": surge_hazard, "surge_pair_inputs": surge_pair_inputs,
               "reg17": reg17_gate, "reg17_inputs": reg17_inputs}[sys.argv[1]]())
    else:
        print({"reg7": reg7_zone, "reg8": reg8_zone}[sys.argv[1]]())   # no default: say which registration is computed
