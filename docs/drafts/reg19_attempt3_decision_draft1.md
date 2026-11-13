# Draft 1 (2026-11-13): decision on the third attempt of seed 18's control, for the owner

Not approved by anyone. The owner's session wrote on 2026-11-13 that attempt 3 needs the owner's decision (agent/STATE.md, top block). This draft is what the agent would propose; the owner can approve it directly, change it, or ask for the delegate's route (rule F and owner-proxy first). **Two lines are left open until the VM is back: the queue's stop line and what the VM's journal shows about the boot's end.**

Proposed heading: `## 2026-11-13 · [DECISION] (owner) REG-19: seed 18's control is run a third and last time after two lost runs; no run is started in the morning hours either; what holds if it is lost again`

- **State:**
  - Seed 18's control has two attempts on record, both lost with the VM going off: `20261112-151030_…` (attempt 1, off at 15:51:32 UTC on 2026-11-12, PROBE(docs/probe/20261113_reg19/poweroff_20261112_20261113T005410Z.txt)) and `20261113-033842_…` (attempt 2, launched 03:38:42 UTC on 2026-11-13, FILE(docs/probe/20261113_reg19/ops_r3/state/attempt_stage2_control_l1pl350cl_r2.0_w3000_s18_2.txt:6); the VM off at about 04:40 UTC, PROBE(docs/probe/20261113_reg19/vm_down_20261113T051450Z.txt)).
  - Nothing of either run has been read. Whether the second folder holds a `checks.json` is unknown until the VM answers (expected: none).
  - The queue's stop line: *to be filled from `docs/probe/20261113_reg19/queue_owner_20261113T033838Z.txt` when the process ends.*
  - What the journal shows for the boot that ended at about 04:40 UTC: *to be filled (a probe like the one of 2026-11-12).*
  - Seeds 15 to 17: six valid runs, three `continue: True` flags, unchanged.

1. **Attempt 3 of `stage2_control_l1pl350cl_r2.0_w3000_s18` is allowed, unchanged, and it is the last** under today's decision ("at most three attempts", decisions.md 2026-11-13 [DECISION] (owner), draft 5 item 1). The record `ops_r3/state/lost_ok_20261113-033842_stage2_control_l1pl350cl_r2.0_w3000_s18.txt` is written and committed with this entry; without it `decide` refuses.
2. **Before it is launched:**
   - the VM is on; the journal of the ended boot is read and saved (no run folder, no harness log);
   - the limit reads 350.00 W, set by the owner;
   - a second session probe, `RENEW=1 zsh docs/probe/20261113_reg19/ops_r3/session_probe.sh` (a new boot id; the old file is kept);
   - the owner's finding about the host is written here, or "not looked at".
3. **No run is started in the morning hours either.** The seven recorded ends of a boot since 2026-10-31, in UTC and in local time (UTC+6):

   | end (UTC) | local | during a GPU run | how it ended |
   |---|---|---|---|
   | 2026-10-31 02:53 | 08:53 | yes | power key |
   | 2026-11-01 15:41 | 21:41 | yes | power key |
   | 2026-11-04 14:35 | 20:35 | yes | power key |
   | 2026-11-07 15:06 | 21:06 | no (last run launched 11:53) | not read |
   | 2026-11-11 17:36 | 23:36 | no (last run launched 15:06) | not read |
   | 2026-11-12 15:51 | 21:51 | yes | power key |
   | 2026-11-13 ≈ 04:40 | ≈ 10:40 | yes | not read |

   (FILE(docs/probe/20261105_vm_checks/boots_and_shutdowns.txt:32) for the first three; PROBE(docs/probe/20261113_reg19/poweroff_20261112_20261113T005410Z.txt) for the next three; PROBE(docs/probe/20261113_reg19/vm_down_20261113T051450Z.txt) for the last; "during a run" from the run folders' names.)
   - No end has fallen between 05:00 and 14:30 UTC or between 18:00 and 02:50 UTC. That this is a pattern is BELIEF from seven events.
   - Rule: no run may overlap 02:30 to 05:00 UTC or 14:15 to 18:00 UTC. A control (70 min, then its burst run of 70 min) starts only between 05:00 and 11:45 UTC or between 18:00 and 00:05 UTC; a burst run only between 05:00 and 13:00 UTC or between 18:00 and 01:15 UTC (DERIVED: 2.45 h for a pair, 1.2 h for a run).
   - This changes `quiet_now` in `ops_r3/common.sh`: a script change, with sandbox cases, logged with its commit. It only adds stops and spends no attempt.
   - **If the cause is a power cut at peak hours with a UPS that runs down under load (open question A18), no hour is safe** and this rule only lowers the odds. What would protect a run is on the host.
4. **If attempt 3 is lost as well,** the queue stops: the three attempts are spent, there is no table, and the owner decides (REG-19, "The queue stops for an operational reason"). Stated now, before any outcome exists: a run that ends without `checks.json` is never opened and carries no outcome, so allowing a further attempt after a loss cannot select on outcomes. Whether to allow one is the owner's; the delegate does not.
5. **Unchanged:** everything else of today's decision: the pin, the worktree, the checks in force before each step and the table, the order, the futility stop, the reads allowed, the records.

- **Sessions.** Seed 18's pair and seed 19 will run in a third boot at the earliest. Item 8 of today's decision already groups by boot id; the [RESULT] lists every boot.
- **Cost:** 1.2 GPU h for this control; 4.7 to 4.9 h for the rest of the queue as before.
- **Risk, said plainly:** two losses in two launches. BELIEF: without a look at the host, a third loss is likely enough that the owner may prefer to wait.
