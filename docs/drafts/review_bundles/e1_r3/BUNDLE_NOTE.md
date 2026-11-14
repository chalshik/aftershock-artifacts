# Bundle e1_r3 (E1 draft 7, review round 3), built at HEAD 3c8e5dc6d87ed7dbf364df49dfa2780282ff4deb

Contents, all listed with sha256 in MANIFEST.txt:

**Registration text**
- `registration_draft7.md`: byte copy of `docs/drafts/e1_draft7.md`.
- `registration_draft6_previous.md`: byte copy of draft 6.
- `text_diff_draft6_to_draft7.diff`: `git diff --no-index --word-diff=plain` of the two.

**Item map and reviews**
- `e1_draft7_itemmap.md`: byte copy of `docs/drafts/e1_draft7_itemmap.md`. It holds:
  - where each of DC1–DC9, DC-O1–DC-O5 and DD1–DD12 went;
  - every departure from a review's words (nine, numbered);
  - the findings left for round 3.
- `rulef-e1-draft6-r2.md` and `proxy-e1-draft6.md`: byte copies of the two round-2 reviews (`docs/drafts/reviews-2026-11-13/`).
- `reviewer_patches/`: byte copies of the reviewer's seven patches as saved in `docs/drafts/e1_r3/`.

**Code: `e1.py` and `test_e1.py`**
- These are **not copies of the main checkout.** They are HEAD's `analysis/e1.py` and `tests/test_e1.py` with `e1_py_draft7.patch` and `test_e1_draft7.patch` applied.
- Each patch is cumulative against HEAD: draft 6's patch, then the reviewer's DC2/DC8 patch. Applied to a fresh `git archive HEAD` copy, they give these two files byte for byte (sha256 `428771e0…` and `dd3f52c5…`, the same as the reviewer's patched files).
- With both files in place, `tests/test_e1.py` gives 16 passed, and `tests/test_e1.py tests/test_k2.py tests/test_withheld.py` gives 39 passed. Both were run in the scratch copy with the repo's `.venv` interpreter. The main checkout keeps HEAD's two files.

**Scripts: `ops/` and `ops_draft7.patch`**
- `ops/` holds HEAD's `docs/probe/20261113_e1/ops/` files with `ops_draft7.patch` applied (DC-O1, DC-O2, DC-O3 and DC4's README edit), plus the draft-7 sandbox output `sandbox_20261113T231637Z.txt` (passed 192, failed 0, run on these scripts in a scratch copy).
- `vm_state.py`, `session_probe.sh`, `launch.sh`, `DESIGN_NOTES.md` and `e1_commit.txt` (still `UNSET`) equal HEAD's.
- `ops_draft7.patch` uses repo-root paths and passes `git apply --check` on the main checkout. It is not applied there.

**Diffs**
- `code_diffs_vs_HEAD/`: one diff per changed file, HEAD to this bundle's copy (HEAD's ops files equal 97a6438's, draft 6's commit).
- `code_diffs_vs_draft6/`: `e1.py` and `test_e1.py` from bundle e1_r2's files to these. Their changed lines equal the reviewer's DC2/DC8 patches (checked).
- `harness_diff_a7bb77a_to_9e249b1.diff`: byte copy of e1_r2's (DA11). The harness is unchanged: `harness/` has tree `e8a3e1e7…` at HEAD, as at 9e249b1 and e87884d.

**Other files**
- The seven configs: `git show HEAD:configs/<name>`, unchanged since e87884d.
- `delegation_entry.md` and `owner_e1_to_review_entry.md`: byte copies of e1_r2's.
- `decisions_headings_cited.txt`: the seven decisions.md headings that draft 7 newly cites, each with its line number: 4166, 4611, 16322, 16421, 16517, 16571 and 16798. The last two, the batch-2 [RESULT]s of 7230ae8, were added after HEAD 3c8e5dc; they are cited in the one sentence saying the freeze disclosure is moot.

**Not in the bundle and not changed:** `agent/RUNBOOK.md` (the RUNBOOK text is in draft 7, "RUNBOOK, for the approval commit"), `docs/decisions.md`, `docs/model.md`, any config, and anything under `analysis/`, `tests/`, `harness/` or `docs/probe/` in the main checkout.
