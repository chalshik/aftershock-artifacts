# proxy-e1-draft5 (proxy-e1-d5), verbatim

Saved by the agent from the reviewer's own final text (its session 09632008, line 563, timestamp 2026-11-13T21:06:15.345Z), which the reviewer ended its turn with and did not send by SendMessage, so it never reached the main session (checked by the agent on 2026-11-13 21:33 UTC: no SendMessage call in that session). The owner-proxy pass on E1 draft 5.

---

**Verdict: APPROVE, on conditions DB1–DB12.** DB1–DB9 are BEFORE: they are applied before the `[REG] E1` entry is appended. DB10–DB12 are LATER: they go into the approving `[DECISION] (delegate) E1 approved` and its commit, before `vm_checkout.sh` runs.

## What I checked (0 GPU h; nothing written in the repo)
- **Bundle.** All 28 MANIFEST checksums pass. Every bundle copy is byte-identical to the repo at e87884d: `ops/`, `analysis/e1.py`, `tests/test_e1.py`, the 7 configs, and drafts 4 and 5. `harness_diff_a7bb77a_to_HEAD.diff` matches `git diff a7bb77a HEAD -- harness/` (sha 3b52b5e1…).
- **Sandbox.** `zsh docs/probe/20261113_e1/ops/test_sandbox.sh` gave "passed 170, failed 0". It ran in a temp dir in my scratchpad and the repo is unchanged.
- **Tests.** `uv run pytest tests/test_e1.py -q` gave 12 passed.
- **Single-rate configs.** I checked by hand, since no test covers this. Each `configs/sweep_l1pl350cl_pc_off_only_r<rate>.yaml` expands to one run, with name `sweep_l1pl350cl_pc_off_r<rate>` and `sweep_parent` `sweep_l1pl350cl_pc_off`. That run equals the sweep's own run at that rate in every key except `sweep`.
- **Citations.** Every line the draft cites says what the draft claims: decisions.md:4516/4520, 4200/4205; checks.py:127; base.yaml:55; run.py:143 (whose print format matches `settle`'s grep); ops_r3/common.sh:11; ops_r3/launch.sh:45.
- **REG-19 side.**
  - REG-19's queue moves its lock away on exit (ops_r3/queue.sh:28), so "no lock" does mean the queue ended.
  - QUEUE DONE and QUEUE END are its only terminal lines.
  - `final.sh` opens no ssh connection: the table needs nothing from the VM's tree.
- **Harness diff, cap off.** The load generator's paths are unchanged apart from per-line flushes. This is BELIEF from reading the diff, and agrees with the draft's R5.
- **Clean slate.** No E1 folder exists on the Mac (folder names only).
- **REG-19 still running or holding the GPU.** The session's git snapshot lists `ops_r3/state/queue.lock/` as present. That is existence only; nothing was opened. E1 cannot start yet.

## 1. Would the owner approve?
Yes, with the conditions below.

**Value.** E1 changes no run decision. But the owner already decided on 2026-11-12 that this sweep "is run in any case", "run whatever step B finds" (FILE(docs/decisions.md:4037), FILE(docs/decisions.md:4040)), and sent E1 to review knowing this (FILE(docs/decisions.md:4520)). So rule A1 does not bar it. The draft has to cite that authority (DB3) instead of leaving it open.

**Cost.** About 2.1 GPU h, with a ceiling the draft never states (≈ 6.3 h; DB7). The GPU would otherwise sit idle:
- REG-19's [RESULT] waits for REG-21 and REG-22.
- REG-20 waits for that [RESULT].

The owner said: "whenever its available use it" (FILE(docs/decisions.md:4506)).

**New start condition.** Starting at the recorded end of REG-19's queue fits what the owner said. But draft 5 never mentions the rule it overrides. The owner-approved REG-19 pin rule says: "The VM stays at `a7bb77a` with a clean tree until REG-19's [RESULT] is written" (FILE(docs/drafts/reg19_resume_decision_draft5.md:41), approved at FILE(docs/decisions.md:4287), kept at FILE(docs/decisions.md:4400)).
- The draft cites only the E1 entry's narrower wording at 4520, and `agent/RUNBOOK.md` §4 still says "never before REG-19's [RESULT]".
- The delegation does cover "the pin rule" (FILE(docs/decisions.md:4233)). So the change is allowed, but only as an explicit amendment the owner can see and reverse (DB2, DB10, DB11).
- Substantively the amendment is safe: no REG-19 run remains after DONE or END, and the table is Mac-only.

**Leaving `a7bb77a`.** Accepted. `runs/` is untouched by the checkout, and REG-19's launch refuses any tree but the pin. A REG-19 rerun would need a backward move, which `vm_checkout.sh` refuses; that is noted for the owner.

**First run on the new harness (R1–R6).** I accept option (a); a smoke run is not worth a registration on a GPU that is otherwise idle.
- R1 is bounded to one run.
- R3, which treats coverage failures as heat, is stricter, never looser.
- R2's bound has a gap. The queue pauses after an invalid run, but the draft never says when the queue may be started again. Restarting by habit would rerun a systematic fault for about 4.2 h more. DB4 sets the restart rule before any data, using only `valid` and `failed`.

**Standing rules.**
- Rule F's output must sit verbatim in the [REG] (the delegation's condition (a); process §3), which the draft has no section for (DB8).
- `docs/model.md` requires the prediction in the ledger before the run (FILE(docs/model.md:3)); there is no row yet (DB12).
- The judged floor should come from the registered code, per RUNBOOK §5, not from whatever `main` holds when REG-21 reports (DB6).
- "Checked when they were written" is an untagged claim (rule B); DB5 replaces it with a test.
- Several files are stale against draft 5: README and DESIGN_NOTES still cite draft 4 and `RESULT19_PAT`, and the header comments of `queue.sh` (line 4) and `vm_checkout.sh` (line 6) say E1 waits for REG-19's [RESULT]. The code is right. DB9 fixes this in the README only, so the reviewed scripts stay as they are.

## 2. Conditions

**DB1 (BEFORE): date of the heading.** In the line `## 2026-11-13 · [REG] E1: the closed-loop cache-off sweep of L1 at 350 W, which measures the 8-turn closed-loop cold floor (GPU, ≈ 2.1 h)`, replace `2026-11-13` with the UTC date on which the entry is appended. Nothing else changes.

**DB2 (BEFORE): the pin rule, named and amended.** Anchor in the ID bullet:
```text
The owner's entry forbids only a run while REG-19's queue holds the GPU (FILE(docs/decisions.md:4520)); draft 4's wait for REG-19's [RESULT] is dropped, since that result waits for two registrations that have no bearing on E1, and the GPU would sit idle meanwhile.
```
Replace with:
```text
The owner's entry on E1 forbids only a run while REG-19's queue holds the GPU (FILE(docs/decisions.md:4520)). REG-19's pin rule says more: "The VM stays at `a7bb77a` with a clean tree until REG-19's [RESULT] is written" (FILE(docs/drafts/reg19_resume_decision_draft5.md:41), approved by the owner as part of that plan, FILE(docs/decisions.md:4287), and kept unchanged by FILE(docs/decisions.md:4400)). **This entry's approval amends that one clause, under the delegation's "the pin rule" (FILE(docs/decisions.md:4233)):** the VM may leave `a7bb77a` once REG-19's queue has ended as recorded here, before REG-19's [RESULT]. The rest of the pin rule stands: REG-19's table is computed on the Mac from the worktree at `a7bb77a` (FILE(docs/probe/20261113_reg19/ops_r3/final.sh:2)) and needs nothing of the VM's tree. Draft 4's wait for REG-19's [RESULT] is dropped because that result waits for two registrations that have no bearing on E1, and the GPU would sit idle meanwhile; the owner: "whenever its available use it" (FILE(docs/decisions.md:4506)). If the owner restores the clause by a [DECISION] or [CORR] entry, E1 launches nothing further until REG-19's [RESULT] exists.
```

**DB3 (BEFORE): the rule A1 authority.** Anchor:
```text
If the owner holds that a measurement that changes no decision should not cost 2.1 GPU h, E1 should not run.
```
Replace with:
```text
Rule A1 and `docs/process.md` §3 say a run whose outcomes change no decision is not proposed. The owner has decided otherwise for this run: the L1 closed-loop cache-off sweep "is run in any case" (FILE(docs/decisions.md:4037)), "run whatever step B finds" (FILE(docs/decisions.md:4040)), and the owner sent E1 to review with this paragraph's content stated (FILE(docs/decisions.md:4520)). The decisions E1's outcomes do change are the wording ones under "Decision under each outcome".
```

**DB4 (BEFORE): when the queue may be started again after a pause.** Anchor in the stopping rule:
```text
**After any invalid run the queue pauses** ("The harness E1 runs on", R2).
```
Replace with:
```text
**After any invalid run the queue pauses** ("The harness E1 runs on", R2). **The queue is started again only if no check name stands in `failed` of E1's runs at two or more different rates;** otherwise E1 stops for a new decision, since one failure at several rates points to the harness's first GPU use (R2) or to the cell, and an unchanged rerun would repeat it. The check is made from the queue's `RUN … INVALID failed=…` lines alone, and each restart is recorded in an [OPS] entry that quotes those lines.
```

**DB5 (BEFORE): a test for the single-rate configs.**

(a) Append to `tests/test_e1.py`:
```python


def test_each_single_rate_config_is_the_sweeps_own_run_at_that_rate():
    """configs/sweep_l1pl350cl_pc_off_only_r<rate>.yaml (E1's reruns and never-started rates) expands to one run,
    equal to the sweep's own run at that rate in every key but `sweep` (its list of rates)."""
    drop = lambda c: {k: v for k, v in c.items() if k != "sweep"}
    sweep = e1._cfgs(e1.E1["configs"]["cl"])
    assert [c["workload"]["rate"] for c in sweep] == [1.5, 2, 2.5, 3, 3.5, 4]
    for c in sweep:
        only = e1._cfgs(f"configs/sweep_l1pl350cl_pc_off_only_r{c['workload']['rate']:g}.yaml")
        assert len(only) == 1 and drop(only[0]) == drop(c)
```

(b) Anchor:
```text
(checked when they were written: equal to the sweep's expansion after the list of rates is removed)
```
Replace with:
```text
(FILE(tests/test_e1.py), `test_each_single_rate_config_is_the_sweeps_own_run_at_that_rate`: one run each, equal to the sweep's own run at that rate in every key but `sweep`)
```

(c) Replace `` `tests/test_e1.py`, 12 tests; `` with `` `tests/test_e1.py`, 13 tests; ``.

(d) `uv run pytest tests/test_e1.py -q` must give 13 passed before the entry is appended. I ran this test's body at e87884d and it passes. `analysis/e1.py` and `tests/test_e1.py` are outside REG-21's freeze (FILE(docs/drafts/reg21_draft27.md:3)).

**DB6 (BEFORE): the floor from the registered code.** Anchor in "Result, computed once":
```text
From committed code, with `analysis/` and `tests/` clean and `uv run pytest` passing; the [RESULT] names the commit.
```
Replace with:
```text
From committed code, with `analysis/` and `tests/` clean and `uv run pytest` passing; the [RESULT] names the commit. **The floor is also computed from the registered code** (`agent/RUNBOOK.md` §5): from a worktree at the commit that holds this entry's approval (`git worktree add --detach ../aftershock-e1-pin <commit>`), with the run folders `*_sweep_l1pl350cl_pc_off_r*` and `*_sweep_l1pl350_pc_off_r*` of the Mac's `runs/` linked into its `runs/`, run from its root with the repo's interpreter: `AFTERSHOCK_UNSEAL=E1 /Users/chalshik/Projects/aftershock-artifacts/.venv/bin/python -c 'import json; from analysis import e1; print(e1.__file__); print(json.dumps(e1.observed()["floor"], default=str))'` (the floor needs no REG-21 statistic). The printed path must lie in the worktree. The worktree's floor (status, n, rates, value) is E1's floor; if the result commit's differs in any of these, the [RESULT] reports both and names the commits between the two that touch `analysis/`.
```

**DB7 (BEFORE): the cost ceiling.** Anchor:
```text
6 runs × (900 + 300 + about 60 s) ≈ 2.1 GPU h (DERIVED); ≈ 4.2 h with one rerun per rate.
```
Replace with:
```text
6 runs × (900 + 300 + about 60 s) ≈ 2.1 GPU h (DERIVED); ≈ 4.2 h with one rerun per rate. At most ≈ 6.3 GPU h (DERIVED: 6 rates × 3 attempts × 1260 s), and less under the stops.
```

**DB8 (BEFORE): rule F, verbatim.** Insert immediately before the line `### Changed from draft 3 (the E1 items of its rule F review)`:
- a section headed `` ### Adversarial review (rule F, `docs/process.md` §3), verbatim ``, holding the full text of the separate rule F review of draft 5 with its bundle;
- then "What was changed because of it", item by item;
- then one line naming this owner-proxy pass, its verdict, and where each of DB1–DB12 was applied.

**DB9 (BEFORE): the README, made consistent with draft 5 without touching the scripts.**

(a) In `docs/probe/20261113_e1/ops/README.md`, insert after the line `# E1: operations scripts` a blank line and then:
```text
**Read with the registration as entered** (docs/decisions.md, `[REG] E1`, and `[DECISION] (delegate) E1 approved`); it rules wherever this folder differs. Stale since draft 5: the citations of `docs/drafts/e1_draft4.md` below and in DESIGN_NOTES.md; "Nothing here is committed or reviewed"; DESIGN_NOTES.md's `RESULT19_PAT` (I11; part 2, item 12); and the header comments of `queue.sh` (line 4) and `vm_checkout.sh` (line 6), which say that E1 waits for REG-19's [RESULT]. The code waits for REG-19's queue end as recorded (`END19_PAT`, `ready_to_run`), as the registration says. The scripts are left unchanged so that the reviewed text is what runs. Step 5's move is approved by E1's approving decision.
```

(b) Replace the row
```text
| `after an invalid run (…)` | The pause, as REG-19's queue does (I7) | Start the queue again; it reruns by E1's rule |
```
with
```text
| `after an invalid run (…)` | The pause, as REG-19's queue does (I7) | Start the queue again only if no check name stands in `failed` of E1's runs at two or more different rates (registration, stopping rule); otherwise E1 stops for a new decision. Each restart gets an [OPS] entry quoting the `RUN … INVALID` lines |
```

**DB10 (LATER): what the approving decision says.**
- Its heading has the form `## <date> · [DECISION] (delegate) E1 approved: …`, so that `APPROVE_PAT` matches.
- It sits after the [REG], in the same commit, and carries this verdict verbatim.
- It states:
  - (i) the amendment of the pin clause, as in DB2, citing FILE(docs/decisions.md:4287), FILE(docs/decisions.md:4400) and the delegation's "the pin rule" (FILE(docs/decisions.md:4233)), and that the owner may overrule it;
  - (ii) that it approves README step 5 (`vm_checkout.sh`) under the delegation, to be run only once `ready_to_run` passes, that is, after the `[OPS] REG-19: the queue ended` entry is committed and REG-19's lock is gone; its probe file is committed with an [OPS] entry;
  - (iii) that a move of the VM back to `a7bb77a` for any REG-19 run is not covered, since `vm_checkout.sh` moves forward only, and needs its own entry;
  - (iv) that no E1 launch happens before the checkout's [OPS] entry and the session probe are committed.

**DB11 (LATER, same commit): RUNBOOK made current.** In `agent/RUNBOOK.md`:

(a) Replace
```text
## 4. Deploying `main` to the VM (only between items, never during a run, never before REG-19's [RESULT])
```
with
```text
## 4. Deploying `main` to the VM (only between items, never during a run, never while REG-19's queue may run; E1's `vm_checkout.sh` moves the VM to E1's commit, detached, once REG-19's queue end is recorded: decisions.md, [DECISION] (delegate) E1 approved)
```

(b) Replace `then deploy HEAD (§4); then` with:
```text
then deploy HEAD (§4; if the VM is at E1's commit, detached, `git checkout main` comes first, and never while E1's queue lock exists); then
```

**DB12 (LATER, same commit, before the first launch): the ledger row, as FILE(docs/model.md:3) requires.** Append after the last row of the prediction ledger in `docs/model.md`, numbered as the next free row:
```text
| <n> | <date> | Model F's replay and the closed-loop cold spans on record (E1: closed-loop cache-off sweep of L1 at 350 W, rates 1.5–4, seed 0) | Status `ok` ≈ 0.75, `tail_ok` ≈ 0.2 (neither ≈ 0.05, DERIVED); floor 1.70–1.80 req/s; model F's replay of E1's config at μ = 1.681 over rates ≥ 2.0: 1.744 (fixed cost) or 1.771 (proportional), `k2.closed_loop_floors` (BELIEF as to the model) | — | Open | decisions.md <date> [REG] E1 |
```

## 3. Later changes that would need another owner-proxy pass
- Any change to the six scripts (`common.sh`, `vm_state.py`, `session_probe.sh`, `launch.sh`, `queue.sh`, `vm_checkout.sh`), comments included, since they are frozen at the registered commit. Also any change to `e1_commit.txt` other than README step 3.
- Any change to:
  - E1's configs, rates or seed;
  - the floor rule, the tail fallback, REG-8's settings, "holes" or `first_valid`;
  - the stopping rule: attempts, the heat rule, the checks that allow no rerun, the global stops, the pause, DB4's restart rule;
  - the allowed reads, the start condition (`END19_PAT` or the lock), or the approval heading.
- Rule F items on draft 5 that go beyond wording, tags and citations.
- Computing or quoting any part of E1's result before REG-21's first [RESULT] (for example splitting the floor out of the report), or reading any E1 run beyond `valid` and `failed` before E1's [RESULT].
- A pre-allowed rerun after a lost run (Note N3), a smoke run, or any start before the `REG-19: the queue ended` entry.
- Applying DB1–DB12 verbatim, renumbering FILE citations, and the [OPS] entries need no new pass.

## 4. Notes for the owner
- **N1. The pin clause.** E1's approval amends your REG-19 pin rule: the VM leaves `a7bb77a` at the recorded end of REG-19's queue, not at its [RESULT]. You can reverse this with one entry; the cost is a GPU idle until REG-19's [RESULT], which waits for REG-21 and REG-22.
- **N2. 350 W after a reboot.** The agent's `sudo -n` was refused, so every reboot (420 W) stops E1 until you set 350 W. A NOPASSWD sudoers rule for `nvidia-smi -pl 350` would remove that step; it is a root action, so it is yours.
- **N3. Lost runs.** All eight recorded boot ends were power-key presses (A18). Any E1 run that ends without `checks.json` stops E1 until a new decision. You could allow, before the run, one further attempt within the three for a run lost to a VM power-off (shown by a changed boot id). Your own reasoning at FILE(docs/decisions.md:4383) item 4 covers this: a lost run carries no outcome. A crash in the same boot (R1) would still stop. This changes the stopping rule, so it is your choice.
- **N4. The floor waits for REG-21.** E1's [RESULT], and with it the floor, waits for REG-21's first [RESULT], and E1's runs stay sealed until then. Quoting the floor earlier would need a registration change.
- **N5. A REG-19 stop holds E1 too.** If REG-19's queue ends in a QUEUE STOP, E1 waits with it, and only your decision on REG-19 releases it.
- **N6. A REG-19 rerun after the move.** If REG-19's `final.sh` ends in an operational stop and you want a REG-19 rerun, the VM has to be moved back to `a7bb77a` by hand, with its own entry. E1's launches refuse until it is moved forward again.
- **N7. Leftover stale text.** The `analysis/e1.py` docstring still says "not yet registered: draft docs/drafts/e1_draft4.md". It is harmless and left as is, so that judged code is not touched at registration.
