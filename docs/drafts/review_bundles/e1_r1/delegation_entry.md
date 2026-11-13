<!-- docs/decisions.md lines 4231-4238 -->
## 2026-11-13 · [DECISION] Owner delegates approvals to the autonomous agent while the owner is unavailable
Owner, verbatim: "it should never depend on me ... it should run end to end, GPU can return at any time ... I allow it run sudo to set power limit".
From this entry on, the autonomous agent (Fable, run in this repo) may give the approvals that CLAUDE.md rule C reserves for the owner, for: registrations and GPU runs; reruns under registered stopping rules; the REG-19 resume decisions (seed-18 control rerun as attempt 2, the pin rule); new configs (as new files); analysis-only registrations; corrections of stale docs; and changes to paper claims or their status in docs/claims.md and docs/paper/.
Each such approval is its own [DECISION] entry tagged "(delegate)", written only after (a) the rule F review by a separate subagent, recorded verbatim in the [REG], and (b) an independent owner-proxy subagent's approval; a reject from either is binding.
Not delegated: editing runs/, a used config or an old decisions.md entry; choosing or widening a threshold after seeing the data it judges (rule A5); reading outcome data a pending registration withholds; deleting anything; vLLM or uv.lock changes; any root action other than sudo -n nvidia-smi -pl 350 on the VM; posting or uploading anything outside this machine and the VM.
The owner may overrule any delegate decision later with a [CORR] or [DECISION] entry.
Ends when the owner writes an entry ending it.
