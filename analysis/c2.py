"""C2, condition 4 (a memory-limited loop, not just a queue) on stuck burst runs. Draft for REG-22; not registered.
Never writes into runs/.

PROTOCOL §3, condition 4: "mean KV >= 0.80, mean N >= 2 x baseline, N below the 256 cap, and the traces follow the
plan's order" (decisions.md 2026-11-01: "at `end`"). The plan's order (hit rate drops first, then recomputed prefill
rises, the batch grows, KV fills) was written for a cache wipe. A burst fills the pool itself, so on a burst run the
entry order is the trigger's, not the loop's. What a burst run can show of the loop is that its links hold together
once the burst's own requests have left. So condition 4 is read here as two judged parts:

  levels   in the end window: mean KV >= min_kv, mean N >= n_factor x baseline N, max N < n_cap   (as registered)
  sustain  in every span of the watch that starts after the last burst request has ended, all four links hold:
           reuse of later turns <= baseline - the verdict's stuck_hit_drop   (the cache is lost)
           session uncached prefill tokens/s >= u_factor x baseline            (the prompts are recomputed)
           mean N >= n_factor x baseline N                                     (the batch is large)
           mean KV >= min_kv                                                   (the pool is full)
and one reported part, the onset times of the four signals after the trigger's start (`onsets`), with their order.
"""
from __future__ import annotations

import math

import numpy as np

from analysis.k1 import later_turns
from analysis.margin import is_burst_request

C2 = {
    "min_kv": 0.80, "n_factor": 2.0, "n_cap": 256,   # PROTOCOL §3 condition 4 (decisions.md 2026-11-01)
    "u_factor": 2.0,        # session uncached prefill rate at least this multiple of its baseline
    "span_s": 300.0,        # the watch is cut into spans of this length from the burst's end
    "min_spans": 2,         # `sustain` needs at least this many spans after the last burst request
    "roll_s": 60.0, "step_s": 10.0, "min_turns": 20,   # onsets: trailing windows on a grid; reuse needs this many turns
    "kv_onset": 0.9,        # as gate.SURGE["kv_onset"]
}
KV, N = "vllm:kv_cache_usage_perc", "vllm:num_requests_running"


def windows(run: dict) -> dict:
    t, v = run["cfg"]["trigger"], run["cfg"]["verdict"]
    at, end = float(t["at_s"]), float(t["at_s"] + t["duration_s"])
    return {"at": at, "end": end, "base": (at - v["baseline_s"], at), "watch_end": end + v["watch_s"],
            "end_window": (end + v["watch_s"] - v["end_s"], end + v["watch_s"])}


def gauge(run: dict, col: str, a: float, b: float, how: str = "mean") -> float:
    m = run["metrics"]
    if not len(m) or col not in m:
        return math.nan
    w = m[(m.t >= a) & (m.t < b)][col].dropna()
    return float(getattr(w, how)()) if len(w) else math.nan


def reuse_in(turns, a: float, b: float, min_turns: int = 1) -> float:
    q = turns[(turns.t_first_token >= a) & (turns.t_first_token < b)]
    den = q.prev_prompt.sum()
    return float(np.minimum(q.cached_tokens, q.prev_prompt).sum() / den) if len(q) >= min_turns and den > 0 else math.nan


def session_uncached_rate(run: dict, a: float, b: float) -> float:
    """Uncached prompt tokens per second over ok session requests (no burst rows) whose first token falls in [a, b)."""
    q = run["requests"]
    w = q[~is_burst_request(run) & (q.status == "ok") & (q.t_first_token >= a) & (q.t_first_token < b)]
    return float((w.prompt_tokens - w.cached_tokens.fillna(0)).clip(lower=0).sum() / (b - a))


def baseline(run: dict) -> dict:
    a, b = windows(run)["base"]
    return {"reuse": reuse_in(later_turns(run), a, b), "u": session_uncached_rate(run, a, b),
            "n": gauge(run, N, a, b), "kv": gauge(run, KV, a, b)}


def levels(run: dict, base: dict | None = None) -> dict:
    """The registered levels in the end window."""
    base = base or baseline(run)
    a, b = windows(run)["end_window"]
    kv, n, n_max = gauge(run, KV, a, b), gauge(run, N, a, b), gauge(run, N, a, b, "max")
    vals = (kv, n, n_max, base["n"])
    ok = None if any(math.isnan(x) for x in vals) else bool(
        kv >= C2["min_kv"] and n >= C2["n_factor"] * base["n"] and n_max < C2["n_cap"])
    return {"kv": kv, "n": n, "n_over_base": n / base["n"] if base["n"] else math.nan, "n_max": n_max, "ok": ok}


def last_burst_end(run: dict) -> float:
    """When the last burst request ended; NaN if a burst request never ended (the burst is then still in the system)."""
    q = run["requests"]
    b = q[is_burst_request(run)]
    if not len(b) or (b.status != "ok").any() or b.t_end.isna().any():
        return math.nan
    return float(b.t_end.max())


def links(run: dict, a: float, b: float, base: dict, turns=None) -> dict:
    """The loop's four links over [a, b); `holds` is None when a value is missing."""
    turns = later_turns(run) if turns is None else turns
    drop = float(run["cfg"]["verdict"]["stuck_hit_drop"])
    v = {"reuse": reuse_in(turns, a, b), "u": session_uncached_rate(run, a, b), "n": gauge(run, N, a, b),
         "kv": gauge(run, KV, a, b)}
    if any(math.isnan(x) for x in (*v.values(), base["reuse"], base["u"], base["n"])):
        return {**v, "span": (a, b), "holds": None}
    holds = (v["reuse"] <= base["reuse"] - drop and v["u"] >= C2["u_factor"] * base["u"]
             and v["n"] >= C2["n_factor"] * base["n"] and v["kv"] >= C2["min_kv"])
    return {**v, "span": (a, b), "holds": bool(holds)}


def sustain(run: dict, base: dict | None = None) -> dict:
    """The links in every span of the watch that starts at or after the last burst request's end."""
    base, w = base or baseline(run), windows(run)
    tb = last_burst_end(run)
    starts = np.arange(w["end"], w["watch_end"] - 1e-9, C2["span_s"])
    turns = later_turns(run)
    rows = [links(run, float(a), float(min(a + C2["span_s"], w["watch_end"])), base, turns)
            for a in starts if not math.isnan(tb) and a >= tb]
    if math.isnan(tb) or len(rows) < C2["min_spans"] or any(r["holds"] is None for r in rows):
        ok = None
    else:
        ok = all(r["holds"] for r in rows)
    return {"last_burst_end": tb, "n_spans": len(rows), "spans": rows, "ok": ok}


def onsets(run: dict, base: dict | None = None) -> dict:
    """Reported, never judged: the first grid time after the trigger's start at which each signal, over the trailing
    roll_s, crosses its level (KV >= kv_onset; N >= n_factor x baseline; reuse <= baseline - stuck_hit_drop with at
    least min_turns turns; session uncached rate >= u_factor x baseline), and the order found."""
    base, w = base or baseline(run), windows(run)
    drop, turns = float(run["cfg"]["verdict"]["stuck_hit_drop"]), later_turns(run)
    out = {"kv": math.nan, "n": math.nan, "reuse": math.nan, "u": math.nan}
    for t in np.arange(w["at"] + C2["step_s"], w["watch_end"] + 1e-9, C2["step_s"]):
        a = t - C2["roll_s"]
        tests = {"kv": lambda: gauge(run, KV, a, t) >= C2["kv_onset"],
                 "n": lambda: gauge(run, N, a, t) >= C2["n_factor"] * base["n"],
                 "reuse": lambda: reuse_in(turns, a, t, C2["min_turns"]) <= base["reuse"] - drop,
                 "u": lambda: session_uncached_rate(run, a, t) >= C2["u_factor"] * base["u"]}
        for k, f in tests.items():
            if math.isnan(out[k]) and f():      # a NaN comparison is False
                out[k] = float(t)
        if not any(math.isnan(x) for x in out.values()):
            break
    seen = sorted((v, k) for k, v in out.items() if not math.isnan(v))
    return {**out, "order": [k for _, k in seen]}


def condition4(run: dict) -> dict:
    """One run's label: 'loop' (levels and sustain hold), 'not_memory_limited' (levels fail: a backlog, not this
    loop), 'not_sustained' (levels hold but a link is missing in some span after the burst's requests left),
    'undefined' (a value is missing, or fewer than min_spans spans after the last burst request)."""
    base = baseline(run)
    lv, su = levels(run, base), sustain(run, base)
    if lv["ok"] is None or (lv["ok"] and su["ok"] is None):
        label = "undefined"
    elif not lv["ok"]:
        label = "not_memory_limited"
    else:
        label = "loop" if su["ok"] else "not_sustained"
    return {"run": run["dir"].name, "baseline": base, "levels": lv, "sustain": su, "onsets": onsets(run, base),
            "evictions": eviction_readout(run), "label": label}



# ---------------------------------------------------------------- the eviction link, read directly (reported only)

HIST = {"idle": "vllm:kv_block_idle_before_evict_seconds", "lifetime": "vllm:kv_block_lifetime_seconds",
        "reuse_gap": "vllm:kv_block_reuse_gap_seconds"}


def _buckets(values: dict, name: str) -> dict[float, float]:
    """Cumulative bucket counts of one histogram in one scrape, summed over label sets: upper edge -> count."""
    out: dict[float, float] = {}
    pre = name + "_bucket{"
    for k, v in values.items():
        if k.startswith(pre):
            le = k.split('le="', 1)[1].split('"', 1)[0]
            e = math.inf if le == "+Inf" else float(le)
            out[e] = out.get(e, 0.0) + v
    return out


def histogram_delta(metrics_jsonl, name: str, a: float, b: float) -> dict:
    """What a sampled residency histogram gained in [a, b): from the first scrape at or after a to the last before b
    (raw metrics.jsonl; `load.metrics_wide` drops the buckets). Returns the count, the upper edge of the bucket that
    holds the median, and the shares at or below 5 s (the mean turn gap) and 30 s. NaN where nothing was sampled.
    SOURCE(vLLM 0.32.0 v1/core/kv_cache_metrics.py:KVCacheMetricsCollector.on_block_evicted): for a sampled block
    `idle` is the time from its last access (its allocation, or a later cache hit) to its eviction, so it includes
    the time the block was held by the request that computed it; `reuse_gap` is the time between two cache hits."""
    import json
    first = last = None
    with open(metrics_jsonl) as f:
        for line in f:
            if not line.strip():
                continue
            s = json.loads(line)
            if "values" not in s or s["t"] < a:
                continue
            if s["t"] >= b:
                break
            if first is None:
                first = _buckets(s["values"], name)
            last = _buckets(s["values"], name)
    nan = {"count": 0.0, "median_le_s": math.nan, "share_le_5s": math.nan, "share_le_30s": math.nan}
    if not first or not last:
        return nan
    d = {e: last.get(e, 0.0) - first.get(e, 0.0) for e in sorted(last)}
    total = d.get(math.inf, 0.0)
    if total <= 0 or any(v < 0 for v in d.values()):      # nothing sampled, or a counter reset
        return nan
    med = next(e for e in sorted(d) if d[e] >= total / 2)
    return {"count": total, "median_le_s": med, "share_le_5s": d.get(5.0, math.nan) / total,
            "share_le_30s": d.get(30.0, math.nan) / total}


def turn_spacing(run: dict, a: float, b: float) -> float:
    """Median time between the first tokens of consecutive turns of a session, over later turns whose first token
    falls in [a, b): how long a prefix has to survive to be reused."""
    q = run["requests"]
    q = q[~is_burst_request(run) & (q.status == "ok")].sort_values(["session_id", "turn"])
    prev = q.groupby("session_id").t_first_token.shift()
    w = q[(q.turn > 0) & (q.t_first_token >= a) & (q.t_first_token < b)]
    gaps = (w.t_first_token - prev[w.index]).dropna()
    return float(gaps.median()) if len(gaps) else math.nan


def eviction_readout(run: dict) -> dict:
    """Reported, never judged: the three residency histograms and the turn spacing in the baseline and in the stretch
    from the last burst request's end (or the burst's end, if that is NaN) to the end of the watch."""
    w, path = windows(run), run["dir"] / "metrics.jsonl"
    tb = last_burst_end(run)
    after = (w["end"] if math.isnan(tb) else max(tb, w["end"]), w["watch_end"])
    out = {}
    for label, (a, b) in (("baseline", w["base"]), ("after", after)):
        out[label] = {"span": (a, b), "turn_spacing_s": turn_spacing(run, a, b),
                      **{k: histogram_delta(path, name, a, b) for k, name in HIST.items()}} if path.exists() else None
    return out


REG22 = {
    # The closed-loop L1 burst runs at 350 W made before REG-19 (REG-11, REG-12, REG-14, REG-15, REG-17, REG-18), as
    # k3.REG21["batch1"]. A run is judged only if its registered verdict (`load.verdict`) is "stuck".
    "runs": ("20261109-042828_burst_l1pl350cl_r2.4_s1", "20261109-080203_burst_l1pl350cl_r2.4_s2",
             "20261109-093609_burst_l1pl350cl_r2.4_s3", "20261109-111316_burst_l1pl350cl_r2.4_s4",
             "20261109-125300_burst_l1pl350cl_r2.4_s5", "20261109-151300_burst_l1pl350cl_r2.4_s6",
             "20261110-063647_burst_l1pl350cl_r2.2_s2", "20261110-085730_confirm_l1pl350cl_r2.2_s12",
             "20261110-182920_burst_l1pl350cl_r2.0_s2", "20261111-101805_burst_l1pl350cl_r2.0_s4",
             "20261111-115409_burst_l1pl350cl_r2.0_s3", "20261111-133019_burst_l1pl350cl_r2.0_s5",
             "20261111-150642_burst_l1pl350cl_r2.0_s6"),
}


def reg22_table() -> dict:
    """Condition 4 on every stuck run of REG22["runs"]; the others are listed with their verdict. Computed once,
    after REG-22 is approved."""
    from analysis.load import RUNS, load_run, verdict
    rows, left = [], []
    for name in REG22["runs"]:
        if not (RUNS / name / "config.yaml").exists():
            left.append({"run": name, "why": "missing"})
            continue
        run = load_run(RUNS / name)
        v = verdict(run)["verdict"]
        if v != "stuck":
            left.append({"run": name, "why": f"verdict {v}"})
            continue
        rows.append({**condition4(run), "lam": float(run["cfg"]["workload"]["rate"]), "seed": run["cfg"].get("seed")})
    labels = [r["label"] for r in rows]
    return {"rows": rows, "left_out": left, "n_stuck": len(rows),
            "counts": {k: labels.count(k) for k in ("loop", "not_sustained", "not_memory_limited", "undefined")}}


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) == 2 and sys.argv[1] == "reg22":
        print(json.dumps(reg22_table(), indent=1, default=str))
    else:
        raise SystemExit("usage: python -m analysis.c2 reg22")
