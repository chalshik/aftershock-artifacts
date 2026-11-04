"""Consistency checks between the docs, the run folders and git. Read-only; stdlib only.

    python3 tools/check_docs.py [--runs-dir runs] [--quick]

Checks (docs/process.md §6):
  run_ids       every run id named in the docs exists in runs/
  validity      what the docs say about a run's validity matches its checks.json
  inventory     status.md's run counts and its invalid / no-checks lists match runs/
  tags          every decisions.md heading from the first tagged one on carries one tag; [RESULT] entries cite RUN(...)
  append_only   docs/decisions.md only ever grew, from APPEND_ONLY_SINCE on, and the working copy extends HEAD
  file_refs     every FILE(path:line) tag points at an existing file and line
  context_pack  docs/context-pack.md equals what tools/context_pack.py generates
  configs       no config used by a run differs at HEAD from the run's commit (CLAUDE.md rule 5)
  manifest      manifests/runs.sha256 only ever grew; every run folder in runs/ is listed in it
`--quick` runs only the checks that need neither runs/ nor git history (for the session-start hook).
If runs/ holds no run folders (the VM after copies are removed), the run checks are skipped and say so.
Exit 1 if any check fails.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUN_ID = re.compile(r"\d{8}-\d{6}_[A-Za-z0-9_.]*[A-Za-z0-9]")
TAGS = ("[REG]", "[RESULT]", "[CORR]", "[DECISION]", "[OPS]")
DOCS = ["CLAUDE.md", "PROTOCOL.md", "docs/status.md", "docs/decisions.md", "docs/open-questions.md",
        "docs/definitions.md", "docs/model.md", "docs/claims.md", "docs/process.md"]
# The one in-place edit of an old decisions.md entry (logged as a [CORR], 2026-11-04). The rule holds from here on.
APPEND_ONLY_SINCE = "cfc18da"
# Used configs edited after use, each logged in decisions.md. Nothing else may be added here without a [CORR] entry.
KNOWN_CONFIG_EDITS = {("configs/base.yaml", "20261023-145613_smoke")}  # decisions.md 2026-10-23, gpu_steady refined


def _git(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)


def run_state(runs: Path) -> dict[str, str]:
    """run id -> VALID | INVALID | NOCHECKS, from each folder's checks.json."""
    out = {}
    for d in sorted(p for p in runs.iterdir() if p.is_dir() and RUN_ID.fullmatch(p.name)):
        c = d / "checks.json"
        out[d.name] = "NOCHECKS" if not c.exists() else ("VALID" if json.loads(c.read_text())["valid"] else "INVALID")
    return out


def claims(text: str) -> list[tuple[int, str, str | None]]:
    """(line number, run id, claimed state or None). A claim is the word VALID or INVALID in the text between this
    id and the next one on the line; or, for ids without one, an "all/both ... VALID" before the line's first id."""
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        ms = list(RUN_ID.finditer(line))
        if not ms:
            continue
        head = line[:ms[0].start()]
        head_claim = "VALID" if re.search(r"\b(all|both)\b[^`]*\bVALID\b", head) and "INVALID" not in head else None
        for i, m in enumerate(ms):
            tail = line[m.end(): ms[i + 1].start() if i + 1 < len(ms) else len(line)]
            if not line.lstrip().startswith("|"):  # prose: a claim belongs to its own clause
                tail = re.split(r"[;.]\s", tail)[0]
            c = "INVALID" if re.search(r"\bINVALID\b", tail) else "VALID" if re.search(r"\bVALID\b", tail) else head_claim
            out.append((n, m.group(), c))
    return out


def check_runs(docs: dict[str, str], state: dict[str, str]) -> list[str]:
    errs = []
    for path, text in docs.items():
        for n, rid, c in claims(text):
            if rid not in state:
                errs.append(f"run_ids: {path}:{n} names {rid}, which is not in runs/")
            elif c and not (c == state[rid] or (c == "INVALID" and state[rid] == "NOCHECKS")):
                errs.append(f"validity: {path}:{n} says {rid} is {c}; checks.json says {state[rid]}")
    return errs


def check_inventory(status: str, state: dict[str, str]) -> list[str]:
    errs = []
    m = re.search(r"(\d+) run folders: (\d+) VALID, (\d+) INVALID, (\d+) without checks", status)
    real = [len(state)] + [sum(v == k for v in state.values()) for k in ("VALID", "INVALID", "NOCHECKS")]
    if not m:
        errs.append("inventory: status.md has no 'N run folders: a VALID, b INVALID, c without checks' line")
    elif [int(x) for x in m.groups()] != real:
        errs.append(f"inventory: status.md says {m.group(0)!r}; runs/ has {real}")
    listed = {"INVALID": set(), "NOCHECKS": set()}
    for line in status.splitlines():
        if line.startswith("- **Invalid"):
            listed["INVALID"] |= set(RUN_ID.findall(line))
        elif line.startswith("- **No checks"):
            listed["NOCHECKS"] |= set(RUN_ID.findall(line))
    for k, ids in listed.items():
        real_ids = {r for r, v in state.items() if v == k}
        if ids != real_ids:
            errs.append(f"inventory: status.md lists {k} {sorted(ids ^ real_ids)} wrongly (missing or extra)")
    return errs


def entries(decisions: str) -> list[tuple[int, str, str]]:
    """(line, heading, body) for each '## ' entry."""
    out, cur = [], None
    for n, line in enumerate(decisions.splitlines(), 1):
        if line.startswith("## "):
            cur = [n, line, []]
            out.append(cur)
        elif cur:
            cur[2].append(line)
    return [(n, h, "\n".join(b)) for n, h, b in out]


def check_tags(decisions: str) -> list[str]:
    errs, started = [], False
    for n, h, body in entries(decisions):
        tagged = [t for t in TAGS if t in h]
        started = started or bool(tagged)
        if started and len(tagged) != 1:
            errs.append(f"tags: docs/decisions.md:{n} heading needs exactly one of {' '.join(TAGS)}")
        if "[RESULT]" in tagged and "RUN(" not in body:
            errs.append(f"tags: docs/decisions.md:{n} [RESULT] entry cites no RUN(run_id, function)")
    return errs


def check_append_only() -> list[str]:
    if _git("rev-parse", "--git-dir").returncode:
        return ["append_only: skipped (not a git checkout)"]
    errs = []
    commits = _git("log", "--reverse", "--format=%H", f"{APPEND_ONLY_SINCE}..HEAD", "--", "docs/decisions.md").stdout.split()
    prev = _git("show", f"{APPEND_ONLY_SINCE}:docs/decisions.md").stdout
    for c in commits:
        cur = _git("show", f"{c}:docs/decisions.md").stdout
        if not cur.startswith(prev):
            errs.append(f"append_only: commit {c[:7]} changed earlier text of docs/decisions.md")
        prev = cur
    work = (REPO / "docs/decisions.md").read_text()
    head = _git("show", "HEAD:docs/decisions.md").stdout
    if head and not work.startswith(head):
        errs.append("append_only: the working copy of docs/decisions.md changes text that is in HEAD")
    return errs


def check_manifest(runs: Path | None) -> list[str]:
    """Append-only over git history and against HEAD; with runs/, every run folder has at least one line."""
    errs, path = [], "manifests/runs.sha256"
    if _git("rev-parse", "--git-dir").returncode == 0:
        prev = ""
        for c in _git("log", "--reverse", "--format=%H", "--", path).stdout.split():
            cur = _git("show", f"{c}:{path}").stdout
            if not cur.startswith(prev):
                errs.append(f"manifest: commit {c[:7]} changed earlier lines of {path}")
            prev = cur
        work = (REPO / path).read_text() if (REPO / path).exists() else ""
        if not work.startswith(prev):
            errs.append(f"manifest: the working copy of {path} changes lines that are in HEAD")
    if runs is not None:
        listed = {line.split("  ", 1)[1].split("/", 1)[0] for line in
                  ((REPO / path).read_text().splitlines() if (REPO / path).exists() else []) if "  " in line}
        missing = sorted(d.name for d in runs.iterdir() if d.is_dir() and RUN_ID.fullmatch(d.name) and d.name not in listed)
        if missing:
            errs.append(f"manifest: {len(missing)} run folders not in {path} (run `python3 tools/manifest.py update`), e.g. {missing[:3]}")
    return errs


def check_file_refs(docs: dict[str, str]) -> list[str]:
    errs = []
    for path, text in docs.items():
        for n, line in enumerate(text.splitlines(), 1):
            for ref, a in re.findall(r"FILE\(([^:()\s]+):(\d+)", line):
                f = REPO / ref
                if not f.exists():
                    errs.append(f"file_refs: {path}:{n} FILE({ref}) does not exist")
                elif int(a) > len(f.read_text(errors="replace").splitlines()):
                    errs.append(f"file_refs: {path}:{n} FILE({ref}:{a}) is past the end of the file")
    return errs


def check_context_pack() -> list[str]:
    sys.path.insert(0, str(REPO / "tools"))
    import context_pack
    pack = REPO / "docs/context-pack.md"
    if not pack.exists():
        return ["context_pack: docs/context-pack.md is missing; run python3 tools/context_pack.py"]
    return [] if pack.read_text() == context_pack.build() else \
        ["context_pack: docs/context-pack.md is stale or hand-edited; run python3 tools/context_pack.py"]


def check_configs(runs: Path) -> list[str]:
    """A run's source config, and every parent it extends, must be identical at the run's commit and at HEAD."""
    errs = []
    for d in sorted(p for p in runs.iterdir() if p.is_dir() and (p / "env.json").exists() and (p / "config.yaml").exists()):
        commit = json.loads((d / "env.json").read_text()).get("git_commit")
        m = re.search(r"^source_config:\s*(\S+)", (d / "config.yaml").read_text(), re.M)
        if not (commit and m):
            continue
        path = "configs/" + m.group(1).split("configs/")[-1]
        while path:
            old, new = _git("show", f"{commit}:{path}"), _git("show", f"HEAD:{path}")
            if old.returncode:
                errs.append(f"configs: {d.name} used {path}, which is not in git at its commit {commit[:7]}")
                break
            if old.stdout != new.stdout and (path, d.name) not in KNOWN_CONFIG_EDITS:
                errs.append(f"configs: {path} changed after {d.name} used it")
            p = re.search(r"^extends:\s*(\S+)", old.stdout, re.M)
            path = f"configs/{p.group(1)}" if p else None
    return errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-dir", type=Path, default=REPO / "runs")
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args(argv)
    missing = [p for p in DOCS if not (REPO / p).exists()]
    errs = [f"missing: {p}" for p in missing]
    docs = {p: (REPO / p).read_text() for p in DOCS if p not in missing}
    errs += check_tags(docs.get("docs/decisions.md", "")) + check_file_refs(docs) + check_context_pack()
    notes = []
    if not a.quick:
        errs += check_append_only()
        state = run_state(a.runs_dir) if a.runs_dir.exists() else {}
        errs += check_manifest(a.runs_dir if state else None)
        if state:
            errs += check_runs(docs, state) + check_inventory(docs.get("docs/status.md", ""), state) + check_configs(a.runs_dir)
        else:
            notes.append(f"run checks skipped: no run folders in {a.runs_dir}")
    for line in notes + errs:
        print(line)
    print(f"check_docs: {'FAIL' if errs else 'OK'} ({len(errs)} problems)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
