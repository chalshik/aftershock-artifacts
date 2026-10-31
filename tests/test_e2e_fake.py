"""End to end: run.py against tests/fake_vllm.py produces a complete, valid run folder."""
import json
import socket
import subprocess
import sys
from pathlib import Path

import pandas as pd
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
