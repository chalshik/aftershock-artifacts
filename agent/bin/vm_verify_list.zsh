#!/bin/zsh
# List the VM's run folders whose every file is in manifests/runs.sha256 with an equal sha256, on the VM and on the
# Mac. Read-only on both sides: it hashes files and lists names; it opens no file for its content, prints no value
# from a run, and removes nothing. It is the input for the owner's choice of VM copies to remove under rule 4's
# exception (decisions.md 2026-11-04; agent/FOR_AUTHOR.md -20). Run it only when no queue is running on the VM
# (hashing loads the VM's CPU and disk).
#
# Folders matching a sealed pattern (the list below; analysis/withheld.py holds the seals in force) are skipped by
# name before anything else is done with them: no size, no hash, no file list.
#
# usage: zsh agent/bin/vm_verify_list.zsh            # prints to stdout
# env:   VM_HOST (default 100.83.53.50), VM_RUNS (default ~/aftershock-artifacts/runs on the VM),
#        REMOTE_CMD (default: ssh to VM_HOST; tests set "sh -c"), MAC_RUNS (default <repo>/runs),
#        MANIFEST (default <repo>/manifests/runs.sha256)
# Output, one line per VM folder:  <name> <STATUS> [vm_kB=<n>] [files=<n>] [<detail>]
#   VERIFIED            every VM file is listed, every listed file is on the VM, hashes equal on VM and Mac
#   SKIP_SEALED         name matches a sealed pattern
#   NOT_IN_MANIFEST     no manifest line for the folder
#   MISMATCH            file lists differ, or a hash differs on either side (detail says which)
# Last line: SUMMARY verified=<n> verified_kB=<n> other=<n> sealed=<n>
set -u
REPO=${0:A:h:h:h}
VM_HOST=${VM_HOST:-100.83.53.50}
VM_RUNS=${VM_RUNS:-'~/aftershock-artifacts/runs'}
MAC_RUNS=${MAC_RUNS:-$REPO/runs}
MANIFEST=${MANIFEST:-$REPO/manifests/runs.sha256}
if [[ -n ${REMOTE_CMD:-} ]]; then
  remote=(${=REMOTE_CMD})
else
  remote=(ssh -i ~/.ssh/id_ed25519_vllm -o BatchMode=yes -o ConnectTimeout=10 chalshik@$VM_HOST)
fi
# Sealed run-name patterns (REG-20 arm A and its drift run, E1/E0's cache-off sweeps, D1's capped runs).
SEALED_RE='_l1pl350ol_r2\.[05]_w3000_s1[5-9]$|_burst_l1pl350cl_r2\.0_w3000_s15_drift$|_sweep_l1pl350cl_pc_off_r|_sweep_l1t16pl350cl_pc_o.*_r|_burst_l1pl350cl_r2\.0_w3000_s1[5-9]_cap$'
SHA_REMOTE='if command -v sha256sum >/dev/null; then sha256sum -c --quiet --strict -; else shasum -a 256 -c --quiet -; fi'
SHA_MAC='shasum -a 256 -c --quiet -'

names=$($remote "ls -1 $VM_RUNS") || { echo "ERROR: cannot list $VM_RUNS on the VM"; exit 2; }
# Second guard: every name that analysis/withheld.py still seals (AFTERSHOCK_UNSEAL removed from the environment).
sealed_now=$(print -r -- "$names" | env -u AFTERSHOCK_UNSEAL python3 -I -c '
import importlib.util, sys
spec = importlib.util.spec_from_file_location("withheld", sys.argv[1]); w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)
for n in sys.stdin.read().split():
    if w.sealed_by(n): print(n)
' "$REPO/analysis/withheld.py") || { echo "ERROR: analysis/withheld.py could not be evaluated"; exit 2; }
nv=0; nk=0; no=0; ns=0
for n in ${(f)names}; do
  [[ -z $n ]] && continue
  if print -r -- "$n" | grep -Eq "$SEALED_RE" || print -r -- "$sealed_now" | grep -Fxq -- "$n"; then
    echo "$n SKIP_SEALED"; (( ns++ )); continue
  fi
  lines=$(grep -F "  $n/" "$MANIFEST")
  if [[ -z $lines ]]; then echo "$n NOT_IN_MANIFEST"; (( no++ )); continue; fi
  want=$(print -r -- "$lines" | sed 's/^[0-9a-f]\{64\}  //' | LC_ALL=C sort)
  have=$($remote "cd $VM_RUNS && find '$n' -type f | LC_ALL=C sort")
  kb=$($remote "cd $VM_RUNS && du -sk '$n' | cut -f1")
  nf=$(print -r -- "$want" | wc -l | tr -d ' ')
  if [[ $want != $have ]]; then
    extra=$(comm -13 <(print -r -- "$want") <(print -r -- "$have") | wc -l | tr -d ' ')
    missing=$(comm -23 <(print -r -- "$want") <(print -r -- "$have") | wc -l | tr -d ' ')
    echo "$n MISMATCH vm_kB=$kb files=$nf lists_differ vm_extra=$extra vm_missing=$missing"; (( no++ )); continue
  fi
  if ! print -r -- "$lines" | $remote "cd $VM_RUNS && $SHA_REMOTE" >/dev/null 2>&1; then
    echo "$n MISMATCH vm_kB=$kb files=$nf vm_hash"; (( no++ )); continue
  fi
  if ! (cd "$MAC_RUNS" && print -r -- "$lines" | eval "$SHA_MAC" >/dev/null 2>&1); then
    echo "$n MISMATCH vm_kB=$kb files=$nf mac_hash"; (( no++ )); continue
  fi
  echo "$n VERIFIED vm_kB=$kb files=$nf"; (( nv++ )); (( nk += kb ))
done
echo "SUMMARY verified=$nv verified_kB=$nk other=$no sealed=$ns"
