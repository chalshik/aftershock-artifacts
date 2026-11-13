**REG-19 resume, rule F review, round 3: NOT READY.** On the scripted path (`session_probe.sh` once, `queue.sh`, then `final.sh`) I found no trace that produces a wrong table. Two fail-open traces remain off that path, nine statements in the decision are false or unsupported, and item 8's session readout is fixed by seed where it should be fixed by boot.

Script references are to `docs/probe/20261113_reg19/ops_r3/`; "the pin" is `a7bb77a` in `/Users/chalshik/Projects/aftershock-reg19-pin`; "the decision" is `docs/drafts/review_bundles/reg19resume_r3/decision_draft3.md`.

**What I ran**
- `zsh -n` on the six scripts and the sandbox test: clean.
- The official sandbox: 116 of 116 pass.
- The conditions of `mac_checks`, by direct git reads: all hold. The last commit of the six scripts is `69f349b`, equal to `scripts_commit.txt:1`.
- 65 stub checks of my own, on the official sandbox's setup but with all ten REG-19 configs at the fake pin, as at the real pin (the official sandbox creates only four, `test_sandbox.sh:20`). Files are in `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/r3_rulef/`: `src/my_cases.sh`, `src/my_cases2.sh`, `src/my_cases3.sh`, with outputs `my_cases.out`, `my_cases2.out`, `my_cases3.out`.
- Main moved from `aa9f09e` to `8f1b2eb` during the review. The six scripts did not change; `analysis/withheld.py` did.
- **My own error:** a `python3 -m py_compile` on `vm_state.py` created `ops_r3/__pycache__/vm_state.cpython-314.pyc` in the repo, against my limits. It was git-ignored and absent from my first listing. I removed that file and the empty folder; the tracked files equal HEAD. The folder's modification time changed.
- I read one file outside the bundle, `docs/probe/20261113_reg19/poweroff_20261112_20261113T005410Z.txt`, which appeared during the review. Its header says no run folder or harness log was read. It bears on item 1.

## 1. Round-2 items R1–R12

| item | status | where |
|---|---|---|
| R1 attempt 1 refused for seed 18's control | FIXED | `common.sh:114` with the committed `state/attempt_stage2_control_l1pl350cl_r2.0_w3000_s18_1.txt`; the real-VM read gives `LAUNCH='2'` (`vm_read_20261113T002837Z.txt:19`) |
| R2 the attempt marker is the launch | FIXED | `launch.sh:41–43`, time-stamped probe at `:20`; item 1 |
| R3 seeds not typed, seed 19 gated | PARTLY | `queue.sh:66–78` and `common.sh:16` do it. `launch.sh:13–17` takes any typed config name and has no gate (T1) |
| R4 unread checks, no launch over a valid run | FIXED | `queue.sh:36–43`; `launch.sh:16–17` with `common.sh:113, 115` |
| R5 no unverified step | FIXED | no step-only mode; `queue.sh:45–56` copies and verifies both runs before every step |
| R6 checked final command, no table after an operational stop | FIXED | `final.sh:9–19`; items 1 and 6 |
| R7 registered exceptions, "stricter" | FIXED | item 1; `common.sh:103–104, 116, 118`. One imprecision (section 3, f) |
| R8 error-file clause | FIXED | `queue.sh:60–65`; item 6 |
| R9 allowed reads named | FIXED | `common.sh:24`; `launch.sh:43, 50, 63, 68, 69`. One sentence too wide (section 3, d) |
| R10 no `ln` onto an existing path | FIXED | `common.sh:56, 60–62` |
| R11 statements corrected | PARTLY | seven of eight corrected; one tag points at an empty line; new untagged statements (section 3) |
| R12 sandbox cases, commit, count | PARTLY | 116 cases, commit and count are right. Five stops have no case, and one case is vacuous at the real pin (section 3, e) |

Round 1's items were tracked as fixed or carried forward in round 2; I found none reopened except through R3.

## 2. Traces

**T1. `launch.sh` by hand skips the futility stop, the order and "each run once". FAILS OPEN.**
- `launch.sh:3` says "safe by hand: it applies the same rule". It applies `decide` only. It never reads a step record, and it accepts any of the 125 configs at the pin.
- Case A1: with no run or record of seed 18, `zsh launch.sh stage2_control_l1pl350cl_r2.0_w3000_s19` launches.
- Case A2b: after seed 18's record says `'continue': False`, the same command launches. `final.sh` then still words the table as a futility stop (A2c).
- Case A3a: if the VM no longer holds seed 15's control, the command launches a second run of it. If it does, the count check stops it (A3b).
- A burst config can also be launched before its control.
- Effect: a run past the futility stop or out of order, about 1.2 GPU h each. n and k are not changed, because only the queue copies.
- Likelihood: low. No step of the decision calls it by hand, but the header and the sandbox's "launch.sh by hand" section present it as supported. This is round 2's N3 again.
- Fix: one function in `common.sh`, called by `launch.sh` and `queue.sh`:
  - accept only the four configs of seeds 18 and 19;
  - refuse when the seed has a step record;
  - for seed 19, require seed 18's record with `'continue': True`;
  - for a burst config, require a valid control.
  - Correct `launch.sh:3`, and add sandbox cases with all ten configs at the fake pin.

**T2. `decide` looks only at the VM, so a config with a verified valid run on the Mac can be launched again. FAILS OPEN.**
- Sequence (cases N1, N2):
  - Seed 18's pair is valid, copied and verified.
  - The queue stops before the step record is written (step crash, manifest, links or a Mac-side check).
  - The VM copies are removed, which CLAUDE.md rule 4's exception allows once a copy is verified.
  - The same command then launches both seed-18 runs again (`common.sh:95–120` never reads the Mac).
- Effect: two valid runs of each seed-18 config and about 2.4 GPU h. The pinned step then raises (`analysis/gate.py:474–475`), so no table is computed, but someone must choose which pair counts.
- The stub's fake step does not raise, so the stub went on to seed 19; the real one would stop.
- This makes item 6's "It launches nothing that is already there" false in this state.
- Likelihood: low. It needs another session or the owner to clean the VM (91 % full) while a stop is open; the decision binds only the delegate ("The agent deletes nothing").
- Fix: in `decide`, stop if `$R/runs` holds a folder of the config that the VM does not list (names only). Or state in the decision and `docs/status.md` that no VM copy of a REG-19 run is removed before the [RESULT].

**T3. Adoption is by count of folders against attempt records, not by run id. FAILS OPEN, only after a launch outside the scripts.**
- Sequence: attempt 2's launch command fails and leaves a record with no folder. A run of that config launched by hand is then taken for it.
- A valid outside run is adopted (case B1b). An invalid one goes unnoticed and attempt 3 runs, four launches in all (B2b).
- The stored validity covers the limit (`power_limit`, expected 350 W ± 1). It does not cover the commit: `clean_git` tests only "not dirty" (`harness/checks.py:147` at the pin). It does not cover the boot session.
- On the scripted path every launch follows the pin check, so I found no adoption of a wrong run there.
- Item 6's "a run folder on the VM without an attempt record" stops is true by count only.
- Fix (optional): `vm_state.py` also prints `git_commit` from `env.json`, and `decide` requires the pin; match the folder to an attempt record's `rid` where one exists.

**T4. The recheck of item 4 runs only before the table, so `reg19_step` counts a run the checks in force would fail. FAILS OPEN against item 4's own rule. Reasoned from `queue.sh:59–66` and `final.sh:28–32`, not stubbed.**
- Sequence: a seed-18 run passes its stored checks but fails the 2026-11-12 coverage checks. The step counts it and prints `'continue': True`. Seed 19 runs. `final.sh` then stops for the owner.
- If the owner rules the run invalid, the rerun comes after seed 19, and a flipped flag means seed 19 should not have run.
- Likelihood: very low. The 2026-11-12 recheck of 182 folders changed no valid run (`docs/decisions.md:4205`). Those 182 include seeds 15–17's six (DERIVED: 176 non-REG-19 links in `linkpath_test_20261113T002923Z.txt:2` plus 6).
- Fix (optional): run the same recheck in `queue.sh` before each step, expecting 6 + 2 per seed done. At the least, cite `decisions.md:4205` for seeds 15–17.

**T5. Nothing ties a launch to the decision being in `decisions.md`. FAILS OPEN on process only.**
- `state/lost_ok_20261112-151030_…s18.txt` was committed in `69f349b`, before the decision exists. Its text says it is void without the decision, and no script checks that (case O2).
- Today only the 420 W limit and the missing session probe stand in the way.
- Fix (optional): `queue.sh` and `launch.sh` require the decision's heading in `docs/decisions.md`.

**Unnecessary stops (FAIL SAFE; the same command resolves them unless noted)**
- `WAIT_MIN` that is not a number gives "STILL RUNNING" straight after the launch (case F5).
- A run invalid on `no_errors` through `http_error` stops for the owner, although REG-19 registers a rerun for it (section 3, f).
- Two failed launch commands spend two attempts with no run made.
- A stderr warning containing "Error" blocks the step, which is then run a second time.
- An extra REG-19 folder with a `config.yaml` in the Mac's `runs/` makes the recheck count wrong for good; the owner must act.
- Two queue instances at once can append the same lines to `manifests/runs.sha256`; every later manifest update then fails. A lock would prevent it.

**Checked and fine**
- `decide`:
  - a run in progress stops as "lost or still running" and is used once it finishes valid (F3, K1);
  - a folder without a config stops (C3);
  - the three no-rerun checks, the second heat failure and the three-attempt limit hold (L3, L4, official cases).
- The wait loop: has-session unreadable, tmux gone with late `checks.json`, VM unreachable (F1–F4).
- Stops with no official case behave: hot GPU after the wait, failed temperature read, failed pre-launch read, failed manifest update (I1–I3, D1). None spends an attempt.
- `final.sh`: the expected count (10, or 8 after a futility stop) is right in every state the scripts can reach, because only valid pairs are copied. An unseal that did not work would give 0 runs and stop.
- The session probe: `RENEW=1` at 420 W or with a dirty tree is refused and the old file stays (E1, E2).
- Everything sent over ssh is quoted correctly. I found no `$VAR:x` hazard, and unquoted right sides in `[[ ]]` are literal in zsh.
- Writes: under `$R/runs` only the rsync copy (`queue.sh:46`). The manifest is `manifests/runs.sha256`, outside `runs/`. `links_ok` writes symlinks into the worktree's `runs/` (`common.sh:60`), by design.

## 3. Statements of fact

**False or unsupported (required corrections)**
- a. Item 1 "Why the VM went off is in no record the agent found" and the last line "The cause of the power-off is unknown". The new probe shows `systemd-logind: Power key pressed short` at 2026-11-12 15:51:32 UTC, a clean power-off, and no thermal or Xid line in that boot. The heat question can be closed from it.
- b. Item 7 `FILE(docs/probe/20261111_reg19/ops/RESUME.md:13)`: line 13 is empty. The pin is at lines 12 and 15; the CLAUDE.md allowance is at line 20.
- c. Item 6 "No file is overwritten, renamed or deleted. File names carry the time and the process id."
  - `session_probe.sh:44` renames the session file.
  - `queue.sh:66` writes a `.tmp` and renames it.
  - The attempt, step and session files carry neither time nor process id.
- d. Item 6 "Every stop message of `launch.sh` prints this list": only the five stops after the launch command do.
- e. Item 6 "every pre-launch stop", and the R12 row.
  - No case exists for a GPU above 45 °C after the wait, a failed temperature read, a failed pre-launch read, a failed manifest update, or "DONE (after tmux ended)".
  - "launch.sh refuses an unknown config" (`test_sandbox.sh:292`) passes only because the sandbox pin lacks seed 15's config.
- f. Item 1 reads the registration's "`client_error`" as the check `no_errors`.
  - `client_error` is a request status (`harness/loadgen.py:80, 112` at the pin).
  - `no_errors` also fails on `http_error` (`:58`), for which REG-19 registers a rerun.
  - So the stop message "REG-19 registers no rerun after no_errors" (`common.sh:116`) is wrong in that case.
- g. Item 4 "validity, no outcome". For a changed run the saved `recorder` detail holds `end_ref_t`, the time the load ended (`harness/checks.py:101–109` on main). A load that ends at the drain deadline points to a backlog at the end, so it hints at the outcome. The owner should rule from `valid` and `failed` only.
- h. Item 3 "94 packages beyond the lock; none of the locked ones differs" has no probe. "Today that command cannot work" rests on `/etc/sudoers.d` alone.
- i. Item 6 "It launches nothing that is already there" (T2), and "a run folder on the VM without an attempt record" (T3, by count).

**Verified**
- The git history: `1cface7` at 15:33:58 UTC is the first code commit after the pin; `72fafb5` is at 19:00:16 UTC; `stats.py` gained 9 lines; `load.py` and `tables.py` differ from the pin.
- All line references into the pinned `checks.py`, `run.py`, `gate.py` and `load.py`.
- `PROTOCOL.md:78` and the quote at `decisions.md:4201`.
- The three `continue: True` lines; the VM state, the lost folder's checksum and the six validity flags against their probes.
- The schedule table against `worktree_test_20261112T200109Z.txt`; "15 modules"; 116 cases; 11 × 4188 s = 12.8 h.
- `withheld.py:26` is now line 27, because main moved.

## 4. Strongest alternative explanation

- **A boot-session shift aliased with seeds 18–19.** Seeds 15–17 ran in one boot (2026-11-12 05:05:54 to 15:52:08 UTC, from the power-off probe); seeds 18–19 run in a later one. These two seeds also plan a higher baseline rate (2.22 and 2.21 against 1.96–1.97).
- A slower machine after the reboot would make a burst run stick, or a control fail, for that reason alone. Two seeds can move the label across the threshold of 3.
- **What separates it:** per-run levels by boot and `env.json` across boots, as item 8 lists. Only a repeat of one of seeds 15–17's controls in the new boot identifies it; item 8 says so.
- **Item 8 is adequate for exactly two sessions, and not otherwise.**
  - Its readout is fixed as "seeds 15–17 and seeds 18–19".
  - The scripts allow a third session with only an [OPS] entry (`RENEW=1`), including a pair split across boots: control before a reboot, burst after.
  - In a split pair the burst-minus-control difference holds the session shift instead of cancelling it.
  - Choosing the grouping after the outcomes are seen is a forking path.
- **A further power-off is likely enough to plan for.** All three recorded boots ended between 15:06 and 17:37 UTC (2026-11-07 15:06:05, 2026-11-11 17:36:47, 2026-11-12 15:52:08), the last by the power key. A queue of about 4.9 h that spans that time will probably lose a run. That it is a regular evening shut-down is BELIEF from three boots.

## 5. Does the decision change a registered rule?

- **Test, thresholds, seeds, order, matrix rule, futility stop:** not changed.
- **Item 1** completes the stopping rule for a case it does not define, and the owner's delegation names this rerun. Three points:
  - a failed launch command counts as an attempt, which is stricter than "an invalid run is rerun at most twice" and only adds stops;
  - the `client_error` reading widens a registered stop to `http_error` (section 3, f);
  - future lost runs need their own decision, enforced only by a file anyone can write.
- **Item 4** does not change which runs count. It adds a condition before the registered final computation ("Result, computed once after the queue ends").
  - When it fires, the registered result is withheld. An owner ruling of "invalid" would then change n or the order.
  - That is a deviation to name in the [RESULT].
  - It is blind except for section 3, g, and late with respect to the step (T4).
  - The deviation from PROTOCOL §5 is declared and rests on `decisions.md:4201`.
- **Item 3** restores the registered 350 W stop. Resuming after a reboot is not covered by the registration either way.

## 6. Verdict: NOT READY

**Required**
1. T1: gate `launch.sh` or make it refuse outside the queue's four configs and order; correct `launch.sh:3`; add sandbox cases at a pin holding all ten configs.
2. T2: the guard in `decide`, or the stated rule that no REG-19 VM copy is removed before the [RESULT]; correct "launches nothing that is already there".
3. Section 3, a–i: correct each statement. For e, add the five cases (mine can be reused) or reword. For f, correct the text and the stop message.
4. Item 8: fix the grouping by boot id now. A pair split across boots is reported as its own row, with the boot id of every run taken from its pre-launch probe.

None of these needs a GPU run or a VM action. Round 4 can be limited to the diff of `launch.sh` and `common.sh`, the new sandbox cases and the changed text.

**Optional**
- Run the recheck before each step (T4).
- Check the commit and run id on adoption (T3).
- Require the decision heading before a launch (T5).
- Put the two committed state records under `mac_checks`.
- Pin the recheck's other inputs: `harness/config.py`, `harness/workload.py`, `configs/defaults.yaml`, `analysis/withheld.py`, `analysis/load.py`.
- Add a lock against two queue instances.
- Start the queue only when about 5 h fit before 15:00 UTC.
- Validate `WAIT_MIN`.
- Read the earlier boot's kernel and driver lines from the journal before the queue.
- Note for the owner: the link-test worktree holds unguarded links to every other run folder, including any that other registrations seal.

## 7. Not checked

- Anything under any `runs/`: the six `checks.json` files, the link targets, and that the Mac holds exactly six REG-19 folders (DERIVED only).
- The VM: tool output formats beyond the probes, whether it still holds seeds 15–17, `/etc/sudoers`.
- The real `analysis.recheck` with the unseal variable, the real `reg19_step` stderr, and the real `uv sync --dry-run` output format. All were stubbed or read as code.
- Real ssh, rsync and tmux timing, including whether the run id appears within 120 s after a reboot.
- `RESUME.md:18–19`, not read to avoid an outcome, so the interim-look entry's two tags are unverified.
- `proxy-reg19-resume-r3.md`, which appeared during the review; not read, to stay independent.
- Whether the three earlier flags came from pin-equal code; the decision says this is not shown.
