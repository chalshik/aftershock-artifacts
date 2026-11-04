"""Checksum manifest of the raw data: manifests/runs.sha256, committed, append-only. Stdlib only.

    python3 tools/manifest.py update [--runs-dir runs]   # append lines for files not yet in the manifest
    python3 tools/manifest.py verify <copy_dir>          # check a copy (a backup of runs/) against the manifest

Format: one line per file, `<sha256>  <run_id>/<path>`, paths relative to the runs directory, sorted within each
append. It is the `sha256sum` format, so `cd <copy_dir> && shasum -a 256 -c <repo>/manifests/runs.sha256` checks
the same thing without this script.

Append-only: `update` never changes or removes a line. If a file already listed now has a different hash, or a
listed file is gone, it stops with an error and writes nothing: raw data is immutable (CLAUDE.md rule 4), so that is
damage to investigate, not an update. `tools/check_docs.py` checks that every committed version of the manifest
extends the one before it.
"""
import argparse
import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "manifests" / "runs.sha256"
CHUNK = 1 << 20


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while b := f.read(CHUNK):
            h.update(b)
    return h.hexdigest()


def read(manifest: Path = MANIFEST) -> dict[str, str]:
    """relative path -> hash. A path listed twice is an error."""
    out = {}
    if not manifest.exists():
        return out
    for n, line in enumerate(manifest.read_text().splitlines(), 1):
        if not line.strip():
            continue
        digest, rel = line.split("  ", 1)
        if rel in out:
            raise SystemExit(f"{manifest}:{n}: {rel} is listed twice")
        out[rel] = digest
    return out


def files(runs: Path) -> list[str]:
    """Every regular file under the run folders, as relative paths. Hidden files at the top (.gitkeep) are skipped."""
    return sorted(str(p.relative_to(runs)) for p in runs.rglob("*")
                  if p.is_file() and not p.relative_to(runs).parts[0].startswith("."))


def update(runs: Path, manifest: Path = MANIFEST) -> int:
    known = read(manifest)
    present = set(files(runs))
    gone = sorted(set(known) - present)
    if gone:
        print(f"ERROR: {len(gone)} listed files are missing from {runs}, e.g. {gone[:3]}. Nothing written.")
        return 1
    changed = [rel for rel in sorted(known) if sha256(runs / rel) != known[rel]]
    if changed:
        print(f"ERROR: {len(changed)} listed files changed since they were recorded, e.g. {changed[:3]}. Nothing written.")
        return 1
    new = sorted(present - set(known))
    manifest.parent.mkdir(exist_ok=True)
    with open(manifest, "a") as f:
        for rel in new:
            f.write(f"{sha256(runs / rel)}  {rel}\n")
    print(f"manifest: {len(known)} files already listed and unchanged; {len(new)} appended")
    return 0


def verify(copy: Path, manifest: Path = MANIFEST) -> int:
    known = read(manifest)
    missing = [rel for rel in known if not (copy / rel).is_file()]
    bad = [rel for rel in known if rel not in missing and sha256(copy / rel) != known[rel]]
    extra = sorted(set(files(copy)) - set(known))
    for label, items in (("missing", missing), ("different", bad), ("not in manifest", extra)):
        for rel in items[:20]:
            print(f"{label}: {rel}")
    print(f"verify {copy}: {len(known)} listed, {len(missing)} missing, {len(bad)} different, "
          f"{len(extra)} not in the manifest -> {'OK' if not (missing or bad) else 'FAIL'}")
    return 1 if missing or bad else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    u = sub.add_parser("update")
    u.add_argument("--runs-dir", type=Path, default=REPO / "runs")
    v = sub.add_parser("verify")
    v.add_argument("copy", type=Path)
    a = ap.parse_args(argv)
    return update(a.runs_dir) if a.cmd == "update" else verify(a.copy)


if __name__ == "__main__":
    sys.exit(main())
