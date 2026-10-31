"""Marks a run valid or invalid, with reasons -> checks.json. A run counts only if every check passes."""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

# NVML clock-throttle bits. A software power cap (0x4) is normal boost behaviour and is ignored.
HW_THROTTLE_MASK = 0x8 | 0x40 | 0x80  # HW slowdown, HW thermal, HW power brake: any sample fails the run
SW_THERMAL_BIT = 0x20                 # SW thermal slowdown: GeForce sets it briefly during boost; fail only if sustained
COUNTER_SUFFIXES = ("_total", "_count", "_sum", "_bucket")


def _jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def check(name: str, passed: bool | None, detail) -> dict:
    return {"name": name, "passed": passed, "detail": detail}


def run_checks(run_dir: Path) -> dict:
    cfg = yaml.safe_load((run_dir / "config.yaml").read_text())
    env = json.loads((run_dir / "env.json").read_text())
    c, wl = cfg["checks"], cfg["workload"]
    recording = cfg["recorder"].get("enabled", True)  # configs from before this switch have no key
    sched = pd.read_parquet(run_dir / "schedule.parquet")
    reqs = pd.DataFrame(_jsonl(run_dir / "requests.jsonl"))
    scrapes = _jsonl(run_dir / "metrics.jsonl")
    gpu = pd.DataFrame(_jsonl(run_dir / "gpu.jsonl"))
    out = []

    # 1. Client lag: arrivals were really open-loop.
    sent = reqs.dropna(subset=["t_sent"]) if len(reqs) else reqs
    lag99 = float(np.percentile(sent.t_sent - sent.t_planned, 99)) if len(sent) else math.inf
    out.append(check("client_lag", lag99 <= c["max_client_lag_p99_s"], {"p99_s": lag99}))

    # 2. No timeouts, retries or connection errors.
    statuses = reqs.status.value_counts().to_dict() if len(reqs) else {}
    n_err = sum(v for k, v in statuses.items() if k not in ("ok", "unfinished"))
    out.append(check("no_errors", n_err == 0, statuses))

    # 3. Accounting: every scheduled request recorded once; ok count matches vLLM's success counter.
    ok_scrapes = [s for s in scrapes if "values" in s]
    succ = None
    if len(ok_scrapes) >= 2:
        f = lambda s: sum(v for k, v in s["values"].items() if k.startswith("vllm:request_success_total{"))
        succ = f(ok_scrapes[-1]) - f(ok_scrapes[0])
    n_ok = int(statuses.get("ok", 0))
    ids_ok = len(reqs) == len(sched) and (len(reqs) == 0 or reqs.request_id.is_unique)
    # A streaming request cut off at the drain deadline may have finished in vLLM before the client read its last chunk.
    cut_off = int((reqs.status.eq("unfinished") & reqs.t_first_token.notna()).sum()) if "t_first_token" in reqs else 0
    out.append(check("accounting", ids_ok and succ is not None and n_ok <= succ <= n_ok + cut_off,
                     {"scheduled": len(sched), "recorded": len(reqs), "ok": n_ok, "vllm_success_delta": succ,
                      "cut_off_with_first_token": cut_off}))

    # 4. Counters never go down; no long scrape gaps (recorder on) or failed scrapes.
    decreases = []
    for a, b in zip(ok_scrapes, ok_scrapes[1:]):
        for k, v in b["values"].items():
            if k.split("{", 1)[0].endswith(COUNTER_SUFFIXES) and v < a["values"].get(k, -math.inf):
                decreases.append({"t": b["t"], "metric": k})
    ts = [s["t"] for s in scrapes]
    max_gap = float(np.max(np.diff(ts))) if len(ts) >= 2 else math.inf
    n_fail = len(scrapes) - len(ok_scrapes)
    gap_ok = max_gap <= c["max_scrape_gap_s"] or not recording
    out.append(check("recorder", not decreases and gap_ok and n_fail == 0,
                     {"counter_decreases": decreases[:10], "max_gap_s": max_gap, "failed_scrapes": n_fail}))

    # 5. GPU: SM clock steady and no thermal throttling during the measured window.
    if cfg["server"]["kind"] == "fake":
        out.append(check("gpu_steady", None, "skipped: fake server"))
    elif not recording:
        out.append(check("gpu_steady", None, "skipped: recorder off, no GPU samples"))
    elif gpu.empty:
        out.append(check("gpu_steady", False, "no gpu.jsonl data"))
    else:
        w = gpu[(gpu.t >= wl["warmup_s"]) & (gpu.t <= wl["duration_s"])]
        busy = w[w.util_pct >= c["gpu_busy_util_pct"]]  # idle clocks are not throttling
        cv = float(busy.sm_clock_mhz.std() / busy.sm_clock_mhz.mean()) if len(busy) > 1 else 0.0
        reasons = w.throttle_reasons.astype(int)
        hw = int(((reasons & HW_THROTTLE_MASK) != 0).sum())
        sw_frac = float(((reasons & SW_THERMAL_BIT) != 0).mean()) if len(w) else 0.0
        out.append(check("gpu_steady",
                         cv <= c["max_sm_clock_cv"] and hw == 0 and sw_frac <= c["max_sw_thermal_frac"],
                         {"busy_sm_clock_cv": cv, "busy_samples": len(busy), "hw_throttle_samples": hw,
                          "sw_thermal_frac": sw_frac, "max_temp_c": float(w.temp_c.max()) if len(w) else None}))

    # 6. Measured arrival rate matches lambda (Poisson-aware tolerance).
    t_lo, t_hi = wl["warmup_s"], wl["duration_s"]
    n = int(((sent.t_sent >= t_lo) & (sent.t_sent < t_hi)).sum()) if len(sent) else 0
    expected = wl["rate"] * (t_hi - t_lo)
    tol = max(c["rate_rel_tolerance"] * expected, 3 * math.sqrt(expected))
    out.append(check("arrival_rate", abs(n - expected) <= tol,
                     {"measured": n / (t_hi - t_lo), "configured": wl["rate"], "count": n, "expected": expected}))

    # 7. Code state is recorded exactly.
    out.append(check("clean_git", not (c["require_clean_git"] and env.get("git_dirty")),
                     {"commit": env.get("git_commit"), "dirty": env.get("git_dirty")}))

    failed = [x["name"] for x in out if x["passed"] is False]
    return {"valid": not failed, "failed": failed, "checks": out}


def write(run_dir: Path) -> dict:
    res = run_checks(run_dir)
    (run_dir / "checks.json").write_text(json.dumps(res, indent=2, default=str))
    return res


if __name__ == "__main__":
    r = run_checks(Path(sys.argv[1]))  # re-check without overwriting the run's checks.json
    print(json.dumps(r, indent=2, default=str))
