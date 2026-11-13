# Quiet-hours patch for REG-19's ops_r3 scripts: prepared, NOT applied

Prepared by the agent on 2026-11-13 for the owner's attempt-3 decision (`docs/drafts/reg19_attempt3_decision_draft2.md`, item 3). It is applied only with that decision: editing `ops_r3` changes REG-19's operations, which is the owner's call.

**What it changes**
- `common.sh`: a second quiet window (`QUIET2_*`) is added. With it, no run overlaps 02:30–05:00 UTC, in addition to the existing 14:15–18:00 UTC:
  - a control is not started from 00:00 to 05:00 UTC;
  - a burst run is not started from 01:15 to 05:00 UTC.
  - The comment about the power-off pattern is brought up to date (seven ends of a boot).
- `launch.sh`: the stop message names both windows.
- `test_sandbox.sh`:
  - The default fake clock moves from 03:00 to 06:00, because 03:00 is now quiet.
  - Seven cases are added: 03:00, 00:00 and 04:59 for a control, which spend no attempt; 01:15 for a burst run; 05:00 and 23:59 allowed.

**A correction to draft 1.** Draft 1 allowed a control until 00:05. That is wrong by the draft's own numbers: DERIVED, 00:05 + 2.45 h = 02:32, which overlaps 02:30. The patch, and draft 2, use 00:00.

**Checked:** the sandbox was run against a scratch copy of `ops_r3` with this patch applied.
- Patched copy: `passed 167, failed 0` (`sandbox_run_patched.txt`).
- The committed scripts, unpatched: `passed 160, failed 0`, the same day.

**To apply (with the owner's entry):**
1. `git apply docs/drafts/reg19_ops_r3_patch/*.patch`.
2. Run `zsh docs/probe/20261113_reg19/ops_r3/test_sandbox.sh`, which should give 167 of 167.
3. Commit the scripts.
4. Write that commit's hash into `ops_r3/scripts_commit.txt` and commit it. `mac_checks` compares the two.

**Not changed:** `RECORDS` still lists attempt 1's records only.
- Adding attempt 2's record and the new `lost_ok` would make `mac_checks` guard them as well.
- It would also change the sandbox's scenario, which would need new cases. It is left out on purpose and can be added with its cases if the owner wants it.
