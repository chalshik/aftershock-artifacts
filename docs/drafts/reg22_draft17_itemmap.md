# REG-22 draft 17: item map (round 3 on the freeze, and the stop)

`docs/drafts/reg22_draft17.md` was built from `docs/drafts/reg22_draft16.md` by `make_reg22_draft17.py`, which is kept in the drafting agent's scratch folder (path in the agent's report, outside the repository). The build uses the method of `make_reg22_draft16.py`: every change is an anchored replacement. Each anchor is asserted to occur exactly once in draft 16 and exactly once at the moment it is applied (39 of 39; table at the end). The reviewers' replacement texts are not retyped. The script reads them by line number from the saved review files and checks each one's prefix, so "verbatim" means the bytes of the saved review. Repository HEAD at build: `8271d71`. The draft-16 line numbers of the body are unchanged in draft 17: no line was added or removed above the change log.

Line numbers below are draft 17's. Lines 80, 81, 133 and 134 are long paragraphs, so the cell also says where in the paragraph the change sits.

| Item | Where applied (draft 17) | How | Why |
|---|---|---|---|
| **BL1(a)** | line 5 ("What this is, in one line") | verbatim | Owner-proxy text, word for word. |
| **BL1(b)** | line 80, directly after "Batch 2 is primary only if the stopping rule's facts (1) and (2) and its validity freeze hold; …" | verbatim; BK1's label merged into it | BL1(b) is the label text. BK1's own label sentences ("Read 1 … is such a read … So batch 2 is labelled retrospective by design") say the same thing and are not added a second time (rule 2 of the brief). |
| **BL1(c)** | line 91 (line a, the standing) | verbatim | Owner-proxy text. |
| **BL2(a)** | line 80, after "(ii)" (the "Found by round 2's owner-proxy on REG-21 …" sentence) | verbatim, with BL2a(a) inside it; BK6(d)'s first bullet and BK1's "also add" merged | BL2(a) already holds REG-21 draft 25's reads (vii)–(ix) and the 17:56:24 UTC listing, so BK6(d)'s "insert (vii)–(ix) verbatim, with the 17:56:24 listing" and BK1's "also add Read 1 and the 17:56:24 UTC listing" are met by it and not inserted twice. The read keeps the number (iii), as the proxy's addendum allows. |
| **BL2(b)** | line 80, read (i), the 300 characters of `checks.json` | verbatim, with BL2a(b); BK8 merged | See BK8. |
| **BL2(c)** | line 80 ("**Three reads are known, (i) to (iii), …**") | verbatim | — |
| **BL2a** | (a) line 80, inside read (iii), after "`ok` over the run's length is its mean completion rate (DERIVED)."; (b) line 80, the end of BL2(b)'s text | verbatim | The addendum's own instructions, applied to BL2's texts before they were inserted. |
| **BL3(a)** | line 80, "**The search is run again at this entry's commit,**" parenthetical on `search2.py` | verbatim; BK6(c) merged | BL3(a) and BK6(c) replace the same parenthetical. BL3(a)'s text is used. BK6(c)'s one further fact ("whose commit and `shasum -a 256` head its output") is a separate sentence at the end of the BL3(b)/BL3a block, tagged "(rule F round 11, BK6(c))". |
| **BL3(b)** | line 80, after "Its output is saved beside the first as …" | verbatim | Owner-proxy text. |
| **BL3(c)** | line 81 (the sentence on reviewer scripts) | verbatim; BK5 merged | BL3(c) replaces the parenthetical that BK5's longer replacement also covers. BL3(c) is used, and BK5's further sentences are placed separately (see BK5). BL3(c) says "as "About batch 2" says", but BL3(b)'s classes sit in line 80's bullet ("Run-time lines and looks"), not line 79's ("About batch 2, what is known"). Left as written, because another wording needs a proxy pass (see "Left for the review"). |
| **BL3a** | line 80, directly after BL3(b) | merged (the proxy's mapping written out as sentences, its label lists and the limit verbatim) | BL3a is a condition on how the classification meets BL3(b), not a replacement text. The brief asks for the classification text, including the `names_or_validity` limit. The text gives: the label→class mapping; the limit (`cat`, `head`, `tail`, `less`, `jq` beyond `valid`/`failed`, or python printing another field, are labelled by hand); the floor ("may replace", as the proxy wrote it); and the proxy's own condition for another pass (an `UNLABELLED` hit, or a label outside the mapping, at E). |
| **BL4** | not in the draft | — | For the [DECISION] (delegate), as BL4 says. The header says so. |
| **BK1** | line 80: (1) after the trigger sentence ("If it then finds … rule F and an owner-proxy pass."); (2) after BL1(b) | merged with BL1 | Verbatim, as separate sentences: BK1's first sentence (draft 16's list is the one the trigger compares against), then the addendum's sentence (a read counts when the inputs make it likely). The addendum's sentence gets "(read (iii) above)" after "Read 1" and the tag "(rule F round 11, BK1 and its addendum)". After BL1(b) comes BK1's last clause as its own sentence, also verbatim: the standing words in line a and in "Batches that disagree at λ = 2.0" name this read beside any other cause. BK1's middle sentences (Read 1 is such a read; so batch 2 is retrospective by design) are covered by BL1(b) and BL2(a)'s read (iii). |
| **BK2** | line 133, fact (2): the `find`, the `git log`, the decisions.md `grep`, the worktree sentence, and the [OPS] clause in the duties | verbatim (five replacements), with BK-O2's `--reflog` added to the `git log` | The fact-(2) sentence that sets the table-file set equal to the review-stop rule's now also cites that rule's check (FILE(docs/decisions.md:4555), BK-S6), because BK2 makes the commands match. |
| **BK3** | line 93 (line a, "batch 2 pending") | verbatim | — |
| **BK4** | line 80, read (i), in place of "(BELIEF: the note that records it, RESUME.md, was not opened)" | **departed** (the brief's change) | BK4's text is used up to "All are found in tool-call inputs only. The [DECISION] (delegate) lists these calls". Its last two sentences ask the [DECISION] to state, from the note, which run-time lines it quotes. The agent may not open `docs/probe/20261111_reg19/ops/RESUME.md` under its delegation, so in their place the text says: what the note quotes is not stated; the owner can open it; and a burst-run line quoted there would be a read under the trigger, with batch 2 labelled retrospective by design in any case. The commit `54a995d` was checked with `git log --diff-filter=A` (metadata only; the note was not opened). |
| **BK5** | line 81: the parenthetical through BL3(c); the further sentences after "if it finds an output of `c2` on a batch-1 run, this entry is not appended as written." | merged with BL3(c), and moved | BK5's sentences from "Every `ran` line …" to "… is read in the transcript's input." are verbatim, introduced by "For the sentence on reviewer scripts above, `search2.py`'s output at E is read as follows (rule F round 11, BK5)." They were placed after the rerun sentence, not inside the reviewer-scripts sentence, so that "Its one hit on batch-1 runs …" still follows the first search. BK5's three classes (stub / guard / read) are for `ran` lines that import `c2`, `k3w` or `gate.reg19*`. BL3(b)'s five classes are for the hits BL3(b) names. Both stand. |
| **BK6(a)** | line 80 (REG-19's own computations, `reg19_step`) | verbatim | — |
| **BK6(b)** | line 80 ("Its stated limits: …") | verbatim | — |
| **BK6(c)** | line 80 | merged with BL3(a) | See BL3(a). |
| **BK6(d)** | line 80: first bullet through BL2(a); second and third bullets at "no other read of a REG-19 run's files …" and "on `main` the seal has refused such runs …" | merged (first bullet), verbatim (second, third) | `final.sh` does reach `AFTERSHOCK_UNSEAL`: it sources `common.sh` and calls `recheck_ok` (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:25), FILE(docs/probe/20261113_reg19/ops_r3/common.sh:210)), so BK6(d)'s "as REG-19's queue and `final.sh` do" was checked true. |
| **BK7** | line 81, after REG-20's smoke-test sentence ("… BF5(a), FILE(…proxy-reg21-draft24-delta.md:144)).") | verbatim | — |
| **BK8** | line 80: through BL2(b) and BL2a(b), and one further sentence after read (i)'s "(rule F round 10, BG5(a); BELIEF either way)." | merged with BL2(b), BL2a(b) | BL2(b) with BL2a(b) already says what the 300 characters hold and that they bear on the control readout. BK8's further facts are one separate sentence, tagged: the counts are not an allowed read under REG-19 (common.sh:36); they bear on the control's `recovered` flag reported beside line a; and read (iii) most likely printed the same control's row (BK8's "add Read 1's control row"). BK8's subject "those counts" is written "The counts that those 300 characters can hold", because the sentence no longer follows the 300-character clause directly. |
| **BK-O1** | line 133, fact (1) (two checks printed beside its commands); line 130 (written into the batch file) | adapted | `git merge-base --is-ancestor E B && echo ancestor` is written with `|| echo not_ancestor`, as fact (2)'s ancestry check is (BG-O1), so the check prints an answer either way. |
| **BK-O2** | line 133, fact (2)'s `git log` | applied | Tested in a scratch repository: with two stash entries that each add a table file, `--all` listed only the newer entry's file and `--all --reflog` listed both (DERIVED; the agent's run). The text says so, in place of the reviewer's BELIEF. The wording "a commit that only a reflog still reaches" replaces the reviewer's "an unreachable commit", because `--reflog` reaches only commits that a reflog names. |
| **BK-O3** | line 133, defect clause | applied | "Lines a, e and h" → "Lines a, d, e and h, the line "Batches that disagree at λ = 2.0" and batch 1's [RESULT]". |
| **BK-O4** | line 130 (the batch file's head) | verbatim commands | `uv --version` and `python -c 'import analysis, numpy; …'` are added beside `python -V`. |
| **BK-O5** | line 133 | applied | "BG2).." → "BG2).". |
| **BK-O6** | line 102 ("Batches that disagree at λ = 2.0") | applied | Each batch's number of judged spans and of failing judged spans is given beside its count, with rule F's DERIVED numbers (0.86 at 4 spans, 0.71 at 9) and a pointer to alternative 5. |
| **BI-O1** (REG-21 rule F round 18, optional) | line 134 (what the batch-2 [RESULT] shows) | cross-applied | REG-22's command is `python -m analysis.c2`, which puts the repository root first on `sys.path` just as REG-21's command does. The two commands are verbatim, and "any other line is a breach it reports" is kept. |
| **BK-S1–S6** | line 4 (reviews bullet: the stop entry, FILE(docs/decisions.md:4541), :4546, :4552, :4556); line 133 (fact (2) cites the stop entry's BK-S6 check, :4555) | applied by the stop entry; cited here | The brief's rule 5. |
| **BK-S4** | line 133, the head of the freeze bullet | adapted | BK-S4's sentence replaces the opening, as the addendum asks. "The text written under item 4 keeps …" is written "This text, written under the review-stop rule's item 4, keeps …". The freeze's own words follow it ("**So from this entry to batch 2 the frozen files do not change, with no exception** (the judged path …)"), so the freeze keeps its meaning and the parenthetical keeps its subject. |
| **Label words** (the agent's) | line 133: "**Batch 2 is labelled retrospective by design (read (iii), …); it would have been primary only if two facts in git held,**"; "Apart from read (iii), the label follows from these facts alone"; the standing words take BL1(c)'s form. Line 134: the pointer to the freeze, and "It keeps the standing of line a, "retrospective (by design<; …>)", exactly". | **departed** (no REG-22 item covers these) | Without them, line 133 still said "Batch 2 is primary only if two facts in git hold" and "The label follows from these facts alone", which BL1 makes false. Line 134 still said the [RESULT] "keeps the standing "registered before REG-19's table"". The first two use the form REG-21's owner-proxy gave for the same sentences (BJ14(d), FILE(docs/drafts/reviews-2026-11-13/proxy-reg21-draft25-delta3.md:56)), with (iii) for (x). These are label words only, and none makes batch 2 primary. The proxy's rule says a pass is needed for "any text that makes batch 2 primary" and for "any wording of BL1 other than as given". These edits are neither, but they are listed here for this text's own review. |
| **Header and change log** | line 3 (draft 17's line), line 4 (round 3 and the stop), lines 229–257 ("Changed from draft 16") | new | As the brief asks. One line per item. |

## Departures, in one place
1. **BK4:** its last two sentences are replaced by the brief's text, because the agent may not open RESUME.md.
2. **Label words at lines 133–134:** the agent's consistency edits under BL1, in BJ14(d)'s form from REG-21's owner-proxy. No REG-22 item asks for them.
3. **BK-S4:** adapted from "The text written under item 4" to "This text, written under the review-stop rule's item 4,", and followed by the freeze's own opening words, so that the freeze stays.
4. **BK-O1:** `|| echo not_ancestor` added. **BK-O2:** "an unreachable commit" written as "a commit that only a reflog still reaches", with a test result in place of the reviewer's BELIEF.
5. **BK1, BK5, BK8:** merged with BL1, BL3(c) and BL2(b). Their further facts are separate sentences, and BK5's sentences moved within line 81 (see the rows). BK1's addendum sentence gets "(read (iii) above)", and BK8's subject is reworded to stand alone.
6. **BL1–BL3, BL2a:** no departure. Read (iii) keeps the proxy's number. **BL3a:** written out from the proxy's mapping (it has no replacement text). Its "may replace" on the floor is kept as the proxy wrote it.

## Not applied
- **BL4:** belongs to the [DECISION] (delegate).
- **BK6(d)'s and BK1's insertions of REG-21's (vii)–(ix) and the 17:56:24 listing:** not inserted a second time, because BL2(a) carries them.
- **BK1's own label sentences:** BL1(b) carries the label.
- **BK5's own wording of the parenthetical:** BL3(c) carries it.
- Nothing else was left out.

## Left for the review (noticed, not changed)
- **BL3(c)'s pointer "as "About batch 2" says"** names line 79's bullet, but BL3(b)'s classes are in line 80's. It is kept verbatim (proxy text).
- **BL3(b) and BL3a:** BL3(b) says "A hit in none of these classes is a read beyond what is listed here", while BL3a maps some labels to "no read", a sixth outcome. Both are the proxy's words.
- **Line 125, order (b):** "unless the same [DECISION] states that REG-21's batch 2 is no longer read blind". REG-21's batch 2 is now also retrospective by design (REG-21's owner-proxy, BJ8). The clause is about REG-21, not about REG-22's standing, and is left as it was.
- **Line 155:** "a blind order test on REG-19's runs". Read (iii) did not reach onsets, so the line is left as it was.
- **Line 130 and BK-O4:** `python -V` and `python -c …` are written without `uv run`, as given. If `python` on PATH is not the venv's interpreter, they describe another interpreter.
- **Line 79:** "Three REG-19 burst runs exist at this draft". This held on the Mac at 17:24 UTC (folder names in `runs/`: seeds 15–17). Seed 18's control was running on the VM, which was not contacted. The [DECISION] (delegate) names the folders at E (BG-O4).
- **Agreement with REG-21 (BJ8, read (x)):** no fact of read (iii) disagrees with BJ8's. REG-22 lacks BJ8's sentence that seeds 15 and 16's counts were read but most likely not printed. Its "reads every folder's … `checks.json`" implies the read.

## Checks
- **FILE and PROBE tags:** 221 tags in draft 17. Each points at an existing file, and each line is within the file (the `check_docs` rule, run over the draft by a scratch script). No tag points into `runs/`. Every FILE tag new in draft 17 was read at its line, at HEAD `8271d71`. Since draft 16 (`90cd0a9`), the files cited by line changed only as follows: `common.sh` changed and kept its line count (the four cited lines were re-read), and `docs/decisions.md` was appended to. No line number moved.
- **Primary standing:** a grep of draft 17 for `primary|registered before REG-19|unread|read blind|blind|never governs|no analysis is known|follows from these facts alone` finds the following body lines:
  - line 5: BL1(a), the label;
  - line 80: "Batch 2 is primary only if …", followed directly by "So batch 2 is never primary" (BL1(b));
  - line 125: about REG-21's batch 2;
  - line 133: "it would have been primary only if", "restores primary standing", and "Apart from read (iii), the label follows …";
  - line 134: the pointer, and "does not call batch 2 "unread"";
  - line 155: an order test.

  None makes batch 2 primary. Every other hit is history in the change log (from line 165 on).
- **Diff from draft 16:** `git diff --no-index --stat`: 1 file, 40 insertions(+), 11 deletions(−).
  - Changed lines: 3–5, 80–81, 91, 93, 102, 130 and 133–134.
  - Added: 229–257, the change log.
  - About 4,280 words added and 600 removed (word diff); 228 → 257 lines.
- **Not done (the brief's limits):** nothing under `runs/` was opened (names only), nor `docs/probe/**/state/`, any `queue_*.txt`, RESUME.md or the backups. No transcript output was opened. No `analysis` module, `tools/tables.py` or `pytest` was run. No existing file was edited, nothing was committed, and the VM was not contacted.

## Anchor check (every anchor once in draft 16, once when applied)
| # | Replacement | Anchor (start) | In draft 16 | When applied | Draft 17 line |
|---|---|---|---|---|---|
| 1 | header | `Draft 16. It is draft 15 with round 2 on the freeze written in:` | 1 | 1 | 3 |
| 2 | header (reviews) | `Under the review-stop rule as amended (decisions.md 2026-11-13 [DECISI` | 1 | 1 | 4 |
| 3 | BL1(a) | `batch 2 is the same table once on REG-19's runs, which no analysis is ` | 1 | 1 | 5 |
| 4 | BL2(c) | `**Two reads are known.**` | 1 | 1 | 80 |
| 5 | BL2(b)+BL2a(b) [BK8 merged] | `at 11:50:49 UTC it printed the first 300 characters of that run's 'che` | 1 | 1 | 80 |
| 6 | BK4 (departure) | `(BELIEF: the note that records it, RESUME.md, was not opened)` | 1 | 1 | 80 |
| 7 | BK8 (further facts) | `and whether the run had ended at 11:45 UTC is not known (rule F round ` | 1 | 1 | 80 |
| 8 | BL2(a)+BL2a(a) [BK6(d) first bullet, BK1 'also add' merged] | `between 17:56 and 17:59 UTC the context-pack subagents also printed th` | 1 | 1 | 80 |
| 9 | BK6(a) | `('analysis.gate reg19_step' from the pinned worktree after each seed, ` | 1 | 1 | 80 |
| 10 | BK6(d) second | `no other read of a REG-19 run's files or logs beyond names, validity a` | 1 | 1 | 80 |
| 11 | BK6(d) third | `on 'main' the seal has refused such runs since '72fafb5' (FILE(analysi` | 1 | 1 | 80 |
| 12 | BL3(a) [BK6(c) merged] | `(committed in '723a16b'; BH8, BG5(b))` | 1 | 1 | 80 |
| 13 | BK6(b) | `Its stated limits: commands run by hand outside these sessions, the co` | 1 | 1 | 80 |
| 14 | BL3(b)+BL3a+BK6(c) fact | `and the [DECISION] (delegate) cites both outputs and classifies every ` | 1 | 1 | 80 |
| 15 | BK1 (further facts) | `If it then finds a run of 'analysis/' code on a REG-19 run folder, or ` | 1 | 1 | 80 |
| 16 | BL1(b) [BK1 label merged] | `Batch 2 is primary only if the stopping rule's facts (1) and (2) and i` | 1 | 1 | 80 |
| 17 | BL3(c) [BK5 merged] | `(its 'script_reads_runs' hits, labelled 'stubbed' where the code assig` | 1 | 1 | 81 |
| 18 | BK7 | `(found by round 2's owner-proxy on REG-21, BF5(a), FILE(docs/drafts/re` | 1 | 1 | 81 |
| 19 | BK5 (further facts) | `if it finds an output of 'c2' on a batch-1 run, this entry is not appe` | 1 | 1 | 81 |
| 20 | BL1(c) | `batch 2 "registered before REG-19's table", only if both facts of "Bat` | 1 | 1 | 91 |
| 21 | BK3 | `  - at λ = 2.0 only, "batch 2 pending" until batch 2 is computed or re` | 1 | 1 | 93 |
| 22 | BK-O6 | `Both counts are then given side by side with each batch's standing,` | 1 | 1 | 102 |
| 23 | BK-O1+BK-O4 (batch file) | `fact (1)'s two commands, 'git rev-parse HEAD' (this is B), 'python -V'` | 1 | 1 | 130 |
| 24 | BK-S4 | `- **From this entry to batch 2 the frozen files do not change, with no` | 1 | 1 | 133 |
| 25 | BK-O5 | `(rule F round 10, BG2)..` | 1 | 1 | 133 |
| 26 | label words (BJ14(d) form) 1 | `**Batch 2 is primary only if two facts in git hold,**` | 1 | 1 | 133 |
| 27 | BK-O1 (fact (1)) | `and 'git status --porcelain -- <the frozen files>' prints nothing in t` | 1 | 1 | 133 |
| 28 | BK2 find | `('find . -name 'reg19_final_*.txt' -not -path './.git/*'', table-file ` | 1 | 1 | 133 |
| 29 | BK2 git log (+BK-O2) | `('git log --all --diff-filter=A --name-only --format='%H %ct' -- ':(gl` | 1 | 1 | 133 |
| 30 | BK2 decisions.md | `and every such time a decisions.md entry quotes for a table file.` | 1 | 1 | 133 |
| 31 | BK2 worktrees | `The 'find' is run in every working tree that 'git worktree list' names` | 1 | 1 | 133 |
| 32 | BK-S6 (cited) | `and the review-stop rule's (FILE(docs/decisions.md:4437)) (REG-21's ow` | 1 | 1 | 133 |
| 33 | BK2 [OPS] | `a pair set aside after a failed run is committed where it was set asid` | 1 | 1 | 133 |
| 34 | label words (BL1(c) form) 2 | `it reads "retrospective (<fact (1) \| fact (2) \| the validity freeze \| ` | 1 | 1 | 133 |
| 35 | label words (BJ14(d) form) 3 | `The label follows from these facts alone` | 1 | 1 | 133 |
| 36 | BK-O3 | `Lines a, e and h quote the frozen output with the [CORR] named;` | 1 | 1 | 133 |
| 37 | label words 4 (pointer) | `("Batch 2 is primary only if", above)` | 1 | 1 | 134 |
| 38 | label words 5 | `It keeps the standing "registered before REG-19's table" exactly and d` | 1 | 1 | 134 |
| 39 | BI-O1 (REG-21, cross-applied) | `It also shows that the heading which lifted the seal is REG-19's final` | 1 | 1 | 134 |
