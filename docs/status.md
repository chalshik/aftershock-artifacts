# Stage 1 status

Living document: update it after every run or decision. Last updated: 2026-10-30.

**Stage 1 is not finished.** The harness is built and the GPU VM works. Run steps 1 to 4 of 6 are done. μ_warm = 4 req/s.

**Next action:** step 5 is running on the VM: `configs/sweep_pc_off.yaml`, 8 rates, about 2.5 h. Then set the step 6 rate.

## Run steps

| # | Step | Config | Status | Run id |
|---|---|---|---|---|
| 1 | Smoke test (1.7B, random prompts, λ = 0.5) | `smoke.yaml` | Done, VALID | `20261023-145933_smoke` |
| 2 | First real run (4B, sessions, λ = 2) | `first_real.yaml` | Done, VALID | `20261030-114115_first_real` |
| 3 | Repeat the same config twice, compare | `repeat.yaml` | Done, all VALID, within tolerance | `20261030-120420_repeat`, `20261030-122024_repeat` |
| 4 | Load sweep, prefix caching on → μ_warm | `sweep_pc_on.yaml` | Done: μ_warm = 4 req/s; λ = 8 INVALID (`accounting`), others VALID | `20261030-131243_sweep_pc_on_r1` … `20261030-151441_sweep_pc_on_r10` |
| 5 | Load sweep, prefix caching off → μ_off | `sweep_pc_off.yaml` | Running | |
| 6 | Long run at a λ between μ_off and μ_warm | `long_run.yaml` (set the rate first) | Blocked by 4–5 | |

Invalid runs kept on record: `20261023-145613_smoke` (`gpu_steady`, before the check was refined; see decisions.md). Failed start, no load sent: `20261030-114021_first_real` (see decisions.md).

GPU time still needed: about 8 h (two 8-point sweeps at ~20 min per point, plus a 2 h long run).

## Done when (from the plan)

- [x] Repeated runs agree within a set tolerance (decisions.md, step 3 result)
- [ ] Every run up to the capacity knee passes all checks
- [ ] Load–latency curves with prefix caching on and off; μ_warm and μ_off known
- [ ] A λ inside the gap stays healthy in a long run
- [ ] SLO for later stages fixed from measured healthy latency
- [x] Harness can switch on the gateway and a trigger without a rewrite (config switches exist and are off; trigger logic is Stage 2)

## Decide before the results they judge (pre-registration)

- [x] Repeat tolerance (step 3): throughput ±2 %, TTFT p50 ±10 %, TTFT p99 ±25 %, hit rate ±0.02 (decisions.md, 2026-10-30)
- [x] Capacity rule for μ: valid run, throughput ≥ 0.95 λ and waiting-queue slope ≤ 0.01 req/s² (decisions.md, 2026-10-30)
- [x] Sweep λ grid: kept as [1, 2, 3, 4, 5, 6, 8, 10] (decisions.md, 2026-10-30)

## Open questions

Answered with evidence: 1–4, 6, 7 (see `open-questions.md`). Still open:
- **5:** does the recorder slow the server? Needs runs with and without it.

## Environment

| Item | Value |
|---|---|
| VM | Ubuntu 24.04, 8 cores, 31 GB RAM, Proxmox |
| GPU | RTX 3090, 24 GB, driver 595.99.02, power limit 420 W |
| Software | vLLM 0.32.0, torch 2.13.0 (CUDA 13.0), Python 3.12.13 (uv-managed) |
| KV cache | Qwen3-4B: 92,432 tokens · Qwen3-1.7B: 165,792 tokens |
| Pinning | vLLM cores 0–5, loadgen 6, recorder 7 |
| Disk | 16 GB free; all runs so far total about 57 MB, so the sweeps fit |
| Address | 192.168.3.249 (DHCP, can change on reboot), key `~/.ssh/id_ed25519_vllm` |
| Sync | Mac `git push vm main` → VM `git pull` in `~/aftershock-artifacts` |

## Watch

- The software thermal flag hit exactly the 5 % limit at low load. If heavier runs fail `gpu_steady`, that is a hardware finding (cooling or power limit) to decide on. Don't just loosen the threshold.
- `first_real` (λ = 2) already reached 84 °C and drew 402 W on average against the 420 W limit, with the SW thermal flag on 3.2 % of samples and no HW throttle samples. The higher sweep rates are the test of this.
