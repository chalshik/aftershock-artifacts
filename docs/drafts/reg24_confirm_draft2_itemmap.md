# REG-24 draft 2: item map for rule F round 1 (not registered)

Written 2026-11-14 ≈ 03:35 UTC (`date -u`) at HEAD `b46c279`.

- **The review:** `docs/drafts/reviews-2026-11-13/rulef-reg24-draft1-r1.md` (sha256 `ae2dd4bc…`), NOT READY on RE1–RE9.
- **The draft:** `docs/drafts/reg24_confirm_draft2.md`.
- **The code:** `docs/drafts/reg24_r2/reg24.patch` and `withheld.patch`.

Each row says where the item went and any departure from the review's text. Section names are the draft's.

## Required items

| item | resolved | where | departure |
|---|---|---|---|
| **RE1**: REG-19's whole-window cold side as a condition (T1) | Taken. The reviewer's `cold_side`; `stuck_not_cold` after `emptied_in_watch`, before `drop_inconclusive`; in `pair_outcome`'s list of labels that stand whatever the control; in `burst_table`. | Result: (d2), label 7, the thresholds' "From REG-19"; Prediction: a `stuck_not_cold` row (P ≈ 0.04, the writer's); Design inputs: λp 2.045 (`inputs` `lam_p_cold_side`, new) | None. The label is item 7 because the list keeps `inconclusive` (NaN cold side) as item 6. That is the review's own order in code. |
| **RE2**: one emptying pass (T2) | Taken. `burst_table` computes `emptyings(run, burst_end, drop_end)` once; split at 5580 s by start time. | Result: "One emptying pass", (f) in the review's words | None. |
| **RE3**: (g), K3 and `after_empty` on the drained total line (T3) | Taken. `owed_series`, `drained_at`; (g) needs a gauge emptying and a drain; K3's `measured_s` is the drain; the gauge's first zero is kept as a readout (`first_empty_s`, `label_first_empty`); `after_empty` is read from the drain. | Result: "The total line and the drain", (g), K3, `after_empty`; Decision: `no_return`; Alternatives 3 and 4 | (g) is split into two sentences; the words are the review's. `drop_inconclusive` raised from 0.05 to 0.06 under (a) for the stricter test (the writer's BELIEF). |
| **RE4**: both runs from one build | Taken. `table` gives `not_same_build` unless both `env.json` `git_commit` are set and equal. | Result: "Both runs from one build"; Operations: "The VM pin" (the review's text, quoted); Stopping rule: a valid run at another commit stops the queue; Decision: `not_same_build` | The review's "Operations" text is quoted in the ops sketch, with one line saying that "the registration commit" is the one in `reg24_commit.txt`. |
| **RE5**: the seal and the queue before registration | Taken. The two exact `SEALS` rows. | `withheld.patch`; "Withheld"; "What must exist before approval, and before the first launch"; "Operations: a sketch" | (1) The seal is a separate patch, `withheld.patch`, against `b46c279`, so that it can land on its own (REG-20 arm A's hold, RD4). (2) The reviewer's test is replaced by `test_reg24_seal_covers_exactly_its_two_configs`, which checks config names via `load_config`, with `sealed == want & names`. So it passes with or without REG-24's configs in the tree. A second test, `test_reg24_seal_lifts_only_on_its_result`, was added. (3) Stricter than the review: the seal, the configs commit and the ops scripts (with their own rule F pass) must exist before the *approval*, not only before the first run. (4) The ops scripts are not written. They are a precondition with a sketch modelled on E1's `docs/probe/20261113_e1/ops/` (the brief). |
| **RE6**: decisions fixed now, with rule H's bound | Taken, the review's text. | "What REG-24 can change, and what it cannot" (said first, rule A1), repeated by reference in "Decision under each outcome"; Stopping rule: `burst_missing` | (1) The `confirms` sentence leaves "[the largest such difference among the [n] schedules …]" as a placeholder for `reg24_tilt`'s output, or for the reviewer's count marked as such (RE9). (2) `drop_inconclusive` has two sentences, one under (a) and one under (b). (3) Under `not_persistent` the sentence also names the end-window mix (RE-O1). Under `stuck_not_cold` it names c and λp. (4) It adds "`control_warm` says the warm state lasts on this schedule, not at λ = 2.0 in general" (review §2). |
| **RE7**: freeze evidence a reviewer can check | Taken in part. `confirm_frozen.py` (sha256 `6801457c…`, the value draft 1 gave) and the freeze record were found in the agent's scratchpad and copied unchanged. A comparison tool and its output show which symbols are byte-identical. | Seed and drop: "Timing"; `docs/drafts/reg24_r2/frozen/` | (1) The files are in `reg24_r2/frozen/`, not `reg24_r1/`. (2) The frozen `tests/test_confirm.py` (`867aba60…`) was **not found**, so the tests' freeze is BELIEF on the freeze record alone (the review's fallback wording, for that file only). (3) `frozen_to_draft2.diff` replaces `frozen_to_registered.diff`, since nothing is registered yet. (4) `compare_frozen.py` is added. It compares symbols by source text and imports neither file. Its output: frozen → draft 1 changes only `REG24`'s seed and drop and `inputs`; frozen → draft 2 has 48 symbols the same (`CONFIGS`, 26 other `REG24` keys, `_resolved`, `burst_cfg`, `control_cfg`, `phases`, `judged_windows`, `_rate`, both models, `used_seeds`, `candidate_seeds`, `design_row`, `seed_rule`, `seed_scan`, `model_check_reg19`, `emptyings`, `_flat`, `check`, `_one`), 12 changed and 11 added. (5) The draft 1 claim "revert those two hunks …" is not repeated. |
| **RE8**: the owner's approval of the drop and the §6 row | Taken, the review's text. | Setup: "Owner approval needed, named separately"; "What must exist", item 4; Open points 1 | The row's date is "2026-11-1x", not the review's "2026-11-14", because the approval date is not known. The draft adds a consequence: the delegate cannot approve until the owner has ruled on the drop. |
| **RE9**: the tilt from a committed function (T5) | Taken in code. Not run in full. | Design inputs: "The tilt from a committed function"; Alternatives 1; Open points 5 | (1) `tilt_scan` also returns `n_positive` and `median`. (2) Only seeds 43 and 61 were run (+0.165 for the pick; seed 61 +0.107 at 5400 s and +0.083 at 9000 s; `test_tilt_scan_on_the_pick_and_seed_61`). The full scan over 160 seeds (640 schedules) was **not run**, because the brief for draft 2 says not to re-run the seed scan. The review's "0 of 25 larger, median +0.003, 13 of 25 positive" is quoted as the reviewer's one-off figure (FILE(docs/drafts/reviews-2026-11-13/rulef-reg24-draft1-r1.md:100)), not provenance under rule I. Whether `reg24_tilt` runs once before the [REG] is open point 5. |

## Optional items: all eight taken

| item | resolved | where | departure |
|---|---|---|---|
| **RE-O1**: the end window measured in the drop (T4) | Taken. `released_after` (the review's code), and `burst_table`'s `end_window_mix` with `released_in_drop`, `pf_by_sent_prev` and `pf_by_sent_end`. | Result: readouts; Decision: `not_persistent`; `test_released_after_counts_late_and_unsent_requests` | None. |
| **RE-O2**: a co-tenant on the GPU | Taken. `cotenant(run)`: per phase, `mem_used_mib` max − min from `run["gpu"]`; `env.json` `gpu_processes`; event `gpu_processes_end`. In both tables. | Result: readouts; Alternatives 7; `test_cotenant_readout` | (1) The end-of-run process list was added. (2) The review says the list "is read only before launch (FILE(harness/run.py:97))". In fact the harness also reads it at the end (FILE(harness/run.py:214)), and the launch list comes from FILE(harness/env_snapshot.py:44). The draft states both. My own first `cotenant` docstring repeated the review's phrase. It was fixed and the patch regenerated (see "Writer's corrections", W7). |
| **RE-O3**: test robustness | Taken. The pick test monkeypatches `candidate_seeds` to `range(40, 200)`. `test_seed_range_is_unused_and_outside_reg20b` now guards that no config other than REG-24's sets seed 43, instead of requiring 40–42 to be unused. | Seed and drop | None. |
| **RE-O4**: K3's band as an r interval | Taken. `implied_r(sched, cfg, drained_s)` by bisection on `READOUT["r_bracket"]` (0.5, 1.5) × U_off. It is reported in `burst_table`'s `k3`. The text says J1's 0.05 is a tolerance on a median over runs, with REG-21's per-run spread. | Drop length: "The band is a tolerance"; Result: K3; Prediction: implied r; `test_implied_r_inverts_the_token_model` | The bracket is the reviewer's value and judges nothing. `implied_r` returns NaN for a drain past what r = 0.5 predicts. |
| **RE-O5**: the factor-two length in code | Taken. `inputs()` `factor_two_s` = 4859.36, by the review's formula. The text is corrected to 2430 s and 4859 s. | Drop length: "The factor of two"; `test_inputs_schedule_facts_at_the_pick`, `test_readout_constants_are_the_studys` | `floor_8` 1.681 is in a new `READOUT` dict, not in `REG24`, so that `REG24` stays byte-identical to the frozen file apart from seed and drop. The test checks `READOUT["floor_8"] == k2.E0["floor_8"]` and that `"floor_8" not in REG24`. |
| **RE-O6**: the planned dips (wording) | Taken in substance. | Design inputs: "The planned dips do not reach the server directly"; Prediction: `emptied_in_watch` lowered from 0.05 to 0.03 | The review's "about 1000–1700 owed requests through the watch (request model)" is replaced. Its lower figure has no committed source that I could check without a new computation. The draft gives REG-19's measured total lines instead (444–811 at 600 s after the burst, 1050–1511 at 3000 s, FILE(docs/decisions.md:16533)–FILE(docs/decisions.md:16537)), plus the model's 1670 at the watch's end. |
| **RE-O7**: both timing sources (wording) | Taken. | Why now: "The two sources on timing"; Order | None; "the owner sets the order" is kept. |
| **RE-O8**: `step` computes only the outcome | Taken. The new `control_outcome(run)` is the decisive part. `control_table` = `control_outcome` + readouts. `step` calls `control_outcome` alone. | Result: Commands; `test_step_computes_no_readout`, `test_step_continues_only_after_a_warm_control` | None. |

## Traces, the alternative, §3 and the writer's open points (review §1–§4)

| review item | where it went |
|---|---|
| T1 (a long drain read as stuck) | RE1; Alternatives 2 |
| T2 (an emptying just before the watch's end) | RE2; (f) |
| T3 (a gauge zero is not a drained line) | RE3; (g); K3; Alternatives 3 |
| T4 (the end window's pf measured in the drop) | RE-O1; Decision `not_persistent` |
| T5 (the pick has the largest admitted tilt) | RE9; Design inputs; Alternatives 1; the `confirms` sentence |
| §2, clients' backlog against the pool, not C2's loop | Alternatives 8, as "not ruled out"; the `confirms` sentence ends "It does not test C2's chain"; the `control_warm` scope sentence under Decision |
| §2, K3's opposite biases | Prediction: "Biases in opposite directions"; RE-O4's implied r |
| §3, can the run change a decision | "What REG-24 can change, and what it cannot" (said first); "In no case does REG-24 start, stop or size another run" |
| §4.1, the drop needs the owner | RE8; Open points 1 |
| §4.2, keep the frozen rule; seed 61 also tilts | Seed and drop: "The frozen rule stands"; the tilt numbers |
| §4.3, the factor-two rule holds | RE-O5; "W alone decides the pick" |
| §4.4, r = 0.95 matters only for K3; the band is r ∈ [0.95, 1.05] | Drop length: "The band is a tolerance, not a prediction interval"; RE-O4 |
| §4.5, no commit holds the frozen state | RE7 |
| §4.6, seal and queue before registration | RE5 |
| §4.7, power-off risk; three invalid burst attempts | Stopping rule: `burst_missing`; Alternatives 5; Prediction: P(valid) |
| §4.8, pinned values as regression guards | No change (agreed) |

## Option (b), the brief's addition (FILE(agent/FOR_AUTHOR.md:11), item −18)

- **Section:** "Under option (b), 1800 s: what changes" in the draft.
- **Not decided:** the choice among (a), (b) and (c). The draft is complete under (a).
- **Not re-run:** the seed scan. No new seed or rule is picked (rule A5). No schedule at 1800 s was built.
- **Stated:**
  - (b) has no design under the frozen rule, and keeping seed 43 at 1800 s would be a new, post-scan choice and the owner's;
  - the code and config changes it would need;
  - P(`drop_inconclusive`) ≈ 0.70 given a warm control and a valid burst run, and ≈ 0.53 unconditionally;
  - K3 likely `undefined`;
  - the cost: ≈ 5.10 h for the pair, ≈ 4.6 h expected, ≈ 15.3 h at most, ≈ 4.0 h less than (a);
  - which outcomes stay informative (condition 5 in full; condition 6 only if the line drains within 1800 s, P ≈ 0.06).

## Writer's corrections (rule A6; none silent)

| # | what was wrong | where | fixed how |
|---|---|---|---|
| W1 | Draft 1 said "REG-16 went cold at 2.2 after a 2.78 peak". The 2026-11-10 [CORR] withdrew that figure (FILE(docs/decisions.md:3417)–FILE(docs/decisions.md:3422)): the tip followed a 120 s peak of 3.45. | Prediction, `control_warm` | Corrected and stated. P stays 0.85, with the reasons for and against written out. |
| W2 | Draft 1 said that a drop-first pick (seed 61 at 5400 s) is "about 1 GPU h cheaper for the pair (2 × 3600 s)". 2 × 3600 s is 2 h. | Seed and drop: post-pick scan | Corrected to ≈ 2 GPU h, and stated. |
| W3 | Draft 1 said that the drain needs "about 3600–5300 s". The rows give 4960, 5060 and 5280 s (the later pessimistic time + 1200 s on seed 43's three schedules that drain). | Seed and drop | Replaced with the three values, and stated. |
| W4 | Draft 1 paraphrased REG-16's review N5 as "taking the shortest drop first picks the lightest schedule". The line says "the lowest-seed rule picks the seed with less room" (FILE(docs/decisions.md:3167)). | Seed and drop | Quoted. The frozen `seed_rule` docstring carries draft 1's paraphrase and is left byte-identical. The draft says so. |
| W5 | Draft 1 cited FILE(docs/decisions.md:3766) for REG-19's 240 MB per run. The figure is in that entry's "Cost" line, FILE(docs/decisions.md:3819), where it is itself scaled from REG-18. | Cost | Citation corrected, and the double scaling stated (BELIEF). |
| W6 | Draft 2's first write cited FILE(docs/drafts/reg20_ops_decision_draft3.md:41) for "E1 is running". That line is about the checkout. | Order | Now FILE(docs/decisions.md:19394) for the checkout, and FILE(docs/decisions.md:19452) for "with E1 running" at 02:54 UTC. |
| W7 | My `cotenant` docstring said the process list "is checked only before launch", which FILE(harness/run.py:214) contradicts. | `analysis/confirm.py` | Docstring fixed. `reg24.patch` regenerated (sha256 in `SHA256SUMS.txt`). Targeted tests, the full suite, the inputs readout and the frozen comparison were rerun on it under new stamps. The four earlier outputs are kept and marked superseded. Their result lines are identical apart from the comparison's sha256 line (DERIVED, `diff`). |
| W8 | The first inputs file's header said `runs/` did not exist in the export. It holds the tracked empty `.gitkeep`. | `inputs_43_9000_20261114T031548Z.txt` (superseded) | Header line corrected after writing, with that fact noted in the header. The output line was unchanged. The new file `inputs_43_9000_20261114T033247Z.txt` has the right header from the start. |
| W9 | The first targeted-tests file passed `-k` across several files and so deselected tests (79 passed, 106 deselected). | `tests_targeted_20261114T031012Z.txt` (superseded) | Rerun without the filter (71 / 69 / 16 passed, and `test_gate.py -k reg15` 6 passed, run separately). |
| W10 | Draft 2's first write said "six of the eight optional items" were taken, and said the reviewer added 4 tests. In fact all eight were taken, and the reviewer's patch adds 8 collected tests (4 functions, 4 parametrized rows); this draft adds 5. | Preamble; Adversarial review; Code and tests | Corrected from `pytest --collect-only` on both exports. |
| W11 | Draft 2's first write counted "all 25 other `REG24` keys" as unchanged. There are 26. | Seed and drop: Timing | Corrected from the comparison output. |
| W12 | Draft 2's first write gave P(`control_not_warm`) ≈ 0.14 under (a). 0.97 × 0.15 = 0.1455, which rounds to 0.15. "Not tested" was 0.06; by the stated parts it is 0.05. | Prediction | Corrected, with each product written in the table. |
