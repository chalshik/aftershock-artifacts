**Owner-proxy delta, round 3: REG-20 arm A operations decision, draft 3, with rule F round 3's DH items**

**Verdict: APPROVE**, with DL1–DL10 BEFORE the first launch and DL11 LATER.
- **DH1:** the main patch `rulef-reg20-ops-draft3-r3-dh.patch` (a control's floor `CONTROL_MIN_FREE_KB` = 1,048,576 kB). Not the fallback `-dh1alt.patch`.
- **DH2:** verbatim, all seven parts. DL4 adds one sentence after it and changes none of its words.
- **DH-O1, DH-O3, DH-O4:** taken. **DH-O2:** not taken as code. DL6 replaces it with a hand rule.
- **Draft 3's own additions** (the once-only delegate check, `e1_ended`, `vm_checkout.sh`, the RUNBOOK §4 clause): accepted, with DH-O4 and DL6.
- **Point D:** arm A may start after E1's end entry without waiting for the owner to free VM space. This is draft 3's option (b), which DH1 makes safe. Freeing space stays the owner's.
- **My round-2 picks stand:** 2a `setaside`, 6 (b), 7 `lost_open`, 8 (b), 9 (a), 16 (a), G (a).

The delegation needs this pass and rule F's (FILE(docs/decisions.md:4234)). Rule F round 3 is READY provided DH1 and DH2 are applied verbatim (FILE(docs/drafts/reviews-2026-11-13/rulef-reg20-ops-draft3-r3.md:3)). This APPROVE assumes the same.

Reviewer: a separate owner-proxy subagent of session 8c5f8396, 2026-11-14, 0 GPU h.
- No ssh, no VM, no network.
- I edited, staged and committed nothing in the repo. My only file is this one.
- My scratch copies are under `scratchpad/px3/`: `base`, `main`, `alt`, `out` and `tools`.
- Section markers use `###` or bold. No line of this file begins `## `.

### What I read, in order

1. `CLAUDE.md` and the auto-memory, from the session context.
2. `docs/decisions.md:4225-4240`, which holds the delegation at 4231–4237.
3. `docs/drafts/reg20_ops_decision_draft3.md`, whole.
4. `docs/drafts/reviews-2026-11-13/rulef-reg20-ops-draft3-r3.md`, whole.
5. My round 2, `docs/drafts/reviews-2026-11-13/proxy-reg20-ops-draft2.md`, whole.
6. `docs/drafts/reg20_ops_decision_draft3_itemmap.md`, whole.
7. The decisions.md headings from 4502 to the end; the entries at 19394–19458 (E1's checkout and the [OPS] VM disk entry); 17072 and 17076 (E1's stop rule, "E1 holds the VM"); 4045–4105 (REG-20's [REG]); 4166–4172 (its approval).
8. `docs/probe/20261114_vm_disk/disk_20261114T025418Z.txt`; `agent/FOR_AUTHOR.md` −20 (by grep); `docs/drafts/reg20_ops_r3/SHA256SUMS.txt` and `disk_probe_20261114.txt`.
9. The three round-3 patches (`-dh`, `-dh1alt`, `-dho1`), `runbook_heading1.patch` and `owner_rulings_rd2.patch`.
10. In my `main` scratch tree: `launch.sh` whole; `common.sh:1-60` and `:100-182`; `vm_checkout.sh` whole; `session_probe.sh:1-20`; `queue.sh:60-82`; parts of `README.md`; `test_sandbox.sh:1-70`; `test_control_due.py:1-30`.
11. `agent/RUNBOOK.md:18-32`, `:44-70` and `:84`. Also `docs/probe/20261113_reg19/ops_r3/common.sh:10-20`, `docs/probe/20261113_e1/ops/common.sh:1-8,28-40` and E1's `launch.sh` by grep.
12. `agent/bin/vm_verify_list.zsh:1-40`.
13. `git diff -- .gitignore`: the uncommitted change adds `docs/potential_gaps.md` only.
14. Late in the review, the commits after 25ad86e: their subjects and `--stat`, the `agent/FOR_AUTHOR.md` diff of 6992e0e, and the 29 lines that 223ce78 adds to `docs/decisions.md` (E1's end entry, from FILE(docs/decisions.md:19459)).

**Not opened:**
- anything under `runs/`: not listed, not opened, and no name matched against a folder;
- `/Users/chalshik/aftershock-backups/`;
- `docs/probe/20261111_reg19/ops/RESUME.md`;
- `docs/paper/`;
- any `docs/probe/**/state/` folder. `e1_ended` tests E1's lock path for existence, but I ran no script against the real repo;
- `docs/FABLE_PROMPT.md`.

`AFTERSHOCK_UNSEAL` was never set: the one Python test ran under `env -u AFTERSHOCK_UNSEAL`.

**Disclosure (A5).** I know REG-19's outcome, `supports` 5 of 5, from the heading at FILE(docs/decisions.md:16517) and from my round 2.
- I saw no E1 or REG-20 run data.
- Whether a REG-20 open run exists: 0 folders, a BELIEF resting on my round 2's count and rule F round 2's. I did not list `runs/` this time.
- HEAD has no heading that matches the scripts' `STOP_PAT`, `START_PAT` or `RULINGS_PAT`. DERIVED: I sourced the patterns from my `main` tree's `common.sh:45-54` and ran `grep -c -E` over `git show HEAD:docs/decisions.md`, which gave 0.
- At 25ad86e, HEAD had no E1 end entry: `E1_END_PAT` gave 0 (same method). It was committed during this review, in 223ce78 (see "HEAD moved").
- None of the rulings below depends on any outcome.

**HEAD moved during this review,** from 25ad86e through 6992e0e to 223ce78, by other sessions (PROBE: `git log 25ad86e..HEAD`).
- **6992e0e** adds rule F round 2 on REG-24 and restates `agent/FOR_AUTHOR.md` −18.
- **223ce78** adds E1's end entry, `[OPS] E1: the queue ended (QUEUE DONE)`, at FILE(docs/decisions.md:19459). Six runs, one per rate, each on attempt 1 and valid. The queue lock was renamed, so `state/queue.lock` is absent (as that entry states; I did not open E1's `state/`).
  - That entry holds run names, `valid` and `failed` only. I read it, and it holds nothing of E1's floor.
  - HEAD now holds 1 line matching `E1_END_PAT` (PROBE: `grep -c -E`) and still 0 REG-20 arm A rulings, start or operations headings.
- **None of the files reviewed here changed,** apart from that one appended entry. `git diff --stat 25ad86e HEAD` over the ops folder, draft 3, `docs/drafts/reg20_ops_r3/`, rule F round 3 and its files and `agent/RUNBOOK.md` is empty. In `docs/decisions.md` the only change is 29 added lines.
- −20 is still at FILE(agent/FOR_AUTHOR.md:7). DL9's two anchors still occur once each at 6992e0e and in the working tree (PROBE), and 223ce78 does not touch that file.
- `docs/probe/20261114_vm_disk/verify_20261114T041949Z.txt` is untracked, from another session. I did not open it.

**What E1's end changes here.** E1 used six launches, the case draft 3 calls expected. So E1's worst case (18 runs, F1 = 2,886,198 kB) no longer applies, and the expected F1 of about 3,742,914 kB is the relevant row. That rests on the BELIEF that each E1 run is about 71,393 kB. The real figure is the `free_kb` of arm A's session probe (DL8). Nothing launches before heading 1, heading 2, heading 3 and `vm_checkout.sh`.

### Checks I ran (all read-only or in scratch)

- **Input hashes** (PROBE: `shasum -a 256`). Draft 3 is `331ee2f7…`, its item map `25be1a8c…`, `ops_draft3.patch` `31dbea7c…`, `owner_rulings_rd2.patch` `18d0bb21…` and `runbook_heading1.patch` `4e92970e…`, all equal to SHA256SUMS.txt. `-dh.patch` is `c2c6f97f…`, `-dh1alt.patch` `a934fe13…` and `-dho1.patch` `05806c4a…`, equal to rule F's §5–6.
- **No drift since the patches were made.** `git diff --stat 40948ba 25ad86e -- docs/probe/20261113_reg20/ops agent/RUNBOOK.md` is empty (PROBE).
- **Scratch trees.**
  - `base`: `git archive 25ad86e | tar -x`, then `ops_draft3.patch`. All 8 files equal SHA256SUMS.txt group (1) (PROBE).
  - `main`: `base` plus `-dh.patch` plus `-dho1.patch`.
  - `alt`: `base` plus `-dh1alt.patch` plus `-dho1.patch`.
  - Every hunk applied. `patch` left `.orig` backups where `-dho1` met offset hunks.
- **The sandbox, run as the README says** (`zsh docs/probe/20261113_reg20/ops/test_sandbox.sh`, with `TMPDIR` in my scratch):
  - `base`: passed 428, failed 0, exit 0;
  - `main`: **passed 441, failed 0, exit 0** (428 + 2 DH2 + 9 DH1 + 2 DH-O1);
  - `alt`: passed 439, failed 0, exit 0.

  PROBE(`scratchpad/px3/out/sandbox_{base,main,alt}.txt`), sha256 `f64d849f…`, `d164023f…` and `09879451…`; 0 lines with `FAIL` in each. Rule F's 445 is 441 plus its four probe-only checks, which are not in the patch (FILE(docs/drafts/reviews-2026-11-13/rulef-reg20-ops-draft3-r3.md:297-298)).
- **`test_control_due.py` on `main`:** 47 passed, exit 0 (PROBE(`scratchpad/px3/out/test_control_due_main.txt`), sha256 `6810d34c…`). The command was `.venv/bin/python -m pytest -q -p no:cacheprovider`, with `PYTHONDONTWRITEBYTECODE=1` and `--basetemp` in scratch. No round-3 patch touches `control_due.py`, `recheck_one.py` or that test (DERIVED from the patches' `+++` lines).
- **sha256 of the files the round-3 patches change in `main`** (PROBE):
  - `common.sh` `a0dcdbd10ac0e74ca8fbc2c1829fa5244396ff479970a9f0f7ec3ed6f111048f`;
  - `launch.sh` `f0d70e3133342ff7ef18b68dd32af5a8aa4e52c9c9d0cbe005917951e0b05be9`;
  - `test_sandbox.sh` `c67a9008c4d1b83006e5ce417b511f487ed5d2e007299ae7b96c887b7d8e0101`.
- **The control test in DH1 selects exactly the controls.** `C=stage2_control_l1pl350ol_r2.0_w3000_s` is set once (FILE(`main` common.sh:29)). No other assignment to `C` exists in `common.sh`, `launch.sh` or `queue.sh` (PROBE: grep). `DRIFT=burst_l1pl350cl_…` cannot match `${C}*`. No `errexit` is set in these files (PROBE: grep), so a failed `[[ … ]] &&` is harmless.
  - The floor check (FILE(`main` launch.sh:53)) is still before the attempt record (FILE(`main` launch.sh:59)).
- **The same blob at the pin, at E1's commit and at HEAD** (PROBE: `git rev-parse`, `git diff --quiet`, `git merge-base`):
  - `uv.lock` `8b1c04b4…`, `pyproject.toml` `b30b8efe…` and `.python-version` `28d9a01b…` are the same at 1cface7, ce5f842 and HEAD;
  - `configs/defaults.yaml` is the same at 1cface7, 5ee6e38, ce5f842 and HEAD;
  - 1cface7 is an ancestor of ce5f842;
  - `harness/` is unchanged from 5ee6e38 to HEAD.
- **RD3 and RD8 are verbatim.** Draft 3's RD3 (:647–653) and RD8 (:249) equal my round 2's (:294–300 and :366) byte for byte (PROBE: `diff`).
- **When RUNBOOK:26 was written.** Its disk rule was committed in `b20fe3bf` at 2026-11-12 19:32 UTC (PROBE: `git blame -L 26,26`). That is before the disk reading of 2026-11-14 02:54 UTC and before draft 3.
- **Anchors.** Every anchor in "Conditions" occurs exactly once in its target file (PROBE: `scratchpad/px3/tools/anchors.py` and `anchors2.py`, "BAD 0", and a final count of this file's `text` blocks against the targets). The targets are draft 3, rule F round 3, `runbook_heading1.patch`, `README.md` as patched in `main`, and `agent/FOR_AUTHOR.md`.
  - One anchor is an exception: DL7 (d)'s bullet, which DH1's text creates. Its source text occurs once in rule F's file (FILE(docs/drafts/reviews-2026-11-13/rulef-reg20-ops-draft3-r3.md:200)).
  - Three more anchors are sentences that DH1 or DH2 inserts (DL3 (b), DL3 (c), DL4). Each occurs once in rule F's file.

### 1. DH1: the main patch, not the fallback

**Ruling: `rulef-reg20-ops-draft3-r3-dh.patch`, as written.** As the owner, I accept lowering a control's launch floor to 1 GiB.

**Why the owner would sign it:**
- **(a) It keeps the registered order.** The control runs "right after it" (FILE(docs/decisions.md:4054)).
  - With one floor for every launch, a disk stop falls between a cold burst run and its control. From the expected F1 that happens with probability 0.0319 at p = 0.10 and 0.1406 at p = 0.25 (PROBE: rule F round 3's enumeration, FILE(docs/drafts/reviews-2026-11-13/rulef-reg20-ops-draft3-r3.md:93-94)).
  - Draft 3's option (a) does not rule it out either: one rerun at its minimum free space pushes C19 to the 12th launch (rule F T1, ibid. :100-103).
  - Under DH1, a control is stopped only if its burst run wrote more than 1,048,576 kB = 4.32 × r. DERIVED: the burst launched with at least 2,097,152 kB free; 1,048,576 / 242,736 = 4.320.
- **(b) The fallback fails exactly where it is needed.** `-dh1alt` keeps the order only if the burst run wrote at most `CONTROL_RESERVE_KB` = 262,144 kB, which is 1.080 × r (DERIVED: 262,144 / 242,736).
  - An open run 8 % larger than REG-19's closed seed-15 run breaks it. Draft 3 itself expects open backlogs may be larger (BELIEF, FILE(docs/drafts/reg20_ops_decision_draft3.md:472)).
  - The cold open runs, the ones that have controls, are the likeliest to be larger: the registration expects about 960 outstanding requests in a stuck open run (FILE(docs/decisions.md:4057)).
  - The fallback also raises P(any disk stop) from 0.0523 to 0.3439 at p = 0.10 (PROBE: rule F's appendix, ibid. :379). It is worse on both counts unless open runs are no larger than r.
- **(c) Rule A5.** The floor judges free disk space. It judges no run, label or verdict.
  - It is set before any arm A run exists.
  - Its value is RUNBOOK:26's per-launch rule, "free space ≥ 4 × the item's expected size (≈ 240 MB per 4080 s run)" (FILE(agent/RUNBOOK.md:26)): 4 × 242,736 = 970,944 kB, rounded up to 1 GiB (DERIVED).
  - That rule was committed on 2026-11-12, before the reading that prompted DH1 (PROBE: blame, above). DH1 therefore adopts a rule that already existed, rather than choosing a number after the data.
  - I do not count this as a widening. An owner who reads any lower floor as one has the fallback, which rule F built for that reading. I judge that the owner weighs a registered scientific requirement, the control right after its burst run, above an operational margin with no scientific role.
- **(d) RUNBOOK:26, read per launch, is the reading the owner signed.**
  - REG-19's resume, approved by the owner (FILE(docs/decisions.md:4284-4289)), ran on ops_r3, whose floor is one check before each launch: `MIN_FREE_KB=2097152 … (about 240 MB per run)` (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:15)). That item had ten runs. Read per item, it would have needed 4 × 10 × 240 MB ≈ 9.6 GB (DERIVED), which nothing checked.
  - E1's approved scripts hold a 2 GiB floor before each launch, for runs of about 70 MB (FILE(docs/probe/20261113_e1/ops/common.sh:34)).
  - Read per item, the rule cannot be met by any variant today: 10,680,384 kB is needed, and F0 is 4,171,272 (FILE(docs/drafts/reg20_ops_decision_draft3.md:470,510)).
- **(e) Rule 5.** `CONTROL_MIN_FREE_KB` is a named setting in `common.sh`'s parameter block, next to `MIN_FREE_KB`, with its derivation in its comment (FILE(`main` common.sh:19-22)). That block is where every ops parameter lives (FILE(docs/probe/20261113_e1/ops/common.sh:4-5)).
- **(f) The residual risk, stated.**
  - DH1 lets a control launch with between 1,048,576 and 2,097,152 kB free. It fills the disk only if it writes more than that, at least 4.32 × r (DERIVED).
  - If it did, the run would most likely end invalid or without `checks.json` (BELIEF). Its next attempt would then wait for the owner (a loss without a reboot, point 8) or be refused for disk before it is spent. That control would run late, but no label changes.
  - The same control under draft 3's single floor would be refused before launch and run late. The difference is one spent control attempt, and only if open runs are 4.3 to 8.6 times r. In that case the queue stops for disk within two launches whatever the floor (DERIVED from the expected F1: 3,742,914 − 2 × 1,048,576 = 1,645,762 < 2,097,152).
  - df's free figure leaves 3,291,748 kB aside (DERIVED: 64,163,468 − 56,820,544 − 4,051,176, PROBE(docs/probe/20261114_vm_disk/disk_20261114T025418Z.txt)). I take that to be ext4's root reserve, so a user-space ENOSPC still leaves room for root processes (BELIEF).
  - DL11 makes the [RESULT] test the BELIEF that an open run is about r.
- **(g) The diff itself.** It is one setting, two lines in `launch.sh` and nine sandbox checks, and it passes 441 of 441 together with DH-O1 (PROBE, above). Read against the code:
  - every config that is not a control keeps `MIN_FREE_KB`;
  - the message now names the floor and the config, and the queue's stop line still takes the `STOP` line (FILE(`main` queue.sh:76));
  - the refusal still spends no attempt.

### 2. DH2 and DH-O1 to DH-O4

- **DH2: taken, verbatim.**
  - It restores the end of the hold my RD4 set: "until final.sh's two output files are committed, or an entry ends arm A" (FILE(docs/drafts/reviews-2026-11-13/proxy-reg20-ops-draft2.md:306)).
  - Draft 3 :540 loosened that end to "an entry matching `STOP_PAT` stops arm A", against its own merge rule, "the stricter text is kept" (FILE(docs/drafts/reg20_ops_decision_draft3.md:538,540)). This is draft 3's one departure from RD1–RD10 that weakens a protection (section 5).
  - Rule F's T2 shows what it costs: a pause would end the hold mid-arm, with REG-24's and D1's SEALS rows waiting (ibid. :564).
  - DL4 adds one sentence after DH2 (4), so that [CORR] and [DECISION] headings follow the same colon rule. It changes no word of DH2.
- **DH-O1: taken** (in DL1).
  - It adds a stop only.
  - `configs/defaults.yaml` equals the pin's (DERIVED, above), and today's checks merge it (FILE(harness/checks.py:48), as rule F cites).
  - A commit to it would otherwise change every later recheck in silence.
- **DH-O2: not taken as code.** It is a script change in words only, untested and without a patch, and RD1's rule would need a further round for it.
  - The trace it closes (rule F T3) needs a dry run that would change packages at the pin. `uv.lock`, `pyproject.toml` and `.python-version` are the same blobs at ce5f842 and at the pin (DERIVED). E1's dry run at ce5f842 read "Would make no changes" (FILE(docs/decisions.md:19394), the probe quoted under it). So I judge the trace unlikely (BELIEF).
  - DL6 closes it by hand at no cost.
- **DH-O3: taken.** Heading 2 must quote my round 2 verbatim, and that file has 6 lines that begin `## ` (PROBE: `grep -c '^## '`). Pasted unquoted, `tools/check_docs.py` would read them as entry headings (rule F T4). A quoted start heading would also pass `gate_in_log` early. Blockquoting fixes both.
- **DH-O4: taken.** It aligns RUNBOOK §4 with :48 and point 18 at no cost (rule F T6).

### 3. Draft 3's own additions

- **The once-only delegate check** (FILE(`main` common.sh:162-164)) is sound.
  - It makes RD2's "not changed again … except by an `(owner)` [DECISION]" mechanical, together with `rulings_ok`'s last-commit test (ibid. :135-136).
  - It fails safe on a quoted heading.
  - An owner's rulings heading written before the delegate's makes the delegate's refused. That is correct: the owner's rulings govern.
- **`e1_ended`** (ibid. :141-146) is sound.
  - It tests the lock for existence only, and `E1_END_PAT` matches E1's three registered end forms and nothing looser (rule F T5, its pattern probe).
  - E1 is first, and the gate holds arm A until E1's end entry, which is RD5 made mechanical.
  - The stale-lock case is the owner's (DL6).
- **`vm_checkout.sh`** (ce5f842 → 1cface7) is sound, with DL6 for T3.
  - Every refusal comes before any change on the VM (FILE(`main` vm_checkout.sh:18-31)).
  - It needs `gate_in_log`, so it runs only after heading 3. That is why DH-O4 starts RUNBOOK §4's ban at heading 3.
  - It covers the move that E1's approval leaves to "its own entry" (FILE(docs/decisions.md:18294), as draft 3 cites), and only from a descendant of the pin.
- **The RUNBOOK §4 clause:** sound, with DH-O4.

### 4. Disk: (b) under DH1. Arm A may start after E1's end entry before the owner frees space

**Ruling:** option (b), made safe by DH1, which is draft 3's option (c) in DH1's form. Starting arm A is a GPU-run decision, which the delegation covers (FILE(docs/decisions.md:4233)). Freeing space means deleting, which stays the owner's (FILE(docs/decisions.md:4235)).

**Reasons:**
- **What a stop costs under DH1.** A disk stop:
  - falls only before a burst run or the drift run (unless a burst run wrote more than 1,048,576 kB);
  - spends no attempt (FILE(`main` launch.sh:53,59));
  - writes no state record and changes no label (rule F §8);
  - is the kind of stop E1's approved rule restarts "once the cause is removed" (FILE(docs/decisions.md:17072)).
- **How likely a stop is.** From the expected F1 = 3,742,914 kB (FILE(docs/drafts/reg20_ops_decision_draft3.md:480)), arm A stops for disk only if at least two of seeds 15–18 are cold.
  - DERIVED: B19 is then at least the 8th launch, and 3,742,914 − 7 × 242,736 = 2,043,762 < 2,097,152. With one or no control due among seeds 15–18, every launch fits, C19 included. The worst cases are B19 at launch 7, with 3,742,914 − 6 × 242,736 = 2,286,498 ≥ 2,097,152, and C19 at launch 8, with 2,043,762 ≥ 1,048,576.
  - At the registration's p = 0.10 (BELIEF, FILE(docs/decisions.md:4085)): P(stop) = 1 − 0.9⁴ − 4 × 0.1 × 0.9³ = 0.0523 (DERIVED; it equals rule F's enumeration).
  - With E1's worst case of 18 runs, a stop before B18 would have been certain (rule F's table). E1 ended with six runs (FILE(docs/decisions.md:19459)), so that case is gone. The real free space is the session probe's (DL8).
- **What (a) costs.** It idles the GPU, with certainty, from E1's end entry until the owner acts. The owner's words were "it should never depend on me ... it should run end to end" (FILE(docs/decisions.md:4232)).
  - It does not guarantee completion either. At (a)'s DH1 minimum of 4,281,776 kB, one burst rerun before seed 19 makes B19 the 11th launch: 4,281,776 − 10 × 242,736 = 1,854,416 < 2,097,152 (DERIVED). That is still a clean stop at a seed boundary.
- **What (b) costs in credibility.**
  - A stop puts seed 19, or seeds 18 and 19, after a gap. The registration fixes the seeds' order, not the time between them (FILE(docs/decisions.md:4056), "Order"). Its alternative 5, time drift, already applies, and the drift run checks one seed (FILE(docs/decisions.md:4093)).
  - The arm is weaker if it is not contiguous, but no label is wrong. The [RESULT] reports the gap (DL11).
  - A stop before B19 shows that at least two controls ran, but the control bits are visible in the queue output anyway (point 15).
  - The stop is kept non-discretionary: its one answer is fixed now (DL7). The queue is started again once space suffices, and the delegate never ends arm A at a disk stop.
- **The hold during a pause.** While a disk stop lasts, arm A keeps the VM and the hold, and REG-24's and D1's SEALS rows wait. Both of those items also need VM disk (FILE(agent/FOR_AUTHOR.md:7), draft figures, BELIEF), so disk space holds them up whatever arm A does.

**What the start entry, and the [OPS] that commits the session probe, must state about disk:** DL8.

### 5. My round-2 picks under draft 3, and draft 3's departures from RD1–RD10

**Picks: all stand.** No new evidence or argument changes one (rule A4):
- **2a `setaside`.** RC5's text (FILE(docs/drafts/reg20_ops_decision_draft3.md:434)) states what my RD3 (vi) assumed: a set-aside seed ends with its rerun's label or as `not_run`.
- **6 (b), 8 (b):** unchanged.
- **7 `lost_open`.** RC3 narrows `not_run`, which has no effect under `lost_open` (ibid. :216).
- **9 (a).** Under DH1, a third control attempt has the control's floor, which is harmless.
- **16 (a).** My round-2 reason was that (a) keeps arm B blind with no code change (FILE(docs/drafts/reviews-2026-11-13/proxy-reg20-ops-draft2.md:188)). The freeze was not the reason, so RC1 (d) does not touch it.
- **G (a).** Its evidence (3) still holds at 25ad86e: one gate pair (PROBE: `git ls-tree -r --name-only HEAD -- docs/probe/reg20/` gives the two files).

**Departures from RD1–RD10:**
- **RD1** ("the only script change … Anything else needs a new round"). Draft 3's diff is larger (FILE(docs/drafts/reg20_ops_decision_draft3.md:21-27)). This delta is that round, and I accept the larger diff.
  - Each added item adds a stop or a record, or (RC3) changes `decide` only in a branch that `lost_open` does not take.
  - Each was reviewed by rule F round 3 and passes the sandbox, 441 of 441 after DH1 and DH-O1.
  - RD1's rule carries forward as DL1's closed list.
- **RD2.** Heading 2 quotes rule F rounds 2 and 3: accepted. Round 2 was NOT READY, so round 3 must be quoted (FILE(docs/drafts/reg20_ops_decision_draft3.md:645)).
- **RD4.**
  - The hold's end at :540 is **not accepted**. DH2 restores it (section 2).
  - Accepted: the name "hold"; nine scripts; D1's row; RC1's stricter rule on uncommitted edits; the apply-and-commit exception; the closure quoted from 40948ba and quoted again at heading 1's commit (item map, RD4 row).
- **RD5.** "Kept by hand" becomes `e1_ended`. That is stricter: accepted.
- **RD6 and RD7:** accepted. The `git diff --stat 56820bd <commit>` quote moves into heading 3, which names heading 1's commit (FILE(docs/drafts/reg20_ops_decision_draft3.md:676)). That is acceptable.
- **RD3 and RD8:** verbatim (PROBE: `diff`).
- **RD9 and RD10:** placed (duties (iii), (v), (ix); "Docs"). Accepted.

**My own omission (rule A6).** My round 2 never checked the VM's disk against arm A's runs, and draft 3 found the shortfall. It is not a wrong statement, but it is an omission, and I record it here.

### Conditions

Where an anchor is given, it occurs exactly once in the file named (PROBE: `anchors.py`, `anchors2.py`). Anchors and new text are given in `text` blocks, exactly as they are to be typed. "Draft" means `docs/drafts/reg20_ops_decision_draft3.md` as amended for heading 1. A † citation in the decision then means the file as committed under DL1.

**DL1 BEFORE: the scripts, exactly.**
- **Order of application** to `docs/probe/20261113_reg20/ops/`:
  1. `docs/drafts/reg20_ops_r3/ops_draft3.patch` (`31dbea7c…`);
  2. `docs/drafts/reviews-2026-11-13/rulef-reg20-ops-r3_files/rulef-reg20-ops-draft3-r3-dh.patch` (`c2c6f97f…`);
  3. `rulef-reg20-ops-draft3-r3-dho1.patch` (`05806c4a…`).

  Not `-dh1alt.patch`.
- **The committed files** have these sha256:
  - `common.sh` `a0dcdbd10ac0e74ca8fbc2c1829fa5244396ff479970a9f0f7ec3ed6f111048f`;
  - `launch.sh` `f0d70e3133342ff7ef18b68dd32af5a8aa4e52c9c9d0cbe005917951e0b05be9`;
  - `test_sandbox.sh` `c67a9008c4d1b83006e5ce417b511f487ed5d2e007299ae7b96c887b7d8e0101`;
  - `recheck_one.py`, `session_probe.sh`, `test_control_due.py` and `vm_checkout.sh`: as SHA256SUMS.txt group (1);
  - `owner_rulings.txt`: as group (1) until the rulings commit, and group (2) (`2daacec3…`) from it on;
  - `README.md`: group (1) plus DL2's text only.

  No `.orig` file is committed.
- **Tests on the committed tree.** Run both test files there and save their outputs beside the old ones. The expected counts are 441 of 441 and 47 of 47 (PROBE, "Checks I ran").
- **The closed list.** The ops [DECISION] quotes `git diff --stat 56820bd <commit> -- docs/probe/20261113_reg20/ops`. That diff holds only these files, the saved outputs and `scripts_commit.txt`. Anything else needs a new round.

**DL2 BEFORE: the ops README** (`docs/probe/20261113_reg20/ops/README.md` as patched).

(a) After the line
```text
9. **`final.sh` uses `$PY`**, `.venv/bin/python`.
```
add the line
```text
10. **A control's disk floor.** A control launches with at least `CONTROL_MIN_FREE_KB` = 1,048,576 kB free on the VM; every other launch keeps ops_r3's `MIN_FREE_KB` = 2,097,152 (rule F round 3, DH1). A disk stop therefore falls before a burst run or the drift run, not between a cold burst run and its control ("right after it", decisions.md 2026-11-12 [REG] REG-20), unless that burst run wrote more than 1,048,576 kB. It spends no attempt.
```

(b) To the end of
```text
ops_r3's recheck guard is kept: `analysis/`, `harness/` and `configs/defaults.yaml` must equal HEAD.
```
append, on the same line,
```text
 Since rule F round 3 (DH-O1), `configs/defaults.yaml` must also equal the pin's, because today's checks merge it beneath each run's config.
```

(c) Replace
```text
draft 3, 428 of 428 passed, exit 0, `docs/drafts/reg20_ops_r3/sandbox_20261114T023449Z.txt` (on a scratch copy of 40948ba with the patch applied).
```
with
```text
draft 3, 428 of 428 passed, exit 0, `docs/drafts/reg20_ops_r3/sandbox_20261114T023449Z.txt` (on a scratch copy of 40948ba with the patch applied); with rule F round 3's DH1 and DH-O1 patches, <n> of <n> passed, exit 0, `<saved output>` (on the committed tree).
```

(d) To the end of
```text
5. Run `zsh docs/probe/20261113_reg20/ops/session_probe.sh`, with `SET=1` if allowed.
```
append, on the same line,
```text
 Commit its probe file with an [OPS] entry headed `[OPS] REG-20 arm A: …` that quotes its `free_kb` line and states the disk facts the decision's point D requires (owner-proxy delta round 3, DL8); start the queue only after that commit.
```

**DL3 BEFORE: point D's DH1 text, with three corrections.** Apply rule F's "*Text, in point D*" bullets (FILE(docs/drafts/reviews-2026-11-13/rulef-reg20-ops-draft3-r3.md:192-201)) verbatim. Then make three changes.

(a) In the draft, replace
```text
Even with no E1 run on the VM, the eleventh launch is refused.
```
with
```text
Even with no E1 run on the VM, the tenth launch is refused (nine fit, as the table shows); under DH1 the tenth launch is refused only when it is B19, that is when the controls of all four seeds 15–18 are due.
```
- DERIVED: at F0, 4,171,272 − 9 × 242,736 = 1,986,648, which is below 2,097,152 but at least 1,048,576.
- Draft 3's "eleventh" understates its own table, which shows 9 launches fitting (FILE(docs/drafts/reg20_ops_decision_draft3.md:487)).

(b) After DH1's inserted sentence
```text
The 27-launch ceiling needs 7,680,080 kB (B19's second attempt, the 24th launch, needs 2,097,152 + 23 × 242,736).
```
add
```text
The [OPS] VM disk entry's 4,524,512 kB (FILE(docs/decisions.md:19452)) is draft 3's figure before DH1; under DH1 it is 4,281,776 kB.
```

(c) After DH1's inserted sentence ending
```text
4.3 × r (DERIVED).
```
add
```text
A control launched with less than `MIN_FREE_KB` free fills the disk only if it writes more than its launch free space, at least 1,048,576 kB (DERIVED). Such a run would end invalid or without `checks.json` (BELIEF); its next attempt would then wait for the owner (point 8) or be refused for disk before it is spent, so that control would run late. No label changes.
```

**DL4 BEFORE: DH2, verbatim, and one sentence after it.** Apply rule F's DH2 parts 1–7 (FILE(docs/drafts/reviews-2026-11-13/rulef-reg20-ops-draft3-r3.md:212-222)) verbatim. Its sandbox cases are already in DL1's patch.

After the paragraph that DH2 (4) adds, which begins
```text
**Headings of arm A's other records** (rule F round 3, DH2).
```
add this delta's own line:
```text
The same colon rule holds for a [CORR] or [DECISION] entry about arm A, with or without `(owner)` or `(delegate)`, other than headings 1 to 3 and arm A's two end entries: the colon follows "arm A", unless the entry is meant to stop every script, since `STOP_PAT` also matches [CORR] and [DECISION] (FILE(docs/probe/20261113_reg20/ops/common.sh:49)†). (Owner-proxy delta round 3, DL4.)
```

**DL5 BEFORE: DH-O3 and DH-O4.**

(a) DH-O3's paragraph (FILE(docs/drafts/reviews-2026-11-13/rulef-reg20-ops-draft3-r3.md:245)) goes verbatim into the draft's "Texts for headings 2 and 3".

(b) In `docs/drafts/reg20_ops_r3/runbook_heading1.patch`, replace
```text
that is from REG-20's `docs/probe/20261113_reg20/ops/vm_checkout.sh` until arm A's end entry
```
with
```text
that is from the commit of arm A's start entry (`[DECISION] (owner|delegate) REG-20 arm A starts: …`) until arm A's end entry
```
- The item map's N3 row notes the change.
- SHA256SUMS.txt's group (2) value for `agent/RUNBOOK.md` then no longer applies. Heading 1's commit records the new one.

**DL6 BEFORE: point 18's hand rules, in place of DH-O2.** In the draft, after
```text
  - If the VM is already at the pin, it records `already_at_pin` and changes nothing.
```
add
```text
  - After a stop of `vm_checkout.sh` at or after its checkout command (the messages "the checkout on the VM failed", "the VM's dry-run sync failed", "the VM's tree is not the pin, clean, after the checkout", "the VM's uv.lock is not the pin's after the checkout", "the dry-run sync on the VM would change"), neither `vm_checkout.sh` nor `session_probe.sh` is run again until an owner's entry decides (rule F round 3, T3; owner-proxy delta round 3, DL6, in place of DH-O2). An `already_at_pin` record is accepted only beside an earlier `vm_checkout_<stamp>.txt` of this decision that shows `uv_changes 0`, and the [OPS] entry that commits it quotes that line.
  - A stale E1 lock (E1's queue not running, its lock present) is the owner's: the agent does not move or delete it, and does not start E1's queue to clear it (rule F round 3, T5).
```
The five quoted messages are those of FILE(`main` vm_checkout.sh:32-39) (PROBE: grep).

**DL7 BEFORE: the disk ruling in the draft.**

(a) Replace
```text
- **Point D, the VM's disk,** is the owner's. Freeing space on the VM means deleting files, and "deleting anything" is not delegated (FILE(docs/decisions.md:4235)).
```
with
```text
- **Point D, the VM's disk.** Freeing space on the VM is the owner's: it means deleting files, and "deleting anything" is not delegated (FILE(docs/decisions.md:4235)). Whether arm A starts before space is freed is a GPU-run decision, the delegate's (FILE(docs/decisions.md:4233)): (b) under DH1 (owner-proxy delta round 3).
```

(b) Replace
```text
| D | The VM's disk | arm A's planned runs do not fit (DERIVED) | **owner** |
```
with
```text
| D | The VM's disk | arm A starts after E1's end entry without waiting for space ((b) under DH1); a disk stop falls at a seed boundary and is restarted once the next launch's floor is met | delegate (the start); **owner** (freeing space) |
```

(c) Replace
```text
**(a), recommended.**
```
with
```text
**(a), recommended to the owner, not waited for (owner-proxy delta round 3, DL7).**
```

(d) After the bullet that DH1's text makes of draft :521, which begins
```text
- **(c), applied (rule F round 3, DH1):**
```
add
```text
**The ruling: (b) under DH1** (delegate; owner-proxy delta round 3). Arm A may start after E1's end entry without waiting for the owner to free space.
- A disk stop is a pause, not an end; the arm A hold continues (DH2). Its record is headed `[OPS] REG-20 arm A: …` (DH2) and quotes the stop line.
- Its one answer is fixed now: the queue is started again, unchanged, once a read-only `df -k` on the VM meets the floor of the launch that stopped, with the owner's removal, if any, recorded in an [OPS] entry. No other choice is made at a disk stop. The delegate never ends arm A at a disk stop; only an owner's entry may.
- The owner's removals, and `agent/bin/vm_verify_list.zsh`, happen only while no run is in progress: before arm A's first launch, or at a disk stop. Never an arm A folder (RD8); E1's only after E1's end entry.
```

(e) Replace
```text
- **Point D:** the owner's. Arm A's planned runs do not fit on the VM's disk as last read.
```
with
```text
- **Point D:** freeing space is the owner's; arm A does not wait for it ((b) under DH1). Arm A's 11 planned runs do not fit on the VM's disk as last read (4,051,176 kB at 02:54 UTC with E1 running, against 4,281,776 kB under DH1).
```

(f) After
```text
- the owner's settle record after RD3 (vi)'s stop under `setaside` (two set-asides, or a set-aside and an invalid run).
```
add
```text
A disk stop is not in this list: its one answer is fixed in point D (restart once space suffices; never an end by the delegate).
```

**DL8 BEFORE: what the start entry and the session probe's [OPS] state about disk.** In the draft, after
```text
- It states that the arm A hold begins with its commit, and quotes the hold's list.
```
add
```text
- It states point D's ruling, (b) under DH1, and the last committed free-space reading, with its time and PROBE (at the owner-proxy delta: 4,051,176 kB at 02:54:18 UTC with E1 running, PROBE(docs/probe/20261114_vm_disk/disk_20261114T025418Z.txt)), against DH1's needs: 3,310,832 kB with no control due and 4,281,776 kB for all 11 planned runs (DERIVED, rule F round 3). It says that a disk stop falls only before a burst run or the drift run, unless a burst run wrote more than 1,048,576 kB, spends no attempt, changes no label, and is answered only as point D fixes; that freeing space is the owner's (`agent/FOR_AUTHOR.md` −20); and whether the owner had freed any by then.
- The [OPS] entry that commits arm A's session probe, before the queue starts, quotes the probe's `free_kb` line. From it, with r = 242,736 kB (BELIEF that an open run is about r) and DH1's floors, it gives, DERIVED, which numbers of due controls among seeds 15–18 would stop the queue for disk, and before which launch.
```

**DL9 BEFORE: `agent/FOR_AUTHOR.md` −20, in heading 1's commit.**

(a) Replace
```text
arm A's 11 planned runs need 4,524,512 kB free at the first launch, and its 27-launch ceiling 8,408,288 kB
```
with
```text
arm A's 11 planned runs need 4,524,512 kB free at the first launch, and its 27-launch ceiling 8,408,288 kB, before rule F round 3's DH1 (a control's floor of 1 GiB), which lowers them to 4,281,776 kB and 7,680,080 kB
```

(b) Replace
```text
(b) accept a disk stop in the middle of arm A, which can make a due control run late (draft 3, "Options").
```
with
```text
(b) **ruled by the delegate (REG-20 ops decision, point D; owner-proxy delta round 3):** arm A starts after E1's end entry without waiting for you; under DH1 a disk stop falls only before a burst run or the drift run, spends no attempt and makes no control late; the queue is started again once space suffices, and only your entry can end arm A there. Remove folders, and run `agent/bin/vm_verify_list.zsh`, only while no run is in progress: before arm A's first launch, or at a disk stop.
```

**DL10 BEFORE: heading 2 quotes this delta.** The rulings entry quotes this file verbatim, blockquoted (DH-O3), together with my round 2 and rule F rounds 2 and 3. Heading 1 carries the owner-proxy line below.

**DL11 LATER: the [RESULT] on disk.** In the draft's duties, replace
```text
- **(xii) Point D:** each disk stop, with the free space it read, and any VM removal the owner recorded.
```
with
```text
- **(xii) Point D:** each disk stop, with the free space it read, the floor it needed and the launch it stopped, and any VM removal the owner recorded; every control launched with less than `MIN_FREE_KB` free (DH1's floor), with its free space; each arm A run's footprint on the VM, DERIVED from the `free_kb` lines of consecutive pre-launch reads, against r = 242,736 kB, as the test of point D's BELIEF that an open run is about r; and, for a seed launched after a disk stop, the time from the previous seed's last run (alternative 5, time drift, FILE(docs/decisions.md:4093)).
```

### Owner-proxy line for the delegate's [DECISION] entry

Owner-proxy delta, round 3 (a separate subagent, 2026-11-14; quoted verbatim in the rulings entry): **APPROVE** of draft 3, with DL1–DL10 before the first launch and DL11 later.
- DH1 is `rulef-reg20-ops-draft3-r3-dh.patch` (a control's floor `CONTROL_MIN_FREE_KB` = 1,048,576 kB, RUNBOOK:26's per-launch rule; not the fallback).
- DH2 is applied verbatim, with one sentence after it for [CORR] and [DECISION] headings.
- DH-O1, DH-O3 and DH-O4 are taken. DH-O2 is replaced by a hand rule.
- The round-2 picks stand: 2a `setaside`, 6 b, 7 `lost_open`, 8 b, 9 a, 16 a, G a.
- Point D: arm A starts after E1's end entry without waiting for VM space ((b) under DH1). A disk stop is a pause, restarted once space suffices and never ended by the delegate. Freeing space stays the owner's.
