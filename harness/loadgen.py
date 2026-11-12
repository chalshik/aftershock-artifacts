"""Load generator. Open loop (default): sends every request at its planned time, never waits for earlier ones.
Closed-loop turns (`workload.sessions.closed_loop: true`, REG-11 draft): session starts and burst requests stay open
loop; a session's later turn is released only after its previous turn has ended, plus the schedule's own gap between
the two turns. `t_planned` stays the schedule's time; `t_released` records when the turn became due (None in open loop).
Session cap (`workload.sessions.cap`, closed loop only; step D, owner 2026-11-12): at most `cap` sessions are in service
at once (from turn 0 sent to the last turn's end). A session that arrives at a full cap waits, first come first served;
its turn 0 records `t_arrived` and `t_admitted`, and its `t_released` is the admission time. Burst requests pass the cap.

Usage (started by run.py): python -m harness.loadgen <run_dir> <t0_monotonic>
Writes one line per request to requests.jsonl. No timeouts, no retries.
"""
import asyncio
import json
import sys
import time
from collections import deque
from pathlib import Path

import aiohttp
import pandas as pd
import yaml

from harness.workload import prompt_tokens


class Gateway:
    """Optional concurrency cap in front of the server. Off in Stage 1 (config gateway.enabled)."""

    def __init__(self, cfg: dict):
        self.sem = asyncio.Semaphore(cfg["max_concurrency"]) if cfg["enabled"] else None

    async def __aenter__(self):
        if self.sem:
            await self.sem.acquire()

    async def __aexit__(self, *exc):
        if self.sem:
            self.sem.release()


class SessionCap:
    """At most `n` sessions in service at once, held at the load generator (the gateway stays off). Waiters are served
    strictly first come first served from an explicit queue; a freed slot is handed straight to the oldest waiter."""

    def __init__(self, n: int):
        if not isinstance(n, int) or isinstance(n, bool) or n < 1:
            raise ValueError(f"workload.sessions.cap must be a positive integer, got {n!r}")
        self.n, self.used, self.waiters = n, 0, deque()

    async def acquire(self):
        if self.used < self.n and not self.waiters:
            self.used += 1
            return
        fut = asyncio.get_running_loop().create_future()
        self.waiters.append(fut)
        try:
            await fut  # resolved by release(): the slot passes over without `used` going down
        except asyncio.CancelledError:
            if fut.done() and not fut.cancelled():
                self.release()  # handed a slot in the same tick as the cancel: give it on
            elif fut in self.waiters:
                self.waiters.remove(fut)
            raise

    def release(self):
        while self.waiters:
            fut = self.waiters.popleft()
            if not fut.done():
                fut.set_result(None)
                return
        self.used -= 1


def session_cap(cfg: dict) -> SessionCap | None:
    """The configured cap, or None. Read with .get (added after defaults.yaml was used; absent = no cap). Refused
    with open-loop turns: an open-loop turn has no session in service to hold a slot."""
    sessions = (cfg["workload"].get("sessions") or {})
    n = sessions.get("cap")
    if n is None:
        return None
    if not sessions.get("closed_loop"):
        raise ValueError("workload.sessions.cap needs closed-loop turns (workload.sessions.closed_loop: true)")
    return SessionCap(n)


def new_rec(row, t_released=None, **extra) -> dict:
    return dict(request_id=int(row.request_id), session_id=int(row.session_id), turn=int(row.turn),
               t_planned=float(row.t_planned), t_released=t_released, prompt_tokens_planned=int(row.prompt_len),
               output_tokens_planned=int(row.output_len), t_sent=None, t_connected=None, t_first_token=None, t_end=None,
               prompt_tokens=None, output_tokens=None, cached_tokens=None, status="unfinished", error=None, **extra)


async def send(session, url, model, row, prompt, gateway, t0, out, inflight, t_released=None, extra=None) -> dict:
    rec = new_rec(row, t_released, **(extra or {}))
    inflight[rec["request_id"]] = rec
    body = {"model": model, "prompt": prompt, "stream": True,
            "max_tokens": rec["output_tokens_planned"], "min_tokens": rec["output_tokens_planned"],
            "ignore_eos": True, "temperature": 0.0,
            "stream_options": {"include_usage": True}}
    try:
        async with gateway:
            rec["t_sent"] = time.monotonic() - t0
            # t_connected: when a new connection for this request was open (None if a pooled one was reused), so the
            # connect time inside TTFT is measured (decisions.md 2026-11-09, amendment review).
            async with session.post(url, json=body, trace_request_ctx={"rec": rec, "t0": t0}) as resp:
                if resp.status != 200:
                    rec["status"], rec["error"] = "http_error", f"{resp.status}: {(await resp.text())[:300]}"
                    return rec  # session_chain needs the record (REG-11 review, T1)
                async for raw in resp.content:
                    line = raw.decode().strip()
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    chunk = json.loads(data)
                    # Any choice chunk counts: a token's text can decode to "" (partial UTF-8).
                    if rec["t_first_token"] is None and chunk.get("choices"):
                        rec["t_first_token"] = time.monotonic() - t0
                    if usage := chunk.get("usage"):
                        rec["prompt_tokens"] = usage.get("prompt_tokens")
                        rec["output_tokens"] = usage.get("completion_tokens")
                        rec["cached_tokens"] = (usage.get("prompt_tokens_details") or {}).get("cached_tokens")
            rec["t_end"] = time.monotonic() - t0
            rec["status"] = "ok"
    except asyncio.CancelledError:
        raise  # stays "unfinished"; written by main()
    except Exception as e:  # recorded, never retried
        rec["status"], rec["error"] = "client_error", f"{type(e).__name__}: {e}"[:300]
    finally:
        if rec["status"] != "unfinished":
            out.write(json.dumps(rec) + "\n")
            out.flush()
            inflight.pop(rec["request_id"], None)
    return rec


async def session_chain(rows, prompts, session, url, model, gateway, t0, out, inflight, cap=None):
    """Closed-loop turns of one session. Turn 0 is released at its planned time; turn k at the end of turn k-1 (or the
    time it failed) plus the planned gap t_planned[k] - t_planned[k-1]. Turns not yet sent stay in `inflight` as
    unfinished placeholders, so a turn never released before the drain deadline is still recorded (as a miss).
    With a session cap the session first waits for a slot (it is called at turn 0's planned time); turn 0 is released
    at admission, and the slot is held until the chain ends (last turn ended, failed, or cancelled at the deadline)."""
    for row in rows:
        inflight[int(row.request_id)] = new_rec(row)
    held, extra = False, None
    try:
        release, prev = float(rows[0].t_planned), None
        if cap is not None:
            arrived = time.monotonic() - t0
            inflight[int(rows[0].request_id)]["t_arrived"] = arrived  # kept if the deadline comes first
            await cap.acquire()
            held = True
            admitted = time.monotonic() - t0
            release, extra = max(release, admitted), {"t_arrived": arrived, "t_admitted": admitted}
        for row in rows:
            prompt = prompt_tokens(prompts, int(row.session_id), int(row.prompt_len))
            if prev is not None:
                done = prev["t_end"] if prev["t_end"] is not None else time.monotonic() - t0
                release = done + float(row.t_planned) - prev["t_planned"]
            delay = t0 + release - time.monotonic()
            if delay > 0:
                await asyncio.sleep(delay)
            kw = {"extra": extra} if extra is not None and prev is None else {}  # turn 0 under a cap only
            prev = await send(session, url, model, row, prompt, gateway, t0, out, inflight, t_released=release, **kw)
    except asyncio.CancelledError:
        raise  # the drain deadline: unsent turns stay unfinished placeholders
    except Exception as e:  # a chain that dies must fail no_errors, not look like a slow server (REG-11 review, T2)
        for row in rows:
            rec = inflight.get(int(row.request_id))
            if rec is not None and rec["t_sent"] is None:
                rec["status"], rec["error"] = "client_error", f"session_chain: {type(e).__name__}: {e}"[:300]
                out.write(json.dumps(rec) + "\n")
                out.flush()  # one line at a time, so a reader never sees a buffer cut mid-line (A14)
                inflight.pop(int(row.request_id), None)
    finally:
        if held:
            cap.release()


async def _connected(session, ctx, params):
    req = ctx.trace_request_ctx or {}
    if "rec" in req:
        req["rec"]["t_connected"] = time.monotonic() - req["t0"]


def make_trace() -> aiohttp.TraceConfig:
    tc = aiohttp.TraceConfig()
    tc.on_connection_create_end.append(_connected)
    return tc


def make_connector(cfg: dict) -> aiohttp.TCPConnector:
    """Unlimited pool: the client must not cap concurrency. With `loadgen_force_close` (added after defaults.yaml, so
    read with .get; absent = the earlier behaviour) every request opens its own connection and none is reused. Reusing
    an idle one raced vLLM's 5 s keep-alive close against aiohttp's 15 s pool timeout, and failed 4 requests in 25,450
    at send time (decisions.md 2026-11-09). No retry either way (rule 2)."""
    return aiohttp.TCPConnector(limit=0, force_close=bool(cfg.get("loadgen_force_close")))


async def main(run_dir: Path, t0: float):
    cfg = yaml.safe_load((run_dir / "config.yaml").read_text())
    sched = pd.read_parquet(run_dir / "schedule.parquet")
    prompts = pd.read_parquet(run_dir / "prompts.parquet")
    srv = cfg["server"]
    url = f"http://{srv['host']}:{srv['port']}/v1/completions"
    gateway = Gateway(cfg["gateway"])
    cap = session_cap(cfg)
    deadline = t0 + (float(sched.t_planned.max()) if len(sched) else 0.0) + cfg["drain_s"]
    inflight, tasks = {}, []
    closed = bool((cfg["workload"].get("sessions") or {}).get("closed_loop"))  # absent = open loop (older configs)
    chains = {}
    if closed:
        for row in sched[~sched.burst].sort_values(["session_id", "turn"]).itertuples(index=False):
            chains.setdefault(int(row.session_id), []).append(row)

    connector = make_connector(cfg)
    timeout = aiohttp.ClientTimeout(total=None, sock_read=None, sock_connect=None)
    with open(run_dir / "requests.jsonl", "a") as out:
        async with aiohttp.ClientSession(connector=connector, timeout=timeout, trace_configs=[make_trace()]) as session:
            for row in sched.itertuples(index=False):
                if closed and not row.burst:
                    if int(row.turn) == 0:  # the session starts open loop; its chain releases the later turns
                        delay = t0 + row.t_planned - time.monotonic()
                        if delay > 0:
                            await asyncio.sleep(delay)
                        tasks.append(asyncio.create_task(session_chain(
                            chains[int(row.session_id)], prompts, session, url, cfg["model"], gateway, t0, out,
                            inflight, cap)))
                    continue
                prompt = prompt_tokens(prompts, int(row.session_id), int(row.prompt_len))  # built before the wait
                delay = t0 + row.t_planned - time.monotonic()
                if delay > 0:
                    await asyncio.sleep(delay)
                tasks.append(asyncio.create_task(
                    send(session, url, cfg["model"], row, prompt, gateway, t0, out, inflight)))
            pending = [t for t in tasks if not t.done()]
            if pending:
                await asyncio.wait(pending, timeout=max(0.0, deadline - time.monotonic()))
            for t in tasks:
                t.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
        for rec in inflight.values():  # still running at the end: counted as misses
            out.write(json.dumps(rec) + "\n")
            out.flush()  # one line at a time (A14)


if __name__ == "__main__":
    asyncio.run(main(Path(sys.argv[1]), float(sys.argv[2])))
