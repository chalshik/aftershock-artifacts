# Bundle reg20_ops_r2, built 20261113T233207Z at HEAD 7be592d50887c8b3f42a2ea931a7952825345423

For rule F round 2 and owner-proxy round 2 on draft 2 of the REG-20 arm A operations decision. 0 GPU h. The VM was not contacted. Nothing in this bundle comes from `runs/` (beyond folder names counted in the draft), from a `state/` folder, from a queue output, from a `reg19_final_*` file or from a transcript. No file here is named `reg19_final_*`.

**Nothing is committed.** The ops files are the working tree at the HEAD above.

**Files**

| Path in the bundle | Source |
|---|---|
| `reg20_ops_decision_draft2.md` | `docs/drafts/reg20_ops_decision_draft2.md`, byte copy |
| `reg20_ops_draft2_itemmap.md` | `docs/drafts/reg20_ops_draft2_itemmap.md`, byte copy |
| `reviews/rulef-reg20-ops-draft1-r1.md`, `reviews/proxy-reg20-ops-draft1.md` | `docs/drafts/reviews-2026-11-13/`, the two round-1 reviews, byte copies |
| `ops/*` | `docs/probe/20261113_reg20/ops/<same name>`, byte copies of every file changed or new since c8b482d, plus the saved test outputs (`sandbox_<stamp>.txt`, `test_control_due_<stamp>.txt`) |
| `withdrawn/gate.sh` | written for RB5 (ii) and withdrawn before any use, because commit 3c8e5dc had already computed the gate (draft 2, point 14). It is not in the ops folder. |
| `diff_c8b482d_ops.patch` | `git diff c8b482d -- docs/probe/20261113_reg20/ops`, at the HEAD above |
| `diff_new_files.patch` | `git diff --no-index /dev/null <file>` for `recheck_one.py` and `owner_rulings.txt` |
| `MANIFEST.txt` | sha256 of every file in the bundle except itself |

**Read with care**
- **The main diff covers tracked files only.** `git diff c8b482d` does not show untracked files. The two new scripts are in `diff_new_files.patch`, and the two saved test outputs are copied whole.
- **Three files are unchanged since c8b482d and not copied:** `vm_state.py`, `session_probe.sh` and `control_due.py`. `git diff c8b482d` over them is empty.
- **The brief's premise is out of date.** The brief said REG-19's table "is not yet computed". Commits 047b95e (REG-19's table), 6748c26 (REG-19's [RESULT]) and 3c8e5dc (REG-20's gate) were already on main when draft 2 was written. Draft 2's "Status", "Timing" and point 14 say what changed and when. Its author saw REG-19's outcome only through the commit subject and the first words of the heading at FILE(docs/decisions.md:16517), after the scripts were written.
- **The line numbers** in the draft and the item map are those of the ops files in this bundle.
