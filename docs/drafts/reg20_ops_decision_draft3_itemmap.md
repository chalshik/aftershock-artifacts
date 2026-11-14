# REG-20 arm A operations, draft 3: item map

**Scope.** This map covers every item of rule F round 2 (RC1–RC8 required, RC-O1–RC-O12 optional; `docs/drafts/reviews-2026-11-13/rulef-reg20-ops-draft2-r2.md`) and of owner-proxy round 2 (RD1–RD10 and RD-O1–RD-O3; `docs/drafts/reviews-2026-11-13/proxy-reg20-ops-draft2.md`). For each item it gives where the item went in draft 3 (`docs/drafts/reg20_ops_decision_draft3.md`, "D3" below) or in its patches (`docs/drafts/reg20_ops_r3/`), and every departure from the reviewer's words. It ends with the merges, the conflicts and their proposed resolutions, and what draft 3 adds that no item asked for. A line marked † is in a file as patched by `ops_draft3.patch`.

Written 2026-11-14 by the draft writer, at 0 GPU h. Nothing is committed.

## Rule F round 2, required

| Item | Where it went | Departures |
|---|---|---|
| **RC1 (a)** point 12 | D3 point 12, verbatim | RD6's two sentences follow it, with "freeze" read as "hold" (M3) |
| **RC1 (b)** the arm A hold | D3 "The arm A hold": when it applies, items 1–5 and the [RESULT] duty, verbatim where RC1 gives text | Merged with RD4 (M3). Item 1's list is the union of RC1's and RD4's. RC1's list leaves out `analysis/tables.py`, which is in k1's closure (PROBE(docs/drafts/reg20_ops_r3/closure_20261114.txt)), and RD4's 19-file list holds it. All of `harness/` (RD4) replaces RC1's four files. `vm_checkout.sh` is the ninth script. Item 2 is RC1's, with RD4's apply-and-commit exception for files outside the list. Item 3 is RD4's ban, with RC1's stop-first path kept (M3). "A later start heading starts the hold again" is added, because `gate_in_log` needs a new start heading after a stop heading |
| **RC1 (c)** point 16 | D3 point 16, merged with RD6's sentence | The merge adds RD6's "Ruling 16 is (a), which changes no file." |
| **RC1 (d)** owner question 16 | D3 "For the owner", 16, verbatim | — |
| **RC1 (e)** Proposal 4 | D3 has no "Proposals" list. The arm-B seal under 16 (b) reads "after `final.sh`'s files are committed" in point 16's merged text | The words land in point 16, not in a Proposal 4 |
| **RC1 (f)** README:130 | README, verbatim, with RD4's first bullet after it (RD6) | — |
| **RC1 (g)** draft 2's item map rows | Draft 2's item map is committed and is not edited. Instead, here: row RA-O1 now reads "The arm A hold bars them (the freeze has ended)", and M10 reads "mitigated by the arm A hold" | The rows are superseded in this map, not edited in the old one |
| **RC2** | Rule F's patch, its first hunk pair, applied verbatim (common.sh:131-133†). Its message names both headings (RD1). RC2's text is added to D3 point 14 | The message and the text say "a rulings heading" (the owner's, or once and first the delegate's) for "the owner's rulings heading", because of RD1 (M1). Draft 3 adds RD2's once-first check, which RC2 does not give (M1) |
| **RC3** | Rule F's `decide` hunks and sandbox cases, verbatim (common.sh:275, :335, :345, :352†). The point 7 wording and the owner question 7 option are verbatim in D3 | The third wording bullet ("Draft 2 recommends **`not_run`** … where both attempts are setup-only") is quoted as superseded, since the pick is `lost_open` (M7) |
| **RC4** | Point 15, verbatim. Duty (iii), second bullet, verbatim. The stricter rule is verbatim in D3 point 7 and in README "Records" | Point 15's list gains RD3 (ii)'s and RD3 (vi)'s owner answers (M5) |
| **RC5** | Owner question 2a, verbatim. The point 2a `setaside` bullet, verbatim. Duty (v), verbatim. "Not settled", verbatim | Duty (v) is preceded by RD9's sentence (M6) |
| **RC6** | D3 point 10a, verbatim except for two marked changes. The README's records list and `copy_verify` describe the `.sha256` list | (i) "before `final.sh`'s files are committed" becomes "before REG-20's [RESULT]", RD8's stricter end (M4). (ii) is made a script step: `copy_verify` writes `<holding folder>/<rid>.sha256` for a held or set-aside run and prints `SHA256 LIST …` (common.sh:592-599†), with three sandbox checks. RC6 asked for the list, not for code |
| **RC7 (a)** point 18 | D3 point 18. The summary row is `18 \| Order with E1 \| …` | Merged with RD5 and E1's [REG] (M2). "Whichever … has its operations [DECISION] committed first" is set beside RD5's and E1's definitions: all three give E1 first (DERIVED, D3 point 18). RC7's "README step 4 waits for E1's end entry and for E1's queue lock" is now enforced by script (`e1_ended`), not only by text. RC7's "this departs from RUNBOOK §5's row order, and the start entry says so" no longer applies: E1's approval added row 2b "(with 2a)", which carries the rule (FILE(agent/RUNBOOK.md:66)) |
| **RC7 (b)** RUNBOOK in heading 1's commit | `runbook_heading1.patch`: :48 is RB6's text plus RC7's "; while REG-20 arm A or E1 has started and not ended, no deploy", verbatim. :64 gains RB6's words. :63 is marked done with 3c8e5dc and G | :48 adds a parenthesis that names `vm_checkout.sh` and point 18. :64 also gains RD5's sentence and the `e1_ended` wait. The §4 heading clause for arm A is this author's addition (N3) |
| **RC7 (c)** README step 4 | README step 4, prefixed verbatim | Step 4's body is now `vm_checkout.sh` (RC-O10), not RB6's hand steps (M10) |
| **RC8** | D3 status block, draft line 7, verbatim. README:8, verbatim | — |

## Rule F round 2, optional

| Item | Taken? | Where it went | Departures |
|---|---|---|---|
| **RC-O1** SEALS tolerance | **No** | — | It conflicts with RD4, which forbids the row itself. RC1 item 3's stop-first path covers a row that cannot wait (M3) |
| **RC-O2** E1's lock | **Yes, widened** | `E1_LOCK` and `e1_ended` (common.sh:51-52, :138-143†), called from `gate_in_log` (:177†) and `session_probe.sh` (:14†) | `e1_ended` also requires E1's end entry in HEAD (`E1_END_PAT`). RC-O2 noted that the lock alone "does not implement 'waits for the end entry'". The message is reworded. The check is not before `rulings_ok`, as RC-O2 placed it, but after it, so that the existing unset-rulings cases keep their messages (the same reason rule F gave for RC2's placement) |
| **RC-O3** `halted` | **Yes** | `STOP_PAT` (common.sh:46†), plus sandbox cases | "ended by a stop" is added, so that arm A's stop-end entry also stops the scripts (M2) |
| **RC-O4** 9 (b) masks `refutes` | **Yes** | Owner question 9, verbatim | — |
| **RC-O5** seed 15's launcher | **Yes** | D3 point 4, verbatim | — |
| **RC-O6** duty (ii) | **Yes** | Duty (ii), verbatim | — |
| **RC-O7** evidence for G | **Yes** | Owner question G, verbatim. Point (3) is re-checked at 5f9f442 (git_facts) | — |
| **RC-O8** k_c = 5 in the rulings entry | **Yes** | D3 "Texts for headings 2 and 3", verbatim | A per-pick list under the rule is added (N5) |
| **RC-O9** owner point 7b | **No** | — | A new ruling key needs a pick, and "any other value needs another owner-proxy pass" (RD2). The proxy delta may take it. RC4's list keeps the rerun-or-not answer as per stop |
| **RC-O10** VM checkout script | **Yes** | New `vm_checkout.sh`, with 20 checks in its own sandbox section (and its refusals before E1's end entry and under E1's lock in point 18's section) | It refuses also before E1's end entry and the other headings (`gate_in_log`), from a dirty tree, and from a commit that the pin is not an ancestor of. It makes no push and no fetch (M10). "tmux `run` alive" is widened to any tmux session, as `launch.sh` does |
| **RC-O11** error field | **Yes** | `recheck_one.py`:49-51†. `test_control_due.py`: the changed assert, plus one new test | — |
| **RC-O12** citation | **Yes** | D3 point 14 cites the count check at common.sh:170† | The line is the patched file's, not 143 |

## Owner-proxy round 2

| Item | Where it went | Departures |
|---|---|---|
| **RD1** | The regex is verbatim at common.sh:43†. `gate_in_log`'s message is verbatim. `owner_rulings.txt`'s comment and README step 2 name both headings. The two sandbox cases are "RD1: the delegate's rulings heading, in its own words, committed with the file: the queue runs" and "RD1: a delegate's heading in the owner's words, committed with the file: no queue" (plus "RA5, RD1: a delegate's heading in the owner's words is not a rulings heading"). The outputs are saved in `docs/drafts/reg20_ops_r3/`. The `git diff --stat 56820bd <commit>` quote is in heading 3's text | (i) RD1 says it is "the only script change" and "Anything else needs a new round". Draft 3's diff holds RC2, RC3, RC-O2, RC-O3, RC-O10, RC-O11, RD-O1, RC6 (ii) and `e1_ended`, so the owner-proxy delta is that round (M12). (ii) The outputs are saved under `docs/drafts/reg20_ops_r3/`, as this draft's brief requires. At heading 1's commit they are copied beside the old ones in the ops folder |
| **RD2** | The six values are in `owner_rulings_rd2.patch`, for the rulings commit only. The heading is in D3 heading 2. "Not changed again … except by an (owner) [DECISION]" is mechanical (M1) | The entry quotes rule F rounds 2 **and 3**, because round 2 was NOT READY and a reject is binding (M11). The order "ops [DECISION], then this entry, then the start" is checked for the last two only, since the scripts do not check heading 1 (RD6's own sentence) |
| **RD3** | D3 heading 2's text, verbatim. Point 15's list gains (ii) and (vi). Duties (iii) and (xi) | (ii) and (vi) stay by hand (RD-O2 not taken) |
| **RD4** | D3 "The arm A hold" (M3) | (i) The name is "hold" (RC1). (ii) "while the queue's lock is held" becomes RC1's whole-hold rule, which is stricter. (iii) "the eight scripts" becomes nine (`vm_checkout.sh`). (iv) D1's seal row is named beside REG-24's. (v) RD4's apply-and-commit exception is kept, for files outside item 1's list. (vi) The closure output is quoted from `closure_20261114.txt` (scratch tree = 40948ba). RD4 asks for the output "at that commit", and heading 1's entry quotes it again then |
| **RD5** | D3 point 18. The RUNBOOK row 2a sentence is in `runbook_heading1.patch` | (i) "The scripts do not read E1's entries, so this rule is kept by hand" is replaced, because draft 3's scripts read E1's end entry and lock (`e1_ended`). The rest of the rule (an E1 rerun later) stays by hand. (ii) "Approved first" is RD5's, E1's [REG]'s and RC7's together: all three give E1 first (M2). (iii) The end-entry forms are RD5's two, and "ended by a stop" is added to `STOP_PAT` (M2) |
| **RD6** | Point 12: the sentence, with "freeze" read as "hold". Point 16: merged with RC1 (c). "The freeze": its first sentence and list are kept, marked ended, and RD4's text follows as the hold. README:130. The status lines name 56820bd. Draft line 29: verbatim, with draft 3's three added conditions after it. "Who decides" and heading 2: "(delegate), under the delegation …". Point 6: the wording | "with this owner-proxy pass and rule F round 2" becomes "with owner-proxy round 2 and its delta, and rule F rounds 2 and 3" (M11). Item map line 9: draft 2's map is not edited (as RC1 (g)) |
| **RD7** | D3 heading 3's text | It also names heading 1's commit and the hold's start |
| **RD8** | D3 point 10, verbatim. README. The status-notice text | — |
| **RD9** | Duties (iii), (v) and (ix) | — |
| **RD10** | RUNBOOK: `runbook_heading1.patch`. Open questions: text in D3 "Docs". `pending_copy`: D3 "Docs" and point 10a (iii) | The open questions are given as text, not as a patch, because this brief allowed edits only under `docs/drafts/reg20_ops_*` |
| **RD-O1** | **Taken.** `recheck_guards` (common.sh:526-527†), with one sandbox case | — |
| **RD-O2** | **Not taken** | It is a script change beyond the reviewed items. The delegate's RD3 (ii) and (vi) duties are clear by hand |
| **RD-O3** | **Not taken** | It needs both texts changed, and E1's is approved. With E1 first, a loan would run arm A inside E1's hold |

## Merges, conflicts and proposed resolutions

- **M1. RD1 + RC2 + RD2: the rulings heading.**
  - RC2 alone (the last commit that changed the rulings adds a rulings heading) allows, under RD1's regex, a second **delegate** heading in a later commit. That re-rules without the owner, against RD2's "except by an (owner) [DECISION]".
  - *Resolution:* the regex is RD1's, verbatim. RC2's check is kept, with its message naming both headings. `gate_in_log` also accepts a `RULINGS_DLG_PAT` heading at most once, and only as the first rulings heading (common.sh:159-161†).
  - The exact regexes are in D3 point 14.
  - The sandbox has seven cases:
    - the delegate's heading runs;
    - the delegate in the owner's words is refused;
    - a delegate after the owner is refused;
    - a second delegate is refused;
    - the owner overrules the delegate and it runs;
    - a ruling changed alone after the delegate is refused (the queue and `final.sh`);
    - a delegate after the start is refused.
- **M2. RC7 + RD5 + E1's [REG]: the order with E1.**
  - The three "first" definitions differ in form, and all three give E1 first now (DERIVED, D3 point 18).
  - *Resolution:* follow E1's registered rule, which is already in force (FILE(docs/decisions.md:17076)), and enforce the wait by script (`e1_ended`).
  - Arm A's end entry is RD5's two forms. "ended by a stop" joins `STOP_PAT`, so that an end by a stop also refuses every REG-20 script (RC7's "or an entry matching STOP_PAT").
  - The move back, from ce5f842 to 1cface7, is covered by heading 1, as DB10 (iii) asks (FILE(docs/decisions.md:18294)). It is made only by `vm_checkout.sh`, which refuses any commit that is not a descendant of the pin. `launch.sh:50` refuses any tree but the pin.
- **M3. RC1 + RD4: the hold.**
  - The list is the union (see RC1 (b)).
  - **Uncommitted edits.** RC1 forbids them for the whole hold, and RD4 only while the queue's lock is held. *Resolution:* RC1's rule is the stricter, and is taken. RD4's single apply-and-commit command is allowed for files outside the list, because its sub-second gap can only stop a copy (fail-safe).
  - **Seal rows.** RD4 forbids a new row. RC1 item 3 allows one after an entry that stops arm A. *Resolution:* forbidden by default. RC1's path is kept for a row that cannot wait. Its first step, a `STOP_PAT` entry, ends the hold, so the row commit is not a breach.
  - **The start of the hold.** Both reviewers start it at the start heading. That can fall while E1 runs (D3 notes this).
- **M4. RC6 (i) + RD8: VM removal.** RC6 bars it until `final.sh`'s files are committed, and RD8 until REG-20's [RESULT]. *Resolution:* RD8's, the later end.
- **M5. RC4 + RD3 (ii) and (vi).** Both RD3 stops wait for the owner, after bits may be visible. *Resolution:* both are added to RC4's list in point 15.
- **M6. RC5 + RD9: duty (v).** *Resolution:* RD9's sentence, then RC5's. RD3 (vi)'s counterfactual line is the same line as RC5's.
- **M7. RC3 + pick 7 `lost_open`.** Under the pick, RC3's narrowing of `not_run` has no effect. *Resolution:* the code is kept as rule F tested it, in case the owner rules `not_run`.
- **M8. RC1 (c) + RD6: point 16.** *Resolution:* RC1 (c)'s text, plus RD6's last sentence.
- **M9. RB6 + RC7 (b) + RC-O10: RUNBOOK:48.** *Resolution:* RB6's and RC7's words, verbatim, plus a parenthesis that names `vm_checkout.sh` (flagged).
- **M10. RB6's VM step + RC-O10.**
  - RB6's steps push main and fetch on the VM. E1's checkout fetched, because its move was forward to a commit the VM lacked.
  - Arm A's move is backward, to an ancestor of ce5f842, which is in the VM's clone (BELIEF that the clone is not shallow; the checkout fails otherwise).
  - *Resolution:* no push and no fetch. RB6's steps are kept as the record of the move.
- **M11. RD2/RD6 "rule F round 2" + a binding NOT READY.** *Resolution:* quote rounds 2 and 3.
- **M12. RD1 "the only script change" + RC2/RC3's tested patches + the optional code items.** *Resolution:* the proxy delta on draft 3 is RD1's "new round".
- **M13. RC-O2 + RC7 "waits for its end entry".** *Resolution:* `e1_ended` tests both the end entry and the lock.

## Added by this author (no item asked for it; flagged for round 3)

- **N1. `e1_ended`'s end-entry test, and its call in `session_probe.sh`.**
  - E1's `vm_checkout.sh` is run only by E1. Without the call, a REG-20 session probe during E1 would write a boot record that arm A later uses. It would also add a read on the VM during E1's runs, though `session_probe.sh` reads only.
- **N2. The disk point D** (DERIVED in D3):
  - with E1's expected six runs, 7 launches fit;
  - in E1's worst case, 4;
  - with no E1 run, 9;
  - all 11 planned runs need 4,524,512 kB free at the first launch;
  - the 27-launch ceiling needs 8,408,288 kB.

  It is the owner's, because deleting is not delegated.
- **N3. The RUNBOOK §4 clause for arm A** (`runbook_heading1.patch`), mirroring E1's.
- **N4. RC6 (ii) as code**, with three sandbox checks.
- **N5. The per-pick list under RC-O8's rule.**
- **N6. D1's seal row** (FILE(docs/drafts/d1_r1/withheld.patch:4)) is named in the hold. It was committed in 5f9f442 while this draft was written.
- **N7. A sandbox run that was stopped.** The first sandbox run of draft 3 (2026-11-14T02:28:44Z) was stopped after 172 ok and 0 FAIL, so that RC6 (ii)'s checks could be added. Its partial output stays in the writer's scratch folder and is not evidence. The saved run is the complete rerun.
