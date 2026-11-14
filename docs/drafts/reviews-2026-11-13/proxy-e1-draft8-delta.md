# proxy-e1-draft8-delta (owner-proxy, delta pass on E1 draft 8: where DF1–DF11 meet rule F round 3's DE1–DE7), verbatim

Saved by the agent at 2026-11-14 01:56 UTC from the reviewer's own verdict file (the same in-process subagent as `proxy-e1-draft7.md`, resumed; scratchpad `reviews_r3/proxy-e1-draft8-delta.md`, 8675 bytes, sha256 c8cfbbd130776f9aef80c944d9395ccbb962ff24c2f4c11045039ce071fb80ea, checked on copy; the reviewer's hand-back message named the same sha256). The reviewer's report follows the line '---' unchanged.

---
# Owner-proxy delta on E1 draft 8: where DF1–DF11 meet rule F round 3's DE1–DE7

**Verdict: APPROVE** draft 8 as the [REG] text, with the replacements X1–X4 below.
- DF1 (rule F round 3 verbatim, before `#### Owner-proxy pass`) is added at assembly.
- Apply X1–X4 before DF1's quote is inserted. Each anchor occurs once in draft 8 (checked by script). After the quote is in, X1's anchor also occurs inside the quoted DE3, which stays verbatim.
- No DE item is changed in its own words. X1 rewords one sentence of DE3. X2 adjusts DF5's lead-in to DE5. X3 removes DF5's sentence that DE5 now replaces. So round 3's "provided DE1–DE7 verbatim" still holds, except for X1, which settles a contradiction between DE3 and DF3 that round 3 could not see. X1 is the stricter reading, so it needs no new rule F round.
- **Checked:**
  - draft 8 sha256 `e1802497…`;
  - the saved copy of my pass, body sha256 `5a3fbe61…`, equal to mine;
  - every DE1–DE7, DE-O2 and DE-O5 replacement text occurs once in draft 8, and every DE anchor is gone from it;
  - DE4 and DE6(d) (approval commit) and DE-O1 and DE-O6 (not taken) are absent, as stated;
  - `git diff --stat f43a5a1 HEAD` over `agent/RUNBOOK.md analysis tests harness configs docs/probe/20261113_e1 docs/drafts/e1_r3` is empty.
- **Not opened:** runs/, state/, RESUME.md, docs/paper, the backups folder. No VM. Nothing written in the repo.

## The seven points

**1. DE1's row against DF7(ii)/(iii): DE1 stands verbatim. DF7(ii) and (iii) are withdrawn.**
- DE1's row cites `[REG] E1, "E1 holds the VM"`. That paragraph now ends with DF3's "The second item neither launches, nor moves the VM's tree, nor starts its queue before the first's end entry".
- Its result cell carries DC1's wait and cites "Result, computed once". DF4's "only a command that sets `AFTERSHOCK_UNSEAL=E1` reads them, and none is run before then" binds from the [REG].
- The concrete "first: …" goes into the approving decision and `docs/status.md` (DF9(g) and (h) below), not into the row.

**2. DE2 against DF7(i)/DF11: DE2 stands. DD10 is restated as draft 8's RUNBOOK section, (a) and (c).**
- DF7(i) is withdrawn: DE2's (a) already ends the §4 wait at E1's end entry, which was DF7(i)'s point.
- Dropping (b) is accepted. §3 item 6's "then deploy HEAD (§4)" is governed by DE2's §4 heading, which forbids a deploy while E1 holds the VM. And RUNBOOK:48 is the anchor that REG-20's RB6 edits.
- DF11 is restated below.

**3. DE3 against DF3: a contradiction, in one case. DF3's definition stands, and X1 rewords DE3's sentence.**
- The case: REG-20 arm A's delegate operations decision lands before E1's approval, while the owner's rulings come after it.
- DE3 reads "first" from the line of REG-20's operations heading, so REG-20 would be first. Its scripts cannot start until the owner returns, so the GPU would sit idle. DF3 makes E1 first.
- The agent's reading ("the item whose last required entry has the earlier line is first") is DF3's. X1 writes it into DE3's sentence. Today both give E1 first.

X1. Anchor:
```text
"Approved first" is read from the committed `docs/decisions.md`: the earlier line of E1's approval heading (`[DECISION] (owner|delegate) E1 approved`) and of the heading of REG-20 arm A's operations decision.
```
Replace with:
```text
"Approved first" is read from the committed `docs/decisions.md`: the item whose last required heading has the earlier line is first; an item's required headings are those its scripts need before their first launch (E1's approval heading `[DECISION] (owner|delegate) E1 approved`; for REG-20 arm A, every heading its operations scripts require, as below), so a REG-20 operations heading that still waits for the owner's rulings does not make arm A first.
```

**4. DE5 with DF5: DE5 stands verbatim, with two fixes around it.**
- **X2 (the lead-in).** In the merge, DE5's "and the owner sent E1 to review on draft 4's statement …" reads as a third item of "the owner has also decided that this run is made in any case: …", which it is not. X2 fixes the lead-in so that DE5's words follow correctly.
- **X3 (the tail).** DF5's appended last sentence repeats DE5's "rests on the owner's two choices above and on the delegation … not on that premise", and its "it" now follows DE5's "who may reverse it". X3 deletes it.

X2. Anchor:
```text
and the owner has also decided that this run is made in any case: the L1 closed-loop cache-off sweep
```
Replace with:
```text
and the owner has twice decided that this run is made in any case, and sent it to review: the L1 closed-loop cache-off sweep
```

X3. Anchor (delete it; the replacement is empty; the anchor starts with a space):
```text
 The two decisions to run E1 in any case do not rest on it, and E1's floor is withheld until E0's [REG] (above), so the delegate's approval rests on those two decisions; the owner may overrule it.
```

**5. DE7: confirmed.**
- It keeps DD6(a)'s stops and fields, so it widens nothing.
- Its parenthesis ("each such stop waits for a decision and is E1's end only once an entry says so; these reads may inform that decision and may be made before it") is my round-3 ruling on finding 4.
- DF6's two sentences after it stand. They overlap with DE7 but do not contradict it, and they add "neither end E1 nor free the VM" and the no-run case.

**6. DE4 against DF8/DF10: confirmed. It is the same act.**
- DE4's five script hashes equal DF8 step 2's.
- DF10's path list holds DE4's six files and is stricter in its exclusions, so DF10's list stands.
- README: DF8 step 2's value `9eb49712…` is checked right after `git apply`. DE6(d) then edits README, and the edited file's sha256 replaces that value in DE4's text and in the approving entry (DF8 below).

**7. DE-O2 to DE-O5 taken, DE-O1 and DE-O6 not: confirmed. None needs another pass.**
- DE-O3 and DE-O4 are wording, and DE-O5 is a citation duty.
- DE-O2 is a reporting duty:
  - its reads come after the result, except the pre-launch temperature in the attempt records, which is pre-launch GPU state and already allowed;
  - it is never judged;
  - any DE-O2 figure that `e1.report` does not print needs a named function in `analysis/` (rule I), placed outside `e1.py`'s frozen closure; otherwise "Result, computed once" requires a [CORR].
- DE-O1 not taken: consistent with my N4.
- DE-O6 not taken: the reads stay as approved, and a widening would need a pass.

## Owner-proxy line (DF2's sentence, extended)

X4. Anchor:
```text
DF9–DF11 belong to the approval commit; DD9 and DD11 stand.
```
Replace with:
```text
DF9–DF11 belong to the approval commit; DD9 and DD11 stand. Owner-proxy delta on draft 8 (`<path where this delta is saved>`): **APPROVE**; DE1–DE7 confirmed; DF7 withdrawn (DE1's row and DE2's (a) replace the RUNBOOK edits it made); DF3's definition governs "approved first" (DE3's sentence reworded, X1); DF5's lead-in adjusted and its last sentence dropped for DE5's (X2, X3); DF8, DF9 and DF11 as that delta restates them.
```

## Changes to DF8–DF11 for the approval commit
- **DF8.**
  - Step 2's README value applies to the file as `ops_draft7.patch` leaves it.
  - Add step 5a, after the sandbox: apply DE6(d) to `docs/probe/20261113_e1/ops/README.md`, then run `shasum -a 256` on it. That value is the committed README's. It takes the place of `9eb49712…` in DE4's text, and the approving entry states it.
  - The rest of DF8 stands. It and DE4 are the same act.
- **DF9.**
  - (c) also quotes the README sha256 from DF8 step 5a.
  - (d) adds: draft 8's merges as ruled here (X1–X4, DF7 withdrawn); DE-O2 to DE-O5 taken; DE-O1 and DE-O6 not.
  - (f) becomes: "states DE5's note for the owner: the 4520 premise was false; E1 run before E0's [REG] is the delegate's departure from the plan, made under DC1's guard; the owner may reverse it with one entry".
  - (g) stands, and DE3's `git grep -n` duty (REG-20's end entry before `vm_checkout.sh`, if arm A runs first) is added.
  - (h) becomes: `docs/status.md`'s next action and open risks carry DE1(iii)'s sentence verbatim, then "No command sets `AFTERSHOCK_UNSEAL=E1` before then (DF4). First: <the item (g) names>."
  - The entry's steps also quote DE4's text, with README's value as replaced.
- **DF10.** Stands. It includes DE4's six files and the DE6(d)-edited README.
- **DF11, restated (DD10).** In the approval commit, apply the [REG]'s section "RUNBOOK, for the approval commit" as draft 8 holds it:
  - (a), DE2's §4 heading, to FILE(agent/RUNBOOK.md:50);
  - (c), DE1's row, to FILE(agent/RUNBOOK.md:66);
  - FILE(agent/RUNBOOK.md:48) is not edited; it is left to REG-20's RB6.

  Both anchors are unchanged since `f43a5a1`.
