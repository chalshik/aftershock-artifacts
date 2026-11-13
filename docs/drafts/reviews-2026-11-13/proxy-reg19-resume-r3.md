**Decision: APPROVE**, for the REG-19 resume decision (draft 3) with the six scripts at commit `69f349b`, on conditions D1–D8 below. Draft 3 unchanged is not approved.

All paths are under `/Users/chalshik/Projects/aftershock-artifacts/`. Decision text: `docs/drafts/review_bundles/reg19resume_r3/decision_draft3.md`; scripts: `docs/probe/20261113_reg19/ops_r3/`.

Read: CLAUDE.md; PROTOCOL.md; docs/claims.md (REG-19 lines); the bundle (delegation, registration, draft 3, interim-look entry, the three owner-proxy reviews); the six scripts, the sandbox test and both state files; the four probes; decisions.md entries (A14, the delegation and the four other 2026-11-13 entries, the 2026-11-09 standing instructions, REG-17's result); RESUME.md and the four queue outputs of 2026-11-12; `analysis/gate.py`, `analysis/load.py`, `harness/checks.py`, `harness/run.py` and `harness/loadgen.py` at `a7bb77a`; `analysis/recheck.py` and `analysis/withheld.py` at HEAD; the owner's start prompt `docs/FABLE_PROMPT.md`. I ran `zsh -n` on the scripts (clean) and the sandbox test (116 passed, 0 failed). I did not read the `rulef-*.md` files.

**Reasons:**

1. **Scope: every clause is inside the delegation** (docs/decisions.md:4233–4235).
   - It names "seed-18 control rerun as attempt 2" and "the pin rule".
   - The only root command is `sudo -n nvidia-smi -pl 350`, behind `SET=1` and only on an idle GPU (session_probe.sh:28–33).
   - Nothing edits `runs/`, a used config or an old entry. No threshold is chosen and nothing is deleted. `uv.lock` and `pyproject.toml` are equal at `a7bb77a` and HEAD (`git diff`).
   - Item 4 marks no run invalid; it stops for the owner.
   - Two clauses sit near the edge, and I accept both. Item 4 lifts the seal for one command (reason 3). Item 6 lets the delegate start the queue again after any stop the script allows, and change scripts without loosening a check, with a log entry only (N3); no such stop comes from reading an outcome.

2. **Fidelity: the registered test, thresholds, seeds, order, futility stop and the VM's checks are unchanged.**
   - The worktree is at `a7bb77a`. The registration commit `4a6b33e` is its ancestor, with no difference in `analysis harness configs tools pyproject.toml uv.lock` (`git diff`).
   - Seeds and order are fixed in code (common.sh:16; queue.sh:19–26).
   - The pinned step returns `continue: False` after the last seed whatever k is (`bool(remaining and …)`, analysis/gate.py:2041 at `a7bb77a`). That is what queue.sh:76 and final.sh:13 expect, so the final flag leaks nothing and a `supports` result is not blocked.
   - Each completion in item 1 can only reduce reruns:
     - every launch counts as an attempt, so never more than three runs of a config;
     - `client_error` is read as `no_errors`, which also covers `http_error` (harness/loadgen.py:58, 80 at `a7bb77a`);
     - "heat-invalid" is read as any `gpu_steady` failure.
   - **One reading is looser than the owner's words and is not flagged: heat failures are counted per config** (common.sh:104, 118). See D2.
   - The completions are made before the data they could favour. The six runs on record already passed the checks in force: the A14 recheck covered 182 folders with "no valid run changes verdict" (docs/decisions.md:4205), and the manifest at `5ee6e38` lists 182 folders, six of them REG-19's (`git show`). So the recheck rule can only bite on the four runs not yet made.

3. **Item 4: within authority, consistent with PROTOCOL §5 and CLAUDE.md C, and better than a recheck after the result. I side with the first proxy (B1).**
   - **Authority.** It is a read-only analysis of existing runs. The delegate marks, reruns and counts nothing, which is what the A14 entry reserves: "marking any run otherwise is the owner's" (docs/decisions.md:4205).
   - **PROTOCOL §5** (PROTOCOL.md:78–79, 84) says a run failing a check in force is "never counted". A [RESULT] that counted such a run would itself be a deviation the delegate may not decide.
   - **Better.** A table not computed can be computed later; a table once read cannot be unread. If the owner prefers "as registered", only time is lost. The price falls on four runs, and none of the valid runs on record changed.
   - **Worse in one respect.** Any change, even one that cannot move the label, makes REG-19, REG-20's gate and REG-21's second batch wait for the owner. Draft 2 waited only on a label flip. This is against "it should never depend on me" (docs/decisions.md:4232).
   - **No breach of "no interim look".**
     - The recheck runs only behind final.sh's gate (final.sh:11–17), after the last step, when no launch or rerun decision is left to the delegate.
     - It prints validity fields only (analysis/recheck.py:30–33, 46). The `recorder` and `gpu_steady` details are scrape and sample counts, gaps, clock CV and temperature (`git diff a7bb77a 5ee6e38 -- harness/checks.py`).
     - That is the class of `checks.json`, which the registration lets a rerun decision read and the seal leaves open on purpose (analysis/withheld.py:7–8).
   - **Two things the text gets wrong or leaves out** (D5b, D5c):
     - "Without knowing the outcome" is overstated. The `continue` flags are known and bound k. DERIVED from analysis/gate.py:1703–1710, 2041 at `a7bb77a`: `True` after seed 17 means k ≥ 1 of 3 and neither matrix stop; `True` after seed 18 will mean k ≥ 2 of 4.
     - The owner's start prompt names `analysis.recheck "*"` among the tools not to run while REG-19's runs are withheld (docs/FABLE_PROMPT.md:55). This use reads those folders once, and the entry does not say so.

4. **Item 1: two points the owner could object to.**
   - **The heat count.** The owner's instruction reads "A second heat failure stops the queue until the owner is back" (docs/decisions.md:2105), and the owner stopped G2 after two heat-invalid runs of different rates (docs/decisions.md:1528). The script would allow one heat rerun for each config.
   - **The class of the lost run.** "Not classed as a heat failure" rests on no evidence, though the VM's journal showed the cause of the earlier power-offs (docs/decisions.md:1373–1378; docs/status.md:66). See D3.
   - The rest is the stricter reading throughout. The stricter rule for a further lost run (B6 over P6) is right: a second power-off in two days deserves a fresh look, and a new reviewed decision does not need the owner.

5. **Earlier conditions.**
   - **Met:** B1–B8, P1–P9, N1–N3.
     - P4's fourth point and N2's numbering are overtaken by stricter designs.
     - B3 was run from a second worktree at the pin, which I accept. I compared its output with REG-17's result (docs/decisions.md:3538–3551): the outcome, both verdicts and every span number agree at the reported rounding.
   - **Not fully met: B9.**
     - The clearing reviews are not verbatim in the entry (D1).
     - "Commit the entry before the first launch" is not stated (D4).
     - B9 asked for an empty stderr file; the script takes P7's weaker "no error line" (queue.sh:61). That is acceptable on merits, since exit 0, the exact `done` list and a valid flag are the decisive tests, but the header's "takes the stricter condition" is not true there (D5g).
   - **N1 for the failed sudo** was withdrawn, not recorded (D5e, D6).

6. **Evidence.**
   - **Verified by me:**
     - the cited lines at the pin: harness/checks.py:69, 112, 165, 183; analysis/gate.py:2022, 2060; analysis/load.py:39; harness/run.py:131;
     - docs/decisions.md:4201; PROTOCOL.md:78; analysis/recheck.py:43; the three `continue: True` lines;
     - every State fact against the two probes;
     - the registered schedule table against the worktree probe, all five seeds;
     - 11 × 4188 s = 12.8 h;
     - the commit times of `1cface7` (15:33:58 UTC) and `72fafb5` (19:00:16 UTC), and `69f349b` as the last commit of the six scripts, equal to HEAD;
     - the DERIVED claim that `main` would return an empty `done` list with `continue: True`.
   - **False or unsupported:** the items of D5.
   - **Minor:**
     - "5.6 GB free" is 5 639 776 KiB in the probe, which is 5.4 GiB;
     - "(`git log`)" is not a rule B tag; the worktree probe, lines 31–32, holds the list;
     - the `.venv` statement (94 extra packages, none differing) has no record until the session probe;
     - "has read no outcome" and "was not opened" are the agent's own reports, so BELIEF.

7. **What the owner must be told beyond the text:** see the notes.

**Conditions:**

- **D1. BEFORE the entry is appended: rule F round 3 and the record.**
  - A rule F pass on draft 3 and the scripts at `69f349b` exists and does not return NOT READY.
  - That pass and this verdict are quoted verbatim inside the entry (delegation (a) and (b), docs/decisions.md:4234; B9). The six earlier reviews may stay as the tracked files the entry names.
  - Each quoted line is prefixed `> `, as in earlier [REG] entries, so that no pasted line starts a `## ` heading. A heading holding the seal's lifting text (analysis/withheld.py:26, 43) would open REG-19's runs to every tool.
  - If that pass leads to a script change or to a change of a rule in items 1–8, the change needs a new owner-proxy pass first. Corrections of wording and tags do not.

- **D2. BEFORE the entry is appended: the heat rule.**
  - Item 1 states that "a second heat failure stops the queue" has two readings and that the delegate applies the one that stops more often: the count runs over all REG-19 runs, not per config.
  - The script counts per config, so the rule is applied by hand. The queue stops after every invalid run (queue.sh:41). After a `gpu_steady` failure the delegate starts it again only if that is the first `gpu_steady` failure of any REG-19 run.
  - A second one, in any config, is an operational stop: no table, the owner decides.
  - A script change instead is allowed under D1's last point.

- **D3. BEFORE the first launch: the cause of the power-off.**
  - Read the VM's non-root logs for the boot that ended on 2026-11-12 between 15:25 and 19:47 UTC, as was done for the earlier power-key events, and save the lines as a probe in `docs/probe/20261113_reg19/`. No run folder or harness log is read.
  - If they show a thermal cause, the lost run is the first heat failure (as item 1 already says), no heat rerun is left under D2, and the owner rules.
  - If they show an outside power-key event, item 1's sentence stands on that evidence.
  - If they cannot be read, the [OPS] entry says so and the class stays BELIEF.

- **D4. BEFORE the first launch: the entry is in the log.**
  - The entry, with D1, D2 and D5, is appended and committed.
  - The [OPS] entry gives that commit and shows that the time in `state/attempt_stage2_control_l1pl350cl_r2.0_w3000_s18_2.txt` is later.
  - The `lost_ok` record is void without it (its lines 3–4).

- **D5. BEFORE the entry is appended: corrections of fact** (rule B, research rule 10; the entry cannot be edited later).
  - a. Item 7: `RESUME.md:13` is an empty line. The pin is at lines 12 and 15; the CLAUDE.md allowance is at line 20.
  - b. Item 4: replace "without knowing the outcome" with "without the table; the `continue` flags printed so far are known".
  - c. Item 4: say that the recheck runs from `main`, not from the worktree, which is an exception to item 2's "every REG-19 computation". Say that the owner's start prompt lists `analysis.recheck "*"` among the tools not to run on withheld runs, and why this single use is not an outcome read.
  - d. Item 4: "the number of runs made" becomes "10, or 8 after a futility stop after seed 18: the valid runs on the Mac" (final.sh:30–32).
  - e. Item 3: "Today that command cannot work" is BELIEF. The probe lists only `/etc/sudoers.d`; `/etc/sudoers` was not read and no attempt is on record. The owner's start prompt says passwordless sudo was allowed for this command (docs/FABLE_PROMPT.md:138).
  - f. Item 6: "No file is overwritten, renamed or deleted" is not exact. A renewal renames the session file and keeps it (session_probe.sh:44), and the step record is written through a temporary file (queue.sh:66).
  - g. Header and the table's B9 row: for the step's stderr the draft follows P7, not B9.

- **D6. BEFORE the first launch: the sudo attempt on record.** Unless the limit already reads 350.00 W, the first session probe is run with `SET=1`, so the result of the one allowed root command is in a probe file (N1; the owner's preflight, docs/FABLE_PROMPT.md:138). If it fails, nothing starts and it is logged for the owner.

- **D7. LATER, in the [OPS] entry.** Beside item 7's list:
  - every start of the queue with its reason;
  - each invalid run with its `failed` list;
  - the count of `gpu_steady` failures at each restart (D2);
  - the D3 and D6 probes.

- **D8. LATER, in the [RESULT].**
  - The control-to-burst launch gap per seed, beside `order_flag` and item 8. The registration's run-order alternative assumed "about 70 min" (reg19_registration.md:49), and seed 17's gap was 201 min against 70 min for seeds 15 and 16. DERIVED from the run ids in `mac_checks_json_20261113T002837Z.txt`: 05:09:20 to 06:19:51, 07:35:16 to 08:45:33, 10:34:23 to 13:55:38.
  - The recheck's file, `n_runs`, `n_changed`, and the Mac's HEAD commit when `final.sh` ran.
  - The stderr line count of each step.

**Notes for the owner:**

- **Confirm the delegation entry.** It was found uncommitted and without its heading, and the agent committed it (docs/decisions.md:4241). This is the first "(delegate)" decision and rests on it.
- **Nothing starts until the limit reads 350.00 W.** Your start prompt assumes passwordless sudo works; the only evidence on file suggests no rule is installed. A reboot during the queue needs you again. A sudoers rule for exactly that command would remove both.
- **Item 4 can make REG-19, REG-20's gate and REG-21's second batch wait for you.** To avoid that, write now, before seeds 18–19 exist, what holds for a run that passes its stored checks and fails the checks in force: PROTOCOL §5 as it reads (not counted, rerun unchanged), or counted as registered with the recheck reported. Either ruling is blind today. After seed 18's flag it no longer fully is.
- **A stricter design exists, not required:** recheck each new pair before its step. It needs a script change and a new review.
- **A failed launch command spends an attempt** although no run was made.
- **No new decision is needed for:** starting the queue again after pre-launch stops, renewing the session after a reboot, or script changes that loosen no check. Each is logged.
- **Seed 17's pair differs from the others:** its control's log was read during a diagnosis (logged, docs/decisions.md:4274), and its burst run started 201 min after the control.
- **Withholding is kept by scripts and the log, not by a lock.** Two worktrees at the pin sit outside the repo without the seal (`/Users/chalshik/Projects/aftershock-reg19-pin` and `/Users/chalshik/Projects/aftershock-linktest-pin`), and `AFTERSHOCK_UNSEAL` is an environment variable. `docs/FABLE_PROMPT.md` is untracked, though `analysis/withheld.py` cites it.
- **The limit stays at 350 W after the queue.**

**Not checked by me:**

- Anything under `runs/` or `/Users/chalshik/aftershock-backups`. The six `checks.json`, the holding copy and its checksum are known to me only from the probes.
- The VM: not contacted. Its state is as of the probe of 2026-11-13 00:28 UTC.
- The rule F reviews, by instruction, and the result of rule F round 3.
- `analysis.recheck`, `analysis.gate`, `uv sync`, `tools/check_docs.py` and `uv run pytest`: not run. The scripts were checked by reading, `zsh -n` and the sandbox only, never against the VM.
- The agent's own reports: that it read no outcome, that the lost folder was not opened, the three sandbox bugs, and when the earlier reviews arrived.
- This is not a line-by-line code review; that is rule F's pass.
