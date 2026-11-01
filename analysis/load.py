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
        # Open loop: latency is measured from the *planned* arrival, so client lag cannot hide delay.
        reqs["ttft"] = reqs.t_first_token - reqs.t_planned
        reqs["e2e"] = reqs.t_end - reqs.t_planned
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


def verdict(run: dict) -> dict:
    """Stage 2 verdict, by the rule in docs/decisions.md; settings are in the run's config under `verdict`.
    Judged around the successful wipe, or at control_t_s for a no-trigger control."""
    c, m, r = run["cfg"]["verdict"], run["metrics"], run["requests"]
    trig = run["trigger"]
    t = float(trig[trig.success].t_end.iloc[0]) if len(trig) else c["control_t_s"]
    hits, q, waiting = m["vllm:prefix_cache_hits_total"], m["vllm:prefix_cache_queries_total"], m["vllm:num_requests_waiting"]
    slo = run["cfg"]["slo"]["ttft_s"]

    def level(a, b):
        reqs = r[(r.t_planned >= a) & (r.t_planned < b)]
        w = (m.t >= a) & (m.t < b)
        dq = np.interp(b, m.t, q) - np.interp(a, m.t, q)
        return {"pf": float(((reqs.status == "ok") & (reqs.ttft <= slo)).mean()),
                "hit": float((np.interp(b, m.t, hits) - np.interp(a, m.t, hits)) / dq) if dq else 0.0,
                "q": float(waiting[w].mean()), "q_slope": float(np.polyfit(m.t[w], waiting[w], 1)[0])}

    t_end = t + c["watch_s"]
    base = level(t - c["baseline_s"], t)
    prev = level(t_end - 2 * c["end_s"], t_end - c["end_s"])
    end = level(t_end - c["end_s"], t_end)
    pf_up, hit_up = end["pf"] - prev["pf"] >= c["climb"], end["hit"] - prev["hit"] >= c["climb"]
    if base["pf"] < c["min_baseline_pf"]:
        v = "bad_baseline"
    elif (end["pf"] >= base["pf"] - c["recovered_pf_drop"] and end["hit"] >= base["hit"] - c["recovered_hit_drop"]
          and end["q"] <= base["q"] + c["recovered_q_excess"]):
        v = "recovered"
    elif end["q_slope"] <= -c["q_slope"] or (pf_up and hit_up):
        v = "slow_drain"
    elif end["pf"] <= base["pf"] - c["stuck_pf_drop"] and end["hit"] <= base["hit"] - c["stuck_hit_drop"]:
        v = "stuck"
    else:
        v = "unclear"
    return {"verdict": v, "t_wipe": t, "baseline": base, "previous": prev, "end": end}


def capacity(curve: pd.DataFrame, min_throughput_frac: float, max_q_slope: float) -> float:
    """mu = highest rate where the server keeps up: throughput >= frac x rate and the queue is not growing.
    Thresholds must be pre-registered in docs/decisions.md before reading the sweep."""
    ok = curve[(curve.throughput >= min_throughput_frac * curve.rate) & (curve.q_slope_per_s <= max_q_slope)]
    return float(ok.rate.max()) if len(ok) else np.nan
