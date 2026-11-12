REG-19 resume review, final (same content as my earlier message 8aec7400, resent on request): NOT READY, nine changes required.

**1. Traces on which the procedure gives a wrong or invalid result.**

T1. `reg19_step` fails open, and the queue never checks that the seed it just ran is in `done` (futility stop).
- queue_reg19e.sh:39 `[[ -e $W/runs/$n ]] || ln -s $d $W/runs/$n` has no error check and the queue has no `set -e`. If a seed-18 link is not made (ln error, or a dangling entry of that name), gate.py:2029 gives `has = (False, False)` for seed 18, `done = [15, 16, 17]`, and gate.py:2041 returns the same `continue` as after seed 17, which was True. queue:44 passes and seed 19 launches with seed 18 never judged.
- Effect: if k after seed 17 is 1 and seed 18 fails, the registered stop (k + 1 < 3) is skipped. That costs 2.4 GPU h and reports n = 5 where the registration says n = 4 with no bound. The label is not changed.
- Same shape at HEAD: withheld.py:26 seals `*_l1pl350cl_r2.0_w3000_s1[5-9]`, so `find_runs` returns [] for every seed and `reg19_step` gives `{'done': [], 'continue': True}` (derived from gate.py:2026–2041 and the `too_few` branch at 1694; not executed). Any recovery typed by hand in the main repo gets "continue: True" whatever the data say.
- Likelihood: a few percent on the scripted path; realistic on the by-hand path (T6).
- Fix: after queue:43, stop unless the `done` list is exactly 15..$sd.

T2. A crashed step is reported as a futility stop with exit 0.
- queue:41 `step=$(cd $W && $PY -m analysis.gate reg19_step 2>… | tail -1)` takes tail's status. Any exception (`reg12_only` "2 valid runs", a truncated jsonl, a failed `cd`) gives `step=""`, `cont=""`, and queue:44 prints `QUEUE END (futility stop or all seeds done)` and `exit 0`.
- Inherited from queue_reg19d, but that line is what decides whether "stopped because ≥ 3 was out of reach" gets written.
- Likelihood: moderate over two steps.
- Fix: `[[ -n $cont ]] || { echo "QUEUE STOP reg19_step failed"; exit 1; }`, and print QUEUE END only on `'continue': False`.

T3. The "clean at pin" check does not cover the data the step reads.
- launch7:20–21 and queue:40 check git state, but `$W/runs/*` is ignored (worktree .gitignore), so nothing checks that each `$W/runs/<id>` is a link to `$R/runs/<id>`. An entry that already exists (a real folder, a link to the same-disk backup) passes `-e` at queue:39 and is read as it is.
- The six runs of seeds 15–17 were linked before this script and decide k.
- Fix: before the step, for every id matching REG-19's two patterns require `$W/runs/$id(:A) == $R/runs/$id`, with the same count on both sides.

T4. The power-limit set erases a reset between runs instead of stopping the queue.
- launch7:25 `ssh $K $H "sudo -n nvidia-smi -pl 350 >/dev/null"` runs on every launch, before the read (line 31) and before the idle checks (lines 38, 40), and discards its output.
- Trace: the VM restarts between seed 18's burst run and seed 19's control. tmux is gone, the tree is clean, there is no compute app, the limit is 420, it is set to 350, the probe reads 350.00, and seed 19 runs. No file records the restart.
- The registration's stopping rule lists "a limit other than 350 W" as a queue stop; under launch6 that read was the tripwire.
- Second effect: if another user's job is on the GPU, the root command changes their limit first and only then stops at line 38.
- Likelihood: not small. The VM went off once in this queue and the bundle does not say why.
- Fix: set 350 W once, as its own recorded step before the queue (limit before and after, plus `uptime -s` or the boot id, in a probe file), and keep launch7 read-only so a non-350 read stops it. At the least, read `power.limit` before the set, write it to the probe, move line 25 after the idle checks, and stop if the value before the set is not 350 on any launch but the first.

T5. Attempt numbers live only in a typed environment variable, and probes are overwritten.
- launch7:31 `> $PROBE` overwrites. If attempt 2 of seed 18's control is invalid and the same command is run again with ATTEMPT=2, the third launch overwrites `…_s18_attempt2.txt` and is recorded as attempt 2. A fourth launch as "attempt 3" then exceeds "at most twice".
- `ATTEMPT_KIND=control` (a typo for `stage2_control`) silently labels everything attempt 1.
- queue:24 `queue19_$cfg.out` and queue:41 `reg19_step_err_s$sd.txt` are overwritten the same way.
- Fix: launch7 stops if `$PROBE` exists; the queue rejects ATTEMPT > 3 and any ATTEMPT_KIND other than `stage2_control` or `burst`; put the attempt in the .out name.

T6. A launched folder with no `checks.json` is undefined, and it is the likeliest failure right after a reboot.
- launch7:41 `… && sleep 15 && grep -m1 run_id $LOG`: the `[run] start` line comes after `uv run`, the imports and the environment snapshot (run.py:124–138). On a cold machine that can exceed 15 s. grep fails, `set -e` exits 1, the queue stops, and the run carries on in tmux unattended.
- run.py:158–161: if the server is not ready in time, `SystemExit` skips `checks.write` (run.py:207) and leaves a folder with no checks.json. By item 1's logic that would be attempt 2 and leave one rerun; the decision does not say.
- A burst run that finishes but is not reported (launch7:49's last ssh failing gives rc 255 after DONE) has no adoption path: queue:19 adopts controls only. Re-running the queue launches a second burst run, against "Each run once", and two valid burst runs make `reg12_only` raise (T2).
- Likelihood: item 6 mentions four queue stops over three seeds, so a stop in the next two seeds is more likely than not (my belief, not checked).
- Fix: state now how a no-checks folder counts; add adoption for the burst run or a step-only mode; give the exact by-hand command, starting with `cd $W`.

T7. Smaller points, fail-safe or cosmetic.
- launch7:23 `git diff --quiet $PIN HEAD -- tools/manifest.py` compares commits, but queue:38 runs the working-tree file. Use `git diff --quiet $PIN -- tools/manifest.py`.
- launch7.sh, queue_reg19e.sh and manifest.py run from the main working tree for about 5 h while that tree keeps changing. "The Mac's HEAD no longer enters REG-19" holds for the analysis, not for the operations. Record the scripts' commit (72fafb5) in the entry and check it at each launch.
- `PIN`, `REG19_WORKTREE`, `VM_HOST`, `WAIT_MIN`, `PROBE_DIR19` and `ADOPT_*` come from the environment. None is set in my shell; a stray `PIN` would move every check.
- There is no `ServerAliveInterval`, so an ssh that hangs mid-command blocks the queue silently.
- launch7:20 and :39 compare `--short` hashes. Safe, but compare full hashes.
- launch7:44–49: if the 120 min wait ends with tmux alive, the queue prints `RUN … INVALID` for a run that is still running.
- Disk is read (`df`) but not checked, though the registration lists it.
- `.venv/bin/python` replaces `uv run`, which synced to the lock. Nothing now checks the venv against `uv.lock` (the lock is identical in both trees).

Checked and fine:
- Both scripts parse (`zsh -n`), including the `(/)` qualifier.
- For the given command, the control of seed 18 gets `attempt2`; its burst run and seed 19 get `attempt1`.
- `.run.lock` is an flock (run.py:227–229), so the power-off left no stale lock.
- The `[run] checks` line carries only `valid` and `failed` (run.py:208), and the queue prints only `done` and `continue`.
- From `$W` with the repo's venv, all eleven closure modules resolve to the worktree; there is no editable install and no PYTHONPATH.
- `reg19_inputs` from the worktree reproduces the registered table for all five seeds and the order 15–19.

**2. The strongest alternative explanation.**

A machine state that changed with the reboot and is common to both runs of seeds 18 and 19.
- The procedure restores one setting (350 W) and checks temperature, an idle GPU and the tree. Nothing compares driver, kernel, persistence mode, CPU governor or anything else the reboot reset against seeds 15–17.
- Seed and session are fully aliased. Seeds 18–19 also have a different schedule (baseline λp 2.22 and 2.21 against 1.96–1.97; seed 18's 1.32 span), so load-dependent readouts (pf, hit, TTFT) cannot separate the two.
- The decision calls `reg19_baseline_pair` "the registered read of it". It is not. gate.py:1939 `out["diff"]` is burst minus control within one pair, and `order_flag` (1940–1942) uses only that difference. A shift that hits both runs of a pair cancels.

What would separate it from a real effect:
- Per-run levels, not differences, of load-independent quantities across all the runs: busy SM clock, busy power and temperature over [300, 900) s. These are already in `out["control"]` and `out["burst"]`.
- `env.json` of a seed 15–17 run against a seed 18–19 run (driver, kernel, packages), and the boot id in the pre-launch probe.
- The clean separation is a repeat of one of 15–17's controls in the new session. That is a GPU run and the owner's call.

**3. Can this decision change any outcome or decision of REG-19?**

Yes.
- Stopping rule, item 1: counting the lost run as attempt 1 is a reading of a case the registration does not define. It is the conservative reading, but it decides whether seed 18 can end the queue after one more invalid run rather than two, which gives no table.
- Stopping rule, item 3: at pre-launch, "a limit other than 350 W … stops the queue" becomes "is set to 350 W" (T4). The in-run `power_limit` check is unchanged.
- Futility stop: unchanged in code, breakable in operation (T1, T2). That affects n, the "k of n" wording and whether a bound is reported.
- Item 4 adds a readout (k of n with and without a run the stricter checks fail). It is declared before the data and the registered outcome stands, which is fine. As written it cannot be done: `analysis.recheck` at HEAD skips REG-19's runs until a `[RESULT] REG-19` heading exists (withheld.py:26, 53), and that entry cannot be edited afterwards. "Ten runs" also assumes no futility stop.
- Not changed: the per-seed test, thresholds, order, matrix rule and the validity checks used for the result. `analysis/gate.py` is byte-identical between a7bb77a and HEAD.

The claim "the worktree's code equals the code that computed the earlier steps in every function REG-19 calls" holds as far as git can show, but not for the reason given.
- The premise is false. `analysis/load.py` and `analysis/tables.py` are not byte-identical between a7bb77a and HEAD (0441027). Commit 72fafb5, the same commit that added these scripts, put `withheld.guard` into `load_run` and `withheld.keep` into `find_runs` and `arrival_table`.
- The rest of the list is right: gate.py, derived.py, margin.py, floor.py, harness/config.py, harness/workload.py and tools/manifest.py are identical, and stats.py gained 9 lines.
- The conclusion holds because the only commits touching the import closure after a7bb77a are 1cface7 (15:33 UTC on 11-12), 5ee6e38 and 72fafb5. All are later than seed 18's control launch (15:10 UTC, from the run id in item 5), so later than the last earlier step.
- The text should also say that HEAD can no longer compute REG-19 at all (T1), so the worktree is the only path.
- With "every run folder linked", the worktree is an unsealed copy of every sealed run (the REG-20, E0 and E1 patterns in withheld.py:27–30), readable by pin-era code with no guard. `reg19_pair` and the helpers I grepped load only REG-19's two patterns.

Unchecked:
- The delegation entry and the owner's allowance of the sudo command (decisions.md was off limits).
- RESUME.md, including "the interim look it records", which sits oddly beside "No interim look beyond `reg19_step`'s `continue` flag" and "This agent has read no outcome".
- The links in `$W/runs` (listing `runs/` was off limits), and the six runs' checks.json.
- The VM: sudoers scope, driver state, the lost folder, whether the 15 s start race actually occurs.
- Uncommitted edits in the Mac's working tree at the time of the seed 15–17 steps.
- The callees of `reg8_gate_verdict` (whether they load any run outside REG-19's two patterns).
- `nvidia-smi -pl`'s exact output and the cause of the four earlier queue stops.

**4. Verdict: NOT READY.** Required before it is committed:

1. Correct item 2's "Difference from seeds 15–17": load.py and tables.py differ from HEAD since 72fafb5. Give the commit-date argument instead, and state that HEAD returns `done: []`, `continue: True` for REG-19.
2. queue_reg19e.sh: stop unless `done` is exactly 15..$sd; stop with a non-zero exit on an empty `continue`; print QUEUE END only on `'continue': False`.
3. queue_reg19e.sh: check the `ln` result, and verify before each step that every REG-19 run id in `$W/runs` resolves to `$R/runs/<id>`. Link only REG-19's folders.
4. launch7.sh: make the 350 W set a single recorded step before the queue (or record the limit before the set and the boot id, and move the set after the idle checks). A non-350 read on a later launch stops the queue, as registered.
5. launch7.sh: refuse to overwrite an existing probe; the queue rejects ATTEMPT > 3 and an unknown ATTEMPT_KIND, and puts the attempt in the .out name.
6. Decision text: say how a launched folder without checks.json counts against "at most twice". Give the exact recovery path after a stop that follows a valid burst run (adoption for the burst run, or a step-only mode, run from `$W`), and the exact final command `cd $W && $R/.venv/bin/python -m analysis.gate reg19`.
7. Risks paragraph: drop "`reg19_baseline_pair` … is the registered read of it". Name per-run levels of busy SM clock, power and temperature, the `env.json` comparison and the boot id as the readout of a session shift, reported and not decisive.
8. Item 4: the recheck goes in a separate entry after the [RESULT]; replace "ten runs" with "the runs made". Say in one clause what "the interim look" in item 6 was.
9. Minor: compare tools/manifest.py against the working tree; pin and check the scripts' commit; add `ServerAliveInterval`; compare full hashes; check free disk.