# Decision log

Append-only. Each entry: date · decision · why · evidence (a run id or probe path). Never edit old entries; supersede them.

## 2026-10-23 · Harness layout deviates slightly from the plan
- Schedule generation lives in `harness/workload.py` (not inside `run.py`) so it can be unit-tested.
- Prompts are stored once per session in `prompts.parquet`. A turn's prompt is `tokens[:prompt_len]`, since each turn extends the previous one. This keeps long-run schedules small.
- The check verdict goes to `runs/<id>/checks.json`. The analysis helpers are `analysis/load.py` (not `io.py`, which would shadow the stdlib).

## 2026-10-23 · vLLM pinned to 0.32.0
- Latest stable release on PyPI on this date. Locked in `uv.lock` (torch 2.13.0). Confirm the driver supports torch's CUDA build on the VM (`env/setup_vm.sh`).

## 2026-10-23 · Initial workload parameters (pre-registered, before any run)
- Sessions: 8 turns, 512 system tokens, 128 user tokens and 128 recorded-reply tokens per turn, exponential turn gap with a 20 s mean, 128 output tokens.
- Session start rate = λ / turns, so the steady request rate is λ. Warm-up is 240 s (covers the ramp-up of about 8 × 20 s).
- Latency is measured from the **planned** arrival time (open loop).
- Run checks: client lag p99 ≤ 50 ms, scrape gap ≤ 2 s, arrival count within max(15 %, 3σ Poisson), SM-clock CV ≤ 5 %, no thermal throttle bits.

## Pending (fill in BEFORE looking at the results they judge)
- Repeatability tolerance (run 3): e.g. TTFT p50/p99 and throughput within ±X % between repeats.
- Capacity definition for μ_warm and μ_off: highest λ with throughput ≥ F·λ and waiting-queue slope ≤ S. Proposed F = 0.95, S = 0.01 req/s².
- Sweep λ grid refinement around the knee after first_real.

## 2026-10-23 · vLLM 0.32.0 verified against the official docs and source (tag v0.32.0)
- **Stable:** v0.32.0 is the "Latest" GitHub release, published 2026-10-18, and is not a pre-release or yanked on PyPI. It supports Python 3.11–3.14 on Linux x86-64/aarch64. It is a fresh `.0` release: if a 0.32.1 bug-fix appears before the first real run, consider it and log the decision.
- **Flags** (docs `configuration/engine_args`): `--enable-prefix-caching` / `--no-enable-prefix-caching` (the default is on, `CacheConfig.enable_prefix_caching = True`); `--kv-cache-metrics` (default off, sampled by `--kv-cache-metrics-sample`, default 0.01); `--gpu-memory-utilization` (default 0.92); `--seed` (default 0); KV offloading (`--kv-offloading-size`, `--cpu-offload-gb`) is off by default.
- **Added `--enable-prompt-tokens-details`:** the source (`entrypoints/openai/completion/serving.py`) returns `cached_tokens` per request only when it is set.
- **Completions API** (`entrypoints/openai/completion/protocol.py`): `prompt` accepts `list[int]`, and `min_tokens`, `ignore_eos` and `stream_options` are supported.
- **Metric names** (docs `usage/metrics`) match the harness: `prefix_cache_hits/queries`, `prompt_tokens(_cached)`, `num_requests_running/waiting`, `kv_cache_usage_perc`, `num_preemptions`, `request_success`, `kv_block_idle_before_evict_seconds`, `admission_rejections`.
- **For Stage 2:** `/reset_prefix_cache` exists, but only with `VLLM_SERVER_DEV_MODE=1`.

## 2026-10-23 · VM facts and CPU pinning
- VM: Ubuntu 24.04.5, kernel 6.8, 8 vCPUs (AMD EPYC 7702P, 1 NUMA node), 31 GB RAM, 62 GB disk (46 GB free). The RTX 3090 (GA102) is passed through, but `nouveau` was loaded and no NVIDIA driver was installed.
- The driver must support CUDA 13 (the locked torch uses the cu13 runtime 13.0–13.4), so it must be ≥ 580. Install the Ubuntu-recommended `nvidia-driver-595-open`.
- Pinning: vLLM on cores 0–5, loadgen on 6, recorder on 7 (open question 6). Whether one core is enough for loadgen is checked by client lag in every run.

## 2026-10-23 · GPU driver setup on the VM (how it was made to work)
- **Driver:** `nvidia-driver-595-open` 595.99.02 (supports up to CUDA 13.2; torch uses 13.0) with Canonical's **prebuilt, signed** kernel modules `linux-modules-nvidia-595-open-generic`. The self-built DKMS module was removed: Secure Boot is on and its signing key was never enrolled, so the kernel refused it.
- **Proxmox:** the GPU's ROM was not passed to the VM, so the driver failed (`kgspExtractVbiosFromRom: did not find valid ROM signature`, `RmInitAdapter failed`). Fixed in the VM's `hostpci` settings on the Proxmox host. The VM needs a full stop/start after such changes.
- **GPU:** RTX 3090, 24 GB, power limit **420 W** (Gigabyte board, subsystem 1458:4041; reference spec is 350 W), max SM clock 2160 MHz. The power limit stays at its default during Stage 1, and `gpu.jsonl` records it every second.

## 2026-10-23 · Use uv-managed Python, not the system Python
- **Evidence:** the first `vllm serve` on the VM failed with `cuda_utils.c: fatal error: Python.h: No such file or directory`. Triton compiles a C helper at startup, and Ubuntu's `/usr/bin/python3.12` has no development headers.
- **Fix:** `[tool.uv] python-preference = "only-managed"`. uv's CPython build includes the headers, needs no sudo, and is the same build on the Mac and the VM. `uv.lock` is unchanged. `env.json` records the exact Python version for every run.

## 2026-10-23 · uv.lock change: prebuilt FlashInfer kernels (rule 3)
- **Evidence:** the second `vllm serve` failed at startup with `RuntimeError: Could not find nvcc` inside `flashinfer.sampling` (vLLM's default FlashInfer top-k/top-p sampler JIT-compiles a kernel). The VM has no CUDA toolkit. vLLM's own startup warning recommends `vllm download-kernels`.
- **Fix:** pin exactly what `vllm download-kernels --dry-run` would install for flashinfer 0.7.0.post1 / CUDA 13.0: `flashinfer-cubin==0.7.0.post1` and `flashinfer-jit-cache==0.7.0.post1+cu130`, plus its per-architecture packages (the RTX 3090 uses `sm80`), all from flashinfer.ai's official index. They are in `uv.lock` instead of a one-off install, so `uv sync` keeps them and every run is pinned.
- **Supporting settings:** `tool.uv.environments` is limited to Linux x86_64 and macOS arm64. `override-dependencies` restricts the ARM-only `sm110a`/`sm121a` packages to aarch64, because uv assumes one metadata set for all wheels.
- **Effect on Linux x86_64:** only the 8 FlashInfer packages are added. vllm 0.32.0, torch 2.13.0, flashinfer-python 0.7.0.post1 and the CUDA 13.0 runtime libraries are unchanged. The removed lock entries were Windows-only packages and CUDA 13.4 variants that were never installed.
- **Kept at vLLM's default** (no `VLLM_USE_FLASHINFER_SAMPLER=0`), so the server stays production-like.

## 2026-10-23 · gpu_steady check refined after the first smoke run (harness debugging, before any measurement)
- **Evidence:** run `20261023-145613_smoke` is INVALID on `gpu_steady`. One of 66 samples had mask `0x24` (SW power cap + SW thermal slowdown) at 53 °C, with the SM clock at its 2040 MHz maximum. Clock CV was 4.4%, only because the GPU alternated idle (1860 MHz) and busy (2040 MHz) at λ = 0.5. Neither is a hardware slowdown.
- **New rule** (configs/base.yaml `checks`): any HW throttle bit (0x8, 0x40, 0x80) in any sample fails the run. SW thermal (0x20) fails it only above 5% of samples. SM-clock CV ≤ 5% is computed over busy samples (util ≥ 50%). The SW power cap (0x4) is ignored, since it is normal boost behaviour.
- That smoke run stays INVALID as recorded. It is not re-judged.

## 2026-10-30 · Repeat tolerance and capacity rule pre-registered (before any sessions-workload run)
Supersedes the first two "Pending" items above. Written before `first_real` ran; the only data so far is the two smoke runs (1.7B, random prompts, λ = 0.5), which say nothing about these numbers.
- **Repeat tolerance (step 3):** `first_real` and two runs of `repeat.yaml` (same seed), compared pairwise using `analysis/load.py` `summarize()` over the measured window. They agree if every pair is within: throughput ±2 %, TTFT p50 ±10 %, TTFT p99 ±25 %, hit rate ±0.02 absolute. Relative differences are taken against the smaller of the pair. p99 gets more room because it rests on about 13 of 1,320 requests at λ = 2. A miss is reported as a miss; the tolerance is not widened afterwards.
- **Capacity rule (steps 4–5):** μ is the highest swept λ whose run is valid, with throughput ≥ 0.95 λ and waiting-queue slope ≤ 0.01 req/s², both over the measured window (F and S as proposed above; `analysis/load.py` `capacity()`).
- The sweep λ grid stays pending until after step 2, as planned.

## 2026-10-30 · VM address changed
- After a reboot the VM came up on 192.168.3.249 instead of 192.168.3.243 (DHCP). Same machine: the SSH host keys match the ones recorded for the old address. The Mac's `vm` remote now points to the new address. SSH uses `~/.ssh/id_ed25519_vllm`; the Mac's default key is not authorized there.

## 2026-10-30 · Failed start `20261030-114021_first_real` (operator error, no load sent)
- **Evidence:** `server.log` says `taskset: failed to execute vllm: No such file or directory`; `events.jsonl` has `server_failed` with return code 127. I had run `uv sync --frozen` on the VM without `--extra server`, which uninstalled vLLM, torch and the other server packages.
- **Fix:** `uv sync --frozen --extra server` (the command in `env/setup_vm.sh`). vLLM 0.32.0 and torch 2.13.0 are back, `uv.lock` is unchanged, and `env_snapshot` matches the valid smoke run on every field except the git commit.
- The folder is kept as it is. It has no `checks.json` because `run.py` exits before the checks when the server never starts, so `find_runs()` already leaves it out with its default `valid_only`. It does not count as a step 2 run.

## 2026-10-30 · Step 3 result: repeats agree within the pre-registered tolerance
- **Evidence:** `20261030-114115_first_real`, `20261030-120420_repeat`, `20261030-122024_repeat`. All three are VALID, with the same workload and seed. `first_real` ran at commit 0178705 and the repeats at bcdaa6e; the only change between them is in docs.
- **Largest pairwise differences:** throughput 0.00 % (limit 2 %), TTFT p50 0.83 % (limit 10 %), TTFT p99 2.31 % (limit 25 %), hit rate 0.0006 (limit 0.02).
- **Limits of this result:** all runs share one seed, so this shows the server and harness repeat on an identical schedule, not how much results vary across schedules. Throughput cannot differ below capacity, because every request completes, so that row is a weak test here. The limits turned out much wider than the observed differences. They stay as registered.

## 2026-10-30 · Sweep λ grid kept (before any sweep run)
- Steps 4 and 5 use the existing grid [1, 2, 3, 4, 5, 6, 8, 10] from `sweep_pc_on.yaml`. **Why:** the λ = 2 runs had an empty queue and KV usage of 22 % at most, so they say nothing about where the knee is. Both sweeps use the same grid so the curves compare point by point.
- If the knee falls in a wide gap, extra rates go in a new config, logged here before they run. μ is only known to the resolution of the rates actually run.

## 2026-10-30 · `20261030-145339_sweep_pc_on_r8` is INVALID on `accounting`
- **Evidence:** `checks.json` reports 5,146 ok at the client and 5,147 in vLLM's success counter, an off-by-one. The other 1,543 of 6,689 requests were still unfinished at the 300 s drain deadline and count as misses. `request_success_total` shows no aborts or errors, and every other check passed.
- **Likely cause, not proven:** a request finished in vLLM just as loadgen hit the drain deadline, so the client cancelled it before reading its last chunk. `requests.jsonl` does not hold enough detail to confirm this. 72 of the unfinished requests had already received a first token.
- The run stays INVALID as recorded and is not re-judged, so it cannot count toward μ under the capacity rule. Any change to the check needs its own entry before the runs it judges.

## 2026-10-30 · Step 4 result: μ_warm = 4 req/s
- **Evidence:** sweep `20261030-131243_sweep_pc_on_r1` to `20261030-151441_sweep_pc_on_r10`, capacity rule as registered (F = 0.95, S = 0.01). λ = 1–6 and 10 are VALID; λ = 8 is INVALID on `accounting`. λ = 4 passes (queue slope 0.000); λ = 5 fails (slope 0.426). The true limit is in [4, 5), at this grid's resolution and the 420 W power limit.
- **Deviation from the plan's definition:** `summarize()` `throughput` counts requests that *arrived* in the measured window and eventually completed, including during the drain, whereas the plan defines throughput as completions per second. It therefore stays near λ during overload (λ = 6 reports 6.12), so in this sweep the queue-slope condition did the rejecting. It cannot change μ_warm: this column can only make a run look better, and every rate above 4 already fails on slope.
- **λ = 8 is not rerun:** λ = 10 is VALID, so the curve already has a valid overloaded point.

## 2026-10-30 · Step 4 follow-up: true completion rate and unsettled runs
- **μ_warm stays 4 with completions per second:** λ = 4 completes 3.991 req/s in the measured window (0.998 of λ). λ = 5 completes 4.723 (0.945), so it fails on this measure as well. The most the server completed at any rate is about 4.7 req/s, and that falls under heavier overload (λ = 8: 4.34, λ = 10: 4.19).
- **Surprising:** hit rate falls with load while the queue is still empty (λ = 2: 0.73, λ = 3: 0.63, λ = 4: 0.49), and λ = 3 keeps drifting inside the measured window (thirds: 0.674, 0.625, 0.585; TTFT p50 0.092, 0.114, 0.126 s). So a 900 s run may not fully settle at these rates. The λ = 4 run was also close to its limits: KV usage peaked at 99.8 %, with 2 preemptions. The cause is not established. The step 6 long run is the direct test of whether these rates are stable.

## 2026-10-30 · `accounting` check and `throughput` definition changed (before step 5, approved by the study owner)
- **`accounting`:** vLLM's success count must now lie between the client's ok count and that count plus the unfinished requests that had already received a first token. Previously the two had to be equal. **Why:** `20261030-145339_sweep_pc_on_r8` failed by one request at the drain deadline, and with prefix caching off more runs will hit that deadline. Any other mismatch still fails.
- **`throughput` in `analysis/load.py` `summarize()`:** now completions per second inside the measured window, the plan's definition. It replaces the arrival-based count described in the step 4 entry.
- **Effect on earlier results:** recorded `checks.json` files are not changed, and `20261030-145339_sweep_pc_on_r8` stays INVALID as recorded, although the new rule would pass it. So the two sweeps were judged under different versions of this check. μ_warm stays 4 under the new `throughput`. The capacity rule's thresholds are unchanged.
- **Scope:** step 5 and later runs. The repeat comparison in step 3 is not re-judged.

## 2026-10-30 · Step 5 result: μ_off = 2 req/s
- **Evidence:** sweep `20261030-154544_sweep_pc_off_r1` to `20261030-175458_sweep_pc_off_r10`, capacity rule as registered. λ = 2 passes. λ = 3 fails narrowly on queue slope alone (0.0130 against the 0.01 limit), with throughput 2.906 (0.969 of λ), so it is near the limit. The rule is applied as registered, and the true limit is in [2, 3). The server saturates at about 3.5 completions/s at every overloaded rate.
- **`20261030-175458_sweep_pc_off_r10` is INVALID on `recorder`:** one scrape timed out at t = 1201.1 s, the moment `load_end` was logged and the load generator was cancelling its remaining connections. That is after the measured window, and every other check passed. It stays INVALID as recorded and is not rerun, because λ = 8 is a valid overloaded point on this curve. The check is unchanged.
- **`accounting`:** this run did use the new allowance (4,207 in vLLM, 4,205 at the client, 57 cut off after a first token).
- **Gap:** μ_off = 2 and μ_warm = 4. Completions saturate at about 3.5 req/s without the cache and about 4.7 with it. Overload lowers completions with the cache on (4.73 at λ = 6, 4.18 at λ = 10) but not with it off, where they stay flat.

## 2026-10-30 · Step 6 load and pass criteria (before the long run)
- **Load:** λ = 3, inside (μ_off, μ_warm), and the only whole-number rate in that gap with data from both sweeps. **Caveat:** cache-off λ = 3 exceeds the capacity rule only narrowly, so a cache loss at this load may be survivable. Other Stage 2 loads get their own no-trigger controls under the plan.
- **Healthy means all of:** (1) the run is VALID; (2) throughput ≥ 0.95 λ and queue slope ≤ 0.01 req/s² over the measured window; (3) comparing the last third of the measured window with the middle third, TTFT p50 is at most 25 % higher and hit rate at most 0.05 lower. The first third is left out because the λ = 3 sweep run was still drifting at that stage.
- If it fails, λ = 3 cannot be used later, as the plan says. These limits are not widened after the result.

## 2026-10-30 · Step 6 result: λ = 3 stays healthy for 2 h
- **Evidence:** `20261030-181851_long_run`, judged with the criteria registered before the run. **All three pass:**
  1. VALID, every check passed. All 21,551 requests finished ok, and vLLM's count matches exactly.
  2. Throughput 3.013 req/s (1.004 of λ, limit 0.95); queue slope about 0 req/s² (limit 0.01).
  3. Last third against middle third: TTFT p50 0.1166 s against 0.1152 s, 1.3 % higher (limit 25 %); hit rate 0.6004 against 0.6083, 0.008 lower (limit 0.05). Computed from counter totals per third instead of the mean of per-interval rates, hit rate is 0.6254 against 0.6363, 0.011 lower, which also passes.
- **Other numbers:** TTFT p50 0.116 s, p99 0.513 s; queue peak 2; KV peak 54.5 %; no preemptions; no HW throttling; peak 81 °C.
- **The step 4 drift did not continue:** the λ = 3 sweep run fell through 0.674, 0.625, 0.585 by thirds of its window, whereas here the thirds hold at 0.609, 0.608, 0.600. The earlier fall looks like settling after start-up, or sweep-run variation; this run does not show which. The cause of the lower hit rate at higher load is still not established.
- **Limit of this result:** one 2 h run at one seed, at one load. It shows no drift over 2 h, not stability at longer times. It says nothing about loads other than λ = 3.

## 2026-10-30 · SLO fixed: TTFT ≤ 1.0 s, measured from the planned arrival
- **Value:** a request is fast if its first token arrives within 1.0 s of its planned arrival and it finishes ok. Unfinished requests are misses. Stage 2 configs set `slo.ttft_s: 1.0`; `base.yaml` keeps `null` because runs have already used it.
- **Why this value:** the plan sets the limit just above healthy latency. In `20261030-181851_long_run`, the measured window has TTFT p99 0.513 s and a maximum of 0.941 s, so percent fast is 100 % in every minute. A limit of 0.5 s would mark healthy requests as misses (98.9 % overall, 89.8 % in the worst minute).
- **It separates the cases Stage 2 needs:** at λ = 3, percent fast is 100 % with the cache on and 77.5 % with it off (`20261030-161749_sweep_pc_off_r3`). So it would register a server left running without its cache at this load.
- **Limits:** the margin over the healthy maximum is only about 6 %, so one slow request can miss without the server being unhealthy. Stage 2 verdicts should rely on percent fast over time, not single misses. At λ = 4 with the cache on, percent fast is already 98.1 %. `1.0` was also the notebook's provisional value before this data existed; it was kept because the data supports it, not chosen independently of it. It is fixed before any Stage 2 run exists.

## 2026-10-30 · Load–latency figure generated; notebook excludes invalid runs
- `analysis/analysis.ipynb` now leaves invalid runs out of the repeat table and the load–latency curves, as `analysis/CLAUDE.md` requires. It previously included them, and the failed start's empty requests crashed it. So the curves have no λ = 8 point with the cache on and no λ = 10 point with it off. From valid runs only, the notebook reproduces μ_warm = 4 and μ_off = 2.

## 2026-10-30 · Noticed in the long run: rare client-lag spikes
- In `20261030-181851_long_run`, 18 of 21,551 requests were sent more than 20 ms late, in 12 short episodes, the worst 0.232 s. Client-lag p99 is 0.0026 s against the 0.05 s limit, so the run is VALID. The cause is not established. Latency is measured from the planned arrival, so these delays count against the server's numbers instead of being hidden, and a 0.23 s spike is a large part of the SLO margin. Worth watching in Stage 2 if isolated misses appear.

## 2026-10-31 · Open question 5: method and limits, before any recorder-off data
- **Question:** does the recorder slow the server? **Runs:** `configs/recorder_off.yaml`, cache on, λ = 3, 4, 5, same seed and settings as `sweep_pc_on`. The baselines are `20261030-134449_sweep_pc_on_r3`, `20261030-140051_sweep_pc_on_r4` and `20261030-141658_sweep_pc_on_r5`. Since their commit only `harness/checks.py` changed in `harness/`, and `uv.lock` did not change.
- **Recorder off means:** no recorder process, so nothing scrapes `/metrics` or reads the GPU during the load. `run.py` scrapes once before and once after the load, so `accounting` still works.
- **Checks in these runs:** the scrape-gap limit does not apply and `gpu_steady` is skipped, because there is no data for them. All other checks apply. **So throttling cannot be ruled out in these runs.** The baselines had no HW throttling. I also will not query `/metrics` or `nvidia-smi` during these runs.
- **Harness change:** `recorder.enabled`, read with a default of on, because older run configs do not have the key. The default is not added to `base.yaml`, since runs have already used that file (rule 5). This departs from `harness/CLAUDE.md`, which asks for new knobs in `base.yaml`. Behaviour with the recorder on is unchanged.
- **No measurable effect if all hold, recorder-off against baseline:**
  - λ = 3 and 4: throughput within ±2 %, TTFT p50 ±10 %, TTFT p99 ±25 %, whole-run hit rate ±0.02. These are the step 3 repeat limits. Whole-run hit rate uses the first and last scrape on both sides.
  - λ = 5: throughput ±2 %, hit rate ±0.02. TTFT is only reported, because it is overloaded and follows the backlog.
- **μ_warm stays 4 if:** λ = 4 keeps up and λ = 5 does not, where keeping up means throughput ≥ 0.95 λ and client backlog slope ≤ 0.01 req/s². Backlog is requests sent without a first token, a client-side stand-in for the queue, which these runs cannot record. Checked on existing data only: it gave the same keep-up verdict as the queue slope on all 14 valid sweep runs.
- **Limits of the method:** the step 3 limits came from λ = 2, so noise at λ = 3–5 has not been measured. Each side is one run, and the baselines ran hours earlier, so GPU temperature at the start may differ. If a difference exceeds a limit, it is reported as exceeding, and a with-recorder repeat at that λ is what would tell an effect from noise. Limits are not widened. μ_off is not retested; any recorder effect on it is inferred only.
