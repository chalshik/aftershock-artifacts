**Rule F adversarial review, round 3: REG-20 arm A operations decision, draft 3**

**Verdict: READY provided DH1 and DH2 are applied verbatim.** DH1 is `rulef-reg20-ops-draft3-r3-dh.patch` plus the point D text in section 5. DH2 is text only (section 5). Neither changes a label, a threshold that judges data, a seed or a GPU hour. DH1 changes a pre-launch check, so the owner-proxy delta on draft 3 must also cover DH1's script diff (RD1's "anything else needs a new round", FILE(docs/drafts/reg20_ops_decision_draft3.md:722)).

Tag conventions used below:
- † means the file as patched in a scratch copy of e788191 with `docs/drafts/reg20_ops_r3/ops_draft3.patch` applied, the way draft 3 itself uses the mark.
- ‡ means the same copy with this review's `-dh.patch` applied as well.
- Section headings use `###`. No line of this file begins with `## `, so it can be quoted into `docs/decisions.md`. Even so, it should go in blockquoted (DH-O3).

### 0. Scope, sources and what was not opened

- **Role.** I am a separate subagent doing rule F's pass, round 3. I read only. I wrote this file and three patches beside it. Scratch copies are under `scratchpad/r3dh/`. I made no edit, add or commit in the repo and ran no git command that changes the repo or its index. No ssh, no VM, no network.
- **HEAD.**
  - It was e788191 when I started.
  - It moved to b2fa956 during the review. b2fa956 adds only `agent/bin/test_vm_verify_list.zsh` and `agent/bin/vm_verify_list.zsh` (PROBE: `git show --stat b2fa956`).
  - None of the reviewed files changed.
  - `git status --short` at the end differs from the start only by other sessions' untracked drafts: `docs/drafts/d1_draft2.md`, `d1_draft2_itemmap.md`, `d1_r2/`, `reg24_confirm_draft2.md`, `reg24_confirm_draft2_itemmap.md` and `reg24_r2/`. No tracked file is modified apart from `.gitignore`, which was already modified at the start (PROBE: `r3dh/git_status_before.txt` against `git status --short` at the end).
- **Reviewed files and their sha256** (PROBE: `shasum -a 256`):

  | File | sha256 |
  |---|---|
  | `docs/drafts/reg20_ops_decision_draft3.md` | 331ee2f7… |
  | `…_draft3_itemmap.md` | 25be1a8c… |
  | `ops_draft3.patch` | 31dbea7c… |
  | `owner_rulings_rd2.patch` | 18d0bb21… |
  | `runbook_heading1.patch` | 4e92970e… |

- **The writer's `SHA256SUMS.txt` holds, in all three groups:**
  - its 11 repo files are OK at HEAD;
  - group (1), the 8 ops files, is OK in the † copy;
  - group (2), `owner_rulings.txt` (2daacec3…) and `agent/RUNBOOK.md` (bc84c57d…), is OK after `owner_rulings_rd2.patch` and `runbook_heading1.patch` are applied in a further scratch copy (PROBE: `shasum -a 256 -c` in the scratch copies).
  - The applied rulings read `2a setaside`, `6 b`, `7 lost_open`, `8 b`, `9 a`, `16 a` (PROBE: same copy).
- **Read:**
  - draft 3 and its item map;
  - the † scripts: `common.sh`, `launch.sh`, `queue.sh`, `final.sh`, `session_probe.sh`, `vm_checkout.sh`, `README.md` and `test_sandbox.sh`;
  - E1's `docs/probe/20261113_e1/ops/queue.sh`, `common.sh` and README at HEAD;
  - from HEAD's `docs/decisions.md`: REG-20's [REG] (4045–4100), its approval (4166) and the delegation (4233–4236); E1's [REG] (17020–17080), E1's approval (18286–18300) and the disk entry;
  - `agent/RUNBOOK.md`;
  - `harness/checks.py:48`, `harness/config.py:24-28`, `analysis/k1.py` (labels and outcome) and `analysis/withheld.py` (SEALS);
  - `tools/check_docs.py:109-131`;
  - the headings of the round 2 reviews in `docs/drafts/reviews-2026-11-13/`;
  - `docs/drafts/reg20_ops_r3/*`.
- **Not opened:**
  - anything under `runs/` (nothing listed or opened, and no sealed name was matched against a folder);
  - `/Users/chalshik/aftershock-backups/`;
  - `docs/probe/20261111_reg19/ops/RESUME.md`;
  - `docs/paper/`;
  - any `docs/probe/**/state/` folder (E1's `state/` appears only as a name in `git status`; the scripts' own fake `state/` inside the sandbox copies was used by the sandbox);
  - `docs/FABLE_PROMPT.md`.
- No `analysis/` function was run on a run folder, and `AFTERSHOCK_UNSEAL` was not set.
- **Tests, all in scratch copies.** The final sandbox counts are in section 9.
  - The unchanged † sandbox: 428 passed, 0 failed, exit 0 (PROBE: `r3dh/sandbox_unchanged.txt`), as the writer reports.
  - `test_control_due.py`: 47 passed, exit 0 (PROBE: `r3dh/test_control_due_r3.txt`).
  - The sandbox with DH1, DH2 and DH-O1, plus three probe-only cases (`r3dh/sandbox_r3_dh_main.txt`).
  - The sandbox with the fallback DH1 and DH-O1 (`r3dh/sandbox_r3_dh1alt.txt`).
  - A pattern probe (`r3dh/probe_patterns.txt`) and a heading probe (`r3dh/probe_headings.txt`).
  - An exact disk enumeration (`r3dh/disk_enum.py` and `r3dh/disk_enum.txt`).

### 1. The verdict in brief

| Item | Kind | Gist |
|---|---|---|
| DH1 | required, patch + text | A control's disk floor is `CONTROL_MIN_FREE_KB = 1,048,576` kB (RUNBOOK:26's per-launch rule). Every other launch keeps `MIN_FREE_KB`. A disk stop then falls only before a burst run or the drift run, never between a cold burst run and its due control. |
| DH2 | required, text | The hold ends only at `final.sh`'s commit or at arm A's "ended by a stop" end entry (RD4's stricter end, which the draft's own merge rule requires). RC1 item 3's seal-row commit is the one named exception. Arm A's other records are headed `[OPS] REG-20 arm A: …`, so none matches `STOP_PAT` by accident. |
| DH-O1 | optional, patch | `recheck_guards` holds `configs/defaults.yaml` to the pin, since today's checks merge it. |
| DH-O2 | optional, text | `vm_checkout.sh` runs its dry-run sync before it moves the VM, and also on `already_at_pin`. |
| DH-O3 | optional, text | Headings 2 and 3 quote reviews blockquoted, so no quoted line starts with `## `. |
| DH-O4 | optional, text | RUNBOOK §4's new clause starts arm A's hold at the start entry's commit, as RUNBOOK:48 and point 18 do. |

### 2. Traces

**T1 (DH1): a disk stop between a cold burst run and its due control.**

The draft's numbers, which I checked exactly (DERIVED):
- F1 = F0 − 6 × 71,393 = 4,171,272 − 428,358 = 3,742,914 kB with E1's expected six runs (FILE(docs/drafts/reg20_ops_decision_draft3.md:470-481)).
- r = 242,736 kB (ibid. :471).
- `MIN_FREE_KB` = 2,097,152 (FILE(docs/probe/20261113_reg20/ops/common.sh:19)†).
- The check is at FILE(docs/probe/20261113_reg20/ops/launch.sh:52)†.

The trace:
- Controls are due at seeds 15, 17 and 18.
- The order (FILE(docs/decisions.md:4054): a control runs "right after it"; the drift run comes after seed 17's burst run and its control) is B15 C15 B16 B17 C17 D B18 C18 B19.
- Launches 1 to 7 pass. Before launch 8, C18, the free space is 3,742,914 − 7 × 242,736 = 2,043,762 < 2,097,152 (DERIVED).
- `launch.sh` prints `STOP: only '2043762' kB free on the VM` and exits 2. The queue stops with `QUEUE STOP stage2_control_l1pl350ol_r2.0_w3000_s18 launch rc=2 …` (FILE(docs/probe/20261113_reg20/ops/queue.sh:76)†).
- B18 ended cold, and its control runs only after the owner frees space, possibly hours later and possibly after a reboot.
- The control exists "to separate overload of the open-loop warm state from a stuck state" (FILE(docs/decisions.md:4054)). A late control weakens exactly that separation, for exactly the seed that needs it.
- The draft states the cost (FILE(docs/drafts/reg20_ops_decision_draft3.md:506)) but leaves the fix as an untested option (c) (ibid. :521).

How often, by exact enumeration of the 2^5 control patterns. Assumptions: each open run is cold with probability p, independently; no reruns; every run is r (PROBE(r3dh/disk_enum.txt) and the p-sweep in the appendix).

| Free space at arm A's first launch | p | Draft: P(stop between a burst run and its control) | Draft: P(any disk stop) | DH1: P(between) | DH1: P(any) |
|---|---|---|---|---|---|
| E1 expected, 3,742,914 kB | 0.10 (the registration's BELIEF, FILE(docs/decisions.md:4085)) | 0.0319 | 0.0815 | 0 | 0.0523 |
| E1 expected | 0.25 | 0.1406 | 0.3672 | 0 | 0.2617 |
| E1 expected | 0.50 | 0.3125 | 0.8125 | 0 | 0.6875 |
| E1 worst, 2,886,198 kB | 0.10 | 0.0180 | 1.0000 | 0 | 1.0000 |
| F0, 4,171,272 kB (no E1 run) | 0.10 | 0.0004 | 0.0005 | 0 | 0.0001 |

The pair breaks most often when cold open runs are common, which is the case in which the controls decide the reading. The draft's recommended option (a) does not prevent it either:
- At its minimum, 4,524,512 kB, exactly 11 launches fit (2,097,152 + 10 × 242,736, DERIVED).
- So one rerun anywhere before seed 19 moves C19 to launch 12.
- C19 then meets 4,524,512 − 11 × 242,736 = 1,854,416 < 2,097,152 and is refused after a cold B19 (DERIVED).
- Under DH1 the same launch needs 1,048,576 and runs.

**T2 (DH2): an [OPS] record ends the arm A hold.**
- The queue stops for disk: under the draft before a control, as in T1; under DH1 before a burst run, such as B19 in T1. The agent records the stop in an [OPS] entry, as it records every stop.
- Draft 3 gives no heading form for such a record. Its own prose calls the event "arm A stops for disk" (FILE(docs/drafts/reg20_ops_decision_draft3.md:500)).
- `## 2026-11-15 · [OPS] REG-20 arm A stops for disk: QUEUE STOP stage2_control_l1pl350ol_r2.0_w3000_s17 launch rc=2` matches `STOP_PAT` (PROBE(r3dh/probe_patterns.txt), cases 11 to 14 in the appendix). An RD3 (ii) record headed "REG-20 arm A stops after an invalid run: …" or "… is stopped by a power-off …" matches as well.
- (i) The hold ends at "an entry matching `STOP_PAT`" (FILE(docs/drafts/reg20_ops_decision_draft3.md:540); item map M3; the notice at :685). Point 18, however, says that of the `STOP_PAT` entries "only '… ended by a stop: …' is an end", and that "a pause, or a stop that waits for a decision, is not an end" (ibid. :367-368).
  - The section's merge rule is "where the two differ, the stricter text is kept" (ibid. :538). RD4's end, "or an entry ends arm A", is the stricter, yet line 540 keeps RC1's.
- (ii) With the hold ended, any session may commit to k1's closure, `harness/`, `configs/defaults.yaml` or `analysis/withheld.py`. REG-24's and D1's SEALS rows are waiting for exactly this (ibid. :564), and several writer sessions are active.
  - A SEALS row moves `withheld.py`'s blob away from `SEAL_BLOBS`, so `mac_checks` refuses every script (FILE(docs/probe/20261113_reg20/ops/common.sh:92)†).
  - Arm A can then restart only after a reviewed scripts commit made mid-arm, when seeds 15 to 18's `CONTROL_DUE` lines are already in the queue output (point 15). That is a script change after data it gates are visible, which is the owner's under CLAUDE.md C and rule A5.
- (iii) A commit to `configs/defaults.yaml` in the gap would change the recheck of every later copy silently, because `recheck_guards` compares that file only with HEAD (FILE(docs/probe/20261113_reg20/ops/common.sh:528)†; `harness/checks.py:48` merges it beneath each run's config). See DH-O1.
- (iv) The restart needs a new start heading (ibid. :541; gate_in_log refuses after a `STOP_PAT` line, FILE(docs/probe/20261113_reg20/ops/common.sh:166-167)†). The [RESULT]'s hold duty runs `git log <start entry's commit>..<final>` (ibid. :572). With two start entries, which one is meant is not said, and from the later one the gap's commits do not show.

**T3 (DH-O2): `vm_checkout.sh` can be passed by a second run.**
- A dry-run sync that would change a package, or a wrong `uv.lock` blob, is detected only after `git checkout --detach <pin>` has run (FILE(docs/probe/20261113_reg20/ops/vm_checkout.sh:32-39)†). The script dies with "the owner decides before any run", leaving the VM at the pin.
- Running the script a second time takes the `already_at_pin` branch, prints `VM ALREADY AT THE PIN …` and exits 0, with no dry run (ibid. :30).
- `session_probe.sh` then writes `SESSION OK`, because it checks the tree, the driver and the lock blob but not the dry run (FILE(docs/probe/20261113_reg20/ops/session_probe.sh:46-48)†).
- Both are shown in the sandbox by the probe-only cases (section 9).
- The owner's barrier at :39 is then kept only by whoever reads the first probe file. No label is affected. The risk is a run on an environment that `uv run` re-syncs at launch (FILE(docs/probe/20261113_reg20/ops/launch.sh:62-64)†, BELIEF that `uv run` syncs by default).

**T4 (DH-O3): the gate passes before heading 3.**
- `gate_in_log` takes the last line of all of `docs/decisions.md` that matches `START_PAT` and requires only that it come after the last rulings line (FILE(docs/probe/20261113_reg20/ops/common.sh:162-165)†).
- Heading 2 must quote reviews verbatim (FILE(docs/drafts/reg20_ops_decision_draft3.md:642-645)). If any quoted text holds a start heading at the start of a line, heading 2's own commit passes the gate as soon as E1's end entry is in, before heading 3, the hold notice and heading 3's facts exist (DERIVED from the lines cited).
- No such line exists today:
  - the round 2 reviews hold 0 lines matching `^## [0-9]{4}.*REG-20 arm A (starts|operations: the rulings|stops|ended by a stop|halted)`, and HEAD's log holds 0 `STOP_PAT` and 0 `E1_END_PAT` lines (PROBE: `grep -cE`);
  - this file holds none.
- So T4 is a trace on future text, and the fix costs only formatting. That is why it is optional.
- Separately, `tools/check_docs.py:113` treats every line beginning `## ` as an entry heading that needs exactly one tag. Draft 3's own `## 1. Pin` style headings (FILE(docs/drafts/reg20_ops_decision_draft3.md:100)) and the round 2 review's `## 1. Traces …` (FILE(docs/drafts/reviews-2026-11-13/rulef-reg20-ops-draft2-r2.md:81)) would fail `check_docs` if pasted unquoted. The log's practice is blockquoting (FILE(docs/decisions.md:2233); 10,575 lines start with `> `, PROBE: `grep -cE '^> '`).

**T5: `e1_ended`. No trace gives a wrong order; its limits are content judgments.**
- The pattern matches E1's three registered end headings exactly, and a suffixed `QUEUE DONE` heading (PROBE(r3dh/probe_patterns.txt), cases 1 to 4).
- It refuses six non-ends, including `(QUEUE END futility stop)`, an unspaced stop line, and a `(delegate)` or `[DECISION]` form (cases 5 to 10). The draft's sandbox adds an empty stop line (FILE(docs/drafts/reg20_ops_decision_draft3.md:382)). These are fail-safe: arm A waits until a heading in E1's registered form is committed.
- HEAD holds 0 matches today (PROBE), so it cannot pass early unless an end entry is committed early, and whether a stop "ends" E1 is the entry's content (FILE(docs/decisions.md:17076)).
- The lock test is for existence only (FILE(docs/probe/20261113_reg20/ops/common.sh:141)†). E1's queue renames the lock on every exit (FILE(docs/probe/20261113_e1/ops/queue.sh:30)), so after a stop that waits for a decision, only the end-entry test holds arm A back. That is the registered rule.
- A stale lock, left after the trap did not run, blocks arm A and `final.sh`. Moving it aside is the owner's, and never done by starting E1's queue again. The message "E1's queue may be running" could say so (minor).
- The gate fixes "E1 first" in code (ibid. :177). An owner's later reordering would need a reviewed scripts commit (DERIVED). That is consistent with RD5.

**T6 (DH-O4): the RUNBOOK §4 window.**
- The new §4 clause starts arm A's VM hold "from REG-20's `vm_checkout.sh`" (FILE(docs/drafts/reg20_ops_r3/runbook_heading1.patch:11)).
- The new :48 and point 18 forbid a deploy from heading 3 on ("while REG-20 arm A or E1 has started and not ended, no deploy", ibid. :8; FILE(docs/drafts/reg20_ops_decision_draft3.md:416-419)).
- Between E1's end entry and `vm_checkout.sh`, §4 allows what the other two forbid.
- A deploy there is caught: `vm_checkout.sh` accepts a descendant of the pin (FILE(docs/probe/20261113_reg20/ops/vm_checkout.sh:31)†), and a deploy's `uv sync` that changed the venv would stop the dry run. So the window costs a stop, not a label.

### 3. Strongest alternative explanation of arm A's likely outcomes

- **If `supports`** (every open run `recovered_open`): the open arm differs from REG-19's closed arm in more than the turn release.
  - (a) It runs days later, and the drift run checks one seed (FILE(docs/decisions.md:4093)).
  - (b) The open arm's harness, and the vLLM server it starts, run under `ulimit -n 65536` (FILE(docs/probe/20261113_reg20/ops/launch.sh:60-62)†). The closed arm and the drift run do not (ibid. :64). The drift run therefore does not test this difference, and what vLLM 0.32.0 does with the raised limit is an open question (FILE(docs/drafts/reg20_ops_decision_draft3.md:687)).
  - (c) The working-set alternative: closed-loop sessions live longer under slowdown, so distinct prefixes grow without any held-prefix loop (FILE(docs/decisions.md:4089)).
  - The separating evidence: the drift run's verdict against REG-19's for its seed; "mechanism shown" in every recovered run (`supports` against `supports_no_mechanism`, FILE(docs/decisions.md:4077-4078)); and arm B, which tests headroom (ibid. :4090).
- **If `refutes`** (k_stuck ≥ 3): operational losses are counted as stuck.
  - `lost_open` counts in k_stuck (FILE(docs/decisions.md:4076)). Rulings 6 (b) and 7 make a second client error, and RA3's case, `lost_open` (FILE(docs/drafts/reg20_ops_decision_draft3.md:650), ibid. :648).
  - An open-loop backlog writes the most lines (draft point 1), so harness failures are likeliest in the cold open runs.
  - The separating evidence: the [RESULT]'s duty (vi) `lost` lines and duty (v)'s counterfactual line (ibid. :601-607). A `refutes` that needs a `lost_open` seed to reach 3 should be stated as such.
- **If `inconclusive`:** most likely from operations (a seed out of n under 2a, which makes `supports` unreachable, ibid. :657) or from the 5-of-5 requirement itself (FILE(docs/drafts/reg20_ops_decision_draft3.md:609)).

### 4. Rule A1: can the run change a decision?

Yes:
- `supports` starts arm B;
- `refutes` takes K1 out of the paper's core claims;
- `inconclusive` leaves the owner to choose between paired seeds 20+ and dropping K1 (FILE(docs/decisions.md:4076-4079)).

The registered prediction is each open run cold ≈ 0.10 (BELIEF, FILE(docs/decisions.md:4085)). The cost is ≈ 6.4–7.4 GPU h for five runs plus the drift run, plus ≈ 1.1 h per conditional control (FILE(docs/decisions.md:4097)). DH1 and DH2 add 0 GPU h. DH1 lowers the expected number of disk stops (T1 table).

### 5. Required items

**DH1. A control's disk floor (patch, and point D's text).**

*Patch:* `rulef-reg20-ops-draft3-r3-dh.patch` (sha256 c2c6f97f309defa178c0345be1738a5259a8830f5405e0aa77c4ef31981d3a1d). It applies to the † copy alone, and together with DH-O1 in either order (PROBE: `patch --dry-run` then `patch` in `r3dh/ver_v1` to `ver_v3`). Its content:
- `common.sh`, after `MIN_FREE_KB`:
  ```
  CONTROL_MIN_FREE_KB=1048576              # rule F round 3 (DH1): a control's floor, RUNBOOK:26's 4 x 240 MB per launch (4 x 242,736 kB,
                                           # REG-19's seed 15 burst run, rounded up to 1 GiB): a burst run launched at MIN_FREE_KB leaves
                                           # room for its control, which runs right after it (decisions.md:4054), unless it wrote > 1 GiB
  ```
- `launch.sh:52` becomes two lines:
  ```
  NEED=$MIN_FREE_KB; [[ $CFG == ${C}* ]] && NEED=$CONTROL_MIN_FREE_KB   # DH1: a control, right after its burst run, has the lower floor
  [[ $FREE == <-> ]] && (( FREE >= NEED )) || { echo "STOP: only '$FREE' kB free on the VM, $NEED needed for $CFG"; exit 2; }
  ```
  The check stays before the attempt record (FILE(docs/probe/20261113_reg20/ops/launch.sh:59)‡), so a refusal still spends no attempt.
- **Sandbox, after the pre-launch block's "none of these launched anything":**
  - a burst run below `MIN_FREE_KB` is stopped, with no attempt and no launch;
  - at 1,500,000 kB a due C15 launches and B16 is refused ("2097152 needed for …s16"); the order is "B15 C15" and no B16 attempt is spent;
  - below 1,048,576 the control is refused too, with no attempt;
  - the drift run is held to `MIN_FREE_KB`, with the order "B15 B16 B17".

*Text, in point D* (replacing what is quoted; everything else in D stays):
- After ":476 … ≥ MIN_FREE_KB = 2,097,152 (…)" add: "; a control's launch needs `CONTROL_MIN_FREE_KB` = 1,048,576 instead (rule F round 3, DH1; FILE(docs/probe/20261113_reg20/ops/common.sh:20)†, FILE(docs/probe/20261113_reg20/ops/launch.sh:52-53)†). It is RUNBOOK:26's per-launch rule (4 × r = 970,944 kB) rounded up to 1 GiB."
- Under the table at :491–498 add: "Under DH1 every figure in this table stays sufficient, since DH1 only lowers a control's floor. All 11 planned runs need 4,281,776 kB at the first launch (B19, the tenth launch, needs 2,097,152 + 9 × 242,736). That is short by 538,862 kB from the expected F1, 110,504 from F0 and 1,395,578 in E1's worst case. The 27-launch ceiling needs 7,680,080 kB (B19's second attempt, the 24th launch, needs 2,097,152 + 23 × 242,736)." (DERIVED: arithmetic as shown.)
- :500's last sentence becomes: "With E1's expected six runs, seven launches fit at `MIN_FREE_KB`, so arm A may stop for disk once two controls are due. Under DH1 that stop falls before a burst run or the drift run, never between a burst run and its control (DERIVED by exact enumeration with each open run cold with probability 0.10, a BELIEF from FILE(docs/decisions.md:4085), and no rerun: P(any disk stop) 0.0523, against the draft's 0.0815, of which 0.0319 fell between a burst run and its control)."
- :503's message becomes `STOP: only '<free>' kB free on the VM, <need> needed for <cfg>`.
- :506's second and third sentences become: "Under DH1 the stop cannot fall between a burst run and its due control unless that burst run wrote more than 2,097,152 − 1,048,576 = 1,048,576 kB, 4.3 × r (DERIVED)."
- :515's figure "4,524,512 kB" becomes "4,281,776 kB", and "8,408,288 kB" becomes "7,680,080 kB".
- :520 (b) becomes: "**(b)** Accept a disk stop mid-arm. Under DH1 it falls at a seed boundary, with no control late. The owner frees space at that stop, and the queue is started again; its [OPS] record is headed as DH2 says."
- :521 (c) becomes: "**(c), applied (rule F round 3, DH1):** a control's own floor `CONTROL_MIN_FREE_KB`, in `common.sh` (rule 5). The form 'burst runs need `MIN_FREE_KB` + r' was rejected: from the expected F1 it raises P(any disk stop) to 0.3439 with no gain in order (rule F round 3, appendix)."
- In "Tests" add the new sandbox count (section 9) and the four DH1 cases.

*Why this form, and why it is not a widening under rule A5.*
- The floor judges no run. It is set before any arm A run exists, and it equals the existing RUNBOOK:26 per-launch rule (FILE(agent/RUNBOOK.md:26)), which the draft already takes as the reading in force (FILE(docs/drafts/reg20_ops_decision_draft3.md:512)).
- A control launched at the floor leaves ≥ 1,048,576 − 242,736 = 805,840 kB if it writes r (DERIVED). The next launch, a burst run, needs `MIN_FREE_KB`, so the queue stops there.
- The fallback, `rulef-reg20-ops-draft3-r3-dh1alt.patch` (sha256 a934fe13d8c75f1a33611dcd56caf42bd34b93113058b69cd1450af7c5ae20ca), is option (c) as the draft wrote it, with a 256 MiB reserve: burst runs need `MIN_FREE_KB` + `CONTROL_RESERVE_KB` = 2,359,296. It never lowers a floor, so it suits an owner who reads any lower floor as a widening.
  - Its cost is a stop at the expected F1 with probability 0.3439. With no control due, the first launch needs 3,572,976 kB, against 3,310,832 (PROBE(r3dh/disk_enum.txt)).
  - It replaces `-dh.patch` and is not applied with it. Its sandbox result is in section 9.

**DH2. The end of the hold, and a heading rule for arm A's records (text).**

1. Draft :540 becomes:
   > **When it applies.** From the commit of the start entry (heading 3) until `final.sh`'s two output files are committed, or until arm A's end entry by a stop (`[OPS] REG-20 arm A ended by a stop: …`, point 18) is committed, whichever comes first (RC1 (b); RD4's "or an entry ends arm A", the stricter, by this section's merge rule; rule F round 3, DH2). An entry that stops arm A without ending it, such as a pause, a stop that waits for a decision, or an RD3 (ii) stop, does not end the hold. RC1 item 3's path under item 3 is the one exception, and it is not a breach.
2. Draft :541 becomes: "A later start heading, after an end by a stop, starts the hold again."
3. Draft :565 is kept, with this sentence added: "Only that commit (the SEALS row, `common.sh`'s `SEAL_BLOBS` and its `scripts_commit.txt`, reviewed) may be made while the hold applies. It lands after an entry that stops arm A and before the queue starts again, and that entry and the [RESULT] name both scripts commits." Item map M3's last sentence becomes: "Its commit is the hold's one named exception (rule F round 3, DH2); the `STOP_PAT` entry that precedes it does not end the hold."
4. Point 18, after :368, add:
   > **Headings of arm A's other records** (rule F round 3, DH2). Every other [OPS] entry about arm A is headed `## <date> · [OPS] REG-20 arm A: <what happened>`, with the colon right after "arm A". That covers a progress record, a disk stop the queue is started again from, the records RD3 asks for, a renewed session probe and `vm_checkout.sh`'s output. None of these matches `STOP_PAT` (sandbox). A heading matching `STOP_PAT` (`REG-20 arm A stops: …`, `… is halted …`) is written only when every script must stop until a decision, as at RD3 (ii). After it, the queue starts again only after a new start heading (:541).
5. The notice at :685: replace "until `final.sh`'s two files are committed or an entry stops arm A)" with "until `final.sh`'s two files are committed or arm A's end entry by a stop (`[OPS] REG-20 arm A ended by a stop: …`) is committed; a pause, or a stop that waits for a decision, does not end it)".
6. The [RESULT] duty at :572: replace "`<start entry's commit>`" with "`<the first start entry's commit>`". Add: "if arm A was started again, the output names each start entry's commit".
7. The sandbox cases in `-dh.patch`, after "and final.sh runs after it":
   - `[OPS] REG-20 arm A stops for disk: QUEUE STOP …s17 launch rc=2` refuses the queue ("a heading that stops arm A", rc 2);
   - `[OPS] REG-20 arm A: QUEUE STOP at seed 17's control (disk); restarted after the owner freed space` lets it run to `QUEUE DONE` (rc 0).

### 6. Optional items

**DH-O1. `configs/defaults.yaml` held to the pin** (`rulef-reg20-ops-draft3-r3-dho1.patch`, sha256 05806c4a88ad41dfc94668109a9744e50e2213eca3c50d2b103ff52981bb2feb).
- `harness/checks.py:48` merges today's `configs/defaults.yaml` beneath each run's config ("old run folders get today's defaults").
- `recheck_guards` compares that file only with HEAD (FILE(docs/probe/20261113_reg20/ops/common.sh:528)†), and `mac_checks` not at all. So a committed change, which the hold forbids by hand, would change every later recheck with no stop.
- The file equals the pin's and the checks commit's today (PROBE: `git diff --quiet 1cface7 HEAD -- configs/defaults.yaml` and the same against 5ee6e38, both 0).
- The patch adds, after the HEAD check in `recheck_guards`:
  ```
    # rule F round 3 (DH-O1): today's checks merge configs/defaults.yaml beneath each run's config (harness/checks.py:48),
    # so a commit to it would change the recheck silently; it is held to the pin, which it equals today.
    git diff --quiet $PIN -- configs/defaults.yaml || { MSG="configs/defaults.yaml differs from the pin's, and today's checks read it (DH-O1; the arm A hold)"; return 2; }
  ```
- Sandbox: a committed change stops the recheck, and nothing enters `runs/`.

**DH-O2. `vm_checkout.sh`: the dry run before the move, and on `already_at_pin`** (text; not tested).
- Move lines 33–35 to just before line 30, and change their header to `"# uv sync --frozen --extra server --dry-run on the VM, before any checkout:"`.
- Move line 39 with them, with its message ending "…: the owner decides before any checkout or run".
- The dry run then runs at E1's commit, whose `uv.lock`, `pyproject.toml` and `.python-version` are the pin's blobs (PROBE(docs/drafts/reg20_ops_r3/git_facts_20261114.txt), checked as held). A stop then changes nothing on the VM, and a second run cannot skip it.
- Lines 37–38 stay after the checkout.

**DH-O3. Quoting in headings 2 and 3** (text). Add to "Texts for headings 2 and 3":
> Every verbatim quotation is blockquoted (each line begins `> `), as at FILE(docs/decisions.md:2233), so that no quoted line begins `## `. A quoted line beginning `## <date> · [DECISION] (owner|delegate) REG-20 arm A starts: …` would pass `gate_in_log` before heading 3 (FILE(docs/probe/20261113_reg20/ops/common.sh:162-165)†). Any quoted `## ` line would also be read as an entry heading by `tools/check_docs.py:113`.

**DH-O4. RUNBOOK §4's start** (text, in `runbook_heading1.patch`, line 11).
- Replace "that is from REG-20's `docs/probe/20261113_reg20/ops/vm_checkout.sh` until arm A's end entry" with "that is from the commit of arm A's start entry (`[DECISION] (owner|delegate) REG-20 arm A starts: …`) until arm A's end entry".
- This matches :48 and point 18 (T6). The item map's N3 should note the change.

**Minor notes (no item).**
- (a) `README` step 4's first branch, "Only if E1 has not started", can never apply now that `e1_ended` requires E1's end entry (FILE(docs/probe/20261113_reg20/ops/common.sh:177)†). These are RC7 (c)'s words, kept verbatim, and they are harmless.
- (b) `e1_ended`'s lock message could add "if E1's queue is not running, the lock is stale: the owner's".
- (c) `launch.sh`'s 45 °C, 60 × 30 s, 24 × 5 s and 6 × 20 s are literals in code (FILE(docs/probe/20261113_reg20/ops/launch.sh:34-38,48,68-69,89)†), against rule 5's "no magic numbers". They come unchanged from ops_r3, as approved before, and are not new in draft 3.
- (d) A `uv run` on the Mac during the hold can re-sync a drifted `.venv`. `--no-sync` or `.venv/bin/python` keeps the hold's "the Mac's `.venv` is not changed" (FILE(docs/drafts/reg20_ops_decision_draft3.md:561)) mechanical. This is a BELIEF about uv's default.

### 7. The writer's additions (N1 to N7), each on its own

- **The once-only delegate heading check** (FILE(docs/probe/20261113_reg20/ops/common.sh:159-161)†): sound.
  - A second delegate heading, or one after an owner's, refuses (the sandbox cases at FILE(docs/drafts/reg20_ops_decision_draft3.md:299-307)).
  - An owner's rulings heading after the delegate's is accepted only with a new start heading after it (`sl > gl`, :165†), and only if the commit that last changed `owner_rulings.txt` adds a rulings heading (`rulings_ok`, :131-133†).
  - It cannot tell who wrote a heading. That is a content judgment, as for every heading.
  - Its one interaction is with quoted text (DH-O3): a quoted delegate heading refuses, which is fail-safe.
  - The heading probe confirms that heading 2's texts, as the draft words them, match `RULINGS_PAT` and `RULINGS_DLG_PAT`, and heading 3's text matches `START_PAT` (PROBE(r3dh/probe_headings.txt)).
- **N1, `e1_ended`, and its call in `session_probe.sh`:** sound (T5). The call at FILE(docs/probe/20261113_reg20/ops/session_probe.sh:14)† stops a boot record written during E1.
- **`vm_checkout.sh`** (ce5f842 → 1cface7), checked for each of the draft's claims:
  - every refusal comes before any change on the VM (:18–31†);
  - the ancestor test covers ce5f842 and any later descendant (:31†);
  - no push and no fetch;
  - `already_at_pin` changes nothing.
  - The one gap is T3 (DH-O2).
  - A shallow clone makes the checkout fail at :32†, and the script stops. BELIEF: git leaves the tree unchanged when the target object is missing.
  - An untracked file outside `runs/` makes the tree dirty and is refused, which is fail-safe (FILE(docs/drafts/reg20_ops_decision_draft3.md:720)).
- **N2, the disk point D:** see section 8. Its arithmetic is exact.
- **N3, the RUNBOOK §4 clause:** correct for the queue lock and for the `git checkout main` step. Its start is later than :48's (T6, DH-O4).
- **N4, RC6 (ii) as code** (`.sha256` lists, FILE(docs/probe/20261113_reg20/ops/common.sh:590-600)†): read and found consistent. Its three sandbox checks pass in every run.
- **N5, the per-pick list:** each line agrees with k1's labels and the outcome rule (FILE(docs/decisions.md:4076-4079); `analysis/k1.py` labels).
  - 2a can take a seed out of n;
  - 7 and 6 (b) add one to k_stuck in their cases;
  - 8 (b) takes no seed out by itself;
  - 9 (a) keeps `pending_control` in play;
  - 16 (a) changes no label.
- **N6, D1's seal row named in the hold:** correct. `analysis/withheld.py`'s present rows cover arm A's open runs and the drift run (FILE(analysis/withheld.py:27-29)).
- **N7, the stopped sandbox run:** acceptable as reported. The complete rerun, 428 of 428, reproduces (section 0).

### 8. Disk (attention point 2), in short

- **Arithmetic:** every figure at FILE(docs/drafts/reg20_ops_decision_draft3.md:479-498) is reproduced exactly (DERIVED; `r3dh/disk_enum.py` gives 3,310,832 and 4,524,512 for the draft's rule).
- **Attempts:** no path spends an attempt on a disk refusal. The check (:52†, :53‡) comes before the attempt record (:58†, :59‡).
- **Labels:** no path mislabels a run. A disk refusal writes no state record (DERIVED from FILE(docs/probe/20261113_reg20/ops/launch.sh:47-58)†).
- **Order:** the draft breaks "right after it" (T1). DH1 removes that.
- **Rule 5:** `MIN_FREE_KB` is a named setting in `common.sh`'s parameter block (FILE(docs/probe/20261113_reg20/ops/common.sh:19)†), as in E1's ops, whose header says "Every parameter of the scripts is set here" (FILE(docs/probe/20261113_e1/ops/common.sh:4-5), :34), and in ops_r3 (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:15)). `CONTROL_MIN_FREE_KB` sits beside it.
- **E1's rule:** a failed free-disk check is not a stop that ends E1 (FILE(docs/decisions.md:17072)). The draft and DH1 treat arm A's in the same way, restarting the queue once space is freed.

### 9. Test results (final)

- **DH1 + DH2 + DH-O1, plus the probe-only cases** (`r3dh/run6`: the † copy with `-dh.patch` and `-dho1.patch`, plus five PROBE lines, four of them checks, after "a dry-run sync that would change packages stops"): **passed 445, failed 0, exit 0** (PROBE(r3dh/sandbox_r3_dh_main.txt), sha256 71914aea…).
  - 445 = 428 + 2 (DH2) + 9 (DH1) + 2 (DH-O1) + 4 (PROBE). All three "none of these launched anything" checks pass.
  - The probe cases: a second `vm_checkout.sh` after that stop gives `VM ALREADY AT THE PIN`, exit 0; an `already_at_pin` record holds no dry-run output; then `session_probe.sh` gives `SESSION OK` with the VM at the pin (T3).
- **The fallback DH1 + DH2 + DH-O1** (`r3dh/run8`: the † copy with `-dh1alt.patch` and `-dho1.patch`): **passed 439, failed 0, exit 0** (PROBE(r3dh/sandbox_r3_dh1alt.txt), sha256 71a9c556…). 439 = 428 + 2 + 7 + 2.
- **Byte checks:** both run trees equal the patches applied to the † copy, apart from the probe lines in `run6`. `-dh.patch` with `-dho1.patch` gives the same files in either order (PROBE: `cmp` in `r3dh/ver_v1` to `ver_v5`).

### 10. My own errors in this review (rule A6)

1. **The first DH1 sandbox block was misplaced.** I put it inside the "pre-launch stops spend no attempt" block. Its launches made that block's closing check "none of these launched anything" fail: 1 FAIL in the fallback's first run, `r3dh/sandbox_dh.txt`, at 409 ok.
   - I stopped both runs, moved the block after that check in both patches (the patches above are the regenerated ones), and reran (section 9).
   - The two stopped runs, `r3dh/sandbox_dh.txt` and `r3dh/sandbox_dh_floor.txt`, are not evidence.
2. **A first reserve of 524,288 kB** for the fallback would have refused B19 from the expected F1 even with no control due (3,835,120 > 3,742,914 kB, DERIVED). I replaced it with 262,144 before any result was used.
3. **A first drift-run case ran the whole queue.** I replaced it with a pre-launch failure from the fourth launch.
4. **An unfound quotation.** An earlier note of mine quoted E1's [REG] as saying an owner's entry "may change the order". I did not find that sentence at HEAD (PROBE: `grep` of `docs/decisions.md`), and nothing here relies on it. The text at FILE(docs/decisions.md:17076) says the VM's tree "is moved only by E1's scripts or under an owner's entry".

### 11. Claims of draft 3 that I checked and that held

- the writer's sha256s (section 0);
- the pin is an ancestor of ce5f842;
- `harness/` at the pin equals a7bb77a's;
- `uv.lock`, `pyproject.toml` and `.python-version` at ce5f842 equal the pin's;
- the move back deletes no tracked file;
- `.gitignore` is the same at both ends, and `runs/` is ignored;
- the project is `package = false`;
- every per-pick DERIVED line (N5);
- the sandbox, 428 of 428, and pytest, 47 of 47, both reproduced;
- the disk arithmetic;
- E1_END_PAT against E1's registered headings;
- `STOP_PAT` does not match arm A's `QUEUE DONE` end entry;
- `owner_rulings_rd2.patch` gives exactly the six picks;
- HEAD b2fa956 touches only `agent/`, and its `vm_verify_list.zsh` skips arm A's sealed names (by pattern, and by `analysis/withheld.py`).

These rest on PROBE runs in the scratch copies (`git merge-base --is-ancestor`, `git diff --quiet`, `git ls-tree`, `shasum`), as recorded in `r3dh/` and in section 0.

### Appendix: probe outputs, verbatim

`r3dh/probe_patterns.txt`:
```
# rule F round 3: the patterns of draft 3 common.sh (scratch tree = e788191 + ops_draft3.patch) against heading variants
MATCH    E1_END_PAT  | ## 2026-11-14 · [OPS] E1: the queue ended (QUEUE DONE)
MATCH    E1_END_PAT  | ## 2026-11-14 · [OPS] E1: the queue ended (QUEUE END)
MATCH    E1_END_PAT  | ## 2026-11-14 · [OPS] E1 ended by a stop: QUEUE STOP second heat failure
MATCH    E1_END_PAT  | ## 2026-11-14 · [OPS] E1: the queue ended (QUEUE DONE), after the owner allowed a fourth attempt
no match E1_END_PAT  | ## 2026-11-14 · [OPS] E1: the queue ended (QUEUE END futility stop)
no match E1_END_PAT  | ## 2026-11-14 · [OPS] E1: the queue stopped (QUEUE STOP after an invalid run)
no match E1_END_PAT  | ## 2026-11-14 · [OPS] (delegate) E1 ended by a stop: QUEUE STOP x
no match E1_END_PAT  | ## 2026-11-14 · [DECISION] (owner) E1 ended by a stop: QUEUE STOP x
no match E1_END_PAT  | ## 2026-11-14 · [OPS] E1 ended by a stop:QUEUE STOP x
no match E1_END_PAT  | ## 2026-11-14 · [OPS] E1: the VM checked out at E1's registered commit ce5f842 by `vm_checkout.sh`
MATCH    STOP_PAT  | ## 2026-11-15 · [OPS] REG-20 arm A stops for disk: QUEUE STOP stage2_control_l1pl350ol_r2.0_w3000_s17 launch rc=2
MATCH    STOP_PAT  | ## 2026-11-15 · [OPS] REG-20 arm A stops after an invalid run: RUN burst_l1pl350ol_r2.0_w3000_s17 INVALID failed=client_lag
MATCH    STOP_PAT  | ## 2026-11-15 · [OPS] REG-20 arm A is stopped by a power-off; lost_ok written
MATCH    STOP_PAT  | ## 2026-11-15 · [OPS] REG-20 arm A halted for the owner (RD3 (ii))
no match STOP_PAT  | ## 2026-11-15 · [OPS] REG-20 arm A: QUEUE STOP at seed 17's control (disk)
no match STOP_PAT  | ## 2026-11-15 · [OPS] REG-20 arm A: the queue ended (QUEUE DONE)
MATCH    STOP_PAT  | ## 2026-11-15 · [OPS] REG-20 arm A ended by a stop: QUEUE STOP x
no match STOP_PAT  | ## 2026-11-15 · [OPS] REG-20 arm A: the VM checked out at the pin 1cface7 by vm_checkout.sh
```

`r3dh/probe_headings.txt`: `H2 matches RULINGS_PAT`, `H2 matches RULINGS_DLG_PAT`, `H2o matches RULINGS_PAT`, `H3 matches START_PAT`.

`r3dh/disk_enum.txt` (r = 242,736 kB; an E1 run = 71,393 kB; `MIN_FREE_KB` = 2,097,152; p_cold = 0.1, a BELIEF; exact over 2^5 control patterns; no reruns):
```
F0 (no E1 run): F1 = 4,171,272 kB
  draft        P(done) 0.9995  P(stop at a seed boundary) 0.0001  P(stop between a burst run and its control) 0.0004
  dh1_floor    P(done) 0.9999  P(stop at a seed boundary) 0.0001  P(stop between a burst run and its control) 0.0000
  alt_reserve  P(done) 0.9963  P(stop at a seed boundary) 0.0037  P(stop between a burst run and its control) 0.0000
E1 six runs (expected): F1 = 3,742,914 kB
  draft        P(done) 0.9185  P(stop at a seed boundary) 0.0496  P(stop between a burst run and its control) 0.0319
  dh1_floor    P(done) 0.9477  P(stop at a seed boundary) 0.0523  P(stop between a burst run and its control) 0.0000
  alt_reserve  P(done) 0.6561  P(stop at a seed boundary) 0.3439  P(stop between a burst run and its control) 0.0000
E1 18 runs (worst): F1 = 2,886,198 kB
  draft        P(done) 0.0000  P(stop at a seed boundary) 0.9820  P(stop between a burst run and its control) 0.0180
  dh1_floor    P(done) 0.0000  P(stop at a seed boundary) 1.0000  P(stop between a burst run and its control) 0.0000
  alt_reserve  P(done) 0.0000  P(stop at a seed boundary) 1.0000  P(stop between a burst run and its control) 0.0000
free needed at the first launch, draft: no control due 3,310,832 kB; all five due (11 runs) 4,524,512 kB
free needed at the first launch, dh1_floor: no control due 3,310,832 kB; all five due (11 runs) 4,281,776 kB
free needed at the first launch, alt_reserve: no control due 3,572,976 kB; all five due (11 runs) 4,543,920 kB
```

The p-sweep at E1's expected F1 (same model; PROBE: `python3 -I` on `r3dh/disk_enum.py`'s functions):
```
p=0.10  draft: between 0.0319 any 0.0815 | dh1_floor: between 0.0000 any 0.0523 | alt_reserve: between 0.0000 any 0.3439
p=0.25  draft: between 0.1406 any 0.3672 | dh1_floor: between 0.0000 any 0.2617 | alt_reserve: between 0.0000 any 0.6836
p=0.50  draft: between 0.3125 any 0.8125 | dh1_floor: between 0.0000 any 0.6875 | alt_reserve: between 0.0000 any 0.9375
p=0.75  draft: between 0.3516 any 0.9844 | dh1_floor: between 0.0000 any 0.9492 | alt_reserve: between 0.0000 any 0.9961
p=1.00  draft: between 0.0000 any 1.0000 | dh1_floor: between 0.0000 any 1.0000 | alt_reserve: between 0.0000 any 1.0000
```
