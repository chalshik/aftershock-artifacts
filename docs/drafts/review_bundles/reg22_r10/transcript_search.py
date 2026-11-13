"""Search every Claude Code transcript of this project for commands that ran an analysis module or read a REG-19 run.

Written 2026-11-13 for REG-21 / REG-22's "What was known" (owner-proxy BB2, BD3; rule F BA4, BC-O1; the reviews in
docs/drafts/reviews-2026-11-13/). Run it at a registration's append and save its stdout under this folder:

    python3 docs/probe/20261113_transcript_search/search.py > docs/probe/20261113_transcript_search/search_<UTC stamp>.txt

What it reads: the tool calls (their inputs only) in every *.jsonl under the project's transcript folder, the
subagents' included, with no date floor. It never reads or prints a tool's output, so nothing a command printed can
reach this file. Commands run by hand outside these sessions (a terminal, the VM's own shell) are not covered: a limit.

Classes of hit (each printed with file, line, time and at most SNIP characters around the match):
  ran        an `analysis` module executed outside pytest: `python -m analysis.X` at the start of a shell command
             (heredoc bodies fed to cat/tee are text and are removed first), or an import of `analysis` inside code
             that runs (`python - <<EOF` bodies, `python -c '...'`, or a .py file written by a Write call and later run
             by `python <that path>`). The functions the code names on the module are listed (`X.f(`).
  reg19_read a Bash command or a Read call that opens a file inside a REG-19 run folder (`*_w3000_s15`..`_s19`) other
             than `checks.json`, or a log whose name carries such a config.
  ran_on_reg19  a `ran` hit whose command text names a REG-19 run or its pattern (`w3000_s15`..`s19`, `s1[5-9]`).
  named      a command that only names an analysis module (a grep, a git command, text written to a file). Counted;
             listed only with --all.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.expanduser("~/.claude/projects/-Users-chalshik-Projects-aftershock-artifacts")
SNIP = 140
HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1")
RUN_M = re.compile(r"(?:^|[;&|(\n'\"`]|\$\()\s*(?:[A-Za-z_]+=\S*\s+)*(?:\S*uv\s+run\s+(?:--\S+\s+)*)?\S*python3?(?:\s+-[BIOuE]+)*\s+-m\s+analysis\.(\w+)([^\n;&|'\"]{0,80})")
IMPORT = re.compile(r"\bfrom\s+analysis(?:\.(\w+))?\s+import\s+([\w, ()]+)|\bimport\s+analysis\.(\w+)(?:\s+as\s+(\w+))?")
PYC = re.compile(r"python3?\S*\s+(?:-\w+\s+)*-c\s+(['\"])(.*?)(?<!\\)\1", re.S)
PYFILE = re.compile(r"\S*python3?\S*\s+(?:-\w+\s+)*([^\s'\"<>|;&-][^\s'\"<>|;&]*\.py)\b")
NAMED = re.compile(r"analysis\.(\w+)")
REG19_FILE = re.compile(r"_w3000_s1[5-9][\w.\-]*/(?!checks\.json\b)[\w.\-]+|_w3000_s1[5-9]_?[\w\-]*\*?\.log\b")


def split_heredocs(cmd):
    """Return (shell text without heredoc bodies, [python bodies], [text bodies])."""
    shell, py, text = [], [], []
    lines = cmd.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        shell.append(line)
        i += 1
        for m in HEREDOC.finditer(line):
            delim = m.group(2)
            body = []
            while i < len(lines) and lines[i].strip() != delim:
                body.append(lines[i])
                i += 1
            i += 1
            (py if re.search(r"python3?\S*(\s+-\S+)*\s+-(\s|$)|python3?\S*\s*$|python3?\S*\s+-\s*<<", line[: m.start()] + "<<") else text).append("\n".join(body))
    return "\n".join(shell), py, text


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
    return text[max(0, a - SNIP // 2): b + SNIP // 2].replace("\n", " \\n ")


def main():
    show_all = "--all" in sys.argv
    files = sorted(glob.glob(os.path.join(ROOT, "**", "*.jsonl"), recursive=True))
    n_calls, hits, named, scripts = 0, [], 0, {}
    seen = set()
    for path in files:
        rel = os.path.relpath(path, ROOT)
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
                    if key in seen:      # the same call copied into a later transcript (a resumed session)
                        continue
                    seen.add(key)
                    n_calls += 1
                    name, inp, ts = c.get("name"), c.get("input") or {}, obj.get("timestamp", "?")
                    if name == "Write":
                        fp, content = str(inp.get("file_path", "")), str(inp.get("content", ""))
                        if fp.endswith(".py") and "/analysis/" not in fp and "/tests/" not in fp and IMPORT.search(content):
                            scripts[os.path.basename(fp)] = (fp, py_hits(content), content)
                        continue
                    if name == "Read":
                        fp = str(inp.get("file_path", ""))
                        if re.search(r"_w3000_s1[5-9]", fp) and not fp.endswith("checks.json"):
                            hits.append((ts, rel, ln, "reg19_read", "Read", fp))
                        continue
                    if name != "Bash":
                        continue
                    cmd = str(inp.get("command", ""))
                    if re.search(r"\bpytest\b", cmd) and not RUN_M.search(cmd):
                        continue
                    shell, pybodies, textbodies = split_heredocs(cmd)
                    found = False
                    for m in RUN_M.finditer(shell):
                        hits.append((ts, rel, ln, "ran", f"-m analysis.{m.group(1)}{m.group(2).rstrip()}", snip(shell, m.start(), m.end())))
                        found = True
                    for body in pybodies + [m.group(2) for m in PYC.finditer(shell)]:
                        for mods, fn, a, b in py_hits(body):
                            hits.append((ts, rel, ln, "ran", f"import analysis.{mods} {fn}", snip(body, a, b)))
                            found = True
                    for m in PYFILE.finditer(shell):
                        base = os.path.basename(m.group(1))
                        if base in scripts:
                            fp, ph, _ = scripts[base]
                            hits.append((ts, rel, ln, "ran", f"script {fp}: " + "; ".join(f"analysis.{x[0]} {x[1]}" for x in ph), snip(shell, m.start(), m.end())))
                            found = True
                    if found and re.search(r"w3000_s1(?:[5-9]|\[5-9\])", cmd):
                        m = re.search(r"w3000_s1(?:[5-9]|\[5-9\])", cmd)
                        hits.append((ts, rel, ln, "ran_on_reg19", "analysis code whose command names a REG-19 run", snip(cmd, m.start(), m.end())))
                    for m in REG19_FILE.finditer(shell):
                        hits.append((ts, rel, ln, "reg19_read", "bash", snip(shell, m.start(), m.end())))
                    if not found and NAMED.search(cmd):
                        named += 1
                        if show_all:
                            m = NAMED.search(cmd)
                            hits.append((ts, rel, ln, "named", m.group(0), snip(cmd, m.start(), m.end())))
    print(f"# transcript search: {len(files)} files under {ROOT}; {n_calls} distinct tool calls read (inputs only)")
    print(f"# ran {sum(h[3] == 'ran' for h in hits)}; ran_on_reg19 {sum(h[3] == 'ran_on_reg19' for h in hits)}; reg19_read {sum(h[3] == 'reg19_read' for h in hits)}; named only {named} (listed with --all)")
    for h in sorted(hits, key=lambda h: (h[0], h[1], h[2])):
        print(" | ".join(str(x) for x in h))


if __name__ == "__main__":
    sys.exit(main())
