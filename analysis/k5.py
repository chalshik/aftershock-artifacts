"""K5 (lead times): does a cache signal warn before latency degrades, and earlier than watching arrivals does?
Draft for REG-23; not registered. Never writes into runs/.

Events are natural departures from the warm state: runs with no trigger whose KV pool fills (`gate.kv_onset` finite).
Burst runs are not events: their onset is the trigger's. Signals are what an operator has, from the server's own
metrics, as trailing means on a grid:

  H  counter hit rate (hits / queries)            U  recomputed prefill tokens per second (prompt - cached)
  Q  mean requests waiting                        N  mean requests running
  L  latency: server time to first token (sum / count)
  A  session requests sent per second (the trivial warning)

Per event a reference window [ref_start_s, KV onset - ref_gap_s) gives each signal's mean and SD. A signal's onset is
the first grid time after the reference window from which it stays beyond its level for hold_s. The lead of X
is onset(L) - onset(X): positive when X moves before latency does. (The column is L, not T: `frame.T` is pandas'
transpose.)

K5 (docs/claims.md) says that U and H "change before latency and queue length do". So each warner's lead is taken
twice: over latency (onset(L) - onset(X)) and over the queue (onset(Q) - onset(X)).

A lead counts only above min_lead_s, the length of the trailing window: two signals that step at the same instant
cross their levels at different times (a level close to the reference mean is crossed sooner), so a lead inside one
window is not a lead.

Judged per signal and per comparator: "leads" only if at least min_events events have both onsets and every one of
them has a lead above min_lead_s; "no_lead" if the median lead is <= 0; "within_window" if the median is above 0 and
not above min_lead_s; "too_few" below min_events; otherwise "mixed". A signal is usable only if it leads both
latency and the queue and the same rule gives fewer than fa_per_hour_max onsets per hour on the runs that never
tipped. K5 as a whole holds ("cache_signal_leads") only if H or U is usable
with a median lead over latency above A's: if watching arrivals warns earlier, the cache signals add nothing.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from analysis.gate import kv_onset
from analysis.load import find_runs
from analysis.margin import is_burst_request

K5 = {
    # Every closed-loop L1 run at 350 W without a trigger made before REG-19 (controls of REG-11, 12, 14, 16, 17, 18
    # and REG-13's cache-on sweep), by folder name. A candidate must be valid; which of them tipped is the data.
    "runs": ("20261109-034255_stage2_control_l1pl350cl_r2.4", "20261109-055910_stage2_control_l1pl350cl_r2.4_s2",
             "20261109-085121_stage2_control_l1pl350cl_r2.4_s3", "20261109-102614_stage2_control_l1pl350cl_r2.4_s4",
             "20261109-120308_stage2_control_l1pl350cl_r2.4_s5", "20261109-134250_stage2_control_l1pl350cl_r2.4_s6",
             "20261109-142813_stage2_control_l1pl350cl_r2.4_s6", "20261109-190221_sweep_l1pl350cl_pc_on_r2",
             "20261109-191845_sweep_l1pl350cl_pc_on_r2.4", "20261109-193526_sweep_l1pl350cl_pc_on_r2.6",
             "20261109-195349_sweep_l1pl350cl_pc_on_r2.8", "20261109-201246_sweep_l1pl350cl_pc_on_r3",
             "20261110-055201_stage2_control_l1pl350cl_r2.2_s2", "20261110-122001_stage2_control_l1pl350cl_r2.2_long_s14",
             "20261110-174432_stage2_control_l1pl350cl_r2.0_s2", "20261111-093312_stage2_control_l1pl350cl_r2.0_s4",
             "20261111-110919_stage2_control_l1pl350cl_r2.0_s3", "20261111-124527_stage2_control_l1pl350cl_r2.0_s5",
             "20261111-142155_stage2_control_l1pl350cl_r2.0_s6"),
    "roll_s": 30.0, "grid_s": 5.0,          # signals: trailing means over roll_s on a grid of grid_s
    "arr_roll_s": 120.0,                    # A's window (gate.SURGE's window)
    "ref_start_s": 240.0, "ref_gap_s": 240.0, "ref_min_s": 120.0,   # the reference window and its least length
    "n_sd": 4.0,                            # a level is at least this many reference SDs from the reference mean
    "h_drop": 0.06,                         # H below mean - max(n_sd SD, h_drop)   (the verdict's stuck_hit_drop)
    "u_frac": 0.5,                          # U above mean + max(n_sd SD, u_frac x mean)
    "q_min": 1.0,                           # Q at least one request waiting on average
    "n_factor": 2.0,                        # N at least n_factor x mean (C2's factor)
    "ttft_s": 1.0,                          # L above max(mean + n_sd SD, ttft_s)   (the SLO)
    "arr_tip": 3.2,                         # A at least this (gate.SURGE's tip reading)
    "hold_s": 15.0,                         # an onset holds at every grid time of [t, t + hold_s]
    "min_events": 5,
    "min_lead_s": 30.0,                     # a lead counts only above this (the trailing window: see the docstring)
    "fa_ref": (240.0, 540.0), "fa_from": 540.0,   # never-tipped runs: reference window, and where the scan starts
    "fa_per_hour_max": 1.0,
}
COL = {"hits": "vllm:prefix_cache_hits_total", "queries": "vllm:prefix_cache_queries_total",
       "prompt": "vllm:prompt_tokens_total", "cached": "vllm:prompt_tokens_cached_total",
       "waiting": "vllm:num_requests_waiting", "running": "vllm:num_requests_running",
       "ttft_sum": "vllm:time_to_first_token_seconds_sum", "ttft_count": "vllm:time_to_first_token_seconds_count"}
SIGNALS = ("H", "U", "Q", "N", "L", "A")
WARNERS = ("H", "U", "Q", "N", "A")          # every signal but latency itself


def signals(run: dict) -> pd.DataFrame:
    """One row per grid time t: the six signals over the trailing window that ends at t. NaN where the window holds
    fewer than two scrapes, spans less than half of roll_s, or has nothing to divide by. Raises if a metric is
    missing or a counter goes down (a restart: flagged, not hidden)."""
    m = run["metrics"]
    miss = [c for c in COL.values() if c not in m]
    if not len(m) or miss:
        raise ValueError(f"metrics missing: {miss or 'no scrapes'}")
    m = m.dropna(subset=list(COL.values())).sort_values("t")
    t = m.t.to_numpy(float)
    for k in ("hits", "queries", "prompt", "cached", "ttft_sum", "ttft_count"):
        if (np.diff(m[COL[k]].to_numpy(float)) < 0).any():
            raise ValueError(f"the counter {COL[k]} goes down: a restart inside the run")
    roll = K5["roll_s"]
    grid = np.arange(roll, t.max() + 1e-9, K5["grid_s"])
    i1 = np.searchsorted(t, grid, side="right") - 1
    i0 = np.searchsorted(t, grid - roll, side="right") - 1
    ok = (i0 >= 0) & (i1 > i0)
    span = np.where(ok, t[np.maximum(i1, 0)] - t[np.maximum(i0, 0)], np.nan)
    ok &= span >= roll / 2

    def delta(k: str) -> np.ndarray:
        v, out = m[COL[k]].to_numpy(float), np.full(len(grid), np.nan)
        out[ok] = v[i1[ok]] - v[i0[ok]]
        return out

    def mean(k: str) -> np.ndarray:
        cs, out = np.concatenate([[0.0], np.cumsum(m[COL[k]].to_numpy(float))]), np.full(len(grid), np.nan)
        out[ok] = (cs[i1[ok] + 1] - cs[i0[ok] + 1]) / (i1[ok] - i0[ok])
        return out

    with np.errstate(divide="ignore", invalid="ignore"):
        dq, dc = delta("queries"), delta("ttft_count")
        h = np.where(dq > 0, delta("hits") / dq, np.nan)
        u = (delta("prompt") - delta("cached")) / span
        ttft = np.where(dc > 0, delta("ttft_sum") / dc, np.nan)
    q = run["requests"]
    sent = np.sort(q[~is_burst_request(run)].t_sent.dropna().to_numpy(float))
    w = K5["arr_roll_s"]
    a = (np.searchsorted(sent, grid, side="right") - np.searchsorted(sent, grid - w, side="right")) / w
    a = np.where(grid >= w, a, np.nan)
    return pd.DataFrame({"t": grid, "H": h, "U": u, "Q": mean("waiting"), "N": mean("running"), "L": ttft, "A": a})


def reference(sig: pd.DataFrame, a: float, b: float) -> dict | None:
    """Mean and SD of each signal over the grid times whose trailing window lies inside [a, b); None if the window
    is shorter than ref_min_s or a signal has fewer than two values there."""
    if b - a < K5["ref_min_s"]:
        return None
    w = sig[(sig.t >= a + K5["roll_s"]) & (sig.t < b)]
    out = {}
    for k in ("H", "U", "Q", "N", "L"):
        v = w[k].dropna()
        if len(v) < 2:
            return None
        out[k] = (float(v.mean()), float(v.std(ddof=1)))
    return out


def levels(ref: dict) -> dict:
    """For each signal, the side and the level beyond which it counts as moved."""
    sd = K5["n_sd"]
    return {"H": ("below", ref["H"][0] - max(sd * ref["H"][1], K5["h_drop"])),
            "U": ("above", ref["U"][0] + max(sd * ref["U"][1], K5["u_frac"] * ref["U"][0])),
            "Q": ("at_least", K5["q_min"]),
            "N": ("at_least", K5["n_factor"] * ref["N"][0]),
            "L": ("above", max(ref["L"][0] + sd * ref["L"][1], K5["ttft_s"])),
            "A": ("at_least", K5["arr_tip"])}


def crossings(sig: pd.DataFrame, col: str, side: str, level: float, start: float, stop: float = math.inf) -> list[float]:
    """The onsets in [start, stop): grid times from which the signal stays beyond its level for hold_s (at every grid
    time of [t, t + hold_s]), and from which it did not at the grid time before (or which is the first one scanned).
    A NaN is never beyond a level."""
    v, t = sig[col].to_numpy(float), sig.t.to_numpy(float)
    with np.errstate(invalid="ignore"):
        beyond = {"below": v < level, "above": v > level, "at_least": v >= level}[side]
    held = beyond.copy()
    for j in range(1, int(round(K5["hold_s"] / K5["grid_s"])) + 1):          # beyond at every grid time of [t, t + hold_s]
        held &= np.concatenate([beyond[j:], np.zeros(j, bool)])
    scan = (t >= start) & (t < stop)
    held_before = np.concatenate([[False], held[:-1]])
    scanned_before = np.concatenate([[False], scan[:-1]])
    # an onset: held now, and either not held at the grid time before or that time was not scanned (the scan's start)
    return [float(x) for x in t[scan & held & ~(held_before & scanned_before)]]


def event(run: dict) -> dict:
    """One run with no trigger: its KV onset, reference window, the first onset of every signal after that window,
    and each warner's lead over latency. `why` says why it is not an event."""
    out = {"run": run["dir"].name, "lam": float(run["cfg"]["workload"]["rate"]), "kv_onset": kv_onset(run)}
    if math.isnan(out["kv_onset"]):
        return {**out, "why": "never tipped"}
    a, b = K5["ref_start_s"], out["kv_onset"] - K5["ref_gap_s"]
    try:
        sig = signals(run)
    except ValueError as e:
        return {**out, "why": str(e)}
    ref = reference(sig, a, b)
    if ref is None:
        return {**out, "why": "no reference"}
    lv = levels(ref)
    on = {k: (crossings(sig, k, *lv[k], start=b) or [math.nan])[0] for k in SIGNALS}
    return {**out, "why": None, "ref": (a, b), "levels": {k: lv[k][1] for k in lv}, "onsets": on,
            "leads": {k: on["L"] - on[k] for k in WARNERS},
            "leads_over_queue": {k: on["Q"] - on[k] for k in WARNERS if k != "Q"}}


def quiet(run: dict) -> dict:
    """A run that never tipped: how many onsets each rule gives after fa_from, and over how many hours."""
    out = {"run": run["dir"].name, "lam": float(run["cfg"]["workload"]["rate"])}
    end = float(run["cfg"]["workload"]["duration_s"])
    try:
        sig = signals(run)
    except ValueError as e:
        return {**out, "why": str(e)}
    ref = reference(sig, *K5["fa_ref"])
    if ref is None or end <= K5["fa_from"]:
        return {**out, "why": "no reference"}
    lv = levels(ref)
    return {**out, "why": None, "hours": (end - K5["fa_from"]) / 3600.0,
            "alarms": {k: len(crossings(sig, k, *lv[k], start=K5["fa_from"], stop=end)) for k in SIGNALS}}


def _lead_label(leads: list[float]) -> dict:
    leads = [x for x in leads if not math.isnan(x)]
    med, least = (float(np.median(leads)) if leads else math.nan), K5["min_lead_s"]
    if not leads:
        label = "too_few"
    elif med <= 0:
        label = "no_lead"
    elif med <= least:
        label = "within_window"
    elif len(leads) < K5["min_events"]:
        label = "too_few"
    else:
        label = "leads" if all(x > least for x in leads) else "mixed"
    return {"n": len(leads), "k_above_window": sum(x > least for x in leads), "k_positive": sum(x > 0 for x in leads),
            "median_lead_s": med, "min_lead_s": min(leads) if leads else math.nan, "label": label}


def judge(events: list[dict], quiets: list[dict]) -> dict:
    """Per warner: its lead over latency and over the queue (n events with both onsets, how many lead, the median
    and the least lead, the label), the false alarms per hour on the never-tipped runs, and whether it is usable.
    Then K5's own label."""
    ev, qu = [e for e in events if e["why"] is None], [x for x in quiets if x["why"] is None]
    hours = sum(x["hours"] for x in qu)
    out = {"n_events": len(ev), "quiet_hours": hours, "signals": {}}
    for k in WARNERS:
        s = {"over_latency": _lead_label([e["leads"][k] for e in ev])}
        if k != "Q":
            s["over_queue"] = _lead_label([e["leads_over_queue"][k] for e in ev])
        fa = sum(x["alarms"][k] for x in qu) / hours if hours > 0 else math.nan
        s["false_alarms_per_hour"] = fa
        s["usable"] = (s["over_latency"]["label"] == "leads" and s.get("over_queue", {}).get("label") == "leads"
                       and not math.isnan(fa) and fa < K5["fa_per_hour_max"])
        out["signals"][k] = s
    a = out["signals"]["A"]["over_latency"]["median_lead_s"]
    better = [k for k in ("H", "U") if out["signals"][k]["usable"]
              and (math.isnan(a) or out["signals"][k]["over_latency"]["median_lead_s"] > a)]
    out["k5"] = "cache_signal_leads" if better else "no_usable_cache_lead"
    out["cache_signals_that_lead"] = better
    return out


def candidates() -> list[dict]:
    """The registered candidate runs that are valid, in order; raises if a folder is missing or has two valid runs."""
    out = []
    for name in K5["runs"]:
        got = find_runs(name, valid_only=False)
        if len(got) != 1:
            raise ValueError(f"K5 needs each registered run folder once: {name} gives {len(got)}")
        if got[0]["checks"] and got[0]["checks"]["valid"]:
            out.append(got[0])
    return out


def k5_table() -> dict:
    """K5 on the registered candidates: events (tipped), quiet runs (never tipped), the judged table. Once."""
    runs = candidates()
    events = [event(r) for r in runs]
    quiets = [quiet(r) for r, e in zip(runs, events) if e["why"] == "never tipped"]
    return {"n_candidates": len(K5["runs"]), "n_valid": len(runs), "judged": judge(events, quiets),
            "events": [e for e in events if e["why"] != "never tipped"], "quiet": quiets}


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) == 2 and sys.argv[1] == "k5":
        from analysis.k3w import _dirty
        if _dirty():
            raise SystemExit("analysis/ or tests/ holds modified or untracked files; K5 runs from committed code:\n" + _dirty())
        print(json.dumps(k5_table(), indent=1, default=str))
    else:
        raise SystemExit("usage: python -m analysis.k5 k5")
