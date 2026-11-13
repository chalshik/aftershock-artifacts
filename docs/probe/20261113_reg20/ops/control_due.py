"""REG-20's control decision for one open burst run of arm A: the only per-run reading allowed mid-matrix.

REG-20 (docs/decisions.md 2026-11-12 [REG], "Controls, conditional") runs `stage2_control_l1pl350ol_r2.0_w3000_s<n>`
only for an open seed whose burst run is cold-backlogged, right after it. This script reads that one bit and nothing
else. Usage, from the repo root on the Mac, after the run folder has been copied and checksum-verified:

    .venv/bin/python docs/probe/20261113_reg20/ops/control_due.py <exact run-folder name>

It prints exactly one line on stdout:
    CONTROL_DUE yes       analysis.k1.cold_backlogged(run)["cold_backlogged"] is True
    CONTROL_DUE no        ... is False
    CONTROL_DUE unclear   ... is None (k1 gives None when any input is NaN) or NaN; no control is then run
and no readout value, reuse, queue or KV number. Anything else (a bad name, a missing, invalid or foreign folder, an
unexpected value) prints nothing on stdout, one reason on stderr, and exits non-zero.

The seal (analysis/withheld.py) is lifted for REG-20 only and only in this process: AFTERSHOCK_UNSEAL is set to
"REG-20" here, replacing any inherited value, before the folder is loaded. The folder is loaded with
analysis.load.load_run from analysis.load.RUNS / <name>, i.e. the Mac's runs/. Never writes anything.
"""
import math
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]          # docs/probe/20261113_reg20/ops/control_due.py -> repo root
NAME = re.compile(r"^\d{8}-\d{6}_(burst_l1pl350ol_r2\.0_w3000_s1[5-9])$")   # arm A's open burst runs, seeds 15-19


def word(value) -> str | None:
    """'yes' / 'no' / 'unclear' for k1's cold_backlogged value; None for a value k1 never gives."""
    if value is None:
        return "unclear"
    if isinstance(value, float) and math.isnan(value):
        return "unclear"
    if type(value).__name__ in ("bool", "bool_"):     # Python's bool or numpy's bool_
        return "yes" if bool(value) else "no"
    return None


def main(argv: list[str]) -> int:
    if len(argv) != 2 or not NAME.match(argv[1]):
        print("control_due: give exactly one run-folder name of an arm A open burst run "
              "(<yyyymmdd-hhmmss>_burst_l1pl350ol_r2.0_w3000_s<15-19>)", file=sys.stderr)
        return 2
    name, cfg_name = argv[1], NAME.match(argv[1]).group(1)
    os.environ["AFTERSHOCK_UNSEAL"] = "REG-20"         # this process only; read by analysis.withheld at load time
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from analysis import k1, load

    d = load.RUNS / name
    if not d.is_dir():
        print(f"control_due: no folder {name} under runs/", file=sys.stderr)
        return 3
    run = load.load_run(d)
    checks = run.get("checks")
    if not (isinstance(checks, dict) and checks.get("valid") is True):
        print(f"control_due: {name} is not a valid run (checks.json)", file=sys.stderr)
        return 3
    if (run.get("cfg") or {}).get("name") != cfg_name:
        print(f"control_due: the config in {name} is not named {cfg_name}", file=sys.stderr)
        return 3
    w = word(k1.cold_backlogged(run)["cold_backlogged"])
    if w is None:
        print(f"control_due: k1.cold_backlogged gave a value of an unexpected type for {name}", file=sys.stderr)
        return 4
    print(f"CONTROL_DUE {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
