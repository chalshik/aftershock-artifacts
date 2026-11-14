# REG-24 draft 3, addendum: the drop length is ruled by delegation, and the commit order after REG-20 arm A

This addendum is for rule F round 3 and the owner-proxy. It is not a decisions.md entry and approves nothing. It was written 2026-11-14 ≈ 08:22 UTC (`date -u`) by the agent. Draft 3 (`docs/drafts/reg24_confirm_draft3.md`; patches `docs/drafts/reg24_r3/reg24.patch`, sha256 `aa9a2548…`, and `withheld.patch`, sha256 `a020a335…`) is unchanged. Both patches still apply together to an export of HEAD `9336dbc` (PROBE: `git apply --check`, this writer, 08:20 UTC), and `git diff --stat 6992e0e 9336dbc -- analysis tests configs harness pyproject.toml uv.lock` is empty.

## 1. What changed in authority since draft 3

- The owner ended the autonomous mode (decisions.md 2026-11-14 [DECISION] (owner), "The autonomous mode ended").
- In the next entry, the owner delegated again the approvals of all work that needs no VM (decisions.md 2026-11-14 [DECISION] (owner), "The owner delegates the approvals of all work that needs no VM to the agent", committed in `9336dbc`). Its list includes "a PROTOCOL row that a reviewed registration needs". The conditions are the 2026-11-13 delegation's: rule F by a separate subagent, quoted verbatim, and an independent owner-proxy's approval; a reject from either is binding. A GPU run's start entry and launch, and everything on the VM, are not delegated.
- Draft 3 says the drop is "the owner's" or "the owner's alone" (lines 16, 24, 637, 761) because a PROTOCOL change was not delegated on 2026-11-13. Under the new entry, the delegate may rule on it, through this round and the owner-proxy.

## 2. The ruling the agent proposes: option (a), 9000 s on seed 43

- The reasons are draft 3's: it is the only option with a real chance of testing condition 6; the seed and drop came from the rule frozen before the scan; under (b), P(`drop_inconclusive`) ≈ 0.53 and K3's point is lost (BELIEF, draft 3's "Prediction"; FILE(agent/FOR_AUTHOR.md:11-16)).
- No REG-24 run exists, so no data judges this choice (rule A5 does not apply).
- The PROTOCOL §6 row is draft 3's row in "Setup" (draft 3 line 95). Its last cell becomes `2026-11-1x [REG] REG-24 (delegate, decisions.md 2026-11-14 delegation)`.

## 3. Text changes this ruling makes to draft 3 (to be applied in draft 4 with this round's items)

1. Line 16, line 24 ("Not approved"), item 4 of "What must exist" (line 637) and open point 1 (line 761): "the owner's alone" becomes "ruled by the delegate under the owner's 2026-11-14 delegation (9336dbc), after rule F round 3 and the owner-proxy". The rest of item 4 stays: the ruling is committed before `[REG] REG-24` or in the approval heading itself.
2. Item 4's headings: `## <date> · [DECISION] (owner|delegate) REG-24: the drop is 9000 s …` or `## <date> · [DECISION] (owner|delegate) REG-24 approved … 9000 s …`.
3. `DROP_PAT` in the ops sketch (line 652): `'^## [0-9]{4}-[0-9]{2}-[0-9]{2} · \[DECISION\] \((owner|delegate)\) REG-24(: the drop is 9000 s| approved .*9000 s)'`. This also answers open point 12's anchoring note: the pattern now needs one of item 4's two forms, not just "9000 s" anywhere after "REG-24".
4. Line 92 ("Owner approval needed, named separately") becomes "Approval needed, named separately: the owner's, or the delegate's under the 2026-11-14 delegation".

## 4. The commit order against REG-20 arm A (proposed; open point 3)

- **REG-20 arm A runs first.** The order in `docs/status.md` ("Next steps", 2026-11-14) is arm A, then D1, then REG-24.
- **Why REG-24 does not register before arm A ends.** Arm A's last required heading is its start entry (`START_PAT`, FILE(docs/probe/20261113_reg20/ops/common.sh:41)). That entry is the owner's and is written only at launch, with the VM back. By E1's rule (draft 3, "Order"), if REG-24's approval landed before it, REG-24 would be first and would hold the VM for ≈ 9.1 h before arm A.
- Arm A's hold also forbids new `SEALS` rows (draft 3, line 607). The line-41 pattern is that of the committed draft-3-era scripts; the patched scripts of arm A's operations draft 4 may change it, but the start entry stays the last required heading.
- **So no REG-24 heading, seal or code is committed before REG-20 arm A's end entry.** Not committed means:
  - none of REG-24's own headings (the drop ruling, `[REG] REG-24`, the approval);
  - `withheld.patch`;
  - `reg24.patch`.
- **Until then, REG-24 is completed as a reviewed draft:**
  - draft 4;
  - the ops scripts and their sandbox;
  - the ops round's rule F pass and owner-proxy pass.

  Each is saved under `docs/drafts/`.
- **After arm A's end entry,** the commits follow draft 3's "What must exist" in order. Between D1 and REG-24, E1's rule decides: the item whose own last required heading lands first runs first.
- This order is a delegate proposal. The owner can set another by an entry.

## 5. Not changed

- Every threshold, the seed rule, both models, the prediction, the code and both patches.
- The VM disk issue stays the owner's (FILE(agent/FOR_AUTHOR.md:7)). Under (a), REG-24's ceiling is ≈ 5.7 GB (BELIEF, draft 3's "Cost").
