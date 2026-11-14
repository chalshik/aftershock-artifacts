# proxy-e1-draft7 (owner-proxy, round 3 on E1 draft 7, bundle e1_r3), verbatim

Saved by the agent at 2026-11-14 01:41 UTC from the reviewer's own verdict file (an in-process subagent of session 8c5f8396; scratchpad `reviews_r3/proxy-e1-draft7.md`, 32486 bytes, sha256 5a3fbe615a46182f045bda3dc55c2249e6870c8a27c8eb3d9d6fdf1fe65eab3c, checked on copy; the reviewer's hand-back message named the same sha256). The reviewer's report follows the line '---' unchanged.

---
# Owner-proxy on E1 draft 7 (review round 3, bundle e1_r3): a delta on the round-2 pass (DD1–DD12)

**Verdict: APPROVE, on conditions DF1–DF11.**
- **BEFORE:** DF1–DF8 are applied before the `[REG] E1` entry is appended. DF8's files are committed with the entry.
- **LATER:** DF9–DF11 go into the approving `[DECISION] (delegate) E1 approved` and its commit.
- **What stands from round 2:** DD9 (the two checks at the registered commit) and DD11 (the ledger row) stand as given. DD1–DD8, DD10 and DD12 are met or replaced as follows:
  - DD1, DD2, DD4 and DD6(a): met (checked by script).
  - DD3: met, merged into DC6 (accepted).
  - DD5: not applied (accepted, point 1).
  - DD6(b): met, merged into DC5 (accepted).
  - DD7: replaced by DF8.
  - DD8: replaced by DF9.
  - DD10: replaced by DF7 and DF11.
  - DD12: replaced by DF10.
- **Rule F round 3 must still return READY** (the delegation's condition (a); FILE(docs/decisions.md:4234)). If it does not, §4 says which of its items need another pass from me.
- **Sentences round 3 changes first.** If round 3 changes a sentence that a DF anchors on, apply round 3's words first. Then append the DF's added sentences after them, unless the two contradict. A contradiction comes back to me.
- **No new rule F code round is needed for these conditions.** None of DF1–DF11 changes code, a threshold, a config or a check:
  - DF3 narrows when a second GPU item may start.
  - DF4 adds an audit duty to an existing wait.
  - DF8 and DF10 are procedure.
  - The rest are wording and disclosures.

## What I checked (0 GPU h; nothing written in the repository)
- **Delegation and owner entries.** Read: FILE(docs/decisions.md:4231-4238) (the delegation), 4516–4520 (the owner sends E1 to review), 4037–4045 (K2 staged) and 4166 (REG-20 approved). Also every heading draft 7 newly cites: 4611, 16322, 16421, 16517, 16571 and 16798, each equal to `decisions_headings_cited.txt`.
- **Bundle.**
  - `shasum -a 256 -c MANIFEST.txt`: every line OK (50 files).
  - Read: BUNDLE_NOTE.md, `e1_draft7_itemmap.md`, `rulef-e1-draft6-r2.md`, `proxy-e1-draft6.md`, and draft 7 lines 1–78 and 805–868.
  - Word diff of draft 6's entry (lines 1–76) against draft 7's (lines 1–78): 99 hunks, each matched to an item-map row or to departure 1, 2, 3 or 9.
- **HEAD.**
  - HEAD is now `f43a5a1`; the bundle was built at `3c8e5dc`, an ancestor (`git merge-base --is-ancestor`).
  - `git diff --stat 3c8e5dc HEAD` over `analysis tests harness configs agent/RUNBOOK.md docs/probe/20261113_e1 docs/experiment-plan.md docs/claims.md pyproject.toml uv.lock` is empty.
  - DA11's `git diff --quiet 9e249b1 HEAD -- <its list>` exits 0.
  - `closure.py --at HEAD analysis/e1.py`: 24 .py files plus `.python-version`, `pyproject.toml`, `uv.lock`. `analysis/withheld.py` is among them.
  - The configs `sweep_l1pl350cl_pc_off.yaml` and `…_only_r1.5.yaml` equal the bundle's.
  - `ls runs | grep -c _sweep_l1pl350cl_pc_off_r` is 0 (names only): no E1 folder yet.
- **Code, in a scratch copy** (`git archive HEAD analysis harness configs tests tools pyproject.toml docs/probe/20261113_e1/ops docs/probe/20261113_freeze`, no `runs/`).
  - All three patches apply.
  - `analysis/e1.py` is `428771e04a7a…` and `tests/test_e1.py` is `dd3f52c579…`. All ten ops files are byte-equal to the bundle's `ops/`, and `e1_commit.txt` reads `UNSET`.
  - With the repo's `.venv` interpreter, importing from the copy:
    - `tests/test_e1.py -k 'not observed'`: 15 passed, 1 deselected;
    - `tests/test_withheld.py`: 14 passed.
  - On the main checkout, `git apply --check` of the three patches passes. Nothing was applied.
- **Sandbox, in the scratch copy.** `TMPDIR=<my scratchpad> zsh …/test_sandbox.sh`: exit 0, `passed 192, failed 0`.
  - The DC-O1 cases pass: the restart still pauses, and no rerun runs before the pause.
  - So do the DC-O2 cases: two launches that name no run stop E1, and there is no third attempt.
  - `git status --short` of the main checkout was the same before and after.
- **DC2's code (I rule on "holes", round-2 §3).** I read the patched `floor` and `floor_tail`.
  - `lo = -inf` when no valid row lies below λ_sat.
  - `have` counts only rows with every value finite, as `cold_floor` reads them.
  - This is the fix my round-2 N8 named. In the cases I traced (§2, point 1), more valid runs never turn a floor into "holes".
- **Verbatim, by script against round 2's text** (draft 7):
  - DD1: the quote at L451–805, unquoted, equals `rulef-e1-draft6-r2.md` byte for byte (355 lines).
  - Verbatim as given: DD4; DD6(a) (once, in the entry); DD6(b)'s appended part; DD2's anchor sentence.
  - Round 2's texts: DC1(a), DC2, DC3, DC5 (both anchors), DC6, DC7, DC-O2, DC-O5, and DC4's bullet up to "… or under an owner's entry.".
- **REG-20 arm A beside E1.**
  - `docs/drafts/reg20_ops_decision_draft2.md`, lines 22–31 and a grep: no mention of E1.
  - Its pin is `1cface7`, an ancestor of HEAD.
  - Its scripts start only after three headings, the second being the owner's rulings. Its `owner_rulings.txt` holds six of them (2a, 6, 7, 8, 9, 16), all `unset` (FILE(docs/drafts/review_bundles/reg20_ops_r2/ops/owner_rulings.txt)).
  - `k1.py`'s closure at HEAD (19 .py files) holds neither `e1.py` nor `k2.py`. REG-20's `JUDGED` list (FILE(docs/drafts/review_bundles/reg20_ops_r2/ops/common.sh:53)) does not hold `e1.py`. E1's commit touches neither `load.py` nor `withheld.py` (REG-20's seal blobs).
  - So E1's registration commit does not trip REG-20's start checks.
- **E1's scripts.**
  - `vm_checkout.sh` (bundle) moves the VM from any ancestor of E1's commit (line 33), so a start at `1cface7` is a forward move.
  - `common.sh` lines 36–41: `SCRIPTS` holds six scripts, and README is not among them.
  - `common.sh` lines 192, 213, 268 and 270: DC-O2's counter and stop.
- **The seal (point 4).**
  - FILE(analysis/withheld.py:30): E1's seal is lifted by `[RESULT] E1` or by `AFTERSHOCK_UNSEAL` naming E1.
  - `load.find_runs` passes every folder through `withheld.keep` (FILE(analysis/load.py:42)).
  - `k2.observed` reads `off_8` with `e1.floor(sweep_rows(...))` and no swept rates (FILE(analysis/k2.py:179)).
- **RUNBOOK at HEAD.**
  - Line 48 holds `then deploy HEAD (§4); then`, and line 50 is the §4 heading.
  - Line 66 is the E1 row; `| 4 | E1 |` occurs once.
  - The draft-6 item map's proposal (a) and (b) was read in full.
- **Freezes.** No registration in force freezes `analysis/e1.py` or `tests/test_e1.py`. The only [REG] headings after line 4500 are REG-22 (4616) and REG-21 (9731), and both batch 2s are computed. REG-24 draft 1's patch touches `analysis/confirm.py`, two configs and `tests/test_confirm.py` only.
- **Not opened:** any `runs/` folder (names only, one count); any `state/` content; RESUME.md; `docs/paper/`; the backups folder; REG-20's gate value; queue outputs; launch logs.
- **Not run:** `k2.observed`, `k1.reg20_table`, any `k3.reg21_*`, `analysis.*` commands, the full pytest, `check_docs.py`. No VM, GPU or ssh.
- **My error (rule A6).** The barred list includes `e1.observed`, and I deselected only the test whose name contains "observed". `test_report_counts_only_the_runs_first_valid_keeps` calls `E.report()` with `withheld.lifted` patched to True, and `report()` calls `observed()` (scratch `analysis/e1.py:250`). So `e1.observed` ran once, inside that test, in the scratch copy. Its rows were synthetic: `sweep_rows`, `swept_rates` and `_kbar` were monkeypatched, and the copy has no `runs/`. No run folder was read. I should have read `report()` before running the tests.

## 1. Would the owner approve E1 as draft 7 writes it, with DF1–DF11?
**Yes.**
- **The run's value is unchanged from draft 6.** It is K2's 8-turn reference: the owner decided it "is run in any case" (FILE(docs/decisions.md:4037)). It is also the first GPU check of the harness after `5ee6e38`.
- **Cost:** about 2.1 GPU h, with a ceiling of 6.3 h, and the GPU is idle. The owner said "whenever its available use it" (FILE(docs/decisions.md:4506)) and "we cant affort just letting be idle" (quoted in this pass's brief).
- **Every change since draft 6 makes the run stricter or the text truer:**
  - DC1 states that E1 feeds E0's gate and withholds the floor until E0's [REG].
  - DC2 closes the "holes" case that round 2 and my N8 found.
  - DC3 limits the worktree's links.
  - DC5 completes the readable fields and discloses the bit they carry.
  - DC-O1 closes the pause gap, and DC-O2 stops launches that make no run.
  - DC-O4 protects the VM copies.
  - DC-O5 covers a withdrawn REG-21.
- **Two places where the owner's intent needs the text tightened:**
  - The order rule could idle the GPU (DF3).
  - The owner's own entry on E1 rested on a statement now known false (DF5).
- **No harm to other items.**
  - REG-19, REG-21 and REG-22 have reported.
  - REG-20 arm A's start checks are not touched (see "What I checked").
  - REG-24 shares no file with E1.

## 2. The five points

**Point 1. DD5 not applied: accepted.**
- DD5 disclosed a case ("1.5 and 2.0 both without a valid run" gives a floor from λ_sat). DC2's code removes that case: `test_a_hole_just_below_lam_sat_is_a_hole` now asserts "holes" with `missing_rates == [1.5, 2.0]`. So DD5's text would be false.
- DC2 is the code fix my round-2 N8 named as the alternative.
- My ruling on DC2's "holes" (round-2 §3): approved.
  - Traced: 1.5 valid and kept up with 2.0 missing gives "holes" [2.0]. With 1.5 missing as well, it gives "holes" [1.5, 2.0]. With 2.0 valid and unsaturated and 1.5 missing, it gives "ok": λ_sat cannot lie at 1.5 then, and the floor's rows do not depend on 1.5.
  - In none of these does a missing run turn "holes" into a floor.
  - The cost: no floor whenever 1.5 has no valid run and no valid row lies below λ_sat. Outside a stop, that needs three failures at 1.5. Inside a `MAX_SAME` stop on the first two rates, the harness is suspect anyway (DA7).
  - The NaN-row clause (`have` from finite rows) is right: a row `cold_floor` drops is not data.
- **E2 inherits this rule** through `floor_status`. E2's registration must cite it (my N9; round 2 DC2).

**Point 2. DD7 and DD12 restated: done as DF8 and DF10.**
- DD7's hashes are now draft 7's. The ops patch is applied in the same step, with all five changed ops files pinned by sha256.
- The sandbox is rerun in the repo and its output committed.
- DD7's clause "never while REG-19's `final.sh` is running" is replaced. REG-19 is finished. REG-20's draft scripts compare `analysis/` with HEAD (FILE(docs/drafts/review_bundles/reg20_ops_r2/ops/common.sh:495)), which is the same kind of guard that stopped REG-19's queue at 21:38 UTC on 2026-11-13.
- DD12's path list gains the five ops files and the sandbox output. Its exclusions gain REG-20's probe folders.

**Point 3. "Whichever has its ops approved first runs first", kept by hand on both sides: acceptable only as DF3 defines it.**
- **As written, it can idle the GPU.** REG-20 arm A's scripts start only after three headings, and the second is the owner's six rulings (FILE(docs/drafts/reg20_ops_decision_draft2.md:24-29)). The owner is away.
  - "Ops approved" can be read as the delegate's REG-20 operations decision (heading 1).
  - Read that way, a REG-20 delegate decision committed before E1's approval makes REG-20 "first". E1 would then wait for REG-20's end entry, and REG-20 cannot start until the owner returns.
  - That is the idle GPU the owner refuses.
- **DF3 makes "first" mean "able to start first":** every entry the item's scripts require before their first launch is committed. E1's approving decision records which item is first, from `git grep` at its commit.
  - Today that is E1: REG-20's owner rulings are unset.
- **"Launches" also covers the VM.** The second item may not move the VM's tree. REG-20's README moves the VM by hand to `1cface7`; done during one of E1's pauses, that move would interleave the two items. DC4 was written to stop exactly that.
- **By hand on both sides is acceptable** for these reasons:
  - E1's side is backed by its pre-launch checks: no compute process, and the tree must be E1's commit.
  - REG-20's start needs the owner's rulings, so the owner can see the order then.
  - The owner can reorder by one entry.
- **The owner would not accept a rule whose other half does not exist.** REG-20's ops draft 2 does not mention E1. DF9(g) makes E1's approval say so, and requires REG-20's operations decision to carry the wait when E1 is first. That requirement belongs to REG-20's review; E1's [REG] already forbids another registration's launch until E1's end entry.

**Point 4. DC1's guard is text only: acceptable, with DF4 and the RUNBOOK cell of DF7(d).**
- **The guard is not text alone.**
  - E1's folders are sealed in code until `[RESULT] E1` (FILE(analysis/withheld.py:30)).
  - `load.load_run` refuses them. `load.find_runs` (FILE(analysis/load.py:42)), `recheck.recheck`, `tables.arrival_table` and `engine_config.scan` skip them (decisions.md 2026-11-13 [DECISION] "A17 answered … analysis code now refuses run folders …"). So `k2.observed`, which reads them through `sweep_rows`, sees none of them.
  - Only a command that sets `AFTERSHOCK_UNSEAL=E1` can read them. What the text adds is a rule on when that deliberate command may be typed.
  - A premature run of it would also fall outside the delegation: it reads outcome data a pending registration withholds (FILE(docs/decisions.md:4235)).
- **A code refusal keyed on E0's [REG] would need another code round** in `e1.py` or `withheld.py`, both in `e1.py`'s closure, plus a test change, before registration. That would delay a 2.1 h run for a guard that bears only on when the result is computed.
- **Two weak points, both fixed in text:**
  - RUNBOOK's E1 row shows the result command with no E0 wait (FILE(agent/RUNBOOK.md:66)). Draft 7's (c) replaces only the row's prefix. DF7(d) adds the wait to that cell.
  - Nothing made a premature command visible. DF4 has the [RESULT] quote `git grep` of E0's [REG] heading and state that no earlier command set the variable.
- **The way out of the wait needs its own review.** "An entry records that E0's gate takes no input from E1's runs" would change K2's staged test (FILE(docs/claims.md:56)). DF4 says it needs its own rule F review and owner-proxy pass, so the wait cannot be lifted by a bare entry.

**Point 5. What the owner would not approve as written.**
- **(a) The order rule's ambiguity:** point 3, fixed by DF3.
- **(b) A premise of the owner's entry is false.**
  - The owner sent E1 to review with the statement "E1 changes no decision about a shock matrix, as its own draft says first" (FILE(docs/decisions.md:4520)). DC1 found that false.
  - Draft 7 still says "the owner sent E1 to review with this paragraph's content stated". After DC1 replaced the paragraph, that is false too.
  - The owner would approve the run anyway: it is "run in any case" and "whatever step B finds" (4037, 4040), and the floor is withheld until E0's gate exists.
  - But the owner would want the approval to say what it rests on. DF5 says it, and DF9(f) repeats it in the approving decision.
- **(c) Two meanings of "E1 has ended"** (item-map finding 4).
  - DD6(a) allows the detail reads once a stop line that ends E1 is printed.
  - DC4 ends E1 only by an end entry.
  - DF6 rules that the reads may come before the end entry, because they serve the decision on the stop. They neither end E1 nor free the VM.
  - DC-O2's stop leaves no `checks.json`, so it allows no such read.
- **(d) DD10(b) uses the older end** ("its queue printed QUEUE DONE or QUEUE END"). DF7 aligns it with the end entry.
- **Accepted as written:**
  - item-map departures 2 (REG-19 facts), 3 (renumbered citations), 4 (DD2's text), 5 (DD3 merged into DC6), 7 (DD6(b) merged into DC5) and 9 (the freeze bullet, moot, kept as a record);
  - DC-O1 to DC-O5 taken;
  - item-map findings 6 (`vm_checkout.sh` line 2 says "from REG-19's pin", a comment; line 33 accepts any ancestor), 7 (DESIGN_NOTES.md stale, as README line 3 lists) and 9 (the home path, already throughout the repo).

## 3. Conditions

**DF1 (BEFORE): rule F round 3, verbatim.** Immediately before the line `#### Owner-proxy pass`, insert:
- a section headed `` ### Adversarial review, round 3 (rule F, `docs/process.md` §3), verbatim ``, holding the full text of rule F's round-3 review of draft 7 (bundle e1_r3). Prefix each line with "> ", as rounds 1 and 2 are, and include any header the agent adds when it saves the review;
- then `#### What was changed because of it (round 3)`, item by item, naming every departure from the reviewer's words.

If round 3 is not READY, the entry is not appended.

**DF2 (BEFORE): this pass, named.** Anchor (draft 7, the owner-proxy line):
```text
Draft 7's DC2 ("holes"), DC-O1 and DC-O2 (the scripts; DC-O2 also the stopping rule) need another owner-proxy pass (its §3).
```
Replace with:
```text
Draft 7's DC2 ("holes"), DC-O1 and DC-O2 (the scripts; DC-O2 also the stopping rule) need another owner-proxy pass (its §3). Owner-proxy on draft 7 (round 3; `<path where this verdict is saved>`): **APPROVE on DF1–DF11**; DD5 not applied, DC2's "holes", DC-O1 and DC-O2 accepted; DF1 (rule F round 3, verbatim, above), DF2 (this line), DF3 ("E1 holds the VM"), DF4 and DF5 ("What E1 can and cannot do"), DF6 ("In neither case"), DF7 ("RUNBOOK, for the approval commit") and DF8 (the three patches, applied in this commit, in place of DD7) are applied in this entry; DF9–DF11 belong to the approval commit; DD9 and DD11 stand.
```
Fill the placeholder with the saved file's path.

**DF3 (BEFORE): the order rule, defined.** Anchor (once, in "E1 holds the VM"):
```text
The approval commit amends RUNBOOK §5's order to match: E1 and REG-20 arm A: whichever has its ops approved first runs first; the other launches only after the first's end entry ([OPS] … the queue ended …, or … ended by a stop …).
```
Replace with:
```text
The approval commit amends RUNBOOK §5's order to match: E1 and REG-20 arm A: whichever has its ops approved first runs first; the other launches only after the first's end entry ([OPS] … the queue ended …, or … ended by a stop …). An item's ops are approved when every entry its scripts require before their first launch is committed: for E1, the approving decision after this entry (`[DECISION] (delegate) E1 approved`, or the owner's); for REG-20 arm A, every heading its operations scripts require before their first launch (its operations decision draft 2 names three: the delegate's operations decision, the owner's rulings, and `[DECISION] (owner|delegate) REG-20 arm A starts`). An approval that still waits for an owner's ruling does not make an item first, so the GPU does not wait for an item that cannot start. E1's approving decision states which item is first, from `git grep -n` of those headings at its commit. The second item neither launches, nor moves the VM's tree, nor starts its queue before the first's end entry. An owner's entry may change the order.
```

**DF4 (BEFORE): the A5 guard, made auditable.** Anchor: the **first** occurrence only, in the entry's bullet "What E1 can and cannot do". The second is inside the quoted round-2 review, which stays verbatim.
```text
or before an entry records that E0's gate takes no input from E1's runs.
```
Replace with:
```text
or before an entry records that E0's gate takes no input from E1's runs. This guard is kept by hand on top of the seal: E1's folders are sealed in code until `[RESULT] E1` (FILE(analysis/withheld.py:30)), so only a command that sets `AFTERSHOCK_UNSEAL=E1` reads them, and none is run before then. The [RESULT] quotes `git grep -n` of E0's [REG] heading, or of that entry, at the commit before its first such command, and states that no earlier command set `AFTERSHOCK_UNSEAL=E1`. An entry recording that E0's gate takes no input from E1's runs changes K2's staged test (FILE(docs/claims.md:56)), so it is the owner's, or a [DECISION] (delegate) with its own rule F review and owner-proxy pass.
```

**DF5 (BEFORE): what the approval rests on.** Anchor (once, in the same bullet):
```text
Rule A1 and `docs/process.md` §3 say a run whose outcomes change no decision is not proposed. The owner has decided otherwise for this run: the L1 closed-loop cache-off sweep "is run in any case" (FILE(docs/decisions.md:4037)), "run whatever step B finds" (FILE(docs/decisions.md:4040)), and the owner sent E1 to review with this paragraph's content stated (FILE(docs/decisions.md:4520)).
```
Replace with:
```text
Rule A1 and `docs/process.md` §3 say a run whose outcomes change no decision is not proposed; E1's outcomes change one (above), and the owner has also decided that this run is made in any case: the L1 closed-loop cache-off sweep "is run in any case" (FILE(docs/decisions.md:4037)), "run whatever step B finds" (FILE(docs/decisions.md:4040)). The owner sent E1 to review (FILE(docs/decisions.md:4516)) with the statement, taken from draft 4, that "E1 changes no decision about a shock matrix" (FILE(docs/decisions.md:4520)); rule F round 2 (DC1) found it false. The two decisions to run E1 in any case do not rest on it, and E1's floor is withheld until E0's [REG] (above), so the delegate's approval rests on those two decisions; the owner may overrule it.
```

**DF6 (BEFORE): when the detail reads may be made.** Anchor (once, in "In neither case"):
```text
and the [RESULT] lists every such read.
```
Replace with:
```text
and the [RESULT] lists every such read. These reads may be made once the stop line is printed, before E1's end entry ("E1 holds the VM"): they serve the decision on that stop, and they neither end E1 nor free the VM. A launch whose log names no run (the stopping rule) leaves no `checks.json`, so its stop allows no such read.
```

**DF7 (BEFORE): the [REG]'s section "RUNBOOK, for the approval commit".**

(i) Anchor:
```text
The owner-proxy's DD10 applies draft 6's merged proposal, (a) and (b), verbatim
```
Replace with:
```text
The owner-proxy's DD10 applies draft 6's merged proposal: (a) verbatim, and (b) with one change by the round-3 owner-proxy pass (DF7), its words `once E1 has ended (its queue printed QUEUE DONE or QUEUE END, or a stop that ends E1 is recorded)` reading `once E1's end entry is committed ("E1 holds the VM")`
```

(ii) Anchor (the row inside (c)'s second `text` block):
```text
| 2b (with 2a) | E1 (E1 and REG-20 arm A: whichever has its ops approved first runs first; the other launches only after the first's end entry ([OPS] … the queue ended …, or … ended by a stop …)) |
```
Replace with:
```text
| 2b (with 2a) | E1 (E1 and REG-20 arm A: whichever has its ops approved first, as "E1 holds the VM" in the [REG] E1 entry defines it, runs first; first: <the item E1's approving decision names>; the second neither launches, nor moves the VM's tree, nor starts its queue before the first's end entry ([OPS] … the queue ended …, or … ended by a stop …)) |
```

(iii) After the paragraph that begins `(The row's other cells stay.`, append:
````text
(d) In the same row, replace
```text
`AFTERSHOCK_UNSEAL=E1 uv run python -m analysis.e1 floor` | [RESULT] E1 |
```
with
```text
`AFTERSHOCK_UNSEAL=E1 uv run python -m analysis.e1 floor`, once, only after REG-21's first [RESULT] and after E0's [REG] or the entry that "What E1 can and cannot do" names; no command sets `AFTERSHOCK_UNSEAL=E1` before then | [RESULT] E1 |
```
````

**DF8 (BEFORE; the files are committed with the entry): the three patches, in place of DD7.**
1. In the main checkout, while no queue, launch or final script of any registration runs from it, run:
   `git apply docs/drafts/e1_r3/e1_py_draft7.patch docs/drafts/e1_r3/test_e1_draft7.patch docs/drafts/e1_r3/ops_draft7.patch`
   (REG-20's draft scripts compare `analysis/` with HEAD, FILE(docs/drafts/review_bundles/reg20_ops_r2/ops/common.sh:495).)
2. Check the hashes. `shasum -a 256 analysis/e1.py tests/test_e1.py docs/probe/20261113_e1/ops/common.sh docs/probe/20261113_e1/ops/queue.sh docs/probe/20261113_e1/ops/vm_checkout.sh docs/probe/20261113_e1/ops/test_sandbox.sh docs/probe/20261113_e1/ops/README.md` must print, in order:
   - `428771e04a7a740bc87b20bc7959d835c56e0eebbfb822086248a373c200d415`
   - `dd3f52c579288cbe9a9a0144b98d2b880f2606eacea153fc268d232e6f6a750d`
   - `1dff7875947d23c84eeb3fd745446741f5603ed02910db19855665efc63cf237`
   - `d727e0069595b650f3814383c1a31f6594da6599c9a293ccaa5b951ea7415f7c`
   - `1fff3e488e8c03ffecb9d62323d0d8c2df0eef9ab07c8b0368b9240293b83c2d`
   - `dddb31361ac95eee21fbb2ac71a9c429e1011c8da1d3d9510e7f4a4073427a10`
   - `9eb497129e7cf1c958a4b169da9df1554a39e8204c76a4e3cad584698871eedd`

   Also:
   - `git diff --quiet HEAD -- docs/probe/20261113_e1/ops/vm_state.py docs/probe/20261113_e1/ops/session_probe.sh docs/probe/20261113_e1/ops/launch.sh docs/probe/20261113_e1/ops/DESIGN_NOTES.md docs/probe/20261113_e1/ops/e1_commit.txt` exits 0;
   - `e1_commit.txt` reads `UNSET`.
3. `uv run pytest tests/test_e1.py -q`: 16 passed.
4. `uv run pytest`: passes in full.
5. Run the sandbox:
   - Run `TMPDIR=<the session's scratchpad> zsh docs/probe/20261113_e1/ops/test_sandbox.sh`, with stdout and stderr saved to a file in the scratchpad. It must exit 0, with a last line that starts `passed 192, failed 0`.
   - Copy that file byte for byte to `docs/probe/20261113_e1/ops/sandbox_<UTC stamp>.txt`, and check the copy with `cmp`.
   - `git status --short` then shows no path outside DF10's list.
6. These files go into the registration commit (DF10).

If round 3 changes any of these files, the hashes in step 2 are those of round 3's files, and §4 applies.

**DF9 (LATER): what the approving decision holds, in place of DD8.** DB10 (i)–(iv) stand. In addition, the entry:
- **(a)** carries the three owner-proxy verdicts on E1 verbatim:
  - `docs/drafts/reviews-2026-11-13/proxy-e1-draft5.md`;
  - `docs/drafts/reviews-2026-11-13/proxy-e1-draft6.md`;
  - this pass, as saved.
- **(b)** names rule F rounds 2 and 3, with each verdict and file.
- **(c)** quotes DD8(c)'s two outputs (the closure of `analysis/e1.py` and DA11's `git diff --quiet 9e249b1 … ; echo $?`, which must print 0), run with the registration commit's content staged. It also quotes DF8 step 5's last line. DD9 repeats the two at the registered commit, and the entry says so.
- **(d)** lists the departures accepted:
  - DD8(d)'s list;
  - draft 7's item-map departures 1 (as DF3 defines it), 2, 3, 4, 5, 6 (DD5 not applied), 7, 8 (DD7 replaced by DF8) and 9;
  - DC-O1 to DC-O5 taken.
- **(e)** states the ruling on DA7's detail reads: allowed as DD6 scopes them and as DF6 times them.
- **(f)** states that the owner's 4516 entry rested on a statement DC1 found false, and that this approval rests on FILE(docs/decisions.md:4037) and FILE(docs/decisions.md:4040) (DF5). The owner may overrule it.
- **(g)** states which item is first (DF3), quoting the `git grep -n` output for both items' start headings at the commit.
  - It also says that REG-20 arm A's operations decision draft 2 does not mention E1.
  - While E1 is first, REG-20's operations decision must carry the wait for E1's end entry before its first launch or VM move.
- **(h)** adds to `docs/status.md`'s open risks: "E1's result waits for E0's [REG] (DF4); no command sets `AFTERSHOCK_UNSEAL=E1` before then".

**DF10 (LATER): the registration commit's paths, in place of DD12.**
- The commit that holds the [REG] and the approval is made with named paths only: `git add <path> …`, never `git add -A`, `git add .` or `git commit -a`.
- **Its paths:**
  - `docs/decisions.md`;
  - `analysis/e1.py` and `tests/test_e1.py`;
  - in `docs/probe/20261113_e1/ops/`: `common.sh`, `queue.sh`, `vm_checkout.sh`, `test_sandbox.sh`, `README.md`, and the new `sandbox_<UTC stamp>.txt` from DF8 step 5;
  - `agent/RUNBOOK.md` and `docs/model.md`;
  - the session files: `docs/status.md`, `docs/context-pack.md`, `agent/STATE.md`, `agent/LOG.md`, `agent/FOR_AUTHOR.md`, and the saved reviews under `docs/drafts/reviews-*/`.
- **It adds nothing under** `runs/`, `docs/probe/20261113_reg19/`, `docs/probe/20261113_reg20/`, `docs/probe/reg20/`, or any `docs/probe/**/state/`. It does not add `.gitignore`, `docs/FABLE_PROMPT.md`, or any untracked draft.
- **These stay as at HEAD:** `e1_commit.txt` (`UNSET`), `vm_state.py`, `session_probe.sh`, `launch.sh` and `DESIGN_NOTES.md`. `e1_commit.txt` is set later, by README step 3, and DD9 follows.
- After the commit, `git status --short` lists none of the named paths.

**DF11 (LATER, in the approval commit): RUNBOOK, in place of DD10.**
- Apply the [REG]'s section "RUNBOOK, for the approval commit" to `agent/RUNBOOK.md`, as DF7 leaves it:
  - (a) verbatim;
  - (b) with DF7(i)'s change;
  - (c) with the placeholder filled with the item DF9(g) names;
  - (d).
- The anchors are FILE(agent/RUNBOOK.md:50), FILE(agent/RUNBOOK.md:48) and FILE(agent/RUNBOOK.md:66), all checked at HEAD `f43a5a1`. Each occurs once.

## 4. Later changes that would need another owner-proxy pass
- **Any change to code, comments included:**
  - the six frozen scripts;
  - `analysis/e1.py` beyond DF8's file;
  - `tests/test_e1.py` beyond added tests;
  - `e1_commit.txt` other than by README step 3.

  A code guard for DC1 (in `e1.py` or `withheld.py`) counts too: it needs a rule F code round and this pass.
- **Any round-3 item that changes:**
  - the stopping rule (including DC-O2's stop and `MAX_SAME`);
  - "holes", the floor, the tail fallback, `first_valid` or REG-8's settings;
  - the allowed reads or their timing (DD6, DF6);
  - the start gate, the approval heading, or the order rule beyond wording (DF3);
  - the configs, rates, seed or cost ceiling.
- **An order between E1 and another GPU item** other than DF3's rule or an owner's entry.
- **Reading any E1 run** beyond `valid`, `failed` and DD6's fields before E1's [RESULT]. Any command with `AFTERSHOCK_UNSEAL=E1` before E0's [REG] or the entry DF4 names.
- **A failure of DD9's two checks.** The registration then goes back to rule F, and then to me.
- **No new pass is needed for:**
  - applying DF1–DF11 verbatim;
  - DF2's path and DF7(ii)'s placeholder;
  - renumbered FILE citations;
  - [OPS] entries;
  - round-3 items that are only wording, tags, citations, disclosures or stricter reporting duties.

## 5. Notes for the owner
- **N1. The order rule.** As the lead wrote it, the order could put E1 behind REG-20 arm A, and arm A cannot start without your six rulings. DF3 ties "first" to being able to start. Today E1 is first.
- **N2. REG-20's operations draft 2 does not mention E1.** Its other half of the order rule must be added in its review (DF9(g)).
  - Its pin `1cface7` is an ancestor of E1's commit, so E1's `vm_checkout.sh` can move forward from it.
  - If you rule `pin_head` (its point 2a) and REG-20 runs first at a commit after E1's, `vm_checkout.sh` refuses, and you decide.
- **N3. Your 4516 entry rested on a false statement.** It quoted "E1 changes no decision about a shock matrix", which round 2 found false. E1's floor is the denominator of E0's 8-turn ratio, and without a floor the committed gate says "missing" (FILE(analysis/k2.py:102-103)).
  - This approval rests on your decisions to run E1 in any case (4037, 4040) and on withholding the floor until E0's [REG].
  - You can overrule with one entry.
- **N4. DC1's guard is the seal plus a rule on one command.**
  - The cheapest code guard would be a second `SEALS` row for E1's pattern, lifted by `[REG] E0`. Adding `SEALS` rows is exempt from E1's freeze.
  - It would need a test change in `tests/test_withheld.py` and a rule F code round.
  - It must not be committed while REG-20 arm A runs, because REG-20's queue stops on a `withheld.py` change.
  - Not required here.
- **N5. E2 inherits DC2's stricter "holes"** through `floor_status` (round 2 DC2; my round-2 N9). E2's registration must cite it.
- **N6. DC-O2 and random power-offs.** A power-off during the server's start leaves a launch log with no `run_id`, and two of them stop E1 for a decision.
  - BELIEF: the chance is small. The VM went off twice in about a day (FILE(docs/decisions.md:4383)), and the start-up window is about 60 s per launch.
- **N7. Round 2's N2 and N6 still hold:**
  - 350 W after a reboot needs you, unless a NOPASSWD rule exists;
  - a crash on an unchanged boot id cannot be diagnosed within the allowed reads.
