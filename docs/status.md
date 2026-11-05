# Study status

Living document: update it after every run or decision. Last updated: 2026-11-05.

**Stage 1 is complete; Stage 2 is in progress (started 2026-10-31).** Stage 1 inputs: μ_warm = 4 req/s, μ_off = 2 req/s (Stage 1 grid 1, 2, 3, …), λ = 3 healthy for 2 h, SLO TTFT ≤ 1.0 s, τ = 300 s (`20261101-131823_tau`), so the watch window is 1500 s.

**Headline so far: no stuck run.** Stuck in 0 of 3 in each of 10 cells (one-sided 95 % bound 0.63 per cell); no gap in the ramp at the default pool. Only the default pool with 20 s gaps is negative by the PROTOCOL rule; the other two setups had no ramp. Whether the test loads could get stuck at all is untested (`docs/model.md` M2, M4). Claims and their status: `docs/claims.md`.

**Next action: G1 reruns, part a** (`configs/sweep_l1_pc_on_rerun1a.yaml`, λ = 4.5 and 5, about 32 min) after the owner improved the GPU cooling. Then part b (`..._rerun1b.yaml`, λ = 5.5, 6, 7) only if part a's λ = 5 run passes `gpu_steady`; otherwise ask the owner (decisions.md 2026-11-05 [DECISION]). The monotone-rule fix is approved and implemented. G1's first pass gave 4 of 9 valid runs (λ = 2–4). No μ is computed yet. REG-7 was approved by the owner on 2026-11-05: it was registered in `d1b360c` and approved in `f4d1110`. It is the feasibility gate for setup L1, and costs ≤ 9 GPU h without reruns.

Steps:
1. **Read-only VM checks: done 2026-11-05** (decisions.md [OPS], evidence in `docs/probe/20261105_vm_checks/`).
   - The 2026-11-04 loss, like those of 2026-10-31 and 2026-11-01, was an ACPI power-key event, sent from outside the VM.
   - The repo was clean at `4d30f1d`. The GPU was idle, with no compute process, and 16 GB of disk was free.
   - microk8s was installed automatically on the VM's first boot, before any login, and is unused: only the three default pods, and never a GPU pod.
2. **REG-6 seed-0 recovery: done.** The folder is copied with identical checksums, the manifest is updated, and the VM copy is removed.
3. **A10, the scheduler limits: answered** (open-questions A10). There is a 2048-token step budget, chunked prefill, the full prompt is reserved at admission, and the policy is fcfs.
4. **Done 2026-11-05: microk8s is disabled for every later run** (owner; decisions.md [DECISION]). The VM was rebooted to clear the pods left running, and the check after the reboot is clean (`docs/probe/20261105_vm_checks/after_reboot.txt`). Not blocking:
   - the output of the installer check the owner ran (`sudo grep -n -A4 snaps /var/log/installer/autoinstall-user-data`), which would confirm the microk8s origin;
   - the Proxmox task log, which shows who sent the three power-off events.
5. **Code on the VM:** the Mac pushes `main` to the `vm` remote, and the VM runs `git pull origin main`. Its `origin` is the bare repo `~/repos/aftershock-artifacts.git`. **Done 2026-11-05:** `ca0e299` was pushed to `origin` and to `vm`, and the VM pulled it with a clean tree. `uv.lock` and `pyproject.toml` are unchanged since `4d30f1d`, and `~/.local/bin/uv sync --frozen --extra server --dry-run` would make no changes. The commit that records this line follows `ca0e299` and is pushed the same way. Before G1, check `git log -1` on the VM against the Mac's `main`.
6. **Start rule for G1:** G1 starts after step 4 is decided and logged, with the tree clean at the latest `main` and the GPU idle. **Stop and ask the owner first** if a check finds anything unexpected: another GPU process, a dirty tree, low disk, or a power-off during a run.
7. **REG-7, in order:**
   - G1: `uv run python -m harness.run configs/sweep_l1_pc_on.yaml` (about 3 h).
   - G2: `configs/sweep_l1_pc_off.yaml` (about 2.3 h).
   - Copy both back and update the manifest. Then compute `uv run python -m analysis.gate` **once**; it gives λ_test, or no λ_test.
   - Write and commit the two G3 configs exactly as registered in REG-7, and run them (about 1.7 h). Compute `gate.gate_verdict` once, and write the `[RESULT]`. Its decision table is in the REG-7 entry.
8. **REG-6** (approved; about 2.2 GPU h) runs after the gate, when the GPU is idle (owner, 2026-11-05). Seed 0 must be rerun, unchanged, at a new run id; REG-6's stopping rule allows it.

**Then, the owner's open items:**
- items 18–21: paper layer, framing, canonical hit rate. Decided 2026-11-05: the C1 metric for future cells, and that the data copies stay on the Mac (decisions.md);
- the installer-check output (microk8s origin), and the Proxmox task log for the three power-offs;

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
- **The VM can shut down mid-run** (2026-10-31, 2026-11-01, and REG-6 seed 0 on 2026-11-04). Each time it was an ACPI power-key event, sent from outside the VM (decisions.md [OPS] 2026-11-05); the sender is not known. An interrupted run is kept and rerun; a stopped sweep has no resume.
- **microk8s was active in all 104 runs before 2026-11-05** (about 8 % of one core, unpinned, unused) and is **disabled from 2026-11-05 on** (decisions.md [DECISION] 2026-11-05). REG-6's result must state the difference. `env.json` records neither state (a harness change, the owner's).
- **Manipulation checks are off** for every past run (thresholds null in `configs/defaults.yaml`). REG-7 registers `burst_min_kv_max: 0.95` for its burst runs (`configs/stage2_l1_base.yaml`).
- **Open-loop turns protect the cache under slowdown** (decisions.md 2026-11-01, limits): REG-7 measures the overlap share.
- **Data:** the copies stay on the Mac (owner, 2026-11-05); one machine is still a single point of failure (Watch, below). A backup can now be verified with `python3 tools/manifest.py verify <copy>`.

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

114 run folders: 97 VALID, 14 INVALID, 3 without checks. All kept; none counts unless VALID.

- **No checks:** `20261030-114021_first_real` (failed start, no load sent); `20261031-025032_tau` (VM shut down 140 s in); `20261104-134159_long_pc_off_r3_s0` (REG-6 seed 0, VM powered off at t = 3168 s of 3600, DERIVED: power key 14:35:45.08 − planned load start 13:42:56.74 from `events.jsonl` `load_t0_planned`; copied 2026-11-05).
- **Invalid, Stage 1:** `20261023-145613_smoke` (`gpu_steady`, before the check was refined); `20261030-145339_sweep_pc_on_r8` (`accounting`); `20261030-175458_sweep_pc_off_r10` (`recorder`).
- **Invalid, Stage 2:** `20261101-151707_stage2_control_r1.5` (stopped on request); `20261101-182452_stage2_control_cap_r3`, `20261102-045827_wipe_preempt_r3_s1`, `20261102-062040_wipe_preempt_r3_s3`, `20261102-080323_wipe_preempt_r3_s3` (hardware thermal samples, before the backplate fan); `20261102-093229_wipe_preempt_r3_s3` (stopped on request after a thermal sample).
- **Invalid, REG-7 G1 (2026-11-05):** `20261105-130250_sweep_l1_pc_on_r4.5` (`no_errors`, 1 client disconnect); `20261105-132035_sweep_l1_pc_on_r5`, `20261105-134018_sweep_l1_pc_on_r5.5`, `20261105-140120_sweep_l1_pc_on_r6`, `20261105-142221_sweep_l1_pc_on_r7` (`gpu_steady`, SW-thermal slowdown).

## Done when (from the plan)

**Stage 1:** all six boxes done (decisions.md, steps 3–6 results and SLO).

**Stage 2** (from the plan):
- [ ] At least one load inside the danger zone gets stuck in most repeats, while its no-trigger control stays healthy. **Not met: no stuck run.**
- [ ] Stuck runs show the loop metrics in the expected order. Not applicable yet. The "few preemptions" part was replaced by a comparison with controls (decisions.md, 2026-11-01).
- [ ] With prefix caching off, the same setup does not get stuck. Not run; needs a defined form (decisions.md, 2026-11-01).
- [ ] The ramp gap stays when dwell time is increased. No gap at either dwell.

## Open questions

Stage 1: all 7 answered. Stage 2: S1, S2, S5, S7 answered; S6 partly; S3 and S4 open. Audit items: A3 and A10 answered. Source questions S8–S11 (hit-counter units, eviction order, preempted blocks, self-refill), added 2026-11-04, answered from the v0.32.0 source. See `open-questions.md`. Terms and the code that computes them: `definitions.md`.

## Environment

| Item | Value |
|---|---|
| VM | Ubuntu 24.04, 8 cores, 31 GB RAM, Proxmox; GPU shared with another user, so the VM can be shut down from outside |
| GPU | RTX 3090 (Gigabyte AORUS Xtreme), 24 GB, driver 595.99.02, power limit 420 W; fan on the backplate since 2026-11-02 |
| Software | vLLM 0.32.0, torch 2.13.0 (CUDA 13.0), Python 3.12.13 (uv-managed); `unattended-upgrades` disabled |
| KV cache | Qwen3-4B: 96,656 tokens by default in load runs; 72,480 tokens when set with `--kv-cache-memory-bytes` |
| Pinning | vLLM cores 0–5, loadgen 6, recorder 7 |
| Data | **All 114 runs are on the Mac** in `runs/`, checksum-verified; the VM's copies were removed (2026-11-04, and REG-6 seed 0 on 2026-11-05), except the 9 REG-7 G1 runs, which are also still on the VM. No second backup yet |
| Disk | 16 GB free on the VM after cleanup; about 170 MB per 40-minute run |
| Address | 100.83.53.50 (Tailscale; the name `inference-vm.tail3b0112.ts.net` is not in the Mac's `known_hosts`, so use the IP); 192.168.3.249 at home; key `~/.ssh/id_ed25519_vllm`. The `vm` git remote uses the home address (repointing it was not done: a permission prompt refused it) |
| Sync | Mac `git push vm main` → VM `git pull origin main` in `~/aftershock-artifacts` (the VM's `origin` is `~/repos/aftershock-artifacts.git`); don't pull during a sweep. Over a non-interactive SSH, `uv` is `~/.local/bin/uv` |

## Watch

Sorted by priority, most urgent first.

- **Backup (top item):** the Mac holds all 114 runs. The owner decided on 2026-11-05 that the copies stay on the Mac (decisions.md). A copy on the same machine guards against deletion, not against losing the Mac; `python3 tools/manifest.py verify <copy>` checks any copy.
- **Heat (top item for REG-7):** before the backplate fan, hardware thermal flags at 83–84 °C invalidated 5 runs. With the fan: 0 flags until 2026-11-05, when SW-thermal slowdown invalidated L1's G1 runs at λ = 5–7 at 81–82 °C (decisions.md [OPS]). A flag still invalidates a run; the rule is not loosened.
