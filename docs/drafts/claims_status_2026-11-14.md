# Draft: restated status lines for `docs/claims.md` (C1, C2, K1–K5), 2026-11-14

**For the owner's review. Not in force.** Nothing in `docs/claims.md` changes because of this file. If adopted, each claim's line is its own `docs/claims.md` edit and needs its own reviewed decision (FILE(docs/status.md:40); REG-19's [RESULT], FILE(docs/decisions.md:16565); REG-22's [REG], FILE(docs/decisions.md:4630); REG-21's [REG], FILE(docs/decisions.md:9793)). Written at HEAD `9582866`. This is a draft (rule C, "Alone: draft docs"). It is not evidence, and no line of it may be cited as evidence.

**Inputs read, in order:** `CLAUDE.md`; `docs/claims.md`; `docs/status.md`; `PROTOCOL.md`; in `docs/decisions.md`, the [RESULT] entries of REG-19 (16517), REG-22 batch 2 (16571), REG-21 batch 2 (16798), REG-22 batch 1 (16322), REG-21 batch 1 (16421), REG-13 (2635), REG-14 (2835), REG-15 (3085), REG-16 (3369), REG-17 (3538) and REG-18 (3735), plus the heads of REG-10, REG-11 and REG-12 (2155, 2307, 2462); also the 2026-11-10 [CORR] on surges (3417), REG-17's rule G paragraph (3457), REG-20's [REG] (4045) and its approval (4166), REG-22's [REG] ceilings (4620–4737), REG-21's [REG] head and ceilings (9731–9801), E1's [REG] seal paragraph (17020–17056), E1's end [OPS] (19459) and the owner's end-of-autonomy [DECISION] (19488); `docs/probe/reg20/gate_20261113T230307Z.txt`; rows A12–A20 of `docs/open-questions.md`; items −18, −17, −16 and −13 of `agent/FOR_AUTHOR.md`; the heads of `docs/drafts/reg24_confirm_draft3.md`, `docs/drafts/d1_draft2.md`, `docs/drafts/reg23_k5_draft5.md` and `docs/drafts/e0_e1_draft3.md`; the `FILE` check of `tools/check_docs.py`.

**Not opened:** `runs/`, the backups folder, `docs/paper/`, any `docs/probe/**/state/` folder, `docs/probe/20261111_reg19/ops/RESUME.md`, `_to_delete/`. Nothing here is computed from a run. Each number is quoted from a committed [RESULT], probe or status text, and is tagged. A `DERIVED` tag marks arithmetic on quoted numbers only. **E1's floor is sealed and not computed. REG-20 arm A and D1 have not run.** Nothing below says or implies an outcome for any of them.

**Words.** "Supports" appears only where a registered test's outcome is named `supports`. REG-21 and REG-22 are called "readings", never tests, as their registrations require (FILE(docs/decisions.md:4620), FILE(docs/decisions.md:9734)). No text below says that condition 4 is met, holds or is passed (FILE(docs/decisions.md:4637)), or uses any word that REG-22's line c forbids for the loop (FILE(docs/decisions.md:4711)).

---

## 0. Where to paste: a choice for the owner (it decides whether old citations keep pointing at the right text)

- **Observed:** `docs/decisions.md` cites lines of `docs/claims.md` by number: `:25` ×3, `:26` ×3, `:31` ×5, `:45` ×5, `:56` ×6, `:63` ×2, `:65` ×1, `:66` ×1, `:82` ×2. `docs/status.md` cites `:31` and `:45` once each (DERIVED: `grep -oE 'FILE\(docs/claims\.md:[0-9,-]+\)'` over `docs/decisions.md`, `docs/status.md`, `PROTOCOL.md`, `docs/definitions.md`, `docs/open-questions.md` and `docs/model.md`). REG-21's and REG-22's registered sentences, quoted below, cite `FILE(docs/claims.md:31)` and `FILE(docs/claims.md:45)` themselves.
- `tools/check_docs.py` checks only that a cited file and line exist (FILE(tools/check_docs.py:11)). An edit that inserts lines therefore passes the check while the old citations point at different text. Old decisions entries cannot be fixed (CLAUDE.md C, "Never: edit an old decisions entry").
- **Option A (in place):** replace each dated status line with the text below. Every cited line after the first edit moves.
- **Option B (recommended):** add a new section, `# Status lines of 2026-11-14`, at the end of `docs/claims.md`, holding the seven texts below in order. Then append, on the same line as each old status line (`:16`, `:28`, `:31`, `:45`, `:60`, `:67`, `:77`, `:83`), the words ` **Superseded on 2026-11-14: see "Status lines of 2026-11-14" at the end of this file.**` No line number moves. The texts below are written so that either option works. Under option A, the `FILE(docs/claims.md:31)` and `:45` tags inside the quoted registered sentences would need retargeting; under option B they stay true.

---

## C1. The symptom

### 1. Current status line

FILE(docs/claims.md:16) to FILE(docs/claims.md:20), verbatim:

> - **Status (2026-11-04):** not supported. Per cell, all stuck 0 of 3, one-sided 95 % upper bound 0.63 each (`analysis/stats.py`, `cp_upper`):
>   - default pool, 20 s gaps: wipe λ = 3, wipe λ = 3.5, burst λ = 3, burst λ = 3.5; ramp at 300 s and 600 s: no gap. Negative by the PROTOCOL rule.
>   - 72,480-token pool, 20 s gaps: wipe λ = 3, burst λ = 3. **No ramp was run, so this setup is not negative by the PROTOCOL rule**; it is "no stuck run".
>   - default pool, 5 s gaps: wipe and burst at λ = 3.5 and 4.5. **No ramp was run**; "no stuck run".
>   - Single-seed controls in every cell. Whether the test loads were inside a real danger zone is in question (`docs/model.md` M2, M4); until the feasibility gate is run, a negative here may say only that these loads recover.

And the shared paragraph, FILE(docs/claims.md:31), verbatim:

> The two status lines above are dated 2026-11-04 and describe the open-loop setups. Later results are in `docs/status.md` and decisions.md: with closed-loop turns at setup L1 (350 W), single-seed pairs stuck with a recovered control at λ = 2.2 and 2.0 (decisions.md 2026-11-10 [RESULT] REG-14, REG-17), and the registered matrix at λ = 2.0 gave 1 of 4 (decisions.md 2026-11-11 [RESULT] REG-18). C1 is still not supported by its own test; REG-19 is under way. **C2 is no longer "untestable":** stuck runs exist, but condition 4 has not been computed on them, no loop figure exists, and neither control that cuts a link has been run, so C2 is untested.

### 2. Proposed replacement (paste-ready)

```markdown
- **Status (2026-11-14):** not supported by its own test (all six conditions of PROTOCOL §3 at one load, FILE(PROTOCOL.md:32)). At one load of one setup, the matrix condition holds under a test written after the earlier matrix. Conditions 5 and 6 are untested at that load, and condition 4's order clause is not judged.
  - **Setup L1, 350 W, closed-loop turns, λ = 2.0 (P0's replication).** REG-19's registered matrix on new seeds 15–19 gave `supports`, k_clear 5 of 5, one-sided 95 % Clopper–Pearson bounds 0.549 to 1.000 (RUN(REG-19's ten runs, gate.reg19_table); FILE(docs/decisions.md:16527)). The registered sentence: "At λ = 2.0, after the burst the server stayed stuck, cold and below its load through a 3000 s watch without the line emptying, while the same schedule without the burst stayed healthy, in 5 of 5 new seeds (15–19), under REG-19's whole-window test, written after REG-18's matrix (1 of 4 under the per-span test). Under REG-18's per-span test on the same runs: 3 of 5." (FILE(docs/decisions.md:16546)). The 3 of 5 under the per-span test is a readout, and the [RESULT] gives no bound for it (FILE(docs/decisions.md:16527)). Each seed has a single control (rule H). Seed 17's request counts were seen before seeds 18 and 19 ran; `supports` does not need seed 17's pass (FILE(docs/decisions.md:16559), FILE(docs/decisions.md:16563)).
  - **Earlier at the same cell:** REG-17 gave `pass_clear` on one seed (1 of 1, one-sided 95 % lower bound 0.05; FILE(docs/decisions.md:3563)). REG-18's registered matrix gave `some`: 1 of 4 on seeds 4, 3, 5, 6, stopped by its futility rule, with no bound, as registered (RUN(REG-18's eight runs, gate.reg18_table); FILE(docs/decisions.md:3737)). REG-19's test does not re-judge REG-18's seeds (FILE(docs/decisions.md:16569)). On C1's verdict pair alone (burst `stuck`, control `recovered`; `k_c1`, a readout, never decisive), REG-18 had 3 of 4 (FILE(docs/decisions.md:3750)) and REG-19 had 5 of 5 (FILE(docs/decisions.md:16527)).
  - **By condition at λ = 2.0** (PROTOCOL §3, FILE(PROTOCOL.md:33) to FILE(PROTOCOL.md:38)):
    1. The trigger ended and the load stayed unchanged, by design. The burst's own requests had left by 1207 to 1228 s in REG-19's burst runs (RUN(REG-19's five burst runs, c2.condition4); FILE(docs/decisions.md:16793)).
    2. The control was `recovered` in 5 of 5, each a single same-seed control (FILE(docs/decisions.md:16542)).
    3. Most seeds stuck: holds under REG-19's test (above).
    4. Not judged. REG-22 read its registered levels and the four links, retrospectively (C2's status). The order clause waits for the owner (FILE(agent/FOR_AUTHOR.md:23)). Until the owner decides, no run in this study has condition 4 met (FILE(docs/status.md:128)).
    5. Persistence over a 4500 s watch: untested at λ = 2.0. At λ = 2.2, REG-15's one run stayed `stuck` through a 4500 s watch with no recovered window (RUN(20261110-085730_confirm_l1pl350cl_r2.2_s12, gate.reg15_table); FILE(docs/decisions.md:3088)). At that load a no-burst control also went cold by itself (RUN(20261110-122001_stage2_control_l1pl350cl_r2.2_long_s14, gate.reg16_table); FILE(docs/decisions.md:3408)), so REG-15's run counts for no load at which conditions 2 and 3 hold.
    6. Two states at one load: untested at any load. REG-15's 1800 s drop did not empty the line (`drop_inconclusive`; FILE(docs/decisions.md:3089)).
  - **Feasibility (rule G) at λ = 2.0:** its pass condition was restated for λ = 2.0 after its inputs were seen (FILE(docs/decisions.md:3457)). REG-17's one seed met it (`pass_clear`, FILE(docs/decisions.md:3551)).
  - Nothing is said about other loads (FILE(docs/decisions.md:16546)).
  - **Open-loop setups (the status of 2026-11-04, which still stands for them):** per cell, all stuck 0 of 3, one-sided 95 % upper bound 0.63 each (`analysis/stats.py`, `cp_upper`): default pool with 20 s gaps (wipe and burst at λ = 3 and 3.5; ramp at 300 s and 600 s with no gap; negative by the PROTOCOL rule); the 72,480-token pool with 20 s gaps (wipe and burst at λ = 3; no ramp, so "no stuck run"); the default pool with 5 s gaps (wipe and burst at λ = 3.5 and 4.5; no ramp, so "no stuck run"). Every cell had a single-seed control. Whether these cells could get stuck at all is in question (`docs/model.md` M2, M4; FILE(docs/claims.md:46)).
```

### 3. What is still missing, and what tests it

- **Conditions 5 and 6 at λ = 2.0 → REG-24** (draft 3; seed 43; design B: a no-burst control, then the burst run on the same schedule, each with a 4500 s watch, then λ = 1 for 9000 s, then back to λ = 2.0 for 1500 s; ≈ 9.1 GPU h; FILE(docs/drafts/reg24_confirm_draft3.md:20), FILE(docs/status.md:28)). It is blocked on the owner's ruling on the drop length: (a) 9000 s, (b) 1800 s or (c) other (FILE(docs/status.md:36)). The ruling is the owner's alone, because a drop other than 1800 s departs from PROTOCOL §3 item 6 (FILE(PROTOCOL.md:38); FILE(docs/drafts/reg24_confirm_draft3.md:24)). After the ruling come rule F round 3, the owner-proxy and REG-24's ops scripts.
- **Condition 4's order clause → the owner's choice** among (a) accept `sustain` for burst runs, (b) have the literal order judged, (c) drop the clause for bursts (FILE(agent/FOR_AUTHOR.md:23)). A blind order test on REG-19's runs is no longer possible, because REG-22's batch 2 printed their onsets (FILE(docs/decisions.md:16749)). Choice (b) is still open for new runs that are registered before they run (FILE(agent/FOR_AUTHOR.md:18)).
- C1 can be judged on all six conditions at λ = 2.0 only after both of these. Nothing pending tests C1 at another load. REG-20 arm A, D1, D2, E0/E2 and REG-23 do not test C1.

### 4. Alternative explanations (rule A2) and what separates them

1. **A long drain, or a plain overload of the cold server on these schedules, not a second stable state** (REG-19's alternative 1). Against a drain within 3000 s: no seed's line emptied, the waiting line grew over the window (ratio 1.94 to 2.51, end slope +0.019 to +0.071 /s), and so did the total line (FILE(docs/decisions.md:16555)). Against warm-side overload: the same-seed controls held the waiting share at or below 0.010 in every span (FILE(docs/decisions.md:16542)). **What separates them:** 3000 s cannot tell a state that holds only while the load stays at 2.0 from one that also outlasts a lower load. Only conditions 5 and 6 (REG-24) can.
2. **A test and a cell chosen after seeing earlier runs.** The load λ = 2.0 was chosen after REG-16 and REG-17, and REG-19's whole-window test was written after REG-18's 1 of 4 (FILE(docs/decisions.md:16556)). Against it: the seeds were new, and REG-18's own per-span rule gives 3 of 5 on the same runs. **What separates them:** a further matrix on new seeds under a test fixed before it. Whether REG-18's 1 of 4 and these 3 of 5 differ by seed or by chance cannot be told from these runs (FILE(docs/decisions.md:16556)).
3. **A ceiling set by the clients in closed loop** (REG-19's alternative 4). Against it: the line was not flat and grew over the window in every seed, and 375 to 607 turns were still unreleased at the end (FILE(docs/decisions.md:16558)). An open-loop arm of the same seeds (REG-20 arm A) would show the server's side without that ceiling. It bears on K1, not on C1's conditions.
4. **Run order, heat or lost runs.** `order_flag` was False in all five seeds. Alternating the order would separate this further, and the owner declined it (FILE(docs/decisions.md:16557)). Seed 18's control was lost twice to power-offs. That selects on power events, not on outcomes, unless the power-offs depend on GPU load (open question A18; FILE(docs/decisions.md:16560)).
5. **Limits, not alternatives:** one load, closed-loop turns, L1, 350 W, one GPU, one control per seed (FILE(docs/decisions.md:16561)). λ = 2.0 is 0.83 of the closed-loop warm capacity (≈ 2.4, one seed, REG-13) and 0.67 of the open-loop one (3.0) (FILE(docs/decisions.md:4047)). By the [CORR] of 2026-11-10, the 2.4 records whether a schedule held a surge, not a capacity sustained over time (FILE(docs/decisions.md:3424)).

---

## C2. The cause

### 1. Current status line

FILE(docs/claims.md:28), verbatim:

> - **Status (2026-11-04):** untestable so far: there is no stuck run. Related evidence, not a test of C2: during bursts KV reached 1.00, and in the first 60 s after each burst the counter hit rate was 0.11–0.35 (a counter that includes the burst requests, which never hit, so it overstates how cold the sessions' cache was; decisions.md 2026-11-05 [CORR]), and every run then recovered within about 5 minutes (decisions.md 2026-11-02, 2026-11-03). The caching-off control has no defined form yet, and the protected-prefixes control (S4) was not investigated; it is replaced by the session-cap arm (2026-11-12).

and its part of FILE(docs/claims.md:31) (quoted under C1): "**C2 is no longer "untestable":** stuck runs exist, but condition 4 has not been computed on them, no loop figure exists, and neither control that cuts a link has been run, so C2 is untested."

### 2. Proposed replacement (paste-ready)

```markdown
- **Status (2026-11-14):** not met. The part of its test that can tell a loop from an overload, the two controls that cut a link, has not run. The order of the loop's signals is not judged, and no loop figure exists. What has been read, retrospectively, at one load:
  - **Setup L1, 350 W, closed-loop turns, λ = 2.0, by REG-22's line a, each batch apart, never pooled:**
    - **Batch 2** (REG-19's seeds 15–19; "retrospective (by design)", with decisions.md 2026-11-13 [CORR] "Two reads of REG-19's seed 17" cited; the run-time lines and the looks are disclosed in the [REG]): "condition 4's registered levels held at the end of the watch, and all four links were present in every 300 s span after the burst's requests had left, in 5 of 5 stuck runs at λ = 2.0 (one-sided 95 % Clopper–Pearson bounds 0.549 to 1.000); the order clause is not judged and no loop figure exists; an overload gives the same picture; the loop-cut controls are not run." All 5 have a same-seed control that is `recovered` and holds the four links in no judged span, against its own baseline and against the burst run's. `not_sustained` 0, `not_memory_limited` 0, `undefined` 0. (RUN(REG-19's five burst runs and their controls, c2.reg22_table); PROBE(docs/probe/reg22/batch2_20261113T231746Z.txt); FILE(docs/decisions.md:16740).)
    - **Batch 1** (the burst runs of REG-17 and REG-18 at λ = 2.0, seeds 2, 4, 3, 6; "thresholds fixed after these runs were reported"): the same sentence with 4 of 4 stuck runs (bounds 0.473 to 1.000). All 4 have a same-seed control that is `recovered` and holds the four links in no judged span, against either baseline. `not_sustained` 0, `not_memory_limited` 0, `undefined` 0. (RUN(REG-17's and REG-18's burst runs at λ = 2.0 and their controls, c2.reg22_table); PROBE(docs/probe/reg22/batch1_20261113T224144Z.txt); FILE(docs/decisions.md:16344).)
    - Both batches meet line a at λ = 2.0, so they do not disagree. Batch 1 had 16 judged spans and batch 2 had 45, and none failed a link (FILE(docs/decisions.md:16742) to FILE(docs/decisions.md:16746)). Neither batch is claimed alone.
  - **λ = 2.4** (batch 1, 5 of 5, bounds 0.549 to 1.000) is given only "at the closed-loop warm capacity; three of five controls did not stay healthy (REG-12)". It is the overload comparison and is not cited as support (FILE(docs/decisions.md:16345)). **λ = 2.2:** two stuck runs, reported one by one, with no sentence about that load (FILE(docs/decisions.md:16338)).
  - Until the owner rules on the order clause, no text says that condition 4 is met, holds or is passed for any run or load (FILE(docs/decisions.md:4637)).
  - **The controls that cut a link:** the session-cap arm (D1) is drafted and not registered. Caching off at matched utilization (D2) is not drafted (FILE(docs/status.md:19), FILE(docs/status.md:31)).
  - **Open-loop setups (the status of 2026-11-04, which still stands for them):** no stuck run. During bursts KV reached 1.00, and every run recovered within about 5 minutes (decisions.md 2026-11-02, 2026-11-03; the hit-rate caveat of decisions.md 2026-11-05 [CORR]).
```

### 3. What is still missing, and what tests it

- **The session-cap arm → D1** (draft 2): REG-19's burst runs at λ = 2.0 on seeds 15–19, repeated with the session cap set to each seed's control peak. Its decision rule is "≥ 3 of 5 cut with none stuck"; ≈ 6.2 GPU h (FILE(docs/drafts/d1_draft2.md:9)). Still to do (FILE(docs/status.md:19) to FILE(docs/status.md:27)):
  - draft 3 (DJ1–DJ3, R1–R21, DM2, DM3);
  - rule F round 3 on the code of DM2 and DM3;
  - the caps computation, five configs, and ops scripts with their reviews.
  Its registered commit lands only after REG-20 arm A's hold ends (DM7). Two open points belong to the owner. First, whether a `harness_fault` run may leave n (FILE(docs/status.md:39)). Second, whether a `cap_did_not_cut` outcome refutes C2, as claims.md's wording reads ("stuck runs that stay stuck under the session cap", FILE(docs/claims.md:27)), or only shows that the cap was not the test intended, as D1's design reads it (FILE(docs/drafts/d1_draft2.md:74), FILE(docs/drafts/d1_draft2.md:143)).
- **Caching off at matched utilization → D2:** not drafted (FILE(docs/status.md:31)).
- **The order clause → the owner** (FILE(agent/FOR_AUTHOR.md:23); see C1 above).
- **A loop figure:** none is registered.

### 4. Alternative explanations (rule A2) and what separates them

1. **Overload, not a loop.** A queue that fills a pool holding about 30 requests also evicts prefixes, so REG-22's label is the same whether the load alone sustains the queue or a loop does (DERIVED by rule F round 1: 96,656 tokens ÷ (3072 + 128) tokens per request = 30.2; FILE(docs/decisions.md:4624)). Against it at λ = 2.0: each burst run's same-seed control, the same schedule without the burst, held the links in no judged span (FILE(docs/decisions.md:16788)). **What separates them:** D1 and D2, and conditions 2, 5 and 6 of PROTOCOL §3 (FILE(docs/decisions.md:4624)).
2. **The label follows from the selection.** The verdict `stuck` already requires a low hit rate at the end, so the levels nearly follow. What is not selected on is the spans before the end window, and every judged span held all four links (FILE(docs/decisions.md:16789)). **What separates them:** a reading on runs not selected by the verdict, such as D1's capped runs read span by span.
3. **The preemption cycle of Ao et al.** A full pool with a large batch is also their limit cycle. REG-22 does not separate it (FILE(docs/decisions.md:16790)), and the comparison of preemptions with controls has no registration (FILE(docs/decisions.md:4732)).
4. **The eviction readout fits both readings.** Reported, never judged, and left out of the status line on purpose, because line a caps what a status sentence says: once the burst's requests had left, the median idle time of a sampled KV block before eviction fell in the (10, 20] s bucket in every stuck run, against a median turn spacing of 89 to 131 s in batch 2 (FILE(docs/decisions.md:16783)) and 70 to 154 s over batch 1's 11 stuck runs (FILE(docs/decisions.md:16405)). That fits "prefixes evicted before their session's next turn". It is also what a full pool under any backlog gives, so it does not separate 1 from C2.
5. **Onsets.** In every stuck run of both batches the onset reading was `differs` from the plan's order. That says nothing about when the cache was lost, because session signals are read by first token while the burst shares the server (alternative 7; FILE(docs/decisions.md:16765)). Open question A19 stays open.
6. **Standing, a caveat rather than an alternative:** batch 1's thresholds were fixed after its runs were reported, and batch 2 is retrospective by design (FILE(docs/decisions.md:16697)).

---

## K1. Turn semantics

### 1. Current status line

FILE(docs/claims.md:45), verbatim:

> - **Status (2026-11-12):** not tested at a clean load. The only related evidence is one matched pair at L1, λ = 2.4, one seed: the open-loop burst run drained with `overlap_share` 0.608 and the closed-loop one stuck (decisions.md 2026-11-09 [RESULT] REG-10 and REG-11); λ = 2.4 is at the closed-loop warm capacity, so overload explains the closed-loop arm as well (decisions.md 2026-11-10 [RESULT] REG-13).

Lines 46 ("Not evidence for K1") and 47 ("Registered test") stay as they are.

### 2. Proposed replacement (paste-ready)

```markdown
- **Status (2026-11-14):** untested. The closed arm of the registered test (REG-20) exists. Its open arm (arm A) has not run.
  - **REG-20's gate passed,** computed once on 2026-11-13 at 23:03:07 UTC: `{'k_closed': 5, 'n': 5, 'best_p': 0.03125, 'may_start': True}` (RUN(REG-19's five burst runs, k1.a_may_start); PROBE(docs/probe/reg20/gate_20261113T230307Z.txt)). So all five of REG-19's closed-loop burst runs were cold-backlogged (`k1.cold_backlogged`) in their end windows. The gate also shows that the exact one-sided McNemar test can reach p ≤ 0.05 if no open run is cold (DERIVED: 0.5⁵ = 0.03125; the gate's rule, FILE(docs/decisions.md:4051)). For 5 of 5 the one-sided 95 % Clopper–Pearson bounds are 0.549 to 1.000 (the same k and n as REG-19's matrix, FILE(docs/decisions.md:16527)). The closed arm's end windows had been seen in REG-19's [RESULT] before the gate; the risk the test takes is on the open arm, which no one has seen (FILE(docs/decisions.md:4050)).
  - **The only paired evidence is unchanged:** one matched pair at L1, λ = 2.4, one seed. The open-loop burst run drained with `overlap_share` 0.608 and the closed-loop one stuck (decisions.md 2026-11-09 [RESULT] REG-10 and REG-11). λ = 2.4 is at the closed-loop warm capacity, so overload explains the closed-loop arm as well (decisions.md 2026-11-10 [RESULT] REG-13; FILE(docs/decisions.md:2657)).
```

### 3. What is still missing, and what tests it

- **REG-20 arm A:**
  - five open-loop burst runs at λ = 2.0 on seeds 15–19;
  - a drift rerun of seed 15's closed run;
  - one control for each open run that ends cold.
  It costs ≈ 6.4–7.4 GPU h, plus ≈ 1.1 h per control that falls due (FILE(docs/status.md:12); FILE(docs/decisions.md:4052) to FILE(docs/decisions.md:4054)). The outcome comes from `k1.k1_outcome`'s table (FILE(docs/decisions.md:4069)). Arm B (λ = 2.5, seeds 15–17, the headroom check) runs only after `supports` or `supports_no_mechanism` (FILE(docs/decisions.md:4055)).
- **Before the first launch** (FILE(docs/status.md:13) to FILE(docs/status.md:18)):
  - operations draft 4 (DH1, DH2 verbatim; DL1–DL10);
  - three decision entries;
  - the VM powered on, then `vm_checkout.sh` to `1cface7`, 350 W, and the session probe with `RENEW=1`.
  Disk: 3,794,420 kB free after E1. Six launches fit under DH1, and all 11 runs need 4,281,776 kB (FILE(docs/status.md:18)).

### 4. Alternative explanations (rule A2) and what separates them

The alternatives are REG-20's own, for any result (FILE(docs/decisions.md:4088) to FILE(docs/decisions.md:4094)), applied here to the evidence so far:

1. **Overload at λ = 2.4, for the REG-10/REG-11 pair.** It explains the closed-loop arm without turn semantics (REG-13). **What separates them:** a matched pair at a load below the closed-loop warm capacity, which is REG-20 arm A at λ = 2.0.
2. **A larger working set, not held prefixes.** With closed-loop turns a session lives longer as its turns slow down. Sessions in service grew from 12–14 before the burst to 149–226 at the end in REG-17's and REG-18's burst runs (FILE(docs/decisions.md:4089)). That is still turn semantics, but not the held-prefix mechanism K1 names. **What separates them:** REG-20's mechanism contrast (held against idle reuse) and its sessions-in-service readout, per arm. They separate the two only partly, and a `supports` must say which was shown.
3. **Headroom.** λ = 2.0 is 0.67 of the open-loop warm capacity and 0.83 of the closed-loop one (FILE(docs/decisions.md:4047)), so an open arm that recovers may only have more room. **What separates them:** arm B at λ = 2.5 = 0.83 × 3.0 (FILE(docs/decisions.md:4055)). With three seeds that is weak evidence (FILE(docs/decisions.md:4081)).
4. **Time and machine drift.** The closed arm ran days before the open arm will. **What separates them:** the drift rerun of seed 15's closed run (FILE(docs/decisions.md:4053)).
5. **Read only on the closed arm (reported, never judged):** in REG-22's batch 2 the cold-state eviction readout shows prefixes idle for (10, 20] s before eviction, against a turn spacing of 89 to 131 s (FILE(docs/decisions.md:16783)). That is what K1's closed-loop half expects, every prefix having an idle, evictable interval. With no open arm it says nothing about the contrast K1 claims.

---

## K2. Cost gap and accumulated context

### 1. Current status line

FILE(docs/claims.md:60), verbatim:

> - **Status (2026-11-12):** untested. The 512-token setups were shocked with open-loop turns only, so they say nothing here. The system prompt is drawn per session (FILE(harness/workload.py:97)); a shared prompt needs a harness change (owner).

### 2. Proposed replacement (paste-ready)

```markdown
- **Status (2026-11-14):** untested. No 16-turn run exists, and E0's gate is not registered.
  - **E1,** the closed-loop cache-off sweep of the 8-turn setup (L1, 350 W, six rates from 1.5 to 4, seed 0; FILE(docs/decisions.md:18286)), ran on 2026-11-14. All six runs are valid by the automatic checks (PROBE(docs/probe/20261113_e1/validity_20261114T041823Z.txt); FILE(docs/decisions.md:19465), FILE(docs/decisions.md:19481)). **Its floor is sealed and not computed.** No part of it is computed, quoted or used before E0's [REG] is committed, or before an entry records that E0's gate takes no input from E1's runs (FILE(docs/decisions.md:17026), FILE(docs/decisions.md:19484)).
  - Until then, 1.681 req/s is the **open-loop** cache-off floor (REG-8), and E1's registration serves to have it written as such (FILE(docs/decisions.md:17025)).
  - Unchanged from 2026-11-12: the 512-token setups were shocked with open-loop turns only, so they say nothing here. The system prompt is drawn per session (FILE(harness/workload.py:97)), and a shared prompt needs a harness change (owner).
```

### 3. What is still missing, and what tests it

- **E0's [REG] (the prediction and the gate, rule G), then E2** (the two 16-turn sweeps, caching on and off; ≈ 4.2 GPU h in the earlier combined draft, FILE(docs/drafts/e0_e1_draft3.md:32)). Next, E1's [RESULT], computed only after E0's [REG] is committed. Then the 16-turn shock matrix, only if the range widens by the registered factor (FILE(docs/claims.md:56)), and later the 4-turn setup (FILE(docs/claims.md:55)).
- **A discrepancy for the owner:** `docs/status.md` lists E0/E2 as "Not drafted yet" (FILE(docs/status.md:30)), while a draft [REG] of E0 and E2 dated 2026-11-13 sits in `docs/drafts/e0_e1_draft3.md` (FILE(docs/drafts/e0_e1_draft3.md:32)), written before E1 was split off and registered alone. Most likely status.md means "no current draft". It does not change any status line here.

### 4. Alternative explanations (rule A2) and what separates them

There is no K2 evidence yet, so these are the alternatives any K2 result will have to separate:

1. **Prompt length, not reuse of accumulated context.** At 16 turns the prompts are longer (the longest is 6016 + 128 tokens, FILE(docs/drafts/e0_e1_draft3.md:40)), so both capacities can move through per-token cost alone. A fixed-cost model predicted "floor_only" (R 1.22 as the gate reads it; BELIEF; FILE(docs/status.md:81)). **What separates them:** R's two factors (warm₁₆/warm₈ and floor₁₆/floor₈), which E0's draft reports, against a gate registered before E1's floor is read.
2. **Turn count changes the system's open or closed character** (Schroeder et al., BELIEF; FILE(docs/claims.md:55)). A widening could then come from turn semantics (K1's subject), not from context. **What separates them:** the 4-turn arm and K1's own arms.
3. **One arrival pattern per sweep.** Every sweep uses seed 0, whose planned load rises across the measured window, so μ may be low (FILE(docs/status.md:130)). **What separates them:** a sweep on a second seed. None is registered.

---

## K3. Model transfer

### 1. Current status line

FILE(docs/claims.md:67) to FILE(docs/claims.md:69), verbatim:

> - **Status (2026-11-12):** no registered test. Model F's equations were read from the paper and evaluated for L1 (`docs/model.md` M5; [CORR] 2026-11-12: this line said the equations were known only through summaries); everything about the model stays BELIEF (open-questions A16). Three readings of runs already seen agree with a drain threshold near the cold floor, none of them blind: the stuck completion rate is 1.03–1.08 times the cold floor (DERIVED: 1.73 / 1.681 and 1.81 / 1.681; `docs/model.md` M2, REG-8 and REG-14 rows); REG-18's seeds 3 and 6 failed the cold side only in spans planned at 1.62 and 1.76 (decisions.md 2026-11-11 [RESULT] REG-18); REG-15's 1800 s drop was short of the ≈ 3960 s a drain at the floor needs (DERIVED: 400 waiting / (1.681 − 1.58) req/s; `docs/model.md` M2, REG-15 row).
>   - Expected under the published model for this workload (computed 2026-11-12 from the model's equations, fixed 8 turns, turn cost proportional to prompt length; BELIEF as to the model, the code is `analysis/modelf.py` with tests, moved 2026-11-12): at λ = 2.0 (ρ = 1.19 against the open-loop floor) sessions complete at 0.89 of the all-miss capacity, the session backlog grows at 1.56 times the excess load, the served prompts are 1.6 % shorter than the schedule's mean, and requests complete at 1.016 times the all-miss request rate (1.71 req/s); at λ = 2.2, 0.83, 1.53, 2.5 % and 1.025 (1.72 req/s). The measured request rates (1.73–1.77 and 1.73–1.81) lie 1–5 % above these. So the request rate is a weak test, and it already leans above the model; the session completion rate and the session backlog slope are the discriminating readouts, and neither has been computed.
>   - Alternatives for the first reading: the floor, measured with open-loop turns on seed 0, is off for closed-loop turns; or the spans were partly re-warming. The mean prompt length of the turns served in those spans separates them.

### 2. Proposed replacement (paste-ready)

```markdown
- **Status (2026-11-14):** no registered test of K3's four quantities (the drain threshold, the backlog slope, the mix of turns served, the healthy-side condition). None of them has a judged comparison on any existing run (FILE(docs/decisions.md:9744)). REG-21 read, retrospectively, the premise the four share, that the cold engine works at the all-miss rate. REG-21 is never called a test (FILE(docs/decisions.md:9734)).
  - **REG-21 batch 1** (the 13 closed-loop burst runs made before REG-19; retrospective, since every run was reported before the tolerances were fixed): "At λ = 2.0 and 2.4, read retrospectively, the cold and backlogged (`k1.cold_backlogged`) engine did the token work of the cache-off sweep within 0.05: r had a median of 1.021 over 11 runs (range 1.015 to 1.032); 1.021 at λ = 2.0 (n 5, 1.020 to 1.025) and 1.020 at λ = 2.4 (n 6, 1.015 to 1.032), with a slope of r on the load of +0.0008 per req/s. Its two factors: the completion rate over W was 1.720 to 1.798 req/s against the reference's 1.681, and the mean served prompt 2931 to 3067 tokens against the 3072 of the eight turns (`k3w.readouts`). C1 is still not supported by its own test (FILE(docs/claims.md:31)); λ = 2.4 sits at the closed-loop warm capacity (FILE(docs/claims.md:45)); load and day coincide in batch 1 (λ = 2.4 on 2026-11-09, λ = 2.0 on 2026-11-10 and 11). Nothing is said about other loads." (RUN(the 13 batch-1 burst runs, k3w.reg21_table); PROBE(docs/probe/reg21/batch1_20261113T224220Z.txt); FILE(docs/decisions.md:16451).)
  - **REG-21 batch 2** (REG-19's five burst runs; a second retrospective reading, retrospective by design; it never governs): "At λ = 2.0, in a second retrospective reading on REG-19's five burst runs (seeds 15–19), labelled retrospective by design (read (x), and the reads of the note under (i)), the cold and backlogged (`k1.cold_backlogged`) engine's r had J1 `inside` with no side: median 1.028, n 5, range 1.023 to 1.029, window 2400 s. Beside it, batch 1's λ = 2.0 group: `inside`, median 1.021, n 5, window 900 s; the contrast +0.0065. Its two factors: the completion rate over W was 1.740 to 1.758 req/s against the reference's 1.681, and the mean served prompt 3017 to 3044 tokens against the 3072 of the eight turns (`k3w.readouts`). C1 is still not supported by its own test (FILE(docs/claims.md:31)). Nothing is said about other loads, and J2 stays "load or day"." r was roughly implied by REG-19's published completion rates (RUN(REG-19's five burst runs, k3w.reg21_table); PROBE(docs/probe/reg21/batch2_20261113T231810Z.txt); FILE(docs/decisions.md:16977), FILE(docs/decisions.md:16979)).
  - The reference is the **open-loop** cache-off sweep (REG-8; FILE(docs/decisions.md:16433)). E1's closed-loop floor is sealed (K2's status).
  - Unchanged from 2026-11-12, BELIEF as to the model: model F's expected values at λ = 2.0 and 2.2 and the three earlier readings of a drain threshold near the cold floor, none of them blind (`docs/model.md` M2, M5; decisions.md 2026-11-11 [RESULT] REG-18; REG-15's drop). The session completion rate and the session backlog slope are the discriminating readouts, and neither has been judged.
```

(Under option A, the two quoted registered sentences' tags `FILE(docs/claims.md:31)` and `FILE(docs/claims.md:45)` would point at moved text; see §0.)

### 3. What is still missing, and what tests it

- **Registered tests of the four quantities,** each with a tolerance fixed before its data. REG-21's table having been read, its five reported readouts can never be judged on those runs, REG-19's included (FILE(docs/decisions.md:9742)). So the four need runs not yet made.
- **REG-24** (if run as drafted) gives one point of K3's model-against-measurement figure (FILE(docs/drafts/reg24_confirm_draft3.md:31)). Under drop option (b) that point is lost (FILE(docs/drafts/reg24_confirm_draft3.md:187)).
- **E1's [RESULT],** after E0's [REG], gives the closed-loop floor that the first reading's alternative needs (§4, item 4).
- No pending registration tests K3 as a whole.

### 4. Alternative explanations (rule A2) and what separates them

1. **REG-21's own strongest alternative:** J1 `inside` follows from the preconditions (all-miss and busy) for any saturated all-miss engine with the same per-token prefill cost, and r restates c, which was published before batch 2 (FILE(docs/decisions.md:17010), FILE(docs/decisions.md:16987)). So r ≈ 1.02 does not tell model F from other models. **What separates them:** the session completion rate and the session backlog slope against model F's values, registered before the data (FILE(docs/claims.md:68)).
2. **Conditions differ between the cold arm and the reference:** dev mode (on in the burst runs, off in the reference), a new connection per request, the day and the GPU clock (REG-21 alternatives 3, 7 and 10; FILE(docs/decisions.md:16505), FILE(docs/decisions.md:16509), FILE(docs/decisions.md:16512)). Two such differences could cancel (alternative 6). **What separates them:** a cache-off reference in the cold arm's conditions. E1 is closed-loop with no dev mode, and it is sealed.
3. **Prefill done twice after preemptions.** The redo proxy is 0.023 to 0.031 in batch 1's cold arm and 0.018 to 0.032 in the reference; it bounds the difference and does not measure it (FILE(docs/decisions.md:16503)).
4. **For the 2026-11-12 drain-threshold reading:**
   - *the 1.681 floor, measured open-loop on seed 0, is off for closed-loop turns.* Open. E1's floor separates it, once E0 is registered.
   - *the spans were partly re-warming.* Read against it, retrospectively: REG-21 reports the reuse of later turns at 0.000 in every 300 s span of W for REG-18's seeds 3 and 6, the two runs whose spans were in question (FILE(docs/decisions.md:16486), FILE(docs/decisions.md:16488)).
5. **Reported, never judged (left out of the status line):** Valse and Jannesari's trap rule held in batch 1 in 4 of 5 at λ = 2.0 (upper bound 0.990), 2 of 2 at 2.2 (1.000) and 6 of 6 at 2.4 (1.000) (FILE(docs/decisions.md:16474)), and in batch 2 in 5 of 5 at 2.0 (1.000) (FILE(docs/decisions.md:16990)).

---

## K4. Lifetime of the warm state near the edge

### 1. Current status line

FILE(docs/claims.md:77), verbatim:

> - **Status (2026-11-12):** exploratory. Every no-burst collapse so far followed a 120 s surge of 3.24–3.49 req/s (decisions.md 2026-11-10 [CORR]); that readout was found in the data and has not judged any new run. Prior work (BELIEF): Valse and Jannesari have a heuristic for the edge at which a healthy run tips by itself, with misses they report; their tests sit at 0.41–0.51 of the warm peak, ours at 0.83–1.0.

### 2. Proposed replacement (paste-ready)

```markdown
- **Status (2026-11-14):** exploratory. No registered test. Every no-burst collapse so far followed a 120 s surge of 3.24–3.49 req/s, and a warm peak of 3.32 that did not tip overlaps that range (decisions.md 2026-11-10 [CORR]; FILE(docs/decisions.md:3423)). That readout was found in the data and has judged no new run.
  - Since that readout was found, the ten no-burst controls at λ = 2.0 (DERIVED: REG-17 1 + REG-18 4 + REG-19 5) all stayed warm (`surge_run`: not tipped). Nine ran on schedules whose highest 120 s planned rate was below 3.2: REG-17's at 2.608 (FILE(docs/decisions.md:3540)) and REG-19's at 2.833 to 3.092 (FILE(docs/decisions.md:16542)). One, REG-18's seed 4, went through a 3.217 peak without tipping, which is weak evidence either way, as registered (FILE(docs/decisions.md:3753)). The stop for a control that tips without a surge (`surge_reading_wrong`), registered in REG-18 and REG-19, fired in neither (FILE(docs/decisions.md:3737), FILE(docs/decisions.md:16551)). These schedules were not chosen on both sides of a threshold, so they do not test K4.
  - Prior work (BELIEF, unchanged): Valse and Jannesari have a heuristic for the edge at which a healthy run tips by itself, with misses they report; their tests sit at 0.41–0.51 of the warm peak, ours at 0.83–1.0.
```

### 3. What is still missing, and what tests it

- **K4's own registration:** a surge threshold fixed beforehand, then no-burst runs on new schedules chosen on both sides of it (`gate.surge_hazard`) (FILE(docs/claims.md:74)). None is drafted, and none appears among the pending items in `docs/status.md`.
- **REG-24** (as drafted) gives one K4 datum. Its control's schedule has no 120 s planned peak at or above 3.2 (its highest is 2.733), so a tip of that control would be the `surge_reading_wrong` event (FILE(docs/drafts/reg24_confirm_draft3.md:32)).
- **REG-23** (K5) reads the six runs that went cold without a trigger, which are K4's tips. It is a retrospective reading and does not test K4.

### 4. Alternative explanations (rule A2) and what separates them

1. **A surge of planned requests or a surge of new sessions.** A surge of new sessions brings cold 2176-token first turns, and here it moves with the request rate (FILE(docs/decisions.md:3426)). **What separates them:** schedules on which the two peaks come apart, for example session starts that are bursty at an even request rate.
2. **A sustained load above a capacity** (REG-13's first reading). Against it: REG-16's run carried 300 s windows at λp 2.57 and 2.60 warm (FILE(docs/decisions.md:3421)). **What separates them:** K4's registered test, at schedules with matched mean load and different peaks.
3. **The threshold does not separate.** A tipped peak of 3.24 overlaps an untipped one of 3.32 (FILE(docs/decisions.md:3423)). The tip may depend on the server's state at the surge (queue or KV level), not on the schedule alone. **What separates them:** runs on both sides of a threshold fixed beforehand, with the state at the surge reported.

---

## K5. Detection lead time (optional)

### 1. Current status line

FILE(docs/claims.md:83), verbatim:

> - **Status (2026-11-12):** not started; kept only if K1–K3 leave room.

### 2. Proposed replacement (paste-ready)

```markdown
- **Status (2026-11-14):** no registered test. REG-23 (0 GPU h; `analysis/k5.py`, `tests/test_k5.py`) is drafted and in review: draft 5 followed rule F round 1 on draft 4 (NOT READY, CA1–CA6) and its owner-proxy (APPROVE with CB1–CB8) (FILE(docs/drafts/reg23_k5_draft5.md:3)). It reads onsets on the runs that went cold with no trigger, not on burst runs. That departs from the test above, "applied to stuck runs" (FILE(docs/drafts/reg23_k5_draft5.md:10)). It would be a retrospective reading. Kept only if K1–K3 leave room (unchanged).
```

### 3. What is still missing, and what tests it

- **REG-23:** a rule F round on draft 5, the owner-proxy, then a [REG] and its approval. 0 GPU h. Its departure from the claim's stated test (burst runs left out) needs the owner's acceptance, since it changes which runs K5 is read on.

### 4. Alternative explanations (rule A2) and what separates them

No K5 reading exists yet. These are the alternatives REG-23 has to separate:

1. **On burst runs, a "lead" is the burst's own shape.** The trigger raises the batch and the recomputed prefill at once (FILE(docs/drafts/reg23_k5_draft5.md:10)). REG-22's onsets on burst runs (reported, never judged) put N and the reuse at about 910–940 s, KV at about 960–970 s and the uncached rate at about 1200–1240 s, after a burst that starts at 900 s (FILE(docs/decisions.md:16766) to FILE(docs/decisions.md:16770)). This is not K5 evidence, for that reason. **What separates them:** no-trigger tips, as REG-23 drafts.
2. **Measurement lag, not a lead.** Session signals are read by first token, and the trailing-window crossings have different lags by construction (FILE(docs/decisions.md:4724)). **What separates them:** onset rules with each signal's lag stated, and false alarms counted on runs that stayed warm.
3. **Arrivals drive every signal.** If the arrival rate moves first, the cache signals only follow it. **What separates them:** REG-23's comparison with the arrival rate (A) (FILE(docs/drafts/reg23_k5_draft5.md:6)).

---

## Other stale lines noticed (not part of the seven; for the owner)

- **FILE(docs/claims.md:35):** "None has a registered test yet" is no longer true. K1 has REG-20 (FILE(docs/decisions.md:4045), approved at FILE(docs/decisions.md:4166)). K2 has E1, a measurement (FILE(docs/decisions.md:17020)). K3 has REG-21, a retrospective reading of the shared premise, not a test of the four quantities (FILE(docs/decisions.md:9731)). A possible replacement: "Each is stated for the cells tested only. Registered so far: K1's test, REG-20 (its open arm not run); for K2, E1, a measurement (its floor sealed); for K3, REG-21, a retrospective reading of the premise the four quantities share, not a test of them. Every other test below needs its own `[REG]`, with thresholds fixed before the data (rule A5)."
- **FILE(docs/claims.md:31)** says "REG-19 is under way". So does PROTOCOL §7's note (FILE(PROTOCOL.md:111)). A PROTOCOL change is the owner's, and this draft proposes none.
- **FILE(docs/status.md:40)** names C1, C2 and K3 as dated. K1, K2, K4 and K5 also date from 2026-11-12.

---

## What the evidence supports now, in one paragraph per claim

**C1.** One registered test says `supports`, and only for C1's matrix condition at one load. At λ = 2.0 (setup L1, 350 W, closed-loop turns), REG-19's matrix found the server stuck, cold and below its load through a 3000 s watch after the burst, while the same schedule without the burst stayed healthy. That held in 5 of 5 new seeds (one-sided 95 % bounds 0.549 to 1.000). The test was written after the previous matrix at the same load had passed 1 of 4 seeds, and under that older per-span test the new runs pass 3 of 5. C1 itself is not supported. Whether the state lasts a 4500 s watch and leaves when the load drops (conditions 5 and 6) is untested at this load, and condition 4's order clause is not judged. Nothing is known about other loads. The open-loop setups had no stuck run.

**C2.** No registered test supports or refutes C2. Two retrospective readings at λ = 2.0 describe every stuck run the same way. In every 300 s span after the burst, the cache was lost, prompts were recomputed, the batch was large and the pool full: 4 of 4 runs in one batch, 5 of 5 in the other. Same-seed controls without the burst showed none of it. The loop would produce this, but so would an overload of the cold server, and the order of the signals is not judged. The part of C2's test that can tell a loop from an overload, the session-cap and caching-off controls, has not run.

**K1.** Untested. The closed-loop arm of the registered test is in place: all five of REG-19's burst runs were cold and backlogged, and the gate passed. So the registered test can give an answer once the open-loop arm runs. Until then no evidence at a clean load bears on K1 either way. The one paired observation (λ = 2.4, one seed) is explained by overload as well.

**K2.** Untested. The runs for the 8-turn closed-loop floor exist and are valid, but the floor stays sealed until E0's gate is registered. No 16-turn run exists.

**K3.** No registered test of K3's four quantities exists. Two retrospective readings, never called tests, find that the cold, backlogged engine prefilled uncached tokens at 1.02 to 1.03 times the cache-off sweep's rate at λ = 2.0 and 2.4. That fits the premise the published models share, but it does not tell them apart: any saturated all-miss engine with the same per-token cost reads the same, and the ratio follows from completion rates already published.

**K4.** Exploratory. The surge readout of 2026-11-10 has judged no run. The ten no-burst controls at λ = 2.0 since then stayed warm, nine of them on schedules without a 120 s peak of 3.2. That is consistent with the readout and tests nothing.

**K5.** No registered test exists. A 0 GPU h reading on the runs that went cold without a trigger is drafted and in review.
