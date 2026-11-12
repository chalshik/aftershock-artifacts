#!/bin/zsh
# REG-19 queue, resume (decisions.md 2026-11-13 [DECISION] (delegate)). Per seed in the registered order: control, then
# burst (launch8.sh), each once; then both folders copied to the Mac and every file's sha256 compared with the VM's; the
# manifest appended; the REG-19 folders linked into the worktree at the pin and the links verified; then
# `analysis.gate reg19_step` once, FROM THE WORKTREE. Only its `done` list and `continue` flag are printed.
# It stops, with a non-zero exit, at: a failed check, a lost or invalid run (the rerun is decided from checks.json only),
# a copy or checksum failure, a link that is missing or points elsewhere, a step that fails or prints no flag, or a
# `done` list that is not exactly 15..<the seed just run>. "QUEUE END futility stop" is printed only on 'continue': False.
# Usage (repo root, in the background):
#   SEEDS="18 19" ATTEMPT_SEED=18 ATTEMPT_KIND=stage2_control ATTEMPT=2 zsh docs/probe/20261113_reg19/ops/queue_reg19f.sh
# Recovery after a stop that left a valid, uncopied run: ADOPT_SEED=<seed> ADOPT_CONTROL_RID=<id> and/or
# ADOPT_BURST_RID=<id> adopt it (its checks.json must say valid) instead of launching that run again.
# STEP_ONLY=1 SEEDS=<seed>: no launch and no copy; link, verify and step for a pair that is already on the Mac.
source ${0:A:h}/common.sh
mac_checks || exit 2
ATT=${ATTEMPT:-1}; AK=${ATTEMPT_KIND:-stage2_control}
[[ $ATT == [123] ]] || { echo "QUEUE STOP: ATTEMPT must be 1, 2 or 3"; exit 2; }
[[ $AK == stage2_control || $AK == burst ]] || { echo "QUEUE STOP: ATTEMPT_KIND must be stage2_control or burst"; exit 2; }
for sd in ${=SEEDS:-18 19}; do [[ $sd == 18 || $sd == 19 ]] || { echo "QUEUE STOP: only seeds 18 and 19 are left"; exit 2; }; done
echo "QUEUE START seeds=${SEEDS:-18 19} attempt=$ATT of $AK for seed ${ATTEMPT_SEED:-none}; scripts $SC; pin $PIN"
cd $R
for sd in ${=SEEDS:-18 19}; do
  rids=()
  if [[ -z $STEP_ONLY ]]; then
    for kind in stage2_control burst; do
      cfg=${kind}_l1pl350cl_r2.0_w3000_s$sd
      a=1; [[ $sd == ${ATTEMPT_SEED:-none} && $kind == $AK ]] && a=$ATT
      adopt=""
      [[ $sd == ${ADOPT_SEED:-none} && $kind == stage2_control ]] && adopt=$ADOPT_CONTROL_RID
      [[ $sd == ${ADOPT_SEED:-none} && $kind == burst ]] && adopt=$ADOPT_BURST_RID
      if [[ -n $adopt ]]; then
        [[ $adopt == *_${cfg} ]] || { echo "QUEUE STOP adopted $adopt is not a run of $cfg"; exit 1; }
        v=$(ssh $K $H "python3 -c \"import json;print(json.load(open('aftershock-artifacts/runs/$adopt/checks.json'))['valid'])\"")
        [[ $v == True ]] || { echo "QUEUE STOP adopted $adopt not valid ($v)"; exit 1; }
        echo "RUN $cfg $adopt VALID (adopted)"; rids+=($adopt); continue
      fi
      outf=$S/queue19_${cfg}_attempt$a.out
      [[ ! -e $outf ]] || { echo "QUEUE STOP $outf exists: this attempt was already launched"; exit 1; }
      out=$(zsh $S/launch8.sh $cfg prelaunch_reg19_${cfg}_attempt$a.txt 2>&1); rc=$?
      echo "$out" > $outf
      rid=$(echo "$out" | sed -n 's/^LAUNCHED //p')
      chk=$(echo "$out" | grep "\[run\] checks" | tail -1)
      if (( rc != 0 )); then echo "QUEUE STOP $cfg rc=$rc rid=$rid: $(echo "$out" | grep -E 'STOP|TMUX|STILL' | tail -1)"; exit 1; fi
      if [[ $chk == *"'valid': True"* ]]; then echo "RUN $cfg $rid VALID"; else echo "RUN $cfg $rid INVALID"; echo "QUEUE STOP after an invalid run"; exit 1; fi
      rids+=($rid)
    done
    for rid in $rids; do
      rsync -a -e "ssh ${K[*]}" "${H}:aftershock-artifacts/runs/$rid" runs/ || { echo "QUEUE STOP copy failed $rid"; exit 1; }
      a=$(ssh $K $H "cd ~/aftershock-artifacts/runs/$rid && find . -type f | sort | xargs sha256sum" | shasum -a 256 | cut -c1-16)
      b=$(cd runs/$rid && find . -type f | sort | xargs shasum -a 256 | shasum -a 256 | cut -c1-16)
      [[ -n $a && $a == $b ]] || { echo "QUEUE STOP checksum mismatch $rid (vm [$a] mac [$b])"; exit 1; }
      echo "COPIED $rid sha-of-sums $a"
    done
    python3 tools/manifest.py update > /dev/null || { echo "QUEUE STOP manifest update failed"; exit 1; }
  fi
  mac_checks || { echo "QUEUE STOP a Mac-side check failed before the step"; exit 1; }
  links_ok || { echo "QUEUE STOP the worktree's links are not as required"; exit 1; }
  errf=$S/reg19_step_err_s${sd}_$(date -u +%Y%m%dT%H%M%SZ).txt
  step=$(cd $W && $PY -m analysis.gate reg19_step 2>$errf); rc=$?
  (( rc == 0 )) || { echo "QUEUE STOP reg19_step failed (rc $rc; see $errf)"; exit 1; }
  step=$(echo "$step" | tail -1)
  dn=$(echo "$step" | grep -o "'done': \[[^]]*\]"); cont=$(echo "$step" | grep -o "'continue': [A-Za-z]*")
  want="'done': [$(seq -s ', ' 15 $sd)]"
  [[ $dn == $want ]] || { echo "QUEUE STOP after seed $sd the step's done list is not 15..$sd: [$dn]"; exit 1; }
  [[ $cont == "'continue': True" || $cont == "'continue': False" ]] || { echo "QUEUE STOP reg19_step printed no continue flag"; exit 1; }
  echo "STEP after seed $sd: $dn $cont"
  if [[ $cont == "'continue': False" ]]; then
    if [[ $sd == 19 ]]; then echo "QUEUE DONE (all five seeds run)"; else echo "QUEUE END futility stop ('continue': False after seed $sd)"; fi
    exit 0
  fi
done
echo "QUEUE STOP the last seed asked for was run and the step says continue: nothing more was asked for"
exit 0
