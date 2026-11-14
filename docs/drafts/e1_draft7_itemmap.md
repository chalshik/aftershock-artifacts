# E1 draft 7: item map (rule F round 2 and the owner-proxy's round-2 conditions)

Inputs:
- the review: `docs/drafts/reviews-2026-11-13/rulef-e1-draft6-r2.md` (NOT READY; DC1 and DC2 blocking);
- the reviewer's patches in `docs/drafts/e1_r3/`: `DC2_DC8_e1_vs_bundle.patch`, `DC2_test_e1_vs_bundle.patch`, `DCO1_*.patch`, `DCO2_*.patch`;
- draft 6: `docs/drafts/e1_draft6.md`, its item map, and bundle e1_r2;
- the owner-proxy's round-2 APPROVE: `docs/drafts/reviews-2026-11-13/proxy-e1-draft6.md` (DD1–DD12);
- the lead's instructions for draft 7.

Outputs:
- `docs/drafts/e1_draft7.md` (868 lines);
- the patches in `docs/drafts/e1_r3/`: `e1_py_draft7.patch`, `test_e1_draft7.patch`, `ops_draft7.patch`;
- the sandbox output `docs/drafts/e1_r3/sandbox_20261113T231637Z.txt`;
- bundle `docs/drafts/review_bundles/e1_r3/`.

Nothing in the main checkout's `analysis/`, `tests/`, `harness/`, `configs/`, `docs/probe/`, `agent/` or `docs/decisions.md` was edited. Line numbers below are draft 7's.

Every "verbatim" below was checked by script:
- each "Replace with" or "Append" text of round 2 (lines 40–234 of the review) occurs in draft 7's entry, except the four marked as departures;
- each owner-proxy replacement occurs, except the four marked as merged or not applied;
- the quoted round-2 review (lines 451–805), unquoted, equals the review file byte for byte (355 lines).

## Rule F round 2

| Item | Where in draft 7 | How | Note |
|---|---|---|---|
| DC1 (a) | L13, "What E1 can and cannot do" | verbatim | |
| DC1 (b) | L13, the bullet's last sentence but one | verbatim | |
| DC1 (c) | L42, "No floor" | verbatim | |
| DC1 (d) | L43, "In neither case", first sentence | verbatim | |
| DC1 (e) | L68, "Result, computed once", first clause | verbatim | Same wait added to README line 52 (DC-O3). |
| DC2, text | L32, "Holes" | verbatim | |
| DC2, code | `e1_py_draft7.patch` (`floor` and its docstring) | the reviewer's hunks, byte for byte | The patched `e1.py` has sha256 `428771e0…`, the same as the reviewer's `out/b/analysis/e1.py`. |
| DC2, tests | `test_e1_draft7.patch` (`test_floor_no_rows_and_holes`, `test_a_hole_just_below_lam_sat_is_a_hole`) | byte for byte | `dd3f52c5…`, the same as the reviewer's. 16 passed. On draft 6's `e1.py`: 2 failed, 14 passed. |
| DC3 | L68, "Result, computed once" | verbatim | |
| DC4, bullet | L61, "E1 holds the VM" | verbatim up to "… or under an owner's entry."; **last sentence replaced** (departure 1) | |
| DC4, RUNBOOK row | not applied; the lead's row instead (draft 7, "RUNBOOK, for the approval commit", (c)) | **departure 1** | |
| DC4, README | `ops_draft7.patch`, README step 9 | verbatim | |
| DC5, field list | L43, "In neither case" | verbatim | DD6(b) merged after it. |
| DC5, R3 | L22 | verbatim | |
| DC6 | L68, "Result, computed once" | verbatim | DD3 merged after it as one sentence. |
| DC7 | L35, "A floor exists" | verbatim | FILE(tests/test_e1.py:59) is the same line at HEAD and in the patched file (checked). |
| DC8 | `e1_py_draft7.patch`, line 1 of `e1.py` | byte for byte | |
| DC9 | L9, ID line | verbatim | Followed by one added sentence: REG-19's [RESULT] since written (the lead's item 4). |
| DC-O1, code | `ops_draft7.patch`: `common.sh` `settle`, `queue.sh` `report_settled` | the reviewer's three patches, byte for byte | `queue.sh`'s comment replaced as the review's text gives it; that change is not in `DCO1_queue.patch`. |
| DC-O1, added | `common.sh` `settle`'s header comment | added by this writer | The comment had gone stale when the code changed (DA12's practice). |
| DC-O1, text | L21, R2's parenthesis; L430, round-1 DA2 bullet | consequential wording | R2 named `report_settled` as the writer of the pause. |
| DC-O2, code | `ops_draft7.patch`: `common.sh` `next_step`, `test_sandbox.sh` | byte for byte | |
| DC-O2, text | L57, stopping rule | verbatim | A README stop-table row was added by this writer. |
| DC-O3 | `ops_draft7.patch`: README lines 3, 5, 9, 12, 39, 41, 52, 85; `queue.sh` 4–5; `vm_checkout.sh` 6–7 | done, as the item allows | README line 3's "Stale" list keeps only what is still stale (DESIGN_NOTES.md). Both comment paragraphs were rewrapped. |
| DC-O4 | L57, stopping rule | verbatim except one citation, renumbered (departure 3) | |
| DC-O5 | L47, "Reported, never judged" | verbatim | Followed by one added sentence: REG-21's first [RESULT] is in the log (FILE(docs/decisions.md:16421)). |

## Owner-proxy, round 2 (DD1–DD12)

The proxy's rule (its §2, opening): "If a round-2 item changes an anchor's text first, apply the DD to the same sentence as changed, keep round 2's words, and say so."

| Item | Where in draft 7 | How | Anchor moved? |
|---|---|---|---|
| DD1 | L449, `### Adversarial review, round 2 …, verbatim`: the quote at L451–805, then "What was changed because of it (round 2)" at L807, immediately before `#### Owner-proxy pass` (L826) | as given | No anchor; the section is placed where DD1 says. |
| DD2 | L827, the owner-proxy line | **changed** (departure 4) | The anchor is unchanged, now at L827 (draft 6, L448). |
| DD3 | L68 | **merged into DC6** (departure 5) | DC6 replaced DD3's anchor first. |
| DD4 | L38, "Prediction" | verbatim; the proxy's numbers kept | Unchanged. The anchor is at L38 (draft 6, L37). |
| DD5 | not applied | **not applied** (departure 6) | DC2 replaced DD5's anchor first. |
| DD6 (a) | L43, first occurrence, "In neither case" | verbatim | Unchanged (draft 6, L42). |
| DD6 (b) | L43 | **merged into DC5** (departure 7) | DC5 replaced the first half of DD6(b)'s anchor. |
| DD7 | the approval steps, not draft text | **its file names and sha256s are now draft 7's** (departure 8) | — |
| DD8 | the approval entry | later | Its (d) list needs this draft's departures added. |
| DD9 | after `e1_commit.txt` | later | Unchanged. |
| DD10 | the approval commit | later | Draft 7, "RUNBOOK, for the approval commit": (a) and (b) verbatim, with (c) the lead's row. Anchors FILE(agent/RUNBOOK.md:50) and FILE(agent/RUNBOOK.md:48) are unchanged since 97a6438. |
| DD11 | the ledger row | later | The numbers are unchanged. |
| DD12 | the registration commit's paths | later; **conflicts with draft 7** (finding 1) | — |

## Departures from a review's words

1. **DC4's RUNBOOK order.**
   - What changed:
     - round 2's RUNBOOK row (`| 1a (before 2) | E1 (runs from REG-19's recorded queue end; items 2 and 2a wait for E1's end entry, …) |`) is not applied;
     - the "E1 holds the VM" bullet's last sentence, which states the same order, is replaced. The replaced sentence: "The approval commit amends RUNBOOK §5's order to match: E1 runs from REG-19's recorded queue end, and REG-20's gate and arm A wait for E1's end entry."
   - What replaces both: the lead's rule, verbatim: "E1 and REG-20 arm A: whichever has its ops approved first runs first; the other launches only after the first's end entry ([OPS] … the queue ended …, or … ended by a stop …)".
   - Reason, from the lead's instruction for draft 7: the facts changed after the review.
     - REG-19's [RESULT] is in the log (FILE(docs/decisions.md:16517), commit 6748c26).
     - REG-20's gate was computed once (commit 3c8e5dc), so it cannot wait for E1's end entry.
     - REG-20 is owner-approved since 2026-11-12 (FILE(docs/decisions.md:4166)). Only arm A's ops decision is in review.
   - Added by this writer, for round 3 to check:
     - the bullet's sentence that, if REG-20 arm A runs first, E1's `vm_checkout.sh` and queue wait for REG-20's end entry by hand, because E1's scripts do not read REG-20's entries;
     - the matching README step-4 lines;
     - the phrase "or the commit REG-20 left it at" in the ID line, R6 and "Pre-launch and launch";
     - the §5 row's order cell, `2b (with 2a)`, which this writer chose.
   - Row 2a is not edited. The same rule belongs in REG-20's ops decision.
2. **The facts since round 2** (the lead's item 4). Every sentence that had E1 or the GPU wait for REG-19's [RESULT] is in the ID line (L9), and each now cites FILE(docs/decisions.md:16517):
   - the pin clause ("The VM stays at `a7bb77a` … until REG-19's [RESULT] is written") is now met;
   - draft 6's amendment of that clause is therefore dropped, with the reason stated;
   - "The rest of the pin rule stands: REG-19's table is computed …" is now in the past tense, with commit 047b95e;
   - draft 4's dropped wait, and the owner's possible restoring entry, now have nothing to wait for, so those two sentences are replaced;
   - the halt sentence is kept, reworded so that it does not refer to the removed clause;
   - the lost seed-18 folder: "which is now written";
   - RUNBOOK §4's "never before REG-19's [RESULT]" is met.

   Also in the header (L3), outside the entry's rule sentences: REG-21's and REG-22's batch-1 [RESULT]s and REG-20's gate. In "Reported, never judged" (L47): REG-21's first [RESULT] is in the log, so `e1.report`'s wait for it is met (DERIVED: `withheld.lifted`'s pattern, FILE(analysis/withheld.py:46), matches the heading at FILE(docs/decisions.md:16421); checked by script on that one line). The quoted reviews keep their words.
3. **Renumbered citations.** These follow from draft 7's script patch. The FILE lines below exist only after `ops_draft7.patch` is applied, as it will be at the registered commit; each sentence says "after draft 7's script patch".

   | Where | Draft 6 | Draft 7 |
   |---|---|---|
   | DC-O4's citation | `common.sh:217-219` | `common.sh:224-226` |
   | Stopping rule, `MAX_SAME` | `common.sh:24,260-262` | `common.sh:24,267-269` |
   | Round-1 change list, DA1 | `common.sh:24,187,235,260-262` | `common.sh:24,193,242,267-269` |
   | Round-1 change list, DA2 | `queue.sh:44,67-70` | `queue.sh:68-71` |
   | The new `settle` lines | — | `common.sh:164-167` |
   | The ID line, `vm_checkout.sh`'s forward-only check | (not cited) | `vm_checkout.sh:33` |

   Unchanged: `common.sh:38`, `:40`, `:98-108`, `:104` and `launch.sh:27`.
4. **DD2's text.** The anchor sentence is kept, followed by DD2's sentence with four changes:
   - "DD3 ("Result, computed once", merged into round 2's DC6 there)";
   - "DD6 ("In neither case"; its (b) merged into round 2's DC5 there)";
   - DD5 named as not applied, with the reason;
   - DD7 annotated: "draft 7's patches and sha256s take the place of draft 6's, so DD7's steps are run with them".

   One sentence is added: DC2, DC-O1 and DC-O2 need another owner-proxy pass. The placeholder holds the saved file's path, as DD2 says.
5. **DD3 merged into DC6.**
   - DC6's words are kept.
   - One sentence is appended with what DD3 adds:
     - the tilt is present only when `gate.cold_floor` gives "ok" on both sweeps (checked: `e1.onset` returns NaN unless both are "ok", and `observed` sets `tilt_reported` only for a finite onset);
     - the prediction is computed once, beside the result, with `uv run`;
     - it is reported as the tilt's description.
   - Not carried:
     - DD3's "replays the two configs through model F's server", for which DC6 says "model-F description … reads no run";
     - DD3's FILE(analysis/e1.py) tag.
6. **DD5 not applied.**
   - Its text says that a swept rate below λ_sat with no valid run, when no valid row lies below λ_sat, "is not a hole". It also says "it is disclosed, not changed, so that the code rule F reviewed is the code that runs".
   - After DC2's code change that is false. The same floor now gives "holes" with `missing_rates` [1.5, 2.0] (DC2's test, `test_a_hole_just_below_lam_sat_is_a_hole`).
   - The proxy's own N8 names this code fix as the alternative to DD5.
   - DC2 changes "holes", which the proxy's §3 puts under another owner-proxy pass, so that pass rules on it.
7. **DD6(b) merged into DC5.**
   - DC5's list and disclosure are kept: they name `end_ref_t` and `busy_samples`.
   - DD6(b)'s words are appended from "`end_ref_t` and `last_ok_scrape_t` show when that run's load ended" to "the [RESULT] lists every such read", verbatim.
   - Its opening "None of them holds a request count, throughput or KV, but" is not repeated: DC5's text already holds that sentence.
8. **DD7's sha256s.**
   - DD7 step 1 now applies `docs/drafts/e1_r3/e1_py_draft7.patch` and `test_e1_draft7.patch` (against HEAD's files; `git apply --check` passes on the main checkout).
   - Step 2's hashes are `428771e04a7a740bc87b20bc7959d835c56e0eebbfb822086248a373c200d415` (`analysis/e1.py`) and `dd3f52c579288cbe9a9a0144b98d2b880f2606eacea153fc268d232e6f6a750d` (`tests/test_e1.py`).
   - This is not draft text. The next owner-proxy pass restates DD7 or accepts it.
9. **The harness freeze.** It is worded as the lead gave it ("until both batch 2s are computed or declared not computed (expected on 2026-11-13/14)"), in a new bullet at L27. It cites REG-21's and REG-22's frozen lists, FILE(docs/decisions.md:9834) and FILE(docs/decisions.md:4748). Both lines list every `harness/*.py` file (checked by grep: `__init__`, `checks`, `config`, `env_snapshot`, `loadgen`, `recorder`, `run`, `trigger`, `workload`). After draft 7 was first written, both batch 2s were committed (7230ae8; [RESULT] headings at FILE(docs/decisions.md:16571) and FILE(docs/decisions.md:16798)). At the lead's instruction, one sentence was appended to the bullet saying the freeze has ended and the disclosure is moot; it was not deleted. E1's inputs are unchanged by that commit: `git diff --stat 3c8e5dc HEAD` over `analysis/e1.py`, `tests/test_e1.py`, `docs/probe/20261113_e1`, `agent/RUNBOOK.md`, `harness` and `configs` is empty.

## Code and scripts

- **`e1_py_draft7.patch` and `test_e1_draft7.patch`.**
  - Each is cumulative against HEAD's file: draft 6's patch, then the reviewer's DC2/DC8 patch, written as one diff. HEAD's `analysis/e1.py` and `tests/test_e1.py` equal e87884d's.
  - Check: in a fresh `git archive HEAD analysis harness configs tests pyproject.toml` copy under the scratchpad, both apply, and the files equal the reviewer's (`428771e0…`, `dd3f52c5…`).
  - With the repo's `.venv` interpreter, importing from the scratch copy (checked: `analysis.e1.__file__` is in the copy):
    - `tests/test_e1.py`: 16 passed;
    - `tests/test_e1.py tests/test_k2.py tests/test_withheld.py`: 39 passed.
  - Closures (`closure.py --at HEAD`):
    - `analysis/e1.py` is in neither `analysis/k3w.py`'s nor `analysis/c2.py`'s closure;
    - `analysis/e1.py`'s own closure is 27 files in all, as draft 6 says.
- **`ops_draft7.patch`** (repo-root paths; `git apply --check` passes on the main checkout; nothing applied).
  - It changes `common.sh`, `queue.sh`, `vm_checkout.sh`, `test_sandbox.sh` and `README.md`.
  - Applied to a fresh `git archive HEAD docs/probe/20261113_e1/ops` copy, it gives the scratch scripts byte for byte. Five files are unchanged: `vm_state.py`, `session_probe.sh`, `launch.sh`, `DESIGN_NOTES.md` and `e1_commit.txt` (`UNSET`).
  - The reviewer's two `test_sandbox.sh` patches both insert before `echo "--- every stop"`. They apply one after the other, DC-O1's cases first.
- **Sandbox.** `TMPDIR=<scratchpad> zsh <patched copy>/test_sandbox.sh`: `passed 192, failed 0` (PROBE(docs/drafts/e1_r3/sandbox_20261113T231637Z.txt)).
  - The count is 184 of draft 6, plus DC-O1's 4 checks and DC-O2's 4. The reviewer had 188 for each alone.
  - The output names the scratchpad path, as the committed draft-6 output does.

## Found while applying, not changed (for round 3, the owner-proxy and the lead)

1. **DD12 conflicts with draft 7.** DD12 says the registration commit "leaves `docs/probe/20261113_e1/ops/` as it is at 97a6438". Under draft 7, `ops_draft7.patch` (DC-O1, DC-O2, DC-O3, DC4's README edit) has to be applied to those files in the registration commit, with `e1_commit.txt` still `UNSET`. The sandbox is then run again in the repo. DD12's path list needs the five ops files. That is for the next owner-proxy pass.
2. **DC1's guard is text only.**
   - E1's seal is lifted by `AFTERSHOCK_UNSEAL=E1` alone (`analysis/withheld.py`).
   - `e1.report`'s only wait, REG-21's first [RESULT], is already met (departure 2).
   - So nothing in code stops `e1.observed`, `e1.floor_status` or `k2.observed` on E1's runs before E0's [REG]. A refusal keyed on E0's [REG] heading would need a code change in `e1.py`, and so another round. Not proposed here.
3. **DC1(a) leaves an older sentence in place.** It still reads: "Rule A1 and `docs/process.md` §3 say a run whose outcomes change no decision is not proposed. The owner has decided otherwise for this run …" After DC1 that premise no longer applies, since E1 changes E0's gate input. The sentence is not false (the owner's decision stands), but round 3 may want it reworded.
4. **Two meanings of "E1 has ended".**
   - DD6(a) allows the detail reads once E1 has "stopped on a rule that ends E1" (`no_errors`/`power_limit`, a second `gpu_steady`, one check in `failed` of two runs, the owner's halt).
   - DC4 defines E1's end by an entry, and "a stop that waits for a decision, is not an end".
   - Several of DD6(a)'s stops are "the owner decides" stops in the scripts. The reads may therefore start before any end entry exists. The two are consistent only if those reads count as part of the deciding.
   - DC-O2's new stop is in neither list.
5. **The order with REG-20 is kept by hand on both sides.**
   - E1's scripts do not read REG-20's entries or lock.
   - Round 2 found that REG-20's ops scripts do not mention E1.
   - If REG-20 arm A runs at a commit later than E1's registered commit, `vm_checkout.sh` refuses a backward move, and the owner decides. REG-20's registered commit 75e627e is an ancestor of HEAD (`git merge-base --is-ancestor`, exit 0), so a move from it to E1's commit is forward.
6. **Two lines still say the move starts at REG-19's pin.** README's file-table row for `vm_checkout.sh` and that script's line 2 still say "from REG-19's pin". DC-O3 did not name them, and they are not changed here.
7. **DESIGN_NOTES.md stays stale.** README line 3 lists what is stale, including that `settle` now writes the pause (I7).
8. **E2 inherits DC2's stricter holes rule** through `floor_status` (round 2's DC2, "Cost and side effect"; the proxy's N9). E2's registration must cite it.
9. **The account's home path appears in three places.**
   - DB6's command, carried verbatim since draft 6;
   - the sandbox output's temp path;
   - the saved review's last line.

   All are left as they are, as in draft 6 and the committed files.

## Not done

- No edit of `docs/decisions.md`, `docs/status.md`, `PROTOCOL.md`, `docs/claims.md`, `agent/RUNBOOK.md`, `analysis/`, `tests/`, `harness/`, `configs/` or `docs/probe/` in the main checkout.
- No run data read, no VM contact, no commit.
- Under `docs/probe/`, only the folder `20261113_e1/ops` was read, from `git archive HEAD` (tracked files only; no `state/`).
- REG-20's gate output file was not opened. Its "passed" is the lead's word, and the draft says only that the gate was computed.
