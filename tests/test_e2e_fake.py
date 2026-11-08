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


def test_burst_run_sends_the_extra_requests(tmp_path):
    burst = {"kind": "burst", "at_s": 8, "duration_s": 4, "rate": 5.0, "prompt_tokens": 64}
    run_dir = run_fake(tmp_path, trigger=burst)
    res = json.loads((run_dir / "checks.json").read_text())
    assert res["valid"], res
    sched = pd.read_parquet(run_dir / "schedule.parquet")
    reqs = pd.read_json(run_dir / "requests.jsonl", lines=True).merge(sched[["request_id", "burst"]], on="request_id")
    b = reqs[reqs.burst]
    assert len(b) == sched.burst.sum() > 0 and (b.status == "ok").all() and (b.cached_tokens == 0).all()
    assert not (run_dir / "trigger.jsonl").exists()


def test_no_trigger_in_dev_mode_writes_no_trigger_file(tmp_path):
    run_dir = run_fake(tmp_path, server=dev_server())
    assert not (run_dir / "trigger.jsonl").exists()
    res = json.loads((run_dir / "checks.json").read_text())
    assert res["valid"] and "trigger" not in [c["name"] for c in res["checks"]]


def test_l1_setup_runs_end_to_end_with_its_prompt_lengths(tmp_path):
    """REG-7's setup L1 (configs/l1_base.yaml) against the fake server: the 2048-token system prompt reaches the
    schedule and the server, and the run records the item-42 capacity rule."""
    run_dir = run_fake(tmp_path, extends=str(REPO / "configs" / "sweep_l1_pc_on.yaml"), sweep=None,
                       # 8 turns at 5 s gaps need ~40 s to ramp up, so the warm-up covers it (configs/base.yaml)
                       workload={"rate": 2.0, "duration_s": 55, "warmup_s": 40, "output_tokens": 8},
                       checks={"require_clean_git": False, "expected_kv_tokens": None})
    sched = pd.read_parquet(run_dir / "schedule.parquet")
    assert set(sched[sched.turn == 0].prompt_len) == {2048 + 128}
    assert ((sched.prompt_len - 2176) % 256 == 0).all()
    cfg = yaml.safe_load((run_dir / "config.yaml").read_text())
    assert cfg["capacity"]["against"] == "planned_rate"
    assert json.loads((run_dir / "checks.json").read_text())["valid"]


def test_force_close_opens_a_connection_per_request_and_is_off_when_absent(tmp_path):
    """decisions.md 2026-11-09: loadgen_force_close stops connection reuse; old configs (no key) keep the pool."""
    import asyncio
    from harness.loadgen import make_connector

    async def flags():
        out = []
        for cfg in ({}, {"loadgen_force_close": False}, {"loadgen_force_close": True}):
            c = make_connector(cfg)
            out.append((c.force_close, c.limit))
            await c.close()
        return out

    assert asyncio.run(flags()) == [(False, 0), (False, 0), (True, 0)]
    run_dir = run_fake(tmp_path, loadgen_force_close=True)
    assert json.loads((run_dir / "checks.json").read_text())["valid"]
    assert yaml.safe_load((run_dir / "config.yaml").read_text())["loadgen_force_close"] is True
    reqs = pd.read_json(run_dir / "requests.jsonl", lines=True)
    ok = reqs[reqs.status == "ok"]  # every request opened its own connection, after it was sent and before its first token
    assert ok.t_connected.notna().all() and (ok.t_connected >= ok.t_sent).all() and (ok.t_connected <= ok.t_first_token).all()


def test_closed_loop_turns_wait_for_the_previous_turn_and_open_loop_is_unchanged(tmp_path):
    """REG-11 draft: with workload.sessions.closed_loop a later turn is released at the previous turn's end plus the
    planned gap; t_planned stays the schedule's; session starts and the checks still work. Absent = open loop."""
    run_dir = run_fake(tmp_path, workload={"rate": 4.0, "duration_s": 20, "warmup_s": 5, "output_tokens": 8,
                                           "sessions": {"turns": 3, "closed_loop": True,
                                                        "turn_gap_s": {"dist": "exponential", "mean": 2.0}}})
    chk = json.loads((run_dir / "checks.json").read_text())
    assert chk["valid"], chk["failed"]
    by = {c["name"]: c for c in chk["checks"]}
    assert by["arrival_rate"]["detail"]["closed_loop"] is True
    assert by["release_chain"]["passed"] is True and by["release_chain"]["detail"]["unexplained"] == 0
    sched = pd.read_parquet(run_dir / "schedule.parquet").set_index("request_id")
    q = pd.read_json(run_dir / "requests.jsonl", lines=True).sort_values(["session_id", "turn"])
    assert (q.set_index("request_id").t_planned - sched.t_planned).abs().max() < 1e-9  # the schedule's own times
    g = q.groupby("session_id")
    q["prev_end"], q["prev_planned"] = g.t_end.shift(), g.t_planned.shift()
    later = q[(q.turn > 0) & q.status.eq("ok")]
    assert len(later) > 0
    assert ((later.t_released - (later.prev_end + later.t_planned - later.prev_planned)).abs() < 1e-6).all()
    assert (later.t_sent >= later.t_released - 1e-3).all() and (later.t_first_token > later.prev_end).all()
    first = q[q.turn == 0]
    assert ((first.t_released - first.t_planned).abs() < 1e-9).all()
    from analysis.load import load_run
    r = load_run(run_dir)["requests"].set_index("request_id")
    ok = r[r.status == "ok"]
    assert ((ok.ttft - (ok.t_first_token - ok.t_released)).abs() < 1e-9).all()  # latency from release


def test_open_loop_runs_record_no_release_time(tmp_path):
    run_dir = run_fake(tmp_path)
    assert "release_chain" not in {c["name"] for c in json.loads((run_dir / "checks.json").read_text())["checks"]}
    q = pd.read_json(run_dir / "requests.jsonl", lines=True)
    assert q.t_released.isna().all()
    from analysis.load import load_run
    r = load_run(run_dir)["requests"]
    ok = r[r.status == "ok"]
    assert ((ok.ttft - (ok.t_first_token - ok.t_planned)).abs() < 1e-9).all()


def test_session_chain_after_an_error_and_at_the_deadline(monkeypatch):
    """REG-11 review T1-T2: after a failed turn the next one is released at the failure time plus the planned gap;
    at cancellation unsent turns stay unfinished placeholders; a chain that raises fails its unsent turns."""
    import asyncio
    import io
    import time
    from types import SimpleNamespace as R
    import harness.loadgen as lg
    rows = [R(request_id=i, session_id=0, turn=i, t_planned=0.05 * i, prompt_len=1, output_len=1) for i in range(4)]
    monkeypatch.setattr(lg, "prompt_tokens", lambda *a: [1])
    t0 = time.monotonic()

    async def fake_send(session, url, model, row, prompt, gw, t0_, out, inflight, t_released=None):
        rec = lg.new_rec(row, t_released)
        rec["t_sent"] = time.monotonic() - t0_
        inflight[rec["request_id"]] = rec
        if row.turn == 1:  # an http_error: no t_end
            rec["status"] = "http_error"
        elif row.turn == 2:
            await asyncio.sleep(10)  # still running at the deadline
        else:
            rec["t_end"], rec["status"] = rec["t_sent"], "ok"
        inflight.pop(rec["request_id"])
        return rec

    monkeypatch.setattr(lg, "send", fake_send)

    async def go():
        inflight, out = {}, io.StringIO()
        task = asyncio.create_task(lg.session_chain(rows, None, None, "", "", None, t0, out, inflight))
        await asyncio.sleep(0.4)
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        return inflight

    inflight = asyncio.run(go())
    # turn 2 was running at the cancel (main() writes it as unfinished); turn 3 was never released: a placeholder
    assert set(inflight) == {2, 3} and inflight[2]["t_sent"] is not None
    assert inflight[3]["t_sent"] is None and inflight[3]["status"] == "unfinished"

    async def boom(*a, **k):
        raise RuntimeError("x")

    monkeypatch.setattr(lg, "send", boom)

    async def go2():
        inflight, out = {}, io.StringIO()
        await lg.session_chain(rows, None, None, "", "", None, time.monotonic(), out, inflight)
        return inflight, out.getvalue()

    inflight, text = asyncio.run(go2())
    assert not inflight and text.count('"client_error"') == 4


def test_session_chain_releases_after_a_failure_at_failure_time_plus_gap(monkeypatch):
    import asyncio
    import io
    import time
    from types import SimpleNamespace as R
    import harness.loadgen as lg
    rows = [R(request_id=i, session_id=0, turn=i, t_planned=0.1 * i, prompt_len=1, output_len=1) for i in range(2)]
    monkeypatch.setattr(lg, "prompt_tokens", lambda *a: [1])
    seen = []

    async def fake_send(session, url, model, row, prompt, gw, t0_, out, inflight, t_released=None):
        rec = lg.new_rec(row, t_released)
        rec["t_sent"] = time.monotonic() - t0_
        rec["status"] = "http_error"
        seen.append(rec)
        return rec

    monkeypatch.setattr(lg, "send", fake_send)
    t0 = time.monotonic()
    asyncio.run(lg.session_chain(rows, None, None, "", "", None, t0, io.StringIO(), {}))
    assert seen[1]["t_released"] >= seen[0]["t_sent"] + 0.1 - 1e-3
