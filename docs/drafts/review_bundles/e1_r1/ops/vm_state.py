"""E1's copy of docs/probe/20261113_reg19/ops_r3/vm_state.py, reduced to E1's allowed reads: it reads only the fields
`valid` and `failed` of checks.json (ops_r3 also read the detail of a failed `no_errors` check and env.json's
`git_commit`; E1's stopping rule needs neither: any `no_errors` stops E1, and the commit comes from the launch log's
run_id line, see common.sh `settle`).

Read-only, run on the VM (sent over ssh on stdin): for the run names given (<sweep>_r<rate>), every run folder of those
names under ~/aftershock-artifacts/runs and the fields `valid` and `failed` of its checks.json. Nothing is written,
and nothing else of a run folder is printed. One line per folder, in name order (= launch time):
"<run id> valid|invalid|nochecks|unreadable <failed check names, comma-joined, or ->". A checks.json whose `valid` is
not a bool, whose `failed` is not a list of plain names, or whose two fields disagree is "unreadable". The last line
is "END <number of names>", so a cut-off answer is not taken for a complete one."""
import json
import pathlib
import re
import sys

names = sys.argv[1:]
root = pathlib.Path.home() / "aftershock-artifacts" / "runs"
if not names or not root.is_dir():
    print("ERROR no run name given or no runs directory")
    sys.exit(3)
pat = re.compile(r"^\d{8}-\d{6}_(" + "|".join(re.escape(n) for n in names) + r")$")
plain = re.compile(r"^[A-Za-z0-9_]+$")
for d in sorted(p for p in root.iterdir() if p.is_dir() and pat.match(p.name)):
    f = d / "checks.json"
    if not f.is_file():
        print(d.name, "nochecks", "-")
        continue
    try:
        c = json.loads(f.read_text())
        valid, failed = c["valid"], c["failed"]
        ok = (isinstance(valid, bool) and isinstance(failed, list)
              and all(isinstance(x, str) and plain.match(x) for x in failed) and valid == (not failed))
    except Exception:
        ok = False
    if not ok:
        print(d.name, "unreadable", "-")
    else:
        print(d.name, "valid" if valid else "invalid", ",".join(failed) or "-")
print("END", len(names))
