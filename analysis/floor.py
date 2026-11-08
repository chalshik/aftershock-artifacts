"""Sustained cache-off capacity at λ = 3 (open item A1, registration REG-6). Never writes into runs/.

The capacity is measured directly: completions per second during *backlogged stretches*, the runs of consecutive
scrapes with waiting >= min_waiting. While requests wait, the server is saturated, so its completion rate there is its
capacity, not the demand. A schedule burst then helps the measurement instead of confounding it (REG-6 review).
Every threshold is an argument; the registered values are in REG6.
"""
import numpy as np
import pandas as pd


def backlogged_stretches(m: pd.DataFrame, a: float, b: float, min_waiting: float, min_stretch_s: float) -> list[tuple[float, float]]:
    """Maximal runs of consecutive scrapes in [a, b) with waiting >= min_waiting, as (first, last) scrape times, kept if
    they last at least min_stretch_s."""
    w = m[(m.t >= a) & (m.t < b)]
    t, high = w.t.to_numpy(), (w["vllm:num_requests_waiting"] >= min_waiting).to_numpy()
    out, start = [], None
    for i in range(len(t)):
        if high[i] and start is None:
            start = t[i]
        if start is not None and (not high[i] or i == len(t) - 1):
            end = t[i] if high[i] else t[i - 1]
            if end - start >= min_stretch_s:
                out.append((float(start), float(end)))
            start = None
    return out


def sustained_capacity(run: dict, a: float, b: float, min_waiting: float, min_stretch_s: float, min_backlog_s: float,
                       margin: float, max_gap_s: float) -> dict:
    """REG-6 label over [a, b), against the realized planned rate λp of the run's own schedule in [a, b):
    - unclear_data: a waiting value is NaN, or a gap between scrapes exceeds max_gap_s (the registered scrape-gap limit);
    - sustainable_no_backlog: backlogged stretches total < min_backlog_s, so the queue never stayed up: the server kept
      up with its own schedule;
    - sustainable: backlogged capacity c_b >= (1 + margin) x λp;
    - not_sustainable: c_b < λp;
    - unclear: in between.
    c_b = ok completions with t_end inside backlogged stretches / their total length."""
    m, r = run["metrics"], run["requests"]
    w = m[(m.t >= a) & (m.t < b)]
    planned = float(((r.t_planned >= a) & (r.t_planned < b)).sum() / (b - a))
    res = {"planned_rate": planned, "backlog_s": 0.0, "c_b": np.nan, "n_stretches": 0}
    if w["vllm:num_requests_waiting"].isna().any() or len(w) < 2 or np.diff(w.t.to_numpy()).max() > max_gap_s:
        return {"label": "unclear_data", **res}
    st = backlogged_stretches(m, a, b, min_waiting, min_stretch_s)
    total = sum(e - s for s, e in st)
    res.update(backlog_s=total, n_stretches=len(st))
    if total < min_backlog_s:
        return {"label": "sustainable_no_backlog", **res}
    done = (r.status == "ok") & np.logical_or.reduce([(r.t_end >= s) & (r.t_end < e) for s, e in st])
    c_b = float(done.sum() / total)
    res.update(c_b=c_b, n_done=int(done.sum()))  # n_done: the completions behind c_b (REG-9 review)
    label = "sustainable" if c_b >= (1 + margin) * planned else ("not_sustainable" if c_b < planned else "unclear")
    return {"label": label, **res}


REG6 = {"runs_pattern": "*_long_pc_off_r3_s*", "window": (600, 3600), "min_waiting": 1.0, "min_stretch_s": 30,
        "min_backlog_s": 300, "margin": 0.05}
# REG-9 (decisions.md 2026-11-07): REG-6 repeated at a 350 W power limit. Only the runs differ; the pattern matches no
# 420 W run, and every run it reads must carry a passed 350 W power_limit check.
REG9 = {**REG6, "runs_pattern": "*_long_pl350_pc_off_r3_s[01]", "power_limit_w": 350}
# REG-9 amended (decisions.md 2026-11-09): the runs with a new connection per request. No run of the first configs was
# valid, so the amendment changes which runs are read and nothing else.
REG9 = {**REG9, "runs_pattern": "*_long_pl350fc_pc_off_r3_s[01]", "force_close": True}
# The 6 default-pool λ = 3 shock runs REG-6's first edge is about (420 W; docs/model.md ledger row 1). REG-9 carries its
# 350 W result only to those that were heat-clean inside their own verdict window (shock_heat_table).
SHOCK_RUNS_R3 = ["20261102-072216_wipe_preempt_r3_s1", "20261102-053935_wipe_preempt_r3_s2",
                 "20261102-100744_wipe_preempt_r3_s3", "20261102-131353_burst_r3_s1", "20261102-135701_burst_r3_s2",
                 "20261102-144008_burst_r3_s3"]


def reg_table(reg: dict) -> pd.DataFrame:
    from analysis.load import find_runs
    rows = []
    for r in find_runs(reg["runs_pattern"]):  # valid runs only
        if "power_limit_w" in reg:
            pl = {c["name"]: c for c in r["checks"]["checks"]}.get("power_limit", {})
            if pl.get("passed") is not True or r["cfg"]["checks"].get("expected_power_limit_w") != reg["power_limit_w"]:
                raise ValueError(f"{r['dir'].name}: not a passed {reg['power_limit_w']} W run")
        if reg.get("force_close") and r["cfg"].get("loadgen_force_close") is not True:  # amendment review, trace B
            raise ValueError(f"{r['dir'].name}: not a run with a new connection per request")
        res = sustained_capacity(r, *reg["window"], reg["min_waiting"], reg["min_stretch_s"], reg["min_backlog_s"],
                                 reg["margin"], r["cfg"]["checks"]["max_scrape_gap_s"])
        rows.append({"run": r["dir"].name, "seed": r["cfg"]["seed"], **res})
    t = pd.DataFrame(rows)
    if len(t) and t.seed.duplicated().any():  # REG-9 review: the registration counts one valid run per seed
        raise ValueError(f"more than one valid run for a seed: {t.run.tolist()}")
    return t


def reg6_table() -> pd.DataFrame:
    return reg_table(REG6)


def reg9_table() -> pd.DataFrame:
    return reg_table(REG9)


SUSTAINABLE = ("sustainable", "sustainable_no_backlog")


def reg9_seed1_may_start() -> bool:
    """REG-9 start rule: seed 1 runs only if seed 0 has a valid run labeled sustainable or sustainable_no_backlog.
    Otherwise both seeds can no longer be sustainable, the only outcome that changes a statement, so seed 1 cannot
    change any decision."""
    t = reg9_table()
    return bool(len(t)) and bool(t[t.seed == 0].label.isin(SUSTAINABLE).any())


def reg9_outcome(t: pd.DataFrame) -> str:
    """REG-9's decision, in order of precedence:
    - first_edge: seeds 0 and 1 both have a valid run labeled sustainable or sustainable_no_backlog;
    - not_decided_at_420W: otherwise, if any seed is not_sustainable (true at 350 W only; it does not carry to 420 W);
    - no_change: everything else (unclear, unclear_data, a missing seed)."""
    lab = dict(zip(t.seed, t.label)) if len(t) else {}
    if all(lab.get(s) in SUSTAINABLE for s in (0, 1)):
        return "first_edge"
    return "not_decided_at_420W" if "not_sustainable" in lab.values() else "no_change"


def window_heat(run: dict) -> dict:
    """SW-thermal share and HW-slowdown samples of `gpu.jsonl` inside a shock run's verdict window, from the baseline's
    start to the end of the watch (load.verdict's times), with gpu_steady's bit masks (harness/checks.py)."""
    from analysis.load import verdict
    from harness.checks import HW_THROTTLE_MASK, SW_THERMAL_BIT
    v, c, g = verdict(run), run["cfg"]["verdict"], run["gpu"]
    a, b = v["t_start"] - c["baseline_s"], v["t_wipe"] + c["watch_s"]
    w = g[(g.t >= a) & (g.t <= b)] if len(g) else g
    reasons = w.throttle_reasons.astype(int) if len(w) else pd.Series(dtype=int)
    return {"a": a, "b": b, "samples": len(w),
            "sw_thermal_frac": float(((reasons & SW_THERMAL_BIT) != 0).mean()) if len(w) else np.nan,
            "hw_samples": int(((reasons & HW_THROTTLE_MASK) != 0).sum()),
            "power_limit_w": sorted(w.power_limit_w.unique().tolist()) if "power_limit_w" in w else []}


def shock_heat_table(runs: list[str] = SHOCK_RUNS_R3) -> pd.DataFrame:
    """REG-9 coverage check, on existing 420 W runs only. A shock run is covered by the carry if, inside its verdict
    window, SW-thermal share <= its own checks.max_sw_thermal_frac and no HW-slowdown sample (gpu_steady's thresholds,
    applied to the window the verdict reads instead of the whole run)."""
    from analysis.load import RUNS, load_run
    rows = []
    for name in runs:
        r = load_run(RUNS / name)
        h = window_heat(r)
        ok = bool(h["samples"]) and h["sw_thermal_frac"] <= r["cfg"]["checks"]["max_sw_thermal_frac"] and h["hw_samples"] == 0
        rows.append({"run": name, "seed": r["cfg"]["seed"], "valid": bool(r["checks"] and r["checks"]["valid"]),
                     **h, "covered": ok and bool(r["checks"] and r["checks"]["valid"])})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    import sys
    pd.set_option("display.width", 250, "display.max_columns", 30)
    which = sys.argv[1] if len(sys.argv) > 1 else "reg6"
    if which == "reg9_shock_heat":
        print(shock_heat_table().round(4).to_string(index=False))
    else:
        t = {"reg6": reg6_table, "reg9": reg9_table}[which]()
        print(t.round(4).to_string(index=False))
        if which == "reg9":
            print("outcome:", reg9_outcome(t))
