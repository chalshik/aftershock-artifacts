"""Session cap (step D; workload change approved by the owner 2026-11-12): harness.loadgen.SessionCap and its use in
session_chain, the startup refusal with open-loop turns, an end-to-end run against fake_vllm, and analysis/cap.py."""
import asyncio
import io
import json
import time
from types import SimpleNamespace as R

import numpy as np
import pandas as pd
import pytest

import harness.loadgen as lg
from tests.test_e2e_fake import run_fake


# ---------------------------------------------------------------- SessionCap

def test_cap_admits_first_come_first_served_and_hands_slots_over():
    async def go():
        cap, order = lg.SessionCap(1), []
        await cap.acquire()

        async def waiter(i):
            await cap.acquire()
            order.append(i)

        tasks = [asyncio.create_task(waiter(i)) for i in range(4)]
        await asyncio.sleep(0)
        for _ in range(4):
            assert cap.used == 1
            cap.release()
            await asyncio.sleep(0)
        await asyncio.gather(*tasks)
        cap.release()
        return order, cap.used, len(cap.waiters)

    assert asyncio.run(go()) == ([0, 1, 2, 3], 0, 0)


def test_cancelled_waiter_leaves_the_queue_and_never_holds_a_slot():
    async def go():
        cap = lg.SessionCap(1)
        await cap.acquire()
        t = asyncio.create_task(cap.acquire())
        await asyncio.sleep(0)
        t.cancel()
        await asyncio.gather(t, return_exceptions=True)
        cap.release()
        return cap.used, len(cap.waiters)

    assert asyncio.run(go()) == (0, 0)


@pytest.mark.parametrize("bad", [0, -1, 1.5, "2", True])
def test_cap_must_be_a_positive_integer(bad):
    with pytest.raises(ValueError):
        lg.SessionCap(bad)


def test_session_cap_from_config():
    assert lg.session_cap({"workload": {"sessions": {"closed_loop": True}}}) is None
    assert lg.session_cap({"workload": {}}) is None
    assert lg.session_cap({"workload": {"sessions": {"closed_loop": True, "cap": 3}}}).n == 3
    with pytest.raises(ValueError):
        lg.session_cap({"workload": {"sessions": {"cap": 3}}})          # open-loop turns


# ---------------------------------------------------------------- session_chain with a cap

def _rows(sid, n=2, gap=0.02):
    return [R(request_id=10 * sid + i, session_id=sid, turn=i, t_planned=gap * i, prompt_len=1, output_len=1)
            for i in range(n)]


def _fake_send(log, dur=0.05):
    async def fake_send(session, url, model, row, prompt, gw, t0_, out, inflight, t_released=None, extra=None):
        rec = lg.new_rec(row, t_released, **(extra or {}))
        rec["t_sent"] = time.monotonic() - t0_
        log.append(("start", row.session_id, row.turn, rec["t_sent"]))
        await asyncio.sleep(dur)
        rec["t_end"], rec["status"] = time.monotonic() - t0_, "ok"
        log.append(("end", row.session_id, row.turn, rec["t_end"]))
        inflight.pop(rec["request_id"], None)
        out.write(json.dumps(rec) + "\n")
        return rec
    return fake_send


def test_chain_waits_for_a_slot_and_records_arrival_and_admission(monkeypatch):
    monkeypatch.setattr(lg, "prompt_tokens", lambda *a: [1])
    log = []
    monkeypatch.setattr(lg, "send", _fake_send(log))

    async def go():
        cap, inflight, out, t0 = lg.SessionCap(2), {}, io.StringIO(), time.monotonic()
        await asyncio.gather(*[lg.session_chain(_rows(s), None, None, "", "", None, t0, out, inflight, cap)
                               for s in range(3)])
        return cap, out.getvalue()

    cap, text = asyncio.run(go())
    assert cap.used == 0 and not cap.waiters
    live, peak = set(), 0
    for kind, sid, turn, _ in sorted(log, key=lambda e: (e[3], e[0] == "start")):
        if kind == "start" and turn == 0:
            live.add(sid)
        if kind == "end" and turn == 1:
            live.discard(sid)
        peak = max(peak, len(live))
    assert peak == 2
    recs = [json.loads(l) for l in text.splitlines()]
    t0s = {r["session_id"]: r for r in recs if r["turn"] == 0}
    assert all("t_admitted" in r and "t_arrived" in r for r in t0s.values())
    waited = [r for r in t0s.values() if r["t_admitted"] - r["t_arrived"] > 0.05]
    assert len(waited) == 1                                       # the third session waited for a slot
    w = waited[0]
    assert abs(w["t_released"] - w["t_admitted"]) < 1e-9 and w["t_sent"] >= w["t_admitted"] - 1e-3
    assert all("t_admitted" not in r for r in recs if r["turn"] > 0)


def test_slot_is_freed_when_a_chain_fails_or_is_cancelled(monkeypatch):
    monkeypatch.setattr(lg, "prompt_tokens", lambda *a: [1])

    async def boom(*a, **k):
        raise RuntimeError("x")

    async def go_fail():
        cap = lg.SessionCap(1)
        monkeypatch.setattr(lg, "send", boom)
        await lg.session_chain(_rows(0), None, None, "", "", None, time.monotonic(), io.StringIO(), {}, cap)
        return cap.used

    assert asyncio.run(go_fail()) == 0

    async def go_cancel():
        cap, inflight = lg.SessionCap(1), {}
        monkeypatch.setattr(lg, "send", _fake_send([], dur=10))
        t0 = time.monotonic()
        a = asyncio.create_task(lg.session_chain(_rows(0), None, None, "", "", None, t0, io.StringIO(), inflight, cap))
        b = asyncio.create_task(lg.session_chain(_rows(1), None, None, "", "", None, t0, io.StringIO(), inflight, cap))
        await asyncio.sleep(0.1)
        a.cancel(), b.cancel()                                   # the drain deadline, b still waiting at the cap
        await asyncio.gather(a, b, return_exceptions=True)
        return cap.used, len(cap.waiters), inflight

    used, waiting, inflight = asyncio.run(go_cancel())
    assert used == 0 and waiting == 0
    assert inflight[10]["t_arrived"] is not None and inflight[10]["t_sent"] is None   # never admitted, kept as a miss


# ---------------------------------------------------------------- end to end, and the analysis side

WL = {"rate": 4.0, "duration_s": 20, "warmup_s": 5, "output_tokens": 8,
      "sessions": {"turns": 3, "closed_loop": True, "turn_gap_s": {"dist": "exponential", "mean": 2.0}}}


def test_capped_run_is_valid_and_never_exceeds_the_cap(tmp_path):
    from analysis import cap as capa
    from analysis.load import load_run
    run_dir = run_fake(tmp_path, workload={**WL, "sessions": {**WL["sessions"], "cap": 2}},
                       trigger={"kind": "burst", "at_s": 8, "duration_s": 2, "rate": 3.0, "prompt_tokens": 64})
    chk = json.loads((run_dir / "checks.json").read_text())
    assert chk["valid"], chk["failed"]
    run = load_run(run_dir)
    assert capa.max_sessions_in_service(run) <= 2
    q = pd.read_json(run_dir / "requests.jsonl", lines=True)
    t0 = q[q.turn == 0]
    sched = pd.read_parquet(run_dir / "schedule.parquet")
    burst_ids = set(sched.request_id[sched.burst])
    sess0 = t0[~t0.request_id.isin(burst_ids)]
    assert sess0.t_arrived.notna().all()
    burst = q[q.request_id.isin(burst_ids)]
    assert len(burst) and ((burst.t_sent - burst.t_planned) < 0.05).all()           # the burst passes the cap
    w = capa.cap_wait(run)
    assert w["n_sessions"] == len(sess0) and w["max_s"] >= 0


def test_cap_with_open_loop_turns_is_refused_before_the_server_starts(tmp_path):
    import subprocess
    with pytest.raises(subprocess.CalledProcessError):
        run_fake(tmp_path, workload={**WL, "sessions": {**WL["sessions"], "closed_loop": False, "cap": 2}})
    assert not any((tmp_path / "runs").glob("*")) if (tmp_path / "runs").exists() else True


def _run(reqs, burst=()):
    """A run-like dict; burst requests carry the trigger's prompt length (analysis.margin.is_burst_request)."""
    reqs = reqs.assign(prompt_tokens_planned=np.where(reqs.request_id.isin(burst), 64, 2176))
    return {"requests": reqs, "cfg": {"trigger": {"kind": "burst", "prompt_tokens": 64}}}


def test_max_sessions_in_service_is_an_exact_sweep():
    from analysis import cap as capa
    q = pd.DataFrame({"request_id": [1, 2, 3, 4, 5, 6, 7],
                      "session_id": [0, 0, 1, 1, 2, 3, 9],
                      "turn": [0, 1, 0, 1, 0, 0, 0],
                      "t_sent": [0.0, 2.0, 1.0, 3.0, 2.5, 3.0, 1.5],
                      "t_end": [1.0, 3.0, 2.0, 4.0, None, 3.5, 1.6]})
    # session 0: [0, 3); 1: [1, 4); 2: [2.5, inf) unfinished; 3: [3, 3.5); 9 is a burst request (excluded)
    assert capa.max_sessions_in_service(_run(q, burst={7})) == 3   # 1, 2 and 3 at t = 3 (0 has ended at 3)
    assert capa.max_sessions_in_service(_run(q)) == 3              # as a session, 9 at [1.5, 1.6) meets only 0 and 1


def test_cap_wait_summary():
    from analysis import cap as capa
    q = pd.DataFrame({"request_id": [1, 2, 3], "session_id": [0, 1, 1], "turn": [0, 0, 1],
                      "t_arrived": [0.0, 1.0, None], "t_admitted": [0.0, 4.0, None],
                      "t_sent": [0.0, 4.0, 6.0], "t_end": [1.0, 5.0, 7.0]})
    w = capa.cap_wait(_run(q))
    assert w["n_sessions"] == 2 and w["n_waited"] == 1 and w["max_s"] == 3.0 and w["mean_s"] == 1.5
