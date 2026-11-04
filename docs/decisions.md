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

## 2026-10-31 · Open question 5 result: no recorder effect beyond the registered limits
- **Evidence:** `20261031-013840_recorder_off_r3`, `20261031-015442_recorder_off_r4` and `20261031-021045_recorder_off_r5` against the registered baselines. All three are VALID under the reduced checks. All limits hold. Recorder-off minus baseline:

| λ | Throughput (±2 %) | TTFT p50 (±10 %) | TTFT p99 (±25 %) | Hit rate (±0.02) |
|---|---|---|---|---|
| 3 | 0.00 % | −2.9 % | −0.3 % | 0.000 |
| 4 | 0.00 % | −1.0 % | −6.3 % | −0.000 |
| 5 | +0.64 % | +2.3 % (reported only) | −5.5 % (reported only) | +0.001 |

- **μ_warm stays 4:** with the recorder off, λ = 4 keeps up and λ = 5 does not. At λ = 5, throughput clears 0.95 λ by a hair (4.753 against 4.75, whereas the baseline's 4.723 did not), so only the backlog slope rejects it (0.404 against the 0.01 limit). The queue is clearly growing, so this is not a close call.
- **What this does not show:** it does not show zero effect. It shows no effect larger than these limits, from one run on each side, and most latency differences lean slightly faster without the recorder, which one pair cannot confirm or dismiss. GPU throttling was not observable in these runs. μ_off was not retested; that the recorder acts the same way with caching off is an inference.
- **Client-lag spikes are not caused by the recorder alone:** the largest send lag with the recorder off is 0.156 s at λ = 5 and 0.050 s at λ = 4, so spikes occur without it. The cause is still not established. The client-lag check passed in all three runs.
- **Decision:** the recorder stays on as configured for later stages. No cache-off check is run, as there is no effect here that would call for one.

## 2026-10-31 · Stage 1 finished
- Every Done-when box is ticked and all open questions have answers. Carried forward as known limits: μ_off rests on a narrow fail at λ = 3; the recorder was tested with caching on only; the λ = 3 health result is one 2 h run; the SLO has a thin margin over healthy latency; and the causes of client-lag spikes and of the lower hit rate at higher load are not established.

## 2026-10-31 · Stage 2 started; correction: Stage 1 did not deliver τ
- **Scope:** the study owner started Stage 2. `CLAUDE.md` and `harness/CLAUDE.md` are updated to match.
- **Correction:** the "Stage 1 finished" entry above is wrong on one point. The plan lists recovery time τ under "Inputs from Stage 1", and it was never measured. It is not in the Done-when list, which is how it was missed. It sets how long to watch after a trigger, so it is measured before the verdict thresholds are fixed.

## 2026-10-31 · τ: method, before the run
- **Run:** `configs/tau.yaml`, cache on, no wipe, no dev mode. λ = 2 to t = 900 s, λ = 3 to t = 2100 s, λ = 2 to t = 3300 s. Both rates are at or below the point where λ = 3 was shown healthy for 2 h. The harness gains `workload.steps`; a config without it draws the same random numbers as before, and a test checks this.
- **Settled level:** hit rate and TTFT p50 over the last 480 s of the segment.
- **τ for one step:** time from the step until a sliding 180 s span, moved 60 s at a time, has hit rate within ±0.03 and TTFT p50 within ±0.02 s of the settled level. **τ is the larger of the up-step and down-step values.**
- **Why these bands:** they come from healthy data and not from this run. In `20261030-181851_long_run`, 60 s hit rate has SD 0.045 and TTFT p50 SD 0.019 s, which is about 0.026 and 0.011 s over 180 s. The expected size of the step is about 0.14 and 0.03 s, so TTFT p50 only weakly separates the levels and the result is coarse.
- **Expected floor:** session arrivals change at the step, but the request rate takes about one session's length (7 turn gaps × 20 s = 140 s) to follow, so τ includes that lag.
- **If a step never settles by this rule,** τ is reported as "more than" the time tested, and the bands are not changed afterwards.
- **Use:** watch window = max(1200 s, 5 τ), so K = 5. The 1200 s floor is at least 8 session lengths, so a slow drain has time to show.

## 2026-10-31 · Cache wipe differs from the plan: it has to preempt running requests
- **Evidence:** the source answer in `docs/open-questions.md` (S1, S2), plus idle time from recorded runs. Windows with nothing running: λ = 2, 4.4 per minute; λ = 3, 0.8 per minute, with up to 485 s between usable ones (`20261030-181851_long_run`); **λ = 4, none in the whole window** (`20261030-140051_sweep_pc_on_r4`).
- **Decision:** the main wipe uses `reset_running_requests=true`, because waiting for an idle instant cannot work across the danger zone and would also pick only unusually quiet moments.
- **Deviation:** the plan says the wipe touches no running requests and adds no work. This wipe adds no requests, but every running request starts over and repeats its prefill: about 8 at λ = 3 and 21 at λ = 4 (mean N). So leftover backlog is not ruled out as a cause, as the plan had hoped. **Check to run:** at λ = 3, also wipe at an idle instant without preempting, and compare. If both behave alike, the redone work is not what decides the result.
- **All Stage 2 cache-wipe runs and their no-trigger controls run in dev mode.** Stage 1 runs did not, so controls are compared within Stage 2 only. From the source, dev mode adds routes and error-stack logging; its effect on speed is not measured beyond that comparison.

## 2026-10-31 · τ run interrupted: the VM was shut down
- `20261031-025032_tau` started at 02:50 VM time. By about 03:30 the VM no longer answered ping or SSH. The study owner believes it was shut down. The run's state has not been inspected, because the VM is off.
- **When the VM is back:** look at the run folder and logs before anything else. If the run has no `checks.json`, it stays on record as unfinished and does not count, and `configs/tau.yaml` is rerun unchanged at a new run id. Its folder is not copied over or deleted.

## 2026-11-01 · τ run: what stopped it, and the rerun
- **Cause, from the VM's journal:** `Power key pressed short` at 02:53:50 on 2026-10-31, then a clean power-off. On this Proxmox VM that signal most likely came from the host; the journal cannot show who or what sent it. No crash, out-of-memory or GPU errors in the journal or `server.log`; last GPU sample 70 °C, 315 W, no throttle reasons.
- **Extent:** `20261031-025032_tau` stopped about 140 s into 3300 s, before the first step at 900 s, with 170 requests and no `checks.json`. It does not count and gives no τ data. It stays on the VM, not yet copied to the Mac.
- **Rerun:** `20261101-131823_tau` started 13:18 VM time from a clean tree at `9fc33c3`, the same commit as the interrupted run. Its `config.yaml` differs only in `run_id`; vLLM, torch and `uv.lock` are unchanged. The tau settings and verdict rule above are unchanged.
- **Not compared:** after the reboot `nvidia-smi` shows persistence mode `Disabled` while `nvidia-persistenced` is active. `env.json` does not record this mode, so it can't be compared with earlier runs. It is noted here in case it matters later.

## 2026-11-01 · τ result: 300 s; watch window 1500 s
- **Run:** `20261101-131823_tau`, VALID, all checks passed, 7872 of 7872 requests ok. Both τ run folders are now copied to the Mac.
- **Result under the registered rule:** τ up-step = 300 s, τ down-step = 60 s, so **τ = 300 s**. Watch window = max(1200 s, 5 × 300 s) = **1500 s**. Settled levels: λ = 3 hit 0.598, TTFT p50 0.131 s; λ = 2 hit 0.748, TTFT p50 0.087 s.
- **Limits of this number, found after the run; the rule and bands are not changed:**
  - The rule takes the first span inside the band, and spans then left it again. Up-step: back out at 660 s (hit +0.041). Down-step: out from 180 s to 300 s (hit up to +0.047), so its 60 s is below the expected 140 s session lag and looks like a chance crossing. Slow hit-rate drift of about ±0.04 is about the size of the ±0.03 band.
  - Time is counted to the start of the 180 s span, so the span's data runs up to 180 s past the stated τ.
  - This is one run with one seed.
- **Reading:** τ = 300 s is the registered value and sets the 1500 s watch window. The real settling time could be longer, by up to several hundred seconds. If Stage 2 verdicts turn out to depend on data near the end of the window, that is a reason to watch longer, recorded as a new pre-registered change.

## 2026-11-01 · Cache-wipe method checked against official sources; trigger built
- **Official docs at v0.32.0:** `docs/serving/online_serving/README.md` and `docs/usage/security.md` list `/reset_prefix_cache` as a development endpoint, enabled by `VLLM_SERVER_DEV_MODE=1`: "Reset prefix cache (can disrupt service)", not for production. Our server listens only on 127.0.0.1 in a private experiment, so that warning doesn't apply.
- **Source at v0.32.0:** the `BlockPool.reset_prefix_cache` docstring names "resetting prefix caching status for benchmarking" as a use. The `reset_running_requests=true` behaviour is not described in the prose docs at v0.32.0. It is established by the source (`Scheduler.reset_prefix_cache`, `_preempt_request`) and by merged PR vllm-project/vllm#28827, which added it.
- **Maintainer position:** issue vllm-project/vllm#32593, closed as not planned: no plan to make the endpoint public, because of denial-of-service risk; set dev mode if you accept that risk.
- **Known failure, not expected here:** issue vllm-project/vllm#60552 (open; reproduced on 0.30.0): the preempting call returns HTTP 500 while an OffloadingConnector load is in flight. We use no offload. If it happens, the `trigger` check marks the run invalid.
- **Conclusion:** the method is a documented endpoint used for a purpose its source names. The plan's "without touching running requests" still doesn't hold, as already logged. Nothing has been run on a live server yet, so these remain claims from docs and source.
- **Built:** `harness/trigger.py` (modes `preempt` and `idle`; one record per attempt in `trigger.jsonl`), `server.env` for dev mode, and a `trigger` check (exactly one successful wipe, before arrivals end). A config with a trigger but no dev mode stops before the server starts. Preempt mode never retries, since a second call would preempt again.
- **To confirm in the live test at λ = 2:** `success: true`; `vllm:num_preemptions_total` rises by about the running count; preempted requests still return all 128 tokens with no errors; `accounting` and the counter-decrease check pass (the reset also clears a metrics collector in the block pool; whether that touches the Prometheus counters is not confirmed); hit rate falls right after the wipe.

## 2026-11-01 · Stage 2 verdict rule and first test matrix, before any wipe
- **Healthy variation these limits sit outside:** `20261030-181851_long_run` (λ = 3): percent fast 1.000 in every 60 s bin; hit rate over 300 s ranged 0.593–0.679; mean waiting 0.004, max 2. `20261101-131823_tau` at λ = 3: lowest 60 s percent fast 0.991, lowest 300 s 0.998.
- **Run shape:** `configs/stage2_base.yaml`. Dev mode on, SLO TTFT ≤ 1.0 s, 2400 s long, wipe at t = 900 s. Baseline is the last 600 s before the wipe. Watch is 1500 s from the end of the wipe. `end` is its last 300 s and `previous` the 300 s before.
- **Verdict, in this order** (code: `analysis/load.py`, `verdict`):
  1. **bad_baseline:** baseline percent fast < 0.98. The run says nothing.
  2. **recovered:** at `end`, percent fast ≥ baseline − 0.02, hit rate ≥ baseline − 0.06, mean waiting ≤ baseline + 1.
  3. **slow_drain:** waiting slope at `end` ≤ −0.01 req/s², or percent fast and hit rate both rose by ≥ 0.02 from `previous` to `end`.
  4. **stuck:** percent fast ≤ baseline − 0.10 and hit rate ≤ baseline − 0.06 at `end`.
  5. **unclear:** none of these. Reported as such, never rounded to another verdict. A longer watch needs a new pre-registered config.
- **A stuck verdict is a metastable failure only if** the no-trigger control at the same load is `recovered` by the same rule, judged at t = 900 s.
- **Matrix, cache wipe with `preempt`:** λ = 1.5 (below μ_off, sanity check), 2.5, 3, 3.5, 4. Seeds 1, 2, 3 each, reported as "stuck in k of n". If a load's seeds disagree, add seeds 4 and 5. One no-trigger control per load at seed 1, same schedule as the wiped seed 1 run. The `--seed` passed to vLLM stays 0; only the workload seed changes.
- **`idle` comparison, λ = 3, seeds 1–3:** retry every 0.05 s, for up to 600 s, duration 3000 s so the full watch always fits. The retries themselves are load on the engine; their count is in `trigger.jsonl`.
- **Order:** live test at λ = 2 (`wipe_test_preempt`, `wipe_test_idle`; mechanics only, no verdict), then controls, then wipes. A failed mechanics item stops the matrix. About 42 min per run; about 15 h for the matrix without extra seeds.

## 2026-11-01 · Live wipe test at λ = 2: every mechanics item passed
- **Runs:** `20261101-144335_wipe_test_preempt`, `20261101-145940_wipe_test_idle`, both VALID, commit `4509afe`, 1661 of 1661 requests ok, all with 128 output tokens. No counter decreases, so the reset does not touch the Prometheus counters we use.
- **`preempt`:** one call, `success: true`, 14 ms. `vllm:num_preemptions_total` went 0 → 2, matching the 2 requests in flight. Both finished with 128 tokens in about 2.7 s against a usual 1.9 s.
- **`idle`:** 178 attempts over 11.5 s (about 15 per second), 177 `success: false`, then `success: true`, with no preemptions and none in flight. At λ = 3 the wait can be far longer, so this retry load is untested there.
- **Hit rate around the wipe:** 0.774 before; 0.229 in the first 15 s; 0.681 at 15–60 s; 0.752 at 60–120 s (`preempt`). `idle` was similar: 0.773, 0.249, 0.634, 0.745. TTFT p50 rose from 0.087 s to 0.229 s (`preempt`) and 0.147 s (`idle`) for 15 s, then returned. This is a mechanics check at a load expected to recover, with one seed and no verdict.
- **Answers the source-only claims logged earlier:** the endpoint and both modes behave as read from the source on a live server.
- **Next:** no-trigger controls, `configs/stage2_control.yaml`. Wipe configs are added once the controls are read.

## 2026-11-01 · Control sweep stopped by the study owner
- **Stopped on request at 15:35 UTC,** about t = 1047 s of the first run, by sending the interrupt to the harness process. No control had finished.
- `20261101-151707_stage2_control_r1.5` is INVALID (`accounting`, `arrival_rate`, because it was cut short: 1562 of 3494 requests). It stays on record and does not count. Nothing failed before the stop: all 1562 recorded requests were `ok`.
- **To continue:** rerun `configs/stage2_control.yaml` unchanged at new run ids. All five loads are still owed, so no new config is needed.

## 2026-11-01 · What limits the running batch: memory, not the sequence cap
- **Run:** highest-load valid sweep run, `20261030-151441_sweep_pc_on_r10` (λ = 10), measured window. `20261030-175458_sweep_pc_off_r10` is INVALID (`recorder`) and is supporting evidence only.
- **Cap:** the run's config sets no `--max-num-seqs`, so no cap value is recorded there, and the server log doesn't print it. The value comes from `vllm/engine/arg_utils.py` at v0.32.0: 256 for a GPU under 70 GiB, for the API server. This is read from the source, not reported by the live server.
- **Result:** N median 65, p99 79, max 80, about 64 in every 2-minute span, while the waiting line grew to 4522. That is about a quarter of the cap. KV usage median 0.952, p99 1.000; ≥ 0.99 for 17.7 % of samples; 328 preemptions. So memory is the limit.
- **Limit of this result:** it was measured under overload. At λ = 3 the healthy server sits far from the limit (`20261030-181851_long_run`: N mean 8.2, KV mean 0.13, p99 0.38, 0 preemptions). Whether a wipe at λ = 3 pushes the server to the memory limit is still untested. With caching off at λ = 3, KV p99 reached 1.00 but the mean was 0.41 (`20261030-161749_sweep_pc_off_r3`).
- **Correction:** docs give the 4B KV capacity as 92,432 tokens, from the 2026-10-23 probe. Every load run checked, from `first_real` to the wipe tests, logged 96,656 tokens, about 4.6 % more. The runs used the larger value. The reason for the difference is not known.

## 2026-11-01 · Tightening before the Stage 2 controls: cap, KV metric, preemptions, which load first
- **Cap stated:** `configs/stage2_cap_base.yaml` adds `--max-num-seqs 256`. `stage2_base.yaml` and `stage2_control.yaml` have been used, so they are not edited. Controls and wipes use the new base; `stage2_control_cap.yaml` replaces `stage2_control.yaml`, which never finished a run. No behaviour change is expected, because 256 is already the default (source).
- **What `vllm:kv_cache_usage_perc` counts (source, v0.32.0, `block_pool.py`):** usage is 1 − free blocks / total. `free_blocks` returns a block to the free queue when its ref count reaches 0, and cached blocks keep their hash there until reused. So usage counts blocks held by running requests, and saved prefixes with no running user count as free. The memory-limit conclusion stands.
- **Cross-check (`20261030-151441_sweep_pc_on_r10`):** 96,656 × 0.952 / 65 ≈ 1416 tokens per running request. Requests started in the window averaged a 1530-token prompt plus up to 128 output tokens, about 1594 with half the output. The implied value is about 11 % lower, in the direction expected from shared prefixes and partly filled requests, so it leaves no room for idle cache in that number.
- **λ = 3 is inside the danger zone.** `20261030-161749_sweep_pc_off_r3` did not keep up: throughput 0.969 λ, queue slope 0.013 (limit 0.01), percent fast 0.775. Percent fast per 150 s: 0.99, 0.98, 0.98, 0.97, 0.88, 0.30. **Correction:** I used its mean KV of 0.41 to suggest a cold server may not stay at the limit. That mean hid a collapse in progress; the last third averaged 0.77 and was still rising when the 900 s run ended.
- **Preemptions, deviation from the plan:** the plan's "few preemptions" (`experiment-plan.md`, showing the loop and done criteria) can't be a pass/fail rule, because preemptions appear wherever memory is the limit: 328 at λ = 10, 202 at λ = 5, 24 at λ = 3 with caching off. New rule, before any Stage 2 result: report preemptions per minute in the watch window, excluding the wipe's own, against the no-trigger control and the caching-off run at the same λ. **Cost:** a count no longer separates this loop from the Ao et al. limit cycle. That has to come from the traces, and from the protected-prefixes control if it can be built.
- **Prediction, untested, written before any matrix run.** C = 96,656. W = sum of the latest prompt over active sessions from the schedule (seeds 1, 2; t ≥ 600 s). The warm state holds if F_warm + W ≤ C; the cold state holds if F_cold + W > C.

| λ | W / C (p10–p90) | F_warm / C (mean; last third) | F_cold / C (mean; last third) | Warm fits | Cold holds |
|---|---|---|---|---|---|
| 2 | 0.49 (0.39–0.59) | 0.06; 0.07 | 0.11; 0.14 | Yes | No (0.60–0.63) |
| 2.5 | 0.62 (0.49–0.75) | no run | no run | Unknown | Unknown |
| 3 | 0.75 (0.61–0.89) | 0.13; 0.16 | 0.41; 0.77 | Yes (0.88–0.91) | Yes (1.16–1.52) |
| 3.5 | 0.87 (0.73–1.03) | no run | no run | Marginal, F_warm needed | Likely, F_cold needed |
| 4 | 1.01 (0.88–1.16) | 0.31; 0.35 | 0.87; 0.95 | No (1.32–1.36) | Yes |

- **Reading:** λ = 3 is the clearest test, so controls and wipes go 3, 3.5, 2.5, 4, 1.5. This changes run order only, not the verdict rule or the set of loads. λ = 2 should recover by this model.
- **Model limits:** the warm test is too strict, or wrong at λ = 4: that run was healthy for 900 s (percent fast 0.981, hit 0.525 against a ceiling of about 0.80). Even at λ = 3 the hit rate (0.661) is below the ceiling, though the model says everything fits, so prefixes are lost earlier than it implies. F and W overlap, because running requests hold part of their own prefix. Caching-off runs only approximate a cold cache, and they were still changing at 900 s. Means hide spikes.
- **Risk to the verdict rule:** `sweep_pc_on_r4` had percent fast 0.981 and a lowest 300 s of 0.959, so λ = 4 could come out `bad_baseline` under the 0.98 limit. The limit is not changed. If that happens, it's reported as such, and λ = 4 can't count as a healthy starting point.
- **KV gap, 92,432 vs 96,656:** the logs account for it. Available KV memory was 12.69 GiB against 13.27 GiB, and vLLM's measured peak activation was 1.17 GiB against 0.58 GiB, the same 0.58 GiB difference. Versions and utilization (0.92) match, and the non-default args differ only in `host` and `port`. Why peak activation differed is not known. Each run's own logged value is used.

## 2026-11-01 · "Stuck" redefined before any verdict was computed
No Stage 2 verdict has been computed under the first rule, and the only wipes so far are the two λ = 2 mechanics tests. This replaces the verdict section of the 2026-11-01 entry above. The plan's key word says "stuck" is percent fast staying low, and that is not enough, for the reasons below.

**Problems found**
- **A recovering server could be called stuck.** Under the first rule, a hit rate climbing alone, with a flat or growing line, fell through to `stuck`.
- **A hopeless queue could be called draining.** Slope −0.01 req/s² counted as draining; at 500 waiting that is about 14 h to empty.
- **The climb limit was inside noise.** On the healthy long run (`20261030-181851_long_run`), 34 % of adjacent 300 s windows rose by ≥ 0.02, and the p95 change was 0.076. For adjacent 600 s windows, the p95 change was 0.059.
- **Percent fast can't tell stuck from backlog.** It is counted by arrival with no timeouts, so it stays low until the line clears, even after the server has regained capacity. It shows the symptom, not the cause. Hit rate and the line's trend have to separate them.

**New run verdict** (`analysis/load.py`, `configs/stage2_cap_base.yaml`), judged on the last 600 s (`end`) against the 600 s before them (`previous`) and the baseline:
1. **bad_baseline:** baseline percent fast < 0.98.
2. **recovered:** percent fast ≥ baseline − 0.02, hit rate ≥ baseline − 0.06, mean waiting ≤ baseline + 1.
3. **slow_drain:** any one sign of recovery: hit rate up ≥ 0.06, or percent fast up ≥ 0.05, or the line shrinking fast enough to empty within 3600 s. These can be set off by noise, which only makes a `stuck` verdict harder to reach. That is the intended direction of error.
4. **stuck:** percent fast ≤ baseline − 0.10 and hit rate ≤ baseline − 0.06, with no sign of recovery.
5. **unclear:** anything else.

The hit-rate noise was measured at λ = 3 only; it may differ at other loads.

**A `stuck` verdict is not yet a metastable failure.** All of these must hold at one load, and the write-up must not use the term otherwise:
1. **Trigger over, same load:** by construction of the run.
2. **Control:** the no-trigger control at that λ is `recovered`.
3. **Repeats:** `stuck` in most seeds.
4. **Memory-limited loop, not just a queue:** at `end`, mean KV ≥ 0.80 (from `20261030-141658_sweep_pc_on_r5`, mean 0.82), mean N ≥ 2 × baseline, N below the cap of 256, and the traces follow the plan's order. A long queue with KV below this is a backlog state, not this loop, even if percent fast is low.
5. **Persistence:** a confirmation run with a 4500 s watch (3 × 1500 s) is also `stuck` by the same rule.
6. **Two states at one load:** in that same run, after the watch, λ drops to 1 req/s for 1800 s, then returns to the original λ for 1500 s. The last 600 s must be `recovered` against the original baseline, and the line must have reached 0 during the drop; if it did not, this item is inconclusive, not passed. A server that stays bad here has not shown two states; it may simply be broken or overloaded. About 2.4 h per run: wipe at 900 s, drop at 5400 s, back at 7200 s, end at 8700 s.

Items 5 and 6 cost GPU time only for loads that reach `stuck`. Their configs get written then, using these values.

**Limits that stay, to be reported with any result**
- **Open-loop turns.** Turns are sent on schedule even if the previous turn hasn't finished, while a real user waits for a reply. A slow server's real users would therefore send less, which could weaken or remove the loop. Sent before the previous turn's first token: 1.3 % at λ = 3, 1.5 % at λ = 4, 43 % at λ = 5 (caching on), and 62 % at λ = 4 (caching off). So any metastable result is only shown for this open-loop arrival pattern. CLAUDE.md rule 2 fixes this choice, so it is not changed here.
- **Where hits come from under pressure.** Mean cached share of the prompt, all later turns vs only those starting after the previous turn had finished: λ = 3, 0.667 vs 0.647; λ = 5, 0.438 vs 0.143; λ = 10, 0.240 vs 0.030. Under pressure, a finished turn's prefix is rarely still there, which fits the plan's eviction link, and most remaining hits depend on the previous turn still running. These come from overload, not from a wipe. The same split is reported for any stuck run.
- **A finite watch can't prove forever.** Persistence and two states are the strongest evidence these runs give.
- **Caching-off control needs rework for the burst stage.** At λ = 3, a caching-off server is already failing (percent fast 0.775, per the entry above), so it can't "get stuck" from a healthy start. The plan's done criterion needs a defined form before trigger 2. It does not block the cache-wipe matrix.

## 2026-11-02 · VM changes between runs: Tailscale on, automatic updates off; a second power-key shutdown
- **Tailscale** installed on the VM by the study owner, between runs: 100.83.53.50, `inference-vm.tail3b0112.ts.net`. Load runs stay on 127.0.0.1 inside the VM, so test traffic doesn't use it. The daemon is a new background process, unpinned; no effect on results is expected, and none has been measured. Runs up to the stopped control predate it; Stage 2 controls and wipes all come after it. vLLM still listens only on 127.0.0.1.
- **`unattended-upgrades`** disabled and inactive, so updates can't change the setup during the study.
- **Second shutdown:** the journal shows `Power key pressed short` at 15:41:07 UTC on 2026-11-01, followed by a clean power-off, the same signal as 2026-10-31 02:53:50 UTC. No run was active. The sender is not known, so unattended runs are not yet safe.

## 2026-11-02 · Shutdowns explained; Claude Code found on the VM
- **Shutdowns:** the study owner shares the GPU with someone else, and says shutdowns can happen because of that and need no further investigation. This replaces "the sender is not known" above; which person or action sent each signal was not confirmed. A shutdown costs the run in progress, which stays on record as unfinished and is rerun. A stopped sweep has no resume, so remaining loads are restarted by hand.
- **Check for shared use:** `server.log` records free GPU memory at startup, and `gpu.jsonl` records memory used. A run with another GPU user present could show less free memory; the existing checks do not test for this.
- **Claude Code on the VM:** installed 2026-11-01 18:11 UTC (file timestamps), one session at 18:19 UTC, after the last run. No measurement overlaps it. It must not run on the VM during a run, because all 8 cores are assigned and `env.json` would not record it. The study's Claude session runs on the Mac.

## 2026-11-02 · λ = 3 control invalid: one hardware thermal sample
- **Run:** `20261101-182452_stage2_control_cap_r3`, INVALID (`gpu_steady`). All other checks passed; 7017 of 7017 requests ok, percent fast 1.000.
- **Cause:** one sample of 2160, at t = 1558, had mask 0x68 (HW slowdown and HW thermal), at 83 °C and 408 W. The samples on either side had no hardware bit. The registered rule fails a run on any such sample, so the run does not count. The rule is not loosened.
- **Effect on the run:** none visible. TTFT p50 0.091 s in the 60 s before and 0.093 s in the 60 s after; max 0.444 s and 0.438 s. It is still not counted, and this is not a reason to use it.
- **Rerun:** `configs/stage2_control_cap_r3_rerun.yaml`, same settings and seed, after the sweep ends.
- **Thermal margin is the wider concern.** Valid runs also peak at 83 °C (`20261101-190602_stage2_control_cap_r3.5`, `20261101-131823_tau`), so this could recur at random. The SW thermal share has been higher in recent runs: 0.022–0.027 against 0.003 in `20261030-181851_long_run`. The wipe matrix pushes the GPU at least as hard. Changing the power limit would change capacity, so μ would need remeasuring; cooling is the option to try first.

## 2026-11-02 · No-trigger controls done
- **Verdicts, judged as if a wipe happened at t = 900 s (`verdict`, `configs/stage2_cap_base.yaml`):**

| λ | Run | Checks | Verdict | Baseline percent fast | Hit, baseline → end | Mean KV at end | Preemptions |
|---|---|---|---|---|---|---|---|
| 1.5 | `20261101-210915_stage2_control_cap_r1.5` | VALID | recovered | 1.000 | 0.792 → 0.791 | 0.04 | 0 |
| 2.5 | `20261101-194705_stage2_control_cap_r2.5` | VALID | recovered | 1.000 | 0.684 → 0.702 | 0.09 | 0 |
| 3 | `20261101-215502_stage2_control_cap_r3_rerun` | VALID | recovered | 1.000 | 0.608 → 0.607 | 0.15 | 0 |
| 3.5 | `20261101-190602_stage2_control_cap_r3.5` | VALID | recovered | 0.996 | 0.550 → 0.565 | 0.20 | 0 |
| 4 | `20261101-202808_stage2_control_cap_r4` | VALID | **bad_baseline** | 0.956 | 0.516 → 0.495 | 0.41 | 32 |

- **`20261101-182452_stage2_control_cap_r3`** stays INVALID and does not count. The rerun's baseline and end levels match it to within 0.001 on percent fast, hit rate and KV, so the same seed reproduces closely.
- **λ = 4:** by the registered rule, a stuck result there can't count as a metastable failure, because its control was not healthy. Percent fast per 300 s varied from 0.787 to 1.000 with no shock. The true steady limit looks a little below 4 over 2400 s, though μ_warm = 4 stands as measured by its rule over 900 s. Whether to keep λ = 4 in the matrix is the study owner's decision and is open.
- **Thermal:** `gpu_steady` passed on all five counted runs. Peak was 84 °C in the rerun; SW thermal share was 0.047 at λ = 4 against a limit of 0.05.

## 2026-11-02 · First `preempt` wipes at λ = 3: recovered; two of three runs invalid on heat
- **Runs, commit `f1ac598`, control `20261101-215502_stage2_control_cap_r3_rerun` (recovered):**

| Seed | Run | Checks | HW thermal samples | Preempted by the wipe | Verdict | Hit, baseline → end |
|---|---|---|---|---|---|---|
| 1 | `20261102-045827_wipe_preempt_r3_s1` | INVALID (`gpu_steady`) | 1 | 11 | recovered, not counted | 0.608 → 0.608 |
| 2 | `20261102-053935_wipe_preempt_r3_s2` | VALID | 0 | 1 | recovered | 0.624 → 0.640 |
| 3 | `20261102-062040_wipe_preempt_r3_s3` | INVALID (`gpu_steady`) | 2 | 6 | recovered, not counted | 0.652 → 0.677 |

- **Counted result: stuck in 0 of 1 valid run.** The matrix needs 3 valid seeds, so seeds 1 and 3 are rerun with their configs unchanged at new run ids.
- **What the wipe did (all three, the invalid two for description only):** hit rate in the first 15 s was 0.19–0.30, then 0.56–0.64 at 15–60 s, and near baseline by 120–300 s. Worst share within the SLO in any listed span was 0.975, at seed 1, 0–15 s. Peak waiting 9, mean N at most 13, KV peak 0.64, no preemptions after the wipe's own. No sign of the memory-limited loop.
- **Prediction check:** the F + W model said two states were possible at λ = 3. The valid run gives no sign of the cold state holding. One likely reason, untested: the cache refills within about a minute, while the caching-off run took about 10 minutes to collapse. So a single wipe may not hold the server cold long enough at this load. Three valid seeds are needed before this is the result.
- **Heat now blocks the matrix.** Hardware thermal samples invalidated 3 of the 9 runs since the controls began, 2 of them in the last 3, and the peak rose to 84 °C. SW thermal share reached 0.043 at seed 3. Reruns may fail the same way until cooling improves. The rule is not loosened.

## 2026-11-02 · λ = 3 reruns, and why runs fail on heat
- **Seed 1 rerun** `20261102-072216_wipe_preempt_r3_s1`: VALID, **recovered** (hit 0.608 → 0.608; 11 preempted by the wipe; first 15 s hit 0.191, the same as the invalid first attempt).
- **Seed 3 rerun** `20261102-080323_wipe_preempt_r3_s3`: INVALID (`gpu_steady`): 3 HW thermal samples in the window, SW thermal share 0.059 (limit 0.05). By the rule it would be `recovered`, but it is not counted. Seed 3 has now failed on heat twice; no further attempt until cooling changes.
- **λ = 3 result so far: stuck in 0 of 2 valid runs** (seeds 1, 2).
- **Cause of the heat failures (all INVALID runs since 2026-11-01):**
  - Every one was a short HW slowdown + HW thermal flag at a core temperature of 83–84 °C, far below the card's 95 °C slowdown point. Most likely another part of the card (likely memory) hits its limit; the driver does not report memory temperature, so this is not confirmed.
  - The wipe is not the cause: flags occurred before it, at t = 483 s and 696 s, and in a no-trigger control.
  - Load is not the cause: every run draws about 401–416 W at the 420 W cap, whatever λ is. Seed 3 sends fewer prompt tokens per second than seed 1 (4,224 vs 4,460).
  - Conditions got hotter: mean busy temperature was 74–79 °C on 2026-11-01 and 79–80 °C on 2026-11-02, with the peak 83 → 84 °C. Runs start from about the same idle temperature (44–50 °C).
  - The GPU fan is already at 97–100 % under load, so a fan-curve change cannot help. The levers are cooler air reaching the card, or a lower power limit (which would require remeasuring μ and the controls).

## 2026-11-02 · Seed 3, third attempt after a cooling change: stopped early
- **Run:** `20261102-093229_wipe_preempt_r3_s3`, started after the study owner changed the cooling. Over t = 240–1152 s it was cooler than the two earlier attempts (mean busy 78.6 °C against 80.1 and 80.6; SW thermal share 3.6 % against 4.2 and 5.3 %). It still had a HW thermal sample at t = 508 s, so it could not be valid.
- **Stopped on request at about t = 1618 s,** by interrupting the harness process. INVALID (`accounting`, `gpu_steady`, `arrival_rate`); it does not count.
- **When the flag fires:** in every flagged second across seeds 1–3, the core briefly peaked at 83–84 °C. Seed 2 had heavier arrivals at t = 483–508 s (41–46 per 10 s against 32) while staying at 80–82 °C, with no flag. So the flag follows temperature peaks, not request load, and the repeat at t = 508 s is seed 3's schedule running warm there. Peaks need to come down about 2–3 °C.
- **Options recorded, none chosen yet:** more cooling (no effect on the study); a lower power limit (reliable, but μ and the controls must be remeasured); or continue as is and accept reruns.

## 2026-11-02 · Fan on the GPU backplate; λ = 3 complete: stuck in 0 of 3
- **Cooling change:** the study owner added a fan on the back of the GPU. This is a change to the physical setup, not to the software or settings. Runs before it ran warmer: mean busy temperature 77.7 °C now, 79–80 °C before.
- **Seed 3, fourth attempt** `20261102-100744_wipe_preempt_r3_s3`: VALID. 0 HW thermal samples, SW thermal share 0.010, peak 82 °C, 90th percentile 80 °C. Over the same span (t = 240–725 s), the earlier attempts each had one HW sample. **Verdict recovered** (hit 0.652 → 0.677; 6 preempted by the wipe; first 15 s hit 0.295, back to 0.61 by 15–60 s; peak waiting 3, peak KV 0.36). Arrival-rate check passed (2.83 measured against 3.0).
- **λ = 3, `preempt` wipe: stuck in 0 of 3 valid runs** (`20261102-072216_wipe_preempt_r3_s1`, `20261102-053935_wipe_preempt_r3_s2`, `20261102-100744_wipe_preempt_r3_s3`). The seeds agree, so seeds 4 and 5 are not added. At λ = 3 a single wipe does not cause the failure. The cache refills within about 1–5 minutes, and N, waiting and KV stay far from the memory limit.
- **Comparability:** seeds 1 and 2 ran before the backplate fan, and seed 3 ran with it. All three recovered, so the cooling change doesn't alter the λ = 3 verdict. From here on, all runs use the new cooling.

## 2026-11-02 · λ = 3.5 `preempt` wipes: stuck in 0 of 3
- **Runs, commit `944f0ee`, all VALID, no HW thermal samples (SW thermal share 0.008–0.025, peak 83 °C). Control `20261101-190602_stage2_control_cap_r3.5`: recovered.**

| Seed | Run | Preempted by the wipe | Verdict | Hit, baseline → end | End: mean KV, N, waiting |
|---|---|---|---|---|---|
| 1 | `20261102-110200_wipe_preempt_r3.5_s1` | 8 | recovered | 0.550 → 0.565 | 0.20, 13.2, 0.02 |
| 2 | `20261102-114305_wipe_preempt_r3.5_s2` | 4 | recovered | 0.542 → 0.578 | 0.16, 10.6, 0.01 |
| 3 | `20261102-122411_wipe_preempt_r3.5_s3` | 15 | recovered | 0.575 → 0.612 | 0.15, 9.4, 0.00 |

- **Wipe effect:** first-minute hit 0.49–0.53, back at baseline within about 5 minutes. Worst share within the SLO in any listed span was 0.944, at seed 3, 0–60 s. Peak waiting after a wipe was 9. Mean KV stayed at or below 0.25 in every listed span. Seed 3 touched KV 0.98 once at 600–900 s after the wipe, with N up to 78, and returned without a queue; its baseline also peaked at 0.64 with no wipe.
- **So far, the cache wipe does not cause the failure at any valid load tested:** λ = 3 and 3.5, 0 of 6 runs stuck.

## 2026-11-02 · Cache-wipe matrix stopped early; trigger 2, the load burst, registered before any burst run
- **Deviation, study owner's decision:** the registered wipe matrix is not finished. λ = 2.5 and 1.5 `preempt` wipes and the λ = 3 `idle` comparison are not run, and λ = 4 is dropped (`bad_baseline` control). Reason: 0 of 6 stuck at the two loads closest to capacity; the lower loads have more spare capacity. So the cache-wipe result is stated for λ = 3 and 3.5 only. With no stuck result, the `preempt` vs `idle` comparison has nothing to explain.
- **Burst design** (`harness/workload.py`, `trigger.kind: burst`): extra one-off requests, Poisson at `rate` for `duration_s` from `at_s`, each with a fresh random prompt of `prompt_tokens` tokens and 128 output tokens. They come from their own random generator, so the session schedule matches the same-seed run without a burst (tested). Requests sent on schedule; the `trigger` check confirms every burst request was sent.
  - **Why one-off requests, not extra sessions:** extra sessions would keep sending later turns for minutes after the burst, so the shock wouldn't end at a known time. One-off requests stop at `at_s + duration_s`.
  - **What the burst does:** it adds a backlog and fills KV with prompts that will never be reused, which evicts the sessions' cached prefixes. So it is a load shock and a cache shock together, closer to a real spike than the wipe.
- **Size, before any run:** +3 req/s for 120 s, 1408-token prompts (the session median), from t = 900 s. At λ = 3 that is 6 req/s, 1.5 × μ_warm, for 2 minutes, about 360 extra requests and about 500k prompt tokens, more than 5 × the 96,656-token KV capacity. Chosen to be clearly bigger than anything the wipe did. If it gives a clear answer, other sizes come later, each registered first.
- **Matrix:** λ = 3 and 3.5 (healthy controls), seeds 1–3, run in that order (`configs/burst_r*_s*.yaml`), about 4.4 h. Verdict rule unchanged, judged from the end of the burst (t = 1020 s), so runs are 2520 s long. Baseline 420–1020 s includes the burst's last 120 s. Burst requests are part of the baseline's percent fast, which makes `bad_baseline` more likely, not less. That is the conservative direction, and it is noted in case it happens.
- **Controls:** the existing no-trigger controls (2400 s, judged at 900 s) are reused. Two mismatches: they end before t = 2520 s, and because the run length changes the random draw, the burst runs' sessions are a different random schedule from the controls', not the same one plus a burst. The "same sessions" property holds only against a same-length run without a burst. Both controls were healthy throughout, so this is not expected to matter. If a burst run comes out `stuck`, a matching 2520 s no-burst control is run before it can count.
- **Not yet defined:** the plan's caching-off burst control. At λ = 3 a caching-off server is already failing, so it needs a lower load or another form. It is needed before any stuck burst result could count.

## 2026-11-02 · Correction after seeing results: the baseline must end where the trigger starts
- **The error:** the verdict took the baseline as the 600 s before the *end* of the trigger. For a burst (900–1020 s) that put the burst itself into the baseline, so baseline percent fast was 0.68–0.70 and every burst run was certain to be `bad_baseline`. The entry above said this made `bad_baseline` "more likely"; it made it certain. It was a mistake in the window, not a threshold choice.
- **Seen before the fix:** the three λ = 3 burst runs, all `bad_baseline` under the rule as registered (`20261102-131353_burst_r3_s1`, `20261102-135701_burst_r3_s2`, `20261102-144008_burst_r3_s3`).
- **Fix, approved by the study owner:** the baseline is the 600 s before the trigger *starts*; the watch still runs from its end (`analysis/load.py`, `verdict`). No threshold changes. For a wipe, start and end are 0.01–0.15 s apart, and every wipe and control verdict is unchanged (rechecked).
- **λ = 3 bursts under the fixed rule:** all **recovered**, so stuck in 0 of 3. Baseline percent fast 1.000 in all; end percent fast 0.999–1.000, hit 0.612–0.667 against baselines 0.616–0.629, waiting about 0.
- **What each burst did:** KV reached 1.00, mean N 62–73, waiting peaked at 178–237, hit fell to 0.17–0.35, and percent fast fell to 0–8 % during the burst and the minute after. The server cleared it within about 5 minutes after the burst ended.

## 2026-11-02 · λ = 3.5 bursts: stuck in 0 of 3; burst total 0 of 6
- **Runs, commit `f0a70b3`, all VALID, every burst request sent, 0 HW thermal samples (SW thermal share 0.002–0.004):** `20261102-152316_burst_r3.5_s1`, `20261102-160625_burst_r3.5_s2`, `20261102-164933_burst_r3.5_s3`. All **recovered** (fixed baseline rule): baseline percent fast 0.999–1.000, end 1.000; hit 0.563 → 0.541, 0.553 → 0.564, 0.581 → 0.624; end waiting about 0.
- **Compared with λ = 3:** a bigger backlog (peak waiting 256–327 against 178–237), slower clearing (percent fast 0.36–0.64 at 60–300 s after, against 0.65–0.91), and more preemptions there (57–111 against 15–53). All back to baseline by 300–600 s after the burst.
- **Status of the burst result (see the next entry for what follows):** +3 req/s for 120 s, at λ = 3 and 3.5, stuck in 0 of 6. With the wipe (0 of 6), no shock tried so far gives a stuck run at a healthy load on this setup: Qwen3-4B, one RTX 3090, 96,656-token KV cache, 8-turn sessions.

## 2026-11-02 · Next: a smaller KV pool; λ = 4 dropped (study owner's decisions)
- **λ = 4 is dropped** from Stage 2 at the default pool. Its no-trigger control was `bad_baseline`, so no result there could count.
- **Why shrink the pool:** in all 12 shock runs the server recovered because it had spare memory. During each burst, KV filled to 1.00 and hits fell to 0.17–0.35, but once the extra load stopped, the backlog cleared and the cache refilled. The plan's prescribed lever is a smaller pool: "big enough to hold the cached sessions beside the normal running batch, but not beside the bigger batch that forms after a cache loss". It is reported as a deliberate setting, with the ratio of pool size to the sessions' cached context.
- **Size, registered before any run: 72,480 tokens** (`--kv-cache-memory-bytes 10687610880`; 4530 blocks × 16 tokens × 147,456 bytes per token, from Qwen3-4B's config: 36 layers, 8 KV heads, head dim 128, bf16). That is 0.75 of the 96,656-token default. A fixed byte size also removes the startup variation behind 92,432 vs 96,656 tokens.
- **Reasoning, using the F + W model from the 2026-11-01 entry, with the new pool C':**
  - λ = 2: W + F_warm ≈ 47.6k + 6.4k = 54k ≤ C'; W + F_cold ≈ 59–61k < C'. The cold state cannot hold, so it recovers.
  - λ = 2.5: W + F_warm ≈ 59.7k + 8.7k = 68k ≤ C'. F_cold is unmeasured; if it is above about 13k, the cold state holds there. **Predicted new danger zone: around λ = 2.5.**
  - λ = 3: W + F_warm ≈ 86k > C', so the warm state is predicted not to fit; λ = 3 may no longer be healthy.
  - **This model has already been wrong once:** it predicted two states at λ = 3 at the default pool, and none appeared in 12 shock runs. So the prediction is a guide to where to look, not a claim. The sweeps decide.
- **Pool-to-context ratio:** 72,480 / W. That is 1.21 at λ = 2.5 (W ≈ 59.7k) and 0.99 at λ = 3 (W ≈ 73.0k). The default pool was 1.62 and 1.32.
- **Step 1, the capacity sweeps at the new pool:** `configs/sweep_kv72k_pc_on.yaml` (λ = 1, 1.5, 2, 2.5, 3, 3.5, 4, 5) and `configs/sweep_kv72k_pc_off.yaml` (λ = 1, 1.5, 2, 2.5, 3, 3.5, 4). Same run shape as Stage 1: 900 s, seed 0, no dev mode, cap 256 stated. Capacity rule unchanged: valid run, throughput ≥ 0.95 λ, waiting slope ≤ 0.01 req/s². About 5 h.
- **Then:** fix μ_warm and μ_off at this pool; pick loads inside the new zone; run no-trigger controls (2400 s); then wipes and bursts, each registered before running. If μ_warm and μ_off come out nearly equal, or the zone is empty, that is recorded and the size is reconsidered.

## 2026-11-02 · Capacity at the 72,480-token pool
- **Runs, commit `cfc18da`, all 15 VALID, 0 HW thermal samples:** `20261102-175648_sweep_kv72k_pc_on_r1` … `20261102-194816_sweep_kv72k_pc_on_r5`, and `20261102-200547_sweep_kv72k_pc_off_r1` … `20261102-214207_sweep_kv72k_pc_off_r4`. The server log confirms `GPU KV cache size: 72,480 tokens`.
- **Rule as registered** (throughput ≥ 0.95 λ, waiting slope ≤ 0.01 req/s²):

| λ | On: keeps up | On: hit | On: percent fast | Off: keeps up | Off: percent fast |
|---|---|---|---|---|---|
| 1 | yes | 0.727 | 1.000 | yes | 1.000 |
| 1.5 | yes | 0.711 | 1.000 | yes | 1.000 |
| 2 | yes | 0.658 | 1.000 | yes | 0.995 |
| 2.5 | yes | 0.574 | 1.000 | yes | 0.969 |
| 3 | yes | 0.511 | 0.999 | **no** (slope 0.021) | 0.715 |
| 3.5 | yes | 0.462 | 0.994 | no | 0.318 |
| 4 | yes | 0.397 | **0.883** | no | 0.116 |
| 5 | **no** | 0.301 | 0.151 | — | — |

- **μ_warm = 4, μ_off = 2.5 req/s at this pool.** The danger zone is 2.5 < λ < 4.
  - λ = 4 is like before: it keeps up by the rule but is not healthy (percent fast 0.883; 0.66 in one 150 s span).
  - The caching-off λ = 2.5 run was sliding at the end (percent fast per 150 s: 1.00, 0.99, 0.99, 0.98, 0.91), so μ_off may be lower over longer runs.
- **Compared with the default pool:** hit rate is 0.10–0.15 lower at the same load (λ = 2: 0.658 vs 0.767; λ = 3: 0.511 vs 0.661; λ = 4: 0.397 vs 0.525). μ_warm is unchanged at 4. μ_off = 2.5 here is not comparable to the old μ_off = 2, because 2.5 was not in the old grid.
  - **The registered prediction was wrong for λ = 3:** it said the warm state would not fit there, but λ = 3 is healthy (percent fast 0.999, hit 0.511). The prediction "danger zone around λ = 2.5" does not hold either: λ = 2.5 is at μ_off, at the low edge.
- **Loads for the next step:** λ = 3 and 3.5, the healthy loads inside the zone. λ = 4 is excluded as before.
- **Next, started now:** no-trigger controls at λ = 3 and 3.5 (`configs/stage2_control_kv72k.yaml`; 2400 s, seed 1, dev mode, same verdict rule). Then wipes and bursts at these loads, each registered before running.

## 2026-11-02 · Controls at the 72,480-token pool; shocks registered at λ = 3
- **Controls, commit `acd3051`, both VALID, 0 HW thermal samples:**
  - `20261102-221019_stage2_control_kv72k_r3`: **recovered** (baseline percent fast 1.000, hit 0.500; end 0.998, 0.487). Percent fast per 300 s never below 0.998.
  - `20261102-225146_stage2_control_kv72k_r3.5`: **bad_baseline** (baseline percent fast 0.951; one 300 s span at 0.912 with no shock; 13 preemptions). So at this pool λ = 3.5 is not steadily healthy, and a stuck result there could not count.
- **Only λ = 3 is usable at this pool.**
- **Shocks at λ = 3, registered before running, the same as at the default pool so the two pools compare directly:**
  - Burst: +3 req/s of 1408-token one-off requests for 120 s from t = 900 s; 2520 s runs (`configs/burst_kv72k_r3_s1..3.yaml`).
  - Wipe: `preempt` at t = 900 s; 2400 s runs (`configs/wipe_kv72k_r3_s1..3.yaml`).
  - Seeds 1–3 each, bursts first. Same verdict rule. About 4.3 h.
- **The control mismatch for bursts, as before:** the burst runs are 2520 s against the 2400 s control. A stuck burst result needs a matching 2520 s no-burst control before it counts.

## 2026-11-03 · Shocks at the 72,480-token pool, λ = 3: stuck in 0 of 6
- **Runs, commit `c964f49`, all VALID, 0 HW thermal samples, all recovered:**

| Run | Verdict | Baseline percent fast / hit | End percent fast / hit |
|---|---|---|---|
| `20261102-234257_burst_kv72k_r3_s1` | recovered | 0.999 / 0.502 | 0.997 / 0.506 |
| `20261103-002556_burst_kv72k_r3_s2` | recovered | 1.000 / 0.496 | 1.000 / 0.514 |
| `20261103-010856_burst_kv72k_r3_s3` | recovered | 1.000 / 0.510 | 0.998 / 0.560 |
| `20261103-015156_wipe_kv72k_r3_s1` | recovered | 0.999 / 0.500 | 0.998 / 0.487 |
| `20261103-023254_wipe_kv72k_r3_s2` | recovered | 0.997 / 0.503 | 1.000 / 0.520 |
| `20261103-031353_wipe_kv72k_r3_s3` | recovered | 1.000 / 0.543 | 1.000 / 0.562 |

- **Bursts against the default pool at λ = 3:** mean N during the burst was about 45–52 against 62–73, since fewer requests fit in less memory. Hit fell to 0.11–0.28 against 0.17–0.35. Peak waiting was 187–254 against 178–237. Clearing took about the same time: percent fast 0.54–0.85 at 60–300 s after, and back to baseline by 300–600 s.
- **Wipes:** the lowest percent fast after a wipe was 0.995; the hit dip was small (to 0.43 at most) and gone within about 5 minutes.
- **Result: a 25 % smaller KV pool does not produce the failure at λ = 3.** Over both pools and both triggers: stuck in 0 of 18 valid shock runs at healthy loads. At this pool, λ = 3.5 is not usable (`bad_baseline` control).

## 2026-11-03 · Up-then-down ramp, registered before running (study owner's decision)
- **Why:** after 0 of 18 stuck shock runs, the ramp is the plan's other test for two states at one load, and it needs no trigger. Load rises in steps past μ_warm, then falls back. A metastable server stays slow on the way down at loads where it was healthy on the way up.
- **Runs:** default KV pool (`stage2_cap_base.yaml`: cap 256, dev mode, seed 1). Levels 2 → 2.5 → 3 → 3.5 → 4 → 4.5 → 5 → 4.5 → … → 2 req/s, 13 steps.
  - `configs/ramp_d300.yaml`: 300 s per step, 3900 s.
  - `configs/ramp_d600.yaml`: 600 s per step, 7800 s. The plan requires a second, longer dwell to tell lag from a real gap.
  - About 3.5 h together.
- **Measure** (`analysis/load.py`, `ramp_table`): each step is judged over its second half (`ramp.settle_frac: 0.5`) for percent fast, hit rate, waiting, N and KV. Session arrivals take about 140 s to follow a step, so half of a 300 s step is the shortest usable window.
- **Gap rule, at each load visited both ways:** a gap if the down step has percent fast ≤ up − 0.10 and hit ≤ up − 0.06 (the stuck thresholds). It counts only at loads that were healthy going up (up percent fast ≥ 0.98). With the controls, that is λ ≤ 3.5.
- **Reading:**
  - A gap at both dwells, at the same load: evidence for two states at that load (C1).
  - A gap at 300 s only: lag. The backlog from the overloaded peak (λ = 4.5–5) hasn't cleared yet. This is expected, because a burst's backlog took about 5 minutes to clear at λ = 3.
  - No gap: no hysteresis on this setup.
- **Caveat stated in advance:** at the peak, λ = 5 is overload (`20261030-141658_sweep_pc_on_r5`). The backlog it leaves, with no timeouts, can take a long time to clear on the way down. That lag is exactly what the second dwell is for.

## 2026-11-03 · Ramp result: no gap at either dwell
- **Runs, commit `a16d4e2`, both VALID, all requests ok, 0 HW thermal samples:** `20261103-043121_ramp_d300` (13,021 requests; peak 82 °C) and `20261103-053730_ramp_d600` (25,989 requests; peak 84 °C).
- **Step table (second half of each step), percent fast / hit:**

| λ | 300 s up | 300 s down | 600 s up | 600 s down |
|---|---|---|---|---|
| 2 | 1.000 / 0.759 | 1.000 / 0.757 | 1.000 / 0.756 | 1.000 / 0.750 |
| 2.5 | 1.000 / 0.646 | 1.000 / 0.613 | 1.000 / 0.722 | 1.000 / 0.740 |
| 3 | 1.000 / 0.608 | 1.000 / 0.680 | 1.000 / 0.606 | 1.000 / 0.660 |
| 3.5 | 1.000 / 0.562 | 1.000 / 0.619 | 1.000 / 0.645 | 1.000 / 0.613 |
| 4 | 1.000 / 0.521 | 0.998 / 0.501 | 0.984 / 0.543 | 0.998 / 0.524 |
| 4.5 | 0.989 / 0.472 | 0.526 / 0.501 | 0.624 / 0.464 | 0.174 / 0.466 |
| 5 (peak) | 0.000 / 0.419 | — | 0.089 / 0.407 | — |

- **Gap rule:** no gap at any load judged, at either dwell.
  - At λ = 4.5 down (300 s), percent fast was 0.526, but hit didn't fall, so it is not a gap. It is the peak's backlog clearing (waiting 6.9), and the next step down was healthy.
  - At 600 s, λ = 4.5 was not healthy going up (0.624), so it isn't judged.
- **Reading:** on this setup the server returns to the same state on the way down as on the way up, one step below the peak. The hit rate on the way down is equal to or higher than on the way up at λ ≤ 3.5. There is no evidence of two states at one load (C1).
- **Stage 2 evidence so far, default pool unless stated:** cache wipe 0 of 6 stuck; load burst 0 of 6; smaller 72,480-token pool, wipe and burst at λ = 3, 0 of 6; up-then-down ramp at 300 s and 600 s dwell, no gap. Untested: triggers 3–5 (power cap, engine restart, popularity shift), bigger bursts, the ramp at the smaller pool, and other workloads (turn gap, session length, model size).

## 2026-11-03 · Shorter turn gaps (5 s), registered before running (study owner's decision)
- **Question (plan, Stage 2 open questions):** "Does turn spacing matter? If sessions come back very quickly, their prefixes may survive even a big batch. Try at least two turn gaps." This is the second gap value; all runs so far used a mean of 20 s.
- **Correction to my own recommendation:** I suggested shorter gaps as the most promising change, saying they make cached prefixes more valuable. The plan's reasoning points the other way, and the working set confirms it. With 5 s gaps, active sessions' latest prompts total about 18.7k tokens at λ = 3 (0.19 of the 96,656-token pool), against 74.8k (0.77) at 20 s (schedule, seed 1). Prefixes are reused sooner and need far less room. **Prediction: getting stuck is less likely at 5 s gaps.** The cache is worth more (a higher hit rate, so a higher μ_warm), but it is much harder to crowd out. If this holds, longer gaps (for example 60 s) are the direction where the eviction link has a better chance.
- **Step 1, capacity at 5 s gaps:** `configs/gap5_base.yaml` (default pool, cap 256 stated, no dev mode), `configs/sweep_gap5_pc_on.yaml` (λ = 2, 3, 3.5, 4, 4.5, 5, 6, 7), `configs/sweep_gap5_pc_off.yaml` (λ = 2, 2.5, 3, 3.5). 900 s runs, seed 0, same capacity rule as Stage 1. About 3.4 h.
- **Then:** fix μ_warm and μ_off at 5 s gaps; choose healthy loads in the zone; controls; then the same burst and wipe as before, each registered before running.

## 2026-11-03 · Capacity with 5 s turn gaps
- **Runs, commit `92ce617`, all 12 VALID, 0 HW thermal samples:** `20261103-113130_sweep_gap5_pc_on_r2` … `20261103-132357_sweep_gap5_pc_on_r7`, and `20261103-134015_sweep_gap5_pc_off_r2` … `20261103-142848_sweep_gap5_pc_off_r3.5`.
- **μ_warm = 6, μ_off = 2.5 req/s** by the registered rule.
  - Cache on: hit rate 0.76–0.79 at every load from 2 to 6 (the ceiling is about 0.80). Percent fast is 1.000 up to λ = 4.5, 0.977 at 5 and 0.899 at 6. Mean KV was only 0.55 at λ = 6. At λ = 7 the server fell behind (slope 0.077), with KV 0.94 and hit still 0.757.
  - Cache off: as at 20 s gaps. λ = 2.5 passes but slides at the end (last 150 s percent fast 0.85).
- **Against 20 s gaps:** the cache is worth far more (hit at λ = 4: 0.786 vs 0.525; μ_warm 6 vs 4). Under overload, cached prefixes survive (hit 0.757 at λ = 7 against about 0.42 at λ = 5 with 20 s gaps). This supports the registered prediction that crowding out the cache is harder here. The danger zone is wider (2.5 < λ < 6), but memory pressure inside it is low.
- **Loads for the next step:** λ = 3.5 and 4.5, inside the zone and healthy (percent fast 1.000). λ = 5 and 6 are below 0.98, so like λ = 4 at 20 s gaps they could not count.
- **Next, started now:** no-trigger controls at λ = 3.5 and 4.5 (`configs/stage2_control_gap5.yaml`; 2400 s, seed 1, dev mode). Then the same burst and wipe, registered before running.

## 2026-11-03 · 5 s-gap controls healthy; shocks registered at λ = 3.5 and 4.5
- **Controls, commit `49ba3df`, both VALID, 0 HW thermal samples, both recovered:**
  - `20261103-145356_stage2_control_gap5_r3.5`: percent fast 1.000 in every 300 s span; hit 0.799–0.805; KV 0.10–0.14.
  - `20261103-153502_stage2_control_gap5_r4.5`: baseline percent fast 1.000, hit 0.799, KV 0.20; end 1.000, 0.801, 0.21.
- **Shocks, registered before running, the same as at 20 s gaps:**
  - Burst: +3 req/s, 1408-token one-off requests for 120 s from t = 900 s, 2520 s runs.
  - Wipe: `preempt` at t = 900 s, 2400 s runs.
  - λ = 4.5 then 3.5, seeds 1–3: bursts at both loads first, then wipes (`configs/burst_gap5_r*_s*.yaml`, `configs/wipe_gap5_r*_s*.yaml`). 12 runs, about 9 h, about 2 GB of disk (7.7 GB free).
  - At λ = 4.5 the burst brings the total to 7.5 req/s, above μ_warm = 6.
- **Prediction (from the sweeps):** recovery, because cached prefixes survived even overload at 5 s gaps. The burst runs keep the same 2520 s vs 2400 s control mismatch as before.

## 2026-11-04 · 5 s-gap shocks: stuck in 0 of 12
- **Runs, commit `79d3fcc`, all 12 VALID, 0 HW thermal samples, all recovered:** bursts `20261103-161947_burst_gap5_r4.5_s1` … `20261103-195529_burst_gap5_r3.5_s3`; wipes `20261103-203837_wipe_gap5_r4.5_s1` … `20261104-000416_wipe_gap5_r3.5_s3`.
- **Bursts:** KV reached 1.00 and waiting peaked at 181–372 (372 at λ = 4.5, seed 1). Percent fast 60–300 s after the burst was 0.66–0.90 at λ = 4.5 and 0.86–1.00 at λ = 3.5. Every run was back to baseline at the end (percent fast 1.000; hit 0.800–0.802 against 0.801–0.804 before).
- **Wipes:** percent fast was 1.000 from 60 s after the wipe in every run; waiting peaked at 3–28.
- **As predicted:** with 5 s gaps the cache barely matters for recovery. Prefixes return before they can be evicted, so the server refills almost at once.
- **Stage 2 total: stuck in 0 of 30 valid shock runs at healthy loads, plus no ramp gap.** This covers two triggers, two KV pool sizes, two turn gaps (5 s and 20 s) and two ramp dwells.

## 2026-11-04 · VM run copies removed after a verified copy to the Mac (study owner's decision)
- **Why:** the VM had 6.1 GB free, too little for another round of runs.
- **Check before removal:** all 104 run folders (1,054 files, 9,942,117,131 bytes) were copied to `runs/` on the Mac and compared by checksum against the VM: 0 differences.
- **Removal:** `rsync -a -c --remove-source-files` from the VM to the Mac. A VM file is removed only after rsync confirms an identical copy on the Mac; empty folders are removed after. Nothing on the Mac was changed or deleted.
- **Effect on rule 4 (raw data immutable):** the data is unchanged, but **the Mac now holds the only copy** of every run. `runs/` is not in git. A second copy (external drive or cloud) is recommended, and not yet made. New runs still land on the VM and are copied to the Mac after each round, as before.

## 2026-11-04 · Documentation audit, changes 1–9 (study owner's request)
The nine entries below come from a read-only audit of the repo, done before any edit. No run, verdict, threshold, config or file in `runs/` was changed. `analysis/load.py` and `verdict` are untouched.

## 2026-11-04 · (1) CLAUDE.md now states PROTOCOL's precedence rule
- **Before:** `CLAUDE.md` line 3, "The source of truth is `docs/experiment-plan.md`." That conflicted with `PROTOCOL.md:3`, "Where they differ, the newer decisions.md entry rules."
- **Now:** "`docs/experiment-plan.md` is the source of truth for intent and `docs/decisions.md` is the append-only log of every change; where they differ, the newer decisions.md entry rules (`PROTOCOL.md`)."
- **Effect:** none on any result. Every deviation from the plan was already logged here, and PROTOCOL §6 lists them.

## 2026-11-04 · (2) PROTOCOL §4 corrected: dev mode was not on in all Stage 2 runs
- **Error:** PROTOCOL §4 said "Dev mode (`VLLM_SERVER_DEV_MODE=1`) in all Stage 2 runs." The saved `config.yaml` of every run folder (`server.env`) shows otherwise.
- **Dev mode on, 49 runs:**
  - every wipe (`wipe_preempt_*`, `wipe_kv72k_*`, `wipe_gap5_*`, including the invalid attempts);
  - every burst (`burst_*`);
  - every no-trigger control (`stage2_control*`, including the stopped `20261101-151707_stage2_control_r1.5`);
  - both wipe tests and both ramps.
- **Dev mode off, 55 runs:**
  - all capacity sweeps: Stage 1 (`sweep_pc_on/off`) and both Stage 2 setups (`sweep_kv72k_pc_on/off`, 15 runs; `sweep_gap5_pc_on/off`, 12 runs);
  - both τ runs (`20261031-025032_tau`, `20261101-131823_tau`);
  - the recorder-off runs, smoke, first_real, repeat and long_run.
- **Consequence, already implied by decisions 2026-10-31 ("controls are compared within Stage 2 only"):** in every setup, μ_warm and μ_off were measured without dev mode, and the test loads' controls and shocks ran with it. The effect of dev mode on speed has not been measured. Verdicts compare a shock with its control, and both had dev mode on, so no verdict is affected. A capacity value would be affected only if dev mode changed speed.
- PROTOCOL §4 now lists both groups.

## 2026-11-04 · (3) PROTOCOL §3 item 6 restated as registered
- **Before:** "drop to λ = 1 until the queue empties, return to λ, and the server comes back `recovered`." That is not what the 2026-11-01 entry registered ("Stuck" redefined, item 6): a fixed 1800 s drop.
- **Now, quoting that entry:** "in that same run, after the watch, λ drops to 1 req/s for 1800 s, then returns to the original λ for 1500 s. The last 600 s must be `recovered` against the original baseline, and the line must have reached 0 during the drop; if it did not, this item is inconclusive, not passed."
- **Effect:** none. No run has reached item 6.

## 2026-11-04 · (4) docs/definitions.md created
- One entry per term: percent fast, goodput, throughput, μ_warm, μ_off, danger zone, τ, K, watch window, baseline window, h, KV usage, N, Q, preemption, R, the five verdicts, metastable failure and trigger end. Plus W, F, the cached-share split and the overlap fraction, now that they have code (entry 6).
- Each entry has one text definition (the newer decisions.md entry where texts differ, by the precedence rule), its file:line, and the code function. Other wordings are listed, not removed.
- **Marked as having more than one computation, with none chosen yet:**
  - **percent fast:** per 1 s bin in `percent_fast`, pooled over a window in `_level`;
  - **hit rate:** mean of per-scrape ratios in `summarize`, counter ratio in `_level`/`hit_between`, first-to-last in `whole_run_hit_rate`;
  - **trigger end:** the same rule in `verdict` and in `derived.trigger_times`.
- **No code exists** for R, K, danger zone, metastable failure, or the registered preemption comparison.
- **Hit-rate values that differ between entries for the same runs are the different computations (checked):**
  - The 2026-10-30 step 4 follow-up gives λ = 2 / 3 / 4 as 0.73 / 0.63 / 0.49. That is `summarize` (the mean of per-scrape ratios over the window): 0.732 / 0.627 / 0.490.
  - The 2026-11-02 72k comparison gives 0.767 / 0.661 / 0.525 for the same default-pool runs (`sweep_pc_on_r2/r3/r4`). That is `whole_run_hit_rate` (first scrape to last, warm-up and drain included): 0.767 / 0.661 / 0.525.
  - Counter hit over the measured window gives a third set: 0.765 / 0.644 / 0.510.
  - **Mixed computations in two published comparisons (checked):**
    - The 72k pool's own values in the 2026-11-02 capacity table (λ = 2 / 3 / 4: 0.658 / 0.511 / 0.397) are `summarize` means of ratios. They were compared with whole-run values at the default pool. Like for like, the 72k pool is **0.07–0.12 lower**, not "0.10–0.15 lower":
      - mean of ratios: 0.658 vs 0.732, 0.511 vs 0.627, 0.397 vs 0.490;
      - whole run: 0.698 vs 0.767, 0.552 vs 0.661, 0.430 vs 0.525.
    - The 5 s-gap comparison (2026-11-03, "hit at λ = 4: 0.786 vs 0.525", and open-questions S6, "0.79 vs 0.53") has the same mix. Like for like it is 0.786 vs 0.490 (mean of ratios) or 0.800 vs 0.525 (whole run).
  - **Direction:** both conclusions keep their direction: a smaller pool lowers the hit rate, and 5 s gaps raise it. Only the sizes quoted change. The old entries stay as written. `open-questions.md` S6 is left as is, and this entry supersedes its numbers.

## 2026-11-04 · (5) Source questions S8–S11: hit-counter units, eviction order, preempted blocks, self-refill
- **Why:** these had been used as beliefs (audit, section 13) with no evidence. Rule 9 allows only probe output, the pinned source or a run id. They are now open items in `docs/open-questions.md`, answered from the vLLM v0.32.0 source only: the GitHub tag tarball, sha256 `bf592c132f27bbb5f65cff0bbd2ee873eae722b79c8286934fd5b5cf88b43d61`. It has not yet been diffed against the wheel installed on the VM.
- **S8, hit counters:** they count tokens, once per admission. **Readmissions of preempted requests are excluded** (they go to `preempted_*`, which is not exported).
  - Consequence for the `preempt` wipe: the requests it preempts start over, and their re-prefill does not appear in h.
  - So the post-wipe hit dips in this log describe new turns only. The dips are not changed by this. Their meaning is narrower than "all prefill".
- **S9, eviction:** approximately LRU by release time. Within one freed request, its tail blocks are evicted before its head blocks. So a session's shared beginning survives longest.
  - This fits the plan's link 5 as written: a session's newest blocks go first.
- **S10, preempted blocks:** they stay cached as eviction candidates until reused. The exception is the `preempt` wipe, which clears every hash right after the preemption.
- **S11, self-refill:** blocks are committed to the cache as they are computed. A missed turn therefore re-caches its own prompt at once, and the generated output's full blocks are cached too. With recorded replies, the output blocks never match a later turn.
  - INFERRED, not tested: this is one plausible reason the wipe never held. A wipe costs each session about one turn; for the loss to persist, eviction must happen within a turn gap. This is a hypothesis for the negative-result write-up, not a finding.

## 2026-11-04 · (6) Derived figures moved into analysis/ and recomputed
- **The original code was never committed.** The W, F, cached-share-split and per-span hit figures in earlier entries were computed by scripts that are not in the repo.
- **New code:** `analysis/derived.py`, with `working_set`, `kv_footprint`, `cached_share_split`, `overlap_fraction`, `hit_between`, `span_hits`, `thirds`, `span_hit_spread`, `adjacent_change` and `trigger_times`, tested in `tests/test_derived.py`. `analysis/recompute_published.py` makes 104 comparisons with published values (some are alternative readings of the same value) and prints them side by side: 79 agree to the published rounding, 25 do not, and they are summarized below.
- **These are reconstructions.** Each function is the reading of the entry's text that reproduces the published numbers. A match shows the reading is consistent with the text, not that it is the original code.
- **Readings fixed by the data** (the text alone was ambiguous):
  - **W:** a session is active from its first planned turn to its last planned turn. The reported centre is the **mean**, not the median. The grid is 1 s from t = 600 s, seeds 1 and 2, the stage2_cap_base 2400 s schedule. The rebuilt schedule was checked against `20261102-072216_wipe_preempt_r3_s1`.
  - **F:** mean `kv_cache_usage_perc` over the sweep run's measured window (240–900 s) and its last third. Warm: `sweep_pc_on_r2/r3/r4`; cold: `sweep_pc_off_r2/r3/r4`.
  - **Cached-share split:** "starting after the previous turn had finished" means **this turn's first token** at or after the previous turn's end. Send time does not reproduce λ = 5 (0.178 against 0.143) or λ = 10 (0.000 against 0.030). Turns are selected by planned arrival inside the measured window. The sweep runs used are `_r3`, `_r5` and `_r10`.
  - **Burst "hit fell to 0.17–0.35"** (2026-11-02, λ = 3) and **"0.11–0.28"** (72k pool) are the counter hit over **the first 60 s after the burst ended**. They are not the low point during the burst: over the burst's own 120 s the λ = 3 runs were 0.169–0.194, and lower at finer resolution. The 72k wipe "dip to 0.43 at most" is the lowest 0–60 s value after the wipe (0.429).
  - **Wipe-test "before":** counter hit from the end of warm-up (240 s) to the wipe. The λ = 3.5 "first-minute hit" means 0–60 s after the wipe call ends.
- **Values that differ beyond the published rounding:**

| Value (entry) | Published | Recomputed | Note |
|---|---|---|---|
| W/C p90, λ = 2.5 (2026-11-01) | 0.75 | 0.756 | rounding edge |
| W/C mean, λ = 4 (2026-11-01) | 1.01 | 1.004 | unexplained; the median is 0.985 |
| W tokens, λ = 2 / 2.5 / 3 (2026-11-02) | 47.6k / 59.7k / 73.0k | 47.5k / 59.6k / 72.9k | unexplained, ≤ 0.3 %; no tried variant (start 240/600/900 s, end at last turn or 2400 s) matches |
| W tokens, 20 s gaps, λ = 3, seed 1 (2026-11-03) | 74.8k | 74.5k | same; the 5 s value matches (18.7k) |
| 72,480 / W at λ = 2.5; 96,656 / W at λ = 3 | 1.21; 1.32 | 1.215; 1.327 | follows from W |
| F_warm/C mean, λ = 3 (2026-11-01) | 0.13 | 0.125 | rounding edge |
| (W+F)/C: λ = 3 warm high, λ = 3 cold low, λ = 4 warm | 0.91; 1.16; 1.32–1.36 | 0.918; 1.168; 1.311–1.353 | follows from W and F; every fits/holds yes/no is unchanged |
| F_warm tokens, λ = 2 and λ = 2.5 (2026-11-02) | 6.4k; 8.7k | 6.51k (`wipe_test_preempt`, 240–900 s), 5.96k (`sweep_pc_on_r2`); 8.78k (control r2.5, 240–2400 s), 9.08k (240–900 s) | **the entry names no source run**; not reproduced exactly; the 72k predictions' yes/no are unchanged |
| Hit "before", `wipe_test_idle` (2026-11-01) | 0.773 | 0.771 (to the successful wipe), 0.774 (to `at_s`) | small; unexplained |
| Adjacent-window hit noise (2026-11-01 "Stuck" redefined): 300 s rose ≥ 0.02 / p95 change; 600 s p95 | 34 % / 0.076; 0.059 | sliding 60 s from t = 0: 34.2 % / 0.075; 0.059. From t = 240 s: 35.5 % / 0.076; 0.059 | **no single reading reproduces all three**; the 600 s value, from which `hit_climb: 0.06` was set, is reproduced by both. The threshold is unchanged |

- **Rounding only, not real differences:** λ = 3 wipe 0–15 s maximum 0.295 published as 0.30; long-run last third 0.62549 published as 0.6254.
- **Every other recomputed value matches its published rounding**, including:
  - all F values for the 2026-11-01 table except λ = 3 warm;
  - all six cached-share values and all four overlap fractions;
  - every wipe-test and λ = 3 / λ = 3.5 span value;
  - the long-run thirds (both readings), the 300 s range 0.593–0.679 and the 60 s SD 0.045.
- **No conclusion in any entry changes.** The differences are ≤ 0.01 in every share-of-pool value and ≤ 0.4 % in tokens.
- **Rerun:** `uv run --extra analysis python -m analysis.recompute_published`.

## 2026-11-04 · (7) "1408 = session median" checked against workload.py
- **The claim:** 2026-11-02, burst design: "1408-token prompts (the session median)". It is also in the `burst_*.yaml` comments ("median session prompt").
- **From `harness/workload.py:97-108`:** turn k's prompt is 512 + 128 + 256k tokens, so 640, 896, …, 2432 for k = 0…7. Turn 3 is 1408. For a full 8-turn session the median of its 8 prompts is 1536, between 1408 and 1664.
- **From the written schedules** (session rows only), in five runs: `20261030-181851_long_run`, `20261101-215502_stage2_control_cap_r3_rerun`, `20261101-190602_stage2_control_cap_r3.5`, `20261102-131353_burst_r3_s1`, `20261103-145356_stage2_control_gap5_r3.5`.
  - The median over all session requests is 1408 in all five, because sessions cut off at the end of arrivals have fewer late turns.
  - **It is a knife edge:** the share of requests at or below 1408 tokens is 0.502–0.510.
  - Over the measured window only (t ≥ 240 s), the median is 1664 in 3 of the 5. The mean is 1522–1534.
- **Verdict:** the claim holds as stated, for the whole schedule's median, but only just, and not over the steady window. "About the session median" is accurate; "the median" depends on the window. The burst size is unchanged, since the configs were used.

## 2026-11-04 · (8) CLAUDE.md: the first reply of each session lists the files read, in order
- **Why:** the audit found the start-of-session reading order (`PROTOCOL.md`, then `docs/status.md`) is not checked by anything. In this session the order was not followed: the first reply read `PROTOCOL.md:1-60` after a grep, and `docs/status.md` only in the second turn.
- **New rule in `CLAUDE.md`:** "The first reply of every session lists the files read so far, in order, including any read before the first reply."

## 2026-11-04 · (9) status.md Watch sorted; data backup first
- The Watch list is now sorted by priority. **Backup is the top item**: the Mac holds the only copy of all 104 runs (9.4 GB), per the entry above. Heat is second. Nothing was removed.

## 2026-11-04 · [CORR] An old entry was edited in place on 2026-11-02
- **What was wrong:** commit `cfc18da` (2026-11-02, "Drop lambda 4; register a 72,480-token KV pool and its capacity sweeps") changed the earlier entry "λ = 3.5 bursts: stuck in 0 of 3; burst total 0 of 6". Its bullet "**Status of the burst result:**" gained "(see the next entry for what follows)". This file is append-only (its header).
- **How it was found:** the 2026-11-04 agent-setup audit (finding N10) compared each committed version of this file with the one before. 42 of 43 later versions only appended; `cfc18da` is the one exception.
- **Since when:** 2026-11-02.
- **Which results it affects:** none. The inserted text is a pointer; no number, verdict or rule changed.
- **Re-check done:** `git show` of every version of `docs/decisions.md` against the previous one.
- **Rule that would have caught it:** the `append_only` check of `tools/check_docs.py`, which holds from `cfc18da` on (added in this audit's tools commit). The edited text stays as it is.

## 2026-11-04 · [CORR] Queue slope is in req/s, not req/s²; "goodput" has two meanings
- **What was wrong:** the capacity rule and later entries give the waiting-queue slope limit as "0.01 req/s²" (this file: 2026-10-23 "Pending", 2026-10-30 capacity rule, and later). The slope is a least-squares fit of a request count against time (FILE(analysis/load.py:103)), so its unit is req/s.
- **Since when:** 2026-10-23.
- **Which results it affects:** none. The number 0.01 and every comparison with it are unchanged; only the unit was misnamed. The comment in the used config `configs/stage2_base.yaml` keeps the old wording (rule 5).
- **Also in definitions.md:** "goodput" is marked ⚠. In this repo it is a synonym of percent fast (FILE(docs/experiment-plan.md:205)); the owner's paper notes use it for completions/s (BELIEF, outside the repo). Until the owner chooses the C1 metric, the docs say "percent fast" or "completions/s". New entries: rule J, "throughput (completion rate c)", "capacity loss", and "post-trigger margin" (defined, not computed).
- **analysis/CLAUDE.md** now names both percent-fast computations instead of "per arrival second" (audit finding 10), and forbids computing an analysis that a pending `[REG]` covers.
- **Rule that would have caught it:** J (single definitions, with units).
