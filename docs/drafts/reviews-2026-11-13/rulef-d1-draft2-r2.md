# Rule F review, round 2: D1 draft 2 (C2, session cap)

**What was reviewed.** At HEAD ab281db:
- `docs/drafts/d1_draft2.md` (sha256 `56b21551a78b13a7d97ecb1de9a733529c25682239c242ec87be7a2c7122bf62`, checked) and its item map.
- The three patches in `docs/drafts/d1_r2/`. Their sha256 equal `SHA256SUMS.txt` (checked).
- `git diff --quiet e788191 ab281db -- analysis/ tests/ harness/ configs/` exits 0, so the patches' base and HEAD agree on every file they touch or read (DERIVED: the command, rerunnable).
- Applied to a `git archive ab281db` export, the three patches give the draft's three sha256 values (checked).

**What else was read:**
- round 1 (`rulef-d1-draft1-r1.md`, sha256 `23b29c09…`, checked), draft 1 and its notes;
- decisions.md:
  - 3945–3952: the owner's cap rule;
  - 3782–3796: REG-19's inputs and bounds;
  - 16517–16570: REG-19's [RESULT];
  - 16752–16756: REG-22 batch 2;
  - 17020–17090: E1's [REG];
  - 18286: E1's approval;
  - 19452–19454: VM disk;
- claims.md C1–C2, and open questions S7, S9 and S11;
- `harness/loadgen.py`, `checks.py`, `run.py` and `config.py`;
- `analysis/withheld.py` and `analysis/load.py`, and every run-name glob in `analysis/` and `tools/` (grep);
- REG-24's and E1 DE-O1's pending seal patches.

**Limits.**
- Nothing was opened among: run folders, sealed paths, `docs/paper/`, `state/` folders, backups, `RESUME.md` and `FABLE_PROMPT.md`. Nothing under `runs/` was listed.
- No cap value and no number from any run was computed.
- The traces are pytest cases on synthetic tmp folders. `RUNS` and `DECISIONS` are monkeypatched, and `AFTERSHOCK_UNSEAL` is set only inside fixtures. They live in the scratch file `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/rf_d1_r2/traces/test_r2_traces.py`, which is not provenance.
- The planned arrival rates in §1 come from configs only: `harness.workload.build_schedule` on `d1.resolved(seed, 1)`, as the draft's DG-O5 readout.

**Verdict: READY provided DJ1–DJ3 are applied verbatim.**
- The code for all three is `rulef-d1-draft2-r2.patch` beside this file. It applies after the writer's three patches. Its text replacements are below.
- 3 required items, 7 optional.

## Reproduced
- **Writer's three patches:** `tests/test_d1.py`, `tests/test_withheld.py` and `tests/test_session_cap.py` give 83 passed (108 s).
- **With `rulef-d1-draft2-r2.patch` on top** (fresh export of ab281db; patch sha256 `9d0e80e372933c2be991b335d6aadbf54be3004cb2b1700e42dd1cbd1f762add`):
  - the three files: 90 passed (113 s), of which `tests/test_d1.py` 62;
  - the full suite without `tests/test_check_docs.py`: 585 passed, 1 skipped (719 s), rc 0. That is the writer's 578 plus the 7 new tests in `tests/test_d1.py`.
- **Patched sha256:** `analysis/d1.py` `4466e1ba422158cc3610dc452b4c6208238efa435928bc9cb33698e4df15be12`; `tests/test_d1.py` `cdcc2065f2f6a7c39f11df66ec9223c57dee36f26944cbdc7bbffc39d618f804`; `analysis/withheld.py` unchanged, `e89e8a4d…`. The import closure of `analysis/d1.py` is unchanged: the patch adds no import to it, and `heapq` is imported inside a test.
- **`d1.predicted_matrix()`** reproduces the draft's numbers (DERIVED). With DJ1 applied it gives:
  - `supports` 0.7628, `mixed` 0.2364, `stuck_split` 0.0003, `refutes` 0.0003, `admission_only` 0.0003, `cap_did_not_cut` < 0.0001, `too_few` < 0.0001;
  - E[k_cut] 3.80; P(`supports` with `below_reg19`) 0.2702 (DERIVED).
- **`d1.inputs()`:** the session and burst row counts match the draft (8048–8420 and 425–466). They also match REG-19's table (FILE(docs/decisions.md:3782-3786)).

## 1. Traces on which D1's outcome or its reading is wrong

**T5 (the matrix): a stuck majority split across the two KV classes is `mixed`.**
- Input: five capped seeds under a temporary `RUNS`, built with DJ3's `harness_like`. These are records of the shape `harness/loadgen.py` writes when the cap binds and the server stays cold:
  - FIFO slots, handed over 2 ms after the last reply;
  - sessions never admitted keep only `t_arrived`;
  - unsent turns are `unfinished` placeholders, and turns are cut at the deadline (FILE(harness/loadgen.py:137-178,209,240)).
  - Seeds 15 and 17 have end KV 0.5, seed 16 has 0.95, and seeds 18 and 19 recovered.
- What `d1.table()` gives:
  - labels `stuck_kv_free`, `stuck_kv_full`, `stuck_kv_free`, `recovered`, `recovered`, which are right;
  - `max_held` 10 = the cap, `idle_share` 0.0016, and 106 sessions never admitted per stuck seed;
  - and then `decision` **`mixed`**, with k_stuck 3 of 5.
- Two stuck under each KV class plus one recovered also gives `mixed`, with k_stuck 4 (scratch trace).
- Why that is wrong:
  - claims.md: "Refutes: … stuck runs that stay stuck under the session cap" (FILE(docs/claims.md:27)).
  - The draft's `mixed` branch says "no C2 status change". So three or four of five stuck under the cap would be reported as no change.
  - The approver's question 4 (read `cap_did_not_cut` as refuting or not) cannot reach such a split, because the code has no branch for it.
- → **DJ1.**

**T6 (the onset split): a cold state that forms after an early re-warm is not seen.**
- The fault: `load_reading` lists only the cold spans before the first warm span, and `onset_class` reads only that list (`d1.load_reading`, `d1.onset_class` in FILE(docs/drafts/d1_r2/d1.patch)).
- Trace (a): spans warm, 0.2, 0.2, 0.2, then warm to the end; exit at 1200 s. This gives `reading` `never_cold` and **`onset_class` `never_cold`**. Yet three cold spans start after the exit, and the watch ends warm.
- Trace (b): spans 0.0, 0.95, 0.5, 0.6, then warm. This gives **`burst_only`**.
- Both are "a cold state that outlasted the burst's exit and then cleared". That is the only kind the status line counts as bearing on C2's sustaining loop (draft, "Decision under each outcome", `supports`).
- The error runs one way: toward "the cap prevented the onset; whether it breaks an established stuck state is not tested by D1".
- → **DJ2.**

**T7 (the onset split): where the exit falls against the fixed 300 s grid.**
- Trace: spans 0.0, 0.9, then warm. Exit at 1379 s gives `formed_then_cleared`; exit at 1381 s gives `burst_only`.
- The arithmetic:
  - Span 1 starts at 1380 s. REG-19's uncapped exits were 1207.2–1228.1 s (FILE(docs/decisions.md:16752-16756)), so span 1 starts 152–173 s after the exit (DERIVED).
  - A span is cold when its reuse is ≤ baseline − 0.06. A fully cold stretch of ≈ 18 s at its start is enough on its own (DERIVED: 0.06 ÷ 0.997 × 300 s, turns evenly spread; baseline reuse 0.996–0.999, same lines).
  - So the two classes divide one clearing time at ≈ 1398 s, ≈ 170–190 s after the exit.
- That cut is fixed before the data, so it is acceptable, but the text must say what it is.
- → **DJ2** (disclosure), **DJ-O5** (a finer clearing time).

**Checked and not wrong; the bounds are on record here.**
- **`harness_fault` on stuck seeds.** On harness-shaped stuck records with cap 10 (scratch trace), `idle_share` depends on the hand-over time as follows:

  | Hand-over | `idle_share` | `harness_fault` |
  |---|---|---|
  | 2 ms | 0.0016 | no |
  | 50 ms | 0.011 | no |
  | 0.3 s | 0.060 | yes |
  | 0.6 s | 0.118 | yes |

  - In the harness, a freed slot goes to the oldest waiter in `release()`, directly after the last reply's record is written. The waiter resumes on the next event-loop iteration (FILE(harness/loadgen.py:65-71,124,131-134,176-178)). So a hand-over takes milliseconds: BELIEF as to the loop's latency under load, a margin of about two orders of magnitude.
  - The error would run one way. Only backlogged seeds have many waiting grid seconds, so a slow hand-over removes stuck seeds from n. → DJ-O1.
- **The drain exception in the cold branch.** It could make a cold seed `partial` while its queue is still high.
  - Planned session starts in the end window [3480, 4080), from configs only (DERIVED):

    | Seed | Whole window (/s) | First half (/s) | Second half (/s) |
    |---|---|---|---|
    | 15 | 0.2567 | 0.2633 | 0.2500 |
    | 16 | 0.2550 | 0.2233 | 0.2867 |
    | 17 | 0.2417 | 0.2200 | 0.2633 |
    | 18 | 0.2350 | 0.2067 | 0.2633 |
    | 19 | 0.2683 | 0.2800 | 0.2567 |

  - At REG-19's cold rates, sessions leave at 0.213–0.225 per s (DERIVED: 1.703–1.800 ÷ 8, FILE(docs/decisions.md:16539)). So a cold seed's cap queue is expected to grow over the end window in every seed, and `partial` by "draining" is not expected at those rates.
  - It could happen if the capped cold rate is higher than on record. The closest case is seed 18. Over the whole window it plans 1.88 req/s (DERIVED: 0.2350 × 8), above REG-19's cold rates, so its queue is expected to grow. In its first half it plans 1.65 req/s (DERIVED: 0.2067 × 8), below them, so its queue may shrink there before it grows. → DJ-O2 (report the planned rates beside the label).
- **`row` on stuck records.** Every readout of `row` returns on harness-shaped stuck records (T5): `slots`, `waits` (sessions never admitted counted), `spans`, `shock_size`, `eviction_readout`, `verdict`, `reg19_baseline_pair`, and the JSON output. DJ3 makes this a test.
- **`_check_capped`.** It compares the run's `config.yaml` with `d1.resolved`. That is the right comparison: `harness/run.py` writes `with_defaults(load_config(path))` plus `run_id` and `source_config` (FILE(harness/run.py:139-140,236-237)), and `resolved` builds the same merge (FILE(harness/config.py:18-28)).
- **Missing data that depends on the outcome.** The checks were read for any failure that depends on the outcome under the cap, which would make a stuck seed `not_run`:
  - `arrival_rate` counts `t_arrived`, sent or not (FILE(harness/checks.py:147-151));
  - `release_chain` excuses turns whose earlier turn never ended (FILE(harness/checks.py:163-171));
  - `accounting` allows deadline cut-offs (FILE(harness/checks.py:78-83)).
  - None fails because a capped run stays stuck (DERIVED from those lines). REG-19's uncapped stuck runs were all valid (FILE(docs/decisions.md:16517)).

## 2. The round-1 items, checked against the code

| Item | Met? | Evidence |
|---|---|---|
| DG1 | Yes | **Code:** in `label`'s cold branch, `_backlogged` (end mean > base + 1.0 and not draining; None gives `unclear`) comes before `stuck_*`, and `partial` follows it. `partial` is in `LABELS`, not in `CUT` or `STUCK`, and `outcome` reports `k_partial`. **Traces:** T1 (0.93, no backlog) gives `partial`; T1c (cold, growing queue) gives `stuck_kv_free`; harness-shaped stuck records give `stuck_*` (T5). **Matrix:** 3 cut + 2 `partial` gives `supports`; 3 `partial` + 2 cut gives `mixed` (as the text says). |
| DG2 | Yes | The three replacement texts verbatim. The docstrings of the module and of `first_order` match. |
| DG3 | Yes | **Row:** `("D1", "*_burst_l1pl350cl_r2.0_w3000_s1[5-9]_cap", "[RESULT] D1 (C2, session cap)")`. **Lift pattern:** `^## \d{4}-\d{2}-\d{2} · <text>(?!\d)` (FILE(analysis/withheld.py:46)). **Lift nothing:** the caps heading, `[RESULT] D1 caps: …`, `[RESULT] D1: …`, `[RESULT] D1-caps`, `[OPS] D1: …`, `[RESULT] D10`, `[RESULT] D2 …`, a [CORR] quoting the text, a [REG] heading, a body line. **Lifts:** `## <date> · [RESULT] D1 (C2, session cap): …`. **Care point:** a heading such as `[RESULT] D1 (C2, session cap) caps` would lift. The caps heading is fixed in the text, so this needs care, not an item. |
| DG4 | Yes | **Code:** `cp_upper_not_cut` = `cp_upper(n − k_cut, n)`; `below_reg19` against `_cp_lower(5, 5)` = 0.549; T4 is a test. **n:** it excludes `harness_fault` and seeds not run. So 0 of 4 gives 0.527, below 0.549, as the text says. |
| DG5 | Yes | Inserted verbatim. |
| DG6 | Yes | Verbatim; the freeze is in bold. |
| DG7 | Yes | Verbatim. E1's additions are cited (FILE(docs/decisions.md:17072)). |
| DG8 | Departure, accepted | See §3.4. |
| DG9 | In part | **Covered:** a recovered seed; the cut seed that was cold past the exit; an invalid attempt before a valid run; a spent seed; `harness_fault`. **Not covered:** no stuck seed, and no records of the harness's shape. `make_run` sends every turn at its planned time whatever `wait` says (FILE(tests/test_d1.py:54-58) as patched), so its "waiting" sessions are served while they wait. → DJ3. |
| DG10 | Yes, refined, with two gaps | T6 and T7. → DJ2. |
| DG11 | Yes | Both citations corrected. The new uses are named and marked the owner's. |

## 3. The six points

### 3.1 The round-1 items against the code, and traces where the label or matrix is wrong
See §2 for the items and §1 for the traces (T5–T7). The label is right on every harness-shaped trace built. The matrix is wrong on T5, and the onset split is wrong on T6.

### 3.2 The writer's DG10 refinement (four classes, cold spans after the exit)
- **Fixed before the data: yes.**
  - The classes and the exit rule are code before any capped run.
  - The exit is `c2.last_burst_end` (FILE(analysis/c2.py:101-108)), and the rule for which spans count is REG-22's (FILE(analysis/c2.py:11-15)), which predates D1.
  - The beliefs 0.10 / 0.60 / 0.25 / 0.05 were set knowing REG-19's uncapped spans. They are beliefs, not thresholds.
- **Can it hide a real result: yes.**
  - T6 is a code fault, and it runs toward the weaker status sentence.
  - T7 is a coarse cut, acceptable once stated.
- **It cannot make up `formed_then_cleared` from the burst's own requests.** Span 0 always starts before the exit. Every exit on record (1207.2–1228.1 s) lies before span 1's start at 1380 s (DERIVED).
- **Read beside the uncapped arm** (it belongs in the text, DJ2). In all five of REG-19's uncapped runs, the span from 1380 s was cold, with N 28.9–30.2 and KV 0.947–0.957 (FILE(docs/decisions.md:16752-16756)). So:
  - `burst_only` means the capped arm was warm again by ≈ 1398 s, when the uncapped arm was already in its stuck state;
  - `formed_then_cleared` means the capped arm was still cold then and cleared later.

### 3.3 The thresholds marked as the owner's (rule A5)
**None was chosen with knowledge of the data it will judge.**
- The capped runs do not exist yet, and the caps are computed only after approval.
- Three values are carried unchanged from configs that predate D1:
  - `hit_climb` 0.06 (FILE(configs/stage2_cap_base.yaml:9), calibrated on the hit counter at a healthy λ = 3);
  - `recovered_q_excess` 1.0 (FILE(configs/stage2_base.yaml:18));
  - `drain_horizon_s` 3600 (FILE(configs/stage2_cap_base.yaml:11); set 2026-11-01, FILE(PROTOCOL.md:101)).
- `max_idle_share` 0.05 is new, and it is argued from the hand-over mechanism, not from data.

**REG-19's and REG-22's published numbers on the same seeds could not have placed a capped outcome.** The uncapped arm lies far from every one of these thresholds:
- reuse is 0.000 in every span against a baseline of 0.996–0.999 (FILE(docs/decisions.md:16752-16756));
- the end-window line slopes are +0.019 to +0.071 per s (FILE(docs/decisions.md:16533-16537));
- nothing on record measures hand-over gaps.

I find no sign that a value was moved to place an outcome (DERIVED from those values; BELIEF as to how the writer worked).

**Two of the new uses lean one way, and the approving entry should name them.**
- `rewarming` comes before `stuck`. Applied to reuse, `hit_climb` lets noise in a capped cold reuse move a seed from `stuck` to `rewarming`, which is neither cut nor stuck. That can only help `supports` (it is bounded by `cp_upper_not_cut`). → DJ-O3.
- `recovered_q_excess` of 1.0 session is looser than the verdict's 1.0 request, since a session holds up to 8 turns. A binding cold state builds ≈ 19 sessions per 600 s (DERIVED, draft "admission confound"), far above either reading.

**A replacement in the approving entry changes reviewed code.** Replacing any of these thresholds, or choosing the other branch of questions 2, 4 or 5, changes code or text after this review. → DJ-O7.

### 3.4 DG8's departure (E1's restricted diff plus `d1.config_chain`)
**What a capped run reads from the repo:**
- the config through `load_config` (the `extends` chain) and `with_defaults` (`configs/defaults.yaml`) (FILE(harness/config.py:18-28), FILE(harness/run.py:236));
- only `harness/` modules (FILE(harness/run.py:23-26));
- vLLM from the uv environment (`pyproject.toml`, `uv.lock`, `.python-version`);
- `tests/fake_vllm.py`, only for a fake server (FILE(harness/run.py:44-45)).

So `harness/ pyproject.toml uv.lock .python-version` plus `d1.config_chain` covers every repo file a capped run reads (DERIVED from those lines).

**The analysis side** is held by the closure rule (W5) and by the worktree for the caps. DG8's literal path list did not add to that.

**Conclusion: as strong as DG8's literal list for what runs, without blocking on unrelated commits. Accepted.**

Small gaps → DJ-O6:
- `--name-only` does not show that the five files are added and not changed;
- the chain is read from the tree it runs in, so it should be printed at the registered commit;
- nothing compares each written config byte for byte with `d1.config_text`;
- nothing checks that the registered `analysis/d1.py` and `tests/test_d1.py` equal the reviewed sha256. E1 had the equivalent check for its harness (FILE(docs/decisions.md:17031)).

### 3.5 The seal and the broad globs
**While sealed, nothing reads a capped folder's records.**
- Readers in `analysis/` go through two functions (FILE(analysis/load.py:18-20,41-43)):
  - `load.find_runs` drops sealed folders by `withheld.keep`, with one stderr line;
  - `load.load_run` raises.
- `recheck`, `engine_config.scan` and `tables.arrival_table` use `keep` too (FILE(analysis/recheck.py:19), FILE(analysis/engine_config.py:65), FILE(analysis/tables.py:152)).
- `tools/` reads only `checks.json` validity, `env.json`, `config.yaml` and checksums (FILE(tools/check_docs.py:40-47,196-214), FILE(tools/manifest.py:48-69)). None of these is outcome data.
- The full list of `RUNS.glob`, `find_runs(` and `iterdir()` calls in `analysis/` and `tools/` came from grep (DERIVED).

**No other pattern matches a capped name:**
- REG-19's and k1's burst patterns end in `_s{seed}` with no trailing `*` (FILE(analysis/gate.py:1807-1808), FILE(analysis/k1.py:43-44));
- the batch-2 patterns (FILE(analysis/k3.py:50), FILE(analysis/k3w.py:65));
- every seal row;
- REG-24's pending rows `*_confirm_l1pl350cl_r2.0_s43` and `*_stage2_control_l1pl350cl_r2.0_long_s43` (FILE(docs/drafts/reg24_r2/withheld.patch));
- E1's DE-O1 row (same pattern as E1's).

**After the lift, exactly what Confounds 7 names takes the folders in:**
- `gate.surge_table`;
- `tables.verdict_table` (and the `tables` CLI; `analysis/analysis.ipynb`, not provenance);
- `k3.reg21_table(1)`'s lookup, which keeps only listed ids (FILE(analysis/k3.py:378-381)).

Nothing beyond these takes them in:
- REG-24's draft uses `surge_run` per run, not `surge_table` (FILE(docs/drafts/reg24_confirm_draft2.md:394)).
- `surge_table` would gain five rows whose planned schedules equal the uncapped burst runs'. The draft's rule that any quoted number names its run set covers this.
- If a later seal row ever matched a capped name, `d1.table()` raises rather than skipping the folder, because `_sealed_capped` checks every seal.

### 3.6 Rule A1: worth it, and which outcome changes C2's status
**Outcomes that change C2's status:**
- **Against C2 (claims.md's refutation wording):** `refutes`, `cap_did_not_cut` and, with DJ1, `stuck_split`. P ≈ 0.0006 by the draft's beliefs (DERIVED: 0.00026 + 0.00001 + 0.00033).
- **Toward C2:** `supports` drafts a status line, but it does not make C2 "supported". That needs D2 (the draft says so).
- **No change:** `mixed`, `admission_only` and `too_few`.

**The decision D1 changes.** Whether D2's registration is the next C2 step (`supports`), or the owner decides on more seeds or stops loop-cut runs (the rest). So yes, it can change a decision.

**What D1 can tell apart.** By the draft's own text, `supports` is predicted alike by:
- C2;
- a failure driven by the population through pool pressure, with or without the cache;
- admission control in any bistable server.

So `supports` hardly separates C2 from its strongest alternatives (BELIEF). D1's information is in the stuck tail and in the onset split, which DJ2 makes count correctly.

**Cost.** ≈ 6.2 GPU h (≈ 7.7 expected) against the plan's 4–6 h for D1 and D2 together.
- D1 has the higher chance of a clean outcome. D2 is the control that separates C2 from the population alternative, so it has more information per GPU hour (BELIEF).
- The overrun, and which of the two goes first if the budget binds, are the owner's (rule C).
- Fewer seeds is not a saving worth taking. At n = 3, `below_reg19` cannot hold (0.632), and P(`supports`) falls to 0.76³ ≈ 0.44 (DERIVED from the beliefs).

## 4. The strongest alternative explanation of `supports`
**A failure sustained by the population, through pool pressure, with or without the prefix cache.**
- The uncapped stuck runs held ≈ 30 running requests at KV 0.95, with 11–21 preemptions per span (FILE(docs/decisions.md:16540)).
- A cap at the healthy peak removes the population growth that any such loop needs, so it predicts `supports` as C2 does.
- **What separates the two:**
  - D2, the caching-off control at matched utilization.
  - Inside D1, only `formed_then_cleared` seeds bear on it. Their capped cold spans after the exit show cache loss with the gauge below 0.80 and N ≈ 14–22. Whether prefixes were evicted before their session's next turn there is read from `c2.eviction_readout`, and whether preemption was present is read from the counter `spans` does not yet report (DJ-O4).

**The second alternative: the two arms are judged by different tests.**
- The uncapped arm was judged by REG-19's whole-window test on the server's line. The capped arm is judged by D1's end-window label on reuse and the cap's queue.
- From published values, D1's label applied to REG-19's uncapped runs, with the server's line in the cap queue's place, gives `stuck_kv_full` in all five (DERIVED):
  - reuse 0.000 in every span, so there is no climb;
  - KV 0.950–0.952 (FILE(docs/decisions.md:16752-16756));
  - mean waiting in the end window 179.8–281.3, with end slopes +0.019 to +0.071 per s (FILE(docs/decisions.md:16533-16537)), so the line is backlogged and not draining. This assumes the pre-burst mean is below ≈ 178 (BELIEF; the same-schedule controls were `recovered`, FILE(docs/decisions.md:16542)).
- So the pairing holds under one rule. It should be stated in the text (DJ-O2).

The third and fourth alternatives, a smaller effective shock and day or drift, are named in the draft with what separates them (`gate.shock_size` and the onset split; the baseline pair and the drift readout).

## 5. Can the run change any decision?
Yes, as in §3.6.

---

## Required items

### DJ1 (code and rule; trace T5): a stuck majority split across the KV classes gets its own outcome
**Code:** `rulef-d1-draft2-r2.patch`:
- `outcome` gains the rule `stuck_split` (k_stuck ≥ 3, neither class ≥ 3), placed after `cap_did_not_cut` and before `supports`;
- the module docstring and `outcome`'s docstring are updated;
- `test_outcome_rules` gains six cases (2 + 1 + 2 cut; 1 + 2 + `partial` + cut; 2 + 2 + cut; 3 free + 2 full gives `refutes`; 2 free + 3 full gives `cap_did_not_cut`; 1 + 1 + 3 cut gives `mixed`).

Text, matrix list. Anchor:
```text
  3. `cap_did_not_cut`: `stuck_kv_full` ≥ 3.
  4. `supports`: no seed stuck under the cap and cut ≥ 3.
  5. `admission_only`: `server_only` ≥ 3.
  6. `mixed`: anything else (including a majority of `partial`, which the [RESULT] names).
```
Replacement:
```text
  3. `cap_did_not_cut`: `stuck_kv_full` ≥ 3.
  4. `stuck_split`: `stuck_kv_free` + `stuck_kv_full` ≥ 3 with neither class ≥ 3 (rule F d1 r2, DJ1: three or more seeds stuck under the cap are never `mixed`).
  5. `supports`: no seed stuck under the cap and cut ≥ 3.
  6. `admission_only`: `server_only` ≥ 3.
  7. `mixed`: anything else (including a majority of `partial`, which the [RESULT] names).
```
Anchor: ``FILE(tests/test_d1.py), `test_outcome_rules` (12 cases).``
Replacement: ``FILE(tests/test_d1.py), `test_outcome_rules` (18 cases, six of them for `stuck_split`).``

Decision section. Anchor:
```text
so a cap ≥ 34 is not a reading made after the data.
- **`admission_only`:**
```
Replacement:
```text
so a cap ≥ 34 is not a reading made after the data.
- **`stuck_split`:** three or more seeds stuck under the cap, split across the two KV classes (for example two `stuck_kv_free` and one `stuck_kv_full`). By claims.md's wording ("stuck runs that stay stuck under the session cap", FILE(docs/claims.md:27)) this refutes C2; by D1's design only the `stuck_kv_free` seeds test the cap with the pool gauge held below 0.80. The [RESULT] gives both readings with the end-window KV and N per seed, as for `cap_did_not_cut`, and the owner decides C2's status; no further loop-cut run until then. The approving entry reads `stuck_split` as it reads `cap_did_not_cut` ("For the approver", 4).
- **`admission_only`:**
```
A1 summary. Anchor: ``P(`supports`) 0.763, P(`mixed`) 0.237, P(`refutes`) 0.0003, P(`admission_only`) 0.0003,``
Replacement: ``P(`supports`) 0.763, P(`mixed`) 0.236, P(`refutes`) 0.0003, P(`stuck_split`) 0.0003, P(`admission_only`) 0.0003,``

A1 summary. Anchor: ``; `refutes` or `cap_did_not_cut` changes C2's status the other way``
Replacement: ``; `refutes`, `cap_did_not_cut` or `stuck_split` changes C2's status the other way``

Prediction. Anchor: ``P(`supports`) 0.7628, P(`mixed`) 0.2367, P(`refutes`) 0.0003, P(`admission_only`) 0.0003,``
Replacement: ``P(`supports`) 0.7628, P(`mixed`) 0.2364, P(`refutes`) 0.0003, P(`stuck_split`) 0.0003, P(`admission_only`) 0.0003,``

"For the approver", 4. Anchor: ``4. `cap_did_not_cut` read as refuting (claims.md) or as not the test intended (D1's design).``
Replacement: ``4. `cap_did_not_cut` and `stuck_split` read as refuting (claims.md) or as not the test intended (D1's design); the two are read alike.``

The same change goes into the item map's question 4.

### DJ2 (code and reporting duty; traces T6 and T7): the onset split reads every span and says what it measures
**Code:** same patch:
- `load_reading` also returns `cold_any` (every cold span of the watch, each with `after_exit`), `nan_any` and `last_warm`. Its `reading`, `rewarm_span` and `cold` are unchanged.
- `onset_class` reads `cold_any`. `formed_then_cleared` needs a cold span starting at or after the exit and the last span warm.
- `undefined` adds a NaN reuse in any span, and a cold span after the exit with the last span not warm.
- Four assertions are added to `test_onset_class_separates_the_bursts_own_transient_from_a_formed_cold_state`: T6 (a) and (b), a cold last span, and a NaN span after the re-warm.
- The writer's end-to-end onsets (`never_cold`, `formed_then_cleared`, `burst_only`) are unchanged.

Text, "What D1 can and cannot do", readout 2. Anchor:
```text
`d1.load_reading` finds the first 300 s span after the burst's end whose reuse is back within 0.06 of the baseline and lists the cold spans before it; `d1.onset_class` names each seed `never_cold`, `burst_only` (cold only in spans that start before the last burst request ended, `c2.last_burst_end`; REG-22 judges no such span, FILE(analysis/c2.py:11-15)), `formed_then_cleared` (a cold span that starts after that exit, then the re-warm) or `undefined`.
```
Replacement:
```text
`d1.load_reading` finds the first 300 s span after the burst's end whose reuse is back within 0.06 of the baseline and lists the cold spans before it (for the floor comparison), and lists every cold span of the watch apart (`cold_any`); `d1.onset_class` reads every span of the watch (rule F d1 r2, DJ2: a cold state that forms after an early re-warm, or resumes after one warm span, counts) and names each seed `never_cold` (no cold span), `burst_only` (cold only in spans that start before the last burst request ended, `c2.last_burst_end`; REG-22 judges no such span, FILE(analysis/c2.py:11-15)), `formed_then_cleared` (a cold span that starts at or after that exit, and the last span warm) or `undefined` (a NaN reuse in any span, the exit unknown while a cold span exists, or a cold span after the exit with the last span not warm). The split cuts one clearing time at one point: span 1 starts at 1380 s, 152–173 s after REG-19's uncapped exits (1207.2–1228.1 s, FILE(docs/decisions.md:16752-16756)), and a span is cold once ≈ 18 s at its start are fully cold (DERIVED: 0.06 ÷ 0.997 × 300 s, turns evenly spread). So `burst_only` says the capped arm was warm again by ≈ 1398 s, ≈ 170–190 s after the exit, and `formed_then_cleared` that it was still cold then and cleared later; in REG-19's uncapped runs the span from 1380 s was cold, with N 28.9–30.2 and KV 0.947–0.957, in all five (same lines).
```

### DJ3 (test; DG9 completed): the stuck outcome runs end to end on records of the harness's shape
**Code:** same patch: `harness_like(cap, …)` and `test_table_end_to_end_on_stuck_seeds_written_like_the_harness`. In it, seeds 15–17 are stuck (KV 0.5, 0.95, 0.5) and seeds 18 and 19 recovered. It asserts:
- the labels;
- `holds`, `idle_share` < 0.01 and `max_held` = cap;
- `cap_backlogged`, and sessions never admitted;
- the decision `stuck_split`, and that the output serialises.

It passes on the writer's code. It holds the path that the outcome against C2 takes, so that a fault there cannot first appear on real stuck data, after the freeze.

Text, "Result, computed once". Anchor: ``, `harness_fault` leaves n, and every readout of `row` returns).``
Replacement:
```text
, `harness_fault` leaves n, and every readout of `row` returns); and `test_table_end_to_end_on_stuck_seeds_written_like_the_harness` (rule F d1 r2, DJ3: three capped seeds whose records have the shape `harness/loadgen.py` writes when the cap binds and the server stays cold, with sessions never admitted, unsent placeholders and turns cut at the deadline; labelled `stuck_kv_free`, `stuck_kv_full` and `stuck_kv_free`, the slot invariant holding, the hand-over gaps no `harness_fault`, and the decision `stuck_split`).
```
"Code and tests". Anchor: ``, 55 tests on configs, synthetic runs, fake run folders under a temporary `RUNS` and one end-to-end pair``
Replacement: ``, 62 tests on configs, synthetic runs, fake run folders under a temporary `RUNS` (three stuck seeds among them with records of the harness's shape, DJ3) and one end-to-end pair``

**The writer redoes three things in the draft's head and in "Code and tests":** the patched sha256, the saved pytest outputs and `SHA256SUMS.txt`, with `rulef-d1-draft2-r2.patch` applied, or folded into the three patches. The values from my run are under "Reproduced".

## Optional items
- **DJ-O1 (`harness_fault`).**
  - The [RESULT] gives each `harness_fault` seed's underlying label (`label_values["label"]`, already in `row`), beside the fault.
  - `slots` adds `max_idle_stretch_s`: the longest continuous stretch with a session waiting and a slot free, from the same event sweep. A reported value, never judged.
  - The text states the margin: a false fault on a stuck seed needs a hand-over of ≈ 0.3 s (§1, synthetic trace).
- **DJ-O2 (planned rates and the paired label).**
  - `row` reports the planned session-start rate over the end window and its two halves (`build_schedule` on the run's config, schedule only). The draft states the values in §1, DERIVED from configs.
  - The text states, DERIVED from FILE(docs/decisions.md:16533-16537,16752-16756), that D1's label puts REG-19's uncapped runs at `stuck_kv_full` in all five, so McNemar's pairing holds under one rule.
- **DJ-O3 (`rewarming`).** Compute `_backlogged` in the `rewarming` branch too, and keep it in `cap_backlogged`. The [RESULT] names every `rewarming` or `partial` seed whose cap queue is backlogged as "possibly stuck". These are already counted by `cp_upper_not_cut`.
- **DJ-O4 (`spans` and Confounds 6).**
  - `spans` adds the preemptions in each span (the difference of `vllm:num_preemptions_total` over it, as `tables._preemptions`, FILE(analysis/tables.py:46-48)). That is the measure of the population alternative's mechanism.
  - `row` adds `d1.cap_queue(run, [burst_end, exit])`. Confounds 6 says "the cap queue at that time is reported beside it (`spans`, first span)", but the first span gives the mean over [1080, 1380), not the value at 1080. Correct that sentence either way.
- **DJ-O5 (finer clearing time).** For each cut seed, report the first 60 s window from the exit whose reuse is back within 0.06 of the baseline (reported, never judged). Report the uncapped arm's value in the same window.
- **DJ-O6 (tree and registered code).**
  - The configs entry and the operations decision use `git diff --name-status` and require exactly five `A` lines.
  - The chain is the output of `python -m analysis.d1 chain` at the registered commit.
  - Before the configs commit, each written config equals `d1.config_text(seed, caps[seed])` byte for byte (printed `True` × 5).
  - The approving entry quotes the sha256 of `analysis/d1.py` and `tests/test_d1.py` at the registered commit, equal to the reviewed values.
- **DJ-O7 (the approver's choices).** Replacing a threshold marked as the owner's, or taking the other branch of questions 2 (`harness_fault` as `unclear`), 4 or 5 (McNemar), changes reviewed code or text. Either it comes back to rule F, as a change after the caps does, or the alternatives become reviewed switches in `D1` now.

## Files
- `rulef-d1-draft2-r2.patch` (beside this file; sha256 `9d0e80e372933c2be991b335d6aadbf54be3004cb2b1700e42dd1cbd1f762add`): against the tree that the writer's three patches give, `analysis/d1.py` and `tests/test_d1.py` only. Apply with `git apply` after `d1.patch`, `test_d1.patch` and `withheld.patch`.
- Scratch traces (not provenance): `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/rf_d1_r2/traces/test_r2_traces.py`, `planned_end.py`.
