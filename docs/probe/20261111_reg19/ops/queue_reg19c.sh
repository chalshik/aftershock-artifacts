#!/bin/zsh
# REG-19 queue: per seed in the registered order, control then burst (launch5.sh: pre-launch checks, launch, wait for
# checks.json); stops at the first launch STOP, lost tmux or invalid run (the rerun is decided by hand from checks.json).
# After each valid pair: copy both to the Mac, verify every file's sha256 against the VM, update the manifest, then
# `analysis.gate reg19_step` once; only its `continue` flag is printed (no verdict, label or count).
S=/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/bc2fcf6d-b7b6-45b7-9398-2cecb62afb9a/scratchpad
R=/Users/chalshik/Projects/aftershock-artifacts
K=(-i $HOME/.ssh/id_ed25519_vllm -o ConnectTimeout=10); H=chalshik@100.83.53.50
cd $R
for sd in ${=SEEDS:-15 16 17 18 19}; do
  rids=()
  for kind in stage2_control burst; do
    cfg=${kind}_l1pl350cl_r2.0_w3000_s$sd
    if [[ $kind == stage2_control && $sd == ${ADOPT_SEED:-none} ]]; then  # adopt a finished control (checks.json valid) instead of rerunning
      rid=$ADOPT_RID; v=$(ssh $K $H "python3 -c \"import json;print(json.load(open('aftershock-artifacts/runs/$rid/checks.json'))['valid'])\"")
      [[ $v == True ]] || { echo "QUEUE STOP adopted $rid not valid ($v)"; exit 1; }
      echo "RUN $cfg $rid VALID (adopted)"; rids+=($rid); continue; fi
    out=$(PROBE_DIR=${PROBE_DIR19:-docs/probe/20261111_reg19} zsh $S/launch5.sh $cfg prelaunch_reg19_${cfg}_attempt${ATTEMPT:-1}.txt 2>&1); rc=$?
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
  step=$(uv run python -m analysis.gate reg19_step 2>$S/reg19_step_err_s$sd.txt | tail -1)
  cont=$(echo "$step" | grep -o "'continue': [A-Za-z]*")
  echo "STEP after seed $sd: $(echo "$step" | grep -o "'done': \[[^]]*\]") $cont"
  [[ $cont == "'continue': True" ]] || { echo "QUEUE END (futility stop or all seeds done)"; exit 0; }
done
echo "QUEUE DONE"
