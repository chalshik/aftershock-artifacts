**Decision: APPROVE**, for the entry with conditions 1–9 written in. The draft unchanged is not approved: item 4's recheck timing and its sentence "the registered outcome stands" must go (condition 1).

**Reasons:**

1. **Scope: inside the delegation, except one clause.** The delegation names "the REG-19 resume decisions (seed-18 control rerun as attempt 2, the pin rule)" and allows `sudo -n nvidia-smi -pl 350`. That is the only root command in the scripts (`launch7.sh:25`). Nothing edits `runs/` (rsync only adds, with no `--delete`; the links go into the worktree's `runs/`), a used config or an old entry. Nothing is deleted, no threshold is chosen, and nothing leaves the Mac and the VM. `uv.lock` and `pyproject.toml` are identical at `a7bb77a` and HEAD (`git diff --quiet`). The clause outside is in item 4 (reason 4).

2. **Fidelity: the test, thresholds, seeds, order, futility stop and validity checks are unchanged.** The stopping rule says "an invalid run … is rerun unchanged, at most twice … A rerun decision reads only `checks.json`". A run with no `checks.json` is not covered by that sentence, so it falls under "The queue stops for an operational reason: … the owner decides", which is the decision delegated.
   - Counting the lost run as attempt 1 is the stricter reading.
   - Rule 4 is met as far as it can be: the folder is kept, and "marked invalid in checks.json" is impossible without editing `runs/`. The precedent is `docs/status.md:64` ("An interrupted run is kept and rerun") and its "No checks" list.
   - PROTOCOL §5 "rerun unchanged" holds: same config, same VM commit, 350 W.
   - The run lock is `fcntl.flock` (`harness/run.py:229` at `a7bb77a`), so the power-off leaves no stale lock to delete.

3. **Pin rule: at least as strict for the analysis code, with two gaps.** The worktree is at exactly `a7bb77a` and checked clean; it is clean now. The old rule compared commits only, and the main tree had uncommitted edits to `analysis/load.py`, `tables.py`, `recheck.py` and `engine_config.py` while I reviewed. I confirmed the draft's identity claims with `git diff`: `gate.py` and its imports (`derived`, `floor`, `load`, `margin`) are identical, and `stats.py` gains 9 lines. Run discovery is `RUNS.glob` plus `config.yaml.exists()`, which follows links. Rule 6 is untouched (VM check at `launch7.sh:39`, harness `clean_git`). Rule I is served, since the numbers come from `gate.reg19_table` at a named commit.
   - Gap (a): `launch6` stopped on a changed `uv.lock` or `pyproject.toml`; `launch7` does not, yet the step runs on the main repo's `.venv`, not the registered `uv run`.
   - Gap (b): the `tools/manifest.py` check compares commits, not the file that runs.
   - The read path through the links is untested (`reg19_inputs` reads no run).

4. **Item 4: I require the old checks to decide, but the stricter recheck must run before the table is read.** Keeping the VM on `a7bb77a`'s harness and checks is right, because 5ee6e38 changes `loadgen`, `recorder` and `run.py` inside one matrix. The queue's reruns and `reg19`'s count stay on the stored `checks.json`, as registered. The stricter checks should not decide validity by the delegate's hand, for seeds 18–19 or for all ten.
   - **"The registered outcome stands" is not the delegate's to say.** PROTOCOL §5 has carried the stricter checks since 2026-11-12 ("Invalid runs are kept, never counted"). The A14 entry says "marking any run otherwise is the owner's", and CLAUDE.md C reserves "marking a run invalid beyond the automatic checks". That item is not in the delegation's list. Declaring in advance that such a run counts is the same decision taken the other way.
   - **Rechecking after the result makes the owner's call outcome-aware.** The registration wants validity decided blind ("no rerun on any verdict or label"). `analysis.recheck` needs no VM and prints only validity, failed lists and the `recorder` and `gpu_steady` details.
   - **One rule for all ten costs nothing.** Seeds 15–17 already passed: the A14 recheck covered 182 folders with "no valid run changes verdict", and the manifest of 54a995d, committed before 5ee6e38, lists 182 folders, six of them REG-19's.
   - **The stakes are small.** At `a7bb77a`, `accounting` already fails a run whose recorder stops while requests still complete (`harness/checks.py:71–81`). What is left is a late start, the last seconds and GPU-sample gaps.

5. **Not stated in the draft:** see conditions 4–9 and the notes.

**Conditions or required changes:**

1. **Replace item 4's last two sentences.** After the queue ends and before `analysis.gate reg19`, run `analysis.recheck` on REG-19's ten runs. Name the commit of `harness/checks.py` and confirm the file is unchanged in the working tree. Lift the seal for that one command only, read only `n_runs`, `n_changed` and `changed`, and save the output in the probe folder.
   - If `n_changed` is 0, `reg19` runs and the [RESULT] says all ten pass the checks in force.
   - Otherwise `reg19` is not run. It is an operational stop: the agent neither marks, reruns nor counts the run, and the owner decides.
2. **Close the two pin gaps.** Replace the manifest line in `launch7.sh` with `git diff --quiet $PIN -- uv.lock pyproject.toml tools/manifest.py || { echo "STOP: uv.lock, pyproject.toml or tools/manifest.py differs from $PIN"; exit 2; }`. Run the same check by hand before the final `reg19`. That exact line is approved in advance.
3. **Test the link path before the launch.** Reproduce an already reported table (REG-18's or REG-17's) from the worktree, compare it with its [RESULT], and record it. Do not use a REG-19 run for this.
4. **Check the pinned versions after the reboot.** Before the first launch, save the VM's driver version, kernel and `git hash-object uv.lock` to the probe folder. Stop if the driver is not 595.99.02 (PROTOCOL §4) or the lock differs. No check compares these; `env.json` only records them.
5. **Log the interim look before the launch, not after the result.** RESUME.md stop 2 (the seed-17 control's live hit rate) breaks "No interim look beyond `reg19_step`'s `continue` flag" and is not yet in `decisions.md` (rule 10, A6). Scope "This agent has read no outcome" to this session.
6. **Limit the approval to attempt 2 of seed 18's control.** Runs with `valid: False` follow the registered rule. Any further run without `checks.json` counts as an attempt and needs a new delegate decision.
7. **State the pooling assumption (rule H).** Seeds 15–19 are one cell only if the session does not matter. Report k of n per session (15–17, 18–19) beside the registered count, as a readout with no threshold.
8. **Restrict the worktree until the [RESULT] heading exists.** Only `reg19_step` (once per pair), `reg19` (once) and condition 3 run from it. Afterwards re-run `gate reg19` from main, and again once the lost folder is copied. State whether the output is identical; if it raises or differs, write a [CORR] and change no code without a decision.
9. **Complete the record.**
   - Put the rule F review verbatim in the entry (delegation (a); there is no [REG] to hold it), together with this approval.
   - Add rule B tags to the State line and the identity claims.
   - Commit the entry and both scripts before the first launch, and do not edit them while the queue runs.
   - Read "QUEUE END" as a futility stop only with `'continue': False`, the expected `done` list and an empty stderr file. Anything else is an operational stop.

**Notes for the owner:**

- **Power limit.** The GPU stays at 350 W after the queue, and the agent cannot set 420 W back. `launch7` sets 350 W before it checks that the GPU is idle, so another user's job would be capped.
- **Power-offs.** The sender of the power-key events is still unknown (`status.md:64`). Seeds 18–19 are exposed to it, and each loss spends an attempt.
- **Known defect.** Seeds 18–19 run on the recorder that A14 fixed, by design.
- **Uncommitted seal.** `analysis/withheld.py` is uncommitted and relies on this worktree as the only unsealed path to REG-19's runs. I did not review it as part of this decision.
- **Worktree.** `/Users/chalshik/Projects/aftershock-reg19-pin` was created before this approval and stays until you remove it.
- **Delegation entry.** It was found uncommitted and without its heading marker (decisions.md 2026-11-13 [OPS]). This approval rests on it, so please confirm it.
- **What I did not check.** I opened nothing under `runs/` or `agent/`, read no other review and did not contact the VM. The VM's state, whether `.venv` is in sync and the draft's `reg19_inputs` test are unverified by me.
