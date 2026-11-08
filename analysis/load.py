"""Read run folders into DataFrames, with one shared set of metric definitions. Never writes into runs/."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

RUNS = Path(__file__).resolve().parent.parent / "runs"


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()] if path.exists() else []


def load_run(run_dir: Path | str) -> dict:
    d = Path(run_dir)
    cfg = yaml.safe_load((d / "config.yaml").read_text())
    reqs = pd.DataFrame(_jsonl(d / "requests.jsonl"))
    if len(reqs):
        # Open loop: latency is measured from the *planned* arrival, so client lag cannot hide delay. Closed-loop
        # turns (REG-11 draft): from the release time t_released, the planned gap after the previous turn's end.
        due = reqs.t_released.fillna(reqs.t_planned).astype(float) if "t_released" in reqs else reqs.t_planned
        reqs["ttft"] = reqs.t_first_token - due
        reqs["e2e"] = reqs.t_end - due
    return {
        "dir": d, "cfg": cfg,
        "checks": json.loads((d / "checks.json").read_text()) if (d / "checks.json").exists() else None,
        "env": json.loads((d / "env.json").read_text()),
        "requests": reqs,
        "metrics": metrics_wide(_jsonl(d / "metrics.jsonl")),
        "gpu": pd.DataFrame(_jsonl(d / "gpu.jsonl")),
        "events": pd.DataFrame(_jsonl(d / "events.jsonl")),
        "trigger": pd.DataFrame(_jsonl(d / "trigger.jsonl")),
    }


def find_runs(pattern: str = "*", valid_only: bool = True) -> list[dict]:
    out = [load_run(p) for p in sorted(RUNS.glob(pattern)) if (p / "config.yaml").exists()]
    return [r for r in out if not valid_only or (r["checks"] and r["checks"]["valid"])]


def metrics_wide(scrapes: list[dict]) -> pd.DataFrame:
    """One row per scrape; one column per metric name, summed over label sets. Histogram buckets dropped."""
    rows = []
    for s in scrapes:
        if "values" not in s:
            continue
        row = {"t": s["t"]}
        for k, v in s["values"].items():
            name = k.split("{", 1)[0]
            if not name.endswith("_bucket"):
                row[name] = row.get(name, 0.0) + v
        rows.append(row)
    return pd.DataFrame(rows)


def rates(m: pd.DataFrame) -> pd.DataFrame:
    """Per-interval rates from raw counters. A negative difference (restart) becomes NaN, never zero."""
    dt = m.t.diff()
    out = pd.DataFrame({"t": m.t})
    for col in m.columns:
        if col.endswith("_total"):
            d = m[col].diff()
            out[col.removesuffix("_total") + "_rate"] = (d.where(d >= 0) / dt)
    hits, q = m.get("vllm:prefix_cache_hits_total"), m.get("vllm:prefix_cache_queries_total")
    if hits is not None and q is not None:
        out["hit_rate"] = hits.diff() / q.diff().replace(0, np.nan)
    p, pc = m.get("vllm:prompt_tokens_total"), m.get("vllm:prompt_tokens_cached_total")
    if p is not None and pc is not None:
        out["recomputed_prefill_tok_s"] = (p.diff() - pc.diff()) / dt
    for g in ["vllm:num_requests_running", "vllm:num_requests_waiting", "vllm:kv_cache_usage_perc"]:
        if g in m:
            out[g.split(":")[1]] = m[g]
    return out


def percent_fast(reqs: pd.DataFrame, slo_ttft_s: float, bin_s: float = 1.0) -> pd.DataFrame:
    """Share of requests *arriving* in each bin that met the TTFT limit. Unfinished/errored = miss."""
    fast = (reqs.status == "ok") & (reqs.ttft <= slo_ttft_s)
    b = (reqs.t_planned // bin_s) * bin_s
    return fast.groupby(b).mean().rename("percent_fast").rename_axis("t").reset_index()


def window(df: pd.DataFrame, cfg: dict, col: str = "t") -> pd.DataFrame:
    """The measured window: after warm-up, before the end of arrivals."""
    wl = cfg["workload"]
    return df[(df[col] >= wl["warmup_s"]) & (df[col] < wl["duration_s"])]


def summarize(run: dict) -> dict:
    cfg, r = run["cfg"], window(run["requests"], run["cfg"], "t_planned")
    done = window(run["requests"], cfg, "t_end")  # completions per second, so a backlog cannot look like throughput
    span = cfg["workload"]["duration_s"] - cfg["workload"]["warmup_s"]
    m = window(rates(run["metrics"]), cfg) if len(run["metrics"]) else pd.DataFrame()
    q = m.get("num_requests_waiting")
    return {
        "run": run["dir"].name, "rate": cfg["workload"]["rate"],
        "prefix_caching": bool(cfg["server"]["args"].get("--enable-prefix-caching")),
        "throughput": float((done.status == "ok").sum() / span),
        # Realized planned arrival rate in the window, from the run's own schedule (item 42, decisions.md 2026-11-04).
        "planned_rate": float(len(r) / span),
        "ttft_p50": r.ttft.quantile(.5), "ttft_p99": r.ttft.quantile(.99),
        "e2e_p50": r.e2e.quantile(.5), "unfinished": int((r.status == "unfinished").sum()),
        "hit_rate": float(m.hit_rate.mean()) if "hit_rate" in m else np.nan,
        "q_mean": float(q.mean()) if q is not None else np.nan,
        "q_slope_per_s": float(np.polyfit(m.t, q, 1)[0]) if q is not None and len(m) > 2 else np.nan,
        "valid": run["checks"]["valid"] if run["checks"] else None,
    }


def whole_run_hit_rate(run: dict) -> float:
    """Hit rate from the first and last scrape, so runs with and without the recorder are measured the same way."""
    m = run["metrics"]
    hits, q = m["vllm:prefix_cache_hits_total"], m["vllm:prefix_cache_queries_total"]
    return float((hits.iloc[-1] - hits.iloc[0]) / (q.iloc[-1] - q.iloc[0]))


def client_backlog_slope(run: dict) -> float:
    """Slope (req/s^2) of requests sent but without a first token, per second of the measured window.
    Client-side stand-in for the queue slope, for runs with no recorder."""
    wl, r = run["cfg"]["workload"], run["requests"]
    grid = np.arange(wl["warmup_s"], wl["duration_s"], 1.0)
    sent, first = np.sort(r.t_sent.dropna()), np.sort(r.t_first_token.dropna())
    return float(np.polyfit(grid, np.searchsorted(sent, grid, "right") - np.searchsorted(first, grid, "right"), 1)[0])


def settling_time(run: dict, t_step: float, t_end: float) -> float | None:
    """Seconds from a load step until hit rate and TTFT p50, over a sliding span, are inside the band around their
    settled level (the end of the segment). None if never. Settings are in the run's config under `tau`."""
    c, m, r = run["cfg"]["tau"], run["metrics"], run["requests"]
    hits, q = m["vllm:prefix_cache_hits_total"], m["vllm:prefix_cache_queries_total"]

    def level(a, b):
        dq = np.interp(b, m.t, q) - np.interp(a, m.t, q)
        p50 = r[(r.t_planned >= a) & (r.t_planned < b)].ttft.median()
        return (np.interp(b, m.t, hits) - np.interp(a, m.t, hits)) / dq, p50

    hit0, p0 = level(t_end - c["settled_s"], t_end)
    span = c["bin_s"] * c["n_bins"]
    for t in np.arange(t_step, t_end - c["settled_s"], c["bin_s"]):
        hit, p50 = level(t, t + span)
        if abs(hit - hit0) <= c["hit_band"] and abs(p50 - p0) <= c["ttft_p50_band_s"]:
            return float(t - t_step)
    return None


def _covered(t: np.ndarray, a: float, b: float, max_gap: float) -> bool:
    """Scrapes span [a, b): one within `max_gap` of each end, and no gap between consecutive scrapes above `max_gap`."""
    inside = t[(t >= a - max_gap) & (t <= b + max_gap)]
    return len(inside) >= 2 and inside[0] <= a + max_gap and inside[-1] >= b - max_gap and np.diff(inside).max() <= max_gap


def _level(run: dict, a: float, b: float) -> dict:
    """Levels over [a, b): percent fast and hit rate by arrival/scrape time, and the server gauges.
    A value the window cannot give is NaN, never a number (REG-4, decisions.md 2026-11-04):
    - pf with no requests;
    - every server value (hit, q, n, kv, q_slope) when the scrapes don't cover the window, i.e. no scrape within the
      registered `checks.max_scrape_gap_s` of each end, or a larger gap inside it;
    - hit when the query counter does not rise, or either cache counter goes down (a restart) inside the window;
    - a gauge's mean or slope over its non-NaN scrapes only; q_slope needs at least 2 of them."""
    m, r, slo = run["metrics"], run["requests"], run["cfg"]["slo"]["ttft_s"]
    reqs = r[(r.t_planned >= a) & (r.t_planned < b)]
    out = {"pf": float(((reqs.status == "ok") & (reqs.ttft <= slo)).mean()) if len(reqs) else np.nan}
    nan = {"hit": np.nan, "q": np.nan, "q_slope": np.nan, "n": np.nan, "kv": np.nan}
    max_gap = run["cfg"]["checks"]["max_scrape_gap_s"]  # the registered scrape-gap limit (configs/base.yaml)
    if not len(m) or not _covered(m.t.to_numpy(), a, b, max_gap):
        return {**out, **nan}
    hits, q = m["vllm:prefix_cache_hits_total"], m["vllm:prefix_cache_queries_total"]
    span = (m.t >= a) & (m.t <= b)
    reset = (np.diff(hits[span].to_numpy()) < 0).any() or (np.diff(q[span].to_numpy()) < 0).any()
    dq = np.interp(b, m.t, q) - np.interp(a, m.t, q)
    out["hit"] = float((np.interp(b, m.t, hits) - np.interp(a, m.t, hits)) / dq) if dq > 0 and not reset else np.nan
    w = (m.t >= a) & (m.t < b)
    wait = m["vllm:num_requests_waiting"][w]
    ok = wait.notna()
    out["q"] = float(wait[ok].mean()) if ok.any() else np.nan
    out["q_slope"] = float(np.polyfit(m.t[w][ok], wait[ok], 1)[0]) if ok.sum() >= 2 else np.nan
    for key, col in (("n", "vllm:num_requests_running"), ("kv", "vllm:kv_cache_usage_perc")):
        g = m[col][w]
        out[key] = float(g.mean()) if g.notna().any() else np.nan
    return out


def ramp_table(run: dict) -> pd.DataFrame:
    """One row per load step of an up-then-down ramp (`workload.steps`). Each step is judged over its last part,
    after `ramp.settle_frac` of the step has passed, so the queue left by the previous step has had time to clear."""
    cfg = run["cfg"]
    wl, settle = cfg["workload"], cfg["ramp"]["settle_frac"]
    starts = [0.0] + [float(s["at_s"]) for s in wl["steps"]]
    ends = starts[1:] + [float(wl["duration_s"])]
    rates = [wl["rate"]] + [s["rate"] for s in wl["steps"]]
    peak = rates.index(max(rates))
    rows = []
    for i, (a, b, lam) in enumerate(zip(starts, ends, rates)):
        lv = _level(run, a + settle * (b - a), b)
        rows.append({"step": i, "rate": lam, "direction": "up" if i <= peak else "down", "start": a, "end": b, **lv})
    return pd.DataFrame(rows)


def verdict(run: dict) -> dict:
    """Stage 2 verdict, by the rule in docs/decisions.md; settings are in the run's config under `verdict`.
    The baseline ends where the trigger starts; the watch starts where it ends (a successful wipe, a burst,
    or control_t_s for a control, where both are the same moment)."""
    c, m, r = run["cfg"]["verdict"], run["metrics"], run["requests"]
    trig, spec = run["trigger"], run["cfg"].get("trigger") or {}
    if spec.get("kind") == "burst":
        t_start, t = float(spec["at_s"]), float(spec["at_s"] + spec["duration_s"])
    elif len(trig):
        wipe = trig[trig.success].iloc[0]
        t_start, t = float(wipe.t_start), float(wipe.t_end)
    else:
        t_start = t = float(c["control_t_s"])
    level = lambda a, b: _level(run, a, b)
    t_end = t + c["watch_s"]
    base = level(t_start - c["baseline_s"], t_start)
    prev = level(t_end - 2 * c["end_s"], t_end - c["end_s"])
    end = level(t_end - c["end_s"], t_end)
    # Each branch is decided only from the values it uses; a branch that needs a NaN cannot be passed, and the verdict
    # becomes `unclear` instead of falling through to a later branch (REG-4).
    nan = lambda *x: any(np.isnan(v) for v in x)
    if nan(base["pf"]):
        v = "unclear"
    elif base["pf"] < c["min_baseline_pf"]:
        v = "bad_baseline"
    elif nan(end["pf"], end["hit"], end["q"], base["hit"], base["q"]):
        v = "unclear"
    elif (end["pf"] >= base["pf"] - c["recovered_pf_drop"] and end["hit"] >= base["hit"] - c["recovered_hit_drop"]
          and end["q"] <= base["q"] + c["recovered_q_excess"]):
        v = "recovered"
    else:
        # Any one sign of recovery rules out stuck. A queue counts as draining only if it would empty within the horizon.
        signs = [None if nan(end["pf"], prev["pf"]) else end["pf"] - prev["pf"] >= c["pf_climb"],
                 None if nan(end["hit"], prev["hit"]) else end["hit"] - prev["hit"] >= c["hit_climb"],
                 None if nan(end["q_slope"]) else end["q_slope"] < 0 and end["q"] / -end["q_slope"] <= c["drain_horizon_s"]]
        if any(s is True for s in signs):
            v = "slow_drain"
        elif any(s is None for s in signs):
            v = "unclear"  # a sign of recovery can't be ruled out
        elif end["pf"] <= base["pf"] - c["stuck_pf_drop"] and end["hit"] <= base["hit"] - c["stuck_hit_drop"]:
            v = "stuck"
        else:
            v = "unclear"
    return {"verdict": v, "t_start": t_start, "t_wipe": t, "baseline": base, "previous": prev, "end": end}


def capacity(curve: pd.DataFrame, min_throughput_frac: float, max_q_slope: float, against: str = "rate",
             monotone: bool = False, swept_rates: list[float] | None = None) -> float:
    """mu = highest rate where the server keeps up: throughput >= frac x reference and the queue is not growing.
    `against` is the reference: "rate" (λ as configured; the 2026-10-30 rule, used by every sweep up to 2026-11-04) or
    "planned_rate" (the realized planned rate in the window; item 42, future sweeps only, decisions.md 2026-11-04).
    `monotone` (REG-7, future sweeps only): the highest rate such that it and every lower swept rate pass, so a rate
    that passes by noise above a failing one cannot set mu. The default keeps the old reading (any passing rate).
    `swept_rates` (monotone only; decisions.md 2026-11-05 [CORR] and the owner's approval): every rate the sweep
    registered. `curve` then holds the valid runs only, and a swept rate with no valid run ends the chain like a failing
    one, so mu can never be set over a rate that was not measured. Two valid runs at one rate, or a rate that was not
    swept, raise: the registration says which run counts.
    Thresholds must be pre-registered in docs/decisions.md before reading the sweep."""
    if against not in ("rate", "planned_rate"):
        raise ValueError(f"unknown capacity reference {against!r}")
    if swept_rates is not None and not monotone:
        raise ValueError("swept_rates is defined for the monotone rule only")
    c = curve.sort_values("rate")
    passes = (c.throughput >= min_throughput_frac * c[against]) & (c.q_slope_per_s <= max_q_slope)
    if monotone and swept_rates is not None:
        if c.rate.duplicated().any():
            raise ValueError("two valid runs at one rate; the registration says which counts")
        unknown = set(c.rate) - set(swept_rates)
        if unknown:
            raise ValueError(f"rates that were not swept: {sorted(unknown)}")
        by_rate = dict(zip(c.rate, passes))
        chain, mu = True, np.nan
        for rate in sorted(swept_rates):
            chain = chain and bool(by_rate.get(rate, False))  # no valid run at this rate ends the chain
            if not chain:
                break
            mu = float(rate)
        return mu
    if monotone:
        passes = passes.cumprod().astype(bool)
    ok = c[passes]
    return float(ok.rate.max()) if len(ok) else np.nan
