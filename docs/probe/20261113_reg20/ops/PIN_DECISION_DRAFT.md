# REG-20: which commit the runs use (draft for the owner; nothing here is binding)

Written 2026-11-13 by a teammate agent, 0 GPU h, no run read. The VM was not contacted.

## Facts (each from `git` on the Mac, 2026-11-13)

- REG-20's approval names no commit. It requires only that `analysis/k1.py`, `analysis/stats.py`, `tests/test_k1.py` and the 17 REG-20 configs are committed before any run (FILE(docs/decisions.md:4169)). They are, in `1cface7` (`1cface77ca001cdf5d90de9313ddd4a3af4569a1`, 2026-11-12).
- `a7bb77a` (REG-19's pin, the commit REG-19's closed arm runs from) is an ancestor of `1cface7`, and `1cface7` is an ancestor of HEAD (`e404c74` when this was written).
- `git diff --stat a7bb77a 1cface7 -- harness/`: **empty**. The harness is byte-identical. Between those two commits only the 17 REG-20 configs are added under `configs/`. `uv.lock`, `pyproject.toml` and `tools/manifest.py` do not change.
- `git diff --stat 1cface7 HEAD -- harness/`: **4 files, 163 insertions and 29 deletions**: `checks.py` 42, `loadgen.py` 83, `recorder.py` 50, `run.py` 17. All of it comes from one commit, `5ee6e38`: the A14 recorder fix with its stricter `recorder`/`gpu_steady` checks, and the session cap, which is off unless a config sets it (FILE(docs/decisions.md:4200-4216)). From `1cface7` to HEAD no REG-20 config changes, and neither do `uv.lock`, `pyproject.toml` or `tools/manifest.py`. In `analysis/`, `k1.py`, `gate.py` and `stats.py` are unchanged. `load.py` changes by 6 lines (the seal guard), and `withheld.py` is new: it seals REG-20's run folders until "[RESULT] REG-20" is in the log.

## Options

| Pin | What it gives | What it costs |
|---|---|---|
| **`1cface7`** (default in `common.sh`) | Same harness as REG-19's closed arm, so the loop flag is the only harness difference between the paired runs. `k1.py` is identical to HEAD's. The VM moves from `a7bb77a` and gains only configs, analysis and docs. No seal module, so the worktree computation needs no `AFTERSHOCK_UNSEAL` | No A14 fix. The recorder can still die on a half-written line, and an open-loop backlog writes the most lines. A run that loses its recorder becomes `lost_open` after its rerun, which counts against K1 (FILE(docs/decisions.md:4067)). The old checks are weaker: a recorder death can go unflagged, as in A14 |
| **HEAD (or any commit ≥ `5ee6e38`)** | A14 fix and stricter checks: a run whose recorder died is invalid, not silently short | The open arm runs a different `loadgen.py`, `recorder.py`, `run.py` and `checks.py` from the closed arm, a harness change confounded with the loop flag. The drift rerun (closed seed 15 at the new pin) measures only part of that. Stricter checks also invalidate more open runs, which pushes them towards `lost_open` |
| `1cface7` for the runs, plus `analysis.recheck` of today's checks before the table (as REG-19's `final.sh` does) | Same harness for both arms, and the A14 checks still flag a recorder death on the record | The recorder's own failure mode is not fixed, only detected, so a detected death still costs a rerun or a `lost_open` |

Either choice is a decision with a decisions.md entry before the VM moves. Research rule 6 requires a clean tree at the registered commit (FILE(docs/decisions.md:4057)).
