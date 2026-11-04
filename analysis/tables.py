"""Committed drivers for the tables quoted in docs/decisions.md and docs/status.md. Read-only on runs/.

    uv run python -m analysis.tables verdicts | ramps | sweeps | capacity | arrivals | published

Every table carries the commit it was computed at (`provenance`), so a quoted number can name its code
(docs/process.md §6). Thresholds come from the run configs or are the registered ones named below; nothing is chosen here.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from analysis import load as L

REPO = Path(__file__).resolve().parent.parent
VERDICT_KEYS = ("control_t_s", "baseline_s", "watch_s", "end_s", "min_baseline_pf", "recovered_pf_drop", "recovered_hit_drop",
                "recovered_q_excess", "stuck_pf_drop", "stuck_hit_drop", "hit_climb", "pf_climb", "drain_horizon_s")
# Capacity rule, registered 2026-10-30 (decisions.md): throughput >= 0.95 lambda, waiting slope <= 0.01 req/s.
CAPACITY_RULE = {"min_throughput_frac": 0.95, "max_q_slope": 0.01}
# Spans of the 2026-11-04 schedule [RESULT] (decisions.md): the measured window 240-900 s of a 900 s sweep.
ARRIVAL_SPANS = [(240, 390), (390, 540), (540, 690), (690, 750), (750, 900)]
# Sweep parents per setup, and the published capacities (decisions.md 2026-10-30, 2026-11-02, 2026-11-03).
SETUPS = {"default_20s": ("sweep_pc_on", "sweep_pc_off", 4, 2), "kv72k_20s": ("sweep_kv72k_pc_on", "sweep_kv72k_pc_off", 4, 2.5),
          "default_5s": ("sweep_gap5_pc_on", "sweep_gap5_pc_off", 6, 2.5)}
# Published verdict claims: every judged Stage 2 run is `recovered` except these two controls (decisions.md
# 2026-11-02 "No-trigger controls done", "Controls at the 72,480-token pool").
PUBLISHED_NOT_RECOVERED = {"20261101-202808_stage2_control_cap_r4": "bad_baseline",
                           "20261102-225146_stage2_control_kv72k_r3.5": "bad_baseline"}


def provenance() -> dict:
    git = lambda *a: subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True).stdout.strip()
    return {"commit": git("rev-parse", "--short", "HEAD"), "dirty": bool(git("status", "--porcelain", "--untracked-files=no"))}


def judgeable(run: dict) -> bool:
    v = run["cfg"].get("verdict") or {}
    return all(v.get(k) is not None for k in VERDICT_KEYS)


def _preemptions(m: pd.DataFrame) -> float:
    p = m["vllm:num_preemptions_total"]
    return float(p.iloc[-1] - p.iloc[0])


def verdict_row(run: dict) -> dict:
    row = {"run": run["dir"].name, "valid": bool(run["checks"] and run["checks"]["valid"]),
           "rate": run["cfg"]["workload"]["rate"], "trigger": (run["cfg"].get("trigger") or {}).get("kind", "none")}
    try:
        v = L.verdict(run)
    except Exception as e:  # e.g. a run stopped early: an empty window
        return {**row, "verdict": None, "error": f"{type(e).__name__}: {e}"}
    row["verdict"] = v["verdict"]
    for part in ("baseline", "end"):
        row.update({f"{part}_{k}": x for k, x in v[part].items()})
    row["preemptions"] = _preemptions(run["metrics"])
    return row


def verdict_table(pattern: str = "*") -> pd.DataFrame:
    """`load.verdict` for every run (valid or not) whose config has the full verdict block."""
    rows = [verdict_row(r) for r in L.find_runs(pattern, valid_only=False) if judgeable(r)]
    return pd.DataFrame(rows)


def ramp_tables(pattern: str = "*ramp*") -> pd.DataFrame:
    out = []
    for r in L.find_runs(pattern, valid_only=False):
        t = L.ramp_table(r)
        t.insert(0, "run", r["dir"].name)
        out.append(t)
    return pd.concat(out, ignore_index=True)


def sweep_table() -> pd.DataFrame:
    """`load.summarize` for every sweep run, with whole-run hit and preemption totals (first to last scrape)."""
    rows = []
    for r in L.find_runs("*", valid_only=False):
        if not r["cfg"].get("sweep_parent") or not len(r["metrics"]):
            continue
        s = L.summarize(r)
        s["parent"] = r["cfg"]["sweep_parent"]
        has_hit = "vllm:prefix_cache_queries_total" in r["metrics"] and r["metrics"]["vllm:prefix_cache_queries_total"].iloc[-1] > 0
        s["whole_run_hit"] = L.whole_run_hit_rate(r) if has_hit else np.nan
        s["preemptions"] = _preemptions(r["metrics"])
        rows.append(s)
    return pd.DataFrame(rows)


def capacity_table(sweeps: pd.DataFrame | None = None) -> pd.DataFrame:
    """μ_warm and μ_off per setup by the registered rule, over valid runs only, next to the published values."""
    sw = sweep_table() if sweeps is None else sweeps
    rows = []
    for setup, (on, off, pub_on, pub_off) in SETUPS.items():
        mu = {p: L.capacity(sw[(sw.parent == p) & sw.valid.astype(bool)], **CAPACITY_RULE) for p in (on, off)}
        rows.append({"setup": setup, "mu_warm": mu[on], "mu_warm_published": pub_on, "mu_off": mu[off], "mu_off_published": pub_off})
    return pd.DataFrame(rows)


def arrival_profile(schedule: pd.DataFrame, rate: float, spans=ARRIVAL_SPANS) -> dict:
    """Planned request rate per span, as a share of λ, plus the whole-window share. All requests, bursts included."""
    t = schedule.t_planned
    out = {f"{a}-{b}": float(((t >= a) & (t < b)).sum() / (b - a) / rate) for a, b in spans}
    lo, hi = spans[0][0], spans[-1][1]
    out["window"] = float(((t >= lo) & (t < hi)).sum() / (hi - lo) / rate)
    return out


def arrival_table() -> pd.DataFrame:
    """`arrival_profile` of every sweep's written schedule (an input, not an outcome)."""
    rows = []
    for d in sorted(L.RUNS.glob("*")):
        if not (d / "config.yaml").exists() or not (d / "schedule.parquet").exists():
            continue
        cfg = yaml.safe_load((d / "config.yaml").read_text())
        if not cfg.get("sweep_parent"):
            continue
        rate = cfg["workload"]["rate"]
        rows.append({"run": d.name, "parent": cfg["sweep_parent"], "seed": cfg["seed"], "rate": rate,
                     **arrival_profile(pd.read_parquet(d / "schedule.parquet"), rate)})
    return pd.DataFrame(rows)


def published_check(verdicts: pd.DataFrame, capacity: pd.DataFrame) -> list[str]:
    """Differences from the published claims: verdicts of valid runs, and μ per setup. Empty means all agree."""
    out = []
    for _, r in verdicts[verdicts.valid].iterrows():
        want = PUBLISHED_NOT_RECOVERED.get(r.run, "recovered")
        if r.verdict != want:
            out.append(f"{r.run}: verdict {r.verdict}, published {want}")
    for _, c in capacity.iterrows():
        for k in ("mu_warm", "mu_off"):
            if c[k] != c[f"{k}_published"]:
                out.append(f"{c.setup}: {k} {c[k]}, published {c[f'{k}_published']}")
    return out


def main(argv: list[str]) -> int:
    pd.set_option("display.width", 250, "display.max_columns", 60, "display.max_rows", 500)
    what = argv[0] if argv else "published"
    print(f"# {what} | {provenance()}")
    if what == "verdicts":
        print(verdict_table().round(4).to_string(index=False))
    elif what == "ramps":
        print(ramp_tables().round(4).to_string(index=False))
    elif what == "sweeps":
        print(sweep_table().round(4).to_string(index=False))
    elif what == "capacity":
        print(capacity_table().to_string(index=False))
    elif what == "arrivals":
        print(arrival_table().round(3).to_string(index=False))
    elif what == "published":
        v, sw = verdict_table(), sweep_table()
        c = capacity_table(sw)
        diffs = published_check(v, c)
        print(f"verdicts: {len(v)} judgeable runs, {int(v.valid.sum())} valid, {int(v.verdict.isna().sum())} raised")
        print(c.to_string(index=False))
        print("differences from published:", diffs or "none")
        return 1 if diffs else 0
    else:
        raise SystemExit(f"unknown table {what!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
