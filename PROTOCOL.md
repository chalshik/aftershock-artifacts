# Protocol

What this study asks, what it claims, what would count for and against, and how runs are done. It gathers rules that are spread over `docs/experiment-plan.md` (the source of truth for intent) and `docs/decisions.md` (the append-only log of every change). Where they differ, the newer decisions.md entry rules. Each rule below names its source and date. Anything marked **[new 2026-11-04]** was first written after results existed and must be read with that in mind.

**Read this first, then `docs/status.md`.** Rules for how to work are in `CLAUDE.md`.

## 1. Research question

After a short shock to a healthy vLLM server with prefix caching, at the same load as before, can the server stay slow after the shock has ended, because the lost cache keeps itself lost? (plan, Stage 2 Purpose)

## 2. Hypothesis

- **C1, the symptom:** at some load λ between μ_off and μ_warm, percent fast stays low after the trigger has ended, while the same load without a trigger stays healthy. (plan)
- **C2, the cause:** a sustaining loop. Cache lost → slow requests → big running batch → KV memory full → cached prefixes evicted before their session's next turn → cache stays lost. (plan)

## 3. What counts for and against

**A run's verdict** (`analysis/load.py`, `verdict`; decisions.md 2026-11-01 "Stuck" redefined, and 2026-11-02 baseline correction):

| Item | Rule |
|---|---|
| Baseline | The 600 s before the trigger starts |
| Judged window | The last 600 s of a 1500 s watch after the trigger ends, against the 600 s before it |
| bad_baseline | Baseline percent fast < 0.98. The run says nothing |
| recovered | Percent fast ≥ baseline − 0.02, hit ≥ baseline − 0.06, mean waiting ≤ baseline + 1 |
| slow_drain | Any one sign of recovery: hit up ≥ 0.06, percent fast up ≥ 0.05, or a queue that would empty within 3600 s. The plan asks for all three signs (deviation, §6) |
| stuck | Percent fast ≤ baseline − 0.10 and hit ≤ baseline − 0.06, with no sign of recovery. A line that shrinks too slowly to empty within 3600 s counts; the plan says "flat or growing" (deviation, §6) |
| unclear | Anything else; never rounded to another verdict |

**Support for a metastable failure at a load: all six must hold** (decisions.md 2026-11-01):
1. The trigger has ended, and the load is unchanged.
2. The no-trigger control at that load is `recovered`.
3. Most seeds are `stuck`.
4. A memory-limited loop: mean KV ≥ 0.80, mean N ≥ 2 × baseline, N below the 256 cap, and the traces follow the plan's order.
5. Persistence: a 4500 s-watch confirmation run is also `stuck`.
6. Two states at one load: in that same confirmation run, after the watch, λ drops to 1 req/s for 1800 s, then returns to the original λ for 1500 s. The last 600 s must be `recovered` against the original baseline, and the line must have reached 0 during the drop; if it did not, this item is inconclusive, not passed. **[restated 2026-11-04 to match decisions.md 2026-11-01 "Stuck" redefined]**

**The ramp test** (decisions.md 2026-11-03): a gap is a down-step with percent fast ≤ up − 0.10 and hit ≤ up − 0.06, at a load healthy going up (≥ 0.98). It counts only if it appears at both the 300 s and the 600 s dwell.

**Against the hypothesis:** the plan says only: "If no load    gets stuck even after shrinking the KV pool, that is a result too: write down the conditions tested and why the loop did not hold."
- **[new 2026-11-04]** A negative result is stated only for the conditions tested: setups, triggers, sizes, loads and seeds. It never says "vLLM cannot fail this way". A result is negative for a setup when every valid trigger run at its healthy loads is `recovered` or `slow_drain`, none is `stuck`, and the ramp shows no gap.
- **[new 2026-11-04]** By that rule only the default pool with 20 s gaps is negative. The 72,480-token pool and the 5 s-gap setup had no ramp, so they are reported as "no stuck run", not as negative.
- **[new 2026-11-04]** Before a negative is stated for a setup, the feasibility gate (`docs/process.md` §4, `docs/model.md` M2) says whether a stuck state was possible at its test loads at all. If it was not, the negative says only that those loads recover.

## 4. System setup

| Item | Value |
|---|---|
| Hardware | One RTX 3090, 24 GB (Gigabyte AORUS Xtreme, backplate fan since 2026-11-02), power limit 420 W (350 W for setup L1 from REG-8, decisions.md 2026-11-06); Proxmox VM, Ubuntu 24.04, 8 cores, 31 GB RAM; GPU shared with another user |
| Software | vLLM 0.32.0, torch 2.13.0 (CUDA 13.0), driver 595.99.02, Python 3.12.13, all pinned in `pyproject.toml` and `uv.lock` |
| Model | Qwen/Qwen3-4B, bf16; 147,456 bytes of KV per token |
| Server | Single replica, served directly. Flags: `--enable-prefix-caching`, `--kv-cache-metrics`, `--enable-prompt-tokens-details`, `--seed 0`, `--max-num-seqs 256`. Everything else at vLLM defaults. Dev mode (`VLLM_SERVER_DEV_MODE=1`) in every shock run (wipes, bursts), every no-trigger control, both wipe tests and both ramps: 49 runs. **Not** in the capacity sweeps (Stage 1 and both Stage 2 setups: 72,480-token pool, 5 s gaps), the τ runs, the recorder-off runs or the other Stage 1 runs: 55 runs. So each setup's μ was measured without dev mode and its controls and shocks with it. **[corrected 2026-11-04; previously "in all Stage 2 runs"]** |
| KV pool | Default 96,656 tokens; or set to 72,480 tokens with `--kv-cache-memory-bytes 10687610880` |
| Workload | Open-loop sessions: 8 turns, 512 system + 128 user + 128 recorded-reply tokens per turn, 128 output tokens, exponential turn gap (mean 20 s, or 5 s), session starts at λ/8 |
| Client | No retries, no timeouts, unlimited connection pool, gateway off |
| CPU pinning | vLLM cores 0–5, load generator 6, recorder 7 |
| SLO | TTFT ≤ 1.0 s, measured from the planned arrival |
| Config | Every setting lives in `configs/*.yaml`. Each run saves its resolved config, `env.json` (versions, git commit, dirty flag) and checks |

## 5. Procedure

1. **Capacity per setup:** 900 s sweeps with caching on and off, seed 0. μ is the highest λ with a valid run, throughput ≥ 0.95 λ and waiting slope ≤ 0.01 req/s (written "req/s²" before 2026-11-04; the number is unchanged). Every sweep shares seed 0's arrival pattern, whose planned load rises through the measured window (`docs/model.md` M4). **[new 2026-11-05]** Sweeps whose config has a `capacity:` block (from REG-7 on) compare throughput with the realized planned rate in the window instead of λ (item 42, decisions.md 2026-11-04). With `monotone: true`, μ is the highest rate that passes along with every lower swept rate (REG-7, decisions.md 2026-11-05). Past μ values stand as judged.
2. **Test loads:** λ inside μ_off < λ < μ_warm whose no-trigger control is `recovered`.
3. **Shock runs:** 2400 s (2520 s for a burst), trigger at t = 900 s, seeds 1–3, plus seeds 4–5 if seeds disagree.
   - **Cache wipe:** `POST /reset_prefix_cache?reset_running_requests=true`, which preempts running requests.
   - **Burst:** +3 req/s of one-off 1408-token random prompts for 120 s.
4. **Ramp:** λ 2 → 5 → 2 in steps of 0.5, at a 300 s and a 600 s dwell; each step judged on its second half.
5. **A run is valid only if every check passes:**
   - client lag p99 ≤ 50 ms
   - no errors, and accounting matches vLLM's counters
   - recorder intact
   - recorder: no counter decrease, no failed scrape, scrape gap ≤ 2 s
   - GPU steady: no HW throttle sample, SW thermal ≤ 5 %, busy SM-clock CV ≤ 5 %
   - arrival rate within tolerance
   - clean git
   - the trigger fired as specified

   Invalid runs are kept, never counted, and rerun unchanged.
6. **Before any run:** its config and thresholds are committed and logged in decisions.md. A config used by a run is never edited.

## 6. Deviations from the plan

| Deviation | Why | decisions.md |
|---|---|---|
| The wipe preempts running requests | The non-preempting reset fails whenever a request runs | 2026-10-31 |
| "Stuck" needs six conditions, not just low percent fast | Low percent fast alone can't tell stuck from a backlog | 2026-11-01 |
| Preemptions are compared with controls, not required to be few | Memory pressure causes them anyway | 2026-11-01 |
| Baseline ends at the trigger start | Corrected after seeing the λ = 3 bursts | 2026-11-02 |
| λ = 4 dropped | Its control was `bad_baseline` | 2026-11-02 |
| Wipe matrix stopped at λ = 3 and 3.5; `idle` comparison not run | Study owner's decision after 0 of 6 | 2026-11-02 |
| One-off burst requests, not extra sessions | Gives a clean end to the shock | 2026-11-02 |
| Burst runs are 2520 s against 2400 s controls | A stuck burst run would need a matching control | 2026-11-02 |
| The caching-off burst control is undefined | λ = 3 with caching off is already failing | 2026-11-01 |
| VM copies of runs removed after a verified copy | Disk space; the Mac now holds the canonical copy | 2026-11-04 |
| `slow_drain` needs any one sign, not all three; `stuck` accepts a line too slow to empty within 3600 s | Noise in single signs; a slowly shrinking line is not recovery. Set before any Stage 2 verdict | 2026-11-01 ("Stuck" redefined) |
| `throughput` changed from arrivals that completed to completions per second | The plan's definition; changed **after** the step 4 sweep results, μ_warm unchanged | 2026-10-30 |
| `accounting` allows requests cut off after a first token | Changed **after** `sweep_pc_on_r8` failed it; that run stays invalid | 2026-10-30 |
| `base.yaml` edited after the first smoke run used it | `gpu_steady` refined during harness debugging; the run stays invalid | 2026-10-23 |
| One no-trigger control per load, seed 1 only | Cost; shock seeds 2–3 have no same-schedule control | 2026-11-01 |
| No ramp at the 72,480-token pool or with 5 s gaps | Not registered; so neither setup is negative by §3 | 2026-11-04 (audit) |
| L1 measured at a 350 W power limit, not 420 W | SW-thermal slowdown invalidated every cache-off L1 run at 420 W | 2026-11-06 (REG-8) |

## 7. Current result (details in `docs/status.md`)

Stuck in 0 of 3 in each of 10 cells (setup × trigger × load), each with a one-sided 95 % upper bound of 0.63 on the stuck probability; no ramp gap at the default pool. Pooled, 0 of 30 bounds a common probability at 0.095, only under the assumption that all cells share one (`docs/process.md` §5). Whether these loads could get stuck at all is untested (`docs/model.md` M2). Untested:
- triggers 3–5 (power cap, engine restart, popularity shift)
- larger bursts
- 60 s turn gaps
- the ramp at the smaller pool
- the caching-off and protected-prefixes controls
