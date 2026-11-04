# analysis/ rules

- Read only from `runs/<id>/`. Never write into a run folder. Save figures to `analysis/figures/` (gitignored is fine).
- Load runs through `load.py` so every figure uses the same definitions (`docs/definitions.md`). Percent fast has two computations: per 1 s arrival bin (`percent_fast`) and pooled over a window (`_level`, which feeds `verdict` and `ramp_table`). Both count unfinished requests as misses. Name the one you use.
- Every number that goes into the docs comes from a committed function here, applied to named run ids, and is quoted as `RUN(run_id, function)` (`docs/process.md` §1, §6). No one-off scripts.
- Never compute an analysis that a pending `[REG]` covers before the owner approves the registration.
- Compute rates from differences of raw counters. A counter that goes down means a restart, so flag it and don't hide it.
- Exclude a run that `checks.json` marks invalid unless the figure is about invalid runs.
