# proxy-reg20-ops-draft2 (owner-proxy on REG-20 arm A's operations decision, draft 2, bundle reg20_ops_r2), verbatim

Saved by the agent at 2026-11-14 01:43 UTC from the reviewer's own verdict file (an in-process subagent of session 8c5f8396; scratchpad `reviews_r3/proxy-reg20-ops-draft2.md`, 34274 bytes, sha256 80ab2a77ae731780a8168e522ecf44260d73eb789265bb8bef7718c8781af5c2, checked on copy; the reviewer's hand-back message named the same sha256). The reviewer's report follows the line '---' unchanged.

---
# Owner-proxy round 2 on the REG-20 arm A operations decision, draft 2 (a delta on round 1, items RB)

**Verdict: APPROVE, with conditions RD1–RD8 BEFORE the first launch and RD9–RD10 LATER.** Every owner point can be picked now, inside the delegation, so arm A can launch once the BEFORE conditions are met and rule F round 2 does not reject. This APPROVE covers the three proposed headings: the ops [DECISION], the rulings, and the start. The ops [DECISION] is the draft as amended by RD1–RD8. The rulings are exactly as RD2 gives them; any other value needs another owner-proxy pass. The start depends on question G (a).

Reviewer: a separate owner-proxy subagent, 2026-11-14. 0 GPU h. The VM was not contacted and no repository file was edited or committed. My only files are this one and a scratch clone (named under "Probe").

---

## What I read, in order

1. `CLAUDE.md` and the auto-memory, both from the session context.
2. `docs/decisions.md:4215-4274`. The delegation is at 4231–4237.
3. The bundle `docs/drafts/review_bundles/reg20_ops_r2/`:
   - `BUNDLE_NOTE.md`;
   - `MANIFEST.txt`. `shasum -a 256 -c MANIFEST.txt` gave **21 of 21 OK**, exit 0;
   - `reg20_ops_decision_draft2.md` and `reg20_ops_draft2_itemmap.md`, whole;
   - `reviews/proxy-reg20-ops-draft1.md` and `reviews/rulef-reg20-ops-draft1-r1.md`, whole.
4. **Bundle against the repo.** I ran `cmp` on each of the 13 bundled ops files against `docs/probe/20261113_reg20/ops/` at HEAD 56820bd: all 13 are equal. The draft and the item map are also equal to their `docs/drafts/` copies. So the bundle is what 56820bd committed.
5. `docs/decisions.md`:
   - 4040–4174: REG-20's [REG] at 4045 and the owner's approval at 4166;
   - 4195–4212: A14;
   - 4284–4408: REG-19's resume (owner) and attempt 3 (owner);
   - the heading list from 4228 to the end;
   - line 9834: the REG-21/REG-22 freeze.
6. The gate:
   - `docs/probe/reg20/gate_20261113T230307Z.txt`, one line: `{'k_closed': 5, 'n': 5, 'best_p': 0.03125, 'may_start': True}`;
   - `gate_err_20261113T230307Z.txt`, 0 bytes;
   - `git show --stat 3c8e5dc`.
7. The ops scripts, whole: `common.sh`, `queue.sh`, `launch.sh`, `final.sh`, `recheck_one.py`, `owner_rulings.txt` and `README.md`. Also `session_probe.sh:1-51`, `test_sandbox.sh:1-60`, and greps of the sandbox output `sandbox_20261113T231823Z.txt` (lines 95–200 and its tail) and of `test_control_due_20261113T231828Z.txt` (its tail).
8. `analysis/withheld.py`, whole. `analysis/k1.py:40-55`, `:140-170`, `:186-200` and `:260-300`.
9. The `import` lines of the modules on k1's path, and of `analysis/recheck.py` and `harness/checks.py`. Also the output of `python3 -I docs/probe/20261113_freeze/closure.py` for `analysis/k1.py` and for `analysis/recheck.py`.
10. `docs/drafts/reg19_resume_decision_draft5.md:31-70`.
11. `PROTOCOL.md:70-95` (§5).
12. `agent/RUNBOOK.md:44-66`.
13. `docs/status.md:1-15`, plus a grep for "freeze".
14. E1:
    - `docs/drafts/e1_draft7.md:50-75`, plus a grep for its RUNBOOK row at 855–870;
    - only the file lists (`+++` lines) of E1's three patches.
15. REG-24:
    - the file list of `docs/drafts/reg24_r1/reg24.patch`;
    - `docs/drafts/reg24_confirm_draft1.md:410-432`.
16. `tools/check_docs.py`, by grep only.

**Not opened:**
- `/Users/chalshik/aftershock-backups/`;
- `docs/probe/20261111_reg19/ops/RESUME.md`;
- `docs/paper/`;
- any `state/` folder (`docs/probe/20261113_reg20/ops/` has none);
- any folder matching REG-20's seal, or E1's and E0's sweeps.

I did not run `k1.reg20_table`, `e1.observed`, `k2.observed`, any `k3.reg21_*`, `reg20_a_may_start` or the sandbox. Rule F round 2 runs the sandbox, so I did not repeat it.

**Disclosure (A5).** Before making the picks below I saw REG-19's outcome three ways:
- the gate file's value (k_closed 5 of 5);
- the heading at FILE(docs/decisions.md:16517) ("`supports`, 5 of 5");
- status.md's headline.

No REG-20 open run is named on the Mac. DERIVED: `ls runs | grep -cE '_l1pl350ol_|_s15_drift$'` gives 0 (my run, 2026-11-14). The picks rest on PROTOCOL, the registration and the owner's recorded choices, not on that outcome. They are symmetric between `supports` and `refutes`, except 7, which leans against K1.

---

## Checks I ran (all read-only)

**HEAD meets the scripts' preconditions** (DERIVED, my commands at HEAD 56820bd):
- 1cface7 is an ancestor of HEAD.
- `tools/manifest.py`, `pyproject.toml` and `uv.lock` equal the pin's.
- The seven JUDGED files equal the pin's, in the working tree and at HEAD.
- `analysis/load.py` hashes to blob `59ef93b9…` and `analysis/withheld.py` to `46b42a76…`, equal to SEAL_BLOBS.
- `harness/checks.py` equals 5ee6e38's, and `analysis/recheck.py` equals 72fafb5's.
- `git diff HEAD -- analysis harness configs` is empty. So `mac_checks` and `recheck_guards` would pass on today's tree, apart from the missing `scripts_commit.txt` and the `unset` rulings.

**k1's import closure** (PROBE: my run of `closure.py analysis/k1.py`): 19 .py files.
- `analysis/{__init__,derived,floor,gate,k1,load,margin,stats,tables,withheld}.py` and `harness/{__init__,checks,config,env_snapshot,loadgen,recorder,run,trigger,workload}.py`.
- The module-level part is exactly JUDGED plus the two seal files (from the import lines).
- `closure.py analysis/recheck.py` gives `analysis/{__init__,load,recheck,withheld}.py` and `harness/{__init__,checks,config,workload}.py`.
- `git diff --stat 5ee6e38 HEAD -- harness/` is empty: today's whole `harness/` is A14's.

**The gate's committed state** (DERIVED):
- At `3c8e5dc^` = 6748c26 (REG-19's [RESULT]), the JUDGED files equal the pin's, the two seal blobs are SEAL_BLOBS, and the lock equals the pin's.
- 6748c26 is an ancestor of 3c8e5dc (committed 22 s earlier).
- `reg20_a_may_start` reads only `closed_pattern(sd)` = `*_burst_l1pl350cl_r2.0_w3000_s{sd}` (FILE(analysis/k1.py:43-44), FILE(analysis/k1.py:269-276)). That pattern never matches `…_s15_drift`.
- With `AFTERSHOCK_UNSEAL=REG-20` only, REG-19's runs could have been read only through the [RESULT] REG-19 heading in the working-tree log. n = 5 with 0 bytes of stderr (no `withheld:` line) is consistent with that.

**The REG-24 seal.** REG-24 draft 1 needs a new row in `analysis/withheld.py` "before either run exists" (FILE(docs/drafts/reg24_confirm_draft1.md:418-422)). That row would change the blob that `mac_checks` pins and stop arm A's queue. E1's seal row already exists (FILE(analysis/withheld.py:30)). E1's patches touch only `analysis/e1.py`, `tests/test_e1.py` and E1's ops folder. REG-24's patch adds `analysis/confirm.py`, two configs and a test. None of these is in k1's closure.

**Probe of the holding-folder recheck on real data.** PROBE: my run, with the clone at `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/holdtest/`.
- I cloned `runs/20261112-061951_burst_l1pl350cl_r2.0_w3000_s15` (REG-19's seed 15 burst run, reported and unsealed) with `cp -cR`. Its sha-of-sums is `6d377d813c658546` in both places.
- `recheck_one.py` on the clone printed `stored_valid true, now_valid true, failed [] [], changed false`, rc 0.
- On the folder in `runs/` it refused with "the folder is inside runs/", rc 3.
- `analysis.recheck` on the same pattern gave `n_runs 1, n_changed 0`.
- `git status` was unchanged.
- So the new per-folder script reads a real 4080 s folder outside `runs/` and agrees with `analysis.recheck`. Only validity fields were printed.

**Sandbox coverage of my picks** (FILE(docs/probe/20261113_reg20/ops/sandbox_20261113T231823Z.txt), by grep):
- 2a setaside: the rerun as attempt 2; no control on a set-aside run; final.sh accepts the folder set; a double set-aside stops and is settled by the owner's not_run (lines 99–109).
- 7 lost_open: a delegate's lost_open is taken (lines 170–171).
- 6(b): the delegate's rerun, refused after a reboot; a second client error is made lost_open by a second delegate record (lines 176–188; FILE(docs/probe/20261113_reg20/ops/test_sandbox.sh:532-536)).
- 8(b): count no; a third loss stops (lines 213–221).
- 9(a): a delegate's third attempt (line 130).
- Saved totals: 350 of 350 passed, and 46 of 46.

---

## The owner points: picks

The owner is away. The approvals the delegation covers include "registrations and GPU runs; reruns under registered stopping rules" (FILE(docs/decisions.md:4233)). Each pick below either applies the registration or PROTOCOL as written, or fixes a rerun rule before any REG-20 run exists. None:
- chooses a threshold after its data;
- changes k1, a label rule or a `checks.json`;
- reads withheld data.

So none needs the real owner. The real owner may overrule any of them (FILE(docs/decisions.md:4236)).

### 2a: `setaside`

This departs from round 1's `keep` (RB2). The reason is new evidence, as rule A4 requires: draft 2 makes a rerun possible.

**Why the owner would pick it:**
- PROTOCOL §5 as in force says a run is valid only if every check passes, including A14's coverage checks "from 2026-11-12 (A14, owner)". It also says "Invalid runs are kept, never counted, and rerun unchanged" (FILE(PROTOCOL.md:74-84)).
- `setaside` does exactly that:
  - **kept:** the run stays in the holding folder, and its VM copy too (RD8);
  - **never counted:** it never enters `runs/`, so k1 never sees it;
  - **rerun unchanged:** the registered one rerun.
- `keep` would count a run that PROTOCOL calls invalid. That is a deviation from PROTOCOL, which is the owner's to make.
- The owner's own REG-19 resume refused to count such a run automatically: "PROTOCOL §5 says invalid runs are never counted, while marking one invalid beyond its automatic checks is the owner's", so a flagged run was an operational stop (FILE(docs/drafts/reg19_resume_decision_draft5.md:65-66), approved at FILE(docs/decisions.md:4284)). That stop is the `stop` option, which idles the GPU while the owner is away. "We cant afford just letting be idle" rules it out.
- `pin_head` would give the open arm a different harness from the closed arm. That contradicts "the only change" (FILE(docs/decisions.md:4052)) and the owner's own pin choice for REG-19 (FILE(docs/decisions.md:4284)). It would also delay the start by a reviewed re-pin.

**What it does to K1:** it keeps a valid reading possible for each seed. Under `keep`, a recorder death at the pin reads `unclear` (FILE(analysis/k1.py:162-163)), so the seed drops out and `supports` becomes unreachable (RA2's trace).

**Cost:**
- On record, no valid run changed verdict over 182 folders (FILE(docs/decisions.md:4205)).
- DERIVED: `stats.cp_upper(0, 182)` = 0.0163 per run. That is a lower value for the bound, since fewer than 182 of those folders were valid. Over 11 runs it gives P(at least one set-aside) ≤ about 0.17 and an expected ≤ 0.2 GPU h extra.
- Open-loop backlogs may raise the rate (BELIEF; FILE(docs/decisions.md:4202)).

**Only `recorder` or `gpu_steady` can newly fail a stored-valid run.**
- A14 changed only those two checks (FILE(docs/decisions.md:4204)).
- So a set-aside never bypasses a stop-and-ask failure, and a set-aside `gpu_steady` counts as a heat failure (FILE(docs/probe/20261113_reg20/ops/common.sh:252-253)).

**Residual case: a burst config whose two attempts end as set-aside plus set-aside, or set-aside plus invalid.**
- The queue stops for the owner, because the scripts accept only an owner's settle record there (FILE(docs/probe/20261113_reg20/ops/common.sh:314), :347).
- k1 cannot read `lost_open` from a stored-valid folder. My recommendation, fixed now (RD3 (vi)): `not_run`, with the [RESULT] adding a line that counts that seed `lost_open`.
- Rare: at most about 0.0163² per config if the two are independent.

### 6: (b)

- The registration's "stop and ask" (FILE(docs/decisions.md:4057)) is answered by a rule fixed now. That is a delegate approval of a rerun under the registered rule.
- Fixing it now is A5-safer than ruling per case after the control bits are visible (RA5).
- A second client error becomes `lost_open`, which counts against K1: the skeptic's direction (T3, FILE(docs/decisions.md:4103)).
- (a) would idle the GPU at each client error while the owner is away. Round 1 also recommended (b).
- RB10's residual-risk sentence stays.
- **Scope, stated as the scripts do it:** 6(b) applies to every open-loop config of arm A, the burst runs and their controls (FILE(docs/probe/20261113_reg20/ops/common.sh:195-197), FILE(docs/probe/20261113_reg20/ops/launch.sh:29,75-77)). The draft's "an open burst run" is narrower; RD6 fixes the wording.

### 7: `lost_open`

This departs from draft 2's recommendation, `not_run`.

**Why:**
- **It is the registered label.** `lost_open` is "burst run invalid after its rerun" for any check (FILE(docs/decisions.md:4067), FILE(analysis/k1.py:158)), approved by the owner (FILE(docs/decisions.md:4166-4167)).
- `not_run` would produce a label the registration does not assign, by holding a run out of `runs/` so that k1 reads `not_run`. That changes what the owner approved, so the real owner would have to make it.
- RA3's real danger is a **systematic** setup fault giving three `lost_open` and a false `refutes`. A stop meets that better than a label change. RD3 (ii) adds that stop, which is inside the delegation because it only adds a stop.
- **Mixed case** (one attempt failed `client_lag`, the other `trigger`). `not_run` would drop a seed whose first failure is the T3 kind, the kind most likely to come from a stuck state, so the label `lost_open` should apply.
- **Both attempts setup-only, one config only.** With the systematic-fault stop in place, only an isolated case remains. Either label kills `supports`. `lost_open` adds 1 toward `refutes`, which needs 3 (FILE(analysis/k1.py:33)).
- `per_stop` would mean ruling with the bits visible (A5), and the GPU idles meanwhile.

### 8: (b)

- **The owner's words:** "power off happens randomly".
- **The owner's REG-19 reasoning:** "a run that ends without `checks.json` is never opened and carries no outcome, so allowing a further attempt after a loss cannot select on outcomes" (FILE(docs/decisions.md:4398)). The owner also allowed a third attempt after two losses (FILE(docs/decisions.md:4393)).
- The delegation itself names a lost-run relaunch among its approvals (FILE(docs/decisions.md:4233)).
- **Under A18's reading (2)** (losses come sooner under load), (a) would drop stuck seeds sooner. Under (b) each lost run's arm, elapsed time and end are recorded (FILE(docs/probe/20261113_reg20/ops/common.sh:461-468)), so the [RESULT] can show whether losses cluster in open runs.
- A loss without a reboot stays the owner's, as the scripts do.
- After any power-off the owner is needed anyway, to power the VM on and set 350 W (FILE(docs/decisions.md:4377)).

### 9: (a)

- The registered row for an open cold run without its control is "run the control, then compute again" (FILE(docs/decisions.md:4073)). (b) settles into `pending_controls`, which the same row says to cure by running the control.
- The seed already counts as cold (`pending_control`, FILE(analysis/k1.py:176)), so a third attempt decides only `stuck_open` against `overload_open`.
- At most three attempts is the owner's own REG-19 limit (FILE(docs/drafts/reg19_resume_decision_draft5.md:32)).
- A third failure stops arm A for the owner.

### 16: (a)

- REG-20's seal row already covers arm B: `*_l1pl350ol_r2.[05]_w3000_s1[5-9]`, lifted by "[RESULT] REG-20" (FILE(analysis/withheld.py:28)).
- So (a) keeps arm B blind from its first folder with no code change, and arm A's outcome is still reported, under a heading that lifts nothing. The lift needs `## <date> · [RESULT] REG-20` with no digit after it (FILE(analysis/withheld.py:46)), and "[RESULT] K1 arm A, …" does not match.
- (b) needs a seal row committed before arm A's [RESULT]. Its "after both batch 2s" is now met (FILE(docs/decisions.md:16571), FILE(docs/decisions.md:16798)), but it adds a commit to a file that `mac_checks` pins.
- (c) would let any glob tool read arm B's runs before its result.
- The cost of (a): arm A's folders stay sealed until arm B ends. That only happens after `supports` or `supports_no_mechanism`.

### G: (a), accept the gate as computed at 3c8e5dc

- The registered command is `python -m analysis.k1 reg20_a_may_start`, "computed once after REG-19's [RESULT]" (FILE(docs/decisions.md:4051), FILE(docs/decisions.md:4168)). RUNBOOK:63's form is that command with `uv run` and a seal variable (FILE(agent/RUNBOOK.md:63)).
- RB5 (ii)'s stricter form was never registered, so the registered command was used.
- **The four differences from RB5 (ii) change no input:**
  - The variable unsealed nothing. No REG-20 folder exists on the Mac (DERIVED, 0), and k1's closed pattern cannot match the drift name.
  - `uv run` against `.venv/bin/python`: the lock equals the pin's at `3c8e5dc^` (DERIVED). Whether `uv run` resynced the .venv is not recorded (BELIEF: a no-op with an unchanged lock).
  - The Mac-side checks did not run. But the committed judged code and the seal blobs at `3c8e5dc^` equal what `mac_checks` requires (DERIVED). Only the working tree at that moment is unrecorded (BELIEF).
  - The folder is `docs/probe/reg20/`: cosmetic.
- (b) would leave arm A without a lawful start: "computed once" forbids a second computation without a new decision.
- The command is known only from the commit subject, which is not evidence (rule B). RD7 makes the start entry say so.

---

## Judged items

**1. The holding-folder recheck: accepted.**
- **Order.** Copy to `/Users/chalshik/Projects/aftershock-reg20-holding`, compare sha256s with the VM's, recheck, apply 2a, then move into `runs/`, compare again, update the manifest and write the copy record (FILE(docs/probe/20261113_reg20/ops/common.sh:543-573)). This meets RA2 (b) and RB2 (ii) at once.
- **Restarts.** I traced each point a restart can resume from. Each one is idempotent: after the rsync, after the recheck record, after the `mv` and before the copy record (:549-551, :557).
- **No control decision without a recheck record** (FILE(docs/probe/20261113_reg20/ops/queue.sh:44)).
- **final.sh** re-runs `analysis.recheck` and requires the same changed set (FILE(docs/probe/20261113_reg20/ops/final.sh:52-70)).
- The probe above shows it works on real data.
- **Gaps:**
  - (i) The recheck's closure includes `harness/config.py` and `harness/workload.py`. `recheck_guards` holds them only to HEAD (:495), so a **commit** to them would change the recheck unseen. RD4 bars that; RD-O1 makes it mechanical.
  - (ii) Any uncommitted change under `analysis/` or `harness/` in the main checkout stops the queue at the next copy (sandbox: "any change in analysis/ (here outside k1's closure) stops the recheck"). That fails safe but idles the GPU: the 2026-11-13 incident class (FILE(docs/decisions.md:4604)). RD4 bars it.
  - (iii) The holding folder is outside git, the manifest and `runs/`. RD8 keeps the VM copies and records the folder.

**2. A rule against commits to `analysis/` during arm A: needed (RD4).**
- The REG-21/REG-22 freeze, which draft 2 relies on, has ended. Both batch 2s are computed (FILE(docs/decisions.md:16571), FILE(docs/decisions.md:16798)).
- A commit to JUDGED or to a seal file stops the queue until `common.sh` changes by a reviewed commit (FILE(docs/probe/20261113_reg20/ops/common.sh:80-83)). It can land between a burst run and its control, so "right after" is lost (RA-O1).
- One such commit is already foreseeable: REG-24's seal row.
- A commit to the recheck's harness closure passes silently (item 1 (i)). An uncommitted edit anywhere in `analysis/` or `harness/` stops the queue (item 1 (ii)).
- Commits to other files are harmless: `analysis/e1.py`, `analysis/confirm.py` and `tests/` are not in k1's or the recheck's closure (DERIVED above).

**3. The ordering with E1: acceptable, but missing from REG-20's side (RD5).**
- E1 draft 7 states the rule and says "the same rule belongs in REG-20's ops decision, which is in review" (FILE(docs/drafts/e1_draft7.md:866)). Draft 2 has no word on E1 (my grep).
- **What the machines enforce (DERIVED from the scripts):** REG-20's `launch.sh` refuses a launch while a compute process runs, while any tmux session exists, or when the VM's tree is not 1cface7 (FILE(docs/probe/20261113_reg20/ops/launch.sh:49-50,56)). E1's pre-launch checks refuse the same way at E1's commit (FILE(docs/drafts/e1_draft7.md:61,71)). So two runs can never overlap, and a launch on the wrong tree fails safe.
- **What only the hand rule protects:** which queue goes first, and that the second does not start while the first is paused. For REG-20 that matters most between a cold burst run and its control. The [RESULT] would show it as a `gap_s`, but "right after" (FILE(docs/decisions.md:4054)) would be lost.
- **The price.** Under E1's words, a pause that waits for the owner is not an end, so the other queue waits and the GPU idles (BELIEF: rare under these picks; after a power-off the owner is needed anyway). A lending rule would need both texts changed, so it is only an optional proposal (RD-O3).

**4. The stale freeze text: must be corrected (RD6).**
- Four texts say the REG-21/REG-22 freeze still protects the seal files: draft point 12 (line 239), point 16 (line 304), the section "The freeze" (lines 366–378) and README:130.
- That freeze ended with the batch 2 results above, so the mitigation those texts name no longer exists.
- Three status lines are also false since 56820bd: draft line 7, item map line 9, README:8 ("not committed").
- Draft line 29 says the scripts check "all three" proposed headings. They check REG-19's [RESULT], the rulings and the start, not heading 1 (FILE(docs/probe/20261113_reg20/ops/common.sh:126-150)).

**5. The rulings heading needs a delegate form (RD1).**
- The scripts accept only `[DECISION] (owner) REG-20 arm A operations: the owner's rulings` (FILE(docs/probe/20261113_reg20/ops/common.sh:40)).
- With the owner away, the agent cannot write that heading truthfully. As drafted, arm A cannot start without the real owner, against the owner's stated wish.

---

## Conditions

### RD1 BEFORE: the rulings heading accepts the delegate

The only script change. Its diff must get a rule F look, a delta pass on the diff alone, before the rulings entry. A NOT READY on it is binding.

- In `common.sh`, replace line 40 with:
  ```
  RULINGS_PAT='^## [0-9]{4}-[0-9]{2}-[0-9]{2} · \[DECISION\] (\(owner\) REG-20 arm A operations: the owner.s rulings|\(delegate\) REG-20 arm A operations: the rulings on the owner.s points)([^0-9A-Za-z]|$)'
  ```
- In line 134's message, replace `no '[DECISION] (owner) REG-20 arm A operations: the owner's rulings' heading` with `no rulings heading ('[DECISION] (owner) REG-20 arm A operations: the owner's rulings' or '[DECISION] (delegate) REG-20 arm A operations: the rulings on the owner's points')`.
- In `owner_rulings.txt`'s comment (lines 4–5), and in README launch step 2, name both headings the same way.
- Add two sandbox cases:
  - with `## 2026-11-20 · [DECISION] (delegate) REG-20 arm A operations: the rulings on the owner's points (sandbox)` in place of `H_RUL`, the queue starts;
  - with `## 2026-11-20 · [DECISION] (delegate) REG-20 arm A operations: the owner's rulings (sandbox)`, it refuses.
- Re-run both test files, save their outputs beside the old ones, and commit. Write `scripts_commit.txt` as README step 1 says.
- The [DECISION] quotes `git diff --stat 56820bd <implementing commit> -- docs/probe/20261113_reg20/ops` and the two counts. That diff holds only:
  - RD1's lines;
  - RD2's six values;
  - the README's RD1, RD5 and RD6 lines;
  - the new sandbox cases and saved outputs;
  - `scripts_commit.txt`;
  - optionally RD-O1's line.

  Anything else needs a new round.

### RD2 BEFORE: the rulings, exactly

- `owner_rulings.txt`'s six lines become:
  ```
  2a setaside
  6 b
  7 lost_open
  8 b
  9 a
  16 a
  ```
- The entry, headed `## <date> · [DECISION] (delegate) REG-20 arm A operations: the rulings on the owner's points`, quotes:
  - the file;
  - question G's answer, (a);
  - this pass;
  - rule F round 2, verbatim (the delegation's (a) and (b)).
- It is committed with the file. The order in decisions.md is: the ops [DECISION] (delegate), then this entry, then the start.
- `owner_rulings.txt` is not changed again before REG-20 arm A's end entry, except by an `(owner)` [DECISION].

### RD3 BEFORE: the delegate's answers at stops, fixed now

Into the rulings entry, verbatim:

> At each stop below the delegate writes the record named here, as soon as the queue stops for it, and no other. It reads nothing beyond the stop line and the reads that common.sh's ALLOWED lists, and makes no choice. Each record carries `under <this entry's heading> (ruling <n>)` and `by delegate`, and is logged in the next [OPS] entry.
> (i) Ruling 7 (RA3's case): `state/settle_<run id of the second attempt>.txt` with `label lost_open`, unless (ii) applies.
> (ii) Systematic-fault stop: when a run of any of arm A's eleven configs is invalid with `clean_git`, `kv_capacity` or `trigger` in its `failed`, and a run of another of the eleven configs already had one of these, the delegate does not start the queue again and writes no settle record. Arm A waits for the owner, and an [OPS] entry quotes both `RUN … INVALID failed=…` lines.
> (iii) Ruling 6(b), for every open-loop config of arm A: after a client error, `state/rerun_ok_<run id>.txt` with `lifts no_errors/client_error`, when the scripts would accept it (launch log nofile ≥ 4096, same boot). After a second client error in the same config, the same record, which makes the seed `lost_open`. A client error with `manipulation` or `power_limit` in the same `failed` waits for the owner.
> (iv) Ruling 8(b): after a power-off, once the VM is back, 350.00 W is read and the session probe is renewed with its [OPS] entry: `state/lost_ok_<run id>.txt` with `count no`, for a run launched in an earlier boot, at most two per config. The lost folder is not opened or copied. A loss without a reboot, or a third, waits for the owner.
> (v) Ruling 9(a): when both attempts of a control are invalid, `state/attempt_ok_<config>_3.txt`. If the third is invalid or lost, arm A waits for the owner.
> (vi) Ruling 2a `setaside`: no record. If a burst config's attempts end as two set-asides, or a set-aside and an invalid run, arm A waits for the owner. The recommendation fixed now is a settle record with `label not_run`, naming the invalid run if there is one, and a [RESULT] line with that seed counted `lost_open`.

### RD4 BEFORE: the arm A freeze

Replaces the stale freeze text. Into the ops [DECISION], verbatim:

> From the commit of the start heading until final.sh's two output files are committed, or an entry ends arm A:
> - no commit, and no uncommitted change in the Mac's main checkout, touches:
>   - the 19 .py files that `python3 -I docs/probe/20261113_freeze/closure.py analysis/k1.py` prints at that commit, quoted in this entry;
>   - `analysis/recheck.py`;
>   - any file under `harness/`;
>   - `configs/defaults.yaml`;
>   - `pyproject.toml`, `uv.lock`, `.python-version`, `tools/manifest.py`;
>   - `owner_rulings.txt`;
>   - the eight scripts of `docs/probe/20261113_reg20/ops/` (a script change only by a reviewed commit with its `scripts_commit.txt`);
> - in particular no row is added to `analysis/withheld.py`'s SEALS: REG-24's row waits until final.sh's files are committed, and lands before REG-24's first run;
> - the Mac's `.venv` is not changed (no `uv add`, `uv remove`, `uv sync`, `uv pip`);
> - no file under `analysis/` or `harness/` of the main checkout is left changed and uncommitted while the queue's lock is held. Work for other items (E1's `analysis/e1.py`, REG-24's `analysis/confirm.py`, any subagent's work) is written and tested in a separate git worktree or a scratch copy. It reaches main only by one command that applies and commits it (`git apply … && git commit …`, or a fast-forward).
>
> A commit to any other file under `analysis/` or `tests/` is allowed: none is in k1's or the recheck's import closure (closure.py output quoted).

### RD5 BEFORE: the mirror of E1's ordering rule

Into the ops [DECISION], verbatim:

> E1 and REG-20 arm A: whichever has its ops approved first runs first; the other launches only after the first's end entry.
> - **Approved first** is the earlier line in docs/decisions.md of `## <date> · [DECISION] (owner|delegate) E1 approved` and of this decision's start heading `## <date> · [DECISION] (owner|delegate) REG-20 arm A starts: k1.reg20_a_may_start passed`.
> - **REG-20 arm A's end entry** is headed either:
>   - `## <date> · [OPS] REG-20 arm A: the queue ended (QUEUE DONE)`, quoting the queue's `QUEUE DONE` line; or
>   - `## <date> · [OPS] REG-20 arm A ended by a stop: <the stop line>`, for a stop that an entry has decided ends arm A.
> - A pause, or a stop that waits for a decision, is not an end.
> - Until arm A's end entry, no other registration's run is launched, and the VM's tree is moved only by README step 4.
> - If E1 runs first, README step 4 (the checkout of 1cface7) is made only after E1's end entry, and its output goes into an [OPS] entry.
> - The scripts do not read E1's entries, so this rule is kept by hand. launch.sh refuses a launch while a compute process or a tmux session exists, or when the VM's tree is not the pin, so two runs cannot overlap.
>
> RUNBOOK §5's row 2a gains the same sentence in the approval commit.

### RD6 BEFORE: stale text, corrected in the decision and README

- Point 12's bullet "The files are frozen by REG-21 and REG-22 … freeze notice)." becomes: "REG-21's and REG-22's freezes ended when both batch 2s were computed (FILE(docs/decisions.md:16571), FILE(docs/decisions.md:16798)). The seal files and k1's closure are now protected only by this decision's arm A freeze (RD4)."
- Point 16's paragraph "The freeze (RB9) …" becomes: "RB9's freeze has ended (both batch 2s computed). Ruling 16 is (a), which changes no file."
- The section "The freeze" keeps its first sentence and its list, marked "ended", and then gives RD4's text.
- README:130 becomes RD4's first bullet, and drops "REG-21's and REG-22's freeze already bars these files …".
- Draft line 7, item map line 9 and README:8 name 56820bd and the implementing commit in place of "not committed".
- Draft line 29 becomes: "The scripts start only when HEAD holds REG-19's [RESULT], the rulings heading and, after both, the start heading, with no stop heading after the start (common.sh `gate_in_log`). They do not check heading 1."
- "Who decides" and proposed heading 2 say "(delegate), under the delegation (FILE(docs/decisions.md:4233)), with this owner-proxy pass and rule F round 2", in place of "(owner)".
- Point 6 says "an open-loop run of arm A (a burst run or its control)".

### RD7 BEFORE: the start entry for question G

The start entry quotes the gate file verbatim and names commit 3c8e5dc. It states:
- the command as the commit subject gives it, labelled BELIEF: the file has no record of its command, and a subject is not evidence;
- the four differences from RB5 (ii);
- these DERIVED facts:
  - 0 REG-20-named folders on the Mac;
  - at `3c8e5dc^`, the judged code, the seal blobs and the lock equal what `mac_checks` requires;
  - 6748c26 is an ancestor of 3c8e5dc;
  - stderr is 0 bytes;
  - k1's closed pattern cannot match the drift name;
- that the working tree's state at the computation is not recorded;
- that the gate is not computed again.

### RD8 BEFORE: holding folder and VM copies

Into the ops [DECISION], verbatim:

> No VM folder of arm A's eleven configs is removed from the VM before REG-20's [RESULT]; the 2026-11-04 exception does not apply to a folder held or set aside outside runs/. Nothing in `/Users/chalshik/Projects/aftershock-reg20-holding` is opened, moved or deleted before REG-20's [RESULT] except by the scripts. `docs/status.md`'s Watch list names that folder.

### RD9 LATER: the [RESULT]

- Duty (v) becomes: "every `recheck_changed` line of `queue_done.txt` with its recomputed `failed`; for each set-aside run, the attempt that replaced it". Under RD3 (vi), it also gives the outcome line with that seed counted `lost_open`.
- The [RESULT] states:
  - that the rulings were made by the delegate after REG-19's outcome was visible (the gate value and REG-19's [RESULT] heading) and before any REG-20 run existed;
  - each RD3 record written, with its stop line;
  - whether arm A or E1 ran first, and every gap the ordering caused between a burst run and its control.

### RD10 LATER: docs

These go in the approval commit or the next docs commit:
- RUNBOOK §3 step 6, §5 row 2 (done, 3c8e5dc, question G) and row 2a, as draft 2's Proposals 1–2, with RD5's sentence;
- the two open questions (RB14 (ii); harness death in a stuck open run);
- any held or set-aside run id named in a canonical doc goes into `manifests/pending_copy.txt` (FILE(tools/check_docs.py:69-76)).

### Optional (not required for this APPROVE)

- **RD-O1.** In `recheck_guards`, add `git diff --quiet $CHECKS_COMMIT -- harness/` (all of today's `harness/` equals 5ee6e38's, DERIVED). This turns RD4's harness clause into a stop.
- **RD-O2.** A later reviewed script revision could let the delegate write RD3 (vi)'s `not_run` and enforce RD3 (ii) mechanically.
- **RD-O3.** A joint E1/REG-20 lending rule, made later in both texts. When the first queue waits for the owner at a seed boundary (no control pending), the other may run its whole queue. This serves "use it whenever it's available"; neither draft allows it now.

---

## Answers in one place

- **Verdict:** APPROVE.
- **Picks:**
  - 2a `setaside`;
  - 6 (b);
  - 7 `lost_open`, with RD3 (ii)'s systematic-fault stop;
  - 8 (b);
  - 9 (a);
  - 16 (a);
  - G (a).

  None needs to stay with the real owner, who may overrule any of them.
- **Departures from earlier recommendations:**
  - 2a: round 1's `keep` becomes `setaside`. The new evidence is the holding folder (rule A4).
  - 7: draft 2's `not_run` becomes `lost_open`. Reasons: the registered label, the mixed case, and a stop that meets RA3.
- **BEFORE:** RD1–RD8. **LATER:** RD9–RD10.
