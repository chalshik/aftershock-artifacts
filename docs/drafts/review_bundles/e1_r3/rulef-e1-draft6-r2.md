<!-- Saved verbatim 2026-11-13 ≈ 23:20 UTC from the reviewer's own file /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/d3f64482-d0cf-4bf8-9ad1-c1dc026c562c/scratchpad/rulef-e1-draft6-r2.md (sha256 8dc8a1463b8db0850d3e97b8a357f336fcf39996e4ff69aa4117075f933b6408, 354 lines); the reviewer (rulef-e1-r2) sent the same text to the agent in five SendMessage parts. Body below this line is byte-identical to that file. -->
Rule F review, round 2, of E1 draft 6 (bundle `docs/drafts/review_bundles/e1_r2/`, commit 97a6438), with the start-gate entry of 302d431

**Verdict: NOT READY.** Two blocking items: DC1 (E1's floor is an input of E0's gate in the plan, in claims.md and in committed code, so "E1 changes no decision about a shock matrix" is false, and running E1 before E0 is registered needs a rule-A5 guard) and DC2 (the "holes" rule in `e1.floor` gives a cleaner status on less data; a code fix, tested). DC3–DC9 are required but do not block: they are text, tags or reporting duties and can be applied verbatim. DC-O1 to DC-O5 are optional; DC-O1 and DC-O2 are code, tested in a scratch sandbox. The start gate with the 4611 entry is sound (section "The start gate").

**Bundle and limits**
- MANIFEST: 41 of 41 sha256 lines OK. Every file in the bundle is in the manifest, and the manifest lists nothing else.
- `ops/` in the bundle is byte-equal to `docs/probe/20261113_e1/ops/` at HEAD (cmp, 10 files).
- `e1_draft6.patch` and `test_e1_draft6.patch`, applied to HEAD's `analysis/e1.py` and `tests/test_e1.py`, give the bundle's `e1.py` and `test_e1.py` byte for byte (patch in scratch, then cmp).
- HEAD moved to 08817af during this review: 7e1a9fd, de80007, d9b324d (REG-22 and REG-21 registered), 62c9d96, 1dc008d and 08817af. `git diff --stat 97a6438 HEAD` over `docs/probe/20261113_e1`, `analysis`, `tests`, `harness`, `configs`, `agent/RUNBOOK.md`, `docs/experiment-plan.md`, `docs/claims.md` and the bundle is empty, so every anchor and FILE line below holds at HEAD. `docs/decisions.md` is append-only and now has 16320 lines; lines 1–4614 are unchanged, and every decisions.md line cited below is in that range unless named otherwise.
- **REG-21's and REG-22's freezes (since d9b324d, after the bundle).**
  - E1's draft-6 patch and DC2's patch change only `analysis/e1.py` and `tests/test_e1.py`. Neither is in REG-22's 27 frozen files (FILE(docs/decisions.md:4748)) or REG-21's 26 (FILE(docs/decisions.md:9834)), and neither adds a `.py` file. So the approval commit does not break either freeze. `analysis/k2.py` is not frozen either, so DC1's guard still matters.
  - E1's seal is already at HEAD (FILE(analysis/withheld.py:30)), and `withheld.py` is frozen, so no seal change is needed or allowed.
  - E1's folders match neither REG-21's reference pattern `*_sweep_l1pl350_pc_off_r*` (FILE(analysis/k3w.py:77); E1's names carry `l1pl350cl`) nor REG-21's or REG-22's batch-2 patterns, which name REG-19's burst configs. So E1's runs enter no batch.
  - Disclosure E1 should carry (in DC5's spirit, not a separate item): the harness E1 runs on (`harness/checks.py`, `run.py`, `recorder.py`, `loadgen.py`, …) is frozen until both batch 2s are computed or declared not computed. A harness fault that DA7's block finds cannot be fixed before then.
- Read: the bundle; the ops scripts; `analysis/e1.py`, `gate.py` (cold_floor, sweep_rows), `load.py` (find_runs), `withheld.py`, `k2.py` (decide, observed), `k3.py` (e1_prediction, legacy); `harness/run.py`, `checks.py`, `config.py`, `loadgen.py` (the drain deadline); the E1 config chain; `tools/manifest.py` (reads bytes only); `docs/decisions.md` (the cited lines, 1744–1752, 4037–4045, 4260–4275, 4516–4521, 4571–4614); `docs/claims.md` K2; `docs/experiment-plan.md` lines 427–428 (a grep for E0/E1); `agent/RUNBOOK.md` lines 46–75; `docs/drafts/reg19_resume_decision_draft5.md` line 41; REG-19's `ops_r3/` scripts (`common.sh`, `queue.sh`, `launch.sh`, `final.sh`); `docs/probe/20261113_reg20/ops/common.sh` (a grep for E1 and the gate); `docs/probe/20261113_freeze/closure.py` (source); `git diff .gitignore`.
- Not opened: anything under `runs/` beyond folder names (`ls runs | grep -E '_sweep_l1pl350(cl)?_pc_off'`: seven REG-8 folders, no E1 folder; 186 folders in all); `docs/probe/**/state/`; `/Users/chalshik/aftershock-backups/`; RESUME.md; `docs/paper/`; any `queue_*.txt` or `launch_*.out`; any transcript; `docs/context-pack.md`; `docs/status.md` beyond the session-start digest a hook put into my context; the draft-3 rule F review (`rulef-e0e1-r2.md`), whose argument DC1 contradicts but which I did not read. Names under `ops_r3/state/` appeared in the git-status snapshot of my context (names only). No VM contact.
- Ran: the sandbox in a temp dir under my scratchpad (`passed 184, failed 0`); `tests/test_e1.py` on the patched files in a scratch copy (`git archive HEAD analysis harness configs tests pyproject.toml`, with no `runs/`), run with the repo's interpreter: 16 passed; `python3 docs/probe/20261113_freeze/closure.py --at HEAD analysis/e1.py` (24 .py files, the same 27 in all as draft 6 says; it reads source only); schedule and config expansion through `e1._cfgs` and `harness.workload.build_schedule` in the scratch copy (no run read); `git diff --quiet 9e249b1 HEAD -- <DA11's list>` (exit 0); `git merge-base --is-ancestor a7bb77a HEAD` (exit 0). No analysis module command, no `tables.py`, `recheck`, `gate`, `check_docs.py` or full pytest. Python may have refreshed gitignored `__pycache__` in the repo when the sandbox ran `vm_state.py`; nothing else in the repo was written. The working tree's other modifications (`docs/decisions.md`, `agent/STATE.md` and others, shown by `git status` during this review) are not mine.
- Scratch files, under `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/d3f64482-d0cf-4bf8-9ad1-c1dc026c562c/scratchpad/`:
  - `DC2_DC8_e1_vs_bundle.patch`, `DC2_test_e1_vs_bundle.patch`: against the bundle's `e1.py` and `test_e1.py`. Patched files: `out/b/analysis/e1.py` (sha256 428771e0…) and `out/b/tests/test_e1.py` (dd3f52c5…); 16 passed.
  - `DCO1_common.patch`, `DCO1_queue.patch`, `DCO1_test_sandbox.patch`: sandbox 188 of 188 (`sandbox_patched_newcase.txt`). Without the fix, the new case fails (`sandbox_unpatched_newcase.txt`, 186 passed, 2 failed).
  - `DCO2_common.patch`, `DCO2_test_sandbox.patch`: sandbox 188 of 188 (`sandbox_dco2.txt`).
- Every replacement anchor below was counted in the entry (lines 1–75 of `registration_draft6.md`): each occurs exactly once. The RUNBOOK and README anchors also occur once each.

---

### Required items

**DC1 (BLOCKING). E1's floor is an input of E0's gate. "E1 changes no decision about a shock matrix" is false, and E1 is run ahead of the gate that will judge it.**
- **Trace.**
  - The owner's plan makes E1's floor K2's 8-turn reference: "E0 … register[s], before any sweep, a numeric prediction of each setup's window ratio (closed-loop warm capacity over closed-loop cold floor) and the gate: the 16-turn shock matrix runs only if the 16-turn ratio exceeds the 8-turn ratio by a factor fixed here (rule G)" (FILE(docs/experiment-plan.md:427)). E1 "gives K2 its 8-turn reference" (FILE(docs/experiment-plan.md:428)). The same is said in FILE(docs/decisions.md:4040) ("E0 (0 GPU h) registers … the gate factor before any sweep (rule G)") and FILE(docs/claims.md:56).
  - In the committed code, `k2.observed` computes `f8 = e1.floor(sweep_rows("sweep_l1pl350cl_pc_off"))`, which is E1's runs (FILE(analysis/k2.py:179)). `k2.decide` puts f8 into R = (warm16/f16)/(warm8/f8) (FILE(analysis/k2.py:109)) and returns "missing", meaning no matrix, when f8 is NaN (FILE(analysis/k2.py:102-103)). The owner's choice 2 of 2026-11-12 is "kept as it is in the E0 … registration" (FILE(docs/decisions.md:4264-4269)).
  - So on E1's no-floor outcomes ("holes", "too_few", "unsaturated", "tail_*" but "tail_ok"), E0's committed gate gives "missing": no 16-turn matrix. Within E1's predicted range, f8 still moves R in proportion. Whether that flips a label depends on g and on E2's grid, which E0 has not fixed.
  - The draft rests its claim on the draft-3 review's argument ("decided by the 16-turn cache-on sweep alone"). That argument is about a gate that is not registered, and it fails on the no-floor branch above. The owner's 4516 entry repeats the claim from the draft ("as its own draft says first", FILE(docs/decisions.md:4520)), so the owner's acceptance rests on it.
  - Rule A5 hazard. E1 runs before E0 is registered. E0's redesign "needs … the owner's choice of a threshold" (draft 6, header). E1's result waits only for REG-21's first [RESULT]. If E1's floor is reported first, E0's threshold is chosen with one of its inputs known. The delegation does not cover choosing a threshold after seeing the data it judges (FILE(docs/decisions.md:4235)).
  - Second inconsistency: `k2.observed` reads E1's runs with `e1.floor` but without `first_valid` and without the swept rates. It skips E1's holes check, and `gate.cold_floor` raises on two valid runs at one rate (FILE(analysis/gate.py:35-36)). E0 could therefore get a floor from runs on which E1's own rule reports "holes".
- **Class:** disclosure and stricter rule (text).
- **Text.** All anchors are in the entry, above the quoted review.
  - (a) Anchor: `- **What E1 cannot do (rule A1), said first:** E1 changes no decision about a shock matrix. The rule F review showed that whether the 16-turn window "widens" is decided by the 16-turn cache-on sweep alone; E1 and the 16-turn cache-off sweep only word the ratio. E1 is proposed as K2's measurement and as the floor every closed-loop margin in the paper is quoted against, and for nothing else.`
    Replace with: `- **What E1 can and cannot do (rule A1), said first:** E1's floor is K2's 8-turn reference: the denominator of the 8-turn window ratio that E0's gate compares the 16-turn ratio against (FILE(docs/experiment-plan.md:427-428); FILE(docs/decisions.md:4040); FILE(docs/claims.md:56)). As committed, `k2.decide` takes it as `f8` in R = (warm16/f16)/(warm8/f8) and returns "missing" (no matrix) when it is undefined (FILE(analysis/k2.py:102-109)), and `k2.observed` computes it from E1's runs (FILE(analysis/k2.py:179)). The draft-3 rule F review argued that the label is set by the 16-turn cache-on sweep alone; that is an argument about a gate that is not registered (BELIEF until E0's [REG] shows it), and it does not hold for E1's outcomes without a floor, which make the committed label "missing". So E1 can change the 16-turn matrix decision and K2's "does not widen" reading, through E0. E1 runs before E0 is registered, which departs from "E0 … registers … the gate factor before any sweep (rule G)" (FILE(docs/decisions.md:4040)). To keep rule A5 for E0's gate, no part of E1's floor (status, value, n, rates, slope) is computed, quoted or used before E0's [REG] is committed, or before an entry records that E0's gate takes no input from E1's runs. E0's registration discloses the one bit per rate that the allowed reads show (stopping rule, first bullet), and takes E1's floor as E1's [RESULT] reports it (the registered code, "holes" included), not recomputed by another rule (`k2.observed` calls `e1.floor` without `first_valid` or the swept rates, FILE(analysis/k2.py:179)). Apart from E0's gate, E1 is proposed as K2's measurement and as the floor every closed-loop margin in the paper is quoted against, and for nothing else.`
  - (b) Anchor: `The decisions E1's outcomes do change are the wording ones under "Decision under each outcome".`
    Replace with: `The decisions E1's outcomes do change are E0's gate input (above) and the wording ones under "Decision under each outcome".`
  - (c) Anchor: `- **No floor:** K2's 8-turn closed-loop floor is reported as unmeasured on this grid; closed-loop margins keep the open-loop floor, named as such. A new grid is a new registration.`
    Replace with the same text followed by: ` Under E0's gate as committed, the label is then "missing": no 16-turn matrix, the owner decides (FILE(analysis/k2.py:94-95,102-103)).`
  - (d) Anchor: `- **In neither case** does E1's floor start, stop or size another run. That is why the paragraph "What E1 cannot do" comes first.`
    Replace with: `- **In neither case** does E1's floor start, stop or size a run other than through E0's gate ("What E1 can and cannot do", which is why that paragraph comes first).`
  - (e) Anchor: `After every rate has a valid run or the stopping rule has ended, and after REG-21's first [RESULT]:`
    Replace with: `After every rate has a valid run or the stopping rule has ended, after REG-21's first [RESULT], and after E0's [REG] is committed or an entry records that E0's gate takes no input from E1's runs ("What E1 can and cannot do"; no computation in this section, and no `e1.observed`, `e1.floor_status` or `k2.observed` on E1's runs, runs before then):`
- **Why blocking.** The first paragraph is the entry's rule-A1 statement, and a delegate approval may not rest on a false one. Without (e), the order of E1's result and E0's registration is left to chance, and with it rule A5 for E0.

**DC2 (BLOCKING). The holes rule gives "ok" when two rates are missing and "holes" when one is; a row `cold_floor` drops is not counted as a hole.**
- **Trace (a), the main one.**
  - The sweep returns 1.5 INVALID `recorder` and 2.0 INVALID `recorder`; 2.5–4.0 are valid. `MAX_SAME` stops E1 after the sweep (common.sh:260-262), and "E1's result is then computed from the runs made".
  - `floor` sees rows 2.5–4.0 only. `cold_floor` returns "ok" with λ_sat 2.5. Draft 6's hole check finds no valid row below λ_sat, sets `lo = lam_sat`, and so reports **"ok", 1.735** (scratch check on synthetic rows).
  - With 1.5 valid and kept up, and only 2.0 missing, the same code reports "holes" [2.0] (DA-O4's own case). Less data gives the cleaner status.
  - 2.0 plans 2.097 req/s and counts as saturated below 1.992, against a predicted floor of 1.70–1.80 (DERIVED from `build_schedule`: 1374 planned arrivals in [240, 900) over 660 s). So the "ok" floor leaves out a row predicted to belong to it, and sits about 0.01–0.015 req/s high (DA6's figures).
  - A fault that hits only the first two runs of the sweep (the coolest and shortest) is the kind DA1's stop is built for, so this trace is reachable.
  - Under the DA4 merge, after a later [CORR] "the registered code's floor is E1's floor". A fix after registration cannot correct this outcome, so it must be in the registered code.
- **Trace (b).** `have` is built from every row's rate, including rows that `cold_floor` drops for a non-finite value (FILE(analysis/gate.py:33)). A valid run with a NaN `kv_mean` or throughput at 3.0 therefore makes no hole, and the floor silently leaves out 3.0. This is unlikely under the new coverage checks, and costs one line.
- **Class:** code fix, plus text.
- **Code** (against the bundle's `e1.py`; full patch `DC2_DC8_e1_vs_bundle.patch`).
  - Replace `        have = set(np.round(rows.rate.to_numpy(float), 6))` with:
    ```
            fin = rows[np.isfinite(rows[["rate", "throughput", "planned_rate", "kv_mean"]]).all(axis=1)]   # as cold_floor reads them
            have = set(np.round(fin.rate.to_numpy(float), 6))
    ```
  - Replace `        lo = max(below) if below else f["lam_sat"]` with `        lo = max(below) if below else -math.inf          # no valid row below lam_sat: lam_sat is not bracketed (DC2)`.
  - In `floor`'s docstring, replace `    lam_sat, or between the highest valid row below lam_sat and lam_sat (rule F e1_r1, DA-O4: lam_sat could lie` / `    there), has no valid run (the floor would average over a gap)."""` with `    lam_sat, or below lam_sat with no valid row between it and lam_sat (rule F e1_r1, DA-O4; e1_r2, DC2: lam_sat` / `    could lie there), has no valid run (the floor would average over a gap); a row with a non-finite rate, throughput,` / `    planned rate or KV mean, which cold_floor drops, counts as no valid run."""`.
- **Tests** (`DC2_test_e1_vs_bundle.patch`; still 16 tests, 16 passed).
  - In `test_floor_no_rows_and_holes`, replace
    ```
        low = E.floor(full[full.rate != 1.5], grid)             # a hole below lam_sat does not matter
        assert low["status"] == "ok" and low["n"] == 5
    ```
    with
    ```
        low = E.floor(full[full.rate != 1.5], grid)             # no valid row below lam_sat: lam_sat could be 1.5
        assert low["status"] == "holes" and low["missing_rates"] == [1.5]
        assert E.floor(full, (1.0,) + grid)["status"] == "ok"   # a hole below a valid unsaturated row does not matter
    ```
  - In `test_a_hole_just_below_lam_sat_is_a_hole`, replace
    ```
        g = e1.floor(no_low, grid)
        assert g["status"] == "ok" and g["lam_sat"] == 2.5                               # 1.5 and 2.0: below, not holes
    ```
    with
    ```
        g = e1.floor(no_low, grid)                                                       # no valid row below lam_sat:
        assert g["status"] == "holes" and g["missing_rates"] == [1.5, 2.0]               # lam_sat could be 1.5 or 2.0
        nan_row = rows([1.5, 2.0, 2.5, 3.0], [1.45, 1.70, 1.72, float("nan")], kv=[0.6, 0.95, 0.95, 0.95])
        assert e1.floor(nan_row, (1.5, 2.0, 2.5, 3.0))["missing_rates"] == [3.0]     # a row cold_floor drops is a hole
    ```
- **Text.**
  - Anchor: `- **Holes:** a swept rate at or above λ_sat, or a swept rate between the highest valid row below λ_sat and λ_sat, with no valid run gives the status "holes" and no floor (the floor would average over a gap); the missing rates are listed.`
  - Replace with: `- **Holes:** a swept rate with no valid run gives the status "holes" and no floor when it lies at or above λ_sat, or below λ_sat with no valid row between it and λ_sat (λ_sat could lie there; with no valid row below λ_sat, every swept rate below it without a valid run is such a hole). A row with a non-finite rate, throughput, planned rate or KV mean, which `gate.cold_floor` drops, counts as no valid run. The missing rates are listed.`
- **Cost and side effect.**
  - The stricter rule costs a floor only when 1.5 has no valid run. Outside a stop, that means three failures at 1.5.
  - It also changes `floor_status`, which E2 reads (E2's lowest rate is 1.0). E2 is not registered; its registration must say so.
  - "holes" is on the owner-proxy's §3 list, so this needs its pass.

**DC3. Two descriptions of the registered-code computation disagree, and one of them would read sealed folders.**
- **Trace.**
  - DA4's sentence runs the registered code "from a worktree at the registered commit whose `runs/` links to the Mac's". DB6's sentence links only the two sweeps' folders.
  - Read as a link to the whole `runs/`, the worktree's `e1.observed` → `gate.sweep_rows` → `load.find_runs("*")` would load every run folder that the registered commit's `withheld.SEALS` does not list (FILE(analysis/load.py:41-44)).
  - E1's result waits for REG-21's first [RESULT] (and, with DC1, for E0's [REG]). Seal rows added after the registered commit, for REG-20 arm A's operations or D1/D2, are unknown to that code, so their sealed runs' requests and metrics would be loaded.
  - That is "reading outcome data a pending registration withholds", which the delegation does not cover.
- **Class:** stricter rule (text; resolves a DA4/DB6 merge conflict).
- **Text.**
  - Anchor, in the entry: ``(run from a worktree at the registered commit whose `runs/` links to the Mac's)``
  - Replace with: ``(the worktree computation below, whose `runs/` is a real directory holding links to E1's and REG-8's cache-off sweep folders only, as REG-19's `links_ok` builds its own, FILE(docs/probe/20261113_reg19/ops_r3/common.sh:88-102); never a link to the whole of the Mac's `runs/`: the registered code's `analysis/withheld.py` does not know seals added after the registered commit, and `gate.sweep_rows` loads every run folder it can see, FILE(analysis/load.py:41-44))``

**DC4. Nothing holds the VM for E1 between its queue runs, and RUNBOOK §5 puts REG-20 first.**
- **Trace.**
  - E1 pauses after an invalid run, or stops for a `lost_ok` decision (likely, given A18). While it waits, E1's queue lock does not exist.
  - REG-19's [RESULT] may land then. REG-21's and REG-22's entries are now committed (d9b324d), so only `final.sh` stands before it.
  - RUNBOOK §5 orders "2 REG-20 gate, 2a REG-20 arm A" before "4 E1" (FILE(agent/RUNBOOK.md:63-66)). REG-20's ops scripts (in review) gate on `[RESULT] REG-19` and know nothing of E1 (a grep of `docs/probe/20261113_reg20/ops/common.sh` for E1 has no hit).
  - REG-20's move puts the VM on a commit that descends from E1's. E1's next pre-launch then stops on the tree, and `vm_checkout.sh` refuses to move backward (FILE(docs/probe/20261113_e1/ops/vm_checkout.sh:32)).
  - E1 is stranded with holes. The 2.1 h already spent may then give no floor.
  - The draft's RUNBOOK proposal amends §4 and §3 item 6 only, and E1's end has no fixed record that another registration's gate could read. This is the mirror of the REG-19 gate E1 itself needed.
- **Class:** stricter rule (text, with RUNBOOK and README edits in the approval commit).
- **Text.**
  - Anchor: `- The owner halts E1 by an entry headed `## <date> · [DECISION] (owner) E1 halted`; no launch follows its commit.`
  - Replace with the same line followed by a new bullet: ``- **E1 holds the VM** from `vm_checkout.sh` until its end is recorded by an entry headed `## <date> · [OPS] E1: the queue ended (QUEUE DONE)`, `## <date> · [OPS] E1: the queue ended (QUEUE END)`, or `## <date> · [OPS] E1 ended by a stop: <the stop line>` (a stop that an entry has decided ends E1). A pause, or a stop that waits for a decision, is not an end. Until the end entry, no other registration's run is launched, and the VM's tree is moved only by E1's scripts or under an owner's entry. The approval commit amends RUNBOOK §5's order to match: E1 runs from REG-19's recorded queue end, and REG-20's gate and arm A wait for E1's end entry.``
- **RUNBOOK, (c), merged with the item map's (a) and (b).**
  - Anchor: `| 4 | E1 |`
  - Replace with: `| 1a (before 2) | E1 (runs from REG-19's recorded queue end; items 2 and 2a wait for E1's end entry, "[OPS] E1: the queue ended …" or "[OPS] E1 ended by a stop: …") |`
- **README.**
  - Anchor: ``   - write the `[OPS]` entry;``
  - Replace with: ``   - write the `[OPS]` entry, headed `[OPS] E1: the queue ended (QUEUE DONE)` or `(QUEUE END)` (registration, "E1 holds the VM");``

**DC5. DA7's readable fields cannot name every cause of a `recorder` or `gpu_steady` failure, and two of them carry DA8's bit without saying so.**
- **Trace.**
  - `gpu_steady` fails on `busy_sm_clock_cv` > 0.05 or on no busy sample, as well as on throttling, SW thermal or coverage (FILE(harness/checks.py:134-138)).
  - Suppose a run fails on the clock CV alone. Every allowed field then reads as passing: `hw_throttle_samples` 0, `sw_thermal_frac` ≤ 0.05, `window_max_gap_s` ≤ 2.
  - Three sentences then pull against each other. DA-O5's "then says which" cannot be met. DA7's block ("no registration runs on this harness until the cause is found") cannot be lifted within the allowed reads. The only way out is a read outside the list.
  - `recorder`'s `counter_decreases` is missing the same way (FILE(harness/checks.py:106-110)).
  - The item map's finding 2: `end_ref_t` (the time of `load_end`) shows whether the run ended early. `busy_samples`, once added, shows how loaded the GPU was. For a failed run, both show DA8's bit per rate.
- **Class:** reporting duty and disclosure (text). It widens what may be read before E1's [RESULT], so the owner-proxy must rule on it (its §3, fourth bullet; item map finding 3).
- **Text.**
  - Anchor: `` `recorder`'s `first_ok_scrape_t`, `last_ok_scrape_t`, `end_ref_t`, `recorder_died`, `max_gap_s`, `failed_scrapes`; `gpu_steady`'s `window_max_gap_s`, `hw_throttle_samples`, `sw_thermal_frac`, `max_temp_c`. None of them holds a request count, throughput or KV. ``
  - Replace with: `` `recorder`'s `first_ok_scrape_t`, `last_ok_scrape_t`, `end_ref_t`, `end_ref`, `recorder_died`, `max_gap_s`, `failed_scrapes`, `counter_decreases`; `gpu_steady`'s `window_max_gap_s`, `window_samples`, `busy_samples`, `busy_sm_clock_cv`, `hw_throttle_samples`, `sw_thermal_frac`, `max_temp_c`, or its detail text when the detail is not a dict ("no gpu.jsonl data"). These are every input of the two checks' pass conditions (FILE(harness/checks.py:106-110,134-138)). None of them holds a request count, throughput or KV. Disclosed: `end_ref_t` is the time of `load_end`, which comes early for a run whose sessions all ended before the drain deadline, and `busy_samples` counts the samples with the GPU at least 50 % busy. For a failed run, both show the same one bit per rate as the stopping rule's first bullet, and no more. ``
  - Anchor (in R3, in the entry): `The [RESULT] names each `gpu_steady` failure "heat or sample coverage" until its detail is read (DA7's fields), then says which.`
  - Replace with: `The [RESULT] names each `gpu_steady` failure "heat, SM-clock steadiness or sample coverage" until its detail is read (the fields listed under "In neither case"), then says which.`

**DC6. Two sentences of "Result, computed once" describe a `report()` that does not exist (item map finding 4).**
- **Trace.**
  - `report()` returns `observed()` plus the work rates. `observed()` gives `tilt_reported` and never calls `prediction()` (bundle `e1.py`:184-199, 242-252).
  - `floor_ol` is `saturated(ol)`: `cold_floor` with no tail fallback and no holes check, which is not "the same way" as E1's floor.
  - For REG-8's seven rows the value is 1.681 either way, since `cold_floor` gives "ok" and every swept rate has a row. So the fix is wording, which keeps REG-8's own definition.
- **Class:** wording.
- **Text.**
  - Anchor: `the open-loop floor recomputed the same way; the common onset; the tilt with its prediction; the work rates of both sweeps.`
  - Replace with: `the open-loop floor recomputed by `gate.cold_floor` with REG-8's settings (`e1.saturated`, as REG-8 computed it: no tail fallback and no holes check); the common onset; the tilt (`tilt_reported`); the work rates of both sweeps. The tilt's model-F description, `e1.prediction()`, reads no run. `e1.report` does not print it; it is quoted beside the tilt from `python -c 'import json; from analysis import e1; print(json.dumps(e1.prediction(), default=str))'`, run from the same code.`

**DC7. Rule H: the floor is a single-seed, pooled quantity, and the entry does not label it so.**
- **Class:** reporting duty.
- **Text.**
  - Anchor: `- **A floor exists** only with status "ok" or "tail_ok". The result reports n and the rates used.`
  - Replace with: `- **A floor exists** only with status "ok" or "tail_ok". The result reports n and the rates used, and labels the floor "single seed (seed 0), one run per rate": no seed-to-seed spread is measured, and the SE of `floor_slope_reported` is across rates, not seeds (rule H). The floor pools its rows under REG-8's assumption that a saturated cache-off server completes requests at one rate whatever the offered load. E1's own prediction says closed-loop rows break that assumption by a slope of about 0.04 req/s per req/s (FILE(tests/test_e1.py:59), BELIEF as to the model), so the result states the assumption beside the floor, with the slope as the evidence on it.`

**DC8. `analysis/e1.py`'s module docstring still says "not yet registered: draft docs/drafts/e1_draft4.md" (item map finding 7; owner-proxy N7).**
- **Why now.** Draft 6 changes `e1.py` anyway, and from the registered commit the file is frozen (DA4). After registration this sentence would be false in judged code, with no way to fix it short of a [CORR].
- **Class:** wording, in code; included in `DC2_DC8_e1_vs_bundle.patch`.
- **Code.**
  - Replace `"""E1 (not yet registered: draft docs/drafts/e1_draft4.md; its [REG] E1 entry does not exist yet): the closed-loop cache-off sweep of setup L1`
  - with `"""E1 (registered: the [REG] E1 entry in docs/decisions.md; frozen from its registered commit): the closed-loop cache-off sweep of setup L1`.
- **Note.** `observed`'s docstring "feeds E0" is true (DC1) and stays.

**DC9. The gate's entry now exists; cite it.**
- **Class:** tag.
- **Text.**
  - Anchor: `It needs no REG-19 result.`
  - Replace with: `It needs no REG-19 result. That entry exists: FILE(docs/decisions.md:4611) (commit 302d431, headed `[OPS] REG-19: the queue ended (QUEUE DONE)`, quoting `QUEUE DONE (all five seeds run). Next: final.sh, once`), which restates FILE(docs/decisions.md:4571) and records no new event.`

---

### Optional items

Every code anchor below occurs exactly once in the ops scripts at HEAD (grep -c -F).

**DC-O1. The DA2 residual gap (item map finding 5), closed by writing the pause in `settle`.**
- **Trace** (reproduced in the scratch sandbox).
  - The sweep is launched by `launch.sh` with 2.0 INVALID, then settled by hand without `report_settled`. This is the state a queue leaves when it dies between the two statements.
  - Restart: the queue launches rate 2's rerun with no pause, rc 0 (`sandbox_unpatched_newcase.txt`: "FAIL the restart still pauses before the rerun").
  - DA1's stop still bounds a systematic fault, so this is optional.
- **Code.**
  - `common.sh`, in `settle`:
    - Replace `  local rec=$1 f log out line id c lines recs=()` with `  local rec=$1 f log out line id c lines recs=() l2 p`.
    - Immediately before the line `  print -r -l -- $recs "time $(date -u +%Y-%m-%dT%H:%M:%SZ)" "scripts $SC" > $f.tmp && mv $f.tmp $f || { MSG="${f:t} could not be written"; return 2; }`, insert:
      ```
        for line in $recs; do                          # the pause (draft 6, DA2), written before the settle record (e1_r2, DC-O1)
          id=${${=line}[2]}
          for l2 in $VMS; do p=(${=l2}); [[ $p[1] == $id && $p[2] == invalid ]] && print -r -- "$id failed=$p[3]" >> $ST/pause_pending.txt; done
        done
      ```
  - `queue.sh`: replace `      invalid) echo "RUN $id INVALID failed=$fl"; print -r -- "$id failed=$fl" >> $ST/pause_pending.txt;;` with ``      invalid) echo "RUN $id INVALID failed=$fl";;   # its pause line was written by `settle` (e1_r2, DC-O1)``. In its comment, replace `# The runs an attempt's launch log names, as the VM's checks.json says them; an invalid one is written to` / `# state/pause_pending.txt (draft 6, rule F e1_r1 DA2), which the next launch turn shows and sets aside.` with `# The runs an attempt's launch log names, as the VM's checks.json says them; `settle` has written each invalid one to` / `# state/pause_pending.txt (draft 6, DA2; e1_r2, DC-O1), which the next launch turn shows and sets aside.`
- **Sandbox.** Before `echo "--- every stop"`, add:
  ```
  echo "--- review e1_r2: the queue dies between settle and report_settled"
  reset
  case_ "the sweep launched by hand" "ENDED sweep attempt 1" 0 FAKE_FAIL="2:recorder" zsh $L sweep
  case_ "settled by hand, as if the queue died before report_settled" "SETTLED-BY-HAND" 0 zsh -c "source $S/common.sh; mac_checks && next_step && [[ \$ACT == settle ]] && settle \$ARG && echo SETTLED-BY-HAND"
  case_ "the restart still pauses before the rerun" "QUEUE STOP after an invalid run" 1 zsh $Q
  chk "no rerun launched before the pause" is "$(launches)" 1
  ```
  188 of 188 with the fix. A death after the append but before the settle record leaves a duplicate pause line, which is harmless.

**DC-O2. Launches that leave no run spend attempts with no stop.**
- **Trace.**
  - A fault that stops the harness before its first folder (a failed `uv run`, a held `.run.lock`, an ssh failure on the launch command) leaves a launch log with no `run_id` line. Each such launch is an attempt.
  - The queue stops after each one (rc 2 or 4), but README has no row for that stop. A habitual restart spends all 13–19 launches, and E1 ends with six holes and no GPU time spent.
- **Code** (`common.sh`, `next_step`; tested with three new sandbox checks, 188 of 188).
  - Replace `  local rec f stem line l2 parts id c r rate name s att n a ids valid inval lost=() stopper="" n_heat=0` with the same line plus ` n_norun=0`.
  - After the inner `done` of the settled-records loop, that is, after `      per[$r]=$id; NAMED[$id]=$stem` / `    done`, insert `    grep -q '^rid ' $f || n_norun=$((n_norun + 1))   # a launch whose log names no run (e1_r2, DC-O2)`.
  - After the `MAX_SAME` loop's `    done`, insert `    (( n_norun < MAX_SAME )) || { MSG="$n_norun launches of E1 named no run (no run_id line in their logs): a question about the harness or the VM, not a rerun. E1 stops; the owner decides"; return 2; }`.
  - Sandbox case: `DCO2_test_sandbox.patch`.
- **Text.**
  - Anchor: `Any `no_errors` in `failed` stops E1 (the details that would separate a client error from another are not read).`
  - Append: ` A launch whose log names no run (no `run_id` line: its command failed, or the harness stopped before its first folder) spends its attempt; a second such launch, at any rate, stops E1 for a new decision.`

**DC-O3. README is not frozen by `mac_checks` (only the six scripts and `e1_commit.txt` are), so its stale lines can be fixed instead of listed.**
- The stale lines are 5, 9, 39, 41, 52 and 85: the citations of draft 4, "Nothing here is committed or reviewed", and the step-4 heading without "(QUEUE DONE)".
- If DC-O1 or DC-O2 changes the scripts, also bring `queue.sh` lines 4–5 and `vm_checkout.sh` lines 6–7 up to the heading form `END19_PAT` requires.

**DC-O4. No E1 run's VM copy may be removed before E1's end entry.**
- **Why.** The queue stops when the Mac holds an E1 folder that the VM does not list (FILE(docs/probe/20261113_e1/ops/common.sh:217-219)). Rule 4's exception (2026-11-04) would otherwise allow the removal.
- **Text.**
  - Anchor: `Every run with a `checks.json`, valid or invalid, is copied and checksum-verified; a run without one is copied by a separate step.`
  - Append: ` No E1 run is removed from the VM before E1's end entry (the queue stops when the Mac holds an E1 folder that the VM does not list, FILE(docs/probe/20261113_e1/ops/common.sh:217-219)).`

**DC-O5. If REG-21 is withdrawn, E1's result can never be computed (owner-proxy N4).**
- **Text.**
  - Anchor: `and E1's result is computed after it.`
  - Append: ` If an entry withdraws REG-21, E1's result is the worktree floor and `e1.observed()` without the work rates, by a [DECISION] entry made before it is computed.`

---

### The start gate, with the 4611 entry (asked by the lead)

**Sound.**
- `git grep -n -E "$END19_PAT" HEAD -- docs/decisions.md` has exactly one hit, at 302d431 and again at 08817af (after REG-21's and REG-22's 11 700 appended lines): line 4611, `## 2026-11-13 · [OPS] REG-19: the queue ended (QUEUE DONE)`. The UTC date matches the commit time (22:18 UTC).
- The entry quotes `QUEUE DONE (all five seeds run). Next: final.sh, once`, as the ID line requires. That line is one of ops_r3's two end lines (FILE(docs/probe/20261113_reg19/ops_r3/queue.sh:91)). The same queue lines are quoted in FILE(docs/decisions.md:4571); I did not open the queue output file it cites.
- After QUEUE DONE, REG-19 has no run left by its own rules (seed 19's `'continue': False`).
- What remains of REG-19 does not need the VM's tree:
  - `final.sh` runs on the Mac, from the worktree at the pin.
  - Its `links_ok` links only REG-19's folders into a real `runs/` and refuses anything else (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:88-102)), so E1's copied folders are never seen by REG-19's unsealed a7bb77a code.
  - Its recheck uses REG-19's pattern only.
  - Applying E1's code at the approval commit keeps the working tree equal to HEAD, which `recheck_ok` requires (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:207)), as long as it is committed and not left in the working tree.
- The gate is a heading pattern and is now permanently open. Three independent guards keep REG-19 and E1 apart afterwards:
  - REG-19's lock is tested at every queue start and before every launch (`launch.sh` calls `ready_to_run`).
  - The tmux check.
  - The tree check: REG-19 launches only at `a7bb77a`, and E1 only at its own commit.
- The restated heading was written to fit the gate (it says so). That is honest, and the event it points to is recorded with its quote in 4571.

**Residual.** The gate only answers "has REG-19 let go of the GPU". The converse, other registrations waiting for E1, is DC4.

---

### Were DA1–DA12 and DB1–DB12 applied, and do the merges keep both?

- **Verbatim.** DA1, DA2, DA3, DA4, DA5 (text), DA6, DA7, DA8, DA10, DA11 and DA12 are verbatim (checked against the round-1 text quoted in the draft).
- **DA9.** "18 launches" → "18 runs" is a correct departure. 18 runs take 13 launches when the sweep starts every rate, and 19 when it starts none (DERIVED: 1 + (6 − k) × 3 + k × 2 launches for k rates started).
- **Optional DA items.** DA-O1, O2, O4, O5, O6 and O7 are applied as given. DA-O3 is not taken, with its reason stated.
- **DB items.** DB1–DB9 are applied. DB9(a) is rewritten, as listed. DB10–DB12 are deferred to the approval commit.
- **Merges.**
  - DA1+DB4: both kept. The claim "every case DB4 stops, the scripts stop too" holds: a check at two rates means two runs, so `MAX_SAME` or the heat rule fires, and `no_errors`/`power_limit` stop at once.
  - DA4+DB6: both kept, but their link specifications conflict (DC3).
  - DA7+DB3: kept, but both understate what E1 changes (DC1).
  - DA-O7+DB10(iii), DB2+DA-O2, DA9+DB7: fine.
- **Item map, "Found while applying".** Items 1 and 6 are correct and benign. Item 2 is DC5. Item 3 is for the owner-proxy. Item 4 is DC6. Item 5 is DC-O1. Item 7 is DC8.

### Do the scripts do what the stopping rule says?

- **Attempt counting.** The sweep counts as attempt 1 for each rate whose `run_id` line it has, and every single-rate launch is one attempt. Records are numbered and checked (common.sh:240-254).
- **The sweep is launched at most once.** `attempt_sweep_1.txt` gates it, and folders or records before it stop the queue.
- **Global stop.** `no_errors`/`power_limit` in any run, a second `gpu_steady` over all runs, and `MAX_SAME` for any other check over all runs all stop E1. When every rate still without a valid run is already spent, the queue prints QUEUE END instead (item map finding 6). Nothing is launched either way.
- **Spent rates** do not hold back the others.
- **The pause.** It survives other stops, and `launch.sh` by hand refuses while it is pending. The one residual gap is DC-O1.
- **Two valid runs:** both are listed, nothing is launched, and the earliest is marked.
- **The commit check** is taken from the start line. `git_commit` comes from FILE(harness/run.py:143), printed by FILE(harness/run.py:80); a missing value fails safe.
- **Copying.** Every run with `checks.json` is copied, the sha256 lists are compared, and the copy record is written after the manifest. `tools/manifest.py` reads bytes only.
- **Sandbox:** 184 of 184 in my scratch run.

### Reads beyond `valid`/`failed` and the allowed log lines

None by the scripts:
- `vm_state.py` prints only `valid` and `failed`.
- `'run_id': '` appears on one harness print only, `ev("start", run_id=…, git_commit=…)`. All 16 `ev(` calls in `harness/run.py` were checked. The `[run] checks` line prints `valid` and `failed` only (FILE(harness/run.py:219)).
- `copy_verify` prints a file count and a hash of hashes.
- The pre-launch read is GPU state before the launch.

What the allowed reads still show:
- The `LAUNCHED`/`ENDED` times and the run-id gaps (DA8's bit, disclosed).
- With DC5, the same bit in two failure fields.
- With DC1, that bit is information about E0's input before E0's gate is fixed, which E0 must disclose.

### Cost arithmetic

- **2.1 h:** 6 × 1260 s = 7560 s. Every rate's schedule ends at 899.2–900.0 s, the drain deadline is t_planned max + 300 s (FILE(harness/loadgen.py:209)), and REG-8's saturated runs started 1262–1264 s apart (FILE(docs/decisions.md:1748-1751)).
- **4.2 h** with one rerun per rate. **At most 18 runs, 6.3 h (22680 s).**
- **Launches:** 13 to 19 for 18 runs; the extra launch is a sweep start that failed before its first rate, which costs at most the server start.
- **What the stops do to the ceiling.** With `MAX_SAME` and the heat rule, the 4.2 h case already needs six invalid runs with six different check names. The practical ceiling is well below 6.3 h, so "every other stop only lowers that ceiling" holds.

### FILE tags

All checked and correct:
- decisions.md: 4037, 4040, 4200, 4201, 4205, 4209, 4233, 4287, 4400, 4506, 4516, 4520, 1745-1751.
- reg19_resume_decision_draft5.md:41.
- ops_r3: final.sh:2, launch.sh:45, common.sh:11, queue.sh:54-60.
- agent/RUNBOOK.md:48.
- harness: checks.py:127, run.py:80 and :143.
- configs/base.yaml:55.
- tests/test_e1.py:59.
- E1's scripts: common.sh:24, :40, :98-108, :104, :187, :235, :260-262; queue.sh:44, :67-70; launch.sh:27.

Not checked: the RUN tags and the cold spans of 1.73–1.81, which need run reads; the replay floors 1.744/1.771, which need an analysis call.

---

### Strongest alternative explanation for the floor E1 would report

The floor will be read as the 8-turn closed-loop server's cold capacity, and through E0 as the denominator of the 8-turn window ratio. The strongest alternative is that it differs from 1.681, and from what a 16-turn sweep reports, mostly because of what is counted.

- **The mix.**
  - Closed loop serves early, short turns first, so completions per second rise with the load at a fixed token rate (FILE(tests/test_e1.py:59); BELIEF as to the model). The 16-turn closed loop tilts by a different amount.
  - E0's ratio of two req/s floors therefore mixes capacity with counting. A "widens" or "does not widen" label could come from the served mix, not from the cost gap K2 is about.
  - **Separating evidence:** the token work rate U per saturated row at 8 turns (reported, `e1.work_rates`) against its 16-turn counterpart. Equal U with different req/s floors means counting. E0's registration should state R also on U-based floors, or say why not.
- **Drift within an ascending sweep.**
  - At 350 W the GPU warms over two hours of back-to-back runs, and the SM clock can fall with it. That lowers the high-rate rows and the slope.
  - REG-8 ran in the same order but on another day.
  - **Separating evidence:** the busy SM-clock mean per run from `gpu.jsonl`, which is not registered.
- **For the margin use.**
  - A cache-off floor is not the capacity of a cold cache-on server, which still hits on whatever prefix survives. So λ ÷ floor at λ = 2.0–2.2 overstates how far the cold state sits below its own capacity.
  - **Separating evidence:** the hit rate of the cold spans on record, already measured.

### Can E1 change any decision, and is it worth its GPU hours?

- **Yes, three.**
  - (1) E0's gate, through f8 (DC1). Under the committed code, an E1 without a floor makes the 16-turn label "missing".
  - (2) Whether the next registration may run on 5ee6e38's harness (DA7).
  - (3) K2's wording and the closed-loop margins.
- **Worth 2.1 GPU h:** yes. It is K2's 8-turn reference, which the owner's plan requires. It is the first GPU exercise of the A14 recorder and the stricter checks. And the GPU is otherwise idle until REG-19's [RESULT].
- **But only on DC1's terms.** Run before E0's gate is registered, its floor must stay unseen until that gate exists. Otherwise the run's main decision value turns into a rule-A5 problem for E0.

### Verdict

**NOT READY.**
- **Blocking, apply first:**
  - DC1 (text; E0 dependency and its A5 guard).
  - DC2 (code and tests in `analysis/e1.py` and `tests/test_e1.py`, patches in scratch, 16 passed; "holes" changes, so the owner-proxy must pass it).
- **Required, not blocking (verbatim):** DC3, DC4 (with its RUNBOOK and README edits in the approval commit), DC5 (the owner-proxy rules on the wider reads), DC6, DC7, DC8 (inside DC2's patch) and DC9.
- **Optional:** DC-O1 to DC-O5. If DC-O1 or DC-O2 is taken, the scripts change and need the sandbox rerun and the owner-proxy's pass.
- **Next round.** DC2 is a code change, so the review-stop rule calls for one more rule F round on the new bundle. That round can be limited to DC1's text and DC2's patch.

Review file: /private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/d3f64482-d0cf-4bf8-9ad1-c1dc026c562c/scratchpad/rulef-e1-draft6-r2.md
