"""harness/run.py guards added 2026-11-04 (audit items 2-4, 6): defaults, port check, lock."""
import socket
import subprocess
import sys
from pathlib import Path

import yaml

from harness import env_snapshot
from harness.config import load_config, with_defaults
from harness.run import _port_in_use

REPO = Path(__file__).resolve().parent.parent


def test_defaults_sit_beneath_a_config():
    cfg = with_defaults(load_config(REPO / "configs/first_real.yaml"))
    assert cfg["load_lead_s"] == 3.0 and cfg["recorder"]["scrape_timeout_s"] == 0.9 and cfg["recorder"]["interval_s"] == 1.0
    assert cfg["checks"]["rate_sigma"] == 3.0 and cfg["checks"]["max_client_lag_p99_s"] == 0.05
    assert with_defaults({"checks": {"rate_sigma": 2.0}})["checks"]["rate_sigma"] == 2.0  # the config wins


def test_port_in_use():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0)); s.listen()
        port = s.getsockname()[1]
        assert _port_in_use("127.0.0.1", port, 1.0)
    assert not _port_in_use("127.0.0.1", port, 1.0)


def test_untracked_config_makes_the_tree_dirty(tmp_path, monkeypatch):
    calls = {("git", "status", "--porcelain", "--untracked-files=no"): "",
             ("git", "ls-files", "--others", "--exclude-standard", "configs"): "configs/new.yaml"}
    monkeypatch.setattr(env_snapshot, "_cmd", lambda *a: calls.get(a))
    snap = env_snapshot.snapshot()
    assert snap["git_dirty"] and snap["untracked_configs"] == ["configs/new.yaml"]
    calls[("git", "ls-files", "--others", "--exclude-standard", "configs")] = ""
    assert not env_snapshot.snapshot()["git_dirty"]


def test_a_second_run_is_refused_while_the_lock_is_held(tmp_path):
    import fcntl
    lock = REPO / with_defaults({})["lock_file"]
    with open(lock, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        cfg = tmp_path / "x.yaml"
        cfg.write_text(yaml.safe_dump({"extends": str(REPO / "configs/first_real.yaml"), "name": "x"}))
        r = subprocess.run([sys.executable, "-m", "harness.run", str(cfg), "--runs-dir", str(tmp_path / "runs")],
                           cwd=REPO, capture_output=True, text=True, timeout=60)
    assert r.returncode != 0 and "one run at a time" in r.stderr and not (tmp_path / "runs").exists()
