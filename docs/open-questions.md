# Stage 1 open questions

Answer each one with evidence only (`docs/probe/...`, the vLLM source at the pinned version, or a run id).

| # | Question | Answer | Evidence |
|---|---|---|---|
| 1 | Is vLLM's admission queue limit on by default (`vllm:admission_rejections`)? | **No.** `max_num_queued_reqs` and `max_num_queued_tokens` default to None. The metric exists and stays 0 | `vllm/config/scheduler.py`; `docs/probe/20261023_Qwen3-1.7B/probe.json`, `metrics.txt` |
| 2 | Does `/v1/completions` accept token IDs as the prompt? | **Yes.** A 300-token-ID prompt returned HTTP 200 | `docs/probe/20261023_Qwen3-1.7B/probe.json` `token_id_prompt` |
| 3 | Does vLLM report cached tokens per request (`usage.prompt_tokens_details.cached_tokens`)? | **Yes**, with `--enable-prompt-tokens-details`. The same 300-token prompt sent twice reported `cached_tokens: 288` (18 full 16-token blocks) | `docs/probe/20261023_Qwen3-1.7B/probe.json` `cached_tokens_per_request` |
| 4 | Exact flag names for prefix caching, KV metrics and the sequence cap | `--enable-prefix-caching` / `--no-enable-prefix-caching`, `--kv-cache-metrics`, `--enable-prompt-tokens-details`, `--max-num-seqs`. All present | `docs/probe/20261023_Qwen3-1.7B/probe.json` `flags_present`, `serve_help.txt` |
| 5 | Does the recorder slow the server? (μ_warm with and without it) | No effect beyond the registered limits at λ = 3, 4, 5 with prefix caching on; μ_warm stays 4. Not tested with caching off | `20261031-013840_recorder_off_r3`, `20261031-015442_recorder_off_r4`, `20261031-021045_recorder_off_r5`; decisions.md |
| 6 | Enough CPU cores to pin loadgen and the recorder away from vLLM? | 8 cores, 1 NUMA node: vLLM on 0–5, loadgen on 6, recorder on 7. Each run's client-lag check confirms whether loadgen keeps up | `nproc`; decisions.md (VM facts) |
| 7 | Real KV capacity per model, from the startup log | **1.7B:** 165,792 tokens (17.71 GiB, 112 KiB/token). **4B:** 92,432 tokens in the probe (12.69 GiB, 144 KiB/token); every load run logged **96,656** tokens (13.27 GiB), because vLLM measured a smaller peak activation (0.58 vs 1.17 GiB). Default `--gpu-memory-utilization 0.92` | `docs/probe/20261023_Qwen3-1.7B/probe.json`; `docs/probe/20261023_Qwen3-4B/server.log`; any load run's `server.log`; decisions.md 2026-11-01 |

# Stage 2 open questions

| # | Question | Answer | Evidence |
|---|---|---|---|
| S1 | Can `vllm serve` reset the prefix cache over HTTP at the pinned version? | **Yes, in dev mode only:** `POST /reset_prefix_cache`, registered only when `VLLM_SERVER_DEV_MODE=1`. Works on a live server in both modes (`success: true`) | vLLM 0.32.0 `entrypoints/serve/dev/cache/api_router.py`, `entrypoints/launchers/api_server/routers.py`; `20261101-144335_wipe_test_preempt`, `20261101-145940_wipe_test_idle` |
| S2 | What does the reset do to running requests? | **By default it fails** (`success: false`) while any block is held, so while any request runs. With `reset_running_requests=true`, every running request is preempted, loses its progress (`num_computed_tokens = 0`) and goes back to the waiting queue, then the cache is cleared. Live: preemptions rose by the number in flight, and those requests still returned all 128 tokens | vLLM 0.32.0 `v1/core/sched/scheduler.py` `reset_prefix_cache`, `_preempt_request`; `v1/core/block_pool.py` `reset_prefix_cache`; `20261101-144335_wipe_test_preempt` |
| S3 | Can the power limit be changed while vLLM runs, and how fast does it take effect? | **Open.** `nvidia-smi -pl` needs root, and `sudo` asks for a password on the VM, so trigger 3 needs the owner's help. Range is 100–450 W | `sudo -n nvidia-smi -pl 420` on the VM; `nvidia-smi -q -d POWER` |
| S4 | Can cached prefixes be protected from eviction, for the protected-prefixes control? | **Open, not investigated.** Not needed so far: no stuck run exists to break | — |
| S5 | K, the watch window, the stuck thresholds and the repeats per cell | **Fixed before any wipe:** K = 5, watch = max(1200 s, 5τ) = 1500 s; the verdict rule as redefined before any verdict; seeds 1–3 per cell, add 4–5 if they disagree | decisions.md 2026-10-31 (τ method), 2026-11-01 (verdict rule; "Stuck" redefined) |
| S6 | Does turn spacing matter? (try at least two turn gaps) | **Partly answered.** At 5 s gaps the cache is worth far more (μ_warm 6 vs 4; hit 0.79 vs 0.53 at λ = 4) but is much harder to crowd out, and every shock recovered (0 of 12). At 20 s, also no stuck run (0 of 18). Longer gaps (about 60 s) are untested | decisions.md 2026-11-03 and 2026-11-04 |
| S7 | What limits the running batch under overload? | **KV memory, not the 256-sequence cap:** N levels off near 65 at KV ≈ 0.95. `kv_cache_usage_perc` counts only blocks held by running requests | `20261030-151441_sweep_pc_on_r10`; vLLM 0.32.0 `v1/core/block_pool.py` `get_usage`; decisions.md 2026-11-01 |
