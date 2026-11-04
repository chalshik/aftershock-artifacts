"""The only entry point. One config (or sweep) -> one run folder per rate under runs/.

    uv run python -m harness.run configs/first_real.yaml

Order: config + env + schedule -> vLLM -> ready -> recorder + trigger -> loadgen -> drain -> stop -> checks.
"""
import argparse
import copy
import fcntl
import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml

from harness import checks, env_snapshot, trigger, workload
from harness.config import _merge, load_config, with_defaults  # noqa: F401  (load_config is imported from here by tests)
from harness.recorder import scrape

REPO = Path(__file__).resolve().parent.parent


def expand(cfg: dict) -> list[dict]:
    if not cfg.get("sweep"):
        return [cfg]
    runs = []
    for rate in cfg["sweep"]["rates"]:
        c = _merge(cfg, {"name": f"{cfg['name']}_r{rate:g}", "workload": {"rate": rate}})
        c["sweep_parent"] = cfg["name"]
        runs.append(c)
    return runs


def server_cmd(cfg: dict) -> list[str]:
    srv = cfg["server"]
    if srv["kind"] == "fake":
        cmd = [sys.executable, str(REPO / "tests" / "fake_vllm.py")]
    else:
        cmd = ["vllm", "serve", cfg["model"]]
    cmd += ["--host", srv["host"], "--port", str(srv["port"])]
    for flag, val in (srv.get("args") or {}).items():
        if val is None or val is False:
            continue
        cmd += [flag] if val is True else [flag, str(val)]
    return _pin(cfg["cpus"]["vllm"]) + cmd


def _pin(cores: str | None) -> list[str]:
    return ["taskset", "-c", str(cores)] if cores else []


def _scrape_once(run_dir: Path, base: str, t: float, timeout_s: float):
    """With the recorder off: one scrape on each side of the load, so accounting still works and the load sees none."""
    try:
        rec = {"t": t, "values": scrape(f"{base}/metrics", timeout_s)}
    except Exception as e:
        rec = {"t": t, "error": f"{type(e).__name__}: {e}"[:200]}
    with open(run_dir / "metrics.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")


class Events:
    def __init__(self, path: Path):
        self.f, self.t0 = open(path, "a"), None

    def __call__(self, event: str, **kw):
        now = time.monotonic()
        rec = {"t": None if self.t0 is None else now - self.t0, "t_mono": now,
               "wall": datetime.now(timezone.utc).isoformat(), "event": event, **kw}
        self.f.write(json.dumps(rec, default=str) + "\n")
        self.f.flush()
        print(f"[run] {event} {kw if kw else ''}", flush=True)


def _http_ok(url: str, timeout_s: float) -> bool:
    try:
        return urllib.request.urlopen(url, timeout=timeout_s).status == 200
    except Exception:
        return False


def _port_in_use(host: str, port: int, timeout_s: float) -> bool:
    """Something already listens there: our server would fail to bind, and the readiness probe would reach the other one."""
    with socket.socket() as s:
        s.settimeout(timeout_s)
        return s.connect_ex((host, port)) == 0


def _gpu_processes() -> str | None:
    try:
        return subprocess.run(["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _stop(proc: subprocess.Popen | None, sig: int, grace: float):
    if proc is None or proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, sig)
        proc.wait(timeout=grace)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()
    except ProcessLookupError:
        pass


def run_one(cfg: dict, runs_dir: Path, allow_dirty: bool) -> Path:
    wl, srv = cfg["workload"], cfg["server"]
    if wl.get("rate") is None:
        raise SystemExit(f"{cfg['name']}: workload.rate is not set")
    if cfg.get("trigger") is not None:
        trigger.validate(cfg)

    env = env_snapshot.snapshot()
    if env["git_dirty"] and cfg["checks"]["require_clean_git"] and not allow_dirty:
        raise SystemExit("git tree is dirty (or untracked files under configs/): commit first "
                         "(or --allow-dirty, which marks the run invalid)")
    if _port_in_use(srv["host"], srv["port"], srv["health_timeout_s"]):
        raise SystemExit(f"{srv['host']}:{srv['port']} is already in use: another server is running")

    run_id = f"{datetime.now(timezone.utc):%Y%m%d-%H%M%S}_{cfg['name']}"
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=True)
    cfg = {**cfg, "run_id": run_id}
    (run_dir / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    (run_dir / "env.json").write_text(json.dumps(env, indent=2))
    ev = Events(run_dir / "events.jsonl")
    ev("start", run_id=run_id, git_commit=env["git_commit"])

    sched, prompts = workload.build_schedule(wl, cfg["seed"], cfg.get("trigger"))
    sched.to_parquet(run_dir / "schedule.parquet", index=False)
    prompts.to_parquet(run_dir / "prompts.parquet", index=False)
    ev("schedule_written", **workload.summary(sched))

    server = recorder = loadgen = trig = None
    aborted = False
    py = [sys.executable, "-m"]
    child_env = {**os.environ, "PYTHONPATH": str(REPO)}
    try:
        cmd = server_cmd(cfg)
        server_env = srv.get("env") or {}  # configs from before this key have none
        ev("server_start", cmd=" ".join(cmd), server_env=server_env)
        with open(run_dir / "server.log", "w") as log:
            server = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT,
                                      start_new_session=True, env={**child_env, **server_env})
        base = f"http://{srv['host']}:{srv['port']}"
        deadline = time.monotonic() + srv["startup_timeout_s"]
        while not _http_ok(f"{base}/health", srv["health_timeout_s"]):
            if server.poll() is not None or time.monotonic() > deadline:
                ev("server_failed", returncode=server.poll())
                raise SystemExit(f"server did not become ready; see {run_dir / 'server.log'}")
            time.sleep(1)
        ev("server_ready", engine_config=_engine_config_lines(run_dir / "server.log"))

        t0 = time.monotonic() + cfg["load_lead_s"]
        ev.t0 = t0
        recording = cfg["recorder"].get("enabled", True)  # configs from before this switch have no key
        if recording:
            recorder = subprocess.Popen(_pin(cfg["cpus"]["recorder"]) + py +
                                        ["harness.recorder", str(run_dir), repr(t0)],
                                        start_new_session=True, env=child_env, cwd=REPO)
        else:
            _scrape_once(run_dir, base, time.monotonic() - t0, cfg["recorder"]["scrape_timeout_s"])
        if (cfg.get("trigger") or {}).get("kind") == "cache_wipe":  # a burst is already in the schedule
            trig = subprocess.Popen(_pin(cfg["cpus"]["recorder"]) + py +  # sleeps until at_s, then one short call
                                    ["harness.trigger", str(run_dir), repr(t0)],
                                    start_new_session=True, env=child_env, cwd=REPO)
        loadgen = subprocess.Popen(_pin(cfg["cpus"]["loadgen"]) + py +
                                   ["harness.loadgen", str(run_dir), repr(t0)],
                                   start_new_session=True, env=child_env, cwd=REPO)
        ev("load_t0_planned", t0_mono=t0, wall_at_t0=time.time() + (t0 - time.monotonic()))
        warm_logged = wl["warmup_s"] <= 0
        while loadgen.poll() is None:
            if server.poll() is not None:
                ev("server_died", returncode=server.returncode)
                break
            if not warm_logged and time.monotonic() >= t0 + wl["warmup_s"]:
                ev("warmup_end")
                warm_logged = True
            time.sleep(0.5)
        ev("load_end", loadgen_returncode=loadgen.poll())
        time.sleep(cfg["recorder"]["after_load_scrapes"] * cfg["recorder"]["interval_s"])  # a scrape after the last completion
        if not recording:
            _scrape_once(run_dir, base, time.monotonic() - t0, cfg["recorder"]["scrape_timeout_s"])
    except KeyboardInterrupt:
        ev("aborted", reason="KeyboardInterrupt")
        aborted = True
    finally:
        grace = cfg["stop_grace_children_s"]
        _stop(loadgen, signal.SIGINT, grace)
        _stop(trig, signal.SIGTERM, grace)
        _stop(recorder, signal.SIGTERM, grace)
        ev("gpu_processes_end", processes=_gpu_processes())  # before the server stops: anything not ours shows here
        _stop(server, signal.SIGINT, srv["stop_grace_s"])
        ev("stopped")

    res = checks.write(run_dir)
    ev("checks", valid=res["valid"], failed=res["failed"])
    if aborted:
        raise KeyboardInterrupt  # stop the whole sweep, not just this run
    return run_dir


def _engine_config_lines(log: Path) -> list[str]:
    keys = ("non-default args", "engine config", "KV cache", "kv cache", "Maximum concurrency")
    return [l.strip() for l in log.read_text(errors="replace").splitlines() if any(k in l for k in keys)][:20]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config", type=Path)
    ap.add_argument("--allow-dirty", action="store_true", help="run from a dirty tree; the run is marked invalid")
    ap.add_argument("--runs-dir", type=Path, default=REPO / "runs")
    a = ap.parse_args()
    cfg = with_defaults(load_config(a.config))
    cfg["source_config"] = str(a.config)
    with open(REPO / cfg["lock_file"], "w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit(f"another harness run holds {cfg['lock_file']}: one run at a time")
        results = [run_one(c, a.runs_dir, a.allow_dirty) for c in expand(cfg)]
    for d in results:
        v = json.loads((d / "checks.json").read_text())
        print(f"{d.name}: {'VALID' if v['valid'] else 'INVALID ' + ','.join(v['failed'])}")


if __name__ == "__main__":
    main()
