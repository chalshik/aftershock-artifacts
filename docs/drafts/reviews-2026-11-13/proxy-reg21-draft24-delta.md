# proxy-reg21-draft24-delta (proxy-reg21-d24), verbatim

Saved by the agent from the teammate message received in the main session transcript (message timestamp 2026-11-13T16:01:10.714Z). Item names as given by the reviewer (prefixes BE, BF, BG, BH were assigned in the round-2 review prompts).

---

Owner-proxy, round 2 on the freeze, REG-21 draft 24 (bundle reg21_r17): APPROVE on conditions BF1–BF10, all BEFORE the entry is appended. Draft 24 cannot be appended as written: fact (2) already fails for every possible entry commit (BF1), and the frozen list leaves out four files (BF2).

# proxy-reg21-draft24-delta (round 2 on the freeze)

**Decision: APPROVE, on conditions BF1–BF10, all BEFORE the entry is appended.**
- Draft 24 as written is not appendable. Read literally, its fact (2) fails today for any E (BF1). Its frozen list leaves out four files (BF2).
- Each condition is wording, a tag, a stricter rule, a disclosure or a reporting duty. Its class is given per item. So under the review-stop rule (FILE(docs/decisions.md:4406), items 2–4) this pass does not stop the review.
- BF1–BF4 change the text of the facts and the validity cut. Draft 25 therefore goes to rule F round 18 (round 3) whatever round 17 says.
- BF1–BF10 written verbatim need no further proxy pass.
- This approval does not cover rule F round 17's items, which I have not seen.

## Integrity checks (mine)
- HEAD is d76211b; ba67e55 added the bundle.
- The bundle's draft 24 and draft 23 are byte-identical to docs/drafts/reg21_draft24.md and reg21_draft23.md. The review-stop entry and the [CORR] in the bundle equal FILE(docs/decisions.md:4406)–4428.
- The bundle's final.sh, common.sh and launch.sh equal the current ops_r3 files.
- `git diff 8164211 HEAD` over analysis/, harness/, pyproject.toml, uv.lock and .python-version touches only c2.py, e1.py and k5.py. None of them is in k3w's import closure (DERIVED: my ast closure).
- No file with a stamped `reg19_final_<stamp>` name exists in:
  - the main working tree (runs/, .git and .venv pruned);
  - either pin worktree (`git worktree list`);
  - any commit on any ref;
  - decisions.md.
  ops_r3/state/ holds no such name (names only).
- The FILE citations I checked hold at HEAD, except common.sh:34 (BF7).

## Q1. Are BB1–BB8 met as written?
- **BB1: met verbatim.**
  - Line 49 has the two required sentences. Line 53 has "(and was seen to pass at the end of W on five runs, above)". Line 111 has "other than the print disclosed under "What was known"".
  - Line 238 names the agent's error, with the [CORR] at FILE(docs/decisions.md:4420).
  - Its rule F half is round 17, which is pending.
  - Residual: the same command also printed each run's cold and recovered flags, the hit rate before the burst and in the end window, and the end window's mean waiting line. Line 49 lists only reuse, `mechanism` and `readouts` (BF5a). Command text: session fdf13821, 2026-11-12 14:22:49 UTC; I read inputs only.
- **BB2: met in substance, not as written.** Line 111 widens the modules (k5 added), drops the date floor, saves the script and its output under docs/probe/, and cites a PROBE in the [DECISION]. It also states the hand-run limit. But "imports" became "heredocs and scripts", and search.py sees neither of these:
  - a .py file written by `cat > x.py <<EOF` and run later (it tracks Write calls only);
  - a loop over every folder (`for d in */`);
  - a `cd` into a folder followed by a bare file name;
  - the Grep tool.
  By hand I found three reads of REG-19 folders that it misses (BF5b) and none of the other kinds (BF6).
- **BB3: first half met.** Line 107 has "(such an entry also states what its author had seen of REG-19's runs)", in BA1's wording. Second half: line 241 says BB3's E1 sentence "is covered" but never says what E1 became, and line 186 still reads as if E1 were in force (BF8).
- **BB4: its object is gone.** Line 104: "whether a change touches it is not asked, so no hunk is ever argued to lie outside it."
- **BB5: not met yet.** It belongs in the [DECISION] (delegate). That entry's only draft, docs/drafts/reg21_decision_draft1.md (last changed in 2a4cf6f, before drafts 23 and 24), still describes the record, its cut and E2's records (BF9a).
- **BB6: met verbatim** (lines 73 and 75).
- **BB7: met** (line 54: FILE(docs/decisions.md:4279); the rest of the lines tagged BELIEF, RESUME.md not opened).
- **BB8: met in substance.** Line 104 names a hand run that saves nothing, and a file moved out and never committed or quoted. A deleted file is not named; BF1's text adds it.

## Q2. Does the review-stop entry meet BB9?
**Yes on all three points:**
- **Which rounds count:** items 1, 2 and 4 combine "fixed once" and "third round" into one mechanical reading with no open case.
- **What triggers the stop:** only items on batch 2's standing (item 3).
- **A batch-1-only text:** gets its own rule F review and proxy pass, binding (item 4).

**Two gaps (BF10):**
- (a) Nothing says who decides whether an item is "wording, a tag, a stricter rule or a reporting duty". Under item 4 that class decides the stop.
- (b) Item 5 says the entry is committed "before the first commit that adds a `reg19_final_*` file". Two problems:
  - That is the cut from before BA1.
  - Read literally, it is already impossible: nine commits on main (ab6988f, 72d4884, 4ad587d, 2bf6a90, 346ee6c, b8ea915, 3e9c73f, e062504, ba67e55) add 15 review-bundle copies named `reg19_final_sh_for_reference.sh` (DERIVED: `git log --all --diff-filter=A` on that glob).

**Process:**
- ba67e55 appended the entry as a [DECISION] (delegate) before any review of its own. The delegation says such an entry is "written only after" rule F and an owner-proxy approval.
- BB9 had timed it "before rule F round 17 is launched", which invited this.
- I approve its content with BF10. The order is to be disclosed (BF9e).

## Q3. Is the whole-file freeze acceptable to the owner?
**Yes (BELIEF as to the owner).** It ends both the hunk arguments and the SEALS exemption hole (rule F round 13, M1) by construction. It is fixed before any data, and it errs toward less claim.

**But the list is wrong.**
- `harness/run.py` imports `env_snapshot`, `loadgen` and `trigger` at its top (FILE(harness/run.py:23), FILE(harness/run.py:24)).
- `gate.py` and `k3.py` import `harness.run` (FILE(analysis/gate.py:751), FILE(analysis/k3.py:395)).
- So the closure has 23 Python files, not 20.
- `.python-version` (3.12.13) also fixes the environment.
- The text defines the frozen set twice, as "the closure" and as "these 22 files". They disagree, so an edit to `harness/loadgen.py` would have two readings (BF2).

**The cost, said plainly:**
- 26 files: all of the harness's Python, 14 analysis modules and the environment.
- The freeze holds until both batch 2s are computed or declared not computed. That is as long as REG-19 stays open, including any wait for the owner after a lost attempt 3.
- It is stricter than the approved plan's "REG-20 code goes into new functions or files" (FILE(docs/drafts/plan_2026-11-13.md:50)). Now it is new files only; work on frozen files waits or is prepared on a branch or worktree. This departure is to be named (BF9f).

## Q4. Is fact (2) mechanical, and is the validity freeze acceptable?
**Fact (2) is not mechanical as written:**
- (a) **The glob.** The ancestry clause says "no commit that adds such a file is E or an ancestor of E". The nine commits above add files named `reg19_final_*` and will be ancestors of any E, so fact (2) fails today. The same names fall under three rules: "committed on main, alone", "no `reg19_final_*` file is deleted", and the `_to_delete/` copies. S itself is unaffected, since those names carry no stamp. A reader holding REG-19's table could choose between the two readings (BF1).
- (b) **The worktrees.** `find .` covers only the main working tree. The two pin worktrees, where REG-19's analysis runs, are outside it (BF1, stricter).
- (c) **Git's history simplification.** `git log` with a path uses it by default. In a scratch repository, a change and its revert on a merged side branch printed nothing for `git log E..main -- k1.py`. The same command with `--full-history` listed both commits. (PROBE: my scratchpad repository, no project data.) This hits fact (1)'s command, whose own sentence says "a later commit that reverts it does not undo it" (BF3). It also hits fact (2)'s search for added files (BF1).

With BF1 and BF3, both facts are mechanical.

**The validity freeze from E is acceptable**, with one ambiguous case (BF4). FILE(docs/decisions.md:4383), item 4, foresees an owner's entry after a lost attempt 3 that allows a further attempt. Whether that entry "changes the seeds REG-19's table counts other than through … registered rerun rules" has two readings. The reading would be chosen by whoever computes batch 2, after REG-19's table.

## Q5. Is the disclosure honest and complete?
**Honest in intent; not complete.**

1. **Two sentences are false as worded.** Line 54 says "no run of `analysis/` code on a REG-19 run folder from any checkout"; line 111 says "no run of `analysis.gate reg19` or any other analysis on a REG-19 run folder". But REG-19's own queue does this by design:
   - it runs `analysis.recheck` (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:210));
   - it runs `analysis.gate reg19_step`, which computes every counted seed's pair and prints only `done` and `continue` (FILE(docs/probe/20261113_reg19/ops_r3/queue.sh:77), FILE(analysis/gate.py:2022));
   - `vm_state.py` reads `env.json`'s `git_commit` and the status names of a failed `no_errors` (FILE(docs/probe/20261113_reg19/ops_r3/vm_state.py:1)).
   This is BB1's pattern on a small scale (BF5b, BF5c).
2. **Three reads of REG-19 folders are not listed.** I found them in the transcripts' tool-call inputs; I opened no output:
   - **(iii)** In the same 11:45:33 UTC command as read (i): `ls -la` of seed 17's control folder on the VM and `tail -3` of its `events.jsonl`. That is a control, not a burst run.
   - **(iv)** On 2026-11-12, 17:56–17:59 UTC, the context-pack subagents printed every run folder's `config.yaml` `source_config` line. At 17:58:13 and 17:58:25 UTC, for every run folder then on the Mac, REG-19's six included, they printed `env.json`'s `nvidia_smi` field and the first `GPU KV cache size: … tokens` match in `server.log`. The grep scanned each whole file and printed only that start-up match.
   - **(v)** At 10:14 UTC on 2026-11-12, the queue session printed the byte size of seed 16's partial metrics file during its copy.
   None of them prints a line that a burst run wrote after its burst (DERIVED from the command texts; BELIEF that the KV-size phrase is start-up only, as for (ii)). So disclosing them now, before the append, does not set off line 54's "beyond what is listed" rule.
3. **The REG-20 smoke test** printed more than line 49 lists (Q1, BB1).
4. **The `analysis.k3` hits** of 2026-11-12, 16:02–16:27 UTC, name batch-1 runs but read only their `config.yaml` and compute on simulated runs. That is consistent with the draft, but not stated (BF5c).
5. **Line 111's claim about reviewer scripts holds.** I checked the guard lines of every heredoc-written reviewer script that imports k3w, c2 or k1, 22 scripts. Each one replaces `find_runs`/`load_run` (or the module's own `find_runs`) before any call. search.py itself cannot show this (BF6).

## Q6. Would the owner approve registering this?
- Not draft 24: fact (2) fails as written, the frozen list is wrong, and the disclosures are incomplete.
- Yes, a draft 25 with BF1–BF10 written verbatim (BELIEF as to the owner), once rule F round 18 is READY or raises only items of the four allowed classes. Rule F round 17 (pending) must also have no required item outside those classes on batch 2's standing.

## CONDITIONS (all BEFORE)

**BF1 (class: wording, with two stricter parts, the worktrees and `--full-history`).**
In line 104, replace the text from "(2) **This entry precedes REG-19's table:**" through "(`git merge-base --is-ancestor`)." with:

"(2) **This entry precedes REG-19's table.** A *table file* is a file whose name matches the extended regular expression `^reg19_final_(err_)?[0-9]{8}T[0-9]{6}Z` (the names `final.sh` gives its two outputs, FILE(docs/probe/20261113_reg19/ops_r3/final.sh:20)); its stamp is the `YYYYMMDDTHHMMSSZ` part, read as UTC. A name that does not match, such as the review bundles' copies `reg19_final_sh_for_reference.sh`, is not a table file. Let S be the earliest stamp among the table files in every working tree that `git worktree list` names (in each: `find . -name 'reg19_final_*' -not -path './.git/*' | grep -E '/reg19_final_(err_)?[0-9]{8}T[0-9]{6}Z[^/]*$'`), the table-file names that any commit on any ref adds (`git log --all --full-history --diff-filter=A --name-only --format='%H %ct' -- ':(glob)**/reg19_final_*'`, filtered by the same expression), and the table-file names any decisions.md entry quotes (`grep -oE 'reg19_final_(err_)?[0-9]{8}T[0-9]{6}Z' docs/decisions.md`). Fact (2) holds if E's committer time (`git log -1 --format=%ct E`) is earlier than S, compared as instants (this Mac commits at +0600, so local clock readings are never compared; the same second counts as after), and no commit that adds a table file is E or an ancestor of E (`git merge-base --is-ancestor`)."

Then, throughout the entry, wherever "file named `reg19_final_*`", "`reg19_final_*` file", "such file" or "the `reg19_final_*` output" refers to these files, it reads "table file". This covers line 55's S, line 104's duties and limits, and line 108's duty (b). The limits sentence becomes:

"a table file deleted, or moved out of the repository, and never committed or quoted, a hand run of REG-19's table that saves nothing, and a local history rewritten after the fact cannot be detected"

Add to the change log: "Round 2's owner-proxy found that nine commits on `main` (ab6988f to ba67e55) add review-bundle copies named `reg19_final_sh_for_reference.sh`, so read literally the ancestry half of draft 24's fact (2) failed for any entry commit; a table file is now defined by `final.sh`'s names (BF1). The agent and every reviewer of drafts 23 and 24 missed it."

**BF2 (class: stricter; also corrects the agent's error).**
In line 104, replace "and the two files that fix the environment:" with "and the three files that fix the environment:". Then replace "`harness/__init__.py`, `harness/checks.py`, `harness/config.py`, `harness/recorder.py`, `harness/run.py`, `harness/workload.py`, `pyproject.toml`, `uv.lock` (22 files)." with:

"`harness/__init__.py`, `harness/checks.py`, `harness/config.py`, `harness/env_snapshot.py`, `harness/loadgen.py`, `harness/recorder.py`, `harness/run.py`, `harness/trigger.py`, `harness/workload.py`, `.python-version`, `pyproject.toml`, `uv.lock` (26 files; `harness/run.py` imports `env_snapshot`, `loadgen` and `trigger` at its top, FILE(harness/run.py:23), FILE(harness/run.py:24), and `analysis/gate.py` and `analysis/k3.py` import `harness.run`, FILE(analysis/gate.py:751), FILE(analysis/k3.py:395); `.python-version` names the interpreter `uv run` uses). The closure is computed at E by a committed script whose verbatim output the [DECISION] (delegate) quotes; if that output and this list differ, every file on either is frozen."

In line 239, replace "(22 files)" with "(26 files; draft 24's list of 22 left out `harness/env_snapshot.py`, `harness/loadgen.py`, `harness/trigger.py` and `.python-version`, the agent's error, found by round 2's owner-proxy)".

**BF3 (class: stricter).**
In line 104, fact (1), replace "`git log --format='%H %ct %s' E..B -- <the frozen files>` prints nothing" with:

"`git log --full-history --format='%H %ct %s' E..B -- <the frozen files>` prints nothing (without `--full-history`, git's default history simplification hides a change and its revert made on a side branch that was merged, which this fact counts)"

**BF4 (class: wording, with a stricter statement duty).**
In line 107, replace "other than through the `checks.json` the harness wrote when the run ended and REG-19's registered rerun rules (such an entry also states what its author had seen of REG-19's runs)" with:

"other than through the `checks.json` the harness wrote when the run ended and REG-19's rerun rules (REG-19's [REG] of 2026-11-11 and every decisions.md entry on REG-19's attempts and reruns committed before this entry, among them FILE(docs/decisions.md:4284) and FILE(docs/decisions.md:4383)) (such an entry also states what its author had seen of REG-19's runs). An owner's entry after this entry that allows a further attempt for a run that ended without `checks.json`, as item 4 of FILE(docs/decisions.md:4383) foresees, is not such a change if it states that its author has read nothing of REG-19's runs beyond the reads listed under "What was known"; if it does not state this, batch 2 is not computed"

**BF5 (class: disclosure).**
- **(a)** In line 49, after "and the sessions in service)", insert: "; its lines also printed each run's `cold_backlogged` and `recovered` flags, the server hit rate before the burst and in the end window, and the mean waiting line in the end window (PROBE: the extended search's output, BF6)".
- **(b)** In line 54, replace "No other read of a REG-19 run's files or logs beyond names, validity and the names of failed checks, and no run of `analysis/` code on a REG-19 run folder from any checkout, is found by a search" with:

"REG-19's own scripts read its folders by design: names, `checks.json` `valid` and `failed`, and, through `vm_state.py`, `env.json` `git_commit` and the status names of a failed `no_errors` (FILE(docs/probe/20261113_reg19/ops_r3/vm_state.py:1)); and they run `analysis/` code on them: `analysis.recheck` (validity by the checks in force, FILE(docs/probe/20261113_reg19/ops_r3/common.sh:210)) and `analysis.gate reg19_step`, which computes each counted seed's pair and prints only `done` and `continue` (FILE(docs/probe/20261113_reg19/ops_r3/queue.sh:77), FILE(analysis/gate.py:2022)). Three more reads were found by round 2's owner-proxy in the tool-call inputs: (iii) in the same command as (i), `ls -la` of seed 17's control folder on the VM and `tail -3` of its `events.jsonl` (that control's last harness events; not a burst run); (iv) on 2026-11-12 between 17:56 and 17:59 UTC the context-pack subagents printed the `source_config` line of every run folder's `config.yaml`, and at 17:58:13 and 17:58:25 UTC printed, for every run folder then on the Mac, REG-19's six runs of seeds 15 to 17 included, the `nvidia_smi` field of `env.json` and the first `GPU KV cache size: … tokens` match in `server.log` (start-up values: the grep scanned each whole file and printed only that match; BELIEF that the phrase occurs only at start-up, as for (ii)); (v) on 2026-11-12 at 10:14 UTC the session that ran the queue printed the byte size of seed 16's partial metrics file while it was being copied. The agent has not read the output of (iii) to (v) (BELIEF: the agent's own report). No other read of a REG-19 run's files or logs, and no other run of `analysis/` code on a REG-19 run folder from any checkout, is found by a search"

If the agent has read any of that output, it writes what it read in place of the "has not read" sentence.
- **(c)** In line 111:
  - Replace "no reading of a REG-19 run beyond `common.sh`'s allowed reads and the two listed there, and no run of `analysis.gate reg19` or any other analysis on a REG-19 run folder from any checkout, is known" with "no reading of a REG-19 run beyond `common.sh`'s allowed reads, the reads REG-19's scripts make and the five listed there, and no run of `analysis.gate reg19` or of any other `analysis/` code on a REG-19 run folder, other than the queue's `analysis.recheck` and `analysis.gate reg19_step`, from any checkout, is known".
  - After "the only such hit is REG-20's smoke test of 2026-11-12 on five batch-1 runs ("What was known");", insert "the `analysis.k3` hits of 2026-11-12 between 16:02 and 16:27 UTC name batch-1 runs but read only their `config.yaml` and compute on simulated runs;".

**BF6 (class: reporting duty).**
In line 111, after "every hit on a batch-1 or reference run is listed under "What was known".", insert:

"Before that run, `search.py` is extended to flag four kinds of call its draft-24 version does not see (round 2 found them by hand): a Bash command that reads files under `runs/` through a glob or a loop over folders (`for d in */`, `runs/*/`); a `cd` into a run folder followed by a bare file name; a `.py` file written by `cat` or `tee` with a heredoc and run later (treated as a Write); and a Grep tool call whose path is under `runs/`. For each hit on a REG-19 run, a batch-1 run or a reference run it prints the whole command (tool-call inputs only). The [DECISION] (delegate) cites that output; a hit beyond (i)–(v), REG-20's smoke test and REG-19's scripts falls under the rules above."

**BF7 (class: tag).**
Replace every "FILE(docs/probe/20261113_reg19/ops_r3/common.sh:34)" (lines 54–55) with "FILE(docs/probe/20261113_reg19/ops_r3/common.sh:36)". The quiet-hours patch of ea4a25e moved `ALLOWED` down two lines; line 34 is now `CONTROL_PAT`. At the append, every FILE(path:line) in the entry is checked against E's tree, and the [DECISION] (delegate) says this was done.

**BF8 (class: wording).**
In line 241, replace "BB3's E1 sentence for the old line 231 is covered: no cut at the first `reg19_final_*` commit remains." with:

"E1 (owner-proxy on draft 12, line 186) is replaced by a stricter cut: a change of a validity flag or of the counted seeds is judged from this entry's commit, so the batch-2 [RESULT] gives no time for it; BB3's sentence for the old line 231 has no object, since no cut at a `reg19_final_*` commit remains."

**BF9 (class: reporting duty).**
The [DECISION] (delegate) that approves this entry is written anew for the final draft. (docs/drafts/reg21_decision_draft1.md still describes the record, its cut and E2's three records, none of which has an object.) Besides what the stopping rule asks of it, it states:
- (a) BB5, verbatim: "The delegate makes no change to the stopping rule after this entry is appended."
- (b) `git diff --stat 8164211 E -- <the 26 frozen files>`, verbatim and empty. If it is not empty, the entry is not appended, and the draft returns to rule F and an owner-proxy pass.
- (c) The closure script's verbatim output at E (BF2).
- (d) The PROBE path of the extended search's output (BF6).
- (e) "The review-stop entry (FILE(docs/decisions.md:4406)) was appended in ba67e55 before any review of its own, although the delegation has a delegate entry written only after rule F and an owner-proxy approval; the owner-proxy's BB9 had timed it before rule F round 17. Round 2's owner-proxy approved its content with BF10."
- (f) "The whole-file freeze departs from the approved plan's 'REG-20 code goes into new functions or files' (FILE(docs/drafts/plan_2026-11-13.md:50)): until both batch 2s are computed or declared not computed, new code goes into new files only, and work that needs a frozen file is prepared on a branch or in another worktree and merged into `main` only after."

**BF10 (class: wording, with one stricter rule; due before the next review round is launched or this entry is appended, whichever comes first).**
A [DECISION] (delegate), or REG-21's own if that comes first, adds the following to the review-stop rule, citing FILE(docs/decisions.md:4406):

"(1) In item 5, 'the first commit that adds a `reg19_final_*` file' means the first table file as REG-21's fact (2) defines it (a name matching `^reg19_final_(err_)?[0-9]{8}T[0-9]{6}Z`), and the entry's commit time is earlier than S, the earliest such stamp; the review bundles' copies `reg19_final_sh_for_reference.sh` are not table files. (2) The class of an item under item 2 (wording, a tag, a stricter rule, a reporting duty, or none of these) is the class its reviewer states; where a reviewer states none, the owner-proxy of the same or the next round states it before the item is applied; an item no one has classed counts as none of these. Round 2's owner-proxy classed its own items BF1 to BF10 in its verdict."

## WHICH LATER CHANGES NEED ANOTHER PROXY PASS
- BF1–BF4 or BF10 written other than as given.
- Any other change to facts (1) or (2), the frozen list, the validity cut, "The two batches" or the review-stop rule.
- A rule F round 17 or 18 item on batch 2's standing, unless it is applied as one of the four classes. Under item 4, an item outside them stops the review.
- An extended-search hit beyond (i)–(v) on a REG-19 run, or a print on a batch-1 or reference run of a quantity that line 111 lists. The draft's own rules then send it to rule F and a proxy.
- BF5–BF9 written as given need no further pass.

## NOTES FOR THE OWNER
1. **The glob finding.** It is the serious one. Read literally, draft 24 lost batch 2's primacy the moment it was written. Whoever held REG-19's table could have invoked that reading, or ignored it.
   - The same glob appears in the plan's wording of the fact, in item 5 of FILE(docs/decisions.md:4383) and in item 5 of the review-stop entry.
   - I class BF1 as wording: draft 24 defines S by "the UTC stamp in the name" and ties it to `final.sh`'s files.
   - If you class it otherwise, item 4 of the review-stop rule stops the review now and batch 1 is registered alone. The batch-1-only text still needs BF1's definition.
2. **REG-22 draft 15 has the same problems (DERIVED).** It uses the glob 11 times. Its harness list omits the same three modules: the ast closure of `analysis/c2.py` includes `harness/env_snapshot.py`, `loadgen.py` and `trigger.py`. Its proxy should see BF1–BF3 (BELIEF: the same fixes apply).
3. **Freeze length.** The freeze covers all of the harness's Python and 14 analysis modules for as long as REG-19 is open. That includes any wait for your decision if attempt 3 is lost. REG-20's or E1's harness work must wait or be prepared off `main`.
4. **A possible witness for E.** At the append, `main` could be pushed to the `vm` remote, the VM's bare repository (`git remote -v`; the delegation allows the VM). That would make a later rewrite of E's time detectable, and it lies outside REG-19's pinned working tree. I recommend it but do not require it. I did not check the VM.
5. **The search approach.** "No look is found by a search" has now been under-reported twice: BB1, and here (iii)–(v). The freeze makes looks disclosures rather than switches, and that design is what keeps these misses harmless.

## NOT CHECKED
- Rule F round 17 on draft 24 (not in the bundle).
- REG-22 draft 15, beyond two greps and the closure of `c2.py`.
- Any transcript output; I read tool-call inputs only. So I did not check whether the agent read the outputs of (iii)–(v).
- Whether `GPU KV cache size`, or read (ii)'s patterns, can occur in vLLM's log after start-up. The agent's own check at 2026-11-13 15:31 UTC on a batch-1 run bears on this; I did not read its output.
- Whether `reg19_step`'s stderr ever carried values.
- The VM, its bare repository, the reflog and any pushed history.
- pytest, tools/check_docs.py and tools/context_pack.py.
- runs/ (only pruned from my find), state/ beyond names, the backups, RESUME.md, and queue or probe outputs other than the bundle's search output.

I wrote nothing into the repository. My scratch files (the closure script and the git test repository) are in /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/3cc38f1d-6772-49b6-bed2-738d3f23bcfe/scratchpad.
