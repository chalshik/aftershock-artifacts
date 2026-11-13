"""search2.py: search.py widened, for REG-21 / REG-22's rerun at the append (owner-proxy BF6 and BH8, rule F BG5(b);
docs/drafts/reviews-2026-11-13/). search.py stays as it was, since drafts cite its output.

    python3 docs/probe/20261113_transcript_search/search2.py > docs/probe/20261113_transcript_search/search2_<UTC stamp>.txt
    python3 docs/probe/20261113_transcript_search/search2.py --selftest

What it reads: the tool calls (inputs only) in every *.jsonl under the project's transcript folder, subagents included,
with no date floor. It never opens a tool's output: tool_result blocks are skipped and the `tool-results/` folders are
not opened. A call copied into a later transcript (a resumed session) is read once, by its tool_use id.

Classes (a call can have several):
  ran              as in search.py: `python -m analysis.X`, an `analysis` import in code that runs (`python - <<EOF`,
                   `python -c`), or a run of a .py script it saw written whose text imports `analysis`. One line each.
  script_reads_runs  python that runs (inline, or a .py script it saw written) and, by its syntax tree, calls a run
                   reader (`find_runs`, `load_run`, `batch1_runs`, ...) or opens, globs or lists a path built from `RUNS`
                   or a 'runs/' literal. Labelled `stubbed` when the code also assigns to `find_runs`, `load_run` or
                   `RUNS` (a guard), `unparsed` when the text is not valid Python. The calling lines are printed.
  ran_unknown      (BH8 c) a python run of a .py file outside `analysis/` and `tests/` whose writing it did not see.
                   Aggregated by path, with whether git tracks that path (its text is then in the repository); listed
                   in full as well when the command names `runs/` or a REG-19 name.
  shell_script     a zsh/bash/sh script file run. Aggregated by path; the script's own commands are not expanded.
  runs_glob_loop   (BF6 1) a command that reads under `runs/` through a glob, a loop over folders, `find`, or a
                   variable folder followed by a run file name (`$d/events.jsonl`).
  cd_run           (BF6 2) a `cd` into `runs/` or a run folder; what follows in the command is printed with it.
  grep_runs        (BF6 4) a Grep call whose path or glob is under `runs/`; glob_runs: a Glob call there (names only).
  read_run         a Read call of a file under `runs/` (any run).
  reg19_read       a read of a file in a REG-19 run folder (`*_w3000_s15`..`_s19`) other than `checks.json`: by Bash
                   (a path or a log name, as search.py), by a `cd` into such a folder, by Read, or by Grep.
  ran_on_reg19     a `ran` hit whose command names a REG-19 run or its pattern.
  names_reg19_run  (BH8 d, BG5 b) any tool's input that names a REG-19 run id (regex
                   `[0-9]{8}-[0-9]{6}_[A-Za-z0-9_.]+_w3000_s1[5-9]`), a REG-19 config name or `w3000_s1[5-9]`.
  write_runs       a Write or Edit whose path is under `runs/`.
Scripts (BH8 a, b; BF6 3): a .py file written by a Write call, by a shell redirection or `tee` (heredoc bodies
included), or changed by an Edit, collected from every transcript before any run is matched. The pytest skip of
search.py is dropped (BG5 b).

What it prints. Every call with a hit other than `ran` gets one record. A command (any tool input with a `command`
field) is printed whole, with two changes:
  - a heredoc body not fed to python is shown as `<<body: N lines -> TARGET, not printed>>`. Such bodies are file
    contents, not commands, and some are notes this search must not open (a REG-19 resume note). The names that matched
    in the input are listed in the record, so a name inside an elided body is still seen.
  - the values of the recorder's status-line keys (`t= h= N= Q= KV= lag= sm=`, harness/recorder.py:157) are
    masked as `<m>`, so that no value a harness log printed can reach this file through a command someone typed.
For any other tool only the tool name, its path or pattern fields and the matched names are printed, never prose or file
content.

Limits (printed at the end too): commands run by hand outside these sessions (a terminal, the VM's own shell); the
commands inside shell scripts (queue.sh, launch.sh, final.sh, ...), listed only as `shell_script` runs; reads made by
code that a script imports from another file; a .py file whose writing is not in any transcript (`ran_unknown`, its
text is in git when tracked); a regex can miss an unusual spelling.
"""
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict

ROOT = os.environ.get("SEARCH2_ROOT") or os.path.expanduser("~/.claude/projects/-Users-chalshik-Projects-aftershock-artifacts")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SNIP = 140

HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1")
RUN_M = re.compile(r"(?:^|[;&|(\n'\"`]|\$\()\s*(?:[A-Za-z_]+=\S*\s+)*(?:\S*uv\s+run\s+(?:--\S+\s+)*)?\S*python3?(?:\s+-[BIOuE]+)*\s+-m\s+analysis\.(\w+)([^\n;&|'\"]{0,80})")
IMPORT = re.compile(r"\bfrom\s+analysis(?:\.(\w+))?\s+import\s+([\w, ()]+)|\bimport\s+analysis\.(\w+)(?:\s+as\s+(\w+))?")
PYC = re.compile(r"python3?\S*\s+(?:-\w+\s+)*-c\s+(['\"])(.*?)(?<!\\)\1", re.S)
PYFILE = re.compile(r"\S*python3?\S*\s+(?:-\w+\s+)*([^\s'\"<>|;&-][^\s'\"<>|;&]*\.py)\b")
SHFILE = re.compile(r"(?:^|[\s;&|(`'\"])(?:zsh|bash|sh)\s+(?:-\w+\s+)*([^\s'\"<>|;&-][^\s'\"<>|;&]*\.(?:sh|zsh))\b")
NAMED = re.compile(r"analysis\.(\w+)")
REG19_FILE = re.compile(r"_w3000_s1[5-9][\w.\-]*/(?!checks\.json\b)[\w.\-]+|_w3000_s1[5-9]_?[\w\-]*\*?\.log\b")
RUN_ID = re.compile(r"[0-9]{8}-[0-9]{6}_[A-Za-z0-9_.]+_w3000_s1[5-9]")
REG19_NAME = re.compile(r"w3000_s1(?:[5-9]|\[5-9\])")
RUNS_GLOB = re.compile(
    r"\bruns/[^\s'\";|&]*[*?\[]"                       # a glob under runs/
    r"|\bruns/\$"                                       # runs/$var
    r"|\bfor\s+\w+\s+in\s+[^;\n]*(?:\bruns\b|\*/)"      # a loop over runs or over folders
    r"|\bfind\s+[^|;\n]*\bruns\b"                       # find under runs
    r"|\$\{?\w+\}?/(?:events\.jsonl|env\.json|server\.log|checks\.json|config\.yaml|gpu\.jsonl|metrics[\w.]*"
    r"|requests[\w.]*|harness\.log|schedule[\w.]*)")    # a variable folder followed by a run file
CD_RUN = re.compile(r"\bcd\s+([^\s;&|)]*(?:\bruns\b|[0-9]{8}-[0-9]{6}_)[^\s;&|)]*)")
REDIR_PY = re.compile(r"(?:>>?|\btee\s+(?:-a\s+)?)\s*(['\"]?)([^\s'\";|&<>]+\.py)\1")
REDIR_ANY = re.compile(r"(?:>>?|\btee\s+(?:-a\s+)?)\s*(['\"]?)([^\s'\";|&<>]+)\1")
STATUS = re.compile(r"\b(t|h|N|Q|KV|lag|sm)=(\s*)-?\d[\d.]*(%|s|MHz)?")
UNDER_RUNS = re.compile(r"(?:^|/|\s)runs/")


def mask(text):
    return STATUS.sub(lambda m: f"{m.group(1)}=<m>", text)


READERS = {"find_runs", "load_run", "batch1_runs", "batch2_runs", "reg19_inputs", "references"}
OPENERS = {"open", "read_text", "read_bytes", "read_csv", "read_json", "read_parquet", "glob", "rglob", "iterdir",
           "listdir", "scandir", "walk", "Path", "exists", "is_dir", "stat"}


def _runs_ref(node):
    import ast
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and n.id == "RUNS" or isinstance(n, ast.Attribute) and n.attr == "RUNS":
            return True
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and (n.value == "runs" or re.search(r"(^|/)runs/", n.value)):
            return True
    return False


def py_reads_runs(body):
    """By the code's syntax tree, not its strings: ('reads', lines) if the code calls a run reader (`find_runs`,
    `load_run`, ...) or opens, globs or lists a path built from `RUNS` or a 'runs/' literal; ('stubbed', lines) if it
    also assigns to `find_runs`, `load_run` or `RUNS` (a reviewer's guard); ('unparsed', lines) if the text is not
    Python and a regex finds `runs/`, `find_runs` or `load_run`; (None, []) otherwise."""
    import ast
    import warnings
    lines = body.split("\n")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tree = ast.parse(body)
    except (SyntaxError, ValueError):
        hit = [l for l in lines if re.search(r"\bruns/|find_runs|load_run", l)]
        return ("unparsed", hit) if hit else (None, [])
    reads, stub = set(), False
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            name = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None
            if name in READERS:
                reads.add(n.lineno)
            elif name in OPENERS and (any(_runs_ref(a) for a in n.args) or isinstance(f, ast.Attribute) and _runs_ref(f.value)):
                reads.add(n.lineno)
        elif isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            for t in (n.targets if isinstance(n, ast.Assign) else [n.target]):
                for x in ast.walk(t):
                    if isinstance(x, ast.Attribute) and x.attr in READERS | {"RUNS"} or isinstance(x, ast.Name) and x.id in READERS | {"RUNS"}:
                        stub = True
    if not reads:
        return None, []
    return ("stubbed" if stub else "reads"), [lines[i - 1] for i in sorted(reads) if 0 < i <= len(lines)]


def split_heredocs(cmd):
    """Return (shell text without bodies, rendered text with non-python bodies elided, [python bodies],
    [(target .py, body)] written by redirection)."""
    shell, rendered, py, written = [], [], [], []
    lines = cmd.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        shell.append(line)
        rendered.append(line)
        i += 1
        if not HEREDOC.search(line):
            m = REDIR_PY.search(line)
            if m and re.search(r"\b(?:printf|echo)\b", line):
                written.append((m.group(2), line))
            continue
        for m in HEREDOC.finditer(line):
            delim = m.group(2)
            body = []
            while i < len(lines) and lines[i].strip() != delim:
                body.append(lines[i])
                i += 1
            closing = lines[i] if i < len(lines) else ""
            i += 1
            text = "\n".join(body)
            if re.search(r"python3?\S*(\s+-\S+)*\s+-(\s|$)|python3?\S*\s*$|python3?\S*\s+-\s*<<", line[: m.start()] + "<<"):
                py.append(text)
                rendered.extend(body)
            else:
                tp, ta = REDIR_PY.search(line), REDIR_ANY.search(line)
                if tp:
                    written.append((tp.group(2), text))
                target = ta.group(2) if ta else "(no file: stdin of the command)"
                rendered.append(f"<<body: {len(body)} lines -> {target}, not printed>>")
            rendered.append(closing)
    return "\n".join(shell), "\n".join(rendered), py, written


def funcs(body, names):
    out = set()
    for n in names:
        out |= set(re.findall(rf"\b{re.escape(n)}\.(\w+)\s*\(", body))
    return sorted(out)


def py_hits(body):
    res = []
    for m in IMPORT.finditer(body):
        if m.group(3):
            mods, alias = [m.group(3)], [m.group(4) or f"analysis.{m.group(3)}"]
        elif m.group(1):
            mods, alias = [m.group(1)], [x.split(" as ")[-1].strip() for x in m.group(2).replace("(", "").replace(")", "").split(",")]
        else:
            parts = [x.strip() for x in m.group(2).replace("(", "").replace(")", "").split(",") if x.strip()]
            mods = [p.split(" as ")[0].strip() for p in parts]
            alias = [p.split(" as ")[-1].strip() for p in parts]
        res.append((",".join(mods), funcs(body, alias), m.start(), m.end()))
    return res


def snip(text, a, b):
    return mask(text[max(0, a - SNIP // 2): b + SNIP // 2].replace("\n", " \\n "))


def strings(x, path=""):
    if isinstance(x, str):
        yield path, x
    elif isinstance(x, dict):
        for k, v in x.items():
            yield from strings(v, f"{path}.{k}" if path else k)
    elif isinstance(x, list):
        for n, v in enumerate(x):
            yield from strings(v, f"{path}[{n}]")


def calls(root):
    """Every distinct tool call (inputs only), in file order."""
    files = sorted(p for p in glob.glob(os.path.join(root, "**", "*.jsonl"), recursive=True) if "/tool-results/" not in p)
    seen, out = set(), []
    for path in files:
        rel = os.path.relpath(path, root)
        with open(path, errors="replace") as fh:
            for ln, line in enumerate(fh, 1):
                try:
                    obj = json.loads(line)
                except ValueError:
                    continue
                msg = obj.get("message")
                if not isinstance(msg, dict) or msg.get("role") != "assistant" or not isinstance(msg.get("content"), list):
                    continue
                for c in msg["content"]:
                    if not isinstance(c, dict) or c.get("type") != "tool_use":
                        continue
                    key = c.get("id")
                    if key in seen:
                        continue
                    seen.add(key)
                    out.append((obj.get("timestamp", "?"), rel, ln, c.get("name"), c.get("input") or {}))
    return files, out


def tracked_paths():
    try:
        r = subprocess.run(["git", "-C", REPO, "ls-files"], capture_output=True, text=True, check=True)
        return r.stdout.split("\n")
    except Exception:
        return []


def is_tracked(p, tracked):
    q = p
    for pre in (REPO + "/", "./", "~/Projects/aftershock-artifacts/", "~/aftershock-artifacts/"):
        if q.startswith(pre):
            q = q[len(pre):]
    return any(t == q or t.endswith("/" + q) for t in tracked if t) if q else False


def search(root, tracked=None):
    tracked = tracked_paths() if tracked is None else tracked
    files, allcalls = calls(root)
    # pass 1: every script written anywhere (BH8 b)
    scripts = defaultdict(list)          # basename -> [(full path, how, text)]
    for ts, rel, ln, name, inp in allcalls:
        if name == "Write" and str(inp.get("file_path", "")).endswith(".py"):
            fp = str(inp["file_path"])
            scripts[os.path.basename(fp)].append((fp, "Write", str(inp.get("content", ""))))
        elif name in ("Edit", "MultiEdit") and str(inp.get("file_path", "")).endswith(".py"):
            fp = str(inp["file_path"])
            texts = [str(inp.get("new_string", ""))] + [str(e.get("new_string", "")) for e in inp.get("edits", []) if isinstance(e, dict)]
            scripts[os.path.basename(fp)].append((fp, "Edit", "\n".join(texts)))
        elif isinstance(inp.get("command"), str):
            for tgt, body in split_heredocs(inp["command"])[3]:
                scripts[os.path.basename(tgt)].append((tgt, "shell redirect", body))

    ran, records, named = [], [], 0
    unknown = defaultdict(list)          # path -> [ts]
    shells = defaultdict(list)
    for ts, rel, ln, name, inp in allcalls:
        classes, details = [], []
        allstr = list(strings(inp))
        names = sorted({m.group(0) for _, s in allstr for m in RUN_ID.finditer(s)} |
                       {m.group(0) for _, s in allstr for m in REG19_NAME.finditer(s)})
        cmd = inp.get("command") if isinstance(inp.get("command"), str) else None
        rendered = None
        if cmd is not None:
            shell, rendered, pybodies, _ = split_heredocs(cmd)
            found = False
            for m in RUN_M.finditer(shell):
                ran.append((ts, rel, ln, "ran", f"-m analysis.{m.group(1)}{m.group(2).rstrip()}", snip(shell, m.start(), m.end())))
                found = True
            for body in pybodies + [m.group(2) for m in PYC.finditer(shell)]:
                for mods, fn, a, b in py_hits(body):
                    ran.append((ts, rel, ln, "ran", f"import analysis.{mods} {fn}", snip(body, a, b)))
                    found = True
                kind, rl = py_reads_runs(body)
                if kind:
                    classes.append("script_reads_runs")
                    details.append(f"inline python, {kind}: " + " || ".join(mask(l.strip())[:200] for l in rl[:12]))
            for m in PYFILE.finditer(shell):
                p = m.group(1)
                base = os.path.basename(p)
                if base in scripts:
                    cands = scripts[base]
                    for fp, how, text in cands:
                        ph = py_hits(text)
                        if ph:
                            ran.append((ts, rel, ln, "ran", f"script {fp} ({how}): " + "; ".join(f"analysis.{x[0]} {x[1]}" for x in ph), snip(shell, m.start(), m.end())))
                            found = True
                        kind, rl = py_reads_runs(text)
                        if kind:
                            classes.append("script_reads_runs")
                            details.append(f"script {fp} ({how}{', one of ' + str(len(cands)) + ' with this name' if len(cands) > 1 else ''}), {kind}:")
                            details.extend("    " + mask(l.strip())[:300] for l in rl[:40])
                elif not re.search(r"(^|/)(analysis|tests)/", p):
                    unknown[p].append(ts)
                    if UNDER_RUNS.search(shell) or names:
                        classes.append("ran_unknown")
                        details.append(f"python runs {p}, whose writing no transcript shows ({'tracked in git' if is_tracked(p, tracked) else 'not tracked'})")
            for m in SHFILE.finditer(shell):
                shells[m.group(1)].append(ts)
            if found and REG19_NAME.search(cmd):
                classes.append("ran_on_reg19")
            for m in REG19_FILE.finditer(shell):
                classes.append("reg19_read")
                details.append(f"bash path: {m.group(0)}")
            if RUNS_GLOB.search(shell):
                classes.append("runs_glob_loop")
                details.append("glob/loop: " + ", ".join(sorted({mask(m.group(0)) for m in RUNS_GLOB.finditer(shell)}))[:300])
            for m in CD_RUN.finditer(shell):
                classes.append("cd_run")
                details.append(f"cd {m.group(1)}")
                if REG19_NAME.search(m.group(1)) and not re.match(r"\s*(?:&&|;)?\s*(?:cd\b|$)", shell[m.end():]):
                    classes.append("reg19_read")
                    details.append("cd into a REG-19 folder followed by commands")
            if not found and NAMED.search(cmd):
                named += 1
        elif name == "Read":
            fp = str(inp.get("file_path", ""))
            if UNDER_RUNS.search(fp):
                classes.append("read_run")
                details.append(f"file_path {fp}")
                if REG19_NAME.search(fp) and not fp.endswith("checks.json"):
                    classes.append("reg19_read")
        elif name == "Grep":
            where = " ".join(str(inp.get(k, "")) for k in ("path", "glob"))
            if UNDER_RUNS.search(where) or re.search(r"(^|/)runs$", str(inp.get("path", ""))):
                classes.append("grep_runs")
                details.append(f"pattern {inp.get('pattern')!r} path {inp.get('path')!r} glob {inp.get('glob')!r} mode {inp.get('output_mode')!r}")
                if REG19_NAME.search(where):
                    classes.append("reg19_read")
        elif name == "Glob":
            where = " ".join(str(inp.get(k, "")) for k in ("pattern", "path"))
            if UNDER_RUNS.search(where) or re.search(r"(^|/)runs(/|$)", where):
                classes.append("glob_runs")
                details.append(f"pattern {inp.get('pattern')!r} path {inp.get('path')!r} (names only)")
        if name in ("Write", "Edit", "MultiEdit", "NotebookEdit") and UNDER_RUNS.search(str(inp.get("file_path", ""))):
            classes.append("write_runs")
            details.append(f"file_path {inp.get('file_path')}")
        if names:
            classes.append("names_reg19_run")
            fields = sorted({k for k, s in allstr if RUN_ID.search(s) or REG19_NAME.search(s)})
            details.append("names: " + ", ".join(names) + "  (in " + ", ".join(fields) + ")")
            if cmd is None:
                pathf = {k: inp.get(k) for k in ("file_path", "path", "pattern", "description", "subagent_type", "to") if inp.get(k)}
                details.append(f"{name} {pathf}; content not printed")
        if classes:
            records.append((ts, rel, ln, name, sorted(set(classes), key=classes.index), details, rendered))

    out = [f"# transcript search 2: {len(files)} files under {root}; {len(allcalls)} distinct tool calls read (inputs only)",
           f"# scripts seen: {sum(len(v) for v in scripts.values())} writes of {len(scripts)} .py names "
           f"(Write {sum(h == 'Write' for v in scripts.values() for _, h, _ in v)}, shell redirect "
           f"{sum(h == 'shell redirect' for v in scripts.values() for _, h, _ in v)}, Edit {sum(h == 'Edit' for v in scripts.values() for _, h, _ in v)})"]
    counts = defaultdict(int)
    for r in records:
        for c in r[4]:
            counts[c] += 1
    out.append(f"# ran {len(ran)}; named only {named}; " + "; ".join(f"{k} {counts[k]}" for k in sorted(counts)))
    out.append(f"# ran_unknown paths {len(unknown)} ({sum(len(v) for v in unknown.values())} runs); shell_script paths {len(shells)}")
    out.append("")
    out.append("## ran (one line each)")
    for h in sorted(ran, key=lambda h: (h[0], h[1], h[2])):
        out.append(" | ".join(str(x) for x in h))
    out.append("")
    out.append("## records (every call with a hit other than `ran`), by time")
    for ts, rel, ln, name, classes, details, rendered in sorted(records, key=lambda r: (r[0], r[1], r[2])):
        out.append(f"### {ts} | {rel}:{ln} | {name} | {', '.join(classes)}")
        out.extend(f"- {d}" for d in details)
        if rendered is not None:
            out.append("  command (heredoc bodies not fed to python elided; status values masked):")
            out.extend("    | " + l for l in mask(rendered).split("\n"))
    out.append("")
    out.append("## ran_unknown by path: path | tracked in git | runs | first | last")
    for p, v in sorted(unknown.items()):
        out.append(f"{p} | {'yes' if is_tracked(p, tracked) else 'no'} | {len(v)} | {min(v)} | {max(v)}")
    out.append("")
    out.append("## shell_script by path: path | tracked in git | runs | first | last")
    for p, v in sorted(shells.items()):
        out.append(f"{p} | {'yes' if is_tracked(p, tracked) else 'no'} | {len(v)} | {min(v)} | {max(v)}")
    out.append("")
    out.append("## limits: commands run by hand outside these sessions; the commands inside shell scripts (listed only as "
               "shell_script runs); reads by code a script imports from another file; .py files whose writing no transcript "
               "shows (ran_unknown; their text is in git when tracked); unusual spellings a regex misses.")
    return out


def selftest():
    rid = "20261112-103423_stage2_control_l1pl350cl_r2.0_w3000_s17"
    calls_ = [
        ("Bash", {"command": "cat > /tmp/x/foo.py <<'EOF'\nfrom analysis import k3w\nprint(open('runs/a/events.jsonl').read())\nEOF"}),
        ("Bash", {"command": "uv run python /tmp/x/foo.py"}),
        ("Bash", {"command": "python3 bar.py runs/"}),
        ("Bash", {"command": "for d in runs/*/; do tail -1 $d/events.jsonl; done"}),
        ("Bash", {"command": f"ssh vm 'cd ~/aftershock-artifacts/runs/{rid} && ls -la && tail -3 events.jsonl'"}),
        ("Grep", {"pattern": "KV", "path": f"runs/{rid}", "output_mode": "content"}),
        ("Write", {"file_path": "docs/x.md", "content": f"secret prose about {rid}"}),
        ("Bash", {"command": "uv run pytest -q && uv run python -m analysis.recheck x"}),
        ("Bash", {"command": "echo 't=  12.0s  h=0.53  Q=4' w3000_s15"}),
        ("Bash", {"command": "cat > notes.md <<EOF\nsecret line w3000_s15 h=0.9\nEOF"}),
        ("Agent", {"description": "d", "prompt": "secret prompt w3000_s18"}),
        ("Read", {"file_path": f"/Users/u/p/runs/{rid}/server.log"}),
        ("Read", {"file_path": f"/Users/u/p/runs/{rid}/checks.json"}),
        ("Bash", {"command": "zsh docs/probe/20261113_reg19/ops_r3/queue.sh"}),
        ("Bash", {"command": "python3 - <<'EOF'\nfrom pathlib import Path\np = Path('analysis/load.py'); t = p.read_text()\n"
                             "t = t.replace('out = find_runs(RUNS)', 'out = []')\np.write_text(t)\nEOF"}),
        ("Bash", {"command": "uv run python - <<'EOF'\nimport analysis.load as L\nL.find_runs = lambda p: []\nprint(L.find_runs('*'))\nEOF"}),
    ]
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "s", "subagents"))
        with open(os.path.join(d, "s.jsonl"), "w") as fh:
            for n, (name, inp) in enumerate(calls_):
                fh.write(json.dumps({"timestamp": f"2026-11-12T10:{n:02d}:00Z", "message": {"role": "assistant", "content": [
                    {"type": "tool_use", "id": f"id{n}", "name": name, "input": inp}]}}) + "\n")
            fh.write(json.dumps({"timestamp": "2026-11-12T11:00:00Z", "message": {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": "id4", "content": "OUTPUT h=0.77 secret_output w3000_s16"}]}}) + "\n")
        with open(os.path.join(d, "s", "subagents", "a.jsonl"), "w") as fh:   # a copied call is read once
            fh.write(json.dumps({"timestamp": "2026-11-12T10:03:00Z", "message": {"role": "assistant", "content": [
                {"type": "tool_use", "id": "id3", "name": "Bash", "input": calls_[3][1]}]}}) + "\n")
        out = "\n".join(search(d, tracked=["docs/probe/20261113_reg19/ops_r3/queue.sh"]))
    rec = {l.split(" | ")[0][4:]: l.split(" | ")[-1] for l in out.split("\n") if l.startswith("### ")}
    def has(n, *cls):
        got = rec.get(f"2026-11-12T10:{n:02d}:00Z", "")
        assert all(c in got.split(", ") for c in cls), (n, cls, got)
    assert "16 distinct tool calls" in out, out[:300]
    assert "script /tmp/x/foo.py (shell redirect): analysis.k3w" in out
    has(1, "script_reads_runs")
    has(2, "ran_unknown")
    has(3, "runs_glob_loop")
    has(4, "cd_run", "reg19_read", "names_reg19_run")
    has(5, "grep_runs", "reg19_read", "names_reg19_run")
    has(6, "names_reg19_run")
    assert "-m analysis.recheck x" in out                       # the pytest skip is gone
    has(8, "names_reg19_run")
    has(9, "names_reg19_run")
    has(10, "names_reg19_run")
    has(11, "read_run", "reg19_read")
    got12 = rec.get("2026-11-12T10:12:00Z", "")
    assert "read_run" in got12 and "reg19_read" not in got12, got12
    assert "docs/probe/20261113_reg19/ops_r3/queue.sh | yes | 1" in out
    assert "2026-11-12T10:14:00Z" not in rec, rec.get("2026-11-12T10:14:00Z")   # a code edit whose strings name find_runs
    has(15, "script_reads_runs")
    assert "inline python, stubbed" in out
    for bad in ("secret", "h=0.53", "0.53", "h=0.9", "0.77", "OUTPUT"):
        assert bad not in out, bad
    assert "<<body: 1 lines -> notes.md, not printed>>" in out
    print("selftest: OK (16 cases)")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    print("\n".join(search(ROOT)))
