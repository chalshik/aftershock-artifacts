"""The files REG-21's and REG-22's freeze covers: the import closure of a module in this repository, with Python's `ast`.

    python3 docs/probe/20261113_freeze/closure.py analysis/k3w.py     # REG-21
    python3 docs/probe/20261113_freeze/closure.py analysis/c2.py      # REG-22
    python3 docs/probe/20261113_freeze/closure.py --at <commit> analysis/k3w.py   # the files as they are at <commit>

Written 2026-11-13 for the owner-proxy's BF2 and BH2 and rule F's BE2 and BG2 (docs/drafts/reviews-2026-11-13/): "the
closure is computed at E by a committed script whose verbatim output the [DECISION] (delegate) quotes".

What it counts. Every `import X` and `from X import Y` anywhere in a file (module level, inside functions, inside
`if`/`try`), relative imports resolved against the file's package. A name resolves to a file of this repository if
`X.py` or `X/__init__.py` exists; for `from X import Y` it also tries the submodule `X/Y.py` or `X/Y/__init__.py`
(`from analysis import k3` imports analysis/k3.py), and every package `__init__.py` on the way is counted, since Python
runs it. Names outside the repository (numpy, pandas, yaml, the standard library) are not followed; the environment is
fixed by the three files printed after the closure: `.python-version`, `pyproject.toml`, `uv.lock`.

What it cannot see: an import built at run time (`importlib.import_module(name)`, `__import__`), code run by `exec`, and
a file outside the repository that shadows a repository module (a site-packages module of the same name). It prints
any `importlib`/`__import__` call it finds in the closure so that a reader can check it by hand.
"""
import ast
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ENV_FILES = [".python-version", "pyproject.toml", "uv.lock"]


def read(rel, at):
    if at is None:
        p = REPO / rel
        return p.read_text() if p.is_file() else None
    r = subprocess.run(["git", "-C", str(REPO), "show", f"{at}:{rel}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def exists(rel, at):
    return read(rel, at) is not None


def module_file(mod, at):
    """The repository file for a dotted module name, or None."""
    base = mod.replace(".", "/")
    for cand in (f"{base}.py", f"{base}/__init__.py"):
        if exists(cand, at):
            return cand
    return None


def packages_on_the_way(mod, at):
    parts = mod.split(".")
    out = []
    for i in range(1, len(parts)):
        f = f"{'/'.join(parts[:i])}/__init__.py"
        if exists(f, at):
            out.append(f)
    return out


def package_of(rel):
    parts = rel[:-3].split("/")
    if parts[-1] == "__init__":
        return ".".join(parts[:-1])
    return ".".join(parts[:-1])


def imports(rel, src):
    tree = ast.parse(src, filename=rel)
    pkg = package_of(rel)
    found, dynamic = [], []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                found.append((a.name, None))
        elif isinstance(n, ast.ImportFrom):
            if n.level:
                base = pkg.split(".") if pkg else []
                base = base[: len(base) - (n.level - 1)] if n.level > 1 else base
                mod = ".".join(base + ([n.module] if n.module else []))
            else:
                mod = n.module or ""
            for a in n.names:
                found.append((mod, a.name))
        elif isinstance(n, ast.Call):
            f = n.func
            name = f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else ""
            if name in ("import_module", "__import__"):
                dynamic.append(n.lineno)
    return found, dynamic


def closure(start, at=None):
    todo, seen, dyn = [start], set(), {}
    while todo:
        rel = todo.pop()
        if rel in seen:
            continue
        src = read(rel, at)
        if src is None:
            continue
        seen.add(rel)
        found, dynamic = imports(rel, src)
        if dynamic:
            dyn[rel] = dynamic
        for mod, name in found:
            if not mod:
                continue
            hits = []
            f = module_file(mod, at)
            if f:
                hits.append(f)
                hits += packages_on_the_way(mod, at)
            if name and name != "*":
                g = module_file(f"{mod}.{name}", at)
                if g:
                    hits.append(g)
                    hits += packages_on_the_way(f"{mod}.{name}", at)
            todo += [h for h in hits if h not in seen]
    return sorted(seen), dyn


def main(argv):
    at = None
    if argv[:1] == ["--at"]:
        at, argv = argv[1], argv[2:]
    start = argv[0]
    files, dyn = closure(start, at)
    print(f"# import closure of {start}" + (f" at {at}" if at else " in the working tree") + f": {len(files)} .py files")
    for f in files:
        print(f)
    print(f"# environment: {len(ENV_FILES)} files")
    for f in ENV_FILES:
        print(f + ("" if exists(f, at) else "   (MISSING)"))
    print(f"# total {len(files) + len(ENV_FILES)} files")
    for f, lines in sorted(dyn.items()):
        print(f"# dynamic import call in {f} at line(s) {', '.join(map(str, lines))}: check by hand")


if __name__ == "__main__":
    main(sys.argv[1:])
