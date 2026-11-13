"""CL15 (REG-22's owner-proxy, round 7): an inputs-only search of every transcript of this project (sessions and their
subagents) for tool-call inputs naming the note `RESUME.md`, the pack section `s6.md`, the folder `ctxpack` or the pack
`context-pack-2026-11-12`. Prints one line per hit: time | transcript:line | tool | class | rule | input head.
Prints no tool result and opens no run folder, note or pack.

Classes:
  1  the note or its copy (the pack's §6.20, lines 3891-4128, whose §6.20.2, lines 4060-4128, is the note verbatim; or
     s6.md) read, whole or in part, or possibly so
     (a print of pack lines by a pattern over the whole pack);
  2  other sections of the pack read (a Read or line range that misses lines 3891-4128), or headings only;
  3  a write, edit, listing, prompt text or no read.
Rules are applied in order; a hand label in noteread_labels.tsv (key, class, note) overrides the rule.
CL17 (REG-22's owner-proxy, round 8) adds hits whose input does not name the note or the pack but can print them; their
rule text starts "CL17:": recursive or folder-level reads whose path covers the note or the pack (grep -r/-R, rg, git grep,
the Grep tool, and cat/head/tail/sed/awk on a glob, over ., docs, docs/probe, docs/probe/20261111_reg19[/ops] or
docs/paper); and git show, git log -p/--patch or git diff that covers 54a995d or da1f836, the commits that hold the note.
A covering command that prints only file names, counts or stats is class 3; one that may print lines is class 1.
usage: python3 noteread.py [LABELS]
"""
import fnmatch
import glob
import json
import os
import re
import shlex
import subprocess
import sys

BASE = os.path.expanduser("~/.claude/projects/-Users-chalshik-Projects-aftershock-artifacts/")
NAMES = re.compile(r"RESUME\.md|s6\.md|ctxpack|context-pack-2026-11-12")
WIDE = re.compile(r"\"(Grep|Bash)\"")  # CL17: any Grep or Bash call is a candidate
COPY = (3891, 4128)  # the pack's §6.20; its §6.20.2 (lines 4060-4128) is the note's copy
labels = {}
if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
    for l in open(sys.argv[1]):
        if l.strip() and not l.startswith("#"):
            k, c, n = l.rstrip("\n").split("\t", 2)
            labels[k] = (c, n)

READERS = r"(cat|sed|grep|egrep|rg|head|tail|awk|cut|less|more|nl|tr|sort|uniq|diff|python3?|open\(|read_text|readlines)"


def bash_segments(body):
    """Split a command into simple commands; expand $VAR from assignments in the same command, a `for V in w...` loop
    variable into one copy per word, and prefix relative paths with the directory of the last `cd`."""
    raw = []
    for line in body.split("\n"):
        try:
            lx = shlex.shlex(line, posix=True, punctuation_chars=True)
            lx.whitespace_split = True
            toks = list(lx)
        except ValueError:
            raw += [s.split() for s in re.split(r";|\|\||&&|\|", line)]
            continue
        cur = []
        for tok in toks:
            if tok in (";", "|", "||", "&&", "&", "(", ")", ";;"):
                raw.append(cur); cur = []
            else:
                cur.append(tok)
        raw.append(cur)
    env, loops, cwd, out = {}, {}, None, []
    for w in raw:
        while w and (re.match(r"^[A-Za-z_]\w*=", w[0]) or w[0] in ("time", "do", "then", "else", "{", "done", "fi", "!")):
            if "=" in w[0]:
                k, v = w[0].split("=", 1)
                env[k] = v
            w = w[1:]
        if len(w) >= 3 and w[0] == "for" and w[2] == "in":
            loops[w[1]] = w[3:] or [""]
            continue
        def exp(tok, env):
            return re.sub(r"\$\{?(\w+)\}?", lambda m: env.get(m.group(1), m.group(0)), tok)
        copies = [env]
        for v, words in loops.items():
            if any(re.search(r"\$\{?" + v + r"\b", x) for x in w):
                copies = [dict(c, **{v: word}) for c in copies for word in words]
        for c in copies:
            ww = [exp(x, c) for x in w]
            if ww and ww[0] == "cd" and len(ww) > 1:
                cwd = ww[1] if ww[1].startswith("/") else (cwd + "/" + ww[1] if cwd else ww[1])
                continue
            out.append((ww, cwd))
    return out


def grep_pattern_alts(w):
    """The alternatives of a grep's pattern (first non-option word, or the word after -e)."""
    args = w[1:]
    for k, a in enumerate(args):
        if a == "-e" and k + 1 < len(args):
            return args[k + 1].split("\0")[0].split("\\|")
    for a in args:
        if not a.startswith("-"):
            return a.split("\0")[0].split("\\|")
    return []


def bash_class(body):
    best = None
    for w, cwd in bash_segments(body):
        if cwd and w:
            w = [w[0]] + [x if x.startswith(("/", "-")) else x + "\0" + cwd + "/" + x for x in w[1:]]
        seg = " ".join(w)
        if not w or not NAMES.search(seg):
            continue
        first = w[0]
        if first in ("cd", "ls", "wc", "git", "echo", "printf", "mkdir", "test", "stat", "cp", "mv", "shasum", "sha256sum",
                     "touch", "find", "du", "rm", "comm", "for", "do", "done"):
            continue
        if first == "sed" and "-i" in w:
            continue
        if first not in ("cat", "sed", "grep", "egrep", "rg", "head", "tail", "awk", "cut", "nl", "less", "more", "python3",
                         "python", "uv", "diff", "sort", "uniq", "tr"):
            continue
        if first in ("grep", "egrep", "rg") and any(re.fullmatch(r"-[a-zA-Z]*[clLq][a-zA-Z]*", x) for x in w[1:]) \
                and not any(re.fullmatch(r"-[a-zA-Z]*[nABCo][a-zA-Z]*", x) for x in w[1:]):
            best = best or ("3", "grep printing counts or file names only (-c/-l/-L/-q)")
            continue
        heads = first in ("grep", "egrep", "rg") and (lambda a: bool(a) and all(re.match(r"\^#", x) for x in a))(grep_pattern_alts(w))
        args = [x for x in w[1:] if not x.startswith("-")]
        if first in ("grep", "egrep", "rg", "sed", "awk") and args and "-e" not in w:
            args = args[1:]
        files = [y for x in args for y in x.split("\0")]
        def touches_copy(x):
            if re.search(r"RESUME\.md$|s6\.md$", x):
                return True
            if "ctxpack" in x and any(ch in x for ch in "*?["):
                return fnmatch.fnmatch(x.rsplit("/", 1)[0] + "/s6.md", x)
            return x.rstrip("/").endswith("ctxpack") and "-r" in " ".join(w)
        if any(touches_copy(x) for x in files):
            if heads:
                best = best or ("2", f"{first} of headings only, over the note or s6.md")
                continue
            return "1", f"{first} on the note or s6.md (or a glob or folder that includes it)"
        if any("context-pack-2026-11-12" in x for x in files):
            m = re.search(r"sed -n '?(\d+),(\d+)p", seg) or re.search(r"sed -n (\d+),(\d+)p", seg) \
                or re.search(r"NR\s*>=?\s*(\d+)\s*&&\s*NR\s*<=?\s*(\d+)", seg)
            if m:
                lo, hi = int(m.group(1)), int(m.group(2))
                c = "1" if lo <= COPY[1] and hi >= COPY[0] else "2"
                if c == "1":
                    return c, f"{first} of pack lines {lo}-{hi}"
                best = best or (c, f"{first} of pack lines {lo}-{hi}")
                continue
            if heads:
                best = best or ("2", "grep of the pack's headings only")
                continue
            return "1", f"{first} over the pack (may print lines of the copy)"
        if any("ctxpack" in x for x in files):
            best = best or ("2", f"{first} of another ctxpack file")
    return best or ("3", "named in a command that does not read it (git, ls, wc, echo, cd, a path in a string)")


def classify(tool, inp):
    s = json.dumps(inp, ensure_ascii=False)
    if tool in ("Write", "Edit", "NotebookEdit", "MultiEdit"):
        return "3", "write or edit"
    if tool in ("Agent", "Task", "SendMessage", "TaskCreate", "ExitPlanMode", "AskUserQuestion"):
        return "3", "prompt or message text"
    if tool in ("Glob", "LS"):
        return "3", "listing"
    if tool == "Read":
        fp = inp.get("file_path", "")
        if fp.endswith("RESUME.md") or fp.endswith("s6.md"):
            return "1", "Read of the note or s6.md"
        if "context-pack-2026-11-12" in fp:
            o, n = inp.get("offset"), inp.get("limit")
            if o is None:
                return "1", "Read of the pack from its start (no offset)"
            o = int(o); hi = o + int(n or 2000) - 1
            return ("1", f"Read of pack lines {o}-{hi}, overlapping 3891-4128") if o <= COPY[1] and hi >= COPY[0] else ("2", f"Read of pack lines {o}-{hi}")
        if "ctxpack" in fp:
            return "2", "Read of another ctxpack file"
        return "3", "Read of a file that names them"
    if tool == "Grep":
        p = inp.get("path", "") or ""
        if re.search(r"RESUME\.md|s6\.md", p):
            return "1", "Grep of the note or s6.md"
        if "context-pack-2026-11-12" in p or "ctxpack" in p or p.rstrip("/").endswith("docs/paper"):
            return "1", "Grep over the pack (may print lines of the copy)"
        return "3", "Grep elsewhere"
    if tool == "Bash":
        cmd = inp.get("command", "")
        for m in re.finditer(r"^([^\n]*?)<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n(.*?)\n\2\b", cmd, flags=re.S | re.M):
            if re.search(r"\bpython3?\b|\buv run\b", m.group(1)) and re.search(r"open\(|read_text|readlines", m.group(3)):
                # a string literal that is a path to the note, s6.md or the pack (no spaces), not prose that names them
                if re.search(r"['\"][^'\"\s]*(RESUME\.md|s6\.md|context-pack-2026-11-12\.md)['\"]", m.group(3)):
                    return "1", "python fed a heredoc that opens a path to the note, s6.md or the pack (may print)"
        # other heredoc bodies are text written to a file or fed to a program, not reads of the named files
        body = re.sub(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n.*?\n\1\b", " ", cmd, flags=re.S)
        # redirect targets are writes
        body = re.sub(r"(?<![\w=<>!'\"])\d?>>?(?!=)&?\s*[^\s;|&)]+", " ", body)
        if not NAMES.search(body):
            return "3", "named only in a heredoc body or a redirect target"
        return bash_class(body)
    return "3", f"other tool {tool}"



NOTE = "docs/probe/20261111_reg19/ops/RESUME.md"
PACK = "docs/paper/context-pack-2026-11-12.md"
S6COPY = "docs/paper/ctxpack-2026-11-12/s6.md"
# The earliest each could be read (UTC): the note's Write (bc2fcf6d line 10376); for docs/paper, the birth time of the
# local s6.md copy (stat, 2026-11-12 18:08:00 UTC), earlier than the pack's (18:16:15) and its folder's (18:13:05).
BORN = {"docs/probe/20261111_reg19/ops/RESUME.md": "2026-11-12T15:53:29", PACK: "2026-11-12T18:08:00", S6COPY: "2026-11-12T18:08:00"}
REPO = "/Users/chalshik/Projects/aftershock-artifacts"
NOTE_COMMITS = {"54a995d": "2026-11-12T15:53:46", "da1f836": "2026-11-13T11:39:09"}  # git log -- NOTE (UTC)
EDIT_WINDOW = ("2026-11-13T11:38:32", "2026-11-13T11:39:09")  # the note edited in the tree, then committed in da1f836
_git_cache = {}


def _git(*args):
    if args not in _git_cache:
        _git_cache[args] = subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True).returncode
    return _git_cache[args]


def _norm(path, cwd):
    if not path.startswith("/") and cwd and cwd.startswith("/"):
        path = cwd.rstrip("/") + "/" + path
    if path.startswith(REPO):
        path = path[len(REPO):].lstrip("/")
    path = re.sub(r"^(\./)+", "", path).rstrip("/")
    return path or "."


CUR_TS = [""]


def _covers(path, cwd, which=None):
    """Does a path (a folder, a file or a glob) cover the note, the pack or the pack's local s6.md, and did that file
    exist at the time of the call (CUR_TS)?"""
    q = _norm(path, cwd)
    for f in which or (NOTE, PACK, S6COPY):
        if CUR_TS[0] and CUR_TS[0] < BORN[f]:
            continue
        if q == "." or f == q or f.startswith(q + "/") or (any(ch in q for ch in "*?[") and _glob(f, q)):
            return True
    return False


def _glob(path, pat):
    """A shell glob: `*` and `?` do not cross `/`; a folder that the glob names covers what is under it."""
    rx = "".join("[^/]*" if c == "*" else "[^/]" if c == "?" else re.escape(c) for c in pat)
    return re.fullmatch(rx + "(/.*)?", path) is not None


def _rev_ok(rev):
    return _git("rev-parse", "--verify", "--quiet", rev + "^{commit}") == 0


def _anc(a, b):
    return _git("merge-base", "--is-ancestor", a, b) == 0


def _git_class(w, cwd, ts):
    """git show / log / diff: does it print the note's text (a diff or a blob)?"""
    sub = w[1] if len(w) > 1 else ""
    args = w[2:]
    names_only = any(x in ("--stat", "--shortstat", "--numstat", "--name-only", "--name-status", "--quiet", "--exit-code", "--summary", "--oneline") or x.startswith(("--format", "--pretty")) and sub == "log" for x in args)
    if "--no-index" in args:
        return None
    if "--" in args:
        k = args.index("--"); toks, paths = [x for x in args[:k] if not x.startswith("-")], args[k + 1:]
    else:
        toks, paths = [x for x in args if not x.startswith("-")], []
    revs = []
    for x in toks:
        if re.fullmatch(r"\d+", x):
            continue
        if re.fullmatch(r"[0-9a-f]{7,40}|HEAD([~^]\d*)*|main|origin/main|[\w./~^-]*\.\.\.?[\w./~^-]*|[0-9a-f]{7,40}:.*", x) or _rev_ok(x):
            revs.append(x)
        else:
            paths.append(x)  # git treats a word that is not a revision as a path
    if paths and not any(_covers(x, cwd, (NOTE,)) for x in paths):
        return None
    if sub == "show":
        hit = [r for r in revs if any(r.startswith(c) for c in NOTE_COMMITS) or r.split(":")[0] in NOTE_COMMITS]
        if not hit:
            return None
        return ("3", "CL17: git show of a commit that holds the note, names or stats only") if names_only else ("1", "CL17: git show of a commit that holds the note (may print its diff)")
    if sub == "log":
        if not any(x in ("-p", "-u", "--patch", "--patch-with-stat") or re.fullmatch(r"-p\w*|-\w*p", x) for x in args):
            return None
        rng = [r for r in revs if ".." in r]
        if rng:
            a, b = rng[0].split("..", 1)
            b = b or "HEAD"
            if not (_rev_ok(a) and _rev_ok(b)):
                return ("1", f"CL17: git log -p over a range not resolved now ({rng[0]})")
            if not any(_anc(c, b) and not _anc(c, a) for c in NOTE_COMMITS):
                return None
        return ("3", "CL17: git log over the note's commits, names or stats only") if names_only else ("1", "CL17: git log -p whose range and paths cover a commit that holds the note")
    if sub == "diff":
        if names_only:
            return None
        rv = []
        for r in revs:
            rv += [x for x in r.split("..") if x] if ".." in r else [r]
        if len(rv) >= 2:
            a, b = rv[0], rv[1]
            if not (_rev_ok(a) and _rev_ok(b)):
                return ("1", f"CL17: git diff between revisions not resolved now ({a} {b})")
            return None if _git("diff", "--quiet", a, b, "--", NOTE) == 0 else ("1", f"CL17: git diff {a} {b} covers a change of the note")
        if len(rv) == 1:
            a = rv[0]
            if not _rev_ok(a) or "HEAD" in a or a in ("main", "origin/main"):
                return ("1", f"CL17: git diff against a revision not resolved for that time ({a}); may cover the note")
            for c, ct in NOTE_COMMITS.items():
                if ts >= ct and _anc(a, c) and not _anc(c, a):
                    return ("1", f"CL17: git diff {a} against the tree of that time covers {c}, a change of the note")
            if EDIT_WINDOW[0] <= ts <= EDIT_WINDOW[1]:
                return ("1", "CL17: git diff while the note's edit was uncommitted")
            return None
        if EDIT_WINDOW[0] <= ts <= EDIT_WINDOW[1]:
            return ("1", "CL17: git diff while the note's edit was uncommitted")
        return None
    return None


def wide_class(tool, inp, ts):
    """CL17's added rules; None if the input is not such a hit."""
    CUR_TS[0] = ts
    if tool == "Grep":
        path = inp.get("path") or REPO
        if not _covers(path, None):
            return None
        g, ty = inp.get("glob"), inp.get("type")
        if g and not (fnmatch.fnmatch("RESUME.md", g) or fnmatch.fnmatch(NOTE, g) or fnmatch.fnmatch("context-pack-2026-11-12.md", g)):
            return None
        if ty and ty not in ("md", "markdown"):
            return None
        mode = inp.get("output_mode") or "files_with_matches"
        return ("1", "CL17: Grep tool over a folder that holds the note or the pack, printing lines") if mode == "content" else ("3", f"CL17: Grep tool over such a folder, {mode} only")
    if tool != "Bash":
        return None
    cmd = inp.get("command", "")
    if not re.search(r"\bgrep\b|\brg\b|\bgit\b|[*?]", cmd):
        return None
    body = re.sub(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n.*?\n\1\b", " ", cmd, flags=re.S)
    body = re.sub(r"(?<![\w=<>!'\"])\d?>>?(?!=)&?\s*[^\s;|&)]+", " ", body)
    best = None
    for w, cwd in bash_segments(body):
        if not w:
            continue
        first = w[0]
        if first == "git" and len(w) > 1 and w[1] in ("show", "log", "diff"):
            r = _git_class(w, cwd, ts)
            if r and (best is None or r[0] < best[0]):
                best = r
            continue
        rec = first in ("rg",) or (first == "git" and len(w) > 1 and w[1] == "grep") or \
            (first in ("grep", "egrep") and any(re.fullmatch(r"-[a-zA-Z]*[rR][a-zA-Z]*|--recursive|--dereference-recursive", x) for x in w[1:]))
        if rec:
            args = w[2:] if first == "git" else w[1:]
            inc = [x.split("=", 1)[1] for x in args if x.startswith("--include=")]
            if inc and not any(fnmatch.fnmatch("RESUME.md", g) or fnmatch.fnmatch("context-pack-2026-11-12.md", g) for g in inc):
                continue
            if any(x in ("-t", "--type") for x in args):
                continue
            pos = [x for x in args if not x.startswith("-")]
            pos = pos[1:] if pos else pos
            paths = pos or ["."]
            if not any(_covers(x, cwd) for x in paths):
                continue
            only = any(re.fullmatch(r"-[a-zA-Z]*[lLcq][a-zA-Z]*|--files-with-matches|--count|--quiet|--files-without-match", x) for x in args)
            r = ("3", f"CL17: {first} recursive over a folder that holds the note or the pack, names or counts only") if only else \
                ("1", f"CL17: {first} recursive over a folder that holds the note or the pack (may print their lines)")
            if best is None or r[0] < best[0]:
                best = r
            continue
        if first in ("cat", "head", "tail", "sed", "awk", "less", "more", "nl"):
            globs = [x for x in w[1:] if any(ch in x for ch in "*?[") and not x.startswith("-")]
            if first in ("sed", "awk") and globs and globs[0] == next((x for x in w[1:] if not x.startswith("-")), None):
                globs = globs[1:]
            if any(_covers(x, cwd) for x in globs):
                r = ("1", f"CL17: {first} on a glob that covers the note or the pack")
                if best is None or r[0] < best[0]:
                    best = r
    return best


CL17_KEYS = set()
rows = []
for f in sorted(glob.glob(BASE + "*.jsonl") + glob.glob(BASE + "*/subagents/*.jsonl")):
    rel = f.replace(BASE, "")
    for i, l in enumerate(open(f, errors="replace"), 1):
        if not NAMES.search(l) and not WIDE.search(l):
            continue
        try:
            d = json.loads(l)
        except Exception:
            continue
        if d.get("type") != "assistant":
            continue
        m = d.get("message")
        if not isinstance(m, dict) or not isinstance(m.get("content"), list):
            continue
        for x in m["content"]:
            if not (isinstance(x, dict) and x.get("type") == "tool_use"):
                continue
            inp = x.get("input") or {}
            s = json.dumps(inp, ensure_ascii=False)
            key = f"{rel}:{i}"
            if NAMES.search(s):
                c, why = classify(x.get("name"), inp)
            else:
                wr = wide_class(x.get("name"), inp, d.get("timestamp") or "")
                if wr is None:
                    continue
                c, why = wr
            if not NAMES.search(s):
                CL17_KEYS.add(key)
            if key in labels:
                c, why = labels[key][0], "hand: " + labels[key][1]
            head = (inp.get("command") or inp.get("file_path") or inp.get("description") or s)[:200].replace("\n", " ").replace("\t", " ")
            rows.append((d.get("timestamp") or "-", key, x.get("name"), c, why, head))

rows.sort(key=lambda r: r[0])
n = {c: sum(1 for r in rows if r[3] == c) for c in "123"}
FRZ = "2026-11-13T10:40:28"
w17 = [r for r in rows if r[4].startswith("CL17") or (r[4].startswith("hand:") and r[1] in CL17_KEYS)]
print(f"# noteread: {len(rows)} hits; class 1: {n['1']}; class 2: {n['2']}; class 3: {n['3']}; hand labels: {len(labels)}")
print(f"# CL17 rules added {len(w17)} hits: before ffc76b3 {sum(r[0] < FRZ for r in w17)} (class 1: {sum(r[0] < FRZ and r[3] == '1' for r in w17)}), "
      f"after {sum(r[0] >= FRZ for r in w17)} (class 1: {sum(r[0] >= FRZ and r[3] == '1' for r in w17)})")
print("## first class, by time")
for r in rows:
    if r[3] == "1":
        print(" | ".join(r))
print("## every hit, by time")
for r in rows:
    print(" | ".join(r))
