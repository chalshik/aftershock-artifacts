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
    span = cfg["workload"]["duration_s"] - cfg["workload"]["warmup_s"]
    m = window(rates(run["metrics"]), cfg) if len(run["metrics"]) else pd.DataFrame()
    q = m.get("num_requests_waiting")
    return {
        "run": run["dir"].name, "rate": cfg["workload"]["rate"],
        "prefix_caching": bool(cfg["server"]["args"].get("--enable-prefix-caching")),
        "throughput": float((r.status == "ok").sum() / span),
        "ttft_p50": r.ttft.quantile(.5), "ttft_p99": r.ttft.quantile(.99),
        "e2e_p50": r.e2e.quantile(.5), "unfinished": int((r.status == "unfinished").sum()),
        "hit_rate": float(m.hit_rate.mean()) if "hit_rate" in m else np.nan,
        "q_mean": float(q.mean()) if q is not None else np.nan,
        "q_slope_per_s": float(np.polyfit(m.t, q, 1)[0]) if q is not None and len(m) > 2 else np.nan,
        "valid": run["checks"]["valid"] if run["checks"] else None,
    }


def capacity(curve: pd.DataFrame, min_throughput_frac: float, max_q_slope: float) -> float:
    """mu = highest rate where the server keeps up: throughput >= frac x rate and the queue is not growing.
    Thresholds must be pre-registered in docs/decisions.md before reading the sweep."""
    ok = curve[(curve.throughput >= min_throughput_frac * curve.rate) & (curve.q_slope_per_s <= max_q_slope)]
    return float(ok.rate.max()) if len(ok) else np.nan
