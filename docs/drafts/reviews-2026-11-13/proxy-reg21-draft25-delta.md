# proxy-reg21-draft25-delta (proxy-reg21-d25), verbatim

Saved by the agent from the teammate message received in the main session transcript (message timestamp 2026-11-13T16:47:04.985Z). Round 3 on the freeze (the last), owner-proxy on REG-21 draft 25: APPROVE on BJ1-BJ7 (all BEFORE). Written before the [CORR] at decisions.md:4453 reached it (verdict message 16:47 UTC; that [CORR] and the agent's reading were sent at about 16:45-16:50 UTC); an addendum, if any, is saved apart.

---

Owner-proxy, round 3 on the freeze (the last), REG-21 draft 25 (bundle reg21_r18): APPROVE on conditions BJ1–BJ7, all BEFORE the entry is appended. None of them is a design change.

# proxy-reg21-draft25-delta (round 3 on the freeze)

**Decision: APPROVE, on conditions BJ1–BJ7, all BEFORE the entry is appended.**
- **Classes:** BJ1, BJ2, BJ5 and BJ7 are wording. BJ3 is a disclosure. BJ4 is a stricter rule, with a reporting duty and a disclosure. BJ6 is a reporting duty and a disclosure. None is a design change, so under the review-stop rule (FILE(docs/decisions.md:4406), items 2–4, and the amendment, FILE(docs/decisions.md:4437), part (2)) this pass does not stop the review.
- **Not covered:** this approval does not cover rule F round 18's items, which I have not seen. If round 18 is NOT READY on batch 2's standing with an item outside the four classes, item 4 applies: batch 1 is registered alone and batch 2 is labelled retrospective by design.
- **No further pass:** BJ1–BJ7 written verbatim need no further proxy pass.
- **Unreviewed by rule F:** round 3 is the last, so BJ1–BJ7 and whatever round 18 asks enter the entry without a rule F review. For that reason I tested BJ4's command myself (Q4).

## Integrity checks (mine)
- **HEAD and the review base:** HEAD is a8036fd. `git diff --stat 90cd0a9 HEAD` touches only agent/STATE.md, docs/context-pack.md and docs/status.md.
- **Bundle copies:** byte-identical (cmp) to the repository files:
  - registration_draft25 = docs/drafts/reg21_draft25.md; the draft 24 copy = docs/drafts/reg21_draft24.md;
  - owner_proxy_on_draft24 = proxy-reg21-draft24-delta.md; round17_rule_f = rulef-reg21-draft24-r17.md;
  - transcript_search.py, transcript_search2.py and closure.py = the files under docs/probe/;
  - final_sh_for_reference.sh, the common.sh copy and the launch.sh copy = the files in ops_r3.
- **The five entries:** the bundle copies match decisions.md verbatim, at lines 4231 (delegation), 4406 (review-stop rule), 4420 ([CORR] on k1.reuse), 4428 ([CORR] on the interim look) and 4437 (amendment).
- **Frozen files unchanged:** `git diff --stat 8164211 HEAD -- <the 26 frozen files>` is empty.
- **Closure:** `closure.py analysis/k3w.py` prints the bundle's 26 files, both in the working tree and with `--at HEAD`.
- **No table file anywhere.** No name matching `^reg19_final_(err_)?[0-9]{8}T[0-9]{6}Z` is found:
  - in any of the three worktrees (runs/, .git and .venv pruned; names only);
  - added by any commit on any ref;
  - quoted in decisions.md.
  The 15 non-matching `reg19_final_sh_for_reference.sh` copies remain: 9 under `_to_delete/`, 6 in older bundles. The reg21_r18 bundle uses `final_sh_for_reference.sh`.
- **Ignored and untracked files:** `git status --porcelain --ignored --untracked-files=all -- analysis harness` lists only two PNGs under analysis/figures/ and `__pycache__`.
- **FILE citations hold at HEAD.** I checked:
  - decisions.md:3785, 4084, 4205, 4276, 4279, 4284, 4308, 4383, 4428, 4437;
  - common.sh:36 (`ALLOWED`), common.sh:210, queue.sh:77, final.sh:20 and :29, launch.sh:28 and :51;
  - gate.py:751 and :2022, k3.py:395, withheld.py:7, :26 and :51, load.py:11 and :20, k1.py:57, k3w.py:91;
  - harness/run.py:23, :24 and :80, recorder.py:141, plan_2026-11-13.md:50.

## Q1. Are BF1–BF8 met as written, and are the departures acceptable?
- **BF1:** met.
  - The fact (2) text (1288 characters) and the limits sentence are verbatim (substring check).
  - "Table file" replaces the old glob wherever a rule refers to these files. The remaining `reg19_final_*` occurrences are change-log lines describing earlier drafts (lines 211, 229, 240, 249) and BF8's own words (line 241).
  - The change-log sentence is a paraphrase: it drops "(ab6988f to ba67e55)" and "a table file is now defined by `final.sh`'s names (BF1)". It sets no rule. As the further pass BF1 asks for, I accept it.
- **BF2:** met verbatim, including line 239. Not taking BE2's "the list in the entry governs" is right: BF2's union rule is stricter.
- **BF3:** met verbatim. BE3's added `git diff --quiet E B -- <frozen>` is acceptable and strictly stricter:
  - when B descends from E and the log is empty, the diff is empty too;
  - otherwise it catches what the log cannot.
- **BF4:** met verbatim.
- **BF5:** met.
  - (a) is verbatim.
  - (b) is verbatim, with the (vi)–(ix) passage placed between its "has not read" sentence and its last sentence. That is acceptable.
  - (c), second edit: verbatim.
  - (c), first edit: "five" → "the nine listed there, (i) to (ix)". Acceptable, because it is the true count.
- **BF6:** verbatim, but its own sentence still says "a hit beyond (i)–(v)" (BJ1).
  - The extension as a new file, search2.py (committed in 723a16b), is acceptable.
  - search.py stays unchanged as the source of its earlier output.
- **BF7:** met. Both `common.sh:34` citations now read `:36`, and line 36 is `ALLOWED` at HEAD.
- **BF8:** met verbatim. BE-O7 marks line 186.
- **BE1:**
  - Its extra limit (a table saved under a name that is not a table file) is an honest limit.
  - Its rule against new `reg19_final_` names is stricter and costs nothing beyond renaming the bundle copies, which is already done. Acceptable.
- **BE5:** acceptable. Its cost: until batch 2 is computed or declared not computed, no run whose folder matches the batch-2 pattern (other than REG-19's) or `*_sweep_l1pl350_pc_off_r*` may be made.
  - E1 is not barred. Its folders match `*_sweep_l1pl350cl_pc_off_r*` (FILE(analysis/withheld.py:30)), which the reference pattern does not match: "l1pl350_" against "l1pl350cl_" (DERIVED: fnmatch).
  - Its text contradicts itself on stamped names (BJ7).
- **BE6:** acceptable. Its default replaces a choice that would be made after the table with a rule fixed before it.
- **BE-O5 and BE-O6 as reporting duties:** acceptable.
  - "image files" is not a mechanical filter (BJ5).
  - The committed form of the same hole is not covered at all (BJ4).

## Q2. Does the amendment entry meet BF10, and is its disclosure of the order honest?
- **BF10:** met. BF10 and BF9(e) appear verbatim in decisions.md (substring check). Its citations hold:
  - proxy-reg22-draft15-delta.md:37, :45 and :96;
  - rulef-reg22-draft15-r10.md:7, :57, :81, :102, :126 and :174;
  - rulef-reg21-draft24-r17.md:7 and proxy-reg21-draft24-delta.md:176.
- **Its application to round 2 is correct.** Every round-2 item was classed by its own reviewer as wording, a tag, a stricter rule, a reporting duty or a disclosure. BH10 has no class, but it is not about batch 2's standing. So item 4 does not fire and round 3 is the last. As round 3's owner-proxy (part (2)), I approve that application.
- **The order disclosure is honest as far as it goes.** It says the amendment was appended before a rule F review. It does not say that its own text beyond BF10's quoted words was appended before any owner-proxy pass: the application to round 2, and the reading that round 3 is the last. This pass is that pass; BJ6(c) records it.

## Q3. Is "What was known" honest and complete?
- **Method:** in search2's dry-run output I read:
  - every record from 2026-11-11 17:15 UTC on that names a REG-19 run or globs or loops over runs/;
  - every `ran` hit since 2026-11-09 that search.py's output lacks.
  I read the text, never the output, of six scripts: s57_inv.py, s57_fam.py, s57_heavy.py, trace_sealed_reg19.py, the review noise.py and t2.py. I opened no output anywhere.
- **The listed reads (i)–(ix) are accurate, and none could have shown a REG-19 burst run's outcome.**
  - On the three burst folders, every read is a listing or a size, `config.yaml` lines, `env.json` fields, `server.log` start-up lines (line 14, the first KV-size match), or validity.
  - s57_inv.py masks the `no_errors` detail for w3000 folders.
  - s57_heavy.py skips w3000 folders.
  - trace_sealed_reg19.py replaces `load_run` and `find_runs` and points at a fake runs folder.
- **Read (vi), the A14 recheck, is a run of `analysis/` code over REG-19's folders.** It is listed before the append, so line 54's trigger ("beyond what is listed here") does not fire. BF6's "(i)–(v)" sentence gives a second reading under which it does (BJ1).
- **Unlisted reads I found:**
  - **(a) 2026-11-12 14:09:43 UTC, fdf13821 line 443.**
    - What it did: ran `k1.cold_backlogged` on REG-17's and REG-18's five λ = 2.0 burst runs and on REG-10's open-loop run.
    - What it printed:
      - the `cold_backlogged` flag;
      - `x['end']` and `x['base']`: hit rate, waiting line, KV, and the end window's request count or the baseline's percent fast, in the code as committed at 15:33 UTC (1cface7; BELIEF that the keys were the same at 14:09);
      - `overlap_after` for REG-10's run.
    - Who found it: search2 lists it as `ran`; search.py missed it.
    - What it adds: it is a print on batch-1 runs of the same kind as BF5(a). If the keys were as committed, it is not a quantity line 111 lists. It is not disclosed (BJ3).
  - **(b) 2026-11-12 13:54:56 UTC, bc2fcf6d line 10235.**
    - What it did: `tail -5` of the queue's output file for seed 17's burst config.
    - When: 12 s after a launch that stopped on a CLAUDE.md mismatch, and before the relaunch at 13:55:32. The burst folder is stamped 13:55:38.
    - So it cannot hold a line that run wrote (DERIVED from the times; BELIEF that the VM's folder stamps are UTC).
    - The [DECISION]'s classification of `names_reg19_run` hits covers it. I ask for no text.
  - **(c) 2026-11-12 15:46:09 UTC, fdf13821 line 1862.**
    - What it did: `head -c 700` of `requests.jsonl` and `head -c 600` of `metrics.jsonl` of the λ = 2 reference run.
    - What it printed: the run's first raw records. That is no quantity line 111 lists. I ask for no text.
- **Answer:** no listed or unlisted read I found could have shown a REG-19 burst run's outcome. "What was known" is honest. It is complete except for (a).

## Q4. Is closure.py's output the right frozen set, and are its limits honest?
- **The 26 files are right for static imports.**
  - The only dynamic import is `__import__("os")`.
  - On k3w's path the code reads one repository file at run time, docs/decisions.md (the seal). `configs/defaults.yaml` is read only through `gate._burst_cfg` and `harness.config.with_defaults`, and k3w's path does not reach them (DERIVED: grep of the functions k3w imports; BELIEF that the grep is complete).
  - It reads one environment variable, `AFTERSHOCK_UNSEAL` (FILE(analysis/withheld.py:51)). Once REG-19's seal is lifted it changes nothing for batch 2: no other seal pattern matches the batch-2 or reference pattern (DERIVED).
- **Its stated limits are incomplete, and one is the wrong way round.**
  - **Lookup order.** closure.py looks for `X.py` before `X/__init__.py`; Python does the reverse. In my scratch test, with both `pkg/load.py` and `pkg/load/__init__.py` present, `from pkg import load` imported the folder (PROBE: my scratchpad, no project data).
  - **Shadow files fact (1) cannot see:**
    - a committed `analysis/load/__init__.py` would be imported in place of the frozen `analysis/load.py`;
    - a root-level `yaml.py` would replace the library, because `uv run python -m` puts the repository root first on the path (tested).
    Fact (1)'s three commands are limited to the frozen paths. BE-O5's status line covers only untracked files, and only as a reported breach. So "this change touches no frozen file" becomes arguable again, which is the argument the freeze was built to end (BJ4).
  - **The wrong-way-round limit.** "A file outside the repository that shadows a repository module (a site-packages module of the same name)" cannot happen while the root comes first on the path. The reverse is the real risk.

## Q5. Would the owner approve registering this?
- **Yes (BELIEF as to the owner)**, with BJ1–BJ7 applied and BF9 written into the [DECISION] (delegate). This holds once rule F round 18 is READY, or raises on batch 2's standing only items of the four classes.
- **BF9 is not met yet.** The only decision draft, docs/drafts/reg21_decision_draft2.md (untracked), describes draft 24 and "the 22 frozen files". It contains none of BF9(a), (e) or (f), no closure output and no search2 PROBE path (DERIVED: substring checks).

## CONDITIONS (all BEFORE)

**BJ1 (class: wording).**
In line 111, replace "a hit beyond (i)–(v), REG-20's smoke test and REG-19's scripts falls under the rules above." with:

"a hit beyond (i)–(ix), REG-20's smoke test, the same session's earlier command listed under "What was known" and REG-19's scripts falls under the rules above (BF6's "(i)–(v)" was written before (vi) to (ix) were found; round 3's owner-proxy, BJ1)."

Why: as written, read (vi) (the A14 recheck, a run of `analysis/` code on REG-19 folders) is "a hit beyond (i)–(v)". Line 111's last sentence would then label batch 2 retrospective by design, while line 54's "beyond what is listed here" would not. Someone holding REG-19's table could pick either reading.

**BJ2 (class: wording).**
In line 3, replace "Draft 24. It is draft 23 with round 1 on the freeze written in:" with:

"Draft 25. It is draft 24 with round 2 on the freeze written in (rule F round 17's BE1–BE6 and the owner-proxy's BF1–BF8 on draft 24; BF9 goes into the [DECISION] (delegate), BF10 into the amendment of the review-stop rule, FILE(docs/decisions.md:4437); the change log's last heading). Draft 24 is draft 23 with round 1 on the freeze written in:"

At the end of line 3, after "REJECT of draft 23 as written, BB1–BB9).", add:

" Round 2 on the freeze: rule F round 17 on draft 24 (FILE(docs/drafts/reviews-2026-11-13/rulef-reg21-draft24-r17.md), NOT READY, BE1–BE6); owner-proxy on draft 24 (FILE(docs/drafts/reviews-2026-11-13/proxy-reg21-draft24-delta.md), APPROVE on BF1–BF10). Round 3, the last: rule F round 18 and the owner-proxy on draft 25, verbatim in the [DECISION] (delegate)."

**BJ3 (class: disclosure).**
At the end of line 49, after "the values in REG-20's entry are the only ones quoted.", insert:

" An earlier command of the same session (2026-11-12 14:09:43 UTC, fdf13821 line 443; listed by `search2.py`'s dry run, PROBE(docs/drafts/review_bundles/reg21_r18/transcript_search2_dryrun_20261113T162249Z.txt), not by `search.py`) ran `k1.cold_backlogged` on the same five runs and on REG-10's open-loop run, and printed each run's flag and the levels it computes in the end window and the baseline (in the code as committed at 15:33 UTC, 1cface7: the hit rate, the waiting line and KV in both, the request count in the end window and percent fast in the baseline; BELIEF that the keys were the same at 14:09, when `analysis/k1.py` was not yet committed), and, for REG-10's run, the overlap share after the burst. The agent has not read that output either (BELIEF: the agent's own report)."

In line 111, replace "the only such hit is REG-20's smoke test of 2026-11-12 on five batch-1 runs ("What was known");" with:

"the known such hits are REG-20's smoke test of 2026-11-12 on five batch-1 runs and the same session's earlier command at 14:09:43 UTC on the same runs ("What was known"; the second found by `search2.py`), and the [DECISION] (delegate)'s classification of every `ran` hit of `search2.py` settles the list;"

If the agent has read any of that output, it writes what it read in place of the "has not read" sentence.

**BJ4 (class: a stricter rule, with a reporting duty and a disclosure).**
- **(a)** In line 104, fact (1), after "and `git status --porcelain -- <the frozen files>` prints nothing in that checkout.", insert:

" Nor does any commit from E to B add, or rename into, a path that Python would import in place of a frozen file or of a library the frozen files import: `git log -m --diff-filter=AR --name-only --format= E..B | grep -E '^([^/]+\.py|[^/]+/__init__\.py|(analysis|harness)/(derived|floor|gate|k1|k3|k3w|load|margin|modelf|modelf_sim|stats|tables|withheld|checks|config|env_snapshot|loadgen|recorder|run|trigger|workload)/.*)$'` prints nothing (Python imports a package folder such as `analysis/load/` before the module `analysis/load.py` of the same name, and `uv run python -m` puts the repository root first on the path, so a new `yaml.py` there would replace the library; a new file anywhere else, a new folder under `analysis/` or `harness/` with another name included, does not count; PROBE: round 3's owner-proxy's scratch repository, no project data; for `8164211..HEAD` the command printed nothing on 2026-11-13)."

- **(b)** In line 112, replace "and new code goes into new files; no run whose folder" with:

"and new code goes into new files, none of them a `.py` file or a package at the repository root or inside a folder named after a frozen module (`analysis/load/`, `harness/run/`, …); no run whose folder"

- **(c)** Next to closure.py's output, the [DECISION] (delegate) states:

"`closure.py` resolves `X.py` before `X/__init__.py`, the reverse of Python's order, and does not see a file in the repository that shadows a frozen module or a library (a package folder named after a frozen module; a root-level module). Its docstring's 'a file outside the repository that shadows a repository module' is the wrong way round, since `uv run python -m` puts the repository root first. Fact (1)'s added command covers committed files of these kinds; the batch-2 [RESULT]'s `--ignored` status covers untracked ones, as a reported breach only."

- **Tested in my scratch repository** with no project data. A commit adding `analysis/load/__init__.py` and `yaml.py` is flagged; so is a side branch adding `numpy/__init__.py` and merged with `--no-ff`, and so is `yaml.py` added and later removed. New files `analysis/k5.py` and `tools/y.py` are not flagged. On the real repository, for 8164211..HEAD, it prints nothing.

**BJ5 (class: wording).**
In line 104, replace "with `__pycache__` and image files left out" with:

"with `__pycache__` folders and the files under `analysis/figures/` left out"

**BJ6 (class: reporting duty and disclosure).**
The [DECISION] (delegate) is written anew. It is not docs/drafts/reg21_decision_draft2.md, which describes draft 24 and 22 files. Besides what the stopping rule asks and BF9(a)–(f) verbatim, it carries:
- **(a)** BJ4(c)'s statement.
- **(b)** The verbatim output at E of BJ4(a)'s command for `8164211..E`, empty. If it is not empty, the entry is not appended.
- **(c)** This sentence: "The amendment of the review-stop rule (FILE(docs/decisions.md:4437)) was appended before any rule F review, and its text beyond BF10's quoted words (its application to round 2 and its reading that round 3 is the last) before any owner-proxy pass; round 3's owner-proxy on REG-21 approved both."
- **(d)** Rule F round 18's verdict and this verdict, verbatim.

**BJ7 (class: wording).**
In line 104, replace "other than `final.sh`'s own files and the entry that reports and commits them (all others write `reg19_final_<stamp>`)" with:

"other than `final.sh`'s own files, the entry that reports and commits them, and, once they exist, the entries that cite them or quote the verbatim output of this rule's commands (REG-19's [RESULT], the batch-2 [RESULT]s of REG-21 and REG-22), each copying the name from the file itself (all others write `reg19_final_<stamp>`)"

Why: the same paragraph requires the batch-2 [RESULT] to quote fact (2)'s command output and "the path ... that adds it" for the stamp that sets S. Hand duty (b) has REG-19's [RESULT] cite the table file. As written, each of these would be a breach that the [RESULT] reports against itself.

## WHICH LATER CHANGES NEED ANOTHER PROXY PASS
- BJ1–BJ7 written other than as given.
- A rule F round 18 item applied to facts (1) or (2), the frozen list, the validity cut or the review-stop rule other than in its reviewer's verbatim text. Item 4 decides whether such an item stops the review.
- A search2 hit at the append beyond the reads listed after BJ1 and BJ3. The draft's own rules then send it to rule F and an owner-proxy pass.
- A non-empty output of BF9(b) or BJ6(b).
- The [DECISION] (delegate) needs no further pass if it carries BF9 and BJ6 verbatim.

## NOTES FOR THE OWNER
1. **BJ4 is the substantive one.** A committed shadow file is unlikely as an honest mistake. It would still reopen the "this change touches no frozen file" argument that the freeze was built to end. Because round 3 is the last, no rule F round reviews its text; I tested it instead (BJ4).
2. **Round 3 adds text no rule F round reviews:** BJ1–BJ7 and whatever round 18 asks. The review-stop rule chose that trade.
3. **REG-22 draft 16 has fact (1) in the same shape** (one match of "prints nothing in that checkout"). So BJ4 likely applies there too (BELIEF; I read no more of REG-22).
4. **"No look is found by a search" has now under-reported a third time:** the 14:09:43 print on batch-1 runs, after BB1 and BF5. The freeze keeps such misses harmless. The [DECISION]'s classification of every `ran` hit is where any others would show up.
5. **Cost of BE5 with the freeze,** until both batch 2s are settled:
   - no new cache-off open-loop sweep at 350 W under the reference's name pattern;
   - no change to the harness;
   - no new seal.
   E1 is not barred by the pattern.
6. **HEAD moved during this review**, to a8036fd. No frozen file was touched.

## NOT CHECKED
- Rule F round 18, which is not in the bundle.
- REG-22 draft 16 and its reviews, beyond six greps.
- search2 records before 2026-11-11 17:15 UTC, and `ran` hits before 2026-11-09. After those dates I read command texts and classes only, and opened no output.
- Whether the A14 recheck printed only what decisions.md:4205 says.
- Whether "GPU KV cache size" can be logged after start-up. vLLM is not installed on the Mac.
- The VM, the clock behind its folder stamps, the reflog and any pushed history.
- pytest, tools/check_docs.py and tools/context_pack.py.
- runs/ beyond names, state/ beyond names, the backups, RESUME.md, and queue or probe outputs other than the bundle's search outputs.
- Script texts that no longer exist. One `noise.py` path in search2's output points at another session's file of the same name; the copy I read is fdf13821's own, and it is synthetic.

I wrote nothing into the repository. My scratch files (check scripts, the shadow test, the scratch git repository) are in /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/0ec2e539-fb6a-424d-bac1-c1fe28ca889c/scratchpad.
