# E1 operations scripts: design notes

Written 2026-11-13 by a teammate agent. 0 GPU h. No VM contact; no run folder opened. The registration is `docs/drafts/e1_draft4.md` (draft 4). Its spec: the "Stopping rule" (FILE(docs/drafts/e1_draft4.md:41-47)) and "Pre-launch and launch" (FILE(docs/drafts/e1_draft4.md:55-56)). Model: ops_r3 (`docs/probe/20261113_reg19/ops_r3/`). Part 1 is for the reviewers to check against the draft. Part 3 is described, not decided.

## 1. Where the draft had to be read, and how the scripts read it

**I1. How attempts are counted when the sweep is attempt 1.**
- A rate's attempts are:
  - 1 if the sweep started it (the sweep's launch log has a `run_id` line for that rate), else 0;
  - plus each single-rate launch of that rate.
- Every launch is one attempt, whatever it left behind, as in ops_r3.
- At most 3 attempts per rate.
- A rate the sweep never started gets single-rate attempt 1 (FILE(docs/drafts/e1_draft4.md:43)).
- "Started" is judged from the log's `run_id` line, which the harness prints right after it makes the folder (FILE(harness/run.py:136-143)).

**I2. The sweep is launched at most once, ever.** "One harness invocation of the sweep" (FILE(docs/drafts/e1_draft4.md:42)). If the sweep's launch fails before any rate starts, every rate counts as never started and runs from its single-rate config. That covers a failed launch command or a harness stop before its first run. A second sweep would be a rule the draft does not have.

**I3. "Stops the sweep" means E1 stops.** These stop before any launch, at any rate, including rates the sweep never started:
- `no_errors` or `power_limit` in any E1 run's `failed`;
- a second `gpu_steady`;
- a run without `checks.json`.

The draft says "stops it" and "stops the sweep" (FILE(docs/drafts/e1_draft4.md:44)). Rates run independently after the sweep, so a per-rate reading would let other rates go on, and the draft does not say that. The first sandbox run had the lost-run stop per rate; it was made global and given its own case.

**I4. The second heat failure is counted among all of E1's runs**, as ops_r3 counted among all of REG-19's (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:136)). It is not counted per rate.

**I5. Any `no_errors` stops E1.**
- The draft equates `no_errors` with "a client error".
- ops_r3 stopped only on `no_errors/client_error`, which it learned by reading that check's detail (FILE(docs/probe/20261113_reg19/ops_r3/vm_state.py:32-35)).
- E1's reads exclude details (FILE(docs/drafts/e1_draft4.md:45)). So an HTTP error also stops E1, which is stricter than ops_r3.

**I6. A rate whose 3 attempts are spent does not stop the other rates.**
- It is not launched again.
- The remaining rates still run.
- The queue then ends with `QUEUE END` (exit 3), naming the rates that have no valid run.

The draft does not list spent attempts among the stops, and its analysis has a "holes" status for a rate with no valid run (FILE(docs/drafts/e1_draft4.md:20)). ops_r3 stopped instead. In REG-19 a spent config ended the seed sequence; E1's rates are independent. The lead's checklist said "3 invalid attempts → stop". Here the rate stops and the queue ends non-zero, but other rates are not held back.

**I7. Pause after an invalid run.** This is ops_r3's behaviour (FILE(docs/probe/20261113_reg19/ops_r3/queue.sh:55)) and is not in the draft.
- After the queue sees an invalid run, it copies what is pending and stops before the next launch.
- Starting it again applies the rule.
- The point: with a new harness (part 3), a systematic failure shows after the sweep, about 2.1 h, before the reruns spend about 4.2 h more.
- Reviewers may drop it. It is the `PAUSE` lines in `queue.sh`.

**I8. Two valid runs at one rate.**
- Nothing is launched.
- The end record and the output list both runs.
- The earliest is marked as the one `e1.first_valid` counts (FILE(docs/drafts/e1_draft4.md:21)).

ops_r3 stopped instead.

**I9. What "a valid run found on the VM" means.** It is a run that one settled launch log of these scripts names, made at the registered commit. Any of these stops E1, for the owner:
- a folder that no log names (a launch outside the scripts, or a lost log);
- a named run missing from the VM;
- an E1 folder on the Mac that the VM does not list (ops_r3's T2).

**I10. How the approval is recognised.**
- `e1_commit.txt` holds a commit.
- At that commit, `docs/decisions.md` must hold the `[REG] E1` heading and, later, a heading `[DECISION] (owner|delegate) E1 approved`.
- The owner's entry of 2026-11-13 lets the delegate register E1 once both reviews clear (FILE(docs/decisions.md:4516-4520)). It prescribes no heading.
- This heading form is a choice made here. Without some fixed form, no script can tell "the commit that holds the approval" (FILE(docs/drafts/e1_draft4.md:47)) from any other commit.

**I11. Waiting for REG-19's `[RESULT]` (open for the owner).**
- The draft says E1 "runs after REG-19's queue has ended and its [RESULT] is written" (FILE(docs/drafts/e1_draft4.md:9)).
- RUNBOOK §4 deploys `main` to the VM only after REG-19's `[RESULT]` (FILE(agent/RUNBOOK.md:50)).
- The owner's entry forbids only running E1 before its `[REG]` is committed, or while REG-19's queue holds the GPU (FILE(docs/decisions.md:4520)).
- Draft 5 drops that wait: the scripts wait for an `[OPS] REG-19: the queue ended` or `[RESULT] REG-19` heading (`END19_PAT`) and for REG-19's lock to be absent.
- REG-19's table waits for REG-21's and REG-22's entries (FILE(docs/status.md:11), "`final.sh` is not run until both entries are committed"). So the GPU may sit idle between REG-19's queue end and E1.
- Dropping the gate is one line in `common.sh`, but it changes the registration's text, so it is the owner's call.

**I12. Checking a run's commit without reading `env.json`.**
- The harness's start line holds both the run id and the commit: `[run] start {'run_id': …, 'git_commit': …}` (FILE(harness/run.py:143)).
- That is a launch-log line "holding run_id", an allowed read (FILE(docs/drafts/e1_draft4.md:46)).
- The scripts take the commit from it. A run made at another commit stops E1.
- ops_r3 read `env.json`'s `git_commit` instead (FILE(docs/probe/20261113_reg19/ops_r3/vm_state.py:21)). E1's rule "read nothing else of any run" excludes that.

**I13. What is copied.**
- Every run with a `checks.json`, valid or invalid, is copied and checksum-verified. This is REG-20's form; ops_r3 copied only valid runs. Raw data is kept and copied whether valid or not, and the copy reads no content.
- Runs without `checks.json` are not copied by the queue. Copying them is a separate step, as RUNBOOK §3.6 did for REG-19's lost run (FILE(agent/RUNBOOK.md:48)).

**I14. When an invocation has "ended".**
- The end is the tmux session `run` being gone. ops_r3 waited for one `checks.json` instead.
- For the sweep, one `checks.json` would mark only the first rate's end.
- The next launch's pre-launch check needs no tmux session in any case.
- `settle` reads the log only once the session is gone.

**I15. "A session probe once" means once per boot.**
- A second probe is refused unless `RENEW=1`, as in ops_r3.
- A reboot between launches fails the boot-id pre-launch check, which is "an unexpected pre-launch check" that stops E1 (FILE(docs/drafts/e1_draft4.md:44)).
- So a renewal needs a decisions entry. The owner also has to set 350 W again, since a reboot resets the limit to 420 W.

**I16. `SET=1` on the probe is kept** from ops_r3, for the owner's use only (FILE(docs/drafts/e1_draft4.md:56): "The owner must set 350 W unless a sudoers rule … exists"). Launches never set the limit.

**I17. The pre-launch read adds `uv.lock`'s blob.** The lead's list asks for it; ops_r3 checked it only in the probe. A clean tree at the commit implies it, but the check is cheap.

**I18. The first launch requires a clean slate.** No E1 folder may exist on the VM or the Mac, and no record in `state/`. The configs are "committed, unused" (FILE(docs/drafts/e1_draft4.md:14-15)).

**I19. How a heat rerun "after cooling to ≤ 45 °C" is done.**
- Every launch first waits up to 30 min for ≤ 45 °C (ops_r3's loop), then checks the temperature again in the pre-launch read.
- A GPU still hot stops the launch without spending an attempt.
- Note: within the sweep the rates run back to back with no cooling. The registered single invocation implies that; REG-8's part b ran the same way at 350 W, all valid (FILE(docs/decisions.md:1745-1752)).

## 2. Differences from ops_r3, and why

1. **No pinned worktree, links, `analysis.recheck`, step records or `final.sh`.** E1's result is a hand command later (FILE(docs/drafts/e1_draft4.md:53)), and its harness *is* the checks in force, so there is nothing to recheck.
2. **`vm_state.py` reads only `valid` and `failed`.** No `no_errors` detail, no `env.json`. It also requires `failed` to be a list of plain check names; anything else is "unreadable".
3. **Records.**
   - The attempt records are `attempt_sweep_1.txt` and `attempt_r<rate>_<n>.txt`. Each names its launch log.
   - New: `settled_<attempt>.txt`, with the run ids and commits from the log's `run_id` lines.
   - Folders are accounted for by name, not by count. ops_r3's rule "folders ≤ attempts" cannot tell a sweep's run from a rerun, because they share one name pattern (FILE(harness/run.py:36), FILE(configs/sweep_l1pl350cl_pc_off_only_r2.yaml:6)).
4. **Copying.** One run at a time, with a copy record written after the manifest update (REG-20's `copy_verify`). Invalid runs are copied too (I13).
5. **Global stops** (I3, I4) where ops_r3's were per config.
6. **No quiet hours.** The owner withdrew them (FILE(docs/decisions.md), 2026-11-13 [DECISION] (owner), quiet hours withdrawn).
7. **Waiting.**
   - The wait polls the tmux session (I14).
   - It stops after `UNREACH_MAX` = 15 unanswered reads in a row. ops_r3 polled for its whole `WAIT_MIN` and then judged only the last three reads (FILE(docs/probe/20261113_reg19/ops_r3/launch.sh:76)). A 240 min sweep wait would otherwise poll a VM that is off for up to 4 h.
   - The default waits: 240 min for the sweep, 60 min for one rate. The sweep needs 6 × (900 + 300 + about 60 s) = 126 min (DERIVED; FILE(docs/drafts/e1_draft4.md:59)). `WAIT_MIN` overrides both.
8. **The pre-launch read adds `uv.lock`** (I17).
9. **The allowed-reads line prints on every stop**, on a line of its own, including Mac-side refusals. The sandbox checks this for every case that ends non-zero.
10. **Scripts are tied to the registered commit.** The scripts must equal their text at the registered commit; `scripts_commit.txt` is gone. This is stricter: the reviewed, registered scripts are what runs.
11. **`vm_checkout.sh` is new** (the lead's item 4; RUNBOOK §4).
12. **`ready_to_run`.** No queue, launch or checkout while REG-19's lock exists (existence only) or before an `[OPS] REG-19: the queue ended` or `[RESULT] REG-19` heading is committed (I11).
13. **Every parameter is in `common.sh`.** ops_r3's `launch.sh` had 45, 60, 30, 24, 5 and 120 written inline.
14. **A zsh trap avoided.** `$VAR:` followed by a letter is a zsh modifier. Example: `$H:repos…` would have dropped `.50` from the VM's address. Every such case is written `${VAR}:`. The sandbox checks the real `common.sh`'s `H` and `VM_GIT`, because it replaces them.

## 3. Open point (described, not decided): E1 would be the first GPU run on the current harness

**Facts.**
- REG-19 runs at `a7bb77a` (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:11)).
- E1's registered commit will be on `main`. `main` includes 5ee6e38: the A14 fix, which is a recorder that survives a half-written line and logs its death; stricter `recorder` and `gpu_steady` checks; and a session cap in the load generator, off unless `workload.sessions.cap` is set (FILE(docs/decisions.md:4200-4205)).
- `git diff --stat a7bb77a HEAD -- harness/`: 4 files, 163 lines in, 29 out. `pyproject.toml` and `uv.lock` are identical between the two (`git diff --stat` empty, checked 2026-11-13).
- The fix was "not deployed to the VM" (FILE(docs/decisions.md:4201)).
- E1's configs set no `cap` (grep of the sweep config, its parent, `base.yaml` and `defaults.yaml`).

**What a first run risks.**

**R1. A code fault that crashes a run.**
- `checks.json` is written only after a run's `try/finally` ends normally (FILE(harness/run.py:218)).
- An exception other than KeyboardInterrupt also ends the whole sweep, because of the list comprehension (FILE(harness/run.py:243)).
- Result: one folder without `checks.json`; E1 stops at it (I3). Cost: at most one run.

**R2. A fault that fails `recorder` on every run without crashing.**
- All six sweep rates come back invalid after about 2.1 h.
- The pause (I7) stops the queue there.
- Without the pause, the reruns would spend about 4.2 h more before every rate is spent. The pause is the only brake.

**R3. `gpu_steady` is no longer only heat.**
- Since 5ee6e38 it also fails when the GPU samples do not cover [warm-up, duration] with no gap above `max_scrape_gap_s` = 2.0 s, or when no sample is busy (FILE(harness/checks.py:127-136), FILE(configs/base.yaml:55)).
- E1's scripts read only `failed`, so they cannot tell a coverage failure from heat. Either one:
  - gets the heat rule's single rerun;
  - counts toward "a second heat failure stops E1".
- The heat rule was written when `gpu_steady` meant heat (BELIEF as to intent; the threshold names `max_sw_thermal_frac` and `max_sm_clock_cv` are heat and clock measures).

**R4. The recheck evidence covers less than it may seem.**
- The recheck of 182 folders under the new checks changed no valid run (FILE(docs/decisions.md:4205)).
- That is evidence that the old recorder's output passes the new checks.
- It is not evidence that the new recorder or load generator produce such output on the GPU.

**R5. E1's floor is compared with REG-8's 1.681 req/s, measured under the old harness.** The draft already names this confound (FILE(docs/drafts/e1_draft4.md:39)). With the cap off, the load generator's closed-loop path changes only in bookkeeping:
- `t_arrived` is written only under a cap;
- the arrival-rate check uses `t_arrived` only if the column exists (FILE(harness/checks.py), the `t_arrived` branch).

This is BELIEF, from reading the diff; no run shows it.

**R6. The move off `a7bb77a` is the first deploy since REG-19.** RUNBOOK §4 allowed a deploy only after REG-19's `[RESULT]`; the registration supersedes that for E1's move and amends RUNBOOK (DA5).

**Options for the reviewers (none chosen here).**
- (a) Accept: the pause bounds R2 to the sweep's 2.1 h before a person looks.
- (b) A short smoke run on the new harness first. That is a GPU run, so the owner decides, and it needs its own registration.
- (c) Re-word the heat rule for R3. That changes the registration.

## 4. Not done

- Nothing is committed.
- The scripts were never run against the real VM.
- `uv run pytest` was not run: the lead's limits exclude anything that reads runs, and `tools/check_docs.py` is part of it.
