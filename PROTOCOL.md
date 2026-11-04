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
| slow_drain | Any sign of recovery: hit up ≥ 0.06, percent fast up ≥ 0.05, or a queue that would empty within 3600 s |
| stuck | Percent fast ≤ baseline − 0.10 and hit ≤ baseline − 0.06, with no sign of recovery |
| unclear | Anything else; never rounded to another verdict |

**Support for a metastable failure at a load: all six must hold** (decisions.md 2026-11-01):
1. The trigger has ended, and the load is unchanged.
2. The no-trigger control at that load is `recovered`.
3. Most seeds are `stuck`.
4. A memory-limited loop: mean KV ≥ 0.80, mean N ≥ 2 × baseline, N below the 256 cap, and the traces follow the plan's order.
5. Persistence: a 4500 s-watch confirmation run is also `stuck`.
6. Two states at one load: drop to λ = 1 until the queue empties, return to λ, and the server comes back `recovered`.

**The ramp test** (decisions.md 2026-11-03): a gap is a down-step with percent fast ≤ up − 0.10 and hit ≤ up − 0.06, at a load healthy going up (≥ 0.98). It counts only if it appears at both the 300 s and the 600 s dwell.

**Against the hypothesis:** the plan says only: "If no load    gets stuck even after shrinking the KV pool, that is a result too: write down the conditions tested and why the loop did not hold."
- **[new 2026-11-04]** A negative result is stated only for the conditions tested: setups, triggers, sizes, loads and seeds. It never says "vLLM cannot fail this way". A result is negative for a setup when every valid trigger run at its healthy loads is `recovered` or `slow_drain`, none is `stuck`, and the ramp shows no gap.

## 4. System setup

| Item | Value |
|---|---|
| Hardware | One RTX 3090, 24 GB (Gigabyte AORUS Xtreme, backplate fan since 2026-11-02), power limit 420 W; Proxmox VM, Ubuntu 24.04, 8 cores, 31 GB RAM; GPU shared with another user |
| Software | vLLM 0.32.0, torch 2.13.0 (CUDA 13.0), driver 595.99.02, Python 3.12.13, all pinned in `pyproject.toml` and `uv.lock` |
| Model | Qwen/Qwen3-4B, bf16; 147,456 bytes of KV per token |
| Server | Single replica, served directly. Flags: `--enable-prefix-caching`, `--kv-cache-metrics`, `--enable-prompt-tokens-details`, `--seed 0`, `--max-num-seqs 256`. Everything else at vLLM defaults. Dev mode (`VLLM_SERVER_DEV_MODE=1`) in all Stage 2 runs |
| KV pool | Default 96,656 tokens; or set to 72,480 tokens with `--kv-cache-memory-bytes 10687610880` |
| Workload | Open-loop sessions: 8 turns, 512 system + 128 user + 128 recorded-reply tokens per turn, 128 output tokens, exponential turn gap (mean 20 s, or 5 s), session starts at λ/8 |
| Client | No retries, no timeouts, unlimited connection pool, gateway off |
| CPU pinning | vLLM cores 0–5, load generator 6, recorder 7 |
| SLO | TTFT ≤ 1.0 s, measured from the planned arrival |
| Config | Every setting lives in `configs/*.yaml`. Each run saves its resolved config, `env.json` (versions, git commit, dirty flag) and checks |

## 5. Procedure

1. **Capacity per setup:** 900 s sweeps with caching on and off. μ is the highest λ with a valid run, throughput ≥ 0.95 λ and waiting slope ≤ 0.01 req/s².
2. **Test loads:** λ inside μ_off < λ < μ_warm whose no-trigger control is `recovered`.
3. **Shock runs:** 2400 s (2520 s for a burst), trigger at t = 900 s, seeds 1–3, plus seeds 4–5 if seeds disagree.
   - **Cache wipe:** `POST /reset_prefix_cache?reset_running_requests=true`, which preempts running requests.
   - **Burst:** +3 req/s of one-off 1408-token random prompts for 120 s.
4. **Ramp:** λ 2 → 5 → 2 in steps of 0.5, at a 300 s and a 600 s dwell; each step judged on its second half.
5. **A run is valid only if every check passes:**
   - client lag p99 ≤ 50 ms
   - no errors, and accounting matches vLLM's counters
   - recorder intact
   - GPU steady: no HW throttle sample, SW thermal ≤ 5 %
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

## 7. Current result (details in `docs/status.md`)

Stuck in 0 of 30 valid shock runs across two KV pools and two turn gaps; no ramp gap. Untested:
- triggers 3–5 (power cap, engine restart, popularity shift)
- larger bursts
- 60 s turn gaps
- the ramp at the smaller pool
- the caching-off and protected-prefixes controls
