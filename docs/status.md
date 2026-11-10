# Study status

Living document: update it after every run or decision. Last updated: 2026-11-10.

**Stage 1 is complete; Stage 2 is in progress (started 2026-10-31).** Stage 1 inputs: μ_warm = 4 req/s, μ_off = 2 req/s (Stage 1 grid 1, 2, 3, …), λ = 3 healthy for 2 h, SLO TTFT ≤ 1.0 s, τ = 300 s (`20261101-131823_tau`), so the watch window is 1500 s.

**Headline so far: the first stuck state that overload does not explain, in one seed.** REG-14 (decisions.md 2026-11-10 [RESULT]): closed-loop turns at L1, 350 W, λ = 2.2, seed 2: the control stays warm with an empty queue; after a 180 s burst the same schedule stays cold, full and backlogged for the whole 1500 s watch, completing near the cache-off floor. Earlier, at λ = 2.4 (REG-11/12) the cold states sat at the closed-loop warm capacity of about 2.4 (REG-13), so overload explained them as well. Not yet C1: needs the matrix and the confirmation run (drop to λ = 1). Claims and their status: `docs/claims.md`.

**Next action: the owner reviews REG-15** (decisions.md 2026-11-10 [REG], reviewed under rule F in two rounds): C1's confirmation run at λ = 2.2, seed 12 (judged-window rule, owner's choice): a 4500 s watch, then λ = 1 for 1800 s, then back to 2.2 for 1500 s (≈ 2.6 GPU h). `confirms` → the matrix at λ = 2.2 on seeds 3–7 (owner, decisions.md 2026-11-10 [DECISION]); `not_persistent`, `reformed` or `no_return` → no matrix. Nothing runs before approval. **REG-14 is done: `pass_clear`**, the first stuck state that warm-side overload does not explain: at λ = 2.2, seed 2, the control ran with an empty queue while after the burst the same schedule stayed cold (hit 0, KV 0.95, queue 116 → 177) at 1.73–1.81 req/s for 1500 s. One seed, exploratory. REG-13 is done: 5 of 5 runs valid; the closed-loop warm capacity at L1, 350 W is about 2.4 (configs' rule; ratio 0.950 at the edge), not 3.0, below the cold runs' λp,max 2.711; the registered test says `overload` through a client-side slope that misfires on a ramping schedule (decisions.md 2026-11-10 [CORR]). At 2.6–3 the warm state lasted 368–602 s, then went cold. So REG-11's `pass` is not evidence of a metastable state: overload explains REG-11/12 as well. Also for the owner: the recorder failure in one REG-12 run and two checks that missed it (open-questions A14). **REG-12 is done:** 10 of 10 runs valid after one rerun. **REG-11 is done: `pass`, the first stuck state of the study** (decisions.md 2026-11-09 [RESULT]; exploratory, one seed). With closed-loop turns at L1, 350 W, λ = 2.4, after a 180 s burst the server stayed cold (0 hits), full (KV 0.95) and backlogged (queue 169 → 248) for the whole 1500 s watch, completing 1.72–1.79 req/s, at the cache-off floor; the same-seed control was healthy. Not yet C1: needs the matrix, the 4500 s confirmation and the drop to λ = 1; C2 needs its controls. Seed-count wording to fix in REG-12 (decisions.md 2026-11-09 [CORR]). **REG-10 is done** (decisions.md 2026-11-09 [RESULT]): both runs valid, the burst filled the pool, outcome `drains`; the post-burst backlog completed at 3.40 req/s (2.0× the cold floor) and cleared; `overlap_share` 0.608 > 0.5. **REG-9 is done** (decisions.md 2026-11-09 [RESULT]): both seeds valid at 350 W with 0 client errors; seed 0 `sustainable` (c_b 3.271 vs 3.201), seed 1 `unclear` (c_b 3.115 vs 3.184); outcome `no_change`, so REG-6's first edge is not applied and A1 stays open. Then the owner picks the next factor for L1 (REG-8 [RESULT]).** REG-8 is done: 13 of 13 runs valid at 350 W; μ_warm 3.0, cold floor 1.681 (`ok`), **no λ_test**, so no shock matrix at L1. The cold state loses 0.585 of capacity (0.116 at the default pool), but the warm side fails TTFT early. The outcome rests on λ = 3.5's queue slope, 0.0145 against 0.01. The owner set the GPU back to 420 W on 2026-11-07 (read 14:30 UTC, `docs/probe/20261107_power_limit/read_420w.txt`); a further L1 run at 350 W needs the owner to set 350 W again. REG-7 ended with no valid G2 run (λ = 1 SW-thermal 0.062, 0.097, 0.135; decisions.md [OPS] 2026-11-06), so the floor is unmeasured. The owner chose a power-limit amendment, and REG-8 (decisions.md 2026-11-06 [REG]) repeats REG-7's gate at 350 W: G2′ part a (λ = 1, the heat test) → G2′ part b → G1′ part a → G1′ part b → gate once → G3′, each step with a registered start rule (`gate.reg8_part_a`, `gate.reg8_g1_may_start`, `gate.reg8_g1b_may_start`). Written, reviewed (rule F) and **approved by the owner on 2026-11-07**. The `power_limit` check was approved by the owner on 2026-11-06. REG-7's G1 (420 W, valid at λ = 2–5.5) stays as judged; no μ is computed.

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
8. **REG-6: not run at 420 W; replaced by REG-9** (decisions.md 2026-11-07 [DECISION], [REG]). Its only 420 W attempt ran in SW-thermal slowdown 0.296 of the time. REG-9 repeats it at 350 W, carried to 420 W in one direction only. **Registered, reviewed (rule F) and approved by the owner on 2026-11-08.** To start: commit and push; compute `floor.shock_heat_table()` once (stop if no shock run is covered); the owner sets 350 W; the VM pulls; the agent reads the limit, checks the tree and an idle GPU at ≤ 45 °C, and launches `configs/long_pl350_pc_off_r3_s0.yaml`; seed 1 only if `floor.reg9_seed1_may_start()`. ≤ 2.2 GPU h.
9. **REG-8, once approved:** commit; push to `vm`; the owner runs `sudo nvidia-smi -pl 350`; the agent reads `nvidia-smi --query-gpu=power.limit --format=csv` and starts `configs/sweep_l1pl350_pc_off_a.yaml` with the GPU idle at ≤ 45 °C, recording idle temperature and wall-clock time in the `[OPS]` entry.

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
- **Old configs have no power check:** every config except the two `*pl350*` bases would run silently at whatever limit the card has. The agent reads `power.limit` before every launch; at 420 W (since 2026-11-07, 14:30 UTC) a `*pl350*` config would fail its `power_limit` check, and an old config is guarded only by that read (decisions.md 2026-11-07 [OPS]).
- **Power limit on a shared GPU (REG-8):** the limit applies to the whole card and can be reset by the other user or a reboot. 350 W runs fail `power_limit` if any sample differs; REG-6 has no such check, so its 420 W is checked by hand before launch and in its result.
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

164 run folders: 136 VALID, 24 INVALID, 4 without checks. All kept; none counts unless VALID.

- **No checks:** `20261030-114021_first_real` (failed start, no load sent); `20261031-025032_tau` (VM shut down 140 s in); `20261104-134159_long_pc_off_r3_s0` (REG-6 seed 0, VM powered off at t = 3168 s of 3600, DERIVED: power key 14:35:45.08 − planned load start 13:42:56.74 from `events.jsonl` `load_t0_planned`; copied 2026-11-05).
- **No checks, REG-7 G2:** `20261105-181511_sweep_l1_pc_off_r2` (stopped by the owner at t = 247 s).
- **Invalid, Stage 1:** `20261023-145613_smoke` (`gpu_steady`, before the check was refined); `20261030-145339_sweep_pc_on_r8` (`accounting`); `20261030-175458_sweep_pc_off_r10` (`recorder`).
- **Invalid, Stage 2:** `20261101-151707_stage2_control_r1.5` (stopped on request); `20261101-182452_stage2_control_cap_r3`, `20261102-045827_wipe_preempt_r3_s1`, `20261102-062040_wipe_preempt_r3_s3`, `20261102-080323_wipe_preempt_r3_s3` (hardware thermal samples, before the backplate fan); `20261102-093229_wipe_preempt_r3_s3` (stopped on request after a thermal sample).
- **Invalid, REG-7 G1 (2026-11-05):** `20261105-130250_sweep_l1_pc_on_r4.5` (`no_errors`, 1 client disconnect); `20261105-132035_sweep_l1_pc_on_r5`, `20261105-134018_sweep_l1_pc_on_r5.5`, `20261105-140120_sweep_l1_pc_on_r6`, `20261105-142221_sweep_l1_pc_on_r7` (`gpu_steady`, SW-thermal slowdown). Reruns, invalid again: `20261105-163225_sweep_l1_pc_on_r6`, `20261105-165327_sweep_l1_pc_on_r7`, `20261105-171648_sweep_l1_pc_on_r6` (`gpu_steady`).
- **REG-8 (350 W), valid:** G2′, all 7: `20261107-075951_sweep_l1pl350_pc_off_r1` … `20261107-095958_sweep_l1pl350_pc_off_r4`; G1′ part a, all 6: `20261107-103010_sweep_l1pl350_pc_on_r2` … `20261107-115311_sweep_l1pl350_pc_on_r5`.
- **Invalid, REG-7 G2 (2026-11-05):** `20261105-174215_sweep_l1_pc_off_r1`, `20261105-175822_sweep_l1_pc_off_r1.5`, `20261105-184607_sweep_l1_pc_off_r1`, `20261106-063534_sweep_l1_pc_off_r1` (`gpu_steady`).
- **REG-9 (350 W, force_close), valid:** `20261108-190906_long_pl350fc_pc_off_r3_s0`.
- **REG-12 (350 W, closed-loop turns), valid, 10:** controls and bursts of seeds 2–6 (decisions.md 2026-11-09 [OPS] REG-12).
- **Invalid, REG-12:** `20261109-134250_stage2_control_l1pl350cl_r2.4_s6` (`accounting`: the recorder stopped at t = 213 s; rerun valid).
- **REG-13 (350 W, closed-loop turns), valid, 5:** `20261109-190221_sweep_l1pl350cl_pc_on_r2` … `20261109-201246_sweep_l1pl350cl_pc_on_r3` (decisions.md 2026-11-10 [OPS] REG-13).
- **REG-14 (350 W, closed-loop turns, λ = 2.2), valid, 2:** `20261110-055201_stage2_control_l1pl350cl_r2.2_s2`, `20261110-063647_burst_l1pl350cl_r2.2_s2` (decisions.md 2026-11-10 [OPS] REG-14).
- **Invalid, REG-9 (350 W):** `20261108-134121_long_pl350_pc_off_r3_s0` (`no_errors`, 2 client errors in 10,711), `20261108-164842_long_pl350_pc_off_r3_s0` (`no_errors`, 1 client error); heat and power limit clean in both.

## Done when (from the plan)

**Stage 1:** all six boxes done (decisions.md, steps 3–6 results and SLO).

**Stage 2** (from the plan):
- [ ] At least one load inside the danger zone gets stuck in most repeats, while its no-trigger control stays healthy. **Not met:** REG-11 stuck in one seed; REG-12 (λ = 2.4, closed-loop turns) stuck with a recovered control in 2 of 5 seeds, and 3 of 5 controls did not stay healthy (`controls_not_healthy`).
- [ ] Stuck runs show the loop metrics in the expected order. Not applicable yet. The "few preemptions" part was replaced by a comparison with controls (decisions.md, 2026-11-01).
- [ ] With prefix caching off, the same setup does not get stuck. Not run; needs a defined form (decisions.md, 2026-11-01).
- [ ] The ramp gap stays when dwell time is increased. No gap at either dwell.

## Open questions

Stage 1: all 7 answered. Stage 2: S1, S2, S5, S7 answered; S6 partly; S3 and S4 open. Audit items: A3 and A10 answered. Source questions S8–S11 (hit-counter units, eviction order, preempted blocks, self-refill), added 2026-11-04, answered from the v0.32.0 source. See `open-questions.md`. Terms and the code that computes them: `definitions.md`.

## Environment

| Item | Value |
|---|---|
| VM | Ubuntu 24.04, 8 cores, 31 GB RAM, Proxmox; GPU shared with another user, so the VM can be shut down from outside |
| GPU | RTX 3090 (Gigabyte AORUS Xtreme), 24 GB, driver 595.99.02, fan on the backplate since 2026-11-02. **Power limit:** 420 W in every run up to 2026-11-06 (all 125); **set to 350 W on 2026-11-07 for REG-8** (`docs/probe/20261107_power_limit/set_350w.txt`), **back to 420 W the same day** after REG-8 (`docs/probe/20261107_power_limit/read_420w.txt`). Any run outside REG-8 needs 420 W (decisions.md 2026-11-07 [OPS]) |
| Software | vLLM 0.32.0, torch 2.13.0 (CUDA 13.0), Python 3.12.13 (uv-managed); `unattended-upgrades` disabled |
| KV cache | Qwen3-4B: 96,656 tokens by default in load runs; 72,480 tokens when set with `--kv-cache-memory-bytes` |
| Pinning | vLLM cores 0–5, loadgen 6, recorder 7 |
| Data | **All 138 runs are on the Mac** in `runs/`, checksum-verified; the VM's copies were removed (2026-11-04, and REG-6 seed 0 on 2026-11-05), except the REG-7 and REG-8 runs, which are also still on the VM. No second backup yet |
| Disk | 16 GB free on the VM after cleanup; about 170 MB per 40-minute run |
| Address | 100.83.53.50 (Tailscale; the name `inference-vm.tail3b0112.ts.net` is not in the Mac's `known_hosts`, so use the IP); 192.168.3.249 at home; key `~/.ssh/id_ed25519_vllm`. The `vm` git remote uses the home address (repointing it was not done: a permission prompt refused it) |
| Sync | Mac `git push vm main` → VM `git pull origin main` in `~/aftershock-artifacts` (the VM's `origin` is `~/repos/aftershock-artifacts.git`); don't pull during a sweep. Over a non-interactive SSH, `uv` is `~/.local/bin/uv` |

## Watch

Sorted by priority, most urgent first.

- **Backup (top item):** the Mac holds all 125 runs. The owner decided on 2026-11-05 that the copies stay on the Mac (decisions.md). A copy on the same machine guards against deletion, not against losing the Mac; `python3 tools/manifest.py verify <copy>` checks any copy.
- **Heat (top item for REG-8):** before the backplate fan, hardware thermal flags at 83–84 °C invalidated 5 runs. With the fan: 0 flags until 2026-11-05, when SW-thermal slowdown invalidated L1's G1 runs at λ = 5–7 at 81–82 °C and every G2 run (decisions.md [OPS]). A flag still invalidates a run; the rule is not loosened. REG-8 lowers the power limit to 350 W instead; a second heat failure of its first run stops L1.
