REG-19 resume, review round 2: **NOT READY**. All nine round-1 changes are in, but the rewrite leaves six traces that give a wrong or invalid result, plus three smaller script and wording defects (twelve required changes in section 4).

What I ran:
- `zsh -n` on all five scripts: clean.
- The official sandbox: 29 of 29 pass.
- The real `mac_checks` (git reads only): rc 0, SC = 7f4efb5f…, equal to `scripts_commit.txt:1`.
- My own stub sandboxes, 13 `links_ok` cases and 19 queue and session-probe cases:
  - `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/r2_links.zsh`
  - `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/r2_queue.zsh`

"Case n" below means a case in `r2_queue.zsh` unless it says links.

**1. Round-1 items**

- F1: FIXED. `decision_draft2.md:12–13`. My `git log` agrees: 1cface7 is the first commit after the pin on those paths, 15:33:58 UTC; 72fafb5 is 19:00:16 UTC. `done: [], continue: True` at main follows from `gate.py:2026–2041`, `1694–1710` and `withheld.py:26`.
- F2: FIXED. `queue_reg19f.sh:59–60` (rc), `63–65` (done list exactly 15..sd), `66` (flag), `68–70` (END only on False). The parse matches what `gate.py:2041` prints (list of ints, `bool()`).
- F3: FIXED. `common.sh:36–46`, `queue:57`. Residual side effect in N8.
- F4: FIXED. `launch8.sh` has no sudo and reads only (`:28`, `:32`); the set is in `session_probe.sh:18–24`, with the limit before and after at `:15` and `:25`. "Once" is not enforced (N9).
- F5: FIXED as asked. `launch8.sh:15`; `queue:17–18`, `37–38`.
- F6: FIXED in text (`decision:10`, `28–29`) and script (`queue:29–36`, `24`). Left: N3, N5, N6.
- F7: FIXED. `decision:34`.
- F8: FIXED. `decision:20`, `:8`.
- F9: FIXED. `common.sh:23`, `24–29`, `10`, `7` and `20`; `launch8.sh:31`, `33`. Left: `common.sh:27` skips the check when `scripts_commit.txt` is missing.
- T1: FIXED on the scripted path; the by-hand path is still open (N3).
- T2: FIXED. The "error file is empty" clause of `decision:26` is not in the script (N7).
- T3: FIXED.
- T4: FIXED, both effects (`session_probe.sh:19` checks for an idle GPU before the set).
- T5: PARTLY. Overwrites and the typo are closed. The attempt number is still only typed, and seed 18's control defaults to attempt 1 (N1, N2).
- T6: PARTLY. The 120 s wait (`launch8.sh:37–42`), the no-checks rule and burst adoption are in. The "last ssh fails after DONE" case is now worse: it prints INVALID (N4).
- T7: FIXED except venv against `uv.lock` (unchanged; it was not on the required list). The `common.sh:2` comment is true of `common.sh` only: `SEEDS`, `ATTEMPT*`, `ADOPT_*`, `STEP_ONLY` and `SET` still come from the environment.

**2. New or remaining traces**

- **N1. Attempt miscount: seed 18's control accepted as attempt 1.**
  - Trace: `SEEDS="18 19" zsh queue_reg19f.sh` with the ATTEMPT variables forgotten. `queue:27` gives a=1, `:38` passes because no `_attempt1.out` exists in this folder, and the run launches (case 1: probe `…_s18_attempt1.txt`, 2 launches). Attempts 2 and 3 can follow, so four launches with the lost one.
  - Likelihood: low on the documented command, realistic on a retyped one.
  - Fix: after `queue:27`, stop if sd is 18, kind is `stage2_control` and a is 1; or commit a marker file for the lost run.
- **N2. Attempt miscount: a pre-launch stop spends the attempt number.**
  - Trace: a 420 W read gives `launch8` exit 2, yet the probe (`launch8.sh:22`) and the `.out` (`queue:40`) are both written. The same command then says "this attempt was already launched" with 0 launches (cases 2a and 2b), so the operator must type ATTEMPT=3 (2c).
  - `decision:10` counts "every launch"; the script counts every call. Two pre-launch stops leave seed 18's control with no number under 4, or push someone to delete evidence files.
  - Likelihood: moderate (four queue stops on 11-12).
  - Fix: create the attempt marker immediately before `launch8.sh:35` and test that marker at `queue:38`; give pre-launch probes a timestamped name. Or state in item 1 that a pre-launch stop spends the number.
- **N3. Futility stop and order can be skipped by hand.**
  - Trace: `queue:19` accepts `SEEDS=19` and `SEEDS="19 18"`. With `SEEDS=19`, both seed-19 runs launch before anything looks at seed 18 (case 3: 2 launches, then the step fails). "19 18" runs seed 19 first (case 4).
  - After a `'continue': False` or a failed step for seed 18, nothing stops a later `SEEDS=19`. The flag is kept in no file, only on stdout. This is round-1 T1's effect again: 2.4 GPU h and n = 5 where the registration says 4.
  - Likelihood: low to moderate; `decision:28` offers `SEEDS=<seed>` forms.
  - Fix: accept only `18`, `19`, `18 19`. Write each step's two fields to `reg19_step_s<sd>_<ts>.txt`. Before launching seed 19 without seed 18 in the same call, require seed 18's record with done 15..18 and `'continue': True`.
- **N4. A valid run is printed as INVALID.**
  - Trace: at `launch8.sh:56`, `grep … | tail -1` returns 0 with no output, so the retry never fires; three ssh failures also fall through with exit 0. `queue:44` then prints `RUN … INVALID` and "QUEUE STOP after an invalid run" (cases 5 and 6).
  - Effect: an operator who believes it reruns a config that already has a valid run. That breaks "Each run once", and `reg12_only` (`gate.py:474`) then raises until someone chooses between two valid runs.
  - Nothing checks before a launch or an adoption that the VM holds no valid run of that config.
  - Likelihood: low (`run.py:79` flushes the line), but the consequence is a forking path.
  - Fix: `launch8` exits 6 unless the line read contains `[run] checks`; `queue:44` gets three branches (True, False, not read). Before any launch, stop if a `runs/*_<cfg>/checks.json` on the VM says valid.
- **N5. `STEP_ONLY=1` runs the step on a pair that was never checksum-verified.**
  - Trace: `queue:24` skips lines 47–54, so there is no checksum, no manifest check and no ssh call (case 9). After a "copy failed" or "checksum mismatch" stop it is one of the two documented recoveries.
  - This breaks registration line 52 ("checksum-verified before `reg19_step`").
  - Fix: remove `STEP_ONLY`, since `ADOPT_*` for both runs does the same with verification; or make it run lines 49–54.
- **N6. The final table has no checks and can be worded as a futility stop after an operational stop.**
  - `decision:29` is typed by hand, with no `mac_checks` or `links_ok` before the one computation that produces the numbers.
  - `gate.py:2060` (`early = len(done) < len(order)`) treats any short matrix as the futility stop. After attempts run out or the VM dies, the table would say "stopped because ≥ 3 was out of reach".
  - Registration line 43 says an operational stop gives no table and the owner decides. The draft does not say when `reg19` may be run.
  - Fix: a `FINAL=1` mode (`mac_checks`, `links_ok`, then `reg19` with stderr to a file), refused unless the last step record is done 15..19 or `'continue': False`; one sentence in item 6.
- **N7. The error-file clause is not implemented.**
  - With step rc 0, `'continue': False` and a non-empty stderr file, the queue prints "QUEUE END futility stop" (case 8; `queue:68–70`). `decision:26` says that is not a futility stop.
  - I could not check whether `reg19_step` normally writes warnings; if it does, enforcing the clause blocks every stop.
  - Fix: decide which holds, then add `[[ ! -s $errf ]]` or drop the clause.
- **N8. `links_ok` writes before it stops.**
  - Trace: at `common.sh:38`, when `$W/runs/<id>` is a real directory, `ln -s` succeeds by putting a link inside it; only then does `:40` stop (links case 3).
  - If `$W/runs` were ever a symlink to the Mac's `runs/`, it writes a link into every REG-19 run folder there before stopping (links case 10: 4 links). Today `$W/runs` is a real directory, so likelihood is low, but that would be a write under `runs/`.
  - Fix: stop unless `$W/runs` is a directory and not a link; call `ln` only when nothing exists at the path.
  - The other 11 cases behave correctly: dangling link, cross-link, foreign entry, relative link, a Mac folder that is itself a link, hidden files, the `_drift` folder.
- **N9. Smaller points, fail-safe or low likelihood.**
  - `launch8.sh:42` says "look before anything else", and exits 3, 4 and 5 leave a log on the VM that holds live rates. The decision lists no allowed reads; this is how the look in `decision:8` happened. Fix: name them (`tmux has-session`, folder names, `checks.json`, the log's `run_id` and `[run] checks` lines).
  - A dead VM is reported as "STILL RUNNING" after the full wait (case 7; `launch8.sh:46–47`, `55`).
  - Empty values pass: `(( TEMP <= 45 ))` reads an empty TEMP as 0 (`launch8.sh:19`, `29`), and an empty boot id equals an empty session file (`launch8.sh:32`; `session_probe.sh:28` writes it unchecked; cases 10 and 19).
  - `session_probe.sh` can be rerun mid-queue and replaces the tripwire file (case 18). It is recorded, but nothing says who may do it after a registered stop.
  - `common.sh:21` passes if `git status` fails with no output.
  - `queue:40` uses zsh `echo`, which rewrites backslash sequences in the saved `.out`.
  - `queue:49`: `a` is never empty, so `-n $a` guards nothing.
  - `queue:73` prints "QUEUE STOP" with exit 0.
  - `launch8.sh` run by hand bypasses the attempt count.
- **Checked and fine.**
  - No `$VAR:x` modifier hazards; `${H}:` is braced.
  - The `[[ ]]` comparisons are literal.
  - `seq`, `sed`, `grep` and `shasum` usage is BSD-safe; `df --output` and `date -Is` run only on the VM.
  - A failed `T=$(ssh …)` exits 255 under `set -e`.
  - `continue` is always False after seed 19 (`gate.py:2041`), so the happy-path case is right.
- **The sandbox test.**
  - Misnamed cases: `test_sandbox.sh:73` ("a step without a flag") passes on the done-list message, not the flag check. `:104` expects an empty string from a stubbed function. `:107` tests `queue:38`, not `launch8.sh:15`.
  - No case for:
    - any of `mac_checks` (stubbed at `:12`), or its calls at `queue:56` and `launch8.sh:11`;
    - `launch8.sh:13–16`, temperature, any ssh failure, "DONE (after tmux ended)", an unread checks line;
    - a copy failure, a manifest failure;
    - adoption of an invalid run (`FAKE_ADOPT_VALID` at `:49` is unused) or of one run only;
    - `STEP_ONLY`;
    - four of the five `links_ok` stops;
    - all of `session_probe.sh` (copied at `:9`, never run).

**3. Registered protocol or operations; statements of fact**

- **Item 1 completes the stopping rule; it is not operations.**
  - It leaves the test, thresholds, order and validity checks alone, and matches the owner's own instance (`delegation.md:3`).
  - The general rule for future lost runs is not literally in the delegation, so mark it as open to the owner's overrule.
  - It does not restate the registered exceptions (registration line 51: heat gets one rerun; `client_error`, `burst_min_kv_max` and a limit other than 350 W stop with no rerun). "At most three attempts", plus a script that accepts ATTEMPT 2 and 3 after any invalid run, reads as overriding them.
  - It does not say what is reported when attempts run out through lost runs: registration line 32 (k of n) or line 43 (no table).
  - "The stricter reading" is true for GPU hours only; it makes an early end for VM reasons more likely.
- **Item 3 restores the registered stop.** The boot-id stop and the 2 GB disk floor (`common.sh:11`, absent from the decision text) are new pre-launch stops that only add stops.
- **Item 4 does not change the registered test.**
  - It is a declared deviation from PROTOCOL §5 (wording verified at `PROTOCOL.md:78–79`).
  - 5ee6e38 and 72fafb5 are the latest commits of those two files (git log).
  - It does not say how "no later version" is enforced, nor that `recheck.py` at 72fafb5 honours the seal (`withheld.py:53`), so it needs the `[RESULT] REG-19` heading in main or `AFTERSHOCK_UNSEAL`.
- **Supported by what I can see:** the commit dates; the differing files; the worktree at the pin and clean; `reg19_inputs` against the registered table (all five rows, probe line 42); the scripts' commit; 29 cases; 11 × 4188 s = 12.8 h; run ids in UTC (`run.py:131`).
- **Not supported or imprecise:**
  - "the ten modules on REG-19's path": `harness/run.py:23–25` also imports `checks`, `env_snapshot`, `trigger` and `recorder`. `checks.py` and `recorder.py` differ from main and are missing from the probe's diff list (lines 26–30). This has no effect from the worktree.
  - "launched at 15:10 UTC, after the third step (FILE(…:31))": line 31 is the commit list and shows neither.
  - "Uncommitted edits … cannot be excluded": understated. 1cface7 was committed 23 min after that launch and changes `analysis/stats.py`, which is on REG-19's path; it was probably in the tree at the third step (my belief). The stated remedy covers it.
  - "The sandbox found one bug": 7f4efb5 corrects two (BSD `seq -s`; a `(:A)` qualifier inside `[[ ]]`).
  - "Before each launch and each step the scripts check … linked": `links_ok` runs before steps only (`queue:57`).
  - "`reg19_step` once per completed pair": not enforced.
  - "its error file is empty": not in the script (N7).
  - "the CLAUDE.md allowance" (item 7): not in CLAUDE.md as given to me; the allowance I can see is `delegation.md:2`, `5`.
  - No tag and no file I was given for: the state paragraph, the 19:52 listing, the 19:53 sudo failure, the 19:58 copy and its checksum, "has read no outcome", the A14 quote.

**4. Verdict: NOT READY**

Required:
1. Refuse attempt 1 for seed 18's control (N1).
2. Make the attempt marker and item 1 agree on what counts as a launch (N2).
3. Restrict `SEEDS`, persist each step's two fields, and gate seed 19 on seed 18's record (N3).
4. Give an unread checks line its own exit and message; stop a launch when the VM already holds a valid run of the config (N4).
5. Remove `STEP_ONLY` or make it verify (N5).
6. Add a checked `FINAL` mode and one sentence: after an operational stop, attempts exhausted included, no table (N6).
7. Item 1: the registered exceptions stand; "stricter" refers to GPU hours.
8. Make the error-file clause and the script agree (N7).
9. Name the reads allowed while diagnosing a stop, in item 6 and in `launch8.sh:42`.
10. `common.sh:38`: no `ln` onto an existing path; `$W/runs` must be a real directory (N8).
11. Correct the eight statements above and tag or save the untagged ones.
12. Add sandbox cases for each change and for `session_probe.sh` (my cases 14–19 can be reused); then update `scripts_commit.txt`, the hash in item 2 and the case count.

Optional:
- Stop when `scripts_commit.txt` is missing.
- Require a numeric TEMP and a non-empty boot id.
- Report "VM not reachable" separately from "STILL RUNNING".
- Refuse a second session probe without an explicit flag and a decision entry.
- Use `print -r --` in place of `echo`.
- Rename the exit-0 "QUEUE STOP".
- Echo `ADOPT_*` and `SET` in the start line.
- Check venv against the lock.
- State the 2 GB floor and the recheck command in the text.

Not checked:
- Anything under `runs/`: the six `checks.json` files and the actual link targets.
- `RESUME.md`, `decisions.md` (the A14 quote) and `status.md`.
- The VM: sudoers, tool output formats, sort order.
- Whether `reg19_step` writes to stderr; I ran no analysis command.
- `.venv` against `uv.lock`.
- Real ssh and rsync behaviour.

Main's HEAD moved from 8b44d26 to 1790dad during this review; `mac_checks` tolerates that by design.
