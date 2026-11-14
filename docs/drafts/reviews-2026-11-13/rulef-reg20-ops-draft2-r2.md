# rulef-reg20-ops-draft2-r2 (rule F, round 2 on REG-20 arm A's operations decision, draft 2, bundle reg20_ops_r2), verbatim

Saved by the agent at 2026-11-14 02:01 UTC from the reviewer's own file (an in-process subagent of session 8c5f8396; scratchpad `reviews_r3/rulef-reg20-ops-draft2-r2.md`, 57371 bytes, sha256 41dc8390505829c9f072d3cde362f77131411c473af02949266db73871fc2785, checked on copy; the reviewer's hand-back named the same sha256). Its patches `rc2_rc3_common.patch`, `rc2_rc3_test_sandbox.patch` and its `probes.txt` and `pytest_control_due.txt` are copied byte for byte to `docs/drafts/reviews-2026-11-13/rulef-reg20-ops-r2_files/`. The reviewer's report follows the line '---' unchanged.

---
# Rule F, round 2: REG-20 arm A operations, decision draft 2 (bundle `reg20_ops_r2`)

**Verdict: NOT READY.** Required: RC1–RC8. Optional: RC-O1–RC-O12.

**Reviewer.** A separate subagent, 2026-11-14, finished at about 02:00 UTC. 0 GPU h. The VM was not contacted and no ssh was run.

**Repository: read-only.**
- I committed nothing and edited no repository file.
- `git status --short` was compared before and after the tests. The only change during the review was two untracked files written by other agents: `docs/drafts/reviews-2026-11-13/proxy-e1-draft7.md` and `docs/drafts/reviews-2026-11-13/proxy-reg20-ops-draft2.md`. I did not open either one, because this pass must not be anchored on the parallel owner-proxy review.
- HEAD moved from 56820bd to 88593dc during the review. The commits were f43a5a1, 47b8e06 and 660a675 ([OPS] entries, STATE, a copy of seed 18's lost control), then 88593dc (E1 draft 8, and three saved reviews, the owner-proxy's on this draft among them).
  - None of them touches `analysis/`, `harness/`, `configs/`, `tools/`, the lock files, `.python-version`, `docs/probe/20261113_reg20/` or `docs/probe/reg20/`. PROBE: `git diff --stat 56820bd 88593dc -- <those paths>` is empty.
  - The two owner-proxy files I did not open are now committed in 88593dc, and I still did not open them.
  - 88593dc also adds `docs/drafts/reviews-2026-11-13/rulef-e1-r3_files/DEO1_withheld.patch`. By its name it is a second proposed change to `analysis/withheld.py`, after REG-24's (RC1). I did not open it.
  - `agent/STATE.md` now shows as modified in the working tree, by another session. That file is not on RC1's list.

**Not opened:**
- `/Users/chalshik/aftershock-backups/`;
- `docs/probe/20261111_reg19/ops/RESUME.md`;
- `docs/paper/`;
- the contents of any `state/` folder;
- any folder matching REG-20's seal, and E1's or E0's sweeps. No REG-20 folder exists: PROBE `ls runs | grep -cE '_l1pl350ol_|_s15_drift$'` gives 0.

**Not run:** `k1.reg20_table`, `k1.reg20_a_may_start`, `e1.observed`, `k2.observed`, any `k3.reg21_*`.

**Read, in order:**
1. CLAUDE.md;
2. the bundle's BUNDLE_NOTE and MANIFEST;
3. the bundle's `reg20_ops_decision_draft2.md` and `reg20_ops_draft2_itemmap.md`;
4. both round-1 reviews;
5. `ops/`: README, owner_rulings.txt, common.sh, queue.sh, launch.sh, final.sh and recheck_one.py in full; test_sandbox.sh's set-up, helpers and the cases cited below; test_control_due.py's test names and fixtures;
6. the repository's unchanged `control_due.py`, `vm_state.py` and `session_probe.sh`;
7. `withdrawn/gate.sh`, and the file list of `diff_c8b482d_ops.patch`;
8. `docs/decisions.md`: 4045–4172 (REG-20's [REG] and its approval), 4231–4238 (the delegation), 530–535 (VM copies), 9830–9838 (REG-21's stopping rule), 16586–16600, 17012, and the headings from 4000 onward;
9. `analysis/k1.py:140–301`, `analysis/withheld.py`, `analysis/recheck.py`; `harness/checks.py` (grep at the pin and at HEAD); `harness/run.py` (Popen lines); `harness/config.py:1–26`;
10. `tools/manifest.py` and `tools/check_docs.py` (greps); `.claude/settings.json`;
11. `agent/RUNBOOK.md:44–70`; `agent/STATE.md` (grep); `docs/status.md:1–12`;
12. `docs/drafts/reg24_confirm_draft1.md:410–430` and REG-24's patch file list; E1's draft 7 (grep) and its bundle's `ops/common.sh:8–16, 98–112` and `ops/vm_checkout.sh:1–24`. `docs/drafts/e1_draft8.md` now exists; I did not read it, so every E1 citation below is to draft 7 or bundle `e1_r3`.

**Checks and tests (PROBE files in `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/`):**
- **The bundle.** MANIFEST: 21 of 21 OK (`shasum -a 256 -c`). The 13 ops files in the bundle are byte-equal to `docs/probe/20261113_reg20/ops/` in the repository (`cmp`), so the draft's line numbers are the repository's.
- **`test_control_due.py`:** 46 passed, on the repository with bytecode and pytest's cache off (PROBE(`reviews_r3/pytest_control_due.txt`)).
- **`test_sandbox.sh`, unchanged, on a scratch copy:** passed 350, failed 0, exit 0, which matches the draft's count of 350 of 350 (PROBE(`sbx/sandbox_run.txt`)).
- **`test_sandbox.sh` with this review's RC2 and RC3 patches** (and the sandbox changes they need): passed 359, failed 0, exit 0. That is the 350 existing cases, with the two RA3 not_run blocks moved to a both-setup case, plus 9 new RC cases (PROBE(`sbx3/sandbox_patched_run.txt`)).
  - The two patch files, `reviews_r3/rc2_rc3_common.patch` and `reviews_r3/rc2_rc3_test_sandbox.patch`, apply cleanly to HEAD's files in a scratch tree. The result is byte-equal to the tested `sbx3/ops/common.sh` and `sbx3/ops/test_sandbox.sh` (`cmp`). The patches were not applied to the repository.
  - An earlier patch, `sbx2`, put the new rulings check first. That run was stopped, and it is not proposed (RC2).
- **Other files in `reviews_r3/`** (`proxy-*.md`, `rulef-e1-*`, `rulef-reg24-*` and others) belong to other passes. This review opened none of them.
- **The probe commands behind each PROBE below:** `reviews_r3/probes.txt`.

---

## Verdict, in brief

The draft fixes round 1's seven required items as worded, and its scripts behave as the draft says on every path I traced. Four gaps remain that let a label or a ruling move after control bits are visible, or that rest on a premise that is no longer true.

**1. The stale freeze (RC1).**
- The freeze that the draft relies on has ended. Both batch 2s are computed (FILE(docs/decisions.md:16571), FILE(docs/decisions.md:16798)), and REG-21's entry says its freeze ends (FILE(docs/decisions.md:17012)).
- A commit to a seal file is now planned: REG-24's draft needs a seal row in `analysis/withheld.py` "before either run exists" (FILE(docs/drafts/reg24_confirm_draft1.md:418-421)). Such a commit stops arm A between a burst run and its control.
- Nothing written keeps E1 off the GPU in the gap that follows (Trace 1).

**2. The rulings file can change without the owner (RC2).** `owner_rulings.txt` can be changed by a commit that holds no owner's entry, and every script accepts it. The sandbox's own helper changes rulings this way (Trace 2).

**3. Ruling 7 drops a T3 seed (RC3).** Under ruling 7 `not_run`, the delegate may drop a seed whose first attempt failed `client_lag`, one of T3's stuck-run failures. The sandbox asserts this behaviour (Trace 2).

**4. `setaside` removes the registered label (RC5).** Under 2a `setaside`, the registered label `lost_open` cannot be reached for any seed that has a set-aside attempt, not only after two set-asides (Trace 3).

**Also required:**
- RC4: point 15 and duty (iii) promise that no discretionary ruling is made after the control bits, which the design does not deliver.
- RC6: held and set-aside folders are raw data with no permanent home, manifest or backup.
- RC7: the order with E1, the VM checkout and RUNBOOK's "deploy HEAD" are left to hand.
- RC8: the status lines are stale again (the scripts are committed in 56820bd).

RC2 and RC3 come with tested patches. The rest are text and duties.

---

## 1. Traces on which arm A's operations or verdict go wrong

### Trace 1 (operations; the likeliest): a seal row stops arm A between seed n's burst run and its control, and nothing keeps the GPU for the control

1. **A seal commit lands mid-run.**
   - Seed 16's open burst run is launched. `launch.sh` waits for its `checks.json` (FILE(docs/probe/20261113_reg20/ops/launch.sh:82-94)); one run lasts 4080 s (FILE(docs/decisions.md:4097)).
   - During that wait, REG-24's seal row is committed to `analysis/withheld.py`, as its draft requires "before either run exists" (FILE(docs/drafts/reg24_confirm_draft1.md:418-421)). D1 is also being drafted (FILE(agent/STATE.md:36); commit 660a675).
   - A review quoted in E1's draft 7 expects such rows too: "Seal rows added after the registered commit, for REG-20 arm A's operations or D1/D2" (FILE(docs/drafts/e1_draft7.md:555)).
   - Draft 2 bars such commits only through REG-21's and REG-22's freeze (point 12; "The freeze"; README:130). That freeze ended with both batch 2s (FILE(docs/decisions.md:17012)).
2. **The queue stops before the copy.**
   - `launch.sh` returns. The next turn's `mac_checks` fails with "analysis/withheld.py is not the blob" (FILE(docs/probe/20261113_reg20/ops/common.sh:81-83), FILE(docs/probe/20261113_reg20/ops/queue.sh:58)). The sandbox shows this stop for a committed change (FILE(docs/probe/20261113_reg20/ops/test_sandbox.sh:704-705)).
   - The QUEUE STOP comes before the copy, the recheck and the control decision.
3. **Both ways back are poor.**
   - One way is a reviewed commit to `common.sh`'s `SEAL_BLOBS`. That needs a new scripts commit and a new `scripts_commit.txt` (FILE(docs/probe/20261113_reg20/ops/common.sh:89-92)), written while seed 15's CONTROL line is visible (point 15).
   - The other is a revert of the other registration's seal.
4. **Nothing keeps the GPU for arm A in the gap.**
   - E1's `ready_to_run` tests only REG-19's queue lock (FILE(docs/drafts/review_bundles/e1_r3/ops/common.sh:100-107)).
   - E1's `vm_checkout.sh` refuses only on E1's own lock, a live tmux session or a compute process (FILE(docs/drafts/review_bundles/e1_r3/ops/vm_checkout.sh:19-24)).
   - E1 is the next GPU work in the lead's state file (FILE(agent/STATE.md:52)). E1 can therefore check the VM out at its own commit and run its sweep. Arm A's next launch then stops on the tree (FILE(docs/probe/20261113_reg20/ops/launch.sh:50)) until a checkout by hand.
5. **The control runs late.**
   - Seed 16's control, if due, runs hours or days after its burst run, possibly after a reboot. The registration says "right after it" (FILE(docs/decisions.md:4054)).
   - That control is what separates `stuck_open` from `overload_open`. Machine drift between the two runs is checked for one closed seed only (alternative 5, FILE(docs/decisions.md:4093)).
   - `gap_s` and the boot line record this (FILE(docs/probe/20261113_reg20/ops/common.sh:398-408)) but do not prevent it.

**Cost.** No label is written wrongly by the scripts. The registered timing is lost, the GPU sits idle or runs E1 out of order, and a scripts change is made mid-arm with outcome bits visible. **Fix:** RC1 and RC7, with RC-O1 and RC-O2 as code options.

### Trace 2 (verdict): a seed T3 calls cold is dropped, and a ruling can move after the bits are visible

1. **The owner rules.** The owner's entry commits `owner_rulings.txt` with `7 per_stop`.
2. **Two seeds are stuck.** Seeds 15 and 16 end `stuck_open`; their `CONTROL_DUE yes` lines are in the queue output (point 15).
3. **Seed 17 fails twice.** Its attempt 1 fails `client_lag`, and its attempt 2 fails `trigger` only.
   - `setup_case` is set, because *either* attempt was setup-only (FILE(docs/probe/20261113_reg20/ops/common.sh:304)).
   - The queue stops for a settle record (FILE(docs/probe/20261113_reg20/ops/common.sh:341)).
4. **The ruling is changed (RC2).**
   - A commit changes only the line `7 per_stop` to `7 not_run`.
   - `rulings_ok` accepts it: the file is tracked, equals HEAD and holds an allowed answer (FILE(docs/probe/20261113_reg20/ops/common.sh:100-120)).
   - `gate_in_log` only orders headings, and the old rulings heading still precedes the start heading (FILE(docs/probe/20261113_reg20/ops/common.sh:133-138)).
   - The sandbox's own helper changes rulings in exactly this way, a commit of `owner_rulings.txt` alone (FILE(docs/probe/20261113_reg20/ops/test_sandbox.sh:235)). Every case built on it passes (PROBE(`sbx/sandbox_run.txt`), for example "2a setaside: a stored-valid run that today's checks fail is set aside", FILE(docs/probe/20261113_reg20/ops/test_sandbox.sh:388-396)).
5. **The delegate drops the seed (RC3).**
   - The delegate writes `settle` with `label not_run`. Under 7 `not_run`, `decide` accepts it in the mixed case (FILE(docs/probe/20261113_reg20/ops/common.sh:314)). The sandbox asserts exactly this with `outs client_lag trigger` (FILE(docs/probe/20261113_reg20/ops/test_sandbox.sh:485-493)).
   - The second run is held out of `runs/`, so k1 reads `not_run` (FILE(analysis/k1.py:286)).
6. **k1's outcome moves from `refutes` to `inconclusive`.** DERIVED:
   - Seed 17 leaves n. That leaves k_stuck = 2 < 3 (FILE(analysis/k1.py:224), FILE(analysis/k1.py:233)).
   - With seeds 18 and 19 recovered: b = 2 and c = 0, so McNemar p = 1/4. The outcome is `inconclusive`.
   - Counted as REG-20 labels it, `lost_open` (a "burst run invalid after its rerun", FILE(docs/decisions.md:4067)), k_stuck = 3 and the outcome is `refutes`.
   - The decisions differ: "K1 … leaves the paper's core claims" (FILE(docs/decisions.md:4076)) against "owner chooses between paired seeds 20+ and dropping K1" (FILE(docs/decisions.md:4079)).

**Each half suffices on its own.**
- Step 5 alone drops the seed even when 7 `not_run` was ruled honestly before the launch. That is RC3.
- Step 4 alone lets any of the six rulings change after the bits are visible. That is RC2.
- The direction is T3's: away from `refutes` (FILE(docs/decisions.md:4103)).

### Trace 3 (verdict): under 2a `setaside`, a seed invalid twice by the checks in force can only leave n

1. **Attempt 1 is set aside.**
   - The ruling is 2a `setaside`. Seed 17's attempt 1 is stored valid at the pin.
   - Its recorder died under the open-loop backlog (A14 at the pin: FILE(docs/decisions.md:4202); "an open-loop backlog writes the most lines", draft point 1). Today's checks fail it on `recorder`.
   - It is set aside (FILE(docs/probe/20261113_reg20/ops/common.sh:530-534)).
2. **Attempt 2 is invalid, and the queue stops.**
   - Attempt 2 is stored invalid (`client_lag`).
   - `decide` finds one invalid run and one set-aside run, with the attempts spent. `LOST` needs two invalid runs (FILE(docs/probe/20261113_reg20/ops/common.sh:340)), so the queue stops: "operational stop, the owner decides" (FILE(docs/probe/20261113_reg20/ops/common.sh:347)).
3. **Only `not_run` can follow.**
   - A settle record with `lost_open` is refused, because it needs two invalid runs (FILE(docs/probe/20261113_reg20/ops/common.sh:320)). The set-aside folder never enters `runs/`.
   - The answers left are `not_run` or the owner's third attempt.
   - k1 sees at most one invalid folder and reads `not_run` (FILE(analysis/k1.py:286)).
4. **The registration's label is lost.**
   - By the checks this decision calls in force, both attempts are invalid, which REG-20 labels `lost_open`, cold.
   - The outcome moves as in Trace 2.
   - The draft names only the two-set-aside case, and says "the owner settles it" (draft line 324) without saying that `not_run` is the only label the owner can then reach. **Fix:** RC5.

---

## 2. Strongest alternative explanation of arm A's likely outcome

**What is likely.**
- The registration's beliefs, given that arm A runs (BELIEF, FILE(docs/decisions.md:4085)): `inconclusive` ≈ 0.49, `supports` ≈ 0.40, `supports_no_mechanism` ≈ 0.10, `refutes` ≈ 0.01.
- The gate fixed k_c = 5 (the brief's quoted gate line; FILE(docs/drafts/review_bundles/reg20_ops_r2/reg20_ops_decision_draft2.md:269) for its shape).
- So `supports` needs all five open seeds `recovered_open`. DERIVED: (4,0) gives 1/16 > 0.05.

**If the outcome is `inconclusive` (the likeliest single outcome):** the 5-of-5 requirement and the operations, not K1.
- DERIVED: at the registration's per-run rates, P(not all five recovered) = 1 − 0.87⁵ = 0.50.
- On top of that, the pin's recorder death adds about 3–6 % per arm (round 1's RA2: 1 − (181/182)⁶ = 0.032 to 1 − (181/182)¹¹ = 0.059).
- Every route out of `supports` is the same McNemar arithmetic: one `partial_open`, one `unclear` (a NaN readout), one `lost_open`, `not_run` or `pending_control`.
- **An `inconclusive` therefore says almost nothing about K1.** What separates "K1 false at this cell" from "one seed was lost to operations" is the per-seed label list together with the queue's `recheck_changed`, `lost`, `held`, `gap_s` and boot lines, and the hand-written records (RC4, RC5, RC6 make these complete).

**If the outcome is `supports`:** headroom, not held prefixes.
- λ = 2.0 is 0.67 of the open-loop warm capacity and 0.83 of the closed-loop one (FILE(docs/decisions.md:4047)). A server with more spare capacity drains a burst's backlog whatever happens to its prefixes.
- The mechanism clause separates the two only weakly: an overlap share above 0.5 is close to guaranteed when e2e is near the mean 5 s gap (FILE(docs/decisions.md:4116)).
- The sessions-in-service readout separates the working-set alternative only partly (FILE(docs/decisions.md:4089)).
- Arm B, the registered test of headroom, runs only after `supports`, on three seeds (P = 0.22 that all three recover at a true cold rate of 0.4, FILE(docs/decisions.md:4081)).
- What would separate them: arm B's `headroom_open` against `headroom_weakened`, and arm A's held-against-idle reuse contrast.

**If the outcome is `refutes`:** an operations artifact in T3's opposite direction.
- Two setup or client-side failures per seed can produce it with no stuck state (round 1's RA3). Draft 2's stop and ruling 7 now cover that.
- What separates it: the failed-check class of each `lost_open` seed, which `queue_done.txt` and the RUN lines record.

---

## 3. Can arm A change a decision?

**Yes.** The three outcomes lead to different decisions:
- `supports` states K1 for this cell and starts arm B (≈ 3.2–3.7 GPU h);
- `refutes` moves K1 out of the paper's core claims;
- `inconclusive` sends the choice to the owner: paired seeds 20+, or dropping K1 as a core claim (FILE(docs/decisions.md:4076-4079)).

**The operations reach the outcome at the margin:**
- Traces 2 and 3 move `refutes` to `inconclusive`;
- Trace 1 moves when a control runs;
- ruling 9(b) can turn any outcome into `pending_controls` (RC-O4).

**After the first non-recovered seed, the rest of arm A still matters.** The remaining runs, about 3.5–6 GPU h, can move the outcome only between `refutes` and `inconclusive` (round 1's RA-O8). That still changes a decision.

**GPU hours.**
- Planned: 6.4–7.4 h, plus about 1.1 h per control (FILE(docs/decisions.md:4097)).
- Ceiling under the caps: 22 launches ≈ 23.5–27.1 h (DERIVED: 22 × 1.07–1.23). Up to 2 uncounted losses per config under 8(b) add to it.

---

## 4. Required items

### RC1. The freeze has ended. The stop it mitigated is open again, and the stale text must be replaced by an arm A hold
**Class:** a stricter rule, wording, and a reporting duty.

**What is wrong.**
- **The text is out of date.** Point 12 (draft lines 237–240), point 16's "The freeze (RB9)" (line 304), "The freeze" (lines 366–378), Proposal 4 (line 427), README:130, item-map row RA-O1 and M10 all say that REG-21's and REG-22's freeze bars commits to the seal files until both batch 2s. Both are computed (FILE(docs/decisions.md:16571), FILE(docs/decisions.md:16798)), and FILE(docs/decisions.md:17012) says REG-21's freeze ends. REG-22's freeze has the same end: changes wait "until both REG-21's and REG-22's batch 2 are computed or declared not computed" (FILE(docs/decisions.md:4748)). Draft 2 cites only REG-21's freeze (FILE(docs/decisions.md:9834)) for both.
- **Planned commits.** REG-24 needs a seal row (FILE(docs/drafts/reg24_confirm_draft1.md:418-421)), D1 is being drafted (FILE(agent/STATE.md:36)), and a review quoted in E1's draft 7 expects seal rows "for REG-20 arm A's operations or D1/D2" (FILE(docs/drafts/e1_draft7.md:555)).
- **The stops are wider than the seal files.**
  - `mac_checks` stops on the seal blobs, on k1's closure against the pin, and on `tools/manifest.py`, `pyproject.toml` and `uv.lock` (FILE(docs/probe/20261113_reg20/ops/common.sh:72-92)).
  - `recheck_guards` stops on any uncommitted edit of a tracked file under `analysis/` or `harness/`, or of `configs/defaults.yaml` (FILE(docs/probe/20261113_reg20/ops/common.sh:495)). That is the stop REG-19 hit on 2026-11-13 (FILE(docs/decisions.md:4604)).
- **Silent changes are also possible.** `harness/__init__.py`, `harness/config.py` and `harness/workload.py` are in the recheck's import closure, which is 8 files: `analysis/{__init__,load,recheck,withheld}.py` and `harness/{__init__,checks,config,workload}.py` (PROBE: `closure.py analysis/recheck.py`, `reviews_r3/probes.txt`). `mac_checks` does not compare these three harness files, or `configs/defaults.yaml`, with the pin, and `recheck_guards` compares them only with HEAD. A commit to them moves HEAD without any stop, so the rechecks at copy time and the one in `final.sh` could run different code. `final.sh` would then refuse the table if their changed sets differ (FILE(docs/probe/20261113_reg20/ops/final.sh:70)).

**Replacement text.**

(a) **Point 12**, replace the bullet list under "**The seal blobs (RA-O1).**" (draft lines 237–240) with:
> **The seal blobs and the judged code (RA-O1).** A change to any file of the arm A hold (below) stops the queue at its next turn (queue.sh:58), possibly between a burst run and its control. REG-21's and REG-22's freeze no longer prevents such a change: both batch 2s are computed (FILE(docs/decisions.md:16571), FILE(docs/decisions.md:16798)), which ends both freezes (FILE(docs/decisions.md:9834) and FILE(docs/decisions.md:17012) for REG-21; FILE(docs/decisions.md:4748) for REG-22). At least one such commit is planned: REG-24's seal row in `analysis/withheld.py` (FILE(docs/drafts/reg24_confirm_draft1.md:418-421)). The check is kept, as the stricter one; the arm A hold replaces the freeze; each control's gap after its burst run (`gap_s`) and whether the boot changed are recorded (FILE(docs/probe/20261113_reg20/ops/common.sh:398)).

(b) **Replace the section "## The freeze"** (draft lines 366–378) with:
> ## The arm A hold (replaces REG-21's and REG-22's freeze, which ended with both batch 2s)
> From the commit of the start entry (proposed heading 3) until `final.sh`'s two output files are committed, or until an entry matching `STOP_PAT` stops arm A, whichever comes first:
> 1. No commit, in any session, changes: `analysis/{__init__,k1,gate,margin,derived,floor,stats,load,withheld,recheck}.py`; `harness/{__init__,checks,config,workload}.py`; `configs/defaults.yaml`; `tools/manifest.py`; `pyproject.toml`; `uv.lock`; `.python-version`; `docs/probe/20261113_reg20/ops/{common.sh,vm_state.py,session_probe.sh,launch.sh,queue.sh,final.sh,control_due.py,recheck_one.py,owner_rulings.txt,scripts_commit.txt}`; and no file named `gate_*.txt` is added under `docs/probe/reg20/`.
> 2. No tracked file under `analysis/` or `harness/` is edited in the main checkout's working tree, committed or not (`recheck_guards` stops the copy, FILE(docs/probe/20261113_reg20/ops/common.sh:495); the stop of 2026-11-13, FILE(docs/decisions.md:4604)). Drafts that touch these folders are written in a worktree or a scratchpad.
> 3. A seal row for another registration (REG-24's, D1's, D2's) waits for the end of the hold. If one cannot wait, an entry first stops arm A (`STOP_PAT`); `common.sh`'s `SEAL_BLOBS` is then changed by a reviewed commit, with a new `scripts_commit.txt`, before the queue starts again, and that entry and the [RESULT] name both scripts commits.
> 4. `docs/status.md` and `agent/STATE.md` carry a notice of the hold, naming this list, from the start entry's commit to its end.
> 5. A commit that breaks the hold is a [CORR] entry.
> **Duty in the [RESULT]:** the output of `git log --full-history --format='%H %ct %s' <start entry's commit>..<the commit of final.sh's files> -- <the files of item 1>` and of `git status --porcelain -- <the same files>` run just before `final.sh`, verbatim, as REG-22's batch 2 quoted its freeze facts (FILE(docs/decisions.md:16586-16598)).
> Draft 2 changes none of the files of item 1 outside its ops folder (DERIVED: `git diff --stat c8b482d 56820bd -- analysis harness configs tools pyproject.toml uv.lock .python-version` is empty).

(c) **Point 16**, replace "**The freeze (RB9).** … (b) also waits for both batch 2s." (line 304) with:
> **The freeze (RB9) has ended:** both batch 2s are computed (FILE(docs/decisions.md:16571), FILE(docs/decisions.md:16798); FILE(docs/decisions.md:17012)). Under (b) the seal row is added after `final.sh`'s files are committed, which is also the end of the arm A hold.

(d) **Owner question 16**, after "Owner-proxy recommends (a), since no frozen file changes." (line 356), add:
> (Written while the freeze was in force. It has ended, so this reason no longer separates (a) from (b): (a) keeps arm A's folders sealed until arm B ends; (b) adds one seal row after `final.sh`, under the hold's end.)

(e) **Proposal 4** (line 427): replace "after `final.sh` and both batch 2s" with "after `final.sh`'s files are committed".

(f) **README:130**, replace the paragraph with:
> While arm A runs, the arm A hold applies (decision, "The arm A hold"): no commit to its files and no uncommitted edit under `analysis/` or `harness/` in the main checkout. A breach stops the queue until `common.sh` is updated by a reviewed commit or the change is reverted. REG-21's and REG-22's freeze has ended (both batch 2s are computed).

(g) **Item map:** in row RA-O1, replace "REG-21's and REG-22's freeze bars commits to both seal files until both batch 2s." with "The arm A hold bars them (the freeze has ended)". In M10, replace "mitigated by the freeze" with "mitigated by the arm A hold".

### RC2. `owner_rulings.txt` can be changed after the owner's entry, by any commit, and every script accepts it
**Class:** a code change (with a sandbox change).

**What is wrong.**
- `rulings_ok` checks only that the file is tracked, equals HEAD and holds allowed answers (FILE(docs/probe/20261113_reg20/ops/common.sh:100-120)).
- `gate_in_log` checks that a rulings heading comes before the start heading (FILE(docs/probe/20261113_reg20/ops/common.sh:133-138)).
- So a later commit that changes only `owner_rulings.txt` passes every check. The file's own comment, "This file is changed only in the commit of the owner's entry" (FILE(docs/probe/20261113_reg20/ops/owner_rulings.txt:4-5)), is enforced by nothing.
- The sandbox's `setrul` is exactly such a commit (FILE(docs/probe/20261113_reg20/ops/test_sandbox.sh:235)). RA5's purpose, rulings fixed before any control bit is visible, is then a matter of text only (Trace 2, step 4).

**Patch** (`reviews_r3/rc2_rc3_common.patch`, first hunk pair; tested, PROBE(`sbx3/sandbox_patched_run.txt`)):
```diff
@@ rulings_ok() {
-  local k v rel=${RULINGS#$R/}
+  local k v rel=${RULINGS#$R/} rc
@@
   [[ $(ruling 2a) != pin_head ]] || { MSG="the owner chose a pin at or after 5ee6e38 (point 2a): common.sh's PIN changes by a reviewed commit first"; return 2; }
+  # RC: the rulings change only in the commit of an owner's rulings entry (RA5): the last commit that touched the file
+  # must add that heading to docs/decisions.md. A later rulings heading also moves `gl`, so the start heading must follow it.
+  rc=$(git -C $R log -1 --format=%H -- $rel)
+  git -C $R show --format= $rc -- docs/decisions.md 2> /dev/null | sed -n 's/^+//p' | grep -qE "$RULINGS_PAT" || { MSG="the last commit that changed owner_rulings.txt (${rc:-none}) adds no '[DECISION] (owner) REG-20 arm A operations: the owner's rulings' heading: a ruling changes only with the owner's entry (RA5)"; return 2; }
   return 0
```

**Sandbox** (`reviews_r3/rc2_rc3_test_sandbox.patch`):
- `setrul` appends an owner's rulings heading and a new start heading in the same commit.
- New cases:
  - a ruling changed by a commit with no rulings heading stops the queue, `launch.sh` and `final.sh`;
  - a new rulings heading without a new start heading after it stops the queue, through the existing `sl > gl` rule.
- Because the new check runs after the value checks, the existing "every point unset" cases keep their messages. A first version that put it first failed those two cases on their message only (rc 2 in both), and is not proposed.

**Text, added to point 14's headings list:** "The last commit that changed `owner_rulings.txt` must add the owner's rulings heading (`rulings_ok`). A ruling therefore changes only with a new owner's entry, after which the start heading must be written again (RA5)."

### RC3. Under ruling 7 `not_run`, the delegate may drop a seed whose other attempt failed a check that T3 ties to a stuck run
**Class:** a code change, a stricter rule and wording.

**What is wrong.**
- `setup_case` is set when *either* attempt failed only setup checks (FILE(docs/probe/20261113_reg20/ops/common.sh:304)).
- Under 7 `not_run`, the delegate's `not_run` is then accepted (FILE(docs/probe/20261113_reg20/ops/common.sh:314)).
- The sandbox asserts this for `client_lag`, then `trigger` (FILE(docs/probe/20261113_reg20/ops/test_sandbox.sh:485-493)).
- `client_lag` is one of the names T3 correlates with a stuck run (FILE(docs/decisions.md:4103); draft point 15). RA3's own reason, "T3's reason for counting a loss as cold does not reach" setup checks (draft line 340), does not cover an attempt that failed outside the class.
- In the mixed case, the only information left is that invalid attempt. The registered label for it is `lost_open` (RB7).

**Patch** (`reviews_r3/rc2_rc3_common.patch`, the `decide` hunks; tested):
```diff
-  local cfg=$1 line id st failed f n_valid=0 n_heat=0 norerun="" bad="" lost="" commit="" only nmax extra n counted sf slab okrec setup_case
+  local cfg=$1 line id st failed f n_valid=0 n_heat=0 norerun="" bad="" lost="" commit="" only nmax extra n counted sf slab okrec setup_case setup_all
@@
   setup_case=""; [[ $cfg == ${B}* ]] && (( counted >= nmax && ${#inval} >= 2 && ${#setup} > 0 )) && setup_case=1
+  # RC: every invalid attempt failed only setup checks. Only then may a delegate settle not_run; in the mixed case
+  # (one attempt failed a check outside the class) the delegate's label is REG-20's registered lost_open (RB7, T3).
+  setup_all=""; (( ${#inval} > 0 && ${#setup} == ${#inval} )) && setup_all=1
@@ not_run)
-            { rec_by $sf owner || { [[ -n $setup_case && $(ruling 7) == not_run ]] && rec_by $sf delegate; }; } || { MSG="${sf:t}: label not_run needs an owner's record, or a delegate's in RA3's case under ruling 7 not_run"; return 2; }
+            { rec_by $sf owner || { [[ -n $setup_case && -n $setup_all && $(ruling 7) == not_run ]] && rec_by $sf delegate; }; } || { MSG="${sf:t}: label not_run needs an owner's record, or a delegate's in RA3's case under ruling 7 not_run when every invalid attempt failed only setup checks (${SETUP_CLASS[*]})"; return 2; }
@@ lost_open)
-            { rec_by $sf owner || { [[ -n $setup_case && $(ruling 7) == lost_open ]] && rec_by $sf delegate; }; } || { MSG="${sf:t}: label lost_open needs an owner's record, or a delegate's in RA3's case under ruling 7 lost_open"; return 2; }
+            { rec_by $sf owner || { [[ -n $setup_case ]] && { [[ $(ruling 7) == lost_open ]] || [[ $(ruling 7) == not_run && -z $setup_all ]]; } && rec_by $sf delegate; }; } || { MSG="${sf:t}: label lost_open needs an owner's record, or a delegate's in RA3's case under ruling 7 lost_open, or under ruling 7 not_run when an attempt failed a check outside the setup class"; return 2; }
```

**Sandbox:**
- The two blocks that settle `not_run` by delegate now use `outs trigger kv_capacity` (both attempts setup-only).
- New cases for the mixed case (`client_lag`, then `trigger`):
  - it stops;
  - the delegate's `not_run` is refused;
  - the delegate's `lost_open` is taken, and the slot reads `lost_open` with both runs in `runs/`;
  - under 7 `per_stop`, the delegate's `lost_open` is refused.

**Wording.**
- **Point 7**, replace "Ruling 7 says which label the delegate may write, or that each case goes to the owner." with:
  > Ruling 7 says which label the delegate may write, or that each case goes to the owner. Under `not_run` the delegate may write `not_run` only when every invalid attempt failed only setup checks; when one attempt failed a check outside the class (for example `client_lag`, which T3 ties to a stuck run, FILE(docs/decisions.md:4103)), the delegate writes `lost_open`, REG-20's registered label (RB7).
- **Owner question 7:** replace the `not_run` option with:
  > `not_run`: when every invalid attempt failed only setup checks, the delegate may settle it as `not_run` and the second run is held out of `runs/`; in the mixed case the delegate settles `lost_open` (RB7).
- **Owner question 7:** in "Draft 2 recommends **`not_run`** for this narrow class only", add after "class only": ", where both attempts are setup-only".

### RC4. Point 15 and duty (iii) promise that no discretionary ruling follows the control bits, but the design keeps several
**Class:** wording and a reporting duty.

**What is wrong.**
- Point 15 ends: "The answers that follow any stop are fixed before the first launch (RA5), so no later choice depends on these lines" (draft line 295).
- Duty (iii) has the [RESULT] state "that no discretionary ruling was made after" the first `CONTROL_DUE yes|unclear` line (draft line 404).
- The scripts leave these answers per stop, all after bits may be visible:
  - a rerun after `manipulation`, `power_limit` or a second `gpu_steady` (the owner's `rerun_ok`, FILE(docs/probe/20261113_reg20/ops/common.sh:194), FILE(docs/probe/20261113_reg20/ops/common.sh:337); RB7's "At each of these stops the owner decides … whether the rerun is made");
  - a loss without a reboot (the owner's `lost_ok`, FILE(docs/probe/20261113_reg20/ops/common.sh:220));
  - every answer under 2a `stop` and 7 `per_stop`;
  - `attempt_ok` beyond 9(a);
  - `nofile_ok`;
  - each "the owner decides" stop in `decide` (FILE(docs/probe/20261113_reg20/ops/common.sh:273-282)).
- With k_c = 5 known, a rerun-or-not answer after `manipulation` moves the outcome between `refutes` and `inconclusive` (RB7's own last sentence).
- The hand-written records carry no time, so whether one came after a bit cannot be checked from them (FILE(docs/probe/20261113_reg20/ops/README.md:99-108)).

**Replacement text.**
- **Point 15**, replace its last sentence with:
  > The answers to the stops of points 2a, 6, 7, 8 and 9 are fixed before the first launch (RA5). These are still given per stop, after control bits and failed-check names may be visible: a rerun after `manipulation`, `power_limit` or a second `gpu_steady` (RB7); a loss without a reboot, or with an unknown launch boot (point 8); every answer under ruling 2a `stop` or 7 `per_stop`; a further attempt by `attempt_ok` other than 9(a)'s; `nofile_ok`; and every "the owner decides" stop of `decide`. Each such answer is a discretionary ruling made after outcome bits may be visible.
- **Duty (iii)**, replace its second bullet with:
  > The [RESULT] names the first `CONTROL_DUE yes` or `unclear` line in the queue output and lists every hand-written record in `state/` (`rerun_ok`, `lost_ok`, `settle`, `attempt_ok`, `nofile_ok`, `recheck_ok`): its name, `by`, `under`, the commit of the [OPS] entry that names it, whether it came after that line, and the label it led to.
- **Stricter rule, added to "Records" (README) and to point 7:**
  > Each hand-written record is named in an [OPS] entry committed when it is written; that commit's time is the record's time.

### RC5. Under 2a `setaside`, `lost_open` cannot be reached for any seed with a set-aside attempt, and the owner's question says otherwise
**Class:** wording and a reporting duty.

**What is wrong.**
- k1 gives `lost_open` only from two stored-invalid folders in `runs/` (FILE(analysis/k1.py:286)). A set-aside folder is stored valid and never enters `runs/`.
- So a seed with a set-aside attempt ends with its valid rerun's label, or with `not_run`. Two cases stop the queue: a set-aside plus an invalid rerun, and two set-asides (FILE(docs/probe/20261113_reg20/ops/common.sh:347); sandbox FILE(docs/probe/20261113_reg20/ops/test_sandbox.sh:397-402)).
- A `lost_open` settle is refused there (FILE(docs/probe/20261113_reg20/ops/common.sh:320)). What remains is the owner's `not_run` or a third attempt (Trace 3).
- Draft 2 states only the two-set-aside case (line 324), and only for the owner's choice. Duty (v) gives the `lost_open` counterfactual line for `keep` only (line 407).

**Replacement text.**
- **Owner question 2a**, replace the bullet "**Risk of `setaside`, found in this draft:** …" with:
  > **Risk of `setaside`:** k1 reads `lost_open` only from two stored-invalid folders in `runs/` (FILE(analysis/k1.py:286)); a set-aside folder is stored valid and stays out of `runs/`. A seed with a set-aside attempt therefore ends with its valid rerun's label or as `not_run`: after a set-aside and an invalid rerun, or two set-asides, the queue stops (FILE(docs/probe/20261113_reg20/ops/common.sh:347)), a `lost_open` settle is refused (FILE(docs/probe/20261113_reg20/ops/common.sh:320)), and the only answers are the owner's `not_run` or a third attempt. Both attempts are then invalid by the checks in force, which REG-20 labels `lost_open`, cold (FILE(docs/decisions.md:4067)); the seed leaves n instead, which can turn `refutes` into `inconclusive` (DERIVED: k_stuck falls by one, FILE(analysis/k1.py:224), FILE(analysis/k1.py:233)), T3's direction (FILE(docs/decisions.md:4103)).
- **Point 2a's `setaside` bullet**, replace "and stop; a restart reruns its config" with:
  > and stop; a restart reruns its config. A later stop with the attempts spent can be settled only `not_run` (or by a third attempt); see owner question 2a.
- **Duty (v)**, replace "Under `keep`, add the second outcome line with that seed counted `lost_open`." with:
  > Under `keep`, and under `setaside` for every seed settled `not_run` with a set-aside attempt, add a second outcome line, which changes no label, with that seed counted `lost_open`.
- **"Not settled"**, replace the bullet "Under 2a `setaside`, two set-asides of one burst config read `not_run` in k1" with:
  > Under 2a `setaside`, any seed with a set-aside attempt and no valid rerun reads `not_run` in k1, never `lost_open` (owner question 2a; duty (v)).

### RC6. Held and set-aside folders are raw data with no permanent home, manifest entry or backup, and VM copies may be removed during arm A
**Class:** a stricter rule and a reporting duty.

**What is wrong.**
- **Not covered by the manifest or the backup.**
  - A held folder (`held_<rid>.txt`) or a set-aside folder (`setaside_<rid>.txt`) stays in `<repo's parent>/aftershock-reg20-holding` (FILE(docs/probe/20261113_reg20/ops/common.sh:12), FILE(docs/probe/20261113_reg20/ops/common.sh:531), FILE(docs/probe/20261113_reg20/ops/common.sh:561)).
  - `tools/manifest.py update` lists `runs/` only (FILE(tools/manifest.py:48-51)), and a backup is checked against that manifest with `tools/manifest.py verify <copy>` (FILE(docs/status.md:170)). I did not open the backup folder (brief).
  - The hold record holds a checksum of the VM's checksum list only (FILE(docs/probe/20261113_reg20/ops/common.sh:561)).
- **Removing the VM copy is allowed.** The owner's 2026-11-04 rule allows removal once a copy on the Mac is checksum-verified (FILE(docs/decisions.md:530-535); CLAUDE.md rule 4). A held copy is verified, so after such a removal the holding folder would be the only copy, outside every manifest.
- **There is no way back into `runs/`.**
  - A set-aside folder can never enter `runs/` while REG-20's table must stay computable, once its config has a valid rerun: two valid runs make k1 raise (FILE(analysis/k1.py:146-147)).
  - A held folder entering `runs/` turns its seed's `not_run` into `lost_open` (FILE(analysis/k1.py:286)).
- **Docs cannot name them.** `check_docs` fails any run id named in the docs that is not in `runs/` (FILE(tools/check_docs.py:6), FILE(tools/check_docs.py:82)), unless it is in `manifests/pending_copy.txt` (FILE(tools/check_docs.py:69-72)). The [RESULT] duties (v) and (vi) name such runs.
- **VM removals stop the queue.** Removing the VM copy of any REG-20 folder during arm A stops the queue: "the Mac holds X, which the VM does not list" (FILE(docs/probe/20261113_reg20/ops/common.sh:275-276)).

**Replacement text.** Add to point 10 (or as a new point 10a):
> **Held and set-aside folders.** A folder kept in the holding folder is raw data outside `runs/`, the manifest and the second copy of `runs/`. Until a decision names its permanent place: (i) its VM copy is not removed, and no VM copy of any folder of the eleven configs is removed before `final.sh`'s files are committed (`decide` stops on a Mac folder the VM does not list, FILE(docs/probe/20261113_reg20/ops/common.sh:275-276)); (ii) when it is held or set aside, its per-file sha256 list is written beside it as `<holding folder>/<run id>.sha256`, and that list's own sha256 is quoted in the [OPS] entry that names the record; (iii) its run id is listed in `manifests/pending_copy.txt` before any doc names it, with the holding path in the [OPS] entry; (iv) the [RESULT] lists each such folder with its record. A set-aside folder whose config has a valid rerun can never enter `runs/` while REG-20's table must stay computable (two valid runs make k1 raise, FILE(analysis/k1.py:146-147)); a held folder entering `runs/` turns `not_run` into `lost_open` (FILE(analysis/k1.py:286)). Either move is RB4 (ii)'s case: `analysis.k1 reg20` is run again and an [OPS] or [CORR] entry reports whether its output changed. Rule 4's custody of these folders after REG-20's [RESULT] is the owner's.

### RC7. The order with E1, the VM checkout and RUNBOOK's "deploy HEAD" are kept by hand, and RUNBOOK says otherwise
**Class:** a stricter rule and wording.

**What is wrong.**
- **No order is written.** The lead's rule ("whichever of E1 and arm A has its operations approved first runs first; the other waits for its end entry", the brief's point 3) is in no draft text. Arm A has no defined end entry.
- **RUNBOOK says otherwise.** RUNBOOK §5 orders arm A (row 2a) before E1 (row 4) (FILE(agent/RUNBOOK.md:64), FILE(agent/RUNBOOK.md:66)). RUNBOOK §3 step 6 tells the agent to "deploy HEAD (§4)" after REG-19's [RESULT] (FILE(agent/RUNBOOK.md:48)), and §4 pulls `main` (FILE(agent/RUNBOOK.md:53)). Done during arm A, between runs, that moves the VM off the pin.
- **Neither script prevents interleaving.** E1's scripts wait only on REG-19 (FILE(docs/drafts/review_bundles/e1_r3/ops/common.sh:100-107)), and E1 is the next GPU work in the state file (FILE(agent/STATE.md:52)). Both arms fail safe on the tree (FILE(docs/probe/20261113_reg20/ops/launch.sh:50), FILE(docs/probe/20261113_reg20/ops/session_probe.sh:44)). Interleaving between runs is still possible (Trace 1, step 4).
- **The VM tree is unknown.** "The watcher reports tree=a7bb77a" is not evidence (rule B). The session probe's `tree` line will be.

**Replacement text.**

(a) **New point 18, "Order with E1".** Add to the Summary table: `| 18 | Order with E1 | the lead's rule; arm A's end heading defined | delegate |`. The point's text:
> Whichever of E1 and REG-20 arm A has its operations [DECISION] committed first runs first; the other waits for its end entry. Arm A's end entry is `## <date> · [OPS] REG-20 arm A: the queue ended (QUEUE DONE)`, written after `QUEUE DONE` and before `final.sh`, or an entry matching `STOP_PAT`. While arm A has started (heading 3) and not ended: no E1 `vm_checkout.sh`, session probe or queue; no change of the VM's checkout other than README step 4; no deploy of HEAD (RUNBOOK §3 step 6, §4). If E1 runs first, README step 4 waits for E1's end entry and for E1's queue lock to be absent. Where E1's decision comes first, this departs from RUNBOOK §5's row order (2a before 4), and the start entry says so. E1's scripts test only REG-19's lock (FILE(docs/drafts/review_bundles/e1_r3/ops/common.sh:100-107)); the matching wait on arm A's start and end headings is for E1's own decision.

(b) **Proposals 1–2:** move from "Proposals for later decisions" into the [DECISION] itself. That is, the RUNBOOK edits (RB6's RUNBOOK:48 and :64 sentences, verbatim, and RUNBOOK:63 marked done with 3c8e5dc) are made in the commit of heading 1, before any launch. Add to RUNBOOK:48's new text: "; while REG-20 arm A or E1 has started and not ended, no deploy".

(c) **README launch order, step 4:** prepend "Only if E1 has not started, or E1's end entry is committed and E1's queue lock is absent (point 18):".

### RC8. The status lines are stale again: draft 2's scripts are committed in 56820bd
**Class:** wording.

**What is wrong.**
- Draft line 7 says draft 2's scripts "are **not committed**", and README:8 says "**Draft 2 is not committed and not reviewed.**"
- They were committed in 56820bd ("[OPS] Drafts for review, none approved: … REG-20 arm A ops decision draft 2 with its draft scripts (owner_rulings.txt all unset, so they refuse to start)"). PROBE: `git log -1 -- docs/probe/20261113_reg20/ops/common.sh` gives 56820bd. The same is true of `queue.sh`, `launch.sh`, `final.sh`, `recheck_one.py` and `owner_rulings.txt`; `control_due.py`, `vm_state.py` and `session_probe.sh` are at c8b482d.
- This is the error of round 1's RA7, now arising from the timing. The bundle note's "Nothing is committed" was true at its HEAD, 7be592d.

**Replacement text.**
- **Draft line 7:**
  > **Draft 2's scripts** are committed in 56820bd ("[OPS] Drafts for review, none approved"), with `owner_rulings.txt` all `unset`, so they refuse to start (FILE(docs/probe/20261113_reg20/ops/common.sh:116)). The [DECISION] names the commit that holds the scripts after round 2's items are applied, with `scripts_commit.txt` and its sandbox count, and the diff from 56820bd to it gets the review RA7 asks for.
- **README:8:**
  > **Draft 2 is committed in 56820bd and not approved.**

---

## 5. Optional items

### RC-O1. Let the seal check tolerate added `SEALS` rows (code change; not run)
**Why.** RC1's hold makes arm A depend on every other session's discipline. A row added to `SEALS` can only seal more:
- `control_due.py` then raises on load (FILE(analysis/withheld.py:62-66)), and its non-zero rc stops the queue (FILE(docs/probe/20261113_reg20/ops/queue.sh:50));
- `final.sh` refuses a `withheld:` line (FILE(docs/probe/20261113_reg20/ops/final.sh:59), FILE(docs/probe/20261113_reg20/ops/final.sh:77)).

So tolerance fails closed.

**Patch.** In `common.sh`, add the function below and replace `mac_checks`' seal loop (lines 81–83) with `seal_ok || { echo "STOP: analysis/load.py is not the blob $SEAL_BLOBS[1], or analysis/withheld.py differs from the blob $SEAL_BLOBS[2] by more than added SEALS rows"; return 2; }`.
```zsh
# The seal: load.py exactly the recorded blob; withheld.py the recorded blob or that blob with SEALS rows inserted
# (every recorded line kept, in order; every added line one `("<id>", "<pattern>", "[RESULT] …"),` row).
seal_ok() {
  [[ -f $R/$SEAL_FILES[1] && $(git -C $R hash-object $R/$SEAL_FILES[1]) == $SEAL_BLOBS[1] && -f $R/$SEAL_FILES[2] ]] || return 1
  [[ $(git -C $R hash-object $R/$SEAL_FILES[2]) == $SEAL_BLOBS[2] ]] && return 0
  git -C $R cat-file -p $SEAL_BLOBS[2] | python3 -I -c 'import difflib, re, sys
rec = sys.stdin.read().splitlines(); cur = open(sys.argv[1]).read().splitlines()
row = re.compile(r"^    \(\"[A-Za-z0-9-]+\", \"[^\"]+\", \"\[RESULT\] [^\"]+\"\),( +#.*)?$")
ops = [o for o in difflib.SequenceMatcher(None, rec, cur, autojunk=False).get_opcodes() if o[0] != "equal"]
sys.exit(0 if all(t == "insert" and all(row.match(x) for x in cur[c:d]) for t, a, b, c, d in ops) else 1)' $R/$SEAL_FILES[2]
}
```
**Sandbox.**
- The cases at FILE(docs/probe/20261113_reg20/ops/test_sandbox.sh:703-705) need the new message.
- Add two cases:
  - a commit adding one SEALS row: the queue goes on;
  - a row whose pattern seals an arm A burst run: `control_due.py` raises, and the queue stops.
- With this, RC1 item 3 can read "may be committed; the [RESULT] lists it".

### RC-O2. Refuse arm A while E1's queue lock exists (code change)
Mirror E1's test of REG-19's lock. In `common.sh`, after `GATE_FILE_RE`:
```zsh
E1_LOCK=$R/docs/probe/20261113_e1/ops/state/queue.lock   # tested for existence only (as E1 tests REG-19's); nothing there is opened
```
and in `gate_in_log`, before `rulings_ok || return 2`:
```zsh
  [[ ! -e $E1_LOCK && ! -L $E1_LOCK ]] || { MSG="E1's queue lock exists ($E1_LOCK; only its existence is tested): E1's queue may be running; arm A waits for E1's end entry (point 18)"; return 2; }
```
This does not implement "waits for the end entry", since a stopped E1 queue leaves no lock. RC7's text does that.

### RC-O3. `STOP_PAT` should also catch "halted" (code change)
E1's stop heading is "[DECISION] (owner) E1 halted" (FILE(docs/drafts/review_bundles/e1_r3/ops/common.sh:104)). An owner writing "REG-20 arm A halted" by analogy would not stop arm A (FILE(docs/probe/20261113_reg20/ops/common.sh:42)).

Replace `(stops|is stopped)` with `(stops|is stopped|halted|is halted)`, and add one sandbox case.

### RC-O4. Ruling 9(b) can mask `refutes` (wording)
k1 checks `pending_control` before `refutes` (FILE(analysis/k1.py:227-234)). One control slot settled under 9(b) therefore turns any outcome, `refutes` included, into `pending_controls`.

Add to owner question 9:
> Under (b) one settled control slot makes the whole outcome `pending_controls`, whatever the other seeds give, `refutes` included (FILE(analysis/k1.py:227-234)).

### RC-O5. Point 4's open question is moot (wording)
Replace "Which queue launched seed 15's closed run is not checked here … (BELIEF until seed 15's launch record is cited)." (line 143) with:
> Every REG-19 launch script on file starts the harness with the same command and no `ulimit`: launch3.sh:27, launch4.sh:31, launch5.sh:32, launch6.sh:36 (all in `docs/probe/20261111_reg19/ops/`), `_to_delete/docs/probe/20261113_reg19/ops/launch7.sh:41` and `launch8.sh:35`, `docs/probe/20261113_reg19/ops_r3/launch.sh:51` (PROBE: `grep -l ulimit` over the three folders finds none, rule F round 2). Whichever of them launched seed 15's closed run, it set no limit; only a launch by hand outside these scripts would differ (BELIEF that there was none).

### RC-O6. Duty (ii): the server itself inherits the limit (wording)
The harness starts vLLM as a child process (FILE(harness/run.py:159)), so the open arm's 65536 is also the server's limit. Replace the first sentence of duty (ii) with:
> The open arm's launch shell raises the soft open-file limit to 65536, and the harness starts vLLM as its child (FILE(harness/run.py:159)), so the server under test inherits it; the closed arm's server ran at the shell's default (BELIEF 1024, FILE(agent/RUNBOOK.md:28)).

### RC-O7. Question G: evidence the draft can add (wording)
Add to question G's options:
> Evidence for (a): (1) `reg20_a_may_start` reads only `*_burst_l1pl350cl_r2.0_w3000_s<seed>` (FILE(analysis/k1.py:43-44), FILE(analysis/k1.py:269-280)); `fnmatch` matches whole names, so the unseal could not change its input even had a REG-20 folder existed. (2) No commit touched k1's import closure from d9b324d to 3c8e5dc, and REG-22 batch 2's prechecks found those files clean in the working tree at about 23:17 UTC (FILE(docs/decisions.md:16586-16598)); an uncommitted edit at 23:03 UTC that was undone by then is not excluded (BELIEF that there was none). (3) HEAD holds exactly one gate pair in `docs/probe/reg20/` (PROBE: `git ls-tree -r --name-only HEAD -- docs/probe/reg20/`, rule F round 2).

### RC-O8. The owner's rulings entry states what k_c = 5 implies (reporting duty)
Add to proposed heading 2's description:
> The entry states that the rulings are made with REG-19's outcome and the gate public (k_c = 5), and, beside each ruling: a ruling that takes a seed out of n makes `supports` unreachable (DERIVED: (4,0) gives 1/16) and can lower k_stuck by one; a ruling that labels a seed `lost_open` adds one to k_stuck.

### RC-O9. Fix rerun-or-not after `manipulation`, `power_limit` and a second `gpu_steady` now (a stricter rule; new owner point 7b)
This shrinks RC4's list. Add to `owner_rulings.txt`:
> `#   7b: rerun | no_rerun | per_stop   (manipulation, power_limit, a second gpu_steady)`

Under `no_rerun`, the delegate settles `not_run`. Under `rerun`, the delegate writes `rerun_ok`. RB7's sentence weighs against `rerun` after `manipulation`. `lift_ok` needs the matching branch.

### RC-O10. A VM checkout script (code change)
Port E1's `vm_checkout.sh` (FILE(docs/drafts/review_bundles/e1_r3/ops/vm_checkout.sh:15-43)) for README step 4. It should:
- refuse while tmux `run` is alive, a compute process is on the GPU, or arm A's or E1's queue lock exists;
- record the tree before and after in a probe file.

That turns "never while a run is in progress" from a hand rule into a check.

### RC-O11. `recheck_one.py`'s error field (code change)
`error` keeps 200 characters of the exception text (FILE(docs/probe/20261113_reg20/ops/recheck_one.py:47)), and the queue's filter keeps it (FILE(docs/probe/20261113_reg20/ops/common.sh:488)). A pandas or numpy message can carry values read from the run.

Keep `type(e).__name__` in the record, and send the text to the stderr file, which ALLOWED does not list.

### RC-O12. One citation (wording)
Point 14 cites "common.sh:126" for "Any second gate file there refuses the start". The count check is at FILE(docs/probe/20261113_reg20/ops/common.sh:143); line 126 is the function's first line.

---

## 6. The writer's six unsettled points

1. **The freezes have ended.** Agreed (FILE(docs/decisions.md:17012)). It is wider than the seal files (RC1), and a commit is already planned (REG-24). → RC1, RC-O1.
2. **The gate was computed once, with RUNBOOK:63's command; `gate.sh` is withdrawn; RB11 cannot be met.**
   - The withdrawal is clean: `gate.sh` is not in `SCRIPTS`, and the sandbox fails if any script calls `reg20_a_may_start` (its last case, PROBE(`sbx/sandbox_run.txt`)).
   - Question G(a) is supportable on the evidence in RC-O7.
   - The "Timing" section answers RB11 honestly. RC-O8 adds the one duty that the known k_c = 5 calls for.
3. **The order with E1 is kept by hand.** → RC7 (text, end heading, RUNBOOK) and RC-O2 (lock).
4. **The VM's checkout is unknown.** This fails safe: `launch.sh:50` and `session_probe.sh:44` stop on any tree but the pin. The watcher's report is not evidence; the session probe's `tree` line will be. → RC7 (b), RC-O10.
5. **The holding folder and `recheck_one.py`.**
   - They work as described: 46 of 46, and the sandbox counts above. `runs/` is a real directory, so `recheck_one.py`'s resolved-parents test is sound (PROBE: `ls -ld runs`).
   - The missing parts are custody (RC6) and the label consequence of `setaside` (RC5).
6. **Four sub-points.**
   - **(a) The setup class is a BELIEF:** acceptable when fixed in advance. RC3 narrows what the delegate may do with it.
   - **(b) Two set-asides give `not_run`:** true, and wider than stated (RC5).
   - **(c) An edit made and undone within one `control_due.py` call:** accepted as residual. The window is the call's own duration, and RC1 item 2 forbids the edit itself (BELIEF that this is enough).
   - **(d) Seed 15's launcher:** moot (RC-O5).

## 7. Claims of the draft that I checked and that held

- **The pin.**
  - The harness at 1cface7 equals a7bb77a's.
  - k1's judged files at the working tree equal the pin's.
  - The seal files equal the recorded blobs.
  - `harness/checks.py` equals 5ee6e38's and `analysis/recheck.py` equals 72fafb5's.
  - `configs/defaults.yaml`, `tools/manifest.py`, `pyproject.toml` and `uv.lock` equal the pin's.
  - All eleven configs exist at the pin.
  - (PROBE, `reviews_r3/probes.txt`.)
- **The judged code.** k1's module-level imports reach only `JUDGED` plus `load.py` and `withheld.py`. `load.py` imports `withheld` only. The full closure adds `tables.py` and `harness/*` through function-level imports only (PROBE: closure of `analysis/k1.py`, 19 files; grep of the import lines). This supports RB14 (iv) as worded.
- **The client-error stop.** It does fire. The pin's check is named `no_errors` (PROBE), and `vm_state.py` rewrites it as `no_errors/client_error` or `no_errors/other` (FILE(docs/probe/20261113_reg20/ops/vm_state.py:35-38)), which is what `decide` matches. The setup-class names (`clean_git`, `kv_capacity`, `trigger`) and the stop list match the pin's check names.
- **The gate file.** HEAD holds exactly one gate pair (PROBE). The gate's printed line (quoted in the brief) matches `GATE_LINE_RE` (DERIVED: `0.03125` matches `[0-9.e+-]+`).
- **The control decision's read.** `control_due.py` and `final.sh` read the same `k1.cold_backlogged(run)` with default windows (FILE(docs/probe/20261113_reg20/ops/control_due.py:64), FILE(analysis/k1.py:160)).
- **No frozen file changed in draft 2.** Draft 2's change set touches only its ops folder (DERIVED: the diff stat in RC1 (b) is empty).

---

**Verdict: NOT READY.** Required: RC1 (the arm A hold replaces the ended freeze), RC2 (rulings change only with the owner's entry; code), RC3 (ruling 7's mixed case is `lost_open`; code), RC4 (per-stop rulings disclosed, with times), RC5 (`setaside` cannot reach `lost_open`; text and duty), RC6 (custody of held and set-aside folders; no VM removals), RC7 (the order with E1, arm A's end heading, RUNBOOK in the decision's commit), RC8 (stale status lines).
