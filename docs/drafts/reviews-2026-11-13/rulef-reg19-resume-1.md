**1. Traces on which the procedure gives a wrong or invalid result.** (Verdict in 4: NOT READY.)

Line numbers are FILE(docs/probe/20261113_reg19/ops/<script>:<line>) or FILE(analysis/gate.py:<line>). "Reproduced" means on dummy directories with the script's own lines, PROBE(/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/41a5ee70-4e70-4e1c-94cf-d6b57d73f40b/scratchpad/zt_test.zsh).

T1. A failed `reg19_step` ends the queue as a futility stop, exit 0. Wrong result; low to moderate.
- queue_reg19e.sh:41 `step=$(cd $W && $PY -m analysis.gate reg19_step 2>… | tail -1)` takes `tail`'s status. Any Python error leaves `step=''` and `cont=''`.
- Line 44 then prints `QUEUE END (futility stop or all seeds done)` and exits 0. Reproduced.
- `reg19_table` reports `stopped_early: True` for four seeds (gate.py:2060), the same as a real futility stop. The [RESULT] would say "stopped because ≥ 3 was out of reach" with seed 19 never run.
- Fix: only `'continue': False` ends with exit 0; anything else is `QUEUE STOP reg19_step failed`, exit 1.

T2. `done` is printed but never checked, which breaks the futility stop. Low.
- If seed 18's folders are not visible in `$W/runs` (T3), `reg19_step` returns `{'done': [15, 16, 17], 'continue': True}` (gate.py:2032–2041): the seed-17 flag again.
- Line 44 passes and seed 19 is launched with seed 18 never judged. Reproduced with that string.
- After seed 19, `reg19_step` raises (gate.py:2030) and T1 prints QUEUE END.
- Fix: require the `done` list to end in `$sd`, else QUEUE STOP.

T3. The link loop accepts wrong links. I could not check how likely: my limits forbid listing `$W/runs`, so "every run folder linked" is unverified.
- Line 39 `[[ -e $W/runs/$n ]] || ln -s $d $W/runs/$n`: on a dangling link of that name `ln` fails ("File exists") and nothing stops (no `set -e`, loop status 0). Reproduced.
- A live link to another folder of the same name (a backup copy, an old path) is accepted. Reproduced.
- `find_runs` then drops the run silently (FILE(analysis/load.py:39)) or reads other bytes.
- Fix: after the loop, `[[ $W/runs/${d:t} -ef $d ]] || QUEUE STOP` for every folder, and stop on any entry of `$W/runs` with no counterpart. Same check before the final `reg19`.

T4. Nothing stops a second launch of a config that already has a valid run. Against "each run once"; moderate.
- ssh failures at launch7.sh:41, 42 and 49 exit under `set -e` while the tmux run goes on or has finished. Rsync, checksum, manifest and step stops also leave a finished run behind.
- The decision gives one command. Re-issued, it relaunches seed 18's control, again labelled attempt 2.
- `ADOPT_*` covers a control only (queue_reg19e.sh:19); a finished burst run cannot be adopted.
- Two valid runs make `reg12_only` raise (gate.py:474), and T1 turns that into QUEUE END.
- `ATTEMPT` is only a file-name label; "at most twice" is enforced nowhere.
- Fix: before each launch count the VM folders `runs/*_$cfg`. One with a valid `checks.json`: adopt it (either kind). Two valid: STOP. Attempt = folders + 1; STOP above 3.

T5. The power limit is re-set silently before every launch. This changes a registered stop; certain by construction.
- launch7.sh:25 `ssh $K $H "sudo -n nvidia-smi -pl 350 >/dev/null"` runs before the read (line 31) and before the checks (lines 36–40).
- A 420 W read is the only sign of a reboot between runs. launch6 stopped on it; the registration says "a limit other than 350 W … stops the queue". launch7 repairs it and discards the "from 420.00 W" text, so seed 19 could run in a third boot session with no record.
- The root command also runs before the compute-process, tmux and tree checks, so it can change the limit under another user's job.
- Fix: read first; STOP on apps, tmux or tree; set the limit only with an explicit flag on the first launch after the known reboot; write the limit before and after, and `uptime -s`, to the probe. On later launches a limit ≠ 350.00 stops.

T6. The final table can be computed from the main tree. Moderate.
- `_burst_cfg` reads `Path(f"configs/{name}.yaml")` relative to the cwd (gate.py:752), and `analysis` resolves from the cwd.
- The queue does `cd $W`. The decision's last step says only "`analysis.gate reg19` once from the worktree".
- With cwd at the repo root, even with `PYTHONPATH=$W`, `analysis/gate.py` and `RUNS` resolve to aftershock-artifacts (checked). Its `analysis/load.py` has been uncommitted-modified since 00:45 today: `withheld.keep` filters `find_runs`.
- Fix: write the exact command, `cd $W && $R/.venv/bin/python -m analysis.gate reg19`, after the pin check, the T3 check and `tools/manifest.py update`, with `analysis.gate.__file__` and `analysis.load.RUNS` printed to the log.

T7. Interpreter and manifest checks are weaker than launch6's. Low.
- The interpreter is the main repo's `.venv`, which follows HEAD's `uv.lock`. launch6 stopped on a changed `pyproject.toml` or `uv.lock`; launch7 dropped that. Both are unchanged today.
- launch7.sh:23 `git diff --quiet $PIN HEAD -- tools/manifest.py` compares two commits, not the file that runs.
- Fix: `git diff --quiet $PIN -- tools/manifest.py uv.lock pyproject.toml`.

T8. launch7.sh:31 `> $PROBE` overwrites the earlier pre-launch read on any relaunch with the same label. Fix: STOP if `$PROBE` exists.

T9. The decision's text widens the rerun rule.
- "if it is invalid by the automatic checks, one more rerun is left (attempt 3)" drops the registered exceptions: `client_error`, `burst_min_kv_max` and a limit ≠ 350 W stop with no rerun; a second heat failure stops.
- The cause of the power-off is not stated. If it was thermal, the lost run is the first heat failure.
- "(no `checks.json` expected)" is not observed. Read its absence on the VM before launching (T4's count does it).
- Fix: restate the exceptions, class the lost run, and say what a second power-off does (I would stop for the owner).

T10. After 120 polls launch7 falls to line 49 and exits 0; the queue prints `RUN … INVALID` (line 28) for a run that may still be running. Old behaviour; low. Fix: a distinct exit code.

Minor:
- ssh has `ConnectTimeout` only; a stalled link hangs the queue. Add `ServerAliveInterval` and `ServerAliveCountMax`.
- `(( TEMP <= 45 ))` passes on an empty `TEMP` (reproduced); only the `LIM` test before it guards this.
- `reg19_step_err_s$sd.txt` holds warnings and tracebacks; open it only after a failed step.

Checked and correct:
- The attempt label with `ATTEMPT_KIND`, the glob `*(/)`, `${d:t}`, the probe file name, and the worktree's `runs/*` and `__pycache__/` ignores.
- No editable install in `.venv`.
- Nothing is printed beyond `done` and `continue`; `[run] checks` carries only `valid` and `failed` (FILE(harness/run.py:208) at the pin).

**2. The strongest alternative explanation**

A boot-session effect. Seeds 18–19 run after an unexplained power-off, in another boot session than seeds 15–17, and the procedure restores and verifies one piece of state, the power limit.
- A reboot can also change the driver or kernel (pending updates), persistence mode, CPU governor, the other user's load, and whatever caused the power-off.
- At λ = 2.0 a few percent of warm capacity is the whole margin (registration: baseline pf 0.978–0.995 against 0.98). The direction is not predictable.

It is confounded with the schedule. From the worktree's `reg19_inputs`, seeds 18 and 19 plan a baseline λp of 2.217 and 2.207 against 1.958–1.972 for seeds 15–17, and seed 18 has the 1.32 span.
- So the pf, hit, TTFT and completion rate in `reg19_baseline_pair` move with λp and cannot separate session from seed.
- The draft's "is the registered read of it" overstates. That readout is burst minus control within a pair, and a session shift cancels in it.

What would separate it:
- Per run, the load-independent parts over [300, 900) s: busy SM clock, busy power and temperature. Compare the controls of 18–19 with those of 15–17, as 2 against 3, not pooled.
- `env.json` field by field between sessions (`cuda_driver`, `platform`, `persistence_mode`, `packages`), plus `uname -r`, `uptime -s` and the driver version in every pre-launch probe. Read these before the GPU hours are spent, not after.
- Only a repeat of an already-run schedule in the new session (seed 15's control, about 1.2 GPU h) identifies it. That is a new registration and the owner's call. Without it the [RESULT] should say the session effect is not identifiable from these ten runs.

**3. Can this decision change any outcome or decision of REG-19?**

Yes.
- **Which seeds run.** T1 can drop seed 19 under a false futility stop; T2 can run it past a real one. Either changes n, k, the label and whether a bound is reported.
- **Reruns.** Counting the lost run as attempt 1 moves the point where "a seed with no valid pair after its reruns stops the queue" fires. The registration's clause for this case is "The queue stops for an operational reason: no table; … the owner decides". The draft does not cite it.
- **The 350 W stop.** T5 changes a registered stop and pre-launch check; it is not operations only. "Unchanged: … stopping rule" is not true while it stands.
- **Item 4.** "k of n with and without that seed" is a new readout. Its sequence is impossible as written: the recheck runs after the [RESULT] but is reported in it, and the log is append-only.
- **Not changed** (verified): per-seed test, thresholds, matrix rule, configs and seeds. The four configs exist at the pin. The order (15, 16, 17, 18, 19) and all five schedule rows reproduce from the worktree.

Is the code-equality claim true? For committed code yes, and more strongly than the draft says. For the code that actually ran it is unproven in two files.
- The worktree is at a7bb77a and clean. `analysis.gate`, `analysis.load`, `harness.run`, `harness.workload`, `harness.config` and `RUNS` all resolve to it (checked with `-B`).
- Every commit from a7bb77a to 9b892e0 (the last before seed 18's control began, 15:10 UTC) touches docs only. `uv.lock` and `pyproject.toml` are unchanged.
- The draft's list omits `harness/run.py`. It is on the path (gate.py:751, `from harness.run import expand`) and changed in 5ee6e38. `expand` itself is unchanged, but the import loads the changed `harness/checks.py` and `recorder.py`. This is immaterial from the worktree, but the sentence was not checked for it.
- The earlier steps ran the working tree, not a commit. `analysis/stats.py` on disk was last written 2026-11-12 20:07 +06, before the seed-17 step, and committed at 21:33 +06 in 1cface7.
- By mtime and identity with the pin, `gate.py`, `derived.py`, `margin.py`, `floor.py`, `harness/config.py` and `harness/workload.py` were the pin's at every step.
- Not shown: `analysis/load.py` (rewritten today 00:45) and `harness/run.py` (last written 22:49 +06 on 11-12).

**4. Verdict: NOT READY.** Required before commit:

1. Queue: a step that is not `'continue': False` or `True` is a STOP with exit 1, and `done` must end in the seed just run (T1, T2).
2. Queue and final command: verify every link with `-ef` and stop on a mismatch (T3).
3. Queue: guard against an existing valid run, adopt either kind, compute the attempt, never overwrite a probe (T4, T8).
4. launch7: read, check, then set the limit once behind a flag; log the limit before and after and the boot time; later launches stop at ≠ 350.00. Otherwise state that the registered stop is changed and by whose authority (T5).
5. launch7: compare the working tree with the pin for `tools/manifest.py`, `uv.lock` and `pyproject.toml`; add the ServerAlive options (T7).
6. Decision text:
   - the exact final command with its guards (T6);
   - the rerun exceptions, the class of the lost run and a second power-off (T9);
   - the code-equality paragraph corrected as in 3;
   - item 4 reordered and named a new readout;
   - the `reg19_baseline_pair` sentence weakened, with the boot and env read added;
   - what "the interim look" in item 6 was.
7. Before any launch: one `reg19_step` from the worktree, with the prediction registered first: `'done': [15, 16, 17] 'continue': True`.
   - It closes the gap in 3: that flag implies the two earlier ones under the pinned code.
   - It tests the links and the loader before 4.7 GPU h are spent.
   - State it as a repeat of a look already taken. Any other output stops for the owner.
8. Lost folder:
   - Say what happens to `reg19` once it is in `runs/`. A truncated JSONL line makes `load_run` raise (FILE(analysis/load.py:13)), so seed 18's pattern would fail for good.
   - I recommend copying it now, checksummed, to a holding place outside `runs/`: the VM holds the only copy.

Could not check:
- `decisions.md`, `status.md`, `RESUME.md` and `delegation.md` (present in the review folder, not on my list, not opened). So the delegate's authority for the rerun, the pin rule and a sudo command per launch is unverified.
- The contents of either `runs/`, the VM, and the cause of the power-off.
