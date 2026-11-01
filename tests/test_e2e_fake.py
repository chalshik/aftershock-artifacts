"""End to end: run.py against tests/fake_vllm.py produces a complete, valid run folder."""
import json
import socket
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def run_fake(tmp_path, **over):
    cfg = {"extends": str(REPO / "configs" / "first_real.yaml"), "name": "e2e_fake",
           "server": {"kind": "fake", "port": free_port(), "startup_timeout_s": 30, "stop_grace_s": 5},
           "workload": {"rate": 4.0, "duration_s": 20, "warmup_s": 5, "output_tokens": 8,
                        "sessions": {"turns": 3, "turn_gap_s": {"dist": "exponential", "mean": 2.0}}},
           "cpus": {"vllm": None, "loadgen": None, "recorder": None},  # taskset is Linux-only
           "drain_s": 10, "checks": {"require_clean_git": False}, **over}
    path = tmp_path / "e2e.yaml"
    path.write_text(yaml.safe_dump(cfg))
    runs = tmp_path / "runs"
    subprocess.run([sys.executable, "-m", "harness.run", str(path), "--runs-dir", str(runs)],
                   cwd=REPO, check=True, timeout=120)
    (run_dir,) = runs.iterdir()
    return run_dir


def test_smoke_against_fake_server(tmp_path):
    run_dir = run_fake(tmp_path)
    for f in ["config.yaml", "env.json", "schedule.parquet", "prompts.parquet", "requests.jsonl",
              "metrics.jsonl", "events.jsonl", "server.log", "checks.json"]:
        assert (run_dir / f).exists(), f
    res = json.loads((run_dir / "checks.json").read_text())
    assert res["valid"], res
    reqs = pd.read_json(run_dir / "requests.jsonl", lines=True)
    assert (reqs.status == "ok").all()
    later = reqs[reqs.turn > 0]
    assert (later.cached_tokens > 0).all()  # prefix reuse across turns reaches the server


def test_recorder_off_scrapes_only_around_the_load(tmp_path):
    run_dir = run_fake(tmp_path, recorder={"enabled": False})
    scrapes = [json.loads(l) for l in (run_dir / "metrics.jsonl").read_text().splitlines()]
    assert len(scrapes) == 2 and scrapes[0]["t"] < 0 and scrapes[1]["t"] > 20
    assert not (run_dir / "gpu.jsonl").exists()
    res = json.loads((run_dir / "checks.json").read_text())
    assert res["valid"], res


def dev_server():
    return {"kind": "fake", "port": free_port(), "startup_timeout_s": 30, "stop_grace_s": 5,
            "env": {"VLLM_SERVER_DEV_MODE": "1"}}


WIPE = {"kind": "cache_wipe", "at_s": 12, "mode": "preempt", "request_timeout_s": 5}


def test_preempt_wipe_empties_the_cache(tmp_path):
    run_dir = run_fake(tmp_path, server=dev_server(), trigger=WIPE)
    res = json.loads((run_dir / "checks.json").read_text())
    assert res["valid"], res
    (wipe,) = [json.loads(l) for l in (run_dir / "trigger.jsonl").read_text().splitlines()]
    assert wipe["success"] and wipe["t_start"] >= 12
    reqs = pd.read_json(run_dir / "requests.jsonl", lines=True).sort_values("t_sent")
    assert reqs[reqs.t_sent > wipe["t_end"]].iloc[0].cached_tokens == 0


def test_idle_wipe_retries_until_nothing_holds_blocks(tmp_path):
    trig = {**WIPE, "mode": "idle", "retry_interval_s": 0.001, "max_wait_s": 5}
    run_dir = run_fake(tmp_path, server=dev_server(), trigger=trig)
    res = json.loads((run_dir / "checks.json").read_text())
    assert res["valid"], res
    attempts = [json.loads(l) for l in (run_dir / "trigger.jsonl").read_text().splitlines()]
    assert attempts[-1]["success"] and not any(a["success"] for a in attempts[:-1])


def test_wipe_without_dev_mode_stops_before_the_run(tmp_path):
    with pytest.raises(subprocess.CalledProcessError):
        run_fake(tmp_path, trigger=WIPE)
    assert not (tmp_path / "runs").exists()


def test_no_trigger_in_dev_mode_writes_no_trigger_file(tmp_path):
    run_dir = run_fake(tmp_path, server=dev_server())
    assert not (run_dir / "trigger.jsonl").exists()
    res = json.loads((run_dir / "checks.json").read_text())
    assert res["valid"] and "trigger" not in [c["name"] for c in res["checks"]]
