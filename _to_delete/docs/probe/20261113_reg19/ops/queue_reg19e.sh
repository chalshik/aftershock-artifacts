#!/bin/zsh
# REG-19 queue, resume (decisions.md 2026-11-13 [DECISION] (delegate)): per seed in the registered order, control then
# burst (launch7.sh: pre-launch checks, launch, wait for checks.json); stops at the first launch STOP, lost tmux or
# invalid run (the rerun is decided from checks.json only). After each valid pair: copy both to the Mac, verify every
# file's sha256 against the VM, update the manifest, link the run folders into the pinned worktree, then
# `analysis.gate reg19_step` once FROM THE WORKTREE AT a7bb77a; only its `done` list and `continue` flag are printed.
# queue_reg19e = queue_reg19d with launch7.sh, the probe folder of 2026-11-13, and reg19_step run from the worktree.
# Usage (repo root, background): SEEDS="18 19" ATTEMPT_SEED=18 ATTEMPT=2 zsh docs/probe/20261113_reg19/ops/queue_reg19e.sh
S=/Users/chalshik/Projects/aftershock-artifacts/docs/probe/20261113_reg19/ops
R=/Users/chalshik/Projects/aftershock-artifacts
W=${REG19_WORKTREE:-/Users/chalshik/Projects/aftershock-reg19-pin}
PY=$R/.venv/bin/python
K=(-i $HOME/.ssh/id_ed25519_vllm -o BatchMode=yes -o ConnectTimeout=10); H=chalshik@${VM_HOST:-100.83.53.50}
cd $R
for sd in ${=SEEDS:-18 19}; do
  rids=()
  for kind in stage2_control burst; do
    cfg=${kind}_l1pl350cl_r2.0_w3000_s$sd
    if [[ $kind == stage2_control && $sd == ${ADOPT_SEED:-none} ]]; then  # adopt a finished control (checks.json valid) instead of rerunning
      rid=$ADOPT_RID; v=$(ssh $K $H "python3 -c \"import json;print(json.load(open('aftershock-artifacts/runs/$rid/checks.json'))['valid'])\"")
      [[ $v == True ]] || { echo "QUEUE STOP adopted $rid not valid ($v)"; exit 1; }
      echo "RUN $cfg $rid VALID (adopted)"; rids+=($rid); continue; fi
    out=$(PROBE_DIR=${PROBE_DIR19:-docs/probe/20261113_reg19} zsh $S/launch7.sh $cfg prelaunch_reg19_${cfg}_attempt$( [[ $sd == ${ATTEMPT_SEED:-none} && $kind == ${ATTEMPT_KIND:-stage2_control} ]] && echo ${ATTEMPT:-1} || echo 1 ).txt 2>&1); rc=$?
    echo "$out" > $S/queue19_$cfg.out
    rid=$(echo "$out" | sed -n 's/^LAUNCHED //p')
    chk=$(echo "$out" | grep "\[run\] checks" | tail -1)
    if (( rc != 0 )); then echo "QUEUE STOP $cfg rc=$rc rid=$rid: $(echo "$out" | grep -E 'STOP|TMUX' | tail -1)"; exit 1; fi
    if [[ $chk == *"'valid': True"* ]]; then echo "RUN $cfg $rid VALID"; else echo "RUN $cfg $rid INVALID"; echo "QUEUE STOP after invalid run"; exit 1; fi
    rids+=($rid)
  done
  for rid in $rids; do
    rsync -a -e "ssh ${K[*]}" ${H}:aftershock-artifacts/runs/$rid runs/ || { echo "QUEUE STOP copy failed $rid"; exit 1; }
    a=$(ssh $K $H "cd ~/aftershock-artifacts/runs/$rid && find . -type f | sort | xargs sha256sum" | sha256sum | cut -c1-16)
    b=$(cd runs/$rid && find . -type f | sort | xargs shasum -a 256 | sha256sum | cut -c1-16)
    [[ $a == $b ]] || { echo "QUEUE STOP checksum mismatch $rid"; exit 1; }
    echo "COPIED $rid sha-of-sums $a"
  done
  python3 tools/manifest.py update > /dev/null || { echo "QUEUE STOP manifest update failed"; exit 1; }
  for d in $R/runs/*(/); do n=${d:t}; [[ -e $W/runs/$n ]] || ln -s $d $W/runs/$n; done
  [[ $(git -C $W rev-parse --short HEAD) == ${PIN:-a7bb77a} && -z $(git -C $W status --short) ]] || { echo "QUEUE STOP worktree not clean at pin"; exit 1; }
  step=$(cd $W && $PY -m analysis.gate reg19_step 2>$S/reg19_step_err_s$sd.txt | tail -1)
  cont=$(echo "$step" | grep -o "'continue': [A-Za-z]*")
  echo "STEP after seed $sd: $(echo "$step" | grep -o "'done': \[[^]]*\]") $cont"
  [[ $cont == "'continue': True" ]] || { echo "QUEUE END (futility stop or all seeds done)"; exit 0; }
done
echo "QUEUE DONE"
