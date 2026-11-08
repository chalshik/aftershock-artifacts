"""Open-loop load generator: sends every request at its planned time, never waits for earlier ones.

Usage (started by run.py): python -m harness.loadgen <run_dir> <t0_monotonic>
Writes one line per request to requests.jsonl. No timeouts, no retries.
"""
import asyncio
import json
import sys
import time
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


async def send(session, url, model, row, prompt, gateway, t0, out, inflight):
    rec = dict(request_id=int(row.request_id), session_id=int(row.session_id), turn=int(row.turn),
               t_planned=float(row.t_planned), prompt_tokens_planned=int(row.prompt_len),
               output_tokens_planned=int(row.output_len), t_sent=None, t_connected=None, t_first_token=None, t_end=None,
               prompt_tokens=None, output_tokens=None, cached_tokens=None, status="unfinished", error=None)
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
                    return
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
    deadline = t0 + (float(sched.t_planned.max()) if len(sched) else 0.0) + cfg["drain_s"]
    inflight, tasks = {}, []

    connector = make_connector(cfg)
    timeout = aiohttp.ClientTimeout(total=None, sock_read=None, sock_connect=None)
    with open(run_dir / "requests.jsonl", "a") as out:
        async with aiohttp.ClientSession(connector=connector, timeout=timeout, trace_configs=[make_trace()]) as session:
            for row in sched.itertuples(index=False):
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


if __name__ == "__main__":
    asyncio.run(main(Path(sys.argv[1]), float(sys.argv[2])))
