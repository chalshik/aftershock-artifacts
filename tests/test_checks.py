import json

import pandas as pd
import yaml

from harness import checks
from harness.run import load_config
from tests.test_workload import CONFIGS


def make_run(tmp_path, n=100, rate=1.0, lag=0.001, status="ok", success_delta=None, dirty=False, gap=1.0):
    cfg = load_config(CONFIGS / "first_real.yaml")
    cfg["server"]["kind"] = "fake"
    cfg["workload"].update(rate=rate, duration_s=n / rate, warmup_s=0)
    (tmp_path / "config.yaml").write_text(yaml.safe_dump(cfg))
    (tmp_path / "env.json").write_text(json.dumps({"git_dirty": dirty, "git_commit": "abc"}))
    t = [i / rate for i in range(n)]
    pd.DataFrame({"request_id": range(n), "t_planned": t}).to_parquet(tmp_path / "schedule.parquet")
    with open(tmp_path / "requests.jsonl", "w") as f:
        for i, tp in enumerate(t):
            f.write(json.dumps({"request_id": i, "t_planned": tp, "t_sent": tp + lag, "status": status}) + "\n")
    ok = n if status == "ok" else 0
    succ = ok if success_delta is None else success_delta
    with open(tmp_path / "metrics.jsonl", "w") as f:
        steps = int(n / rate / gap) + 2
        for k in range(steps):
            v = succ * k / (steps - 1)
            f.write(json.dumps({"t": k * gap, "values": {'vllm:request_success_total{finished_reason="length"}': v}}) + "\n")
    return tmp_path


def failed(run_dir):
    return checks.run_checks(run_dir)["failed"]


def test_good_run_valid(tmp_path):
    assert failed(make_run(tmp_path)) == []


def test_client_lag(tmp_path):
    assert "client_lag" in failed(make_run(tmp_path, lag=0.5))


def test_errors(tmp_path):
    assert "no_errors" in failed(make_run(tmp_path, status="client_error"))


def test_accounting(tmp_path):
    assert "accounting" in failed(make_run(tmp_path, success_delta=90))


def with_cut_off(d, unfinished, first_tokens):
    """Mark the last `unfinished` requests as cut off at the drain; `first_tokens` of them had started streaming."""
    recs = [json.loads(l) for l in (d / "requests.jsonl").read_text().splitlines()]
    for i, rec in enumerate(recs[-unfinished:]):
        rec.update(status="unfinished", t_first_token=rec["t_sent"] + 1 if i < first_tokens else None)
    (d / "requests.jsonl").write_text("".join(json.dumps(r) + "\n" for r in recs))
    return d


def test_accounting_allows_requests_cut_off_after_first_token(tmp_path):
    assert "accounting" not in failed(with_cut_off(make_run(tmp_path, success_delta=91), 10, 1))


def test_accounting_exact_match_with_cut_off_requests(tmp_path):
    assert "accounting" not in failed(with_cut_off(make_run(tmp_path, success_delta=90), 10, 1))


def test_accounting_fails_above_cut_off_allowance(tmp_path):
    assert "accounting" in failed(with_cut_off(make_run(tmp_path, success_delta=92), 10, 1))


def test_accounting_no_allowance_without_first_token(tmp_path):
    assert "accounting" in failed(with_cut_off(make_run(tmp_path, success_delta=91), 10, 0))


def test_accounting_fails_when_vllm_counts_fewer(tmp_path):
    assert "accounting" in failed(with_cut_off(make_run(tmp_path, success_delta=89), 10, 1))


def recorder_off(d):
    cfg = yaml.safe_load((d / "config.yaml").read_text())
    cfg["recorder"]["enabled"] = False
    cfg["server"]["kind"] = "vllm"
    (d / "config.yaml").write_text(yaml.safe_dump(cfg))
    return d


def test_recorder_off_allows_scrape_gap_and_no_gpu_samples(tmp_path):
    assert failed(recorder_off(make_run(tmp_path, gap=3.0))) == []


def test_recorder_off_still_fails_a_failed_scrape(tmp_path):
    d = recorder_off(make_run(tmp_path, gap=3.0))
    with open(d / "metrics.jsonl", "a") as f:
        f.write(json.dumps({"t": 1000, "error": "URLError"}) + "\n")
    assert "recorder" in failed(d)


def test_recorder_off_still_checks_accounting(tmp_path):
    assert "accounting" in failed(recorder_off(make_run(tmp_path, success_delta=90)))


def with_trigger(d, attempts):
    cfg = yaml.safe_load((d / "config.yaml").read_text())
    cfg["trigger"] = {"kind": "cache_wipe", "at_s": 10, "mode": "preempt"}
    (d / "config.yaml").write_text(yaml.safe_dump(cfg))
    (d / "trigger.jsonl").write_text("".join(json.dumps(a) + "\n" for a in attempts))
    return d


def test_trigger_one_wipe_passes(tmp_path):
    assert failed(with_trigger(make_run(tmp_path), [{"success": True, "t_start": 10.0, "t_end": 10.1}])) == []


def test_trigger_no_successful_wipe_fails(tmp_path):
    assert "trigger" in failed(with_trigger(make_run(tmp_path), [{"success": False, "t_start": 10.0, "t_end": 10.1}]))


def test_trigger_no_attempt_fails(tmp_path):
    assert "trigger" in failed(with_trigger(make_run(tmp_path), []))


def test_trigger_two_wipes_fail(tmp_path):
    assert "trigger" in failed(with_trigger(make_run(tmp_path), [{"success": True, "t_start": 10.0, "t_end": 10.1}] * 2))


def test_trigger_wipe_after_arrivals_end_fails(tmp_path):
    assert "trigger" in failed(with_trigger(make_run(tmp_path), [{"success": True, "t_start": 10.0, "t_end": 500.0}]))


def with_burst(d, sent_all=True):
    cfg = yaml.safe_load((d / "config.yaml").read_text())
    cfg["trigger"] = {"kind": "burst", "at_s": 10, "duration_s": 5, "rate": 1.0, "prompt_tokens": 8}
    (d / "config.yaml").write_text(yaml.safe_dump(cfg))
    s = pd.read_parquet(d / "schedule.parquet")
    s["burst"] = s.request_id.isin([20, 21, 22])
    s.to_parquet(d / "schedule.parquet")
    if not sent_all:
        recs = [json.loads(l) for l in (d / "requests.jsonl").read_text().splitlines()]
        recs[21]["t_sent"] = None
        (d / "requests.jsonl").write_text("".join(json.dumps(r) + "\n" for r in recs))
    return d


def test_burst_all_sent_passes(tmp_path):
    assert "trigger" not in failed(with_burst(make_run(tmp_path)))


def test_burst_request_not_sent_fails(tmp_path):
    assert "trigger" in failed(with_burst(make_run(tmp_path), sent_all=False))


def test_scrape_gap(tmp_path):
    assert "recorder" in failed(make_run(tmp_path, gap=3.0))


def test_dirty_git(tmp_path):
    assert "clean_git" in failed(make_run(tmp_path, dirty=True))


def test_counter_decrease(tmp_path):
    d = make_run(tmp_path)
    with open(d / "metrics.jsonl", "a") as f:
        f.write(json.dumps({"t": 1000, "values": {'vllm:request_success_total{finished_reason="length"}': 0}}) + "\n")
    assert "recorder" in failed(d)


def with_gpu(d, masks, clocks=None, util=100):
    cfg = yaml.safe_load((d / "config.yaml").read_text())
    cfg["server"]["kind"] = "vllm"
    (d / "config.yaml").write_text(yaml.safe_dump(cfg))
    clocks = clocks or [2040] * len(masks)
    with open(d / "gpu.jsonl", "w") as f:
        for i, (m, c) in enumerate(zip(masks, clocks)):
            f.write(json.dumps({"t": float(i), "throttle_reasons": m, "sm_clock_mhz": c,
                                "util_pct": util if c == 2040 else 0, "temp_c": 50}) + "\n")
    return d


def test_gpu_brief_sw_thermal_and_idle_clocks_ok(tmp_path):
    masks = [0x4] * 50 + [0x24] + [0] * 49
    clocks = [2040, 1860] * 50
    assert "gpu_steady" not in failed(with_gpu(make_run(tmp_path), masks, clocks))


def test_gpu_hw_throttle_fails(tmp_path):
    assert "gpu_steady" in failed(with_gpu(make_run(tmp_path), [0] * 99 + [0x40]))


def test_gpu_sustained_sw_thermal_fails(tmp_path):
    assert "gpu_steady" in failed(with_gpu(make_run(tmp_path), [0x20] * 10 + [0] * 90))


# ---- checks added 2026-11-04 (audit items 1-8), all off or lenient by default (configs/defaults.yaml)

def set_checks(d, **kw):
    cfg = yaml.safe_load((d / "config.yaml").read_text())
    cfg.setdefault("checks", {}).update(kw)
    (d / "config.yaml").write_text(yaml.safe_dump(cfg))
    return d


def names(run_dir):
    return [c["name"] for c in checks.run_checks(run_dir)["checks"]]


def test_new_checks_are_skipped_by_default(tmp_path):
    d = make_run(tmp_path)
    assert "kv_capacity" not in names(d) and "manipulation" not in names(d) and failed(d) == []


def test_kv_capacity(tmp_path):
    d = set_checks(make_run(tmp_path), expected_kv_tokens=96656)
    (d / "server.log").write_text("INFO GPU KV cache size: 96,656 tokens\n")
    assert "kv_capacity" in names(d) and "kv_capacity" not in failed(d)
    (d / "server.log").write_text("INFO GPU KV cache size: 72,480 tokens\n")
    assert "kv_capacity" in failed(d)
    (d / "server.log").write_text("no such line\n")
    assert "kv_capacity" in failed(d)


def write_gpu(d, limits):
    with open(d / "gpu.jsonl", "w") as f:
        for i, lim in enumerate(limits):
            f.write(json.dumps({"t": float(i), "power_w": 300.0, "power_limit_w": lim, "sm_clock_mhz": 1800,
                                "temp_c": 60, "util_pct": 90, "throttle_reasons": 4}) + "\n")
    return d


def test_power_limit_is_skipped_without_the_key(tmp_path):
    d = write_gpu(make_run(tmp_path), [420.0] * 5)
    assert "power_limit" not in names(d)  # old configs and defaults.yaml have no key (REG-8, option 1)


def test_power_limit(tmp_path):
    d = set_checks(write_gpu(make_run(tmp_path), [350.0] * 5), expected_power_limit_w=350, power_limit_tol_w=1.0)
    assert "power_limit" in names(d) and "power_limit" not in failed(d)
    write_gpu(d, [350.0, 350.0, 420.0, 350.0])  # one sample at another limit, e.g. reset by the other GPU user
    assert "power_limit" in failed(d)
    write_gpu(d, [350.4] * 3)                   # within the tolerance
    assert "power_limit" not in failed(d)
    write_gpu(d, [350.0, None, 350.0])          # a sample without a value (REG-8 review, T10)
    assert "power_limit" in failed(d)
    write_gpu(d, [])                            # no GPU samples: cannot show the limit held
    assert "power_limit" in failed(d)


def test_trigger_first_attempt_must_start_on_time(tmp_path):
    d = with_trigger(make_run(tmp_path), [{"success": True, "t_start": 12.5, "t_end": 12.6}])  # at_s = 10
    assert "trigger" in failed(d)
    d = with_trigger(make_run(tmp_path), [{"success": True, "t_start": 10.2, "t_end": 10.3}])
    assert "trigger" not in failed(d)


def test_idle_retries_are_allowed_after_an_on_time_first_attempt(tmp_path):
    attempts = [{"success": False, "t_start": 10.0, "t_end": 10.01}, {"success": True, "t_start": 21.5, "t_end": 21.6}]
    assert "trigger" not in failed(with_trigger(make_run(tmp_path), attempts))


def _with_hits(d, hit_after):
    """Rewrite metrics: hit 0.6 per scrape, `hit_after` from t = 10 (the wipe) on; KV 0.5, or 1.0 from t = 40 to 50."""
    lines = []
    for k in range(0, 102):
        h = 0.6 if k <= 10 else hit_after
        lines.append({"t": float(k), "values": {'vllm:request_success_total{finished_reason="length"}': 100.0 * k / 101,
                                                "vllm:prefix_cache_queries_total{}": 100.0 * k,
                                                "vllm:prefix_cache_hits_total{}": sum(100 * (0.6 if j <= 10 else hit_after) for j in range(1, k + 1)),
                                                "vllm:kv_cache_usage_perc{}": 1.0 if 40 <= k < 50 else 0.5}})
    (d / "metrics.jsonl").write_text("".join(json.dumps(x) + "\n" for x in lines))
    return d


def test_manipulation_wipe(tmp_path):
    attempts = [{"success": True, "t_start": 10.0, "t_end": 10.0}]
    d = set_checks(_with_hits(with_trigger(make_run(tmp_path), attempts), 0.2), manipulation={"wipe_window_s": 15, "wipe_max_hit": 0.4})
    assert "manipulation" in names(d) and "manipulation" not in failed(d)
    d = set_checks(_with_hits(with_trigger(make_run(tmp_path), attempts), 0.55), manipulation={"wipe_window_s": 15, "wipe_max_hit": 0.4})
    assert "manipulation" in failed(d)


def test_manipulation_burst(tmp_path):
    d = _with_hits(with_burst(make_run(tmp_path)), 0.6)
    cfg = yaml.safe_load((d / "config.yaml").read_text())
    cfg["trigger"].update(at_s=40, duration_s=10)
    (d / "config.yaml").write_text(yaml.safe_dump(cfg))
    assert "manipulation" not in failed(set_checks(d, manipulation={"burst_min_kv_max": 0.99}))
    cfg = yaml.safe_load((d / "config.yaml").read_text())
    cfg["trigger"].update(at_s=60, duration_s=10)  # KV stays at 0.5 in this burst
    (d / "config.yaml").write_text(yaml.safe_dump(cfg))
    assert "manipulation" in failed(d)
