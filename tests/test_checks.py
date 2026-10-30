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
