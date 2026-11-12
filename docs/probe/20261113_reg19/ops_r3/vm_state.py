"""Read-only, run on the VM (sent over ssh on stdin): for one config name, every run folder of that config under
~/aftershock-artifacts/runs and what its checks.json says. Only the fields `valid` and `failed` are read; nothing is
written. One line per folder: "<run id> valid|invalid|nochecks|unreadable <failed check names, comma-joined, or ->";
the last line is "END <config>", so a cut-off answer is not taken for a complete one."""
import json
import pathlib
import re
import sys

cfg = sys.argv[1]
root = pathlib.Path.home() / "aftershock-artifacts" / "runs"
if not root.is_dir():
    print("ERROR no runs directory")
    sys.exit(3)
pat = re.compile(r"^\d{8}-\d{6}_" + re.escape(cfg) + r"$")
for d in sorted(p for p in root.iterdir() if p.is_dir() and pat.match(p.name)):
    f = d / "checks.json"
    if not f.is_file():
        print(d.name, "nochecks", "-")
        continue
    try:
        c = json.loads(f.read_text())
        valid, failed = c["valid"], c["failed"]
        ok = isinstance(valid, bool) and isinstance(failed, list) and valid == (not failed)
    except Exception:
        ok = False
    if not ok:
        print(d.name, "unreadable", "-")
    else:
        print(d.name, "valid" if valid else "invalid", ",".join(str(x) for x in failed) or "-")
print("END", cfg)
