# E1 draft 6: item map (2026-11-13)

Where each item of the two reviews of draft 5 went in `docs/drafts/e1_draft6.md` (line numbers below) and in the code and scripts, whether it was applied verbatim, merged or not taken, and why. The reviews:
- rule F round 1: `docs/drafts/reviews-2026-11-13/rulef-e1-draft5-r1.md` (NOT READY; DA1–DA12 required, DA-O1–DA-O7 optional). Its tested patches (reviewer's scratchpad, `patch_*.diff`) were used only as a cross-check: the code lines of DA1 and DA2 in the repo equal the patches' lines.
- owner-proxy: `docs/drafts/reviews-2026-11-13/proxy-e1-draft5.md` (APPROVE on DB1–DB12; DB1–DB9 BEFORE, DB10–DB12 LATER).

"Verbatim" means the reviewer's replacement text is in the file, character for character. That was checked by a script that pulls each anchor and replacement out of the two review files, not by retyping them. Line numbers in the scripts are those of the main checkout's working tree when this map was written. `analysis/e1.py` and `tests/test_e1.py` are held as patches against HEAD (see "Note on `analysis/e1.py` and `tests/test_e1.py`" at the end); their line numbers are those of the patched copies in `docs/drafts/review_bundles/e1_r2/` (`e1.py`, `test_e1.py`).

Results: sandbox `passed 184, failed 0` (PROBE(docs/probe/20261113_e1/ops/sandbox_20261113T214307Z.txt)). `tests/test_e1.py`: 16 passed with both patches applied (first in the main checkout before 21:46 UTC, then in a scratch copy of `analysis/`, `harness/`, `configs/` and `tests/test_e1.py` run with the repo's `.venv` interpreter); 12 passed in the main checkout as it now stands (HEAD's two files).

## Rule F, required items

| Item | Where in draft 6 | Code / scripts | Status | Why / note |
|---|---|---|---|---|
| DA1 | L56 (stopping rule: "Likewise any other check …"); L21 (R2's last clause) | `common.sh:24` (`MAX_SAME`), `:187` (`nfail`), `:235` (count), `:260-262` (stop); `test_sandbox.sh:197,198,204` (three different checks), `:447-451` (new case); `README.md:76` (stop-table row) | verbatim; merged with DB4 | DB4's restart rule is kept as the registered rule and DA1's code as its enforcement. A sentence after DB4 (L56, "The scripts enforce this restart rule and are stricter than it in one case …") says where they differ. Also in `common.sh:182-183`: the `next_step` rule-list comment names the new stop (addition). |
| DA2 | L21 (R2's parenthesis) | `queue.sh:44` (`report_settled` writes `state/pause_pending.txt`), `:67-70` (the `launch` branch shows it and sets it aside); `launch.sh:27` (refuses while it exists); `test_sandbox.sh:255` (inserted case), `:453-458` (new block) | verbatim | `PAUSE=""` stays, unused (the review allows it). Comments made stale by the change were updated: `queue.sh:13-16` header, `:34-35` `report_settled` comment, `launch.sh:6-8` header (addition). |
| DA3 | L56 (two sentences) | none | verbatim | The README's stop table already handles pre-launch stops as restartable (`README.md:79-80`); DESIGN_NOTES I15 is now stale and is listed as such in README's first paragraph. |
| DA4 | L66 ("**The code is the registered code:** …") | none | verbatim; merged with DB6 | DB6 follows it verbatim. One added sentence (L66, end: "The two rules give one order: …") says that the registered code's floor is E1's floor under both rules. |
| DA5 | L9 (ID line: "nothing of REG-19 is lost: …") | none | text verbatim; RUNBOOK edits deferred | The two RUNBOOK edits are not made now (the lead: `agent/RUNBOOK.md` is not edited in this pass). They are merged with DB11's two edits into one proposal for the approval commit: "RUNBOOK" below. |
| DA6 | L40 (decision); L66 (result: "… with its SE (`floor_slope_reported`) …") | `analysis/e1.py:195-196`; test `tests/test_e1.py:169` (`test_observed_reports_the_floors_slope_on_rate`) | verbatim | The test was added by this draft's writer (the review checked the code on synthetic rows in scratch only). |
| DA7 | L42 ("In neither case") | none | verbatim | DB3's last sentence (L13) says that the decisions E1 changes are "the wording ones"; DA7 adds one that is not about wording. A sentence was added after DB3 (L13: "E1's validity record changes one more …"). See also "Found while applying" items 2 and 3. |
| DA8 | L53 | none | verbatim | |
| DA9 | L72 | none | **departure (one word)**; merged with DB7 | "at most 18 launches" → "at most 18 runs". The sweep is one launch for six runs, so 18 runs take 13 launches (DA1's own trace: "13 launches (the sweep plus 12 single rates)"), or 19 when the sweep's launch fails before any rate starts (every rate then gets three single-rate launches). The ceiling of 6.3 h is per run (6 × 3 × 1260 s), so "runs" is the right noun. DB7: see below. |
| DA10 | L12 (RUN tag); L18 (4200/4209, DERIVED no cap, 4201); L9 (`common.sh` lines); L56 (`run.py:80`) | none | verbatim but one, **renumbered** | `common.sh:96-104` → `common.sh:98-108`: the same `ready_to_run` comment and function, moved by this draft's edits (DA1's `MAX_SAME` line, DA-O1's longer comment, DA-O2's line). The owner-proxy's §3 says renumbering FILE citations needs no new pass. The DERIVED "no cap" was rechecked by this writer from the configs alone (`e1._cfgs` on the sweep and the six single-rate configs: no `cap` key in `workload.sessions`). |
| DA11 | L18 | none | verbatim | Rechecked 2026-11-13: `harness/` tree `e8a3e1e7425da486327884d093055e0846229d38` at 9e249b1, e87884d and the working HEAD; the text's `git diff --quiet 9e249b1 HEAD -- …` exits 0; `git diff --stat a7bb77a 9e249b1 -- harness/` gives 4 files, 163 in, 29 out. |
| DA12 | none | `queue.sh:2`, `:4-5`; `vm_checkout.sh:6-7`; `common.sh:3-4`; `DESIGN_NOTES.md:67`, `:122` (§2 item 12), `:165` (R6) | verbatim; comment lines rewrapped | The words are the review's. Comment lines were rewrapped to the files' width. DA12 conflicts with DB9's "scripts unchanged" (see "DA and DB conflicts"). |

## Rule F, optional items

| Item | Where in draft 6 | Code / scripts | Status | Why / note |
|---|---|---|---|---|
| DA-O1 | L9 (ID line) | `common.sh:38` (`END19_PAT`); `test_sandbox.sh:36` (the heading `(QUEUE DONE)`) | verbatim, **extended** | Additions by this writer: the `END19_PAT` line's trailing comment and the `ready_to_run` comment (`common.sh:98-101`) name the two end lines; the refusal message adds "(the [OPS] heading must end '(QUEUE DONE)' or '(QUEUE END futility stop)')", and its old words are kept so that the existing cases still match; three sandbox cases (`test_sandbox.sh:460-466`: the futility-stop end passes; a `(QUEUE STOP …)` heading and a bare heading are refused). |
| DA-O2 | L59 (a bullet of the stopping rule) | `common.sh:104` (`ready_to_run`'s first line after `MSG=""`) | verbatim, **extended** | Four sandbox cases added by this writer (`test_sandbox.sh:468-473`: the queue, `launch.sh` and `vm_checkout.sh` refuse; nothing launched, the VM's tree not moved). The review's code line also accepts `[CORR] (owner) E1 halted`, which the text does not name; kept as given (it can only stop more). README stop-table row added (`README.md:78`). Merged with DB2 (see "DA and DB conflicts"). |
| DA-O3 | none | none | **not taken** | It changes the stopping rule for lost runs (a pre-registered rerun after a power-off), which the owner-proxy's note N3 leaves to the owner (N3: "This changes the stopping rule, so it is your choice"). A run that ends without `checks.json` still stops E1 until a new decision. Recorded in draft 6 at L441. |
| DA-O4 | L31 ("Holes") | `analysis/e1.py:162-164` (and the docstring, `:152-155`); test `tests/test_e1.py:143` (`test_a_hole_just_below_lam_sat_is_a_hole`) | verbatim | The test was added by this writer. The docstring of `floor` was updated to match (addition). The owner-proxy's §3 lists "holes" among changes that need another proxy pass. |
| DA-O5 | L22 (end of R3) | none | verbatim | "DA7's fields" stays as written: the review is quoted in full in the entry (L77 on), so the label can be looked up. |
| DA-O6 | none | `analysis/e1.py:249`; test `tests/test_e1.py:183` (`test_report_counts_only_the_runs_first_valid_keeps`) | verbatim | The test was added by this writer. |
| DA-O7 | L9 (ID line: "needs the VM moved back first: …") | none | verbatim; merged with DB10(iii) | Added sentence (L9, last): "The move back is not covered by this entry's approval: it needs its own entry, as the REG-19 rerun it serves does." DB10(iii) and the owner-proxy's N6 say the move back needs its own entry; DA-O7 gives the steps and an [OPS] record. Both are kept. |

## Owner-proxy items

| Item | Where | Status | Why / note |
|---|---|---|---|
| DB1 (BEFORE) | L7 | as the lead instructed | The heading's date is `<date of append>`, to be replaced by the UTC date on which the entry is appended. |
| DB2 (BEFORE) | L9 | verbatim; merged with DA-O2 | Added sentence after DB2's last one: "The scripts see such an entry only when it is headed as the owner's halt (the stopping rule, FILE(docs/probe/20261113_e1/ops/common.sh:104)); an entry of any other form is applied by hand: no queue start and no launch after its commit." DB2 says that an owner's [DECISION] or [CORR] restoring the pin clause stops further launches, but no script reads such an entry unless it carries DA-O2's heading. |
| DB3 (BEFORE) | L13 | verbatim; merged with DA7 | Added sentence: "E1's validity record changes one more, about other runs on this harness (the same section, "In neither case")." |
| DB4 (BEFORE) | L56 | verbatim; merged with DA1 | Added sentences after it: the scripts are stricter in one case. DA1's `MAX_SAME` stops on one check in `failed` of two runs at one rate, which DB4 would allow to restart. `gpu_steady` in two runs stops by the heat rule. One `no_errors` or `power_limit` stops at once. So the code stops in every case DB4 stops, before any launch, and in one more (two runs at one rate). |
| DB5 (BEFORE) | (a) `tests/test_e1.py:132`; (b) L15; (c) L75 | (a), (b) verbatim; (c) **departure** | (c) says "13 tests". Draft 6 has 16: DB5's test, plus one test each for DA6, DA-O4 and DA-O6, added by this writer because those three code changes had been checked only in a reviewer's scratch copy. On a scratch copy of e87884d's `e1.py`, these three tests fail and the other 13 pass. (d) holds: 16 passed. |
| DB6 (BEFORE) | L66 | verbatim; merged with DA4 | See DA4. DB6's command contains the account's home path (`/Users/<account>/Projects/aftershock-artifacts/.venv/bin/python`), as `common.sh`'s `R` does; kept verbatim. |
| DB7 (BEFORE) | L72 | merged into DA9 | DA9 replaces the same anchor and already holds DB7's ceiling and derivation (6.3 h; 6 × 3 × 1260 s). DB7's "and less under the stops" is kept as a sentence of its own: "Every other stop only lowers that ceiling." |
| DB8 (BEFORE) | L77 (heading), L79–L424 (the review, each line prefixed "> "), L426 ("What was changed because of it", item by item), L447–L448 (the owner-proxy line) | as the lead instructed | The quoted block includes the saved file's three-line header ("Saved by the agent …"). Unquoting the block gives back the file byte for byte (checked). |
| DB9 (BEFORE) | `README.md:3` (a); `README.md:73` (b) | (b) verbatim; (a) **rewritten** | DB9 keeps the scripts unchanged and fixes only the README. DA1, DA2, DA12, DA-O1 and DA-O2 change the scripts anyway, so DA12 is applied and (a)'s paragraph is written with only the facts still true. Dropped: the stale `queue.sh` and `vm_checkout.sh` header comments and DESIGN_NOTES' `RESULT19_PAT` (fixed by DA12), and "The scripts are left unchanged …" (false now). Kept: "Read with the registration as entered …", the draft-4 citations, "Nothing here is committed or reviewed", the code waiting for the recorded queue end, and "Step 5's move …". Added: README step 4's heading form (DA-O1), and DESIGN_NOTES I7, I3, I4, R2 and I15 as stale under DA1–DA3. Also updated: the README's test line (184 of 184, the new PROBE) and two stop-table rows (DA2's launch-by-hand refusal, DA-O2's halt). |
| DB10 (LATER) | not applied | later | Goes into `[DECISION] (delegate) E1 approved` in the approval commit: (i) the pin-clause amendment, (ii) README step 5 approved, (iii) a move back not covered, (iv) no launch before the checkout's [OPS] entry and the session probe. The approving entry should also quote DA4's closure output and DA11's `git diff --quiet` (both say so). |
| DB11 (LATER) | not applied | later; merged with DA5 | See "RUNBOOK" below. |
| DB12 (LATER) | not applied | later | The `docs/model.md` ledger row, in the approval commit, before the first launch. |

## Every departure from verbatim
1. **DA9:** "at most 18 launches" → "at most 18 runs" (reason above).
2. **DA10:** `common.sh:96-104` → `common.sh:98-108` (renumbered). Also, outside the review items, draft 5's `common.sh:38` (APPROVE_PAT) → `common.sh:40` (L60), for the same reason.
3. **DB5(c):** "13 tests" → "16 tests" (three added tests).
4. **DB9(a):** the paragraph is rewritten with the facts still true (details above).
5. **DA12:** comment lines rewrapped. More comments brought up to date beyond DA12's list: `common.sh` `ready_to_run` and `next_step` comments, `END19_PAT`'s trailing comment, `queue.sh`'s header and `report_settled` comment, `launch.sh`'s header.
6. **DA-O1:** a longer refusal message, and three sandbox cases (additions).
7. **DA-O2:** four sandbox cases and a README row (additions).
8. **Merges** (each keeps both reviewers' text verbatim and adds one sentence): DB4 + DA1, DA4 + DB6, DB3 + DA7, DA-O7 + DB10(iii), DB2 + DA-O2, DA9 + DB7.
9. **Header and change sections of draft 6** (above and below the entry) are new text: the header (round 2, sandbox 184, the reviews), "What was changed because of it", the owner-proxy line, and "Changed from draft 5".

## DA and DB conflicts, and how each was resolved
- **DA1 vs DB4** (a code stop at two runs vs. a restart rule at two rates). Both kept. DB4 is the registered restart rule, with an [OPS] entry per restart. DA1's `MAX_SAME` enforces it in code and is stricter where they differ: two failing runs at one rate stop E1 under DA1 and would allow a restart under DB4. This is stated in the text (L56).
- **DA4 vs DB6** (frozen closure vs. a worktree floor). Both kept. They agree: the registered code's floor is E1's floor, and the two codes differ only after a [CORR]. One sentence says so (L66).
- **DA5 vs DB11** (RUNBOOK anchors). DA5's text sentence is applied. The RUNBOOK edits are merged into one proposal for the approval commit (below). RUNBOOK is not edited now.
- **DA12 vs DB9** (edit the script comments vs. keep the scripts and fix only the README). DA12 is applied, because DA1, DA2, DA-O1 and DA-O2 change the scripts anyway, so DB9's reason ("so that the reviewed text is what runs") no longer holds. DB9(a) is rewritten; DB9(b) is verbatim.
- **DA9 vs DB7** (the same anchor). DA9 is applied; DB7's content is in it, and DB7's "less under the stops" is a sentence of its own.
- **DA7 vs DB3** (DB3: the decisions E1 changes are "the wording ones"; DA7: the validity record changes a decision about other runs). Both kept, with one sentence after DB3.
- **DA-O7 vs DB10(iii)/N6** (DA-O7: the move back is done by RUNBOOK §4's steps with an [OPS] record; DB10(iii): the move back is not covered by E1's approval and needs its own entry). Both kept, with one sentence.
- **DB2 vs DA-O2** (DB2: an owner's [DECISION] or [CORR] restoring the pin clause stops launches; the scripts see only DA-O2's halt heading). Both kept, with one sentence saying how other entry forms are applied.
- **DA-O3 vs N3**: DA-O3 is not taken (N3 leaves it to the owner).
- **DA7 vs owner-proxy §3, fourth bullet** ("reading any E1 run beyond `valid` and `failed` before E1's [RESULT]" needs another proxy pass). DA7 allows ten detail fields of a failed `recorder` or `gpu_steady` check after E1's queue has ended, which can be before E1's [RESULT]. Applied verbatim; the next owner-proxy pass must rule on it.

## RUNBOOK: one proposal for the approval commit (DA5 + DB11 merged; not applied)
In `agent/RUNBOOK.md` (anchors checked at the working tree on 2026-11-13: line 50 for (a); line 48, item 6, for (b)):

(a) Replace
```text
## 4. Deploying `main` to the VM (only between items, never during a run, never before REG-19's [RESULT])
```
with
```text
## 4. Deploying `main` to the VM (only between items, never during a run; never while REG-19's queue may run, nor before its end is recorded (E1's gate); never while E1 has not ended: E1 moves the VM only with its own `docs/probe/20261113_e1/ops/vm_checkout.sh`, to E1's commit, detached, once REG-19's queue end is recorded: decisions.md, [DECISION] (delegate) E1 approved)
```
(DA5's "never before REG-19's queue has ended (E1's gate); never while E1 has not ended: E1 moves the VM only with its own `…/vm_checkout.sh`" and DB11(a)'s "never while REG-19's queue may run; E1's `vm_checkout.sh` moves the VM to E1's commit, detached, once REG-19's queue end is recorded: decisions.md, [DECISION] (delegate) E1 approved".)

(b) Replace `then deploy HEAD (§4); then` with
```text
then, once E1 has ended (its queue printed QUEUE DONE or QUEUE END, or a stop that ends E1 is recorded) and never while E1's queue lock exists, deploy HEAD (§4; if the VM is at E1's commit, detached, `git checkout main` comes first); then
```
(DA5's "once E1 has ended (…)" and "after `git checkout main` on the VM, whose HEAD E1 leaves detached"; DB11(b)'s "if the VM is at E1's commit, detached, `git checkout main` comes first, and never while E1's queue lock exists".)

## Found while applying, not changed (for round 2 and the lead)
1. **DA9's "18 launches"** is wrong as a count of launches (13, or 19); changed to "runs" (departure 1).
2. **DA7's readable fields carry DA8's bit.** `recorder`'s `end_ref_t` is the time of the `load_end` event (FILE(harness/checks.py:109)), and `last_ok_scrape_t` is near it. A rate the server keeps up with ends its load early (DA8), so these fields show the same one bit per rate that DA8 discloses. They show it only for runs with `recorder` in `failed`. DA7's sentence "None of them holds a request count, throughput or KV" is true, but the disclosure does not mention this. No text was changed; round 2 may want DA8's disclosure to cover it.
3. **DA7 against the owner-proxy's §3** (above): the next proxy pass must rule on the detail reads after the queue's end.
4. **"Result, computed once" says `e1.report` prints "the tilt with its prediction".** `report()` returns `observed()` plus the work rates, and `observed()` gives `tilt_reported` but never calls `prediction()` (FILE(analysis/e1.py:184-200, 242-252), with draft 6's edits). The same text says "the open-loop floor recomputed the same way", but `floor_ol` is `saturated(ol)`: `gate.cold_floor` without the tail fallback or the holes check. Both date from draft 5, and neither review raised them. Not changed here: either the text or `report` must change, and that is for round 2.
5. **A residual gap in DA2.** `settle` writes `settled_<attempt>.txt`, and `report_settled` then appends to `pause_pending.txt`. If the queue process dies between the two, the restart finds the attempt settled and never writes the pause. The window is two shell statements. DA1's stop and DB4's rule still bound a systematic fault.
6. **Where DA1's stop sits.** `MAX_SAME` is tested inside the rate loop, after the spent-attempt check, like the heat and `no_errors` stops. When every rate without a valid run is spent, the queue therefore ends with `QUEUE END` and does not print the `MAX_SAME` message, even if a check is in `failed` of two runs. No launch follows in either case, so "stops E1" holds.
7. **N7 (the e1.py docstring still names draft 4).** N7 left it unchanged so that judged code would not be touched at registration. Draft 6 changes `e1.py` anyway (DA6, DA-O4, DA-O6), so that reason no longer applies. Left unchanged; the lead decides.

## Note on `analysis/e1.py` and `tests/test_e1.py`
- This writer edited `analysis/e1.py` in the main checkout at 21:38 UTC while REG-19's queue was running. That queue requires `analysis/`, `harness/` and `configs/defaults.yaml` to equal HEAD before each step (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:207)), so the edit stopped it before seed 19's step at 21:46 UTC. The agent restored the file to HEAD, saved the change as `docs/drafts/e1_r2/e1.py.draft6` and `e1_py_draft6.patch`, and started the queue again; it ended QUEUE DONE (decisions.md 2026-11-13 [OPS] "REG-19: the queue stopped before seed 19's step …" and [CORR] "The agent let a subagent edit `analysis/e1.py` …", commit 538f400). The writer did not know about that guard. The lead's task asked for the code change; the edit is still the error the [CORR] records.
- Following the [CORR]'s rule (code changes as patch files), `analysis/e1.py` is not edited again in the main checkout. `tests/test_e1.py` was written back to its HEAD text (by writing the file, not by git checkout): with HEAD's `e1.py`, the three new tests fail, and `uv run pytest` would then fail for any session that needs it to pass.
- Both changes are in `docs/drafts/review_bundles/e1_r2/`: `e1_draft6.patch` and `test_e1_draft6.patch` (against HEAD; `git apply` of both onto HEAD's two files gives the bundle's `e1.py` and `test_e1.py` byte for byte, checked), and the patched files themselves. The bundle's `e1.py` is byte-equal to the agent's saved `docs/drafts/e1_r2/e1.py.draft6` (sha256 `615e386f…`).
- The scripts under `docs/probe/20261113_e1/ops/` are edited in the main checkout. No queue guards that path, and REG-19's queue has ended. Their diffs against e87884d, which equals HEAD for these files, are in the bundle's `code_diffs_vs_e87884d/`.
