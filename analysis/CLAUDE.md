# analysis/ rules

- Read only from `runs/<id>/`. Never write into a run folder. Save figures to `analysis/figures/` (gitignored is fine).
- Load runs through `load.py` so every figure uses the same definitions: percent fast per arrival second, with unfinished requests counted as misses.
- Compute rates from differences of raw counters. A counter that goes down means a restart, so flag it and don't hide it.
- Exclude a run that `checks.json` marks invalid unless the figure is about invalid runs.
