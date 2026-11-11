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

## 2026-11-04 · [CORR] PROTOCOL: incomplete check list and deviations; which setups are negative
- **What was wrong** (audit findings 6, 7, 8, N16):
  - §5 left out the recorder check and the SM-clock CV limit (FILE(harness/checks.py:64)).
  - §6 omitted these deviations: `slow_drain` needs one sign and `stuck` accepts a slowly shrinking line (2026-11-01, before any Stage 2 verdict); `throughput` redefined (2026-10-30, **after** the step 4 results); the `accounting` allowance (2026-10-30, **after** `20261030-145339_sweep_pc_on_r8` failed it); `base.yaml` edited after the first smoke run used it; single-seed controls; no ramp at the 72,480-token pool or with 5 s gaps.
  - By §3's own negative-result rule (itself written after results), only the default pool with 20 s gaps is negative. The only ramps, `20261103-043121_ramp_d300` and `20261103-053730_ramp_d600`, ran there. The other two setups are "no stuck run".
  - §7 pooled 30 runs without stating the assumption.
- **Since when:** PROTOCOL.md was created 2026-11-04.
- **Effect:** no verdict changes. The result's statement narrows, and §3 gains a rule: a negative is stated for a setup only after the feasibility gate (`docs/process.md` §4) has said whether a stuck state was possible at its loads. The gate has not been run.
- **Approval:** the study owner, with the audit proposal.

## 2026-11-04 · [DECISION] Agent rules A–J installed (owner's request and approval)
- **CLAUDE.md** is now a 60-line index: role (A), evidence tags (B), authority (C), session protocol (D), and short forms of E–J. The full text is in the new `docs/process.md`: templates, adversarial review, feasibility gate, statistics, provenance, a table of past errors and the rule that now catches each, the stage-end rule, data.
- **New `docs/model.md`:** M1 (F + W), M2 (completion-rate margin), M3 (self-refill), M4 (capacity measured on one arrival pattern), and a prediction ledger. M1 is 0 for 3 on its tested predictions and is not to be used to choose loads until revised.
- **New `docs/claims.md`:** C1 and C2 with test, support, refutation and status. C3–C9 stay in the owner's Paper Plan v2 for now.
- **Choices made where the request needed one** (proposal, "Where I disagree"): one-sided 95 % Clopper–Pearson bounds by default, always stated; unregistered descriptive findings use `[RESULT]` with "Registration: none"; old entries are not retagged; a decisions entry is a record, not evidence.
- **Owner's decisions left open:** where the paper layer lives; yes/no question or thesis; C1 metric; canonical hit rate.
- From this entry on, every heading carries exactly one tag.

## 2026-11-04 · [DECISION] Provenance tools and the session-start hook
- **`tools/check_docs.py`** (stdlib only): run ids named in the docs exist; validity claims match `checks.json`; status.md's run inventory matches `runs/`; heading tags, and `RUN(...)` in every `[RESULT]`; decisions.md append-only from `cfc18da`; `FILE(path:line)` targets exist; the context pack is current; no used config changed after use, with one named exception (`configs/base.yaml`, `20261023-145613_smoke`, logged 2026-10-23). Run by `uv run pytest` (`tests/test_check_docs.py`); run checks are skipped where `runs/` is empty (the VM).
- **`tools/context_pack.py`** writes `docs/context-pack.md`, which `.claude/settings.json` forbids editing by hand.
- **SessionStart hook** (`.claude/settings.json`) prints `context_pack.py --digest`. Claude Code caps SessionStart context at 10,000 characters and sets `CLAUDE_PROJECT_DIR` for hook commands (Claude Code docs, hooks page, read 2026-11-04). The pack is about 50,000 characters, so the hook prints a digest under 9,500 and the agent still reads the pack.
- **`analysis/stats.py`:** `cp_upper` (exact Clopper–Pearson) and `cell`, with tests.

## 2026-11-04 · [RESULT] Sweep schedules share one rising-load pattern (audit, descriptive)
- **Registration:** none. A look at the schedules (inputs, written before each run) during the agent-setup audit. No threshold was judged and no verdict changed.
- **Observed:** in all 43 capacity sweeps (Stage 1, 72,480-token pool, 5 s gaps), planned arrivals are 0.67–0.97 λ in 240–390 s and 1.05–1.34 λ in 750–900 s, while the window average is 0.99–1.06 λ. RUN(every `*_sweep_*` run, `schedule.parquet` counted per span; audit scratch script, to be committed as a function before any further use). Every sweep used seed 0, and session starts come from the same random stream at every rate, so the pattern repeats.
- **λ = 3:** 2.49 req/s in 240–390 s and 3.52 req/s in 750–900 s, RUN(20261030-161749_sweep_pc_off_r3, schedule.parquet). The cache-on and both 72k runs at λ = 3 have this same schedule.
- **Cache-off completions** at λ = 4, 5, 6, 8: 3.453, 3.511, 3.521, 3.533 req/s, RUN(20261030-163358_sweep_pc_off_r4 … 20261030-173356_sweep_pc_off_r8, load.summarize).
- **Alternatives still open:**
  1. μ_off = 2 is low. The cache-off λ = 3 run failed on slope (0.0130) because its last 150 s carried load at cache-off saturation, not because λ = 3 is unsustainable without the cache.
  2. λ = 3 is truly unsustainable without the cache. The 72k cache-off failure (slope 0.0211) is no second sample: same schedule.
  - Separating evidence: a cache-off run at λ = 3 with other seeds or a longer window (GPU, owner's decision; open-questions A1).
- **Also:** the 2026-10-30 hit drift at λ = 3 (thirds 0.674, 0.625, 0.585; "cause not established") coincides with this rising load. Candidate explanation, not tested.
- **Decision taken:** none. μ values stand as measured by their rule; `docs/status.md` (Open risks) and `docs/model.md` (M4) carry the risk. Prediction ledger unchanged.

## 2026-11-04 · [REG] REG-1: post-trigger completion margin (tests assumption A of M2)
- **ID:** REG-1. Nothing below has been computed on any run. **Approved by the study owner on 2026-11-04**, before any computation, and committed with `analysis/margin.py` (`post_trigger_margin`; registered settings and runs in `REG1`, driver `reg1_table`) and `tests/test_margin.py`.
- **Question:** after each trigger ends, when the server is backlogged and the sessions' cache is cold, does it still complete at least as fast as the deepest valid cache-on overload?
- **Claim tested:** assumption A of `docs/model.md` M2: no post-trigger state completes less than the λ = 10 overload state, c_ref = 4.185 req/s, RUN(20261030-151441_sweep_pc_on_r10, load.summarize). If A holds, no healthy test load ≤ 3.5 at the default pool with 20 s gaps could have been stuck.
- **Definitions** (`analysis/margin.py`, `post_trigger_margin`; one clock, seconds from t0; scrapes every 1 s):
  - **Trigger end:** `derived.trigger_times` (a wipe's first successful call `t_end`; a burst's `at_s + duration_s`).
  - **Spans after the end:** [0, 60) s and [60, 180) s.
  - **c:** ok completions with `t_end` in the span ÷ span length. **c_upper:** its one-sided 99 % exact Poisson upper bound (`stats.poisson_rate_upper`). 99 %, not 95 %, because about two dozen spans are judged.
  - **share:** the sessions' own cached share, Σ `cached_tokens` ÷ Σ `prompt_tokens` over ok session requests whose first token is in the span. **share_base:** the same over the 600 s before the trigger starts.
  - **Qualifying span:** all three of:
    - capacity-limited: Q > 0 at every scrape;
    - burst-free: no burst request completes in the span;
    - cold: share ≤ share_base − 0.06, the stuck threshold.
  - Also reported, not judged: λ, the server counter hit, KV, N, Q (mean, minimum), preemptions.
- **Runs:** the 30 valid shock runs, listed below. Invalid runs are excluded.
  - **Default pool, 20 s gaps** (A is defined here):
    - wipes: `20261102-072216_wipe_preempt_r3_s1`, `20261102-053935_wipe_preempt_r3_s2`, `20261102-100744_wipe_preempt_r3_s3`, `20261102-110200_wipe_preempt_r3.5_s1`, `20261102-114305_wipe_preempt_r3.5_s2`, `20261102-122411_wipe_preempt_r3.5_s3`;
    - bursts: `20261102-131353_burst_r3_s1`, `20261102-135701_burst_r3_s2`, `20261102-144008_burst_r3_s3`, `20261102-152316_burst_r3.5_s1`, `20261102-160625_burst_r3.5_s2`, `20261102-164933_burst_r3.5_s3`.
  - **Reported only, no reference overload exists:**
    - 72k pool: `20261103-015156_wipe_kv72k_r3_s1`, `20261103-023254_wipe_kv72k_r3_s2`, `20261103-031353_wipe_kv72k_r3_s3`, `20261102-234257_burst_kv72k_r3_s1`, `20261103-002556_burst_kv72k_r3_s2`, `20261103-010856_burst_kv72k_r3_s3`;
    - 5 s gaps: `20261103-203837_wipe_gap5_r4.5_s1`, `20261103-211946_wipe_gap5_r4.5_s2`, `20261103-220054_wipe_gap5_r4.5_s3`, `20261103-224202_wipe_gap5_r3.5_s1`, `20261103-232310_wipe_gap5_r3.5_s2`, `20261104-000416_wipe_gap5_r3.5_s3`, `20261103-161947_burst_gap5_r4.5_s1`, `20261103-170255_burst_gap5_r4.5_s2`, `20261103-174604_burst_gap5_r4.5_s3`, `20261103-182912_burst_gap5_r3.5_s1`, `20261103-191220_burst_gap5_r3.5_s2`, `20261103-195529_burst_gap5_r3.5_s3`.
- **Prediction, as numbers** (default pool):
  1. At most 2 of the 12 burst spans qualify, because burst requests are still completing for most of them. 0 of the 12 wipe spans qualify; published peak waiting after a wipe was ≤ 9.
  2. Every qualifying span has c between 4.3 and 4.7. None has c_upper < 4.185.
  3. **Most likely outcome: inconclusive** (fewer than 3 qualifying spans), at a stated probability of about 0.6.
- **Decision rule and the decision under each outcome** (default pool; counted per trigger and per run):
  - **A contradicted:** some qualifying span has c_upper < 4.185. Let c_min be the lowest c among those spans.
    - c_min < 3.5: a stuck state was possible in principle at loads in (c_min, 3.5]. The default-pool negative is informative there, and a registered follow-up at that λ (a longer watch or a larger shock) is proposed to the owner.
    - c_min ≥ 3.5: A is false, but no tested load is affected. M2's window becomes (c_min, c_warm), recorded in model.md.
  - **A supported:** no qualifying span contradicts A, and there are ≥ 3 qualifying spans from ≥ 3 distinct runs.
    - The default-pool negative is restated as forced by capacity (M2), **for the triggers that contributed a qualifying span only**.
    - No further shock matrix at λ ≤ 3.5 on this setup is proposed for those triggers.
    - Any new setup must pass gate G with a measured cold completion rate.
  - **Inconclusive** (fewer than 3 qualifying spans, or fewer than 3 runs): A stays a BELIEF. A deliberate cold-overload run is proposed to the owner (GPU). A sketch: cache wipes repeated during a sustained overload, so that both backlog and cold cache hold for minutes.
  - **Wipes that never qualify because Q reached 0:** recorded as "the wipe built no backlog". Completions kept up with demand, which agrees with M2 but does not test A. That is evidence that the wipe never reached a state that could be stuck, and is stated as such, not as a test of the cold capacity.
  - **72k pool and 5 s gaps:** reported as margins for gate G; no decision rests on them.
- **Alternatives:**
  1. Right after a burst, the running batch is already prefilled. Completions then drain a full pipeline, so c is a best case. A state that stays cold with a small batch would not be sampled. Ruled in: this tests A only for states the triggers reached.
  2. Completions arrive in batches, so the Poisson bound understates their spread; c_upper is a floor on doubt. A contradiction therefore needs the 99 % bound below c_ref.
  3. c_ref = 4.185 comes from one 660 s window of one run with the seed-0 schedule (decisions.md 2026-11-04 [RESULT]).
  4. After a `preempt` wipe, `cached_tokens` on readmitted requests reflects their final admission, while the server counters exclude readmissions (S8). The two hit measures can disagree; both are reported.
- **Stopping rule:** one pass over the 30 listed runs, after approval. No reruns, no new spans, no new thresholds.
- **Cost:** 0 GPU hours.

### Adversarial review (separate subagent; it saw only this registration's first draft, `analysis/margin.py`, `tests/test_margin.py` and `derived.trigger_times`/`hit_between`)

Verbatim summary of its three answers:
1. **A trace where the verdict is wrong.** The first draft judged "cold" from the server counters. Burst prompts (1408 random tokens) always miss, so draining burst prefills (11,264 tokens per 5 s, 0 hits) gave a span counter hit of 0.339 against a baseline of 0.598 while the sessions' cache stayed at 0.6. The span then qualified as cold with c_all = 4.5, and six such burst spans would have declared "A holds" without ever sampling a cold session state. **Reverse:** with a true capacity of 4.5, a 60 s span holds about 270 completions (±0.27 req/s), so P(c < 4.185) ≈ 0.12 per span, and with about 12 spans P(min < 4.185) ≈ 0.78. The minimum of noisy spans against a point reference, with no tolerance, would most likely report "A fails" even if A is true.
2. **Alternatives.** For "A holds": burst dilution, and a draining, already-prefilled pipeline; both bias c upward. For "A fails": the burst-request mix in c_all, noise in the minimum, and a one-off recompute transient after a `preempt` wipe. For "inconclusive": the backlog rule is strict, and wipes that build no backlog are evidence for a margin, not a lack of evidence.
3. **Can it change a decision?** Weakly, with skewed outcomes. "A holds" would stop wipe follow-ups on burst spans alone, which cannot represent a cold wipe state.
   - Also found: the baseline window is silently clamped when it starts before the first scrape; a test for `t_start == t_end` cannot tell which is used; no test covers dilution, clamping or one empty scrape; the clocks and the burst-identification rule were unverified from the allowed files.

**Changed because of it:**
- "Cold" now uses the sessions' own `cached_tokens` share, not the server counters.
- A span must be burst-free, so only session requests are counted.
- A contradiction needs the one-sided 99 % Poisson upper bound below c_ref, not the point value.
- Support needs ≥ 3 qualifying spans from ≥ 3 distinct runs. It is counted per trigger, and conclusions are restricted to the triggers that contributed.
- Wipes with no backlog get their own reading.
- The baseline-clamp check raises an error.
- New tests cover the dilution trace, one empty scrape, a failed call before the successful one, the clamp, and the indistinguishable burst prompt (13 tests pass).
- Clocks are checked: one monotonic clock, as `time.monotonic() − t0`, in FILE(harness/recorder.py:102), FILE(harness/loadgen.py:46) and FILE(harness/trigger.py:64). A session's turn 0 is always 512 + 128 tokens (FILE(harness/workload.py:97)).
- The predictions were revised to the new rule before any computation: inconclusive is now the most likely outcome.
- **Not changed:** the spans stay [0, 60) and [60, 180), as the owner specified.

## 2026-11-04 · [RESULT] REG-1: no qualifying span, so assumption A is untested (inconclusive)
- **Registration:** REG-1 (2026-11-04, commit `c83751c`), approved before computation. One pass, as registered: RUN(each of the 30 runs listed in REG-1, margin.reg1_table), at commit `c83751c`.
- **Qualifying spans (capacity-limited, burst-free, cold): 0 of 60** (30 runs × 2 spans). Default pool: 0 of 24, so 0 runs contribute. **By the registered rule the outcome is inconclusive**: A stays a BELIEF.
- **Why nothing qualified, by condition:**
  - **Wipes, all setups: no backlog.** Q fell to 0 at some scrape in every wipe span (q_min = 0 in 30 of 30). This is the registered reading "the wipe built no backlog": completions kept up with demand, and the wipe never reached a state that could be stuck. It is not a test of cold capacity. Several wipe spans were cold by the session share (default pool [0, 60): 4 of 6, share 0.486–0.560 against baselines 0.550–0.652) but never backlogged.
  - **Bursts, [0, 60):** capacity-limited and cold in 6 of 6 default-pool runs (q_min 45–282; share 0.302–0.512 against 0.552–0.629), but **none burst-free**: 96–132 burst requests completed in each. c (all requests) was 4.050–4.683.
  - **Bursts, [60, 180):** no default-pool span was cold (share 0.542–0.652 against baselines 0.552–0.629); only `20261102-152316_burst_r3.5_s1` stayed capacity-limited, and it was not burst-free.
- **Prediction (REG-1):**
  1. ≤ 2 of 12 default-pool burst spans and 0 of 12 wipe spans qualify. **Hit** (0 and 0).
  2. c 4.3–4.7 in qualifying spans. **Not testable** (no qualifying span).
  3. Most likely outcome inconclusive (stated about 0.6). **Hit.** Update `docs/model.md` ledger row 9.
- **Not judged, reported because it bears on the reviewer's alternative 1:** default-pool burst spans at [60, 180) completed up to 5.950 req/s, RUN(20261102-160625_burst_r3.5_s2, margin.reg1_table), above the best steady value 4.735. Draining an already-prefilled backlog runs faster than steady state, so post-burst spans are a best case, as the review warned.
- **Defect found in the output (see the next entry):** `c_upper` was wrong for spans with more than about 700 completions. No span qualified on the other three conditions, which do not use `c_upper`, so the outcome does not depend on it. Not rerun, per the stopping rule.
- **Alternatives still open:**
  1. A is true, and no trigger tested so far makes a lasting cold backlog at these loads.
  2. A is false, but these triggers cannot reach the cold, backlogged state where it would fail.
  - Separating evidence: a run that holds both backlog and cold cache for minutes. That needs the GPU, so it is the owner's call.
- **Decision taken, as registered:** propose to the owner a deliberate cold-overload run (GPU). Its full `[REG]`, with prediction, decisions, cost and adversarial review, is written only if the owner wants it. Gate G stays unpassed for every setup.

## 2026-11-04 · [CORR] REG-1: Poisson upper bound underflowed for large counts
- **What was wrong:** `analysis/stats.py` `poisson_rate_upper` summed `exp(-mu)` terms directly. Near mu ≈ 745 that underflows to 0, and the bound collapsed to n / t or a stale value. In the REG-1 output, four spans with n = 714–861 showed `c_upper` ≤ c + 0.26 (e.g. n = 861: 7.175 against a correct 7.765, DERIVED from the fixed function).
- **Since when:** the function was added with REG-1 (`c83751c`).
- **Which results it affects:** none. The REG-1 outcome rests on no span qualifying, and qualification uses neither c nor `c_upper`. No span had a wrong bound and qualified.
- **Re-check done:** the CDF is now summed in log space; `tests/test_stats.py` gains a large-count test (bounds rise with n and match the normal approximation within 2). REG-1 is not rerun (its stopping rule); its recorded numbers stand, with this defect noted.
- **Rule that would have caught it:** F asked for a trace on which the verdict is wrong, but not for one on which a helper is wrong at the scale of the real data. Tests of numeric helpers now include counts at the real scale (process.md §7 row added).

## 2026-11-04 · [CORR] Hit rates from different computations compared again: λ = 7 at 5 s gaps vs λ = 5 at 20 s
- **What was wrong:** 2026-11-03 "Capacity with 5 s turn gaps": "cached prefixes survive (hit 0.757 at λ = 7 against about 0.42 at λ = 5 with 20 s gaps)".
  - 0.757 is a mean of per-scrape ratios: RUN(20261103-132357_sweep_gap5_pc_on_r7, load.summarize).
  - "About 0.42" is a counter ratio: either the measured window of the λ = 5 sweep, 0.424 RUN(20261030-141658_sweep_pc_on_r5, load._level over 240–900 s), or the ramp peak, 0.419 RUN(20261103-043121_ramp_d300, load.ramp_table) / 0.407 RUN(20261103-053730_ramp_d600, load.ramp_table). Which one was meant is not recorded.
- **Like for like:**
  - mean of ratios 0.757 vs 0.378 (load.summarize);
  - counter over the measured window 0.785 vs 0.424 (load._level over 240–900 s);
  - whole run 0.785 vs 0.446 (load.whole_run_hit_rate).
- **Source of the default-pool values in the 2026-11-02 72k comparison (0.767 / 0.661 / 0.525):** the original F script printed `hit` as first scrape to last over the whole run (`analysis/recovered/2026-11-01T173632_toolu_015jLzJdYAJ9HPDZ9RCwj2UE.out.txt`). This is what `load.whole_run_hit_rate` computes, as found in entry (4) above.
- **Pool effect, one method at a time,** λ = 2 / 3 / 4, 72,480-token pool minus default pool:
  - counter over the measured window: 0.686 − 0.765, 0.526 − 0.644, 0.415 − 0.510, so −0.079 / −0.118 / −0.095. RUN(20261102-182839_sweep_kv72k_pc_on_r2 … 20261102-193218_sweep_kv72k_pc_on_r4, load._level over 240–900 s) and RUN(20261030-132844_sweep_pc_on_r2 … 20261030-140051_sweep_pc_on_r4, load._level over 240–900 s).
  - mean of ratios: −0.074 / −0.116 / −0.093. Whole run: −0.069 / −0.109 / −0.095 (entry (4)).
  - By any single method the pool lowers hit by about 0.07–0.12, not "0.10–0.15".
- **Since when:** 2026-11-02 (pool comparison), 2026-11-03 (λ = 7 vs λ = 5).
- **Which results it affects:** none. Every method keeps the direction: the cache holds up better under overload at 5 s gaps, and the smaller pool lowers hit. No verdict uses these values. The old entries stay as written.
- **Re-check done:** the three computations on the eight sweep runs above.
- **Rule that would have caught it:** J (every quoted hit names its computation).

## 2026-11-04 · [CORR] Derived-figure differences explained by the recovered originals
- **What was wrong:** entry (6) above says "The original code was never committed", and it lists 25 published values that the reconstruction (`analysis/derived.py`) does not reproduce, several marked "unexplained". The original code was never committed, but it was recoverable: the commands and their outputs are in the Claude Code session transcripts.
- **Now committed:** `analysis/recovered/`, verbatim. That is 19 tool calls (command + recorded output), the scratch `judge.py` behind the long-run thirds, and `INDEX.md` (figure → file, transcript, timestamp, tool id, sha256).
  - It is one file per tool call, not per figure: some calls print several figures, and some figures need several calls.
  - `analysis/recompute_published.py` gains an "Original" column: the value the original printed, read from its `.out.txt`. The originals are not re-run, because several ssh to the VM or read scratch files.
- **Result, 104 comparisons:**
  - The original agrees with the published value in 91 rows and differs in 3. 10 rows have no recovered original.
  - Of the 25 values the reconstruction does not reproduce, the original reproduces 18.
- **Explained by a different reading in the original** (14 values):
  - **W:** sampled every 5 s from 600 s (every 10 s for the 5 s-gap comparison), not every 1 s. This covers W/C p90 at λ = 2.5, W/C mean at λ = 4, the W tokens at λ = 2 / 2.5 / 3 (original 47,580 / 59,722 / 72,968), the two pool/W ratios, and 74.8k at 20 s gaps (original 74,843).
  - **Wipe-test "before":** the 120 s before the wipe, not 240 s → wipe. Original 0.773 for `wipe_test_idle`.
  - **Adjacent-window noise:** 60 s steps from t = 600 s, a start the reconstruction never tried. The original gives 0.34 / 0.076 / 0.059, all three.
- **Rounding** (4 values): F_warm/C at λ = 3 (original 0.125, published 0.13), λ = 3 wipe 0–15 s max (0.295, published 0.30), long-run last third (0.6254), and (W+F_warm)/C high at λ = 4.
- **Hand arithmetic** (3 values): (W+F)/C 0.91, 1.16 and 1.32 are sums of 2-decimal values (0.75 + 0.16, 0.75 + 0.41, 1.01 + 0.31). At the original's precision they are 0.919, 1.170 and 1.313. Every fits/holds yes/no is unchanged.
- **Still without an original:** F_warm 6.4k and 8.7k (2026-11-02). 8.7k = 0.090 × 96,656 = 8,699, where 0.09 is the control r2.5 end-window KV printed to 2 decimals in `analysis/recovered/2026-11-01T215355_toolu_01ERXSiZtFdmg4pHCtdknqgA.out.txt`; that this is its origin is a BELIEF. 6.4k: no source found. Also not recovered: the 72k spans (0.11–0.28, 0.43), the long-run 60 s SD 0.045, and the λ = 3.5 seed-3 first minute.
- **Canonical functions unchanged:** `derived.py` keeps its readings, and `docs/definitions.md` notes the original's reading where it differs. Aligning the functions with the originals would change a definition (rule J), so it is left for the owner.
- **Since when:** 2026-11-04, entry (6).
- **Which results it affects:** none. No verdict uses these values, and `hit_climb: 0.06` rests on the 600 s value 0.059, which both the original and the reconstruction reproduce.
- **Re-check done:** `uv run --extra analysis python -m analysis.recompute_published`.
- **Rule that would have caught it:** I (numbers only from committed functions).

## 2026-11-04 · [CORR] A used config that cannot be fixed: stage2_base.yaml
- **What was wrong:** the verdict block of `configs/stage2_base.yaml` (FILE(configs/stage2_base.yaml:10)) lacks `pf_climb`, `hit_climb` and `drain_horizon_s`, which `load.verdict` needs (FILE(analysis/load.py:192)). It keeps the retired `q_slope`, `climb` and `end_s: 300`. Its comment still says "req/s^2" (FILE(configs/stage2_base.yaml:21)).
- **Since when:** 2026-11-01, when `stage2_cap_base.yaml` introduced the new keys (FILE(configs/stage2_cap_base.yaml:7)) and every later Stage 2 config extended that file.
- **Which results it affects:** none. `load.verdict` cannot judge the runs that use the file directly: `20261101-144335_wipe_test_preempt`, `20261101-145940_wipe_test_idle`, and the stopped `20261101-151707_stage2_control_r1.5`. None was meant to be judged (2026-11-01, "Live wipe test"). The wipe tests fail before the missing keys are even read: they are 900 s runs with the wipe at 450 s, so the watch window is empty and `np.polyfit` raises a TypeError (`load.verdict` on `20261101-144335_wipe_test_preempt`).
- **Re-check done:** that call, and the `extends:` chain of every config.
- **Not changed:** the config (rule 5). Both defects are recorded in `docs/definitions.md`, "Used configs that cannot be fixed".
- **Rule that would have caught it:** a test that resolves every used config and runs `verdict` on a synthetic trace of its shape (audit finding N15, not yet written).

## 2026-11-04 · [DECISION] "Session median" defined; saturation threshold 0.85 (study owner)
- **"Session median"** is now defined in `docs/definitions.md`: the p50 of prompt length over every scheduled session request of the whole schedule, truncated sessions included, burst requests excluded. The claim "1408 = the session median" (2026-11-02) is correct under this definition (entry (7)).
  - Recount: p50 = 1408 and share ≤ 1408 = 0.508, RUN(20261101-215502_stage2_control_cap_r3_rerun, schedule.parquet).
- **Saturation threshold:** the owner chose mean KV ≥ 0.85 for the pending drafts of the cold-state floor μ_sat,off (audit item 38) and of the 5 s-gap cache-off extension (item 40, whose draft had 0.9). This is fixed before any μ_sat,off is computed. Those registrations are not yet written or approved, and nothing has been computed under them.

## 2026-11-04 · [CORR] Two audit numbers rest on scratch scripts: marked "pending committed code"
- **What was wrong:** two results from the 2026-11-04 audit were computed by scripts in the session's scratch directory, not by committed functions, against rule I (`docs/process.md` §6):
  1. the `[RESULT]` "Sweep schedules share one rising-load pattern" (per-span planned arrival rates of all 43 sweeps);
  2. the audit's statement that all 43 recomputed Stage 2 verdicts reproduce the published ones (and the sweep throughputs and hit rates quoted with it).
- **Status:** both are **pending committed code**. Neither may be cited as `RUN(...)` evidence until the functions exist, are committed, and their output is logged in a new entry.
- **Since when:** both were made today. The REG-1 result is not affected: it was computed by the committed `margin.reg1_table`.
- **Rule that would have caught it:** I. The agent installed it and broke it in the same session.

## 2026-11-04 · [OPS] Checksum manifest of runs/ (owner's decision: manifests/runs.sha256, committed, append-only)
- **`manifests/runs.sha256`:** one line per file, `<sha256>  <run_id>/<path>`, relative to `runs/` (the `sha256sum` format). First write: 1,053 files in 104 run folders. With `runs/.gitkeep`, which is not data, that is the 1,054 files of the 2026-11-04 copy. Total 9,942,117,131 bytes, matching that copy's checksum comparison exactly. `shasum -a 256 -c` agrees on spot checks.
- **`tools/manifest.py update`** appends lines only for new files. It stops and writes nothing if a listed file is missing or its hash changed: raw data is immutable, so that is damage to investigate.
- **`tools/manifest.py verify <copy>`** checks a backup against the manifest (missing, different, unlisted). Without the script: `cd <copy> && shasum -a 256 -c <repo>/manifests/runs.sha256`. `verify runs` passes: 1,053 listed, 0 missing, 0 different.
- **`tools/check_docs.py`** now checks that the manifest only grows (git history and working copy), and that every run folder in `runs/` is listed. So after each copy from the VM, `manifest.py update` is due before the docs check passes.
- **Not done:** the second copy itself. A copy can now be verified, but none exists yet (status.md, Watch).

## 2026-11-04 · [DECISION] Owner's decisions on audit items 38–42
- **Draft kept:** the audit addendum (items 34–43) is in `docs/drafts/addendum_34-43.md`, marked DRAFT and not registered.
- **Item 38, the cold-state floor μ_sat,off** (to be registered as REG-2):
  - Saturation threshold: mean KV ≥ 0.85, as in the entry above.
  - "At the floor": |λ − μ_sat,off| ≤ 0.05 μ_sat,off. Chosen over the min–max of the contributing runs because it works with one contributing point; per the owner, the 72k pool has one cache-off point at KV ≥ 0.85 (not checked by the agent, since that would compute part of the pending registration).
  - **Both values were chosen after the default-pool and 72k sweep data had been seen.** The default-pool inputs are published (cache-off KV 0.415 and 0.867 at λ = 3 and 4, 2026-11-01; throughputs 3.453–3.533, `docs/model.md` M2). So the default-pool classification is not a blind test, and REG-2 must say so.
- **Items 38 and 39:** approved to write up. Each gets its separate review pass (rule F), and both registrations and their review output go to the owner before anything is committed or any GPU time is used. Item 39's 2.2 GPU h is approved once that review is done.
- **Item 40, the 5 s-gap cache-off extension:** on hold until the owner chooses the next direction. If it runs, its stopping rule is two consecutive λ steps at mean KV ≥ 0.85.
- **Item 41, the danger zone:**
  - The registered zone (μ_off < λ < μ_warm, PROTOCOL §5) stays unchanged for every existing result.
  - The floor is written up as a **[new] post-hoc analysis** that answers the plan's question "why the loop did not hold". It does not re-judge any cell.
  - For future cells only, to be proposed: lower edge μ_sat,off; upper edge the highest load whose 2400 s no-trigger control is `recovered`.
- **Item 42, the capacity rule:** approved for future sweeps only. The throughput test becomes throughput ≥ 0.95 × the realized planned arrival rate over the measured window. Past μ values stand as judged, and **every past capacity sweep used seed 0** (2026-11-04 [RESULT], schedules). The code change goes to the owner with the registrations, because another session is editing `analysis/` at the same time.
- **Push:** the owner pushes after reviewing `git log --stat origin/main..main`.
- **One writing session at a time:** a lockfile is to be proposed; any other session stays read-only.

## 2026-11-04 · [DECISION] One writer, one numbering; the other session's items 34–43 mapped (study owner)
- **Writer:** session `4de6c4e2` (this agent) is the only writing session. The other session stops after committing its drafts as DRAFT (`docs/drafts/addendum_34-43.md`, already committed as such in `9211d6b`). This supersedes "any other session stays read-only" in the entry above only in naming which session writes.
- **Numbering:** the audit numbering of `PROPOSAL.md` rules: items 1–33, N1–N17, open items A1–A7, registrations REG-1 onward. The other session's numbers are retired. Its committed entries stay as written (append-only) and are read through this map:

| Other session | Here | Status |
|---|---|---|
| 34 (push; `vm` remote key) | owner item 23 (push) | owner to answer |
| 35 (λ = 7 vs λ = 5 hit mix) | item 9 (hit computations) | logged: [CORR] "Hit rates from different computations compared again" |
| 36 (session median) | item 13 | logged: [DECISION] "Session median defined" |
| 37 (recovered originals) | item 12 (provenance) | logged: [CORR] "Derived-figure differences explained by the recovered originals" |
| 38 (cold-state floor μ_sat,off; REG-2 draft) | new open item **A8**: the floor under assumption B (`docs/model.md` M2, "weaker floor") | to register; the owner notes the floor argument needs only B |
| 39 (cache-off λ = 3, 3600 s; REG-3 draft) | **A1** | one registration, merged with the owner's item 12 |
| 40 (5 s-gap cache-off beyond λ = 3.5; REG-4 draft) | new open item **A9** | on hold until the next direction |
| 41 (danger-zone edge) | owner decision, recorded in the entry above | as recorded there |
| 42 (capacity rule vs realized arrivals) | **N1** | one entry; future sweeps only |
| 43 (stage2_base.yaml defects) | items 24 and N7 | logged: [CORR] "A used config that cannot be fixed" |

- **One ambiguity, flagged:** the owner's instruction reads "its REG-2 / item 39 = your A1". In the draft, REG-2 is item 38 (the floor) and item 39 is REG-3 (the λ = 3 run). This map reads it as item 39 = A1, which is what A1 asks. Item 38 becomes A8. The owner may correct this.
- **Owner's answers to the approval list, same date:**
  - Items 1–8 (harness and checks) are approved for future runs only. Item 6 means untracked files under `configs/` make the tree dirty. Item 8's thresholds are registered before any run is judged by them.
  - Items 9–10 are approved as one registered verdict-code change (NaN → `unclear`, empty window → `unclear`), with all 43 verdicts rechecked and any change logged.
  - Item 11 (cold-overload run) is deferred, because no decision depends on assumption A. Item 12 is merged into A1. Items 13 and 14 are deferred until the owner chooses the next direction.
  - A3 and A4 registrations are to be drafted now, with code and review passes. A5 comes later. Items 18–23 are to be answered separately.

## 2026-11-04 · [RESULT] The two "pending committed code" numbers, now from committed functions
- **Registration:** none; this recomputes published numbers (rule I). It clears both marks of the [CORR] "Two audit numbers rest on scratch scripts".
- **Verdicts:** RUN(all 44 runs with a full verdict block, ramps excluded, tables.verdict_table) at `d7a8edc`, clean tree.
  - It gives 43 verdicts, plus `20261102-093229_wipe_preempt_r3_s3` (invalid, stopped early), which raises on an empty window (item N7).
  - Every verdict and every baseline and end level (pf, hit, q, KV, N) equals the scratch recompute to within 0.001.
  - `tables.published_check` finds **no difference** from the published claims: every valid judged run is `recovered`, except the two `bad_baseline` controls.
  - μ_warm / μ_off by the registered rule (`tables.capacity_table`) are 4 / 2 (default pool, 20 s), 4 / 2.5 (72k pool) and 6 / 2.5 (5 s gaps), as published.
- **Throughputs and hit rates quoted in the audit:** RUN(the sweep runs named in `docs/model.md` M2, tables.sweep_table) at `d7a4f85`.
  - All match: 4.735, 4.723, 4.185, 3.453, 3.511, 3.521, 3.533, 4.567, 7.185, 2.906, and slope 0.013.
  - 72k cache-off λ = 4 is 3.4485, quoted as 3.449 (rounding).
  - Hit rates: `summarize` 0.732 / 0.627 / 0.490 and whole-run 0.767 / 0.661 / 0.525.
- **Schedules:** RUN(the 43 capacity sweeps, tables.arrival_table) at `d7a4f85`, all seed 0.
  - 240–390 s: 0.673–0.971 λ. 750–900 s: 1.047–1.336 λ. Window: 0.992–1.056 λ.
  - λ = 3: 2.493 → 3.520 req/s.
  - These are the values of the [RESULT] "Sweep schedules share one rising-load pattern". That entry stands, now with this evidence.
  - A first version of `arrival_table` also picked up control and recorder-off runs. It was fixed in `d7a4f85` before any output was quoted.
- **Decision taken:** none. Both "pending committed code" marks are cleared.

## 2026-11-04 · [DECISION] Tests for untested analysis functions (audit item N15)
- **New `tests/test_load_more.py`:** `metrics_wide` (label sums, buckets dropped, failed scrapes skipped); `rates` (a counter decrease becomes NaN, a no-query interval NaN hit); `percent_fast` (bins by planned arrival, unfinished requests are misses); `capacity` (both tests, nothing passing → NaN); `_level` (pooled levels, NaN percent fast with no requests). One more test pins the verdict fixture to `configs/stage2_cap_base.yaml`. `tests/test_tables.py` covers `analysis/tables.py`.
- **Two strict `xfail` tests** state the approved target of the registered verdict-code change (items 9–10): a window with no queries gives NaN hit, and an empty window gives `unclear`. Both fail today for the stated reasons (hit 0.0; `np.polyfit` raises). Because they are strict, they turn into errors when the change lands, so the markers must be removed in that commit.
- No analysis code was changed.

## 2026-11-04 · [REG] REG-2 (A3): what the no-trigger control dips are
- **ID:** REG-2, open item A3. **Approved by the owner on 2026-11-04** ("Let's finish it", in reply to the agent's recommendation to approve), before any computation. Not computed on any run at commit. Code: `analysis/mechanisms.py` (`bin_series`, `episodes`, `cv`, `cv_chance`, `classify_dips`; settings `REG2`; driver `reg2_table`); `tests/test_mechanisms.py`.
- **Question:** the two no-trigger controls that came out `bad_baseline` dipped with no shock. Is the pattern a regular preemption cycle of the Ao et al. kind, or arrival excesses of the seed-1 schedule at a load on the capacity edge?
- **Claim tested:** whether a competing mechanism to C2's loop shows at the zone's edge. This can at most motivate the Paper Tracker's output-length question, not answer it: output length is fixed in both runs.
- **Runs:** `20261101-202808_stage2_control_cap_r4` (default pool, λ = 4) and `20261102-225146_stage2_control_kv72k_r3.5` (72k pool, λ = 3.5). VALID, single seed each.
- **Already seen** (not blind): the published verdict levels, the percent fast per 300 s range, and the preemption totals (32, 13). The time series were not looked at.
- **Method** (60 s bins, 240–2400 s):
  - **Per bin:** planned arrival rate in the bin, and over **[a − 180 s, a + 60 s)**, which includes the bin itself because percent fast is counted by arrival; `load._level` values; KV max; preemptions; mean planned prompt tokens; unfinished requests; busy SM clock.
  - **Episode:** a run of bins with percent fast < 0.98, with runs separated by ≤ 2 healthy bins merged into one.
  - **High lead:** that 240 s rate ≥ 1.05 λ. arrival_share is the share of episodes with a high lead in any of their bins; base_share is the share of all bins with one.
  - **Spacing:** CV of the intervals between episode starts, sample SD (ddof = 1). **cv_chance** is the share of 20,000 random placements of the same number of starts among the bins (seed 0) whose CV is at or below the observed one.
- **Labels, in order:**
  1. `too_few_episodes`: fewer than 2 episodes.
  2. `ao_like_cycle`: ≥ 4 episodes, cv_chance ≤ 0.05, preemptions in or in the bin before ≥ 2/3 of episodes, and arrival_share − base_share < 0.3.
  3. `arrival_driven`: arrival_share ≥ 2/3 and arrival_share − base_share ≥ 0.3.
  4. `unclassified`: anything else.
- **Prediction:**
  - λ = 4: `arrival_driven` ≈ 0.5, `unclassified` ≈ 0.35, `too_few_episodes` ≈ 0.1, `ao_like_cycle` ≈ 0.05.
  - 72k λ = 3.5: `too_few_episodes` ≈ 0.6, `arrival_driven` ≈ 0.25.
- **Decision, over the pair of labels:**
  - **`ao_like_cycle` in either run:** open a new open item, add the cycle to claims.md as a C2 alternative, and propose (registered, to the owner) a test that varies output length.
  - **No `ao_like_cycle`, and `arrival_driven` in at least one run:** the `bad_baseline` dips are attributed to the schedule at the capacity edge, for that run only. Recorded as support for the owner's proposed upper edge for future cells (the highest λ with a `recovered` 2400 s control). No run proposed.
  - **Neither label in either run:** A3 closes as "not resolved by existing data". No run proposed.
  - This analysis changes at most whether a new item and a proposal are opened. The λ = 4 exclusion stands either way.
- **Alternatives:**
  1. Heat. The SM clock is reported; λ = 4 had a SW thermal share of 0.047 against 0.05.
  2. Session-mix excursions, i.e. long late-turn prompts. Mean prompt per bin is reported, not judged.
  3. Arrival-driven dips amplified by preemptions. `arrival_driven` names the trigger, not the absence of a preemption mechanism.
  4. n = 1 per setup.
- **Stopping rule:** one pass after approval. **Cost:** 0 GPU hours.

### Adversarial review (separate subagent; it saw only the first draft, `analysis/mechanisms.py`, the tests and `load._level`)

Summary of its answers:
1. **Wrong labels, checked against the code:**
   - **(A)** Dips land in their own excess bin, because percent fast is counted by arrival. A lead window that ended at the bin's start never saw the excess, so arrival-driven dips came out `ao_like_cycle`: arrival_share 0, preempt_share 1, CV 0.167.
   - **(B)** One slump flickering across 0.98 split into 4 "episodes" with CV 0 and came out `ao_like_cycle`.
   - **(C)** With 3 episodes, chance alone gives CV ≤ 0.3 with probability 0.33 (0.14 for 4).
   - **(D)** 1.10 λ over 120 s is about a 2.2σ excess, too high to see the small sustained excesses that matter near ρ ≈ 1.
   - **(E)** Unfinished requests at the end could create a spurious final episode.
2. **Alternatives:** `ao_like_cycle` could be (A), (B) or (C); `arrival_driven` does not exclude a preemption-amplified, excitable edge; `unclassified` could be a real arrival link hidden by (A) or (D); `too_few` says nothing about cause.
3. **Decision value:** barely; only `ao_like_cycle` triggers action, and it was the label most prone to false positives. The table had no row for a mixed result, which was the most likely one.
   - **Code issues:** mean prompt per bin was promised but missing; the lead window excluded the bin; ddof was unstated; there was no merge rule; preemptions just before an episode were not counted; no test covered noise, the excess-in-bin case or fragmentation.

**Changed because of it:**
- The lead window now includes the bin ([a − 180, a + 60)), and the threshold is 1.05 λ (A, D).
- Runs separated by ≤ 2 healthy bins are merged (B).
- `ao_like_cycle` needs ≥ 4 episodes and a seeded chance test, cv_chance ≤ 0.05; ddof = 1 is stated (C).
- Preemptions in the bin before an episode count.
- Mean prompt and unfinished counts per bin are reported (E).
- The decision table now covers every pair of labels.
- New tests reproduce traces A and B and the chance case; 10 pass.
- The predictions were revised before any computation.
- **Not changed:** n = 1 per setup, which only another seed could fix (GPU, deferred).

## 2026-11-04 · [DECISION] REG-3 (A4) dropped; A4 stays open
- **What:** the REG-3 draft (does first-admission prefill growth exceed any possible recompute growth, λ = 6 against λ = 10, cache on) is not registered and not computed. The owner's "Let's finish it" was read as accepting the agent's recommendation to drop it.
- **Why** (the draft's adversarial review, and rule A1): even after revision, the likely outcome follows from published numbers (first-admission hit 0.317 → 0.197; flat preemptions per unit time, ≈ 79 and 78). It would change one write-up sentence and nothing else.
- **What stays:** A4 is open in `docs/open-questions.md`. The informative test is a logging run that exports vLLM's internal recompute count (`preempted_queries − preempted_hits`, SOURCE(vLLM 0.32.0 v1/metrics/stats.py:PrefixCacheStats)), which needs the GPU and the owner. Its code (`work_per_completion`, `attribute_loss`) was removed before commit, so no unregistered analysis code is left in `analysis/`.

## 2026-11-04 · [RESULT] REG-2 (A3): both control dips are arrival-driven; no Ao-like cycle
- **Registration:** REG-2 (commit `c70c9e6`), approved before computation. One pass: RUN(20261101-202808_stage2_control_cap_r4, mechanisms.reg2_table) and RUN(20261102-225146_stage2_control_kv72k_r3.5, mechanisms.reg2_table), at `c70c9e6`.
- **Default pool, λ = 4: `arrival_driven`.**
  - 3 episodes (11 of 36 bins), starting at 540, 1980 and 2340 s.
  - arrival_share 0.667 against base_share 0.306 (excess 0.36).
  - Spacing CV 0.85, cv_chance 0.67, so not regular.
  - Preemptions in 2 of 3 episodes; all 32 of the run's preemptions fall inside episodes.
  - **Knife edge:** arrival_share is exactly the 2/3 threshold (2 of 3 episodes). One episode fewer with a high lead would have given `unclassified`.
- **72k pool, λ = 3.5: `arrival_driven`.**
  - 2 episodes (bins at 720 and 2100 s), both with a high lead (arrival_share 1.0 against base 0.278).
  - All 13 preemptions fall inside them.
- **Also seen, not judged:**
  - Every low bin in both runs had KV max ≥ 0.948, and every bin with preemptions had KV max ≥ 0.978.
  - Planned arrivals in the low bins were 3.9–5.2 req/s at λ = 4 and 4.1–4.3 at λ = 3.5.
  - No unfinished requests, so the last-bin episode at λ = 4 is not an end-of-run artifact.
  - Mean planned prompt in low bins was 1,480–1,598 tokens at λ = 4 and 1,598–1,686 at λ = 3.5 (not compared with other bins).
  - Busy SM clock 1,889–1,941 MHz.
- **Prediction:** λ = 4 `arrival_driven` was the modal prediction (≈ 0.5): **hit**. 72k: `too_few_episodes` was predicted at ≈ 0.6 and `arrival_driven` at ≈ 0.25; the outcome was the latter, so a **miss** of the modal prediction. `ao_like_cycle` (≈ 0.05 and less) did not occur. Ledger row 10.
- **Alternatives still open:** these runs are KV-full episodes started by arrival excesses. Labelling them `arrival_driven` names the trigger. It does not rule out preemptions amplifying a dip (alternative 3), and n = 1 per setup.
- **Decision taken, as registered (no `ao_like_cycle`, `arrival_driven` in both):** the two `bad_baseline` controls are attributed to arrival excesses of the seed-1 schedule at the capacity edge. This is recorded as support for the owner's proposed upper edge for future cells (the highest λ with a `recovered` 2400 s control). No run is proposed. A3 closes.

## 2026-11-04 · [DECISION] Harness and check changes, audit items 1–8 (owner-approved, future runs only)
- **Where the new knobs live:** `configs/defaults.yaml`, merged **beneath** every config by `harness/config.py` `with_defaults`. Every new run's saved `config.yaml` records the values. `base.yaml` is not edited (rule 5). Old run folders get the same defaults when re-checked. A check whose setting is null is skipped. `load_config` moved to `harness/config.py`; `harness.run` re-exports it.
- **1. `kv_capacity` check:** the server log's "GPU KV cache size: N tokens" must equal `checks.expected_kv_tokens`. That is null by default, so a future config must set it to use the check.
- **2. GPU processes:** `env.json` gains `persistence_mode` and `gpu_processes` (`nvidia-smi --query-compute-apps`) at start, and `events.jsonl` gains `gpu_processes_end` before the server stops. Recorded only, not judged.
- **3. One run at a time:** `run.py` holds an `fcntl` lock on `lock_file` (`.run.lock`, gitignored), and refuses to start if the server's host:port already answers. Before this, a foreign server answering `/health` would have been accepted (audit item 20).
- **4. Magic numbers into config:** `load_lead_s`, `server.health_timeout_s`, `recorder.scrape_timeout_s`, `recorder.after_load_scrapes`, `stop_grace_children_s` and `checks.rate_sigma`, all at their old values. `recorder.scrape(url, timeout_s=0.9)` keeps 0.9 as its default only for callers without a config.
- **5.** `checks.py` no longer reuses `sent`: it is now `sent_df` and `sent_ids`. No behaviour change.
- **6.** Untracked files under `configs/` make the tree dirty (`env.json` `untracked_configs`; the `clean_git` detail shows them).
- **7. Trigger timing:** a wipe's **first** attempt must start within `checks.max_trigger_delay_s` = 1.0 s of `trigger.at_s`. The first attempt is used because `idle` mode then retries by design.
- **8. Manipulation checks, off until registered:** a wipe's counter hit over `wipe_window_s` after the successful call must be ≤ `wipe_max_hit`, and a burst's KV max must reach `burst_min_kv_max`. All three are null. Their values must be registered in a `[REG]` before any run is judged by them (owner's condition).
- **Effect on recorded runs:** none; `checks.json` files are not rewritten.
  - `harness.checks.run_checks` was re-run read-only on the 101 run folders it can read. Valid/failed matches the recorded `checks.json` in all but one.
  - That one is `20261030-145339_sweep_pc_on_r8`, which now passes `accounting`. This is the 2026-10-30 allowance ("the new rule would pass it"), not these changes. It stays INVALID as recorded.
  - `20261023-145613_smoke` cannot be re-checked: its config predates `gpu_busy_util_pct`. This was already so at HEAD before these changes.
- **Tests:** `tests/test_checks.py` (+7) and `tests/test_run_guards.py` (new, 4). The old trigger fixtures gained the `t_start` field that real `trigger.jsonl` records always have. Full suite: 138 passed, 2 xfailed.
- `harness/CLAUDE.md` updated: knobs go in `defaults.yaml`; one run at a time.

## 2026-11-04 · [REG] REG-4: verdict-code change, values a window can't give are NaN; a branch that needs one gives `unclear` (audit items 9–10, 11, N7)
- **ID:** REG-4. The owner approved it in principle (approval list items 9–10: "one registered verdict-code change (NaN → unclear; empty window → unclear). Recheck all 43 verdicts after and log any change"). This entry fixes the exact change and the recheck. It is committed together with the change and before the recheck.
- **Change to `load._level`** (diff in the commit):
  - pf is NaN with no requests (unchanged in effect: the mean of an empty set was already NaN).
  - **Every server value** (hit, q, n, kv, q_slope) is NaN when the scrapes don't cover the window: no scrape within the registered `checks.max_scrape_gap_s` (2.0 s, `configs/base.yaml`) of each end, or a larger gap inside it. Before, `np.interp` held the last value past the final scrape, so a half-empty window gave numbers from a fraction of it.
  - **hit** is NaN when the query counter does not rise (it was 0.0, audit item 11), or when either cache counter goes down inside the window (a restart).
  - Gauge means and the q slope use only non-NaN scrapes; q_slope needs at least 2. Before, one NaN made the slope NaN, and 0 scrapes raised a `TypeError` (N7). With exactly 1 scrape, `polyfit` returned a number.
- **Change to `load.verdict`:** each branch is decided only from the values it uses; a branch that needs a NaN gives `unclear` and does not fall through. In order:
  1. base pf NaN → `unclear`.
  2. base pf < 0.98 → `bad_baseline`.
  3. Any of end pf, end hit, end q, base hit, base q NaN → `unclear`. Otherwise the `recovered` test, unchanged.
  4. Signs of recovery: pf climb (end and previous pf), hit climb (end and previous hit), draining (end q, q_slope). Any sign true → `slow_drain`. Otherwise, if any sign can't be computed → `unclear`. Otherwise the `stuck` test, unchanged. Otherwise `unclear`.
  - Every threshold and window is unchanged. A window with all values present takes exactly the old path.
- **Known consequence, accepted under the owner's rule (NaN → unclear):** a total stall that admits nothing has no defined hit rate, so it is `unclear`, not `stuck`. Its pf and queue stay visible in the levels.
- **Prediction:**
  1. All 43 verdicts from `tables.verdict_table` are unchanged, and so are all their levels.
  2. `20261102-093229_wipe_preempt_r3_s3` (INVALID; stopped at about 1618 s, so its end window has no requests or scrapes) changes from raising to `unclear`. Its baseline is complete, so it is not `bad_baseline` unless its baseline pf is < 0.98.
  3. The 26 ramp steps (`tables.ramp_tables`) and the REG-2 rows (`mechanisms.reg2_table`) are unchanged.
- **Recheck:**
  - **Before:** captured at `677559d` (clean tree) and saved in the session scratchpad. `verdict_table` uses `find_runs(valid_only=False)` and records a raised error per run, so the invalid run is included.
  - **After:** the same three calls at this commit.
  - **Comparison:** verdict labels exactly. Every level with `np.isclose(rtol=0, atol=1e-9, equal_nan=True)`, plus an explicit check that NaN appears in exactly the same places. Error-to-verdict transitions are listed. Every difference is logged.
- **Decision under each outcome:** this is a correctness fix, so the change stands under every outcome; the recheck is an impact log, not a test of the decision.
  - **No valid verdict changes:** audit items 9–11 and N7 close.
  - **A valid verdict changes:** a `[RESULT]` names the run with its old and new verdict and every published statement that used it, and a `[CORR]` corrects each statement.
  - **Any ramp or REG-2 value changes:** logged the same way; REG-2's labels are restated if they change.
- **Stopping rule:** one recheck. **Cost:** 0 GPU hours.

### Adversarial review (separate subagent; it saw only the first draft, its diff, `analysis/load.py` and the two load test files)

Summary:
1. **Traces, run on a scratch copy:**
   - **A:** a total stall with no queries turned from `stuck` into `unclear`.
   - **B:** a NaN previous window blocked a correct `recovered`.
   - **C:** the NaN check came before `bad_baseline` and hid it.
   - **D:** a window covered by scrapes for only 50 of 600 s was judged with no warning (old and new code alike).
   - **D2:** exactly one scrape gave a number from `polyfit`, not a `TypeError` as the draft claimed.
   - **E:** a counter reset became NaN, a change the draft didn't list.
   - **F:** one NaN gauge made q_slope NaN while q, n and kv skipped it, which hid a real drain.
   - **G:** interpolation across a gap still gave a number.
2. **Recheck:** a plain 1e-9 comparison misses a value turning NaN; the before-outputs had to survive runs that raise; the invalid run's coverage had to be named; and the plan is an impact log, not a test, which should be said.
3. **Code:**
   - `dq > 0` also catches resets.
   - The scrape count included NaN rows.
   - The pf, q, n and kv edits did nothing (the means were already NaN).
   - No coverage check existed.
   - Missing tests: a reset; one scrape; a NaN gauge; a NaN previous window with `recovered`; `bad_baseline` with an empty end; a stall; a partly covered window; a ramp step without scrapes.

**Changed because of it:**
- Branch-aware NaN handling: `bad_baseline` and `recovered` are decided whenever their own inputs exist (B, C).
- A coverage rule using the registered scrape-gap limit makes every server value NaN in a partly covered or gapped window (D, D2, G).
- Counter resets give NaN hit, and this is now stated (E).
- Gauges skip NaN rows (F).
- The stall outcome is stated as a known consequence (A).
- The recheck uses a NaN-aware comparison, names `valid_only=False`, and records raised errors.
- The diff's no-op edits are described as such.
- New tests cover each trace. The fixtures gain `checks.max_scrape_gap_s`, which `_level` now requires (no magic default). Full suite: 147 passed.
- **Disclosure:** the "switching" file the reviewer saw was the agent stashing the change to capture the before-outputs during the review. Its scratch copy was the right response.

## 2026-11-04 · [RESULT] REG-4: no valid verdict changed; the stopped run is now `unclear`
- **Registration:** REG-4 (commit `ebb0647`, with the change). Before: RUN(all runs with a full verdict block, tables.verdict_table), `tables.ramp_tables` and `mechanisms.reg2_table` at `677559d`, clean tree. After: the same three at `ebb0647`, clean tree.
- **Comparison** (labels exact; levels NaN-aware to 1e-9; NaN positions explicit): 9 differences, **all in `20261102-093229_wipe_preempt_r3_s3`** (INVALID, stopped at about 1618 s).
  - Before, it raised.
  - Now its baseline is computed (pf 1.000, hit 0.652, q 0.0, 6 preemptions) and its verdict is `unclear`, because its end window has no requests or scrapes.
  - The `error` column is gone, because no run raises any more.
- **Unchanged:** every verdict and every level of the other 43 rows; all 26 ramp steps (RUN(20261103-043121_ramp_d300, tables.ramp_tables), RUN(20261103-053730_ramp_d600, tables.ramp_tables)); both REG-2 rows (RUN(20261101-202808_stage2_control_cap_r4, mechanisms.reg2_table), RUN(20261102-225146_stage2_control_kv72k_r3.5, mechanisms.reg2_table)), episode starts included.
- **Published claims:** `tables.published_check` still finds no difference. The valid runs are 37 `recovered` and 2 `bad_baseline`.
- **Prediction:** 1 hit (all 43 unchanged); 2 hit (the stopped run became `unclear`, its baseline being complete with pf 1.000); 3 hit (ramps and REG-2 unchanged).
- **Decision, as registered:** the change stands. Audit items 9–10 (the owner's approval list), 11 (`_level` hit 0.0) and N7 (the crash on an empty window) are closed. `docs/definitions.md` now gives the new NaN rules and the shifted `load.py` line numbers.

## 2026-11-04 · [DECISION] REG-5 (A8, cold-state floor) not computed; what it would have shown, written as a calculation
- **Why it is not computed** (its adversarial review, and rule A1):
  - **Fixed in advance.** At the default pool the published cache-off throughputs (3.453–3.533 req/s at λ = 4–8) fix the floor in [3.45, 3.53], so λ = 3 is "below" and λ = 3.5 "at" whatever the code computes.
  - **The check of assumption B would test the wrong states.** The backlogged cache-on windows available are warm, high-hit states, which trivially beat cache-off; the burst windows almost never qualify. The state B is about (cold, thrashing, after a shock) is not among them.
  - So the analysis could change no decision, and could present a foregone result as evidence. Its code was removed before commit.
- **The calculation (default pool, 20 s gaps):**
  - DERIVED: cache-off saturated throughput is about 3.50 req/s, the mean of 3.453, 3.511, 3.521 and 3.533 (RUN(20261030-163358_sweep_pc_off_r4 … 20261030-173356_sweep_pc_off_r8, tables.sweep_table)).
  - The 6 shock runs at λ = 3 lie about 14 % below it.
  - The 6 at λ = 3.5 lie at it, within 0.2 %.
  - The highest load with a `recovered` 2400 s control is 3.5 (λ = 4 was `bad_baseline`).
- **What follows, and only on two conditions:**
  1. Assumption B holds in the post-shock state (untested; it could fail exactly where the hypothesis lives, through preemption thrash).
  2. The 900 s saturation is a sustained capacity (REG-6 tests this).
  - On both conditions, the 6 λ = 3 runs could not have stayed stuck. The 6 λ = 3.5 runs are at the edge, and nothing follows for them: near zero drift, a backlog need not drain.
  - On the same conditions, this setup has no healthy load clearly above its cold floor, so a further shock matrix here is unlikely to be informative.
- **The 18 runs at the 72k pool and with 5 s gaps:** no cache-off floor is measured for them, so nothing is concluded.
- `docs/model.md` M2 gets this as a note.

## 2026-11-04 · [REG] REG-6 (A1): sustained cache-off capacity at λ = 3, default pool (GPU, 2.2 h)
- **ID:** REG-6, open item A1 (merged with the owner's item 12 and the other session's item 39). **Approved by the owner on 2026-11-04 ("ok"), before any run.** Committed together with `analysis/floor.py` (`backlogged_stretches`, `sustained_capacity`; settings `REG6`; driver `reg6_table`), `tests/test_floor.py` and `configs/long_pc_off_r3_s0.yaml` and `_s1.yaml`.
- **Question:** is λ = 3 below the default pool's cache-off capacity in sustained operation?
  - μ_off = 2 rests on one 900 s run that failed the slope test narrowly, under the seed-0 rising load.
  - If λ = 3 is below cold capacity, the 6 default-pool shock runs at λ = 3 were bound to recover, and were not tests of C1.
  - It is also condition 2 of the floor calculation (decisions.md 2026-11-04, REG-5 not computed).
- **Design:**
  - The same server settings as `sweep_pc_off`: base flags plus cache off, with the cap of 256 stated (its default anyway), no dev mode, and `kv_capacity` expected at 96,656.
  - λ = 3, 3600 s, judged over 600–3600 s, seeds 0 and 1.
  - The 3600 s schedules share no arrivals with the 900 s one (the count is drawn over the whole duration; `harness/workload.py:55-57`).
  - Planned rate over the window, from the schedules: 3.049 (seed 0) and 3.032 (seed 1). Seed 0 has a 3.91 req/s stretch at 3051–3201 s; seed 1 never exceeds 3.46 req/s in any 150 s.
- **Measurement:** the capacity is measured directly. Backlogged stretches are runs of consecutive scrapes with waiting ≥ 1 that last ≥ 30 s. c_b = ok completions inside them ÷ their total length. While requests wait the server is saturated, so c_b is its capacity, not the demand.
- **Label per seed** (λp = that seed's planned rate):
  - `unclear_data`: a NaN waiting value, or a scrape gap > `checks.max_scrape_gap_s`.
  - `sustainable_no_backlog`: backlogged stretches total < 300 s, so the server kept up with its own schedule.
  - `sustainable`: c_b ≥ 1.05 λp.
  - `not_sustainable`: c_b < λp.
  - `unclear`: otherwise.
- **Prediction:**
  - Seed 0: `sustainable`, c_b 3.35–3.60, from the backlog its 3.91 req/s stretch builds.
  - Seed 1: `sustainable_no_backlog` (≈ 0.6) or `sustainable` (≈ 0.3).
  - Both `not_sustainable` or `unclear`: ≈ 0.1.
- **Decision:**
  - **Both seeds `sustainable` or `sustainable_no_backlog`:**
    - The 6 default-pool λ = 3 shock runs were below sustained cache-off capacity, so they were not tests. μ_off = 2 is recorded as an underestimate due to the seed-0 schedule.
    - Combined with the floor calculation, the default pool with 20 s gaps has no healthy load clearly above its cold floor. **No further shocks are proposed there**; the next experiment must use a setup whose floor is measured first and lies below a healthy load (the owner chooses the setup).
  - **Either seed `not_sustainable`:**
    - λ = 3 is above sustained cold capacity, so the 6 λ = 3 runs were real tests, and they recovered. That is evidence against C1 at this load, to be written up as such.
    - 900 s saturation overstates sustained capacity, so the floor calculation is withdrawn.
  - **Otherwise** (`unclear`, `unclear_data`, or one seed of each kind): no change to any statement; the stopping rule applies.
- **Alternatives:**
  1. Heat or slowdown over the hour; `gpu_steady` applies, and c_b is reported per stretch time.
  2. A backlog at λ ≈ 3 is small, so batches there are smaller than in deep overload and c_b may be lower than the 900 s saturation. This is a real effect, and it is what the run measures.
  3. With few stretches, c_b rests on little time. The 300 s minimum guards against this.
- **Stopping rule:** both seeds once; an invalid run is rerun unchanged, at most twice. **Cost:** about 2.2 GPU h. The VM must `git pull` first.

### Adversarial review (separate subagent; it saw only the first draft, the two configs and their parents, `analysis/floor.py`, the tests, `harness/workload.py` and `harness/config.py`; it built schedules, which are inputs, but opened no runs)
1. **The first draft's queue-shape rule** (throughput, waiting slope, late vs early waiting) **would most likely give a split.**
   - A queue model run on the actual schedules shows seed 0's 3.91 req/s stretch drives the late waiting mean above 5 × max(1, early) → `unclear`, while seed 1 comes out `bounded`. By the draft's own table a split moves no edge, so 2.2 GPU h would buy nothing.
   - The same rule labels a critically loaded run `bounded` when its early queue is large, and a healthy run `unclear` when a late burst drains before the end.
   - Within one schedule, the planned rate's own SD is about 0.07 req/s.
2. **Code and claims:**
   - One NaN scrape made the slope NaN and produced `growing`.
   - The claim that seed 0 is "comparable" to the 900 s run was false: no shared arrivals.
   - The throughput criterion never decided anything.
   - The settings match `sweep_pc_off` once its flags are checked; the server `--seed` stays 0 for both seeds.
3. **The fix the review recommended:** measure the capacity directly over backlogged stretches, so a schedule burst becomes the measurement instead of its confound.

**Changed because of it:**
- The rule is replaced by c_b over backlogged stretches.
- NaN and gaps give `unclear_data`.
- "Comparable" is removed, and the schedules' planned rates and the seed-0 burst are stated.
- The decision is restricted to the 6 default-pool λ = 3 runs (the first draft said 12, which was wrong).
- New tests: a burst that drains, a saturated server below its load, a capacity just above it, and NaN or a gap; 6 pass.

## 2026-11-04 · [OPS] REG-6 interrupted: the VM went offline during seed 0; microk8s found on the VM
- **Started:** `20261104-134159_long_pc_off_r3_s0` at 13:41:59 UTC from `4d30f1d`, clean tree. The GPU was idle (1 MiB, no compute processes), with 16 GB disk free. Seed 1 was queued behind it in one shell.
- **Lost:** at about 14:35 UTC, with seed 0 at about t = 3161 s of 3600, the VM stopped answering on both addresses (Tailscale: offline; ping and SSH time out). The Mac's network was fine. The cause is not known.
  - Earlier shutdowns were attributed to the shared GPU (decisions.md 2026-11-02).
  - The owner had just asked to pause. The agent's stop command (to the wrapper shell only, so seed 0 would finish and seed 1 would not start) never reached the VM.
- **State:** seed 0 is incomplete and almost certainly has no `checks.json`, so it does not count. It is **only on the VM**, not yet copied. Seed 1 never started. REG-6 has no valid run.
- **When the VM is back, in order:**
  1. Inspect the seed-0 folder and the VM's journal for the cause.
  2. Copy the folder to the Mac (it stays on record, never deleted), run `python3 tools/manifest.py update`, delete its line from `manifests/pending_copy.txt` (new: the list of run ids that exist only on the VM, which `tools/check_docs.py` accepts until the folder is copied), and remove the VM copy only after a checksum-verified copy (decisions.md 2026-11-04).
  3. Log what the journal shows.
  4. With the owner's go, rerun `configs/long_pc_off_r3_s0.yaml` unchanged at a new run id, then `..._s1.yaml`. REG-6's stopping rule allows an invalid run to be rerun unchanged, at most twice.
  5. Compute `uv run python -m analysis.floor` once, and write the `[RESULT]`.
- **Found while checking the VM:** microk8s (Kubernetes: kubelite, containerd, calico) runs on the VM. It was installed 2026-10-23 at 11:49 UTC (`/var/snap/microk8s/common`, the first kubelite start), about 3 hours before the first run, so it was present for all 104 runs. It sat at load 0.1–0.2 when idle and is not pinned. It is the same for every run, so it confounds no comparison, but `env.json` doesn't record it, and it shares the cores the harness pins. Whether to stop it during runs is the owner's decision.

## 2026-11-05 · [DECISION] Audit of Stage 2, and the owner's choice of the next direction: setup L1 with a feasibility gate first
- **What was done (0 GPU h):** a read-only audit of all 104 runs, the harness, the analysis code, the docs history and the literature on metastable failures. Nothing in `runs/` was touched.
- **Data integrity:**
  - `git_dirty` is false in all 104 runs.
  - `uv run python -m analysis.tables published` gives "44 judgeable runs, 39 valid, 0 raised" and "differences from published: none" (the commit of this entry, before its own changes to `analysis/`).
  - The 39 valid judged runs are 37 `recovered` and 2 `bad_baseline`, as in REG-4's result. **Correction of the audit's own draft:** it said "41 valid judged verdicts, 39 `recovered`". That came from an agent summary, not from the table above.
- **Why no run got stuck** (DERIVED or BELIEF, as marked; to be tested, not asserted):
  - Metastability without retries needs the bad state to lose capacity. Plain queues are only stable or unstable (Isaacs et al., "Formal Analysis of Metastable Failures in Software Systems", arXiv 2510.03551). A trigger must also exceed the gap between capacity and load (Huang et al., OSDI'22).
  - This study removed retries on purpose (CLAUDE.md rule 2), so the only possible sustaining effect is a capacity loss from the lost cache: c_b(λ) < λ ≤ c_warm(λ) (`docs/model.md` M2).
  - At the default pool that loss is small. DERIVED from M2's inputs: 1 − 4.185 / 4.735 = 0.116. BELIEF: larger batches in a backlog make up for most of the lost cache.
  - Every burst backlog drained, and the λ = 4 control met a natural backlog and recovered from it (REG-2).
  - At the loads that passed pf ≥ 0.98, mean KV at the end was 0.15–0.20 (decisions.md 2026-11-02, "No-trigger controls done").
- **Design points for future cells only** (no past verdict changes):
  1. **The pf ≥ 0.98 baseline excludes loads near capacity.** Future test loads are chosen at ≤ 0.8 μ_warm, so the rule is kept unchanged rather than loosened.
  2. **Every shock seed gets a control with the same seed and the same duration**, so the session schedules match (the burst uses its own generator, `harness/workload.py`). Until now only seed 1 had one, and no burst run matched any control (2520 s against 2400 s).
  3. **Seed 3 was a lighter test.** In every valid seed-3 shock run, the `arrival_rate` check's count is 0.944–0.953 of its expected count. Examples: 6116 of 6480 in `20261102-100744_wipe_preempt_r3_s3`; 9237 of 9720 in `20261103-220054_wipe_gap5_r4.5_s3` (FILE(runs/<id>/checks.json), `arrival_rate` detail). This passes the check's tolerance, but it is reported with any pooled statement.
  4. **Thin heat margins in two counted runs:** SW-thermal share 0.047 against the 0.05 limit in `20261102-072216_wipe_preempt_r3_s1` and `20261101-202808_stage2_control_cap_r4` (`checks.json`, `gpu_steady`). The rule is not changed.
  5. **The scheduler settings that shape the loop are not recorded:** `max_num_batched_tokens` (probably 2048, from the compile range in `docs/probe/20261023_Qwen3-4B/server.log`; BELIEF) and `--scheduler-reserve-full-isl`. They are to be probed on the VM (open-questions A10).
  6. **60 s gaps are advised against.** From schedules (`derived.working_set`, seed 1, 2400 s, /96,656): W/C mean is 0.77 at 20 s gaps and λ = 3, but 1.48 at 60 s gaps already at λ = 2. The warm state could not hold its own working set, so there would be no warm state to lose (DERIVED; inputs, not outcomes).
- **Owner's choices (2026-11-05):**
  - **Direction:** setup L1. It is the 5 s-gap setup with a 2048-token system prompt per session, measured first by a feasibility gate (REG-7, next entries).
  - **REG-6:** run after the gate, when the GPU is idle. Its result changes how the default-pool negative is written up, not the next experiment.
  - **Turns stay open-loop** (rule 2). The overlap share is measured in the gate, and closed-loop turns are proposed only if overlap hits are more than half of the post-burst hits.
  - **C1 metric for future cells:** the registered pf/hit/queue verdict, unchanged. The completion rate in backlog (c_b against λ) is reported as a pre-registered secondary readout and never decides a verdict.
- **Rejected claim from the audit:** that preempted readmissions inflate the hit counter. S8 (SOURCE, `docs/open-questions.md`) says their numbers go to unexported `preempted_*` fields, so nothing changes.

## 2026-11-05 · [CORR] Doc statements found wrong or inconsistent in the 2026-11-05 audit
- **What was wrong:**
  1. FILE(docs/claims.md:26) says "during bursts KV reached 1.00 and hits fell to 0.11–0.35". The hit values are the first 60 s *after* the burst ended, not during it (decisions.md 2026-11-03, the 72k entry). The counter also includes the burst requests, which never hit, so it overstates how cold the sessions' cache was (REG-1's review, decisions.md 2026-11-04). Corrected in claims.md.
  2. decisions.md 2026-11-02 "Fan on the GPU backplate": "peak KV 0.36" for `20261102-100744_wipe_preempt_r3_s3` holds only for 900–1500 s. The window was not stated. Over the full watch the peak is higher (an audit agent's inline count; the value is not quoted until a committed function gives it). The old entry stays as written, and no verdict uses the peak.
  3. FILE(docs/open-questions.md:51), A8, says "Open. To be registered". REG-5 (A8) was decided not to be computed (decisions.md 2026-11-04 [DECISION] REG-5). Corrected.
  4. FILE(docs/model.md:18) says M2 is "Not yet registered or tested". REG-1 tested its assumption A (inconclusive). Corrected.
  5. FILE(docs/open-questions.md:23), S5, says "the verdict rule as redefined before any verdict". The baseline window was later moved after the λ = 3 burst verdicts (decisions.md 2026-11-02, correction after seeing results). A note is added; the original wording stays visible.
  6. FILE(docs/status.md:15) lists "push" as an open owner item and as done ("pushed 2026-11-04"). Fixed in status.md.
  7. **For the owner (process.md, PROTOCOL.md and CLAUDE.md need the owner's approval to change):**
     - FILE(docs/process.md:121) says the manifest location is "the owner's decision", but it was decided: `manifests/runs.sha256` (decisions.md 2026-11-04 [OPS]).
     - PROTOCOL §5.1 states only the 2026-10-30 capacity rule, without item 42's rule for future sweeps.
     - CLAUDE.md rule H says "95 % Clopper–Pearson upper bound" without "one-sided"; process.md §5 makes one-sided the default.
- **Since when:** each since the date of the statement it corrects.
- **Which results it affects:** none. No verdict, μ or threshold uses these statements.
- **Re-check done:** `analysis.tables published`: no difference (previous entry).
- **Rule that would have caught it:** I (numbers only from committed functions, with their window), plus a docs pass at the end of each session (D).

## 2026-11-05 · [CORR] `derived.hit_between` gave a number when a counter went down
- **What was wrong:** FILE(analysis/derived.py:16) tested only `if dq`, so a negative difference (a counter reset) gave a number, while `load._level` gives NaN (REG-4).
- **Since when:** the function was committed (2026-11-04).
- **Fix:** NaN when the query counter does not rise or either counter goes down inside [a, b], as in `_level`. Test: `tests/test_derived.py::test_hit_between_is_nan_on_a_counter_reset_or_no_queries`.
- **Which results it affects:** none.
  - Every caller reads valid runs, and the `recorder` check fails any run with a counter decrease (FILE(harness/checks.py:83-93)).
  - Re-check: `analysis.recompute_published` prints identical output under the old and the new function (109 lines, compared in one process).
- **Rule that would have caught it:** J (one definition, one computation), with a reset test from the start.

## 2026-11-05 · [DECISION] Item 42's capacity rule implemented, for future sweeps only
- **The owner approved it on 2026-11-04** (decisions.md, items 38–42): the throughput test compares against the realized planned arrival rate over the measured window, not the configured λ. Past μ values stand as judged.
- **Code:**
  - `load.summarize` gains `planned_rate`: requests planned in [warm-up, end of arrivals) per second.
  - `load.capacity(..., against="rate" | "planned_rate")`; the default is the old rule.
  - `tables.capacity_rule(cfg)` reads a sweep's own `capacity:` block, else the 2026-10-30 rule.
  - `tables.sweep_capacity(parent)` refuses a sweep whose runs registered different rules.
  - Old configs are not edited, so every old sweep keeps the old rule.
  - Tests: `tests/test_load_more.py::test_capacity_against_the_realized_planned_rate` and two in `tests/test_tables.py`.
- **Re-check:** `analysis.tables published` reports no difference; every published μ is unchanged.

## 2026-11-05 · [REG] REG-7: feasibility gate for setup L1 (2048-token system prompt, 5 s gaps) before any shock matrix (GPU, ≤ 9 h)
- **ID:** REG-7. The owner chose the direction on 2026-11-05 (the audit [DECISION] above). **Not approved yet:** no GPU run before the owner approves this entry. Committed together with `analysis/gate.py`, `tests/test_gate.py`, the `capacity` changes in `analysis/load.py` and `analysis/tables.py`, and `configs/l1_base.yaml`, `sweep_l1_pc_on.yaml`, `sweep_l1_pc_off.yaml` and `stage2_l1_base.yaml`.
- **Question:** is there a setup and load where a stuck state is possible at all? It needs c_b(λ) < λ ≤ c_warm(λ): the cold, backlogged completion rate below λ while the warm server keeps up at λ (`docs/model.md` M2). At the default pool overload costs only 1 − 4.185 / 4.735 = 0.116 of capacity (DERIVED from M2's inputs), and every burst backlog drained.
- **Claim tested:** M2 (feasibility, `docs/process.md` §4), as the precondition of C1. Not C1 itself: one burst run is not a cell.
- **Setup L1:** the measured 5 s-gap setup (`configs/gap5_base.yaml`) with one factor changed, `system_tokens` 512 → 2048. Everything else stays: default pool, cap 256 stated, 8 turns, 128 user / 128 reply / 128 output tokens, exponential 5 s gaps, open-loop turns, no retries, gateway off.
  - Inputs from schedules (`harness.workload.build_schedule`, seed 1, 2400 s; inputs, not outcomes): W/C mean (`derived.working_set` / 96,656) is 0.38 at λ = 3 and 0.53 at λ = 4 (p90 0.52, 0.68), against 0.19–0.29 for the 5 s-gap setup at λ = 3–4.5.
  - Mean prompt 3070 tokens (1534 at 512). About 498 prompt tokens per request are left to prefill when warm.
  - Session median prompt 2944 tokens, max 3968.
- **Design:**
  - **G1:** `configs/sweep_l1_pc_on.yaml`, λ = 2, 3, 3.5, 4, 4.5, 5, 5.5, 6, 7. 900 s, seed 0, no dev mode (the run shape of every capacity sweep).
    - μ_warm by the rule in `configs/l1_base.yaml`: throughput ≥ 0.95 × the realized planned rate (item 42), waiting slope ≤ 0.01 req/s, and **monotone**: the highest rate that passes along with every lower swept rate (`load.capacity`, through `tables.sweep_capacity`).
    - Seed 0's realized rate is 2.4–7.1 % above λ at every L1 rate (the review, from schedules), so this rule asks for throughput ≈ 0.97–1.02 λ. That is item 42's intent.
  - **G2:** `configs/sweep_l1_pc_off.yaml`, λ = 1, 1.5, 2, 2.5, 3, 3.5, 4, the same shape with caching off. The sweep runs in full.
  - **Test load**, computed once after G1 and G2 by `gate.reg7_zone`:
    - μ_sat,off = `gate.cold_floor`. Drop rows with a non-finite value. λ_sat is the lowest λ with measured-window mean KV ≥ 0.85 (owner, decisions.md 2026-11-04). Every row at λ ≥ λ_sat must be saturated (KV ≥ 0.85 and throughput < 0.95 × planned_rate), else the floor is undefined (`not_monotone`). The floor is the mean throughput over ≥ 2 such rows, else `too_few`; with no saturated row it is `unsaturated`.
    - λ_test = `gate.choose_lambda`. Take the largest multiple of 0.5 that is ≤ 0.8 μ_warm and ≥ 1.3 μ_sat,off (`gate.zone_check`). Then step down by 0.5 until the G1 run at the smallest swept rate ≥ λ_test has pooled percent fast ≥ 0.98 at TTFT ≤ 1.0 s (`load._level` over 240–900 s; `gate.slo_feasible`), staying ≥ 1.3 μ_sat,off. Otherwise there is no λ_test.
  - **G3**, at λ_test: two runs of 2580 s, seed 1, extending `configs/stage2_l1_base.yaml` (dev mode, SLO 1.0 s, the verdict block of `stage2_cap_base.yaml`, `burst_min_kv_max: 0.95`). Their configs are written with exactly these contents and committed before they run:
    - `configs/stage2_control_l1_r<λ>.yaml`: `extends: stage2_l1_base.yaml`, `seed: 1`, `workload.rate: <λ_test>`, `verdict.control_t_s: 1080`. It is judged at the burst's end, so both watches end at 2580 s.
    - `configs/burst_l1_r<λ>_s1.yaml`: `extends: stage2_l1_base.yaml`, `seed: 1`, `workload.rate: <λ_test>`, `trigger: {kind: burst, at_s: 900, duration_s: 180, rate: <λ_test>, prompt_tokens: 2944}`.
    - Same seed and duration, so the same session schedule: the burst draws from its own generator (FILE(harness/workload.py:24-26)). Burst requests can't be mistaken for session requests: they are turn 0 with 2944 tokens, while a session's turn 0 is 2176 (`margin.check_burst_rule`).
- **Analysis plan** (`gate.gate_verdict`, settings `gate.REG7`). Spans are [600, 900), [900, 1200) and [1200, 1500) s after the burst's last planned arrival (1080 s).
  - A span **holds** in the burst run when `margin.post_trigger_margin` finds it qualifies: waiting > 0 at every scrape; no burst request completes in it; the sessions' cached share is ≤ the baseline's minus 0.06, over the 600 s before the burst. And the one-sided 99 % Poisson upper bound of its completions/s must be below **both** λ_test and the span's planned session rate λp.
  - A span **counts** when it holds and the control at the same absolute span is defined and not backlogged (waiting > 0 at every scrape there; `gate.control_backlog`).
  - **Labels:**
    - `inconclusive`: the control or the burst verdict is `unclear`, the burst run is `bad_baseline`, or a span needed for the decision is undefined. The pair is rerun under the stopping rule; this is never read as `drains`.
    - `control_not_healthy`: the control is defined but not `recovered`.
    - `pass`: some span counts.
    - `inconclusive` also when the burst run is `stuck` by `load.verdict` but no span counts. For example, burst requests may still be completing in every span, so none is burst-free. The span test could not confirm, so this is not read as a drain (pre-commit review, 2026-11-05; see the approval entry).
    - `drains`: otherwise.
    - The family error over 3 spans is ≤ 0.03 for the Poisson part.
  - **Readouts, reported:**
    - `gate.overlap_share` over [1080, 2580): the share of session cache hits served while the previous turn still ran. It decides the closed-loop proposal below.
    - Never decisive: `gate.secondary_cb` (`floor.sustained_capacity`, REG-6's settings), `derived.cached_share_split`, completions/s and percent fast per 60 s.
- **Prediction** (BELIEF, from M2 arithmetic; DERIVED: the default cache-off saturation 3.5 req/s × 1525 prompt tokens ≈ 5.3k prefill tokens/s, so c_off,L1 ≈ 5.3k / 3070 ≈ 1.7 req/s):
  - μ_sat,off ∈ [1.4, 2.2] (point 1.7), status `ok`; μ_off ∈ {1, 1.5, 2}; μ_warm ∈ [3, 6] (point 4.5).
  - λ_test exists with p ≈ 0.7 (point 3.5).
  - Given G3: `pass` ≈ 0.3, `drains` ≈ 0.45, `control_not_healthy` ≈ 0.1, `inconclusive` ≈ 0.15.
  - Overall `pass` ≈ 0.2.
- **Decision under each outcome:**
  - **No λ_test:**
    - With a floor status `ok`: L1 has no load clearly above its cold floor that is healthy when warm, so no shock matrix runs at L1. μ goes into M2, and the owner picks the next factor.
    - With a floor status `unsaturated`, `not_monotone` or `too_few`: the floor is *unmeasured*, not absent. A new registration extends or repeats G2.
  - **pass:** the shock matrix at λ_test, registered first: burst seeds 2–5, each with a same-seed, same-duration control. "Most" = ≥ 3 of 5, with the one-sided Clopper–Pearson bound. Then the condition-5/6 confirmation run, the caching-off control and the loop figure for C2.
  - **drains:**
    - Record c_b and 1 − c_b / μ_warm in M2.
    - If `overlap_share` > 0.5: propose closed-loop turns (a change to rule 2) to the owner as the next single factor.
    - Otherwise: propose writing up the negative with its mechanism.
  - **control_not_healthy:** one retry pair at λ_test − 0.5 if that is still ≥ 1.3 μ_sat,off; otherwise as "No λ_test" with status `ok`.
  - **inconclusive:** rerun the pair unchanged.
- **Alternatives:**
  1. Longer prompts also cut the warm capacity, by attention cost and fewer requests in the pool. The zone check measures this.
  2. Overlap protection may keep hits up in the backlog, so `drains` would not refute the loop for closed-loop traffic. The overlap share is measured, and it decides.
  3. Larger batches in a backlog may make up for the lost cache, as at the default pool. That gives `drains`.
  4. Dev mode is on in G3 and off in G1 and G2 (A6).
  5. One seed per G3 run: `pass` is a reason for a matrix, not a result.
  6. "Cold" follows from any long backlog (reuse gaps exceed eviction time), so `cold` alone does not separate causes. The matched control span does (review).
- **Stopping rule:**
  - Each sweep once; an invalid run is rerun unchanged, at most twice.
  - G3 at most at 2 λ_test values.
  - An `inconclusive` pair is rerun at most twice.
- **Cost:** G1 ≈ 3.0 h (9 runs); G2 ≈ 2.3 h (7 runs); G3 ≈ 1.7 h per pair. In total ≤ 9 GPU h without the inconclusive reruns.
- **Not changed:** every past verdict, μ and threshold. `capacity`'s new options are off by default, and the old sweeps have no `capacity:` block. Re-check: `analysis.tables published` reports no difference after the change.

### Adversarial review (separate subagent; it saw only the first draft, its diff and the code those call; it built schedules, which are inputs, and synthetic traces; it opened no runs). Verbatim:

> **1. Traces on which the verdict is wrong.**
> **A. False `pass` on a draining server (main defect).** `holds` compares `c_upper < λp(span)` where λp is the *span's own* planned rate, not λ. With the G3 schedule at λ_test=3.0 (seed 1, burst at 900 s), λp over the three spans = **2.737, 3.393, 2.977**; at 3.5: 3.17, **3.847**, 3.66; at 4.0: 3.65, **4.31**, 4.137. Exact `poisson_rate_upper(n,300,0.99)`: span 2 at λ=3.0 holds whenever c ≤ **3.143**. Trace: cold backlogged rate c_b = 3.10 > λ = 3.0 (no stuck state by M2); after the burst, Q ≈ 528+excess drains at ~0.1/s so Q>0 at every scrape; burst requests finish by ~1080+600/3.1 ≈ 1270 s so spans are burst-free; long queue pushes reuse gap past eviction ⇒ cold. Span 2 → holds → label `pass`. `load.verdict` likely says `stuck` too (end window [1980,2580) planned rate (3.393+2.977)/2 ≈ 3.19 > 3.10 ⇒ positive q slope). So the gate cannot distinguish c_b<λ from c_b<λ+~13 % schedule fluctuation; the 0.03 family error covers only Poisson noise on completions, not the choice of λp as target.
> **B. Control never judged where the burst run is.** Control verdict windows: end [1800,2400), prev [1200,1800). Burst spans: [1680,1980), [1980,2280), [2280,2580); end [1980,2580). Nothing judges the control on [2400,2580) — where the planned rate peaks at 4.017 (λ=3.5) / 4.422 (λ=4.0). A local overload there can make span 3 hold while the control reads `recovered`. `post_trigger_margin` raises on a run with no trigger, so no matched-span check of the control exists.
> **C. Missing data → `drains`.** Burst run verdict `unclear` (NaN from a scrape gap) or `bad_baseline`, with no span holding (NaN share/NaN baseline/no scrapes all make `holds` False) → `drains`. Neither case is tested; only `slow_drain`→`drains` is. A `drains` label then drives "write up the negative".
> **D. False `control_not_healthy`.** Control `unclear` for the same NaN reasons → `control_not_healthy` → retry at λ−0.5, which can then fail the 1.3×floor test → "No λ_test", from an instrument fault.
> **E. Zone check (run on the real functions).** μ_warm from an integer grid: `zone_check` → {2:None, 3:None, 4:3.0, 5:4.0, 6:4.5, 7:5.5} for μ_warm 2–7, μ_sat,off=1.7. **The predicted λ_test=3.5 cannot occur.** True capacity anywhere in [μ, μ+1) ⇒ λ_test at 0.6–0.8 of it. `cold_floor` averages *every* row ≥ λ_sat including unsaturated ones: synthetic sweep rates 1.5–3, KV ≥0.85 from 1.5, throughput 1.5/2.0/2.4/2.4 → μ_sat,off = 2.075, λ_test=3.0 at μ_warm=4; with the true plateau 2.4, 1.3×2.4=3.12 ⇒ no λ_test. Ran a similar trace: {mu_sat_off: 1.9375, lam_sat: 1.5, n: 4}. Non-monotone KV: one noisy row ≥0.85 at a low λ pulls λ_sat down; nothing checks that rows above are saturated. NaN counts as a run: throughput [NaN, 1.8] → n=2, mean 1.8 — `min_runs`=2 passes with one value; NaN `kv_mean` row silently skipped. Grid ceiling: if c_off,L1 ≥ 3, no row saturates → NaN → "No λ_test" (verified), a grid artifact that the decision reads as "L1 infeasible". `capacity` takes the max passing rate: λ=4 fails, λ=5 passes by noise ⇒ μ_warm=5, λ_test=4.0 above the failing rate.
> **2. Strongest alternative explanation per outcome.** *No λ_test*: G2 grid stops at 3, or the grid is too coarse (μ_warm 4 vs true 4.9), not evidence of no zone. *pass*: slow drain with c_b slightly above λ judged against a local λp up to 13 % above λ (trace A), or local overload in the control's unjudged tail (B). The "cold" criterion does not separate these: any long queue makes the cached share drop because reuse gaps exceed eviction time, so `cold` follows from backlog of any cause. *drains*: the burst did not push the server over (KV≥0.95 proves pressure, not loss of the sessions' cache); or burst-run verdict `unclear` (C); single seed (1/1 has 95 % upper bound near 1). *control_not_healthy*: the SLO, not capacity — G1's throughput rule says nothing about TTFT p98 ≤ 1.0 s with 2–4k-token prompts at 0.6–0.8 of capacity, and dev mode is on only in G3; or instrument NaN (D).
> **3. Can the run change a decision?** Yes, if "No λ_test" and `drains` are fixed as above: "No λ_test" stops the L1 shock matrix; `pass` starts the matrix at seeds 2–5. As drafted, `pass` is vulnerable to trace A, so it could commit ~8 h GPU on a false positive. The overlap-share > 0.5 branch under `drains` is not computable as written (see 4).
> **4. Code/config defects.** (1) `holds` vs `lam_p(span)` not λ (trace A); no check that the queue grows across spans. (2) Control/burst verdict windows differ (control at `control_t_s`=900, watch ends 2400; burst watch ends 2580); last 180 s of control unjudged. (3) `unclear`/`bad_baseline` burst verdicts → `drains`; `unclear` control → `control_not_healthy`; untested. (4) Overlap decision has no named function: "overlap share > 0.5 of post-burst cached share" — `cached_share_split` returns two means over the whole measured window [240,2580), not post-burst; no function returns an "overlap share". Choosing this computation after data is a threshold-after-data risk. (5) `cold_floor`: unsaturated rows averaged, NaN rows counted toward n, no monotonicity. (6) Grid: μ_warm integer grid ⇒ λ_test ∈ {3,4,4.5,5.5}; prediction inconsistent; λ_test = 4.5 has no G1 run at that rate. (7) Item-42 `planned_rate` in `summarize` = all requests with `t_planned` in [warmup, duration) / span: for sweeps this is the realized planned rate (warm-up excluded, no bursts in sweeps); it would include burst requests if ever applied to a burst run. With seed 0 the realized rate is **+2.4 % to +7.1 % above λ** at every L1 rate (on: 2.097, 3.124, 4.186, 5.217, 6.159, 7.171; off: 1.05, 1.606, 2.097, 2.638, 3.124), so the rule effectively requires throughput ≥ ~0.99–1.02 λ — near "zero shortfall". G3 uses seed 1, whose baseline at λ=3 is 3.153 — a different realized load from G1. (8) `is_burst_request` is safe: session turn 3 = 2944 tokens, but bursts have turn = 0 and session turn 0 = 2176; `check_burst_rule` holds. Verified turn-3 length set {2944}, burst turns {0}. (9) Burst requests (528–796 × 2944 tok ≈ 1.6–2.3 M prefill tokens) may still be finishing in span 1: at the predicted ~5.3k tok/s cold rate (BELIEF), the last burst completion approaches the span-1 start at 1680 s when c_b ≲ 1.5, so span 1 can fail burst-free; biases against `pass`, not toward it. (10) Errored requests count in λp but not in c → inflates `holds`. (11) `sweep_kv_table` fails on runs with empty metrics (`tables.sweep_table` skips them); duplicate valid runs at one rate double-weight the floor mean. (12) G3 control/burst configs are not in the diff — trigger keys, rate = λ_test, `control_t_s` unreviewed.
> **5. Recommended changes, most important first.** 1. `holds` must require `c_upper < λ` (configured) AND `< λp`, or a positive Q slope across the three spans jointly; register now. 2. Add a matched-span negative control: compute Q>0 / c_upper / share on the control at the same absolute spans, and require the control not to hold there (Q ≈ 0); judge the control at `control_t_s` = 1080 or extend it to cover [2400,2580). 3. Map burst-run verdict `unclear`/`bad_baseline` and NaN spans to a new `inconclusive` label (rerun under the stopping rule), never `drains`; map control `unclear` to `inconclusive` too. Add tests for each. 4. Fix `cold_floor`: require every row ≥ λ_sat to have KV ≥ 0.85 and throughput < 0.95×planned_rate; use finite rows only; extend G2 to 3.5 and 4, or register that a NaN floor means "unmeasured" rather than "infeasible". 5. Use 0.5-step G1 rates 2–7 (or interpolate μ_warm) and fix the λ_test prediction; make `capacity` monotone (highest λ with all lower rates passing). 6. Pre-register an SLO feasibility check before G3: percent fast ≥ 0.98 at TTFT 1.0 s in the G1 run at the rate ≥ λ_test; otherwise "control_not_healthy" is predictable from data in hand. 7. Write and test a named function for the overlap share over [burst end, duration), and register the 0.5 rule against it. 8. Commit G3 control/burst configs now (parametrized by λ_test) for review. 9. Count errored requests as completions or drop them from λp; make `sweep_kv_table` skip runs without metrics.

**Changed because of it:**
- **A:** `holds` needs c_upper below both λ_test and λp. A test reproduces trace A (c = 3.10, λ = 3.0, λp = 3.39 → does not hold).
- **B:** a matched-span negative control (`gate.control_backlog`); the control is judged at `control_t_s: 1080`; `gate_verdict` raises otherwise.
- **C and D:** a new `inconclusive` label for an `unclear` verdict on either run, a `bad_baseline` burst run, or undefined spans, with a test for each.
- **E, 4.5:**
  - `cold_floor` uses finite rows only, requires every row at λ ≥ λ_sat to be saturated, and refuses duplicate rates. Its four statuses are registered, and an undefined floor means "unmeasured".
  - G2 is extended to λ = 4.
- **E, 4.6:** G1 now uses 0.5 steps (2, 3, 3.5, …, 6, 7), `capacity` gains `monotone` (on for L1 only), and the prediction is restated.
- **Recommendation 6:** `gate.slo_feasible` and `gate.choose_lambda`, registered as part of the λ_test rule.
- **4.4 and recommendation 7:** `gate.overlap_share`, defined and tested, decides the closed-loop branch.
- **4.7:** item 42's rule stays as the owner approved it; the review's numbers on how strict it is are stated in Design.
- **Recommendation 8, modified:** the G3 configs' exact contents are registered above, and the files are committed before they run. λ_test is not known until G1 and G2 are done.
- **4.10, not changed:** an errored request fails `no_errors`, so the run is invalid and `gate_verdict` raises.
- **4.11:** `sweep_rows` skips runs without metrics, and duplicates raise.
- **4.9 is accepted as stated:** it biases against `pass`.
- Full suite after the changes: `uv run pytest`, 183 passed. `analysis.tables published`: no difference.

## 2026-11-05 · [DECISION] Owner approves REG-7; the data copies stay on the Mac; three wording fixes made
- **REG-7 approved** by the owner on 2026-11-05 ("I approve reg 7"), before any L1 run exists. Registered in commit `d1b360c`.
  - **One change made after the owner's message and before that commit** (no data existed): in the agent's pre-commit review, a burst run that `load.verdict` calls `stuck` while no span counts is now `inconclusive`, not `drains` (`gate.gate_verdict`; `tests/test_gate.py`).
  - **Reason:** with a very low c_b, burst requests can still be completing in every span. Then no span is burst-free and none can hold, and the old rule would have read a stuck server as a drain, which leads to "write up the negative".
  - It makes `pass` no easier. The owner is told of it in the same session.
- **Data copies:** the owner decided that the copies of `runs/` stay on the Mac ("its ok to mac have copies"). The agent reads this as: no copy off the Mac is required.
  - **Risk left open, stated and not loosened:** one machine is still a single point of failure. Status.md's Watch keeps it as a risk.
  - Any copy on the Mac can be checked with `python3 tools/manifest.py verify <copy>`.
- **Wording fixes approved by the owner ("fix words")**, from the 2026-11-05 [CORR] item 7:
  1. `docs/process.md` §9: the manifest is at `manifests/runs.sha256` (decided 2026-11-04 [OPS]), and the copy location is the owner's decision above.
  2. `PROTOCOL.md` §5.1: item 42's rule and the monotone reading for sweeps with a `capacity:` block, marked **[new 2026-11-05]**. Past μ values stand.
  3. `CLAUDE.md` rule H: "one-sided 95 % Clopper–Pearson upper bound", as in process.md §5.

## 2026-11-05 · [CORR] status.md's next action was not updated when REG-7 was approved, although commit `f4d1110` says it was
- **What was wrong:**
  - Commit `f4d1110`'s message says "status.md: next action is running REG-7 when the VM is back; push first".
  - FILE(docs/status.md:9) still read "Next action: the owner reviews and approves REG-7 … nothing from 2026-11-05 is committed yet".
  - Only the backup line of status.md changed in that commit (`git show f4d1110 -- docs/status.md`).
  - The agent also told the owner that status.md held the current plan before checking it.
- **Since when:** `f4d1110`, 2026-11-05.
- **Fix:** status.md's next action now holds the full ordered steps:
  - the read-only VM checks, including microk8s;
  - REG-6's recovery;
  - the A10 probe;
  - the microk8s decision;
  - `git pull`;
  - the start rule for G1: start when the checks are clean and the GPU is idle, and ask the owner first on anything unexpected;
  - REG-7's sequence;
  - REG-6 after the gate.
- **Which results it affects:** none. No run started, and REG-7's registration and approval in decisions.md were correct.
- **Rule that would have caught it:** D (session end): re-read status.md after editing it, before the commit message describes it.

## 2026-11-05 · [CORR] Two stale statements found at session start: model.md's REG-7 ledger row and status.md's push commit
- **What was wrong:**
  1. FILE(docs/model.md:70), ledger row 11 (REG-7), read "Not run (awaits the owner's approval)". The owner approved REG-7 on 2026-11-05 (decisions.md 2026-11-05 [DECISION] "Owner approves REG-7"). The row now reads "Not run (approved by the owner 2026-11-05, decisions.md; awaits the VM)".
  2. FILE(docs/status.md:9) read "Everything is pushed to `origin` at `e8bbca6`". `git rev-list --left-right --count main...origin/main` gives 0 0 with both at `1da6a73` (checked 2026-11-05, 11:2x UTC, after `git fetch`). Changed to `1da6a73`.
- **Since when:** (1) `f4d1110`, 2026-11-05, when REG-7 was approved and the ledger was not updated; (2) `1da6a73`, 2026-11-05, which was pushed after status.md named `e8bbca6`.
- **Which results it affects:** none. Neither statement is used by a verdict, μ, threshold or the order of the next steps.
- **Re-check done:** `python3 tools/check_docs.py`: OK before the change; rerun at session end.
- **Own slip, before commit:** this entry was first drafted with the date 2026-11-06; `date -u` gave 2026-11-05. Corrected before commit.
- **Rule that would have caught it:** D (session end): every doc that names a registration's state is updated with the approval (model.md's ledger as well as status.md), and status.md's push line is written after the last push.

## 2026-11-05 · [OPS] VM back: read-only checks; REG-6 seed 0 copied; why it went offline; where microk8s came from; A10 answered
- **Scope:** read-only commands over SSH as the user `chalshik`, with no sudo. Each output is saved in `docs/probe/20261105_vm_checks/` and cited below. 0 GPU h. Nothing on the VM changed except the removal of the copied run folder (below).
- **Why the VM went offline (2026-11-04 14:35 UTC):** an ACPI power-button event, not a crash. The log reads "Power key pressed short", then "System is powering down", at 14:35:45 (FILE(docs/probe/20261105_vm_checks/boots_and_shutdowns.txt:38-39)).
  - The two earlier mid-run losses end the same way: 2026-10-31 02:53:50 and 2026-11-01 15:41:07 (FILE(docs/probe/20261105_vm_checks/boots_and_shutdowns.txt:32-36)). So do three setup-day boots on 2026-10-23 (`:21-30`).
  - The VM came back at 2026-11-05 10:55:48 (`:13`).
  - BELIEF: in a Proxmox VM this event comes from the hypervisor (a "Shutdown" of the VM, or the host shutting down). A shell command in the VM logs no power-key line. Who sent it is not visible from inside the VM; the Proxmox task log would show it (owner).
  - **On the 2026-11-04 [OPS] entry:** it says the agent's stop command "never reached the VM". The journal shows SSH sessions from the Mac's Tailscale address at 14:32:35, 14:34:23 and 14:35:37, the last ending 7.4 s before the power key (FILE(docs/probe/20261105_vm_checks/shutdown_20261104.txt:3-14)). Which command each ran is not logged, so that statement can be neither confirmed nor refuted. It does not bear on the cause, which is the power-key event.
- **Repo:** clean (0 lines of `git status --porcelain`) at `4d30f1d` (FILE(docs/probe/20261105_vm_checks/repo_disk.txt:3-5)). The VM's `origin` is the bare repo `~/repos/aftershock-artifacts.git` on the VM itself, which the Mac pushes to as `vm`.
- **GPU and disk:** RTX 3090, 1 MiB used, 0 %, 420 W limit, no compute process (FILE(docs/probe/20261105_vm_checks/microk8s_now.txt:29-30)); 16 GB free (`repo_disk.txt`).
- **REG-6 seed 0 (`20261104-134159_long_pc_off_r3_s0`):**
  - It has no `checks.json`, so it does not count, as expected. Its last writes are at 14:35:44.86, 0.2 s before the power key.
  - Copied to the Mac with `rsync -a`. The sha256 of all 9 files is identical on both machines (`sha256sum` on the VM, `shasum -a 256` on the Mac, compared with `diff`).
  - `python3 tools/manifest.py update` appended 9 lines and left the 1053 earlier lines unchanged. Its line in `manifests/pending_copy.txt` is removed.
  - The VM copy is removed, under the owner's exception (decisions.md 2026-11-04).
  - `runs/` now holds 105 folders. The new one is the third without checks.
- **microk8s: where it came from.** It was installed automatically during the VM's very first boot, before anyone logged in.
  - The journal starts at 2026-10-23 11:48:36 (FILE(docs/probe/20261105_vm_checks/boots_and_shutdowns.txt:4)). The OS was installed just before from the Ubuntu Server 24.04.5 ISO (FILE(docs/probe/20261105_vm_checks/microk8s_install.txt:3), `/` born 11:35:45, `:13`).
  - snapd started at 11:48:46. At 11:48:48 it logged `Installing snap "microk8s"`, a request through its API (`:26-27`). The snap file landed at 11:49:32 (`:9`). The first login session is at 11:51:28 (`:30`).
  - So no user session existed when the install was requested. Two of the three earlier explanations are ruled out: the other GPU user, and a manual install by the owner or an agent session.
  - BELIEF, the remaining explanation: microk8s was ticked on the installer's "featured server snaps" screen, and the installer had it installed on first boot. The decisive file, `/var/log/installer/autoinstall-user-data`, is readable only by root (owner: `sudo grep -n -A4 snaps /var/log/installer/autoinstall-user-data`).
- **microk8s: what it does.** It is unused.
  - The `microk8s` group has no members, and no `~/.kube` exists (`microk8s_install.txt:32-34`).
  - Over all 10 boots, kubelite's journal names only the three default `kube-system` pods (calico-node, calico-kube-controllers, coredns) and never mentions nvidia (`microk8s_now.txt:23-26`). So no GPU addon pod has ever run.
  - Its CPU use, as `ps` pcpu (CPU time over elapsed time since this boot): kubelite 4.3 %, k8s-dqlite 1.4 %, calico-node 1.3 %, containerd 0.9 % of one core (`microk8s_now.txt:6-9`). DERIVED: about 8 % of one core, unpinned, so it can run on the loadgen and recorder cores 6–7.
  - It was present for all 104 earlier runs.
  - It bears on A7 only partly. The kubelite log rules out a GPU pod. It cannot rule out a GPU process outside Kubernetes.
- **A10, the scheduler limits:**
  - `analysis/engine_config.py` (`a10_table`, tests in `tests/test_engine_config.py`) reads every run's `server.log`.
  - The unlogged defaults were read from the installed wheel (FILE(docs/probe/20261105_vm_checks/scheduler_source.txt)).
  - Answer in open-questions A10.
- **Not done, needs the owner:**
  - whether microk8s is stopped during runs;
  - the root-only installer check;
  - who sent the three power-key events (Proxmox task log).
  G1 does not start before the microk8s decision (status.md step 4).

## 2026-11-05 · [DECISION] VM evidence kept as committed files; `analysis/engine_config.py` added for A10 (agent, within its authority)
- **VM outputs as files:** journal, snap and `ps` output from the VM fits none of rule B's tags, and a chat transcript is not evidence. So each read-only check's output is saved under `docs/probe/20261105_vm_checks/` and cited as `FILE(path:line)`. Future VM checks follow the same pattern: one dated folder, one file per check, a capture time in the first line, and no secrets.
- **`analysis/engine_config.py`:**
  - `engine_settings` reads one run's `server.log`: the non-default args, chunked prefill, compile ranges and async-off warnings.
  - `scan` and `a10_table` apply it to every run folder.
  - It is descriptive of configuration, not of outcomes, so it needs no `[REG]`. Tests: `tests/test_engine_config.py` (3).
  - Its async-off pattern covers every disabling message in the installed vLLM 0.32.0, `config/vllm.py:1559-1639`.
- **Not done:** repointing the Mac's `vm` git remote to the Tailscale address. The permission system refused it, so the remote keeps the home address.
- **Re-check:** `uv run pytest`: 186 passed. `python3 tools/check_docs.py`: OK.

## 2026-11-05 · [DECISION] microk8s disabled on the VM for every later run (study owner)
- **Owner's decision:** "I allow you to run it", answering the agent's recommendation to disable microk8s before G1 for every later run, REG-7 and REG-6 alike. The agent could not run it: sudo needs a password (`sudo -n`). So the owner ran `sudo snap disable microk8s` at 11:51:08 and again at 11:51:42 UTC, then the installer grep at 11:51:42 and `reboot` at 11:52:47 (FILE(docs/probe/20261105_vm_checks/sudo_log.txt:4-7)). The services stopped at 11:51:09 (FILE(docs/probe/20261105_vm_checks/microk8s_disabled.txt:30-36)).
- **Leftovers, found by the agent:** after the disable, all 8 services were disabled and inactive. The pods' processes still ran, though: calico-node, coredns, kube-controllers, 3 containerd-shim and 3 pause (FILE(docs/probe/20261105_vm_checks/microk8s_disabled.txt:16-28)), and calico's network links `vxlan.calico` and two `cali*` were still up. The agent asked for a reboot rather than start G1 in a state no earlier run had and no boot would reproduce. The owner rebooted at 11:52:47 UTC (FILE(docs/probe/20261105_vm_checks/sudo_log.txt:7)).
- **State after the reboot** (FILE(docs/probe/20261105_vm_checks/after_reboot.txt)):
  - microk8s is `disabled`, and all its services are disabled and inactive.
  - There are no k8s, containerd or calico processes and no CNI links. 255 processes in all, against 437 before.
  - GPU: 1 MiB, 0 %, 36 °C, no compute process. Repo clean at `10d233c`. 16 GB free. Nothing listens on port 8000.
- **Consequence for comparisons:**
  - All 104 runs before 2026-11-05 ran with microk8s active, at about 8 % of one core, unpinned (decisions.md [OPS] 2026-11-05).
  - Every later run has it disabled: REG-7's G1–G3 and REG-6's reruns.
  - REG-7 measures its own μ, so its internal comparisons are unaffected.
  - REG-6's `[RESULT]` must state this difference from the 2026-10-30 cache-off sweep it helps to interpret.
  - `env.json` records neither state. Adding the snap services list to `harness/env_snapshot.py` is a harness change and is left to the owner.
- **Reversible:** `sudo snap enable microk8s`.
- **Still open:** the owner ran the installer check (`grep -n -A4 snaps /var/log/installer/autoinstall-user-data`, sudo log 11:51:42), but its output is not yet in the record. So "chosen in the installer" stays BELIEF.

## 2026-11-05 · [OPS] REG-7 G1 done: 4 of 9 runs valid; λ ≥ 5 invalid from SW-thermal slowdown
- **Ran:** `configs/sweep_l1_pc_on.yaml`, 11:57:49–14:37 UTC, from `8ef814f` with a clean tree, microk8s disabled and the VM up throughout. All 9 folders were copied to the Mac with identical sha256 (`shasum` against `sha256sum`), and `tools/manifest.py update` appended 90 lines. The VM keeps its copies.
- **Validity** (FILE(runs/<id>/checks.json), `gpu_steady` and `no_errors` details):
  - Valid: `20261105-115752_sweep_l1_pc_on_r2`, `20261105-121403_sweep_l1_pc_on_r3`, `20261105-123008_sweep_l1_pc_on_r3.5` and `20261105-124617_sweep_l1_pc_on_r4`. Max 75–77 °C, SW-thermal share ≤ 0.015.
  - `20261105-130250_sweep_l1_pc_on_r4.5`: INVALID, `no_errors`. One request (id 2580, t_planned 620.6 s) got `ServerDisconnectedError: Server disconnected`; 4027 were ok. `server.log` has no error or warning near that time. The cause is unknown. BELIEF: a client-side connection reset; no earlier run had a client error.
  - `20261105-132035_sweep_l1_pc_on_r5`, `20261105-134018_sweep_l1_pc_on_r5.5`, `20261105-140120_sweep_l1_pc_on_r6` and `20261105-142221_sweep_l1_pc_on_r7`: INVALID, `gpu_steady`. SW-thermal share 0.098 / 0.165 / 0.103 / 0.177 against the 0.05 limit. Max 81–82 °C, no HW throttle sample.
- **Observed, not yet from a committed function:** an inline split of `gpu.jsonl` by quarter of [240, 900) showed the SW-thermal flag in every quarter at λ = 5 and 5.5, with the GPU at 78–79 °C by t = 240 s. The numbers are not quoted until a committed function gives them. BELIEF from it: at these loads the slowdown is the steady state, so a cool-down before a rerun is unlikely to help.
- **Against earlier sweeps:** they peaked at 79–83 °C with SW-thermal share ≤ 0.038 and stayed valid, e.g. `20261103-132357_sweep_gap5_pc_on_r7` at 83 °C and 0.038 (FILE(runs/20261103-132357_sweep_gap5_pc_on_r7/checks.json)). So core temperature alone does not explain the L1 failures.
  - Alternatives, unchecked: memory (GDDR6X) heat from L1's heavier traffic; a warmer room; sustained draw at the 420 W cap.
  - The flag rule is not loosened (status.md, Watch).
- **Not computed:** throughput and μ of any G1 run. REG-7 computes the gate once, after G1 and G2.
- **Not started:** G2. Its cold floor needs ≥ 2 valid saturated runs, and cache-off L1 is the heavier load, so the same heat failure is likely. The owner decides first how the heat is handled (status.md).

## 2026-11-05 · [CORR] REG-7's monotone μ_warm rule does not say what an invalid rate means; the code skips it
- **What was wrong:**
  - REG-7 (decisions.md 2026-11-05 [REG]) defines μ_warm as "the highest rate that passes along with every lower swept rate".
  - The code applies this to valid runs only: `tables.sweep_capacity` keeps `valid` rows (FILE(analysis/tables.py:108)), and `load.capacity(monotone=True)` sees only those.
  - An invalid rate is therefore dropped, and the chain runs over it. With G1's validity (λ = 4.5–7 invalid), any valid passing rerun above λ = 5.5 could set μ_warm over rates with no valid run.
  - The registration never stated the case; the agent wrote both the registration and the code.
- **Since when:** `d1b360c` (REG-7).
- **Which results it affects:** none yet. No μ for L1 has been computed.
- **Fix, proposed, needs the owner's approval** (it changes analysis registered in REG-7):
  - A swept rate with no valid run after the reruns REG-7 allows ends the monotone chain. μ_warm is the highest rate below the first rate that fails or has no valid run.
  - Code and a test would follow before any μ is computed.
  - The choice is made knowing only which runs are valid, not any throughput.
- **Rule that would have caught it:** F. The adversarial review built traces with failing rates, not with missing ones; a review should also feed the rule an invalid row.

## 2026-11-05 · [DECISION] Monotone-rule fix approved and implemented; GPU cooling improved; G1's invalid rates rerun unchanged in two parts
- **Owner:** "approve fix capcity rule … gpu I have enhanced cooling". The agent reads the cooling change as the owner's choice of option 1: improve the cooling, then rerun the invalid G1 rates unchanged, as REG-7's stopping rule allows (at most twice each).
- **Fix** (the [CORR] entry above):
  - `load.capacity(..., monotone=True, swept_rates=...)`: a swept rate with no valid run ends the chain. Two valid runs at one rate, or a rate that was not swept, raise.
  - `tables.sweep_table` records each run's saved `sweep.rates`. `tables.sweep_capacity` passes their union over every run of the parent, valid or not.
  - The non-monotone rule, used by every sweep before REG-7, is unchanged.
  - Tests: four in `tests/test_tables.py`, including the trace "λ = 4 invalid, λ = 5 valid and passing → μ = 3, not 5".
  - Re-check: `uv run python -m analysis.tables published` reports no difference, and `uv run pytest` gives 190 passed.
  - The fix was made knowing only which G1 runs are valid; no G1 throughput or μ was computed. That `published` output prints μ only for the three old setups.
- **Cooling:** the owner improved the GPU cooling (details are not recorded). At idle the GPU reads 37 °C with the fan at 0 %, against 35–36 °C idle this morning (FILE(docs/probe/20261105_vm_checks/after_cooling.txt)), so idle readings cannot show the change. The reruns test it.
- **Reruns, the first allowed rerun of each rate:**
  - `configs/sweep_l1_pc_on_rerun1a.yaml`: λ = 4.5 and 5.
  - `configs/sweep_l1_pc_on_rerun1b.yaml`: λ = 5.5, 6 and 7.
  - Both extend `sweep_l1_pc_on.yaml` and keep `name: sweep_l1_pc_on`. Every resolved per-run config equals the original apart from the `sweep` list, seed 0 included (checked with `harness.run.expand`).
  - **Order rule, set before either part runs:** part b starts only if part a's λ = 5 run passes `gpu_steady`. Otherwise the agent stops and the owner decides, because further runs at higher load would most likely fail the same way.
  - This decides only whether to spend GPU time, from a validity check. No outcome is read.
- **G2** waits until G1 is complete or the owner decides otherwise.

## 2026-11-05 · [CORR] Commit `a0284e0` included `analysis/analysis.ipynb`, which the agent did not change
- **What was wrong:** the agent staged with `git add -A configs docs analysis tests`. That picked up `analysis/analysis.ipynb`, re-executed outside the agent at 15:28:46 UTC (file mtime; 206 lines added, 163 removed, mostly cell outputs and execution counts). It was committed in `a0284e0` together with the capacity-rule fix.
- **Since when:** `a0284e0`, 2026-11-05.
- **Which results it affects:** none.
  - Notebook output is not provenance (rule I).
  - Its new outputs contain no 2026-11-05 run id and nothing from setup L1 (checked with `git show a0284e0 -- analysis/analysis.ipynb`), so no G1 outcome was exposed.
  - Run validity is unaffected: the VM's tree is clean, and the configs are committed.
- **Not done:** the change is neither reverted nor rewritten out of history (`a0284e0` is pushed). The file holds the owner's working state, so whether it stays is the owner's call.
- **Rule that would have caught it:** stage files by name, never a whole directory, and read `git status --short` before committing.

## 2026-11-05 · [OPS] G1 rerun part a: λ = 4.5 and 5 both valid after the cooling change; part b started
- **Runs** (from `49a6fa1`, clean; `configs/sweep_l1_pc_on_rerun1a.yaml`, 15:33–16:10 UTC):
  - `20261105-153307_sweep_l1_pc_on_r4.5`: VALID. Max 79 °C, SW-thermal share 0.000 (FILE(runs/20261105-153307_sweep_l1_pc_on_r4.5/checks.json)).
  - `20261105-155052_sweep_l1_pc_on_r5`: VALID. Max 78 °C, SW-thermal share 0.000 (FILE(runs/20261105-155052_sweep_l1_pc_on_r5/checks.json)). In the first pass it was 81 °C and 0.098, invalid.
  - The schedules match the first pass: 4028 and 3443 scheduled requests (`events.jsonl` `schedule_written`; seed 0 unchanged).
- **Copied** to the Mac with identical sha256. The manifest gained 20 lines.
- **Order rule applied** (decisions.md 2026-11-05 [DECISION]): λ = 5 passed `gpu_steady`, so part b (`configs/sweep_l1_pc_on_rerun1b.yaml`: λ = 5.5, 6, 7) started at 16:11:23 UTC from `49a6fa1`.
- Observed only, not a test of a cause: the cooling change and the end of SW-thermal slowdown at λ = 5 coincide. The first-pass alternatives (memory heat, room temperature) are not separated.
- **Not computed:** throughput and μ.
- **The owner on the notebook in `a0284e0`:** "no problem". It stays in git.

## 2026-11-05 · [DECISION] G1 rerun part b: λ = 5.5 valid, λ = 6 and 7 invalid again; second rerun of λ = 6, then λ = 7 only if λ = 6 is valid (agent, within REG-7's stopping rule)
- **Part b** (`configs/sweep_l1_pc_on_rerun1b.yaml`, from `49a6fa1`, 16:11–17:14 UTC; copied with identical sha256, manifest +30 lines):
  - `20261105-161123_sweep_l1_pc_on_r5.5`: VALID. Max 77 °C, SW-thermal 0.000.
  - `20261105-163225_sweep_l1_pc_on_r6`: INVALID, `gpu_steady`. SW-thermal 0.055 against 0.05, max 81 °C. It started right after λ = 5.5.
  - `20261105-165327_sweep_l1_pc_on_r7`: INVALID, `gpu_steady`. SW-thermal 0.171, max 82 °C.
  - (FILE(runs/<id>/checks.json) for each.) G1 now has a valid run at every rate from 2 to 5.5.
- **Why a second rerun can change a decision** (rule A1):
  - Under the monotone rule as fixed today, μ_warm ≤ 5.5 unless λ = 6 has a valid run.
  - λ_test ≤ 0.8 μ_warm, rounded down to a multiple of 0.5: 4.0 at μ_warm = 5.5, 4.5 at 6, 5.5 at 7 (DERIVED: 4.4 → 4.0, 4.8 → 4.5, 5.6 → 5.5). So valid runs at λ = 6 and 7 can change λ_test.
  - λ = 7 matters only if λ = 6 is valid, so λ = 6 runs alone first.
- **Prediction** (BELIEF): P(λ = 6 valid) ≈ 0.5. It missed by 0.005 after a hot start. P(λ = 7 valid | run) ≈ 0.2, since 0.171 is far above the limit both times.
- **Plan:**
  - The second, last allowed rerun of λ = 6 is `configs/sweep_l1_pc_on_rerun2a.yaml`, started after the GPU has cooled to idle (≤ 45 °C), as part a did. The start temperature is an operating condition, not a config setting; the check is unchanged.
  - Then `configs/sweep_l1_pc_on_rerun2b.yaml` (λ = 7) only if λ = 6 is valid.
  - A rate still invalid after this ends the monotone chain, and G1 is closed.
  - Every resolved per-run config equals the original apart from the `sweep` list (checked with `harness.run.expand`).
- **Cost:** about 0.35 GPU h, plus 0.35 h for λ = 7.

## 2026-11-05 · [OPS] G1 closed: λ = 6's second rerun invalid (SW thermal 0.159); λ = 7 not rerun; G2 waits for the owner
- **Run:** `20261105-171648_sweep_l1_pc_on_r6` (`configs/sweep_l1_pc_on_rerun2a.yaml`, from `5a5eeb9`, 17:16–17:38 UTC, started with the GPU idle at 38 °C): INVALID, `gpu_steady`. SW-thermal share 0.159, max 81 °C (FILE(runs/20261105-171648_sweep_l1_pc_on_r6/checks.json)). Copied with identical sha256.
- **Prediction miss:** the [DECISION] entry before this run gave P(valid) ≈ 0.5. λ = 6's three shares are 0.103, 0.055 and 0.159, so the single near-miss did not predict the next run.
- **Observed, not from a committed function:** an inline count over [240, 900] gave the GPU at 80 °C by t = 240 s despite the cold start. BELIEF from it: a cold start does not help at this load.
- **G1 closed, by the rules registered beforehand:**
  - λ = 6 has had both allowed reruns, so by the monotone rule as fixed today the chain ends below it.
  - λ = 7 is not rerun (its rerun was conditional on λ = 6 being valid).
  - Valid G1 runs, one per rate:
    - `20261105-115752_sweep_l1_pc_on_r2`, `20261105-121403_sweep_l1_pc_on_r3`, `20261105-123008_sweep_l1_pc_on_r3.5` and `20261105-124617_sweep_l1_pc_on_r4` (first pass);
    - `20261105-153307_sweep_l1_pc_on_r4.5` and `20261105-155052_sweep_l1_pc_on_r5` (rerun 1a);
    - `20261105-161123_sweep_l1_pc_on_r5.5` (rerun 1b).
- **Consequence, stated before any μ is computed:** μ_warm ≤ 5.5, so λ_test ≤ 4.0. The heat limit is reported as "rates ≥ 6 unmeasured (SW-thermal slowdown)", not as capacity.
- **G2 not started.** The agent recommends more cooling first. Cache-off runs at and above saturation keep the GPU as busy as cache-on λ = 6–7, which failed 4 of 5 times, and the cold floor needs ≥ 2 valid saturated runs. The owner decides between more cooling, running G2 as is with the allowed reruns, or a power-limit amendment.

## 2026-11-05 · [DECISION] G2 stopped by the owner after 2 heat-invalid runs; retry after cooling, λ = 1 first
- **First pass of G2** (`configs/sweep_l1_pc_off.yaml`, from `dccd8ab`, started 17:42 UTC after the owner's added cooling):
  - `20261105-174215_sweep_l1_pc_off_r1`: INVALID, `gpu_steady`. SW-thermal 0.062, max 82 °C.
  - `20261105-175822_sweep_l1_pc_off_r1.5`: INVALID, `gpu_steady`. SW-thermal 0.135, max 82 °C.
  - (FILE(runs/<id>/checks.json).)
  - `20261105-181511_sweep_l1_pc_off_r2`: stopped at t = 246.7 s on the owner's instruction (`events.jsonl` `aborted`). No `checks.json`, so it never counts.
  - All three were copied with identical sha256; the manifest gained 29 lines.
- **Owner:** "lets stop everything, I will check coolig and let gpu cool down, after 15 minutes retry invalid ones". Stopping the registered sweep before it ran in full is a deviation from REG-7 ("the sweep runs in full"), made by the owner.
- **Retry plan:**
  - At ≥ 15 min after the stop (18:20 UTC) and with the GPU idle at ≤ 45 °C: `configs/sweep_l1_pc_off_rerun1a.yaml` (λ = 1), the first rerun.
  - Only if it passes `gpu_steady`: `configs/sweep_l1_pc_off_rerun1b.yaml` (λ = 1.5–4). That is the first rerun of 1.5 and 2, and the first run of 2.5–4.
  - Otherwise stop and ask the owner. If the lightest load still throttles, the heavier ones would too.
  - Every resolved per-run config equals the original apart from the `sweep` list (checked with `harness.run.expand`).
- **Not retried:** cache-on λ = 6, which has had both allowed reruns, and λ = 7, whose rerun was conditional on λ = 6.
- **Reading of the cold-floor rule, stated before any G2 run is valid or read:** `gate.cold_floor` uses valid runs only. If the lowest saturated rate has no valid run, λ_sat is the lowest *valid* saturated rate. The floor stays a mean over ≥ 2 valid saturated runs, else `too_few`. Unlike the monotone μ chain, a missing rate can't make the floor rest on an unmeasured rate. Recorded so the owner can object; no code change.

## 2026-11-05 · [CORR] The agent's launch command (`… | tee`) left the vLLM server running when the sweep was stopped
- **What was wrong:**
  - The agent started every sweep today as `tmux new-session … "uv run python -m harness.run <cfg> 2>&1 | tee -a <log>"`.
  - The owner's stop was a Ctrl-C to that tmux session. It also killed `tee`.
  - The harness logged `aborted` and `gpu_processes_end` (FILE(runs/20261105-181511_sweep_l1_pc_off_r2/events.jsonl)), then died before `_stop(server, …)` (FILE(harness/run.py:204)). So `vllm serve` was left running as an orphan (parent PID 1), holding the GPU and port 8000.
  - BELIEF: its next print hit the broken pipe.
  - The agent found it in the check after the stop, sent SIGTERM to its process group, and confirmed that no process was left, the GPU was free (1 MiB) and port 8000 was closed. The server log ends with "Application shutdown complete".
- **Since when:** today's first launch (G1, 11:57 UTC). No earlier stop hit it.
- **Which results it affects:** none. The stopped run never counts, and every finished run stopped its server normally.
- **Fix, operational:** launches now redirect to a file (`> <log> 2>&1`), with no pipe.
- **Proposed to the owner, not done:** make the harness's event print tolerant of a closed stdout. That is a harness change.
- **Rule that would have caught it:** test the stop path of the exact launch command before relying on it.

## 2026-11-05 · [OPS] G2 retry: λ = 1 invalid again (SW thermal 0.097); stopped by the pre-set rule, the owner decides
- **Run:** `20261105-184607_sweep_l1_pc_off_r1` (`configs/sweep_l1_pc_off_rerun1a.yaml`, from `9b6075f`, 18:46–19:02 UTC). It started after the owner's cooling check, with the GPU idle at 44 °C; it had been 37 °C at 18:22.
  - INVALID, `gpu_steady`: SW-thermal share 0.097, max 83 °C (FILE(runs/20261105-184607_sweep_l1_pc_off_r1/checks.json)). In the first pass it was 0.062 and 82 °C.
  - It stopped normally (`events.jsonl` `stopped`): the launch had no `tee`, and no process was left.
  - Copied with identical sha256; the manifest gained 10 lines.
- **Rule applied:** part b (`configs/sweep_l1_pc_off_rerun1b.yaml`) is not started, because λ = 1 did not pass `gpu_steady`.
- **State of G2:** no valid run at any rate. λ = 1 has had 1 of its 2 allowed reruns. λ = 1.5 and 2 have had none (2 was stopped), and 2.5–4 have never run.
- **Observed** (inline reading of `gpu.jsonl`, not a committed function): mean core temperature in the window was about 72 °C, with peaks of 83 °C. So the slowdown at the lightest cache-off load comes in spikes, not a high steady temperature. BELIEF: a sensor we do not record (memory or hotspot) trips the slowdown. This is not separated from room temperature or airflow.

## 2026-11-06 · [DECISION] G2: the second and last allowed rerun of λ = 1 (owner); λ = 1.5–4 only if it passes
- **Owner:** "rerun it again", after the agent laid out three options (power-limit amendment, recommended; more cooling and λ = 1's last rerun; stop L1).
- **Run:** `configs/sweep_l1_pc_off_rerun1a.yaml` again, unchanged (λ = 1). This is the second rerun of λ = 1, the last REG-7 allows. The config is identical to its use at 18:46 UTC; reusing an unchanged config is not an edit.
- **Rule, as before:** `configs/sweep_l1_pc_off_rerun1b.yaml` (λ = 1.5–4) starts only if this run passes `gpu_steady`. Otherwise stop, and the owner decides.
- **Prediction** (BELIEF): P(valid) ≈ 0.2. Earlier shares were 0.062 and 0.097, the GPU idles at 45 °C (35–37 °C yesterday morning), and the cooling has not changed since the last try.
- **Decision under each outcome:** valid → part b (about 1.7 h). Invalid → no rerun left at λ = 1, and the floor needs the higher rates, which would throttle as well (BELIEF). So the owner decides between the power-limit amendment and stopping L1.
- **Cost:** about 0.27 GPU h.

## 2026-11-06 · [OPS] G2 λ = 1 last rerun invalid (SW thermal 0.135); no rerun left at λ = 1; part b not started
- **Run:** `20261106-063534_sweep_l1_pc_off_r1` (`configs/sweep_l1_pc_off_rerun1a.yaml`, from `946c4ac`, 06:35–06:52 UTC, GPU idle at 45 °C at the start). INVALID, `gpu_steady`: SW-thermal share 0.135, max 83 °C (FILE(runs/20261106-063534_sweep_l1_pc_off_r1/checks.json)). It stopped normally, and the copy has identical sha256.
- **Prediction:** P(valid) ≈ 0.2. The run was invalid, as expected more likely than not.
- **λ = 1 across 3 runs:** 0.062, 0.097, 0.135. No further rerun is allowed (REG-7 stopping rule).
- **State of G2:** no valid run at any rate, so the cold floor is unmeasured. λ = 1.5 and 2 each have both reruns left (2 was stopped); 2.5–4 have never run.
- **Per REG-7's decision table**, an unmeasured floor is "unmeasured, not absent", and "a new registration extends or repeats G2". The agent recommends that registration be the power-limit amendment, with G1 repeated at the same limit. The owner decides.

## 2026-11-06 · [DECISION] Owner chooses a power-limit amendment for L1 (350 W); `power_limit` check approved; a knob added after `defaults.yaml` lives only in the configs that use it
- **Owner:** "Alright lets try to power cap", after the agent laid out three options (cap with G1 and G2 repeated; more cooling at 420 W and G2 continued; stop L1) and recommended the cap. The agent proposed 350 W; the value is part of REG-8 (next entry), which the owner approves or changes.
- **Rule conflict found and reported before going on** (CLAUDE.md D): `harness/CLAUDE.md` said new knobs go in `configs/defaults.yaml`, and `defaults.yaml` says it is never edited once used (rule 5). It has been used by every run since 2026-11-04 (one commit, `677559d`).
- **Owner:** "option 1, power limit check approved".
  - Option 1: the new keys (`expected_power_limit_w`, `power_limit_tol_w`) live only in the configs that use them, and `harness/checks.py` reads them with `.get`, so a missing key means "not checked". Every earlier run and config is unaffected. `harness/CLAUDE.md` now says so.
  - The `power_limit` check (`harness/checks.py`, 7c): every `gpu.jsonl` sample must show the expected enforced limit within the tolerance; no samples fail it. Tests: `tests/test_checks.py::test_power_limit`, `::test_power_limit_is_skipped_without_the_key`.
- **Not the agent's change, left alone:** `.gitignore` gained the line `docs/potential_gaps.md` at 19:35 today, outside the agent. It is neither committed nor reverted by the agent.

## 2026-11-06 · [CORR] `gate.sweep_rows` crashed on a sweep with no valid run (REG-7 code)
- **What was wrong:** `sweep_rows` built its table from a list of rows without column types. With no rows, the numeric columns were `object`, and `gate.cold_floor` raised a `TypeError` in `np.isfinite` instead of returning an unmeasured floor. Found by a smoke call of `gate.reg8_g1_may_start` before any 350 W run exists.
- **Since when:** `d1b360c` (REG-7). The agent wrote the code.
- **Which results it affects:** none. No gate has been computed, and REG-7's computation with rows is unchanged.
- **Fix:** the numeric columns are typed `float` even with no rows. Test: `tests/test_gate.py::test_sweep_rows_of_an_empty_sweep_gives_an_unmeasured_floor`.
- **Rule that would have caught it:** test each function on an empty input, as REG-4 did for windows.

## 2026-11-06 · [REG] REG-8: REG-7's feasibility gate for setup L1, repeated at a 350 W GPU power limit (GPU, ≤ 8.3 h without reruns)
- **ID:** REG-8. **Not approved yet:** no GPU run before the owner approves this entry.
- **Why:** REG-7 ended with no valid G2 run. λ = 1 was invalid in all three allowed runs, from SW-thermal slowdown (shares 0.062, 0.097, 0.135 against 0.05; decisions.md [OPS] 2026-11-06). By REG-7's decision table, an unmeasured floor means "a new registration extends or repeats G2". The owner chose a power-limit amendment (decisions.md 2026-11-06 [DECISION]).
  - Observed, from an inline reading of `gpu.jsonl` over [240, 900) s (not a committed function, so not quoted as a result): in all 19 L1 runs, the median busy power draw was 415–418 W against the 420 W limit. The power-cap throttle flag (0x4, which `gpu_steady` ignores) was set in 0.79–1.00 of samples. Busy SM-clock CV was 0.007–0.019. So the GPU sat at its limit at every rate, cache on or off.
- **Question:** the same as REG-7's: is there a load in setup L1 with c_b(λ) < λ ≤ c_warm(λ) (`docs/model.md` M2)? Here, at a 350 W power limit.
- **Claim tested:** M2 (feasibility), as the precondition of C1. Not C1 itself. A `pass` supports "a stuck state is possible at 350 W" only.
- **Setup L1 at 350 W:** every setting of REG-7's L1 configs, unchanged, plus a power limit of 350 W set by the owner on the VM (`sudo nvidia-smi -pl 350`; root is needed, open-questions S3).
  - The configs differ from REG-7's only by two check settings, `checks.expected_power_limit_w: 350` and `checks.power_limit_tol_w: 1.0`, in `configs/l1_pl350_base.yaml` and `configs/stage2_l1pl350_base.yaml`. Checked with `harness.run.expand` and `with_defaults`: every resolved per-run config equals its REG-7 counterpart apart from `name`, `sweep_parent`, `sweep` and these two keys; seed 0 unchanged. The review confirmed it independently.
  - Check `power_limit` (`harness/checks.py`, 7c; owner-approved 2026-11-06): every `gpu.jsonl` sample must show an enforced limit within 1 W of 350. No samples, or a sample without a value, fail it. GPU samples are written on every recorder tick, and the existing `recorder` check fails a run with a gap over 2 s, so coverage is checked there.
  - The GPU is shared, and the limit applies to the whole card. The check makes a changed limit an invalid run, not a silent confound. It cannot see a co-tenant compute process (open-questions A7).
- **Design** (new sweep names, so no 420 W run can enter a 350 W computation):
  - **G2′ part a:** `configs/sweep_l1pl350_pc_off_a.yaml`, λ = 1 alone. 900 s, seed 0, cache off, no dev mode. The heat test.
  - **G2′ part b:** `configs/sweep_l1pl350_pc_off_b.yaml`, λ = 1.5, 2, 2.5, 3, 3.5, 4. Starts only if part a is valid.
  - **G1′ part a:** `configs/sweep_l1pl350_pc_on_a.yaml`, λ = 2, 3, 3.5, 4, 4.5, 5, cache on. Starts only if `gate.reg8_g1_may_start()` (`gate.cold_floor` on G2′ alone) has status `ok`. Otherwise no λ_test is possible whatever G1′ shows. This reads only G2′, which G1′ does not judge.
  - **G1′ part b:** `configs/sweep_l1pl350_pc_on_b.yaml`, λ = 5.5, 6, 7. Starts only if `gate.reg8_g1b_may_start()` is true: every part-a rate has a valid run passing the capacity rule (monotone μ over the rates swept so far = 5). Otherwise the chain has ended, and higher rates cannot change μ_warm or λ_test. Computed after part a's reruns.
  - **Gate:** computed once, after G1′ and G2′ are copied back: `uv run python -m analysis.gate reg8` (`gate.reg8_zone` = `gate.zone(gate.REG8)`). `REG8` equals `REG7` in every REG-7 value except the two sweep names; it adds `power_limit_w` and `g1a_top` (`tests/test_gate.py::test_reg8_is_reg7_with_the_350w_sweeps_only`). `reg7_zone` = `zone(REG7)`, the same computation as before.
  - **G3′** at λ_test: REG-7's G3 (two 2580 s runs, seed 1; the control sets `verdict.control_t_s: 1080`, the burst `trigger: {kind: burst, at_s: 900, duration_s: 180, rate: <λ_test>, prompt_tokens: 2944}`), except they extend `configs/stage2_l1pl350_base.yaml` and are named `stage2_control_l1pl350_r<λ>.yaml` and `burst_l1pl350_r<λ>_s1.yaml`. Judged by `gate.reg8_gate_verdict`, which refuses a pair unless both runs are 350 W runs at the same λ, then calls `gate.gate_verdict` with REG-7's settings. **The two G3′ configs get their own separate review against this entry before they run.**
- **Analysis plan:** REG-7's, unchanged: μ_warm and μ_off by the capacity rule in `configs/l1_base.yaml` (item 42, monotone; a swept rate with no valid run ends the chain); `gate.cold_floor`, `gate.choose_lambda`, `gate.gate_verdict`, `gate.overlap_share`; REG-7's secondary readouts. The "no λ_test" outcome is reported with its cause: the floor status, the capacity chain's end, or `slo_feasible`.
  - **Dropped after the review:** the readout μ_warm(350) against μ_warm(420). At 420 W, rates ≥ 5 had heat-invalid runs, so μ_warm(420) is censored by heat and the ratio would be biased (review T7). The cap's effect on the warm/cold balance stays open (open-questions A12).
- **Prediction** (BELIEF):
  - Part a `valid`, p ≈ 0.75. Peak temperature ≈ 74 °C (DERIVED, assuming a 25 °C room, which is not measured, and a temperature rise proportional to power: (83 − 25) × 350/415 + 25 ≈ 74). Valid L1 runs peaked at 75–79 °C, invalid ones at 81–83 °C.
  - Clock ≈ 5 % lower than at 420 W (DERIVED from clock ∝ power^(1/3) near the top of the curve, an approximation: (350/415)^(1/3) ≈ 0.945).
  - μ_sat,off ∈ [1.3, 2.1] (point 1.6, REG-7's 1.7 × 0.945), floor status `ok` p ≈ 0.7; μ_warm ∈ [3, 5.5] (point 4.5); λ_test exists p ≈ 0.6 (point 3.5).
  - Given G3′: as REG-7: `pass` ≈ 0.3, `drains` ≈ 0.45, `control_not_healthy` ≈ 0.1, `inconclusive` ≈ 0.15. Overall `pass` ≈ 0.75 × 0.6 × 0.3 ≈ 0.14.
- **Decision under each outcome:**
  - **Part a, by `gate.reg8_part_a`:**
    - `heat` (the limit held, and the SW-thermal share > 0.05 or a HW-thermal sample): one rerun after the GPU is idle at ≤ 45 °C. A second `heat` stops L1: "gate not completed: GPU heat at 420 and 350 W". No lower cap is registered here; the owner decides between a new registration and stopping L1.
      - Why one rerun, not two: at 420 W, λ = 1 spread 0.062–0.135 between runs, so one run near the limit is not conclusive. But the cap is predicted to clear the limit by a margin (≈ 74 °C against 81–83 °C), so two failures are enough.
    - `rerun` (any other failure: `power_limit`, clock CV, a HW power-brake sample, `no_errors`, …): rerun unchanged, at most twice, like every other invalid run. Its heat result is ignored.
    - `valid`: part b starts.
  - **G2′ floor not `ok` after part b's reruns:** stop before G1′. The floor is unmeasured at 350 W (status named). The owner decides.
  - **Otherwise:** REG-7's decision table, unchanged, applied to the 350 W gate (No λ_test with floor `ok`; `pass`; `drains`; `control_not_healthy`; `inconclusive`). A `pass` registers the shock matrix at 350 W.
- **Alternatives:**
  1. The cap may change the warm/cold balance. Cold requests spend more time in prefill, which is compute-bound and slows with the clock; warm ones less (BELIEF). So a lower cap may widen the capacity loss and make a stuck state easier. A `pass` supports "possible at 350 W" only; a claim at 420 W needs a replication there once the heat is solved (A12).
  2. A valid part a does not show that the cap fixed the heat. A cooler room or an idle co-tenant gives the same (review §2). For the gate only validity matters. To help tell them apart later, the `[OPS]` entries record the idle temperature and wall-clock time at each launch.
  3. The heat may come from a sensor that board power limits only partly (memory or hotspot, not recorded). Part a tests it.
  4. A lower clock lengthens TTFT, so `gate.slo_feasible` may lower or remove λ_test. "No λ_test" would then partly reflect the cap; it is reported with its cause (Analysis plan).
  5. `drains` may reflect a narrower window, not a missing mechanism: a lower μ_warm lowers λ_test, and the backlog clears at the lower load. The margin λ_test − μ_sat,off and `gate.secondary_cb` are reported with it.
  6. A co-tenant compute process on the shared GPU is not ruled out by `power_limit` (A7). `gpu_processes` is captured at the start and the end of each run only; sampling it through the run is a harness change, proposed, not done.
  7. REG-7's alternatives 1–6 stand.
- **Stopping rule:** REG-7's (each invalid run rerun unchanged, at most twice; G3′ at most at 2 λ_test values; an `inconclusive` pair rerun at most twice), with part a's rule and the two G1′ start rules above. A run invalid on `power_limit` counts toward its reruns. **After any heat-invalid run in G2′ part b or G1′, the agent asks the owner before spending its rerun.**
- **Operations:**
  - Before each part: the owner sets the limit; the agent reads `nvidia-smi --query-gpu=power.limit --format=csv` on the VM and launches only at 350 W, with the GPU idle at ≤ 45 °C. A VM reboot or driver reload may reset the limit (BELIEF); the check catches it.
  - Launch with a redirect, no pipe (decisions.md 2026-11-05 [CORR]).
  - After REG-8: the limit goes back to 420 W before REG-6, which is registered at 420 W. REG-6's configs carry no `power_limit` check and its seed-0 rerun must be unchanged, so the agent reads the limit before launch, and REG-6's result must show 420 W in every `gpu.jsonl` sample (review T11).
- **Cost:** part a 0.27 h; part b ≈ 1.6 h (6 runs); G1′ ≈ 3.0 h (9 runs); G3′ ≈ 1.7 h per pair. **≤ 8.3 GPU h without reruns. Worst case with every allowed rerun ≈ 25 h** (DERIVED: G2′ 7 runs × 3 × 0.27 ≈ 5.7, G1′ 9 × 3 × 0.33 ≈ 8.9, G3′ 2 λ × 3 pairs × 1.7 ≈ 10.2). The pause rule above keeps the heat reruns with the owner. If part a ends on `heat`: ≤ 0.55 h.
- **To change in PROTOCOL.md after approval (owner):** §4 hardware: "power limit 420 W; 350 W for setup L1 from REG-8". §6: a deviation row "L1 measured at a 350 W limit; SW-thermal slowdown at 420 W (decisions.md 2026-11-06)".
- **Not changed:** every past verdict, μ, threshold and config. REG-7's runs stay as judged; REG-7's gate is not computed.

### Adversarial review (separate subagent; it saw only the first draft, its diff and the code and configs those call; it opened no runs and no docs). Verbatim:

> **Adversarial review of REG-8.** This review read only the draft, the diff and the code/configs it calls. It used no runs/ and no docs. Checked: `uv run pytest tests/test_checks.py tests/test_gate.py` gives 58 passed. Resolved per-run configs, via `load_config`, `expand` and `with_defaults`, differ from REG-7's only in `checks.expected_power_limit_w`, `checks.power_limit_tol_w`, `name` and `sweep_parent`. So the registration's equivalence claim holds.
>
> **1. Traces on which the verdict comes out wrong or misleading**
> - **T1. Part a fails `gpu_steady` and `power_limit` together.** gpu.jsonl has `power_limit_w` = 350 for t < 300 and 420 for t ≥ 300 (the co-tenant reset it), and the SW-thermal share is 0.08. `failed = [gpu_steady, power_limit]`. The rule "Part a invalid on `gpu_steady`: stop" applies, and L1 is reported as "heat at 420 and 350 W", although for 2/3 of the run the heat test ran at 420 W. Nothing gives `power_limit` precedence.
> - **T2. Part a fails `power_limit` but passes `gpu_steady`.** Example: limit 300 W in every sample (co-tenant lowered it) and SW-thermal share 0. Part a is invalid. "Part b starts only if part a passes `gpu_steady`" says part b starts. "Invalid on another check → rerun" says rerun part a. The two rules conflict, and the configs' comments say "_b only if _a passes gpu_steady". Part b could start without a valid heat test at 350 W.
> - **T3. Part a fails `gpu_steady` for a reason other than heat.** Example: busy SM-clock CV 0.06, or one sample with HW power brake (0x80), with SW-thermal share 0.00. The rule stops L1 and labels it "GPU heat", though nothing thermal failed. `gpu_steady` mixes CV, HW-bit and SW-thermal failures (harness/checks.py:110-112).
> - **T4. One run decides L1.** At 420 W, λ = 1 gave SW-thermal shares of 0.062, 0.097 and 0.135: a spread of 0.07 between runs of one config. A single 350 W run at 0.051 ends L1 with no rerun, while every other invalid run gets two. The design itself predicts a 0.25 chance of this.
> - **T5. G1′ starts when it cannot change the decision.** G2′ valid runs: λ = 1, 1.5, 2 with kv_mean 0.4, 0.6, 0.8, and 2.5–4 heat-invalid three times each. Valid count is 3 ≥ 2, so G1′ starts (about 3.0 GPU h). `cold_floor` returns `unsaturated`, so `mu_sat_off` = NaN and `zone_check` returns None whatever μ_warm is. The same happens for `not_monotone` and for `too_few` with ≥ 2 valid runs: e.g. valid runs at 1, 1.5 and 4, only 4 saturated, gives n = 1. Floor status depends only on G2′ rows. Reading it before G1′ is not reading anything G1′ judges, so the "validity only" blinding buys nothing.
> - **T6. G1′ above a broken chain.** Under the monotone rule (`tables.sweep_capacity`), if λ = 4 fails capacity, or has no valid run after its reruns, μ_warm ≤ 3.5. λ_test ≤ 0.8 × μ_warm, and `slo_feasible` only reads the smallest swept rate ≥ λ_test, which is ≤ μ_warm. So runs at 4.5–7 (≈ 1.7 h, plus up to 2 reruns each) cannot change μ_warm or λ_test. These are also the hottest runs.
> - **T7. The readout compares with a heat-censored number.** At 420 W, `sweep_l1_pc_on` λ = 5, 5.5, 6 and 7 were heat-invalid (config comments: sweep_l1_pc_on_rerun2a.yaml:5 and rerun2b.yaml:5 say 6 and 7 each failed twice; the 6/7 rerun configs are the last allowed reruns). The monotone chain therefore ends at or below 5.5 whatever the true capacity. "μ_warm(350) ≥ 0.9 × μ_warm(420)" is biased toward passing. A 350 W μ_warm of 6 would read as "the cap gained capacity". It decides nothing, but its stated purpose is the write-up's wording.
> - **T8. G3′ can pair mismatched runs.** Control `stage2_control_l1pl350_r3.5` (λ 3.5) with burst `burst_l1pl350_r3_s1` (λ 3): same seed 1, same duration 2580, valid, `control_t_s` 1080. `gate_verdict` accepts the pair. It checks seed, duration and control_t_s only, not rate and not power limit. A control from the 420 W `stage2_l1_base` with `control_t_s` 1080 would also pass the guards. This predates REG-8, but REG-8 uses it.
> - **T9. The cost cap is not a bound.** Title "≤ 9 h". Without reruns: 0.27 + 1.6 + 3.0 + 2 × 1.7 = 8.27 h. The registered stopping rule allows 2 reruns for each of 16 sweep runs (≈ +9.7 h), and for G3′, 2 λ_test values × up to 3 pairs (≈ +6.8 h beyond the first pairs). That is about 25 GPU h worst case.
> - **T10. Gaps in `power_limit` samples.** Rows with `power_limit_w` null or missing are skipped by `.max()`. `[350, null, missing]` gives dev 0 and passes (checked). The recorder always writes the field, so this is latent. The check also proves only that the limit was set, not that draw stayed at or below 350 W or that the cap was binding.
> - **T11. REG-6 after REG-8 is unchecked.** REG-6 configs carry no `expected_power_limit_w`. If the limit is not restored to 420 W, REG-6 runs silently at 350 W: the 350/420 mixing the sweep names prevent inside REG-8, moved into REG-6. env.json records `power.limit` (harness/env_snapshot.py:33), but no check reads it.
>
> **2. Strongest alternative explanation for each expected outcome**
> - **Part a valid:** the cap did not cause it; ambient conditions did. The draft's own numbers show that board power does not set temperature: runs at the same 415–418 W peaked at 75–79 °C (valid) and 81–83 °C (invalid). A cooler room, time of day, an idle co-tenant or a cooler preceding run would also give a pass. Separate them by logging an ambient proxy (idle temperature at launch, time of day, co-tenant processes during the run, not only at start) and comparing with the 420 W invalid runs.
> - **Part a invalid:** an uncontrolled ambient or co-tenant heat load, or a CV or HW-bit failure (T3), not "the cap does not help". Separate them by the failing sub-condition (sw_frac vs CV vs HW bits) and the same ambient log.
> - **pass:** a 350 W artefact (draft alternative 1: a lower clock slows compute-bound cold prefill more than warm work), or a co-tenant compute process during the burst run only. `gpu_processes` is captured at start only, and the power check cannot see a co-tenant. Separate them by capturing co-tenant processes through the run and, if C1 is pursued, by a replication at 420 W once the heat problem is solved.
> - **drains:** the cap may narrow the window rather than show the mechanism absent. With μ_warm lower, λ_test is lower, and the backlog clears at the lower load. Separate them by the margin λ_test − μ_sat,off at 350 vs 420 W, and the secondary `secondary_cb`.
> - **No λ_test:** (a) the floor is unmeasured (`unsaturated`/`not_monotone`/`too_few`), not absent; (b) the heat-censored monotone chain lowers μ_warm, as in T6/T7; (c) the cap raises TTFT, so `slo_feasible` fails (draft alternative 4). `zone()` returns `status`, `lam_sat` and `n`, but the decision text must name which of (a), (b) or (c) applied.
> - **control_not_healthy:** the control at λ_test is itself near saturation, because μ_warm is measured with seed 0 and 900 s runs and the control uses seed 1 and 2580 s. Or a co-tenant or heat transient in a 2580 s run that `gpu_steady`'s 0.05 share tolerates (up to 129 s of SW thermal). Separate them by the control's `gpu_steady` detail and its queue trace.
>
> **3. Can the run change any decision?**
> Yes:
> - Part a decides whether L1 continues or is reported as "gate not completed: heat".
> - G2′ + G1′ decide whether λ_test exists, so whether G3′ runs.
> - G3′ decides between registering a shock matrix at 350 W (`pass`), the closed-loop proposal or dropping L1 (`drains`), and a new registration.
>
> The scope is narrower than the decision table implies. A `pass` supports "stuck state possible at 350 W" only. G1′ cannot change anything when the G2′ floor is not `ok` (T5), and the G1′ rates above the first failed or chain-ending rate cannot change anything (T6).
>
> **4. Code and config defects**
> - harness/checks.py:139: NaN or missing `power_limit_w` samples are skipped by `.abs().max()` (T10). There is no coverage requirement, such as a sample count against duration/interval_s.
> - harness/checks.py:110-112 (existing, used by REG-8's stop rule): `gpu_steady` gives one boolean for three causes. The part-a stop rule needs the sub-cause (T3). The `sw_frac` denominator is all window samples, while the CV uses busy samples only.
> - analysis/gate.py `gate_verdict` (existing): no rate-equality or power-limit-equality guard between control and burst (T8).
> - analysis/gate.py `zone()`: G1′'s start condition is not a function of the code. Nothing computes "G2′ ≥ 2 valid runs", let alone floor status.
> - configs/stage2_l1pl350_base.yaml: resolves to `verdict.control_t_s` 900 (inherited from stage2_base.yaml:11) and `trigger` None. The G3′ control and burst configs are not in the diff, so they could not be reviewed. "Contents as registered in REG-7" points to text, not files, and no `stage2_control_l1_*`/`burst_l1_*` configs exist. `gate_verdict` raises on a wrong `control_t_s`, which is safe but would waste a run pair.
> - configs/sweep_l1pl350_pc_off_a.yaml:1 and _b.yaml:1: the comments say "only if _a passes gpu_steady", which conflicts with "invalid on another check → rerun" (T2).
> - tests/test_checks.py `test_power_limit`: no case for a mixed limit with `gpu_steady` failing (T1), and no NaN case.
>
> **5. Recommended changes (most important first)**
> 1. **Part a's rule:** part b starts only if part a is **valid**. If `power_limit` fails, the run is a rerun whatever `gpu_steady` says, and its heat result is ignored. "Stop: heat" only if `sw_thermal_frac` > 0.05 or HW-thermal bits are set, with the limit held. A CV or HW-power-brake failure is rerun like any other.
> 2. **Gate G1′ on floor status:** register now that G1′ starts only if `cold_floor(sweep_rows("sweep_l1pl350_pc_off"), …)` has `status == "ok"`. Otherwise stop: "floor unmeasured at 350 W". This saves ≈ 3 h on the outcomes where G1′ cannot change anything, and reads nothing G1′ judges.
> 3. **G1′ early stop:** run in ascending order and stop when the monotone chain ends (a rate fails capacity, or has no valid run after its reruns). Higher rates cannot change μ_warm or λ_test.
> 4. **Part a reruns:** either allow part a REG-7's two reruns on a heat failure, or state plainly that one run decides L1, and why that is acceptable given 0.062–0.135 between runs at 420 W.
> 5. **Guards in `gate_verdict`, or a REG-8 wrapper:** require equal `workload.rate`, and `checks.expected_power_limit_w` == 350 in both runs. Commit and review the G3′ configs before G1′ starts, or register that G3′ gets its own review.
> 6. **Readout:** label μ_warm(420) as a heat-censored lower bound and do not compute a ratio from it. Or compare throughput only at rates valid at both limits.
> 7. **Restore 420 W after REG-8:** add `expected_power_limit_w: 420` to REG-6's not-yet-used configs (new files), or make the restore a pre-launch check. Otherwise REG-6 can run silently at 350 W.
> 8. **Coverage check:** `power_limit` should fail on any NaN sample and require ≥ 0.95 × duration/interval_s samples. Add NaN and mixed-limit tests.
> 9. **Cost:** state the worst case with reruns (≈ 25 GPU h) or cap it explicitly. The owner pauses on any SW-thermal failure in part b or G1′ rather than spending the automatic reruns.
> 10. **Ambient logging:** record idle temperature at launch, wall-clock time, and co-tenant processes sampled through the run (not only at start), so that "the cap fixed heat" can be told apart from "the room was cooler".

**Changed because of it:**
- **T1–T3, recommendation 1:** `gate.reg8_part_a` returns `valid`, `heat` or `rerun`. `heat` needs the limit held and the SW-thermal share over the limit or a HW-thermal sample; every other failure is `rerun`. Part b starts only if part a is valid. Config comments fixed. Test: `tests/test_gate.py::test_reg8_part_a_separates_heat_from_other_failures` (T1, T2, T3 cases).
- **T4, recommendation 4:** part a gets one rerun on `heat`; the reason is stated in the decision table.
- **T5, recommendation 2:** G1′ starts only if `gate.reg8_g1_may_start()` has status `ok`.
- **T6, recommendation 3:** G1′ runs in two parts; part b only if `gate.reg8_g1b_may_start()`. A finer split (per rate) was not adopted: it saves at most the part-a rates above a break, ≤ 1.3 h, against six more configs.
- **T7, recommendation 6:** the 420 W readout is dropped; open-questions A12 added.
- **T8, recommendation 5:** `gate.reg8_gate_verdict` refuses a pair unless both are 350 W runs at the same λ (test `::test_reg8_gate_verdict_refuses_mismatched_or_420w_pairs`). The G3′ configs get their own separate review before they run. `gate_verdict` itself is unchanged (REG-7).
- **T9, recommendation 9:** the worst case (≈ 25 h) is stated; heat reruns in part b and G1′ wait for the owner.
- **T10, recommendation 8:** a sample without a value fails `power_limit` (test case added). No sample-count rule: GPU samples are written on the recorder's tick, whose gaps the `recorder` check already fails (> 2 s, FILE(harness/recorder.py:111-114)). The cap being binding is not required; the check states the limit only.
- **T11, recommendation 7:** a pre-launch read of 420 W before REG-6, and REG-6's result must show 420 W in every sample. No REG-6 config is added: its seed-0 rerun must be unchanged.
- **Recommendation 10:** idle temperature and wall-clock time at each launch go into the `[OPS]` entries. Sampling GPU processes through the run is a harness change, proposed to the owner, not done.
- **Not adopted:** `gpu_steady`'s denominators (sw_frac over all window samples, CV over busy ones) stay; changing them would change a used check.
- **Also found while making the changes:** `gate.sweep_rows` crashed on a sweep with no valid run ([CORR] above).
- Tests after the changes: `uv run pytest`, 195 passed; the one failure was `test_check_docs::test_the_repo_passes` on a stale context pack, regenerated with `tools/context_pack.py`, after which `tools/check_docs.py` is OK.

## 2026-11-07 · [DECISION] Owner approves REG-8 as written; PROTOCOL.md updated for the 350 W setup
- **Owner:** "ok / Continue", in reply to the agent's request to approve REG-8 as written (or change the wattage or the one-rerun heat rule), to commit it, and to apply the drafted PROTOCOL.md lines. The agent reads it as yes to all three, with 350 W and the one-rerun heat rule unchanged. No 350 W run exists; approval comes before any run.
- **PROTOCOL.md:** §4 hardware now reads "power limit 420 W (350 W for setup L1 from REG-8 …)"; §6 gains the row "L1 measured at a 350 W power limit, not 420 W".
- **Committed by name**, without `.gitignore` (the owner's uncommitted line `docs/potential_gaps.md` stays out).
- **Next:** push to `vm`; the owner sets 350 W; the agent reads the limit and starts `configs/sweep_l1pl350_pc_off_a.yaml` with the GPU idle at ≤ 45 °C.

## 2026-11-07 · [OPS] Power limit set to 350 W for REG-8; audit of what the change affects: no run invalid, old configs unguarded
- **Set:** the owner ran `sudo nvidia-smi -pl 350` on the VM ("set to 350.00 W from 420.00 W"; persistence mode disabled). The agent read 350 W back after that client exited, and again at the launch of G2′ part a, `20261107-075951_sweep_l1pl350_pc_off_r1` (07:59:50 UTC, GPU idle at 43 °C, from `3fa9563`, clean, microk8s inactive). FILE(docs/probe/20261107_power_limit/set_350w.txt).
- **Audit, asked by the owner ("Which runs, configs, files now invalid after we changed power cap"):**
  - **Runs: none invalid.** All 125 run folders before REG-8 ran at 420 W. 121 have `power_limit_w` = 420.0 in every `gpu.jsonl` sample. The other 4 have no `gpu.jsonl` (`20261030-114021_first_real`, a failed start; the three `recorder_off` runs), and their `env.json` `nvidia_smi` reads "420.00 W" at the start. (Inline scan of every run folder, read-only; no committed function, so it supports this audit only.) Every past verdict, μ and validity stands.
  - **Configs: none edited, none invalid, but none guarded.** Every config except `l1_pl350_base.yaml` and `stage2_l1pl350_base.yaml` has no `power_limit` check, so it would run silently at 350 W while the card is set so. That matters for:
    - REG-6 (`configs/long_pc_off_r3_s0.yaml`, `long_pc_off_r3_s1.yaml`), registered at 420 W;
    - REG-7's unused rerun configs (`sweep_l1_pc_off_rerun1b.yaml`, `sweep_l1_pc_on_rerun2b.yaml`). REG-8 supersedes REG-7, so they are not to be run; a 350 W run under REG-7's sweep names would mix limits in one parent;
    - every other earlier setup.
    - **Rule, operational, from now on:** while the card is at 350 W, only REG-8 configs are launched, and the agent reads `power.limit` before every launch. Before any other run, the owner sets 420 W again.
    - **Proposed to the owner, not done:** a harness pre-launch guard that refuses to start when the live limit differs from the config's `checks.expected_power_limit_w`. For configs without the key it can only warn, since 420 W cannot become a default without editing `defaults.yaml` (rule 5).
  - **Docs updated (stale "420 W" as current):** `docs/status.md` (Environment, GPU row; a new open risk), `docs/open-questions.md` S3 (partly answered), `docs/model.md` M2 (its inputs are at 420 W and do not carry over to L1 at 350 W). `PROTOCOL.md` §4 and §6 were updated with REG-8's approval.
  - **Not affected:** the analysis code (it reads the limit nowhere except the new check), the verdict rules and thresholds, `docs/definitions.md`, `docs/claims.md`.

## 2026-11-07 · [OPS] REG-8 G2′ part a VALID at 350 W (SW thermal 0.012, max 74 °C); part b starts
- **Run:** `20261107-075951_sweep_l1pl350_pc_off_r1` (`configs/sweep_l1pl350_pc_off_a.yaml`, from `3fa9563`, clean; 07:59:51–08:16:01 UTC; launched with the GPU idle at 43 °C and the limit read at 350 W). It stopped normally (`events.jsonl` `stopped`), and no process was left.
- **Checks:** VALID, every check passed (FILE(runs/20261107-075951_sweep_l1pl350_pc_off_r1/checks.json)):
  - `gpu_steady`: SW-thermal share 0.012, max 74 °C, busy SM-clock CV 0.015, no HW throttle sample.
  - `power_limit`: 350 W in all 914 samples (max deviation 0.0 W).
  - `gate.reg8_part_a` gives `valid`, so part b starts (REG-8 decision table).
- **Prediction:** part a valid p ≈ 0.75, peak ≈ 74 °C. Observed: valid, peak 74 °C. At 420 W the same config gave SW-thermal 0.062, 0.097 and 0.135, with peaks of 82–83 °C (decisions.md 2026-11-05/06 [OPS]).
  - **Not a test of cause** (REG-8 alternative 2): one run per limit, and room conditions are not measured. The nearest 420 W run, `20261106-063534_sweep_l1_pc_off_r1`, started at a similar hour (06:35 UTC) with the GPU idle at 45 °C, against 43 °C here.
- **Copied** to the Mac with identical sha256 for all 10 files (`sha256sum` on the VM against `shasum -a 256`); `tools/manifest.py update` appended 10 lines. The VM keeps its copy.
- **Not computed:** throughput, KV and the floor. The gate is computed once, after G1′ and G2′; `gate.reg8_g1_may_start` is computed after part b.

## 2026-11-07 · [OPS] REG-8 G2′ done: 7 of 7 runs valid at 350 W; cold floor μ_sat,off = 1.681 (`ok`); G1′ part a starts
- **Runs** (`configs/sweep_l1pl350_pc_off_b.yaml`, from `abc42ea`, clean; 08:20:35–10:20:59 UTC; launched with the GPU idle at 40 °C and the limit read at 350 W). Every one VALID, with 350 W in every `gpu.jsonl` sample (FILE(runs/<id>/checks.json), `gpu_steady` and `power_limit`):
  - `20261107-082035_sweep_l1pl350_pc_off_r1.5`: SW thermal 0.005, max 75 °C.
  - `20261107-083730_sweep_l1pl350_pc_off_r2`: 0.000, 73 °C.
  - `20261107-085650_sweep_l1pl350_pc_off_r2.5`: 0.000, 74 °C.
  - `20261107-091752_sweep_l1pl350_pc_off_r3`: 0.000, 74 °C.
  - `20261107-093854_sweep_l1pl350_pc_off_r3.5`: 0.000, 72 °C.
  - `20261107-095958_sweep_l1pl350_pc_off_r4`: 0.000, 73 °C.
  - With part a (`20261107-075951_sweep_l1pl350_pc_off_r1`), G2′ has a valid run at every rate, and needed no rerun.
- **Copied** to the Mac with identical sha256 for every file; the manifest gained 60 lines.
- **G1′ start rule** (REG-8), computed once: `gate.reg8_g1_may_start()` = μ_sat,off 1.681 req/s, λ_sat 2.0, n = 5, status `ok`. RUN(the seven 20261107 `sweep_l1pl350_pc_off` runs, gate.reg8_g1_may_start). So G1′ part a (`configs/sweep_l1pl350_pc_on_a.yaml`, λ = 2–5) starts.
  - **Prediction** (REG-8): μ_sat,off ∈ [1.3, 2.1], point 1.6; status `ok` p ≈ 0.7. **Hit.**
  - DERIVED from REG-7's zone rule, before any G1′ run: λ_test ≥ 1.3 × 1.681 = 2.185, so λ_test ≥ 2.5 if it exists; that needs 0.8 μ_warm ≥ 2.5, so μ_warm ≥ 3.5 on the swept grid.
  - Nothing else from G2′ is computed. μ_off and λ_test come from the gate, once, after G1′.
- **Observed, inline (`gpu.jsonl`, not a committed function; instrument data, not a gate input):** the busy median SM clock was 1830–1890 MHz at 350 W, against 1920–1965 MHz in the heat-invalid 420 W runs at λ = 1 and 1.5 (about 4 % lower). Reported to the owner, who asked whether the cap made the server slower; throughput and TTFT were not computed.

## 2026-11-07 · [CORR] REG-8's prediction was not entered in the model.md ledger before its first run
- **What was wrong:** `docs/model.md` says "A model that predicts is updated here before the run". REG-8's predictions were committed in its registration (`3fa9563`) but not as a ledger row, and its first run started at 07:59 UTC without one. REG-7's row 11 also still read "Not run".
- **Since when:** `3fa9563`.
- **Which results it affects:** none. The predictions were committed before any 350 W run, in decisions.md. The ledger row copies them unchanged.
- **Fix:** row 12 added, marked as added late, with part a's and the floor's outcomes; row 11 closed as superseded by REG-8.
- **Rule that would have caught it:** a registration checklist that includes the ledger row; `tools/check_docs.py` could flag a `[REG]` with no ledger row (proposed, not done).

## 2026-11-07 · [RESULT] REG-8: no λ_test at 350 W (μ_warm 3.0, μ_sat,off 1.681); G1′ part b and G3′ not run; the owner picks the next factor
- **Registration:** REG-8 (decisions.md 2026-11-06 [REG]; approved 2026-11-07).
- **Runs, all VALID at 350 W** (FILE(runs/<id>/checks.json); `power_limit` 350 W in every sample, SW thermal ≤ 0.012):
  - G2′, cache off: `20261107-075951_sweep_l1pl350_pc_off_r1` … `20261107-095958_sweep_l1pl350_pc_off_r4` (7 runs, λ = 1–4).
  - G1′ part a, cache on: `20261107-103010_sweep_l1pl350_pc_on_r2`, `20261107-104614_sweep_l1pl350_pc_on_r3`, `20261107-110219_sweep_l1pl350_pc_on_r3.5`, `20261107-111833_sweep_l1pl350_pc_on_r4`, `20261107-113511_sweep_l1pl350_pc_on_r4.5`, `20261107-115311_sweep_l1pl350_pc_on_r5` (from `212327f`, clean; 10:30–12:16 UTC; max 64–69 °C). Copied with identical sha256; manifest +60 lines.
  - No rerun was needed anywhere in REG-8.
- **G1′ part b:** not run. `gate.reg8_g1b_may_start()` = False, since the monotone μ over λ = 2–5 is 3.0 (`tables.sweep_capacity`).
- **Gate, computed once:** `uv run python -m analysis.gate reg8` → μ_warm 3.0, μ_off 1.0, μ_sat,off 1.681 (λ_sat 2.0, n = 5, `ok`), λ_test None. RUN(the 13 REG-8 runs above, gate.reg8_zone).
  - **Cause, as REG-8 requires:** the capacity chain. DERIVED: λ_test ≤ 0.8 × 3.0 = 2.4 → at most 2.0, below 1.3 × 1.681 = 2.185. `slo_feasible` was not reached.
  - **Where the chain broke** (`tables.sweep_table`, G1′ rows): λ = 3.5 had throughput 3.485 against 0.95 × planned 3.620 = 3.439 (passes), and queue slope 0.0145 against 0.01 req/s (**fails**). RUN(20261107-110219_sweep_l1pl350_pc_on_r3.5, load.summarize). λ = 4 failed both (3.929 against 3.977; slope 0.147).
  - **Pooled percent fast at TTFT ≤ 1.0 s** over the measured window (`gate.sweep_rows`, `load._level` pf): 1.000, 0.990, 0.716, 0.406, 0.155, 0.000 at λ = 2, 3, 3.5, 4, 4.5, 5. RUN(the six G1′ runs, gate.sweep_rows).
- **The outcome rests on one marginal failure,** stated so it is not read as clear-cut. Had λ = 3.5 passed its slope test, μ_warm would be 3.5, and λ_test = 2.5 (≤ 2.8 and ≥ 2.185; the G1′ run at 3.0 has pf 0.990 ≥ 0.98, DERIVED). The 0.01 threshold was registered before the runs (rule A5) and is not reopened here.
- **Prediction** (`docs/model.md` row 12): μ_sat,off ∈ [1.3, 2.1], hit (1.681); μ_warm ∈ [3, 5.5], point 4.5: hit at the bottom edge (3.0); λ_test exists p ≈ 0.6: it does not. As a probability that is not a miss by itself, but the point estimates for μ_warm (4.5) and λ_test (3.5) missed.
- **Capacity loss** (DERIVED, M2): the best cache-on completion rate in G1′ is 4.047 (λ = 4.5); the cold floor is 1.681; so the cold state completes 1 − 1.681 / 4.047 = 0.585 less, against 0.116 at the default pool (M2). L1 does create the large warm/cold gap it was designed for. What limits it is the warm side: percent fast falls below 0.98 between λ = 3 and 3.5, close to the floor × 1.3 margin.
- **Alternatives still open:**
  1. **One arrival pattern:** μ_warm comes from seed 0, whose planned rate runs 3.4 % above λ at 3.5 (3.620) and rises through the window (M4). Another seed could pass at 3.5, or fail at 3. Separable only by other seeds (GPU).
  2. **The 350 W cap:** the clock ran about 4 % lower than at 420 W (inline `gpu.jsonl`, decisions.md 2026-11-07 [OPS]). The warm side may be slightly lower than at 420 W. Not separable with existing data (A12).
  3. **The margins are registered choices** (0.8 μ_warm, 1.3 μ_sat,off). DERIVED from the numbers above, the raw M2 condition, a load between 1.681 and the highest warm-healthy rate 3.0, is not empty. Testing a load inside it (e.g. λ = 2.5) is allowed only as a **new** registration, and would be chosen after seeing these data, so it must be labeled exploratory, not confirmatory.
  4. **Latency, not throughput, limits the warm side:** at λ = 3.5 throughput kept up (3.485 against 3.620 planned) while percent fast was 0.716. With 2–4k-token prompts, TTFT ≤ 1.0 s binds before capacity does.
- **Decision taken** (REG-7's table, applied by REG-8): no λ_test with floor `ok` → no shock matrix at L1 at 350 W. The μ values go into M2, and **the owner picks the next factor.**
- **Power limit:** REG-8 is done. The card stays at 350 W until the owner decides; before any run outside a 350 W registration (REG-6 first), the owner sets 420 W again.

## 2026-11-07 · [OPS] Power limit back to 420 W after REG-8
- **What:** the owner set the RTX 3090's power limit back to 420 W. The agent read it at 14:30 UTC: limit 420 W (default 420, max 450), 43 °C, 0 % utilization, no compute process, no tmux session. PROBE(docs/probe/20261107_power_limit/read_420w.txt).
- **Why:** REG-8 is done; REG-6 and every setup before REG-8 are registered and measured at 420 W.
- **Effect:** no run was in progress; no run is affected. A `*pl350*` config launched now would fail its `power_limit` check. A further L1 run at 350 W needs the owner to set 350 W first.
- **VM tree:** at `212327f`, behind the Mac's `main`; it pulls before the next launch.

## 2026-11-07 · [DECISION] REG-6 is not run at 420 W; the owner chooses to repeat it at 350 W (REG-9, to be registered)
- **Found before launch:** REG-6's only attempt at 420 W, `20261104-134159_long_pc_off_r3_s0` (interrupted, no `checks.json`), ran in SW-thermal slowdown for 0.296 of its `gpu.jsonl` samples in [600, 3168] s, against the 0.05 `gpu_steady` allows, with 2 HW-slowdown samples and a peak of 82 °C; every 600 s slice was 0.15–0.33. Inline reading with `gpu_steady`'s masks, not a committed function. With every L1 cache-off run at 420 W also heat-invalid (decisions.md [OPS] 2026-11-06), a 420 W rerun would most likely be invalid and could spend REG-6's two reruns (about 3.3 GPU h) with no valid run.
- **Options put to the owner:** run REG-6 at 420 W anyway; re-register it at 350 W; drop it.
- **Owner's choice:** "lets do option 2": a new registration (REG-9) at 350 W, read in one direction only: a sustainable λ = 3 at 350 W carries to 420 W, a non-sustainable one does not.
- **Not launched:** no run started. The VM was unavailable when the owner asked to prepare the files only; the GPU limit was 420 W at its last reading (decisions.md [OPS] 2026-11-07).

## 2026-11-07 · [REG] REG-9 (A1): REG-6's sustained cache-off capacity at λ = 3, default pool, repeated at a 350 W power limit (GPU, ≤ 2.2 h without reruns)
- **ID:** REG-9, open item A1. Replaces REG-6, which is not run at 420 W. **Not approved yet:** no GPU run before the owner approves this entry.
- **Why not REG-6 at 420 W:** REG-6's only attempt, `20261104-134159_long_pc_off_r3_s0` (420 W, interrupted at t ≈ 3168 s, no `checks.json`), ran in SW-thermal slowdown for 0.296 of its samples in [600, 3168] s, against the 0.05 that `gpu_steady` allows, with 2 HW-slowdown samples and a peak of 82 °C. Every 600 s slice was 0.15–0.33. Inline reading of `gpu.jsonl` with `gpu_steady`'s masks (0x20; 0x8 | 0x40 | 0x80), not a committed function, so not quoted as a result. It matches every L1 cache-off run at 420 W (decisions.md [OPS] 2026-11-06). At 350 W all 13 REG-8 runs were valid (SW thermal ≤ 0.012, peak 64–75 °C; decisions.md 2026-11-07 [RESULT]). The owner chose this amendment (decisions.md 2026-11-07 [DECISION]).
- **Question:** REG-6's: is λ = 3 below the default pool's sustained cache-off capacity? Here measured at 350 W, and carried to 420 W in one direction only (assumption P below).
- **Claim tested:** none of C1–C2 directly. The result decides whether the 6 default-pool λ = 3 shock runs (420 W) count as tests of C1 (REG-6's decision).
- **Setup:** `configs/long_pl350_pc_off_r3_s0.yaml` and `_s1.yaml`. Each extends its REG-6 config (`long_pc_off_r3_s0.yaml`, `_s1.yaml`, unchanged) and adds only `checks.expected_power_limit_w: 350` and `checks.power_limit_tol_w: 1.0`. Checked with `load_config`, `harness.run.expand` and `with_defaults`: each resolved config equals its REG-6 counterpart apart from `name` and these two keys. Seeds 0 and 1, λ = 3, 3600 s, cache off, default pool, `kv_capacity` 96,656, server `--seed` 0. Same schedules as REG-6 (planned rate over the window 3.049 and 3.032, from REG-6).
- **Assumption P (BELIEF, open-questions A12):** for this config, the sustained capacity at 420 W **inside a window without thermal slowdown** is at least the capacity at 350 W. A lower power limit lowers the clock (about 4 % lower busy SM clock at 350 W than in the 420 W L1 runs, inline, decisions.md 2026-11-07 [OPS]), and cache-off prefill is compute-bound.
- **Coverage of the 6 shock runs (review T3):** a run's validity bounds SW thermal over its whole duration, not inside the window its verdict reads. So the carry covers only the shock runs that were heat-clean inside that window. `floor.shock_heat_table()` (`uv run python -m analysis.floor reg9_shock_heat`) reads only the 6 default-pool λ = 3 shock runs (`floor.SHOCK_RUNS_R3`, 420 W, model.md ledger row 1) and, with `gpu_steady`'s masks, takes the SW-thermal share and the HW-slowdown samples of `gpu.jsonl` from the baseline's start to the watch's end (`load.verdict`'s times). **Pass condition, registered here:** a run is `covered` if it is valid, its window has samples, its SW-thermal share is ≤ its own `checks.max_sw_thermal_frac` (0.05) and it has no HW-slowdown sample. Computed once, after approval and before REG-9's first run. It uses no REG-9 data. If no run is covered, REG-9 cannot change any decision and is not run (start rule). It also lists each run's seed and power limit; microk8s was active in all 6 (2026-11-02, before 2026-11-05).
- **Measurement and labels:** REG-6's, unchanged: `floor.sustained_capacity` over [600, 3600) s, with REG-6's settings (`floor.REG9` = `floor.REG6` except `runs_pattern` `*_long_pl350_pc_off_r3_s*` and `power_limit_w` 350; `tests/test_floor.py::test_reg9_is_reg6_with_the_350w_runs_only`). Labels `unclear_data`, `sustainable_no_backlog`, `sustainable` (c_b ≥ 1.05 λp), `not_sustainable` (c_b < λp), `unclear`. Computed once: `uv run python -m analysis.floor reg9` (`floor.reg9_table`, then `floor.reg9_outcome`). It reads only valid runs, refuses one without a passed 350 W `power_limit` check, and refuses more than one valid run for a seed. No 420 W run matches its pattern (`*_long_pl350_pc_off_r3_s[01]`), and no 350 W run matches REG-6's. Each label is reported with `n_stretches`, `backlog_s` and `n_done`, the completions behind c_b; no threshold is added.
- **Not computed before the result:** the c_b of the interrupted 420 W seed-0 run. Its schedule is the same as REG-9 seed 0's, so it would inform the prediction from nearly the data being judged; it is invalid anyway.
- **Prediction** (BELIEF):
  - Each run valid, p ≈ 0.8 (REG-8 runs at 350 W were 900 s; these are 3600 s, so more time to heat).
  - Seed 0: REG-6's c_b 3.35–3.60, scaled by about 0.96 for the clock: c_b ≈ 3.2–3.45. The `sustainable` threshold is 1.05 × 3.049 = 3.20 (DERIVED), so seed 0 sits near it: `sustainable` ≈ 0.5, `unclear` ≈ 0.3, `not_sustainable` ≈ 0.2.
  - Seed 1: `sustainable_no_backlog` ≈ 0.55, `sustainable` ≈ 0.25, otherwise ≈ 0.2.
  - Both seeds sustainable or sustainable_no_backlog: ≈ 0.4.
- **Decision under each outcome:** the outcome is `floor.reg9_outcome(reg9_table())`, in this order of precedence (`tests/test_floor.py::test_reg9_outcome_precedence`):
  - **`first_edge`, both seeds `sustainable` or `sustainable_no_backlog` at 350 W:** with P, λ = 3 is below sustained cache-off capacity at 420 W too. REG-6's first edge applies: the 6 default-pool λ = 3 shock runs were not tests of C1; μ_off = 2 is recorded as an underestimate due to the seed-0 schedule; no further shocks at the default pool with 20 s gaps. This changes how the default-pool negative is written up, not the next experiment. It applies only to the shock runs `covered` by `shock_heat_table`; the others are named as not covered.
  - **`not_decided_at_420W`, otherwise, if any seed is `not_sustainable` at 350 W:** λ = 3 is above cold capacity at 350 W only. Because P runs one way, this says nothing about 420 W: REG-6's second edge (the 6 runs were real tests; the floor calculation withdrawn) is **not** applied. No statement changes; recorded as "not decided at 420 W".
  - **`no_change`, everything else** (`unclear`, `unclear_data`, a missing seed): no change to any statement.
  - So only `first_edge` changes a decision (rule A1), and only a write-up. Its prior is ≈ 0.4 × the share of covered runs. The review: this meets rule A1 only just; **the owner confirms that a write-up change is worth ≤ 2.2 GPU h.**
- **Order and start rules:**
  - First, `floor.shock_heat_table()` once (0 GPU h). If no shock run is `covered`, stop: REG-9 is not run.
  - Seed 0 next. Seed 1 starts only if `floor.reg9_seed1_may_start()` is true: seed 0 has a valid run labeled `sustainable` or `sustainable_no_backlog`. Otherwise the first outcome is no longer possible, and seed 1 cannot change any decision. Computing seed 0's label early is the registered computation, not a peek: nothing judged later depends on it.
  - If seed 1 does not start, `reg9_table` is still the result, on seed 0 alone, and only `no_change` or `not_decided_at_420W` is possible; the result says so.
- **Alternatives:**
  1. **P may be wrong:** if the 350 W cap changes how the server batches or schedules (not only its speed), capacity at 420 W could be lower for some loads. Not separable with existing data (A12).
  2. **Heat at 350 W over an hour.** `gpu_steady` and `power_limit` apply; an invalid run is rerun (stopping rule).
  3. **microk8s:** active in every 420 W run before 2026-11-05 (about 8 % of one core, unpinned, so it may share vLLM's cores), disabled for REG-9. Its direction is unfavourable to P (it can only lower the shock runs' capacity); its size is unknown (added to A12). Stated in the result.
  4. **REG-6's alternatives 1–3 stand** (heat, the small backlog at λ ≈ 3 giving smaller batches, few stretches).
  5. **A co-tenant process** on the shared GPU is not ruled out by `power_limit` (A7).
  6. **c_b noise (review):** with a few hundred seconds of backlog, c_b rests on a few thousand completions or fewer, close to the 5 % margin; seed 0 is predicted near its threshold, so it can pass or fail by chance. The margin is not changed; `n_done` and `backlog_s` are reported.
  7. **Slow heat under the limits:** SW thermal ≤ 0.05 and clock CV ≤ 0.05 still allow a slow clock drop; a lower c_b may then come from heat, not the cap. The busy median SM clock is reported inline from `gpu.jsonl` (not a decision input).
  8. **Batch mix:** a slower GPU has longer steps, so the mix of chunked prefill and decode per step differs at 350 W; throughput need not scale one way with the clock. Weak; not ruled out (A12).
- **Stopping rule:** each seed once; an invalid run is rerun unchanged, at most twice. After a heat-invalid run (SW thermal > 0.05 or a HW-thermal sample), the agent asks the owner before spending its rerun. A run invalid on `power_limit` counts toward its reruns. **A rerun decision is made without computing c_b, the backlog or any label of the invalid run** (review); only `checks.json` is read.
- **Operations:** the owner sets 350 W (`sudo nvidia-smi -pl 350`); the VM runs `git pull origin main`; the agent reads `nvidia-smi --query-gpu=power.limit --format=csv`, checks a clean tree at the Mac's `main`, no GPU compute process, GPU idle at ≤ 45 °C, and launches with a redirect, no pipe; idle temperature and wall-clock time go into the `[OPS]` entry. After REG-9 the limit stays at 350 W until the owner decides.
- **Cost:** 1.1 h per seed, ≤ 2.2 GPU h without reruns; 1.1 h if seed 1 does not start; worst case with every rerun 6.6 h.
- **Code and files:** `configs/long_pl350_pc_off_r3_s0.yaml`, `_s1.yaml`; `analysis/floor.py` (`REG9`, `SHOCK_RUNS_R3`, `reg_table`, `reg9_table`, `reg9_seed1_may_start`, `reg9_outcome`, `window_heat`, `shock_heat_table`; `sustained_capacity` also returns `n_done`; `reg6_table` = `reg_table(REG6)`, the same computation as before plus the one-run-per-seed guard; `python -m analysis.floor` with no argument still prints REG-6's table); `tests/test_floor.py` (5 new tests, 11 pass).
- **Not changed:** REG-6's configs, its settings and its interrupted run. REG-6 is closed without a result: superseded by REG-9.

### Adversarial review (separate subagent; it saw only the first draft, its diff and the code and configs those call; it opened no runs and no docs). Verbatim:

> **Adversarial review of REG-9 (rule F).** I read only the draft, the diff, and the code and configs listed. I opened nothing in runs/ or docs/. Facts I checked myself: `uv run pytest tests/test_floor.py` gives 9 passed. Each resolved config (load_config → expand → with_defaults) equals its REG-6 counterpart apart from `name`, `checks.expected_power_limit_w` and `checks.power_limit_tol_w`. Schedules from `build_schedule` give a planned rate in [600, 3600) of 3.0487 for s0 (threshold 3.2011) and 3.0323 for s1 (threshold 3.1840).
>
> **1. Traces where the verdict or decision comes out wrong**
> - T1 (code). `reg_table` does not refuse two valid runs for one seed. `reg9_seed1_may_start` uses `.any()` over seed 0's rows. Suppose seed 0 has a valid `unclear` run and a second valid run (an accidental relaunch, or a rerun that should not have happened) labeled `sustainable`. Seed 1 then starts, and the final table holds two seed-0 rows with no rule for which one counts. `capacity()` already raises in this case; `reg_table` should too.
> - T2 (code). The decision rule (both seeds sustainable / either not_sustainable / otherwise) exists only as prose, so the outcome is read by hand. The prose also overlaps: s0 `sustainable` with s1 `not_sustainable` fits both "either not_sustainable" and "a split". Both bullets give the same action, but the overlap shows the rule is not mechanical.
> - T3 (carry to 420 W). P compares two clean states. The shock runs only had to keep SW thermal ≤ 0.05 over [warmup, duration] taken as a whole (`checks.py` gpu_steady). Those ≤ 5 % of samples could all fall inside a shock run's end/watch window. In that window the clock may sit well below the 350 W clock, so that run's cold capacity during the window may be below what REG-9 measures. Validity of the shock runs does not establish P for the windows the verdict reads.
> - T4 (carry to 420 W). The draft says microk8s ran in every 420 W run before 2026-11-05 and is off for REG-9. Its CPU use unpinned could land on vLLM's cores 0–5. That pushes shock-run capacity *below* REG-9's, which is the direction P assumes cannot happen. The draft calls this harmless on the strength of a BELIEF (that the server is GPU-bound).
> - T5 (carry to other schedules). `sustainable_no_backlog` says this schedule never kept a queue in [600, 3600). It says nothing about capacity. If the 6 shock runs use other seeds, or the wipe lands in a denser stretch (s0's 600 s slices reach 3.15 req/s), the result does not carry over.
>
> **2. Strongest alternative explanation for each outcome**
> - Both sustainable: c_b noise. With about 300–600 s of backlog, c_b rests on roughly 1,000–2,000 completions, so its relative SD is about 2–3 %. That is close to the 5 % margin, so s0 (predicted near 3.20) can pass by chance. Do not change the margin; report the counts behind c_b.
> - not_sustainable: heat that stays under the check limits. SW thermal ≤ 0.05 and clock CV ≤ 0.05 still allow a slow drop in clock. A lower capacity at 350 W can then come from heat, not from the power limit itself.
> - unclear_data / no_backlog: too few or too short backlog stretches. Report `n_stretches` and `backlog_s`.
> - Against P itself: a slower GPU gives longer steps, so each step admits more prefill tokens. The mix of chunked-prefill and decode work then differs between 350 W and 420 W. Throughput need not scale one way with the clock. Weak, but nothing rules it out.
>
> **3. Can the run change a decision? Is the seed-1 rule sound?**
> - Only the first outcome changes anything (prior ≈ 0.4, ≤ 2.2 GPU h), and it changes how the default-pool negative is written up, not the next experiment. That meets rule A1, but only just. The owner should confirm that a write-up change is worth 2.2 h.
> - Computing seed 0's label before seed 1 runs is not a peek. The label is final, its threshold is fixed, and seed 1's label does not depend on whether it was run. Stopping when the joint outcome is already settled adds no bias to seed 1. One real peek channel exists: after a heat-invalid run, the agent asks the owner whether to rerun. If c_b of the invalid run has been looked at, it can sway that choice.
>
> **4. Recommendations**
> 1. **Blocking.** `reg_table` raises on more than one valid run per seed (as in `capacity`). Add a test.
> 2. **Blocking.** Code the decision as `floor.reg9_outcome()`, returning one of three values: `first_edge`, `not_decided_at_420W`, `no_change`. Give a precedence for splits and test it. The registered result is that function's output.
> 3. **Blocking.** Restate P as covering the shock runs' actual conditions. Before the result, register a check that reads only the 6 shock runs' `gpu.jsonl`: SW-thermal fraction and HW samples inside each run's verdict windows (baseline, prev, end), plus their seeds and whether microk8s was on. Register its pass condition now. Shock runs that fail it are not covered by the carry. This uses existing data, not REG-9's.
> 4. **Blocking.** Rerun choices after an invalid run are made without computing c_b, its backlog or any label of that run. State this in the stopping rule.
> 5. Tighten `runs_pattern` to `*_long_pl350_pc_off_r3_s[01]`, so later names like `…_s10` or `…_s0_x` cannot match.
> 6. Report `n_stretches`, `backlog_s` and the completion count behind c_b next to each label. Add no new threshold.
> 7. Downgrade the microk8s alternative to "direction unfavourable to P, size unknown" and add it to A12.
> 8. State in the result that seed-1 not starting leaves only `no_change` or `not_decided_at_420W` possible.

**Changed because of it:**
- Recommendation 1: `reg_table` raises on more than one valid run per seed; tested.
- Recommendation 2: `floor.reg9_outcome` with the precedence `first_edge` → `not_decided_at_420W` → `no_change`; tested on splits and on a missing seed.
- Recommendation 3 (T3, T4): P restated for a window without slowdown; `floor.shock_heat_table` with its pass condition registered above, computed once before the first run, on the 6 shock runs' whole verdict window (baseline start to watch end, which contains prev and end); a start rule if none is covered; `first_edge` applies only to covered runs. microk8s was on in all 6 (by date); it is listed, not tested.
- Recommendation 4: the stopping rule forbids computing anything but `checks.json` of an invalid run before the rerun decision.
- Recommendations 5–8: pattern tightened (tested); `n_done` added and the three counts reported; microk8s downgraded and added to A12; the seed-1 consequence stated.
- **Not changed:** T5. The shock runs' seeds (1–3) differ from REG-9's (0–1), and a capacity, unlike a schedule, does not depend on the seed; `sustainable_no_backlog` is REG-6's label and its first edge already accepts it. The carry is a statement about sustained capacity at λ = 3, which is what REG-6 registered. The point is listed for the result: a `sustainable_no_backlog` seed shows that its schedule never kept a queue, not a measured capacity.

## 2026-11-08 · [DECISION] Owner approves REG-9 as written
- **Owner's answer:** "Approve as written", to the question whether REG-9 is approved for at most 2.2 GPU h, given that its only decision-changing outcome (`first_edge`, prior ≈ 0.4) changes the write-up of the default-pool negative. This also confirms the review's point that the write-up change is worth the cost.
- **VM at approval** (read-only, 12:32 UTC): rebooted about 1 min earlier; power limit 420 W (the reboot or the owner's 2026-11-07 setting; either way not 350 W); 36 °C, 0 %, 1 MiB, no compute process, no tmux session; 14 GB free; tree clean at `212327f`.
- **Next, in order:** commit and push; `floor.shock_heat_table()` once; the owner sets 350 W; the VM pulls; launch seed 0 by REG-9's Operations.

## 2026-11-08 · [OPS] REG-9 coverage check: all 6 default-pool λ = 3 shock runs are covered; REG-9 proceeds
- **Computed once,** by REG-9's start rule: `uv run python -m analysis.floor reg9_shock_heat` (`floor.shock_heat_table`). RUN(20261102-072216_wipe_preempt_r3_s1, floor.shock_heat_table), RUN(20261102-053935_wipe_preempt_r3_s2, floor.shock_heat_table), RUN(20261102-100744_wipe_preempt_r3_s3, floor.shock_heat_table), RUN(20261102-131353_burst_r3_s1, floor.shock_heat_table), RUN(20261102-135701_burst_r3_s2, floor.shock_heat_table), RUN(20261102-144008_burst_r3_s3, floor.shock_heat_table).
- **Inside each verdict window** (baseline start to watch end; 2100 samples for the wipes, 2220 for the bursts), all at 420 W, no HW-slowdown sample. SW-thermal share:
  - wipes s1, s2, s3: 0.0457, 0.0267, 0.0100;
  - bursts s1, s2, s3: 0.0095, 0.0086, 0.0050.
- **All 6 `covered`** (≤ 0.05, the registered pass condition). The closest, `20261102-072216_wipe_preempt_r3_s1` at 0.0457, passes by a small margin; that is stated with any `first_edge` result.
- **Next:** the owner sets 350 W; the VM pulls `d59efff`; seed 0 by REG-9's Operations.

## 2026-11-08 · [OPS] REG-9 seed 0 launched at 350 W
- **Pre-launch read** (13:41:11 UTC, PROBE(docs/probe/20261108_reg9/prelaunch_s0.txt)): power limit 350 W, set by the owner; 36 °C idle, 0 %, 1 MiB, no compute process; tree clean at `1a12624`; 14 GB free; no tmux session.
- **Launched:** `20261108-134121_long_pl350_pc_off_r3_s0` from `1a12624`, at 13:41:21 UTC, in tmux with a redirect to `~/reg9_s0.log`, no pipe. Schedule: 10,711 requests, 1365 sessions. Expected end about 14:45 UTC. Listed in `manifests/pending_copy.txt` until copied.

## 2026-11-08 · [OPS] REG-9 seed 0 INVALID on `no_errors` (2 client errors in 10,711); heat and power limit clean
- **Run:** `20261108-134121_long_pl350_pc_off_r3_s0`, ended about 14:45 UTC. Copied to the Mac with identical sha256 for all 10 files; the manifest gained 10 lines; removed from `manifests/pending_copy.txt`. The VM copy is kept.
- **Checks** (FILE(runs/20261108-134121_long_pl350_pc_off_r3_s0/checks.json)): `no_errors` failed with 10,709 ok and 2 `client_error`. Every other check passed:
  - `gpu_steady`: SW thermal 0.0006, 0 HW samples, clock CV 0.016, max 74 °C;
  - `power_limit`: 350 W in all 3608 samples;
  - `accounting`: 10,711 scheduled and recorded, 10,709 ok, equal to vLLM's success delta;
  - `arrival_rate`, `recorder`, `client_lag`, `clean_git`, `kv_capacity`.
- **What was read:** only `checks.json`, by REG-9's stopping rule. Not c_b, the backlog, any label, nor the two error rows of `requests.jsonl`.
- **Heat:** the 350 W cap held over the full hour, at 74 °C peak against 82 °C and SW thermal 0.296 at 420 W in REG-6's attempt (decisions.md 2026-11-07 [DECISION]).
- **Precedent:** one earlier client error, `20261105-130250_sweep_l1_pc_on_r4.5` (`ServerDisconnectedError`, cause unknown; decisions.md 2026-11-05 [OPS]); rerun unchanged.
- **By REG-9's stopping rule:** not a heat failure, so the rule gives a rerun of `configs/long_pl350_pc_off_r3_s0.yaml`, unchanged (1 of 2). Put to the owner before launch, as every GPU run is.

## 2026-11-08 · [OPS] REG-9 seed 0 rerun 1 of 2 launched (owner: "ok")
- **Owner's answer:** "ok", to the agent's recommendation to rerun seed 0 unchanged. Taken as approval of the rerun only; the two error rows of the invalid run were not read.
- **Pre-launch read** (16:48:32 UTC, PROBE(docs/probe/20261108_reg9/prelaunch_s0_rerun1.txt)): 350 W, 36 °C, 0 %, 1 MiB, no compute process; tree clean at `5fbafa1` after `git pull`; 14 GB free.
- **Launched:** `20261108-164842_long_pl350_pc_off_r3_s0` from `5fbafa1`, `configs/long_pl350_pc_off_r3_s0.yaml` unchanged, at 16:48:42 UTC, in tmux with a redirect to `~/reg9_s0_rerun1.log`. Expected end about 17:52 UTC. Listed in `manifests/pending_copy.txt` until copied.

## 2026-11-08 · [REG] REG-10 (exploratory): one G3′ burst/control pair at L1, 350 W, λ = 2.4 (GPU, ≈ 1.6 h)
- **ID:** REG-10. **Exploratory, not confirmatory:** λ is chosen after REG-8's data. **Not approved yet:** no GPU run before the owner approves this entry.
- **Why:** REG-8 found no λ_test (decisions.md 2026-11-07 [RESULT]): μ_warm 3.0, μ_sat,off 1.681, so REG-7's zone rule (largest multiple of 0.5 that is ≤ 0.8 μ_warm = 2.4 and ≥ 1.3 μ_sat,off = 2.185) has no grid value. The raw M2 condition, a load between 1.681 and the highest warm-healthy rate 3.0, is not empty (REG-8 [RESULT], alternative 3). No stuck attempt has run since 2026-11-04; this is the first in the only setup where M2 allows one.
- **Choice of λ = 2.4 (owner, 2026-11-08, after seeing REG-8's data):** REG-8's warm margin itself, 0.8 × 3.0, with the 0.5 grid dropped; it is ≥ 1.3 × 1.681 = 2.185, so both registered margins hold (DERIVED; `tests/test_gate.py::test_reg10_lambda_is_reg8s_warm_margin_and_above_its_floor_margin`). `slo_feasible` at 2.4: the smallest swept cache-on rate ≥ 2.4 is 3.0, pooled percent fast 0.990 ≥ 0.98 (RUN(20261107-104614_sweep_l1pl350_pc_on_r3, gate.sweep_rows), REG-8 [RESULT]). Dropping the grid is a registered choice changed after the data (rule A5), so the entry is exploratory.
  - The first draft used 2.25 (a 0.25 step). The review showed the step is a free parameter (every step of 0.05–0.3 except 0.25 gives 2.4), and that 2.4 widens the band the gate can detect (below). Put to the owner, who chose 2.4.
- **Question:** after a 180 s burst at λ = 2.4, does the L1 server at 350 W hold a cold backlog (a counting span) while a same-seed control without the burst is healthy?
- **Claim tested:** none confirmatory. A `pass` is a reason to register a confirmatory matrix (C1), not evidence for C1 by itself.
- **Setup:** REG-8's G3′, unchanged except λ:
  - `configs/stage2_control_l1pl350_r2.4.yaml`: `extends: stage2_l1pl350_base.yaml`, `seed: 1`, `workload.rate: 2.4`, `verdict.control_t_s: 1080`.
  - `configs/burst_l1pl350_r2.4_s1.yaml`: `extends: stage2_l1pl350_base.yaml`, `seed: 1`, `workload.rate: 2.4`, `trigger: {kind: burst, at_s: 900, duration_s: 180, rate: 2.4, prompt_tokens: 2944}`.
  - Both 2580 s, cache on, dev mode, 350 W `power_limit` check, `burst_min_kv_max: 0.95` (the burst must fill the pool, `configs/stage2_l1_base.yaml`).
  - **Schedule** (DERIVED, `harness.workload.build_schedule` on the resolved burst config; inputs, not results): 422 burst requests (2.34 req/s, 6902 prompt tok/s), the last at 1079.5 s. Session rate 2.548 in the baseline [480, 1080), 2.722 during the burst [900, 1080), so ≈ 5.1 req/s in all during the burst, and 2.359 over the watch [1080, 2580).
- **Detectable band** (DERIVED from the schedule and `stats.poisson_rate_upper(n, 300, 0.99)`): a span holds only if c_upper < min(λ, λp). λp in the three spans is 2.150, 2.677, 2.353, so a span can hold only if its completion rate c ≤ 1.953, 2.190, 2.147. The cold floor 1.681 is inside all three. A stuck state completing between about 2.0–2.2 and 2.4 req/s cannot give `pass`; it gives `drains` or `stuck_unconfirmed`.
- **Analysis, computed once after both runs are valid and copied:** `uv run python -m analysis.gate reg10` (`gate.reg10_gate`). It takes the latest valid control and burst run at λ = 2.4 (`gate.reg10_pick`; a rerun is launched only after an invalid run or an `inconclusive` pair) and calls `gate.reg8_gate_verdict` (350 W and equal λ checked; then `gate.gate_verdict` with REG-7's spans, baseline, cold-hit drop and confidence). Outcome, REG-7's labels with `inconclusive` split:
  - `stuck_unconfirmed`: `inconclusive` with the burst verdict `stuck` and the control `recovered` (the span test could not confirm);
  - `inconclusive`: every other `inconclusive` (an instrument gap);
  - `control_not_healthy`, `pass`, `drains`: as REG-7.
  - **Readouts:** `gate.overlap_share` over [1080, 2580) (decisive only under `drains`); never decisive: `gate.secondary_cb`, `gate.queued_miss_share` (per span, the share of cold later turns whose previous turn had no first token yet at their planned arrival: misses from open-loop queueing, not eviction), `gate.span_clock` (median busy SM clock in the baseline and each span).
- **Prediction** (BELIEF):
  - The burst run fills the pool (`burst_min_kv_max` passes) p ≈ 0.85: at 350 W the cache-off sweep was saturated (KV ≥ 0.85) from λ = 2, and the burst brings ≈ 5.1 req/s with 2.34 of them cold.
  - Given a valid pair: `pass` ≈ 0.25, `drains` ≈ 0.45, `control_not_healthy` ≈ 0.1 (seed-1 baseline load 2.548, against percent fast 0.990 at 3.0 on seed 0), `stuck_unconfirmed` ≈ 0.1, `inconclusive` ≈ 0.1. Overall `pass` ≈ 0.2.
  - Against the band: a stuck span should complete near the cold floor (1.681, plus a few hits), inside the band. A stuck state above the band is less likely (BELIEF); it would be counted as `drains` or `stuck_unconfirmed`, and ≈ 0.05 of the `drains` share is that case.
- **Decision under each outcome:**
  - **`pass`:** register REG-11, the confirmatory matrix at λ = 2.4 as REG-7 specified for a pass: burst seeds 2–5, each with a same-seed, same-duration control; "most" = ≥ 3 of 5 with the one-sided Clopper–Pearson bound. REG-10's pair is not counted in it.
  - **`drains`:** record c_b (`secondary_cb`) and 1 − c_b / μ_warm in M2. If `overlap_share` > 0.5: propose closed-loop turns to the owner (REG-7's rule). Otherwise the owner chooses the next factor. **A `drains` here does not by itself license writing up L1 as negative**: the band above leaves stuck states the gate cannot see. Any follow-up at λ = 2.5 is a second after-data deviation, and breaks the warm margin.
  - **`stuck_unconfirmed`:** not rerun (the same schedule would likely repeat it). Reported as "stuck by the verdict, not confirmed by a span", with the readouts; the owner decides.
  - **`control_not_healthy`:** no retry. REG-7's retry at λ − 0.5 = 1.9 is below 1.3 μ_sat,off = 2.185; the owner decides.
  - **`inconclusive`:** rerun the pair unchanged, at most twice.
  - **Burst run invalid on `burst_min_kv_max`:** not rerun. Reported as "one run at 2.4 did not fill the pool" (the server's timing varies between runs, so it is one run, not the schedule); the owner decides.
- **Alternatives:**
  1. **Open-loop queueing, not eviction:** with a backlog longer than the 5 s turn gap, a turn arrives before its previous turn's prefix is computed, and misses with any cache size. `queued_miss_share` measures it.
  2. **The detectable band** (above).
  3. **Seed:** μ_warm 3.0 and the floor come from seed 0 (660 s windows, no dev mode); the pair runs 2580 s on seed 1. `gate_verdict` checks c_upper against both λ and the span's λp (REG-7 review A).
  4. **Batched completions** make the Poisson bound optimistic (`stats.poisson_rate_upper`), so a span can hold that should not. A `pass` goes to REG-11 for seeds, not to a claim.
  5. **Dev mode** is on here and off in the sweeps (A6).
  6. **Overlap protection:** `overlap_share` decides under `drains`.
  7. **Heat or clock drift at 350 W:** `span_clock` against the baseline.
  8. **350 W:** a `pass` holds at 350 W only (A12). **One seed:** a reason for the matrix, not a result.
- **Stopping rule:** each run once; an invalid run (other than `burst_min_kv_max`) is rerun unchanged, at most twice; after a heat-invalid run the agent asks the owner first; a rerun decision reads only `checks.json`. An `inconclusive` pair is rerun at most twice.
- **Operations:** REG-9's: the limit read at 350 W, clean tree at the Mac's `main`, no GPU compute process, idle ≤ 45 °C, tmux with a redirect. Control first, then the burst run. Starts after REG-9 has finished.
- **Cost:** 2 × 2580 s plus start-up ≈ 1.6 GPU h; ≈ 4.8 h with every rerun of single runs; ≈ 14 h with two `inconclusive` reruns of the pair at their worst.
- **Code and files:** `analysis/gate.py` (`REG10`, `reg10_pick`, `reg10_gate`, `queued_miss_share`, `span_clock`, `python -m analysis.gate reg10`); `tests/test_gate.py` (3 new tests); the two configs above.
- **Not changed:** REG-8's result and settings; `REG8["step"]` stays 0.5; no published verdict.

### Adversarial review (separate subagent; it saw only the first draft at λ = 2.25, its diff and the code and configs those call; it opened no runs and no docs). Verbatim:

> **Adversarial review of REG-10 (rule F).** I read only the draft, the diff, the analysis/harness code it calls and the config chain. `uv run pytest tests/test_gate.py`: 30 passed. Schedules were built with `harness/workload.py` from the resolved configs (seed 1, 2580 s). They are inputs, not results.
>
> **1. Traces where the verdict is wrong or misleading**
>
> A. **Code bug: the rerun path breaks `reg10_gate`.** After an `inconclusive` pair, the draft says to rerun the pair unchanged. Both reruns are valid and match the same globs, so `find_runs` returns 2 runs of each kind and `reg10_gate` raises (FILE(analysis/gate.py:295-297)). Nothing in the code or the draft says which pair counts. The new test does not cover this case.
>
> B. **The gate can only detect part of the band M2 allows.** `burst_backlog` requires c_upper < min(λ, λp). On the seed-1 schedule (DERIVED, `planned_session_rate` logic on the built schedule), λp in the three spans is 2.023, 2.507 and 2.070. So the thresholds are 2.023, 2.25 and 2.070. With `poisson_rate_upper(n, 300, 0.99)`, a span holds only if c ≤ 1.83, 2.05 or 1.88 respectively.
> - Consequence: a real stuck state with c_b in (2.05, 2.25) cannot pass. The burst verdict would be `stuck`, which gives `inconclusive`. The stopping rule then reruns the same deterministic schedule twice, which is likely to repeat the result at about 3.2 GPU h each time.
> - At λ = 2.4 the same computation gives max passing c of 1.95, 2.19 and 2.14 (seed 1, its own schedule).
>
> C. **False `pass`: the Poisson bound may be too tight.** The docstring of `stats.poisson_rate_upper` says batched completions make the bound optimistic. In that case c_upper is too low and a span can hold that should not.
>
> D. **The draft's load figures are off.** The burst has 395 requests (2.19/s, 6460 prompt tok/s). Session load in [900, 1080) is 2.72/s, not 2.25, so the total during the burst is ≈ 4.9 req/s. Planned session rate over the watch [1080, 2580) is 2.19, below λ.
>
> **2. Strongest alternative explanation for each outcome**
> - **`pass`:**
>   - Open-loop queueing, not eviction. With a backlog longer than the 5 s turn gap, turn k+1 is scheduled before turn k's prefix is computed, so it misses even with an infinite cache. This is the opposite of the "overlap protection" in alternative 4.
>   - Separate it by the share of cold later turns whose previous turn had no first token yet.
>   - Also possible: late-run clock drift at 350 W. Separate by comparing SM clock in the spans with the baseline.
> - **`drains`:** 2.25 sits below the self-sustaining load (alternative 1). Or a stuck state with c_b > 2.05 that did not reach `stuck` by the verdict, e.g. a pf climb between [1380, 1980) and [1980, 2580). Neither is separable in one pair.
> - **`control_not_healthy`:** μ_warm 3.0 comes from 660 s seed-0 sweep windows, without dev mode. The control runs 2580 s on seed 1, with local load 2.445 in its baseline window [480, 1080). Drift or heat over a long run is not excluded by the sweep.
> - **`inconclusive`:** an instrument gap, or trace B (stuck but not confirmed). The response should differ between the two, and the draft treats them the same.
> - **Burst does not fill the pool:** the kv gauge is sampled at 1 s and may miss a peak. Or a scheduler token budget limits how much is admitted, so the pool does not fill. One run cannot tell these apart from "2.25 cannot fill".
>
> **3. Can the run change a decision? Is λ = 2.25 defensible?**
> - It can change a decision. `pass` leads to REG-11 (≈ 6.4 GPU h, DERIVED 8 × 0.8 h). `drains` and `control_not_healthy` hand the choice to the owner. But `drains` at 2.25 cannot support "L1 negative" because of trace B, and the draft does not say so.
> - The draft's numbers check out:
>   - 0.8 × 3.0 = 2.4; floor(2.4 / 0.25) × 0.25 = 2.25; 1.3 × 1.681 = 2.185.
>   - 2.25 − 1.681 = 0.569; 2.5 − 1.681 = 0.819.
>   - Cost: 1.43 h + start-up ≈ 1.6 h; worst cases 4.8 h and ≈ 14.4 h.
>   - `pass` ≈ 0.8 × 0.25 = 0.2.
> - **λ = 2.25 vs 2.5:** 2.5 breaks the registered 0.8 μ_warm margin, so 2.25 is the better of those two.
> - **The step is a free parameter.** Every step of 0.05, 0.1, 0.15, 0.2 or 0.3 gives 2.4; only 0.25 gives 2.25, and no sweep used a 0.25 grid. 2.4 respects both margins and widens the detectable band (trace B), at the cost of tighter control health (seed-1 baseline load 2.52).
> - So 2.25 is defensible as exploratory only if the reason for 0.25 is stated, e.g. control-health margin. Otherwise 2.4 is the more informative choice. This is the owner's call and should be recorded.
>
> **4. Recommendations**
> 1. **(Blocking)** Define which pair counts after an `inconclusive` rerun, e.g. the pair named in an [OPS] entry or the latest valid pair. Make `reg10_gate` select it and add a test for it.
> 2. **(Blocking)** Split `inconclusive`:
>    - an instrument gap is rerun as planned;
>    - `burst_verdict == stuck` with no span counting is not rerun unchanged. Report it as "stuck, not confirmed" and the owner decides.
> 3. **(Blocking)** Put the detectable band into the entry (c ≤ 1.83 / 2.05 / 1.88 against floor 1.681). Revise the `pass` 0.25 / `drains` 0.5 predictions, or justify them against that band.
> 4. **(Blocking)** Pre-commit that a `drains` at 2.25 does not by itself license writing up L1 as negative. Label any λ = 2.5 follow-up as a second after-data deviation that breaks the warm margin.
> 5. **(Owner decision, before approval)** Choose between 2.25 and 2.4 with a stated reason for the step. Record that the step was picked after seeing the data.
> 6. **(Recommended, register before data)** Add a non-decisive readout: the share of cold session turns in the spans whose previous turn had no first token yet when they arrived (open-loop queueing misses).
> 7. **(Recommended)** Correct the load description: 395 burst requests, 2.19/s, 6460 tok/s; session load 2.72/s during the burst; watch λp 2.19.
> 8. **(Minor)** Report a failed `burst_min_kv_max` as "one run did not fill the pool", since the server's timing varies between runs even though the schedule is fixed.
> 9. **(Minor)** Add the burst run's SM clock in the spans vs its baseline as a reported readout, to address heat.

**Changed because of it:**
- Recommendation 5: put to the owner, who chose λ = 2.4 (the warm margin itself, no step), recorded above as an after-data choice.
- Recommendation 1: `gate.reg10_pick` takes the latest valid run of each kind; tested with a rerun.
- Recommendation 2: `stuck_unconfirmed` split from `inconclusive` in `gate.reg10_gate`, not rerun; tested.
- Recommendation 3: the band, recomputed for λ = 2.4 (1.953, 2.190, 2.147), is in the entry; the predictions are restated against it.
- Recommendation 4: written into the `drains` row.
- Recommendations 6 and 9: `gate.queued_miss_share` and `gate.span_clock`, never decisive; `queued_miss_share` tested.
- Recommendation 7: the load figures are recomputed for λ = 2.4 from the schedule (the review's figures were for 2.25).
- Recommendation 8: written into the `burst_min_kv_max` row.

## 2026-11-08 · [DECISION] Owner approves REG-10 as written (λ = 2.4)
- **Owner's answer:** "ok", to the question whether REG-10 is approved as written: one exploratory control and burst pair at L1, 350 W, λ = 2.4, ≈ 1.6 GPU h, after REG-9. λ = 2.4 was the owner's choice over 2.25 earlier the same day (REG-10 entry).
- **Order:** REG-9 finishes first (seed 0 rerun 1 running; seed 1 only by `floor.reg9_seed1_may_start()`); then REG-10's control, then its burst run, by REG-10's Operations.

## 2026-11-08 · [OPS] REG-9 seed 0 rerun 1 INVALID on `no_errors` again (1 client error in 10,711); heat and power limit clean
- **Run:** `20261108-164842_long_pl350_pc_off_r3_s0`, ended about 17:53 UTC. Copied with identical sha256 for all 10 files; manifest +10 lines; removed from `manifests/pending_copy.txt`; VM copy kept.
- **Checks** (FILE(runs/20261108-164842_long_pl350_pc_off_r3_s0/checks.json)): `no_errors` failed, 10,710 ok and 1 `client_error`. All others passed: `gpu_steady` SW thermal 0.0009, 0 HW samples, CV 0.015, max 75 °C; `power_limit` 350 W in all 3608 samples; `accounting` 10,711 recorded, 10,710 ok, equal to vLLM's success delta.
- **What was read:** only `checks.json`, by REG-9's stopping rule.
- **Pattern** (DERIVED from the three `checks.json` files with `client_error`): 1 in `20261105-130250_sweep_l1_pc_on_r4.5` (4028 requests), 2 in `20261108-134121_long_pl350_pc_off_r3_s0`, 1 in this run; 4 errors in 25,450 requests of these three runs, about 1 per 6400. If errors are independent at that rate, the last allowed rerun has P(no error) ≈ exp(−10,711 / 6400) ≈ 0.19 (BELIEF on independence). The same risk applies to REG-10's runs (about 3000 requests each: ≈ 0.6 each).
- **Not done:** the last allowed rerun (2 of 2). Put to the owner with the alternative of first reading the error text of the 4 errored requests (a logged deviation from REG-9's rule, not capacity data).

## 2026-11-09 · [OPS] The client errors are a keep-alive race between client and server (diagnosis; owner-approved deviation from REG-9's rerun rule)
- **Deviation, approved by the owner** ("Read the error text first"): REG-9's stopping rule allows only `checks.json` before a rerun decision. The owner allowed reading the error rows of the 4 failed requests and the server logs. Nothing about capacity was computed: no c_b, backlog or label.
- **The 4 errors** (FILE(runs/<id>/requests.jsonl), `status == client_error`):
  - `20261105-130250_sweep_l1_pc_on_r4.5`: request 2580, `ServerDisconnectedError: Server disconnected`;
  - `20261108-134121_long_pl350_pc_off_r3_s0`: request 3264, `ClientOSError: [Errno 104] Connection reset by peer`; request 8029, `ServerDisconnectedError`;
  - `20261108-164842_long_pl350_pc_off_r3_s0`: request 4550, `ServerDisconnectedError`.
  - In each, t_sent is within 0.05 s of t_planned and there is no first token: the connection failed as the request was sent.
- **Server side:** no line matching error, exception or traceback in any of the three `server.log` files.
- **Settings:**
  - vLLM closes an idle HTTP connection after 5 s: SOURCE(vLLM 0.32.0 `vllm/envs.py`:VLLM_HTTP_TIMEOUT_KEEP_ALIVE, default 5; passed as `timeout_keep_alive` in `vllm/entrypoints/launchers/api_server/entry.py`).
  - The client's pool keeps an idle connection for 15 s: `aiohttp.TCPConnector(limit=0)` (FILE(harness/loadgen.py:89)), whose `keepalive_timeout` default is 15.0 in aiohttp 3.14.5 (`aiohttp/connector.py`), on the Mac and the VM.
- **Diagnosis (BELIEF, consistent with all of the above):** a request reuses a pooled connection that has been idle about 5 s, just as the server closes it. The server sees no request, so it logs nothing; the client gets a disconnect or reset. It is a property of the client, not of the server under test. It cannot bias a valid run, which has no errored request.
- **Test of the diagnosis:** with a client that does not reuse idle connections past the server's limit, the rate (about 1 per 6400 requests) should drop to 0. REG-9's last rerun would show it.
- **Proposed fix (harness change, for the owner):** below, in the next entry if approved. Nothing changed yet.

## 2026-11-09 · [REG] Amendment to REG-9 and REG-10 (approved): a new client connection per request (`loadgen_force_close`)
- **Approved by the owner:** the fix ("New connection per request"), then the amendment and every registered run of REG-9 and REG-10 ("Alright, plan it, run all all planed ones", 2026-11-09). The registrations' own owner checkpoints stand (a heat rerun, `stuck_unconfirmed`, a burst that does not fill the pool).
- **Why:** 4 requests in 25,450 failed at send time with `ServerDisconnectedError` or `Connection reset by peer`, invalidating REG-9 seed 0 twice (decisions.md 2026-11-08 [OPS], 2026-11-09 [OPS]). The diagnosis (decisions.md 2026-11-09 [OPS]): vLLM closes idle connections after 5 s (SOURCE(vLLM 0.32.0 vllm/envs.py:VLLM_HTTP_TIMEOUT_KEEP_ALIVE)), the client pool keeps them 15 s and reuses the oldest first (SOURCE(aiohttp 3.14.5 connector.py:BaseConnector._get, `popleft`), per the review), and a reused connection races the close (BELIEF). The server logged no error.
- **Harness change:** `harness/loadgen.py` `make_connector(cfg)`: `aiohttp.TCPConnector(limit=0, force_close=bool(cfg.get("loadgen_force_close")))`. Absent or false = the previous pool, so every earlier config and re-check is unchanged. Still unlimited, still no retries or timeouts (rule 2). Each request also records `t_connected`, when its new connection was open (aiohttp `TraceConfig.on_connection_create_end`; None for a reused one), so the connect time inside TTFT is measured (review recommendation 5).
- **REG-9:** its configs were used, so new ones: `configs/long_pl350fc_pc_off_r3_s0.yaml` and `_s1.yaml` extend them and add only `loadgen_force_close: true` (resolved: each differs from REG-6's config only by the two power keys, this key and `name`). `floor.REG9["runs_pattern"]` becomes `*_long_pl350fc_pc_off_r3_s[01]`, and `reg_table` refuses a run without `loadgen_force_close: true` (review trace B). No run of the first configs was valid. Everything else in REG-9 is unchanged.
  - **Reruns:** the count starts again for the new configs (each seed once, an invalid run rerun at most twice), because the cause of both failures is fixed. The two invalid runs stay on record. Budget per seed: the 2 invalid runs plus at most 3 new ones; for seed 0 that is ≤ 3.3 more GPU h.
  - **Not seen before the reset (review recommendation 4):** no c_b, backlog or label of the two invalid runs was computed or looked at; `reg9_table` reads valid runs only and was never run on them. Only their `checks.json` and the 4 error rows were read.
  - **If any `client_error` recurs under `loadgen_force_close`** (REG-9 or REG-10): the diagnosis is wrong or incomplete. Stop, report to the owner; no further rerun under the reset count.
  - **The carry to 420 W now crosses two differences** (review trace 3): power limit and connection mode (the 6 shock runs used the pool). Opening a connection per request adds work on the client and on vLLM's API event loop, so if anything it lowers the capacity measured here (BELIEF). Then a `sustainable` λ = 3 with that overhead is still sustainable without it: the same direction as assumption P, so a `first_edge` still changes the decision. `t_connected − t_sent` per request is reported with the result, to size the overhead.
- **REG-10:** its two configs had not been used; `loadgen_force_close: true` is added to both, with a note in their headers. `gate.reg10_gate` refuses a run without the key (review trace A). Nothing else changes.
- **Effect on measurement (BELIEF):** each request opens a loopback TCP connection: well under 1 ms against a 1 s TTFT SLO and a planned-arrival clock (latency is measured from t_planned, so it is counted, not hidden). The server's HTTP layer handles more connections; at ≤ 5.1 req/s this is small. Not separable from other run-to-run variation; comparisons with older runs (pool) carry this difference, stated in each result.
- **Prediction:** 0 client errors in the next runs. Weak as a test (review): under the old pool P(0 errors) ≈ e^−1.7 ≈ 0.18 for one REG-9 run and ≈ 0.03 for two (DERIVED from 4 / 25,450 × about 10,800 requests).
- **Tests:** `tests/test_e2e_fake.py::test_force_close_opens_a_connection_per_request_and_is_off_when_absent` (also checks `t_connected`); `tests/test_floor.py::test_reg9_is_reg6_with_the_350w_runs_only` and `test_reg9_table_refuses_a_run_without_a_passed_350w_check` (pooled run refused); `tests/test_gate.py::test_reg10_gate_takes_the_latest_valid_pair_and_splits_inconclusive` (pooled run refused).
- **Open (review):** whether vLLM's uvicorn starts a keep-alive timer on a new connection; not checked (BELIEF that it cannot matter with `Connection: close`).

### Adversarial review (separate subagent; it saw only the first draft, its diff, the code it touches and the installed aiohttp source; it opened no runs and no docs). Verbatim:

> **Adversarial review (rule F): amendment adding `loadgen_force_close` to REG-9 and REG-10**
>
> **1. Does it remove the race?**
> Yes, for the race that was diagnosed. In aiohttp 3.14.5:
> - With `force_close=True`, `keepalive_timeout` is set to None. SOURCE(aiohttp 3.14.5 connector.py:BaseConnector.__init__)
> - On release, every connection is closed and never goes back into `_conns`. SOURCE(connector.py:BaseConnector._release, line 828)
> - Each request is sent with `Connection: close`. SOURCE(client_reqrep.py:1693)
>
> So no request is ever written to a connection that was already used. Old behaviour, for comparison: the pool reuses the *oldest* idle connection first (`conns.popleft()`, connector.py:744). After a spike in concurrency, that means picking connections idle for up to 15 s, against vLLM's 5 s close. This is consistent with the diagnosis but does not prove it.
>
> What is left:
> - The server could still reset a fresh connection before reading the request (accept backlog full, worker overloaded). Any connect error is still counted as `client_error` and fails `no_errors` (FILE(harness/checks.py:63-66)).
> - I could not check whether vLLM's uvicorn/h11 starts a keep-alive timer on a new connection. Neither vLLM nor uvicorn is installed on the Mac. BELIEF; add it to open-questions.
> - Port / TIME_WAIT exhaustion is not a risk. About 5.1 req/s × 60 s TIME_WAIT ≈ 306 sockets, against roughly 28k ephemeral ports on loopback. DERIVED. Host is the IP 127.0.0.1, so no DNS (FILE(configs/base.yaml:9)).
> - Tests: 20 of 20 pass for `uv run pytest tests/test_e2e_fake.py tests/test_floor.py`.
>
> **2. Bias**
> - `t_sent` is stamped before `session.post` (FILE(harness/loadgen.py:46-47)). So the time to open a connection lands in TTFT and is invisible to `client_lag`. Arrivals stay open-loop: the connect happens inside each send task.
> - Under a stuck state, vLLM's single API event loop may accept connections late. That would look like server latency, which could confound "stuck" with "slow to accept". Today "small" is only a BELIEF.
> - **Confound for the carry:** REG-9's carry to the 420 W shock runs (SHOCK_RUNS_R3, which used the pool) now crosses two differences, power limit and connection mode. The draft states this only after the fact ("stated in each result"). It needs to be in the registration now.
>
> **3. Resetting the rerun count, and wrong-verdict traces**
> - Resetting is defensible only if the invalidation could not depend on the outcome, and if no one saw the floor labels of the two invalid runs. Errors may also cluster with load state (connection churn in overload), so this needs to be stated, not assumed.
> - **Trace A (REG-10):** `reg10_pick` takes the latest valid run whose name matches. Config names are unchanged, so a run launched from a commit before the amendment (no force_close) would match and be judged. Nothing checks the key.
> - **Trace B (REG-9):** the pattern is the only guard. Unlike `power_limit_w`, `reg_table` never checks the key.
> - **Weak prediction:** under the old pool, P(0 errors in one REG-9 run) = e^-1.7 ≈ 0.18, and ≈ 0.03 for two runs. DERIVED from 4/25,450 × ~10,800 requests per run. A single clean run says little about whether the diagnosis is right.
>
> **4. Recommendations**
> 1. **(Blocking)** Add `cfg.get("loadgen_force_close") is True` to `reg_table` for REG9 (next to the power-limit check) and to `reg10_gate`, so both traces raise an error. Add a test for each.
> 2. **(Blocking)** Register now what happens if any `client_error` recurs under force_close: the diagnosis is wrong, stop and go to the owner, and no further rerun under the reset count. Also state the total rerun budget per seed (2 invalid + up to 3 new) and the cost in GPU hours.
> 3. **(Blocking)** State in the `[REG]` that REG-9's carry to the pooled 420 W runs now crosses power plus connection mode. Say whether a `first_edge` outcome still changes the decision under that confound.
> 4. **(Blocking)** Confirm and record that the floor labels of REG-9's invalid runs were not computed or looked at before the reset.
> 5. Before running, log when each connection opens: aiohttp `TraceConfig.on_connection_create_end`, written as `t_connected` in requests.jsonl. This turns the overhead BELIEF into a measurement, and it cannot be added after the runs. Recommended; blocking only if the owner treats the TTFT confound as material.
> 6. Tag the diagnosis "vLLM closes idle connections after 5 s" with SOURCE/PROBE, or mark it BELIEF. A cheap check: the failed requests should come after a drop in concurrency.
> 7. The REG-10 config headers still say "Contents as REG-7/REG-8 registered". Add a note that they were amended.

**Changed because of it:** recommendations 1–4 (guards with tests; the stop rule on a recurring error and the budget; the two-difference carry and why `first_edge` still counts; the record that nothing of the invalid runs was computed), 5 (`t_connected`, tested against the fake server), 6 (SOURCE tags for both timeouts; the race itself marked BELIEF; the concurrency check not done) and 7 (config headers). The open uvicorn question is listed above.

## 2026-11-09 · [OPS] REG-9 (amended) seed 0 launched with a new connection per request
- **Pre-launch read** (2026-11-08 19:09:04 UTC on the VM clock; the entry date is the owner's local date, PROBE(docs/probe/20261108_reg9/prelaunch_fc_s0.txt)): 350 W, 45 °C, 0 %, 1 MiB, no compute process; tree clean at `933d2cf` after `git pull`; 13 GB free; no tmux session.
- **Launched:** `20261108-190906_long_pl350fc_pc_off_r3_s0` from `933d2cf`, `configs/long_pl350fc_pc_off_r3_s0.yaml`, in tmux with a redirect to `~/long_pl350fc_pc_off_r3_s0.log`. Expected end about 20:13 UTC. Listed in `manifests/pending_copy.txt` until copied.
- **Next, by the owner's approval of all registered runs:** if valid, `floor.reg9_seed1_may_start()`; seed 1 if true; then REG-10's control and burst run.

## 2026-11-09 · [DECISION] Standing instructions while the owner is away (REG-9 and REG-10)
- **Owner's answers** (2026-11-09):
  - "Yes, rerun once after cooling": a heat-invalid REG-9 or REG-10 run is rerun unchanged once the GPU is idle at ≤ 45 °C, within the registered rerun limit, without asking first. A second heat failure stops the queue until the owner is back.
  - "Write up + draft next REG": when REG-10 is done, compute it once, log the `[RESULT]`, and draft and review the next registration (REG-11 on `pass`; otherwise the change the readouts point to). No new registration runs before the owner approves it.
- **Unchanged, so they still stop the queue:** a `client_error` under `loadgen_force_close` (amendment); `stuck_unconfirmed`; a burst run that does not fill the pool; a power limit other than 350 W (setting it needs root); any unexpected pre-launch check.
- **The run order is as approved:** REG-9 seed 0 (running), seed 1 only if `floor.reg9_seed1_may_start()`, then REG-10's control and burst run.

## 2026-11-09 · [OPS] REG-9 seed 0 VALID (0 client errors with force_close); `sustainable`; seed 1 starts
- **Run:** `20261108-190906_long_pl350fc_pc_off_r3_s0`, ended about 20:13 UTC. Copied with identical sha256 for all 10 files; manifest +10 lines; removed from `manifests/pending_copy.txt`.
- **Checks** (FILE(runs/20261108-190906_long_pl350fc_pc_off_r3_s0/checks.json)): VALID. `no_errors` 10,711 ok, **0 client errors** (amendment's prediction: hit; weak as a test, P ≈ 0.18 under the old pool). `gpu_steady` SW thermal 0.001, 0 HW samples, CV 0.016, max 75 °C; `power_limit` 350 W in all 3608 samples.
- **Start rule, computed once** (`floor.reg9_seed1_may_start()`, through `floor.reg9_table`): seed 0 `sustainable`, c_b 3.2712 req/s against 1.05 × λp = 1.05 × 3.0487 = 3.2011 (DERIVED); 7 backlogged stretches totalling 1036.0 s; 3389 completions behind c_b. RUN(20261108-190906_long_pl350fc_pc_off_r3_s0, floor.reg9_table). So seed 1 starts.
  - It clears the threshold by 0.070 req/s, about 2 % (DERIVED: 3.2712 / 3.2011 − 1 = 0.022): within the c_b noise the review named (relative SD about 2–3 %, alternative 6). Stated now, before seed 1.
  - Prediction (model.md row 13): seed 0 c_b ≈ 3.2–3.45 and `sustainable` ≈ 0.5: hit.

## 2026-11-09 · [OPS] REG-9 seed 1 launched
- **Pre-launch read** (PROBE(docs/probe/20261108_reg9/prelaunch_fc_s1.txt)): 350 W, 38 °C, 0 %, 1 MiB, no compute process; tree clean at the Mac's `main` after `git pull`; no tmux session.
- **Launched:** `20261108-201227_long_pl350fc_pc_off_r3_s1`, `configs/long_pl350fc_pc_off_r3_s1.yaml`, at 20:12:27 UTC, in tmux with a redirect to `~/long_pl350fc_pc_off_r3_s1.log`. Expected end about 21:16 UTC. Listed in `manifests/pending_copy.txt` until copied.

## 2026-11-09 · [RESULT] REG-9: outcome `no_change`; seed 0 `sustainable`, seed 1 `unclear` (c_b 3.115 against 3.184); REG-6's first edge is not applied
- **Runs, both valid** at 350 W in all samples, 0 client errors with `loadgen_force_close`: `20261108-190906_long_pl350fc_pc_off_r3_s0` (SW thermal 0.001, 75 °C) and `20261108-201227_long_pl350fc_pc_off_r3_s1` (FILE(runs/20261108-201227_long_pl350fc_pc_off_r3_s1/checks.json): 10,575 ok, SW thermal 0.000, 0 HW samples, CV 0.015, max 75 °C, 350 W in 3608 of 3608 samples). Seed 1 copied with identical sha256 for 10 files; manifest +10; removed from `manifests/pending_copy.txt`.
- **Computed once:** `uv run python -m analysis.floor reg9` (`floor.reg9_table`, `floor.reg9_outcome`). RUN(20261108-190906_long_pl350fc_pc_off_r3_s0, floor.reg9_table), RUN(20261108-201227_long_pl350fc_pc_off_r3_s1, floor.reg9_table):

  | seed | label | λp | c_b | 1.05 λp | backlog_s | stretches | n_done |
  |---|---|---|---|---|---|---|---|
  | 0 | `sustainable` | 3.0487 | 3.2712 | 3.2011 | 1036 | 7 | 3389 |
  | 1 | `unclear` | 3.0323 | 3.1153 | 3.1840 | 451 | 7 | 1405 |

  1.05 λp DERIVED. Seed 1: c_b / λp = 3.1153 / 3.0323 = 1.027 (DERIVED), above λp but under the 5 % margin.
- **Outcome `no_change`** (registered precedence): seed 1 is neither sustainable label, and no seed is `not_sustainable`. **No statement changes.** REG-6's first edge is not applied: the 6 default-pool λ = 3 shock runs are not reclassified as non-tests of C1, and μ_off = 2 is not recorded as an underestimate by this route. A1 stays open.
- **Connect overhead** (amendment; reported, not a decision input): `uv run python -m analysis.floor reg9_connect` (`floor.connect_overhead`, added with this entry, `tests/test_floor.py::test_connect_overhead_counts_only_requests_with_a_new_connection`). Every request opened a new connection. t_connected − t_sent median 0.547 / 0.560 ms, p99 1.24 / 1.31 ms, max 38 / 49 ms (seed 0 / seed 1). RUN(20261108-190906_long_pl350fc_pc_off_r3_s0, floor.connect_overhead), RUN(20261108-201227_long_pl350fc_pc_off_r3_s1, floor.connect_overhead). About 0.1 % of the 1 s SLO at the p99 (DERIVED).
- **Prediction** (model.md row 13): validity p ≈ 0.8 each, both valid (after the client-error fix); seed 0 `sustainable` ≈ 0.5: hit; seed 1 `sustainable_no_backlog` ≈ 0.55 (modal): miss. Seed 1 had 451 s of backlog, over the 300 s minimum, so its schedule did hold a queue. `first_edge` ≈ 0.4: did not occur.
- **Alternatives** (rule A2):
  1. **c_b noise** (REG-9 alternative 6): both seeds sit within about 2–3 % of their thresholds (seed 0 +2.2 %, seed 1 −2.2 %, DERIVED from the table). Seed 1's c_b rests on 1405 completions over 451 s. A true capacity of about 3.2 for both seeds fits both labels. Separating it needs more backlogged time per seed (longer runs, or more seeds), not this pair.
  2. **The capacity is near λ = 3 at 350 W:** c_b 3.12–3.27 against λp ≈ 3.03–3.05 means cache-off at the default pool is only 3–8 % above the load. With P, 420 W is at least this, so λ = 3 is near, not clearly below, the cache-off capacity. Not separable from 1 with these data.
  3. **Shorter backlogs give lower c_b** (REG-6 alternative 2: smaller batches at a short queue): seed 1's backlog is less than half of seed 0's and its c_b is lower. Two points; not a test.
  4. **The 350 W clock and force_close** both lower measured capacity, if anything (P and the amendment's carry); they bias toward `no_change`, not away from it. Their size is not measured (A12).
- **What follows:** none of REG-9's outcomes changes the next experiment. REG-10 starts now by the owner's approval (decisions.md 2026-11-09 [DECISION]). The power limit stays at 350 W.

## 2026-11-09 · [OPS] REG-10 control launched
- **Pre-launch read** (2026-11-08 21:16:44 UTC, VM clock; PROBE(docs/probe/20261108_reg9/prelaunch_reg10_control.txt)): 350 W, 39 °C, 0 %, 1 MiB, no compute process; tree clean at `dc62f76` (the Mac's `main`) after `git pull`; 13 GB free; no tmux session.
- **Launched:** `20261108-211646_stage2_control_l1pl350_r2.4`, `configs/stage2_control_l1pl350_r2.4.yaml` (force_close), in tmux with a redirect to `~/stage2_control_l1pl350_r2.4.log`. 2580 s; expected end about 22:00 UTC. Listed in `manifests/pending_copy.txt` until copied.
- **Next:** if valid, the burst run `configs/burst_l1pl350_r2.4_s1.yaml`; then `gate.reg10_gate` once.

## 2026-11-09 · [OPS] REG-10 control VALID; burst run starts
- **Run:** `20261108-211646_stage2_control_l1pl350_r2.4`. Copied with identical sha256 for 10 files; manifest +10; removed from `manifests/pending_copy.txt`.
- **Checks** (FILE(runs/20261108-211646_stage2_control_l1pl350_r2.4/checks.json)): VALID. 6168 ok, 0 client errors; SW thermal 0.001, 0 HW samples, CV 0.015, max 75 °C; 350 W in 2586 of 2586 samples; arrival rate 2.420 against 2.4. Only `checks.json` was read; no verdict or label computed (REG-10: computed once after both runs).

## 2026-11-09 · [OPS] REG-10 burst run launched
- **Pre-launch read** (2026-11-08 22:02:46 UTC, VM clock; PROBE(docs/probe/20261108_reg9/prelaunch_reg10_burst.txt)): 350 W, 37 °C, 0 %, 1 MiB, no compute process; tree clean at the Mac's `main` after `git pull`; no tmux session.
- **Launched:** `20261108-220248_burst_l1pl350_r2.4_s1`, `configs/burst_l1pl350_r2.4_s1.yaml` (force_close), in tmux with a redirect to `~/burst_l1pl350_r2.4_s1.log`. 2580 s; expected end about 22:47 UTC. Listed in `manifests/pending_copy.txt` until copied.
- **Next:** if valid, `uv run python -m analysis.gate reg10` once, then the `[RESULT]`.

## 2026-11-09 · [RESULT] REG-10: `drains`; the burst filled the pool, the backlog cleared at 3.40 req/s, and the server was fully back by 600 s after the burst; `overlap_share` 0.608 > 0.5, so closed-loop turns are proposed to the owner
- **Runs, both valid** at 350 W in all samples, 0 client errors with `loadgen_force_close`:
  - control `20261108-211646_stage2_control_l1pl350_r2.4` (decisions.md 2026-11-09 [OPS]);
  - burst `20261108-220248_burst_l1pl350_r2.4_s1` (FILE(runs/20261108-220248_burst_l1pl350_r2.4_s1/checks.json): 6590 ok; 422 of 422 burst requests sent; `manipulation` KV max during the burst 0.9998 ≥ 0.95, so **the burst filled the pool**; SW thermal 0.002, 0 HW samples, CV 0.024, max 75 °C; 350 W in 2586 of 2586 samples). Copied with identical sha256 for 10 files; manifest +10; removed from `manifests/pending_copy.txt`.
- **Computed once:** `uv run python -m analysis.gate reg10` (`gate.reg10_gate`). RUN(20261108-211646_stage2_control_l1pl350_r2.4, gate.reg10_gate), RUN(20261108-220248_burst_l1pl350_r2.4_s1, gate.reg10_gate). Verdicts: control `recovered`, burst `recovered`. **Outcome `drains`.**

  | span (s after the burst's last arrival) | n_done | c | c_upper | λp | hit share (baseline 0.838) | KV | waiting q | holds |
  |---|---|---|---|---|---|---|---|---|
  | 600–900 | 655 | 2.183 | 2.390 | 2.150 | 0.841 | 0.160 | 0.000 | no |
  | 900–1200 | 796 | 2.653 | 2.880 | 2.677 | 0.838 | 0.236 | 0.003 | no |
  | 1200–1500 | 713 | 2.377 | 2.592 | 2.350 | 0.838 | 0.183 | 0.000 | no |

  In every span the hit share is at the baseline, KV is low, nothing waits, and c tracks λp: no span is cold or backlogged, so none qualifies.
- **Readouts:**
  - `overlap_share` over [1080, 2580): **0.608**, above REG-7's 0.5 limit. 61 % of the session cache hits after the burst came from a previous turn that was still running.
  - `secondary_cb` (burst end to end of arrivals): `sustainable`, one backlogged stretch of 393 s, c_b **3.397** req/s over 1335 completions, against λp 2.359. For M2: 1 − c_b / μ_warm = 1 − 3.397 / 3.0 = −0.132 (DERIVED). The post-burst backlog completed faster than the warm TTFT-healthy rate, and 2.0× the cache-off floor 1.681 (DERIVED: 3.397 / 1.681).
  - `queued_miss_share`: NaN, 0.0, NaN. Spans 1 and 3 had no cold later turns to count.
  - `span_clock`: baseline 1875 MHz, spans 1875 / 1860 / 1875. No clock drift.
- **Prediction** (model.md row 14): burst fills the pool p ≈ 0.85: hit. `drains` ≈ 0.45 (modal): hit. A stuck span near 1.7 req/s: not seen.
- **What the detectable band means here:** REG-10 says a `drains` does not by itself license a negative, because a stuck state completing above about 2.0–2.2 req/s could not hold a span. That case did not occur: the spans have no backlog at all (q ≤ 0.003, hit share at baseline), and the one post-burst backlog completed at 3.4 req/s. This pair shows recovery, not a stuck state hidden by the band.
- **Alternatives** (rule A2):
  1. **Overlap protection (open-loop turns):** a session's next turn arrives while its previous turn is still running, so its prefix blocks are pinned in use and cannot be evicted. The cache stays warm through the backlog, and the backlog drains at near-warm speed. Supported by `overlap_share` 0.608 and c_b 3.4 ≫ 1.681. Separated by closed-loop turns: if the backlog then completes near the cache-off floor and holds, this was the cause.
  2. **The burst was too short to evict the sessions:** 422 cold prompts × 2944 tokens fill the pool (KV 0.9998), but sessions keep only about 6–10 in flight (`n` in the spans), so few session prefixes may have been resident to lose. The hit share inside the backlog is not computed by a registered function, so not separable here; a longer or larger burst, or a hit-share readout over the backlog stretch, would separate it.
  3. **λ = 2.4 has too much headroom:** M2 needs c(s*) < λ. The measured post-burst completion rate 3.397 is 1.4× λp (DERIVED: 3.397 / 2.359), so this state cannot be stuck at 2.4, whatever caused it. This is what `drains` says. It does not separate alternative 1 from 2.
  4. **One seed, 350 W, dev mode:** as registered (alternatives 3, 5, 8); none of them points toward a hidden stuck state.
- **Decision (registered):** record c_b in M2 (done, docs/model.md M2). `overlap_share` > 0.5, so **closed-loop turns are proposed to the owner** as the next single factor. This changes research rule 2 (open-loop arrivals) and the harness, so only the owner can decide. A draft registration follows (REG-11), written and reviewed by the standing instruction; **it does not run before the owner approves it.** L1 is not written up as negative: REG-10 is one exploratory pair, and the readout points to a mechanism that open-loop traffic cannot test.

## 2026-11-09 · [REG] REG-11 (exploratory, draft): REG-10's pair with closed-loop turns, L1, 350 W, λ = 2.4 (GPU, ≈ 1.6 h)
- **ID:** REG-11. **Exploratory.** **Not approved:** no GPU run, and no merge of its code into `main`, before the owner approves this entry. The code is on branch `reg11-closed-loop` (commit `78c1106`); `main` and the VM do not have it.
- **Why:** REG-10 gave `drains` with `overlap_share` 0.608 > 0.5 (decisions.md 2026-11-09 [RESULT]). REG-7's rule for that case: propose closed-loop turns to the owner as the next single factor (decisions.md 2026-11-05 [REG] REG-7, "If `overlap_share` > 0.5"). With open-loop turns, a session's next turn often arrives while its previous turn still runs, so the prefix it needs is pinned in use and cannot be evicted (REG-10 [RESULT], alternative 1). The post-burst backlog completed at 3.397 req/s, 2.0× the cache-off floor (RUN(20261108-220248_burst_l1pl350_r2.4_s1, gate.secondary_cb)). Closed-loop turns remove the overlap by construction and test whether it is what kept the cache warm.
- **Owner decisions this needs (C. Authority):**
  1. **Research rule 2** ("open-loop arrivals") changes for this registration's runs only: **session starts and burst requests stay open loop**; a session's later turn is released at the previous turn's end (or failure time) plus the schedule's own gap between the two turns. Rule 2's other parts stay: no client retries or timeouts, unlimited connections, no gateway.
  2. **Checks**, changed only when `workload.sessions.closed_loop` is true:
     - `client_lag` measures `t_sent − t_released`;
     - `arrival_rate` counts only the open-loop arrivals (turn 0: session starts at λ / turns, plus burst requests), because later turns follow the server, and counting them would fail a stuck run for being stuck;
     - **new check `release_chain`** (review T2): every later turn never sent must have been blocked by its own session (its previous turn never ended, or ended so late that end + planned gap is past the drain deadline, 1 s slack). A chain that stops releasing turns fails the run instead of looking like a slow server. A chain task that raises writes its unsent turns as `client_error`, so `no_errors` fails too.
  3. **Definition of TTFT and e2e latency** (`analysis/load.py:load_run`, docs/definitions.md on the branch): measured from `t_released` when it is set, otherwise from `t_planned` as before. **Percent fast stays binned by `t_planned`** (review T3): a turn released late, or never, counts as fast or not in the window of its planned time. This keeps the verdict windows on the schedule's clock, as in every earlier run; its cost is that never-released turns near the end count as misses in their planned window, which pushes a burst run toward `stuck`, never toward `recovered`. `unreleased` reports their number per span. A false `pass` cannot come from this alone, since `pass` also needs a span that holds (review). Under closed loop, the time a session waited for its own previous turn is the system's queueing, not this request's latency. `t_planned` stays the schedule's time, so `gate.planned_session_rate` (λp) is still the planned rate, not a rate that follows completions (see "Why λp stays static").
- **Question:** with closed-loop turns and everything else as in REG-10, does a 180 s burst at λ = 2.4 leave the L1 server at 350 W holding a cold backlog (a counting span) while the same-seed control is healthy?
- **Claim tested:** none confirmatory. A `pass` is a reason for a confirmatory matrix, not evidence for C1.
- **Setup:** REG-10's two configs, extended, with one key added:
  - `configs/stage2_control_l1pl350cl_r2.4.yaml`: `extends: stage2_control_l1pl350_r2.4.yaml`, `workload.sessions.closed_loop: true`.
  - `configs/burst_l1pl350cl_r2.4_s1.yaml`: `extends: burst_l1pl350_r2.4_s1.yaml`, the same key.
  - Resolved (`load_config`, `with_defaults`, `harness.run.expand`): each differs from its REG-10 config only by `name` and `workload.sessions.closed_loop` (checked). Seed 1, λ = 2.4, 2580 s, burst at 900 s for 180 s at 2.4 req/s with 2944-token prompts, cache on, dev mode, 350 W check, `burst_min_kv_max` 0.95, force_close. The schedule file is the same as REG-10's (the key is read only by loadgen).
- **Harness change** (`harness/loadgen.py`): with `closed_loop`, each session runs as one task (`session_chain`): turn 0 at its planned time, turn k at `t_end(k−1) + t_planned(k) − t_planned(k−1)`. Burst requests are sent open loop as before. Each record gains `t_released` (None in open loop). A turn not yet released at the drain deadline is written as `unfinished` (a miss) from a placeholder, so `accounting` still sees every scheduled request. After a failed turn (`http_error`, `client_error`), the next turn is released at the failure time plus the gap (review T1: `send` returned None on `http_error`; fixed, tested); any such failure already invalidates the run (`no_errors`).
- **Why λp stays static:** under closed loop, releases follow completions: in a stuck state the release rate is about the completion rate times 7/8 (non-final turns) plus the session-start rate 0.3 (DERIVED: 2.4 / 8). A span test against the *realized* rate could then never hold, since c_upper would sit above it. Against the planned rate λp and λ, the test asks the question M2 asks: does the server complete less than the offered load? Sessions keep arriving at λ / 8 and each brings 8 turns, so the long-run demand is λ in either loop mode (BELIEF; true if sessions are not cut off by the run's end).
- **Analysis, computed once after both runs are valid and copied:** `uv run python -m analysis.gate reg11` (`gate.reg11_gate` = `gate.reg10_gate(REG11)`, `REG11 = {**REG10, "closed_loop": True}` with the `cl` patterns). It refuses a run whose `closed_loop` is not true (and `reg10_gate` now refuses a closed-loop run). Labels and outcomes are REG-10's: `pass`, `drains`, `control_not_healthy`, `stuck_unconfirmed`, `inconclusive`. Readouts, never decisive except as stated under `drains`:
  - REG-10's. `overlap_share` is 0 by construction (a harness check). `queued_miss_share` now tests the previous turn's first token against the release time (review T4: against the static `t_planned` it would be large exactly when sessions fall behind); open-loop runs are unchanged.
  - `gate.release_delay` per span, and `release_delay_baseline` over the 600 s before the burst (review 6): how far sessions fell behind their schedule, against a healthy closed loop's own drift.
  - **`gate.shock_size`** (review 1): session requests due by the burst's end and not ended by then (`outstanding`), and post-burst backlogged time (`backlog_s`, `secondary_cb`'s stretches). Reference: REG-10's burst run, `gate.reg11_reference()`. **`shock_comparable`** = both values ≥ 0.5 × REG-10's (`REG11["comparable_frac"]`, fixed in code before the reference was computed). The reference, computed after that: outstanding 267, backlog_s 393.0 (RUN(20261108-220248_burst_l1pl350_r2.4_s1, gate.reg11_reference)); so comparable means ≥ 134 outstanding and ≥ 196.5 s backlogged (DERIVED).
  - `gate.turn0_share` per span (review 7): share of first turns among session completions; `gate.unreleased` per span (review 4).
- **Prediction** (BELIEF):
  - Both runs valid p ≈ 0.85; the burst fills the pool p ≈ 0.9 (the same burst filled it to 0.9998 in REG-10).
  - Control `recovered` p ≈ 0.85. Without overlap, warm hits rest on freed blocks still cached; at KV 0.16–0.24 in REG-10's spans little is evicted.
  - Given a valid pair: `pass` ≈ 0.15, `drains` ≈ 0.55, `control_not_healthy` ≈ 0.1, `stuck_unconfirmed` ≈ 0.1, `inconclusive` ≈ 0.1.
  - Post-burst `secondary_cb` lower than REG-10's 3.397, point ≈ 2.8.
  - `shock_comparable` p ≈ 0.35. The review's estimate (DERIVED there, with a BELIEF session lifetime): closed loop bounds the session backlog by the active sessions, ≈ 100 against ≈ 378 turns queued in open loop, so the shock is likely smaller.
- **Decision under each outcome:**
  - **`pass`:** report `turn0_share` against REG-10's spans (the queue-mix alternative, review). Draft REG-12, the confirmatory matrix with closed-loop turns at λ = 2.4: burst seeds 2–5, each with a same-seed control; ≥ 3 of 5 with the one-sided Clopper–Pearson bound. REG-11's pair is not counted.
  - **`drains` with `shock_comparable`:** record `secondary_cb` in M2 next to REG-10's. Open-loop overlap is then not what kept L1 out of a stuck state at λ = 2.4 (REG-10's alternative 1 is out; 2 and 3 remain). The owner picks the next factor (a larger burst, a higher λ, a different setup) or writes L1 at λ = 2.4 up as negative in both loop modes, with REG-10's detectable-band caveat.
  - **`drains` without `shock_comparable`:** reported as "closed loop weakened the shock"; nothing is ruled out (review). The next step, for the owner: a larger trigger under closed loop (a longer or denser burst), sized from `shock_size`.
  - **`control_not_healthy`:** closed-loop traffic changes the warm side; no stuck attempt in closed loop before a closed-loop cache-on sweep measures μ_warm. The owner decides.
  - **`stuck_unconfirmed`:** not rerun; reported with the readouts; the owner decides.
  - **`inconclusive`:** rerun the pair unchanged, at most twice.
  - **Burst run invalid on `burst_min_kv_max`:** not rerun; the owner decides.
- **Alternatives:**
  1. **Closed loop changes more than the overlap:** it bounds the post-burst session backlog by the number of active sessions and delays later turns when the server is slow (self-throttling). So the same burst is a smaller shock (review). `shock_size` against REG-10, with the comparability rule above, decides whether a `drains` can be read.
  5. **Queue mix** (review): in a closed-loop backlog, first turns (no session prefix) may make up more of the completions, lowering the cold capacity for a reason other than eviction. `turn0_share`.
  2. **μ_warm and the floor come from open-loop sweeps;** λ = 2.4 is 0.8 of an open-loop μ_warm. Closed-loop warm capacity may differ (alternative 3 of the prediction).
  3. **End-of-run truncation:** sessions fall behind their schedule in a backlog, so turns near 2580 s can be cut off by the drain deadline; they count as misses. The spans end 1500 s after the burst, at the run's last planned arrival; `release_delay` shows how late releases run there.
  4. REG-10's alternatives 2–8 stand (band, seed, batched completions, dev mode, heat, 350 W, one seed).
- **Stopping rule:** REG-10's. Each run once; an invalid run (other than `burst_min_kv_max`) is rerun unchanged, at most twice; a heat-invalid run is rerun once after cooling (owner's standing instruction, 2026-11-09), a second heat failure stops; a `client_error` stops; a rerun decision reads only `checks.json`.
- **Operations:** merge `reg11-closed-loop` into `main` after approval; push to `origin` and `vm`; then REG-10's operations (350 W read, clean tree at the Mac's `main`, no compute process, idle ≤ 45 °C, tmux with a redirect). Control first.
- **Cost:** ≈ 1.6 GPU h; ≈ 4.8 h with every single-run rerun.
- **Code and files** (branch `reg11-closed-loop`): `harness/loadgen.py` (`new_rec`, `session_chain`, `t_released`); `harness/checks.py` (`client_lag`, `arrival_rate` in closed loop); `analysis/load.py` (latency from `t_released`); `harness/checks.py` (`release_chain`); `analysis/gate.py` (`release_delay`, `release_delay_baseline`, `shock_size`, `turn0_share`, `unreleased`, `closed_loop`, `reg10_gate(spec)`, `REG11`, `reg11_reference`, `reg11_shock_comparable`, `reg11_gate`; `python -m analysis.gate reg11` and `reg11_reference`; `queued_miss_share` against the release time); `docs/definitions.md` (percent fast, closed-loop latency); the two configs; tests: `tests/test_e2e_fake.py` (4 new: closed-loop timing, checks and latency; open loop unchanged; a chain after an error, at the deadline and when it raises), `tests/test_gate.py` (3 new). Full suite: 213 passed on the branch.
- **Not changed:** every open-loop run, config and check result: absent `closed_loop`, loadgen, checks and latency are as before (tested). REG-10's result and its readouts (`queued_miss_share` gives the same values on open-loop runs: `t_released` is absent or None).

### Adversarial review (separate subagent; it saw only the first draft, its diff and the code and configs those call; it opened no runs and no docs). Verbatim:

> ## Adversarial review (rule F), REG-11 draft. Sources read: the draft, `reg11.diff`, harness/loadgen.py, harness/checks.py, harness/workload.py, analysis/gate.py, load.py, margin.py, derived.py, configs base/stage2_base/stage2_cap_base. `uv run pytest -q tests/test_gate.py`: 33 passed.
>
> ### 1. Traces on which the verdict or the harness is wrong
>
> **T1: harness bug after an `http_error` (FILE(harness/loadgen.py:59, :104, :98)).** On a non-200 response, `send` runs a bare `return` inside `try`, so it returns `None` instead of `rec`. In `session_chain`, `prev = None`. On the next turn `if prev is not None` is false, so `release` keeps the failed turn's release time, and turn k+1 goes out at once with a stale `t_released`. The chain then carries on from that stale base. `no_errors` would already invalidate the run (checks.py:68), so this cannot produce a wrong verdict on a valid run. But it breaks the release formula the draft states, and the tests never cover it. Fix: `return rec` on that path.
>
> **T2: a silent chain death becomes "stuck"-looking misses.** `session_chain` writes placeholders for every turn first (loadgen.py:93-94). If the chain task raises anything outside `send`'s handler, `gather(..., return_exceptions=True)` swallows the exception (loadgen.py:167). The placeholders are then written as `unfinished`. Every check still passes:
> - `accounting` passes: recorded = scheduled (checks.py:78).
> - `no_errors` passes: it ignores `unfinished` (checks.py:68).
> - `arrival_rate` passes: it now counts turn 0 only (checks.py:121).
>
> Those turns count as pf misses in `_level` (load.py:164). In closed loop, nothing checks that later turns were released at all. I found no current code path that raises, so this is a monitoring gap, not a known bug.
>
> **T3: `percent fast` is binned by planned time while latency is measured from release (load.py:163-164 vs load.py:23-25).** Suppose a stuck burst run where sessions have fallen behind by D. A turn planned in the verdict's end window [1980, 2580) is released at t_planned + D. If that release is after the drain deadline (t_planned.max + 300 s, loadgen.py:134), the server never sees the turn, yet it counts as a miss in the window of its *planned* time. This works against `recovered` and toward `stuck`. It is harmless in the control (D is small). But pf no longer measures the server state during the window. The span test is not affected, because it counts completions by `t_end` (margin.py:67). The registration should say which binning it uses, and why.
>
> **T4: the draft's claim that `queued_miss_share` is "0 or NaN by construction" is false.** It tests `prev_first > t_planned` against the *static* `t_planned` (gate.py:299). Under closed loop, any delayed session satisfies that. The readout will be large exactly when sessions fall behind. `overlap_share` (gate.py:167) is 0 by construction, as claimed.
>
> **Span test (DERIVED).** `holds` needs waiting > 0 at every scrape and c_upper < min(λ, λp) (gate.py:101). With a non-empty queue the server is capacity-limited, so c is its capacity whatever the loop mode. Releases then follow c (≈ 0.3 + 7c/8), but λp and λ stay the demand. So "server completes less than offered load" still holds. I found no false-pass trace: a healthy server has c ≈ λ and no persistent queue. The static λp is sound.
>
> **`client_lag` and `arrival_rate`.** I found no failure trace. A gap shorter than the time to write the record and build the prompt is rare: P(gap < 5 ms) ≈ 2.5e-4 with mean gap 20 s (DERIVED: 1 − e^(−0.005/20)). The burst rows are turn 0 and are counted, and `expected` adds them (checks.py:121-124). The cost: `arrival_rate` no longer tests later turns at all (see T2).
>
> ### 2. Strongest alternative explanation per outcome
>
> **`drains` (the likely outcome): closed loop shrinks the shock, not just the overlap.**
> - In open loop, the session turns planned during the 180 s burst all join the queue: ≈ 2.4 × 7/8 × 180 ≈ 378 (DERIVED).
> - In closed loop, each session holds at most one queued turn. The queue is bounded by the active sessions: ≈ 0.3 × (7 × 20 s + Σe2e) + 0.3 × 180 ≈ 42 + 54 ≈ 100 (DERIVED; the session lifetime is a BELIEF).
> - So the post-burst session backlog is about 4× smaller, and the cache has less time to go cold.
>
> A `drains` therefore does not separate "overlap was not what kept the cache warm" from "the trigger got weaker". The decision text "REG-10's alternative 1 is out" overreaches. The draft's own alternative 1 (self-throttling) is the same concern, and `release_delay` alone does not size it.
>
> **`pass`:** T3 could make the burst verdict `stuck` from unreleased-turn misses. But `pass` also needs a span that holds, which needs a capacity-limited span with c_upper < λ. So T3 alone cannot create a pass. The remaining alternative is a different queue mix (many turn-0 prompts with no prefix, 640 tokens): a lower cold capacity because the closed loop changes the mix, not because of eviction. Separate the two by the share of turn-0 requests among the span's completions, compared with REG-10.
>
> **`control_not_healthy`:** closed-loop warm capacity differs from the open-loop μ_warm (the draft's alternative 2), or latency measured from release interacts with the baseline pf.
>
> ### 3. Can it change a decision? Are the prediction and table coherent?
>
> Yes: `pass` leads to the confirmatory matrix, and the other outcomes go to the owner. The table is not fully coherent, though. `drains` (p ≈ 0.55) is mapped to a conclusion, "the overlap is ruled out", that the run cannot support without a shock-size readout. Without that readout, `drains` changes only "what to try next", which the owner picks anyway.
>
> ### 4. Recommendations
> 1. **(Blocking)** Register a shock-size readout before the run, with a pre-stated reading, so `drains` can be read:
>    - the session requests waiting or running at the burst's end;
>    - the length of the post-burst backlogged stretch (waiting > 0);
>    - both compared with REG-10's run.
>
>    Reword the `drains` decision: overlap is ruled out only if the backlog is comparable (a threshold fixed now). Otherwise the result is "closed loop weakened the shock".
> 2. **(Blocking)** Fix T1: return `rec` from the `http_error` path (loadgen.py:59). Add a fake-server test for a closed-loop chain after an error and after cancellation at the deadline.
> 3. **(Blocking)** Add a closed-loop check, or a `checks.json` detail that the stopping rule reads, for T2. Every `unfinished` turn with `t_sent` None must have a predecessor that is unfinished or whose end plus gap is past the deadline. Also log any chain-task exception.
> 4. (Not blocking) State in the registration that pf stays binned by `t_planned` (T3), and report the count of never-released turns in each verdict window.
> 5. (Not blocking) Correct the `queued_miss_share` claim (T4). Either drop it for closed loop or compute it against `t_released`.
> 6. (Not blocking) Report `release_delay` for the pre-burst baseline too. A healthy closed loop drifts by Σe2e, so the post-burst values need a reference.
> 7. (Not blocking) Under `pass`, report the share of turn-0 requests among the span's completions against REG-10 (the queue-mix alternative).

**Changed because of it:** all seven recommendations. 1: `shock_size`, `reg11_reference` and `shock_comparable` (0.5 × REG-10's, fixed in code before REG-10's reference was computed), and the `drains` decision split in two. 2: `send` returns its record on `http_error`; fake tests for a chain after an error, at the deadline and when it raises. 3: the `release_chain` check, and a chain that raises writes its unsent turns as `client_error`. 4: the binning stated under owner decision 3; `unreleased` per span. 5: `queued_miss_share` against the release time. 6: `release_delay_baseline`. 7: `turn0_share`, read under `pass`. The review's line numbers refer to the first draft; the fixes moved them. **Not changed:** the static λp (the review found it sound).

## 2026-11-09 · [DECISION] Owner approves REG-11 as written
- **Owner's answer:** "ok", to the question whether REG-11 is approved (decisions.md 2026-11-09 [REG]): REG-10's pair with closed-loop turns, ≈ 1.6 GPU h, with its three owner decisions: rule 2 relaxed for these two runs only (later turns wait for the previous turn; session starts and burst stay open loop), the closed-loop checks (`client_lag`, `arrival_rate`, new `release_chain`), and latency measured from the release time.
- **Done:** branch `reg11-closed-loop` (`78c1106`) merged into `main`; open-loop behaviour unchanged (tested).
- **Standing instructions** (decisions.md 2026-11-09 [DECISION]) apply to REG-11 as to REG-10: one heat rerun after cooling, stop on a `client_error`, `stuck_unconfirmed`, a burst that does not fill the pool, a limit other than 350 W, or an unexpected pre-launch check. After REG-11: compute it once, log the `[RESULT]`, draft and review the next registration; nothing new runs before the owner approves it.
- **Order:** control `configs/stage2_control_l1pl350cl_r2.4.yaml`, then the burst run `configs/burst_l1pl350cl_r2.4_s1.yaml`.

## 2026-11-09 · [OPS] REG-11 control launched
- **Pre-launch read** (2026-11-09 03:42:53 UTC, VM clock; PROBE(docs/probe/20261108_reg9/prelaunch_reg11_control.txt)): 350 W, 43 °C, 0 %, 1 MiB, no compute process; tree clean at `1944c2b` (the Mac's `main`) after `git pull`; no tmux session.
- **Launched:** `20261109-034255_stage2_control_l1pl350cl_r2.4`, `configs/stage2_control_l1pl350cl_r2.4.yaml` (closed-loop turns, force_close), in tmux with a redirect to `~/stage2_control_l1pl350cl_r2.4.log`. 2580 s; expected end about 04:27 UTC. Listed in `manifests/pending_copy.txt` until copied.

## 2026-11-09 · [OPS] REG-11 control VALID; burst run starts
- **Run:** `20261109-034255_stage2_control_l1pl350cl_r2.4`. Copied with identical sha256 for 10 files; manifest +10; removed from `manifests/pending_copy.txt`.
- **Checks** (FILE(runs/20261109-034255_stage2_control_l1pl350cl_r2.4/checks.json)): VALID. 6168 ok of 6168 scheduled, 0 client errors; `client_lag` p99 2.2 ms (against the release time); `arrival_rate` closed loop, 707 session starts against 702 expected; `release_chain` 0 unsent later turns; SW thermal 0.001, 0 HW samples, CV 0.012, max 76 °C; 350 W in 2601 of 2601 samples. Only `checks.json` was read.
- **Note:** the live progress line in the VM log prints `lag` against the schedule's `t_planned`, so under closed loop it shows the sessions' accumulated delay (4–8 s in the first minute), not client lag. Not a check input.

## 2026-11-09 · [OPS] REG-11 burst run launched
- **Pre-launch read** (2026-11-09 04:28:26 UTC, VM clock; PROBE(docs/probe/20261108_reg9/prelaunch_reg11_burst.txt)): 350 W, 39 °C, 0 %, 1 MiB, no compute process; tree clean at the Mac's `main` after `git pull`; no tmux session.
- **Launched:** `20261109-042828_burst_l1pl350cl_r2.4_s1`, `configs/burst_l1pl350cl_r2.4_s1.yaml` (closed-loop turns, force_close), in tmux with a redirect to `~/burst_l1pl350cl_r2.4_s1.log`. 2580 s; expected end about 05:13 UTC. Listed in `manifests/pending_copy.txt` until copied.
- **Next:** if valid, `uv run python -m analysis.gate reg11` once, then the `[RESULT]`.

## 2026-11-09 · [RESULT] REG-11: `pass`, the first stuck state of the study (exploratory, one seed): with closed-loop turns, after the burst the L1 server at 350 W stays cold and backlogged for the whole 1500 s watch, completing at the cache-off floor, while the same-seed control is healthy
- **Runs, both valid** at 350 W in all samples, 0 client errors:
  - control `20261109-034255_stage2_control_l1pl350cl_r2.4` (decisions.md 2026-11-09 [OPS]);
  - burst `20261109-042828_burst_l1pl350cl_r2.4_s1` (FILE(runs/20261109-042828_burst_l1pl350cl_r2.4_s1/checks.json)): 5638 ok and 952 unfinished of 6590 scheduled (accounting passes; vLLM success delta 5638); 422 of 422 burst requests sent; **`manipulation` KV max during the burst 0.9998**; `release_chain`: 702 later turns never released, 0 unexplained (each one's previous turn never ended, or ended too late); `client_lag` p99 2.6 ms; `arrival_rate` 1129 open-loop arrivals against 1134 expected; SW thermal 0.000, 0 HW samples, CV 0.012, max 77 °C; 350 W in 2884 of 2884 samples. Copied with identical sha256 for 10 files; manifest +10; removed from `manifests/pending_copy.txt`.
  - The burst run's waiter stopped early on an SSH timeout while the owner was off the local network ("TMUX GONE", a false alarm of the agent's wait script, which treated a failed connection as a dead session). The run itself was never touched; the VM was reached over Tailscale and the wait resumed.
- **Computed once:** `uv run python -m analysis.gate reg11` (`gate.reg11_gate`). RUN(20261109-034255_stage2_control_l1pl350cl_r2.4, gate.reg11_gate), RUN(20261109-042828_burst_l1pl350cl_r2.4_s1, gate.reg11_gate). Verdicts: control `recovered`, burst **`stuck`**. **Outcome `pass`: all three spans hold.**

  | span (s after the burst's last arrival) | n_done | c | c_upper | λp | sessions' hit share (baseline 0.828) | counter hit rate | KV | running N | waiting q (mean / min) | preemptions | holds |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | 600–900 | 515 | 1.717 | 1.901 | 2.150 | 0.000 | 0.000 | 0.950 | 29.8 | 169.4 / 159 | 14 | yes |
  | 900–1200 | 537 | 1.790 | 1.978 | 2.677 | 0.000 | 0.000 | 0.950 | 31.0 | 200.3 / 166 | 19 | yes |
  | 1200–1500 | 532 | 1.773 | 1.961 | 2.350 | 0.000 | 0.000 | 0.951 | 30.6 | 247.7 / 223 | 13 | yes |

  In every span the cache gives no hits at all, KV is full, the server's own queue is never empty and grows from span to span, and even the upper bound of the completion rate is below both λ = 2.4 and λp. The spans complete at 1.02–1.06× the cache-off floor μ_sat,off = 1.681 (DERIVED: 1.717 / 1.681, 1.790 / 1.681).
- **Readouts:**
  - `secondary_cb` (burst end to end of arrivals): **`not_sustainable`**, one backlogged stretch over the whole 1499 s, c_b **1.793** req/s over 2687 completions, against λp 2.359. For M2: 1 − c_b / μ_warm = 1 − 1.793 / 3.0 = 0.402 (DERIVED). REG-10's open-loop pair had c_b 3.397 (−0.132).
  - `shock_size`: 65 session requests outstanding at the burst's end, 1499 s backlogged; REG-10's reference 267 and 393 s (`gate.reg11_reference`). `shock_comparable` false (65 < 133.5). **This rule only reads a `drains`;** under `pass` it says the closed-loop shock was the smaller one at the burst's end, and it held anyway.
  - `release_delay`: 347, 360, 477 s in the spans, against 11.8 s in the 600 s before the burst. Sessions fell 6–8 minutes behind their schedule.
  - `unreleased`: 27, 257, 418 later turns planned in the spans and never sent (misses in percent fast, binned by planned time, registered). They do not enter the span test, which counts completions by `t_end`.
  - `turn0_share` (registered for `pass`): 0.155, 0.179, 0.148; REG-10's spans 0.122, 0.124, 0.126 (`uv run python -m analysis.gate reg11_turn0_reference`, `gate.reg11_turn0_reference`, added with this entry). First turns make up 0.03–0.05 more of the completions here. A first turn is the shortest prompt (2048 + 128 = 2176 tokens; turn k adds 256, to 3968 at turn 7; DERIVED from `configs/base.yaml` user and reply tokens and `configs/stage2_l1_base.yaml` system tokens), so with every turn cold the shift makes the mix lighter. **The queue-mix alternative is not supported:** it would predict a heavier mix.
  - `queued_miss_share` 0.0, 0.0, 0.0; `overlap_share` NaN (no cached tokens after the burst): as constructed.
  - `span_clock`: baseline 1860 MHz, spans 1830 MHz (−1.6 %, DERIVED: 30 / 1860). A small drop, against a cold-state completion rate 40 % below the warm rate.
- **Prediction** (model.md row 15): both valid: hit. Burst fills the pool: hit. Control `recovered`: hit. `pass` ≈ 0.15: **it happened, against the modal `drains` (0.55)**. Post-burst c_b ≈ 2.8: miss (1.79). `shock_comparable` p ≈ 0.35: false. REG-10's own prediction of a stuck span "near the floor (≈ 1.7 req/s)" fits the spans here.
- **What it shows, and what it does not:**
  - **Observed:** at one load, the same server and the same session schedule end in two different states. Without the burst it is healthy: the control `recovered`, the hit share is 0.83. After a 180 s burst it sits cold for at least the 1500 s watch: 0 hits, KV full, a growing queue, completions at the cache-off floor. This is the two-state picture M2 requires, c(s*) < λ ≤ c_warm, here with c(s*) ≈ 1.79 < 2.4.
  - **Derived, two runs, one seed each:** in open loop the same burst drained (REG-10, `overlap_share` 0.608); in closed loop it held, with a smaller shock at the burst's end. This supports REG-10's alternative 1 (open-loop turns protect the cache through a backlog) over alternative 2 (the burst too short).
  - **Not shown:** that it holds in most seeds (C1 needs a matrix); that it lasts beyond 1500 s or recovers after a drop in load (C1 conditions 5–6); the causal loop (C2 needs the controls that cut a link). The result is at 350 W, with dev mode, with closed-loop turns (a registered deviation from rule 2), at L1 only.
- **Alternatives** (rule A2):
  1. **A slow drain, not a stuck state:** the queue grows across the spans (mean 169 → 200 → 248) and c_upper < λ in each. A drain would show a falling queue. Over a longer watch it could still turn around. C1's confirmation run (a 4500 s watch) separates them.
  2. **A harness artifact (the closed loop):** the queue and the hit rate are the server's own (`vllm:` metrics and counters, waiting > 0 at every scrape), not the client's. `release_chain` explains every unsent turn; `client_lag` is 2.6 ms. If the chain logic were wrong, the server would see fewer requests, not a full KV and a growing queue. Not fully ruled out: same-seed controls in closed loop, more seeds.
  3. **Closed-loop demand is not λ:** releases follow completions, so the offered rate is not fixed by the schedule. But the server's waiting queue grows in every span, so requests arrive faster than they complete: the server is below its offered load, whatever that load is. The span test compares c with the planned λp (registered, review: sound).
  4. **Queueing, not eviction:** a turn released 5 s after its previous turn ends then waits minutes in the server's queue (`release_delay` 6–8 min). Its prefix is freed when the previous turn ends and is gone by the time it is admitted. That is C2's link "cached prefixes evicted before their session's next turn", lengthened by the queue. Whether it is eviction or something else (e.g. an unrelated miss) needs the C2 controls (caching off, protected prefixes).
  5. **Preemption and recompute:** 13–19 preemptions per span at KV 0.95 add recompute work. Part of the loop, or a separate cost; not separable here.
  6. **Heat:** the clock is 1.6 % lower in the spans. Too small for a 40 % drop in completion rate (BELIEF; the cache-off floor itself was measured at 350 W).
  7. **One seed, dev mode, 350 W** (REG-10 alternatives 3, 5, 8).
- **Decision (registered):** `pass` → `turn0_share` against REG-10 (above) and **draft REG-12, the confirmatory matrix with closed-loop turns at λ = 2.4**; REG-11's pair is not counted. Drafted and reviewed next by the owner's standing instruction; **it does not run before the owner approves it.** The seed count in the registered text is inconsistent ([CORR] below); REG-12 puts it to the owner.

## 2026-11-09 · [CORR] "Burst seeds 2–5 … ≥ 3 of 5" counts four seeds as five
- **Error:** REG-7's `pass` branch (decisions.md 2026-11-05 [REG] REG-7) says "burst seeds 2–5, each with a same-seed, same-duration control. 'Most' = ≥ 3 of 5". Seeds 2–5 are four. In REG-7 the G3 pair (seed 1) may have been meant as the fifth, but REG-10 and REG-11 (both written by the agent) added "REG-10's pair is not counted" / "REG-11's pair is not counted" and kept "≥ 3 of 5", which makes the rule impossible to apply as written. The agent copied it twice without checking; the review of neither registration caught it.
- **Effect:** none yet; no matrix has run. REG-12 states the seeds explicitly and puts the choice (four seeds 2–5, or five seeds 2–6) to the owner.
- **Not changed:** the old entries (append-only).

## 2026-11-09 · [REG] REG-12 (confirmatory, draft): the shock matrix of REG-11's cell, closed-loop turns at L1, 350 W, λ = 2.4, burst seeds 2–6 each with a same-seed control (GPU, ≈ 8 h)
- **ID:** REG-12. **Confirmatory** for the C1 matrix condition ("stuck in most seeds, the control recovered", docs/claims.md C1). **Not approved:** no GPU run before the owner approves this entry.
- **Why:** REG-11 gave `pass` (decisions.md 2026-11-09 [RESULT]). Its registered decision: draft the confirmatory matrix with closed-loop turns at λ = 2.4, burst seeds with same-seed controls, REG-11's pair not counted. One seed is not a result (REG-11 alternative 7).
- **Seed count: five seeds, 2–6, "most" = ≥ 3 of 5** ([CORR] 2026-11-09: REG-7's "seeds 2–5 … ≥ 3 of 5" named four seeds). **Chosen by the owner on 2026-11-09** ("go with 5 seeds"), before any REG-12 run and before this entry's review; the alternative was seeds 2–5 with ≥ 3 of 4.
- **Question:** in REG-11's cell, does the burst run end `stuck` while its same-seed control ends `recovered`, in most seeds?
- **Claim tested:** C1's matrix condition at one load, with closed-loop turns (rule 2 relaxed as for REG-11, owner 2026-11-09). C1's other conditions (the 4500 s confirmation, the drop to λ = 1) and C2 are not tested here.
- **Setup:** for each seed s in 2–6, two configs, each REG-11's with only `name` and `seed` changed (resolved with `load_config`, `with_defaults`, `harness.run.expand`: checked):
  - `configs/stage2_control_l1pl350cl_r2.4_s<s>.yaml`: `extends: stage2_control_l1pl350cl_r2.4.yaml`, `seed: s`;
  - `configs/burst_l1pl350cl_r2.4_s<s>.yaml`: `extends: burst_l1pl350cl_r2.4_s1.yaml`, `seed: s`.
  - So: L1, 350 W check, closed-loop turns, force_close, dev mode, λ = 2.4, 2580 s, burst at 900 s for 180 s at 2.4 req/s with 2944-token prompts, `burst_min_kv_max` 0.95, control `control_t_s` 1080.
  - The seed changes the session schedule and the burst draw. Schedule inputs (DERIVED, `harness.workload.build_schedule` on the resolved burst configs; inputs, not results): burst requests 463, 416, 407, 450, 436 for seeds 2–6 (REG-11's seed 1: 422); session requests 5999, 5790, 6615, 6356, 6173 (seed 1: 6168).
- **Per-seed outcome** (`gate.reg12_pair`): **exactly one** valid control and one valid burst run of that seed (`gate.reg12_only` refuses two, review T4: a rerun is made only after an invalid run, never on a verdict or label, so a second valid run is outside the registration), checked for seed, λ, 350 W, force_close and closed loop, then `gate.reg10_gate` with REG-11's settings. A seed is **stuck** if the burst run's `load.verdict` is `stuck` and the control's is `recovered` (C1's test, PROTOCOL §3). Every other valid pair counts in n and not in k (conservative: a control that is not `recovered` makes its seed not stuck). **Beside k, fixed now (review T2, recommendation 2): `k_pass`**, the seeds that are stuck *and* whose span test gives `pass` (spans burst-free, cold, backlogged, c_upper < min(λ, λp)). k decides `supports`; k_pass decides what follows it (below).
  - **Known asymmetry** (review T5): the burst run's baseline is [300, 900) s and the control's [480, 1080) s (`load.verdict` with `control_t_s` 1080); both are judged on the same end window [1980, 2580) s. As in REG-10 and REG-11.
- **Result, computed once after all 10 runs are valid and copied:** `uv run python -m analysis.gate reg12` (`gate.reg12_table`): per seed (control verdict, burst verdict, gate label, stuck, stuck_pass), k of n with the one-sided 95 % Clopper–Pearson upper bound (rule H), k_pass, `n_control_recovered`, and **`outcome`** (`gate.reg12_outcome`, in this order, review T1): `controls_not_healthy` if 2 or more controls are not `recovered`; else **`supports` if k ≥ 3**; `some` if k = 1–2; `none` if k = 0 (so `none` always has ≥ 4 recovered controls).
  - **Per-seed readouts** (never decisive): REG-11's (`release_delay`, `shock_size`, `turn0_share`, `unreleased`, λp per span) and **`gate.end_window`** of the burst run (review recommendation 4): burst requests with a first token in the verdict's end window (a burst backlog still draining, T2), later turns planned there and never sent, sent but unfinished (T3), and the end window's queue and queue slope with the time to empty. On REG-11's burst run, for reference only (RUN(20261109-042828_burst_l1pl350cl_r2.4_s1, gate.end_window)): 0 burst requests, 675 never-released and 193 unfinished later turns, queue 224 rising at 0.165 per s. So in REG-11 the burst itself had cleared, but percent fast in the end window is diluted heavily by never-released turns; the stuck verdict there also rests on the server's hit counter (0) and its growing queue.
  - What k can show (DERIVED with `stats.cp_upper`; the lower bound is 1 − cp_upper(n − k, n)): with n = 5, k = 3 gives the stuck probability p ∈ [0.189, 0.924], k = 4 gives [0.343, 0.990], k = 5 gives [0.549, 1]. Only 5 of 5 shows p > 0.5 at 95 %. "Most" is C1's count rule, not a statistical claim about p; the result says so.
- **Prediction** (BELIEF): per seed, P(stuck by C1's test, i.e. burst `stuck` **and** control `recovered`) ≈ 0.65, with P(burst `stuck`) ≈ 0.72 and P(control `recovered`) ≈ 0.9 (review: p's definition). REG-11 held in one seed with a smaller shock than REG-10's; seeds 3 and 4 have fewer burst requests (416, 407) and seed 4 more session load. Then k ≥ 3 of 5 ≈ 0.77 (DERIVED from p: 0.336 + 0.312 + 0.116). Each control `recovered` p ≈ 0.9. Each run valid p ≈ 0.9; each burst fills the pool p ≈ 0.95.
- **Decision under each outcome:**
  - **`controls_not_healthy`** (checked first): λ = 2.4 is not reliably warm-healthy with closed-loop turns; the matrix cannot speak to C1, whatever k is. The owner decides (a closed-loop cache-on sweep to measure μ_warm first).
  - **`supports` (k ≥ 3) with k_pass ≥ 3:** draft for the owner C1's confirmation run (a burst run with a 4500 s watch, then the drop to λ = 1, conditions 5–6) and C2's controls (caching off; protected prefixes), in that order. Report the cell as "stuck in k of 5" with the bound; C1's status changes only after the owner reviews it (a paper claim).
  - **`supports` with k_pass < 3:** reported as "stuck by C1's verdict in k of 5; the span test confirms k_pass". Only C1's confirmation run is drafted next, since it separates a long drain from a stuck state; C2's controls wait for it.
  - **`some` (k = 1–2):** stuck in some seeds. Report k of 5 with the bound; the owner chooses between more seeds, a larger trigger, or reporting the cell as seed-dependent.
  - **`none` (k = 0, ≥ 4 controls recovered):** REG-11's `pass` did not reproduce; reported as a one-seed result. Under the prediction P(k = 0) ≈ 0.35⁵ ≈ 0.005 (DERIVED, review), so this would weigh strongly against it. The owner decides.
  - **The queue stops** (a burst that does not fill the pool, a second heat failure, a `client_error`, a limit other than 350 W, an unexpected pre-launch check; review recommendation 7): no table is computed. The seeds run so far are reported from `checks.json` only, and the owner decides.
- **Alternatives:**
  1. **Seed-dependent load:** session load and burst size vary across seeds (above). A stuck seed may just be a heavier seed. `gate.planned_session_rate` (λp) and the burst count are reported per seed.
  2. **A slow drain read as `stuck`** (review T2): `load.verdict` judges the 1500 s watch with the counter hit rate, which includes burst requests; a finite backlog of cold burst prompts can hold the hit rate down without a sustained cold state. `end_window`'s burst count and k_pass (the span test's spans are burst-free) separate it; the confirmation run settles it.
  3. **Percent-fast binning** by planned time counts never-released turns as misses (REG-11, owner decision 3; review T3): it pushes a burst run toward `stuck`. `end_window` counts them per seed; the verdict's hit-rate and queue conditions are server-side and unaffected; k_pass is the independent check.
  4. **Heat over ≈ 8 h:** `gpu_steady` and `power_limit` per run; `span_clock` per seed.
  5. **Closed loop, dev mode, 350 W, L1 only** (REG-11).
  6. **Single control per seed** (rule H): each control is one run.
- **Stopping rule:** each run once; an invalid run is rerun unchanged, at most twice; **no rerun on any verdict or label** (no `inconclusive` rerun, unlike REG-10 and REG-11); a heat-invalid run once after cooling (standing instruction), a second heat failure stops the queue; a `client_error`, a burst that does not fill the pool, a limit other than 350 W, or an unexpected pre-launch check stops the queue. A rerun decision reads only `checks.json`. **No interim look:** no verdict or label of any seed is computed before all 10 runs are valid; the matrix is not stopped early for any count.
- **Operations:** REG-11's. Seed order 2, 3, 4, 5, 6; in each, the control first, then the burst run. The VM is reached over Tailscale when the owner is off the local network.
- **Cost** (corrected, review): each run is 2580 s of arrivals, up to 300 s of drain (`drain_s`) and about 60 s of start-up: 10 × 2940 s ≈ 8.2 GPU h, plus cooling waits ≈ 8.7 h wall-clock (DERIVED). Worst case with every rerun (3 attempts per run) ≈ 24.5 GPU h.
- **Code and files:** `analysis/gate.py` (`REG12`, `reg12_spec`, `reg12_only`, `end_window`, `reg12_pair`, `reg12_outcome`, `reg12_table`, `python -m analysis.gate reg12`; `reg10_pick`'s docstring); the 10 configs; `tests/test_gate.py` (2 new: counting, k_pass, outcome precedence, the patterns never pick up REG-11's runs or another seed's, the seed check, two valid runs refused; and `reg12_pair` through the real λ, force_close, closed-loop, 350 W and seed checks, with only the verdict stubbed). Gate tests: 36 passed.
- **Not changed:** REG-11's result, settings and runs; no harness change.

### Adversarial review (separate subagent; it saw only the draft, its diff and the code and configs those call; it opened no runs and no docs; a first attempt ended on a network error before reporting and was rerun with the same inputs). Verbatim:

> **Adversarial review of REG-12 (rule F).** Read: the draft, the diff, analysis/gate.py, load.py, stats.py, harness/workload.py, loadgen.py, run.py, checks.py and the config chain. `uv run pytest -q tests/test_gate.py`: 35 passed.
>
> **1. Traces where `reg12_table` gives a wrong count or a wrong `supports`**
>
> *T1: the decision table has overlapping branches (Blocking).* Take seeds 2, 3, 4 at (control `recovered`, burst `stuck`) and seeds 5, 6 with an `unclear` control. Then k = 3, n = 5 and `supports` = True (gate.py:490). The branch "two or more controls not `recovered`" also fires. The draft gives no precedence between them. The same problem hits k = 0: k = 0 with five `unclear` controls is read as "REG-11's pass did not reproduce", but here the matrix measured nothing. `reg12_table` reports neither the count of recovered controls nor a flag for it.
>
> *T2: a slow drain of the burst's own backlog is read as `stuck`.* `verdict` takes the hit rate from server counters over the scrapes in [1980, 2580) (load.py:166–171). It does not leave out burst requests. Suppose about 450 cold 2944-token burst prompts are still queued under FCFS after 900 s. They pull the hit rate down by ≥ 0.06. The queue falls, but more slowly than q/3600 per second, so the drain sign fails (load.py:236). Percent fast stays low. The verdict is `stuck` while the server is working through a finite backlog. The span test would catch this, because its spans are burst-free (gate.py:93). But the gate label is "reported, not counted", so k still counts the seed.
>
> *T3: turns that are never sent count as misses.* Percent fast is binned by `t_planned` (load.py:161), and latency runs from `t_released` (load.py:23). A turn whose release falls after the drain deadline (max t_planned + 300 s, loadgen.py:145) stays `unfinished`, and that counts as a miss. In a run with a large release lag, pf in the end window falls through client-side lag alone. Measuring latency from release then hides how slow the server is for the turns that were sent. A closed-loop run behind schedule therefore drifts toward `stuck` on pf. The `unreleased` readout (gate.py:367) only covers the post-burst spans. It does not cover the verdict's end window.
>
> *T4: a later run silently replaces the registered one.* `reg10_pick` takes the latest valid run by id (gate.py:314–319). Suppose any later rerun, or a later registration, reuses a config name such as `burst_l1pl350cl_r2.4_s2`. REG-12's table then changes after the fact. Its docstring also allows a rerun after an `inconclusive` pair. That conflicts with this draft's rule that a rerun reads only `checks.json`. A rerun chosen by its verdict would bias k.
>
> *T5: the two runs are judged on different baselines.* The burst run's baseline is [300, 900). The control's is [480, 1080), because `t_start` = `control_t_s` (load.py:213). Both end at [1980, 2580). This is minor, but the control's baseline covers a different 180 s of the seed's schedule.
>
> The seed and λ checks are sound. The globs end at `_s<s>`, so they cannot match `s1` or `s26` (test lines 352–356). The fixed `--seed: 0` server flag (base.yaml:19) means seeds vary only the workload. I found no trace that picks a run from the wrong seed.
>
> **2. Strongest alternative explanations**
> - **For `supports`:** the stuck state is a backlog of cold prompts and released turns that clears after the 1500 s watch, not a self-sustaining eviction state. T2 and T3 both push the verdict toward `stuck`. Evidence that separates them, per seed:
>   - burst requests with a first token in [1980, 2580);
>   - unreleased later turns planned in [1980, 2580);
>   - the gate label (`pass` vs `stuck_unconfirmed`/`inconclusive`);
>   - `turn0_share`.
>
>   The 4500 s confirmation run is the final test.
> - **For k = 0:** seed 1's stuck state came from its schedule (a high λp near the burst), not from the cell. Separate it with λp per seed and `shock_size` against seed 1. A further alternative: closed-loop self-throttling, which makes stuck hard to reach at λ = 2.4. Under the draft's own p ≈ 0.65, P(k = 0) = 0.35⁵ ≈ 0.005 (DERIVED), so k = 0 would weigh strongly against the belief.
>
> **3. Decisions, prediction and cost**
> - **Can it change a decision?** Yes. `supports` leads to the C1 confirmation and C2 drafts. k = 1–2 and k = 0 go to the owner. Apart from T1, the branches are coherent.
> - **The prediction is ambiguous.** "Per-seed stuck p ≈ 0.65" does not say whether that is P(burst `stuck`) or P(burst `stuck` and control `recovered`). Under the second reading the arithmetic holds: 0.336 + 0.312 + 0.116 = 0.765. Under the first, with the stated P(control recovered) ≈ 0.9, p = 0.585 and P(k ≥ 3) ≈ 0.345 + 0.243 + 0.069 = 0.66 (DERIVED).
> - **The Clopper–Pearson intervals check out** with `stats.cp_upper`.
> - **Cost is understated.** Each run can use the full `drain_s` (300 s, base.yaml) after 2580 s. That gives 10 × (2580 + 300 + 60) s ≈ 8.2 GPU h, not 7.3. The four-seed figure (6.4 h) scales the 8 h total including cooling, not the GPU hours (8 × 2640 s ≈ 5.9 GPU h).
> - **One outcome is missing from the table.** A burst that does not fill the pool stops the queue (checks.py:178–184). `reg12_table` then raises (no valid run), and the draft does not say what is reported.
>
> **4. Recommendations**
> 1. **(Blocking)** Make the decision branches mutually exclusive. Evaluate "≥ 2 controls not `recovered`" first, and have `reg12_table` return `n_control_recovered` and an `outcome` field. Define k = 0 only when at least 4 controls are `recovered`.
> 2. **(Blocking)** Before any run, say whether a `stuck` seed with a gate label other than `pass` counts in k. If it does, pre-register a second count, k_pass, reported beside k. If it does not, change the code. Leaving it to the reader after the data is in breaks rule A5.
> 3. **(Blocking)** Pin the run ids. Either `reg12_table` refuses a seed with more than one valid run unless the run id is listed in an append-only REG12 entry, or the stopping rule and the `reg10_pick` docstring say plainly that no rerun is made on a verdict or label.
> 4. Add per-seed readouts for the end window [1980, 2580): burst requests with a first token there, unreleased and unfinished later turns, and the queue slope against `drain_horizon_s`. These separate T2 and T3 from a real stuck state.
> 5. State p's definition and correct the GPU-hour figures, including the four-seed alternative.
> 6. Note the different baseline windows of control and burst run (T5) as a known asymmetry.
> 7. Add the "burst does not fill the pool, or the queue stops" outcome to the decision table.
> 8. Add a test that runs the real `gate_verdict` on fake runs, without mocking `reg10_gate`. The current test (test_gate.py:362–365) mocks out every check that matters (control_t_s, power limit, closed loop).

**Changed because of it:** all eight recommendations. 1: `reg12_outcome` with `controls_not_healthy` first, `n_control_recovered` and `outcome` returned, `none` only with ≥ 4 recovered controls. 2: k decides `supports`; `k_pass` is fixed now and decides what follows it. 3: `reg12_only` refuses a second valid run per pattern; no rerun on a verdict or label; `reg10_pick`'s docstring says so. 4: `gate.end_window`, with REG-11's values for reference. 5: p defined; cost 8.2 GPU h. 6: the baseline asymmetry stated. 7: the queue-stop outcome added. 8: `test_reg12_pair_runs_the_real_checks` (λ, force_close, closed loop, 350 W, seed; only the verdict stubbed, not `gate_verdict` on fake runs, which needs full run folders). The four-seed point is moot: the owner chose five seeds. The review's line numbers refer to the first draft.

## 2026-11-09 · [DECISION] Owner approves REG-12 and its runs
- **Owner's answer:** "ok, approve REG-12, run it", to the question whether REG-12 (decisions.md 2026-11-09 [REG]) is approved: the C1 matrix of REG-11's cell, seeds 2–6 (the owner's choice, "go with 5 seeds"), each with a same-seed control, ≈ 8.2 GPU h.
- **Order:** seeds 2, 3, 4, 5, 6; in each, `configs/stage2_control_l1pl350cl_r2.4_s<s>.yaml`, then `configs/burst_l1pl350cl_r2.4_s<s>.yaml`. Each launch after REG-11's pre-launch checks, run by an agent queue script that stops at the first run that is not valid or any pre-launch STOP; the agent then applies the stopping rule (reading only `checks.json`).
- **Standing instructions** (decisions.md 2026-11-09 [DECISION]) apply. No verdict or label of any seed is computed before all 10 runs are valid and copied; then `gate.reg12_table` once, the `[RESULT]`, and the next drafts by the registered outcome, which do not run before the owner approves them.

## 2026-11-09 · [OPS] REG-12 runs: 10 of 10 valid after one rerun (seed 6 control, `accounting`); pre-launch reads in `docs/probe/20261109_reg12/`
- **Launched** by the agent's queue script, in the registered order, each after REG-11's pre-launch checks (350 W limit, clean tree at `32ae2f9` on the VM and the Mac, no compute process, GPU ≤ 45 °C; PROBE(docs/probe/20261109_reg12/prelaunch_reg12_<config>.txt)). The VM was reached over Tailscale (owner off the local network). The Mac slept on battery about 06:43–08:01 UTC, which delayed the seed-2 burst launch; from then on `caffeinate` held it awake on mains power.
- **Runs and checks** (FILE(runs/<id>/checks.json) each; all at 350 W in every sample, 0 HW-throttle samples, SW thermal ≤ 0.003, max 67–78 °C, `client_lag` p99 ≤ 2.6 ms, `release_chain` 0 unexplained):

  | seed | control | burst | burst KV max during burst | burst requests unfinished |
  |---|---|---|---|---|
  | 2 | `20261109-055910_stage2_control_l1pl350cl_r2.4_s2` | `20261109-080203_burst_l1pl350cl_r2.4_s2` | 0.9997 | 764 of 6462 |
  | 3 | `20261109-085121_stage2_control_l1pl350cl_r2.4_s3` | `20261109-093609_burst_l1pl350cl_r2.4_s3` | 0.9995 | 673 of 6206 |
  | 4 | `20261109-102614_stage2_control_l1pl350cl_r2.4_s4` | `20261109-111316_burst_l1pl350cl_r2.4_s4` | 0.9975 | 1411 of 7022 |
  | 5 | `20261109-120308_stage2_control_l1pl350cl_r2.4_s5` | `20261109-125300_burst_l1pl350cl_r2.4_s5` | 0.9997 | 1049 of 6806 |
  | 6 | `20261109-142813_stage2_control_l1pl350cl_r2.4_s6` (rerun) | `20261109-151300_burst_l1pl350cl_r2.4_s6` | 0.9998 | 1024 of 6609 |

  Every burst filled the pool (`manipulation` ≥ 0.95). The seed-5 control ended with 296 of 6356 requests unfinished and 193 later turns never released (FILE(runs/20261109-120308_stage2_control_l1pl350cl_r2.4_s5/checks.json)); every other control finished all its requests.
- **One invalid run: `20261109-134250_stage2_control_l1pl350cl_r2.4_s6`**, failed `accounting` only (FILE(runs/20261109-134250_stage2_control_l1pl350cl_r2.4_s6/checks.json)): 6173 of 6173 requests ok, but the vLLM success counter rose by 426. Not heat, not a client error, not a queue-stop condition, so by the stopping rule (read from `checks.json` only) it was **rerun unchanged once**; the rerun is valid. Kept and marked invalid; copied with identical sha256.
  - **Cause, observed:** the recorder stopped writing `gpu.jsonl` and `metrics.jsonl` at t = 213 s (FILE(runs/20261109-134250_stage2_control_l1pl350cl_r2.4_s6/gpu.jsonl), last line) while the load ran to t = 2612 s (`events.jsonl` `load_end`). No error line in `metrics.jsonl`, so the recorder process exited outside its scrape `try`. **Suspected, BELIEF:** `LagTail.recent_max` (harness/recorder.py) `json.loads` a half-written line of `requests.jsonl` while loadgen appends to it, and the exception is not caught. Its traceback, if any, went to the VM console log, which the rerun overwrote ([CORR] below). Added to open-questions.
  - **Two checks passed on the broken run** and so would not have caught it alone: `gpu_steady` (0 busy samples, max temp null) and `recorder` (max gap 1.0 s, which looks only at gaps inside the recorded data, not at its end). `accounting` caught it. A fix to the recorder and to both checks needs the owner (checks: rule C); proposed after REG-12, not made during it (it would change the commit mid-matrix).
- **Copied** to the Mac with identical sha256 (10 files per run); manifest +110 lines; none listed in `manifests/pending_copy.txt`. The VM copies are kept.
- **Stray file:** the first queue start (a seed-list bug in the agent's script, no GPU use) left a 128-byte log `~/stage2_control_l1pl350cl_r2.4_s2` in the VM home; harmless, left in place (deleting needs the owner).

## 2026-11-09 · [CORR] The rerun's console log overwrote the invalid run's on the VM
- **Error:** the agent's launch script writes the console log to `~/<config>.log` on the VM. The rerun of the seed-6 control used the same config name, so it overwrote the log of `20261109-134250_stage2_control_l1pl350cl_r2.4_s6`, the only place a recorder traceback would have been. The agent saved the pre-launch probe of the first attempt (`prelaunch_reg12_stage2_control_l1pl350cl_r2.4_s6_attempt1.txt`) but not the console log.
- **Effect:** the recorder failure's cause stays a BELIEF. The run folder (raw data) is intact. No result changes.
- **Fix:** later launches name the console log by run attempt (agent script; no harness change).

## 2026-11-09 · [RESULT] REG-12: `controls_not_healthy`. Stuck with a recovered control in 2 of 5 seeds; three controls did not recover without any burst, one (seed 5) collapsing into the same cold, full, backlogged state
- **Computed once:** `uv run python -m analysis.gate reg12` (`gate.reg12_table`) on the ten valid runs above (each RUN(<id>, gate.reg12_table)).

  | seed | control verdict | burst verdict | gate label | stuck (C1 test) | stuck and `pass` | λp after t = 1080 s (control) |
  |---|---|---|---|---|---|---|
  | 2 | recovered | stuck | pass | yes | yes | 2.339 |
  | 3 | recovered | stuck | pass | yes | yes | 2.222 |
  | 4 | **stuck** | stuck | control_not_healthy | no | no | 2.711 |
  | 5 | **stuck** | bad_baseline | inconclusive | no | no | 2.400 |
  | 6 | **unclear** | stuck | inconclusive | no | no | 2.419 |

  **k = 2 of n = 5**, one-sided 95 % Clopper–Pearson upper bound **0.811**, lower bound 0.076 (DERIVED: 1 − cp_upper(3, 5)); k_pass = 2; **`n_control_recovered` = 2**; **outcome `controls_not_healthy`** (checked first, as registered); `supports` false. λp column: RUN(<control id>, gate.planned_session_rate) over [1080, 2580) s.
- **The controls** (RUN(<id>, load.verdict); baseline [480, 1080) s, end window [1980, 2580) s; thresholds configs/stage2_base.yaml:15–20):
  - seed 2: pf 0.999 → 1.000, hit 0.828 → 0.835, q 0.005 → 0.002: recovered.
  - seed 3: pf 1.000 → 1.000, hit 0.832 → 0.835, q 0.000 → 0.002: recovered.
  - **seed 4:** pf 1.000 → 0.741, hit 0.829 → 0.653, q 0.008 → 1.29, KV 0.23 → 0.48: `stuck` by the thresholds, but **partly degraded, not the cold state** (hits 0.65, KV half full, a short queue).
  - **seed 5:** pf 0.999 → **0.000**, hit 0.818 → **0.000**, q 0.012 → **100.2** (slope +0.12/s), KV 0.24 → **0.95**, running 7.6 → 30.5: **the same cold, full, backlogged state the burst runs reach, with no burst.**
  - **seed 6:** pf 1.000 → 0.978, hit 0.828 → 0.747, q 0.003 → 0.033: not recovered (pf drop 0.022 > 0.02, hit drop 0.081 > 0.06), not stuck: `unclear`; mildly degraded.
- **The burst runs:** four of five `stuck` (2, 3, 4, 6); seed 5's is `bad_baseline` (baseline pf 0.970 < 0.98, RUN(20261109-125300_burst_l1pl350cl_r2.4_s5, load.verdict)) and ends at pf 0, hit 0, q 261. In all five, every span after the burst is cold (hit share 0.000), full (KV 0.95) and backlogged, with c 1.70–1.84 req/s (RUN(<burst id>, gate.reg12_table) `details.spans`); `secondary_cb` `not_sustainable` in all five (c_b 1.79–1.83). `end_window`: 0 burst requests with a first token in [1980, 2580) s in every seed; queue 204–282, slope +0.06 to +0.20 per s.
- **Prediction** (model.md row 16): runs valid: 10 of 11 attempts (p ≈ 0.9 each: fits). Bursts fill the pool: 5 of 5 (fits). Each control `recovered` p ≈ 0.9: **2 of 5, a miss**; P(≤ 2 of 5 | p = 0.9) = 0.0086 (DERIVED: 1 − 0.9⁵ − 5·0.9⁴·0.1 − 10·0.9³·0.1² = 1 − 0.59049 − 0.32805 − 0.0729). k ≥ 3 ≈ 0.77: did not happen. P(burst `stuck`) ≈ 0.72: 4 of 5 (fits).
- **What it shows, and what it does not:**
  - **Observed:** at λ = 2.4 with closed-loop turns, the cold, full, backlogged state is reached **without the trigger** in one of five controls (seed 5), and two more controls degrade partway (seeds 4, 6). After the burst it is reached in all five seeds (four `stuck`, seed 5 already degrading).
  - **Derived:** the registered reading applies: **λ = 2.4 is not reliably warm-healthy with closed-loop turns; the matrix cannot speak to C1**, whatever k is. The burst is not shown to be the cause of the stuck state in this cell: the load alone reaches it within 2580 s in at least one seed.
  - **Two readings of seed 5's control, not separated here:**
    1. **Plain overload:** λ = 2.4 (λp 2.40 in the watch) is at or above the closed-loop warm capacity, so the queue grows by itself. Then there is no healthy state at this load to be metastable against.
    2. **A self-triggered metastable transition:** the warm state held for ≥ 1080 s (baseline pf 0.999, hit 0.818), and a load fluctuation tipped it into the cold state, which then held. That is a metastable failure with the load's own variance as the trigger, but C1 as written needs a recovered control, so it cannot be claimed from this matrix.
    - **Evidence that separates them:** the closed-loop warm capacity (a cache-on sweep with closed-loop turns: if μ_warm,cl is well above 2.4 and the state still forms and holds, reading 2 gains); how long the warm state lasts at loads below 2.4 (a fluctuation-triggered transition becomes rare quickly as λ falls; plain overload does not occur below capacity); and in seed 5's control, when the collapse began and whether the λp of the minutes before it was high (`gate.planned_session_rate` on windows; descriptive, needs a function for the onset).
  - **Not shown:** whether C1 holds at a lower λ; whether the two `stuck`-with-recovered-control seeds (2, 3) differ from the others only by lighter load (their λp 2.22–2.34 are the two lowest; the controls that failed have 2.40–2.71). This pattern fits alternative 1 of REG-12 (seed-dependent load) and reading 1 above, from five points, unregistered: BELIEF.
- **Alternatives** (rule A2):
  1. **The recorder or harness failed in the controls:** all five controls are valid; seed 5's degraded state is in the server's own metrics (hit counter 0, `num_requests_waiting` 100, KV 0.95), not only the client's.
  2. **Heat:** SW thermal ≤ 0.003 in every run, 350 W in every sample; the clock is not the cause of a 0.000 hit rate.
  3. **Closed-loop artifact:** in closed loop, released turns follow completions, so a slow server sees fewer turns; that protects it. A collapse despite that is not a client artifact. `release_chain` explains every unsent turn.
  4. **The verdict thresholds:** seeds 4 and 6 sit near them (seed 6 misses `recovered` by 0.002 in pf drop); seed 5 does not (pf 0, hit 0). With seed 6 counted `recovered`, `n_control_recovered` = 3 and the outcome would still be `controls_not_healthy` (2 not recovered); the thresholds are not changed after the fact (rule A5).
- **Decision (registered):** `controls_not_healthy` → **the owner decides**; the registration names a closed-loop cache-on sweep to measure μ_warm first. The agent's recommendation and the options go to the owner; nothing is drafted as a [REG] before the owner picks a direction (the registered branch overrides the standing instruction to draft the next REG). C1's status does not change; REG-11's `pass` stays as an exploratory one-seed result, now with the caveat that its control's health is seed-dependent at this load.

## 2026-11-09 · [REG] REG-13 (draft): μ_warm of L1 at 350 W with closed-loop turns, to separate overload from a cold state that outlasts its load (GPU, ≈ 1.8 h)
- **ID:** REG-13. **Confirmatory** for the question below; exploratory otherwise. **Not approved:** no GPU run before the owner approves this entry.
- **Why:** REG-12 ended `controls_not_healthy` (decisions.md 2026-11-09 [RESULT]); its registered decision: the owner decides, "a closed-loop cache-on sweep to measure μ_warm first". The owner asked for this draft on 2026-11-09 ("ok, draft the closed-loop sweep REG"). REG-12 left two readings apart: **overload** (λ = 2.4 is at or above the warm capacity with closed-loop turns) and **a metastable cold state** (the warm server carries the load; once cold, it stays cold). μ_warm = 3.0 was measured open-loop only (REG-8).
- **Question:** what load does the warm server carry with closed-loop turns, and is it at or above the planned load each cold run of REG-11/12 faced after its trigger?
- **Design inputs** (computed before this entry from existing runs; `uv run python -m analysis.gate reg13_inputs`, `gate.post_trigger_rate`; **fixed in `REG13["cold_runs"]`**, and `reg13_table` refuses to run if a recomputed value differs). The seven runs whose end window [1980, 2580) s was cold and backlogged, with the planned session rate λp from the trigger's end to the end of arrivals:

  | run | trigger end (s) | λp after it |
  |---|---|---|
  | `20261109-042828_burst_l1pl350cl_r2.4_s1` (REG-11) | 1080 | 2.359 |
  | `20261109-080203_burst_l1pl350cl_r2.4_s2` | 1080 | 2.339 |
  | `20261109-093609_burst_l1pl350cl_r2.4_s3` | 1080 | 2.222 |
  | `20261109-111316_burst_l1pl350cl_r2.4_s4` | 1080 | **2.711** |
  | `20261109-125300_burst_l1pl350cl_r2.4_s5` (`bad_baseline`; end window hit 0, queue 261) | 1080 | 2.400 |
  | `20261109-151300_burst_l1pl350cl_r2.4_s6` | 1080 | 2.419 |
  | `20261109-120308_stage2_control_l1pl350cl_r2.4_s5` (no trigger: first backlogged stretch, REG-6 settings) | 1330 | 2.287 |

  Not included: seed 4's control (backlogged only from 2467 s, end hit 0.65) and seed 6's (no backlog). **λp,max = 2.711** (seed 4's burst run) decides between `below` and `partial` on its own (review T5).
  - **Exploratory, found by looking, no decision rests on it** (RUN(20261109-120308_stage2_control_l1pl350cl_r2.4_s5, gate.planned_session_rate), 120 s windows): seed 5's control had λp 3.39 in [1200, 1320) s, just before its backlog began, and 1.62–3.02 per window afterwards, while it stayed cold. Seed 2's control survived a 3.08 window and seed 6's a 3.22 window.
  - In the cold runs the completion rate was 1.70–1.84 req/s per span and c_b 1.79–1.83 (decisions.md 2026-11-09 [RESULT] REG-12, RUN(<burst id>, gate.reg12_table)), well below any μ_warm,cl ≥ 2.4. Near-critical queueing without a cache loss would complete near the warm rate (review alternative for `below`).
- **Setup:** `configs/sweep_l1pl350cl_pc_on.yaml` = REG-8's G1′ sweep (`sweep_l1pl350_pc_on.yaml`: L1, 350 W check, seed 0, 900 s per rate with 240 s warm-up, no dev mode) with `workload.sessions.closed_loop: true` and `loadgen_force_close: true` (as REG-11/12; connect cost median 0.55 ms, REG-9). **Rates 2, 2.4, 2.6, 2.8, 3**, one harness invocation, ascending. Resolved with `load_config`, `with_defaults`, `harness.run.expand` (checked).
  - At λ = 2 and 3 the planned schedules equal REG-8's `20261107-103010_sweep_l1pl350_pc_on_r2` and `20261107-104614_sweep_l1pl350_pc_on_r3` (1802 and 2673 rows, `build_schedule` against their `schedule.parquet`; test): a paired open/closed comparison, which also differs in force_close.
  - Seed 0's schedule in the measured window [240, 900) s (DERIVED, `build_schedule`): realized planned rate 2.097, 2.529, 2.758, 2.968, 3.124; highest 120 s window 2.21, 3.04, 3.33, 3.61, 3.55, at λ = 2, 2.4, 2.6, 2.8, 3.
- **Result, computed once after every rate has a valid run or the stopping rule ends:** `uv run python -m analysis.gate reg13` (`gate.reg13_table`). Only valid runs of the sweep parent with closed loop, force_close and 350 W are read (`gate.reg13_check`).
  - **Pass test per rate** (closed loop, review T3): throughput ≥ 0.95 × planned rate (the configs' rule) **and** the server queue slope plus `due_unreleased_slope` (slope of later turns already due by plan and not yet released) ≤ 0.01 req/s. On a healthy REG-12 control over [240, 900) s the second slope is −0.013 (RUN(20261109-055910_stage2_control_l1pl350cl_r2.4_s2, gate.due_unreleased_slope); a check of the function, not a threshold choice).
  - **μ_warm,cl:** the highest registered rate whose run and every lower rate pass (`load.capacity`, monotone, over the registered rates; a rate with no valid run ends the chain). **`carried`:** the realized planned rate of the run at μ_warm,cl (review T2).
  - **`collapsed`** (per failing rate, review T1): its first backlogged stretch after warm-up (REG-6 settings) starts ≥ 300 s after warm-up; before it, ok completions ≥ 0.95 × planned session requests; after it, the counter hit rate is ≥ 0.06 lower (`stuck_hit_drop`).
  - **`outcome`** (`gate.reg13_outcome`, in this order): `incomplete` (the chain reaches a registered rate with no valid run); **`below`** (`carried` ≥ 2.711: every cold state persisted at a planned load the warm server carried); **`collapsed`** (the first failing rate carried its load for ≥ 300 s, then went cold); **`overload`** (μ_warm,cl undefined or < 2.4); `partial` (otherwise: 2.4 carried, not 2.711). `n_cold_below`: cold runs with λp ≤ `carried`.
  - **Readouts, never decisive:** per rate pooled percent fast at TTFT ≤ 1.0 s (valid runs only), KV, unfinished, `release_delay`, `surge_max`, `collapsed` details; μ by the configs' rule alone (`tables.sweep_capacity`); REG-8's paired rows; λ_test by REG-7's rule with μ_sat,off 1.681.
- **Prediction** (BELIEF; revised after the review, which showed seed 0's own surges reach 3.04–3.61 in the window): 2.4 passes p ≈ 0.8 (its highest window, 3.04, is below what seeds 2 and 6 survived); 2.6 passes p ≈ 0.5 (3.33, near seed 5's 3.39); 2.8 p ≈ 0.3. A failure at 2.4–2.8 is a collapse p ≈ 0.6. So P(`below`) ≈ 0.38, `collapsed` ≈ 0.32, `partial` ≈ 0.15, `overload` ≈ 0.1, `incomplete` ≈ 0.05. Paired runs: throughput within 3 % of REG-8's at λ = 2 (p ≈ 0.85); at λ = 3 the closed-loop run fails (p ≈ 0.6). Each run valid p ≈ 0.9.
- **Decision under each outcome:**
  - **`below`:** the cold states held at loads the warm server carries over 660 s: not plain overload (one seed; exploratory for C1). Draft for the owner, in order: (1) C1's confirmation at REG-11's cell (a burst run with a 4500 s watch, then the drop to λ = 1; C1 conditions 5–6), which tests the hysteresis directly; (2) a note that C1's matrix test as written (the no-trigger control must recover) cannot pass in this cell when the load's own surges trigger the same state: whether to reword C1 is the owner's (a paper claim).
  - **`collapsed`:** the sweep found a warm state that carried its load and then went cold within 660 s: the same transition as REG-12's seed-5 control, at a known load. μ_warm,cl above it is not measurable this way. Draft the same confirmation run as under `below`; the owner decides whether the transition itself (its rate vs λ) is the next measurement.
  - **`partial`:** report `n_cold_below` of 7. The owner chooses between the confirmation run and a lower-λ cell.
  - **`overload`:** λ = 2.4 is beyond the closed-loop warm capacity; REG-12's control failures and the cold states of REG-11/12 are explained by overload. A [RESULT] note that REG-11's `pass` is not evidence of a metastable state (claims.md only after the owner reviews it). The owner picks another factor or cell.
  - **`incomplete`:** reported from `checks.json`; the owner decides.
- **Alternatives:**
  1. **One seed, 660 s per rate:** capacity under seed 0's schedule in its window. `collapsed` separates a transition from steady overload; `surge_max` and `release_delay` per rate are reported.
  2. **Warm for 660 s is not stable for 1500 s:** `below` says the cold state was not forced by the average load; it does not say the warm state lasts at that load (REG-12's controls at 2.4 did not in 3 of 5 seeds).
  3. **Near-critical queueing** (review): at ρ ≈ 0.97, long backlogs occur without any cache mechanism, and a cold cache can follow a long queue rather than cause it. The cold runs completed at 1.70–1.84 req/s, far below a warm rate ≥ 2.4; queueing alone predicts completion near the warm rate. The hysteresis test (drop to λ = 1) separates the rest.
  4. **The 5 % tolerance:** "carried" means throughput ≥ 0.95 × planned; `carried` uses the realized planned rate.
  5. **Dev mode** (off here, on in REG-11/12; it only registers endpoints, open-questions S1; BELIEF that it does not change capacity) and **force_close** in the paired comparison.
  6. **Heat:** `gpu_steady`, `power_limit` per run; REG-8's G1′ at 350 W ran at 64–69 °C.
  7. **Recorder failure** (open-questions A14): not fixed; `accounting` catches it, as in REG-12.
- **Stopping rule:** one harness invocation; an invalid rate is rerun unchanged with a rerun config listing that rate only (same `name`), at most twice; a heat-invalid run once after cooling to ≤ 45 °C, a second heat failure stops; a `client_error`, a limit other than 350 W or an unexpected pre-launch check stops. A rerun decision reads only `checks.json`. **No interim look** at any rate's throughput, slope or μ before all rates are valid or the rule ends.
- **Operations:** REG-12's pre-launch checks (350 W, clean tree at this entry's commit on the VM and the Mac, no compute process, GPU ≤ 45 °C). The console log is named per attempt ([CORR] 2026-11-09).
- **Cost:** 5 × (900 s + up to 300 s drain + ≈ 60 s start-up) ≈ 1.75 GPU h (DERIVED: 6300 s); worst case with every rerun ≈ 5.3 GPU h.
- **Code and files:** `configs/sweep_l1pl350cl_pc_on.yaml`; `analysis/gate.py` (`REG13`, `post_trigger_rate`, `surge_max`, `due_unreleased_slope`, `collapsed`, `reg13_check`, `reg13_outcome`, `reg13_table`, `reg13_inputs`; CLI `reg13`, `reg13_inputs`); `tests/test_gate.py` (7 new). Gate tests 43 passed; full suite 220 passed before the review's changes, gate tests after.
- **Not changed:** REG-12's result and runs; the configs' capacity rule (REG-13's pass test adds a closed-loop condition for this sweep only; `sweep_capacity` is reported beside it); no harness or check change.

### Adversarial review (separate subagent; it saw only the first draft, its diff and the code and configs those call; it opened no runs and no docs). Verbatim:

> **Rule F review of REG-13 (draft).** I read the draft, the diff, analysis/gate.py, load.py and tables.py, harness/loadgen.py, workload.py, run.py and checks.py, and the configs in the extends chain. I did not open runs/ or docs/. `pytest -k reg13`: 5 passed. Schedule numbers below come from `build_schedule` on the resolved configs (DERIVED, seed 0, measured window [240, 900) s).
>
> **1. Traces where the result is wrong or misleading**
>
> T1. **A collapse inside the sweep is read as `overload`** (gate.py `reg13_outcome`; tables.py:106 `sweep_capacity`). Seed 0's schedule has 120 s surges well above the open-loop μ_warm. Peak planned rate per 120 s window: 3.04 at λ = 2.4, 3.33 at 2.6, 3.61 at 2.8 (DERIVED). The draft treats seed 5's 3.39 surge as a possible trigger. Trace: the 2.4 run carries its load until a surge near 600 s, then turns cold and backlogged. Throughput falls below 0.95 × planned, so the chain ends at 2.0, μ = 2.0 and the outcome is `overload`. The registered decision under `overload` then calls REG-11's `pass` "not evidence" and stops closed-loop work at L1. But that trace is the metastable mechanism itself. The rule has no class for "carried, then collapsed".
>
> T2. **Nominal μ is compared with realized λp** (`reg13_outcome(mu, …, post_max)`). μ is a grid value. The capacity rule judges each run against its realized planned rate (`l1_base.yaml` `against: planned_rate`). Seed 0 runs high: realized 2.097, 2.529, 2.758, 2.968 and 3.124 at nominal 2, 2.4, 2.6, 2.8 and 3. A pass at nominal 2.6 means the server carried 2.758, which is above λp,max = 2.711. Yet the outcome would be `partial`, and `n_cold_below` (nominal) undercounts. The basis of the comparison has to be registered: nominal, realized planned rate, or delivered throughput.
>
> T3. **The queue-slope criterion is weaker under closed loop** (load.py:107 `summarize`; loadgen.py `session_chain`). With 8 turns and 5 s gaps, part of a deficit piles up as client release lag, not as `num_requests_waiting`. Rough estimate (DERIVED, BELIEF-level): mean lag ≈ 4 × e2e, so client-side growth ≈ 4 × dQ/dt. A slope of 0.01 req/s² then admits a deficit of about 0.05 req/s instead of 0.01. With the 5 % throughput tolerance, a nominal 2.8 run passes while delivering about 2.82 req/s against its realized 2.968. The rule leans towards a higher μ and so towards `below`. Nothing measures client backlog: `release_delay` is a median over the whole window, not a slope.
>
> T4. **λp,max is not actually fixed.** `reg13_table` recomputes `post_max` from runs/ and the current `backlogged_stretches`/REG7 settings at analysis time. It is not the registered 2.711. Any later change to those settings moves the threshold.
>
> T5. **Seed 4's burst decides between `below` and `partial` on its own.** It is the only λp above 2.42. Including seed 5's control rests on its first backlog start (1330 s), which was found by looking at the data. If λp were defined from the first cold window instead, the threshold would change.
>
> T6. **Smaller code issues:**
> - `sweep_rows` (gate.py:188) does not filter on validity. The readout `lam_test_reg7_rule`/`slo_feasible` can therefore use an invalid run's pf.
> - `on[on.run == name].iloc[0]` raises IndexError for a valid run with empty metrics.
> - `chain_end`/`complete` agree with `sweep_capacity`'s union-of-swept-rates rule, including after a stop mid-sweep (chain reaches 2.8, which has no run → `incomplete`). That part is correct.
>
> Mechanics I checked, all fine:
> - `expand` sets parent and rates.
> - The `arrival_rate` check counts turn 0 only under closed loop. Seed 0's turn-0 counts are 175, 212, 231, 249, 264 against expected 165–247.5, all inside tolerance.
> - `burst_requests(None)` returns 0.
> - `release_chain` needs no trigger.
> - Against the REG-11 burst config, only duration, dev mode, SLO/verdict and trigger keys differ. Turns and gaps are the same.
>
> **2. Strongest alternatives**
>
> - **`overload`:** a metastable collapse inside the sweep (T1), or a capacity cut from force_close or no-dev-mode that is specific to the sweep. What separates them is each run's time course. Overload shows a queue rising from the start at warm hit rate. A collapse shows a warm stretch (throughput ≈ planned, warm hit rate), then a surge, then a hit-rate drop and backlog.
> - **`below`:** near-critical heavy traffic. At ρ ≈ 2.711 / ~2.8 ≈ 0.97, long backlog excursions happen with no cache mechanism, and a cold cache can be a result of the long queue rather than its cause. What separates them: in each cold run's stuck windows, is the completion rate well below μ_warm,cl, with the hit drop *preceding* the queue rise? Then the hysteresis test (drop to λ = 1). `below` alone cannot tell these apart.
>
> **3. Decisions, prediction, cost**
>
> - The outcomes do lead to different owner choices, so the run can change a decision.
> - **The prediction does not fit the study's own data.** REG-12's controls at 2.4 went cold without a burst in 3 of 5 seeds, and seed 0 has bigger surges at 2.6 and 2.8. P(`below`) ≈ 0.65 needs three 660 s windows in a row with no collapse, and the draft gives no argument for that.
> - Cost: 5 × 1260 s ≈ 1.75 h is right as an upper bound per run.
> - **Missing from the decision table:**
>   - a `collapsed` outcome (T1);
>   - what `below` means when the confirmation burst run cannot be told apart from a self-triggered collapse (REG-12 seed 5);
>   - a `partial` case judged on realized load (T2).
>
> **4. Recommendations**
>
> 1. **Blocking.** Register a `collapsed` class, with a criterion fixed before any run, for a failing rate that carried its load before failing. For example: an initial stretch of ≥ X s with throughput ≥ 0.95 × planned and warm hit rate, followed by a backlogged stretch with a hit drop ≥ `stuck_hit_drop`. Map `collapsed` to its own decision, not to `overload`.
> 2. **Blocking.** Register the basis of comparison (realized planned rate or throughput of the highest chain-passing run vs λp). Fix `n_cold_below` to match.
> 3. **Blocking.** Hard-code λp,max = 2.711 and the seven λp values in `REG13`, and assert that the recomputed values equal them.
> 4. **Blocking.** Add a client-backlog criterion for closed loop to the capacity rule, or at least register it as a decisive co-condition. For example: the slope of turns due but not sent, or of the release delay, over the window ≤ a set limit. Without it the rule leans towards `below` (T3).
> 5. Not blocking. Before spending GPU time, apply the capacity rule over [240, 900) to the 11 existing closed-loop runs at 2.4 (REG-11/12 bursts before the trigger, and the controls). This gives 2.4 with 11 seeds at no cost. Register the rule before computing it.
> 6. Not blocking. For each cold run, report the completion rate in its stuck windows next to μ_warm,cl, and whether the hit drop came before the queue rise or after it.
> 7. Not blocking. Revise P(`below`) in light of REG-12's collapse rate, or argue why a 660 s window avoids it.
> 8. Not blocking. Filter `sweep_rows` on validity, and handle a valid run with empty metrics.

**Changed because of it:**
- **1–4 (Blocking): all adopted.**
  - 1: `collapsed` (300 s warm and carried, then a hit drop ≥ 0.06), with its own outcome and decision. The order puts `below` first: a rate that carried ≥ 2.711 is the stronger statement even if a higher rate then collapsed.
  - 2: `carried`, the realized planned rate of the run at μ_warm,cl; `n_cold_below` uses it.
  - 3: the seven λp values and λp,max are in `REG13`; `reg13_table` raises if a recomputed value differs.
  - 4: `due_unreleased_slope`, added to the server queue slope under the configs' 0.01 limit; decisive.
- **6: partly.** The cold runs' completion rates (1.70–1.84) are cited above, against alternative 3. Whether the hit drop came before the queue rise is not implemented; it is left for the confirmation run.
- **7, 8: adopted.** 7: the prediction is revised. 8: valid runs only; a valid run with no metrics raises.
- **5: not adopted.** It measures 2.4 only, where 11 healthy baselines are already known from REG-11/12's verdicts. No outcome turns on 2.4 alone except `overload`, and the sweep's own 2.4 run covers that.

## 2026-11-10 · [DECISION] Owner approves REG-13 and its runs
- **Owner's answer:** "ok, approve REG-13, run it", to the question whether REG-13 (decisions.md 2026-11-09 [REG]) is approved: the closed-loop cache-on sweep at L1, 350 W, seed 0, rates 2, 2.4, 2.6, 2.8, 3, ≈ 1.8 GPU h.
- **Run:** one harness invocation, `configs/sweep_l1pl350cl_pc_on.yaml`, after REG-12's pre-launch checks (350 W read, the VM tree clean at the Mac's `main`, no compute process, GPU ≤ 45 °C), reads saved in `docs/probe/20261110_reg13/`. The VM console log is named per attempt (`~/<config>_<UTC time>.log`), after the [CORR] of 2026-11-09.
- **Standing instructions** (decisions.md 2026-11-09 [DECISION]) and REG-13's stopping rule apply; a rerun decision reads only `checks.json`. No rate's throughput, queue slope or μ is looked at before every rate has a valid run or the rule ends; then `gate.reg13_table` once, the `[RESULT]`, and the next drafts by the registered outcome, which do not run before the owner approves them.

## 2026-11-10 · [OPS] REG-13 runs: 5 of 5 valid in one invocation, no rerun; pre-launch read in `docs/probe/20261110_reg13/`
- **Pre-launch** (PROBE(docs/probe/20261110_reg13/prelaunch_reg13_attempt1.txt)): 2026-11-09 19:02:19 UTC, limit 350.00 W, 42 °C, 0 % use, no compute process, VM tree `723fc40` with 0 changed files (the Mac's `main`), 11 GB free, no tmux session. Launched `configs/sweep_l1pl350cl_pc_on.yaml`; console log `~/sweep_l1pl350cl_pc_on_20261109T190219Z.log` on the VM.
- **Runs** (each valid, `failed` empty, RUN(<id>, checks.json)); heat and limit as printed by the copy script from each run's `checks.json` details:

  | rate | run | sw_thermal | max °C | limit (W) |
  |---|---|---|---|---|
  | 2 | `20261109-190221_sweep_l1pl350cl_pc_on_r2` | 0.002 | 72 | 350.0 |
  | 2.4 | `20261109-191845_sweep_l1pl350cl_pc_on_r2.4` | 0.000 | 72 | 350.0 |
  | 2.6 | `20261109-193526_sweep_l1pl350cl_pc_on_r2.6` | 0.002 | 72 | 350.0 |
  | 2.8 | `20261109-195349_sweep_l1pl350cl_pc_on_r2.8` | 0.000 | 72 | 350.0 |
  | 3 | `20261109-201246_sweep_l1pl350cl_pc_on_r3` | 0.000 | 72 | 350.0 |

- **Copied** to the Mac, sha256 identical for 10 files per run; `manifests/runs.sha256` +50 lines. The VM copies are kept.
- The agent's watcher script printed shell errors (a count parse) for its first 20 min; it never touched the VM run, and was fixed and restarted. Only `checks.json` lines were read before the result.

## 2026-11-10 · [CORR] REG-13's client-side backlog test (`due_unreleased_slope`) was not checked on a healthy closed-loop run before registration, and it fails one
- **Error (the agent's):** adopting review recommendation T3, the agent added `gate.due_unreleased_slope` to the capacity test (sum with the server queue slope ≤ 0.01) without first applying it to closed-loop runs already known to be healthy. Found after the result, at λ = 2, where every other readout is healthy: pf 1.000, queue slope 0.000004, 0 unfinished, throughput 0.974 × planned, but `due_slope` 0.0195 (RUN(20261109-190221_sweep_l1pl350cl_pc_on_r2, gate.reg13_table)).
- **Why it fires** (exploratory, after the result; computed on the same run with the definition in `gate.due_unreleased_slope`): later turns due but not yet released ≈ (rate of later turns) × (release lag). Seed 0's later-turn planned rate rises from 1.395 to 2.174 req/s between the first and last 120 s of the window, which alone gives a slope of 0.011 at a 10 s lag; the median lag by planned minute drifts 8.7 → 12.7 s. The count stays between 10 and 25 per minute mark with no runaway. So the test measures the schedule's ramp, not a deficit, and 0.01 was a limit set for a server queue, not for this quantity.
- **What it changes:** nothing in the registered result (rule A5: no threshold or test is changed after the data it judges). The [RESULT] reports the registered outcome and, separately and labeled exploratory, what the configs' own rule gives. Any future closed-loop capacity test is checked on known-healthy runs before registration.

## 2026-11-10 · [RESULT] REG-13: `overload` by the registered test (the chain ends at λ = 2, on the client-side slope; see the correction above). By the configs' own rule μ_warm,cl = 2.4, below λp,max 2.711; at 2.6, 2.8 and 3 the server went cold 368–602 s after warm-up (DERIVED: backlog start − 240)
- **Computed once:** `uv run python -m analysis.gate reg13` (`gate.reg13_table`) on the five valid runs of the [OPS] entry above; every value below is RUN(<run at that rate>, gate.reg13_table) unless tagged otherwise.

  | rate | throughput | planned | ratio | queue slope | due slope | pf | KV mean | unfinished | backlog from (s) | hit before → after | release delay (s) | surge max |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|
  | 2 | 2.042 | 2.097 | 0.974 | 0.000 | 0.0195 | 1.000 | 0.169 | 0 | — | — | 9.8 | 2.21 |
  | 2.4 | 2.403 | 2.529 | 0.950 | −0.000 | 0.0460 | 0.992 | 0.243 | 0 | — | — | 11.5 | 3.04 |
  | 2.6 | 2.395 | 2.758 | 0.869 | 0.0077 | 0.134 | 0.825 | 0.335 | 0 | 842 | 0.786 → 0.000 | 12.8 | 3.33 |
  | 2.8 | 2.533 | 2.968 | 0.854 | 0.0142 | 0.191 | 0.765 | 0.415 | 0 | 810 | 0.772 → 0.000 | 14.8 | 3.61 |
  | 3 | 2.221 | 3.124 | 0.711 | 0.114 | 0.700 | 0.425 | 0.659 | 125 | 608 | 0.698 → 0.000 | 23.1 | 3.55 |

  Ratio = throughput / planned (DERIVED from the two columns). `collapsed` is false at every rate: at 2.6, 2.8 and 3 the ok completions before the backlog were 0.938, 0.932 and 0.883 × planned, under the registered 0.95.
- **Registered outcome: `overload`.** μ_warm,cl is undefined: λ = 2 fails the registered test only through `due_slope` (0.0195 > 0.01). n_cold_below 0.
- **The configs' own rule** (`mu_config_rule`, `tables.sweep_capacity`, no due slope): μ = **2.4**, and 2.4 passes with a ratio of 0.9503 against 0.95, at the edge. This reading is exploratory (the registered test includes the due slope), but it gives the same answer to REG-13's question: the warm closed-loop server does not carry λp,max = 2.711, and 2.6 (realized 2.758) fails. Had it been the test, the outcome would have been `partial` (realized load carried 2.529; 6 of 7 cold runs at λp ≤ 2.529, DERIVED from the λp table in the [REG]). Neither reading supports `below`.
- **Paired with REG-8** (open-loop, same schedules; RUN(20261107-103010_sweep_l1pl350_pc_on_r2, gate.reg13_table), RUN(20261107-104614_sweep_l1pl350_pc_on_r3, gate.reg13_table)): at λ = 2, throughput 2.042 vs 2.071 (−1.4 %, DERIVED), pf 1.000 vs 1.000. At λ = 3, 2.221 vs 3.023 (−26.5 %, DERIVED), pf 0.425 vs 0.990, KV mean 0.659 vs 0.336, hit 0 after 608 s. **Closed-loop turns lower the warm capacity at L1 from 3.0 to about 2.4–2.6:** a large effect, one seed.
- **Prediction** (model.md row 17): `overload` had p ≈ 0.1; the config-rule reading (`partial`) 0.15. Held: λ = 2 within 3 % of REG-8 (p ≈ 0.85); λ = 3 fails (p ≈ 0.6). Missed: 2.4 passes (p ≈ 0.8: fails the registered test, passes the config rule at the edge); a failure is a collapse (p ≈ 0.6: three failures went cold, none met the 0.95 bar).
- **Alternatives:**
  1. **Overload, not a transition** (the registered reading): above 2.4 the server cannot keep up, the backlog grows, and the cache goes cold as a consequence. Separates from 2: a queue that rises from warm-up at a warm hit rate. Here the backlog started late (608–842 s) after 368–602 s at 0.883–0.938 × planned with hit 0.698–0.786; that fits a slow deficit as well as a switch. Not separated by this sweep.
  2. **A cold switch at a surge** (the `collapsed` reading, missed by its 0.95 bar): each failing rate went from hit ≈ 0.78 to exactly 0 with surges of 3.33–3.61 in its window. Separates from 1: dropping the load after the switch (C1 condition 6), which this sweep does not do.
  3. **Closed-loop working set:** with turns released only after the previous reply, sessions last longer, more prefixes are live at once (KV mean 0.66 vs 0.34 at λ = 3), and the pool fills at a lower rate. This is a mechanism for 1 and 2 alike (BELIEF; open-questions A15).
  4. **One seed and a rising schedule:** seed 0's load rises across the window (status.md, M4); each rate's failure starts late, where the realized load is highest. μ from one schedule may be low.
  5. **The due-slope test** ([CORR] above) decides `overload` vs `partial` here; it does not change whether `below` holds.
- **Registered decision (`overload`):** λ = 2.4 is at or beyond the closed-loop warm capacity at L1, 350 W; REG-12's control failures and the cold states of REG-11/12 are explained by overload as well as by a metastable state, and this sweep cannot tell them apart. **REG-11's `pass` is not evidence of a metastable state** (claims.md changes only after the owner reviews this). The owner picks another factor or cell. Under the config-rule reading (`partial`) the choice would be the same: the owner's, between the confirmation run and a lower-λ cell.
- **Not changed:** REG-11/12's results and runs; claims.md; no threshold or code.

## 2026-11-10 · [CORR] The numbers in the REG-13 due-slope correction came from an uncommitted script; recomputed with `gate.due_unreleased_profile`
- **Error (the agent's):** the [CORR] of 2026-11-10 on `due_unreleased_slope` quoted later-turn planned rates of 1.395 and 2.174 req/s, a slope of 0.011 at a 10 s lag, and lags of 8.7 → 12.7 s, all from a one-off script, against `analysis/CLAUDE.md` and rule I (every number from a committed function).
- **Recomputed** with the committed `gate.due_unreleased_profile` (RUN(20261109-190221_sweep_l1pl350cl_pc_on_r2, gate.due_unreleased_profile)): due slope 0.0195; later-turn planned rate **1.433** over the first 120 s of the measured window and **2.467** over the last 120 s (the script had used trailing 60 s windows averaged over 120 s, a different quantity); median release lag by planned minute 8.7–12.7 s, median of the minutes 9.7 s.
- **The explanation holds, with these values:** due ≈ later-turn rate × lag gives a slope of (2.467 − 1.433) × 9.7 / 540 = 0.019 (DERIVED; 540 s between the two windows' midpoints, 300 s and 840 s), against the measured 0.0195. **The 0.011 figure is withdrawn.**
- **Not changed:** REG-13's registered outcome and its [RESULT].
## 2026-11-10 · [REG] REG-14 (exploratory, draft): REG-12's seed-2 pair at λ = 2.2 instead of 2.4, closed-loop turns, L1, 350 W (GPU, ≈ 1.5 h)
- **ID:** REG-14. **Exploratory.** **Not approved:** no GPU run before the owner approves this entry.
- **Why:** REG-13 ended `overload` (decisions.md 2026-11-10 [RESULT]): with closed-loop turns the warm server at L1, 350 W carries about 2.4 req/s by the configs' rule, so REG-11/12's cold states at λ = 2.4 sit at the warm capacity and overload explains them as well as a metastable state. Its registered decision: the owner picks another factor or cell. The owner asked on 2026-11-10 for a closed-loop cell at λ = 2 ("ok, draft the λ = 2 closed-loop cell REG"). The first draft (λ = 2, seed 1) failed review: at λ = 2 the registered span test can see a cold span only if it completes ≤ 1.81 req/s, against cold rates of 1.70–1.84 seen so far (review T1, below). **The owner then chose λ = 2.2, seed 2** (2026-11-10, answering the agent's question with the sensitivity numbers below). A cold state that holds at λ = 2.2, with the same-seed control healthy, sits below the warm capacity rather than at it.
- **Owner decisions this needs (C. Authority):** (1) research rule 2 relaxed for these runs as for REG-11/12 (owner, 2026-11-09): closed-loop later turns, session starts and burst requests open loop; (2) the cell λ = 2.2, seed 2 (given 2026-11-10, before any run of it); (3) approval of the run.
- **Question:** with REG-11's setup and burst, at λ = 2.2 and seed 2, does the server hold a cold backlog after the burst (a counting span) while the same-seed control stays healthy?
- **Claim tested:** none confirmatory. A `pass` is a reason for a confirmatory matrix, not evidence for C1.
- **Setup:** REG-12's seed-2 configs with `rate: 2.2`. Resolved with `load_config`, `with_defaults`, `harness.run.expand`: each differs from its REG-12 config only in `name` and `workload.rate` (test `test_reg14_configs_are_reg12_seed2_at_lambda_2_2_and_share_the_session_schedule`).
  - `configs/stage2_control_l1pl350cl_r2.2_s2.yaml`: `extends: stage2_control_l1pl350cl_r2.4_s2.yaml`.
  - `configs/burst_l1pl350cl_r2.2_s2.yaml`: `extends: burst_l1pl350cl_r2.4_s2.yaml`. **The burst is unchanged:** at 900 s, 180 s at 2.4 req/s, 2944-token prompts, `burst_min_kv_max` 0.95.
  - So: L1, 350 W check, closed-loop turns, force_close, dev mode, seed 2, 2580 s, control judged at 1080 s. No harness or check change.
- **Design inputs** (computed before this entry from the configs and from runs that exist; no REG-14 data exists): `uv run python -m analysis.gate reg14_inputs` and `reg14_sensitivity` (`gate.reg14_inputs`, `gate.reg14_schedule_inputs`, `gate.span_sensitivity`, `gate.max_holding_c`, `gate.reg14_seed_rule`; schedules DERIVED from `build_schedule` on the resolved configs).
  - **What the span test can see** (review recommendation 1). A span holds only if `poisson_rate_upper(n, 300 s, 0.99)` < min(λ, λp) (`gate.burst_backlog`), so `max_holding_c` is the highest cold completion rate that can still hold. For seeds 1–10:
    - at **λ = 2**, every span's limit is ≤ 1.81 for every seed. The cold runs at 2.4 completed 1.70–1.84 per span (decisions.md 2026-11-09 [RESULT] REG-12, RUN(<burst id>, gate.reg12_table)). With seed 1, spans 1 and 3 could not hold even at 1.717 (limits 1.54, 1.65). **No seed qualifies under the rule below.**
    - at **λ = 2.2**, limits reach 2.00.
  - **Seed rule** (`gate.reg14_seed_rule`): the lowest seed in 1–10 whose every span has a limit above 1.84 (`REG14["cold_c_max"]`, the highest cold span rate seen). At λ = 2.2 it gives **seed 2**; at λ = 2 none. The rule was written after REG-11/12's cold rates were known and before any λ = 2.2 run.
  - **Seed 2 at λ = 2.2:**

    | | value |
    |---|---|
    | session requests | 5489 |
    | burst requests | 463 (REG-12's seed 2: 463) |
    | control schedule equals the burst run's session rows | yes |
    | λp, 600 s baseline before the burst | 2.200 |
    | λp, burst's end to end of arrivals | 2.178 |
    | λp in REG-8's spans (600–900, 900–1200, 1200–1500 s after the burst's end) | **2.207, 2.100, 2.347** |
    | holding limit per span | **2.000, 1.903, 2.000** |
    | 120 s windows above 2.4 | 2.742 (480–600 s, before the burst), 2.675 (1560 s), 2.617 (1680 s), 2.425 (2280 s), 2.433 (2400 s) |

  - **Warm side** (review recommendation 5): REG-13's closed-loop runs carried planned 2.097 at λ = 2 (throughput 2.042) and 2.529 at λ = 2.4 (2.403, ratio 0.950, the configs' rule at its edge) (RUN(20261109-190221_sweep_l1pl350cl_pc_on_r2, gate.reg13_table), RUN(20261109-191845_sweep_l1pl350cl_pc_on_r2.4, gate.reg13_table)). REG-13's registered test failed λ = 2 on the client-side slope only ([CORR] 2026-11-10). **The direct evidence that this schedule is carried warm is its own control**; a `pass` needs it `recovered` and not backlogged in the counting span.
  - **Shock reference:** REG-12's seed-2 burst run (`20261109-080203_burst_l1pl350cl_r2.4_s2`, same seed and burst at λ = 2.4, `stuck`): 46 outstanding session requests at the burst's end, 1499 s backlogged (RUN(20261109-080203_burst_l1pl350cl_r2.4_s2, gate.shock_size)).
- **Analysis, computed once after both runs are valid and copied:** `uv run python -m analysis.gate reg14` (`gate.reg14_gate` = `gate.reg10_gate(REG14)`, `REG14 = {**REG11, "lam": 2.2, "seed": 2}` with the `r2.2_s2` patterns). It refuses a run not at λ = 2.2, not seed 2, not closed loop or not force_close. Labels are REG-11's: `pass`, `drains`, `control_not_healthy`, `stuck_unconfirmed`, `inconclusive`. **`outcome`** (`gate.reg14_outcome`, round-2 review B1) splits `pass`: **`pass_clear`** if in some counting span the control waited (waiting > 0) at ≤ 0.5 of its scrapes (`REG14["max_control_waiting"]`, fixed now), else **`pass_warm_edge`** (the control queued through every counting span, so overload at the warm edge is not excluded there).
  - Readouts, never decisive except as stated under `drains`: REG-11's (`release_delay`, `release_delay_baseline`, `turn0_share`, `unreleased`, `span_clock`, `secondary_cb`, λp and c per span) and `post_trigger` (λp from the burst's end).
  - New readouts (review recommendation 4): `max_holding_c` per span next to its c; `release_rate`, the session requests released per second in each span (first turns included, the same population as λp; round-2 review T5), against λp (review T2: under closed loop the released load falls when sessions lag); `control_waiting`, the share of the control's scrapes with waiting > 0 and its mean in each span (review T3).
  - **`shock_comparable`** against REG-12's seed-2 burst run with REG-11's rule: outstanding ≥ 0.5 × 46 and backlog_s ≥ 0.5 × 1499 (`REG11["comparable_frac"]`, unchanged).
- **Prediction** (BELIEF):
  - Both runs valid p ≈ 0.85.
  - The burst fills the pool p ≈ 0.85 (review recommendation 6). The same burst filled it at 2.4; baseline KV at 2.2 is lower, between REG-13's 0.169 at λ = 2 and 0.243 at 2.4. No fallback is registered: a burst that does not fill the pool goes to the owner.
  - Control `recovered` p ≈ 0.75. Seed 2's control at 2.4 recovered (REG-12), but this schedule surges to 2.68 at 1560 s, inside the control's watch.
  - Burst verdict `stuck` p ≈ 0.55. At 2.4 seed 2 was stuck; at 2.2 the cold-side surplus is λp − c ≈ 2.18 − 1.8 ≈ 0.4 (DERIVED), against ≈ 0.5 at 2.4.
  - Given a valid pair: `pass` ≈ 0.35, `stuck_unconfirmed` ≈ 0.1, `drains` ≈ 0.3, `control_not_healthy` ≈ 0.15, `inconclusive` ≈ 0.1.
  - A `pass` is `pass_clear` p ≈ 0.6 (BELIEF: REG-13's λ = 2.4 run kept the queue near empty at a 0.950 ratio, but a waiting share was not measured there).
  - `shock_comparable` p ≈ 0.6.
  - **`cold_c_max` caveat** (round-2 T7): 1.84 is the highest point rate at λ = 2.4; if the cold rate rises at lower load, a span's limit may not cover it. A `drains` reports c per span against its limit.
- **Decision under each outcome:**
  - **`pass_clear`:** the first cold state that held below the closed-loop warm capacity, with its own control healthy. Report as exploratory, one seed, with `release_rate` and `control_waiting` in the counting span. Draft for the owner, in order: (1) a confirmatory matrix at λ = 2.2 (REG-12's design, five seeds, each with a same-seed control, ≈ 8 GPU h; which seeds is the owner's call, since this seed was picked by the detector rule); (2) C1's confirmation run (4500 s watch, then the drop to λ = 1).
  - **`pass_warm_edge`:** reported as "held, but the control was queueing in the counting span"; no matrix is drafted. The owner decides.
  - **`stuck_unconfirmed`:** not rerun; reported with the readouts; the owner decides.
  - **`drains` with `shock_comparable`** (review recommendation 2): report "no cold state held at λ = 2.2, seed 2, with this detector (limits 1.90–2.00 per span)", with c per span against its limit. It is not by itself a negative result for L1. The owner chooses between a second seed at 2.2, λ = 2.3, or a larger trigger.
  - **`drains` without `shock_comparable`:** "λ = 2.2 made the shock smaller"; nothing is ruled out. For the owner: a larger trigger, sized from `shock_size`.
  - **`control_not_healthy`:** the closed-loop warm state does not last 2580 s at 2.2 either. With REG-12 (3 of 5 controls not healthy at 2.4), the window between a stable warm state and a detectable cold one is narrow or absent at L1 with closed loop. The owner decides.
  - **`inconclusive`:** rerun the pair unchanged, at most twice.
  - **Burst run invalid on `burst_min_kv_max`:** not rerun; the owner decides.
- **Alternatives:**
  1. **A slow drain or criticality read as `stuck`:** a backlog that neither grows nor clears over 1500 s. The span test needs c_upper below both λ and λp; `release_rate` shows whether the server kept up with what was released. C1's confirmation run (4500 s, then λ = 1) separates the rest.
  2. **The released load is not λp** (review T2): closed-loop sessions that fall behind release less than planned. `release_rate` below λp in a counting span says part of the deficit sits as session lag rather than in the server's queue; the size of the cold-state deficit is then smaller than λp − c. Reported, never decisive.
  3. **Near-saturation queueing in the control** (review T3, round-2 T6): REG-11's rule counts a control as not backlogged if a single scrape shows an empty queue, and the seed rule favours spans with high λp (span 1 follows windows of 2.675 and 2.617; span 3 has λp 2.347). `pass_warm_edge` separates a `pass` whose control queued through the counting span; only `pass_clear` leads to the matrix.
  4. **Load-dependent cold rate** (review): the cold completion rate may rise at lower λ (a smaller working set), so a `drains` could mean bistability over a narrower λ range rather than none. c per span against REG-12's seed-2 spans at 2.4.
  5. **Seed picked by the detector:** seed 2's spans have high λp, which favors both a holding span and warm-side strain. Its own control checks the warm side; a matrix would not reuse this rule without the owner.
  6. **Surges:** seed 2 surges to 2.74 before the burst and 2.68 after; the control has the same schedule.
  7. **Percent-fast binning by planned time** pushes the burst verdict toward `stuck` (REG-11 owner decision 3); `pass` also needs a holding span.
  8. **Recorder failure** (open-questions A14): not fixed; `accounting` catches it. One seed, dev mode, 350 W, L1 only.
- **Stopping rule:** REG-11's. Each run once; an invalid run (other than `burst_min_kv_max`) is rerun unchanged, at most twice; a heat-invalid run once after cooling to ≤ 45 °C, a second heat failure stops; a `client_error`, a limit other than 350 W or an unexpected pre-launch check stops. A rerun decision reads only `checks.json`. No interim look at either run's verdict before both are valid.
- **Operations:** REG-13's pre-launch checks (350 W read, the VM tree clean at the Mac's `main`, no compute process, GPU ≤ 45 °C); console log named per attempt. Control first, then the burst run.
- **Cost:** 2 × (2580 s + about 60 s start-up) ≈ 1.5 GPU h (DERIVED: 5280 s), plus cooling; worst case with every rerun ≈ 4.4 GPU h.
- **Code and files:** the two configs; `analysis/gate.py` (`REG14`, `max_holding_c`, `span_sensitivity`, `reg14_seed_rule`, `reg14_sensitivity`, `reg14_schedule_inputs`, `reg14_inputs`, `release_rate`, `control_waiting`, `reg14_gate`, `reg14_outcome`; CLI `reg14`, `reg14_inputs`, `reg14_sensitivity`; also `due_unreleased_profile`, for the [CORR] of 2026-11-10); `tests/test_gate.py` (8 new: the configs against REG-12's with the same session schedule; the patterns and spec; `max_holding_c`; the seed rule; the gate's shock comparison and its λ and seed checks; `release_rate`; `reg14_outcome`; `due_unreleased_profile`).
- **Not changed:** REG-11/12/13's results and runs; no harness, check or threshold change.

### Adversarial review (separate subagent; it saw only the draft, its diff and the code and configs those call; it opened no runs and no docs). Round 1, on the first draft (λ = 2, seed 1). Verbatim:

> ## Rule F review: REG-14 draft (registration and diff only; no runs/ or docs/ opened)
>
> I ran `uv run pytest -q tests/test_gate.py`: 48 passed. I ran `uv run python -m analysis.gate reg14_inputs` and it reproduces the draft's inputs: λp,post 1.950; spans 1.717 / 2.103 / 1.833; surge 2.558 at 960 s; 422 burst requests and 5137 session requests; schedules identical; warm planned rate 2.097; reference 65 requests / 1499 s; feasible True.
>
> ### 1. Traces where the verdict or the code is wrong
>
> **T1. In practice the gate tests one 300 s span, and the feasibility check measures the wrong quantity.** A span holds only when `c_upper < min(λ, λp)` (analysis/gate.py, `burst_backlog`, the `row["holds"]` line). `c_upper` is `poisson_rate_upper(n, 300, 0.99)`. I computed the largest point completion rate c that can still hold in each span (DERIVED, by searching over n):
> - span 1: below 1.717 needs c ≤ 1.54
> - span 2: below min(2.0, 2.103) = 2.0 needs c ≤ 1.81
> - span 3: below 1.833 needs c ≤ 1.65
>
> The draft's cold reference rates are 1.717–1.84. On those, spans 1 and 3 cannot hold, and the 1.84 that `reg14_feasible` uses holds in no span at all (`p(552, 300, .99)` = 2.03 > 2.0). `reg14_feasible` compares the post-burst average λp (1.95) with a point c (1.84), so it reports a 6 % margin. The real margin is 1.81 against REG-11's 1.717–1.79, which is 0.02–0.09 req/s, in span 2 only.
>
> - **Concrete trace:** a burst run that stays cold, backlogged and burst-free, with c = 1.79, 1.80 and 1.82 across the spans, yields `drains`, and the `drains`+comparable branch then reads it as "overload explains every stuck state". The test cannot detect the hypothesis it is meant to test.
>
> **T2. Under closed loop, λp is not the offered load.** The loadgen releases a later turn at the previous turn's `t_end` plus the planned gap (harness/loadgen.py:90–105), so a session that falls behind never catches up. The turns actually released in a span fall below the planned λp whenever the lag grows. "c < λp while the queue never empties" therefore also fits a server that serves everything released to it while the deficit builds up as session lag (the subject of the [CORR] on `due_unreleased_slope`). The span test gets its force from c being well below the warm capacity of ≈2.4, not from c < λp. No readout reports the per-span release rate next to λp.
>
> **T3. The control's "not backlogged" rule is weak in span 2.** `control_backlog` sets `backlogged = q.min() > 0` (gate.py, `control_backlog`). In span 2 λp is 2.103. A control with waiting > 0 at all scrapes but one counts as healthy there, so a `pass` can come from queueing near saturation that the burst's leftover backlog amplifies. This is REG-11's rule and is not a code bug, but the risk is highest exactly in span 2.
>
> **T4. The warm-side bound contradicts itself.** The feasibility bound is 2.097, and span 2, where the draft expects a `pass`, has λp 2.103 > 2.097. The evidence that λ = 2 is carried warm is a run that failed REG-13's registered test (the due slope, per the [CORR]). This does not change any decision: the same-seed control is the real check. It should be stated as such.
>
> **Code:** I found no logic bug. The patterns, the λ check (YAML `2` == `2.0`), the inherited `comparable_frac` and the reference override are all correct. `reg14_gate` loads the reference run on every call, which is harmless.
>
> ### 2. Strongest alternative explanation per outcome
> - **`pass` (span 2 only):** a slow drain during a local rise in the schedule, with lag growing under closed loop (T2), or near-saturation queueing (T3). These are separated by the per-span release rate, the control's waiting fraction and mean in that span, and c compared with 2.4. Only C1's watch-then-drop run separates them fully.
> - **`drains` with `shock_comparable`:** the gate was blind to the result (T1), or the cold completion rate depends on load (fewer concurrent sessions leave a smaller working set, so it recovers at 2.0 but not at 2.4). That would be bistability over a narrower range of λ, not overload. These are separated by c per span against the T1 thresholds, the hit share per span, and an intermediate λ such as 2.2.
> - **`stuck_unconfirmed` / `inconclusive`:** criticality (cold c ≈ λp ≈ 1.83 in span 3), where the backlog neither grows nor drains. The span test cannot settle it; it needs a longer watch.
> - **`control_not_healthy`:** the 2.558 surge at 960–1080 s, which falls inside the control's baseline window. It is separated by the control's first backlogged stretch against the surge time.
>
> ### 3. Can the run change a decision?
> Partly. `pass` and `drains`+comparable lead to different actions (an 8 GPU h matrix against a pivot). `stuck_unconfirmed`, `control_not_healthy`, `drains` without comparable, and invalid on `burst_min_kv_max` all end in "the owner decides" or something close to it, so they are not distinct decisions. Given T1, a `drains` is weak evidence. If the `drains`+comparable outcome reads it as "no metastable state shown at L1", the run can push a negative write-up it cannot support.
>
> The feasibility check is not a gate: its inputs were known when it was written (the draft says so), and it computes the wrong quantity (T1). As written it cannot fail.
>
> ### 4. Recommendations
> 1. **Blocking.** Replace `reg14_feasible` with a per-span sensitivity design input. For each span, compute the largest c that can hold, from `min(λ, λp)` and `poisson_rate_upper` at 0.99, and set it against REG-11/12's observed cold span c values. Put these numbers in the entry and label them as design inputs, not a test.
> 2. **Blocking.** Rewrite the decision under `drains` with `shock_comparable`. It should read "no cold state held at λ = 2 with this detector (one span testable, c ≤ 1.81)". It should not read "overload explains every stuck state". Writing L1 up as negative should not be one of its options without an intermediate λ or a second seed.
> 3. **Blocking (owner).** Decide whether seed 1 stays. At λ = 2 the schedule already differs from REG-11's, so keeping seed 1 buys only the shared burst. If the owner prefers a seed whose spans are all ≥ ≈ 2.0, pick it from `build_schedule` before any run and record the rule used to pick it.
> 4. **Non-blocking.** Add readouts: the per-span release rate (`t_released` in the span), the share of control scrapes with waiting > 0 and its mean in each span, and each span's c next to its threshold from recommendation 1.
> 5. **Non-blocking.** Restate the warm-side evidence (T4): the same-seed control is the evidence. REG-13's λ = 2 run failed its registered test, and span 2's λp is above 2.097.
> 6. **Non-blocking.** Estimate how often the burst will fail to fill the pool, given the lower baseline KV (0.169), since that outcome means no rerun. If that probability is high, decide before the run whether a larger burst is the fallback.

### Round 2, on the revised draft (λ = 2.2, seed 2, the owner's choice). Verbatim:

> ## Rule F review, round 2: REG-14 revised (λ = 2.2, seed 2)
>
> Neither file under runs/ or docs/ was opened. `uv run pytest -q tests/test_gate.py`: 50 passed. `uv run python -m analysis.gate reg14_inputs` reproduces the draft's numbers:
> - λp per span: 2.207 / 2.100 / 2.347; post-burst λp 2.178.
> - `max_c` per span: 2.000 / 1.903 / 2.000.
> - 120 s windows above 2.4 start at 480, 1560, 1680, 2280 and 2400 s.
> - 463 burst requests; the control's schedule equals the burst run's session rows.
> - Warm runs: planned 2.097 / 2.529.
> - Reference: 46 requests / 1499 s; `seed_rule` = 2.
>
> I started `reg14_sensitivity` and stopped it before it finished. Its output was not seen; its seed-2 result agrees with `reg14_inputs`.
>
> ### (1) Status of recommendations 1–6
> 1. **Addressed.** `max_holding_c`, `span_sensitivity` and `reg14_seed_rule` compute the quantity the gate actually tests. At λ = 2.2, seed 2, every span's limit (≥ 1.90) is above the cold rates seen so far (1.70–1.84).
> 2. **Addressed.** `drains` is now read as "with this detector, at λ = 2.2, seed 2" and is no longer a negative result for L1.
> 3. **Addressed.** The owner chose the cell and the seed by a stated rule, before any run of it. The draft also admits the seed is picked by the detector (alternative 5).
> 4. **Partly addressed.** `release_rate` is defined wrongly (T5 below). `control_waiting` is a readout only.
> 5. **Addressed.** The control is now named as the direct evidence that the schedule is carried warm.
> 6. **Partly addressed, acceptable.** p ≈ 0.85 is given and no fallback is registered; a burst that does not fill the pool goes to the owner.
>
> ### (2) New traces
> **T5. `release_rate` leaves out first turns but is compared with a λp that includes them** (analysis/gate.py:818). It counts only `turn > 0`. λp (`planned_session_rate`) counts every session request, first turns included, and first turns are open loop. So `release_rate` < λp by the first-turn share even when no session lags at all.
> - Concrete trace: a healthy server that keeps up, with first turns at about 0.4 of λp in a span. `release_rate` reads about 0.6 × λp, which looks like heavy session lag.
> - The other direction: a server that is truly cold and lagging can show `release_rate` ≈ c by coincidence. Alternative 2's reading "`release_rate` ≈ c means the deficit is session lag" then rests on a mismatched comparison.
> - Fix: add the first turns planned in the span (open loop), or compare with the planned rate of later turns only.
>
> **T6. The seed rule favours spans near the warm capacity, and the control check there is weak.** The rule picks the seed with high λp in every span. Span 1 (1680–1980 s) opens with the 2.617 window at 1680 s and follows the 2.675 window at 1560 s. Span 3 has λp 2.347 and windows of 2.425 and 2.433. The closed-loop warm server was shown to carry 2.4 only at the edge of the configs' rule (2.403 / 2.529 = 0.950).
> - In those spans the control counts as not backlogged if a single scrape shows an empty queue (gate.py:115, `q.min() > 0`).
> - So a `pass` counted in span 1 or 3 is still open to the overload explanation that REG-14 was built to remove. The draft only "names" a control waiting share above 0.9; nothing in the code acts on it, and `pass` still leads to the ≈ 8 GPU h matrix.
> - Span 2 (λp 2.100, limit 1.903) is the only span that is clean on this point.
>
> **T7 (minor).** `cold_c_max` = 1.84 (gate.py:733) is the highest point estimate from the λ = 2.4 runs. If the cold rate depends on load, it can be higher at 2.2, so "every span can see a cold state" is a belief, not a guarantee. A `drains` result already reports c per span against its limit, which covers this. Non-blocking.
>
> The rest of the code (patterns, λ and seed checks, `max_holding_c` boundaries, shock comparison, burst RNG independent of the rate) looks correct.
>
> ### (3) Remaining blocking items
> - **B1 (needs the owner, because it changes the decision map; register before any run).** Make the `pass` → matrix decision depend on the counting span. The matrix is drafted only if:
>   - the counting span is span 2, or
>   - in the counting span the control's `share_waiting` is ≤ a threshold fixed now (e.g. 0.5) and the control's queue mean is near its baseline.
>
>   Any other `pass` is reported as "pass at the warm edge" and goes to the owner. This can be a readout rule in the decisions entry; `reg10_gate`'s label does not need to change.
> - **B2.** Fix `release_rate` (T5) and its test before registration, or remove the "`release_rate` ≈ c" reading from alternative 2.

### Changed because of it
- **Round 1:** 1 adopted: `reg14_feasible` removed; `max_holding_c`, `span_sensitivity`, `reg14_seed_rule`, `reg14_sensitivity` added, and their numbers are in the design inputs. 2 adopted: `drains` is read as "not detected with this detector". 3: put to the owner, who chose λ = 2.2, seed 2 (the rule's pick). 4 adopted: `release_rate`, `control_waiting`, `max_holding_c` per span. 5 adopted. 6 adopted as a prediction; no fallback.
- **Round 2:** B2 adopted: `release_rate` counts every session request sent (first turns included), the same population as λp, with its test. B1 adopted in a stricter, uniform form: `pass_clear` requires a counting span whose control waited at ≤ 0.5 of its scrapes, whatever the span; no span-2 exemption, because span 2 (λp 2.10) can also queue. The queue-mean condition was not adopted: there is no registered baseline for it, and the waiting share already measures it. Other `pass` → `pass_warm_edge`, to the owner. The 0.5 is fixed in `REG14["max_control_waiting"]` before any run; it is the agent's choice, and the owner can change it before approval. T7: noted as a caveat in the prediction.

## 2026-11-10 · [DECISION] Owner approves REG-14 and its runs
- **Owner's answer:** "ok, approve REG-14, run it", to the question whether REG-14 (decisions.md 2026-11-10 [REG]) is approved: REG-12's seed-2 control and burst run at λ = 2.2 with closed-loop turns, ≈ 1.5 GPU h. The `pass_clear` threshold stays at 0.5 (the owner did not change it). Research rule 2 is relaxed for these two runs as for REG-11/12.
- **Order:** `configs/stage2_control_l1pl350cl_r2.2_s2.yaml`, then `configs/burst_l1pl350cl_r2.2_s2.yaml`, each after REG-13's pre-launch checks, reads saved in `docs/probe/20261110_reg14/`; VM console logs named per attempt. An agent queue script stops at the first run that is not valid or any pre-launch STOP; the agent then applies the stopping rule, reading only `checks.json`.
- **Standing instructions** (decisions.md 2026-11-09 [DECISION]) apply. No verdict is computed before both runs are valid and copied; then `gate.reg14_gate` once, the `[RESULT]`, and the next drafts by the registered outcome, which do not run before the owner approves them.

## 2026-11-10 · [OPS] REG-14 runs: 2 of 2 valid, no rerun; pre-launch reads in `docs/probe/20261110_reg14/`
- **Control** `20261110-055201_stage2_control_l1pl350cl_r2.2_s2`: launched 05:51:59 UTC at 350.00 W, 42 °C, no compute process, VM tree `41d1850` clean (PROBE(docs/probe/20261110_reg14/prelaunch_reg14_stage2_control_l1pl350cl_r2.2_s2_attempt1.txt)). Valid, `failed` empty (RUN(20261110-055201_stage2_control_l1pl350cl_r2.2_s2, checks.json)); sw_thermal 0.001, max 72 °C, limit 350.0 W.
- **Burst** `20261110-063647_burst_l1pl350cl_r2.2_s2`: launched 06:36:45 UTC at 350.00 W, 44 °C (PROBE(docs/probe/20261110_reg14/prelaunch_reg14_burst_l1pl350cl_r2.2_s2_attempt1.txt)). Valid, `failed` empty (RUN(20261110-063647_burst_l1pl350cl_r2.2_s2, checks.json)), so the burst filled the pool (`burst_min_kv_max`); sw_thermal 0.000, max 72 °C, limit 350.0 W.
- Console logs on the VM: `~/stage2_control_l1pl350cl_r2.2_s2_20261110T055158Z.log`, `~/burst_l1pl350cl_r2.2_s2_20261110T063644Z.log`. Copied to the Mac, sha256 identical (10 files each); `manifests/runs.sha256` +20 lines. VM copies kept.

## 2026-11-10 · [RESULT] REG-14: `pass_clear`. At λ = 2.2 the burst left the server cold, full and backlogged in all three spans, while the same-seed control kept an empty queue and full speed
- **Computed once:** `uv run python -m analysis.gate reg14` (`gate.reg14_gate`) on the two runs above; values RUN(<run>, gate.reg14_gate) unless tagged otherwise. Verdicts (`load.verdict`): control **`recovered`**, burst **`stuck`**. Label `pass`; all three spans count; **outcome `pass_clear`** (the control's waiting share in the counting spans is 0.000–0.003, under 0.5).

  | span (s after the burst's end) | c | c_upper | holding limit | λp | released rate | sessions' hit share (baseline 0.834) | KV | waiting q mean (min) | control: share of scrapes waiting |
  |---|---|---|---|---|---|---|---|---|---|
  | 600–900 | 1.807 | 1.996 | 2.000 | 2.207 | 1.893 | 0.000 | 0.948 | 116 (96) | 0.000 |
  | 900–1200 | 1.733 | 1.919 | 1.903 | 2.100 | 1.860 | 0.000 | 0.952 | 152 (129) | 0.003 |
  | 1200–1500 | 1.753 | 1.940 | 2.000 | 2.347 | 1.803 | 0.000 | 0.948 | 177 (163) | 0.003 |

- **End window** (`load.verdict`, RUN(<run>, load.verdict)): the burst run ends at pf 0.000, hit 0.000, queue 164.5, KV 0.950, 30.0 running, against its own baseline pf 0.992, hit 0.834, queue 0, KV 0.191. The control ends at pf 1.000, hit 0.836, queue 0.003, KV 0.183, 5.7 running: the same schedule, without the burst, carried at full speed.
- **Readouts:** `secondary_cb` `not_sustainable`, one backlogged stretch over the whole 1499 s, c_b 1.784 against λp 2.178. `shock_size` 44 outstanding and 1499 s backlogged against REG-12's seed-2 reference 46 and 1499 s: `shock_comparable` true. `release_delay` 234, 354, 356 s per span against 11.1 s before the burst. `unreleased` 0, 74, 314. `turn0_share` 0.155, 0.142, 0.156. `span_clock` 1890 MHz before the burst, 1845 MHz in each span (−2.4 %, DERIVED: 45 / 1890).
- **Prediction** (model.md row 18): both valid, hit (0.85). Burst fills the pool, hit (0.85). Control `recovered`, hit (0.75). Burst `stuck`, hit (0.55). `pass` ≈ 0.35 with `pass_clear` ≈ 0.6 of it, so ≈ 0.21 (DERIVED: 0.35 × 0.6): it happened. `shock_comparable`, hit (0.6).
- **Alternatives:**
  1. **Warm-side overload** (REG-13's reading of REG-11/12): ruled out for this schedule. In the same spans, the control on the identical session schedule waited at 0–0.3 % of scrapes and ended at pf 1.000, hit 0.836. The warm server carried this exact load with an empty queue; the burst run, cold, did not.
  2. **A slow drain:** not within 1500 s. The queue grew in every span (116 → 152 → 177), and completions (1.73–1.81) stayed below what was released into the server (1.80–1.89). A later turn-around is not excluded; C1's confirmation run (4500 s watch) separates it.
  3. **The released load is not λp** (review T2): sessions lagged 4–6 minutes, so the server received 1.80–1.89 req/s, not the planned 2.10–2.35. Even against that lower, self-throttled load the cold server fell behind; the warm control kept up with the full planned load.
  4. **Heat or clock:** busy SM clock 2.4 % lower in the spans; completions are ≈ 20 % below λp (DERIVED: 1.75 / 2.18 ≈ 0.80). The clock cannot account for it; both runs ran at 350 W with sw_thermal ≤ 0.001.
  5. **Queue mix:** first turns made up 0.14–0.16 of completions, as in REG-11 (0.15–0.18); no shift toward short prompts explains the rate.
  6. **Percent-fast binning:** 74 and 314 never-released turns count as misses in spans 2–3 and push pf down; the pass rests on the span test, which counts completions by `t_end`.
  7. **One seed, picked by the detector rule** (REG-14 alternative 5): seed 2 has high λp in every span. A matrix with seeds not chosen by this rule tests whether it generalizes.
  8. **Not yet hysteresis:** this shows a cold state held for 1500 s at a load the warm state carries. Whether it persists when the load drops (C1's λ = 1 condition) is untested.
- **What this is:** the first stuck state of the study that warm-side overload does not explain: the same schedule, warm, ran with an empty queue; after a 180 s burst it ran cold at the cache-off floor (c_b 1.784 against μ_sat,off 1.681, ×1.06, DERIVED) with a growing queue. One seed, exploratory; not evidence for C1 until the matrix and the confirmation run.
- **Registered decision (`pass_clear`):** draft for the owner, in order, (1) a confirmatory matrix at λ = 2.2 (REG-12's design, five seeds each with a same-seed control, ≈ 8 GPU h; which seeds is the owner's call) and (2) C1's confirmation run (4500 s watch, then the drop to λ = 1). Neither runs before the owner approves it. claims.md is not changed before the owner reviews this.
- **Not changed:** REG-11/12/13's results; claims.md; no code or threshold.

## 2026-11-10 · [CORR] C1's λ = 1 condition is recovery after the drop, not persistence; misstated in REG-14's result and to the owner
- **Error (the agent's):** the REG-14 [RESULT] (alternative 8) says "whether it persists when the load drops (C1's λ = 1 condition) is untested", and the agent told the owner in chat that staying stuck at low load would be the core of C1. **docs/claims.md C1 ("Supports") requires the confirmation run to be `stuck` over a 4500 s watch and then `recovered` after the drop to λ = 1 (condition 6).** The drop shows the cold state is held by the load, not a broken server; staying stuck at λ = 1 would not support C1.
- **Correct reading of REG-14's open point:** untested are (a) whether the cold state lasts the 4500 s watch and (b) whether it recovers after the drop to λ = 1.
- **Not changed:** REG-14's outcome and decision; C1's text.

## 2026-11-10 · [DECISION] Owner: C1's confirmation run before the matrix; the matrix at λ = 2.2 on seeds 3–7
- **Owner's answer:** "Agree", to the agent's recommendation after REG-14's `pass_clear` (decisions.md 2026-11-10 [RESULT]): (1) draft C1's confirmation run (PROTOCOL §3 conditions 5–6: a 4500 s watch, then λ = 1 for 1800 s, then λ back for 1500 s) at λ = 2.2 with seed 2 **before** the confirmatory matrix, reversing the order REG-14 registered; (2) the matrix, when drafted, uses seeds 3–7 (seed 2, the pilot, not counted; no seed chosen by the detector rule).
- **Why the order changed** (the agent's argument): the confirmation run costs less than a third of the matrix and can rule C1 out at this cell on its own (a cold state that clears within 4500 s fails condition 5 whatever the matrix shows).
- Each is a separate registration with its own review; nothing runs before the owner approves it.

## 2026-11-10 · [CORR] The confirmation run does not repeat REG-14's session schedule, though it uses the same seed
- **Error (the agent's):** recommending the confirmation run, the agent told the owner that with seed 2 it "repeats the REG-14 burst run with a longer watch". It does not. `build_schedule` draws each load segment's session starts at once over the segment's length (`harness/workload.py` `_poisson_times`, `_arrival_times`), so a longer run gives a different session schedule from t = 0: 5921 session requests planned before 2580 s, against REG-14's 5952, with different times (DERIVED: `build_schedule` on `configs/confirm_l1pl350cl_r2.2_s2.yaml` and `configs/burst_l1pl350cl_r2.2_s2.yaml`; test `test_reg15_config_is_reg14s_burst_run_with_the_watch_drop_and_return`). Only the burst is identical (its own generator).
- **What it changes:** REG-14's control is not a control for the confirmation run's schedule. The return to λ = 2.2 inside the run (condition 6) is the in-run check that the warm server carries that schedule. The REG-15 draft says so.
## 2026-11-10 · [REG] REG-15 (draft): C1's confirmation run at REG-14's cell, seed 12: a 4500 s watch, then λ = 1, then back to λ = 2.2 (GPU, ≈ 2.6 h)
- **ID:** REG-15. **Confirmatory for C1's conditions 5 and 6 at one load, in one run** (PROTOCOL §3); not for C1 as a whole, which also needs the matrix (condition 3) and condition 4. **Not approved:** no GPU run before the owner approves this entry.
- **Why:** REG-14 gave `pass_clear` (decisions.md 2026-11-10 [RESULT]). The owner chose to run C1's confirmation run before the matrix (decisions.md 2026-11-10 [DECISION]). It costs less than a third of the matrix and can rule C1 out at this cell on its own. The first draft used seed 2. The review (below, T1–T2) showed that seed 2's schedule loads the window judged `stuck` at 2.44 and the window judged `recovered` at 2.21. **The owner then chose seed 12** (2026-11-10), picked by the judged-window rule below.
- **Question:** at λ = 2.2 with closed-loop turns (L1, 350 W):
  - (5) is the server still `stuck` 4500 s after the burst, without having recovered on the way?
  - (6) λ then drops to 1 req/s for 1800 s and returns to 2.2 for 1500 s. Does the queue reach 0 during the drop, and are the last 600 s `recovered` against the original baseline?
- **Setup:** `configs/confirm_l1pl350cl_r2.2_s12.yaml`: `extends: burst_l1pl350cl_r2.2_s2.yaml` (REG-14's burst run), with `seed: 12`, `workload.duration_s: 8880`, `workload.steps: [{at_s: 5580, rate: 1}, {at_s: 7380, rate: 2.2}]` and `verdict.watch_s: 4500`.
  - Resolved with `load_config`, `with_defaults`, `harness.run.expand`. It differs from REG-14's burst config only in `name`, `seed`, `workload.duration_s`, `workload.steps` and `verdict.watch_s` (test `test_reg15_config_is_reg14s_burst_run_with_the_watch_drop_and_return`).
  - So: L1, 350 W check, closed-loop turns, force_close, dev mode. The burst starts at 900 s and lasts 180 s, at 2.4 req/s with 2944-token prompts; `burst_min_kv_max` 0.95.
  - `workload.steps` is the harness's existing load-step mechanism (the ramp configs use it). No harness or check change.
  - **Phases** (absolute s): baseline 300–900; burst 900–1080; watch 1080–5580; drop 5580–7380 at λ = 1; return 7380–8880 at λ = 2.2.
  - **Judged windows:** `verdict.end_s` is 600 in the resolved config, so condition 5 is judged on the end window 4980–5580, with the previous window 4380–4980 for the recovery signs. Condition 6 is judged on 8280–8880. The test checks these windows against the config (review recommendation 6).
  - **No separate control** ([CORR] 2026-11-10, above): REG-14's control used another schedule. The burst draw also depends on the seed: 440 burst requests here, against REG-14's 463. **The return phase is the in-run check that the warm server carries this schedule at λ = 2.2.**
- **Seed rule** (`gate.reg15_seed_rule`, `gate.reg15_judged_windows`; DERIVED from `build_schedule`): the lowest seed in 1–30 whose four judged windows (baseline, previous, end, return's end) all have planned λp within ± 5 % of 2.2 (`REG15["window_tol"]`). Of 30 seeds **only seed 12 qualifies**. The rule and its 5 % tolerance were written after the review and after seeing seed 2's windows, before any run of this design. The tolerance judges no result, only the choice of schedule.

  | judged window | seed 12 λp | seed 2 λp (first draft) |
  |---|---|---|
  | baseline 300–900 | 2.260 | 2.345 |
  | previous 4380–4980 | 2.165 | 2.133 |
  | end 4980–5580 | **2.155** | **2.442** |
  | return's end 8280–8880 | **2.237** | **2.208** |

  - Highest 120 s window inside the end window: 2.567. Inside the return's end: 2.942. The heavier peak is on the side judged `recovered`, which biases the run against `confirms`.
- **Design inputs** (DERIVED, `uv run python -m analysis.gate reg15_inputs`, `gate.reg15_inputs`, from the config alone):
  - 17373 session requests and 440 burst requests.
  - Planned session rate λp by phase: watch 2.124, drop 1.153, return 2.252.
  - **The drop is not exactly λ = 1 in the planned schedule** (round-2 review N1): λp is 1.052, 1.067 and **1.340** over its three 600 s windows. Sessions started before the drop still have turns planned in it, and the last window holds a surge. This makes `line_reached_zero` slightly harder to reach, and `drop_level` (over the drop's last 600 s, at 1.34) understates how warm the server gets at λ ≈ 1.
  - 120 s windows above 2.2 include 3.100 at 240–360 s (the baseline starts at 300 s), 3.058 at 4320–4440 s (just before and into the previous window), 2.875 at 7920 s and 2.942 at 8400 s (the return's end).
- **Result, computed once after the run is valid and copied:** `uv run python -m analysis.gate reg15` (`gate.reg15_table`, on the latest valid run of the pattern).
  - `gate.reg15_check` refuses a run that is not seed 12, λ = 2.2, closed loop, force_close and 350 W. `gate.reg15_phases` refuses one whose watch, drop and return are not this design.
  - **Condition 5:** `load.verdict` with `watch_s` 4500, judged on the windows above, with the thresholds of `configs/stage2_base.yaml` (unchanged).
  - **Persistence through the watch** (review T3, decisive): `gate.watch_broken` applies `recovered_against` to the baseline in each 300 s window from the burst's end to the watch's end. A window that passes breaks persistence. Each window's λp is reported, so a break on a dip in the schedule can be seen (round-2 N2; the watch's 300 s λp ranges 1.78–2.63). A break in the first window (1080–1380 s) would mean a delayed onset rather than a re-formed collapse (round-2 N3); it is still scored `reformed`, which works against `confirms`.
  - **Condition 6:**
    - `gate.line_reached_zero`: some scrape in the drop (5580–7380 s) shows 0 requests waiting;
    - `gate.recovered_against`: the return's end (8280–8880 s) passes `load.verdict`'s `recovered` test against the original baseline: pf ≥ base − 0.02, hit ≥ base − 0.06, waiting mean ≤ base + 1.
  - **`outcome`** (`gate.reg15_outcome`, in this order):
    - **`bad_baseline`**;
    - **`not_persistent`**: the watch ended `recovered` or `slow_drain`, so condition 5 fails;
    - **`inconclusive`**: `unclear`, or a needed value is missing;
    - **`reformed`**: `stuck` at the watch's end, but some 300 s window of the watch was `recovered`;
    - **`drop_inconclusive`**: the line never reached 0 in the drop (PROTOCOL §3);
    - **`no_return`**: the line reached 0, but the return's end is not `recovered`;
    - **`confirms`**: stuck through the whole watch, the line reached 0, and the return's end is `recovered`.
  - **Readouts, never decisive:**
    - the span test over the watch in 300 s spans (`gate.burst_backlog`, REG-8's settings);
    - condition 4's levels over the watch's last 1500 s: mean KV, mean N, N / baseline N, and max N against the 256 cap;
    - `drop_level`, `_level` over the drop's last 600 s (review recommendation 5): hit with the line near 0, which splits `no_return`;
    - `release_delay` at the end of the watch, of the drop and of the return;
    - the judged windows' λp, from the run's own requests (round-2 N5);
    - the baseline's pf and queue next to the outcome (round-2 N4: the 3.10 window at 240–360 s can loosen both `recovered` tests);
    - a 300 s timeline of pf, hit, queue, KV, N and λp over the whole run (`gate.reg15_timeline`).
- **Checks over a long run with load steps** (review T5):
  - `gpu_steady` computes one SM-clock CV over all busy samples. On past runs it was 0.011–0.016, against its 0.05 limit, including the open-loop ramps whose loads change from step to step: RUN(20261103-043121_ramp_d300, checks.json) 0.014; RUN(20261103-053730_ramp_d600, checks.json) 0.016; RUN(20261110-063647_burst_l1pl350cl_r2.2_s2, checks.json) 0.013; RUN(20261108-190906_long_pl350fc_pc_off_r3_s0, checks.json) 0.016. So the check is expected to be outcome-neutral here (BELIEF from those runs).
  - `recorder` (any gap over 2.0 s) is more exposed over 8880 s, but not differentially by outcome.
  - `arrival_rate`, `accounting` and `release_chain` use the step segments and the same deadline as loadgen (review: correct).
- **Prediction** (BELIEF):
  - The run valid p ≈ 0.75. It is 2.6 h, longer than any closed-loop run so far (open-questions A14).
  - The baseline healthy p ≈ 0.85, with the 3.10 window at its start.
  - The burst fills the pool p ≈ 0.85: 440 burst requests, against 463 in REG-14.
  - Given a valid run with a healthy baseline:
    - stuck at 4500 s with no recovered window, p ≈ 0.5;
    - the line reaches 0 in the drop, p ≈ 0.85;
    - the return `recovered`, p ≈ 0.6, since the return's end carries a 2.94 window.
  - So `confirms` ≈ 0.26 (DERIVED: 0.5 × 0.85 × 0.6), `not_persistent` ≈ 0.35, `reformed` ≈ 0.1, `no_return` ≈ 0.17, `drop_inconclusive` ≈ 0.08, other ≈ 0.04.
- **Decision under each outcome:**
  - **`confirms`:** C1's conditions 5 and 6 hold at λ = 2.2 in one run: two states at one load. The cold one lasted the whole 4500 s watch and left when the load dropped. Draft the confirmatory matrix at λ = 2.2 on seeds 3–7 (owner, decisions.md 2026-11-10 [DECISION]). C1's status changes only after the owner reviews the matrix's result (condition 3) and condition 4's readouts.
  - **`not_persistent`** or **`reformed`:** persistence is not shown at this cell. The cold state cleared on its own (the timeline says when), or cleared and came back. **The matrix is not drafted.** The owner chooses between another cell and reporting the cell as a long but transient cold state.
  - **`no_return`:** the server did not end healthy after the drop and return. `drop_level` and the timeline separate two readings:
    - the cold state never left during the drop (hit stayed low with the line near 0): not held by load, which goes against condition 6;
    - it left and came back on the return: a re-trigger by the 2.94 window.

    The owner decides; no matrix before that.
  - **`drop_inconclusive`:** reported; the owner decides (a longer drop).
  - **`bad_baseline`:** the server was unhealthy before the burst. A spontaneous collapse at λ = 2.2 would itself be news; the timeline shows it. Not rerun; the owner decides.
  - **`inconclusive`:** rerun unchanged, at most twice.
  - **Run invalid on `burst_min_kv_max`:** not rerun; the owner decides.
- **Alternatives:**
  1. **Load, not history** (review T2): the seed rule puts all four judged windows within ± 5 % of λ. The remaining load difference favors `recovered` at the return (peak 2.94 against 2.57 at the watch's end).
  2. **A collapse that ended and re-formed** (review T3): `reformed` catches it, using 300 s windows. A recovery shorter than one 300 s window is not caught; the timeline is reported.
  3. **A long transient read as `stuck`:** a queue that shrinks slowly counts as stuck only if it would not empty within 3600 s (`drain_horizon_s`). The timeline and the span test show the trend.
  4. **No separate control:** a cold state late in the watch could come from this schedule's own surges (3.06 at 4320 s), not from the burst. `watch_broken` requires it to run unbroken from the burst. The return shows that the warm server carries λ = 2.2 here.
  5. **Closed loop in the drop:** sessions lagging 4–6 minutes keep releasing turns planned before the drop, so the released load falls to λ = 1 only gradually. 1800 s is ≈ 5 × that lag. `release_delay` at the drop's end shows it.
  6. **A single 1 s scrape at 0 satisfies "the line reached 0"** (review T4): it matches PROTOCOL's wording, and the return's recovery stays decisive.
  7. **Heat and the recorder over 2.6 h:** see the checks above. One run, one seed, L1, 350 W, closed loop, dev mode.
- **Stopping rule:** the run once.
  - An invalid run (other than on `burst_min_kv_max`) is rerun unchanged, at most twice.
  - A heat-invalid run is rerun once, after cooling to ≤ 45 °C; a second heat failure stops.
  - A `client_error`, a limit other than 350 W or an unexpected pre-launch check stops.
  - A rerun decision reads only `checks.json`. No interim look at the verdict.
- **Operations:** REG-14's (pre-launch checks, a console log per attempt, reads in `docs/probe/20261110_reg15/`).
- **Cost:** 8880 s + up to 300 s drain + about 60 s start-up ≈ 2.6 GPU h (DERIVED: 9240 s); worst case with two reruns ≈ 7.7 GPU h.
- **Code and files:**
  - `configs/confirm_l1pl350cl_r2.2_s12.yaml`;
  - `analysis/gate.py`: `REG15`, `reg15_phases`, `line_reached_zero`, `recovered_against`, `reg15_outcome`, `watch_broken`, `reg15_timeline`, `reg15_check`, `reg15_judged_windows`, `reg15_seed_rule`, `reg15_table`, `reg15_inputs`; CLI `reg15`, `reg15_inputs`;
  - `tests/test_gate.py`, 8 new: the config against REG-14's and the judged windows from the config; `load.verdict` itself judging those windows (round-2 point 6); the phase check; the outcome classes including `reformed`; `line_reached_zero` and `recovered_against`; the run check; the seed rule; `watch_broken`.
- **Not changed:** REG-14's result and runs; the verdict thresholds; no harness or check change.

### Adversarial review (separate subagent; it saw only the draft, its diff, the code and configs those call, and PROTOCOL §3; it opened no runs and no other docs). Round 1, on the first draft (seed 2). Verbatim:

> ## REG-15 adversarial review (rule F)
>
> Scope: I read the draft, the diff, `analysis/gate.py`, `analysis/load.py`, `harness/{workload,loadgen,checks,config,run}.py`, the config chain and PROTOCOL §3. `tests/test_gate.py` passes (56/56). `reg15_inputs` gives the same numbers as the draft. I also computed λp for the windows the verdict actually judges (DERIVED, `build_schedule` on the resolved config, same method as `reg15_inputs`).
>
> ### 1. Traces where the outcome or the code is wrong
>
> **T1. The draft names the wrong judged window.** The resolved config has `verdict.end_s: 600` (`configs/stage2_base` via defaults). So `load.verdict` judges the end window **4980–5580 s** and the "previous" window **4380–4980 s** (`analysis/load.py:verdict`, `prev`/`end`). The draft says "end window 5280–5580 s" and quotes λp for the last 300 s (2.333). Neither is what gets judged. The judged windows have:
> - end window 4980–5580: λp **2.442**
> - previous window 4380–4980: λp **2.133**
> - return's end 8280–8880: λp **2.208**
> - baseline 300–900: λp **2.345**
>
> **T2. Condition 5 and condition 6 are confounded by planned load.** "Stuck at 5580" is judged on a window planned at 2.44, which contains the 2.983 surge at 5160 s. "Recovered at 8880" is judged on a window planned at 2.21. Trace: a server with no memory of the burst, whose warm closed-loop capacity sits near 2.4, falls behind in 4980–5580 because of the surge and is cleanly warm at 2.21. That gives v5 = `stuck` and back = True, so `confirms` (gate.py `reg15_outcome`). The two-states reading would then come from a 10.6 % difference in offered load, not from history (DERIVED: 2.442 / 2.208 = 1.106).
> - The slow_drain signs make this worse. They compare end with prev, and prev is lighter (2.13 against 2.44). A pf or hit climb is therefore less likely, which pushes `stuck` over `slow_drain`.
> - REG-13's warm capacity figure is something I could only see in a commit message ("2.4"), which is not evidence. The owner should check it in decisions.md.
>
> **T3. A collapse that ended and then re-formed still counts as persistent.** Trace: the cold state clears around 2500 s. The timeline shows `recovered` windows, and the span test shows `holds = False`. The 5160 s surge then tips the server cold again, and the end window is `stuck`. The result is `confirms`, because the span test and the timeline are "readouts, never decisive" (`reg15_table`). Condition 5 ("persistence") is then passed by a second collapse. The draft's alternative 2 names this risk, but no pre-registered rule acts on it.
>
> **T4. `line_reached_zero` passes on a single 1 s scrape with 0 waiting** (`gate.py:901–906`). This matches PROTOCOL's wording. But a single zero is weak evidence that the cold state left (hit can stay low with an empty queue). That gap matters only if the return's recovery is not itself decisive, and it is decisive. Low severity.
>
> **T5. Checks over an 8880 s run with load steps:**
> - **gpu_steady** (`checks.py:106–115`): one SM-clock CV over every busy sample from 240 to 8880 s, across stuck, λ = 1 and warm phases. At a 350 W cap, the clock depends on the load mix. The check has never been exercised on a closed-loop run with steps (the ramps were open loop).
>   - Possible trace: a healthy run fails on CV > 0.05 only because the phases differ.
>   - The failure is tied to the outcome: a run that stays stuck throughout has a uniform load and a low CV, while a `confirms`-shaped run mixes phases. That makes invalidation differential across outcomes.
> - **recorder** (`checks.py:91–96`): a single gap over 2.0 s in about 9000 scrapes invalidates the run. The risk grows with duration but does not depend on the outcome. Acceptable under the stopping rule.
> - **arrival_rate** (`checks.py:120–128`): `expected_requests` uses the segments with steps, and burst turn-0 requests are added. Correct.
> - **release_chain** and the **accounting** cut-off rule: the deadline is max t_planned + drain_s in both `loadgen` and `checks`, so they agree. Correct.
> - **client_lag**, **power_limit**: no step-specific issue.
> - I found no trace where a broken run is marked valid.
>
> **T6. The schedule is not REG-14's.** `_arrival_times` draws per segment, so changing `duration_s` reshuffles the whole first segment. The draft acknowledges this. The consequence is that this run has no warm reference at λ = 2.2 for the 4980–5580 window specifically.
>
> ### 2. Strongest alternative per outcome
> - **`confirms`:** overload in a heavy judged window (2.44, with a 2.98 surge) against a light return window (2.21), or a re-formed collapse (T3). What separates them: a no-burst control on this exact 8880 s schedule (its 4980–5580 window must be `recovered`), or a pre-registered decisive rule that the cold state stays unbroken through the watch.
> - **`not_persistent`:** a genuine transient, or a recovery made easier by the light previous window. The timeline separates these, together with λp per span.
> - **`no_return`:** a re-trigger on the return's 2.60 and 2.56 windows, or the cold state never left. Hit during the drop with the queue at 0 separates them, as the draft says.
> - **`drop_inconclusive`:** closed-loop lag still releasing turns planned before the drop. `release_delay` at the end of the drop separates this.
>
> ### 3. Can the run change a decision?
> Yes. `not_persistent`, `no_return` and `drop_inconclusive` each stop the matrix at this cell. That is a real, cheap kill test. `confirms` triggers drafting the matrix, but T2 and T3 mean it can be reached by artifact. So the run's power to *support* C1 is weaker than the draft implies; its power to *refute* it is intact.
>
> ### 4. Recommendations
> 1. **Blocking:** Correct the judged windows in the draft (end 4980–5580, previous 4380–4980) and report their λp (2.442, 2.133) beside the return's end (2.208) and the baseline (2.345).
> 2. **Blocking:** Pre-register a decisive guard against T2. Any one of these would do:
>    - a λp tolerance on the end window (e.g. |λp − λ| ≤ x), with the outcome `confounded` if it is exceeded;
>    - a different seed, or shifted steps, that puts the watch-end window near λ, chosen by a rule fixed before the run (as with REG-14's seed rule);
>    - a no-burst control on this schedule (+2.6 GPU h).
> 3. **Blocking:** Make persistence decisive against T3. For example, `confirms` requires no 300 s timeline window in the watch to be `recovered` (or requires the span test to hold in all spans after the first k). Otherwise call the outcome `reformed`.
> 4. **Non-blocking:** Before approval, have the owner read `busy_sm_clock_cv` in past checks.json files (ramps, REG-14) to judge the gpu_steady risk on a mixed-load run. State in the registration whether the check is expected to be outcome-neutral.
> 5. **Non-blocking:** Add `drop_level` to the output: `_level` over the drop's last 600 s (hit with the line at 0). It is already needed to split `no_return`, so it should not be left to the timeline's reading.
> 6. **Non-blocking:** Add a test that `reg15_table`'s verdict uses `end_s` from the config, so the registration and code cannot drift on the window again.

### Round 2, on the revised draft (seed 12, the owner's choice). Verbatim:

> ## REG-15 review, round 2 (seed 12)
>
> No blocking item remains. I reran the gate tests (58/58 pass) and confirmed `reg15_seed_rule()`: it picks 12, and 12 is the only seed in 1–30 that qualifies. Its judged windows are baseline 2.260, previous 2.165, end 2.155 and return's end 2.237 (DERIVED, `reg15_judged_windows(12)`).
>
> ### (1) Status of recommendations 1–6
> 1. **Wrong judged windows: addressed.** The draft now gives 4980–5580 (end) and 4380–4980 (previous), with their λp.
> 2. **Planned-load confound (T2): addressed.** The seed rule fixes it on design inputs alone, before any run. The highest 120 s peak now sits on the side judged `recovered` (2.94 at the return's end against 2.57 at the watch's end), which works against `confirms`, as the draft says.
>    - The 5 % tolerance was set after seeing seed 2. It lets exactly one seed through and judges no result, so it does not break rule A5. The draft should still say plainly that the tolerance was chosen at that moment.
> 3. **Collapse that re-forms (T3): addressed.** `watch_broken` is decisive and `reformed` stops the matrix (gate.py, diff lines 83–89 and 72–73).
> 4. **gpu_steady risk: addressed, but not verified by me.** The draft cites CVs of 0.011–0.016 from four runs' checks.json. I was not allowed to open runs/, so I could not check them.
> 5. **`drop_level`: addressed** (diff line 130).
> 6. **Window test: partly addressed.** `test_reg15_config_is_reg14s…` checks the windows of `reg15_judged_windows`, which is a separate copy of `load.verdict`'s window arithmetic. No test checks that `verdict()` itself judges 4980–5580 on a run at this config, so the two copies could drift apart unnoticed. A small fake-metrics test calling `verdict` would close this.
>
> ### (2) New traces
> - **N1. The drop is not λ = 1 in the planned schedule.** Seed 12's session starts in the drop come to 1.142 req/s, and planned λp per 600 s is 1.052, 1.067 and **1.340** (6780–7380) (DERIVED, `build_schedule`; seed 2 had 0.94 overall). The seed rule never constrained the drop.
>   - Effect: `line_reached_zero` (diff line 36) is a little harder to reach, which pushes towards `drop_inconclusive`.
>   - `drop_level` is measured over the 1.34 window, so it understates how warm the server got at λ ≈ 1. That weakens the split it is meant to give for `no_return`.
>   - This is not decisive, but the draft quotes a drop λp of 1.153 without saying it falls short of PROTOCOL's "drops to 1 req/s".
> - **N2. Light watch windows tilt the persistence test.** The watch's 300 s λp ranges from 1.78 to 2.63, with 1.867 and 1.783 at 3180–3780. `watch_broken` can therefore break on a dip in the schedule. That is arguably a true break (the load dipped and the server re-warmed, which is condition 6's logic), and it biases against `confirms`, not towards it. Report the λp of any breaking window in the result.
> - **N3. A slow-onset collapse could read as `reformed`.** With a smaller burst (440 against 463), the first window 1080–1380 could pass `recovered` (it needs q ≤ base q + 1) before the backlog builds. Persistence would then be scored as broken although there was a single delayed collapse. This is unlikely, since the pool is full at the burst's end and the backlog shows at once, and it is conservative. Non-blocking: say in the draft that a break in the first window means delayed onset, not re-formation.
> - **N4. The baseline surge loosens both `recovered` tests.** The window 240–360 peaks at 3.10, and the first baseline half runs at 2.39. If that raises the baseline's q or lowers its pf, both `recovered_against` tests become easier (`watch_broken` and the return). The effects run in opposite directions for `confirms`. Readout only: report the baseline's q and pf next to the outcome.
> - **N5. Minor code issue.** `reg15_table` gets `judged_lam_p` from `reg15_judged_windows(seed)` (diff line 131). That function rebuilds the schedule from the repo config, not the run's own config.yaml, so this readout comes from a different source than the rest of the table. It is not decisive.
> - I found no new trace where the outcome code (`reg15_outcome`, `watch_broken`, `recovered_against`) returns a wrong class for its inputs. The ordering bad_baseline → not_persistent → inconclusive → reformed → drop → return is consistent with PROTOCOL §3.
>
> ### (3) Remaining blocking items
> None. These are non-blocking but worth doing before approval:
> - the `verdict()` window test (point 6);
> - stating the drop's realized λp, 1.15 rising to 1.34 at the end (N1);
> - the note on a first-window break (N3).
>
> The run can still change a decision. `not_persistent`, `reformed`, `no_return` and `drop_inconclusive` each stop the matrix at this cell. `confirms` is no longer reachable through the planned-load confound.

### Changed because of it
- **Round 1:**
  - 1: adopted; the windows are corrected.
  - 2: put to the owner, who chose seed 12 by the judged-window rule (`reg15_seed_rule`).
  - 3: adopted; `watch_broken` makes persistence decisive, and the outcome is `reformed` when it breaks.
  - 4: adopted. The agent read `busy_sm_clock_cv` in four runs' `checks.json` (cited above with their run ids).
  - 5: adopted; `drop_level` is reported.
  - 6: adopted; the test is in round 2's point 6.
  - REG-13's warm capacity is in decisions.md 2026-11-10 [RESULT] REG-13: μ = 2.4 by the configs' rule, with a ratio of 0.950.
- **Round 2:**
  - point 6: adopted; `test_load_verdict_judges_reg15s_windows_from_the_config` calls `load.verdict` itself.
  - The tolerance's timing is now stated (point 2).
  - N1: the drop's λp by 600 s window (1.052, 1.067, 1.340) is in the design inputs (`reg15_inputs` `drop_by_600`).
  - N2: `watch_broken` reports each window's λp.
  - N3: the note on a first-window break is in the draft.
  - N4: the baseline's pf and queue are reported next to the outcome.
  - N5: `judged_lam_p` is now computed from the run's own requests.

## 2026-11-10 · [DECISION] Owner approves REG-15 and its run
- **Owner's answer:** "approved", to the question whether REG-15 (decisions.md 2026-11-10 [REG]) is approved: C1's confirmation run at λ = 2.2 with closed-loop turns, seed 12, a 4500 s watch, then λ = 1 for 1800 s, then 2.2 for 1500 s, ≈ 2.6 GPU h.
- **Run:** `configs/confirm_l1pl350cl_r2.2_s12.yaml` after REG-14's pre-launch checks, reads in `docs/probe/20261110_reg15/`, VM console log named per attempt. Research rule 2 relaxed for this run as for REG-11 to REG-14.
- **Standing instructions** (decisions.md 2026-11-09 [DECISION]) and REG-15's stopping rule apply; a rerun decision reads only `checks.json`. No look at the verdict before the run is valid and copied; then `gate.reg15_table` once, the `[RESULT]`, and the next draft by the registered outcome, which does not run before the owner approves it.

## 2026-11-10 · [OPS] REG-15 run: valid on the first attempt, no rerun; pre-launch read in `docs/probe/20261110_reg15/`
- **Run** `20261110-085730_confirm_l1pl350cl_r2.2_s12`: launched 08:57:28 UTC at 350.00 W, 42 °C, 0 % busy, no compute process, VM tree `3c30215` clean, 9.9 GB free (PROBE(docs/probe/20261110_reg15/prelaunch_reg15_attempt1.txt)). Valid, `failed` empty, all 12 checks passed, including `trigger` (the burst filled the pool) and `power_limit` (RUN(20261110-085730_confirm_l1pl350cl_r2.2_s12, checks.json)). sw_thermal 0.000, max 75 °C, busy SM-clock CV 0.009, limit 350.0 W over 9185 samples.
- Console log on the VM: `~/confirm_l1pl350cl_r2.2_s12_20261110T085727Z.log`. Copied to the Mac, sha256 identical (10 files); `manifests/runs.sha256` +10 lines. VM copy kept.

## 2026-11-10 · [RESULT] REG-15: `drop_inconclusive`. Stuck through the whole 4500 s watch with no recovered window (condition 5 holds), but the queue never reached 0 in the 1800 s drop, so condition 6 is untested
- **Computed once:** `uv run python -m analysis.gate reg15` (`gate.reg15_table`) on `20261110-085730_confirm_l1pl350cl_r2.2_s12`; values RUN(20261110-085730_confirm_l1pl350cl_r2.2_s12, gate.reg15_table) unless tagged otherwise.
- **Baseline** (300–900 s): pf 0.984, hit 0.835, queue 0.007, KV 0.199, 6.1 running, at λp 2.26 from the run's own requests.
- **Condition 5:** `load.verdict` of the 4500 s watch is **`stuck`**. End window (4980–5580 s): pf 0.000, hit 0.000, queue 399.7, KV 0.949, 30.1 running. **`watch_broken` false:** none of the 15 windows of 300 s from 1080 to 5580 s passes `recovered` against the baseline (window λp 1.78–2.63).
- **Condition 6:** **`line_reached_zero` false**. No scrape in 5580–7380 s shows 0 waiting. `return_recovered` false (return's end: pf 0.000, hit 0.000, queue 351.8, KV 0.950); it is not decisive here, because the outcome order stops at `drop_inconclusive`.
- **Timeline** (300 s windows, `gate.reg15_timeline`; t in s):

  | phase | t | λp | hit | waiting q mean | KV |
  |---|---|---|---|---|---|
  | baseline | 600–900 | 2.13 | 0.838 | 0.007 | 0.175 |
  | burst | 900–1200 | 1.92 | 0.017 | 130 | 0.937 |
  | watch | 1500–1800 | 2.41 | 0.000 | 116 | 0.949 |
  | watch | 3000–3300 | 2.13 | 0.000 | 227 | 0.952 |
  | watch | 5100–5400 | 2.08 | 0.000 | 399 | 0.950 |
  | drop | 5700–6000 | 1.00 | 0.000 | 411 | 0.951 |
  | drop | 6300–6600 | 1.15 | 0.000 | 363 | 0.950 |
  | drop | 6900–7200 | 1.38 | 0.000 | 309 | 0.949 |
  | drop → return | 7200–7500 | 1.65 | 0.000 | 265 | 0.950 |
  | return | 8400–8700 | 2.61 | 0.000 | 346 | 0.953 |

  - Every 300 s window from 1200 s to the end has hit 0.000 and KV 0.947–0.955. Within each watch window the queue's slope was positive (q_slope +0.02 to +0.21 /s); within each drop window it was negative (−0.06 to −0.12 /s).
- **Readouts:**
  - **Span test** over the watch (15 spans of 300 s): c 1.72–1.90; it holds in 11 of 15. The 4 that fail are spans whose λp (1.78–2.07) is under c_upper (1.92–2.09).
  - **Condition 4** (watch's last 1500 s): KV 0.949, N 30.3 (4.93 × baseline), max N 34 against the 256 cap.
  - **`drop_level`** (6780–7380 s): pf 0, hit 0, queue 301.5, q_slope −0.127 /s, KV 0.950, N 28.4.
  - **`release_delay`** at the end of the watch, the drop and the return: 856, 930, 719 s.
  - **Judged windows' λp** from the run's own requests: baseline 2.260, previous 2.165, end 2.155, return's end 2.237. All are within ± 5 % of 2.2, as the seed rule planned.
- **Prediction** (model.md row 19):
  - valid: hit (0.75);
  - baseline healthy: hit (0.85);
  - the burst fills the pool: hit (0.85);
  - stuck through the watch with no recovered window: hit (0.5);
  - the line reaches 0: **miss** (0.85);
  - `drop_inconclusive` had 0.08.
- **Alternatives:**
  1. **The drop was too short for the backlog** (design): at the drop's start the server held ≈ 410 waiting (above), and the clients lagged 856–930 s. The queue fell in every drop window at 0.06–0.13 /s, so it was draining, not held. A linear extrapolation of the last drop window (301.5 / 0.127 ≈ 2370 s more, DERIVED; BELIEF that the fall stays linear) puts the empty line ≈ 40 min past the drop's end. A longer drop separates this from 2.
  2. **A cold state that the load does not hold** (against condition 6's reading): hit stayed 0.000 through the drop, but with ≥ 265 requests still waiting and KV at 0.95 the pool was still full of backlog. The data cannot tell a cache that would warm once the line empties from one that would not. Only a drop in which the line reaches 0 separates them.
  3. **Persistence by overload rather than history:** this run has no same-schedule control (REG-15, "No separate control"), and the return, its in-run check, never ran warm. Against it: the baseline carried λp 2.26 at pf 0.984 with an empty queue, and REG-14's control carried λ = 2.2 on another schedule (decisions.md 2026-11-10 [RESULT] REG-14). Evidence for a persistence that overload does not explain, not proof.
  4. **Heat or clock:** sw_thermal 0.000, max 75 °C, CV 0.009 (OPS above). Not a factor.
- **What this is:** condition 5 at one load, in one run. The cold state that REG-14 held for 1500 s held here for 4500 s, unbroken, with a queue that grew from 116 to 399. Condition 6 (it leaves when the load drops) is untested, not failed. Not C1.
- **Registered decision (`drop_inconclusive`):** reported; the owner decides (a longer drop). **The matrix is not drafted.** Nothing runs before the owner chooses and approves a new registration.
- **Not changed:** claims.md, REG-11–14's results, code, thresholds.

## 2026-11-10 · [CORR] REG-15's registration assumed a 4–6 minute client lag in the drop; the lag had grown to 14–16 minutes
- REG-15's alternative 5 (decisions.md 2026-11-10 [REG]) said sessions lag 4–6 minutes and that the 1800 s drop is ≈ 5 × that lag. The figure came from REG-14's 1500 s watch (release_delay 234–356 s). Over a 4500 s watch the backlog keeps growing, and so does the lag. Measured: 856 s at the watch's end and 930 s at the drop's end (RUN(20261110-085730_confirm_l1pl350cl_r2.2_s12, gate.reg15_table)), so the drop was ≈ 1.9 × the lag (DERIVED: 1800 / 930).
- I carried a value measured over a short watch into a design three times longer without checking how it scales. The registered outcome order already handled the case (`drop_inconclusive`), so no result changes. A new drop length must come from this run's drain (alternative 1 of the result above), not from REG-14.

## 2026-11-10 · [CORR] REG-15's write-up: the check that shows the burst filled the pool is `manipulation`, not `trigger`; and the drop's received load was 1.58 req/s, not ≈ 1
- Found by the reviewer session, on the owner's request; checked here against the run.
- **Wrong check named.** The REG-15 [OPS] entry says `trigger` shows the burst filled the pool. `trigger` only counts burst requests sent (440 of 440). The pool check is `manipulation`: KV max during the burst 1.0 against a minimum of 0.95 (RUN(20261110-085730_confirm_l1pl350cl_r2.2_s12, checks.json)). The run's validity does not change.
- **The drop was not a drop to λ ≈ 1 at the server.** Session requests released per second (`gate.release_rate`, RUN(20261110-085730_confirm_l1pl350cl_r2.2_s12, gate.release_rate)): 1.803 over the watch (1080–5580 s) and **1.582 over the drop** (5580–7380 s), by thirds 1.650, 1.568, 1.527. Under closed loop, sessions kept releasing turns planned before the drop. The result table's λp column (planned rate, 1.00–1.38 in the drop) is correct as defined, but the model.md M2 note's "the 1800 s drop to λ ≈ 1" is wrong. The released load was ≈ 1.6.
- **The drain estimate in the result's alternative 1 used the server queue only.** It ignored turns owed by the clients but not yet released, so it understates how long a drop must be. A new drop length must come from the total backlog (server waiting plus turns not yet released), computed by a committed function.
- No outcome changes: `drop_inconclusive` stands.

## 2026-11-10 · [REG] REG-16 (draft): a no-burst control at λ = 2.2 on the exact schedule of a later confirmation run with a 9000 s drop (seed 14; GPU, ≈ 4.5 h)
- **ID:** REG-16. **Confirmatory for one condition at one load:** does the warm state at λ = 2.2 (closed-loop turns, L1, 350 W) last without a burst for as long as the confirmation run watches? The owner pre-approved it on 2026-11-10, before its final text and before any run (decisions.md [DECISION] below).
- **Why:**
  - REG-15 gave `drop_inconclusive` (decisions.md 2026-11-10 [RESULT] REG-15): stuck through 4500 s, but the line never emptied in the 1800 s drop.
  - The reviewer session pointed out (2026-11-10, on the owner's request) that recovery after a drop does not separate a metastable state from overload, because both predict it. Only a same-schedule control without a burst that stays warm does.
  - No run at λ = 2.2 without a burst has been watched for more than 1500 s (REG-14's control). The reviewer also reported an exploratory onset check (its scratch script, not provenance): seed 5's 2.4 control and REG-13's 2.6 run went cold after short surges (120 s λp ≈ 3.4–4.3) with no burst.
  - The owner agreed (2026-11-10, "alright") to draft the control first. It is the cheaper step that can stop the plan at λ = 2.2. The burst run on the same schedule (REG-17) is registered only after this result.
- **Question:** on REG-17's session schedule at λ = 2.2, without a burst, does the server stay warm for the whole run? That covers the burst run's watch window (1080–5580 s), the drop to λ = 1 (5580–14580 s) and the return to 2.2 (14580–16080 s).
- **Setup:** `configs/stage2_control_l1pl350cl_r2.2_long_s14.yaml`: `extends: stage2_control_l1pl350cl_r2.2_s2.yaml` (REG-14's control), with `seed: 14`, `workload.duration_s: 16080`, `workload.steps: [{at_s: 5580, rate: 1}, {at_s: 14580, rate: 2.2}]` and `verdict.watch_s: 4500`.
  - Resolved, it differs from REG-14's control only in `name`, `seed`, `workload.duration_s`, `workload.steps` and `verdict.watch_s` (test `test_reg16_control_is_reg14s_control_with_reg17s_schedule`).
  - So: L1, 350 W check, closed-loop turns, force_close, dev mode, no trigger, `control_t_s` 1080.
  - **REG-17's config is written now**, unregistered: `configs/confirm_l1pl350cl_r2.2_long_s14.yaml`. It is REG-15's config with seed 14 and the same duration and steps. The test checks that its 24927 session requests equal the control's row for row (`t_planned`, session, turn, prompt length); the burst draws from its own generator.
  - **A shorter control cannot share the schedule.** `harness/workload.py` `_arrival_times` draws every segment from one generator, and the session contents and gaps come after it. So changing `duration_s` or a step changes every later draw. The control must run the full 16080 s.
  - **Phases** (absolute s): the burst run's baseline 300–900; watch 1080–5580; drop 5580–14580 at λ = 1; return 14580–16080 at 2.2; return's end 15480–16080.
  - **Baseline window:** 300–900 s for both runs (`REG16["baseline"]`). `load.verdict` on a control uses `control_t_s` 1080, so its own baseline is 480–1080, where this schedule plans λp 2.430 against 2.210 in 300–900. The cold windows and the return test use 300–900, so the control and REG-17 are judged against the same window. `load.verdict` is still used for the watch's verdict, with its own baseline.
- **Drop length and seed rule** (`gate.reg16_seed_rule`, `gate.reg16_calibration`, `gate.reg16_empty_time`; DERIVED, no run of this design). Following the reviewer's suggestion, the drop is sized from the total owed backlog, not from the server queue.
  - **Owed backlog** (`gate.owed_backlog`): requests planned before t and not completed by t, which covers server waiting and running plus turns not yet released.
  - **Calibration** on REG-15's run (RUN(20261110-085730_confirm_l1pl350cl_r2.2_s12, gate.reg16_calibration)): owed 28 at the trigger, 2149 at the watch's end, 1215 at the drop's end. Completions 1.758 req/s over 900–5580 s and 1.672 over the drop. Lowest 600 s rate: 1.728 in the watch, 1.637 in the drop. Released rate in the drop 1.582.
  - REG-15's completion rate fell through the run, from 1.817 in the first 600 s after the burst to 1.637 at the end of the drop (`gate.completion_rate`, 600 s windows from 1080 s; review T3). One possible reason is that late turns carry longer prompts and are served cold (BELIEF).
  - **Prediction model:** owed at the trigger, plus every request this schedule plans after it, minus completions at REG-15's cold rates per phase. It predicts when the owed backlog reaches 0 in the drop.
  - **Pessimistic version** (review T3): REG-15's lowest 600 s rate in each phase, lowered by `c_pessimism` 0.05, the spread of c_b across REG-11/12/14 (1.784–1.83, decisions.md [RESULT] REG-11, REG-12, REG-14). So 1.678 in the watch and 1.587 in the drop, 0.08 and 0.085 below REG-15's means.
  - **Rule:** take the shortest drop in (5400, 7200, 9000) s, and within it the lowest seed among 1–30 excluding 3–7. The seed must satisfy two conditions:
    1. its four judged windows (baseline 300–900, the verdict's previous and end windows 4380–4980 and 4980–5580, the return's last 600 s) all have λp within ± 5 % of 2.2, as in REG-15's rule;
    2. its pessimistic empty time plus `warm_watch_s` 1200 s fits in the drop.

    Seeds 3–7 are kept for the matrix (owner, decisions.md 2026-11-10 [DECISION]).
  - **The rule picks drop 7200 s, seed 14.** At 5400 s no seed passes both conditions. Seeds 14 and 24 pass the windows, but seed 14's pessimistic line never empties in the drop, and seed 24's empties at 5120 s, leaving less than 1200 s.
  - **Seed 14 at 7200 s:** judged λp 2.202, 2.290, 2.150 and 2.255. Predicted empty 4230 s into the drop, which leaves 2970 s to watch the cache; pessimistic 5580 s, which leaves 1620 s.
  - **Only seeds 14 and 24 pass at 7200 s.** Seed 24's pessimistic empty time is 4830 s, which leaves more room (review N5: the lowest-seed rule picks the seed with less room).
  - **Chosen: seed 14 with a 9000 s drop** (review round 2, N1; the owner left the choice to the agent, decisions.md [DECISION] below). Three designs were compared on their schedules alone (DERIVED, `gate.reg16_burst_cfg`, `gate.reg16_judged_windows`, `gate.reg16_empty_time`):

    | design | watch λp | watch peak 120 s | judged λp | empty (pessimistic) | room left |
    |---|---|---|---|---|---|
    | seed 14, 7200 s | 2.223 | 3.217 | 2.202 / 2.290 / 2.150 / 2.255 | 4230 (5580) s | 1620 s |
    | seed 24, 7200 s | 2.180 | 3.000 | 2.207 / 2.105 / 2.305 / 2.175 | 3640 (4830) s | 2370 s |
    | seed 14, 9000 s | 2.225 | 3.217 | 2.210 / 2.288 / 2.127 / 2.222 | 4340 (5540) s | 3460 s |

    Seed 24 carries a lighter watch, which would favour `control_warm` (review N5). Seed 14 at 9000 s keeps the rule's seed and the same watch load, with all four judged windows within ± 5 %, and leaves the most room, for ≈ 0.5 GPU h more per run. "Room left" is the drop minus the pessimistic empty time; the judged window needs 1200 s of it.
  - Across the 25 seeds at 7200 s, the predicted empty time ranges 2700–5070 s (pessimistic 3580–6230 s). The schedule alone moves it by tens of minutes, as the reviewer said.
  - The rule, its candidates, `c_pessimism` and the lowest-600 s start were written after REG-15's result, the reviewer's note and this review's round 1, before any run of this design. They judge no result, only the choice of drop and seed. The 9000 s choice was made on margin and load alone, before any run.
- **Design inputs** (DERIVED, `uv run python -m analysis.gate reg16_inputs`, `gate.reg16_inputs`, from the configs alone): 24927 session requests. Planned λp: 2.210 in the baseline (300–900), 2.225 over the watch, 1.021 over the drop, 2.115 over the return, 2.222 at the return's end. Highest 120 s λp: 2.917 in the baseline, 3.217 in the watch, 1.517 in the drop, 2.850 in the return. 120 s windows above 3.0: 1 in the watch, 0 in the return. Predicted empty 4340 s into the drop, pessimistic 5540 s.
- **Result, computed once after the run is valid and copied:** `uv run python -m analysis.gate reg16` (`gate.reg16_table`, on the latest valid run of `*_stage2_control_l1pl350cl_r2.2_long_s14`).
  - `gate.reg16_check` refuses a run whose config differs from the registered file on any key the file sets, or that has any trigger (review N6). That pins seed 14, λ, closed loop, force_close, 350 W and the steps.
  - `gate.reg16_phases` refuses another design.
  - **Cold window** (`gate.cold_windows`): a 300 s window from 1080 s to the run's end is cold when both conditions hold against the baseline, at `load.verdict`'s stuck levels (`stuck_hit_drop`, `stuck_pf_drop`, `configs/stage2_base.yaml`, unchanged; no new threshold):
    - the hit share by scrape time is ≤ base − 0.06;
    - the percent fast of requests **sent** in the window (`gate.pf_by_sent`) is ≤ base − 0.10.

    Review T2: under closed loop a request is served near its send time, up to 15 min after its planned time. `_level`'s pf by planned time would put a collapse's slow requests in earlier windows than its low hit.
  - **Low hit with a queue** (`hit_low_queued`, review T2): hit ≤ base − 0.06 with a waiting mean above base + 1 (`recovered_q_excess`), whatever pf says.
  - **Persistent** (`gate.cold_persistent`, review T1 and round 2, T1): true if either holds:
    - a cold window is the last window of its phase (watch 5580, drop 14580 or return 16080 s), i.e. still cold when the phase ends;
    - a stretch of consecutive cold windows lasts `persistent_s` 1500 s or more: the study's watch window, max(1200 s, 5τ) (docs/definitions.md "watch window"). It was set before the run, not from its data.

    A phase's last window that is missing right after a cold window gives `inconclusive`. `gate.longest_cold_s` reports the longest stretch.
  - **`outcome`** (`gate.reg16_control_outcome`, in this order):
    - **`bad_baseline`:** the baseline's pf < `min_baseline_pf` 0.98, or the watch verdict is `bad_baseline` on its own 480–1080 s baseline. The schedule fixes that window, so a rerun would not change it (review N3);
    - **`inconclusive`:** the baseline pf is missing;
    - **`control_cold_persistent`:** persistent (above), or the watch verdict is `stuck`;
    - **`inconclusive`:** a phase's last window is missing right after a cold window;
    - **`control_cold_transient`:** some window is cold, but every cold stretch ended inside its phase and lasted less than 1500 s;
    - **`inconclusive`:** any other missing value (a window, the return's end), or the watch verdict is `unclear`;
    - **`control_unclear`:** never cold, but some window has a low hit with a queue;
    - **`control_not_recovered`:** the watch verdict is not `recovered`, or the return's end fails `recovered_against` the baseline (a queue, not the cache);
    - **`control_warm`:** never cold, no low hit with a queue, the watch `recovered`, and the return's end `recovered`.

    A cold window decides even if another value is missing.
  - **Readouts, never decisive:**
    - the first cold window, its phase, and the highest 120 s λp in the 600 s before it; the longest cold stretch;
    - per window (`gate.window_mix`, round 2, T3 and N2): requests planned in it and never sent, which `pf_by_sent` cannot count, and the first-turn share of the requests sent. The first return window may queue briefly from new first turns and give `control_unclear` on a healthy server; this readout shows it;
    - both baselines: 300–900 s (judged) and `load.verdict`'s own 480–1080 s. Review N4: 300–900 s sits about 0.005 below the later warm hit in REG-14's control, a small bias towards `control_warm`;
    - the end levels;
    - the 300 s timeline of pf, hit, queue, KV, N and λp (`gate.reg15_timeline`).
  - **Check of the code on past runs** (exploratory, not a result): against the 300–900 s baseline, `cold_windows` marks all 15 watch windows of REG-15's run cold and low-hit-with-queue. It marks none of the 5 watch windows of REG-14's control (1080–2580 s).
- **Prediction** (BELIEF):
  - The run valid p ≈ 0.7. At 16080 s it is the longest run of the study, so the recorder and heat have more chances to fail (open-questions A14).
  - The baseline healthy p ≈ 0.9.
  - Given a valid run with a healthy baseline:
    - `control_warm` ≈ 0.5;
    - `control_cold_persistent` ≈ 0.2: REG-13 put the closed-loop warm capacity near 2.4, and the reviewer saw no-burst collapses after surges of 3.4–4.3; this schedule peaks at 3.22;
    - `control_cold_transient` ≈ 0.1;
    - `control_unclear` or `control_not_recovered` ≈ 0.15;
    - `inconclusive` ≈ 0.05.
- **Decision under each outcome:**
  - **`control_warm`:** the warm state lasts on this schedule without a burst, in one run (0 cold of 1). Per rule H the one-sided 95 % upper bound on the chance of a cold episode per 4.5 h run is 0.95 (review N7). This permits REG-17; it does not show that spontaneous collapse is rare. Draft REG-17, the burst run on `configs/confirm_l1pl350cl_r2.2_long_s14.yaml`, with the outcome rules below. Together the pair separates a burst-made cold state from overload: REG-16 warm and REG-17 stuck through the watch (round 2, T2). Nothing runs before the owner approves REG-17.
  - **`control_cold_persistent`:** the warm state does not last at λ = 2.2 on this schedule. REG-14's and REG-15's cold states are then not separated from a spontaneous collapse over long horizons. **No REG-17 and no matrix at 2.2.** The owner chooses: a lower λ, or reporting λ = 2.2 as a load where the warm state is not stable. The first cold window's phase and its preceding peak are reported.
  - **`control_cold_transient`:** the server went cold without a burst but came back by itself within its phase (review T1). That shows the warm state pulls back, which is not the collapse REG-15 would be confused with, but REG-15's cold state did not pull back. Reported; the owner decides whether REG-17 goes ahead. It does not stop REG-17 by itself.
  - **`control_unclear`** or **`control_not_recovered`:** reported; the owner decides. No REG-17 before that.
  - **`bad_baseline`:** not rerun; the owner decides.
  - **`inconclusive`:** rerun unchanged, at most twice.
- **REG-17's planned outcome rules** (reviewer point 3), written now so this review can check them; they are reviewed again when REG-17 is registered:
  - REG-15's order: `bad_baseline` → `not_persistent` → `inconclusive` → `reformed` → `drop_inconclusive` → ….
  - **t0** = the first of 3 consecutive scrapes in the drop with 0 waiting (review T5: a single momentary 0 near the end of the drain would set t0 early). The owed backlog at t0 and at t0 + 600 s is reported. Even a healthy run owes about 28 (running plus normal lag), so the drain model aims slightly late.
  - **Judged window** [t0 + 600, t0 + 1200) s. If it does not end inside the drop: `drop_inconclusive`.
  - **Reference: REG-16's control in the same absolute window** (review T4), not the baseline. At λ = 1, new sessions rebuild their own prefixes within about one session lifetime (8 turns × 20 s). So hit ≥ base − 0.06 would be close to automatic for a trigger-made cold state and for plain overload alike.
  - In that window: **`warmed`** if REG-17's hit ≥ the control's hit − 0.06 (`recovered_hit_drop`); **`cold_after_empty`** if it is lower; **`inconclusive`** if either hit is NaN.
  - **`warmed` is consistent with both hypotheses** (round 2, T2). New sessions at λ = 1 rebuild prefixes within about 140 s, so a burst-made cold state and plain overload both warm up once the line clears. The separating evidence is the pair: REG-16 `control_warm` with REG-17 stuck through the watch. The drop checks only C1's recovery condition.
  - After `warmed`: `confirms` if the return's end is `recovered_against` the baseline, else `no_return`.
  - `cold_after_empty`: the cold state outlives its load. Reported; the owner decides. No matrix before that.
  - Closed-loop sessions have a 20 s mean gap between turns (`configs/base.yaml` `turn_gap_s`). A working cache should show hits within a minute or two once the line is empty (BELIEF).
- **Alternatives:**
  1. **A cold control from one surge, not from the load level:** `control_cold_transient` if it pulls back within its phase, `control_cold_persistent` if not. The readout of the peak before the first cold window shows the surge.
  2. **Warm for this run, cold for a longer one:** the control covers exactly the burst run's horizon, nothing longer.
  3. **The drain model is fitted on one run** (REG-15, seed 12). The pessimistic rates start from REG-15's lowest 600 s rates. If the decline continues well below 1.587 in the drop, the line may still not empty in time, and REG-17 is `drop_inconclusive` again. With the 9000 s drop leaving 3460 s in the pessimistic case, the prediction for REG-17 is ≈ 0.15 (BELIEF). This is decided now because the drop length fixes the control's schedule (review T3).
  4. **Baseline window:** 300–900 s rather than the control's own 480–1080 s at λp 2.47. A heavier window would give a higher pf and hit reference; the cold test's two-part, 0.06/0.10 margins make this matter only at the edge. Both baselines are reported.
  5. **Heat and the recorder over 4.5 h:** the automatic checks judge it; sw_thermal was 0.000 over REG-15's 2.5 h.
  6. One run, one seed, L1, 350 W, closed loop, dev mode.
- **Cost:** 16080 s ≈ 4.5 GPU h plus start-up. REG-17, if drafted, is another ≈ 4.5 h.
- **Stopping rule:** the run once.
  - An invalid run is rerun unchanged, at most twice.
  - A heat-invalid run is rerun once, after cooling to ≤ 45 °C; a second heat failure stops.
  - A `client_error`, a limit other than 350 W or an unexpected pre-launch check stops.
- **Not changed:** harness, checks, thresholds, PROTOCOL. New analysis functions only (`analysis/gate.py`: `REG16`, `REG16_CONTROL`, `completion_rate`, `owed_backlog`, `pf_by_sent`, `cold_windows`, `longest_cold_s`, `cold_persistent`, `window_mix`, `reg16_*`), with tests. `docs/definitions.md`: `pf_by_sent` added under percent fast, already marked ⚠ (round 2, T3). The seeds 3–7 are untouched.
- **Adversarial review (rule F), round 1, verbatim** (a separate pass that saw only the round-1 draft and the code diff):
>
> ## Rule F review of the REG-16 draft (adversarial pass, read-only)
>
> **Reproduced with the committed functions:** `reg16_calibration` (28 / 2149 / 1215; c_watch 1.758, c_drop 1.672, released 1.582), `reg16_inputs` (23314 requests; λp 2.202 / 2.473 / 2.223 / 1.021 / 2.253 / 2.255; peaks 2.900 / 3.217 / 1.633 / 3.067; 2 and 1 windows above 3.0; judged 2.202 / 2.290 / 2.150 / 2.255; empty 4230 s, pessimistic 5070 s) and `reg16_seed_rule` (picks 7200 s and seed 14; at 5400 s seeds 14 and 24 fail on 5060 and 4550 s; at 7200 s the 25 seeds range 2700–5070 and 3230–5710 s). Every number matches.
>
> **T1 (should-fix, borders on blocking): a short dip that clears is scored `control_cold`, which stops the 2.2 plan.** One 300 s window at both stuck levels anywhere in 1080–14280 s gives `control_cold` ("no REG-17, no matrix at 2.2"). That happens even if the next window is warm again and the watch verdict is `recovered`.
> - REG-14's 2.4 control already dipped once with no burst (window 1500 s: hit 0.787 at λp 2.78, `_level` on 20261109-055910). It recovered at once.
> - A dip that recovers by itself shows the warm state pulls back, which helps the bistability argument. It is not the spontaneous collapse that would undercut REG-15.
> - Fix, registered now: split the outcome into `control_cold_persistent` (cold windows that are still cold at the phase's end, or the watch verdict `stuck`) and `control_cold_transient` (reported, owner decides, does not stop REG-17 by itself).
>
> **T2 (should-fix): `cold_windows` can miss a collapse, giving `control_warm` on a server that went cold.** `_level` takes pf from requests whose t_planned falls in the window, but hit from scrape time. Under closed loop, the release lag is permanent for each session (`harness/loadgen.py` `session_chain`: release = previous end + gap). REG-15 measured 14–16 min of lag. Trace: hit is cold at scrape time in 2400–3300 s. The requests served then were planned about 15 min earlier, so the low pf lands in windows 1500–2400 s. No single window has both conditions, the episode clears before 4980 s, the verdict is `recovered`, and the outcome is `control_warm`.
> - Fix: align pf with the hit (requests by t_released or t_sent).
> - Also report hit-only cold windows with waiting > 0 as a readout. Any such window should block `control_warm` and give `inconclusive` instead.
>
> **T3 (should-fix): the drain margin does not cover the decline REG-15 itself shows.** `c_pessimism` 0.05 is the spread of c_b across REG-11/12/14 (1.78–1.83). But REG-15's own c_drop (1.672) is already 0.11 below the lowest c_b. Its 600 s completion rates also fall through the run: 1.827 → 1.73 in the watch → 1.695, 1.655, 1.645 in the drop (`completion_rate` on the calibration run).
> - Sensitivity for seed 14 at 7200 s: lowering both rates by 0.10 gives empty at 5900 s, by 0.15 gives 6960 s (only 240 s left, so `drop_inconclusive`), and by 0.20 the line never empties (NaN).
> - A plausible reason for the decline: late turns have longer prompts and are served cold, so requests per second drop as the backlog ages.
> - REG-17's `drop_inconclusive` risk is therefore well above the stated ≈ 0.2.
> - Fix:
>   - Set the pessimistic rate to REG-15's lowest 600 s cold rate (1.645) minus 0.05, or model completions in prompt tokens per second.
>   - With that rate, seed 14 at 7200 s fails. Either take 9000 s (+0.5 h per run, ≈ +1 h for the pair) or re-run the rule. This must be decided before REG-16 runs, because the control's schedule is fixed by the drop length.
>
> **T4 (should-fix, for REG-17's rules): `warmed` is judged against the wrong reference.** The judged window runs at λ = 1, right after the line clears. New sessions rebuild their own prefixes within about one session lifetime (8 turns × 20 s), so hit ≥ base − 0.06 is close to automatic, whatever the cache did before.
> - A trigger-made cold state and plain overload would both pass this test. That is the same weakness the reviewer raised against the 1800 s drop.
> - Fix: compare REG-17's hit in [t0+600, t0+1200) with the control's hit in the same absolute window. This is the control's best use.
> - Also define what a NaN hit in that window gives (`inconclusive`). The two outcomes do not "partition" the range when the value is missing.
>
> **T5 (minor): t0 can come too early, and owed backlog does not fall to 0.** t0 is the first scrape with 0 waiting, but the drop is sized on owed backlog reaching 0.
> - Even a healthy run owes about 28–34 requests (running requests plus normal per-turn lag; `owed_backlog` at 600 s and at the trigger), so the model aims slightly late.
> - A momentary 0 in waiting near the end of the drain sets t0 early.
> - Fix: require waiting = 0 for, say, 3 consecutive scrapes, and report owed backlog at t0 and at t0+600.
>
> **N1 (minor): the docstring contradicts the code.** `reg16_control_outcome`'s docstring puts `inconclusive` before `control_cold`. The code and the draft put `control_cold` first. Fix the docstring.
>
> **N2 (minor): the peak readout includes the cold window itself.** `peak_120s_before_first_cold` scans up to `first[1]-120`, not up to `first[0]`. The draft says "in the 600 s before it". Fix one or the other.
>
> **N3 (minor): a rerun cannot fix a bad own baseline.** The watch verdict uses the control's own 480–1080 s baseline at λp 2.47, which is fixed by the schedule. If that verdict is `bad_baseline`, "rerun unchanged" repeats the same load. Route this case to the owner, not to a rerun.
>
> **N4 (minor): the baseline sits slightly low.** The 300–900 s baseline is a little below the later warm hit (REG-14 control: 0.832 / 0.836 against 0.838–0.842 after 900 s). That lowers the cold bar by about 0.005, a small bias toward `control_warm`. Report it.
>
> **N5 (minor): the seed rule favours lighter schedules, and seed 14 is close to its limit.** The empty-time condition selects seeds with lighter schedules, which also helps the control stay warm. Seed 14 does not look light (watch λp 2.223, peak 3.22), but this should be stated. Also, seed 24 passes at 7200 s with much more margin (pessimistic 4290 s against 5070 s). The lowest-seed rule picks the seed with the least room left to watch the cache. Under T3, that is the one most likely to end `drop_inconclusive`.
>
> **N6 (minor): `reg16_check` does not pin the run to the registered config.** It does not check for no trigger of any kind (a wipe would pass `reg16_phases`), and it does not check a config hash against the registered file. Add both.
>
> **N7 (minor): one control seed is weak evidence for `control_warm`.** It is 0 cold of n = 1, and the one-sided 95 % upper bound on the chance of a cold window per 4 h is 0.95. Label it per rule H. `control_warm` permits REG-17; it does not show that spontaneous collapse is rare.
>
> **Strongest alternative explanation for each outcome:**
> - **`control_warm`:** the collapse was missed (T2), or the warm state is only borderline and seed-dependent (N5, N7).
> - **`control_cold`:** a dip driven by one surge in the schedule (peak 3.22), not instability at the load level (T1).
> - **`control_not_recovered`:** a lagging closed-loop queue at λp 2.29 in the previous window, not the cache.
> - **`inconclusive`:** recorder or heat failure over 4 h (A14).
>
> **Verdict:** the run can change a decision. `control_cold` (persistent) stops the 2.2 line, and `control_warm` licenses REG-17, so ≈ 4 GPU h is justified. The control's long drop and return also give REG-17 its matched reference (T4). Fix T1–T3 before approval. T3 matters most, because the drop length fixes the control's schedule and cannot be changed after REG-16 runs. Write T4 into REG-17's rules now. The rest are minor.
- **Adversarial review (rule F), round 2, verbatim** (the same reviewer, on the revised draft and diff):
>
> ## Rule F review of the REG-16 draft, round 2 (read-only)
>
> **Reproduced:** `reg16_calibration` gives c_watch_min 1.728 and c_drop_min 1.637. The pessimistic empty time is 5580 s for seed 14 and 4830 s for seed 24 at a 7200 s drop. The rule still picks 7200 s and seed 14. `cold_windows` against the 300–900 s baseline marks every window of REG-15 from 1080 to 8880 s as cold and as low-hit-with-queue, so `cold_persistent` is True. It marks none of REG-14's control windows. The `reg16_check`-style flat comparison of REG-14's control config against its resolved file finds 0 differing keys, so the check does not refuse a valid run by mistake.
>
> The round-1 fixes T1, T2, T5, N1, N2, N3 and N6 are in the code as described. Nothing is blocking. Three should-fix items remain.
>
> **R2-T1 (should-fix): `cold_persistent` looks only at the last window of each phase.**
> - Trace A: the control is cold in every window from 1380 to 5280 s (65 min, as long as REG-15's state), and only the final 5280–5580 s window clears, for example in the end window's lower λp (2.15). The verdict's 600 s end window averages one cold half and one warm half, so it is probably not `stuck`. The outcome is `control_cold_transient`, the same label as a single 300 s dip.
> - Trace B: the last window of the watch is None (a scrape gap) and its neighbours are cold. The code checks `x is True` at the phase end, so the outcome is `transient`, not `inconclusive`.
> - Fix:
>   - A None at a phase's end that follows a cold window gives `inconclusive`.
>   - Report the longest cold stretch in the result.
>   - Write into the decision rule that a transient stretch longer than the cold window seen in REG-15's watch goes to the owner as equivalent to `persistent`.
>   - Register any length limit now, not after the run.
>
> **R2-T2 (should-fix): REG-17's `warmed` test still cannot separate the two hypotheses.** Using the control's hit in the same absolute window as the reference is right. But after the line clears at λ = 1, new sessions rebuild their prefixes within about 140 s, so both a burst-made cold state and plain overload reach the control's level in [t0+600, t0+1200). The draft itself says this.
> - The separating evidence is the pair: REG-16 `control_warm` together with REG-17 stuck through the watch. The drop only checks C1's recovery condition.
> - Fix: say this in REG-17's rules, and treat `warmed` as consistent with both hypotheses, not as support for either.
>
> **R2-T3 (should-fix): a third percent-fast computation is undefined.** `pf_by_sent` (by send time) is a third pf definition, next to `percent_fast` and `_level`. Rule J needs a `docs/definitions.md` entry marked "more than one computation" and left for the owner.
> - It also leaves out requests never sent: 6.1 % of REG-15's requests have no t_sent. In a collapse these are the most delayed turns, so pf_by_sent biases upward. Because of the lag, those turns cannot be attributed to any one window. The bias is small, but it leans toward "not cold".
> - The baseline pf it is compared with is still `_level` by planned time. In a warm baseline the two agree, but this should be stated.
> - Fix: add the definitions entry, and report the unsent count per window as a readout.
>
> **R2-N1 (minor): the margin before `drop_inconclusive` is thin.** The pessimistic case leaves seed 14 1620 s. Three zero scrapes plus the 1200 s judged window leave about 420 s of slack. Two cheaper margins exist at the same design:
> - seed 24 leaves 2370 s;
> - a 9000 s drop with seed 14 gives a pessimistic 5540 s and leaves 3460 s, at +0.5 h per run.
>
> With P(drop_inconclusive) ≈ 0.3 by the draft's own estimate, the owner should weigh +1 h for the pair against a likely 4 h rerun. This is the owner's choice, but it must be made before REG-16 runs.
>
> **R2-N2 (minor): `hit_low_queued` may fire on the step back to 2.2.** It uses base q + 1, about 1 here. At 12780 s, turn-0 starts rise and a short queue can form, so the first return window could give `control_unclear` on a healthy server. Report that window's turn-0 share.
>
> **R2-N3 (minor): the docstring still lists `inconclusive` twice.** It is correct in effect, but say "base_ok None" and "other missing values" explicitly.
>
> **Verdict:** the run can still change a decision. `control_cold_persistent` stops the 2.2 line, and `control_warm` permits REG-17, so ≈ 4 GPU h is justified. Before approval, fix R2-T1 (persistence judged by one window), R2-T2 (wording only) and R2-T3 (the definitions entry), and have the owner decide R2-N1. None of them blocks approval once addressed.
- **Changed because of it:**
  - Round 1:
    - T1: `control_cold` split into `control_cold_persistent` and `control_cold_transient`.
    - T2: pf by send time (`gate.pf_by_sent`), and `hit_low_queued` → `control_unclear`.
    - T3: the pessimistic rates start from REG-15's lowest 600 s rates.
    - T4, T5: written into REG-17's planned rules.
    - N1–N3, N6: in code. N4, N5, N7: in the text.
  - Round 2:
    - R2-T1: persistent also when a cold stretch lasts 1500 s (the watch window); a gap at a phase's end after a cold window gives `inconclusive`; the longest stretch is reported.
    - R2-T2: `warmed` is stated as consistent with both hypotheses.
    - R2-T3: `pf_by_sent` entered in `docs/definitions.md` under percent fast (⚠); unsent requests per window reported.
    - R2-N1: the 9000 s drop with seed 14 (agent's choice, delegated by the owner; table above).
    - R2-N2: first-turn share per window reported.
    - R2-N3: docstring fixed.
  - **Not re-reviewed:** the round-2 changes and the 9000 s drop. They were checked by tests (`uv run pytest tests/test_gate.py`) and by `reg16_inputs` on the final configs.

## 2026-11-10 · [DECISION] Owner pre-approves REG-16 and its run, and leaves the seed to the agent; agent picks seed 14 with a 9000 s drop
- **Owner (2026-11-10), while the round-2 fixes were in progress:** "I preaprove it, ok ? choose whatever seed that gives correct output".
- **Read as:** approval of REG-16 as finally written above, with the round-2 fixes, and of its run under its stopping rule. "Correct output" is read as a valid, decisive test, not a wished-for result. A seed chosen for the result it might give would bias the test, so the choice used only margin and load, before any run.
- **Agent's choice:** seed 14, drop 9000 s (REG-16 entry, table). Seed 24 was set aside because its lighter watch (λp 2.180, peak 3.000) would favour `control_warm`. The rule's 7200 s left 1620 s in the pessimistic case against the 1200 s needed. The longer drop costs ≈ 0.5 GPU h per run.
- **Not covered:** REG-17 still needs its own registration, review and approval.

## 2026-11-10 · [OPS] REG-16 run: valid on the first attempt, no rerun; pre-launch read in `docs/probe/20261110_reg16/`
- **Run** `20261110-122001_stage2_control_l1pl350cl_r2.2_long_s14`: launched 12:19:59 UTC at 350.00 W, 45 °C, 0 % busy, no compute process, VM tree `c198a30` clean, 9.4 GB free (PROBE(docs/probe/20261110_reg16/prelaunch_reg16_attempt1.txt)). Valid, `failed` empty, all 10 checks passed, including `power_limit` (RUN(20261110-122001_stage2_control_l1pl350cl_r2.2_long_s14, checks.json)). sw_thermal 0.004, max 73 °C, busy SM-clock CV 0.017, limit 350.0 W over 16109 samples.
- Console log on the VM: `~/stage2_control_l1pl350cl_r2.2_long_s14_20261110T121959Z.log`. Copied to the Mac, sha256 identical (10 files); `manifests/runs.sha256` +10 lines. VM copy kept.

## 2026-11-10 · [RESULT] REG-16: `control_cold_persistent`. With no burst, the control went cold at 4080–4380 s, after three windows of λp 2.46–2.71, and stayed cold to the end of the watch (`stuck`); it warmed again in the drop and stayed warm on the return to 2.2
- **Computed once:** `uv run python -m analysis.gate reg16` (`gate.reg16_table`) on `20261110-122001_stage2_control_l1pl350cl_r2.2_long_s14`; values RUN(20261110-122001_stage2_control_l1pl350cl_r2.2_long_s14, gate.reg16_table) unless tagged otherwise.
- **Baseline** (300–900 s, `REG16["baseline"]`): pf 1.000, hit 0.838, queue 0.003, KV 0.184. The watch verdict's own baseline (480–1080 s): pf 1.000, hit 0.828, queue 0.008. Neither is `bad_baseline`.
- **Watch** (1080–5580 s): `load.verdict` is **`stuck`**. End window (4980–5580 s): pf 0.000, hit 0.000, queue 96.9 (slope +0.087 /s), KV 0.949, 30.2 running.
- **Cold windows** (`gate.cold_windows`, 50 windows of 300 s from 1080 s): 8 cold, 4080–6480 s, one unbroken stretch. `longest_cold_s` 2400 s ≥ `persistent_s` 1500 s, and the watch's last window is cold, so `cold_persistent` is true by both rules. `first_cold` 4080–4380 s, in the watch. `hit_low_queued` in 7 windows, 4380–6480 s. No other window is cold.
- **Outcome** (`gate.reg16_control_outcome`): **`control_cold_persistent`**.
- **Timeline** (300 s windows from 0 s, `gate.reg16_table` timeline; t in s):

  | phase | t | λp | pf | hit | waiting q mean | KV |
  |---|---|---|---|---|---|---|
  | baseline | 600–900 | 2.24 | 1.000 | 0.835 | 0.007 | 0.183 |
  | watch | 3000–3300 | 1.97 | 1.000 | 0.840 | 0.003 | 0.159 |
  | watch | 3600–3900 | 2.57 | 1.000 | 0.826 | 0.007 | 0.242 |
  | watch | 3900–4200 | 2.46 | 1.000 | 0.834 | 0.000 | 0.216 |
  | watch | 4200–4500 | 2.71 | 0.453 | 0.417 | 2.6 | 0.708 |
  | watch | 4500–4800 | 2.13 | 0.000 | 0.000 | 22.1 | 0.949 |
  | watch | 4800–5100 | 2.54 | 0.000 | 0.000 | 58.5 | 0.951 |
  | watch | 5100–5400 | 2.16 | 0.000 | 0.000 | 98.1 | 0.948 |
  | watch → drop | 5400–5700 | 1.54 | 0.000 | 0.000 | 113.1 | 0.950 |
  | drop | 6000–6300 | 1.23 | 0.014 | 0.000 | 47.6 | 0.952 |
  | drop | 6300–6600 | 0.91 | 0.713 | 0.335 | 9.0 | 0.650 |
  | drop | 6600–6900 | 1.01 | 1.000 | 0.840 | 0.000 | 0.063 |
  | return | 15000–15300 | 2.30 | 1.000 | 0.835 | 0.003 | 0.195 |
  | return | 15600–15900 | 2.24 | 0.999 | 0.815 | 0.000 | 0.183 |

  - Every window from 0 to 4200 s is warm (hit 0.823–0.843, pf 1.000, queue ≤ 0.01), including windows at λp 2.57 and 2.60. Every drop window from 6600 s and every return window is warm (hit 0.815–0.848, queue ≤ 0.003).
- **Readouts:**
  - **Peak before the first cold window** (`peak_120s_before_first_cold`): λp 2.783 over 120 s.
  - **Return:** `return_recovered` true; return's end (15480–16080 s): pf 0.999, hit 0.816, queue 0.002, KV 0.202.
  - **`window_mix`:** 0 planned-but-unsent requests in every window, so `pf_by_sent` misses nothing here. First-turn share 0.074–0.156; the highest (0.149–0.156) fall in the cold watch windows, the lowest (0.074–0.099) in the first drop windows.
- **Prediction** (model.md row 20):
  - valid: hit (0.7);
  - baseline healthy: hit (0.9);
  - outcome: **miss** of the modal `control_warm` (0.5); `control_cold_persistent` had 0.2.
- **Alternatives:**
  1. **Overload during a surge, then a backlog** (the reading the registration feared): the collapse came in the third straight window above λp 2.4 (2.57, 2.46, 2.71; peak 2.78 over 120 s), above the closed-loop warm capacity of about 2.4 (decisions.md 2026-11-10 [RESULT] REG-13). REG-13's runs at 2.6–3 went cold in the same way after 368–602 s. Once the queue held ≈ 100 requests in a full pool, any state would lag. This explains the collapse without a second stable state.
  2. **Two states at one load, with a surge as the trigger:** after the collapse the server stayed cold at λp 2.13 and 2.16 with a growing queue (slope +0.09 /s and +0.10 /s), loads that the same run carried warm before (2.20–2.29) and after (2.24–2.30). The same load held both states, depending on history. The two readings differ in what the cold state does when the surge has passed; this run cannot separate them, because the watch ended 1100–1400 s after the collapse with the backlog still growing.
  3. **The client backlog, not the cache, held the cold state:** under closed loop the late sessions keep arriving with long prompts. Against a cache-only cause: the line emptied in the drop by ≈ 6600 s and hit returned to 0.840 in the next window (above). That is what a cold state held by its backlog does; it says nothing about a cache that holds without one.
  4. **Heat or clock:** sw_thermal 0.004, max 73 °C, CV 0.017 (OPS above). Not a factor.
- **What this is:** in one control run at λ = 2.2, without any burst, the schedule's own surge took the server cold, and it stayed cold until the load dropped. So REG-14's and REG-15's cold states are not shown to need the burst: on a long enough schedule at this load, the warm state does not last. One seed (rule H: 1 cold of n = 1; the one-sided 95 % Clopper–Pearson lower bound on the chance of a cold episode per 4.5 h run is 0.05, DERIVED: 0.05^(1/1)). Observed as a side result in this run: the cold state left once the line emptied at λ = 1, and λ = 2.2 then ran warm for 1500 s.
- **Registered decision (`control_cold_persistent`):** **no REG-17 and no matrix at λ = 2.2.** The owner chooses: a lower λ, or reporting λ = 2.2 as a load where the warm state is not stable. Nothing runs before the owner chooses and approves a new registration.
- **Not changed:** claims.md, REG-11–15's results, code, thresholds. `configs/confirm_l1pl350cl_r2.2_long_s14.yaml` stays unregistered and unused.

## 2026-11-10 · [DECISION] Owner approves the reviewer session's proposal after REG-16: commit the surge statistic, correct the REG-13 and REG-16 readings, and draft REG-17 (REG-14's seed-2 pair at λ = 2.0)
- **Owner (2026-11-10):** pasted the reviewer session's "Proposed next run" (REG-17, the seed-2 pair at λ = 2.0, ≈ 1.45 GPU h; before it, at 0 GPU h: commit the surge statistic with tests, a [CORR] on the REG-13 and REG-16 readings, and rule G's pass condition stated as written after its numbers were seen) and wrote "I approve".
- **Read as:** approval of the plan and of drafting REG-17 as proposed. The proposal itself says "Nothing runs before you approve a registration", so the GPU run waits for the owner's word on the reviewed [REG] below.
- **Agent's changes to the proposal, for the owner to see:** the decisive test is C1's per-seed verdict pair, not REG-14's span test, because at λ = 2.0 the span test cannot confirm the cold rates seen (REG-17 entry).

## 2026-11-10 · [CORR] REG-16's result and REG-13's reading: the no-burst collapses follow a 120 s surge of planned arrivals, not a sustained load above a "closed-loop warm capacity ≈ 2.4"
- **Found by:** the reviewer session (2026-11-10, at the owner's request), in exploratory scripts; reproduced here by committed code (`gate.surge_table`, `gate.surge_hazard`; tests in `tests/test_gate.py`).
- **What I wrote:** REG-16's [RESULT], model.md M2 and status.md read the collapse as following "three windows of λp 2.46–2.71, above the closed-loop warm capacity ≈ 2.4", and gave "the peak before the first cold window" as λp 2.783 over 120 s. status.md and model.md also call REG-13's 2.4 "the closed-loop warm capacity".
- **Why that is wrong:**
  - The same REG-16 run carried 300 s windows at λp 2.57 and 2.60 warm (RUN(20261110-122001_stage2_control_l1pl350cl_r2.2_long_s14, gate.reg16_table) timeline). A mean above 2.4 is not what tipped it.
  - My readout stopped at the first cold 300 s window's start (4080 s), before the tip, and stepped 60 s. On a 5 s grid up to the KV onset (4433 s, 60 s trailing mean KV ≥ 0.9) the highest 120 s planned rate in the 180 s before onset − 60 s was 3.45, against at most 2.95 in the run's earlier warm time (RUN(20261110-122001_stage2_control_l1pl350cl_r2.2_long_s14, gate.surge_run)).
  - Over the 21 valid closed-loop L1 350 W runs (`gate.surge_table`): 6 runs with no burst tipped (REG-12's controls of seeds 4 and 5, REG-13's runs at 2.6, 2.8 and 3.0, REG-16). Each tip followed a 120 s peak of 3.24–3.49 req/s. The highest peak in warm time that did not tip was 3.32 (seed 4's control at 2.4, before its later tip at 3.49). About 27,000 s of warm time are covered.
  - REG-13's runs at 2.6, 2.8 and 3.0 tipped after peaks of 3.42, 3.24 and 3.33; its runs at 2.0 and 2.4 peaked at 2.73 and 3.12 and did not tip. So "μ_warm,cl ≈ 2.4" records whether a 900 s schedule held such a surge; it is not shown to be a sustained capacity. REG-13's computed `overload` stands as computed; only its reading changes.
- **What follows (schedule only, `gate.surge_hazard`, REG-14's control workload, seeds 1–40):** a 120 s peak ≥ 3.2 appears within 2600 s / 5600 s in 31 / 39 seeds at λ = 2.4, 13 / 19 at 2.2, 7 / 8 at 2.1, 1 / 2 at 2.0 and 0 / 0 at 1.9. A 4500 s warm control at 2.2 was close to a coin flip before REG-16 ran.
- **Limits (rule A5):** the level ≈ 3.2–3.4 was found by looking at these runs, and 3.24 (tipped) overlaps 3.32 (did not), so it is a readout, not a threshold, until a registration fixes it. A second reading fits the same runs: a surge of new sessions (cold 2176-token first turns), which moves with the request rate here. Neither is separated yet.
- **Corrected in place of the old wording:** status.md's headline and model.md's REG-13 and REG-16 notes now point here. The old entries stay as written.

## 2026-11-10 · [REG] REG-17 (draft): REG-14's seed-2 pair at λ = 2.0, the only change; rule G's pass condition for a matrix at 2.0, stated after its inputs were seen (GPU, ≈ 1.5 h)
- **Origin:** the reviewer session's proposal (2026-11-10, at the owner's request), approved by the owner (decisions.md 2026-11-10 [DECISION] above). It follows REG-16's `control_cold_persistent` and the [CORR] below: no-burst collapses follow a 120 s surge of planned arrivals, rare at λ = 2.0.
- **Question:** at λ = 2.0, seed 2, does REG-14's 180 s burst leave the server stuck through the 1500 s watch while the same schedule without the burst stays healthy?
- **Configs** (written now; each is REG-14's config with `workload.rate: 2.0` and a new name, nothing else; `test_reg17_configs_change_only_the_rate`):
  - `configs/stage2_control_l1pl350cl_r2.0_s2.yaml` (extends `stage2_control_l1pl350cl_r2.2_s2.yaml`);
  - `configs/burst_l1pl350cl_r2.0_s2.yaml` (extends `burst_l1pl350cl_r2.2_s2.yaml`; burst unchanged: 900 s, 180 s at 2.4 req/s, 2944-token prompts).
  - 2580 s each, closed-loop turns, a new connection per request, L1, 350 W. The control's session schedule equals the burst run's session rows (4993 requests; 463 burst requests) (`gate.reg17_inputs`).
- **Schedule inputs** (schedule only, no run; `gate.reg17_inputs`, `gate.pair_schedule`):
  - λp baseline (300–900 s) 1.970; watch (1080–2580 s) 1.984, by thirds 1.726 / 2.114 / 2.112.
  - Highest 120 s planned rate in the whole run 2.608 (at 590 s), so the control's schedule has no surge near the 3.24–3.49 that preceded every no-burst tip (`gate.surge_table`).
  - REG-14's span test at λ = 2.0 (`gate.span_sensitivity`): every span can confirm a cold rate only up to 1.81 req/s, inside the range of cold rates seen (REG-14 c 1.73–1.81, REG-15 span c 1.72–1.90; decisions.md [RESULT]s). REG-14's seed rule picks no seed at 2.0 (`gate.reg14_seed_rule`). **So the span test is a readout here, and the decision uses C1's per-seed test plus a measured cold side (below)** (REG-12's: burst `stuck`, control `recovered`; docs/claims.md). This departs from the proposal's "pair passes", which did not name the test.
- **Cold side, measured** (`gate.reg17_cold_side`, review T2, fixed before any run): in every REG-8 span after the burst's end (600–900, 900–1200, 1200–1500 s), the point completion rate (`gate.completion_rate`, all requests by t_end) is below min(λ = 2.0, the span's λp), **and** the verdict's end-window queue slope is > 0. `holds` is None if any value is NaN. This keeps a slowly draining backlog, or a cold state at ≈ 2.1 that is above 2.0, from passing as a cold state at 2.0.
- **Outcome** (`gate.reg17_outcome`, in this order; verdicts by `load.verdict`, the control judged at the burst's end as in REG-14):
  1. **`bad_baseline`:** either run's baseline fails. Not rerun; the owner decides.
  2. **Control not `recovered`** (review T1):
     - **`control_cold_surge`:** it tipped (`gate.kv_onset`: 60 s trailing mean KV ≥ 0.9) after a 120 s planned-rate peak ≥ `surge_tip` 3.2. Cannot happen on this schedule (peak 2.61) unless the run's schedule differs; reported, the owner decides.
     - **`control_cold_no_surge`:** it tipped with no such peak. The surge reading is wrong: **stop, no matrix, rethink** (proposal).
     - **`control_unclear`:** it did not tip and its verdict is `unclear` (an instrument gap is not a refutation). Reported; the owner decides.
     - **`control_warm_queue`:** it did not tip but is `slow_drain` or `stuck` (queued without going cold). Reported; the owner decides.
  3. **Burst `stuck`, control `recovered`:**
     - **`inconclusive`:** the cold side is None (a NaN). Reported; the owner decides.
     - **`stuck_draining`:** the cold side does not hold. Reported; no matrix; the owner decides.
     - **`pass_clear`:** the cold side holds, and the control had waiting > 0 in at most 0.5 of the scrapes of every span (REG-14's `max_control_waiting`, applied to every span, since no span may count under the span test here).
     - **`pass_warm_edge`:** the cold side holds, but the control queued more in some span (or a share is NaN). Reported; the owner decides.
  4. **`drains`:** burst `recovered` or `slow_drain`.
  5. **`unclear`:** burst `unclear`. Reported; the owner decides.
- **Readouts, never decisive:** the span label and `stuck_unconfirmed` from `reg10_gate`; per-span λp and max holding c; release rate; control waiting; shock size against REG-12's seed-2 burst run; both runs' `surge_run`; `gate.drain_time` (seconds from the burst's end to a line empty for 30 s, read against the watch's thirds; review T4); release delay; turn-0 share; unreleased.
- **What this weakens (review T3):** REG-14's span test gave a 99 % upper bound on each span's cold rate below min(λ, λp). Here only point rates are compared, so the evidence against "a backlog draining slower than the watch" is weaker than REG-14's. The point test and the rising end-window queue are the guard.
- **Rule G (feasibility), restated for λ = 2.0, numbers already seen:** the default pass condition (docs/process.md §4) is that λ lies strictly between the cold-state completion rate and the warm capacity, both measured. Under the [CORR] above the warm side is not a fixed capacity: it is the absence of a surge that tips it. Pass condition, registered now:
  - **warm side:** the control at λ = 2.0 is `recovered` (a no-trigger control at the candidate load, 2580 s ≥ the 2400 s minimum);
  - **cold side:** `reg17_cold_side` holds, a measured completion rate below 2.0 and below each span's λp, with the queue still rising at the end;
  - so the matrix at 2.0 is drafted only on `pass_clear`.
  - **Seen before writing this:** the surge hazard by λ (`gate.surge_hazard`: at 2.0, 1 of 40 seeds reaches a 120 s rate ≥ 3.2 within 2600 s, 2 within 5600 s; at 2.2, 13 and 19), the pair schedules of seeds 2–7 at 2.0–2.2 (`gate.surge_pair_inputs`) and the 21 closed-loop runs' surge readouts (`gate.surge_table`). No closed-loop run exists at λ = 2.0 except REG-13's sweep run (warm, peak 2.73), so neither side is measured yet. The test can fail on both sides.
  - **The warm side barely tests the surge reading (review N1):** the control's peak 2.61 is below every untipped peak, so `recovered` is predicted by both the surge reading and a capacity near 2.2–2.4. Only a cold control is informative about the surge reading.
  - **`surge_tip` 3.2 is a covariate, not a tip threshold (review N2, rule A5):** it was found in the same 21 runs, and untipped peaks (3.25, 3.275, 3.317) overlap the tip range 3.24–3.49. It only splits a cold control's label here, and is moot on this schedule.
  - **The hazard is a distribution, not a per-seed forecast (review N3):** `surge_hazard` builds 8000 s schedules, which differ from a seed's 2580 s schedule (seed 2 peaks at 3.05 before 2580 s in the 8000 s schedule, at 2.608 in the run's own). Per-seed peaks come from `pair_schedule`. Matrix seed 4 at 2.0 has a 120 s peak of 3.217 at 2435 s, inside its watch; the matrix registration must handle it.
- **Prediction** (BELIEF): control `recovered` ≈ 0.9; burst `stuck` ≈ 0.6; given `stuck`, the cold side holds ≈ 0.8; `pass_clear` ≈ 0.45; `drains` ≈ 0.35. Readouts if stuck (review N5): span c ≈ 1.70–1.82 (REG-14: 1.73–1.81); end-window queue ≈ 60–200 and rising; release rate ≈ span c. If it drains: the line empties within the first third (≤ 500 s after the burst's end), where λp is 1.73.
- **Decision under each outcome:**
  - **`pass_clear`:** draft the matrix at λ = 2.0 on the reserved seeds 3–7 (5 pairs, ≈ 7.2 GPU h), decided by C1's per-seed test and the same cold-side condition, with each schedule's highest 120 s peak in the control and its watch lull registered beforehand as covariates, not seed filters. Its own registration, review and approval.
  - **`drains`** (review T4): **seed 2's schedule at 2.0 does not hold a cold state** (0 of 1, rule H). It does not show that no schedule at 2.0 can. `drain_time` against the thirds tells "the lull" (empty in the first third) from "the load" (empty later). The owner chooses between λ = 2.1, another seed at 2.0, and reporting the zone as too narrow for this workload.
  - **`control_cold_no_surge`:** stop; no matrix; the surge reading is rethought before anything else is drafted.
  - **Every other outcome:** reported; the owner decides. No matrix.
- **Alternatives to read against each outcome:**
  1. **`pass_clear`:** a slowly draining backlog with c ≈ λp, or bistability at the local 2.11 rather than at 2.0. The cold-side condition (point c below 2.0 and λp, queue rising) is the guard; one seed and the point test are its limits.
  2. **`pass_warm_edge`:** the late watch (λp 2.11) queues even a warm server. The control's waiting mean and hit rate per span separate it.
  3. **`drains`:** the 500 s lull at 1.73 lets the cold state drain, not the load. `drain_time` against the thirds separates them.
  4. **`control_cold_no_surge`:** warm queueing at λp 2.11 without a cold tip, which T1's split now labels `control_warm_queue`; or a tip with no surge, which refutes the surge reading.
  5. **A control that stays warm by luck:** one run, peak 2.61; rule H: 0 tips of 1.
- **Stopping rule:** REG-14's. Each run once; an invalid run (other than `burst_min_kv_max`) is rerun unchanged, at most twice; a heat-invalid run once after cooling to ≤ 45 °C, a second heat failure stops; a `client_error`, a limit other than 350 W or an unexpected pre-launch check stops. A rerun decision reads only `checks.json`. No interim look at either run's verdict before both are valid. Burst run invalid on `burst_min_kv_max`: not rerun; the owner decides.
- **Order:** the control, then the burst run, each after the pre-launch checks (350 W limit, ≤ 45 °C, idle GPU, clean tree at the registered commit, disk), reads saved in `docs/probe/20261110_reg17/`.
- **Cost:** 2 × (2580 s + about 60 s start-up) ≈ 1.5 GPU h (DERIVED: 5280 s); worst case with every rerun ≈ 4.4 GPU h.
- **Not changed:** harness, checks, thresholds, PROTOCOL, seeds 3–7. New analysis functions with tests (`analysis/gate.py`: `SURGE`, `rolling_rate`, `kv_onset`, `surge_run`, `surge_table`, `schedule_peak_series`, `surge_hazard`, `pair_schedule`, `surge_pair_inputs`, `REG17`, `reg17_cold_side`, `reg17_outcome`, `drain_time`, `reg17_gate`, `reg17_inputs`). `docs/definitions.md`: "120 s surge peak" and "KV onset" added.
- **Adversarial review (rule F), one round, verbatim** (a separate read-only pass that saw only this draft and the code diff):

> ## Rule F review of the REG-17 draft (read-only)
>
> **Reproduced with the committed code (no mismatches):** `reg17_inputs`: λp baseline 1.970, watch 1.984, thirds 1.726/2.114/2.112, peak 2.608 at 590 s, 4993 session and 463 burst requests, schedules identical, rates (2.0, 2.0), seeds (2, 2). `span_sensitivity(2.0, 2)`: span λp 2.097/2.007/2.167, max_c 1.81 in all three; `reg14_seed_rule(2.0)` returns None. `surge_table`: 21 runs, 6 tipped, tip peaks 3.24–3.49. `surge_hazard` at 2.0: 1 of 40 seeds (2600 s) and 2 of 40 (5600 s); at 2.2: 13 and 19.
>
> ### Findings
>
> **T1 (should-fix, close to blocking): an unclear control is read as a refutation.** Trace: the control's end window has a scrape gap, so `hit` is NaN and `verdict` returns `unclear`. `reg17_outcome` then returns `control_cold_no_surge`, which means "stop, no matrix, rethink". The test pins this (`reg17_outcome("unclear","stuck",{tipped False})`). An instrument gap is not evidence that the surge reading is wrong, and the stopping rule gives no rerun for a valid but unclear run. A control that is `slow_drain` or `stuck` but never reached KV onset (a warm queue, not cold) gets the same label. Fix: an unclear control gets its own outcome (rerun or owner). Split "not recovered" into tipped without a surge (the surge reading is wrong) and not tipped (warm queueing; owner decides).
>
> **T2 (should-fix): the cold side of rule G is not measured.** §4 says the cold-state completion rate must be measured. The draft's cold side is "burst `stuck`". But `stuck` allows a queue that is draining, as long as q/−slope exceeds `drain_horizon_s` = 3600 s. Trace: in the end window q ≈ 200 and the slope is −0.05/s, so it would empty in 4000 s. Hit 0 and pf low give `stuck`, yet c > λp and the line drains. A related case: the last ~1000 s plan λp ≈ 2.11. A cold state completing at 2.02 is below λp, so the queue grows, but it is above λ = 2.0. That gives `pass_clear` at "λ = 2.0" while M2's c_cold < λ fails at 2.0; the bistability shown is at the local ≈ 2.1. Fix: register now, before any run, a point-estimate cold-side condition. For example: in every REG-8 span, point c < min(λ, λp) and the end-window q_slope > 0, using `completion_rate` and `secondary_cb`.
>
> **T3 (should-fix): dropping the span test removes the only confidence statement against "a slowly draining backlog".** Switching to C1's per-seed test is justified for power: max_c 1.81 sits inside the cold rates seen, so the span test would almost surely give `stuck_unconfirmed`. It also matches docs/claims.md C1 "Supports". What it loses is c_upper < min(λ, λp). The control-waiting rule, now applied to every span, still answers "the schedule made the backlog". Nothing answers "the burst's backlog drains slower than the watch". T2's condition restores this at no cost. Say in the draft that the evidence against overload is weaker than REG-14's.
>
> **T4 (should-fix): a `drains` result is over-read.** "The zone, if any, is between 2.0 and 2.2" comes from one seed. It also comes from a seed whose first watch third plans 1.73, below the cold rates seen (1.72–1.90), so the server can drain there. Rule H: 0 of 1. Reword to "seed 2's schedule at 2.0 does not hold a cold state", and register the per-span drain timing as the readout that separates "lull" from "load".
>
> **N1: the warm side barely tests the surge reading.** Peak 2.61 is below every non-tipping peak and below REG-13's warm λ = 2.0 sweep run (2.73). So `recovered` is predicted by the surge reading and also by "capacity ≈ 2.2–2.4". Only a cold control is informative. State this.
>
> **N2 (rule A5): surge_tip 3.2 does not separate tipped from untipped runs.** It was fitted to the same 21 runs. Untipped warm peaks reached 3.317 (`20261109-102614_…_r2.4_s4`, before it tipped), 3.275 (s1 control) and 3.25 (s6). Those overlap the tip range 3.24–3.49. On this run 3.2 is moot (peak 2.61). Call it a hazard covariate, never a tip threshold.
>
> **N3: the hazard seeds are not the run's seeds.** `surge_hazard` builds 8000 s schedules. With the same seed they differ from the 2580 s ones: seed 2 peaks at 3.05 before 2580 s at 8000 s, but 2.608 at 2580 s. As a distribution the hazard is valid (a stationary Poisson process), but it cannot be read per seed. Matrix seed 4 at 2.0 has, in its real pair schedule, a peak of 3.217 at 2435 s, inside the watch (`surge_pair_inputs`). The matrix registration must handle that.
>
> **N4:** the code comment gives the cold-rate range as "1.64–1.90"; the draft text gives 1.72–1.90. Make them agree, with sources.
>
> **N5 (rule A1):** add numeric predictions for the readouts (span c, end-window q, release rate), not only outcome probabilities.
>
> ### Strongest alternative explanation for each outcome
> - **`pass_clear`:** a slowly draining cold backlog (c ≈ λp, drain time > 3600 s), or bistability at the local 2.11 rather than at 2.0 (T2). Separated by per-span point c against 2.0 and against λp, and by the end-window q_slope.
> - **`pass_warm_edge`:** the late-watch schedule (2.11) queues even a warm server. Separated by the control's waiting mean per span and its hit rate.
> - **`drains`:** the 500 s lull at 1.73 lets the cold state drain; the load is not the cause. Separated by the time of the drain against the thirds.
> - **`control_cold_no_surge`:** an instrument gap (T1), or warm queueing at λp 2.11 without going cold. Separated by kv_onset (whether it tipped), the verdict's NaN fields, and the hit rate.
> - **`control_cold_surge`:** cannot occur with this schedule's peak of 2.61. If it occurs, the schedule differs from the registered one; check `control_schedule_same` on the run.
>
> ### Verdict
> The run can change a decision: `pass_clear` drafts a ≈ 7.2 GPU h matrix, `drains` moves to 2.1 or ends the search, and a cold control stops the surge line. So ≈ 1.5 GPU h (DERIVED: 2 × 2640 s = 5280 s) is justified.
>
> Rule G is honestly flagged as written after seeing its inputs. It can fail on both sides, so it is a real test. But its cold side is not a measured completion rate, as §4 requires.
>
> Before approval: fix T1 (outcome map and test) and T2 (a registered point-c and slope condition, fixed now), and reword T3 and T4. The N items can be fixed in the text.

- **Changed because of it:**
  - T1: a control that is not `recovered` is split by whether it tipped: `control_cold_surge`, `control_cold_no_surge` (tipped), `control_unclear`, `control_warm_queue` (not tipped). Only a tip with no surge stops the line. Test updated.
  - T2: the cold side is measured (`gate.reg17_cold_side`: point c below min(2.0, λp) in every span and a rising end-window queue), required for `pass_clear`; new outcomes `stuck_draining` and `inconclusive`. Tested on REG-14's burst run.
  - T3: "What this weakens" added.
  - T4: `drains` reworded to seed 2's schedule only; `gate.drain_time` added as the readout that tells the lull from the load; another seed at 2.0 added to the owner's options.
  - N1–N3: stated under rule G. N3's per-seed figures checked with `gate.schedule_peak_series` (3.05 in the 8000 s schedule before 2580 s, 2.608 in the run's own). N4: the code comment and the text both give 1.72–1.90 with sources. N5: readout predictions added.
- **Not covered:** the run waits for the owner's approval of this registration.

## 2026-11-10 · [DECISION] Owner approves REG-17 and its run
- **Owner (2026-11-10):** "yes", in reply to "Do you approve the REG-17 run?", asked after the reviewed registration above (with its two changes from the proposal: the C1 verdict pair plus a measured cold side instead of the span test, and the review's fixes) was committed in `39f01a9`.
- **Approved:** REG-17 as registered, and its run under its stopping rule: the control `configs/stage2_control_l1pl350cl_r2.0_s2.yaml`, then the burst run `configs/burst_l1pl350cl_r2.0_s2.yaml`, pre-launch reads in `docs/probe/20261110_reg17/`.

## 2026-11-10 · [OPS] REG-17 runs: 2 of 2 valid, no rerun; pre-launch reads in `docs/probe/20261110_reg17/`
- **Control** `20261110-174432_stage2_control_l1pl350cl_r2.0_s2`: launched 17:44:30 UTC at 350.00 W, 43 °C, 0 % busy, no compute process, VM tree `778f24b` clean, 8.6 GB free (PROBE(docs/probe/20261110_reg17/prelaunch_reg17_stage2_control_l1pl350cl_r2.0_s2_attempt1.txt)). Valid, `failed` empty (RUN(20261110-174432_stage2_control_l1pl350cl_r2.0_s2, checks.json)). sw_thermal 0.004, max 71 °C, busy SM-clock CV 0.011, limit 350.0 W over 2599 samples.
- **Burst run** `20261110-182920_burst_l1pl350cl_r2.0_s2`: launched 18:29:18 UTC at 350.00 W, 43 °C, 0 % busy, no compute process, VM tree `778f24b` clean, 8.4 GB free (PROBE(docs/probe/20261110_reg17/prelaunch_reg17_burst_l1pl350cl_r2.0_s2_attempt1.txt)). Valid, `failed` empty (RUN(20261110-182920_burst_l1pl350cl_r2.0_s2, checks.json)). sw_thermal 0.002, max 70 °C, CV 0.014, limit 350.0 W over 2886 samples.
- Both copied to the Mac, sha256 identical (10 files each); `manifests/runs.sha256` +20 lines. VM copies kept.

## 2026-11-10 · [RESULT] REG-17: `pass_clear`. At λ = 2.0, seed 2, the control stayed warm with an empty queue while after the burst the same schedule stayed cold, full and backlogged for the 1500 s watch, completing 1.73–1.77 req/s, below 2.0 and below every span's planned load
- **Computed once:** `uv run python -m analysis.gate reg17` (`gate.reg17_gate`) on the two runs above; values RUN(20261110-182920_burst_l1pl350cl_r2.0_s2, gate.reg17_gate) and RUN(20261110-174432_stage2_control_l1pl350cl_r2.0_s2, gate.reg17_gate) unless tagged otherwise. Baselines and end windows: `load.verdict` on each run.
- **Control:** `recovered`. Baseline pf 1.000, hit 0.842, queue 0.000; end window pf 1.000, hit 0.838, queue 0.003, KV 0.171. Waiting > 0 in 0.007, 0.003, 0.003 of the scrapes of the three spans. Never reached KV onset (`surge_run`: not tipped; its highest 120 s planned rate 2.608 at 590 s).
- **Burst run:** `stuck`. Baseline pf 0.996, hit 0.841, queue 0.002. KV onset at 965 s (the burst runs 900–1080 s). End window pf 0.000, hit 0.000, queue 110.8 (slope +0.061 /s), KV 0.949, 30.0 running.
- **Cold side** (`gate.reg17_cold_side`): **holds**.

  | span after the burst's end (s) | λp | c | c 95 % upper | waiting q mean (min) | KV | hit (counter) |
  |---|---|---|---|---|---|---|
  | 600–900 | 2.097 | 1.773 | 1.961 | 76.5 (54) | 0.951 | 0.000 |
  | 900–1200 | 2.007 | 1.733 | 1.919 | 101.5 (91) | 0.950 | 0.000 |
  | 1200–1500 | 2.167 | 1.753 | 1.940 | 120.2 (101) | 0.948 | 0.000 |

  Every span's c is below min(2.0, λp), and the end-window queue slope is > 0.
- **Outcome** (`gate.reg17_outcome`): **`pass_clear`**.
- **Readouts:**
  - **Span test** (`reg10_gate`, not decisive here): label `pass`. Every span's upper bound (1.92–1.96) is below min(λ, λp), so it confirms as well. The registration expected it could not (max holding c 1.81); the cold rates came in at 1.73–1.77, under that limit.
  - **The lull did not drain it:** `drain_time` NaN. The line never emptied after the burst's end (q_min 54 in the first span), though the first third of the watch planned λp 1.73.
  - `secondary_cb` c_b 1.772 over one 1499 s backlogged stretch, `not_sustainable` against λp 1.984. Release rate 1.90 / 1.78 / 1.84; release delay 218 / 259 / 304 s (baseline 10 s); unreleased later turns 0 / 0 / 166; turn-0 share 0.141 / 0.146 / 0.141.
  - Shock size: 36 outstanding over 1499 s, against REG-12's seed-2 burst run's 46.
- **Prediction** (model.md row 21): control `recovered` (0.9): hit; burst `stuck` (0.6): hit; cold side holds given stuck (0.8): hit; `pass_clear` (0.45): hit. Readouts: span c 1.73–1.77 within the predicted 1.70–1.82; end-window queue 110.8 and rising within 60–200. `drains` (0.35) did not happen.
- **Alternatives:**
  1. **Overload at this schedule's load:** against it, the control on the identical session schedule ran with waiting in ≤ 0.7 % of scrapes and hit 0.838 to the end, and the burst run's own baseline was warm. The warm state carries this load; the cold state does not.
  2. **A slowly draining burst backlog:** against it, every span's completion rate is below its planned load and the queue rose from span to span (76 → 101 → 120) with a positive end slope. The span test's upper bounds agree.
  3. **Bistability at the local λp ≈ 2.1, not at 2.0:** against it, c is below 2.0 in every span, including the one at λp 2.007.
  4. **Heat or clock:** sw_thermal ≤ 0.004, max 71 °C (OPS above). Not a factor.
  5. **Limits:** one seed (rule H: 1 of 1; one-sided 95 % lower bound 0.05, DERIVED: 0.05^(1/1)); a 1500 s watch, not 4500 s; no drop to λ = 1 in this design. The warm side barely tests the surge reading: the control's peak was 2.61 (registration, review N1).
- **What this is:** M2's condition c_cold < λ < c_warm observed at λ = 2.0 in one seed, with a measured cold side, at a load where the schedule's own surges are rare (1 of 40 seeds within 2600 s, `gate.surge_hazard`). Unlike λ = 2.2, the no-burst control is not expected to tip by itself here. Not yet C1: it needs the matrix and the long confirmation with the drop.
- **Registered decision (`pass_clear`):** draft the matrix at λ = 2.0 on the reserved seeds 3–7 (5 pairs, ≈ 7.2 GPU h), decided by C1's per-seed test and the same cold-side condition, with each schedule's highest 120 s peak in the control and its watch lull registered as covariates, not seed filters. Its own registration, rule F review and owner approval; nothing runs before that.
- **Not changed:** claims.md, earlier results, code, thresholds.

## 2026-11-11 · [REG] REG-18 (confirmatory, draft): REG-17's pair on seeds 3–7 at λ = 2.0, the only change; per seed C1's test plus REG-17's measured cold side; ≥ 3 of 5 clear passes, with a futility stop (GPU, ≈ 6.1 h expected, ≤ 7.5 h)
- **ID:** REG-18. **Confirmatory** for C1's matrix condition ("stuck in most seeds, the control recovered", docs/claims.md C1) at λ = 2.0. **Not approved:** no GPU run before the owner approves this entry.
- **Origin:** REG-17's registered branch under `pass_clear` (decisions.md 2026-11-10 [REG] REG-17, "Decision under each outcome"): "draft the matrix at λ = 2.0 on the reserved seeds 3–7 (5 pairs), decided by C1's per-seed test and the same cold-side condition, with each schedule's highest 120 s peak in the control and its watch lull registered beforehand as covariates, not seed filters". REG-17 gave `pass_clear` (decisions.md 2026-11-10 [RESULT]). Seeds 3–7 were agreed by the owner (decisions.md 2026-11-10 [DECISION]); REG-17's seed 2 is not counted.
- **Question:** at λ = 2.0, does REG-14's 180 s burst leave the server stuck and cold through the 1500 s watch, while the same schedule without the burst stays healthy, in most of seeds 3–7?
- **Claim tested:** C1's matrix condition at one load. C1's other conditions (the 4500 s confirmation and the drop to λ = 1, condition 6) and C2 are not tested here.
- **Configs** (written now; each is REG-17's with only `name` and `seed` changed; `test_reg18_configs_change_only_the_seed` compares the resolved configs key by key):
  - `configs/stage2_control_l1pl350cl_r2.0_s<s>.yaml`: `extends: stage2_control_l1pl350cl_r2.0_s2.yaml`, `seed: s`;
  - `configs/burst_l1pl350cl_r2.0_s<s>.yaml`: `extends: burst_l1pl350cl_r2.0_s2.yaml`, `seed: s`.
  - So: L1, 350 W check, closed-loop turns, a new connection per request, λ = 2.0, 2580 s, burst at 900 s for 180 s at 2.4 req/s with 2944-token prompts, `burst_min_kv_max` 0.95, control `control_t_s` 1080. The seed changes the session schedule and the burst draw (`harness/workload.py`: the burst uses `default_rng([seed, 1])`).
- **Schedule inputs** (schedule only, no run; `gate.reg18_inputs`, which calls `pair_schedule`, `span_sensitivity`, `reg18_exposed`, `reg18_lull`; reproduced by the review). For every seed the control's schedule equals the burst run's session rows, and λ and seed resolve as registered (`test_reg18_inputs_schedule_facts`).

  | seed | session / burst requests | λp baseline | λp watch (thirds) | λp per span (600–900, 900–1200, 1200–1500 s after the burst's end) | lowest span λp | control's highest 120 s rate (at) |
  |---|---|---|---|---|---|---|
  | 3 | 4804 / 416 | 1.838 | 1.873 (1.844, 2.080, 1.694) | 2.190, 1.880, **1.623** | 1.623 | 2.450 (1940 s) |
  | 4 | 5548 / 407 | 1.975 | 2.262 (2.036, 2.468, 2.282) | 2.423, 2.123, 2.513 | 2.123 | **3.217 (2435 s)** |
  | 5 | 5306 / 450 | 2.065 | 1.969 (2.332, 1.602, 1.972) | **1.763**, 1.910, 1.883 | 1.763 | 2.950 (1295 s) |
  | 6 | 5148 / 436 | 1.840 | 2.081 (2.002, 1.954, 2.286) | **1.760**, 2.560, 2.057 | 1.760 | 3.000 (2280 s) |
  | 7 | 5200 / 449 | 2.088 | 2.085 (1.990, 2.254, 2.010) | 2.197, 2.223, 1.847 | 1.847 | 2.742 (590 s) |

  For reference, REG-17's seed 2: span λp 2.097, 2.007, 2.167; control peak 2.608 (RUN(20261110-182920_burst_l1pl350cl_r2.0_s2, gate.reg17_gate)).
- **Per-seed outcome** (`gate.reg18_pair`): exactly one valid control and one valid burst run of that seed (`gate.reg12_only`; a rerun is made only after an invalid run, never on a verdict), checked for seed, λ, force_close and closed loop (`reg10_gate`); then REG-17's readouts and **`gate.reg18_seed_outcome`**, which is REG-17's `reg17_outcome` unchanged plus two rules fixed now:
  - REG-17's order: `bad_baseline` (either run); control not `recovered` → `control_cold_surge` / `control_cold_no_surge` / `control_unclear` / `control_warm_queue`; burst `stuck` → `inconclusive` (cold side NaN) / `stuck_draining` (cold side fails) / `pass_clear` / `pass_warm_edge`; `drains`; `unclear`. The cold side is `gate.reg17_cold_side`: in every REG-8 span after the burst's end, point completion rate < min(2.0, the span's λp), and the verdict's end-window queue slope > 0.
  - **Late surge tip (review T1):** on an exposed seed (below), a control that is not `recovered` and whose KV onset comes at or after the schedule's first 120 s rate ≥ 3.2 is `control_cold_surge`, whatever the lead from that surge. The 60–240 s lead of earlier tips is not required, since an onset in the drain after 2580 s would otherwise read as a tip without a surge. An onset before the surge is not excused.
  - **No pass on missing data (review T3, R2-N6):** a `pass_warm_edge` with any NaN control waiting share, or none, is `inconclusive`.
  - **The control is judged on its own (review R2-T2):** if only the burst run has `bad_baseline` and the control is not `recovered`, the seed gets the control's label (`control_*`, with the late-tip rule), so a failed control is never hidden behind the burst run's instrument gap.
  - The anchor `onset ≥ t_first` (R2-N2): the 120 s window ending at 2435 s covers arrivals in [2315, 2435) s, and KV onset is a trailing 60 s mean, so an onset caused by that surge before 2435 s is unlikely. An onset after 2435 s may also come from seed 4's heavy watch (λp 2.28–2.51), not the surge, so an excluded seed 4 is reported as "excused, not attributed" (R2-N1).
- **Matrix decision** (`gate.reg18_outcome`, in this order):
  1. **Exclusion, fixed now from the schedule:** a seed leaves n only if its control schedule reaches a 120 s planned rate ≥ `surge_tip` 3.2 (`gate.reg18_exposed`; only seed 4, at 2435 s) **and** its outcome is `control_cold_surge`. Such a pair cannot speak to the burst: its control went cold after a surge of its own. Any other control failure stays in n, including a `control_warm_queue` caused by the same surge (asymmetric but conservative; review N1).
  2. **`surge_reading_wrong`:** any seed is `control_cold_no_surge`. Stop, as REG-17 registered: no next step is drafted before the surge reading is rethought.
  3. **`controls_not_healthy`:** 2 or more seeds left in n have a bad control: a `control_*` outcome, or a **control** verdict of `bad_baseline`. A `bad_baseline` on the burst side only is an instrument gap: in n, not a pass, not a bad control (review T2).
  4. **`too_few`:** fewer than 3 seeds left (cannot happen: only seed 4 can leave).
  5. With **k_clear** = seeds left that are `pass_clear`, and **k** = those that are `pass_clear` or `pass_warm_edge`: **`supports` if k_clear ≥ 3; `supports_edge` if k ≥ 3 but k_clear < 3** (some passes came with a queueing control, review T3); **`some` if k = 1–2; `none` if k = 0.** Reported with the one-sided 95 % Clopper–Pearson upper bound on k of n (rule H).
  - What k can show (DERIVED, `stats.cp_upper`; lower bound 1 − cp_upper(n − k, n)), n = 5: k = 3 gives p ∈ [0.189, 0.924], k = 4 [0.343, 0.990], k = 5 [0.549, 1]. "Most" is C1's count rule, not a claim that p > 0.5.
  - `unclear`, `inconclusive`, `control_unclear` and a burst-side `bad_baseline` count in n against the hypothesis, with no rerun (conservative; review N4); their number is reported (`outcome_counts`).
- **Futility stop (review T5, R2-T1), fixed now:** seeds run in the order **4, 3, 5, 6, 7**: seed 4 first, since it is the exposed seed and the likeliest control failure, so a stop can never skip it (R2-T1); then the lowest span λp first. After each seed's two runs are valid and copied, `uv run python -m analysis.gate reg18_step` is computed once. It prints only the seeds done and `continue` (True or False), never a verdict, label, outcome or count. It is False once the remaining seeds cannot reach `supports` or `supports_edge` (k + seeds left < 3), or once `surge_reading_wrong` or `controls_not_healthy` is reached (`gate.reg18_continue`). On False the queue stops and the result is computed on the seeds run. **What a stop gives up** (R2-T1, R2-T3): `some` and `none` may not be told apart; the control and surge checks of the seeds not run are lost (so a stop alone does not support any next step that rests on the surge reading, such as λ = 2.1, without the owner's review); and the seeds run were picked by order, with the stop firing on a low k. So after a stop the result is reported as "k of n on seeds …, run in the order 4, 3, 5, 6, 7 (lowest span λp first after seed 4); stopped because ≥ 3 was out of reach", **with no Clopper–Pearson bound** (`reg18_table` gives NaN): it is a count on those seeds, not a rate for λ = 2.0.
  - **A seed with no valid pair after its reruns stops the queue** (R2-T4); it is never skipped. `reg18_step` raises if a later seed has a valid run while an earlier one lacks its pair.
  - `continue` = False after 3 seeds tells the agent that k is 0 or that a control check fired (R2-N3). It does not unlock anything: marking a run invalid beyond the automatic checks still needs the owner, and a rerun decision still reads only `checks.json`.
- **Readouts, never decisive:** k_c1 (C1's test alone), counts of each outcome, per seed the span label and `stuck_unconfirmed` from `reg10_gate`, max holding c, release rate, control waiting, both runs' `surge_run` and whether each control tipped (also when `recovered`; review N6), `drain_time`, `end_window`, shock size, turn-0 share, unreleased; REG-17's seed 2 beside the table, not counted, not pooled.
  - **`backlog_persists`** (review T4): a `stuck_draining` seed whose line never emptied (`drain_time` NaN) and whose end-window queue still rose. That is a server still stuck and cold that failed the cold side in one span only. It separates "the state did not hold" from "the test at 2.0 is stricter than stuck".
  - **The lull** (`gate.reg18_lull`): each seed's lowest span λp, and whether it is below REG-14's `cold_c_max` 1.84 (fixed 2026-11-10). In such a span a cold state completing 1.73–1.84 may complete more than is planned, so the cold side can fail while a backlog persists. Seeds 3, 5 and 6 are below (1.623, 1.763, 1.760); 4 and 7 are not (2.123, 1.847). Only seed 3 is below every cold rate seen (1.72–1.90); seeds 5, 6 and 7 (1.847 is inside that range too, R2-N4) are each close to a coin flip, so `lull_agrees` is a weak readout. `lull_agrees` counts the seeds where it matched. The statistic was chosen after the schedules were seen (a forking path, review T4), so it decides nothing and no branch below depends on it.
- **What this means for the matrix, stated before it runs:** the cold side asks that every span complete less than it plans. At λ = 2.0 the cold rate sits only 8–14 % below λ, and a random schedule often has a 300 s span planned near or below it (3 of these 5 seeds). So at 2.0 the test measures "stuck and every span overloaded" as much as "stuck". The registration keeps the agreed seeds 3–7 and does not filter them by span λp (REG-17: "covariates, not seed filters"): filtering would turn "most seeds" into "most seeds without a quiet span".
- **Seed 4:** its control faces a 3.217 peak at 2435 s, inside its verdict's end window [1980, 2580) s. If seed 4's control is `recovered`, it counts as usual (its tip, if any, is reported). If it goes cold at or after 2435 s, seed 4 leaves n and is reported as a tip the surge reading predicted. 3.217 is only 0.017 above `surge_tip`, and untipped peaks have reached 3.317 (REG-17 review N2), so either result is weak evidence about the surge reading. A pass on seed 4 is also weaker evidence of metastability than one near λp 2.0, since its spans plan 2.12–2.51.
- **Prediction** (BELIEF), P(`pass_clear` or `pass_warm_edge`) per seed: seed 3 ≈ 0.10 (span 3 at 1.62), seed 4 ≈ 0.45 (heavy watch; the control may queue at λp 2.47 or tip late), seed 5 ≈ 0.35 (span 1 at 1.763; REG-17's span 1 completed 1.773), seed 6 ≈ 0.40 (span 1 at 1.760), seed 7 ≈ 0.55. Then (DERIVED, independent seeds; the review reproduced it) E[k] ≈ 1.85, P(k = 0) ≈ 0.09, P(k = 1–2) ≈ 0.66, **P(k ≥ 3) ≈ 0.26**. P(supports, k_clear ≥ 3) is lower, ≈ 0.2. Each control `recovered` ≈ 0.9 (seed 4 ≈ 0.75). Readouts if stuck: span c ≈ 1.70–1.84; end-window queue 60–200. Under the futility stop the queue runs 3 seeds with P ≈ 0.32, 4 with ≈ 0.28 and all 5 with ≈ 0.40: 4.1 seeds expected (DERIVED from the same p, order 4, 3, 5, 6, 7; the stop on a control check is left out).
- **Decision under each outcome:**
  - **`supports` (k_clear ≥ 3):** draft C1's remaining conditions at λ = 2.0 for the owner: a confirmation run with a 4500 s watch, then a drop to λ = 1 long enough for the line to empty (REG-16's calibration), then the return (conditions 5–6). Report the cell as "stuck in k of n" with the bound. C1's status changes only after the owner reviews it (a paper claim).
  - **`supports_edge`:** reported as such; the owner decides whether the confirmation run is drafted. Nothing is drafted automatically.
  - **`some`, `none` or a futility stop** (a stop: see "What a stop gives up"): report k of n with the bound and the readouts (`backlog_persists`, the lull). REG-17's pass did not generalize to most seeds at 2.0 under this test. The owner chooses, with no recommendation drafted beforehand, among: a matrix at λ = 2.1 (fewer quiet spans, more surges: REG-17's hazard, 13 of 40 seeds ≥ 3.2 within 2600 s at 2.2, 1 at 2.0); a revised per-seed test registered as a new claim; or reporting the zone as too narrow for this workload.
  - **`controls_not_healthy`:** λ = 2.0 is not reliably warm with these schedules; the owner decides.
  - **`surge_reading_wrong`:** stop; rethink before anything else is drafted.
  - **The queue stops for an operational reason** (below): no table is computed; the runs so far are reported from `checks.json` only, and the owner decides.
- **Alternatives to read against each outcome** (review):
  1. **`supports`:** the passes come from seeds whose spans are all ≥ 1.85 (4, 7, and one of 5 or 6), so a server that is merely overloaded, not metastable, could produce them, most of all on seed 4 at λp 2.5. Separated by k_clear, the control's waiting share in the same spans, and the burst run's hit rate and KV in the passing spans (cold or warm).
  2. **`some`:** the burst does leave the server stuck, but the per-span cold side fails it in a quiet span while the backlog persists. Separated by `backlog_persists` (no drain, end queue rising) on the failing seeds.
  3. **`none`:** REG-17's seed 2 was a favourable schedule (all its spans were above 2.0). Separated by span-wise c against λp: if c stays at 1.73–1.84 with the queue never emptying, the state exists and the test is too strict at 2.0.
  4. **`controls_not_healthy`:** seed 4's surge plus one instrument gap. Separated by which run and which label carries each failure.
  5. **A drain read as `stuck`** by the verdict: `end_window` (burst first tokens, unreleased turns) and the cold side separate it. **Burst size:** 407–450 burst requests; shock size against REG-12's seed-2 reference. **Heat and order over ≈ 7.5 h:** the order mixes seed with time and GPU heat (R2-N5); `gpu_steady`, `power_limit` and `span_clock` are reported per seed in run order. **Single control per seed** (rule H); closed loop, dev mode, 350 W, L1 only.
- **Stopping rule:** REG-12's, plus the futility stop. Each run once; an invalid run (other than `burst_min_kv_max`) is rerun unchanged, at most twice; no rerun on any verdict or label; a heat-invalid run once after cooling to ≤ 45 °C, a second heat failure stops the queue; a `client_error`, a burst that does not fill the pool (`burst_min_kv_max`), a limit other than 350 W, or an unexpected pre-launch check stops the queue. A rerun decision reads only `checks.json`. **No interim look** beyond `reg18_step`'s `continue` flag: no verdict, label, outcome or count is computed or shown before the queue ends.
- **Order:** seeds 4, 3, 5, 6, 7; in each, the control first, then the burst run, each after the pre-launch checks (350 W limit, ≤ 45 °C, idle GPU, clean tree at the registered commit, disk), reads saved in `docs/probe/<date>_reg18/`. Each pair is copied to the Mac and checksum-verified before `reg18_step`. The VM is reached over Tailscale; it has 8.3 GB free now.
- **Result, computed once after the queue ends:** `uv run python -m analysis.gate reg18` (`gate.reg18_table`, on the seeds run).
- **Cost** (wall-clock, including start-up and cooling: REG-17's two runs started 2688 s apart, DERIVED from 20261110-174432 and 20261110-182920): ≈ 1.5 h per seed; ≈ 6.1 h expected under the futility stop (4.1 seeds), 7.5 h for all five; worst case with every run needing both reruns ≈ 22 h plus cooling waits (review N5).
- **Code and files:** `analysis/gate.py` (`REG18`, `PASS18`, `reg18_spec`, `reg18_exposed`, `reg18_lull`, `reg18_seed_outcome`, `reg18_pair`, `reg18_outcome`, `reg18_continue`, `reg18_step`, `reg18_table`, `reg18_inputs`; `python -m analysis.gate reg18 | reg18_inputs | reg18_step`); the 10 configs; `tests/test_gate.py` (8 new: configs change only the seed; schedule facts, including exposure and the quiet spans; the patterns never pick another seed or REG-17's runs; matrix order and counting, including the burst-side `bad_baseline` and `supports_edge`; the per-seed rules, including review T1's late-tip trace, R2-T2's control behind a burst-side `bad_baseline`, and R2-N6's empty shares; the futility stop and seed 4 first; `reg18_step` never skips a seed (R2-T4); a missing run is refused). `reg18_pair` refuses to run if REG-18's λ differs from REG-17's, since `reg17_cold_side` judges against REG-17's λ (review N2).
- **Not changed:** harness, checks, thresholds, PROTOCOL, REG-17's functions and result.

### Adversarial review (separate subagent; it saw only the draft, its diff, and the code and configs those call; it opened no runs and no other docs). Round 1, on the first draft (order 3, 5, 6, 4, 7 was not yet in it; k counted `pass_warm_edge`). Verbatim:

>
> **Reproduced.** `uv run pytest -q tests/test_gate.py -k "reg18 or reg17"` gives 10 passed. `reg18_inputs` matches every value in the draft's table: request counts, λp baseline, watch and thirds, span λp, lull, lull_below = {3, 5, 6}, control peaks and times. Only seed 4 is exposed (3.217, t_first 2435 s), and the control schedule equals the burst's session rows for every seed. Per-span max_c is 1.45–1.81. The draft's per-seed prediction gives P(k ≥ 3) = 0.258 and E[k] = 1.85 (DERIVED, exact Poisson-binomial). Cost: 10 × 2688 s = 7.47 h. I found no mismatches.
>
> **T1 (should-fix): a late tip on seed 4 is read as `surge_reading_wrong` and stops the whole matrix.** `surge_run` sets peak_tip to the maximum over [onset−240, onset−60]. I ran it on seed 4's schedule. peak_tip is 3.217 for KV onset ≤ 2675 s, 3.142 at 2680, 2.85 at 2700 and 2.11 at 2800. Trace: the 2435 s surge queues seed 4's control, so its verdict is `slow_drain` or `stuck`; KV onset comes at 2700 s during the drain; peak_tip 2.85 < 3.2 → `control_cold_no_surge` → `surge_reading_wrong` for the whole matrix. The surge reading actually predicted this tip; it only ended outside the 60–240 s lead fixed from earlier runs. Fix before registering: either set seed 4's tip window to "onset after t_first" for exposed seeds, or register that onset > t_first + 240 is read as `control_cold_surge_late` (excluded, not a stop).
>
> **T2 (should-fix): a burst-side `bad_baseline` counts as a bad control.** `reg17_outcome` returns `bad_baseline` if *either* run is bad, and `reg18_outcome` adds every `bad_baseline` to `bad`. Trace: two burst runs get `bad_baseline` and all five controls are `recovered` → `controls_not_healthy`, and the draft reads that as "λ = 2.0 is not reliably warm". That reading is false. Fix: pass the control verdict separately, or count `bad_baseline` as an instrument gap.
>
> **T3 (should-fix): k counts `pass_warm_edge`, including when control waiting is NaN.** `pass_warm_edge` means the control queued in more than half the scrapes of some span. On seed 4 (span λp 2.42/2.12/2.51 with a 3.2 surge in span 3), a warm server that is merely overloaded can give c < 2.0 and a positive end slope in the burst run while its control queues. That is exactly the "load, not burst" alternative. NaN shares also fall into `pass_warm_edge` (`clear` is False → warm_edge), so an instrument gap counts as a pass. Recommend: NaN → `inconclusive`, and `supports` requires k_clear ≥ 3. Otherwise label it `supports_edge` and don't let it trigger the confirmation draft automatically. The test currently fixes the opposite (`k == 5` with one warm_edge).
>
> **T4 (should-fix): the lull argument is wrong as stated, and its outcome is partly fixed in advance.** The cold side compares c with λp in each span, not λp with 1.84. A span with λp 1.76 fails only if c ≥ 1.76; the cold rates seen are 1.72–1.90, so seeds 5 and 6 are close to coin flips, not "arithmetic". Seed 3 (λp 1.623, below every cold rate seen) is close to certain to fail, so it adds about one forced "agree" to `lull_agrees`. "The queue cannot keep growing" is also not what the test checks: a backlog of 76–120 shrinking at about 0.1 req/s survives a 300 s lull, and the server stays stuck and cold, yet the cold side fails it. So the test at 2.0 measures "every span overloaded" as much as "stuck". Rule A5: the 1.84 threshold predates the schedules, so this is not a threshold breach. But choosing the "lowest span" statistic after seeing these seeds is a forking path. It is acceptable as a readout only if the `some` branch does not use `lull_agrees = 5/5` to recommend a seed rule. Rewrite the sentence and either drop that branch's dependence on the lull or register the span-wise c vs λp comparison as the readout.
>
> **T5 (should-fix): low decision value for the cost.** Only `supports` (P ≈ 0.26) leads to a concrete next step. `some`, `none` and `controls_not_healthy` all end in "owner decides", with λ = 2.1 as the common option. Cheaper design with the same seeds and configs: register a futility stop. Run seeds in the order 3, 5, 6, 4, 7 (the predicted fails first), counting only per-seed outcomes. Once three seeds are non-pass, `supports` is impossible, so stop and report "≤ 2 of 5". This is a pre-registered stopping rule, not an interim look at a threshold. Expected saving is about 1.5–3 GPU h, and the decision under each reachable outcome is unchanged. Alternatively, ask the owner whether `some` and `none` lead to different actions; if not, the futility stop costs nothing.
>
> **N1.** An exposed seed is excluded only when it is cold-surge; a `control_warm_queue` from the same surge stays in n as a bad control. This is asymmetric but conservative. State it.
>
> **N2.** `reg17_cold_side` uses `REG17["lam"]` (2.0), which equals REG-18's λ. It is correct, but referencing REG18 makes the dependence explicit.
>
> **N3.** `reg12_only` raises on more than one match, and glob prefix collisions raise rather than pick a wrong run. `reg10_gate` then re-picks the same single run. This is fine.
>
> **N4.** `unclear`, `inconclusive` and `control_unclear` count in n against the hypothesis, with no rerun. This is conservative. Report how many there are.
>
> **N5.** Worst case of about 22 h ignores cooling waits. "≈ 7.3 GPU h" mixes wall-clock time with arrival time; give one number.
>
> **N6.** The surge test on a `recovered` control is ignored. If seed 4's control tips after 2580 s, the seed still counts. Report `surge_control.tipped` per seed.
>
> ### Strongest alternative explanation
> - **`supports`:** passes come from seeds whose spans all have λp ≥ 1.85 (4, 7, plus one of 5 or 6), so overload of a server that may be warm, not metastability, produces them. This is worst on seed 4 at λp 2.5. Separated by k_clear, the control's waiting share in the same spans, and the burst run's KV/hit-rate (cold vs warm) in the passing spans.
> - **`some`:** the burst does leave the server stuck, but the per-span cold side fails it in a lull while the backlog persists. Separated by `drain_time` (NaN = never emptied) and end-window q on the failing seeds: a stuck-but-failed seed has no drain and a positive q.
> - **`none`:** REG-17's seed 2 was a favourable schedule (its spans were all above 2.0). Separated by span-wise c vs λp: if c stays at 1.73–1.84 with the queue never emptying, the state exists and the test is too strict at 2.0.
> - **`controls_not_healthy`:** a burst-side `bad_baseline` (T2), or seed 4's surge plus one instrument gap. Separated by which run carries each label.
>
> ### Verdict
> Not ready to register. Fix T1 and T2, which are code paths that produce the wrong decision, and T3 (NaN → pass) before approval. Rewrite T4's lull text and decouple the `some` branch from `lull_agrees`. The run can change one decision (draft C1's confirmation at 2.0, P ≈ 0.26). At ≈ 7.5 GPU h that is justifiable only with the T5 futility stop, or if the owner states that `some` and `none` lead to different actions.

- **Changed because of it:**
  - T1: `gate.reg18_seed_outcome`: on an exposed seed, a control that went cold at or after the surge is `control_cold_surge` whatever the lead. Tested on the review's trace (onset 2700 s, peak_tip 2.85).
  - T2: only a control-side `bad_baseline` counts as a bad control. Tested.
  - T3: a NaN control waiting share gives `inconclusive`; `supports` needs k_clear ≥ 3, and `supports_edge` (k ≥ 3, k_clear < 3) drafts nothing automatically. Tested.
  - T4: the quiet-span text rewritten (only seed 3 is below every cold rate seen); no branch depends on it; `backlog_persists` added as the readout that separates "the state did not hold" from "the test is stricter than stuck".
  - T5: a futility stop (`gate.reg18_continue`, `gate.reg18_step`), with the predicted fails run first. Tested.
  - N1, N4, N6: stated or reported. N2: `reg18_pair` refuses a λ other than REG-17's. N5: cost given as wall-clock only.

### Adversarial review, round 2 (a separate subagent; same inputs plus the round-1 review and the revised draft and diff). Verbatim:

>
> **Round-1 fixes.** `uv run pytest -q tests/test_gate.py -k "reg18 or reg17"` gives 12 passed. The code and text fix T1 (late tip at or after `t_first`), T2 (only a control-side `bad_baseline` counts as a bad control), T3 (a NaN share is now `inconclusive`, and `supports` needs k_clear ≥ 3), T4 (the lull text is rewritten and no branch uses it) and T5 (futility stop). N1, N2, N4, N5 and N6 are addressed in the text or code. N3 needed no change. The per-seed numbers are consistent (DERIVED from the draft's p): P(stop after 3 seeds) = 0.9·0.65·0.6 = 0.351. P(stop after 4) = P(k₃ = 1)·0.55 = 0.462·0.55 = 0.254. P(all 5) = 0.395. E[seeds] = 4.04, and 4.04 × 1.49 h ≈ 6.0 h. Two of the fixes create new problems, below.
>
> **R2-T1 (blocking): the futility stop can hide `surge_reading_wrong` and `controls_not_healthy`. The claim "every decision is the same with or without the stop" is false.** In `reg18_outcome`, `surge_reading_wrong` and `controls_not_healthy` come before any count. Seed 4 is the exposed seed and the one most likely to have a control failure (draft: P(recovered) ≈ 0.75), and the order puts it fourth. Trace, checked on the pure functions: seeds 3, 5 and 6 give `stuck_draining`, `drains`, `drains`. Then k = 0 with 2 seeds left, `reg18_continue` returns False, and the queue stops. The result is a futility stop, and the λ = 2.1 option becomes available. If seed 4 had run, a control onset before 2435 s would give `control_cold_no_surge`, so the result would be `surge_reading_wrong` ("rethink before anything else is drafted"). The λ = 2.1 option depends on the surge-hazard reading, so the decision changes. This happens with probability ≈ 0.35 × P(seed 4's control fails without a surge). Fix, one of:
> - (a) Run seed 4 first, or at least before the stop can fire.
> - (b) Under a futility stop, block any next step that relies on the surge reading until seed 4's control has run alone.
> - (c) Say plainly that a stop forfeits the surge and control checks on the seeds not run.
>
> **R2-T2 (should-fix): a burst-side `bad_baseline` masks a failed control.** `reg17_outcome` returns `bad_baseline` before it looks at the control. `reg18_outcome` then counts a bad control only if the control verdict is `bad_baseline`. Trace (run on the pure functions): burst `bad_baseline`, control `stuck` with a tip at 1500 s and peak_tip 2.4. The outcome is `bad_baseline` and `n_control_bad` is 0, so no `surge_reading_wrong` fires even though the control tipped without a surge. With another `control_warm_queue`, the matrix reads `some` instead of `controls_not_healthy`. Fix: classify the control on its own (verdict ≠ `recovered`, tip rule) whatever the burst run's verdict, and count it in `bad` and in the surge check.
>
> **R2-T3 (should-fix): k of n after an early stop is not a sample of seeds, and the bound is optimistic.** A stop after 3 or 4 seeds reports k of n on the seeds that were chosen *because* their lowest span is lowest (3, 5, 6). The stop also fires only when k is low, so the Clopper–Pearson upper bound is biased downward under optional stopping. Fix: when `stopped_early`, report "k of n on seeds 3/5/6[/4], ordered by lowest span λp; the stop was triggered by low k". Report no bound, or label it as conditional and not a rate for λ = 2.0.
>
> **R2-T4 (should-fix): `reg18_step` and `reg18_table` drop seeds after a gap.** `done` stops at the first seed in the order without both valid runs. The stopping rule does not say what happens after a non-heat invalid run whose two reruns are used up. If the queue goes on to the next seed, that seed's valid runs are never counted. `remaining` still counts the missing seed, and `reg18_table` silently computes on the prefix. Fix: register that a seed with no valid pair after its reruns either stops the queue or counts in n as a non-pass. Then make `reg18_step` raise if valid runs exist for a seed after the gap.
>
> **R2-N1.** The late-tip rule excuses any onset ≥ 2435 s, including one at 2550 s or later that comes from seed 4's heavy watch (λp 2.28–2.51) and not from the surge. Report it as "excused, not attributed", not as "a tip the surge reading predicted".
>
> **R2-N2.** The anchor `onset >= t_first` is reasonable. The 120 s window is [g − 120, g) and `kv_onset` is a trailing 60 s mean, so a surge-driven onset before 2435 s is unlikely. Say this in the text.
>
> **R2-N3.** `continue` leaks a coarse outcome (False after 3 seeds means k = 0 or a bad-control or surge stop). This cannot be avoided with a futility stop. Restate that marking a run invalid beyond the automatic checks still needs the owner.
>
> **R2-N4.** Seed 7's lowest span (1.847) is inside the cold range 1.72–1.90, yet it is listed as "not below". Seed 7 is near a coin flip like 5 and 6, so `lull_agrees` mislabels it.
>
> **R2-N5.** Running the seeds in a fixed order mixes seed with time and heat (low-lull seeds run first, on a cool GPU). Report `gpu_steady` and `span_clock` per seed in run order.
>
> **R2-N6.** `reg18_seed_outcome` keeps `pass_warm_edge` when `control_waiting` is empty, because `all([])` is True. This cannot happen with 3 spans, but a guard would make that explicit.
>
> **Verdict.** Not ready for the owner's approval. Fix R2-T1 (reorder so seed 4 runs before the stop can fire, or limit what a stop allows) and R2-T2 (classify the control independently of the burst's `bad_baseline`) in code, with tests for both traces. Rewrite the early-stop reporting (R2-T3) and register the rule for an exhausted rerun (R2-T4). The minor items are text only. The cost and prediction arithmetic hold for the current order. If seed 4 moves earlier, recompute E[seeds] (it will rise above 4.0).

- **Changed because of it:**
  - R2-T1: the order is now 4, 3, 5, 6, 7, so the stop can never skip seed 4; "What a stop gives up" states that a stop loses the control and surge checks of the seeds not run, and supports no next step that rests on the surge reading without the owner's review. E[seeds] recomputed: 4.1, ≈ 6.1 h. Tested (seed 4 first).
  - R2-T2: `reg18_seed_outcome` judges the control on its own when only the burst run has `bad_baseline`. Tested on the review's trace (control tip at 1500 s, peak_tip 2.4 → `control_cold_no_surge`).
  - R2-T3: after a stop `reg18_table` reports no bound, and the result is worded as a count on the seeds run.
  - R2-T4: a seed with no valid pair after its reruns stops the queue; `reg18_step` raises if a later seed has a valid run. Tested.
  - R2-N1, N2, N3, N4, N5: in the text. R2-N6: no shares gives `inconclusive`. Tested.
- **Not covered:** no third review round; the round-2 fixes were checked by tests only. The run waits for the owner's approval of this registration.
