# Process

How this study is worked. `CLAUDE.md` holds the short form of each rule; this file holds the full text. Installed 2026-11-04 (decisions.md, `[DECISION]` entries of that date). Changing it needs the owner (CLAUDE.md C).

## 1. Evidence tags (rule B)

Every factual statement in a doc, an entry or a reply carries one tag.

| Tag | Use for | Example |
|---|---|---|
| `RUN(run_id, function)` | a number computed from a run folder by a named function in `analysis/` | `RUN(20261030-151441_sweep_pc_on_r10, load.summarize)`: throughput 4.185 req/s |
| `SOURCE(vLLM 0.32.0 path:symbol)` | behaviour read from the pinned source | `SOURCE(vLLM 0.32.0 v1/core/block_pool.py:get_usage)` |
| `FILE(path:line)` | what a file in this repo says or does | `FILE(analysis/load.py:152)` sets hit = 0.0 when a window has no queries |
| `PROBE(path)` | output of `env/probe.py` | `PROBE(docs/probe/20261023_Qwen3-4B/server.log)` |
| `DERIVED` | arithmetic on tagged values; show it | `DERIVED`: 1 − 4.185 / 4.735 = 0.116 |
| `BELIEF` | anything else. Not evidence | If it can be checked, it goes into `docs/open-questions.md` |

- Commit messages, chat history, earlier replies and impressions are not evidence. A decisions.md entry is a record of a claim, not its evidence: cite the run and function it rests on.
- A number with several computations (definitions.md ⚠) names the computation: `RUN(id, load._level)`, not just "hit".
- Several values from one function and one run set can share one tag at the end of the sentence or table caption.

## 2. Templates (rule E)

Every decisions.md heading reads `## YYYY-MM-DD · [TAG] title`, with exactly one tag. `tools/check_docs.py` enforces this from the first tagged entry on; older entries stay as written.

| Tag | Use for |
|---|---|
| `[REG]` | a registration, written and committed before the run or analysis it registers |
| `[RESULT]` | the result of a registered run or analysis; must cite `RUN(...)` |
| `[CORR]` | a correction of an earlier entry, doc or number |
| `[DECISION]` | a choice: by the owner, or by the agent within its authority |
| `[OPS]` | operations: VM, data copies, cooling, backups |

### Registration `[REG]`, written before any run or analysis
```
## YYYY-MM-DD · [REG] <ID>: <title>
- ID: REG-<n>
- Question:
- Claim tested: C1 / C2 / a model in docs/model.md (name it)
- Prediction, as a number: (and the model it comes from, M<n>)
- Decision under each outcome: outcome → decision (if no outcome changes a decision, stop: rule A1)
- Alternatives ruled in or out by this design:
- Design: configs, seeds, n per cell, run ids to be analyzed (for analyses of existing runs)
- Analysis plan: functions (file:symbol), windows, thresholds; anything new goes into config or this entry now
- Stopping rule:
- Cost: GPU hours (0 for an analysis of existing runs)
- Adversarial review (section 3): verbatim output, and what was changed because of it
```

### Result `[RESULT]`
```
## YYYY-MM-DD · [RESULT] <ID>: <title>
- Registration: REG-<n> (date)
- Runs: RUN(id, function) for each; validity of each
- Per cell: k of n, with the 95 % Clopper–Pearson upper bound (section 5)
- Prediction: hit or miss, with the number observed against the number predicted; update docs/model.md's ledger
- Alternatives still open:
- Decision taken:
```

### Correction `[CORR]`
```
## YYYY-MM-DD · [CORR] <title>
- What was wrong: (quote the entry or doc, with its date or FILE(path:line))
- Since when:
- Which results it affects: list them, including "none" with the reason
- Re-check done: function and runs, with the result
- Rule that would have caught it (section 7):
```

## 3. Adversarial review (rule F)

Before any `[REG]` is committed, a separate pass (a subagent, or a fresh session) receives **only** the registration text and the code diff it depends on. It does not see the conversation, the expected outcome's rationale, or results. It must return:
1. **A trace on which the verdict comes out wrong:** concrete numbers for the windows the analysis reads, where the rule says stuck but the server is not, or the reverse.
2. **The strongest alternative explanation** for each outcome the registration expects.
3. **Can the run change any decision?** Yes or no, and which.

The output goes verbatim into the `[REG]` entry, followed by what was changed because of it. If the review shows that no outcome changes a decision, the run is not proposed (rule A1).

## 4. Feasibility gate (rule G)

Before any shock matrix (more than one trigger run), compute whether a stuck state is possible at the candidate load, from existing or cheap runs, with the pass condition registered first:
- a healthy no-trigger control at the candidate load, at least 2400 s, `recovered`;
- the peak completion rate of the setup (cache on);
- the completion rate in deep overload (cache on, and cache off).

The model is M2 in `docs/model.md`. Default pass condition, to be restated in each `[REG]`: the candidate λ must lie strictly between the cold-state completion rate and the warm capacity, with the cold-state completion rate measured, not assumed. If it fails, the matrix is not run, and the reason is logged.

## 5. Statistics (rule H)

- Report every cell as "stuck in k of n", with the **one-sided** 95 % Clopper–Pearson upper bound on the stuck probability (`analysis/stats.py`, `cp_upper`). For k = 0 this is 1 − 0.05^(1/n): n = 3 → 0.63, n = 5 → 0.45, n = 6 → 0.39 (DERIVED). The two-sided 95 % bound is larger (n = 3 → 0.71); say which one is used.
- A cell is one setup × trigger × size × load. Do not pool cells without writing down the assumption that makes them one population, typically a common stuck probability, and why it is plausible. Seeds 1–3 are reused in every cell, and seeds share random streams across loads (decisions.md 2026-11-04 audit), so cells are not independent draws; say so whenever cells are pooled.
- A control with one seed is labeled "single-seed control". Shock seeds 2–3 have no same-schedule control in any cell so far.
- Means hide spikes: when a mean is reported for a window, also report the minimum span or the distribution if a span is shorter than the window (lesson of the 2026-11-01 KV-mean correction).

## 6. Provenance and consistency (rule I)

- Every number in the docs comes from a named function in `analysis/`, applied to named run ids, and is tagged `RUN(...)`. One-off scripts are not provenance: commit the function first, then quote its output.
- `tools/check_docs.py` (run by `uv run pytest`, `tests/test_check_docs.py`) checks: every run id in the docs exists; validity claims match `checks.json`; status.md's run inventory matches `runs/`; decisions.md tags and append-only history; `FILE(path:line)` targets exist; the context pack is current; no used config changed after use.
- `tools/context_pack.py` writes `docs/context-pack.md` (status, PROTOCOL, definitions, the model ledger, open items, the last 5 decisions entries). It is generated and never edited by hand (`.claude/settings.json` denies direct edits). The session-start hook prints `--digest`, a summary under 10,000 characters, because Claude Code caps hook context at that size.

## 7. Errors already made, and the rule that now catches each

| Error (decisions.md) | Rule that would have prevented it |
|---|---|
| Baseline window put the burst inside the baseline; found after the λ = 3 burst results (2026-11-02) | F: the adversarial pass must build a trace on which the verdict is wrong; a burst trace makes it `bad_baseline` at once. Plus a test of `verdict` on a burst trace before the run |
| τ missing from "Stage 1 finished" (2026-10-31) | Section 8: a stage ends only after every item of the plan's "Inputs" and "Outputs" tables is checked, not only "Done when" |
| F + W model code never committed, twice (2026-11-01, 2026-11-02) | I: numbers only from committed functions, tagged `RUN(...)` |
| Mean KV 0.41 hid a collapse in progress (2026-11-01) | A3 and section 5: a mean is reported with its minimum span or distribution |
| Hit rates from two computations compared as one (2026-11-02, 2026-11-03; found 2026-11-04) | J: every quoted hit names its computation |
| 5 s gaps recommended as the most promising change, then reversed (2026-11-03) | A1: a numeric prediction (here W at 5 s) before proposing a run |
| An old decisions entry edited in place (commit `cfc18da`, 2026-11-02; found 2026-11-04) | `check_docs` append-only check |
| `poisson_rate_upper` underflowed at real-data counts (REG-1, 2026-11-04) | Tests of numeric helpers include inputs at the scale of the real data |

## 8. Ending a stage

A stage is finished only when every row of the plan's input and output tables for it, every "Done when" box, and every open question for it has an answer with evidence. If any is answered "not applicable" or "dropped", that is a `[DECISION]` entry by the owner.

## 9. Data

- `runs/` is the canonical raw data and exists only on the Mac (status.md, Watch). The owner decided on 2026-11-05 that the copies stay on the Mac (decisions.md 2026-11-05 [DECISION]).
- A checksum manifest (`sha256` of every file in `runs/`) is kept at `manifests/runs.sha256` (decisions.md 2026-11-04 [OPS]); `python3 tools/manifest.py verify <copy>` checks any copy without the VM.
