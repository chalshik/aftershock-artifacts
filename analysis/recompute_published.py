"""Recompute the derived values published in docs/decisions.md with analysis/derived.py, and compare.

Usage (on the Mac, from the repo root): uv run --extra analysis python -m analysis.recompute_published
Prints one row per value: what, decisions.md line, published, the original, recomputed, and whether each agrees
with the published value to its precision. Every parameter below is the one stated in the cited entry.
Reads runs/ and analysis/recovered/ only.

"Original" is the value the original, never-committed code printed at the time, read from its recorded output in
analysis/recovered/ (see INDEX.md there). The originals are not re-run: several ssh to the VM or read scratch files.
"—" means no original was recovered for that value.
"""
import copy
import re
from pathlib import Path

import numpy as np

from analysis import derived as D
from analysis import load as L
from harness.run import load_config
from harness.workload import build_schedule

ROOT = Path(__file__).resolve().parent.parent
C_DEFAULT, C_72K = 96_656, 72_480          # pool sizes from the server logs (decisions.md 2026-11-01, 2026-11-02)
REC = ROOT / "analysis" / "recovered"
ROWS = []


def _agrees(value, published, decimals):
    """Agree if |value - published| is within half a unit of the published precision."""
    return value is not None and not np.isnan(value) and abs(value - published) <= 0.5 * 10 ** -decimals + 1e-12


def row(what, line, published, value, decimals, original=None):
    r = lambda v: None if v is None else round(float(v), decimals + 2)
    ROWS.append((what, line, published, r(original), r(value), "ok" if _agrees(value, published, decimals) else "DIFFERS",
                 "—" if original is None else ("ok" if _agrees(original, published, decimals) else "DIFFERS")))


def rec(tool_id, pattern, group=1, after=None):
    """A number the original code printed: regex `pattern` in analysis/recovered/*<tool_id>*.out.txt,
    searched from the first occurrence of `after` on (to pick one run's block)."""
    text = next(REC.glob(f"*{tool_id}*.out.txt")).read_text()
    if after is not None:
        text = text[text.index(after):]
    return float(re.search(pattern, text).group(group))


def run(pattern):
    found = L.find_runs(pattern, valid_only=False)
    assert len(found) == 1, (pattern, [r["dir"].name for r in found])
    return found[0]


def schedule(rate, seed, gap_mean=None):
    """The schedule the harness would build for a stage2_cap_base run at this rate and seed (2400 s)."""
    cfg = load_config(ROOT / "configs/stage2_cap_base.yaml")
    wl = copy.deepcopy(cfg["workload"])
    wl["rate"] = rate
    if gap_mean is not None:
        wl["sessions"]["turn_gap_s"]["mean"] = gap_mean
    return build_schedule(wl, seed)[0]


def w_values(rate, seeds, t_from, gap_mean=None):
    out = []
    for s in seeds:
        sc = schedule(rate, s, gap_mean)
        out.append(D.working_set(sc, np.arange(t_from, sc.t_planned.max(), 1.0)))
    return np.concatenate(out)


def main():
    # Sanity: the rebuilt schedule is the one the harness wrote for a real run.
    real = run("20261102-072216_wipe_preempt_r3_s1")
    rebuilt = schedule(3.0, 1)
    assert np.allclose(real["requests"].sort_values("request_id").prompt_tokens_planned.to_numpy(), rebuilt.prompt_len.to_numpy())

    # --- W, decisions.md 2026-11-01 table (lines 250-256): seeds 1, 2; t >= 600 s; mean (p10-p90), as a share of C.
    W, W_ORIG = {}, {}
    for lam, (mean, p10, p90), line in [(2, (0.49, 0.39, 0.59), 252), (2.5, (0.62, 0.49, 0.75), 253), (3, (0.75, 0.61, 0.89), 254),
                                        (3.5, (0.87, 0.73, 1.03), 255), (4, (1.01, 0.88, 1.16), 256)]:
        w = w_values(lam, [1, 2], 600)
        W[lam] = w.mean()
        # The original sampled W every 5 s from 600 s (stage2_base.yaml schedule); this reconstruction every 1 s.
        o = rf"λ={lam:g}: active [\d.]+ W mean (\d+) = [\d.]+C p10 ([\d.]+) p90 ([\d.]+)"
        W_ORIG[lam] = rec("toolu_015jLzJd", o, 1)
        row(f"W/C mean, lambda={lam}", line, mean, w.mean() / C_DEFAULT, 2, W_ORIG[lam] / C_DEFAULT)
        row(f"W/C p10, lambda={lam}", line, p10, np.quantile(w, .1) / C_DEFAULT, 2, rec("toolu_015jLzJd", o, 2))
        row(f"W/C p90, lambda={lam}", line, p90, np.quantile(w, .9) / C_DEFAULT, 2, rec("toolu_015jLzJd", o, 3))
    # W in tokens and pool ratios, decisions.md 2026-11-02 (lines 405-409).
    for lam, k, line in [(2, 47.6, 405), (2.5, 59.7, 406), (3, 73.0, 409)]:
        row(f"W tokens (k), lambda={lam}", line, k, W[lam] / 1000, 1, W_ORIG[lam] / 1000)
    for lam, pub72, pubdef in [(2.5, 1.21, 1.62), (3, 0.99, 1.32)]:
        row(f"72,480 / W, lambda={lam}", 409, pub72, C_72K / W[lam], 2, C_72K / W_ORIG[lam])
        row(f"96,656 / W, lambda={lam}", 409, pubdef, C_DEFAULT / W[lam], 2, C_DEFAULT / W_ORIG[lam])
    # 5 s vs 20 s gaps, decisions.md 2026-11-03 (line 499): lambda = 3, seed 1. t >= 600 s assumed, as in the 11-01 table.
    for gap, k, share in [(5.0, 18.7, 0.19), (20.0, 74.8, 0.77)]:
        w = w_values(3, [1], 600, gap)
        o = rec("toolu_01Fkc7Rr", rf"gap {gap:g} s: W at lambda 3 mean (\d+)")   # original: 10 s grid
        row(f"W tokens (k), {gap:g} s gaps, lambda=3 seed 1", 499, k, w.mean() / 1000, 1, o / 1000)
        row(f"W/C, {gap:g} s gaps, lambda=3 seed 1", 499, share, w.mean() / C_DEFAULT, 2, o / C_DEFAULT)

    # --- F, decisions.md 2026-11-01 table: mean KV over the measured window, and over its last third (lines 252-256).
    F, F_ORIG = {}, {}
    for lam, side, pat, (mean, last), line in [
            (2, "warm", "*sweep_pc_on_r2", (0.06, 0.07), 252), (3, "warm", "*sweep_pc_on_r3", (0.13, 0.16), 254),
            (4, "warm", "*sweep_pc_on_r4", (0.31, 0.35), 256), (2, "cold", "*sweep_pc_off_r2", (0.11, 0.14), 252),
            (3, "cold", "*sweep_pc_off_r3", (0.41, 0.77), 254), (4, "cold", "*sweep_pc_off_r4", (0.87, 0.95), 256)]:
        r = run(pat)
        a, b = r["cfg"]["workload"]["warmup_s"], r["cfg"]["workload"]["duration_s"]
        F[lam, side] = (D.kv_footprint(r, a, b, 1.0), D.kv_footprint(r, a + 2 * (b - a) / 3, b, 1.0))
        o = rf"{pat[1:]} dur 900 KV mean ([\d.]+) last third ([\d.]+)"
        F_ORIG[lam, side] = (rec("toolu_015jLzJd", o, 1), rec("toolu_015jLzJd", o, 2))
        row(f"F_{side}/C mean, lambda={lam} ({r['dir'].name})", line, mean, F[lam, side][0], 2, F_ORIG[lam, side][0])
        row(f"F_{side}/C last third, lambda={lam}", line, last, F[lam, side][1], 2, F_ORIG[lam, side][1])
    # The table's "fits/holds" columns: W mean + F (mean; last third).
    for lam, side, (lo, hi), line in [(2, "cold", (0.60, 0.63), 252), (3, "warm", (0.88, 0.91), 254), (3, "cold", (1.16, 1.52), 254),
                                      (4, "warm", (1.32, 1.36), 256)]:
        wc, wo = W[lam] / C_DEFAULT, W_ORIG[lam] / C_DEFAULT   # the published sums were added by hand from 2-decimal values
        row(f"(W+F_{side})/C low, lambda={lam}", line, lo, wc + F[lam, side][0], 2, wo + F_ORIG[lam, side][0])
        row(f"(W+F_{side})/C high, lambda={lam}", line, hi, wc + F[lam, side][1], 2, wo + F_ORIG[lam, side][1])
    # 72,480-pool reasoning (lines 405-407): F_warm in tokens. The entry names no source run; candidates shown.
    for what, pub, pat, a, b, line in [("F_warm tokens (k), lambda=2, wipe_test_preempt 240-900 s", 6.4, "*wipe_test_preempt", 240, 900, 405),
                                       ("F_warm tokens (k), lambda=2, sweep_pc_on_r2 240-900 s", 6.4, "*sweep_pc_on_r2", 240, 900, 405),
                                       ("F_warm tokens (k), lambda=2.5, control r2.5 240-2400 s", 8.7, "*stage2_control_cap_r2.5", 240, 2400, 406),
                                       ("F_warm tokens (k), lambda=2.5, control r2.5 240-900 s", 8.7, "*stage2_control_cap_r2.5", 240, 900, 406)]:
        row(what, line, pub, D.kv_footprint(run(pat), a, b, C_DEFAULT) / 1000, 1)

    SHARE = (r"{} later turns \d+ \| sent before prev first token ([\d.]+), .*?"
             r"cached share: all ([\d.]+), prev already done at own start ([\d.]+)")
    # --- Cached-share split and overlap, decisions.md 2026-11-01 "Limits that stay" (lines 292-293).
    for pat, (al, af), line in [("*sweep_pc_on_r3", (0.667, 0.647), 293), ("*sweep_pc_on_r5", (0.438, 0.143), 293),
                                ("*sweep_pc_on_r10", (0.240, 0.030), 293)]:
        s = D.cached_share_split(run(pat))
        row(f"cached share, all later turns, {pat[1:]}", line, al, s["all_later"], 3, rec("toolu_01YMQ5wz", SHARE.format(pat[1:]), 2))
        row(f"cached share, after previous finished, {pat[1:]}", line, af, s["after_prev_finished"], 3,
            rec("toolu_01YMQ5wz", SHARE.format(pat[1:]), 3))
    for pat, pub, dec in [("*sweep_pc_on_r3", 0.013, 3), ("*sweep_pc_on_r4", 0.015, 3), ("*sweep_pc_on_r5", 0.43, 2),
                          ("*sweep_pc_off_r4", 0.62, 2)]:
        row(f"sent before previous first token, {pat[1:]}", 292, pub, D.overlap_fraction(run(pat)), dec,
            rec("toolu_01YMQ5wz", SHARE.format(pat[1:]), 1))

    # --- Per-span hit rates around a trigger: counter hit over [end + a, end + b).
    for pat, pubs in [("*wipe_test_preempt", (0.774, 0.229, 0.681, 0.752)), ("*wipe_test_idle", (0.773, 0.249, 0.634, 0.745))]:
        r = run(pat)
        start, end = D.trigger_times(r)
        blk = "=== runs/" + r["dir"].name   # the original's "before" is the 120 s before the wipe
        before = rec("toolu_01NT9QvG", r"-120\.\.  \+0s hit=([\d.]+)", after=blk)
        row(f"hit before (240 s to wipe start), {pat[1:]}", 226, pubs[0], D.hit_between(r["metrics"], 240, start), 3, before)
        row(f"hit before (240 s to trigger.at_s), {pat[1:]}", 226, pubs[0], D.hit_between(r["metrics"], 240, r["cfg"]["trigger"]["at_s"]), 3, before)
        for (a, b), pub, o in zip([(0, 15), (15, 60), (60, 120)], pubs[1:],
                                  [r"\+0\.\. \+15s hit=([\d.]+)", r"\+15\.\. \+60s hit=([\d.]+)", r"\+60\.\.\+120s hit=([\d.]+)"]):
            row(f"hit {a}-{b} s after wipe, {pat[1:]}", 226, pub, D.span_hits(r, [(a, b)], end)[a, b], 3, rec("toolu_01NT9QvG", o, after=blk))

    def span_range(pats, a, b, use_end=True):
        vals = []
        for p in pats:
            r = run(p)
            vals.append(D.span_hits(r, [(a, b)], D.trigger_times(r)[1])[a, b])
        return min(vals), max(vals)
    BURST_ORIG = [rec("toolu_012hfq29", r"\+0\.\.60 +sessions-only fast [\d.]+ p99 [\d.]+ \| hit ([\d.]+)")] + [
        rec("toolu_01XKSd8X", r"\+0\.\.60 +fast [\d.]+ \| hit ([\d.]+)", after=rid + " |")
        for rid in ("20261102-135701_burst_r3_s2", "20261102-144008_burst_r3_s3")]
    lam3 = ["20261102-045827_wipe_preempt_r3_s1", "20261102-053935_wipe_preempt_r3_s2", "20261102-062040_wipe_preempt_r3_s3"]
    for (a, b), (lo, hi), o in [((0, 15), (0.19, 0.30), r"\+   0\.\.  15 n .*? hit ([\d.]+)"),
                                ((15, 60), (0.56, 0.64), r"\+  15\.\.  60 n .*? hit ([\d.]+)")]:
        lo_v, hi_v = span_range(lam3, a, b)
        orig = [rec("toolu_018ir8No", o, after="== " + p) for p in lam3]
        row(f"hit {a}-{b} s after wipe, lambda=3 first attempts, min", 339, lo, lo_v, 2, min(orig))
        row(f"hit {a}-{b} s after wipe, lambda=3 first attempts, max", 339, hi, hi_v, 2, max(orig))
    row("hit 0-15 s after wipe, 20261102-072216_wipe_preempt_r3_s1", 344, 0.191,
        span_range(["20261102-072216_wipe_preempt_r3_s1"], 0, 15)[0], 3, rec("toolu_01HSt1Px", r"hit 0-15s ([\d.]+)"))
    row("hit 0-15 s after wipe, 20261102-100744_wipe_preempt_r3_s3", 362, 0.295,
        span_range(["20261102-100744_wipe_preempt_r3_s3"], 0, 15)[0], 3, rec("toolu_017XQn8t", r"\+0\.\.15 fast [\d.]+ hit ([\d.]+)"))
    row("hit 15-60 s after wipe, 20261102-100744_wipe_preempt_r3_s3", 362, 0.61,
        span_range(["20261102-100744_wipe_preempt_r3_s3"], 15, 60)[0], 2, rec("toolu_017XQn8t", r"\+15\.\.60 fast [\d.]+ hit ([\d.]+)"))
    for pats, (lo, hi), what, line in [
            (["*wipe_preempt_r3.5_s1", "*wipe_preempt_r3.5_s2", "*wipe_preempt_r3.5_s3"], (0.49, 0.53), "first minute after wipe, lambda=3.5", 375),
            (["*burst_r3_s1", "*burst_r3_s2", "*burst_r3_s3"], (0.17, 0.35), "0-60 s after burst end, lambda=3", 393),
            (["*burst_kv72k_r3_s1", "*burst_kv72k_r3_s2", "*burst_kv72k_r3_s3"], (0.11, 0.28), "0-60 s after burst end, 72k lambda=3", 459)]:
        lo_v, hi_v = span_range(pats, 0, 60)
        orig = BURST_ORIG if line == 393 else None   # the lambda = 3.5 and 72k originals were not recovered
        row(f"hit {what}, min", line, lo, lo_v, 2, None if orig is None else min(orig))
        row(f"hit {what}, max", line, hi, hi_v, 2, None if orig is None else max(orig))
    row("hit 0-60 s after wipe, 72k lambda=3, lowest", 460, 0.43,
        span_range(["*wipe_kv72k_r3_s1", "*wipe_kv72k_r3_s2", "*wipe_kv72k_r3_s3"], 0, 60)[0], 2)
    for p in ["*burst_r3_s1", "*burst_r3_s2", "*burst_r3_s3"]:   # for the record: the dip during the burst itself
        r = run(p)
        s, e = D.trigger_times(r)
        ROWS.append((f"(not published) hit during the burst, {r['dir'].name}", 393, None, None, round(D.hit_between(r["metrics"], s, e), 3), "info", "—"))

    # --- Thirds and healthy noise.
    lr, s3 = run("*long_run"), run("*sweep_pc_on_r3")
    third = lambda i, g: rec("toolu_01Tq9Ecx", rf"third {i}: .*?hit\(mean of intervals\) ([\d.]+) hit\(counter ratio\) ([\d.]+)", g)
    for i, pub in enumerate([0.609, 0.608, 0.600]):
        row(f"long run third {i + 1}, mean of per-scrape ratios", 118, pub, D.thirds(lr, "mean_of_ratios")[i], 3, third(i + 1, 1))
    row("long run middle third, counter", 116, 0.6363, D.thirds(lr, "counter")[1], 4, third(2, 2))
    row("long run last third, counter", 116, 0.6254, D.thirds(lr, "counter")[2], 4, third(3, 2))
    for i, pub in enumerate([0.674, 0.625, 0.585]):
        row(f"sweep_pc_on_r3 third {i + 1}, mean of per-scrape ratios", 93, pub, D.thirds(s3, "mean_of_ratios")[i], 3,
            rec("toolu_017iqsdv", r"rate  3 completions.*?thirds: hit \[([\d.]+), ([\d.]+), ([\d.]+)\]", i + 1))
    wl = lr["cfg"]["workload"]
    sp300 = D.span_hit_spread(lr, 300, wl["warmup_s"], wl["duration_s"])
    o300 = [float(x) for x in re.search(r"hit 300s: \[([^\]]+)\]", next(REC.glob("*toolu_01LsHsS5*.out.txt")).read_text()).group(1).split(",")]
    row("long run 300 s hit, min", 209, 0.593, sp300["min"], 3, min(o300))
    row("long run 300 s hit, max", 209, 0.679, sp300["max"], 3, max(o300))
    row("long run 60 s hit, SD", 169, 0.045, D.span_hit_spread(lr, 60, wl["warmup_s"], wl["duration_s"])["sd"], 3)
    for start, step in [(0.0, 60), (wl["warmup_s"], 60), (0.0, 1)]:
        a300 = D.adjacent_change(lr, 300, step, start, wl["duration_s"], 0.02)
        a600 = D.adjacent_change(lr, 600, step, start, wl["duration_s"], 0.02)
        tag = f"from {start:g} s, step {step} s"
        # The original slid 60 s steps from t = 600 s; none of these readings starts there.
        adj = lambda w, g: rec("toolu_01YMQ5wz", rf"adjacent {w}s windows hit diff: sd [\d.]+ p95\|d\| ([\d.]+) max [\d.]+; rises>=\.02 share ([\d.]+)", g)
        row(f"adjacent 300 s rose >= 0.02, {tag}", 269, 0.34, a300["rose_frac"], 2, adj(300, 2))
        row(f"adjacent 300 s p95 abs change, {tag}", 269, 0.076, a300["p95_abs_change"], 3, adj(300, 1))
        row(f"adjacent 600 s p95 abs change, {tag}", 269, 0.059, a600["p95_abs_change"], 3, adj(600, 1))

    print("| What | decisions.md line | Published | Original | Recomputed | Recomputed vs published | Original vs published |\n"
          "|---|---|---|---|---|---|---|")
    for r in ROWS:
        print("| " + " | ".join("—" if v is None else str(v) for v in r) + " |")


if __name__ == "__main__":
    main()
