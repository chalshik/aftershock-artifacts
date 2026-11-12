"""Model F replayed on one run's own schedule (REG-21, rule F review recommendation 1). BELIEF as to the model.

The long-run values of `analysis/modelf.py` describe the self-similar regime that a trap reaches after many cycles;
a 900 s window that ends 1500 s after a burst is not there yet, and the turn gaps and the burst's size move it
(review T1, T2). This module replays the run's schedule instead, through model F's server:
  - one first-come-first-served server, one request at a time (model F's fluid FIFO server, made discrete);
  - session starts and burst requests arrive at their planned times (open loop); a later turn k is released at the end
    of turn k - 1 plus the schedule's gap t_planned[k] - t_planned[k-1] (harness/loadgen.py:101, closed loop); with
    open-loop turns it is released at its planned time;
  - a request costs cost(L) = (a + b L) / ((a + b Lbar) mu) seconds, where L is the tokens it must prefill, Lbar = 3072
    is the stationary mean prompt at L1 and mu is the all-miss capacity in req/s at the stationary mix (so the
    stationary mean cost is 1 / mu); (a, b) = (0, 1) is cost proportional to the prompt, REG21["fixed_cost"] the
    alternative with a fixed part;
  - warm until the burst starts (a later turn prefills only its new tokens, L - previous prompt; turn 0 and burst
    requests prefill everything), every request a miss from then on (from t = 0 when caching is off). The real server
    goes cold during the burst, not at its start; the window W starts 600 s after the burst's end.
The schedule is rebuilt from the run's config with `harness.workload.build_schedule` (the same code and seeds the
harness used), so no run output is read here.
"""
from __future__ import annotations

import heapq
import math

import numpy as np
import pandas as pd

from harness.workload import build_schedule

LBAR = 3072.0


def schedule(cfg: dict) -> pd.DataFrame:
    trig = cfg.get("trigger") if (cfg.get("trigger") or {}).get("kind") == "burst" else None
    df, _ = build_schedule(cfg["workload"], cfg["seed"], trig)
    return df


def _cost_fn(mu: float, cost: tuple[float, float]):
    a, b = cost
    unit = (a + b * LBAR) * mu
    return lambda L: (a + b * L) / unit


def simulate(cfg: dict, mu: float, cost: tuple[float, float] = (0.0, 1.0), sched: pd.DataFrame | None = None,
             all_miss_from: float | None = None) -> pd.DataFrame:
    """One model-F trajectory on the run's schedule. Returns one row per request served, with the columns the k3
    readouts use (session_id, turn, t_planned, t_sent, t_first_token, t_end, status, prompt_tokens,
    prompt_tokens_planned, cached_tokens). `all_miss_from` defaults to the burst's start, or 0 with caching off, or
    never when there is neither."""
    sched = schedule(cfg) if sched is None else sched
    wl = cfg["workload"]
    closed = bool((wl.get("sessions") or {}).get("closed_loop"))
    if all_miss_from is None:
        trig = cfg.get("trigger") or {}
        caching = bool(((cfg.get("server") or {}).get("args") or {}).get("--enable-prefix-caching", True))
        all_miss_from = 0.0 if not caching else (float(trig["at_s"]) if trig.get("kind") == "burst" else math.inf)
    c = _cost_fn(mu, cost)
    s = sched.sort_values(["session_id", "turn"]).reset_index(drop=True)
    burst = s["burst"].fillna(False).astype(bool).to_numpy() if "burst" in s else np.zeros(len(s), bool)
    sid, turn = s.session_id.to_numpy(), s.turn.to_numpy()
    tp, L = s.t_planned.to_numpy(float), s.prompt_len.to_numpy(float)
    nxt = np.full(len(s), -1)
    same = (sid[1:] == sid[:-1]) & (turn[1:] == turn[:-1] + 1)
    nxt[:-1][same] = np.arange(1, len(s))[same]
    prev_len = np.zeros(len(s))
    prev_len[1:][same] = L[:-1][same]
    heap = []
    for i in range(len(s)):
        if turn[i] == 0 or burst[i] or not closed:
            heapq.heappush(heap, (tp[i], i))
    t_free = 0.0
    rel = np.full(len(s), np.nan)
    start, end, cached = rel.copy(), rel.copy(), np.zeros(len(s))
    while heap:
        r, i = heapq.heappop(heap)
        st = max(t_free, r)
        miss = st >= all_miss_from
        hit = 0.0 if (miss or turn[i] == 0 or burst[i]) else prev_len[i]
        t_free = st + c(L[i] - hit)
        rel[i], start[i], end[i], cached[i] = r, st, t_free, hit
        j = nxt[i]
        if closed and j >= 0 and not burst[i]:
            heapq.heappush(heap, (t_free + tp[j] - tp[i], j))
    out = pd.DataFrame({"session_id": sid, "turn": turn, "t_planned": tp, "t_sent": rel, "t_first_token": start,
                        "t_end": end, "prompt_tokens": L.astype(int), "prompt_tokens_planned": L.astype(int),
                        "cached_tokens": cached.astype(int), "burst": burst})
    out["status"] = np.where(np.isnan(end), "unsent", "ok")
    return out


def as_run(cfg: dict, reqs: pd.DataFrame, name: str = "sim") -> dict:
    """A run-like dict for the k3 readouts (no metrics)."""
    from pathlib import Path
    return {"cfg": cfg, "requests": reqs, "metrics": pd.DataFrame(), "dir": Path(name)}
