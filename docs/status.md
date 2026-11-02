# Study status

Living document: update it after every run or decision. Last updated: 2026-11-01.

**Stage 2 has started (2026-10-31), and Stage 1's inputs are all in.** τ = 300 s from `20261101-131823_tau` (VALID), so the watch window is 1500 s; see decisions.md for the limits of that number. All 6 run steps are done. μ_warm = 4 req/s, μ_off = 2 req/s, λ = 3 stayed healthy for 2 h, and the SLO is TTFT ≤ 1.0 s.

**Next action:** no-trigger controls are done: λ = 1.5, 2.5, 3, 3.5 healthy, λ = 4 `bad_baseline` (decisions.md). `preempt` wipes at λ = 3 done: stuck in 0 of 3 (decisions.md). A fan on the GPU backplate fixed the heat failures. `preempt` wipes at λ = 3.5 done: stuck in 0 of 3. Wipe matrix stopped there (decisions.md). Trigger 2, the load burst: λ = 3 done, stuck in 0 of 3 (after a baseline-window correction, decisions.md); λ = 3.5, seeds 1–3, running. Whether λ = 4 stays in the matrix is still undecided. When they end, read them with `verdict` in `analysis/load.py`, then add the wipe configs and run the matrix. Verdict rule and matrix are registered, and the live wipe test passed (decisions.md). The interrupted `20261031-025032_tau` does not count (decisions.md).

## Run steps

| # | Step | Config | Status | Run id |
|---|---|---|---|---|
| 1 | Smoke test (1.7B, random prompts, λ = 0.5) | `smoke.yaml` | Done, VALID | `20261023-145933_smoke` |
| 2 | First real run (4B, sessions, λ = 2) | `first_real.yaml` | Done, VALID | `20261030-114115_first_real` |
| 3 | Repeat the same config twice, compare | `repeat.yaml` | Done, all VALID, within tolerance | `20261030-120420_repeat`, `20261030-122024_repeat` |
| 4 | Load sweep, prefix caching on → μ_warm | `sweep_pc_on.yaml` | Done: μ_warm = 4 req/s; λ = 8 INVALID (`accounting`), others VALID | `20261030-131243_sweep_pc_on_r1` … `20261030-151441_sweep_pc_on_r10` |
| 5 | Load sweep, prefix caching off → μ_off | `sweep_pc_off.yaml` | Done: μ_off = 2 req/s; λ = 10 INVALID (`recorder`), others VALID | `20261030-154544_sweep_pc_off_r1` … `20261030-175458_sweep_pc_off_r10` |
| 6 | Long run at a λ between μ_off and μ_warm | `long_run.yaml` (λ = 3) | Done, VALID, healthy under the pre-registered criteria | `20261030-181851_long_run` |

Invalid runs kept on record: `20261023-145613_smoke` (`gpu_steady`, before the check was refined; see decisions.md). Failed start, no load sent: `20261030-114021_first_real` (see decisions.md).

GPU time still needed: Stage 2.

## Done when (from the plan)

- [x] Repeated runs agree within a set tolerance (decisions.md, step 3 result)
- [x] Every run up to the capacity knee passes all checks (decisions.md, steps 4 and 5)
- [x] Load–latency curves with prefix caching on and off; μ_warm and μ_off known (`analysis/analysis.ipynb`, valid runs only)
- [x] A λ inside the gap stays healthy in a long run (decisions.md, step 6 result)
- [x] SLO for later stages fixed from measured healthy latency: TTFT ≤ 1.0 s (decisions.md)
- [x] Harness can switch on the gateway and a trigger without a rewrite (config switches exist and are off; trigger logic is Stage 2)

## Decide before the results they judge (pre-registration)

- [x] Repeat tolerance (step 3): throughput ±2 %, TTFT p50 ±10 %, TTFT p99 ±25 %, hit rate ±0.02 (decisions.md, 2026-10-30)
- [x] Capacity rule for μ: valid run, throughput ≥ 0.95 λ and waiting-queue slope ≤ 0.01 req/s² (decisions.md, 2026-10-30)
- [x] Sweep λ grid: kept as [1, 2, 3, 4, 5, 6, 8, 10] (decisions.md, 2026-10-30)

## Open questions

Answered with evidence: all 7 (see `open-questions.md`). Question 5, the recorder, was tested with prefix caching on only.

## Environment

| Item | Value |
|---|---|
| VM | Ubuntu 24.04, 8 cores, 31 GB RAM, Proxmox |
| GPU | RTX 3090, 24 GB, driver 595.99.02, power limit 420 W |
| Software | vLLM 0.32.0, torch 2.13.0 (CUDA 13.0), Python 3.12.13 (uv-managed) |
| KV cache | Qwen3-4B: 96,656 tokens in load runs, 92,432 in the probe (see decisions.md) · Qwen3-1.7B: 165,792 tokens |
| Pinning | vLLM cores 0–5, loadgen 6, recorder 7 |
| Disk | 15 GB free on the VM; all runs total 1.4G |
| Address | `inference-vm.tail3b0112.ts.net` / 100.83.53.50 (Tailscale, from anywhere); 192.168.3.249 at home (DHCP, can change on reboot); key `~/.ssh/id_ed25519_vllm` |
| Sync | Mac `git push vm main` → VM `git pull` in `~/aftershock-artifacts` |

## Watch

- The software thermal flag hit exactly the 5 % limit at low load. If heavier runs fail `gpu_steady`, that is a hardware finding (cooling or power limit) to decide on. Don't just loosen the threshold.
- `first_real` (λ = 2) already reached 84 °C and drew 402 W on average against the 420 W limit, with the SW thermal flag on 3.2 % of samples and no HW throttle samples. The higher sweep rates are the test of this.
