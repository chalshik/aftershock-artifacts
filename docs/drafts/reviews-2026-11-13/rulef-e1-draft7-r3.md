# rulef-e1-draft7-r3 (rule F, round 3 on E1 draft 7, bundle e1_r3), verbatim

Saved by the agent at 2026-11-14 01:50 UTC from the reviewer's own file (teammate `rulef-e1-r3` of session 8c5f8396; scratchpad `reviews_r3/rulef-e1-draft7-r3.md`, 32640 bytes, 375 lines, sha256 4ab9bebf887dd52dabc4ae382c8aacdd798204e4b5110dc52d57d4f98dd5cf61, checked on copy; the reviewer's message named the same sha256 and line count). Its companion files are copied byte for byte to `docs/drafts/reviews-2026-11-13/rulef-e1-r3_files/`. The reviewer's report follows the line '---' unchanged.

---
Rule F review, round 3 (limited), of E1 draft 7 (bundle `docs/drafts/review_bundles/e1_r3/`, commit 56820bd)

**Verdict: READY, provided DE1–DE7 are applied verbatim.**
- DC1 is met in text and DC2 in text and code (sections 1 and 2).
- All seven required items are text: wording, stricter rules or reporting duties. None changes code, a threshold, the floor or the stopping rule, so they need no fourth rule F round.
- DE2, DE3 and DE4 change the owner-proxy's DD10 and DD12. Its next pass is already due for DC2, DC-O1 and DC-O2, and it rules on them there.
- DE-O1 to DE-O6 are optional. DE-O1 is code (a SEALS row and a test, patch tested here). DE-O6 widens a read, so the owner-proxy would have to pass it.

## 0. Bundle, scope and limits

**Bundle**
- MANIFEST: 50 of 50 sha256 lines OK (`shasum -a 256 -c`).
- HEAD was 56820bd when I started. During the review it moved to 47b8e06 (f43a5a1: STATE and FOR_AUTHOR; 47b8e06: REG-19 seed 18's lost control copied from the VM). `git diff --stat 56820bd HEAD` over `analysis tests harness configs docs/probe/20261113_e1 agent/RUNBOOK.md docs/experiment-plan.md docs/claims.md`, the bundle, `docs/drafts/e1_r3` and `docs/drafts/e1_draft7.md` is empty. So every anchor and FILE line below holds at HEAD. `docs/decisions.md` is append-only; the cited lines are unchanged.

**Code**
- I took `git archive 56820bd analysis harness configs tests pyproject.toml tools docs/probe/20261113_e1/ops docs/probe/20261113_freeze` into my scratchpad and ran `git apply` with `e1_py_draft7.patch`, `test_e1_draft7.patch` and `ops_draft7.patch`.
- Results:
  - `analysis/e1.py` has sha256 `428771e0…` and `tests/test_e1.py` has `dd3f52c5…`. Both are byte-equal to the bundle's.
  - All ten ops files are byte-equal to the bundle's `ops/` (cmp). The five unpatched ones equal HEAD's.
- `tests/test_e1.py tests/test_k2.py tests/test_withheld.py`: 39 passed, with the repo's `.venv` interpreter on the scratch copy (`analysis.e1.__file__` is in the copy).

**DC2: two exhaustive checks of `e1.floor` on synthetic rows** (scripts in `rulef-e1-r3_files/`)
- Setup: six rates, each row one of three types: kept up and not full; full but kept up; saturated. Every subset of missing rates was tried.
- (i) **Soundness.** Every floor that the patched rule reports on partial data equals the floor of every completion of the missing rows (`holes_sound.py`):
  - draft 7: 438 floors on partial data, 0 completions that change the floor;
  - draft 6's `e1.py`: 2457 completions that change the floor.
- (ii) **Monotonicity.** Over present sets S ⊂ S′ of one sweep, a floor on S never becomes "holes" or another floor on S′ (`holes_mono.py`):
  - draft 7: 1122 pairs, 0 bad;
  - draft 6: 915 bad.

**Ops scripts**
- Sandbox: `TMPDIR=<my scratchpad> zsh <patched copy>/test_sandbox.sh` gives `passed 192, failed 0`, rc 0 (`sandbox_r3_reviewer.txt`).
- Control: HEAD's scripts with only the patched `test_sandbox.sh` give `passed 188, failed 4`. The four failures are exactly the new DC-O1 and DC-O2 checks (`sandbox_r3_control_unpatched_scripts.txt`), so the new cases test the change.

**Citations checked**
- FILE lines that exist after the patch: `vm_checkout.sh:33` (the ancestor check); `common.sh:24`, `:164-167`, `:193`, `:224-226`, `:242`, `:267-269`; `queue.sh:68-71`.
- decisions.md headings at 4166, 4611, 16322, 16421, 16517, 16571 and 16798.
- `git grep -n -E "$END19_PAT" HEAD -- docs/decisions.md` hits 4611 and 16517.
- `withheld.lifted` on the real `docs/decisions.md` (headings only): "[RESULT] REG-21" True, "[REG] E0" False, "[RESULT] E1" False.
- `analysis/k2.py:94-95,102-109,179` as DC1 cites them.

**Other reads**
- RUNBOOK lines 40–80, and draft 6's item map, section "RUNBOOK: one proposal for the approval commit" (DD10's text).
- `docs/drafts/reg20_ops_decision_draft2.md`, by grep for E1, deploy and pin, and lines 417–425.
- `git merge-base --is-ancestor 1cface7 HEAD`: exit 0.
- `git merge-base --is-ancestor 5ee6e38 1cface7`: exit 1. REG-20 ops draft 2's pin predates the A14 harness.

**Not opened or not run**
- Not opened: `runs/` (no folder name either); the contents of any `state/` folder; `/Users/chalshik/aftershock-backups/`; RESUME.md; `docs/paper/`; any sealed folder; `docs/context-pack.md`; `docs/status.md` beyond the session-start digest that a hook put into my context; the other reviews in this `reviews_r3/` folder (I listed only their names).
- Not run: `e1.observed`, `e1.report`, `e1.floor_status`, `k2.observed`, any `k1`/`k3` function or any analysis command on run data. No VM contact.

**Writes**
- Only in my scratchpad and in this folder's `rulef-e1-r3_files/`.
- `git apply --check` of the DE-O1 patches on the main checkout writes nothing.
- The main checkout's `git status` changed during my sandbox run because the lead committed 47b8e06. I wrote nothing there.

## 1. DC1: met in text; the guard is text only (the lead's question 4)

**What round 2 asked for, and what draft 7 does**
- Round 2 classed DC1 as "disclosure and stricter rule (text)" and gave (a)–(e) as its fix.
- All five are in draft 7 verbatim, at L13, L13, L42, L43 and L68 (checked).
- README step 9's result line now names the wait for E0's [REG] (DC-O3).

**Is a text-only guard enough? Yes, for registration, on three grounds:**
1. Computing the floor needs a deliberate `AFTERSHOCK_UNSEAL=E1` (FILE(analysis/withheld.py:30), the E1 row). No tool, test or other module calls `e1.observed`, `e1.report` or `e1.floor_status`; `k2.observed` is the only other caller of `e1.floor` (grep of `analysis/`, `tools/`, `tests/`).
2. No computation is possible before E1's folders reach the Mac, which is about 2.1 h after launch at the earliest.
3. A code refusal inside `e1.py` would not cover `k2.observed`, which calls `e1.floor` directly (FILE(analysis/k2.py:179)). It would also re-open `e1.py` for a fourth round.

**But the text guard is missing where an operator reads the command.**
- RUNBOOK §5's E1 row keeps `AFTERSHOCK_UNSEAL=E1 uv run python -m analysis.e1 floor` as the item's "Registered computation (once)", with no wait (FILE(agent/RUNBOOK.md:66)).
- Draft 7's (c), like round 2's DC4 row, replaces only the first two cells ("The row's other cells stay").
- So after the approval commit, the playbook the agent works from names the command with no condition. **DE1** closes that.

**A mechanical guard exists and the entry already permits it, but it is optional (DE-O1).**
- It is one SEALS row that `AFTERSHOCK_UNSEAL=E1` does not lift. The entry allows rows added to `SEALS` after the registered commit ("Result, computed once").
- It requires one existing test, `test_e1_seal_lifts_alone`, to also hold the new heading.

## 2. DC2: met in text and in code

**Code**
- `floor` builds `have` from the finite rows, the same filter `gate.cold_floor` applies (FILE(analysis/gate.py:33)).
- `lo = -inf` when no valid row lies below λ_sat.
- A missing swept rate is therefore a hole whenever no valid row separates it from λ_sat, and whenever it lies at or above λ_sat.
- This is round 2's patch byte for byte. The two exhaustive checks in section 0 show that the rule is now sound and monotone over every subset of a six-rate grid with three row types.

**One residue in the status label, not in the value**
- A missing rate below a valid unsaturated row can still change the full-data status between "ok" and "tail_ok" (a full row there would make `cold_floor` "not_monotone"). The floor's value and λ_sat cannot change.
- My soundness check accepts that pair. It changes no decision: both statuses are floors under "Decision under each outcome".

**Text.** "Holes" at L32 is round 2's text verbatim, and it matches the code clause by clause.

**DD5 not applied (departure 6): correct.** Its sentence "is not a hole" is false under DC2: `test_a_hole_just_below_lam_sat_is_a_hole` now asserts "holes" [1.5, 2.0] for DD5's own example, and my soundness check reaches the same.

## 3. Scripts: DC-O1, DC-O2, DC-O3, DC4's README edit

**DC-O1**
- `settle` writes each invalid run's pause line from `$VMS` before the settle record (`common.sh:164-167`). `report_settled` only prints (`queue.sh`).
- `$VMS` is the read that `next_step` makes in the same turn, after the tmux session has ended, so the runs' `checks.json` exist.
- A death after the append and before the record leaves a duplicate line, which is harmless, as round 2 said. The reviewer's case passes, and it fails on HEAD's scripts.

**DC-O2**
- `n_norun` counts settled records with no `rid ` line, the sweep's included.
- The stop sits in the rate loop with the other global stops (`common.sh:270`). When every rate still without a valid run is spent, the queue therefore ends with `QUEUE END` and not this message; nothing is launched either way.
- This matches the appended text ("a second such launch, at any rate, stops E1"). A failed sweep start followed by one failed single-rate launch stops E1, which is stricter and accepted.
- A pre-launch refusal writes no attempt record and so does not count (DA3's text holds).

**DC-O3 and DC4's README edit:** done as the items allow. Finding 6 is DE6 below.

## 4. The writer's departures and "Found while applying"

- **Departure 1 (DC4's RUNBOOK order replaced by the lead's rule):**
  - The rule is accepted. The facts changed: REG-20's gate was computed (3c8e5dc), and REG-20 is owner-approved (FILE(docs/decisions.md:4166)). Round 2's row (E1 first, REG-20's gate waiting for E1's end entry) can no longer be met.
  - Three gaps remain:
    - (i) DD10 (a) and (b), applied verbatim, still force E1 first. (b) also collides with REG-20 ops draft 2's RB6 on the same RUNBOOK:48 anchor. See **DE2**.
    - (ii) "Approved first" and REG-20's end entry are undefined: REG-20 ops draft 2 defines no end-entry heading and does not mention E1. See **DE3**.
    - (iii) The RUNBOOK row's computation cell. See **DE1**.
- **Departure 2 (facts since round 2):**
  - Checked: the pin clause is met; END19_PAT matches 16517; `lifted("[RESULT] REG-21")` is True.
  - One fact is now at risk. RUNBOOK §3 item 6 ("copy the lost seed-18 folder …; then deploy HEAD (§4)", FILE(agent/RUNBOOK.md:48)) is under way: its first half landed in 47b8e06. If its deploy runs before E1's approval, the VM leaves `a7bb77a` at HEAD, and R6's "first move of the VM off `a7bb77a`" and the ID line's "leaves REG-19's pin" become false. See **DE6**.
- **Departures 3–9:** accepted.
  - Renumbered citations: checked.
  - DD2: accepted.
  - DD3's merge: one wording point, DE-O4.
  - DD5: correct, as section 2 says.
  - DD6(b)'s merge: redundant but true.
  - DD7's hashes: checked.
  - The freeze bullet: moot, and kept as a record.
- **Found 1 (DD12 conflicts):** the draft is right and DD12 is not. See **DE4**.
- **Found 2:** section 1, DE1, DE-O1.
- **Found 3:** the sentence is now false in its last clause. See **DE5**.
- **Found 4:** see **DE7**. DC-O2's stop is rightly absent from DD6(a)'s list: a launch that names no run has no `checks.json` details to read. The cost of that is DE-O6.
- **Found 5:** **DE3**.
- **Found 6:** **DE6** (README). `vm_checkout.sh:2` is a frozen script's comment; it is left, and DE6 discloses it.
- **Found 7:** accepted. README line 3 names what is stale.
- **Found 8:** DE-O5.
- **Found 9:** no item.

## 5. A trace on which E1's verdict would be wrong

**Trace A (E1's floor)**
1. The sweep runs 1.5 → 4.0 back to back in one invocation, about 2.1 h at 350 W. At 3.0, `gpu_steady` fails on `busy_sm_clock_cv` > 0.05. That check is new since `5ee6e38` and has never run on the GPU (R3, R4). DD4 gives P(a `recorder` or `gpu_steady` failure) ≈ 0.1 (BELIEF).
2. R3 gives it the heat rule's single rerun, after cooling to ≤ 45 °C. The rerun 3.0′ starts cold and runs alone.
3. All six rates now have a valid run. `cold_floor` gives "ok", λ_sat 2.0, n 5, and the floor is the mean of 2.0, 2.5, 3.0′, 3.5 and 4.0.
4. Four of those rows were measured on a GPU that had been under load for 20–100 min, and one from a cool start.
5. If a cooler die holds a higher SM clock at the same 350 W (BELIEF, unmeasured here), 3.0′ is high by some x %. The floor is then high by about x/5 %, and `floor_slope_reported` gets a bump at 3.0.
6. The original 3.0's clock-steadiness failure also says that the hot sweep's clock was moving, so the other rows may sit just under the 0.05 cut.
7. The registered verdict ("ok", the 8-turn closed-loop cold floor) is then a mix of thermal states that REG-8's sweep (no reruns) does not have. E0's R inherits it through f8.
- **Separating evidence:**
  - each launch's pre-launch GPU temperature, already in the attempt records (an allowed read);
  - after the result, each saturated row's busy SM-clock mean from `gpu.jsonl`, which is not registered.
- Reporting both is DE-O2.

**Trace B (DC1's guard fails through the playbook)**
1. E1 ends `QUEUE DONE`. REG-21's first [RESULT] is in the log, so `e1.report`'s code wait is met.
2. RUNBOOK §5's E1 row, as the approval commit leaves it, names `AFTERSHOCK_UNSEAL=E1 uv run python -m analysis.e1 floor` as the registered computation, with no wait.
3. A later session follows the playbook, and the floor is printed before E0's [REG].
4. E0's gate factor is then chosen with f8 known: rule A5 is broken for E0's gate. E0 can no longer use E1's floor without a [CORR], and E1 (2.1 GPU h) may have to be rerun to give E0 a blind input.
- **DE1** closes the text gap. DE-O1 would make it mechanical.

## 6. Strongest alternative explanation of E1's likely outcome

**The likely outcome:** status "ok", with a floor of 1.70–1.80 req/s, above REG-8's 1.681 (the draft's prediction).

**The alternative.** The whole gap is counting, not capacity: closed loop serves early, shorter turns first, so the same token work completes more requests.
- REG-21's batch 1 measured this on cold, backlogged cache-on runs (decisions.md 2026-11-13 [RESULT] REG-21 batch 1, FILE(docs/decisions.md:16421); its figures as in docs/status.md, from RUN(the 13 burst runs, k3w.reg21_table)):
  - a completion rate of 1.720–1.798 req/s against 1.681;
  - a mean served prompt of 2931–3067 tokens against the planned 3072;
  - a token-work ratio r with median 1.021.
- 1.681 × 3072 / 2950 = 1.750 (DERIVED). That is the centre of E1's predicted floor, with no change in capacity.
- E1's floor in req/s would then carry the 8-turn served mix, and the 16-turn sweep would carry a different one. So part of E0's R would measure counting, not the cost gap K2 is about.

**Other explanations**
- The day and harness difference against REG-8 ("Confounds, named").
- Trace A's thermal composition.

**Separating evidence**
- U per saturated row (`e1.work_rates`, reported) against REG-8's.
- U ÷ throughput, which with caching off is the mean served prompt (DERIVED from two reported numbers). DE-O2 asks the [RESULT] to state it.
- Equal U with a higher req/s floor means counting.

## 7. Can the run change any decision?

**Yes:**
1. E0's gate, through f8, once E0's [REG] exists. Without a floor the committed label is "missing": no 16-turn matrix (FILE(analysis/k2.py:94-95,102-103)).
2. Through the validity record, whether any registration may run on `5ee6e38`'s harness.
3. K2's wording and the closed-loop margins.
4. Not an inference, but under the lead's rule E1's start sets when REG-20 arm A can start.

**Worth 2.1 GPU h:** yes. It is K2's 8-turn reference, which the owner's plan requires, and the first GPU use of the A14 harness. The GPU is idle.

## 8. Required items

**DE1 (stricter rule and reporting duty; text, in the approval commit). DC1's wait where the playbook names the command.**

(i) In `agent/RUNBOOK.md` §5, this replaces draft 7's (c) and round 2's DC4 row. Anchor (FILE(agent/RUNBOOK.md:66); one occurrence):
```text
| 4 | E1 | `uv run python -m harness.run configs/sweep_l1pl350cl_pc_off.yaml` (one invocation; rerun configs list one rate, same `name`) | `AFTERSHOCK_UNSEAL=E1 uv run python -m analysis.e1 floor` | [RESULT] E1 |
```
Replace with:
```text
| 2b (with 2a) | E1 (E1 and REG-20 arm A: whichever has its ops approved first runs first; the other launches only after the first's end entry; decisions.md [REG] E1, "E1 holds the VM") | `docs/probe/20261113_e1/ops/queue.sh` (its README, "Run order"): the sweep `configs/sweep_l1pl350cl_pc_off.yaml` once; a rate never started, or a rerun, from its single-rate config (same `name`) | `AFTERSHOCK_UNSEAL=E1 uv run python -m analysis.e1 floor`, once, only after REG-21's first [RESULT] (met) and after E0's [REG] is committed or an entry records that E0's gate takes no input from E1's runs; before then no part of E1's floor is computed, quoted or used (no `e1.observed`, `e1.floor_status` or `k2.observed` on E1's runs; decisions.md [REG] E1, "Result, computed once") | [RESULT] E1 |
```

(ii) In the draft's section "RUNBOOK, for the approval commit": replace the block under "(c)" (from `In `agent/RUNBOOK.md` §5's table, replace` to the closing parenthesis about row 2a) with (i)'s anchor and replacement, and keep the sentence "Row 2a, REG-20 arm A, is not edited here: the same rule belongs in REG-20's ops decision, which is in review."

(iii) Reporting duty: the approval commit's `docs/status.md` next action, and every status update until E1's [RESULT], states: "E1's floor is not computed before E0's [REG] is committed or an entry records that E0's gate takes no input from E1's runs."

**DE2 (wording; RUNBOOK text in the approval commit). DD10 (a) and (b) as written force E1 first, and (b) collides with REG-20's RB6.**
- **Why.**
  - (a) says §4 deploys happen "never while E1 has not ended", which is true before E1 starts. REG-20's VM step begins with "push main to the VM's bare repo (RUNBOOK §4 step 1)" (FILE(docs/drafts/reg20_ops_decision_draft2.md:421)).
  - (b) makes item 6's deploy wait "once E1 has ended".
  - Both contradict "whichever has its ops approved first runs first".
  - (b)'s anchor, `then deploy HEAD (§4); then` (FILE(agent/RUNBOOK.md:48)), is the one REG-20 ops draft 2's RB6 replaces (FILE(docs/drafts/reg20_ops_decision_draft2.md:418)), so whichever commit lands second fails to apply.
- **Text.** In draft 7's section "RUNBOOK, for the approval commit", replace its first paragraph (from `The owner-proxy's DD10 applies draft 6's merged proposal, (a) and (b), verbatim` to `which this draft replaces by the lead's rule:`) with:
```text
In place of DD10's (a) and (b) (draft 6's merged proposal, which put E1 first), the approval commit makes one edit, (a), and leaves FILE(agent/RUNBOOK.md:48) to REG-20's ops decision (its RB6 edits that line). (a) In `agent/RUNBOOK.md`, replace `## 4. Deploying `main` to the VM (only between items, never during a run, never before REG-19's [RESULT])` (FILE(agent/RUNBOOK.md:50)) with `## 4. Deploying `main` to the VM (only between items, never during a run, never before REG-19's [RESULT]; never while E1 holds the VM, that is from E1's `docs/probe/20261113_e1/ops/vm_checkout.sh` until E1's end entry (decisions.md [REG] E1, "E1 holds the VM"), nor while E1's queue lock `docs/probe/20261113_e1/ops/state/queue.lock` exists; E1 moves the VM only with its own `vm_checkout.sh`, to E1's commit, detached: decisions.md, [DECISION] (delegate) E1 approved; if the VM is at E1's commit, detached, `git checkout main` comes first)`. This holds under either order: before E1's `vm_checkout.sh`, and after E1's end entry, §4 is as before. Round 2's DC4 adds a §5 row, (c), replaced by the lead's rule:
```
- The owner-proxy's next pass restates DD10 with this text, or rules otherwise.

**DE3 (stricter rule and reporting duty; text). The order rule's terms, which the scripts cannot check.**
- Anchor (in "E1 holds the VM"; one occurrence):
  ```text
  The approval commit amends RUNBOOK §5's order to match: E1 and REG-20 arm A: whichever has its ops approved first runs first; the other launches only after the first's end entry ([OPS] … the queue ended …, or … ended by a stop …). If REG-20 arm A runs first, E1's `vm_checkout.sh` is not run, and E1's queue is not started, before REG-20's end entry; E1's scripts do not read REG-20's entries, so this is kept by hand (E1's pre-launch checks still refuse a launch while a compute process is on the GPU or the VM's tree is not E1's commit, "Pre-launch and launch").
  ```
- Replace with:
  ```text
  The approval commit amends RUNBOOK §5's order to match: E1 and REG-20 arm A: whichever has its ops approved first runs first; the other launches only after the first's end entry. "Approved first" is read from the committed `docs/decisions.md`: the earlier line of E1's approval heading (`[DECISION] (owner|delegate) E1 approved`) and of the heading of REG-20 arm A's operations decision. E1's end entry is one of the three headings above. REG-20 arm A's end entry, for this rule, is REG-20's [RESULT] heading, or an [OPS] entry that quotes REG-20's `QUEUE DONE` line or records a stop of REG-20 that an entry has decided ends arm A, or the end heading REG-20's ops decision names, if it names one. If REG-20 arm A runs first, E1's `vm_checkout.sh` is not run, and E1's queue is not started, before REG-20's end entry; E1's scripts do not read REG-20's entries, so this is kept by hand, and the [OPS] entry that commits `vm_checkout.sh`'s output quotes `git grep -n` of that end entry's heading at the Mac's HEAD (E1's pre-launch checks still refuse a launch while the tmux session `run` exists, a compute process is on the GPU or the VM's tree is not E1's commit, "Pre-launch and launch"). If E1 runs first, REG-20's scripts do not read E1's entries either (rule F e1_r2, DC4), so the approving decision asks that REG-20's ops decision carry this rule's other side, and until it does REG-20 arm A is not launched before E1's end entry, by hand.
  ```

**DE4 (reporting duty; the registration commit). DD12's "leaves `docs/probe/20261113_e1/ops/` as it is at 97a6438" is replaced.**
- **Why.** As written, DD12 would register draft 6's scripts: `mac_checks` freezes the six scripts at the registered commit (FILE(docs/probe/20261113_e1/ops/common.sh:92)). Meanwhile the entry cites `common.sh:24,267-269` and `:224-226` "after draft 7's script patch", and R2 says `settle` writes the pause.
- **Text**, for the approving [DECISION]'s steps (beside DD7) and the commit:
  ```text
  The commit that holds the [REG] and the approval also applies `docs/drafts/e1_r3/ops_draft7.patch` (`git apply`, after `git apply --check`), so that `docs/probe/20261113_e1/ops/` holds `common.sh` 1dff7875947d23c84eeb3fd745446741f5603ed02910db19855665efc63cf237, `queue.sh` d727e0069595b650f3814383c1a31f6594da6599c9a293ccaa5b951ea7415f7c, `vm_checkout.sh` 1fff3e488e8c03ffecb9d62323d0d8c2df0eef9ab07c8b0368b9240293b83c2d, `test_sandbox.sh` dddb31361ac95eee21fbb2ac71a9c429e1011c8da1d3d9510e7f4a4073427a10 and `README.md` 9eb497129e7cf1c958a4b169da9df1554a39e8204c76a4e3cad584698871eedd (sha256; the bundle e1_r3's `ops/` copies), with `vm_state.py`, `session_probe.sh`, `launch.sh`, `DESIGN_NOTES.md` and `e1_commit.txt` (`UNSET`) unchanged. Before that commit, `TMPDIR=<a scratchpad> zsh docs/probe/20261113_e1/ops/test_sandbox.sh` is run on the applied files and must print `passed 192, failed 0`; its output is saved as `docs/probe/20261113_e1/ops/sandbox_<stamp>.txt` and committed in the same commit. DD12's path list gains these six files; the rest of DD12 stands (named paths only; nothing under `runs/`, `docs/probe/20261113_reg19/` or `docs/probe/20261113_e1/ops/state/`).
  ```

**DE5 (wording). The rule-A1 sentence rests on the owner's premise that DC1 corrected.**
- Anchor (one occurrence):
  ```text
  and the owner sent E1 to review with this paragraph's content stated (FILE(docs/decisions.md:4520)).
  ```
- Replace with:
  ```text
  and the owner sent E1 to review on draft 4's statement that "E1 changes no decision about a shock matrix" (FILE(docs/decisions.md:4520)). Rule F round 2 found that statement false (DC1), so this registration rests on the owner's two choices above and on the delegation (FILE(docs/decisions.md:4233)), not on that premise. Its departure from the plan's order, E1 run before E0's [REG] ("E0 … registers … the gate factor before any sweep", FILE(docs/decisions.md:4040)), is the delegate's, made under DC1's guard; the approving entry states it among its notes for the owner, who may reverse it with one entry.
  ```
- Note: after this replacement, the sentence before the anchor ("Rule A1 and `docs/process.md` §3 say a run whose outcomes change no decision is not proposed. The owner has decided otherwise for this run: …") still stands as history. E1 now does change a decision, so A1 is also met directly.

**DE6 (wording). The VM's starting commit is not necessarily `a7bb77a`.**
- **(a)** ID line. Anchor:
  ```text
  **The VM then leaves REG-19's pin** `a7bb77a` for this entry's commit (`vm_checkout.sh`), or, if REG-20 arm A runs first ("E1 holds the VM"), the commit REG-20 left it at;
  ```
  Replace with:
  ```text
  **The VM then moves to this entry's commit** (`vm_checkout.sh`) from the commit it is at: REG-19's pin `a7bb77a`; HEAD of the day, if RUNBOOK §3 item 6's deploy (§4) ran after REG-19's [RESULT]; or, if REG-20 arm A runs first ("E1 holds the VM"), the commit REG-20 left it at; `vm_checkout.sh`'s probe file records which (its `before` line);
  ```
- **(b)** Anchor:
  ```text
  R6: this is the first move of the VM off `a7bb77a` since REG-19 began (the ID line), unless REG-20 arm A runs first ("E1 holds the VM").
  ```
  Replace with:
  ```text
  R6: this may be the first move of the VM off `a7bb77a` since REG-19 began (the ID line); it is not if RUNBOOK §3 item 6's deploy of HEAD, or REG-20 arm A ("E1 holds the VM"), moved it first. Either way `vm_checkout.sh` moves it only from an ancestor of E1's commit, and its probe file records the commit it starts from.
  ```
- **(c)** Anchor:
  ```text
  The VM moves from `a7bb77a` (or from REG-20 arm A's commit, if that runs first: "E1 holds the VM") to the registered commit by `vm_checkout.sh`
  ```
  Replace with:
  ```text
  The VM moves from the commit it is at (`a7bb77a`, HEAD deployed under RUNBOOK §3 item 6, or REG-20 arm A's commit if that runs first: "E1 holds the VM"; it must be an ancestor of the registered commit) to the registered commit by `vm_checkout.sh`
  ```
- **(d)** `docs/probe/20261113_e1/ops/README.md`, in the registration commit after DE4's patch. README is not among the frozen scripts.
  - Anchor:
    ```text
    | `vm_checkout.sh` | The owner-approved step that moves the VM's tree from REG-19's pin to the registered commit. No other script changes the VM's tree. |
    ```
  - Replace with:
    ```text
    | `vm_checkout.sh` | The owner-approved step that moves the VM's tree to the registered commit, from the commit it is at, which must be an ancestor (REG-19's pin, HEAD deployed after REG-19's [RESULT], or REG-20 arm A's commit; its line 2 still says "from REG-19's pin", a comment in a frozen script). No other script changes the VM's tree. |
    ```
  - After this edit, README's sha256 differs from DE4's value. DE4's README hash is then replaced by that of this edited file, stated in the approving entry.

**DE7 (wording). Two meanings of "E1 has ended" (found 4).**
- Anchor (in "In neither case"; one occurrence):
  ```text
  After E1's queue has ended (it printed `QUEUE DONE` or `QUEUE END`, or stopped on a rule that ends E1: `no_errors` or `power_limit` in a run's `failed`, a second `gpu_steady`, one check in `failed` of two runs, or the owner's halt), and only for the runs that have that check in `failed`,
  ```
- Replace with:
  ```text
  After E1's queue has printed `QUEUE DONE` or `QUEUE END`, or has stopped on one of these rules: `no_errors` or `power_limit` in a run's `failed`, a second `gpu_steady`, one check in `failed` of two runs, or the owner's halt (each such stop waits for a decision and is E1's end only once an entry says so, "E1 holds the VM"; these reads may inform that decision and may be made before it), and only for the runs that have that check in `failed`,
  ```
- This is DD6(a)'s sentence, so the owner-proxy confirms it. It widens nothing: the same stops and the same fields.

## 9. Optional items

**DE-O1 (code; a mechanical guard for DC1).** Patches in `rulef-e1-r3_files/`:
- `DEO1_withheld.patch` (sha256 1c1c8c1a…): adds after E1's SEALS row
  ```text
  ("E1-after-E0", "*_sweep_l1pl350cl_pc_off_r*", "[OPS] E1: the floor may be computed"),
  ```
  with a comment.
- `DEO1_test_withheld.patch` (cf7da521…):
  - `test_e1_seal_lifts_alone` also writes the [OPS] heading;
  - a new test, `test_e1_floor_waits_for_e0_even_when_unsealed`: with `AFTERSHOCK_UNSEAL=E1`, the folders stay sealed until that heading exists. E0's [REG] heading alone, or a quote of the heading, lifts nothing.

Results:
- `tests/test_withheld.py tests/test_e1.py tests/test_k2.py`: 40 passed in my scratch copy.
- `git apply --check` passes on the main checkout (nothing applied).

How it would be used:
- The agent writes `## <date> · [OPS] E1: the floor may be computed (…)`, quoting E0's [REG] heading or the entry that frees E1's floor, before the registered command. Like REG-19's queue-end gate, it is a recorded act.
- It covers `e1.observed`, `e1.floor_status`, `k2.observed` and the worktree computation, because it acts at `load` level.
- The entry already allows SEALS rows after the registered commit ("Result, computed once"), and `tests/` is outside `e1.py`'s closure. So it can land in the registration commit or in any commit before E1's first `COPIED` line.

Side effects to state if taken:
- Before the heading exists, `e1.observed` raises with "set AFTERSHOCK_UNSEAL=E1" even when the variable is set. The stderr line names the seal `E1-after-E0`.
- `k2.observed` would get no E1 rows and return "missing" without an error. That is already its behaviour on sealed E1 rows today, and is for E0's registration.

**DE-O2 (reporting duty; Trace A and section 6).** Append to "Reported, never judged":
```text
- For each counted row: whether it came from the sweep or from a later single-rate launch, and that launch's pre-launch GPU temperature (its attempt record); after the result, each saturated row's busy SM-clock mean from `gpu.jsonl`; and U ÷ throughput (with caching off, the mean served prompt, DERIVED from `e1.work_rates` and the row) beside REG-8's rows. None of these is judged; they separate a thermal or a served-mix cause from a capacity cause of any difference from 1.681.
```

**DE-O3 (wording).**
- Anchor:
  ```text
  the queue ends with `QUEUE END`, naming the rates without a valid run ("holes").
  ```
- Replace with:
  ```text
  the queue ends with `QUEUE END`, naming the rates without a valid run (not each of them is a hole of `e1.floor`: "Holes").
  ```

**DE-O4 (wording; DD3's merge).**
- Anchor:
  ```text
  the prediction is computed once, beside the result, with `uv run` before that command, and reported as the tilt's description.
  ```
- Replace with:
  ```text
  the prediction is computed once, beside the result, as `uv run python -c '…'` (the command above with `uv run` in front), and reported as the tilt's description.
  ```

**DE-O5 (reporting duty; found 8).** Append to "Code and tests":
```text
`e1.floor_status`, the flag E2 reads between its sweeps, applies the same holes rule (rule F e1_r2, DC2), and `k2.observed` calls `e1.floor` without the swept rates, so without it (FILE(analysis/k2.py:179)); E2's and E0's registrations cite both.
```

**DE-O6 (widens a read; the owner-proxy must pass it).**
- Why: under DC-O2, a launch log with no `run_id` line can only be diagnosed by lines that the allowed reads exclude.
- Append to "Reads allowed while diagnosing a stop":
  ```text
  A launch log that holds no `run_id` line may be read in full while the VM lists no E1 folder that no settled log names (no run was made, so it holds no outcome); the read is quoted in the [OPS] entry that records the cause.
  ```

## 10. Verdict

**READY**, provided DE1–DE7 are applied verbatim.

Each required item, with its class:

| Item | Class |
|---|---|
| DE1 | stricter rule and reporting duty |
| DE2 | wording |
| DE3 | stricter rule and reporting duty |
| DE4 | reporting duty |
| DE5 | wording |
| DE6 | wording |
| DE7 | wording |

DC1 is met in text, and DC2 in text and code. No required item is code.

The owner-proxy's next pass, already due for DC2, DC-O1 and DC-O2, must restate DD10 (DE2, DE1 (ii)) and DD12 (DE4), and confirm DD6(a)'s wording (DE7).
