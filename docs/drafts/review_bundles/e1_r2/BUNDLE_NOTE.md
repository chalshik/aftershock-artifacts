# Bundle e1_r2 (E1 draft 6, review round 2), built at HEAD 538f400325bfe2252cc151d3b3d8d764f40930fb

Contents, all listed with sha256 in MANIFEST.txt:
- `registration_draft6.md`: byte copy of `docs/drafts/e1_draft6.md`. `registration_draft5_previous.md`: byte copy of draft 5. `text_diff_draft5_to_draft6.diff`: `git diff --no-index --word-diff=plain` of the two.
- `e1_draft6_itemmap.md`: byte copy of `docs/drafts/e1_draft6_itemmap.md`. It says where each of DA1–DA12, DA-O1–DA-O7 and DB1–DB12 went, lists every departure from verbatim and every DA/DB conflict, and holds the merged RUNBOOK proposal (DA5 + DB11) and the findings left for round 2.
- `rulef-e1-draft5-r1.md` and `proxy-e1-draft5.md`: byte copies of the two round-1 reviews (`docs/drafts/reviews-2026-11-13/`).
- `ops/`: byte copies of the main checkout's `docs/probe/20261113_e1/ops/` files, including the sandbox output `sandbox_20261113T214307Z.txt` (passed 184, failed 0). `vm_state.py`, `session_probe.sh` and `e1_commit.txt` (still `UNSET`) are unchanged since e87884d.
- `e1.py` and `test_e1.py`: **not copies of the main checkout.** They are HEAD's `analysis/e1.py` and `tests/test_e1.py` with `e1_draft6.patch` and `test_e1_draft6.patch` applied (`git apply` onto HEAD's two files gives these two files byte for byte; checked). Draft 6 holds its code changes as patches by the rule of decisions.md 2026-11-13 [CORR]: an edit of `analysis/e1.py` in the main checkout had stopped REG-19's queue. `e1.py` is byte-equal to `docs/drafts/e1_r2/e1.py.draft6` (sha256 615e386f…), which the agent saved. With both files in place, `tests/test_e1.py` gives 16 passed. That was run in a scratch copy of `analysis/`, `harness/` and `configs/` with the repo's `.venv` interpreter; the main checkout keeps HEAD's two files (12 passed).
- `code_diffs_vs_e87884d/`: `git diff e87884d -- <file>` for each changed script, README and DESIGN_NOTES (e87884d equals HEAD for these files), and the diffs of `e1.py` and `test_e1.py` from e87884d to the patched copies (e87884d's `e1.py` equals HEAD's).
- `harness_diff_a7bb77a_to_9e249b1.diff`: `git diff a7bb77a 9e249b1 -- harness/` (DA11), byte-equal to e1_r1's `harness_diff_a7bb77a_to_HEAD.diff`. The harness is unchanged since: `harness/` has tree e8a3e1e7… at 9e249b1, e87884d and HEAD.
- The seven configs, byte copies, unchanged since e87884d.
- `delegation_entry.md` and `owner_e1_to_review_entry.md`: byte copies of e1_r1's (decisions.md lines 4231-4238 and 4516-4521).

Not in the bundle and not changed: `agent/RUNBOOK.md` (DA5 and DB11 go into the approval commit; proposal in the item map), `docs/decisions.md`, `docs/model.md`, any config.
