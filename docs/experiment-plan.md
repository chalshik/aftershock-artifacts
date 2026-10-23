# Experiment Plan: Stage 1 — Harness

Oct 22, 2026 · @Nurmukhammed

## Purpose

Stage 1 builds the measurement harness and uses it to describe one healthy, production-like vLLM server under realistic load. Nothing is broken on purpose yet: no triggers, no shrunken memory, no ablations.

Stage 1 answers two questions:

- **Can we trust the measurements?** The same run repeated gives the same numbers, and every run passes automatic checks.
- **What does the healthy server look like?** Its load–latency curve and its capacity, with prefix caching on and off. Every later stage is compared against this baseline.

## Fixed choices

The setup is a single replica: one vLLM engine, one GPU, one KV cache. Each production feature below is either kept out on purpose or built but switched off, so it can become an experiment factor later.

| Production feature | Stage 1 | Why |
| --- | --- | --- |
| Router across replicas | Out | Adds its own feedback loops; the mechanism under test lives inside one server |
| Gateway queue with a concurrency cap | Built into the load generator, **off** | A cap limits the running batch and could hide or shift the failure; tested later as a mitigation |
| vLLM's own waiting queue | In | Part of the server; measured as Q |
| KV offloading to CPU or disk | Off | Refills the cache from outside and hides eviction; tested later as a factor |
| Cross-instance KV sharing | Off | Same reason as offloading |
| Client retries and timeouts | Off | The claim is that the failure needs neither |

In the paper, state this as scope: "a single replica, served directly". It is a real configuration, not the only one.

## Environment and GPU check

The server runs on the RTX 3090 under Linux; the Mac is used only for writing code and analysis.

1. **Pin vLLM.** Install the latest stable release (not the developer preview) in a clean `uv` environment and never upgrade it during the study.
2. **Match the driver and CUDA** to what that vLLM release requires.
3. **Check the GPU is visible:** `nvidia-smi` lists the 3090.
4. **Start vLLM once** and read its startup log: it should report the GPU and the KV cache size. Record that KV size per model; it replaces the estimates below.
5. **Send one test request** and get an answer back.
6. **Save an environment snapshot** (`env.json`): vLLM version, Python, CUDA, driver, GPU name, and your code's git commit. Every run includes it.

## Model and server

Qwen3-4B is the main model; Qwen3-1.7B is used only while debugging the harness. Both use plain full attention on every layer (no sliding window, per their `config.json`), so vLLM's prefix cache behaves as its design doc describes.

| Model | Role | KV per token (bf16) | Weights (approx.) |
| --- | --- | --- | --- |
| Qwen3-1.7B | Debugging the harness | 112 KiB | ≈ 3.4 GB |
| Qwen3-4B | Main Stage 1 model | 144 KiB | ≈ 8 GB |

KV per token = 2 × layers × KV heads × head size × 2 bytes, from each model's config. Weights = 2 bytes × the nominal parameter count.

**Server settings**

- vLLM **defaults**, plus prefix caching on. Defaults are what "production-like" means here; the KV pool is not shrunk in Stage 1.
- KV cache metrics on (`--kv-cache-metrics`), so block lifetimes and reuse gaps are recorded.
- Every setting, default or not, is written into the run's config file.
- Check whether vLLM's own admission queue limit is on by default (`vllm:admission_rejections` exists). If it is, record it: it is a throttle inside the "direct" baseline.

## Workload

The load is multi-turn chat sessions whose context grows each turn, because prefix caching only behaves realistically when prompts share prefixes. Random prompts are used only for the first smoke test.

- **Sessions:** each turn's prompt is the whole conversation so far plus a new message. The previous turn's context is the reusable prefix.
- **Open schedule:** session start times and turn send times are generated before the run from a fixed seed and saved. A turn is sent at its scheduled time whether or not the previous turn has finished, so the server's speed never slows down the arrivals.
- **Recorded replies:** because turns don't wait for answers, each turn carries a pre-written reply for the previous turn, not the model's real one. The cache hit therefore covers the previous turn's prompt, not its generated tokens.
- **Token IDs, not text:** prompts are sent as token IDs, so a chat template can't change tokens between turns and silently break prefix matching. (Check that the completions endpoint accepts token IDs in the pinned version.)
- **Output length:** fixed per request, so runs are comparable.
- **Report** sessions, turns per session, prompt lengths and turn gaps for every workload.

## Code

Six code files; all except the analysis notebook run on the same computer as the vLLM server (the one with the GPU); `run.py` is the only thing you launch.

&#91;embedded content: stage 1 harness · 4 processes, 1 run folder\]

| File | Job | Runs as |
| --- | --- | --- |
| `env_snapshot.py` | Writes versions, GPU, driver and code commit to `env.json` | Called by `run.py` |
| `loadgen.py` | Reads the schedule, sends requests at their planned times, writes one line per request. Contains the optional gateway layer (off in Stage 1) | Own process, one async program simulating all sessions |
| `recorder.py` | Every 1 s reads vLLM's `/metrics` and GPU stats, writes them to files, prints h, N, Q, KV usage, client lag and GPU clock to the terminal | Own process |
| `run.py` | Writes the config, generates the schedule, starts vLLM, waits until it is ready, starts the recorder and load, stops everything in order, runs the checks | Parent process |
| `checks.py` | Marks each run valid or invalid, with the reason | Called by `run.py` |
| `analysis.ipynb` | Plots over time and the load–latency curve, read only from run folders | Afterwards, on any machine |

vLLM's own output goes straight to `server.log`; it needs no collector. Pin the load generator and recorder to CPU cores separate from vLLM, and confirm with the client-lag check that the load generator never fell behind.

## What each run records

Each run writes one folder; the raw files are the record, and every figure is regenerated from them.

```
runs/<run_id>/
  config.yaml        # every setting: model, λ, workload, seeds, SLOs
  env.json           # versions, GPU, driver, code commit
  schedule.parquet   # planned send time of every request, written before the run
  requests.jsonl     # one line per request: id, session, turn, planned and actual send,
                     #   first-token time, end time, prompt and output tokens, status
  metrics.jsonl      # one line per scrape: time + raw vLLM metric values
  gpu.jsonl          # one line per second: power, power limit, SM clock, temperature, memory
  events.jsonl       # start, warm-up end, anything unusual
  server.log         # vLLM output
```

- One file per run, one line per request; each line carries its session id, so sessions are filtered afterwards.
- Counters are stored as raw totals; rates are computed later from differences, which also reveals a server restart (a counter going down).
- All files use the same clock on the same machine.
- Getting first-token time requires streaming responses.

## What we measure

The main number is the share of requests that were fast enough; everything else explains it.

**Main: percent fast (SLO attainment)**

- Pick a speed limit, mainly on first-token time. In Stage 1 the limit is not fixed yet: Stage 1 measures how fast the healthy server is, and the limit is set just above that for later stages.
- Each second, take the requests that **arrived** in that second and count how many met the limit.
- Requests still unfinished when the run ends count as misses.

**Helpers**

| Number | Source | Tells you |
| --- | --- | --- |
| Throughput (completions per second) | Client log | Whether the server keeps up with the arrival rate |
| Waiting line Q | `vllm:num_requests_waiting` | Whether requests pile up |
| Running batch N | `vllm:num_requests_running` | How many requests share the GPU |
| Hit rate h | Δ`vllm:prefix_cache_hits` ÷ Δ`vllm:prefix_cache_queries` | How much prefill the cache saves |
| Recomputed prefill per second | rate of `vllm:prompt_tokens` − `vllm:prompt_tokens_cached` | Work the cache did not save |
| KV usage | `vllm:kv_cache_usage_perc` | How full the memory pool is |
| Preemptions | `vllm:num_preemptions` | Whether running requests get pushed out |
| Block idle time before eviction | `vllm:kv_block_idle_before_evict_seconds` | How long a cached prefix survives (R) |
| GPU SM clock and temperature | `gpu.jsonl` | Whether the GPU throttled |

Throughput alone cannot show trouble: a struggling server can still finish as many requests per second as arrive, just each one late. That is why percent fast is the main number.

## Run checks

A run counts only if every check passes; a failed run is kept but marked invalid, with the reason.

| Check | Catches |
| --- | --- |
| Client lag (actual − planned send time) stays below a set limit | Load generator fell behind, so arrivals were not really open |
| No timeouts, retries or connection errors | Breaks the no-retry condition |
| Sent = completed + still running at the end, and matches vLLM's success counter | Lost or duplicated requests |
| Counters never go down; no gap longer than about 2 s between scrapes | Server restart, recorder stall |
| SM clock steady, no thermal throttling | Hardware slowdown mistaken for a server effect |
| Measured arrival rate matches the configured λ | Wrong schedule or generator bug |

## Stage 1 runs, in order

Each step starts only once the one before works.

1. **Smoke test.** Qwen3-1.7B, random prompts, low load. The pieces start, talk to each other, and write their files.
2. **First real run.** Qwen3-4B, session workload, one moderate λ. All checks pass and the plots look sensible.
3. **Repeat.** The same config twice. The two runs give nearly the same numbers.
4. **Load sweep, prefix caching on.** λ from low to high in steps, each held long enough to settle. Result: the load–latency curve, with latency flat and then rising sharply at the server's capacity (μ\_warm).
5. **Load sweep, prefix caching off.** Same steps. Result: the capacity without caching (μ\_off). The gap between the two curves is the range where later experiments happen.
6. **No-trigger long run.** One λ inside that gap, held much longer than usual. The server should stay healthy the whole time; if it degrades on its own, that λ can't be used later.

## Done when

Stage 1 is finished when all of these hold:

- [ ] Repeated runs with the same config agree within a tolerance you set
- [ ] Every run up to the capacity knee passes all checks
- [ ] Load–latency curves exist with prefix caching on and off, and μ\_warm and μ\_off are known
- [ ] A λ inside the gap stays healthy in a long run without any trigger
- [ ] The speed limit (SLO) for later stages is fixed, based on the healthy server's measured latency
- [ ] The harness can switch on the gateway layer and a trigger without being rewritten

## Open questions to settle during Stage 1

Each is answered by reading the pinned vLLM version's docs or source, or by a quick test on the machine.

- [ ] Is vLLM's admission queue limit on by default? If yes, the baseline already has a throttle.
- [ ] Does the completions endpoint accept token IDs as the prompt?
- [ ] Does vLLM report cached tokens per request? If yes, log it: it gives hit data per request, finer than 1-second sampling.
- [ ] Exact flag names for prefix caching, KV metrics and the sequence cap at the pinned version (`vllm serve --help`).
- [ ] Does the recorder slow the server? Compare μ\_warm with and without it.
- [ ] Enough CPU cores to keep the load generator and recorder off vLLM's cores?
- [ ] Real KV capacity per model from vLLM's startup log, replacing the estimates.

# Stage 2 — Reproducing the failure

## Purpose

Stage 2 shows that the server can get stuck after a short shock and stay stuck once the shock is over, and shows the loop that keeps it stuck. The method in one line:

> **Start healthy → push briefly → stop pushing → see whether it comes back.**

- **C1, the symptom:** percent fast stays low after the trigger has ended, at the same load as before.
- **C2, the cause:** the sustaining loop. Cache lost → slow requests → big running batch → no room for cache → cache stays lost.

The goal is not to make the server as slow as possible. Heavy overload is always slow and proves nothing; what matters is slowness that outlives its cause.

## Key words

The server has two capacity limits, one with a working cache and one without, and the failure can only happen at loads between them.

| Word | Meaning |
| --- | --- |
| **Load (λ)** | Requests arriving per second |
| **μ\_warm** | Highest load the server keeps up with when the cache works. Measured in Stage 1 with prefix caching on |
| **μ\_off** | Highest load the server keeps up with when nothing comes from the cache. Measured in Stage 1 with prefix caching off |
| **Danger zone** | Loads between μ\_off and μ\_warm: fine while the cache works, too much once it is lost |
| **Trigger** | A short, controlled shock that ends: a cache wipe, a burst of extra load, a temporary power cap |
| **Percent fast** | Share of requests that met the speed limit (SLO); the goodput measure from Stage 1 |
| **Recovered** | Percent fast returns to its pre-trigger level |
| **Stuck** | Percent fast stays low after the trigger has ended, at the same load. The metastable failure |

The three zones of load:

- **Below μ\_off (safe):** even a server with no cache help keeps up, so it always recovers.
- **Between μ\_off and μ\_warm (danger zone):** where Stage 2 runs.
- **Above μ\_warm (overload):** too much load even with a perfect cache. Always slow, but that is overload, not this failure.

## Inputs from Stage 1

Stage 2 starts only when Stage 1 has delivered these; each one is fixed before the first Stage 2 run and not changed after seeing results.

| Input | Used for |
| --- | --- |
| μ\_off and μ\_warm | Placing the test loads inside the danger zone |
| Speed limit (SLO) | Counting percent fast |
| Recovery time τ: how long the healthy server takes to settle after a normal load change that wipes nothing | Setting how long to watch after a trigger |
| A load that stays healthy for a long run with no trigger | The first test load, already proven safe without a shock |
| A harness that can switch on triggers | Running Stage 2 without rewriting code |

If μ\_off and μ\_warm turn out almost equal, the danger zone is too narrow to test. Then shrink the KV pool on purpose: big enough to hold the cached sessions beside the normal running batch, but not beside the bigger batch that forms after a cache loss. Repeat the Stage 1 sweeps at that pool size, and state it in the paper as a deliberate setting, reporting the ratio of pool size to the sessions' cached context.

## One run, step by step

Every Stage 2 run has the same three phases at one fixed load; only the trigger changes between runs.

1. **Baseline.** Run at load λ, inside the danger zone, until percent fast and hit rate are steady. This is the "before" picture.
2. **Trigger.** Fire the shock at time t = 0 and let it end. For a burst or a power cap, it lasts a fixed, recorded duration; a cache wipe is instant. The load returns to λ, or never left it.
3. **Watch.** Keep the load at exactly λ and change nothing else, for a fixed window much longer than the recovery time τ (K × τ, with K chosen beforehand).

Then the run ends, the checks from Stage 1 run, and the verdict rules below decide the outcome. Retries and timeouts stay off in every run.

## Triggers, in order

Start with the cache wipe: it changes only the cached state and adds no extra requests, so a stuck result cannot be blamed on leftover backlog from extra load.

| Order | Trigger | How | Size you can vary |
| --- | --- | --- | --- |
| 1 | Cache wipe | vLLM's `reset_prefix_cache`, without touching running requests | Instant; vary only the load |
| 2 | Load burst | Extra requests for a fixed time, then back to λ | Burst height and duration |
| 3 | Power cap | Lower the GPU power limit for a fixed time, then restore it | Cap level and duration |
| 4 | Engine restart | Stop and start the server while load continues | Downtime |
| 5 | Popularity shift | Switch to a different set of active sessions | How many sessions switch |

One trigger at a time, and every trigger logs its exact start and end time. Triggers 4 and 5 come only after 1 to 3 work.

## Verdict rules

Each run gets one of three verdicts, judged in the watch window after the trigger has ended, using thresholds written down before the first run.

| Verdict | Percent fast | Waiting line | Hit rate |
| --- | --- | --- | --- |
| **Recovered** | Back to its baseline level before the window ends | Back to its baseline length | Back to baseline |
| **Slow drain** (not metastable) | Still low but climbing | Shrinking steadily | Climbing |
| **Stuck** | Still low at the end of the window | Flat or growing | Stays low |

**Why "slow drain" is separate:** a trigger can leave a long waiting line that takes a while to clear even when no loop holds the server down. If the line is shrinking, the server is recovering, just slowly. Calling that "stuck" would be wrong.

**"Stuck" counts as the metastable failure only when all three hold:** the trigger has ended, the load is the same as before, and the same load without a trigger stays healthy (control run below).

## Control runs

Control runs prove that the trigger and the cache caused a stuck result, not the load itself.

| Control | Same as the test run, except | Expected result | Proves |
| --- | --- | --- | --- |
| **No trigger** | No shock at all | Stays healthy for the whole run | The load alone does not cause the failure |
| **Prefix caching off** | Caching disabled; use the load burst, since there is no cache to wipe | Server returns to its single (slower) level; never stuck at a lower level than before | The cache is needed for the failure |
| **Prefixes protected** (later) | Cached prefixes of active sessions cannot be evicted during the trigger | Recovers | Eviction by the running batch is the link that keeps it stuck |

The no-trigger control is run at every load used in Stage 2. The protected-prefixes control may need a code change or a feature vLLM does not have; see open questions.

## Showing the loop

Low percent fast shows that the server is stuck; the loop shows why. Two kinds of evidence are needed: watching the loop happen, and breaking it.

&#91;embedded content: sustaining loop · 5 links, starts at the trigger\]

**Watch it happen.** For every stuck run, one figure stacks the helper metrics on the same time axis, with the trigger at t = 0. They should move in this order and then stay there:

1. Hit rate drops.
2. Recomputed prefill per second rises.
3. Running batch N grows (same load × longer time per request = more requests running at once).
4. KV memory fills; cached prefixes are evicted sooner (shorter idle time before eviction).
5. Hit rate stays low, because new cache entries are evicted before their session's next turn arrives.

Preemptions stay low throughout. Frequent preemptions would point to a different known failure, the eviction limit cycle of Ao et al., not this loop.

**Break it.** The prefix-caching-off and protected-prefixes controls each cut one link. If the server stops getting stuck when a link is cut, that link is part of the cause.

## What we vary: the danger-zone map

The main Stage 2 result is a map: for each combination of load and trigger size, does the server recover or get stuck?

| Vary | Values | Learn |
| --- | --- | --- |
| Load λ | Several points across the danger zone, plus one just below μ\_off as a sanity check | At which loads the server can get stuck |
| Trigger size | For bursts and power caps: a few heights and durations. Cache wipe has no size | How big a shock it takes |
| KV pool size | Only if needed to open up the danger zone | How much memory protects the server |

**Repeats.** Near the edge of the danger zone, the same setup may sometimes recover and sometimes get stuck, just by chance. Run each cell several times with different seeds and report "stuck in k of n runs", not a single yes or no.

**Start small.** Begin with the cache wipe at three or four loads. Add trigger sizes and pool sizes only after those cells give clear results.

## Up-then-down ramp

A second way to show two states at one load, without a separate trigger: raise the load step by step past μ\_warm, then lower it step by step back down.

- **Going up**, percent fast stays high until the load passes the server's limit, then drops.
- **Coming down**, if the server is metastable, percent fast stays low even at loads where it was fine on the way up. It recovers only once the load is lower still.
- The **gap between the two curves** is the "two states at one load" picture for C1.

**Dwell time matters.** Each step is held for a fixed time. If the steps are too short, the server simply hasn't caught up yet, and that also creates a gap. Repeat the ramp with longer steps: a gap that shrinks to nothing was just lag; a gap that stays is real.

## Outputs and done criteria

Stage 2 produces four figures, all regenerated from run folders:

1. **The danger-zone map:** load × trigger size, each cell "stuck in k of n runs".
2. **The loop figure:** one stuck run's helper metrics stacked on one time axis, trigger at t = 0.
3. **The ramp figure:** percent fast against load, going up and coming down, at two or more dwell times.
4. **The control figure:** the same load with trigger, without trigger, and with prefix caching off, side by side.

Stage 2 is done when:

- [ ] At least one load inside the danger zone gets stuck in most repeats, while its no-trigger control stays healthy
- [ ] Stuck runs show the loop metrics moving in the expected order, with few preemptions
- [ ] With prefix caching off, the same setup does not get stuck
- [ ] The ramp gap stays when dwell time is increased

If no load gets stuck even after shrinking the KV pool, that is a result too: write down the conditions tested and why the loop did not hold.

## Stage 2 open questions

The first one blocks the first trigger, so check it before anything else.

- [ ] Can `vllm serve` reset the prefix cache over HTTP at the pinned version? If not, wrap the engine in a small server of our own that exposes it.
- [ ] What exactly does `reset_prefix_cache` do to requests that are running at that moment? Read the source before trusting the cache-wipe trigger.
- [ ] Can the power limit be changed on the 3090 while vLLM runs, and how fast does it take effect?
- [ ] Is there any way to protect cached prefixes from eviction in vLLM, or does the protected-prefixes control need a code change?
- [ ] K, the watch window length, the stuck thresholds and the number of repeats per cell: fix them from Stage 1 numbers before the first Stage 2 run.
- [ ] Does turn spacing matter? If sessions come back very quickly, their prefixes may survive even a big batch. Try at least two turn gaps.
