# proxy-e1-draft6 (proxy-e1-d6), verbatim

Saved by the agent from the reviewer's own verdict file (its session 1a592fe9, scratchpad `proxy-e1-draft6.md`, 24165 bytes, sha256 cc3a73b8aabbc2b9f4e2d1073ddf333345a5724d30af35ac1d99e58d224e90f1, checked on copy), which the reviewer sent in three SendMessage parts (its transcript lines 585, 595 and 605, 2026-11-13T22:36:23.695Z, 22:36:55.532Z and 22:37:12.664Z); each part's body, less its "[Part n of 3]" line and part 3's closing file line, is a substring of the file (checked by script, 2026-11-13 22:38 UTC). The owner-proxy pass on E1 draft 6 (round 2, bundle e1_r2).

---
# Owner-proxy on E1 draft 6 (review round 2, bundle e1_r2)

**Verdict: APPROVE, on conditions DD1–DD12.**
- DD1–DD7 are BEFORE: they are applied before the `[REG] E1` entry is appended. DD7's two files are committed with the entry.
- DD8–DD12 are LATER: they go into the approving `[DECISION] (delegate) E1 approved` and its commit. DD9 comes after `e1_commit.txt` is set and before `vm_checkout.sh` runs.
- This approval also needs rule F round 2 to return READY (the delegation's condition (a)). If round 2 asks for changes, §3 says which ones need another pass from me.
- None of DD1–DD12 changes code, a rule, a threshold or a config. DD6 narrows a read the draft allows. The rest are wording, disclosures, reporting duties, one prediction and procedure. So they need no new rule F code round.
- If a round-2 item changes an anchor's text first, apply the DD to the same sentence as changed, keep round 2's words, and say so in the [REG]'s change list. That needs no new pass unless §3 lists the change.

## What I checked (0 GPU h; nothing written in the repo)
- **Bundle.** MANIFEST: 41 of 41 sha256 lines OK. The bundle is committed in 97a6438 and has no uncommitted change. Every file in `ops/` is byte-equal to the main checkout's `docs/probe/20261113_e1/ops/`.
- **Sandbox.** `TMPDIR=<my scratchpad> zsh docs/probe/20261113_e1/ops/test_sandbox.sh` gave `passed 184, failed 0`. `git status --short` was the same before and after.
- **Code (scratch copy from `git archive HEAD`; the repo's `.venv` interpreter).**
  - Both patches apply. The results are byte-equal to the bundle's `e1.py` (sha256 `615e386f…`) and `test_e1.py` (`23672c2a…`).
  - `pytest tests/test_e1.py -q`: 16 passed.
  - The patched tests against HEAD's `e1.py`: 3 failed (the DA6, DA-O4 and DA-O6 tests) and 13 passed, as the item map says.
  - `tests/test_k2.py tests/test_withheld.py tests/test_e1.py` on the patched copy: 39 passed. `analysis/k2.py` is the only module that imports `e1`.
  - `git apply --check` of both patches against the main checkout passes. Nothing was applied.
- **Closures** (`docs/probe/20261113_freeze/closure.py --at HEAD`, a static `ast` reader).
  - `analysis/e1.py`: 24 .py files plus 3 environment files.
  - `e1.py` is in neither `k3w.py`'s closure (26 files) nor `c2.py`'s (27). The patch changes no import.
- **DB1–DB9, checked by script against the review text.**
  - DB2, DB3, DB4, DB5(b) and DB6's added text (after DA4's sentences) are in draft 6 character for character.
  - DB5(a)'s test is verbatim in the patched `test_e1.py`.
  - DB8: the quoted block, unquoted, equals `rulef-e1-draft5-r1.md` byte for byte.
  - DB9(b)'s row is in `README.md` verbatim.
  - DB1 is the placeholder `<date of append>`.
- **Draft 5 → 6.**
  - The word diff outside the quoted review has no change that the item map does not list.
  - The script diffs against e87884d are DA1, DA2, DA12, DA-O1, DA-O2 and comments, nothing else.
- **Citations rechecked.**
  - decisions.md 1744, 4037, 4040, 4200, 4201, 4205, 4209, 4233, 4287, 4400, 4506, 4516, 4520.
  - E1 `common.sh` 24, 37, 40, 98–108, 104, 187, 235, 260–262; `queue.sh` 44, 67–70; `launch.sh` 27.
  - ops_r3 `final.sh:2` and `common.sh:207`; `agent/RUNBOOK.md` 48 and 50.
  - The ten field names of DA7 are in `harness/checks.py`'s `recorder` and `gpu_steady` details.
- **The start gate as it stands.**
  - decisions.md:4611, `## 2026-11-13 · [OPS] REG-19: the queue ended (QUEUE DONE)`, matches `END19_PAT`.
  - REG-19's lock is absent: names only, from the session's git status (`queue.lock.ended_*` only) and the entry's own `test -e`.
- **REG-19's `final.sh` beside E1.**
  - It runs on the Mac.
  - It links only `*_stage2_control_…_s1[5-9]` and `*_burst_…_s1[5-9]`, and rechecks only `*_l1pl350cl_r2.0_w3000_s1[5-9]`. No E1 folder matches either pattern.
  - It needs the Mac's `analysis/` to equal HEAD (ops_r3 `common.sh:207`). So E1 can stop it only if the patches sit uncommitted (DD7).
- **REG-20's commit.** REG-20's approval commit 75e627e is older than 5ee6e38, and 5ee6e38 is not in a7bb77a (git, commit order only).
- **Not opened:** `runs/` beyond names, any `state/` file, RESUME.md, `docs/paper/`, queue outputs, launch logs, transcripts.
- **Not done:** no VM contact, no `analysis.*` command, no full pytest.

## 1. Would the owner approve registering and running E1 now, as written in draft 6?
**Yes, with DD1–DD12, once rule F round 2 is READY.**

**Value.**
- The owner decided that this sweep "is run in any case" (FILE(docs/decisions.md:4037)).
- DA7 adds a decision that matters beyond wording. E1 is the first GPU test of the harness that every later registration on HEAD will use.
- The GPU has been idle since 21:49 UTC on 2026-11-13, with nothing else approved. The owner said: "whenever its available use it" (FILE(docs/decisions.md:4506)).
- The cost is 2.1 GPU h, with a ceiling of 6.3 h, and DA1's stop keeps a broken harness near the 2.1.

**No harm to other items.**
- REG-19: its table is computed on the Mac and does not read E1's folders, and its VM folders are untracked.
- REG-21 and REG-22: `e1.py` is outside both closures.
- REG-20: unaffected. Its commit question exists already (N5).

**My round-1 conditions.** Each is met as given, or with a departure I accept:
- **DB5(c), "16 tests":** accepted. The three added tests are the repo's only check of DA6, DA-O4 and DA-O6.
- **DB7 merged into DA9, with "runs" for "launches":** accepted. 18 runs × 1260 s = 6.3 h (DERIVED), in 13 or 19 launches.
- **DB9(a) rewritten:** accepted. DB9's premise (the scripts stay unchanged) fell when DA1, DA2, DA-O1 and DA-O2 changed them. `README.md` is not among the frozen `SCRIPTS` (`common.sh:37`).
- **DB4 with DA1:** accepted. I traced `next_step`. A check name at two rates means at least two runs with it:
  - `gpu_steady` gives `n_heat` ≥ 2, the heat stop;
  - `no_errors` or `power_limit` sets `stopper`;
  - any other check gives `nfail` ≥ `MAX_SAME`.
  So the code stops in every case DB4 stops.
- **DB6 with DA4, DB2 with DA-O2, DB3 with DA7:** consistent; accepted.
- **Other departures:** DA10's renumbering, DA12's further comment updates, and DA-O1's and DA-O2's added sandbox cases, messages and `[CORR] (owner) E1 halted` form. Accepted: they can only stop more, and the sandbox passes.
- **DA-O3 not taken:** accepted (N3).

**What the item map left for this pass.**
- **Item 3, DA7's detail reads before E1's [RESULT]:** accepted, scoped by DD6.
  - The floor's code is frozen (DA4, DB6), so no analytic choice remains that a peek could steer.
  - After a stop that ends E1, the scripts refuse every launch.
- **Item 2, `end_ref_t` carries DA8's bit:** disclosed by DD6.
- **Item 4, the result's text:** the text is wrong, and DD3 makes it match the code.
  - It says `e1.report` prints "the tilt with its prediction", but `report` never calls `prediction()`.
  - It says the open-loop floor is recomputed "the same way", but `floor_ol` is `saturated(ol)`.
  - The tilt is absent unless both sweeps are `ok` under `gate.cold_floor`.
- **Item 5, DA2's two-statement window:** accepted (N10).
- **Item 6:** no change.
- **Item 7, the docstring:** N7.

**New finds.**
- **F1.** The validity record, the one decision DA7 adds, has no numeric prediction (rule A1; `docs/process.md` §2's template). Fixed by DD4 and DD11.
- **F2. "Holes" is not monotone in the data.**
  - 1.5 valid and kept up, 2.0 without a valid run, 2.5–4.0 saturated: "holes".
  - 1.5 and 2.0 both without a valid run: "ok" from 2.5.
  - The second case is likelier now that DA1's stop can end E1 with several rates unrun.
  - No selection on outcomes follows, since validity comes from checks, so DD5 discloses it and does not change code (N8).
- **F3.** The result's text, as above (DD3).
- **F4. A circular reference.** DA4's closure and DA11's `git diff` are to be run "at <registered commit>" and quoted in the approval entry. But that commit is the one that contains the entry. DD8 quotes both from the staged tree, and DD9 repeats them at the commit before the VM moves.
- **F5. When the patches are applied, and REG-19's guard.** DD7.
- **F6. Untracked REG-19 state files.** The main checkout holds untracked REG-19 state files (recheck and step outputs, launch outputs; names only), so the registration commit must name its paths (DD12).

## 2. Conditions

**DD1 (BEFORE): rule F round 2, verbatim.** Insert immediately before the line `#### Owner-proxy pass`:
- a section headed `` ### Adversarial review, round 2 (rule F, `docs/process.md` §3), verbatim ``. It holds the full text of rule F's round-2 review of draft 6 (bundle e1_r2), each line prefixed "> " as round 1's is, including any header the agent adds when it saves the review;
- then `#### What was changed because of it (round 2)`, item by item, naming every departure from the reviewer's words.

If round 2 is not READY, the entry is not appended.

**DD2 (BEFORE): this pass, named.** Anchor:
```text
draft 6's script, holes and stopping-rule changes need another owner-proxy pass (its §3).
```
Replace with:
```text
draft 6's script, holes and stopping-rule changes need another owner-proxy pass (its §3). Owner-proxy on draft 6 (round 2; `<path where this verdict is saved>`): **APPROVE on DD1–DD12**; DD1 (rule F round 2, verbatim, above), DD2 (this line), DD3 ("Result, computed once"), DD4 ("Prediction"), DD5 ("Holes"), DD6 ("In neither case") and DD7 (the two patches, applied in this commit) are applied in this entry; DD8–DD12 belong to the approval commit and the steps after it.
```
The placeholder is filled with the saved file's path, as DB1's date is.

**DD3 (BEFORE): the result's text matches the code.** Anchor:
```text
the open-loop floor recomputed the same way; the common onset; the tilt with its prediction; the work rates of both sweeps.
```
Replace with:
```text
the open-loop floor of REG-8's sweep recomputed by REG-8's own rule (`floor_ol`: `e1.saturated`, that is `gate.cold_floor` with REG-8's settings; neither E1's tail fallback nor its holes check applies to it); the common onset; the tilt (`tilt_reported`, present only when `gate.cold_floor` gives "ok" on both sweeps, since otherwise there is no common onset); the work rates of both sweeps. The tilt's prediction is not in this output (FILE(analysis/e1.py), `observed` and `report`): `e1.prediction()` replays the two configs through model F's server and reads no run; it is computed once beside the result, from the same code, with `uv run python -c 'import json; from analysis import e1; print(json.dumps(e1.prediction(), default=str))'`, and reported as the tilt's description.
```

**DD4 (BEFORE): a number for the validity record (rule A1).** Anchor, in "Prediction (BELIEF)":
```text
RUN(20261110-063647_burst_l1pl350cl_r2.2_s2, gate.reg14_gate)).
```
Replace with:
```text
RUN(20261110-063647_burst_l1pl350cl_r2.2_s2, gate.reg14_gate)). The status figures assume a valid run at every rate. **E1's validity record** (the decision under "In neither case"; rule A1 asks for a number): P(clean: every launched run ends with a `checks.json`, and neither `recorder` nor `gpu_steady` is in any run's `failed`) ≈ 0.7; P(not clean) ≈ 0.3, of which a run lost to a power-off ≈ 0.2 and a `recorder` or `gpu_steady` failure ≈ 0.1. BELIEF: the VM went off twice during REG-19's runs, at 15:51 UTC on 2026-11-12 and at 04:39 UTC on 2026-11-13, and every boot end the journal keeps was a power-key press (FILE(docs/decisions.md:4383); open question A18); no run of REG-8's cache-off sweep failed a check (FILE(docs/decisions.md:1744)), and the recheck of 182 folders under the new checks changed no valid verdict (FILE(docs/decisions.md:4205)), but no GPU run has used the new recorder.
```
The three numbers are this pass's BELIEF. The agent may put its own numbers in their place before the entry is appended, if it states its basis in the same sentence. Any number serves rule A1, provided it is written before the run.

**DD5 (BEFORE): the holes case that fewer runs pass.** Anchor:
```text
with no valid run gives the status "holes" and no floor (the floor would average over a gap); the missing rates are listed.
```
Replace with:
```text
with no valid run gives the status "holes" and no floor (the floor would average over a gap); the missing rates are listed. A swept rate below λ_sat with no valid run, when no valid row lies below λ_sat (for example 1.5 and 2.0 both without one), is not a hole (FILE(tests/test_e1.py), `test_a_hole_just_below_lam_sat_is_a_hole`): the floor is then reported from λ_sat, and the [RESULT] says that λ_sat may lie lower and that the floor, a mean over rates on which closed-loop throughput is predicted to rise, would then be lower. This is the one case in which fewer valid runs give a floor where more would give "holes" (1.5 valid and kept up, 2.0 without a valid run); it is disclosed, not changed, so that the code rule F reviewed is the code that runs. The stop on a check in `failed` of two runs makes it likelier, since E1 can then end with several rates unrun.
```

**DD6 (BEFORE): DA7's reads, scoped and disclosed.** Both anchors occur twice. Apply each to its **first** occurrence, the entry's bullet `- **In neither case**`. The second occurrence is inside the quoted round-1 review, which stays verbatim.

(a) Anchor:
```text
After E1's queue has ended, only these fields of a failed check may be read for that:
```
Replace with:
```text
After E1's queue has ended (it printed `QUEUE DONE` or `QUEUE END`, or stopped on a rule that ends E1: `no_errors` or `power_limit` in a run's `failed`, a second `gpu_steady`, one check in `failed` of two runs, or the owner's halt), and only for the runs that have that check in `failed`, only these fields of a failed check may be read for that:
```
(b) Anchor:
```text
None of them holds a request count, throughput or KV. If every run is valid,
```
Replace with:
```text
None of them holds a request count, throughput or KV, but `end_ref_t` and `last_ok_scrape_t` show when that run's load ended, so they carry the same one bit per rate as the run ids (the stopping rule, "Disclosed"). The read is one command that prints these fields and nothing else; the command and its output are quoted in the [OPS] or [CORR] entry that records the cause, and the [RESULT] lists every such read. If every run is valid,
```

**DD7 (BEFORE; the files are committed with the entry): the two patches.**
1. In the main checkout, and never while REG-19's `final.sh` is running, run `git apply docs/drafts/review_bundles/e1_r2/e1_draft6.patch docs/drafts/review_bundles/e1_r2/test_e1_draft6.patch`.
2. `shasum -a 256 analysis/e1.py tests/test_e1.py` must print `615e386f201734b686550918c601bfd85ecaea1d2aedd5fd51c7b62c6ee53c94` and `23672c2a81d9203186645046b5a6bee2d6a048dd68132c08721ea5f30643de9e`.
3. `uv run pytest tests/test_e1.py -q` must give 16 passed.
4. `uv run pytest` must pass in full. REG-22's batch command will require that (FILE(docs/drafts/reg22_draft18.md:131)).
5. Both files go into the registration commit, so `analysis/` and `tests/` are clean again at that commit.

`final.sh` is not started between the `git apply` and that commit. Its recheck refuses while `analysis/` differs from HEAD (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:207)).

**DD8 (LATER): what the approving decision also holds.** DB10 (i)–(iv) stand as given. In addition, the entry:
- (a) carries both owner-proxy verdicts on E1 verbatim: round 1 (`docs/drafts/reviews-2026-11-13/proxy-e1-draft5.md`) and this one;
- (b) names rule F round 2's verdict and file;
- (c) quotes two outputs, run in the working tree with the registration commit's content staged and nothing else changed in these paths. DD9 repeats both at the registered commit, and the entry says so. The two outputs:
  - `python3 docs/probe/20261113_freeze/closure.py analysis/e1.py` (DA4);
  - `git diff --quiet 9e249b1 -- harness/ pyproject.toml uv.lock .python-version configs/defaults.yaml configs/base.yaml configs/gap5_base.yaml configs/l1_base.yaml configs/l1_pl350_base.yaml configs/sweep_l1pl350_pc_off.yaml configs/sweep_l1pl350cl_pc_off.yaml 'configs/sweep_l1pl350cl_pc_off_only_r*.yaml'; echo $?` (DA11), which must print 0;
- (d) lists the departures from round 1's words that this pass accepted: DA9's "runs", DA10's renumbering, DB5(c)'s 16 tests, DB7 merged into DA9, DB9(a) rewritten, DA12's further comment updates, DA-O1's and DA-O2's added sandbox cases and messages, and DA-O3 not taken;
- (e) states this pass's ruling on DA7's detail reads, which are allowed as DD6 scopes them.

**DD9 (LATER; after `e1_commit.txt` is committed, before `vm_checkout.sh` runs): the two checks, at the registered commit.**
- Run `python3 docs/probe/20261113_freeze/closure.py --at <E1 commit> analysis/e1.py`. It must print the list the approval entry quotes.
- Run `git diff --quiet 9e249b1 <E1 commit> -- <the paths of DD8 (c)>; echo $?`. It must print 0.
- `<E1 commit>` is the hash in `e1_commit.txt`.
- Both outputs are quoted in the [OPS] entry that commits `vm_checkout.sh`'s probe file.
- If either differs, `vm_checkout.sh` is not run, and the registration goes back to rule F.

**DD10 (LATER, in the approval commit): RUNBOOK.**
- Apply the item map's merged proposal verbatim, both (a) and (b), in place of DB11. The proposal is in `docs/drafts/e1_draft6_itemmap.md`, under "RUNBOOK: one proposal for the approval commit".
- Its anchors are at FILE(agent/RUNBOOK.md:50), the §4 heading, and FILE(agent/RUNBOOK.md:48), `then deploy HEAD (§4); then`. Both were checked at HEAD.

**DD11 (LATER, same commit, before the first launch): the ledger row, in place of DB12's.** Append after the last row of the prediction ledger in `docs/model.md`, numbered as the next free row:
```text
| <n> | <date> | Model F's replay and the closed-loop cold spans on record (E1: closed-loop cache-off sweep of L1 at 350 W, rates 1.5–4, seed 0) | Status `ok` ≈ 0.75, `tail_ok` ≈ 0.2 (neither ≈ 0.05, DERIVED), given a valid run at every rate; floor 1.70–1.80 req/s; model F's replay of E1's config at μ = 1.681 over rates ≥ 2.0: 1.744 (fixed cost) or 1.771 (proportional), `k2.closed_loop_floors` (BELIEF as to the model). Validity record clean ≈ 0.7 (a run lost to a power-off ≈ 0.2; `recorder` or `gpu_steady` failing ≈ 0.1; BELIEF) | — | Open | decisions.md <date> [REG] E1 |
```
If the agent replaced DD4's numbers, this row carries the agent's numbers.

**DD12 (LATER): the registration commit's paths.**
- The commit that holds the [REG] and the approval is made with named paths only: `git add <path> …`, never `git add -A`, `git add .` or `git commit -a`.
- Its paths: `docs/decisions.md`, `analysis/e1.py`, `tests/test_e1.py`, `agent/RUNBOOK.md` and `docs/model.md`, plus the session files (`docs/status.md`, `docs/context-pack.md`, `agent/STATE.md`, `agent/LOG.md`, and the saved reviews under `docs/drafts/reviews-*/`).
- It adds nothing under `runs/`, `docs/probe/20261113_reg19/` or `docs/probe/20261113_e1/ops/state/`.
- It leaves `docs/probe/20261113_e1/ops/` as it is at 97a6438, with `e1_commit.txt` still `UNSET`.
- Reason: REG-19's untracked state files are in the checkout, and REG-19's own rule commits its table files at once and alone.

## 3. Later changes that would need another owner-proxy pass
- Any change to code, comments included:
  - the six frozen scripts (`common.sh`, `vm_state.py`, `session_probe.sh`, `launch.sh`, `queue.sh`, `vm_checkout.sh`);
  - `analysis/e1.py` beyond the bundle's patched file;
  - `tests/test_e1.py` beyond added tests;
  - any change to `e1_commit.txt` other than README step 3.
  A docstring-only fix of `e1.py` (N7) needs no owner-proxy pass, provided a rule F round has seen it.
- Any rule F round-2 item that changes:
  - the stopping rule (attempts, the heat rule, `MAX_SAME`, `no_errors` and `power_limit`, the pause, DB4's restart rule, the lost-run stop);
  - the floor, the tail fallback, "holes", `first_valid`, or REG-8's settings;
  - the allowed reads, including DA7's fields as DD6 scopes them;
  - the start gate (`END19_PAT`, the lock, the halt), the approval heading;
  - E1's configs, rates or seed;
  - the cost ceiling.
- Adopting DA-O3, or any rerun allowed in advance after a lost run.
- Reading any E1 run beyond `valid`, `failed` and DD6's fields before E1's [RESULT]. Computing or quoting any part of E1's result before REG-21's first [RESULT].
- Any move of the VM other than `vm_checkout.sh` forward to E1's commit, such as a move back to `a7bb77a` or to REG-20's commit. Each needs its own entry and is outside this approval.
- A failure of DD9's two checks. The registration then goes back to rule F, and then to me.
- **No new pass is needed for:**
  - applying DD1–DD12 verbatim, or DD4's numbers replaced as DD4 allows;
  - DB1's date and DD2's path;
  - renumbered FILE citations;
  - [OPS] entries;
  - rule F round-2 items that are only wording, tags, citations, disclosures or stricter reporting duties.

## 4. Notes for the owner
- **N1. The pin clause.** E1's approval amends your REG-19 pin rule. The VM leaves `a7bb77a` at the recorded end of REG-19's queue, not at REG-19's [RESULT].
  - REG-19's table is computed on the Mac and does not read the VM's tree.
  - REG-19's VM folders are untracked and stay where they are.
  - You can reverse this with one entry. The cost is an idle GPU until REG-19's [RESULT].
- **N2. 350 W after any reboot.** The agent's `sudo -n` was refused, so each reboot (back to 420 W) stops E1 until you set 350 W. A NOPASSWD rule for `nvidia-smi -pl 350` would remove that step. It is a root action, so it is yours.
- **N3. Runs lost to a power-off.**
  - A run that ends without `checks.json` stops E1 until a new decision. DA-O3 would have allowed the next attempt in advance, and it was not taken. DD4 puts the chance of a loss during E1 at about 0.2.
  - You must come back to set 350 W anyway. When you do, the same entry can allow the lost rate's next attempt (`state/lost_ok_<run id>.txt`), as you did twice for REG-19 (FILE(docs/decisions.md:4284), FILE(docs/decisions.md:4383)).
  - Allowing it now, in advance, would change the stopping rule and needs a pass.
- **N4. The floor waits for REG-21.** E1's [RESULT], and the floor with it, waits for REG-21's first [RESULT], and E1's folders stay sealed until then.
- **N5. Which harness REG-20 runs on is not settled.**
  - REG-20 is registered with "clean tree at the registered commit". Its approval commit, 75e627e, is older than the A14 harness fix, 5ee6e38.
  - RUNBOOK §3 item 6 deploys HEAD before REG-20.
  - E1's validity record, which DA7 makes binding, bears only on HEAD's harness.
  - This conflict predates E1. Settle it before REG-20 runs.
- **N6. A crash cannot be diagnosed within E1's allowed reads.**
  - A run that ends without `checks.json` on an unchanged boot id leaves no allowed read that could find the cause. The launch log also holds the recorder's status lines, which are outcome data.
  - DA7 then holds every registration on this harness until the cause is recorded.
  - Only you can allow a narrow read, for example a traceback block, or decide otherwise.
- **N7. A stale docstring.** `analysis/e1.py`'s docstring still says "not yet registered: draft docs/drafts/e1_draft4.md". It is harmless. A fix can ride with any code change that rule F round 2 asks for.
- **N8. Making "holes" consistent would need code.** The fix: a missing rate below λ_sat is a hole whenever no valid row lies between it and λ_sat. That would also make "1.5 missing" a hole, which today's registered test calls "ok". It was not done here, to avoid another code round. DD5 discloses the case instead.
- **N9. E2 inherits this holes rule.** E2's between-sweeps flag (`floor_status`) uses the same `floor`, so it inherits DA-O4's holes rule. E2's registration must cite it.
- **N10. DA2's window.** If the Mac's queue process dies between `settle` and `report_settled`, the pause for that attempt is lost. The window is two shell statements, and DA1's stop and DB4's rule still bound a systematic fault. Left as is.
