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
    res["c_b"] = c_b
    label = "sustainable" if c_b >= (1 + margin) * planned else ("not_sustainable" if c_b < planned else "unclear")
    return {"label": label, **res}


REG6 = {"runs_pattern": "*_long_pc_off_r3_s*", "window": (600, 3600), "min_waiting": 1.0, "min_stretch_s": 30,
        "min_backlog_s": 300, "margin": 0.05}


def reg6_table() -> pd.DataFrame:
    from analysis.load import find_runs
    rows = []
    for r in find_runs(REG6["runs_pattern"]):  # valid runs only
        res = sustained_capacity(r, *REG6["window"], REG6["min_waiting"], REG6["min_stretch_s"], REG6["min_backlog_s"],
                                 REG6["margin"], r["cfg"]["checks"]["max_scrape_gap_s"])
        rows.append({"run": r["dir"].name, "seed": r["cfg"]["seed"], **res})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    pd.set_option("display.width", 250, "display.max_columns", 30)
    print(reg6_table().round(4).to_string(index=False))
