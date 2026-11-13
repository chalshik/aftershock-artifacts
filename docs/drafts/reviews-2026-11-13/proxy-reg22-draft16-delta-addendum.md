# proxy-reg22-draft16-delta-addendum (proxy-reg22-d16), verbatim

Saved by the agent from the teammate message received in the main session transcript (message timestamp 2026-11-13T17:12:12.526Z; message 2 of 2 from this teammate). Addendum: BL2a, BL3a.

---

Addendum to the owner-proxy verdict on REG-22 draft 16 (round 3 on the freeze), answering the two messages on the [CORR] at decisions.md:4453 and on the agent's reading of D16:80. Save it after the verdict, verbatim.

**The decision is unchanged: APPROVE on BL1–BL4.**
- My verdict already took the [CORR] into account. Before sending it I found d960ef3 (:4453) and f3abd23 (`agent/STATE.md`) in git.
- **The agent's reading of D16:80: accepted.** This is my BL1, for the reasons given there:
  - D16 lists s57_inv.py's read as "names, configs, validity and sizes". The `no_errors` counts in seed 17's burst `checks.json` are lines that run wrote after its burst began, and they are beyond that listing.
  - A listing that misstates what a look read cannot cover the look.
  - So batch 2 is labelled retrospective (by design) from the entry, and batch 1 is registered as the primary analysis.

**Item (x).**
- D16 numbers its reads (i) and (ii) only. In REG-22 the item is my BL2(a)'s read (iii), and BL2(a)'s replacement text is the text I want.
- If the next draft numbers it (x) to match REG-21, the numbering is wording and needs no pass:
  - replace "(iii)" with "(x)" throughout BL1 and BL2;
  - replace BL2(c)'s "(i) to (iii)" with the draft's own range.
- REG-21's items (iii) and (viii) are not REG-22's. For REG-22:
  - the 17:56:24 `ls` is already in BL2(a);
  - the 300 characters are already in BL2(b).

**BL2a (BEFORE; class: a disclosure). The control side, from the agent's point that the control's counts bear on condition 4's control side.**
(a) In BL2(a)'s replacement text, directly after
`` `ok` over the run's length is its mean completion rate (DERIVED).``
insert
` Seed 17's control's counts, from the same print, bear on batch 2's control readout, which reports the same-seed control's values beside each run; the trigger above concerns burst runs only, so for the control this read is a disclosure.`
(b) In BL2(b)'s replacement text, replace
`: a control's counts, not a burst run's)`
with
`: a control's counts, which bear on batch 2's control readout, not on a burst run's label)`

**BL3a (BEFORE; class: a stricter rule. It tells how the agent's classification meets BL3.)** The labels in `labels.tsv` and `classify2.py` meet BL3(b) under this mapping:
- `disclosed(<item>)`, `disclosed_BJ3` and `disclosed_smoke_test` = listed.
- `non_reg19_run` and `before_reg19_folders` = not REG-19.
- `config_only` and `names_only` = listed, when the folder is a REG-19 folder; otherwise not REG-19.
- `synthetic` = synthetic.
- `excludes_runs` = excluded.
- `false_positive` and `denied_never_ran` = no read. The note must say why.
- The rule labels `names_in_text`, `code_text`, `own_tools`, `reg19_scripts` and `no_run_read` = no read.
- **One limit on the rule label `names_or_validity`.** It stands only where the command takes `valid` or `failed` (or the file's existence) from `checks.json`. A command that prints `checks.json` any other way is labelled by hand by reading its input: `cat`, `head`, `tail`, `less`, `jq` beyond those two fields, or python that prints another field.
- **The floor.** classify2's floor, 2026-11-11 17:15:21 UTC, may replace BL3(b)'s 2026-11-11 00:00 UTC. No REG-19 folder existed before 2026-11-12 05:09:20 UTC: the first folder's name is `20261112-050920`.
- **BL4 item 4.** The [DECISION] (delegate) may cite `labels.tsv` and the classify2 output at their commit instead of listing every hit, if each hit has one line there with its transcript file, line and class.

**What I checked for this addendum** (tool-call inputs only; I opened no output):
- **Every Bash input since 2026-11-12 05:09 UTC that names `checks.json` together with a path into `runs/`:** 60 distinct commands. Only two print a REG-19 `checks.json` beyond `valid` and `failed`, and both are known (DERIVED from the inputs):
  - the `head -c 300` of 11:50:49 UTC, read (i);
  - s57_inv.py at 17:59:38 UTC.
  The other commands take `valid` and/or `failed`, or test that the file exists. Examples: `agent-a625ca98c29ea904b` line 308 prints `failed`, because `checks` is a list; session d4d16c2c at 10:30 UTC and session fdf13821 at 13:58 and 15:49 UTC print `valid` only.
- **The REG-21 review session's script of 2026-11-13 16:43:34 UTC** (session 9aa8df0a, line 749). It holds s57_inv.py's loop as a string passed to search2's classifier and never executed: synthetic.

**Which later changes need another proxy pass:** as in the verdict.
- No pass for BL2a and BL3a written as given, or for the (iii)/(x) renumbering.
- A pass if the classify2 output has any `UNLABELLED` hit, or any hit whose label falls outside BL3a's mapping, at E.

**Not checked:** the classify2 and search2 outputs at 163634Z, which I did not open. So I have not checked the claim that no hit is unlabelled.
