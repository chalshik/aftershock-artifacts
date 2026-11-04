"""tools/check_docs.py: unit tests on small fixtures, then the real repo (CLAUDE.md rule I)."""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import check_docs as C  # noqa: E402
import context_pack  # noqa: E402

A, B = "20261102-053935_wipe_preempt_r3_s2", "20261101-182452_stage2_control_cap_r3"
STATE = {A: "VALID", B: "INVALID", "20261031-025032_tau": "NOCHECKS"}


def test_claims_read_the_clause_after_each_id():
    text = f"`{A}` is VALID; `{B}` is INVALID on heat.\n| 1 | `{B}` | INVALID (`gpu_steady`) |\nall 2 VALID: `{A}`, `{A}`"
    assert [c for _, _, c in C.claims(text)] == ["VALID", "INVALID", "INVALID", "VALID", "VALID"]


def test_a_wrong_validity_claim_and_an_unknown_run_fail():
    errs = C.check_runs({"d.md": f"`{A}` is INVALID. `20261199-000000_nope` ran."}, STATE)
    assert len(errs) == 2 and "validity" in errs[0] and "run_ids" in errs[1]


def test_no_checks_counts_as_invalid_claim():
    assert C.check_runs({"d.md": "`20261031-025032_tau` is INVALID"}, STATE) == []


def test_inventory_counts_and_lists():
    good = (f"3 run folders: 1 VALID, 1 INVALID, 1 without checks\n- **Invalid, Stage 2:** `{B}`\n"
            "- **No checks:** `20261031-025032_tau`\n")
    assert C.check_inventory(good, STATE) == []
    assert len(C.check_inventory(good.replace(f"`{B}`", ""), STATE)) == 1


def test_tags_required_from_the_first_tagged_entry():
    old = "## 2026-10-01 · untagged old entry\nx\n"
    assert C.check_tags(old) == []
    assert C.check_tags(old + "## 2026-11-05 · [DECISION] a\nx\n## 2026-11-05 · no tag\n")  # error
    assert C.check_tags(old + "## 2026-11-05 · [RESULT] r\nno run cited\n")
    assert C.check_tags(old + f"## 2026-11-05 · [RESULT] r\nRUN({A}, load.verdict)\n") == []


def test_file_refs(tmp_path):
    assert C.check_file_refs({"d.md": "FILE(analysis/load.py:1)"}) == []
    assert C.check_file_refs({"d.md": "FILE(analysis/load.py:99999)"})
    assert C.check_file_refs({"d.md": "FILE(no/such.py:1)"})


def test_context_pack_is_deterministic_and_digest_fits_the_hook_limit():
    assert context_pack.build() == context_pack.build()
    assert len(context_pack.digest()) <= context_pack.DIGEST_MAX


def test_the_repo_passes(capsys):
    """The real docs, git history and run folders. Run checks are skipped where runs/ is empty (the VM)."""
    code = C.main(["--runs-dir", str(REPO / "runs")])
    assert code == 0, capsys.readouterr().out


def test_pending_copy_ids_are_accepted_until_copied():
    vm_only = "20261104-134159_long_pc_off_r3_s0"
    assert C.check_runs({"d.md": f"`{vm_only}` ran"}, STATE, {vm_only}) == []
    assert C.check_runs({"d.md": f"`{vm_only}` ran"}, STATE) != []
    assert C.check_runs({}, {**STATE, vm_only: "NOCHECKS"}, {vm_only})  # copied but still listed: error
