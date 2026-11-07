# harness/ rules

- **One clock:** `time.monotonic()` for every recorded time. It is CLOCK_MONOTONIC, shared across processes on Linux. `events.jsonl` holds a wall-clock anchor.
- **Raw counters:** store Prometheus values exactly as scraped. Compute rates later, in analysis.
- **Open loop:** loadgen never waits for an earlier request before sending the next one. No timeouts, no retries, unlimited connection pool.
- **Prompts are token IDs**, never text. The output length is fixed (`min_tokens = max_tokens`, `ignore_eos`).
- **Config only:** every number comes from the resolved config dict. `base.yaml` has been used, so new knobs go in `configs/defaults.yaml`, which `harness/config.py` `with_defaults` merges beneath every config (and beneath old run folders' configs when they are re-checked). A check whose setting is null there is skipped. `defaults.yaml` has been used too, so it is not edited either: a knob added after it (from `power_limit`, REG-8) lives only in the configs that use it and is read with `.get`, absent = skipped (owner, decisions.md 2026-11-06).
- **One run at a time:** `run.py` holds `lock_file` and refuses to start if the server port already answers.
- **Append-only files:** one JSON line per record, flushed right away, so a crash keeps everything up to that point.
- `gateway` stays inert. Triggers are built one at a time, in the plan's order.
