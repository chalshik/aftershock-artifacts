# aftershock-artifacts

Stage 1 harness for a metastable-failure study of vLLM prefix caching. Plan: `docs/experiment-plan.md`. Rules: `CLAUDE.md`.

## On the GPU VM
```bash
git clone <repo> && cd aftershock-artifacts
bash env/setup_vm.sh                                  # driver check, pinned env, model download
uv run python env/probe.py                            # answers open questions -> docs/probe/
uv run python -m harness.run configs/smoke.yaml       # then first_real, repeat, sweep_pc_on, sweep_pc_off, long_run
```
Each run writes `runs/<run_id>/` and prints VALID or INVALID (the reasons are in `checks.json`). Commit before you run: a dirty tree is refused.

## On the Mac
```bash
uv sync --extra analysis && uv run pytest             # full harness test against tests/fake_vllm.py
rsync -av vm:aftershock-artifacts/runs/ runs/         # then open analysis/analysis.ipynb
```
