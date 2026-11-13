# Draft 2 (2026-11-13): decision on the third attempt of seed 18's control, for the owner

Not approved by anyone. Draft 1 (`docs/drafts/reg19_attempt3_decision_draft1.md`) is kept as cited by decisions.md 2026-11-13 [OPS]. Draft 2 differs only in this way:
- it fills in the queue's stop line;
- it gives the `lost_ok` record's text ready to commit;
- it names the session-probe renewal (`RENEW=1`) as allowed by this entry, because `session_probe.sh` requires an entry but does not check for one, FILE(docs/probe/20261113_reg19/ops_r3/session_probe.sh:14);
- it notes one wording mismatch in attempt 1's record.

**One line is still open until the VM answers:** what the VM's journal shows about the end of the boot. `zsh agent/bin/vm_back_probe.zsh` reads and saves it, opening no run folder and no harness log.

The owner can approve this directly, change it, or ask for the delegate's route (rule F and owner-proxy first). The delegate does not decide it: the owner reserved attempt 3 (agent/STATE.md, top block).

Proposed heading: `## 2026-11-13 · [DECISION] (owner) REG-19: seed 18's control is run a third and last time after two lost runs; no run is started in the morning hours either; what holds if it is lost again`

- **State:**
  - **Attempt 1:** `20261112-151030_…`. The VM went off at 15:51:32 UTC on 2026-11-12 (PROBE(docs/probe/20261113_reg19/poweroff_20261112_20261113T005410Z.txt)).
  - **Attempt 2:** `20261113-033842_…`, launched at 03:38:42 UTC on 2026-11-13 (FILE(docs/probe/20261113_reg19/ops_r3/state/attempt_stage2_control_l1pl350cl_r2.0_w3000_s18_2.txt:6)). The VM went off at about 04:40 UTC (PROBE(docs/probe/20261113_reg19/vm_down_20261113T051450Z.txt)).
  - Nothing of either run has been read. Whether the second folder holds a `checks.json` is unknown until the VM answers; the expectation is that it does not.
  - **The queue's stop line** (FILE(docs/decisions.md:4306), quoting FILE(docs/probe/20261113_reg19/queue_owner_20261113T033838Z.txt:2)): `QUEUE STOP stage2_control_l1pl350cl_r2.0_w3000_s18 launch rc=7 rid=20261113-033842_stage2_control_l1pl350cl_r2.0_w3000_s18: VM NOT REACHABLE for the last 60 reads`. The queue's lock was released at 05:49:28 UTC (`state/queue.lock.ended_20261113T054928Z_61168_2`).
  - **What the journal shows for the boot that ended at about 04:40 UTC:** *to be filled from the `vm_back_<stamp>.txt` probe.*
  - Seeds 15 to 17: six valid runs, three `continue: True` flags, unchanged.

1. **Attempt 3 of `stage2_control_l1pl350cl_r2.0_w3000_s18` is allowed, unchanged, and it is the last.** This follows today's rule of at most three attempts (decisions.md 2026-11-13 [DECISION] (owner), the plan of resume draft 5, item 1).
   - The record `docs/probe/20261113_reg19/ops_r3/state/lost_ok_20261113-033842_stage2_control_l1pl350cl_r2.0_w3000_s18.txt` is written and committed with this entry. Without it, `decide` refuses.
   - Its text, ready to commit:
     ```
     The rerun of stage2_control_l1pl350cl_r2.0_w3000_s18 after this lost run (no checks.json; the VM went off at about
     04:40 UTC on 2026-11-13) is allowed by decisions.md 2026-11-13 [DECISION] (owner), "REG-19: seed 18's control is run
     a third and last time": it is attempt 3, the last. This record is void unless that owner decision is in decisions.md.
     ```
   - **A wording mismatch, disclosed, which changes nothing.** Attempt 1's record (`state/lost_ok_20261112-151030_…s18.txt`) names "decisions.md 2026-11-13 [DECISION] (delegate), REG-19 resume, item 1" and calls itself void without that entry. The resume was in fact approved by the owner directly ([DECISION] (owner), FILE(docs/decisions.md:4284)), for the same plan (draft 5, item 1).
     - `decide` checks only that the record exists. The queue therefore ran attempt 2 on it.
     - This entry states that the owner's decision is the one that record meant. The record itself is not edited (records are kept as written).
2. **Before attempt 3 is launched:**
   - The VM is on, and the journal of the ended boot is read and saved (`agent/bin/vm_back_probe.zsh`; no run folder, no harness log).
   - The limit reads 350.00 W, set by the owner (`sudo nvidia-smi -pl 350`, or the sudoers rule in FOR_AUTHOR −2).
   - **The session probe is renewed:** `RENEW=1 zsh docs/probe/20261113_reg19/ops_r3/session_probe.sh` records a new boot id and keeps the old file. This entry is the decisions.md entry that `session_probe.sh` asks for (FILE(docs/probe/20261113_reg19/ops_r3/session_probe.sh:7)). The probe's files are committed before the queue starts.
   - The owner's finding about the host is written here, or "not looked at".
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

   Sources: FILE(docs/probe/20261105_vm_checks/boots_and_shutdowns.txt:32) for the first three; PROBE(docs/probe/20261113_reg19/poweroff_20261112_20261113T005410Z.txt) for the next three; PROBE(docs/probe/20261113_reg19/vm_down_20261113T051450Z.txt) for the last. "During a run" comes from the run folders' names.
   - No end has fallen between 05:00 and 14:30 UTC or between 18:00 and 02:50 UTC. That this is a pattern is a BELIEF resting on seven events.
   - **Rule:** no run may overlap 02:30 to 05:00 UTC or 14:15 to 18:00 UTC.
     - A control (70 min, then its burst run of 70 min) starts only between 05:00 and 11:45 UTC, or between 18:00 and 00:05 UTC.
     - A burst run starts only between 05:00 and 13:00 UTC, or between 18:00 and 01:15 UTC.
     - DERIVED: 2.45 h for a pair, 1.2 h for a run.
   - **This changes `quiet_now` in `ops_r3/common.sh`.**
     - It is a script change with sandbox cases, logged with its commit.
     - It only adds stops and spends no attempt.
     - The agent has the change ready as a patch with its sandbox cases, not applied: `docs/drafts/reg19_ops_r3_patch/`. It is applied only with this entry.
   - **If the cause is a power cut at peak hours with a UPS that runs down under load (open question A18), no hour is safe.** This rule then only lowers the odds. What would protect a run is on the host.
4. **If attempt 3 is lost as well,** the queue stops:
   - The three attempts are spent, there is no table, and the owner decides (REG-19, "The queue stops for an operational reason").
   - Stated now, before any outcome exists: a run that ends without `checks.json` is never opened and carries no outcome. Allowing a further attempt after a loss therefore cannot select on outcomes.
   - Whether to allow one is the owner's decision; the delegate does not make it.
5. **`final.sh` waits for REG-21 and REG-22.** When the queue has ended, REG-19's table (`final.sh`) is not run until REG-21's and REG-22's entries are committed, or until their review has ended with batch 2 labelled retrospective by design (plan of 2026-11-13, Step 1; FOR_AUTHOR −10). This delays REG-19's [RESULT] by at most the time those reviews take. It changes no rule of REG-19.
6. **Unchanged:** everything else of today's decision:
   - the pin and the worktree;
   - the checks in force before each step and the table;
   - the order and the futility stop;
   - the reads allowed;
   - the records.

- **Sessions.** Seed 18's pair and seed 19 will run in a third boot at the earliest. Item 8 of today's decision already groups by boot id; the [RESULT] lists every boot.
- **Cost:** 1.2 GPU h for this control; 4.7 to 4.9 h for the rest of the queue, as before.
- **Risk, said plainly:** two losses in two launches. BELIEF: without a look at the host, a third loss is likely enough that the owner may prefer to wait.
