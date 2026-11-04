"""Post-trigger completion margin (docs/model.md M2; registration REG-1). Never writes into runs/.

For spans [end + a, end + b) after a trigger's end: completions per second against λ, with the server state.
A span tests assumption A only if it *qualifies*:
  - capacity-limited: Q > 0 at every scrape in the span (scrapes are 1 s apart, configs/base.yaml recorder);
  - burst-free: no burst request completes in it, so completions are session requests only;
  - cold: the sessions' own cached share (per-request `cached_tokens / prompt_tokens`, summed over session requests
    whose first token falls in the span) is at or below the baseline's minus `cold_hit_drop`. Burst prompts never
    hit, so the server counters would make a warm session cache look cold (adversarial review, REG-1).
All times are seconds from the run's t0 on one monotonic clock (harness/recorder.py:102, harness/loadgen.py:46-66,
harness/trigger.py:64). Every threshold is an argument, set in the registration.
"""
import numpy as np
import pandas as pd

from analysis.derived import hit_between, trigger_times
from analysis.stats import poisson_rate_upper


def is_burst_request(run: dict) -> pd.Series:
    """Burst requests: turn 0 with the burst's prompt length. A session's turn 0 is always system + user tokens
    (harness/workload.py:97-108), which `check_burst_rule` requires to differ."""
    r, spec = run["requests"], run["cfg"].get("trigger") or {}
    if spec.get("kind") != "burst":
        return pd.Series(False, index=r.index)
    return (r.turn == 0) & (r.prompt_tokens_planned == spec["prompt_tokens"])


def check_burst_rule(run: dict) -> None:
    s = run["cfg"]["workload"]["sessions"]
    spec = run["cfg"].get("trigger") or {}
    if spec.get("kind") == "burst" and spec["prompt_tokens"] == s["system_tokens"] + s["user_tokens"]:
        raise ValueError("burst prompt length equals a session's first prompt; burst requests can't be told apart")


def session_cached_share(r: pd.DataFrame, burst: pd.Series, a: float, b: float) -> float:
    """Σ cached_tokens / Σ prompt_tokens over ok session requests whose first token is in [a, b). NaN if none."""
    s = r[(~burst) & (r.status == "ok") & (r.t_first_token >= a) & (r.t_first_token < b)]
    tot = s.prompt_tokens.sum()
    return float(s.cached_tokens.sum() / tot) if tot else float("nan")


def post_trigger_margin(run: dict, spans: list[tuple[float, float]], baseline_s: float, cold_hit_drop: float,
                        conf: float) -> list[dict]:
    """One row per span after the trigger's end (a wipe's first successful call, a burst's last planned arrival).
    c: ok completions in the span per second; c_upper: its one-sided `conf` Poisson upper bound."""
    check_burst_rule(run)
    tt = trigger_times(run)
    if tt is None:
        raise ValueError("no trigger in this run")
    start, end = tt
    m, r = run["metrics"], run["requests"]
    if start - baseline_s < m.t.iloc[0]:
        raise ValueError(f"baseline starts at {start - baseline_s:.1f} s, before the first scrape ({m.t.iloc[0]:.1f} s)")
    lam = float(run["cfg"]["workload"]["rate"])
    burst = is_burst_request(run)
    share_base = session_cached_share(r, burst, start - baseline_s, start)
    rows = []
    for a, b in spans:
        lo, hi = end + a, end + b
        done = (r.status == "ok") & (r.t_end >= lo) & (r.t_end < hi)
        w = (m.t >= lo) & (m.t < hi)
        q = m["vllm:num_requests_waiting"][w]
        share = session_cached_share(r, burst, lo, hi)
        n = int(done.sum())
        row = {
            "span": (a, b), "lam": lam, "n_done": n, "c": n / (b - a), "c_upper": poisson_rate_upper(n, b - a, conf),
            "burst_done": int((done & burst).sum()),
            "share": share, "share_base": share_base, "h_counter": hit_between(m, lo, hi),
            "kv": float(m["vllm:kv_cache_usage_perc"][w].mean()), "n": float(m["vllm:num_requests_running"][w].mean()),
            "q": float(q.mean()), "q_min": float(q.min()) if len(q) else float("nan"),
            "preemptions": float(np.interp(hi, m.t, m["vllm:num_preemptions_total"])
                                 - np.interp(lo, m.t, m["vllm:num_preemptions_total"])),
        }
        row["capacity_limited"] = bool(len(q) and q.min() > 0)
        row["burst_free"] = row["burst_done"] == 0
        row["cold"] = bool(share <= share_base - cold_hit_drop)
        row["qualifies"] = row["capacity_limited"] and row["burst_free"] and row["cold"]
        rows.append(row)
    return rows


# REG-1 (docs/decisions.md 2026-11-04): the registered runs, spans and thresholds. Not to be changed after approval.
REG1 = {
    "spans": [(0, 60), (60, 180)], "baseline_s": 600, "cold_hit_drop": 0.06, "conf": 0.99, "c_ref": 4.185,
    "default_pool": ["20261102-072216_wipe_preempt_r3_s1", "20261102-053935_wipe_preempt_r3_s2", "20261102-100744_wipe_preempt_r3_s3",
                     "20261102-110200_wipe_preempt_r3.5_s1", "20261102-114305_wipe_preempt_r3.5_s2", "20261102-122411_wipe_preempt_r3.5_s3",
                     "20261102-131353_burst_r3_s1", "20261102-135701_burst_r3_s2", "20261102-144008_burst_r3_s3",
                     "20261102-152316_burst_r3.5_s1", "20261102-160625_burst_r3.5_s2", "20261102-164933_burst_r3.5_s3"],
    "reported_only": ["20261103-015156_wipe_kv72k_r3_s1", "20261103-023254_wipe_kv72k_r3_s2", "20261103-031353_wipe_kv72k_r3_s3",
                      "20261102-234257_burst_kv72k_r3_s1", "20261103-002556_burst_kv72k_r3_s2", "20261103-010856_burst_kv72k_r3_s3",
                      "20261103-203837_wipe_gap5_r4.5_s1", "20261103-211946_wipe_gap5_r4.5_s2", "20261103-220054_wipe_gap5_r4.5_s3",
                      "20261103-224202_wipe_gap5_r3.5_s1", "20261103-232310_wipe_gap5_r3.5_s2", "20261104-000416_wipe_gap5_r3.5_s3",
                      "20261103-161947_burst_gap5_r4.5_s1", "20261103-170255_burst_gap5_r4.5_s2", "20261103-174604_burst_gap5_r4.5_s3",
                      "20261103-182912_burst_gap5_r3.5_s1", "20261103-191220_burst_gap5_r3.5_s2", "20261103-195529_burst_gap5_r3.5_s3"],
}


def reg1_table() -> pd.DataFrame:
    """REG-1 over its registered runs: one row per run and span. Valid runs only (raises otherwise)."""
    from analysis.load import RUNS, load_run
    rows = []
    for group in ("default_pool", "reported_only"):
        for rid in REG1[group]:
            run = load_run(RUNS / rid)
            if not (run["checks"] and run["checks"]["valid"]):
                raise ValueError(f"{rid} is not valid")
            for row in post_trigger_margin(run, REG1["spans"], REG1["baseline_s"], REG1["cold_hit_drop"], REG1["conf"]):
                rows.append({"group": group, "run": rid, "trigger": run["cfg"]["trigger"]["kind"], **row})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    pd.set_option("display.width", 250, "display.max_columns", 40)
    print(reg1_table().round(3).to_string(index=False))
