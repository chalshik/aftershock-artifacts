# Owner-proxy pass on D1 draft 2 with rule F round 2's DJ1–DJ3 (C2, the session-cap arm)

**Who.** An independent owner-proxy subagent, 2026-11-14 (UTC), under the delegation (FILE(docs/decisions.md:4231-4237)). It judges as the owner would: the study's credibility first, GPU time second. It wrote this file and scratch files only; nothing in the repo was edited, staged or committed.

**Inputs, checked.**
- HEAD 6992e0e at the start, 1acbc95 at the end. The commits between them are E1's end entry (223ce78) and the VM disk files with REG-20's owner-proxy delta (1acbc95). `git diff --quiet 6992e0e 1acbc95 -- docs/drafts/d1_draft2.md docs/drafts/d1_draft2_itemmap.md docs/drafts/d1_r2 analysis/ tests/ harness/ configs/ pyproject.toml uv.lock .python-version docs/probe/20261113_reg20/ops/common.sh` exits 0 (DERIVED).
- sha256: `docs/drafts/d1_draft2.md` `56b21551a78b13a7d97ecb1de9a733529c25682239c242ec87be7a2c7122bf62`; `rulef-d1-draft2-r2.md` `7017505f082f8c05e62bfa2c72a1294d6ade4d852f5952aedd271ecfb3b093f5` (committed in 223ce78); `rulef-d1-draft2-r2.patch` `9d0e80e372933c2be991b335d6aadbf54be3004cb2b1700e42dd1cbd1f762add`, the value the review states (DERIVED: `shasum -a 256`).
- On a `git archive` export of 6992e0e, the writer's three patches give `analysis/d1.py` `b1ec2948…`, `tests/test_d1.py` `d83b5463…` and `analysis/withheld.py` `e89e8a4d…`, the draft's values. Rule F's patch on top gives `4466e1ba…` and `cdcc2065…`, the review's values. `tests/test_d1.py` then gives 62 passed in 73 s (scratch run, not provenance). `git diff --quiet e788191 HEAD -- analysis/ tests/ harness/ configs/` and `git diff --quiet ce5f842 HEAD -- harness/ pyproject.toml uv.lock .python-version` both exit 0 (DERIVED).
- **Read:** CLAUDE.md (rule C, FILE(CLAUDE.md:19)); the delegation; the draft in full and its item map; rule F round 2 in full, with its patch applied. Rule F round 1 was read only through the item map and round 2's table. decisions.md:
  - 3930–3989 (the design choices, item 2 among them);
  - 4045–4060 (REG-20's [REG]) and the headings at 4200 and 4209;
  - 16527–16542 (REG-19's [RESULT]) and 16748–16758 (REG-22 batch 2);
  - 17020–17094 (E1's [REG]), 18286–18420 (E1's approval) and 19394–19500 (E1's checkout, the VM disk entry, E1's end entry).
  
  Also read: `docs/claims.md`; `docs/experiment-plan.md` 395–444; REG-20 operations draft 3 (headings 36–75, 255–269, point 18, "The arm A hold"); REG-20's owner-proxy delta (verdict, point D, DH2, the hold during a pause); `docs/probe/20261113_reg20/ops/common.sh` 50–86; REG-24 draft 2, "Order"; `agent/DECISION_TREE.md`, the GPU order; `agent/FOR_AUTHOR.md` −20 to 0; `agent/RUNBOOK.md` §5; `harness/loadgen.py` 65–71 and 176–178; `analysis/tables.py` 46–48; `harness/run.py`'s diff from `a7bb77a`; parts of `d1.patch`.
- **Not opened:** anything under `runs/`, the backups, `RESUME.md`, `docs/paper/`, any `state/` folder, `docs/FABLE_PROMPT.md`. No cap and no number from any run was computed. `AFTERSHOCK_UNSEAL` was never set. `d1.predicted_matrix`, which reads no run, was run in scratch.

---

**Verdict: APPROVE.** Conditions:
- DM1–DM7: BEFORE the approval entry.
- DM8–DM14: BEFORE the first capped launch.
- DM15–DM16: LATER.

**What is approved:** draft 2, plus DJ1–DJ3 verbatim, plus R1–R21 below, plus the code of DM2 and DM3. The approval stands only if rule F round 3 returns READY on that code (DM4).

**Two briefed points are the owner's alone, and this pass does not decide them.**
- **Taking a `harness_fault` run out of n.** This does not block approval: the draft's own fallback lies inside the delegation, and DM2 takes it.
- **Freeing VM disk.** This blocks only a launch (DM12).

### 1. Would the owner approve D1, and before D2?
**Yes: after REG-20 arm A, with D2 drafted meanwhile.** Reasons the owner would accept:
1. **The owner put this control in C2's test.**
   - claims.md names "a session-cap arm" as one of the two controls that cut a link (FILE(docs/claims.md:25)).
   - C2's refutation is "stuck runs that stay stuck under the session cap" (FILE(docs/claims.md:27)).
   - The cap's rule was fixed before any capped run (FILE(docs/decisions.md:3949)), and the owner approved the load-generator change for it (FILE(docs/decisions.md:4209)).
   - Approving a mostly confirmatory step that the owner placed in the plan has a precedent: E1 (FILE(docs/decisions.md:18286), DF9 (f)).
2. **Rule A1 is met, if weakly.** Outcomes change decisions:
   - `supports` gives a C2 status line, and D2 becomes the next C2 step;
   - `refutes`, `cap_did_not_cut` or `stuck_split` stop loop-cut runs, which saves D2's ≈ 6.25–12.5 h;
   - `mixed` goes to the owner.

   The ≈ 0.0006 for an outcome against C2 is computed from the writer's per-seed belief P(stuck under the cap) ≈ 0.04 (DERIVED by rule F §3.6). No capped cold state has ever been run, so that belief is untested (BELIEF). The draft itself calls D1 largely confirmatory, and I accept that. Its value lies elsewhere:
   - (a) It tests C2's population link by prevention. The prior work on record tests it only by rescue (FILE(docs/decisions.md:3980), FILE(docs/decisions.md:4224), FILE(docs/decisions.md:4227); BELIEF as to the papers).
   - (b) The onset split: P ≈ 0.65 that at least one cut seed is `formed_then_cleared` (BELIEF, the draft). DJ2 makes the split count correctly.
3. **`supports` hardly separates C2 from pool pressure driven by the population** (rule F §3.6 and §4). That is right, and the draft's `supports` line already says so: D1 does not say which link mattered, nor whether the loop runs through the cache, and the caching-off control is not run. It is no reason to skip D1. D2 cannot answer D1's question either: D2 cuts the cache and D1 the population, and C2's loop needs both links.
4. **D2 first, or D2 instead: no.**
   - D2 cannot be registered now. Its load needs a cache-off capacity choice that the plan leaves to its registration (FILE(docs/experiment-plan.md:424)). The closed-loop floor E1 measured stays withheld until E0's [REG] (FILE(docs/decisions.md:17026)), and the item map lists this as question 13. "D2 first" therefore means the GPU waits for design work.
   - "D2 instead" leaves unrun a control that claims.md names.
   - If both run, the order does not change the total cost, and D1 first has option value: a stuck outcome stops D2.
5. **Cost.**
   - D1 alone is 6.2 GPU h (≈ 7.7 expected, ≤ 18.7). That exceeds the plan's 4–6 h for D1 and D2 together (FILE(docs/experiment-plan.md:422)), and step D becomes ≈ 12.5–18.7 h (DERIVED in the draft).
   - The plan says its hours are rough and fixed only at registration (FILE(docs/experiment-plan.md:401)).
   - Fewer seeds save nothing worth having: at n = 3, `below_reg19` cannot hold, and P(`supports`) ≈ 0.44 (rule F §3.6, DERIVED from the beliefs).
   - Accepted. DM6 states it, and D2's registration states step D's total (DM16).
6. **When: not before REG-20 arm A's hold ends.**
   - D1's registered commit adds a `SEALS` row. REG-20's scripts pin `analysis/withheld.py`'s blob (FILE(docs/probe/20261113_reg20/ops/common.sh:55), FILE(docs/probe/20261113_reg20/ops/common.sh:82)), and arm A's hold forbids the row (FILE(docs/drafts/reg20_ops_decision_draft3.md:563-566)).
   - REG-20 arm A carries K1, a paper claim; D1 is a control for the premise. Reopening REG-20's reviewed scripts to put D1 first would cost REG-20 a review round and gain no GPU time:
     - D1 also needs disk that only the owner can free (DM12);
     - its caps, configs and operations scripts do not exist yet.
   - D1's tests need its seal row (`test_d1_seal_…`, `test_table_refuses_while_the_capped_folders_are_sealed`), so the code cannot be committed without the row (DERIVED from FILE(docs/drafts/d1_r2/test_d1.patch)). See DM7.

### 2. The 13 owner questions (item map, "Questions that remain")
Ruling codes: (i) picked now, inside the delegation; (ii) the owner's alone; (iii) not needed for approval.

1. **The two departures from item 2: (i), both accepted.**
   - Item 2 is the agent's choice, made under the owner's "do whatever leads to correct results" and left open to change in the [REG] (FILE(docs/decisions.md:3947)).
   - Read literally, it could never give `stuck`. Under the cap the server's line is near 0 by construction (the draft, "The server's waiting line cannot fail", DERIVED there). A capped run judged on that line is never backlogged, so D1 could never refute C2.
   - Departure (1) makes `stuck` reachable through the cap's queue, and it makes `recovered` stricter, since the cap's queue must also clear. It is stricter in both directions.
   - Departure (2) reads the prefix reuse of later turns, which is REG-20's readout, approved by the owner (FILE(docs/experiment-plan.md:415)). The hit counter mixes in first turns and burst requests (the draft, "Inputs"), and under a cap the served mix differs between the arms.
   - Item 2's server-side reading stays as `k_cut_server_side`, a readout.
2. **`harness_fault`.**
   - **(ii) Taking the run out of n is the owner's alone.** CLAUDE.md rule C reserves "marking a run invalid beyond the automatic checks" (FILE(CLAUDE.md:19)), and the delegation's list does not name it (FILE(docs/decisions.md:4233)).
   - **(i) The pick inside the delegation is the draft's fallback:** the run counts in n as `unclear` (DM2). Approval does not wait for the owner.
   - The bias left over: a false flag on a stuck seed still turns it from stuck to `unclear`. That needs hand-overs of ≈ 0.3 s, against the milliseconds the harness takes (rule F §1, a synthetic trace; FILE(harness/loadgen.py:65-71)). The [RESULT] therefore reports `decision_underlying` (DM2, DM15).
3. **The thresholds no earlier entry fixes: (i), all four accepted as drafted.** They are fixed before any capped run and before the caps, so rule A5 holds: the capped data do not exist (rule F §3.3).
   - **`hit_climb` 0.06 on reuse.** `rewarming` is tested before `stuck`, so this leans toward `supports`. The lean is bounded by `cp_upper_not_cut`, and DJ-O3 names such seeds "possibly stuck" (R16).
   - **`recovered_q_excess` 1.0 session.** This is looser than 1.0 request. A cold cap builds ≈ 19 sessions per 600 s (DERIVED in the draft), far from 1.
   - **`drain_horizon_s` 3600.** Rule F's planned session starts in the end window run at 0.235–0.268 per s, against 0.213–0.225 per s leaving at REG-19's cold rates (DERIVED from configs and FILE(docs/decisions.md:16539)). So the drain exception is not expected to make a cold seed `partial`. DJ-O2 reports the planned rates.
   - **`max_idle_share` 0.05.** It is argued from the mechanism, and under DM2 it can no longer take a run out of n.
   - The approval entry names the two leans (DM6).
4. **`cap_did_not_cut` and `stuck_split`: (i).**
   - The two are read alike (DJ1).
   - The reading is fixed now for any delegate's draft (R10): these seeds count as "stuck under the session cap" in claims.md's words, with the caps, KV, N and the gauge stated beside them. They are not set aside as "not the test intended".
   - The owner still decides C2's status, as the draft says for `refutes`.
   - Reason: rule A's default stance. A reading that rescues C2, chosen after a stuck outcome, is what rule A5 guards against, and the design fact is kept by stating KV and N beside the count. P ≈ 0.0003 for each (DERIVED from the draft's beliefs), so fixing the reading now costs nothing.
5. **The decision rule: (i), "most", as drafted.**
   - It is REG-18's and REG-19's rule. On the same seeds, the uncapped arm was judged by it (FILE(docs/decisions.md:16527)).
   - McNemar's test needs all five seeds cut. It is reported.
   - The status line may say the cells separate only with `below_reg19`, and it quotes McNemar's p beside the bounds (DM15).
6. **Cost: (i), the overrun is accepted** (§1, reason 5).
7. **Drift, and the cap path: (i), neither is added.**
   - **The uncapped rerun** would cost ≈ 1.25 h and a further review round, for one run.
     - REG-20's drift rerun checks the day, but it runs at REG-20's pin `1cface7`, whose `harness/` is `a7bb77a`'s (DERIVED: `git diff --quiet a7bb77a 1cface7 -- harness/` exits 0). So it does not cover the harness change. The draft did not say this; R11 and R12 now do.
     - The change is not server-facing: recorder robustness and its log, stricter checks, and the cap path (BELIEF; FILE(docs/decisions.md:4200), FILE(docs/decisions.md:4209); `harness/run.py`'s diff from `a7bb77a` adds only the cap's validation and the recorder's log).
     - If the drift rerun is read and is not cold-backlogged, the `supports` line may not credit the cap (R11).
   - **DG-O1** would read a sealed capped run's records before D1's [RESULT]. That is close to "reading outcome data a pending registration withholds", which is not delegated (FILE(docs/decisions.md:4235)), and it would save ≈ 0.15 h (BELIEF, item map). Under DM2, a systematic slot leak costs at most the five runs and yields `unclear`, never a wrong label.
8. **The tree check: (i).** E1's restricted form, plus DJ-O6 in full (R19–R21, DM6, DM9). Rule F §3.4 found it as strong for what runs.
9. **The order: (i).** The drafted rule, E1's (FILE(docs/decisions.md:17076)), applies with DM7 and DM11. Facts at 1acbc95:
   - E1 has ended (FILE(docs/decisions.md:19459));
   - no REG-20 arm A operations, rulings or start heading exists yet (DERIVED: `grep -n '^## .*REG-20 arm A'` matches only the VM disk entry at 19452);
   - REG-24 needs the owner's ruling on the drop, a PROTOCOL matter (FILE(agent/FOR_AUTHOR.md:11)).

   So arm A comes next. D1 and REG-24 follow arm A's hold, by the rule.
10. **`write_configs`: (i).** Written by code, new files only, with the byte-for-byte check (R19).
11. **VM disk.**
    - **(iii) for approval.** For a launch it is **(ii), the owner's alone**: deleting is not delegated (FILE(docs/decisions.md:4235)).
    - 3,794,420 kB were free after E1 (PROBE(docs/probe/20261114_vm_disk/disk_after_e1_20261114T042056Z.txt)). Arm A's 11 runs need 4,524,512 kB (FILE(docs/decisions.md:19452)), and arm A starts under option (b), so a disk stop in the middle is accepted (FILE(docs/drafts/reviews-2026-11-13/proxy-reg20-ops-draft3-delta.md:8)). D1 needs 1.2–3.6 GB (DERIVED in the draft).
    - So D1 cannot launch unless the owner frees space (DERIVED: 3.79 GB < 4.52 GB before D1's own need). The list of verified folders is ready for the owner (FILE(agent/FOR_AUTHOR.md:7)). See DM12.
12. **350 W: (iii).**
    - The agent may run `sudo -n nvidia-smi -pl 350` (FILE(docs/decisions.md:4232), FILE(docs/decisions.md:4235)).
    - It needed a password on 2026-11-12 (FILE(agent/FOR_AUTHOR.md:33)). So unless a NOPASSWD rule now exists, the owner sets 350 W after a reboot.
    - The operations scripts read the limit and never set it (DM14).
13. **D2's capacity: (iii) for D1.** It is why D2 cannot go first (§1, reason 4), and it goes into D2's registration (DM16).

### 3. DJ-O1 to DJ-O7
- **DJ-O1: taken.**
  - `max_idle_stretch_s` in `slots`.
  - The margin is stated in the text (R2).
  - The underlying label is reported, which DM2 extends to `decision_underlying`.
- **DJ-O2: taken.**
  - The planned session-start rates over the end window and its halves, in `row` (schedule only).
  - The paired-label sentence (R17).
- **DJ-O3: taken, extended.**
  - `cap_backlogged` is computed in the `rewarming` branch too.
  - "Possibly stuck" also covers a `partial` seed whose cap queue is above its baseline + 1 while draining (R16).
- **DJ-O4: taken.**
  - Preemptions per span: the population alternative's mechanism, rule F §4.
  - The cap queue at the burst's end and at the exit.
  - Confounds 6 corrected (R13). Its sentence was wrong as written: the first span gives a mean, not the value at 1080 s.
- **DJ-O5: taken.** A 60 s clearing time from the exit, in both arms, reported and never judged. It shows where each seed falls against T7's ≈ 1398 s cut.
- **DJ-O6: taken in full.**
  - `--name-status` with exactly five `A` lines.
  - The chain from the registered commit.
  - Byte-for-byte equality with `d1.config_text`.
  - The sha256 of `analysis/d1.py` and `tests/test_d1.py`, quoted (R19–R21, DM6).
- **DJ-O7: taken.** DM2's change and DM3's code go to rule F round 3 (DM4). No other threshold or branch changes.

### 4. Conditions

**BEFORE the approval entry**
- **DM1. DJ1–DJ3 verbatim.**
  - The text is applied by script from the review's `text` blocks.
  - The code is `rulef-d1-draft2-r2.patch`, applied after the three draft patches.
  - The item map's question 4 changes as DJ1 asks.
  - The writer redoes the head's sha256, the saved pytest outputs and `SHA256SUMS.txt` (the review's last paragraph of DJ3).
- **DM2. `harness_fault` counts in n as `unclear`** (question 2). Code, on top of DM1:
  - `row`: `label` is `unclear` when `harness_fault(sl)`, with a new key `harness_fault` (bool). `label_values["label"]` keeps the label the records would otherwise give.
  - `outcome`: refuses a `harness_fault` label (ValueError), so that no path of the registered computation takes a valid capped run out of n.
  - `predicted_matrix`: maps the `harness_fault` belief to `unclear` before it calls `outcome`.
  - `table`: adds `harness_faults` (the seeds flagged) and `decision_underlying`, the decision `outcome` gives on the `label_values["label"]` of every row (a readout, never judged).
  - The module docstring and `outcome`'s docstring are changed to match.
  - Tests:
    - `test_outcome_rules`' `harness_fault` cases are replaced by a refusal test;
    - the end-to-end seed 18 is `unclear`, has `harness_fault` True and is in n;
    - a flagged seed with stuck-shaped records is `unclear`, and `decision_underlying` counts it as stuck;
    - the prediction test is updated.
  - Text: R1–R9.
  - Numbers (DERIVED: my scratch run of `d1.predicted_matrix` with that mapping, against the round-2 code): every decision probability is unchanged to four decimals; P(`too_few` from labels) becomes 0; P(`supports` with `below_reg19`) becomes 0.2536, from 0.2702. The writer's run at the registered code is the number's source, and it must match.
- **DM3. DJ-O1 to DJ-O5's code**, reported only. No label, threshold or decision changes.
  - `slots`: `max_idle_stretch_s`.
  - `row`: the planned session-start rates over [3480, 4080) s and its halves; `cap_queue_at` at the burst's end and at the exit; `clear_60s` for both arms (the start of the first 60 s window from the exit with reuse ≥ baseline − 0.06 over at least 20 turns, or None).
  - `label`: `cap_backlogged` in the `rewarming` branch, plus the cap queue's end mean against its baseline + 1.0 for `partial`.
  - `spans`: preemptions.
  - `table`: `possibly_stuck`.
  - Tests for each.
  - Text: R13 and R16–R18.
- **DM4. Rule F round 3** is run by a separate subagent. It sees only the merged [REG] text (draft 2 + DJ1–DJ3 + R1–R21) and the diff of DM2 and DM3 against the round-2 tree. It must return READY. It is quoted verbatim in the [REG].
  - If it requires items, they are applied verbatim, and an owner-proxy delta pass checks them before the approval entry.
  - If it returns READY with no required item, this approval stands.
  - If it rejects DM2's design, that is binding, and D1 goes back to drafting.
- **DM5. Text:** R10 (question 4), R11 and R12 (what REG-20's drift rerun separates, and the `supports` line's condition on it).
- **DM6. The approval entry**, headed `## <date> · [DECISION] (delegate) D1 approved …`, states:
  - (a) What is approved: the [REG] text as in DM4, and the code. It quotes the sha256 of `analysis/d1.py`, `tests/test_d1.py` and `analysis/withheld.py` at the registered commit, equal to round 3's values (DJ-O6).
  - (b) The authority: the delegation; rule F rounds 1–3 verbatim in the [REG]; this verdict verbatim. It also names what was not taken: the n-removal branch, VM disk, and 350 W.
  - (c) The 13 rulings of §2. It names the two threshold leans (rule F §3.3) and both departures from item 2, with their reasons.
  - (d) The cost: 6.2 GPU h (≈ 7.7 expected, ≤ 18.7) accepted against the plan's 4–6 h for D1 and D2 together, with step D at ≈ 12.5–18.7 h if D2 runs.
  - (e) These outputs, quoted at the registered commit:
    - `git diff --quiet ce5f842 <registered commit> -- harness/ pyproject.toml uv.lock .python-version; echo $?` → 0 (item 7);
    - `closure.py --at <registered commit> analysis/d1.py`;
    - the full `uv run pytest`, `tests/test_check_docs.py` included, passing;
    - `git grep -n` of the order headings: E1's end entry, and REG-20 arm A's start entry, end entry and `final.sh` files commit, and REG-24's.
  - (f) RUNBOOK §5's row 5 ("D1, D2 | not registered", FILE(agent/RUNBOOK.md:68)) is amended for D1: the commands, the registered computation, and "Seal lifted by `[RESULT] D1 (C2, session cap)`".
  - (g) A FOR_AUTHOR item for the owner: the n-removal branch was not taken, and the owner may overrule DM2 by an (owner) entry before the caps are computed; the cost overrun; R10's reading; D1's disk need.
- **DM7. The registered commit lands after REG-20 arm A's hold has ended.** The registered commit is the approval entry with every patch applied, the seal row included (R15).
  - The hold ends when `final.sh`'s two files are committed, or with arm A's "ended by a stop" end entry. A pause does not end it (DH2, FILE(docs/drafts/reviews-2026-11-13/proxy-reg20-ops-draft3-delta.md:133-136)).
  - Before that, whether or not arm A has started, it lands only by an entry that changes REG-20's `SEAL_BLOBS` by a reviewed commit.
  - Until then only drafts and reviews of D1 are committed. That includes the operations scripts, as drafts.

**BEFORE the first capped launch**
- **DM8. The caps.**
  - D1's [REG] is the registration of the caps computation: an analysis-only registration of existing runs, which is delegated (FILE(docs/decisions.md:4233)). It names the inputs, the code, the command, the output and the heading before anyone computes the caps, so no separate [REG] is needed. The approval entry names it as approved.
  - The caps are computed once, from the registered worktree, after DM7's commit.
  - `## <date> · [RESULT] D1 caps (registered computation on REG-19's five controls)` is committed with its saved output and nothing else.
  - The caps do not decide whether D1 runs (R14).
- **DM9. The configs commit.** It contains the five files written by `write_configs`. The commit's entry quotes three things (R19–R21):
  - the line `True` printed five times by the byte-for-byte check;
  - `git diff --name-status`, giving exactly five `A` lines;
  - the chain, from `python -m analysis.d1 chain` at the registered commit.
- **DM10. The operations scripts.** Written under `docs/probe/<date>_d1/ops/` in E1's shape. Their own rule F pass and owner-proxy pass come first. They are committed with `[DECISION] (owner|delegate) D1 starts` while `d1_commit.txt` reads `UNSET`, and then `d1_commit.txt` is set and committed alone. Beyond the draft's sketch, they must have:
  - (a) A gate by pattern on the end entry of every item ahead. That is REG-20 arm A's two end headings as its approved operations decision names them, plus the absence of REG-20's queue lock, tested for existence only (REG-20's form for E1, FILE(docs/drafts/reg20_ops_decision_draft3.md:371-378)). Use the same form for REG-24 if REG-24 is ahead.
  - (b) A free-disk floor checked before each attempt record, no lower than E1's 2,097,152 kB (FILE(docs/probe/20261113_e1/ops/common.sh:34)).
  - (c) `vm_checkout.sh`, moving the VM forward from arm A's pin `1cface7`, an ancestor, to D1's launch commit.
  - (d) The tree check with DJ-O6's form.
- **DM11. The order.** No capped launch, VM move or queue start happens before the end entry of every item ahead under E1's rule. D1's first [OPS] after the VM move quotes `git grep -n` of those end entries at the Mac's HEAD.
- **DM12. Disk.**
  - D1 launches only when the VM has free space at or above DM10's floor. A shortfall spends no attempt.
  - Freeing space is the owner's alone.
  - The agent may only hand the owner the verified list (FILE(agent/FOR_AUTHOR.md:7)) and record D1's need there.
- **DM13. E1's validity record.** E1's end entry is now committed: six runs, `valid True failed []` (FILE(docs/decisions.md:19459)). `D1 starts` cites it, which meets precondition 7.
- **DM14. 350 W** is read as 350.00 W by the session probe after every boot. It is set by `sudo -n nvidia-smi -pl 350` if that works, otherwise by the owner.

**LATER**
- **DM15. The [RESULT]**, besides the draft's duties, reports:
  - the seeds flagged `harness_fault` with their underlying labels and `decision_underlying`;
  - the "possibly stuck" seeds;
  - the onset split with DJ2's statement of where its cut falls, and `clear_60s`;
  - McNemar's p beside the bounds in any `supports` line;
  - the drift-readout condition of R11;
  - the real GPU hours against the plan.
- **DM16. D2 is drafted now**, while arm A and D1 run, and it is not gated on D1 except by D1's stop outcomes. Its registration states:
  - which capacity sets its load: E1's floor after E0's [REG], the open-loop floor, or μ_off = 1.0 (FILE(docs/experiment-plan.md:424));
  - step D's total cost against the plan.

  Its place in the GPU order follows E1's rule.

### 5. Text replacements (R1–R21)
**How they were checked.**
- Apply DJ1–DJ3 first (rule F's ten pairs), then R1–R21 in the order given.
- Each of the 31 anchors occurs exactly once in `docs/drafts/d1_draft2.md` (sha256 `56b21551…bf62`), and each is unique at its turn in that order (DERIVED by `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/proxy_d1_r2/scripts/check_anchors.py`, which parses DJ1–DJ3 from the saved review; output `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/proxy_d1_r2/work/anchors_check.txt`; scratch, not provenance).
- The other order fails: R4 rewrites the words that DJ3's second anchor needs.
- The merged text's sha256 in that order is `e5140670402407b9b109e5328ebfbad594b0a3b5f02e1f39c4972ae0dabfa609`. It holds one line starting with `## `, the [REG] heading template, which is the draft's own.
- Each anchor and replacement below sits in a `text` block, in the same form as rule F's, so the same script can take them.

**R1** (DM2). Anchor:
```text
- **`harness_fault`** (needs the owner's approval: it removes a run from n beyond the automatic checks, CLAUDE.md rule C):
```
Replacement:
```text
- **`harness_fault`** (a flag; the run stays in n as `unclear`, owner-proxy d1 r2, DM2):
```

**R2** (DM2). Anchor:
```text
Such a run is listed and leaves n; it is not rerun under this entry (its cause needs an [OPS] or [CORR] first). If this label is not approved, the same run counts in n as `unclear` (one line in `d1.row`).
```
Replacement:
```text
Such a run counts in n as `unclear`, neither cut nor stuck, and `cp_upper_not_cut` counts it as possibly stuck; `d1.row` keeps `harness_fault` True and the label its records would otherwise give (`label_values["label"]`), and `d1.table` lists the seeds flagged and gives `decision_underlying`, the decision `d1.outcome` gives with those underlying labels in place of `unclear` (a readout, never judged; rule F d1 r2, DJ-O1). It is not rerun under this entry (its cause needs an [OPS] or [CORR] first). Taking such a run out of n would mark a run invalid beyond the automatic checks, which CLAUDE.md rule C gives the owner and the delegation does not name (FILE(docs/decisions.md:4233-4235)); that branch is not taken. The margin: on records of the harness's shape, a stuck seed is flagged only when a hand-over takes about 0.3 s (rule F d1 r2, section 1, a synthetic trace), while the harness hands a freed slot to the oldest waiter as the session's last reply is recorded (FILE(harness/loadgen.py:65-71), FILE(harness/loadgen.py:176-178)); `d1.slots` also reports `max_idle_stretch_s`, the longest stretch with a session waiting and a slot free (reported, never judged; DJ-O1).
```

**R3** (DM2). Anchor:
```text
- **The matrix** (`d1.outcome`; `harness_fault` leaves n), rules in this order
```
Replacement:
```text
- **The matrix** (`d1.outcome`; a `harness_fault` run counts in n as `unclear`), rules in this order
```

**R4** (DM2). Anchor:
```text
the spent seed is in `not_run`, `harness_fault` leaves n
```
Replacement:
```text
the spent seed is in `not_run`, the seed with a slot left free counts in n as `unclear` with `harness_fault` True
```

**R5** (DM2). Anchor:
```text
`unclear` 0.05, `harness_fault` 0.01. So P(cut)
```
Replacement:
```text
`unclear` 0.05, `harness_fault` 0.01 (counted as `unclear` in the matrix). So P(cut)
```

**R6** (DM2). Anchor:
```text
P(`too_few` from labels) < 0.0001; E[k_cut] 3.80; P(`supports` and the cells separate, `below_reg19`) 0.270.
```
Replacement:
```text
P(`too_few` from labels) 0 (a flagged seed stays in n); E[k_cut] 3.80; P(`supports` and the cells separate, `below_reg19`) 0.254 (0.270 while a flagged seed left n).
```

**R7** (DM2). Anchor:
```text
P(`too_few`) < 0.0001; E[k_cut] 3.80, E[k_stuck] 0.20;
```
Replacement:
```text
P(`too_few`) 0; E[k_cut] 3.80, E[k_stuck] 0.20;
```

**R8** (DM2). Anchor:
```text
P(`supports` with `below_reg19`) 0.2702.
```
Replacement:
```text
P(`supports` with `below_reg19`) 0.2536 (the `harness_fault` belief counted as `unclear`, DM2; 0.2702 while it left n).
```

**R9** (DM2). Anchor:
```text
2. `harness_fault` leaves n (CLAUDE.md rule C), or the run counts in n as `unclear`.
```
Replacement:
```text
2. `harness_fault`: settled (owner-proxy d1 r2, DM2): the run counts in n as `unclear`; taking it out of n is the owner's (CLAUDE.md rule C) and is not taken.
```

**R10** (DM5). Anchor:
```text
The [RESULT] gives both readings with the end-window KV and N per seed, and the owner decides C2's status.
```
Replacement:
```text
The [RESULT] gives both readings with the end-window KV and N per seed, and the owner decides C2's status (as for `refutes`). The reading a delegate may draft is fixed here, before the caps are computed (owner-proxy d1 r2, question 4): the status line counts these seeds as "stuck under the session cap" in claims.md's words (FILE(docs/claims.md:27)) and states beside them the caps, the end-window KV and N per seed and that the gauge reached 0.80; it does not set them aside as "not the test intended".
```

**R11** (DM5). Anchor:
```text
(c) day or drift (the capped runs run days after REG-19's), separated only partly by `gate.reg19_baseline_pair` against the control and the baseline completion rate, and by REG-20's drift rerun if its seal has lifted (`d1.drift_readout`, readout);
```
Replacement:
```text
(c) day, drift or harness (the capped runs run days after REG-19's, and on `5ee6e38`'s harness where REG-19's ran on `a7bb77a`'s), separated only partly by `gate.reg19_baseline_pair` against the control and the baseline completion rate, and, for the day alone, by REG-20's drift rerun if its seal has lifted (`d1.drift_readout`, readout): that rerun runs at REG-20's pin `1cface7` (FILE(docs/drafts/reg20_ops_decision_draft3.md:48)), whose `harness/` is `a7bb77a`'s (DERIVED: `git diff --quiet a7bb77a 1cface7 -- harness/` exits 0), so it does not separate the harness change; that change is not server-facing (BELIEF: the recorder's survival of a half-written line and its log, stricter `recorder` and `gpu_steady` checks, and the session cap, FILE(docs/decisions.md:4200), FILE(docs/decisions.md:4209)), and no uncapped run on D1's harness is made (the approving entry, question 7); if `d1.drift_readout` reads and REG-20's rerun is not `cold_backlogged`, the status line says so, says that drift is not excluded, and gives k of n without saying that the cap prevented the stuck state (owner-proxy d1 r2, DM5);
```

**R12** (DM5). Anchor:
```text
REG-20's drift rerun, once its seal lifts, is a readout; an uncapped rerun of one seed (≈ 1.25 GPU h) would measure drift inside D1 and is not added (a question for the approver).
```
Replacement:
```text
REG-20's drift rerun, once its seal lifts, is a readout of the day alone (it runs at REG-20's pin `1cface7`, whose `harness/` is `a7bb77a`'s; DERIVED: `git diff --quiet a7bb77a 1cface7 -- harness/` exits 0); an uncapped rerun of one seed on D1's harness (≈ 1.25 GPU h) would measure day and harness together inside D1 and is not added (the approving entry, question 7).
```

**R13** (DM3). Anchor:
```text
the cap queue at that time is reported beside it (`spans`, first span).
```
Replacement:
```text
the cap queue at the burst's end and at the exit is reported beside it (`d1.cap_queue(run, [burst_end, exit])` in `d1.row`; rule F d1 r2, DJ-O4); the first span of `spans` gives its mean over [1080, 1380) s, not its value at 1080 s.
```

**R14** (DM7). Anchor:
```text
No rule, label or threshold of D1 may change after the caps are seen; a change is a [CORR] and goes back to rule F.
```
Replacement:
```text
No rule, label or threshold of D1 may change after the caps are seen; a change is a [CORR] and goes back to rule F. Nor do the caps decide whether D1 runs: D1 runs at the computed caps whatever they are, a cap at or above 34 (which could let the gauge reach 0.80) included; only a cap that `d1.cap_value` refuses stops D1, for a [CORR] (owner-proxy d1 r2, DM8).
```

**R15** (DM7). Anchor:
```text
with the three patches applied (`analysis/d1.py`, `tests/test_d1.py`, the seal row) and `uv run pytest` passing.
```
Replacement:
```text
with the three patches, `rulef-d1-draft2-r2.patch` and the round-3 delta's code applied (`analysis/d1.py`, `tests/test_d1.py`, the seal row) and `uv run pytest` passing. That commit adds a row to `analysis/withheld.py`'s `SEALS`, a file whose blob REG-20 arm A's scripts pin (`SEAL_BLOBS`, FILE(docs/probe/20261113_reg20/ops/common.sh:55), checked at FILE(docs/probe/20261113_reg20/ops/common.sh:82)) and whose `SEALS` arm A's hold freezes (FILE(docs/drafts/reg20_ops_decision_draft3.md:563-566)). So it is committed only after REG-20 arm A's hold has ended (`final.sh`'s two output files committed, or arm A's end entry headed `… REG-20 arm A ended by a stop: …`; a pause does not end it, rule F reg20 ops r3, DH2); before that, whether or not arm A has started, only by an entry that puts D1's row first and changes REG-20's `SEAL_BLOBS` by a reviewed commit with a new `scripts_commit.txt` before REG-20's queue starts again (RC1 item 3's path, FILE(docs/drafts/reg20_ops_decision_draft3.md:565)): an (owner) entry, or a (delegate) one with its own rule F review and owner-proxy pass. Until then nothing of D1 is committed but drafts and reviews (owner-proxy d1 r2, DM7).
```

**R16** (DM3). Anchor:
```text
`bad_baseline`, `unclear`, `rewarming` and `partial` count in n, neither cut nor stuck.
```
Replacement:
```text
`bad_baseline`, `unclear`, `rewarming` and `partial` count in n, neither cut nor stuck; the [RESULT] names every `rewarming` or `partial` seed whose cap queue's end mean is above its baseline mean + 1.0 session (`cap_backlogged`, computed in the `rewarming` branch too) as "possibly stuck", and these count in `cp_upper_not_cut` (rule F d1 r2, DJ-O3).
```

**R17** (DM3). Anchor:
```text
0.031 for 5, 0.063 for 4, 0.125 for 3 (DERIVED); a readout, never judged.
```
Replacement:
```text
0.031 for 5, 0.063 for 4, 0.125 for 3 (DERIVED); a readout, never judged. The pairing holds under one rule: D1's label applied to REG-19's uncapped runs, with the server's line in the cap queue's place, gives `stuck_kv_full` in all five (DERIVED from published values: reuse 0.000 in every span and end-window KV 0.950–0.952, FILE(docs/decisions.md:16752-16756); end-window mean waiting 179.8–281.3 with end slopes +0.0193 to +0.0714 per s, FILE(docs/decisions.md:16533-16537); BELIEF that each pre-burst mean waiting is below ≈ 178, the same-schedule controls being `recovered`, FILE(docs/decisions.md:16542); rule F d1 r2, DJ-O2).
```

**R18** (DM3). Anchor:
```text
`gate.reg19_baseline_pair(control, capped run)`; `c2.eviction_readout`. Matrix:
```
Replacement:
```text
`gate.reg19_baseline_pair(control, capped run)`; `c2.eviction_readout`; preemptions per span in both arms (`spans`, the rise of `vllm:num_preemptions_total` over the span, as `tables._preemptions`, FILE(analysis/tables.py:46-48); DJ-O4); the cap queue at the burst's end and at the exit (DJ-O4); the first 60 s window from the exit whose reuse is back within 0.06 of the baseline, in both arms (DJ-O5); the planned session-start rate over the end window and over its two halves (`harness.workload.build_schedule` on the run's config, schedule only; DJ-O2); `slots`' `max_idle_stretch_s` (DJ-O1); `harness_fault` and the underlying label (DM2). Matrix: the seeds flagged `harness_fault` and `decision_underlying` (DM2); the "possibly stuck" seeds (DJ-O3);
```

**R19** (DM9). Anchor:
```text
quoting the command and `git diff --name-only <registered commit> <configs commit> -- harness/ pyproject.toml uv.lock .python-version <every file of d1.config_chain for the five seeds>`, which lists the five capped configs and nothing else.
```
Replacement:
```text
quoting the command, the line `True` printed five times by a check that each written file equals `d1.config_text(seed, caps[seed])` byte for byte, and `git diff --name-status <registered commit> <configs commit> -- harness/ pyproject.toml uv.lock .python-version <every file of d1.config_chain for the five seeds>`, which prints exactly five lines, each `A` and one of the five capped configs; the chain is the output of `python -m analysis.d1 chain` run at the registered commit (rule F d1 r2, DJ-O6).
```

**R20** (DM9). Anchor:
```text
The configs entry (item 3) quotes `git diff --name-only <registered commit> <configs commit>
```
Replacement:
```text
The configs entry (item 3) quotes `git diff --name-status <registered commit> <configs commit>
```

**R21** (DM9). Anchor:
```text
D1's operations decision (item 4) quotes the same command up to the launch commit,
```
Replacement:
```text
D1's operations decision (item 4) quotes the same command (`--name-status`, exactly five `A` lines) up to the launch commit,
```

### 6. Owner-proxy line for the delegate's [DECISION] entry
> **Owner-proxy** (an independent subagent, on D1 draft 2 with rule F round 2's DJ1–DJ3; `proxy-d1-draft2.md`, sha256 <of this file>): **APPROVE.** Conditions: DM1–DM7 before this entry, DM8–DM14 before the first capped launch, DM15–DM16 later. What is approved: draft 2, plus DJ1–DJ3 verbatim, plus R1–R21, plus DM2 and DM3's code; it stands only if rule F round 3 (DM4) is READY on that code. The owner's questions are ruled inside the delegation, except two that stay the owner's: taking a `harness_fault` run out of n (CLAUDE.md rule C), which is not taken, so such a run counts in n as `unclear`; and freeing VM disk. The cost of 6.2 GPU h (≈ 7.7 expected, ≤ 18.7) is accepted against the plan's 4–6 h for D1 and D2 together. D1's registered commit lands only after REG-20 arm A's hold has ended, and D2 is drafted meanwhile, not run first or instead.

### 7. Limits of this pass
- The 0.0006, 0.65 and 0.2536 figures rest on the writer's beliefs (`D1["prediction"]`). DERIVED here means computed from those beliefs, not from data.
- The anchors were checked against draft 2 at 56b21551. The code changes of DM2 and DM3 are specified, not written. Rule F round 3 sees them first (DM4).
- REG-20 arm A's operations decision is not yet committed. DM7 and DM10 (a) cite its draft 3 and its owner-proxy delta. If the approved text names the hold's end or the end headings differently, the approved text governs, and DM7 and DM10 follow it.
- Statements about the three preprints are BELIEF (open question A16).
