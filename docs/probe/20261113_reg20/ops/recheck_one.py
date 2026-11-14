"""Today's checks (harness.checks.run_checks, the checks in force since A14) on ONE run folder in REG-20's holding
folder, read-only, against the verdict stored in its checks.json (draft 2 of REG-20's arm A operations decision, RB2
and RA2 (b)). It is analysis/recheck.py's per-folder step for a folder that is not yet in runs/: analysis.recheck reads
only runs/, and a run must be rechecked before it enters runs/, so that a run today's checks fail can be set aside
under the owner's ruling 2a without a second valid run of its config ever reaching k1.

Usage, from the repo root on the Mac (common.sh `recheck_one` calls it):

    .venv/bin/python docs/probe/20261113_reg20/ops/recheck_one.py <holding-folder>/<run id>

It prints one JSON object with the validity fields only: run, stored_valid, now_valid, stored_failed, now_failed,
changed (True when the verdict or the list of failed checks differs, as analysis.recheck.changed), or `error` when
today's code cannot read the folder (listed, not hidden, as analysis.recheck does). No check detail is printed: the
details could hint at an outcome. It refuses a folder inside the repository's runs/ (analysis.recheck covers those) and
writes nothing. It imports harness.checks only (no analysis module, so the seal is not involved; harness.checks reads
no analysis code).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]          # docs/probe/20261113_reg20/ops/recheck_one.py -> repo root


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("recheck_one: give exactly one run folder", file=sys.stderr)
        return 2
    d = Path(argv[1]).resolve()
    if not d.is_dir() or not (d / "config.yaml").is_file():
        print(f"recheck_one: {argv[1]} is not a run folder (no config.yaml)", file=sys.stderr)
        return 3
    if (ROOT / "runs") in d.parents:
        print("recheck_one: the folder is inside runs/; analysis.recheck covers those", file=sys.stderr)
        return 3
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from harness.checks import run_checks

    stored_p = d / "checks.json"
    stored = json.loads(stored_p.read_text()) if stored_p.exists() else None
    row = {"run": d.name, "stored_valid": stored["valid"] if stored else None,
           "stored_failed": stored["failed"] if stored else None}
    try:
        now = run_checks(d)
    except Exception as e:  # a folder today's code cannot read is listed, not hidden
        row.update({"now_valid": None, "now_failed": None, "changed": True, "error": f"{type(e).__name__}: {e}"[:200]})
    else:
        row.update({"now_valid": now["valid"], "now_failed": now["failed"],
                    "changed": row["stored_valid"] != now["valid"]
                    or sorted(row["stored_failed"] or []) != sorted(now["failed"])})
    print(json.dumps(row, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
