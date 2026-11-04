# Study status

Living document: update it after every run or decision. Last updated: 2026-11-05.

**Stage 1 is complete; Stage 2 is in progress (started 2026-10-31).** Stage 1 inputs: μ_warm = 4 req/s, μ_off = 2 req/s (Stage 1 grid 1, 2, 3, …), λ = 3 healthy for 2 h, SLO TTFT ≤ 1.0 s, τ = 300 s (`20261101-131823_tau`), so the watch window is 1500 s.

**Headline so far: no stuck run.** Stuck in 0 of 3 in each of 10 cells (one-sided 95 % bound 0.63 per cell); no gap in the ramp at the default pool. Only the default pool with 20 s gaps is negative by the PROTOCOL rule; the other two setups had no ramp. Whether the test loads could get stuck at all is untested (`docs/model.md` M2, M4). Claims and their status: `docs/claims.md`.

**Next action: the owner reviews and approves REG-7** (decisions.md 2026-11-05: the feasibility gate for setup L1, a 2048-token system prompt at 5 s gaps; ≤ 9 GPU h). Nothing is running, and nothing from 2026-11-05 is committed yet. The VM was offline at the session's start (Tailscale: last seen about 4 h earlier).
1. **On the Mac, before any run:** the owner reviews and commits the 2026-11-05 changes (REG-7 is committed with its code and configs before it runs); push.
2. **When the VM is back:**
   - REG-6's recovery steps: inspect `runs/20261104-134159_long_pc_off_r3_s0` and the journal (`journalctl --list-boots`; the VM was seen online after the 14:35 loss); copy the folder to the Mac (kept, incomplete); `python3 tools/manifest.py update`; delete its line from `manifests/pending_copy.txt`; remove the VM copy only after a checksum-verified copy.
   - Probe and record the scheduler limits (open-questions A10).
   - Log the microk8s decision.
3. **With the owner's go, GPU idle, after `git pull`:**
   - G1 `uv run python -m harness.run configs/sweep_l1_pc_on.yaml` (about 3 h);
   - G2 `configs/sweep_l1_pc_off.yaml` (about 2.3 h);
   - copy back, update the manifest, compute `uv run python -m analysis.gate` **once** (λ_test);
   - write and commit the two G3 configs exactly as registered, run them (about 1.7 h), compute `gate.gate_verdict` once, and write the `[RESULT]`.
4. **REG-6** (approved; about 2.2 GPU h) runs after the gate, when the GPU is idle (owner, 2026-11-05).

**Then, the owner's open items:**
- items 18–22: paper layer, framing, canonical hit rate, backup location. The C1 metric is decided for future cells (decisions.md 2026-11-05); push was done 2026-11-04;
- whether to stop microk8s on the VM during runs;
- for the owner's approval: three doc fixes in process.md, PROTOCOL.md and CLAUDE.md (decisions.md 2026-11-05 [CORR], item 7).

**Done 2026-11-05 (0 GPU h):**
- Audit of all runs, code, docs and literature: every published verdict and μ reproduces; why nothing got stuck (the capacity loss is too small at the default pool); design rules for future cells; the owner's choices.
- `[CORR]` entries: doc contradictions, and `derived.hit_between` on a counter reset (no published value changed).
- Item 42's capacity rule implemented, for future sweeps only.
- REG-7 written, reviewed (rule F) and revised; `analysis/gate.py` with tests.

**Done 2026-11-04, after the audit:**
- REG-1 (post-trigger margin): inconclusive.
- REG-2 (control dips): both arrival-driven, no Ao-like cycle; A3 answered.
- REG-3 (A4): dropped.
- REG-4 (verdict code): no valid verdict changed.
- Harness and check items 1–8: done, for future runs only.
- Checksum manifest: `manifests/runs.sha256`.
- Committed table drivers: `analysis/tables.py`.

## Open risks

- **Feasibility:** the test loads may lie outside any real danger zone. Cache off saturates at about 3.5 completions/s and cache on still completes 4.185 at λ = 10, both above the healthy test loads at 20 s gaps (`docs/model.md` M2). REG-1 (0 GPU h) was inconclusive: no trigger so far held a cold backlog, so the floor is still unmeasured.
- **μ from one arrival pattern:** every sweep used seed 0, whose planned load rises from 0.67–0.97 λ to 1.05–1.34 λ across the measured window; μ_off = 2 may be low (`docs/model.md` M4, open-questions A1).
- **M1 (F + W) is 0 for 3** on tested predictions; do not use it to choose loads until revised.
- **Single-seed controls** in every cell.
- **The VM can shut down mid-run** (2026-10-31, 2026-11-01, and REG-6 seed 0 on 2026-11-04). An interrupted run is kept and rerun; a stopped sweep has no resume.
- **REG-6 seed 0 exists only on the VM** until copied.
- **microk8s runs on the VM**, unrecorded in `env.json` (decisions.md [OPS] 2026-11-04).
- **Manipulation checks are off** for every past run (thresholds null in `configs/defaults.yaml`). REG-7 registers `burst_min_kv_max: 0.95` for its burst runs (`configs/stage2_l1_base.yaml`).
- **Scheduler limits unrecorded** (`max_num_batched_tokens`, `--scheduler-reserve-full-isl`; open-questions A10).
- **Open-loop turns protect the cache under slowdown** (decisions.md 2026-11-01, limits): REG-7 measures the overlap share.
- **Data:** one copy only (Watch, below). A backup can now be verified with `python3 tools/manifest.py verify <copy>`.

## Stage 2 results

| Setup | Capacity (μ_warm / μ_off) | Healthy test loads (no-trigger control) | Cache wipe | Load burst | Other |
|---|---|---|---|---|---|
| Default pool (96,656 tokens), 20 s gaps | 4 / 2 | 3, 3.5 (4 `bad_baseline`, dropped) | 0 of 6 stuck | 0 of 6 stuck | Ramp, 300 s and 600 s steps: no gap |
| Smaller pool (72,480 tokens), 20 s gaps | 4 / 2.5 | 3 (3.5 `bad_baseline`) | 0 of 3 stuck | 0 of 3 stuck | — |
| Default pool, 5 s gaps | 6 / 2.5 | 3.5, 4.5 | 0 of 6 stuck | 0 of 6 stuck | — |

- **Triggers:** cache wipe in `preempt` mode at t = 900 s; burst of +3 req/s of one-off 1408-token requests for 120 s from t = 900 s. Seeds 1–3. Verdict rule: decisions.md 2026-11-01 ("Stuck" redefined), with the baseline-window correction of 2026-11-02.
- **Stopped early by decision:** the wipe matrix at λ = 2.5 and 1.5 and the `idle` wipe comparison.
- **Not yet done:** triggers 3–5 (power cap, engine restart, popularity shift), bigger bursts, the ramp at the smaller pool, 60 s gaps, the caching-off and protected-prefixes controls, and the plan's four Stage 2 figures (danger-zone map, loop figure, ramp figure, control figure).

## Stage 1 run steps

| # | Step | Config | Status | Run id |
|---|---|---|---|---|
| 1 | Smoke test (1.7B, random prompts, λ = 0.5) | `smoke.yaml` | Done, VALID | `20261023-145933_smoke` |
| 2 | First real run (4B, sessions, λ = 2) | `first_real.yaml` | Done, VALID | `20261030-114115_first_real` |
| 3 | Repeat the same config twice, compare | `repeat.yaml` | Done, all VALID, within tolerance | `20261030-120420_repeat`, `20261030-122024_repeat` |
| 4 | Load sweep, prefix caching on → μ_warm | `sweep_pc_on.yaml` | Done: μ_warm = 4 req/s; λ = 8 INVALID (`accounting`), others VALID | `20261030-131243_sweep_pc_on_r1` … `20261030-151441_sweep_pc_on_r10` |
| 5 | Load sweep, prefix caching off → μ_off | `sweep_pc_off.yaml` | Done: μ_off = 2 req/s; λ = 10 INVALID (`recorder`), others VALID | `20261030-154544_sweep_pc_off_r1` … `20261030-175458_sweep_pc_off_r10` |
| 6 | Long run at a λ between μ_off and μ_warm | `long_run.yaml` (λ = 3) | Done, VALID, healthy under the pre-registered criteria | `20261030-181851_long_run` |

## Runs on record

104 run folders: 93 VALID, 9 INVALID, 2 without checks. All kept; none counts unless VALID.

- **No checks:** `20261030-114021_first_real` (failed start, no load sent); `20261031-025032_tau` (VM shut down 140 s in).
- **Invalid, Stage 1:** `20261023-145613_smoke` (`gpu_steady`, before the check was refined); `20261030-145339_sweep_pc_on_r8` (`accounting`); `20261030-175458_sweep_pc_off_r10` (`recorder`).
- **Invalid, Stage 2:** `20261101-151707_stage2_control_r1.5` (stopped on request); `20261101-182452_stage2_control_cap_r3`, `20261102-045827_wipe_preempt_r3_s1`, `20261102-062040_wipe_preempt_r3_s3`, `20261102-080323_wipe_preempt_r3_s3` (hardware thermal samples, before the backplate fan); `20261102-093229_wipe_preempt_r3_s3` (stopped on request after a thermal sample).

## Done when (from the plan)

**Stage 1:** all six boxes done (decisions.md, steps 3–6 results and SLO).

**Stage 2** (from the plan):
- [ ] At least one load inside the danger zone gets stuck in most repeats, while its no-trigger control stays healthy. **Not met: no stuck run.**
- [ ] Stuck runs show the loop metrics in the expected order. Not applicable yet. The "few preemptions" part was replaced by a comparison with controls (decisions.md, 2026-11-01).
- [ ] With prefix caching off, the same setup does not get stuck. Not run; needs a defined form (decisions.md, 2026-11-01).
- [ ] The ramp gap stays when dwell time is increased. No gap at either dwell.

## Open questions

Stage 1: all 7 answered. Stage 2: S1, S2, S5, S7 answered; S6 partly; S3 and S4 open. Source questions S8–S11 (hit-counter units, eviction order, preempted blocks, self-refill), added 2026-11-04, answered from the v0.32.0 source. See `open-questions.md`. Terms and the code that computes them: `definitions.md`.

## Environment

| Item | Value |
|---|---|
| VM | Ubuntu 24.04, 8 cores, 31 GB RAM, Proxmox; GPU shared with another user, so the VM can be shut down from outside |
| GPU | RTX 3090 (Gigabyte AORUS Xtreme), 24 GB, driver 595.99.02, power limit 420 W; fan on the backplate since 2026-11-02 |
| Software | vLLM 0.32.0, torch 2.13.0 (CUDA 13.0), Python 3.12.13 (uv-managed); `unattended-upgrades` disabled |
| KV cache | Qwen3-4B: 96,656 tokens by default in load runs; 72,480 tokens when set with `--kv-cache-memory-bytes` |
| Pinning | vLLM cores 0–5, loadgen 6, recorder 7 |
| Data | **All 104 runs (9.4 GB) are only on the Mac** in `runs/`, checksum-verified; the VM's copies were removed 2026-11-04. No second backup yet |
| Disk | 16 GB free on the VM after cleanup; about 170 MB per 40-minute run |
| Address | `inference-vm.tail3b0112.ts.net` / 100.83.53.50 (Tailscale); 192.168.3.249 at home; key `~/.ssh/id_ed25519_vllm`. The `vm` git remote still uses the home address |
| Sync | Mac `git push vm main` → VM `git pull` in `~/aftershock-artifacts`; don't pull during a sweep |

## Watch

Sorted by priority, most urgent first.

- **Backup (top item):** the Mac holds all 104 runs (9.4 GB). The owner decided on 2026-11-05 that the copies stay on the Mac (decisions.md). A copy on the same machine guards against deletion, not against losing the Mac; `python3 tools/manifest.py verify <copy>` checks any copy.
- **Heat:** before the backplate fan, hardware thermal flags at 83–84 °C invalidated 5 runs. With the fan: 0 flags in every run since. A flag still invalidates a run; the rule is not loosened.
