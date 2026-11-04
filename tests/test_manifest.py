"""tools/manifest.py on temporary folders (never on runs/)."""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import manifest as M  # noqa: E402


def make(tmp_path):
    runs = tmp_path / "runs"
    (runs / "20261101-000000_a").mkdir(parents=True)
    (runs / "20261101-000000_a" / "x.jsonl").write_text("one\n")
    (runs / ".gitkeep").write_text("")
    return runs, tmp_path / "m" / "runs.sha256"


def test_update_appends_only_new_files(tmp_path):
    runs, man = make(tmp_path)
    assert M.update(runs, man) == 0
    first = man.read_text()
    assert first.count("\n") == 1 and "  20261101-000000_a/x.jsonl" in first and ".gitkeep" not in first
    (runs / "20261102-000000_b").mkdir()
    (runs / "20261102-000000_b" / "y.json").write_text("{}")
    assert M.update(runs, man) == 0
    assert man.read_text().startswith(first) and man.read_text().count("\n") == 2


def test_update_refuses_a_changed_or_missing_file(tmp_path):
    runs, man = make(tmp_path)
    M.update(runs, man)
    before = man.read_text()
    (runs / "20261101-000000_a" / "x.jsonl").write_text("two\n")
    assert M.update(runs, man) == 1 and man.read_text() == before
    (runs / "20261101-000000_a" / "x.jsonl").unlink()
    assert M.update(runs, man) == 1 and man.read_text() == before


def test_verify_a_copy(tmp_path):
    runs, man = make(tmp_path)
    M.update(runs, man)
    copy = tmp_path / "backup"
    shutil.copytree(runs, copy)
    assert M.verify(copy, man) == 0
    (copy / "20261101-000000_a" / "x.jsonl").write_text("corrupt\n")
    assert M.verify(copy, man) == 1
    (copy / "20261101-000000_a" / "x.jsonl").unlink()
    assert M.verify(copy, man) == 1
