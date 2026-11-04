"""Derived figures quoted in docs/decisions.md whose original code was never committed.

Each function is the reading of the decisions.md text that reproduces the published values; the readings,
and every value that still differs, are logged in docs/decisions.md (2026-11-04, "Derived figures moved into
analysis/"). Nothing here feeds `load.verdict`. Never writes into runs/.
"""
import numpy as np
import pandas as pd

from analysis.load import rates, window


def hit_between(metrics: pd.DataFrame, a: float, b: float) -> float:
    """Hit rate over [a, b) from the raw counters (interpolated at a and b), the same reading as `load._level`.
    NaN when the query counter does not rise or either counter goes down inside [a, b] (a restart), as in `_level`
    (decisions.md 2026-11-05 [CORR]; before, a negative difference gave a number)."""
    h, q = metrics["vllm:prefix_cache_hits_total"], metrics["vllm:prefix_cache_queries_total"]
    span = (metrics.t >= a) & (metrics.t <= b)
    if (np.diff(h[span].to_numpy()) < 0).any() or (np.diff(q[span].to_numpy()) < 0).any():
        return float("nan")
    dq = np.interp(b, metrics.t, q) - np.interp(a, metrics.t, q)
    return float((np.interp(b, metrics.t, h) - np.interp(a, metrics.t, h)) / dq) if dq > 0 else float("nan")


def trigger_times(run: dict) -> tuple[float, float] | None:
    """(start, end) of the shock: a burst's planned arrivals, or the successful wipe call. None for no trigger.
    Mirrors `load.verdict`, which is left unchanged."""
    spec, trig = run["cfg"].get("trigger") or {}, run["trigger"]
    if spec.get("kind") == "burst":
        return float(spec["at_s"]), float(spec["at_s"] + spec["duration_s"])
    if len(trig):
        w = trig[trig.success].iloc[0]
        return float(w.t_start), float(w.t_end)
    return None


def span_hits(run: dict, spans: list[tuple[float, float]], origin: float) -> dict[tuple[float, float], float]:
    """Counter hit rate over each span [origin + a, origin + b)."""
    return {(a, b): hit_between(run["metrics"], origin + a, origin + b) for a, b in spans}


def thirds(run: dict, how: str = "counter") -> list[float]:
    """Hit rate in each third of the measured window. `how`: "counter" (ratio of counter differences) or
    "mean_of_ratios" (mean of the per-scrape ratios, as `load.summarize` does)."""
    wl, m = run["cfg"]["workload"], run["metrics"]
    e = np.linspace(wl["warmup_s"], wl["duration_s"], 4)
    if how == "counter":
        return [hit_between(m, a, b) for a, b in zip(e, e[1:])]
    r = rates(m)
    return [float(r.hit_rate[(r.t >= a) & (r.t < b)].mean()) for a, b in zip(e, e[1:])]


def span_hit_spread(run: dict, span_s: float, start: float, end: float) -> dict:
    """Tiled spans of `span_s` from `start`: counter hit range and standard deviation."""
    hs = np.array([hit_between(run["metrics"], a, a + span_s) for a in np.arange(start, end - span_s + 1e-9, span_s)])
    return {"n": len(hs), "min": float(hs.min()), "max": float(hs.max()), "sd": float(hs.std(ddof=1))}


def adjacent_change(run: dict, span_s: float, step_s: float, start: float, end: float, rise: float) -> dict:
    """Change of counter hit rate between adjacent spans [t, t+s) and [t+s, t+2s), t sliding by `step_s`:
    share that rose by at least `rise`, and the 95th percentile of the absolute change."""
    m = run["metrics"]
    ts = np.arange(start, end - 2 * span_s + 1e-9, step_s)
    d = np.array([hit_between(m, t + span_s, t + 2 * span_s) - hit_between(m, t, t + span_s) for t in ts])
    return {"n": len(d), "rose_frac": float(np.mean(d >= rise)), "p95_abs_change": float(np.quantile(np.abs(d), .95))}


def working_set(schedule: pd.DataFrame, grid: np.ndarray) -> np.ndarray:
    """W(t) in tokens: the sum over active sessions of their latest planned prompt length. A session is active from
    its first turn's planned time to its last turn's planned time. Burst rows are left out."""
    s = schedule[~schedule.burst] if "burst" in schedule else schedule
    out = np.zeros(len(grid))
    for _, g in s.sort_values("t_planned").groupby("session_id"):
        t, p = g.t_planned.to_numpy(), g.prompt_len.to_numpy()
        lo, hi = np.searchsorted(grid, t[0], "left"), np.searchsorted(grid, t[-1], "right")
        if hi > lo:
            out[lo:hi] += p[np.searchsorted(t, grid[lo:hi], "right") - 1]
    return out


def kv_footprint(run: dict, a: float, b: float, capacity_tokens: float) -> float:
    """F in tokens: mean `kv_cache_usage_perc` over [a, b) times the pool size. Usage counts only blocks held by
    running requests (decisions.md 2026-11-01), so F is the running batch's footprint, not the cache."""
    m = run["metrics"]
    w = (m.t >= a) & (m.t < b)
    return float(m["vllm:kv_cache_usage_perc"][w].mean() * capacity_tokens)


def _later_turns(run: dict) -> pd.DataFrame:
    """Turns after the first, inside the measured window by planned arrival, with the previous turn's times."""
    q = run["requests"].sort_values(["session_id", "turn"]).copy()
    g = q.groupby("session_id")
    q["prev_turn"], q["prev_first"], q["prev_end"] = g.turn.shift(), g.t_first_token.shift(), g.t_end.shift()
    q = q[(q.turn > 0) & (q.prev_turn == q.turn - 1)]
    return window(q, run["cfg"], "t_planned")


def cached_share_split(run: dict) -> dict:
    """Mean cached share of the prompt (`cached_tokens / prompt_tokens`) over ok later turns: all of them, and only
    those whose own first token came at or after the previous turn's end (the previous turn had finished)."""
    ok = _later_turns(run)
    ok = ok[ok.status == "ok"]
    after = ok[ok.t_first_token >= ok.prev_end]
    share = lambda d: float((d.cached_tokens / d.prompt_tokens).mean())
    return {"all_later": share(ok), "after_prev_finished": share(after), "n_all": len(ok), "n_after": len(after)}


def overlap_fraction(run: dict) -> float:
    """Share of later turns sent before the previous turn's first token."""
    q = _later_turns(run)
    return float((q.t_sent < q.prev_first).mean())
