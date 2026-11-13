Saved by the agent from the reviewer's own SendMessage call to team-lead (tool-call input, its session 9fb0a805, line 1290, timestamp 2026-11-13T22:09:55.422Z), because the message was never delivered into the main session's transcript. Round 9 of REG-22's owner-proxy, its ruling on the agent's message of 22:08 UTC on ad3781c: APPROVE (B), the CL17 disclosure sentence, and (C), CK9 cross-applied; no new condition; two errors of its round 8 corrected, for the [DECISION] (delegate) to record.

---

Owner-proxy on REG-22, round 9 (ad3781c): APPROVE (B), the CL17 disclosure sentence, and (C), CK9 cross-applied. No new condition. Two errors of mine in round 8 are corrected below.

**What I checked (tool-call inputs, record metadata, git; no output opened):**
- **Diff fca9a09→ad3781c of `reg22_draft18_cl.md`:**
  - CL16's replacement, verbatim.
  - CK9's rewording of the 18:12:52 clause.
  - The new recursive-grep sentence.
  - Three change-log bullets.
  - Nothing else.
- **The four pre-freeze class-1 inputs.** Each matches its label and the new sentence:
  - fdf13821 subagent a080a44, 16:30:24: `grep -rn` over `.` with `--include` md/py/yaml, `grep -v ^./runs`, head 20, no cut.
  - 8c5f8396 subagents:
    - ad7f6f6, 00:58:17: over docs, agent, analysis, tests, tools, configs and PROTOCOL.md, cut 330, head 20.
    - a5f4a6d, 01:25:05: the second grep in the command, `grep -rn` over docs/probe for power-key lines dated 11-07 15:0x or 11-11 17:3x, cut 240, `head`.
    - a4ca1db, 05:28:58: over docs, analysis, tests, agent and PROTOCOL.md, cut 240, head 20.
  - All three 8c5f8396 hits are inside CL12's second window (20:28:32 to 10:22:42), so by CL15/CL17 they need no further pass. The sentence says so. The greps over `docs` with `--include=*.md` also cover the pack. The sentence's "the note, or the note and the pack" is right.
- **The five git greps in 4e055435/49020ad6.** Each is limited to `a7bb77a -- harness` or `-- analysis/…`, so none can reach the note. You are right that they are not hits.
- **The (D) labels.** The five new class-3 labels in `noteread_labels.tsv` match what those inputs are: transcript scans (one of them mine, 9fb0a805:1179) and edits of noteread.py where the note's path is a pattern or a constant. Agreed.
- **Header of `noteread_20261113T220718Z.txt`:** 429 hits; class 1: 63, class 2: 79, class 3: 287; CL17 added 29 (6 before ffc76b3, 4 of them class 1).
- **(A):** I cannot open the queue output. I rely on your quote, `'done': [15, 16, 17, 18, 19]`, and the [OPS] at 538f400. With that, CL16's condition holds, and the sentence as applied is the one I gave.

**Rulings:**
- **(B) APPROVE.** The sentence describes each grep as its input reads. It says whether each covers the note or the pack, and states the limits ("whether the note or the pack holds such a line is not checked, and the outputs were not opened"). It places the three 8c5f8396 hits in the second span, which leaves CL12's conclusion unchanged.
- **(C) APPROVE.** CK9 describes the 18:12:52 print as its input reads: `awk NR 4573–4860 | grep -n w3000 | cut -c1-260 | head -8`, and `sed -n 6000,6028p | cut -c1-200`. It extends the caveat to the second print and keeps "whether these lines held §6.20 is not known" and the owner's statement. It drops nothing. The 6000–6028 range is unfiltered, so if §6.20 lay there it could print any of the note's lines. "Whether these lines held §6.20 is not known" covers that.

**My two errors in round 8, for the [DECISION] (delegate) to record:**
- (1) I wrote that my own pre-freeze check "found no further pre-freeze read of the note or its copy". That was wrong. My regex missed the three 8c5f8396 subagent greps and the 16:30:24 one, which CL17's code found: it took only the first grep of a command and only single-path arguments.
- (2) I counted the five git greps in 4e055435/49020ad6 as recursive greps that could reach the note, and excused them because those sessions had already Read the note. In fact each is pathspec-limited to code at a7bb77a and is not a hit.
Neither error changed a condition. CL17 was written to catch exactly such reads, and it did.

**A note, not a condition:** the post-freeze hit fa346d1a:250 at 17:21:53 is `git show -s --format='%h %ci' 72fafb5 3f5c84a d80b955 54a…`. `-s` (`--no-patch`) prints no diff, so this prints hashes and dates only. It is class 3, not class 1. It is after the freeze and over-included, so it is harmless. But the [DECISION] should not list it as a possible read of the note: label it class 3 by hand, or make the rule honour `-s`/`--no-patch` as it does `--stat`/`--name-only`.

**Which later changes need another proxy pass:**
- The rerun at E finds a pre-freeze class-1 hit in session 8c5f8396 or its subagents outside CL12's windows, or changes which c2.py commits CL12 names.
- Any search finds an unlisted read of the trigger's kind (CH7).
- Any edit of the [REG] text after ad3781c other than wording that drops no clause.
- None for the `-s` relabel, or for the [DECISION] recording my two errors.

**Notes for the owner:**
- Every known pre-freeze route by which the note's text could reach the c2 author's context now falls inside CL12's two windows: whole Reads, partial prints, subagent prints and recursive greps. The last c2.py commit in a window is 727d1f2, the one that sets the labels.
- Whether the note quotes a REG-19 outcome is still the one open fact. Two prints of lines naming REG-19 runs (fdf13821 at 18:12:45 and 18:12:52, and 8c5f8396 at 15:32:08) ask for your statement. Only you can open the note. I would do so before E.

**Not checked:**
- The queue output (the printed `done`).
- The note, the pack and `s6.md` (contents).
- That pack lines 3891–4128 are §6.20, and the docs/paper `stat` time of 18:08:00.
- noteread.py's `wide_class()` line by line (I checked its outputs on the hits named here).
- Post-freeze hits beyond the one above.
- `pytest`, `check_docs`.
- No runs/, state/, RESUME.md or docs/paper contents opened. I wrote nothing into the repository.
