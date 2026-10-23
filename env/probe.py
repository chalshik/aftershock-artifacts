"""Answer Stage 1 open questions on the pinned vLLM, with evidence. Run on the VM after setup_vm.sh.

    uv run python env/probe.py [--model Qwen/Qwen3-1.7B]

Writes docs/probe/<date>_<model>/: probe.json, serve_help.txt, server.log, metrics.txt.
Copy the answers into docs/open-questions.md and fix flag names in configs/base.yaml if needed.
"""
import argparse
import json
import os
import re
import signal
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from harness import env_snapshot  # noqa: E402

PORT = 8011
FLAGS = ["--enable-prefix-caching", "--no-enable-prefix-caching", "--kv-cache-metrics", "--max-num-seqs",
         "--enable-prompt-tokens-details", "--kv-transfer-config", "--kv-offloading-size", "--max-model-len",
         "--gpu-memory-utilization"]
METRICS = ["vllm:prefix_cache_hits", "vllm:prefix_cache_queries", "vllm:prompt_tokens", "vllm:prompt_tokens_cached",
           "vllm:num_requests_running", "vllm:num_requests_waiting", "vllm:kv_cache_usage_perc",
           "vllm:num_preemptions", "vllm:kv_block_idle_before_evict_seconds", "vllm:admission_rejections",
           "vllm:request_success"]


def post(path, body):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-1.7B")
    a = ap.parse_args()
    out = REPO / "docs" / "probe" / f"{datetime.now():%Y%m%d}_{a.model.split('/')[-1]}"
    out.mkdir(parents=True, exist_ok=True)
    res = {"model": a.model, "env": env_snapshot.snapshot()}

    # Q4: exact flag names at the pinned version.
    help_txt = subprocess.run(["vllm", "serve", "--help=all"], capture_output=True, text=True).stdout
    (out / "serve_help.txt").write_text(help_txt)
    res["flags_present"] = {f: bool(re.search(rf"(^|\s){re.escape(f)}[\s,=]", help_txt)) for f in FLAGS}

    # Start once with base flags that exist (Q7: KV size from the startup log).
    args = [f for f in ["--enable-prefix-caching", "--kv-cache-metrics", "--enable-prompt-tokens-details"]
            if res["flags_present"].get(f)]
    log = open(out / "server.log", "w")
    srv = subprocess.Popen(["vllm", "serve", a.model, "--port", str(PORT), *args], stdout=log,
                           stderr=subprocess.STDOUT, start_new_session=True)
    try:
        for _ in range(900):
            try:
                if urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=2).status == 200:
                    break
            except Exception:
                pass
            if srv.poll() is not None:
                raise SystemExit(f"vllm exited; see {out / 'server.log'}")
            time.sleep(1)
        log_txt = (out / "server.log").read_text(errors="replace")
        res["startup_log_kv_lines"] = [l.strip() for l in log_txt.splitlines()
                                       if re.search(r"KV cache|kv cache|Maximum concurrency|non-default", l)]

        # Q2 + Q3: token-ID prompts, and cached tokens reported per request (same prompt twice).
        prompt = list(range(1000, 1000 + 300))
        body = {"model": a.model, "prompt": prompt, "max_tokens": 8, "min_tokens": 8, "ignore_eos": True}
        st1, r1 = post("/v1/completions", body)
        st2, r2 = post("/v1/completions", body)
        res["token_id_prompt"] = {"status": st1, "response": r1[:500]}
        try:
            usage = json.loads(r2)["usage"]
            res["cached_tokens_per_request"] = {"second_call_usage": usage,
                                                "reported": (usage.get("prompt_tokens_details") or {}).get(
                                                    "cached_tokens") is not None}
        except Exception as e:
            res["cached_tokens_per_request"] = {"error": str(e), "status": st2, "raw": r2[:500]}

        # Q1 + metric names.
        metrics_txt = urllib.request.urlopen(f"http://127.0.0.1:{PORT}/metrics").read().decode()
        (out / "metrics.txt").write_text(metrics_txt)
        names = sorted({l.split("{")[0].split(" ")[0] for l in metrics_txt.splitlines()
                        if l.startswith("vllm:")})
        res["metric_names"] = names
        res["metrics_present"] = {m: any(n.startswith(m) for n in names) for m in METRICS}
    finally:
        if srv.poll() is None:
            os.killpg(srv.pid, signal.SIGINT)
            try:
                srv.wait(30)
            except subprocess.TimeoutExpired:
                os.killpg(srv.pid, signal.SIGKILL)

    # Q6: CPU cores for pinning.
    res["nproc"] = os.cpu_count()
    (out / "probe.json").write_text(json.dumps(res, indent=2, default=str))
    print(json.dumps({k: res[k] for k in ["flags_present", "metrics_present", "startup_log_kv_lines", "nproc"]},
                     indent=2))
    print(f"\nEvidence in {out}. Update docs/open-questions.md and configs/base.yaml, then commit.")


if __name__ == "__main__":
    main()
