# aftershock-artifacts

A metastable-failure study of vLLM prefix caching. The source of truth is `docs/experiment-plan.md`.
**Current scope: Stage 1 only** (the harness plus a healthy baseline). Do not build Stage 2.

## Map
- `harness/`: runs on the GPU VM. `run.py` is the only entry point: `uv run python -m harness.run configs/<x>.yaml`
- `configs/`: one YAML per run or sweep. Each one `extends: base.yaml`.
- `env/`: VM setup (`setup_vm.sh`) and `probe.py`, which answers the open questions on the pinned vLLM.
- `analysis/`: notebook plus `load.py`. Reads only from `runs/`.
- `runs/<run_id>/`: raw output of every run, gitignored. Copy it off the VM with rsync.
- `docs/status.md`: current state of Stage 1. Update it after every run or decision.
- `docs/decisions.md` (append-only log), `docs/open-questions.md`
- `tests/`: `uv run pytest` runs on the Mac against `tests/fake_vllm.py`, with no GPU.

## Research rules (non-negotiable)
1. **Stage 1 scope.** Triggers and the gateway exist only as config switches that stay off (`trigger: null`, `gateway.enabled: false`).
2. **Fixed choices:** single replica, served directly; open-loop arrivals; no client retries or timeouts; no KV offload or sharing.
3. **Pinned versions.** vLLM is pinned in `pyproject.toml`. Never upgrade it during the study. Any `uv.lock` change needs an entry in `docs/decisions.md`.
4. **Raw data is immutable.** Never edit, rewrite or delete anything in `runs/`. A failed run is kept and marked invalid in `checks.json`.
5. **Every parameter lives in config.** No magic numbers in code. Once a run has used a config, never edit it; copy it to a new file.
6. **Reproducible.** Seeds are fixed, the schedule is written before the run, and a run from a dirty git tree is invalid.
7. **Pre-register.** Write thresholds, tolerances and SLOs into config or `decisions.md` *before* looking at the results they judge.
8. **Figures** come only from run folders, through `analysis/`.
9. **Evidence, not memory.** Answer an open question only with probe output, the vLLM source at the pinned version, or a run id.
10. **Report honestly.** An invalid run, a surprising number or a deviation from the plan goes into `decisions.md`, not under the rug.

## Machines
The Mac is for code and analysis only. The Linux VM with the RTX 3090 runs `harness/` and vLLM.
