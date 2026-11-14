"""REG-24 (draft, docs/drafts/reg24_confirm_draft1.md): C1's confirmation at λ = 2.0 (PROTOCOL §3, conditions 5 and 6),
REG-19's registered branch for `supports` (docs/decisions.md 2026-11-11 [REG] REG-19, "Decision under each outcome").

One cell, one seed, two runs on one session schedule:
  - the burst run: REG-19's λ = 2.0 burst config with a 4500 s watch, then λ = 1 for a drop sized beforehand, then
    λ = 2.0 for 1500 s (REG-15's design, `gate.reg15_*`, at λ = 2.0 with a longer drop);
  - the no-burst control on the same session schedule (REG-16's control design, `gate.reg16_*`, at λ = 2.0), run first.

Design functions read configs and schedules only (`harness.workload.build_schedule`); they never open a run folder.
The drop is sized by two drain models fixed before any candidate schedule was read:
  - REG-16's request model (`gate.reg16_empty_time`), with REG-15's calibration as REG-16 registered it;
  - a token model (agent/DECISION_TREE.md, K3 row "J1 inside, J2 inside": "The confirmation run's drop is sized from
    U_off and the mean served prompt"): the cold engine prefills uncached tokens at r x U_off (REG-21's [RESULT]).
Outcome functions read a run only after it is valid and copied; never writes into runs/.
"""
import math
from pathlib import Path

import numpy as np
import yaml

from analysis import gate as G
from analysis.load import _level, verdict

CONFIGS = Path(__file__).resolve().parent.parent / "configs"

REG24 = {
    "lam": 2.0, "power_limit_w": 350,
    "watch_s": 4500.0,         # PROTOCOL §3 condition 5 (a 4500 s watch)
    "drop_rate": 1.0,          # PROTOCOL §3 condition 6 (λ drops to 1 req/s)
    "return_s": 1500.0,        # condition 6: back to the original λ for 1500 s
    "return_end_s": 600.0,     # condition 6: the last 600 s must be `recovered` (REG-15's REG15["return_end_s"])
    "baseline": (300.0, 900.0),   # the burst run's baseline window (trigger at 900 s, baseline_s 600), for both runs
                                  # (REG-16's REG16["baseline"])
    "timeline_s": 300.0,       # REG-15's watch windows (`gate.watch_broken`) and REG-16's cold windows
    # the configs this design extends (REG-19's family; both used, never edited)
    "burst_parent": "burst_l1pl350cl_r2.0_s2", "control_parent": "stage2_control_l1pl350cl_r2.0_s2",
    "reg19_seeds": (15, 16, 17, 18, 19),
    "burst_name": "confirm_l1pl350cl_r2.0_s{seed}",
    "control_name": "stage2_control_l1pl350cl_r2.0_long_s{seed}",
    # ---- the seed and drop rule (fixed before any candidate's schedule was read)
    "drop_candidates": (3600.0, 5400.0, 7200.0, 9000.0),   # REG-16's 5400-9000 s and the design note's 3600 s
    "seed_candidates": tuple(range(40, 200)),   # 20-39 left to REG-20b ("seeds 20, 21, ... (the first unused)",
                                                # agent/DECISION_TREE.md); none of 40-199 is used by a config
    "window_tol": 0.05,        # REG-15's (gate.REG15["window_tol"]): every judged window's λp within 5 % of λ
    "surge_tip": 3.2,          # REG-17's (gate.REG17["surge_tip"]): no 120 s planned-rate peak this high anywhere
    "warm_watch_s": 1200.0,    # REG-16's (gate.REG16["warm_watch_s"]): drop time left after the pessimistic empty time
    # REG-16's request model, REG-15's calibration (RUN(20261110-085730_confirm_l1pl350cl_r2.2_s12,
    # gate.reg16_calibration), docs/decisions.md:3156; full values as in tests/test_gate.py:916-918)
    "cal15": {"owed_at_trigger": 28, "c_watch": 1.758119658119658, "c_drop": 1.6716666666666666,
              "c_watch_min": 1.7283333333333333, "c_drop_min": 1.6366666666666667},
    "c_pessimism": 0.05,       # REG-16's (gate.REG16["c_pessimism"])
    # the token model: REG-21's [RESULT] (PROBE(docs/probe/reg21/batch1_20261113T224220Z.txt), k3w.reference / judge)
    "u_off": 5164.761212121212,          # uncached tokens per second, REG-8's five saturated cache-off runs
    "r_expected": 1.0209631954979448,    # the λ = 2.0 group's median r
    "u_tol": 0.05,                       # REG-21's J1 tolerance (k3w.REG21["tol_level"]): pessimistic r = 0.95,
                                         # optimistic r = 1.05 (the K3 band)
    "grid_s": 10.0,            # REG-16's empty-time grid (gate.REG16["grid_s"])
    # ---- outcome settings, none new
    "empty_hold_s": 30.0,      # REG-19's emptying: 0 waiting at a scrape and for the next 30 s (`gate.reg19_emptyings`)
    "n_cap": 256,              # condition 4's cap (gate.REG15["n_cap"]), a readout here
    # filled in once by the seed rule's output (docs/drafts/reg24_confirm_draft1.md, "Seed and drop")
    "seed": None, "drop_s": None,
}


# ---------------------------------------------------------------- configs and phases

def _resolved(name: str) -> dict:
    return G._burst_cfg(name)


def burst_cfg(seed: int, drop_s: float) -> dict:
    """REG-19's λ = 2.0 burst config (through its parent, REG-17's seed-2 burst config) at `seed`, with the 4500 s watch,
    the drop to λ = 1 for `drop_s`, and the return to λ for return_s; resolved."""
    b = _resolved(REG24["burst_parent"])
    we = float(b["trigger"]["at_s"] + b["trigger"]["duration_s"] + REG24["watch_s"])
    wl = {**b["workload"], "duration_s": we + drop_s + REG24["return_s"],
          "steps": [{"at_s": we, "rate": REG24["drop_rate"]}, {"at_s": we + drop_s, "rate": REG24["lam"]}]}
    return {**b, "name": REG24["burst_name"].format(seed=seed), "seed": seed, "workload": wl,
            "verdict": {**b["verdict"], "watch_s": REG24["watch_s"]}}


def control_cfg(seed: int, drop_s: float) -> dict:
    """REG-19's λ = 2.0 control config (through its parent) on the burst run's session schedule: same seed, duration
    and steps, no trigger, judged at control_t_s (the burst's end) with the 4500 s watch; resolved."""
    c, b = _resolved(REG24["control_parent"]), burst_cfg(seed, drop_s)
    return {**c, "name": REG24["control_name"].format(seed=seed), "seed": seed, "workload": b["workload"],
            "verdict": {**c["verdict"], "watch_s": REG24["watch_s"]}}


def phases(cfg: dict) -> dict:
    """The design's phases (absolute s) from a config. Raises unless it is REG-24's design: λ, a 4500 s watch from the
    burst's end (a burst run) or from control_t_s (the control, no trigger), one drop to drop_rate at the watch's end
    lasting one of drop_candidates, the return to λ, and arrivals ending return_s later."""
    wl, v, tr = cfg["workload"], cfg["verdict"], cfg.get("trigger") or {}
    if tr.get("kind") == "burst":
        at, end = float(tr["at_s"]), float(tr["at_s"] + tr["duration_s"])
    elif not tr:
        at = end = float(v["control_t_s"])
    else:
        raise ValueError(f"{cfg.get('name')}: a trigger other than a burst")
    we = end + float(v["watch_s"])
    steps = wl.get("steps") or []
    ok = (float(wl["rate"]) == REG24["lam"] and float(v["watch_s"]) == REG24["watch_s"] and len(steps) == 2
          and float(steps[0]["at_s"]) == we and float(steps[0]["rate"]) == REG24["drop_rate"]
          and float(steps[1]["rate"]) == REG24["lam"]
          and float(steps[1]["at_s"]) - we in REG24["drop_candidates"]
          and float(wl["duration_s"]) == float(steps[1]["at_s"]) + REG24["return_s"])
    if not ok:
        raise ValueError(f"{cfg.get('name')} does not have REG-24's watch, drop and return")
    dur, ds = float(wl["duration_s"]), float(steps[1]["at_s"])
    return {"baseline": REG24["baseline"], "burst_end": end, "watch_end": we, "drop": (we, ds), "drop_s": ds - we,
            "return": (ds, dur), "return_end": (dur - REG24["return_end_s"], dur)}


def judged_windows(cfg: dict) -> dict:
    """The windows the outcome judges (absolute s): the baseline, `load.verdict`'s previous and end windows of the
    4500 s watch (end_s from the config), and the return's last 600 s."""
    ph, v = phases(cfg), cfg["verdict"]
    we = ph["watch_end"]
    return {"baseline": ph["baseline"], "previous": (we - 2 * v["end_s"], we - v["end_s"]),
            "end": (we - v["end_s"], we), "return_end": ph["return_end"]}


# ---------------------------------------------------------------- drain models (schedule only)

def _rate(tp: np.ndarray, a: float, b: float) -> float:
    return float(((tp >= a) & (tp < b)).sum() / (b - a))


def empty_time_requests(sched, cfg: dict, cal: dict, pessimistic: bool = False) -> float:
    """REG-16's request model (`gate.reg16_empty_time`, the same arithmetic on a schedule already built): seconds from
    the drop's start until owed at the trigger + every request (session and burst) planned since - completions at
    REG-15's cold rates per phase reaches 0, on the grid_s grid; NaN if not within the drop. Pessimistic: REG-15's
    lowest 600 s rate per phase, lowered by c_pessimism."""
    dc = REG24["c_pessimism"] if pessimistic else 0.0
    cw, cd = (cal["c_watch_min"], cal["c_drop_min"]) if pessimistic else (cal["c_watch"], cal["c_drop"])
    tp = np.sort(sched.t_planned.to_numpy(float))
    t0 = float(cfg["trigger"]["at_s"])
    we, de = (float(s["at_s"]) for s in cfg["workload"]["steps"])
    grid = np.arange(we, de + 1e-9, REG24["grid_s"])
    planned = np.searchsorted(tp, grid) - np.searchsorted(tp, t0)
    done = (cw - dc) * (we - t0) + (cd - dc) * (grid - we)
    i = np.flatnonzero(cal["owed_at_trigger"] + planned - done <= 0)
    return float(grid[i[0]] - we) if len(i) else math.nan


def owed_requests_model(sched, cfg: dict, cal: dict, t: float, pessimistic: bool = False) -> float:
    """The request model's owed backlog at time t in the watch (t >= the trigger, t <= the watch's end)."""
    dc = REG24["c_pessimism"] if pessimistic else 0.0
    cw = cal["c_watch_min"] if pessimistic else cal["c_watch"]
    tp = np.sort(sched.t_planned.to_numpy(float))
    t0 = float(cfg["trigger"]["at_s"])
    return float(cal["owed_at_trigger"] + np.searchsorted(tp, t) - np.searchsorted(tp, t0) - (cw - dc) * (t - t0))


def u_rate(which: str) -> float:
    """Uncached tokens per second of the cold engine: `expected` (r of the λ = 2.0 group), `pessimistic` (r = 1 - u_tol)
    or `optimistic` (r = 1 + u_tol)."""
    r = {"expected": REG24["r_expected"], "pessimistic": 1 - REG24["u_tol"], "optimistic": 1 + REG24["u_tol"]}[which]
    return r * REG24["u_off"]


def excess_tokens(sched, t0: float, t: np.ndarray | float, u: float) -> np.ndarray | float:
    """Prompt tokens (session and burst requests, all served without a cache hit) planned in [t0, t) minus u x (t - t0):
    the work owed beyond the backlog at t0."""
    s = sched.sort_values("t_planned", kind="stable")
    tp = s.t_planned.to_numpy(float)
    cum = np.concatenate([[0.0], np.cumsum(s.prompt_len.to_numpy(float))])
    tt = np.asarray(t, float)
    out = cum[np.searchsorted(tp, tt)] - cum[np.searchsorted(tp, t0)] - u * (tt - t0)
    return out if out.ndim else float(out)


def empty_time_tokens(sched, cfg: dict, u: float) -> float:
    """The token model: seconds from the drop's start until the work planned since the trigger (every request's full
    prompt, no hit) is done at `u` uncached tokens per second, i.e. the backlog is back to its level at the trigger,
    on the grid_s grid; NaN if not within the drop."""
    t0 = float(cfg["trigger"]["at_s"])
    we, de = (float(s["at_s"]) for s in cfg["workload"]["steps"])
    grid = np.arange(we, de + 1e-9, REG24["grid_s"])
    if u <= 0:
        return math.nan
    i = np.flatnonzero(excess_tokens(sched, t0, grid, u) <= 0)
    return float(grid[i[0]] - we) if len(i) else math.nan


# ---------------------------------------------------------------- the seed and drop rule

def used_seeds() -> set[int]:
    """Every `seed:` set by a config file, REG-24's own two configs left out (so the rule gives the same pick once they
    exist)."""
    import fnmatch
    own = [REG24["burst_name"].format(seed="*") + ".yaml", REG24["control_name"].format(seed="*") + ".yaml"]
    out = set()
    for f in CONFIGS.glob("*.yaml"):
        if any(fnmatch.fnmatch(f.name, p) for p in own):
            continue
        sd = (yaml.safe_load(f.read_text()) or {}).get("seed")
        if sd is not None:
            out.add(int(sd))
    return out


def candidate_seeds() -> tuple[int, ...]:
    used = used_seeds()
    return tuple(s for s in REG24["seed_candidates"] if s not in used)


def design_row(seed: int, drop_s: float) -> dict:
    """Schedule only: the burst config at (seed, drop_s), its judged windows' λp (session requests), the highest 120 s
    planned session rate from start_s to the end of arrivals (`gate.rolling_rate`, REG-18's exposure grid), and the
    predicted empty times (s into the drop) under both models, expected and pessimistic. `ok` when:
    W: every judged window's λp is within window_tol x λ of λ;
    E: the 120 s peak is below surge_tip (the control is not exposed, and no surge sits in either run's return);
    F: the later of the two pessimistic empty times + warm_watch_s fits in the drop."""
    from harness.workload import build_schedule
    cfg = burst_cfg(seed, drop_s)
    s, _ = build_schedule(cfg["workload"], seed, cfg["trigger"])
    tp = s[~s.burst].t_planned.to_numpy(float)
    lam = {k: _rate(tp, *w) for k, w in judged_windows(cfg).items()}
    dur = float(cfg["workload"]["duration_s"])
    grid = np.arange(G.SURGE["start_s"], dur, G.SURGE["grid_s"])
    x = G.rolling_rate(tp, grid, G.SURGE["window_s"])
    cal = REG24["cal15"]
    t_req, t_req_p = empty_time_requests(s, cfg, cal), empty_time_requests(s, cfg, cal, pessimistic=True)
    t_tok, t_tok_p = empty_time_tokens(s, cfg, u_rate("expected")), empty_time_tokens(s, cfg, u_rate("pessimistic"))
    w_ok = all(abs(v - REG24["lam"]) <= REG24["window_tol"] * REG24["lam"] + 1e-12 for v in lam.values())
    e_ok = bool(x.max() < REG24["surge_tip"])
    worst = max(t_req_p, t_tok_p) if np.isfinite(t_req_p) and np.isfinite(t_tok_p) else math.nan
    f_ok = bool(np.isfinite(worst) and worst + REG24["warm_watch_s"] <= drop_s)
    return {"seed": seed, "drop_s": drop_s, "lam_p": lam, "peak_120s": float(x.max()),
            "t_peak": float(grid[x.argmax()]), "empty_req": t_req, "empty_req_pess": t_req_p, "empty_tok": t_tok,
            "empty_tok_pess": t_tok_p, "windows_ok": w_ok, "not_exposed": e_ok, "drop_ok": f_ok,
            "ok": bool(w_ok and e_ok and f_ok)}


def seed_rule(rows_fn=None) -> dict:
    """REG-24's seed and drop, a rule fixed before any candidate's schedule was read: the lowest candidate seed (not
    used by any config, REG-24's own left out) that passes W, E and F (`design_row`) at some drop candidate; with it,
    the shortest such drop. Seeds first, then drops (answers REG-16's review N5: drop-first picks the lightest
    schedule that fits the shortest drop). Rows for every (seed, drop) tried, in order, up to the pick."""
    rows_fn = rows_fn or design_row
    rows = []
    for sd in candidate_seeds():
        for d in REG24["drop_candidates"]:
            r = rows_fn(sd, d)
            rows.append(r)
            if r["ok"]:
                return {"picked": {"seed": sd, "drop_s": d}, "rows": rows}
    return {"picked": None, "rows": rows}


def seed_scan(seeds=None) -> dict:
    """Readout only, after the pick (how strongly the rule selects): over every candidate seed and drop, how many
    pass W, E, F and all three, and the median pessimistic empty times."""
    rows = [design_row(sd, d) for sd in (seeds or candidate_seeds()) for d in REG24["drop_candidates"]]
    out = {}
    for d in REG24["drop_candidates"]:
        rr = [r for r in rows if r["drop_s"] == d]
        fin = lambda k: [r[k] for r in rr if np.isfinite(r[k])]
        out[d] = {"n": len(rr), "windows_ok": sum(r["windows_ok"] for r in rr),
                  "not_exposed": sum(r["not_exposed"] for r in rr), "drop_ok": sum(r["drop_ok"] for r in rr),
                  "all": sum(r["ok"] for r in rr), "seeds_all": [r["seed"] for r in rr if r["ok"]],
                  "median_empty_req_pess": float(np.median(fin("empty_req_pess"))) if fin("empty_req_pess") else math.nan,
                  "median_empty_tok_pess": float(np.median(fin("empty_tok_pess"))) if fin("empty_tok_pess") else math.nan}
    return out


def model_check_reg19() -> list[dict]:
    """Schedule only: the request model's owed backlog (expected and pessimistic) at the start and end of REG-19's
    window W (1680 and 4080 s) on REG-19's five burst configs, to set beside the measured total line that REG-19's
    [RESULT] reports (decisions.md, its per-seed table). No run is read here."""
    from harness.workload import build_schedule
    out = []
    for sd in REG24["reg19_seeds"]:
        cfg = _resolved(f"burst_l1pl350cl_r2.0_w3000_s{sd}")
        s, _ = build_schedule(cfg["workload"], sd, cfg["trigger"])
        row = {"seed": sd}
        for t in (1680.0, 4080.0):
            row[t] = {"expected": owed_requests_model(s, cfg, REG24["cal15"], t),
                      "pessimistic": owed_requests_model(s, cfg, REG24["cal15"], t, pessimistic=True)}
        out.append(row)
    return out


def inputs(seed: int | None = None, drop_s: float | None = None) -> dict:
    """Design inputs for the chosen seed and drop, from the configs alone (no run): request counts; λp per phase, per
    600 s window of the drop and per third of the watch; the judged windows' λp; the 120 s peaks per phase; both
    models' predicted owed backlog at the watch's end and empty times; the K3 band; whether the control's schedule
    equals the burst run's session rows."""
    from harness.workload import build_schedule
    seed = REG24["seed"] if seed is None else seed
    drop_s = REG24["drop_s"] if drop_s is None else drop_s
    b, c = burst_cfg(seed, drop_s), control_cfg(seed, drop_s)
    sb, _ = build_schedule(b["workload"], seed, b["trigger"])
    sc, _ = build_schedule(c["workload"], seed, c.get("trigger"))
    cols = ["t_planned", "session_id", "turn", "prompt_len"]
    same = bool(sc[cols].equals(sb[~sb.burst][cols].reset_index(drop=True)))
    ph = phases(b)
    tp = sb[~sb.burst].t_planned.to_numpy(float)
    grid = np.arange(G.SURGE["start_s"], float(b["workload"]["duration_s"]), G.SURGE["grid_s"])
    x = G.rolling_rate(tp, grid, G.SURGE["window_s"])
    peak = lambda a, z: float(x[(grid >= a) & (grid < z)].max())
    end, we = ph["burst_end"], ph["watch_end"]
    w3 = (we - end) / 3
    t0 = float(b["trigger"]["at_s"])
    cal = REG24["cal15"]
    tok_we = {k: excess_tokens(sb, t0, we, u_rate(k)) for k in ("optimistic", "expected", "pessimistic")}
    return {"seed": seed, "drop_s": drop_s, "phases": ph, "n_session": int((~sb.burst).sum()),
            "n_burst": int(sb.burst.sum()), "control_schedule_same": same, "seeds": (b["seed"], c["seed"]),
            "lam_p": {"baseline": _rate(tp, *ph["baseline"]), "watch": _rate(tp, end, we),
                      "watch_thirds": [_rate(tp, end + i * w3, end + (i + 1) * w3) for i in range(3)],
                      "drop": _rate(tp, *ph["drop"]), "return": _rate(tp, *ph["return"])},
            "drop_by_600": [(a, _rate(tp, a, min(a + 600.0, ph["drop"][1])))
                            for a in np.arange(ph["drop"][0], ph["drop"][1] - 1e-9, 600.0)],
            "judged_lam_p": {k: _rate(tp, *w) for k, w in judged_windows(b).items()},
            "peak_120s": {"before_burst": peak(G.SURGE["start_s"], t0), "watch": peak(end, we),
                          "drop": peak(*ph["drop"]), "return": peak(*ph["return"])},
            "owed_at_watch_end": {"expected": owed_requests_model(sb, b, cal, we),
                                  "pessimistic": owed_requests_model(sb, b, cal, we, pessimistic=True)},
            "excess_tokens_at_watch_end": tok_we,
            "empty_s": {"requests": empty_time_requests(sb, b, cal),
                        "requests_pessimistic": empty_time_requests(sb, b, cal, pessimistic=True),
                        "tokens": empty_time_tokens(sb, b, u_rate("expected")),
                        "tokens_pessimistic": empty_time_tokens(sb, b, u_rate("pessimistic")),
                        "tokens_optimistic": empty_time_tokens(sb, b, u_rate("optimistic"))},
            "u": {k: u_rate(k) for k in ("optimistic", "expected", "pessimistic")}}


# ---------------------------------------------------------------- outcome (after the runs, never before)

def emptyings(run: dict, a: float, b: float) -> list[float]:
    """REG-19's emptying (`gate.reg19_emptyings`) over [a, b): a scrape with 0 waiting followed by 0 waiting for
    empty_hold_s, those seconds ending by b; a new emptying counts only after the line refilled. Absolute times."""
    m, hold = run["metrics"], REG24["empty_hold_s"]
    w = m[(m.t >= a) & (m.t < b)]
    t, q = w.t.to_numpy(float), w["vllm:num_requests_waiting"].to_numpy(float)
    out, refilled = [], True
    for i in range(len(t)):
        if q[i] != 0:
            refilled = True
        elif refilled and t[i] + hold <= b and (q[(t >= t[i]) & (t < t[i] + hold)] == 0).all():
            out.append(float(t[i]))
            refilled = False
    return out


BURST_LABELS = ("bad_baseline", "not_persistent", "inconclusive", "reformed", "emptied_in_watch",
                "drop_inconclusive", "no_return", "confirms")


def burst_outcome(v5: str, broken: bool, emptied_watch: bool, emptied_drop: bool, back: bool | None) -> str:
    """The burst run's outcome, REG-15's order (`gate.reg15_outcome`) with REG-19's emptying in place of REG-15's
    single zero scrape, in the watch and in the drop:
    - bad_baseline: v5 (`load.verdict` of the 4500 s watch) `bad_baseline`;
    - not_persistent: v5 `recovered` or `slow_drain` (condition 5 fails);
    - inconclusive: v5 `unclear`;
    - reformed: stuck at the watch's end, but some 300 s window of the watch was `recovered` (`gate.watch_broken`);
    - emptied_in_watch: stuck, never `recovered`, but the waiting line emptied in the watch (REG-19's test: stuck
      through the watch means the line never empties);
    - drop_inconclusive: the line never emptied in the drop (condition 6 inconclusive, PROTOCOL §3);
    - inconclusive: the return's end has a missing value;
    - no_return: emptied in the drop, but the return's end is not `recovered` against the baseline;
    - confirms: stuck through the watch without emptying, emptied in the drop, the return's end `recovered`."""
    if v5 == "bad_baseline":
        return "bad_baseline"
    if v5 in ("recovered", "slow_drain"):
        return "not_persistent"
    if v5 != "stuck":
        return "inconclusive"
    if broken:
        return "reformed"
    if emptied_watch:
        return "emptied_in_watch"
    if not emptied_drop:
        return "drop_inconclusive"
    if back is None:
        return "inconclusive"
    return "confirms" if back else "no_return"


def pair_outcome(control_label: str | None, burst_label: str | None) -> str:
    """The cell's outcome. The control runs first; the burst run only after `control_warm` (`step`). A burst run that
    fails condition 5 or has an instrument gap keeps its own label whatever the control; otherwise the burst run's
    label stands only beside a `control_warm` control:
    - control_not_warm: the control is not `control_warm` (no burst run, or one run against the stopping rule);
    - control_missing: no control label;
    - else the burst run's label (`burst_missing` if the burst run was not run)."""
    if burst_label in ("bad_baseline", "not_persistent", "reformed", "emptied_in_watch", "inconclusive"):
        return burst_label
    if control_label is None:
        return "control_missing"
    if control_label != "control_warm":
        return "control_not_warm"
    return burst_label or "burst_missing"


def k3_band(measured_s: float, t_opt: float, t_pess: float) -> str:
    """The registered blind prediction (agent/DECISION_TREE.md, K3): the waiting line's first emptying in the drop (s
    after its start) against the token model's band [empty time at r = 1 + u_tol, at r = 1 - u_tol]. `undefined` if
    either end or the measurement is NaN."""
    if not all(np.isfinite(x) for x in (measured_s, t_opt, t_pess)):
        return "undefined"
    if measured_s < t_opt:
        return "outside_early"
    return "inside" if measured_s <= t_pess else "outside_late"


def _flat(d: dict, p: str = "") -> dict:
    return {k2: v2 for k, v in d.items() for k2, v2 in (_flat(v, p + k + ".") if isinstance(v, dict)
                                                        else {p + k: v}).items()}


def check(run: dict, kind: str) -> None:
    """Refuses a run that is not valid, or whose config differs from the registered file (`burst` or `control`) on any
    key that file sets (as `gate.reg16_check`): pins seed, λ, closed loop, force_close, 350 W, the steps, the watch, and
    the trigger (the burst run's burst; none for the control)."""
    if not (run["checks"] and run["checks"]["valid"]):
        raise ValueError(f"{run['dir'].name} is not valid")
    name = REG24[f"{kind}_name"].format(seed=REG24["seed"])
    reg, got = _flat(_resolved(name)), _flat(run["cfg"])
    diff = sorted(k for k in reg if got.get(k) != reg[k])
    want_trigger = "burst" if kind == "burst" else None
    if diff or (run["cfg"].get("trigger") or {}).get("kind") != want_trigger:
        raise ValueError(f"{run['dir'].name} is not REG-24's registered {kind} run (differs on {diff[:5]})")
    phases(run["cfg"])


def _one(kind: str) -> dict:
    from analysis.load import find_runs
    pat = "*_" + REG24[f"{kind}_name"].format(seed=REG24["seed"])
    run = G.reg12_only(find_runs(pat), pat)   # exactly one valid run: reruns only after an invalid run
    check(run, kind)
    return run


def control_table(run: dict | None = None) -> dict:
    """The control: REG-16's outcome (`gate.reg16_control_outcome`) on REG-24's phases, against the burst run's
    baseline window (300-900 s): cold windows from control_t_s to the end, persistence at each phase's end or over
    1500 s, the watch verdict at control_t_s + 4500 s, the return's end. Readouts: the timeline, the window mix."""
    run = run or _one("control")
    ph, v = phases(run["cfg"]), verdict(run)
    base = _level(run, *REG24["baseline"])
    base_ok = None if np.isnan(base["pf"]) else bool(base["pf"] >= run["cfg"]["verdict"]["min_baseline_pf"])
    cw = G.cold_windows(run, base, ph["burst_end"], ph["return"][1])
    persistent = G.cold_persistent(cw, [ph["watch_end"], ph["drop"][1], ph["return"][1]])
    back = G.recovered_against(run, base, *ph["return_end"])
    return {"run": run["dir"].name, "v_watch": v["verdict"], "verdict_baseline": v["baseline"], "baseline": base,
            "phases": ph, "cold_windows": cw, "longest_cold_s": G.longest_cold_s(cw), "return_recovered": back,
            "return_end_level": _level(run, *ph["return_end"]),
            "outcome": G.reg16_control_outcome(base_ok, v["verdict"], cw, persistent, back),
            "window_mix": [G.window_mix(run, lo, hi) for lo, hi in cw["windows"]],
            "surge": G.surge_run(run), "timeline": G.reg15_timeline(run)}


def step() -> dict:
    """The queue's only look between the two runs: once the control is valid and copied, `continue` is True only if
    its outcome is `control_warm`. Prints no label, level or count."""
    return {"control_done": True, "continue": control_table()["outcome"] == "control_warm"}


def burst_table(run: dict | None = None, control: dict | None = None) -> dict:
    """The burst run's outcome (`burst_outcome`) and readouts (never decisive): the watch's 300 s windows with their
    λp (`gate.watch_broken`), every emptying in the watch and the drop, the owed backlog at the watch's end, at the
    first emptying in the drop and 600 s later, the hit in [first emptying + 600, + 1200) against the control's hit in
    the same window (REG-16's planned reading; `warmed` is consistent with both hypotheses), the drop's last 600 s,
    REG-15's loop levels over the watch's last 1500 s, release delay at each phase's end, the cold side over
    [burst end + 600, watch end), the judged windows' λp from the run's own requests, the K3 band, the timeline."""
    run = run or _one("burst")
    ph, v = phases(run["cfg"]), verdict(run)
    base = v["baseline"]
    brk = G.watch_broken(run, base, ph["burst_end"], ph["watch_end"])
    e_watch, e_drop = emptyings(run, ph["burst_end"], ph["watch_end"]), emptyings(run, *ph["drop"])
    back = G.recovered_against(run, base, *ph["return_end"])
    label = burst_outcome(v["verdict"], brk["broken"], bool(e_watch), bool(e_drop), back)
    out = {"run": run["dir"].name, "v5": v["verdict"], "baseline": base, "watch_end_level": v["end"],
           "watch_broken": brk, "emptyings_watch": e_watch, "emptyings_drop": e_drop, "return_recovered": back,
           "return_end_level": _level(run, *ph["return_end"]), "outcome": label, "phases": ph}
    vc, we, de = run["cfg"]["verdict"], ph["watch_end"], ph["drop"][1]
    out["owed"] = {"trigger": G.owed_backlog(run, float(run["cfg"]["trigger"]["at_s"])),
                   "watch_end": G.owed_backlog(run, we)}
    t_e = e_drop[0] if e_drop else math.nan
    out["first_empty_drop_s"] = t_e - we if np.isfinite(t_e) else math.nan
    if np.isfinite(t_e):
        out["owed"].update(first_empty=G.owed_backlog(run, t_e), first_empty_600=G.owed_backlog(run, t_e + 600))
        a, b = t_e + 600.0, t_e + 1200.0
        if b <= de:
            h = _level(run, a, b)["hit"]
            hc = _level(control, a, b)["hit"] if control is not None else math.nan
            out["after_empty"] = {"window": (a, b), "hit": h, "control_hit": hc,
                                  "reading": None if not (np.isfinite(h) and np.isfinite(hc)) else
                                  ("warmed" if h >= hc - vc["recovered_hit_drop"] else "cold_after_empty")}
    out["drop_level"] = _level(run, de - REG24["return_end_s"], de)
    loop = _level(run, we - 1500.0, we)
    m = run["metrics"]
    n_max = float(m["vllm:num_requests_running"][(m.t >= we - 1500.0) & (m.t < we)].max())
    out["loop"] = {"kv": loop["kv"], "n": loop["n"], "n_over_base": loop["n"] / base["n"], "n_max": n_max,
                   "n_cap": REG24["n_cap"]}
    out["release_delay"] = G.release_delay(run, [(we - 300, we), (de - 300, de), ph["return_end"]], end=0.0)
    a = ph["burst_end"] + 600.0
    c, lp = G.completion_rate(run, a, we), G.planned_session_rate(run, a, we)
    out["cold_side"] = {"c": c, "lam_p": lp, "below": bool(c < min(REG24["lam"], lp))}
    out["judged_lam_p"] = {k: G.planned_session_rate(run, *w) for k, w in judged_windows(run["cfg"]).items()}
    pred = inputs(REG24["seed"], REG24["drop_s"])["empty_s"]
    out["k3"] = {"predicted_s": pred["tokens"], "band_s": (pred["tokens_optimistic"], pred["tokens_pessimistic"]),
                 "measured_s": out["first_empty_drop_s"],
                 "label": k3_band(out["first_empty_drop_s"], pred["tokens_optimistic"], pred["tokens_pessimistic"])}
    out["timeline"] = G.reg15_timeline(run)
    return out


def table() -> dict:
    """REG-24's result, computed once after both runs are valid and copied (or after the control alone, when `step`
    stopped the queue): the control's table, the burst run's table, the pair's outcome, and the baseline pair
    (`gate.reg19_baseline_pair`, the run-order readout)."""
    from analysis.load import find_runs
    ctl_run = _one("control")
    ctl = control_table(ctl_run)
    pat = "*_" + REG24["burst_name"].format(seed=REG24["seed"])
    if not find_runs(pat):
        return {"control": ctl, "burst": None, "outcome": pair_outcome(ctl["outcome"], None)}
    b_run = _one("burst")
    bt = burst_table(b_run, ctl_run)
    return {"control": ctl, "burst": bt, "outcome": pair_outcome(ctl["outcome"], bt["outcome"]),
            "baseline_pair": G.reg19_baseline_pair(ctl_run, b_run)}


if __name__ == "__main__":
    import sys
    fns = {"reg24_seed_rule": seed_rule, "reg24_inputs": inputs, "reg24_scan": seed_scan,
           "reg24_model_check": model_check_reg19, "reg24_step": step, "reg24": table}
    print(fns[sys.argv[1]]())
