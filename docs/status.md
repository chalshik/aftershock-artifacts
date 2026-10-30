# Stage 1 status

Living document: update it after every run or decision. Last updated: 2026-10-23.

**Stage 1 is not finished.** The harness is built and the GPU VM works. Only run step 1 of 6 (the smoke test) is done.

**Next action:** step 2, the first real run, on the VM:
`uv run python -m harness.run configs/first_real.yaml` (Qwen3-4B, sessions workload, λ = 2, about 20 min).

## Run steps

| # | Step | Config | Status | Run id |
|---|---|---|---|---|
| 1 | Smoke test (1.7B, random prompts, λ = 0.5) | `smoke.yaml` | Done, VALID | `20261023-145933_smoke` |
| 2 | First real run (4B, sessions, λ = 2) | `first_real.yaml` | Not started | |
| 3 | Repeat the same config, compare | `repeat.yaml` | Not started | |
| 4 | Load sweep, prefix caching on → μ_warm | `sweep_pc_on.yaml` | Not started | |
| 5 | Load sweep, prefix caching off → μ_off | `sweep_pc_off.yaml` | Not started | |
| 6 | Long run at a λ between μ_off and μ_warm | `long_run.yaml` (set the rate first) | Blocked by 4–5 | |

Invalid runs kept on record: `20261023-145613_smoke` (`gpu_steady`, before the check was refined; see decisions.md).

GPU time still needed: about a day (two 8-point sweeps at ~20 min per point, plus a 2 h long run).

## Done when (from the plan)

- [ ] Repeated runs agree within a set tolerance
- [ ] Every run up to the capacity knee passes all checks
- [ ] Load–latency curves with prefix caching on and off; μ_warm and μ_off known
- [ ] A λ inside the gap stays healthy in a long run
- [ ] SLO for later stages fixed from measured healthy latency
- [x] Harness can switch on the gateway and a trigger without a rewrite (config switches exist and are off; trigger logic is Stage 2)

## Decide before the results they judge (pre-registration)

- [x] Repeat tolerance (step 3): throughput ±2 %, TTFT p50 ±10 %, TTFT p99 ±25 %, hit rate ±0.02 (decisions.md, 2026-10-30)
- [x] Capacity rule for μ: valid run, throughput ≥ 0.95 λ and waiting-queue slope ≤ 0.01 req/s² (decisions.md, 2026-10-30)
- [ ] Sweep λ grid, refined after step 2

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
| Disk | 16 GB free (consider growing it before the sweeps) |
| Address | 192.168.3.249 (DHCP, can change on reboot), key `~/.ssh/id_ed25519_vllm` |
| Sync | Mac `git push vm main` → VM `git pull` in `~/aftershock-artifacts` |

## Watch

- The software thermal flag hit exactly the 5 % limit at low load. If heavier runs fail `gpu_steady`, that is a hardware finding (cooling or power limit) to decide on. Don't just loosen the threshold.
