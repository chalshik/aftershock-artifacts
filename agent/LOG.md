# LOG (append-only)

One block per work block: what was done, what was found, the commit.

## 2026-11-13, block 1 (session 8c5f8396): start, first actions

**Done**
- Read `docs/FABLE_PROMPT.md`. `git log -5`, `git status`: HEAD `9958414`, dirty `.gitignore` (the owner's, left alone) and `docs/decisions.md` (the delegation entry, uncommitted).
- No other Claude process has this repo as its working folder (four other `claude` processes: `tam-sat` ×2, `cocobolo` ×2; OBSERVED via `lsof -d cwd`).
- Delegation entry: found uncommitted and without `## `; marker and line breaks added, words unchanged; committed with an [OPS] entry.
- S1: 31 draft files copied byte for byte into `docs/drafts/scratchpad-2026-11-12/`. Papers (5 PDFs + text), Schroeder 2006 and others from a second scratchpad, and the snapshot's 61 section files copied into `docs/paper/` (local).
- S2: `git init` in `docs/paper/`, `.gitignore` for `pdfs/`, `paper-text/`, `*.pdf`; first commit `3e41741`.
- S3 started: `rsync` of `runs/` to `/Users/chalshik/aftershock-backups/runs-2026-11-13`, then `tools/manifest.py verify` (background).
- Read in full: `PROTOCOL.md`, `docs/process.md`, `docs/claims.md`, `docs/status.md`, `docs/definitions.md`, `docs/model.md`, `docs/experiment-plan.md` (the "Stage 2, revised" section, lines 350–481), `docs/open-questions.md` (source questions and A1–A17), `docs/probe/20261111_reg19/ops/RESUME.md`; the pack's §0, §6.0, §6.20, §10.3–10.5, §12.1–12.5, §13, §14.

**Found**
- The pack is at `docs/paper/context-pack-2026-11-12.md`, not at the path the start prompt names.
- `PAPERS_DIR` and `DRIVE_COPIES` were left as placeholders. Papers found in scratchpads; Drive copies not found (searched the mounted Drive folder to depth 8 and the home folder to depth 6 for `context-alignment*`, `paper-plan*`, `related-work*`).
- No external volume is mounted (`/Volumes`: Macintosh HD, Recovery). 120 GiB free.
- The VM is offline on Tailscale.
- `docs/claims.md` K4 still says "0.41–0.51 of the warm peak" (line 77); the 2026-11-12 [CORR] fixed 0.43–0.52 against 3.15 only in the local paper files. Added to Z6a.
- `check_docs` failed at session start only on the stale context pack (the uncommitted delegation text); passes after regeneration.

**Commit:** `c94a77d` (main repo); `3e41741` (docs/paper inner repo).
