"""Marks a run valid or invalid, with reasons -> checks.json. A run counts only if every check passes."""
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from harness.config import with_defaults
from harness.workload import burst_requests, expected_requests

# NVML clock-throttle bits. A software power cap (0x4) is normal boost behaviour and is ignored.
HW_THROTTLE_MASK = 0x8 | 0x40 | 0x80  # HW slowdown, HW thermal, HW power brake: any sample fails the run
SW_THERMAL_BIT = 0x20                 # SW thermal slowdown: GeForce sets it briefly during boost; fail only if sustained
COUNTER_SUFFIXES = ("_total", "_count", "_sum", "_bucket")


def _jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def _total(sample: dict, name: str) -> float | None:
    vals = [v for k, v in sample["values"].items() if k.split("{", 1)[0] == name]
    return sum(vals) if vals else None


def _hit_between(scrapes: list[dict], a: float, b: float) -> float | None:
    """Counter hit rate over [a, b), interpolated at both ends from the successful scrapes."""
    t = np.array([s["t"] for s in scrapes])
    h = np.array([_total(s, "vllm:prefix_cache_hits_total") or 0.0 for s in scrapes])
    q = np.array([_total(s, "vllm:prefix_cache_queries_total") or 0.0 for s in scrapes])
    if len(t) < 2:
        return None
    dq = np.interp(b, t, q) - np.interp(a, t, q)
    return float((np.interp(b, t, h) - np.interp(a, t, h)) / dq) if dq > 0 else None


def check(name: str, passed: bool | None, detail) -> dict:
    return {"name": name, "passed": passed, "detail": detail}


def run_checks(run_dir: Path) -> dict:
    cfg = with_defaults(yaml.safe_load((run_dir / "config.yaml").read_text()))  # old run folders get today's defaults
    env = json.loads((run_dir / "env.json").read_text())
    c, wl = cfg["checks"], cfg["workload"]
    recording = cfg["recorder"].get("enabled", True)  # configs from before this switch have no key
    sched = pd.read_parquet(run_dir / "schedule.parquet")
    reqs = pd.DataFrame(_jsonl(run_dir / "requests.jsonl"))
    scrapes = _jsonl(run_dir / "metrics.jsonl")
    gpu = pd.DataFrame(_jsonl(run_dir / "gpu.jsonl"))
    out = []

    # 1. Client lag: every request was sent when it was due: at its planned time, or (closed-loop turns, REG-11 draft)
    #    at its release time t_released.
    closed = bool((wl.get("sessions") or {}).get("closed_loop"))  # .get: defaults.yaml was used and can't gain the key
    sent_df = reqs.dropna(subset=["t_sent"]) if len(reqs) else reqs
    due = sent_df.t_released.fillna(sent_df.t_planned).astype(float) if "t_released" in sent_df else sent_df.t_planned
    lag99 = float(np.percentile(sent_df.t_sent - due, 99)) if len(sent_df) else math.inf
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

    # 6. Measured arrival rate matches lambda (Poisson-aware tolerance). With closed-loop turns only the open-loop
    #    arrivals are the generator's: session starts (turn 0, at lambda / turns) and burst requests. Later turns follow
    #    the server, so counting them would fail a run for being slow (REG-11 draft).
    t_lo, t_hi = wl["warmup_s"], wl["duration_s"]
    arr = sent_df[sent_df.turn == 0] if closed and len(sent_df) else sent_df
    n = int(((arr.t_sent >= t_lo) & (arr.t_sent < t_hi)).sum()) if len(arr) else 0
    per = 1 / wl["sessions"]["turns"] if closed else 1.0
    expected = expected_requests(wl, t_lo, t_hi) * per + burst_requests(cfg.get("trigger"), t_lo, t_hi)
    tol = max(c["rate_rel_tolerance"] * expected, c["rate_sigma"] * math.sqrt(expected))
    out.append(check("arrival_rate", abs(n - expected) <= tol,
                     {"measured": n / (t_hi - t_lo), "configured": wl["rate"] * per, "count": n, "expected": expected,
                      "closed_loop": closed}))

    # 6b. Closed-loop turns only (REG-11 review, T2): every later turn never sent was blocked by its own session, i.e.
    #     its previous turn never ended, or ended so late that end + planned gap is past the drain deadline (1 s slack).
    #     Anything else means a chain stopped releasing turns, which would look like a slow server.
    if closed and len(reqs):
        q = reqs.sort_values(["session_id", "turn"])
        q = q[~q.request_id.isin(sched.request_id[sched.burst])] if "burst" in sched else q
        g = q.groupby("session_id")
        prev_end, prev_planned = g.t_end.shift(), g.t_planned.shift()
        deadline = float(sched.t_planned.max()) + cfg["drain_s"]
        unsent = q.t_sent.isna() & (q.turn > 0)
        blocked = prev_end.isna() | (prev_end + q.t_planned - prev_planned > deadline - 1.0)
        bad = q[unsent & ~blocked]
        out.append(check("release_chain", len(bad) == 0,
                         {"unsent_later_turns": int(unsent.sum()), "unexplained": int(len(bad)),
                          "examples": bad.request_id.head(5).tolist()}))

    # 7. Code state is recorded exactly.
    out.append(check("clean_git", not (c["require_clean_git"] and env.get("git_dirty")),
                     {"commit": env.get("git_commit"), "dirty": env.get("git_dirty"),
                      "untracked_configs": env.get("untracked_configs")}))

    # 7b. The KV pool the server reports is the one the config expects (only if the config states it).
    if c["expected_kv_tokens"] is not None:
        log = (run_dir / "server.log").read_text(errors="replace") if (run_dir / "server.log").exists() else ""
        m = re.search(r"GPU KV cache size: ([\d,]+) tokens", log)
        kv = int(m.group(1).replace(",", "")) if m else None
        out.append(check("kv_capacity", kv == c["expected_kv_tokens"], {"logged": kv, "expected": c["expected_kv_tokens"]}))

    # 7c. The GPU power limit stayed at the value the config expects, in every GPU sample of the run (only if the config
    #     states it). The GPU is shared, so the limit can change under a run. Read with .get: configs/defaults.yaml was
    #     used by runs and can't gain the key, so a missing key means "not checked" (REG-8, decisions.md 2026-11-06).
    if c.get("expected_power_limit_w") is not None:
        lim = gpu.power_limit_w if "power_limit_w" in gpu else pd.Series(dtype=float)
        # No samples, or a sample without a value, cannot show that the limit held (REG-8 review, T10).
        dev = float((lim - c["expected_power_limit_w"]).abs().max()) if len(lim) and not lim.isna().any() else math.inf
        out.append(check("power_limit", dev <= c["power_limit_tol_w"],
                         {"expected_w": c["expected_power_limit_w"], "max_dev_w": dev, "samples": len(lim),
                          "min_w": float(lim.min()) if len(lim) else None,
                          "max_w": float(lim.max()) if len(lim) else None}))

    # 8. Only with a trigger. Burst: every burst request in the schedule was sent.
    #    Cache wipe: the cache was wiped exactly once, while arrivals were still running.
    trig = cfg.get("trigger")
    man = c["manipulation"]
    if trig is not None and trig.get("kind") == "burst":
        ids = set(sched.request_id[sched.burst]) if "burst" in sched else set()
        sent_ids = set(reqs.request_id[reqs.t_sent.notna()]) if len(reqs) else set()
        out.append(check("trigger", bool(ids) and ids <= sent_ids, {"burst_requests": len(ids), "sent": len(ids & sent_ids)}))
        if man["burst_min_kv_max"] is not None:
            # 9. Manipulation: the burst filled the KV pool (threshold registered before any run is judged by it).
            a, b = trig["at_s"], trig["at_s"] + trig["duration_s"]
            kvs = [_total(s, "vllm:kv_cache_usage_perc") for s in ok_scrapes if a <= s["t"] < b]
            kv_max = max((k for k in kvs if k is not None), default=None)
            out.append(check("manipulation", kv_max is not None and kv_max >= man["burst_min_kv_max"],
                             {"kv_max_during_burst": kv_max, "min": man["burst_min_kv_max"]}))
    elif trig is not None:
        attempts = _jsonl(run_dir / "trigger.jsonl")
        wiped = [a for a in attempts if a["success"]]
        # The first attempt must start on time (idle mode may then retry for up to max_wait_s, by design).
        delay = attempts[0]["t_start"] - trig["at_s"] if attempts else None
        on_time = delay is not None and abs(delay) <= c["max_trigger_delay_s"]
        out.append(check("trigger", len(wiped) == 1 and wiped[0]["t_end"] < wl["duration_s"] and on_time,
                         {"attempts": len(attempts), "wipe": wiped[0] if wiped else None, "first_attempt_delay_s": delay,
                          "last_attempt": attempts[-1] if attempts else None}))
        if man["wipe_max_hit"] is not None and wiped:
            # 9. Manipulation: the hit rate right after the wipe fell (threshold registered before any run is judged by it).
            a, b = wiped[0]["t_end"], wiped[0]["t_end"] + man["wipe_window_s"]
            hit = _hit_between(ok_scrapes, a, b)
            out.append(check("manipulation", hit is not None and hit <= man["wipe_max_hit"],
                             {"hit_after_wipe": hit, "window_s": man["wipe_window_s"], "max": man["wipe_max_hit"]}))

    failed = [x["name"] for x in out if x["passed"] is False]
    return {"valid": not failed, "failed": failed, "checks": out}


def write(run_dir: Path) -> dict:
    res = run_checks(run_dir)
    (run_dir / "checks.json").write_text(json.dumps(res, indent=2, default=str))
    return res


if __name__ == "__main__":
    r = run_checks(Path(sys.argv[1]))  # re-check without overwriting the run's checks.json
    print(json.dumps(r, indent=2, default=str))
