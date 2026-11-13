"""Read-only, run on the VM (sent over ssh on stdin): for the config names given, every run folder of those configs
under ~/aftershock-artifacts/runs and what its checks.json and env.json say. Read: the fields `valid` and `failed` of
checks.json; for a failed `no_errors` check, whether any request ended with the status `client_error` (the names of
the statuses, never their counts); and `git_commit` of env.json. Nothing is written. One line per folder:
"<run id> valid|invalid|nochecks|unreadable <failed check names, comma-joined, or -> <commit or ->"; a failed
`no_errors` is printed as `no_errors/client_error` or `no_errors/other`. The last line is "END <number of configs>",
so a cut-off answer is not taken for a complete one."""
import json
import pathlib
import re
import sys

cfgs = sys.argv[1:]
root = pathlib.Path.home() / "aftershock-artifacts" / "runs"
if not cfgs or not root.is_dir():
    print("ERROR no config given or no runs directory")
    sys.exit(3)
pat = re.compile(r"^\d{8}-\d{6}_(" + "|".join(re.escape(c) for c in cfgs) + r")$")
for d in sorted(p for p in root.iterdir() if p.is_dir() and pat.match(p.name)):
    try:
        commit = str(json.loads((d / "env.json").read_text())["git_commit"]).strip() or "-"
    except Exception:
        commit = "-"
    f = d / "checks.json"
    if not f.is_file():
        print(d.name, "nochecks", "-", commit)
        continue
    try:
        c = json.loads(f.read_text())
        valid, failed = c["valid"], [str(x) for x in c["failed"]]
        ok = isinstance(valid, bool) and valid == (not failed)
        if ok and "no_errors" in failed:
            detail = next(x["detail"] for x in c["checks"] if x["name"] == "no_errors")
            kind = "client_error" if detail.get("client_error", 0) > 0 else "other"
            failed = [f"no_errors/{kind}" if x == "no_errors" else x for x in failed]
    except Exception:
        ok = False
    if not ok:
        print(d.name, "unreadable", "-", commit)
    else:
        print(d.name, "valid" if valid else "invalid", ",".join(failed) or "-", commit)
print("END", len(cfgs))
