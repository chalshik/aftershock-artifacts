"""K2, stage E0 (draft, not registered): the predicted widening of the window from 8 to 16 turns per session, and the
gate that decides whether E2's 16-turn shock matrix runs (docs/experiment-plan.md "Stage 2, revised", step E;
decisions.md 2026-11-12 [DECISION] "K2 staged"). Nothing here reads a run folder: the inputs are the session shape in
the configs and two reported numbers of REG-8 (`E0["floor_8"]`, `E0["warm_best_8"]`, docs/model.md M2).

Window ratio of a setup: its closed-loop warm capacity (configs' capacity rule, `tables.sweep_capacity`) over its
closed-loop cold floor (`gate.cold_floor` on its closed-loop cache-off sweep). The gate is on the ratio of ratios
R = ratio_16 / ratio_8, so the 8-turn absolutes cancel and the prediction needs no E1 result.

The prediction is a per-request cost model, cost = a + b x (tokens to prefill), at the stationary turn mix:
  - cold (every turn misses): the mean prompt, system + user + (user + reply)(T - 1)/2 tokens;
  - warm (every later turn hits its previous prompt): the mean uncached prompt, (system + user + (T - 1)(user + reply))/T.
Two models, as in REG-21 (`k3.REG21["costs"]`): proportional (a = 0) and a fixed part per request. The fixed model's
(a, b) solve two equations, cost(cold mix at 8 turns) = 1 / 1.681 and cost(warm mix at 8 turns) = 1 / 4.047, so it is
REG-8's two capacities rewritten (0.180 s + 0.135 ms per token). Known blind spot, stated in the draft: neither model
has a KV pool, and at 16 turns each session's live context is about a third larger at the same session count, so the
closed-loop warm capacity may lose more than either says (BELIEF).
"""
from __future__ import annotations

import math

E0 = {
    "floor_8": 1.681,        # req/s, REG-8's open-loop cache-off floor (docs/model.md M2; RUN(REG-8, gate.reg8_zone))
    "warm_best_8": 4.047,    # req/s, REG-8's best cache-on completion rate (M2; RUN(..._pc_on_r4.5, load.summarize))
    "warm_cl_8": 2.4,        # req/s, REG-13's closed-loop warm capacity by the configs' rule (M2; decisions [RESULT])
    "warm_grid_8": (2.0, 2.4, 2.6, 2.8, 3.0),            # REG-13's rates (configs/sweep_l1pl350cl_pc_on.yaml)
    "warm_grid_16": (2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2),  # E2 (configs/sweep_l1t16pl350cl_pc_on.yaml); 2.2 added
                                                          # after the E0/E1 review (owner, 2026-11-12)
}


def shape(cfg_sessions: dict) -> dict:
    return {k: int(cfg_sessions[k]) for k in ("system_tokens", "user_tokens", "reply_tokens", "turns")}


def cold_tokens(s: dict, turns: int | None = None) -> float:
    T = turns or s["turns"]
    return s["system_tokens"] + s["user_tokens"] + (s["user_tokens"] + s["reply_tokens"]) * (T - 1) / 2


def warm_tokens(s: dict, turns: int | None = None) -> float:
    T = turns or s["turns"]
    return (s["system_tokens"] + s["user_tokens"] + (T - 1) * (s["user_tokens"] + s["reply_tokens"])) / T


def token_gap(s: dict, turns: int | None = None) -> float:
    """Cold over warm prefill tokens per request at the stationary mix (decisions.md 2026-11-12, design choices,
    item 4: 3.48, 6.19, 10.9 at 4, 8 and 16 turns of L1)."""
    return cold_tokens(s, turns) / warm_tokens(s, turns)


def calibrate_fixed(s: dict, floor: float | None = None, warm_best: float | None = None) -> tuple[float, float]:
    """(a, b) with a + b x cold_tokens(8) = 1 / floor and a + b x warm_tokens(8) = 1 / warm_best."""
    floor, warm_best = floor or E0["floor_8"], warm_best or E0["warm_best_8"]
    c, w = cold_tokens(s, 8), warm_tokens(s, 8)
    b = (1 / floor - 1 / warm_best) / (c - w)
    return 1 / floor - b * c, b


def predict(s: dict, turns: int = 16) -> dict:
    """For each cost model: warm_T / warm_8, floor_T / floor_8, and R = (warm ratio) / (floor ratio)."""
    out = {}
    for name, (a, b) in {"prop": (0.0, 1.0), "fixed": calibrate_fixed(s)}.items():
        cost = lambda L: a + b * L
        warm = cost(warm_tokens(s, 8)) / cost(warm_tokens(s, turns))
        floor = cost(cold_tokens(s, 8)) / cost(cold_tokens(s, turns))
        out[name] = {"a": a, "b": b, "warm_ratio": warm, "floor_ratio": floor, "R": warm / floor,
                     "warm_cl_T": E0["warm_cl_8"] * warm, "floor_T_open": E0["floor_8"] * floor}
    return out


def gate_factor(c8: float | None = None, grid8: tuple | None = None) -> float:
    """g: the measured R must reach it before the 16-turn matrix runs. A capacity read by the configs' rule is the
    highest passing grid rate, so the true 8-turn capacity may lie up to one grid step above the measured one; a
    measured R >= 1 + step / c8 then still implies a true R >= 1. The 16-turn capacity is rounded down the same way,
    which can only lower the measured R (conservative). Floors are means of saturated runs, not rounded. Not covered:
    a lucky pass at one grid rate (REG-13's 2.4 passed at 0.9503 against 0.95) and noise in the floors."""
    c8, grid8 = c8 or E0["warm_cl_8"], grid8 or E0["warm_grid_8"]
    above = [r for r in grid8 if r > c8 + 1e-9]
    if not above:
        return math.inf   # capacity at the grid's top: its true value is unbounded above
    return 1 + (min(above) - c8) / c8


def decide(warm8: float, f8: float, warm16: float, f16: float, low16_measured: bool = True,
           grid8: tuple | None = None, grid16: tuple | None = None) -> dict:
    """The E0 gate. Labels:
      'widens'          R >= g and warm16 > warm8: the 16-turn shock matrix may be registered;
      'floor_only'      R >= g but warm16 <= warm8: the window widened only because the floor fell; no matrix
                        (E0/E1 review, recommendation 2: the warm side must gain too);
      'does_not_widen'  R <= 1: K2's first half refuted for L1 at sweep cost; no matrix;
      'unresolved'      1 < R < g; no matrix, the owner decides;
      'missing'         an input is undefined for want of data (no valid run where one is needed, or a floor the
                        rules leave undefined); no matrix, reported, the owner decides.
    A 16-turn capacity below its grid (the lowest rate measured and failed, `low16_measured`) bounds R above by its
    value at that rate (`R_upper`): 'does_not_widen' if that bound is <= 1, else 'unresolved'."""
    grid16 = grid16 or E0["warm_grid_16"]
    g = gate_factor(warm8, grid8)
    out = {"g": g, "warm_ratio": warm16 / warm8 if warm8 else math.nan,
           "floor_ratio": f16 / f8 if f8 else math.nan}
    if any(math.isnan(x) for x in (warm8, f8, f16)):
        return {**out, "R": math.nan, "label": "missing"}
    if math.isnan(warm16):
        if not low16_measured:
            return {**out, "R": math.nan, "label": "missing"}
        R_up = measured_R(warm8, f8, min(grid16), f16)
        return {**out, "R": math.nan, "R_upper": R_up, "label": "does_not_widen" if R_up <= 1 else "unresolved"}
    R = measured_R(warm8, f8, warm16, f16)
    if R >= g:
        lab = "widens" if warm16 > warm8 + 1e-9 else "floor_only"
    else:
        lab = "does_not_widen" if R <= 1 else "unresolved"
    return {**out, "R": R, "label": lab}


def gate(R: float, g: float | None = None) -> str:
    """R alone against g (no warm-side condition): kept for the prediction table; the registered rule is `decide`."""
    g = gate_factor() if g is None else g
    if math.isnan(R):
        return "nan"
    return "widens" if R >= g else ("does_not_widen" if R <= 1 else "unresolved")


def measured_R(warm8: float, floor8: float, warm16: float, floor16: float) -> float:
    return (warm16 / floor16) / (warm8 / floor8)


E0_SWEEPS = {"off_8": "configs/sweep_l1pl350cl_pc_off.yaml", "off_16": "configs/sweep_l1t16pl350cl_pc_off.yaml"}


def closed_loop_floors(s: dict, turns: int = 16, onset_8: float = 2.0, onset_16: float = 1.5) -> dict:
    """Model F's closed-loop floors on the replay of E1's and E2's cache-off sweeps (analysis/e1.py `replay_rows`,
    seed 0, at REG-8's floor): the mean throughput over the rates from each sweep's onset of saturation up, as
    `gate.cold_floor` averages them. Under model F a closed-loop sweep serves a mix tilted to short turns, so its floor
    lies above the open-loop one by an amount that grows with the overload, and R moves. The onsets are inputs, not
    read from the replay: the replay has no KV pool, and its stand-in for "full" (throughput < 0.95 x planned) already
    fires at 1.5 req/s at 8 turns, below REG-8's measured onset of 2.0 (`gate.cold_floor` on KV). Defaults: 2.0 at 8
    turns (REG-8) and 1.5 at 16 turns (the first grid rate above the predicted 16-turn floor of 1.26-1.36). When the
    real onsets are known, the comparison is redone at them (`by_onset`)."""
    from analysis import e1
    base, out = predict(s, turns), {}
    for name, cost in e1.E1["costs"].items():
        rows = {k: e1.replay_rows(p, E0["floor_8"], cost, 0) for k, p in E0_SWEEPS.items()}
        fl = {k: {float(lo): float(r[r.rate >= lo - 1e-9].throughput.mean()) for lo in r.rate[:-1]}
              for k, r in rows.items()}
        ratio = fl["off_16"][onset_16] / fl["off_8"][onset_8]
        out[name] = {"floor_cl_8": fl["off_8"][onset_8], "floor_cl_16": fl["off_16"][onset_16],
                     "floor_ratio_cl": ratio, "R_cl": base[name]["warm_ratio"] / ratio, "by_onset": fl}
    return out


E0_PARENTS = {"warm_8": "sweep_l1pl350cl_pc_on", "off_8": "sweep_l1pl350cl_pc_off",
              "warm_16": "sweep_l1t16pl350cl_pc_on", "off_16": "sweep_l1t16pl350cl_pc_off"}


def predict_measured(s: dict, turns: int = 16) -> dict:
    """The prediction on the gate's own scale (E0/E1 review: the table gave the true R): each model's 16-turn warm
    capacity (2.4 x its warm ratio) rounded down onto E2's grid, as the configs' rule would read it, with model F's
    closed-loop floors; then `decide`."""
    base, fl, out = predict(s, turns), closed_loop_floors(s, turns), {}
    for name in base:
        c16 = base[name]["warm_cl_T"]
        read = max([r for r in E0["warm_grid_16"] if r <= c16 + 1e-9], default=math.nan)
        d = decide(E0["warm_cl_8"], fl[name]["floor_cl_8"], read, fl[name]["floor_cl_16"])
        out[name] = {"warm_cl_16_true": c16, "warm_cl_16_read": read, **d}
    return out


def observed() -> dict:
    """The measured gate, from the four closed-loop sweeps (valid runs only): warm capacities by the configs' rule
    (`tables.sweep_capacity`), floors by `e1.floor` (`gate.cold_floor`, REG-8's settings, with the registered tail
    fallback). Never call before E1 and E2 have run under approved registrations."""
    from analysis import e1
    from analysis.gate import sweep_rows
    from analysis.tables import sweep_capacity, sweep_table
    sw = sweep_table()
    warm = {k: sweep_capacity(E0_PARENTS[k], sw) for k in ("warm_8", "warm_16")}
    floor = {k: e1.floor(sweep_rows(E0_PARENTS[k])) for k in ("off_8", "off_16")}
    mine = sw[(sw.parent == E0_PARENTS["warm_16"]) & sw.valid.astype(bool)]
    low16_measured = bool((mine.rate == min(E0["warm_grid_16"])).any())
    d = decide(warm["warm_8"], floor["off_8"]["mu_sat_off"], warm["warm_16"], floor["off_16"]["mu_sat_off"],
               low16_measured)
    return {"warm": warm, "floor": floor, "low16_measured": low16_measured, **d}
