# Stage 1 open questions

Answer each one with evidence only (`docs/probe/...`, the vLLM source at the pinned version, or a run id).

| # | Question | Answer | Evidence |
|---|---|---|---|
| 1 | Is vLLM's admission queue limit on by default (`vllm:admission_rejections`)? | No (from source): `max_num_queued_reqs`, `max_num_queued_tokens` and `max_num_active_seqs` all default to None. The metric exists | `vllm/config/scheduler.py`; vLLM v0.32.0 source/docs; see decisions.md 2026-10-23. Confirm with env/probe.py |
| 2 | Does `/v1/completions` accept token IDs as the prompt? | Yes (from source): `prompt: list[int]` | `entrypoints/openai/completion/protocol.py`; vLLM v0.32.0 source/docs; see decisions.md 2026-10-23. Confirm with env/probe.py |
| 3 | Does vLLM report cached tokens per request (`usage.prompt_tokens_details.cached_tokens`)? | Yes, only with `--enable-prompt-tokens-details` (now in base.yaml) | `completion/serving.py:453`; vLLM v0.32.0 source/docs; see decisions.md 2026-10-23. Confirm with env/probe.py |
| 4 | Exact flag names for prefix caching, KV metrics and the sequence cap | `--enable-prefix-caching` / `--no-enable-prefix-caching`, `--kv-cache-metrics` (+ `--kv-cache-metrics-sample`), `--max-num-seqs` | docs engine_args v0.32.0; vLLM v0.32.0 source/docs; see decisions.md 2026-10-23. Confirm with env/probe.py |
| 5 | Does the recorder slow the server? (μ_warm with and without it) | | |
| 6 | Enough CPU cores to pin loadgen and the recorder away from vLLM? | | |
| 7 | Real KV capacity per model, from the startup log | 1.7B: · 4B: | |
