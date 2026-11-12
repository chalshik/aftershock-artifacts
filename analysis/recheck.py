"""Today's `harness.checks` applied, read-only, to every run folder, against the verdict stored in its checks.json.

Used when a check changes (A14 coverage rules, owner 2026-11-12) to list every run whose verdict the change would move.
Nothing is written: `harness.checks.run_checks` returns its result, and checks.json stays as the run wrote it. Marking
a run invalid beyond its automatic checks is the owner's decision (CLAUDE.md, C).
"""
from __future__ import annotations

import json
import sys

from analysis.load import RUNS
from harness.checks import run_checks


def recheck(pattern: str = "*") -> list[dict]:
    rows = []
    for d in sorted(RUNS.glob(pattern)):
        if not (d / "config.yaml").exists():
            continue
        stored_p = d / "checks.json"
        stored = json.loads(stored_p.read_text()) if stored_p.exists() else None
        try:
            now = run_checks(d)
        except Exception as e:  # a folder today's code cannot read is listed, not hidden
            rows.append({"run": d.name, "stored_valid": stored and stored["valid"], "now_valid": None,
                         "error": f"{type(e).__name__}: {e}"[:200]})
            continue
        rows.append({"run": d.name, "stored_valid": stored["valid"] if stored else None, "now_valid": now["valid"],
                     "stored_failed": stored["failed"] if stored else None, "now_failed": now["failed"],
                     "recorder": next((c["detail"] for c in now["checks"] if c["name"] == "recorder"), None),
                     "gpu_steady": next((c["detail"] for c in now["checks"] if c["name"] == "gpu_steady"), None)})
    return rows


def changed(rows: list[dict]) -> list[dict]:
    """Runs whose verdict or list of failed checks differs from the stored one."""
    return [r for r in rows if r.get("error") or r["stored_valid"] != r["now_valid"]
            or sorted(r["stored_failed"] or []) != sorted(r["now_failed"])]


if __name__ == "__main__":
    rows = recheck(sys.argv[1] if len(sys.argv) > 1 else "*")
    ch = changed(rows)
    print(json.dumps({"n_runs": len(rows), "n_changed": len(ch), "changed": ch}, indent=1, default=str))
