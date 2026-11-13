**Decision on draft 2: APPROVE** — my approval stands for the REG-19 resume decision as revised; P1–P9 are met, and three small new conditions (N1–N3) must be in the entry before it is appended. None needs a script change.

**Conditions P1–P9:**
- **P1 met.** Draft 2 item 2, first two sub-points: the byte-identical sentence is withdrawn as false, the equivalence rests on the commit dates (1cface7, 15:33:58 UTC, first), and the [RESULT] states whether the three earlier `continue: True` flags agree with the worktree's table.
- **P2 met.** `docs/probe/20261113_reg19/worktree_test_20261112T200109Z.txt`: worktree at the full hash of a7bb77a, dirty 0, ten modules resolving to the worktree, and `reg19_inputs` output equal to the registered schedule table for all five seeds.
- **P3 met.** `common.sh` line 23 compares the working tree with the pin for `tools/manifest.py`, `pyproject.toml` and `uv.lock`; it runs in `launch8.sh` line 11 and `queue_reg19f.sh` lines 15 and 56. In place of the diff in the entry, the scripts are pinned at commit 7f4efb5 (`scripts_commit.txt`, checked by `common.sh` lines 24–29), which I accept. Git confirms 7f4efb5 is the last commit of the four scripts and that they equal HEAD 8b44d26.
- **P4 met.** Draft 2 item 4: the PROTOCOL §5 deviation is named with the A14 sentence; the recheck is fixed at `harness/checks.py` of 5ee6e38 and `analysis/recheck.py` of 72fafb5 (git confirms these are the last commits of both files); "the registered outcome stands" is gone; no reliance on a label that flips until the owner rules.
- **P5 met.** Draft 2 item 5. By a listing only: the holding folder exists outside every `runs/`, with nine files and no `checks.json`. Its record is missing (N1).
- **P6 met.** Draft 2 item 1: every launch counts as an attempt, three per config, a folder without `checks.json` is kept and not opened, worst case 12.8 GPU h.
- **P7 met.** `queue_reg19f.sh` lines 59–70: a failed step, a `done` list other than 15..seed, or a missing flag stops with exit 1; "QUEUE END futility stop" is printed only on `'continue': False`. The empty-error-file part is the agent's check (item 6), not the script's.
- **P8 met.** Draft 2 item 2 (three commands only), item 6 (the [RESULT] names a7bb77a and the worktree), and the "Unchanged" point (nothing deleted). `links_ok` in `common.sh` links only REG-19's folders; the pinned `reg19_step`, `reg19_pair` and `reg19_table` load only REG-19's patterns, so the final command still works.
- **P9 met as a commitment.** Draft 2 item 7; to be checked against the [OPS] entry when it is written.

**Any new condition:**
- **N1. Three facts in draft 2 have no record file** (rule B). They are the VM listing of 19:52 UTC, the failed `sudo -n` of 19:53 UTC, and the copy of the lost folder with its checksum `8b6c4720032939de` at 19:58 UTC. That checksum appears only in the draft itself, and `docs/probe/20261113_reg19/` holds only the worktree test. Save each as a probe file, or cite the file that already holds it, before the entry is appended.
- **N2. State what a stop before `LAUNCHED` does to the attempt count.** `queue_reg19f.sh` line 40 writes the attempt's output file whatever the exit code, and line 38 then refuses that number, so a pre-launch stop (another user's process, 420 W, a reboot, heat) uses up an attempt number without a launch. The entry must say:
  - such a stop is not a launch and does not count toward the three;
  - the next try takes the next number for its file names;
  - the [OPS] entry lists each numbered try and whether it launched;
  - if the numbers run out with launches still allowed, the queue stops for a new reviewed decision;
  - no file is deleted or renamed.
- **N3. Say what this approval covers later.** The entry names 7f4efb5 as the reviewed scripts. A resume after a further stop under these scripts and rules needs no new decision and is logged in [OPS] with a new session probe. Any later change to the four scripts is logged with its commit and diff, and a change that removes or loosens a check needs a new reviewed decision.

**Notes for the owner:**
- **350 W now depends on you.** `sudo -n nvidia-smi -pl 350` asks for a password on the VM, and the agent may not change that. A sudoers rule for exactly that command would remove the dependency. `docs/probe/20261105_vm_checks/sudo_log.txt` contains the same message; I did not read it further, so this may not be new.
- **A reboot during the queue stops it and needs you again** for the limit. The launch script only reads the limit and compares the boot id, which is stricter than draft 1.
- **The session-shift readouts are new and not decisive** (per-run SM clock, power, temperature, `env.json`, boot ids). They are fixed before any outcome is read. They should come from named functions (rule I) and must not be used to drop or re-judge a seed.
- **Not checked by me:** the six `checks.json` files, the VM's state, and whether `.venv` matches `uv.lock`. I did not run the sandbox test; I counted its 29 cases by reading. It stubs `mac_checks`, so that function is covered only by my reading and the git checks above.
- **One untagged sentence remains:** that at `main` the step "would print `'done': [], 'continue': True`". It is harmless, because the queue requires the exact `done` list.
- **My earlier notes still hold:** the old recorder fault stays possible for four more runs; if the recheck fails a counted run you will rule knowing the outcome; the limit stays at 350 W after the queue.
