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

if __name__ == "__main__":
    import sys
    if sys.argv[1] in ("reg10", "reg11", "reg11_reference", "reg11_turn0_reference", "reg12"):
        print({"reg10": reg10_gate, "reg11": reg11_gate, "reg11_reference": reg11_reference,
               "reg11_turn0_reference": reg11_turn0_reference, "reg12": reg12_table}[sys.argv[1]]())
    else:
        print({"reg7": reg7_zone, "reg8": reg8_zone}[sys.argv[1]]())   # no default: say which registration is computed
