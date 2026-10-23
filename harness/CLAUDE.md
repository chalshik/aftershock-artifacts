# harness/ rules

- **One clock:** `time.monotonic()` for every recorded time. It is CLOCK_MONOTONIC, shared across processes on Linux. `events.jsonl` holds a wall-clock anchor.
- **Raw counters:** store Prometheus values exactly as scraped. Compute rates later, in analysis.
- **Open loop:** loadgen never waits for an earlier request before sending the next one. No timeouts, no retries, unlimited connection pool.
- **Prompts are token IDs**, never text. The output length is fixed (`min_tokens = max_tokens`, `ignore_eos`).
- **Config only:** every number comes from the resolved config dict. Add new knobs to `configs/base.yaml` with their defaults.
- **Append-only files:** one JSON line per record, flushed right away, so a crash keeps everything up to that point.
- Stage 2 hooks (`trigger`, `gateway`) stay inert. Do not add trigger logic in Stage 1.
