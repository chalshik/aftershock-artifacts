# Rule F review, round 1: D1 draft 1 (C2, session cap)

Reviewed: `docs/drafts/d1_draft1.md` at 5f9f442 (sha256 dd06a955…63c9, checked), and the three patches in `docs/drafts/d1_r1/`. They were applied to a scratch export of 5f9f442 (`git archive`). The patched files' sha256 equal the draft's three values. No run folder, sealed path, `docs/paper/` or state file was opened. No quantity was computed on a real run. Traces are scratch scripts on synthetic inputs (`scratchpad/traces/t_d1.py`), so they are not provenance.

**Verdict: NOT READY.** 11 required items (DG1–DG11), 6 optional (DG-O1–DG-O6).

## Reproduced
- `tests/test_d1.py`, `tests/test_withheld.py` and `tests/test_session_cap.py` on the scratch copy: 68 passed (103 s). Full suite without `test_check_docs.py`: 563 passed, 1 skipped (710 s; the writer reports 559, but their run was at 88593dc and this one is at 5f9f442).
- `d1.inputs()` from configs at 5f9f442 matches PROBE(docs/drafts/d1_r1/inputs_20261114.txt) line 4 byte for byte (DERIVED: `diff`).
- I wrote the five configs with `d1.write_configs` in the scratch copy, at placeholder caps 26/25/28/24/27. Loaded through the harness (`load_config`, `with_defaults`, `expand`), each is key for key equal to `d1.resolved` (diff `[]`). `_check_control` passes on all five resolved REG-19 control configs (DERIVED: scratch check, configs only).
- The matrix enumeration reproduces: supports 0.7405, mixed 0.2586, refutes 0.0006, admission_only 0.0003, cap_did_not_cut < 0.0001. `cp_upper` n = 5 gives 0.451, 0.657, 0.811, 0.924, 0.990, 1.000; 0 of 4 gives 0.527 and 0 of 3 gives 0.632. `first_order(26)` gives KV 0.547, and the cap reaches 0.80 at 33.99 and 0.95 at 38.72. (All DERIVED, scratch trace.)

## 1. A trace on which D1's verdict is wrong
**T1 (stuck, but nothing is backlogged).** Input: `tests/test_d1.py:make_run(reuse_after=0.93, q_after=0.0, kv_after=0.5)`. Before the burst every later turn reuses its whole previous prompt. After it, 93 % is reused, there is no server line and no wait at the cap, and KV is 0.5. `d1.label` gives `stuck_kv_free`, from reuse base 1.000, prev 0.930 and end 0.930, server q 0/0, cap queue mean 0/0 with slope 0, kv_end 0.5. `outcome(["stuck_kv_free"]*3 + ["recovered"]*2)` then gives `refutes`. The right label is neither stuck nor cut. Nothing is backlogged at the server or at the cap, so the system carries its load at a lower reuse. REG-20's readout calls this `partial`: it is cold only when also backlogged and full (FILE(analysis/k1.py:85-88)). `load.verdict` calls it `stuck` only if pf also falls by 0.10 (FILE(analysis/load.py:244)). **T1c:** reuse 0.0 with a growing cap queue (end mean 72 sessions, slope +0.023/s) gets the same label, `stuck_kv_free`. So the label cannot tell a stuck seed from an unbacklogged one. Under the cap the server's line is empty by construction (the draft, "The server's waiting line cannot fail"), and the stuck branch (FILE(analysis/d1.py:315-316) in the patch) reads no client-side backlog. → DG1.

**T3 (the seal lifts before the runs).** `withheld.lifted("[RESULT] D1")` matches any heading that starts `[RESULT] D1` followed by a non-digit (FILE(analysis/withheld.py:47)). The heading `## 2026-11-15 · [RESULT] D1 caps: 26, 25, 28, 24, 27` gives `sealed_by(<a capped folder>) = None`, and so do `[RESULT] D1: cap values` and `[RESULT] D1-caps …`. Three headings keep the seal: `[OPS] D1: caps computed`, `[RESULT] D10` and `[RESULT] D2`. The caps computation is a registered analysis, and rule E's template gives such output a `[RESULT]` (FILE(docs/process.md:29)). So the template's natural heading would unseal all five capped folders. → DG3.

**T4 (the cells "separate" on undecided seeds).** `outcome(["recovered"]*3 + ["unclear"]*2)` gives `supports` with k_stuck 0 of 5 and `cp_upper_stuck` 0.451. The draft's sentence would then say the cell lies below REG-19's 0.549. If the two `unclear` seeds may be stuck, the bound is `cp_upper(2,5)` = 0.811 and the cells do not separate. → DG4.

## 2. Strongest alternative explanation of the likely outcome (`supports`, P 0.74)
- **Admission control against a cut link: what the draft does separate.** In the warm branch, `recovered` needs the cap queue back to its baseline + 1. That needs sessions to finish at ≥ 0.25/s, about 2.0 req/s, which is above every cold rate on record: 1.703–1.800 per span (FILE(docs/decisions.md:16539)). So a capped `recovered` means the server left the cold state. It does not mean the waiting is hidden at the client. A cold server instead grows the cap queue by ≈ 0.25 − 1.75/8 = 0.031 sessions/s, ≈ 19 per 600 s (DERIVED). That half holds.
- **What it does not separate, and the strongest alternative.** A cap at the healthy peak takes away the population growth that *any* population-driven failure needs. The uncapped stuck runs held ≈ 30 running requests at KV 0.95, with 11–21 preemptions per span (FILE(docs/decisions.md:16540)). Pool pressure with preemption and recompute, without the prefix cache, would vanish under the cap too, and only D2 separates it. Further, a `never_cold` seed shows that the cap shrank the shock, not that it cut a *sustaining* loop, which is what C2 claims (FILE(docs/claims.md:23)). `load_reading`'s floor comparison does not help. With a binding cap and closed-loop turns the server is sent what it completes, so a cold span's server-side rate is its cold completion rate (1.70–1.80 on record), and `in_window` is expected whenever the cold state formed (DERIVED). → DG10.
- **The "KV link cut by construction" premise is wrong.** The gauge counts only blocks held by running requests, and cached free blocks are evicted from the free queue about least recently used first. Both are already answered from the pinned source: open questions S7 and S9 (FILE(docs/open-questions.md:25), FILE(docs/open-questions.md:34); SOURCE(vLLM 0.32.0 v1/core/block_pool.py:get_usage, get_new_blocks)). The draft's own arithmetic has a freed prefix surviving ≈ 8 s of cold churn against 5 s mean gaps at gauge 0.55. So the cap bounds the gauge, not eviction, and `stuck_kv_free` cannot "refute the KV link". → DG2.
- **Does the cap rule do what the draft says?** Mostly. `cap.max_sessions_in_service` runs from first `t_sent` to last `t_end`. A session with an unfinished turn counts as in service to ∞, burst rows are excluded, and ends come before starts at equal times (FILE(analysis/cap.py:18-37)). That matches the owner's words. The load generator's slot runs from admission to the chain's end, and turn 0 is sent at admission (FILE(harness/loadgen.py:149-155,161-165,176-178)), which is the same span. The rule's premise "on the control's own schedule it never binds" holds for the planned schedule only, since closed-loop latency jitter changes the realised count. The draft says so. Item 2's other clause, "judged on the server's hit rate and waiting line; waiting at the cap is reported apart" (FILE(docs/decisions.md:3949)), is not kept and is not stated as a departure. → DG5.
- **Drift.** The capped runs run on a later harness (≥ 5ee6e38) and days after REG-19 (a7bb77a). → DG-O2.

## 3. Can the run change a decision? (A1)
Yes. `supports` makes D2 the next C2 step and drafts a C2 status line. `refutes` stops loop-cut runs until the owner decides. `mixed` sends the choice between more seeds and "inconclusive" to the owner. By the draft's own beliefs the run is largely confirmatory (P(refutes) 0.0006). Its information is in the never_cold/in_window split (DG10) and in the stuck tail. The cost is ≈ 6.2 GPU h (7.7 expected, ≤ 19), above the plan's 4–6 h for D1 *and* D2 (FILE(docs/experiment-plan.md:422)). It is justified as the plan's step D only if DG10's split is reported. The approver should accept the overrun explicitly (notes item 10).

## 4–5. Code against text, and the rules (checked, no item unless named)
- Burst requests bypass the cap. Chains are built from non-burst rows only (FILE(harness/loadgen.py:214)). The cap is acquired inside the chain task, so the main loop never waits on it (FILE(harness/loadgen.py:149-155,222-229)). Burst rows go to a plain `send` (FILE(harness/loadgen.py:231-236)). `harness/trigger.py` only validates a burst (FILE(harness/trigger.py:21-34)), and `run.py` starts a trigger process only for `cache_wipe` (FILE(harness/run.py:181)). Fake test: FILE(tests/test_session_cap.py:173).
- The configs are new files only: `write_configs` raises `FileExistsError` (FILE(analysis/d1.py:208-209) in the patch; tested).
- The seal's pattern covers the five capped names and none of the other registrations' patterns (tested). Its lift text is too loose (DG3).
- Every threshold is fixed before data, but the text says "No threshold is new", which is false (DG11).
- Rule H: k of n with `cp_upper` is right, and `_cp_lower` = 1 − cp_upper(n − k, n) is the one-sided lower bound (DERIVED). The cross-cell sentence is not (DG4).
- Rule B: two BELIEFs are already answered (DG2). FILE(docs/decisions.md:3797) is the futility stop, while 0.549 is at :3796 (DG4). One fact cites a draft file (DG11).
- Stopping rule: weaker than E1's on lost runs, and missing E1's disclosure and its allowed reads (DG6, DG7).
- Withheld: the five folders, but run length shows each seed's outcome (DG6).
- Must exist before registration: ops scripts, the configs commit, the caps entry's heading, and an end-to-end test of the result path (DG3, DG8, DG9).

## Required items

### DG1 (code; rule): "stuck" needs the cap's backlog; add `partial`
Trace T1. Code: in `label`, the stuck branch needs `cq["end"]["mean"] > cq["base"]["mean"] + v["recovered_q_excess"]` and the queue not draining: not (slope < 0 and end mean ÷ −slope ≤ `drain_horizon_s`), with `unclear` when the slope is NaN. Otherwise the label is `partial`. Add `partial` to `LABELS`. Rewrite `test_cold_reuse_with_an_empty_server_line_is_stuck_not_recovered`, whose first assertion (no cap wait, so an empty cap queue) encodes the flaw. Add T1 and T1c as tests. Redo the enumeration with P(`partial`).
Anchor (Labels bullet):
```text
→ if end reuse ≤ baseline − 0.06: `stuck_kv_full` (end KV ≥ 0.80) or `stuck_kv_free` (end KV < 0.80; `unclear` if KV is missing) → `unclear`.
```
Replacement:
```text
→ if end reuse ≤ baseline − 0.06 and the cap's queue is backlogged (end mean > baseline mean + 1.0 session, and not draining: not (slope < 0 and end mean ÷ −slope ≤ 3600 s); `unclear` if the slope is missing): `stuck_kv_full` (end KV ≥ 0.80) or `stuck_kv_free` (end KV < 0.80; `unclear` if KV is missing) → if end reuse ≤ baseline − 0.06 without that backlog: `partial` (no line at the server or at the cap: the system carries its load at a lower reuse) → `unclear`. A cold reuse alone is never `stuck`: under the cap the server's line is empty by construction, so a stuck state's backlog is the cap's queue (REG-20's readout also requires a backlog, FILE(analysis/k1.py:86)). A cold server cannot empty that queue: at REG-19's cold rates (1.703–1.800 req/s per span, FILE(docs/decisions.md:16539)) it grows by ≈ 0.031 sessions/s (DERIVED: 0.25 − 1.75 ÷ 8).
```
Anchor (matrix bullet):
```text
`bad_baseline`, `unclear` and `rewarming` count in n, neither cut nor stuck.
```
Replacement:
```text
`bad_baseline`, `unclear`, `rewarming` and `partial` count in n, neither cut nor stuck.
```

### DG2 (wording; rule B): the cap bounds the gauge, not eviction
Anchor:
```text
So under the expected caps **the KV link is cut by construction, and D1 tests whether the cache comes back once the pool is not full.** That can still fail: a seed that stays cold with the pool below 0.80 is `stuck_kv_free`, which refutes the KV link as what sustains the stuck state.
```
Replacement:
```text
So under the expected caps **the running batch is held near the healthy level and the pool gauge below condition 4's 0.80 by construction; eviction is not cut by construction.** The gauge counts only blocks held by running requests, and cached free blocks stay in the free queue and are evicted about least recently used first (open questions S7 and S9: FILE(docs/open-questions.md:25), FILE(docs/open-questions.md:34); SOURCE(vLLM 0.32.0 v1/core/block_pool.py:get_usage, get_new_blocks)); at a gauge of 0.55 a freed prefix survives ≈ 8 s of cold churn against 5 s mean gaps ("Prediction"), so idle prefixes can still be evicted. D1 tests whether the cache comes back when the batch and the gauge are held down. That can still fail: a seed that stays cold and backlogged with the gauge below 0.80 is `stuck_kv_free`, which says the stuck state needs neither a big running batch nor a gauge at 0.80; whether idle prefixes are still evicted is read from `c2.eviction_readout`.
```
Anchor (`refutes`):
```text
"stuck under the session cap with the pool below 0.80 in k of n seeds: the stuck state does not need a full pool, so the KV link of C2's loop is not what sustains it at this cell." Alternatives (rule A2): (a) as stated; (b) the KV gauge counts only blocks of running requests, so prefixes can be evicted by churn in a pool that reads below 0.80; separated by
```
Replacement:
```text
"stuck under the session cap, with the running batch held down and the pool gauge below 0.80, in k of n seeds: at this cell the stuck state does not need the big running batch and full pool of C2's stated loop; whether cached prefixes were still evicted before their session's next turn is given by c2.eviction_readout." Alternatives (rule A2): (a) C2's loop as stated is not what sustains it; (b) the loop runs through eviction from the free queue, which the gauge does not count (a fact of the pinned source, open question S7, not a hypothesis); separated by
```
Anchor (Prediction):
```text
BELIEF that vLLM 0.32.0 reuses free blocks least-recently-used first and that the gauge counts only blocks of running requests: open question, `d1_draft1_notes.md`
```
Replacement:
```text
the free-queue order and what the gauge counts are answered from the pinned source, open questions S9 and S7 (FILE(docs/open-questions.md:34), FILE(docs/open-questions.md:25)); the survival estimate itself is BELIEF as a model
```

### DG3 (code; rule E): the seal must not lift on the caps entry
Trace T3. Code: change the row in `withheld.patch` to `("D1", "*_burst_l1pl350cl_r2.0_w3000_s1[5-9]_cap", "[RESULT] D1 (C2, session cap)")`. Test that the caps entry's registered heading and `[RESULT] D1 caps …` do not lift it, and that `## <date> · [RESULT] D1 (C2, session cap): …` does. I checked this lift text on the scratch copy: False, False, True.
Anchor:
```text
seal "D1", lifted by a heading `## <date> · [RESULT] D1`;
```
Replacement:
```text
seal "D1", lifted only by a heading that begins `## <date> · [RESULT] D1 (C2, session cap)` (the lift text is that whole prefix, so another heading that begins `[RESULT] D1`, such as the caps entry's, lifts nothing; FILE(tests/test_d1.py), a test of both);
```
Anchor:
```text
committed alone with an [OPS] entry quoting it.
```
Replacement:
```text
committed alone with an entry headed `## <date> · [RESULT] D1 caps (registered computation on REG-19's five controls)`, which quotes it with RUN(<control id>, d1.cap_values) for each seed (rule E: a registered analysis's output); that heading does not lift D1's seal (test).
```

### DG4 (rule H; stricter rule): bound the stuck share on the seeds that are not cut
Trace T4. Code: `outcome` adds `cp_upper_not_cut` = `cp_upper(n − k_cut, n)`.
Anchor:
```text
**With 0 of 5 stuck, the upper bound 0.451 lies below REG-19's lower bound 0.549 on the same seeds** (FILE(docs/decisions.md:16527), FILE(docs/decisions.md:3797)), so the two cells separate; with 0 of 4 the bound is 0.527 (separates), with 0 of 3 it is 0.632 (does not; the [RESULT] then says the cells overlap).
```
Replacement:
```text
The share stuck is bounded twice: on k_stuck of n, and on n − k_cut of n, which counts every seed that is not cut (`bad_baseline`, `unclear`, `rewarming`, `partial`, `server_only`) as possibly stuck. The [RESULT] may say that the capped cell lies below REG-19's lower bound 0.549 on the same seeds (FILE(docs/decisions.md:16527), FILE(docs/decisions.md:3796)) only when the second bound does: n − k_cut = 0 of 5 gives 0.451, 0 of 4 gives 0.527, 1 of 5 gives 0.657 and does not, 0 of 3 gives 0.632 and does not (DERIVED, `cp_upper`). This compares two one-sided bounds of cells that share seeds and schedules; it is a readout, not a test at a stated level (rule H), and the paired readout is McNemar's.
```

### DG5 (rule): state the departures from item 2 of 2026-11-12
Insert before the line that begins:
```text
- **The server's waiting line cannot fail under the cap, and the pool probably cannot fill.**
```
Text to insert:
```text
- **Departures from the cap rule of record, for the approver.** (1) Item 2 says "The capped arm is judged on the server's hit rate and waiting line; waiting at the cap is reported apart" (FILE(docs/decisions.md:3949)), and the plan expects "`recovered`, with the waiting moved to the load generator" (FILE(docs/experiment-plan.md:423)). D1 makes the cap's queue part of the label: a warm server whose cap queue does not clear is `server_only`, not cut, and a cold reuse without a cap backlog is `partial`, not stuck. Reason: under the cap the server's line is empty by construction, so it cannot tell a cleared state from a moved one. The owner's reading is kept as `k_cut_server_side` (readout). (2) "Hit rate" is read as the prefix reuse of later turns (REG-20's readout, FILE(analysis/k1.py:8)), with the hit counter's thresholds. The approving entry accepts both departures, or restores item 2's reading, before the caps are computed.
```

### DG6 (reporting duty; stricter rule): run length leaks each seed's outcome
The load generator waits for every chain until the last planned time plus 300 s (FILE(harness/loadgen.py:209,237-239)). A recovered capped run ends about one session length (55–58 s) after 4080 s. A stuck one keeps sessions at the cap until the deadline. Launch gaps therefore show D1's outcome bit per seed.
Anchor:
```text
No interim look at any run's records, verdict or label before the result; no futility stop (none of the outcomes needs one, and an interim look would need its own one-bit rule).
```
Replacement:
```text
No interim look at any run's records, verdict or label before the result; no futility stop (none of the outcomes needs one, and an interim look would need its own one-bit rule). Disclosed: the allowed reads still show each seed's outcome bit. The load generator waits for every session until the last planned time plus the 300 s drain (FILE(harness/loadgen.py:209,237-239)); a capped run whose server recovered ends about one healthy session length (≈ 55–58 s) after 4080 s, while one that stays stuck holds sessions at the cap to the deadline, up to ≈ 240 s longer (DERIVED). Run ids carry their launch time, so the gaps between consecutive run ids, and a launch's LAUNCHED and ENDED times, show which seeds recovered (E1 discloses the same for its sweep, FILE(docs/decisions.md:17069)). No step of the stopping rule uses this, and the [RESULT] says so. No rule, label, threshold or readout of D1 changes after the first capped launch; a [CORR] after that point is reported in the [RESULT] beside the bits visible when it was written. **Reads allowed while diagnosing a stop** (E1's, FILE(docs/decisions.md:17074)): `tmux has-session`, folder names, `valid` and `failed`, and in a launch log only the lines holding `run_id` or `[run] checks`.
```

### DG7 (stricter rule): lost runs need a decision; E1's other stops
Anchor:
```text
A launch that leaves no `checks.json` (a lost run) counts as an attempt and stops D1 until an [OPS] entry records its cause; a lost run is never opened.
```
Replacement:
```text
A launch that leaves no `checks.json` (a lost run) counts as an attempt and stops D1 until a new decision (a [DECISION] entry, the owner's or the delegate's), as in E1 (FILE(docs/decisions.md:17072)) and as REG-19's lost runs were handled (FILE(docs/decisions.md:4284), FILE(docs/decisions.md:4383)); an [OPS] entry records the boot id before and after; a lost run is never opened. A `gpu_steady` failure is named "heat, SM-clock steadiness or sample coverage" until its detail is read, and each kind gets the heat rule (FILE(docs/decisions.md:17035)). A folder that no launch log of D1's scripts names, a named run missing from the VM, or a run made at a commit other than the one registered for D1's launches stops D1 for the owner.
```

### DG8 (rule; must exist before registration): the tree D1 runs, the start gate, the order
Anchor:
```text
its place relative to E1, REG-20 arm A and REG-24 is set by RUNBOOK §5 at approval (open point). The launch scripts are a separate ops draft, modelled on E1's (`docs/probe/20261113_e1/ops/`), not part of this draft.
```
Replacement:
```text
its place relative to E1, REG-20 arm A and REG-24 is fixed in the approving entry (RUNBOOK §5), not left open. **No capped run is launched before** (1) the caps entry and the configs entry are committed, (2) D1's operations decision, headed `## <date> · [DECISION] (owner|delegate) D1 starts`, is committed after its own rule F review of the launch scripts (modelled on E1's, `docs/probe/20261113_e1/ops/`), and (3) the item ahead of D1 has its end entry. **The tree D1 runs:** the registered commit cannot hold the five configs, which are written after the caps are computed; the VM runs the configs entry's commit, and that entry quotes `git diff --name-only <registered commit> <configs commit>`, which may list only the five `configs/burst_l1pl350cl_r2.0_w3000_s1{5..19}_cap.yaml`, `docs/probe/d1/…`, `docs/decisions.md`, `docs/status.md` and `docs/context-pack.md`; the launch scripts refuse any other tree.
```

### DG9 (code; test): the result path is not tested end to end
`row`, `table`, `capped_run`, `control_run` and `cap_values` never run in a test. The fake end-to-end test calls only `label`, `slots`, `waits`, `spans` and `verdict` (FILE(tests/test_d1.py:299-323) in the patch). `row` also calls `c2.levels`, `c2.eviction_readout` (which reads `metrics.jsonl`), `gate.shock_size`, `gate.reg19_baseline_pair` and `reg12_only`, and none of them is exercised on a capped run. REG-20 has a precedent: a pattern bug "would have made every computation return `too_few`", and the end-to-end tests on fake folders were added after it (FILE(docs/decisions.md:4133)).
Anchor:
```text
on `tests/fake_vllm.py`; the seal row in `analysis/withheld.py`.
```
Replacement:
```text
on `tests/fake_vllm.py`; the seal row in `analysis/withheld.py`. A further test builds fake run folders under a monkeypatched `RUNS` (per seed a control, an uncapped burst run and a capped run; one seed with an invalid capped attempt before its valid one, one seed with only invalid attempts) and runs `cap_values()` and `table()` end to end: the invalid attempt is skipped, the spent seed is in `not_run`, and every readout of `row` returns.
```

### DG10 (reporting duty): `supports` must split onset from sustainment and name the population alternative
Anchor:
```text
Alternatives to state with it (rule A2): (a) the loop was cut (C2), separated from (b) a smaller effective shock (the cap held back session turns during the burst) by `load_reading` (`never_cold` against `in_window`) and `gate.shock_size` in both arms;
```
Replacement:
```text
The status line gives k_cut split by `load_reading`: seeds `never_cold` (the cap kept the cold state from forming) and seeds `in_window` or `below_floor` (it formed and then cleared under the cap). Only the second kind bears on C2's "sustaining" loop; if there are none, the line ends "the cap prevented the onset; whether it breaks an established stuck state is not tested by D1". Alternatives to state with it (rule A2): (a) the loop was cut (C2), separated from (b) a smaller effective shock (the cap held back session turns during the burst) by that split and by `gate.shock_size` in both arms; (d) a failure driven by the population through pool pressure, with or without the prefix cache (the uncapped stuck runs held ≈ 30 running requests at KV 0.95 with 11–21 preemptions per span, FILE(docs/decisions.md:16540)), which a cap removes as well: D1 cannot separate it from C2, D2 can; (e) `in_window` is no evidence against admission relief: with a binding cap and closed-loop turns the server is sent what it completes, so a cold span's server-side rate is its cold completion rate, 1.703–1.800 on record (FILE(docs/decisions.md:16539)), above 1.681, and `in_window` is expected whenever the cold state formed (DERIVED);
```

### DG11 (wording; rule B): new uses of thresholds, and two citations
Anchor:
```text
Condition 4's `min_kv` 0.80 (FILE(analysis/c2.py:30)). No threshold is new.
```
Replacement:
```text
Condition 4's `min_kv` 0.80 (FILE(analysis/c2.py:30)). New, and all fixed here before any capped run (rule A5): `max_idle_share` 0.05 (`harness_fault`); `recovered_q_excess` 1.0 and `drain_horizon_s` 3600 applied to the cap's queue, whose unit is sessions (up to 8 turns each), not requests; and the hit counter's 0.06 thresholds applied to reuse, where `hit_climb` was calibrated on adjacent 600 s hit windows at a healthy λ = 3 (FILE(configs/stage2_cap_base.yaml:9)), not on reuse.
```
Anchor:
```text
FILE(docs/drafts/e1_draft7.md:18), FILE(docs/decisions.md:4209)
```
Replacement:
```text
FILE(docs/decisions.md:17031), FILE(docs/decisions.md:4209)
```
(:3797 is corrected to :3796 by DG4's replacement.)

## Optional items
- **DG-O1.** A one-bit cap-path step after seed 15 (`harness_fault` only, printed as REG-19's `reg19_step` printed `continue`). A leaked slot would then cost one run, not five. It needs a narrow seal exception (notes item 13).
- **DG-O2.** Drift: list REG-20's drift run (`*_burst_l1pl350cl_r2.0_w3000_s15_drift`, closed loop on the new harness) as a readout once REG-20's [RESULT] lifts its seal, or interleave one uncapped seed-15 run (≈ 1.25 GPU h, single seed) (notes item 7).
- **DG-O3.** Predict `manipulation` as a number, since a failure stops D1. The burst alone offers ≈ 2.4 × 3072 ≈ 7,370 prompt tokens/s against a cold uncached rate of ≈ 5,300 tokens/s (REG-22 batch 2, FILE(docs/decisions.md:16752)), so the line should build and the pool fill under any cap (DERIVED arithmetic; BELIEF as to the scheduler).
- **DG-O4.** For two valid runs of one seed, follow E1 (list both; the earliest counts) rather than raise, so that the table is not lost.
- **DG-O5.** P(any wait before 900 s) ≈ 0.15 is set for all seeds. Seeds 18 and 19 plan baselines of 2.217 and 2.207, and seed 18's control peaked at 385 s (FILE(docs/decisions.md:3785)), so give per-seed values.
- **DG-O6.** Once D1's seal lifts, broad globs pick up the capped folders: `gate.SURGE["pattern"]` `*_l1pl350cl_*` (FILE(analysis/gate.py:1345)) and FILE(analysis/k3.py:381). State whether any published table they feed changes.

## The writer's notes, read after the above
I agree with items 2 (= DG5), 3 (= DG11), 7 (= DG-O2), 9 and 12 (= DG8), 10 (A1 above) and 13 (= DG-O1). Item 1's fallback (`unclear` if `harness_fault` is not approved) is sound. I disagree with item 4: the cap does not cut the KV link by construction (DG2). Assumption 4 is not unverified; open questions S7 and S9 answer it from the pinned source (DG2). Items 5, 6, 8 and 14 are acceptable as drafted.
