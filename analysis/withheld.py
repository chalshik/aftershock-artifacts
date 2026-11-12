"""Run folders whose outcome a pending registration withholds (rule 7, rule A5; docs/FABLE_PROMPT.md §3).

A run is sealed from the moment its folder exists until `docs/decisions.md` holds the [RESULT] heading of the
registration that owns it. While sealed, `load.load_run` refuses it, and `load.find_runs`, `recheck.recheck`,
`tables.arrival_table` and `engine_config.scan` skip it and say so on stderr. Nothing here reads a run folder.

Not covered, on purpose: `checks.json`, which a rerun decision may read directly (the registrations' stopping rules),
and `tools/` (checksums, validity flags, inventory), which read no outcome.

The owning registration's own computation is the one exception. It sets the environment variable
AFTERSHOCK_UNSEAL to its id (several ids separated by commas), e.g. `AFTERSHOCK_UNSEAL=REG-20 python -m analysis.k1 …`.
REG-19's registered computation needs no variable: it runs from the worktree at a7bb77a (decisions.md 2026-11-13
[DECISION] (delegate), REG-19 resume), whose code predates this module.
"""
from __future__ import annotations

import fnmatch
import os
import sys
from pathlib import Path

DECISIONS = Path(__file__).resolve().parent.parent / "docs" / "decisions.md"

# (registration id, pattern over the run-folder name, text of the decisions.md heading that lifts the seal)
SEALS: tuple[tuple[str, str, str], ...] = (
    ("REG-19", "*_l1pl350cl_r2.0_w3000_s1[5-9]", "[RESULT] REG-19"),
    ("REG-20", "*_l1pl350ol_r2.[05]_w3000_s1[5-9]", "[RESULT] REG-20"),
    ("REG-20", "*_burst_l1pl350cl_r2.0_w3000_s15_drift", "[RESULT] REG-20"),
)


class WithheldError(RuntimeError):
    """A sealed run folder was about to be read."""


def lifted(heading_text: str, decisions: Path | None = None) -> bool:
    """True once a `## ` heading of decisions.md contains `heading_text`."""
    p = decisions or DECISIONS
    if not p.exists():
        return False
    return any(line.startswith("## ") and heading_text in line for line in p.read_text().splitlines())


def unsealed_ids() -> set[str]:
    return {x.strip() for x in os.environ.get("AFTERSHOCK_UNSEAL", "").split(",") if x.strip()}


def sealed_by(run_name: str, decisions: Path | None = None) -> str | None:
    """The id of the registration that still seals this run folder, or None."""
    for reg, pattern, heading in SEALS:
        if fnmatch.fnmatchcase(run_name, pattern) and reg not in unsealed_ids() and not lifted(heading, decisions):
            return reg
    return None


def guard(run_name: str) -> None:
    reg = sealed_by(run_name)
    if reg:
        raise WithheldError(f"{run_name} is withheld until the [RESULT] of {reg} is in docs/decisions.md "
                            f"(analysis/withheld.py). Only its checks.json may be read.")


def keep(paths, what: str = "runs") -> list:
    """`paths` (run folders) without the sealed ones; one stderr line names how many were skipped and by which seal."""
    out, skipped = [], {}
    for p in paths:
        reg = sealed_by(Path(p).name)
        if reg:
            skipped[reg] = skipped.get(reg, 0) + 1
        else:
            out.append(p)
    for reg, n in sorted(skipped.items()):
        print(f"withheld: {what} skipped {n} run folder(s) sealed by {reg} (analysis/withheld.py)", file=sys.stderr)
    return out
