# Claims

The study's two claims, each with its test, what would support it, what would refute it, and its status. Created 2026-11-04. Changing a claim or its status needs the owner (CLAUDE.md C).

**Paper claims C3–C9 live in the owner's Paper Plan v2 for now**, outside this repo. Where the paper layer lives is the owner's decision (open, 2026-11-04 audit). Until then, nothing here may cite them as evidence, and they are not checked by `tools/check_docs.py`.

## C1. The symptom
**Claim:** at some load λ between μ_off and μ_warm, percent fast stays low after the trigger has ended, while the same load without a trigger stays healthy (plan, Stage 2 Purpose; PROTOCOL §2).

- **Test:** shock runs judged by `load.verdict` (PROTOCOL §3), and all six conditions of a metastable failure at one load; plus the up-then-down ramp at two dwells.
- **Supports:** at one load, `stuck` in most seeds, the control `recovered`, the confirmation run `stuck` over a 4500 s watch, and `recovered` after the drop to λ = 1 (condition 6). Or a ramp gap that stays at both dwells.
- **Refutes, for the conditions tested:** every valid trigger run at a setup's healthy loads `recovered` or `slow_drain`, none `stuck`, and that setup's ramp shows no gap (PROTOCOL §3; this rule was written after results, **[new 2026-11-04]**).
- **Metric:** percent fast is the plan's main number. Whether C1 is stated in percent fast or completions/s is the owner's decision (open, 2026-11-04 audit).
- **Status (2026-11-04):** not supported. Per cell, all stuck 0 of 3, one-sided 95 % upper bound 0.63 each (`analysis/stats.py`, `cp_upper`):
  - default pool, 20 s gaps: wipe λ = 3, wipe λ = 3.5, burst λ = 3, burst λ = 3.5; ramp at 300 s and 600 s: no gap. Negative by the PROTOCOL rule.
  - 72,480-token pool, 20 s gaps: wipe λ = 3, burst λ = 3. **No ramp was run, so this setup is not negative by the PROTOCOL rule**; it is "no stuck run".
  - default pool, 5 s gaps: wipe and burst at λ = 3.5 and 4.5. **No ramp was run**; "no stuck run".
  - Single-seed controls in every cell. Whether the test loads were inside a real danger zone is in question (`docs/model.md` M2, M4); until the feasibility gate is run, a negative here may say only that these loads recover.

## C2. The cause
**Claim:** a sustaining loop. Cache lost → slow requests → big running batch → KV memory full → cached prefixes evicted before their session's next turn → cache stays lost (plan; PROTOCOL §2).

- **Test:** in stuck runs, the loop figure (helper metrics in the plan's order) and condition 4 (mean KV ≥ 0.80, mean N ≥ 2 × baseline, N below the 256 cap); then the controls that cut a link: prefix caching off, and protected prefixes.
- **Supports:** stuck runs that show the order and the memory limit, and stop getting stuck when a link is cut.
- **Refutes:** stuck runs without a memory limit (a backlog, not this loop), or stuck runs that stay stuck with prefixes protected.
- **Status (2026-11-04):** untestable so far: there is no stuck run. Related evidence, not a test of C2: during bursts KV reached 1.00 and hits fell to 0.11–0.35, and every run then recovered within about 5 minutes (decisions.md 2026-11-02, 2026-11-03). The caching-off control has no defined form yet, and the protected-prefixes control (S4) is not investigated.
