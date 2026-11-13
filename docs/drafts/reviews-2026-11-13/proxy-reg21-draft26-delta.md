# proxy-reg21-draft26-delta (proxy-reg21-d26), verbatim

Saved by the agent from the teammate message received in the main session transcript (message timestamp 2026-11-13T18:08:54.915Z; message 1 of 1 from this teammate). Round 4. Item names CF1–CF8 are this round's.

---

Owner-proxy, round 4 (the text written under the stop), REG-21 draft 26 (bundle reg21_r19): APPROVE, on CF1–CF7 BEFORE the entry is appended and CF8 LATER, in the [DECISION] (delegate). (Sent to team-lead: SendMessage to "main" was refused as addressing myself.)

# Decision: APPROVE on CF1–CF8

- **Bundle:** reg21_r19, HEAD 0d86f02. Today's HEAD is 128fd88.
- **Copies:** `registration_draft26.md` is byte-identical to `docs/drafts/reg21_draft26.md`. `item_map.md` is byte-identical to `docs/drafts/reg21_draft26_itemmap.md`. The draft 25 copy is byte-identical to `docs/drafts/reg21_draft25.md`.
- **Classes** (BI-S1 rule: class, and whether the item concerns batch 2's standing):

| Item | Class | Concerns batch 2's standing |
|---|---|---|
| CF1 | disclosure, reporting duty | no |
| CF2 | stricter rule | yes (it limits the one way back to "primary"); under the stop entry's rule 5 it is applied as usual and no further stop exists |
| CF3 | wording | no |
| CF4 | wording, reporting duty | no |
| CF5 | wording (a correction) | no |
| CF6 | reporting duty (process.md §3) | no |
| CF7 | disclosure | no |
| CF8 | reporting duty | no |

- **None is a design change.**
- **Anchors:** every anchor below occurs exactly once in `registration_draft26.md` (my substring counts).

## My checks (no runs/, state/, queue_*.txt, RESUME.md, backups or tool outputs opened)

**Round 3's texts in draft 26, by substring check against the three saved proxy messages:**
- BJ8 (P3, 2506 characters) is verbatim, at P3's anchor.
- BJ9, BJ10, BJ11(a) and BJ11(b) are verbatim.
- BJ14(a)–(h) are verbatim. Each anchor is gone except line 253's "nine", which is history, as BJ14(e) says.
- BJ1 is verbatim with "(i)–(x)".
- BJ2, BJ3, BJ4(a), BJ4(b), BJ5 and BJ7 are verbatim.
- BJ12 is absent (withdrawn).

**Rule F round 18's texts:**
- BI2, BI4b, BI5's trigger edit, BI6, BI7, BI8 and BI-O1 are verbatim.
- BI5's (ix) addition is not verbatim. Line 284 added "on 2026-11-12" to it, and line 284 discloses that.

**FILE citations at HEAD:**
- `load.py:183` and `1cface7:analysis/load.py:179` are both the `("n", "vllm:num_requests_running")` line. At 1cface7, `k1.py:79` and `:91` take `end["n"]` from `_level`. So BI4 is right and BJ3's "the request count" is wrong.
- These also hold: `checks.py:67/69/237`, `check_docs.py:41/196`, `test_check_docs.py:57`, `vm_state.py:3–4`, `common.sh:36`, `withheld.py:51`, `load.py:11/20`, `k1.py:57`, and decisions.md:4084, 4205, 4276, 4279, 4406, 4428, 4437, 4453, 4541 and 4231 (the delegation).
- `agent/INGEST.md:69` says the review-2 findings "survive as two sentences in status.md:15". That supports line 9's new tag.

**Commit times (UTC):**

| Commit | Time | What |
|---|---|---|
| 72fafb5 | 2026-11-12 19:00:16 | `tol_level`/`tol_spread` 0.05 first in `k3w.py` |
| 3f5c84a | 20:07:42 | `busy_min` 0.99 |
| d80b955 | 16:19:45 | |
| 1cface7 | 15:33:58 | |
| 54a995d | 15:53:46 | |
| d960ef3 | 2026-11-13 16:43:16 | |

**Freeze and closure:**
- `git diff --stat 8164211 HEAD` over the 26 frozen files is empty.
- BJ4(a)'s shadow command over `8164211..HEAD` prints nothing.
- The bundle's closure output lists the 26 files of line 104.

**Line diff (draft 25 to 26):**
- Changed lines: 1, 3, 4, 9, 49, 54, 71, 104, 111, 112, 113 and 127, plus lines 261–284 appended.
- No line before the change log moved.
- **The item map is stale.** It predates line 284 ("Agent's wording fixes before round 4"). Line 284 changed line 9, the "3 to 25" count, BI5's date, and line 54's "**None of this is a switch after this entry** (read (x), made before it, is the trigger's case, above)". The item map's "untouched" and "left verbatim" for those places no longer hold.
- I accept all four as wording, the last as a needed fix: it makes the sentence agree with BI7 and with (x). Each is to be listed in the [DECISION] (CF8).

**Inputs only, the agent's own session (8c5f8396 = the autonomous agent, FILE(agent/LOG.md:5)):**
- tool_use line 265: Read of the whole `RESUME.md` at 2026-11-12T18:28:18Z.
- Line 2302: `cat RESUME.md | cut -c1-1800` at 20:28:32Z.
- Lines 6720 and 7544: `head -3` and `sed -n 18,22p` on 2026-11-13.
- Line 6730: an edit at 11:38Z.
- The agent's ingest record says "`docs/probe/20261111_reg19/ops/RESUME.md`, … | in full" (FILE(agent/INGEST.md:15)).

## Q1. Round 3's conditions, and the two departures

- **Verbatim:** yes for BJ1–BJ5 and BJ7–BJ11 (BJ6 and BJ13 are for the [DECISION]) and BJ14(a)–(h).
- **BJ14(i) was applied too narrowly.** Line 71 changed only its parenthesis. But line 71's ceiling ("in n runs whose r had not been computed when the tolerance was fixed") and line 113's duty to keep that wording "exactly" both still read as a reading on unread runs (CF3, CF4).
- **BJ3 ("the request count"):** honest, but not acceptable as written.
  - It leaves a phrase in an append-only [REG] that the code shows is false, next to a sentence saying "not a request count".
  - P1 sends "BJ1–BJ7 written other than as given" to another proxy pass. This is that pass, and I approve the change (CF5).
- **BK4 (what RESUME.md quotes):** right not to open the note; not acceptable as worded.
  - Not opening it is right. The delegation does not cover "reading outcome data a pending registration withholds" (FILE(docs/decisions.md:4231)). Whether the note holds such data is the open question. And BK4's consequence (the trigger, so retrospective) is already in force for REG-21.
  - **First problem:** "the agent may not open the note under its delegation" is stated as a rule, but it is the agent's reading of that exclusion.
  - **Second problem, the real one:** the sentence hides that the agent's own session read the whole note on 2026-11-12 at 18:28:18 UTC (FILE(agent/INGEST.md:15), "in full"). That was 32 min before the 0.05 on r was first committed (72fafb5, 19:00:16) and 99 min before busy ≥ 0.99 (3f5c84a, 20:07:42). BJ8's Timing sentence ("Both came after (x), in the autonomous agent's commits, not session fdf13821's") is true. Read with "the agent may not open the note", though, it suggests that whoever fixed the thresholds saw none of it.
  - BK4's list also dates "by Read at 18:28 and 18:43 UTC" after a 2026-11-13 time, so the date is ambiguous.
  - **Fix:** CF1, which discloses this and adds an owner-check duty parallel to BI-O3.
- **Other departures in the item map** (BI1 at BJ8's anchor, BI2 inline, BI4 not repeated, BI8 at the end of line 4, BI-O2 not taken, BI1's "[RESULT]" not repeated): acceptable.
- **Line 111's last sentence** still restates the trigger without BI5's exception. Batch 2 is already retrospective, so this has no consequence. I leave it.

## Q2. Is anything false, or worded as if a batch were blind or confirmatory?

- **False:** BJ3's "the request count" (CF5). BK4's "may not open" with the agent's full read left out (CF1).
- **Readable as confirmatory:**
  - Line 71 still gives a live wording ceiling for batch 2: "in n runs whose r had not been computed when the tolerance was fixed".
  - Line 113 tells the batch-2 [RESULT] to keep "whose r had not been computed" exactly.
  - Line 73 says "Batch 2's J1 inside" does not apply to a retrospective batch 2, so the text contradicts itself.
  - After (x), and after the agent's 18:28 read of the note, that phrase in a [RESULT] would read as a blind test (CF3, CF4).
- **Batch 1:** lines 4, 49, 52 and 66 ("read retrospectively"), BI8 and line 75 are clear. "Judged" is the registration's term for its tolerance comparisons, and line 4 limits what it may claim. No other change is needed.
- **Restoring batch 2's standing:** "only the owner can, by an entry made before batch 1 is computed" matches the plan (plan_2026-11-13.md:54). But batch 1 can come after S: line 102 lets batch 1 proceed from S if REG-22 is late. An entry made after REG-19's table, which fixes r's first factor, would not be blind. Line 55 already times the owner's overrule of the two-batch rule against batch 1, any U/r print and S. CF2 applies the same timing. It is stricter than the plan and costs the owner nothing they would want.

## Q3. Would the owner approve?

- **Yes (BELIEF as to the owner).** The text does what the owner's plan says for a third round still NOT READY: "register batch 1 alone, label batch 2 retrospective by design, and stop iterating" (FILE(docs/drafts/plan_2026-11-13.md:64)).
- **Batch 1:** computed once by the registered command after the entry is appended, and not before REG-22's [REG] and [DECISION] (delegate) are committed (or S, line 102). The definitions come first (line 119), and so does the status.md notice (line 112).
- **Batch 2:** computed once after REG-19's final [RESULT] and batch 1's [RESULT], frozen as registered. It is labelled retrospective by design and never governs.
- **What this approval does not cover:** rule F round 19's items, which I have not seen (next section).

## Conditions

### CF1 (BEFORE; disclosure and reporting duty; line 54, BK4's sentence)

Replace:
`the agent may not open the note under its delegation; the owner can.`

with:
`the agent does not open the note again: whether it holds lines a pending registration withholds is the open question, and reading such lines is not delegated (FILE(docs/decisions.md:4231)); the owner can. Of these calls, the Read of the whole note at 2026-11-12 18:28:18 UTC and the print of its first 1800 characters per line at 2026-11-12 20:28:32 UTC were made in the autonomous agent's own session (8c5f8396, FILE(agent/LOG.md:5); tool-call inputs, lines 265 and 2302), whose ingest record lists the note as read "in full" (FILE(agent/INGEST.md:15)); so were the reads of 2026-11-13 at 11:38 and 12:07 UTC and the edit at 11:38 UTC, and the reads of 2026-11-13 00:39 UTC and 12:04–12:23 UTC were made by its subagents (rule F round 11, BK4's trace). The first came 32 minutes before the 0.05 on r was first committed (72fafb5, 2026-11-12 19:00:16 UTC) and 99 minutes before busy ≥ 0.99 (3f5c84a, 20:07:42 UTC) (DERIVED), so whatever the note quotes was in the agent's context before it fixed both; "Timing" under (x) below is read with this. The batch-2 [RESULT] states what the owner found the note to quote of REG-19 runs' run-time lines, or that it was not checked (round 4's owner-proxy, CF1).`

### CF2 (BEFORE; stricter rule; line 54, after BJ8's text, which stays verbatim)

Replace:
`only the owner can, by an entry made before batch 1 is computed.`

with:
`only the owner can, by an entry made before batch 1 is computed. Such an entry counts only if it is also made before the other two points at which the next bullet's owner's overrule stops counting as blind (any computation that prints U, an uncached-token rate or r on a batch-1 or reference run, and S), timed as that bullet times them, and if it states what its author had seen of REG-19's runs, read (x) and the reads of the note under (i) included (round 4's owner-proxy, CF2).`

### CF3 (BEFORE; wording; line 71)

Replace:
`- **Batch 2's J1 inside** (with five runs the likeliest outcome of the one item that would have been unread;`

with:
`- **Batch 2's J1 inside** (while batch 2 is labelled retrospective by design under read (x), this line does not apply to it ("The two batches"); it is kept as the ceiling that would have applied; with five runs the likeliest outcome of the one item that would have been unread;`

### CF4 (BEFORE; wording and reporting duty; line 113)

Replace:
`and keeps the wording "whose r had not been computed" exactly.`

with:
`and keeps the wording "whose r had not been computed" exactly if batch 2's standing is restored; while it is labelled retrospective by design (read (x)), it uses none of the wording of "Batch 2's J1 inside", those words included: it calls batch 2 a second retrospective reading and names read (x) and the reads of the note under (i) (round 4's owner-proxy, CF4).`

### CF5 (BEFORE; wording, a correction; line 49; two replacements)

(a) Replace:
`the request count in the end window and percent fast in the baseline`

with:
`the mean running batch in the end window and percent fast in the baseline`

(b) Replace:
``Rule F round 18 (BI4) gives the end window's fourth level as the mean running batch: in that code `n` is the mean of `vllm:num_requests_running` over the window (FILE(analysis/load.py:183); the same code at `1cface7`, its line 179), not a request count.``

with:
``In that code the end window's fourth level, `n`, is the mean of `vllm:num_requests_running` over the window (FILE(analysis/load.py:183); the same code at `1cface7`, its line 179): round 3's owner-proxy (BJ3) had written "the request count", rule F round 18 (BI4) gave the mean running batch, and round 4's owner-proxy (CF5) put BI4's words into BJ3's sentence.``

### CF6 (BEFORE; reporting duty; process.md §3 "The output goes verbatim into the [REG] entry"; the delegation's (a); the stop entry's "recorded verbatim in the [REG]")

Replace:
`### Changed because of the reviews of draft 4`

with:
`### Adversarial review of this text (rule F round 19, a separate subagent), verbatim, each line prefixed with "> " so that no line begins a heading` + blank line + rule F round 19's review, verbatim, each line prefixed with `> ` + blank line + `Earlier rounds are saved verbatim at the paths in the ID line; rule F round 18 and round 3's owner-proxy messages are quoted verbatim in the [DECISION] (delegate) (BJ6(d), BJ13(c)). What changed because of round 19 is listed under the change log's last heading.` + blank line + `### Changed because of the reviews of draft 4`

### CF7 (BEFORE; disclosure; the change log)

Replace:
`is limited to looks after the entry, since (x) is a switch.`

with:
`is limited to looks after the entry, since (x) is a switch.` + blank line + `### Changed from draft 26: round 4 on the text written under the stop (rule F round 19; owner-proxy APPROVE on CF1–CF8)` + blank line + ``- **CF1–CF7, verbatim:** the agent's own session's reads of `RESUME.md`, with their times against the thresholds' commits, and the owner's check as a duty of the batch-2 [RESULT] (CF1); an owner's entry restoring batch 2's standing timed as the owner's overrule is (CF2); "Batch 2's J1 inside" marked as not applying while batch 2 is labelled retrospective (CF3), and the batch-2 [RESULT] using none of its wording then (CF4); BJ3's "the request count" replaced by BI4's "mean running batch", attributed (CF5); rule F round 19 verbatim under "Adversarial review" (CF6). Rule F round 19's items and their placements follow.``

### CF8 (LATER: the [DECISION] (delegate), written anew; not `docs/drafts/reg21_decision_draft2.md`)

It states or carries:
- **(a) Earlier conditions:**
  - BF9(a)–(f) verbatim, with (b) the empty `git diff --stat 8164211 E` over the 26 files;
  - BJ4(c) verbatim;
  - BJ6(b), the empty output of BJ4(a)'s command for `8164211..E` (if either is not empty, the entry is not appended);
  - BJ6(c)'s sentence verbatim;
  - BJ13(a)–(f), with P3's section 1 quoted verbatim;
  - BI7's sentence repeated.
- **(b) Verbatim texts:**
  - rule F round 18 and its addendum;
  - all three round-3 proxy messages (P3 governs);
  - this verdict.
- **(c) Line 104:** the closure script's verbatim output at E, with the union rule.
- **(d) Line 111's duties:**
  - `search.py` and `search2.py` run again at the append, with their PROBE paths;
  - the classification of every `search2.py` hit after 2026-11-11 17:15 UTC under BI2's and BI6's rules, citing `labels.tsv` at its entry-commit version;
  - the check that nothing printed U, r, the busy share or the other listed quantities;
  - every REG-19 run folder made since draft 23, by name (attempt 3 of seed 18's control and any later);
  - the statement on REG-19 readings up to the append, with (i)–(x);
  - `done` and `continue` for every step since draft 23, with the bound they imply.
- **(e) Line 108(a):** the list of folders matching the batch-2 pattern, each with `test -e …/checks.json`.
- **(f) BK4's list of the note's calls:**
  - with full dates (2026-11-12 for 18:28, 18:43 and 20:28);
  - naming those made in 8c5f8396 and its subagents;
  - stating that decisions.md:4279's "The agent has read no outcome of any REG-19 run" does not cover the agent's reads of the note, whose content the agent does not state.
- **(g) Every departure:**
  - the item map's six departures;
  - BJ14(i)'s label edit at line 71;
  - the four "Agent's wording fixes before round 4" of line 284, not from a review, with the statement that the item map (FILE(docs/drafts/reg21_draft26_itemmap.md)) was written before them and its "untouched" and "left verbatim" on those places no longer hold;
  - CF1–CF7.
- **(h) Order:** batch 1 waits on REG-22's [REG] and [DECISION] (delegate), or on S (line 102).
- **(i) Wording:** "batch 1 is the primary analysis" means only the first computation (BJ13(e)).
- **Also, in the commit that appends the entry:**
  - the status.md notice of line 112;
  - P3 note 3's fix: the read was found by 16:43:16 UTC (d960ef3), not "≈ 16:50".

## Which later changes need another proxy pass
- CF1–CF8 written other than as given.
- A rule F round 19 item that is not applied in its reviewer's verbatim words.
- A round 19 item that is classed as none of wording, a tag, a stricter rule, a reporting duty or a disclosure.
- A round 19 item that changes any of these:
  - a threshold, J1/J2, a precondition, a run set, the judged code or the frozen list;
  - facts (1)/(2), the validity cut or the not-computed rules;
  - the trigger, "The two batches", batch 2's label, or CF2;
  - any wording that would let either batch read as blind or confirmatory.
- A round 19 item and a CF that change the same words, unless both texts can stand together.
- A non-empty output of BF9(b) or BJ6(b): the entry is not appended.
- An append-time search hit beyond the listed reads (line 111 already sends this to rule F and a proxy pass).
- Any entry restoring batch 2's standing: the owner's alone, under CF2.
- **No pass needed for:** the header or the draft number recording round 4.

## Notes for the owner
1. **Please open `docs/probe/20261111_reg19/ops/RESUME.md`.** The agent's own session read it in full 32 min before it committed the 0.05 on r (FILE(agent/INGEST.md:15)). Say whether it quotes any run-time line of a REG-19 run.
   - For a burst run after its burst: REG-21's label does not change (it is already retrospective). It belongs in REG-19's deviations, and in a [CORR] of decisions.md:4279's "The agent has read no outcome of any REG-19 run".
   - BI-O3 asks you to check the 2026-11-12 context pack and the subagent's report for seed 17's counts too.
2. **REG-21 now judges nothing on unread data.** Its value is batch 1's readouts and a retrospective batch 2, and line 52 already predicts batch 1's labels from published numbers. A prospective K3 reading would need new runs, registered before anyone reads them.
3. **CF2 is stricter than your plan's "before batch 1".** It adds "before any U/r print and before S", as line 55 already does for your overrule of the two-batch rule. You can always override by your own entry.
4. **"Its size against 0.05 decides whether batch 2 governs"** (lines 76, 84) is now empty while batch 2 is retrospective (line 73 rules). It is not false, so I asked for no change.
5. **Line 59's "one attempt is left"** describes the state before attempt 3 began (16:55 UTC). The [DECISION] names attempt 3's folder.

## Not checked
- `RESUME.md`, `runs/` (names only, none opened), `state/`, `queue_*.txt` (so line 54's citation of `queue_run4_output.txt:5` is unchecked), backups, and any tool output.
- Rule F round 19, which I have not seen.
- REG-22 draft 17 and its bundle.
- BI1's ±0.02 req/s derivation.
- The search2 dry-run and classify2 outputs, `labels.tsv`, and `classify2.py`'s self-test.
- Who owns sessions 4e055435 and 49020ad6.
- Subagent transcripts. I read the RESUME.md tool-call inputs of 8c5f8396's main file only.
- `closure.py`, pytest, check_docs and context_pack: none run by me.
- status.md's history behind INGEST.md:69.

I wrote nothing into the repository. My scratch scripts are in /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/e1890469-fa93-4ca8-af9a-4c034439b43f/scratchpad (worddiff.py, verb.py, verb1.py, chk.py, inputs_resume.py; the last prints tool-call inputs only).
