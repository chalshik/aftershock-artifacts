# Stage 1 open questions

Answer each one with evidence only (`docs/probe/...`, the vLLM source at the pinned version, or a run id).

| # | Question | Answer | Evidence |
|---|---|---|---|
| 1 | Is vLLM's admission queue limit on by default (`vllm:admission_rejections`)? | **No.** `max_num_queued_reqs` and `max_num_queued_tokens` default to None. The metric exists and stays 0 | `vllm/config/scheduler.py`; `docs/probe/20261023_Qwen3-1.7B/probe.json`, `metrics.txt` |
| 2 | Does `/v1/completions` accept token IDs as the prompt? | **Yes.** A 300-token-ID prompt returned HTTP 200 | `docs/probe/20261023_Qwen3-1.7B/probe.json` `token_id_prompt` |
| 3 | Does vLLM report cached tokens per request (`usage.prompt_tokens_details.cached_tokens`)? | **Yes**, with `--enable-prompt-tokens-details`. The same 300-token prompt sent twice reported `cached_tokens: 288` (18 full 16-token blocks) | `docs/probe/20261023_Qwen3-1.7B/probe.json` `cached_tokens_per_request` |
| 4 | Exact flag names for prefix caching, KV metrics and the sequence cap | `--enable-prefix-caching` / `--no-enable-prefix-caching`, `--kv-cache-metrics`, `--enable-prompt-tokens-details`, `--max-num-seqs`. All present | `docs/probe/20261023_Qwen3-1.7B/probe.json` `flags_present`, `serve_help.txt` |
| 5 | Does the recorder slow the server? (μ_warm with and without it) | | |
| 6 | Enough CPU cores to pin loadgen and the recorder away from vLLM? | 8 cores, 1 NUMA node: vLLM on 0–5, loadgen on 6, recorder on 7. Each run's client-lag check confirms whether loadgen keeps up | `nproc`; decisions.md (VM facts) |
| 7 | Real KV capacity per model, from the startup log | **1.7B:** 165,792 tokens (17.71 GiB, 112 KiB/token). **4B:** 92,432 tokens (12.69 GiB, 144 KiB/token). Both match the plan's estimates. Default `--gpu-memory-utilization 0.92` | `docs/probe/20261023_Qwen3-1.7B/probe.json`; `docs/probe/20261023_Qwen3-4B/server.log` |
