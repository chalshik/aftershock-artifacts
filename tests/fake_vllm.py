"""Tiny stand-in for `vllm serve`, for testing the harness on a machine without a GPU.

Speaks the subset the harness uses: GET /health, GET /metrics, POST /v1/completions (streaming,
token-ID prompts). Simulates a block prefix cache so hit-rate metrics move. Not a performance model.
"""
import argparse
import asyncio
import json
import time

from aiohttp import web

BLOCK = 16
PREFILL_S_PER_TOKEN = 2e-6
DECODE_S_PER_TOKEN = 1e-3


class State:
    def __init__(self):
        self.cache: set[int] = set()
        self.c = dict(success=0, hits=0, queries=0, prompt=0, gen=0)
        self.running = 0


def cached_prefix(state: State, prompt: list[int]) -> int:
    h, hit = 0, 0
    for i in range(0, len(prompt) - len(prompt) % BLOCK, BLOCK):
        h = hash((h, tuple(prompt[i:i + BLOCK])))
        if hit == i and h in state.cache:
            hit = i + BLOCK
        state.cache.add(h)
    return hit


async def completions(req: web.Request):
    st: State = req.app["state"]
    body = await req.json()
    prompt, n_out = body["prompt"], body["max_tokens"]
    hit = cached_prefix(st, prompt)
    st.c["queries"] += len(prompt); st.c["hits"] += hit; st.c["prompt"] += len(prompt)
    st.running += 1
    resp = web.StreamResponse(headers={"Content-Type": "text/event-stream"})
    await resp.prepare(req)
    try:
        await asyncio.sleep((len(prompt) - hit) * PREFILL_S_PER_TOKEN)
        for _ in range(n_out):
            chunk = {"choices": [{"index": 0, "text": "x", "finish_reason": None}], "usage": None}
            await resp.write(f"data: {json.dumps(chunk)}\n\n".encode())
            await asyncio.sleep(DECODE_S_PER_TOKEN)
        usage = {"prompt_tokens": len(prompt), "completion_tokens": n_out, "total_tokens": len(prompt) + n_out,
                 "prompt_tokens_details": {"cached_tokens": hit}}
        await resp.write(f"data: {json.dumps({'choices': [], 'usage': usage})}\n\n".encode())
        await resp.write(b"data: [DONE]\n\n")
        st.c["success"] += 1; st.c["gen"] += n_out
    finally:
        st.running -= 1
    return resp


async def metrics(req: web.Request):
    st: State = req.app["state"]
    lab = 'model_name="fake"'
    lines = [
        "# TYPE vllm:num_requests_running gauge", f"vllm:num_requests_running{{{lab}}} {st.running}",
        "# TYPE vllm:num_requests_waiting gauge", f"vllm:num_requests_waiting{{{lab}}} 0",
        "# TYPE vllm:kv_cache_usage_perc gauge", f"vllm:kv_cache_usage_perc{{{lab}}} {min(1.0, st.running / 64)}",
        "# TYPE vllm:request_success counter",
        f'vllm:request_success_total{{finished_reason="length",{lab}}} {st.c["success"]}',
        "# TYPE vllm:prefix_cache_queries counter", f"vllm:prefix_cache_queries_total{{{lab}}} {st.c['queries']}",
        "# TYPE vllm:prefix_cache_hits counter", f"vllm:prefix_cache_hits_total{{{lab}}} {st.c['hits']}",
        "# TYPE vllm:prompt_tokens counter", f"vllm:prompt_tokens_total{{{lab}}} {st.c['prompt']}",
        "# TYPE vllm:generation_tokens counter", f"vllm:generation_tokens_total{{{lab}}} {st.c['gen']}",
        "# TYPE vllm:num_preemptions counter", f"vllm:num_preemptions_total{{{lab}}} 0",
    ]
    return web.Response(text="\n".join(lines) + "\n")


async def health(_):
    return web.Response(text="ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    a, _ = ap.parse_known_args()  # ignore vLLM flags from the config
    app = web.Application(client_max_size=64 * 2**20)
    app["state"] = State()
    app.add_routes([web.get("/health", health), web.get("/metrics", metrics),
                    web.post("/v1/completions", completions)])
    print(f"fake vllm on {a.host}:{a.port} started at {time.time()}", flush=True)
    web.run_app(app, host=a.host, port=a.port, print=None)


if __name__ == "__main__":
    main()
