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

# Stage 2, revised 2026-11-12 — From reproducing the failure to mapping its boundary

Added at the end so that the text above keeps its line numbers (other docs cite them). Where this section and the text above differ, this section rules; the change is logged in decisions.md 2026-11-12 [DECISION]. Nothing here is a registration: every run and every analysis below still needs its own `[REG]`, a rule F review and the owner's approval, and the numbers given are planning estimates.

## Why the plan changed

Three preprints (arXiv 2611.02543, 2611.08902, 2611.13412) now report the stuck state on real engines, one of them on the vLLM version pinned here. Showing that the failure exists is no longer the goal. Stage 2 now asks where it does and does not happen, and whether the published models put that boundary in the right place. The method stays the same:

> **Start healthy → push briefly → stop pushing → see whether it comes back.**

What changes is what is compared: not only "burst against no burst", but the same burst under two kinds of client, two kinds of reuse, and several context lengths.

## Claims this stage serves (full text: `docs/claims.md`)

| Claim | Question in one line |
| --- | --- |
| **P0** (C1 and C2, now a cited premise) | Does the stuck state appear here too, at chat-sized contexts and close to the cold capacity? |
| **K1** | Does it need turns that wait for the previous reply? |
| **K2** | Does the danger zone widen with context, and vanish when all reuse comes from one shared prompt? |
| **K3** | Do the published models predict our numbers? |
| **K4** | Near the warm capacity, does the healthy state end at an arrival surge? |
| **K5** (optional) | Do cache signals warn before latency does? |

## Key words added

| Word | Meaning |
| --- | --- |
| **Cold floor** | Completions per second of the saturated server with caching off (μ\_sat,off in `docs/definitions.md`). The other papers call this the all-miss capacity |
| **Margin** | Load divided by the cold floor. Setup L1 at λ = 2.0: 2.0 / 1.681 = 1.19. Reported for every cell so that cells compare across papers |
| **Open-loop turns** | Each turn is sent at its scheduled time, whether or not the previous reply has arrived |
| **Closed-loop turns** | The next turn is sent a think time after the previous reply (`workload.sessions.closed_loop`) |
| **Cache gain** | The warm hit rate of the no-trigger control |
| **Shared-only workload** | Every reusable token is in one of a fixed set of prefixes shared across sessions (tenants); the set's total size does not change with load or backlog; no request reuses its own session's earlier turns |
| **Session cap** | A limit on how many sessions are in service at once, held at the load generator. The gateway stays off |

## What stays, what is replaced

| Part of the plan above | Now |
| --- | --- |
| Fixed choices, run checks, one run step by step | Unchanged |
| Verdict rules and the six conditions (PROTOCOL §3) | Unchanged; they judge every P0 run |
| Triggers, in order | The burst is the only trigger used. The cache wipe is reported as a weak trigger (no stuck run). Power cap, restart and popularity shift are not planned; the power cap is a stretch item |
| Control: no trigger | Unchanged, at every cell |
| Control: prefix caching off | Given a form: same share of the cache-off capacity as the test load has of the warm capacity, same absolute burst (step D) |
| Control: prefixes protected | Replaced by the session-cap arm (step D) |
| The danger-zone map (load × trigger size) | Replaced by the boundary map below |
| Up-then-down ramp | Not repeated; the ramps run so far used open-loop turns and showed no gap |
| The four figures and the done list | Replaced below |

## Steps, in order

Each step names what it needs before it can start. GPU hours are rough (BELIEF, from the cost of REG-8 and REG-19) and are fixed only at registration.

**A. P0: finish REG-19 as registered.** Under way; nothing in it changes. Its outcome picks the cell for steps C and D: a cell where the closed-loop arm passes its test, or, if REG-19 does not reach 3 of 5, the owner chooses between λ = 2.1 and reporting λ = 2.0 as a cell where the zone is too narrow to hold.

**B. K3 on the runs already made (0 GPU h, retrospective).** One registered analysis of the closed-loop cold runs (REG-12, REG-14 to REG-18, and REG-19 once reported). Needs first: the models' equations checked against the papers (open-questions A16), and a cold-turn cost by prompt length from the cache-off sweeps. Readouts, each with a tolerance fixed before it is computed:
- the drain threshold: is the backlog slope's sign set by the span's planned load against the cold floor?
- the backlog slope against the model's value;
- the mean prompt length of the turns served while cold, against the schedule's mix (the published model says shorter);
- uncached prefill tokens per second against the cache-off rate (a cold test that does not depend on the mix of turns);
- the 5-minute hit-ratio rule of Huang and Liu, as a second reading beside our verdict.

These runs have been seen, so this is a consistency check, never a blind test. The blind test is step C onward, where the predictions are registered before the runs.

**C. K1: the matched arm (about 11 to 12 GPU h for five pairs).** The cell chosen in step A, with the same seeds and the same burst, and one change: open-loop turns. Control and burst run per seed, as in REG-19.
- Supports K1: the open-loop arm `recovered` while the closed-loop arm passed, with most open-loop session hits served while the previous turn runs (`gate.overlap_share`).
- Refutes K1: the open-loop arm stuck.
- Known confound to state in the registration: the warm capacity differs between the two arms (3.0 open-loop against about 2.4 closed-loop at L1), so the same λ is a different share of it; the cold floor is the same.
- Registered with it: the K3 predictions for both arms.

**D. C2: cut the loop (about 4 to 6 GPU h).** Two controls on the cell from step A.
- *Session-cap arm:* the burst run repeated with the session cap on. Needs a load-generator change and tests on `tests/fake_vllm.py` (the owner's approval, as a workload change), and a rule for the cap's value fixed beforehand. Expected if the loop is the cause: `recovered`, with the waiting moved to the load generator.
- *Caching off, matched on utilization:* caching disabled, the load at the same share of the cache-off capacity, the same absolute burst. Expected: one level only, and the backlog drains.

**E. K2: reuse structure and context (about 12 to 17 GPU h per setup).** Each new setup needs its own cold floor and warm capacity (sweeps with caching off and on, closed-loop turns) before any shock run, as the feasibility gate requires.
1. *Shared-only setup first,* at a cache gain matched to L1's (warm hit about 0.84). Needs a harness change: M tenant prefixes shared across sessions and no reuse of a session's own turns (details in the answered questions below). Expected under K2: no stuck run. The setup is built so that it can fail: any tenant's prefix can be evicted.
2. *One further context size,* under closed-loop turns: 16 turns per session instead of 8, the system prompt unchanged (see the answered questions below for why turns and not `system_tokens`). Expected under K2: a wider zone and a higher stuck share than at 8 turns. Four turns is the next point if GPU time remains.
The one shared GPU decides how far this goes; one setup of each kind is the minimum for K2 to be stated at all.

**F. K4: lifetime of the warm state (only after C to E).** A surge threshold fixed from the schedule alone, then no-burst runs on new schedules on both sides of it. Long runs (REG-16 took 16,080 s), so few of them.

**G. K5: lead times (0 GPU h, optional).** A registered onset rule per signal, applied to the stuck runs on record.

## The boundary map

The main result is a table, each cell "passes in k of n seeds" with its one-sided 95 % bound, its margin, and its no-trigger controls:

| Vary | Values | Learn |
| --- | --- | --- |
| Turn semantics | Open-loop, closed-loop | Whether idle, evictable prefixes are needed (K1) |
| Reuse structure | Per-session context, shared-only | Whether reuse that does not grow with load is safe (K2) |
| Context per session | 8 turns (L1), 16 turns, then 4; the 512-token setups on record are open-loop only | Whether the zone widens with the cold-to-warm cost gap (K2) |
| Margin | The loads on record at L1 (2.0, 2.2, 2.4), in units of the cold floor | How close to the floor the state can be entered |

The open-loop runs already on record (no stuck run in any of 10 cells) fill the first row; they are reported as they were judged.

## Outputs and done criteria

Four figures, all from run folders through `analysis/`:

1. **The boundary map** above.
2. **The matched-arm figure:** one seed, open-loop against closed-loop, hit rate, KV usage and waiting line on one time axis with the burst at t = 0.
3. **Model against measurement:** the registered predictions beside the measured values, per quantity.
4. **The loop-cut figure:** the same cell with the burst, with the burst under the session cap, and with caching off.

Stage 2 is done when:

- [ ] P0: REG-19 is reported, pass or not, and the cell for the later steps is chosen
- [ ] K1: the matched arm is run and judged
- [ ] C2: the session-cap arm and the caching-off control are run and judged
- [ ] K2: a shared-only setup and one further context size (16 turns) are measured and shocked, or the owner records that the GPU budget ends K2 earlier
- [ ] K3: every registered prediction is compared once, inside or outside its tolerance
- [ ] Every statement taken from the three preprints is checked against the papers (open-questions A16)

A result against a claim counts as done: an open-loop arm that gets stuck, a shared-only setup that gets stuck, or a model that misses its tolerance is written up as such.

## Open questions for this revision, answered 2026-11-12

The owner left these to the agent ("do whatever leads to correct results"); the reasoning is in decisions.md 2026-11-12 [DECISION] (design choices). Each choice still enters a `[REG]` before any run, where the owner can change it.

- [x] **Conditions 5 and 6 of PROTOCOL §3 stay required for P0.** What the preprints show about persistence is not evidence about this setup, and condition 6 (warm again after a load drop, at the same load) is the one test that separates two states from plain overload; it has not yet been passed after a burst. The drop is sized beforehand from the expected backlog and the cold floor, with a factor of two; 1800 s was too short (REG-15), 9000 s was enough (REG-16).
- [x] **Session cap value:** per seed, the highest number of sessions in service at once in that seed's no-trigger control (in service: from a session's first turn sent to its last reply). Computed from the control before the capped run, no tuning, no extra GPU time. With this value the cap never binds on the control's own schedule, so it changes nothing in a healthy run. Burst requests are one-off and pass the cap, so the trigger is identical in both arms. The capped arm is judged on the server's hit rate and waiting line; time spent waiting at the cap is reported separately.
- [x] **Shared-only workload at a matched cache gain:** the same sessions as L1 (8 turns, closed-loop, 5 s gaps, 128 output tokens), with only the token content changed: every turn is one of M tenant prefixes of 2576 tokens plus 496 fresh tokens, 3072 in all. This matches L1's mean prompt (3072), its mean uncached tokens per turn (496) and its hit rate (2576 / 3072 = 0.8385, against L1's 20608 / 24576 = 0.8385 by design and 0.838 measured). M is set so that M × 2576 equals L1's warm working set at the test load, so the pool is as full when warm and each prefix sits idle for about as long as an L1 session's prefix does; a skewed popularity is a harsher second variant. **Not one prefix for everyone** (corrected the same day after review): every request would hold it, it could never be evicted, and "no stuck run" would follow from the design, not from K2. What cannot be matched is the spread: L1's uncached part is 2176 tokens on a session's first turn and 256 afterwards, and L1's prompts run from 2176 to 3968 tokens. Both are registered as differences.
- [x] **Second point for K2: turns per session, not system-prompt length; 16 turns first.** With a system prompt that is unique per session, a longer prompt also makes the first turn dearer, so the cold-to-warm cost gap hardly moves (512 → 3072 tokens changes the token ratio from 5.1 to 6.6), and beyond about 3072 tokens a first turn alone takes most of the 1.0 s limit. Doubling the turns to 16 widens the gap more (6.2 → 10.9), leaves the first turn as it is, and fits the pool. Halving to 4 turns (ratio 3.5) is the second point if GPU time remains. A 16-turn cell should also hold a stuck state more firmly than L1, which steps C and D need if REG-19 does not pass.
- [x] **Cold floor for closed-loop cells: not assumed, measured.** First, in step B, the uncached prefill tokens per second of the closed-loop cold spans are compared with the cache-off sweep's (0 GPU h). From step E on, every new setup's cache-off sweep uses closed-loop turns. For L1 a closed-loop cache-off sweep is registered before step C if the step B comparison is outside its tolerance. Until then 1.681 is written as "the open-loop floor".
