#!/bin/zsh
# Moves the VM's tree from REG-19's pin to E1's registered commit. A separate step, run only with the owner's approval:
# it is the one E1 script that changes the VM's tree (no other one does). Usage, from the Mac:
#   zsh docs/probe/20261113_e1/ops/vm_checkout.sh
# Refuses (nothing changed): while e1_commit.txt says UNSET, or any Mac-side check fails (common.sh `mac_checks`);
# before the committed log records REG-19's queue end ('[OPS] REG-19: the queue ended') or its [RESULT], or while
# REG-19's queue lock exists (only its existence is tested; nothing under REG-19's state/ is opened); while E1's own
# queue lock exists; while the tmux session 'run' exists on the VM or a compute process is on the GPU; when the VM's
# tree is dirty, or its commit is not an ancestor of E1's commit on the Mac (a forward move only). Then, as
# agent/RUNBOOK.md section 4: push the Mac's main (which must hold E1's commit) to the VM's bare repository, fetch it on
# the VM and check out E1's commit, detached; read back the commit, the dirty count and uv.lock's blob, and run a
# dry-run `uv sync` (it must show no change). Everything goes to a time-stamped probe file. No root command, no run, no
# other change on the VM.
source ${0:A:h}/common.sh
die() { echo "STOP: $1"; echo "$ALLOWED"; exit ${2:-2}; }
mac_checks || die "$MSG"
ready_to_run || die "$MSG"
[[ ! -e $ST/queue.lock ]] || die "E1's queue lock exists ($ST/queue.lock): no checkout under a queue"
git -C $R merge-base --is-ancestor $E1 main || die "the registered commit $E1 is not on the Mac's main, which is what is pushed"
vm_tmux || die "$MSG"
(( ! TMUX_ON )) || die "the tmux session 'run' is alive on the VM: no checkout while a run may be in progress"
apps=$(ssh $K $H "nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l") || die "the VM could not be read (compute apps)"
[[ ${apps// /} == 0 ]] || die "a compute process is on the GPU ('$apps')"
before=$(ssh $K $H "cd ~/aftershock-artifacts && git rev-parse HEAD && git status --short | wc -l") || die "the VM's tree could not be read"
vh=${${(f)before}[1]}; vd=${${(f)before}[2]// /}
[[ $vd == 0 ]] || die "the VM's tree is dirty ($vd entries): the owner decides"
mkdir -p $PROBE_DIR
stamp; out=$PROBE_DIR/vm_checkout_$REPLY.txt
[[ ! -e $out ]] || die "$out exists"
print -r -l -- "# E1: vm_checkout (agent, with the owner's approval). scripts $SC; Mac HEAD $(git -C $R rev-parse HEAD); registered commit $E1" "before $vh dirty $vd" > $out
if [[ $vh == $E1 ]]; then echo "already_at_e1" >> $out; cat $out; echo "VM ALREADY AT $E1, clean"; exit 0; fi
git -C $R cat-file -e "${vh}^{commit}" 2> /dev/null && git -C $R merge-base --is-ancestor $vh $E1 || die "the VM's commit '$vh' is not an ancestor of $E1 on the Mac (a forward move only): the owner decides"
GIT_SSH_COMMAND="ssh ${K[*]}" git -C $R push $VM_GIT main >> $out 2>&1 || die "git push of main to the VM's bare repository failed (see ${out:t})"
ssh $K $H "cd ~/aftershock-artifacts && git fetch -q origin && git checkout -q --detach $E1 && echo \"head \$(git rev-parse HEAD)\" && echo \"dirty \$(git status --short | wc -l)\" && echo \"lock_blob \$(git hash-object uv.lock)\"" >> $out 2>&1 || die "the fetch or checkout on the VM failed (see ${out:t})"
dry=$(ssh $K $H "cd ~/aftershock-artifacts && ~/.local/bin/uv sync --frozen --extra server --dry-run 2>&1") || die "the VM's dry-run sync failed"
n_chg=$(print -r -- "$dry" | grep -c '^ [-+~] ')
print -r -l -- "# uv sync --frozen --extra server --dry-run on the VM:" "$dry" "uv_changes $n_chg" >> $out
cat $out
[[ $(grep '^head ' $out | awk '{print $2}') == $E1 && $(grep '^dirty ' $out | awk '{print $2}') == 0 ]] || die "the VM's tree is not the registered commit, clean, after the checkout (see ${out:t})"
[[ $(grep '^lock_blob ' $out | awk '{print $2}') == $(git -C $R rev-parse ${E1}:uv.lock) ]] || die "the VM's uv.lock is not the registered commit's after the checkout"
[[ $n_chg == 0 ]] || die "the dry-run sync on the VM would change $n_chg packages: the owner decides before any run"
echo "VM AT $E1, clean; uv.lock the registered commit's; next: session_probe.sh (RENEW=1 only with a decisions.md entry)"
