#!/bin/zsh
# REG-19 queue, resume, third version (decisions.md 2026-11-13 [DECISION] (delegate), REG-19 resume). One command, no
# settings:      zsh docs/probe/20261113_reg19/ops_r3/queue.sh        (in the background)
# It can be started again after any stop and launches nothing that is already there. Per seed, in the registered order
# 18 then 19: the control, then the burst run. For each config `decide` (common.sh) reads the attempt records and the
# VM's checks.json files: one valid run is used as it is; otherwise the next attempt is launched (launch.sh) if
# REG-19's rerun rule allows one. `valid` is read from checks.json, never from a log. Then both folders are copied to
# the Mac and every file's sha256 compared with the VM's; the manifest is updated; the REG-19 folders are linked into
# the worktree at the pin and the links verified; then `analysis.gate reg19_step` runs once FROM THE WORKTREE and its
# two fields, the `done` list and the `continue` flag, are written to state/reg19_step_s<seed>.txt. A seed with that
# record is never launched, copied or stepped again; seed 19 is reached only through seed 18's record saying
# 'continue': True. Every stop exits non-zero. "QUEUE END futility stop" needs 'continue': False in the record.
source ${0:A:h}/common.sh
mac_checks || exit 2
mkdir -p $ST
stop() { echo "QUEUE STOP $*"; exit 1; }
echo "QUEUE START seeds ${SEEDS[*]}; scripts $SC; pin $PIN; $(date -u +%Y-%m-%dT%H:%M:%SZ)"
cd $R || stop "no repo"
for sd in $SEEDS; do
  rec=$ST/reg19_step_s$sd.txt
  seeds_done=(); for x in {15..$sd}; do seeds_done+=($x); done
  want="'done': [${(j:, :)seeds_done}]"
  if [[ ! -e $rec ]]; then
    rids=()
    for kind in stage2_control burst; do
      cfg=${kind}_l1pl350cl_r2.0_w3000_s$sd
      decide $cfg || stop "$cfg: $MSG"
      if [[ -n $RID ]]; then echo "RUN $cfg $RID VALID (found on the VM; not launched)"; rids+=($RID); continue; fi
      ts=$(stamp); outf=$ST/launch_${cfg}_$ts.out
      [[ ! -e $outf ]] || stop "$outf exists"
      out=$(zsh $S/launch.sh $cfg 2>&1); rc=$?
      print -r -- "$out" > $outf
      rid=$(print -r -- "$out" | sed -n 's/^LAUNCHED \([^ ]*\).*/\1/p')
      (( rc == 0 )) || stop "$cfg launch rc=$rc rid=$rid: $(print -r -- "$out" | grep -E 'STOP|TMUX GONE|STILL RUNNING|VM NOT REACHABLE' | tail -1)"
      [[ -n $rid ]] || stop "$cfg: launch.sh ended with rc 0 and no run id"
      vm_state $cfg || stop "$cfg: the VM's run folders could not be read after the run; $rid is not judged. Start the queue again"
      state=""; failed=""
      for line in $VMS; do parts=(${=line}); if [[ $parts[1] == $rid ]]; then state=$parts[2]; failed=$parts[3]; fi; done
      case $state in
        valid) echo "RUN $cfg $rid VALID"; rids+=($rid);;
        invalid) echo "RUN $cfg $rid INVALID failed=$failed"; stop "after an invalid run. Starting the queue again applies REG-19's rerun rule from checks.json alone";;
        *) stop "$cfg: checks.json of $rid could not be read after the run (state '$state')";;
      esac
    done
    for rid in $rids; do
      rsync -a -e "ssh ${K[*]}" "${H}:aftershock-artifacts/runs/$rid" runs/ || stop "copy failed $rid"
      la=$(ssh $K $H "cd ~/aftershock-artifacts/runs/$rid && find . -type f | LC_ALL=C sort | xargs sha256sum") || stop "the VM's checksums of $rid could not be read"
      lb=$(cd runs/$rid && find . -type f | LC_ALL=C sort | xargs shasum -a 256) || stop "the Mac's checksums of $rid could not be computed"
      [[ -n $la && -n $lb ]] || stop "empty checksum list for $rid"
      a=$(print -r -- "$la" | shasum -a 256 | cut -c1-16); b=$(print -r -- "$lb" | shasum -a 256 | cut -c1-16)
      [[ $a == $b ]] || stop "checksum mismatch $rid (vm [$a] mac [$b])"
      echo "COPIED $rid ${#${(f)la}} files sha-of-sums $a"
    done
    python3 tools/manifest.py update > /dev/null || stop "manifest update failed"
    mac_checks || stop "a Mac-side check failed before the step"
    links_ok || stop "the worktree's links are not as required"
    ts=$(stamp); errf=$ST/reg19_step_err_s${sd}_$ts.txt; outf=$ST/reg19_step_out_s${sd}_$ts.txt
    [[ ! -e $errf && ! -e $outf ]] || stop "$outf exists"
    (cd $W && $PY -m analysis.gate reg19_step > $outf 2> $errf); rc=$?
    (( rc == 0 )) || stop "reg19_step failed (rc $rc; see $errf); no step is recorded"
    if grep -qE 'Traceback|Error|Exception' $errf; then stop "reg19_step wrote an error line (see $errf); no step is recorded"; fi
    step=$(tail -1 $outf)
    dn=$(print -r -- "$step" | grep -o "'done': \[[^]]*\]"); cont=$(print -r -- "$step" | grep -o "'continue': [A-Za-z]*")
    [[ "$dn" == "$want" ]] || stop "after seed $sd the step's done list is not 15..$sd: [$dn]; no step is recorded"
    [[ "$cont" == "'continue': True" || "$cont" == "'continue': False" ]] || stop "reg19_step printed no continue flag; no step is recorded"
    print -r -l -- "$dn" "$cont" "seed $sd" "time $(date -u +%Y-%m-%dT%H:%M:%SZ)" "scripts $SC" "pin $PIN" "stderr_lines $(wc -l < $errf | tr -d ' ') ${errf:t}" > $rec.tmp && mv $rec.tmp $rec || stop "the step record could not be written"
  fi
  dn=$(sed -n 1p $rec); cont=$(sed -n 2p $rec)
  [[ "$dn" == "$want" ]] || stop "the step record of seed $sd does not say done 15..$sd"
  echo "STEP after seed $sd: $dn $cont ($(sed -n 7p $rec))"
  case $cont in
    "'continue': False")
      if [[ $sd == ${SEEDS[-1]} ]]; then echo "QUEUE DONE (all five seeds run). Next: final.sh, once"; else echo "QUEUE END futility stop ('continue': False after seed $sd). Next: final.sh, once"; fi
      exit 0;;
    "'continue': True")
      [[ $sd != ${SEEDS[-1]} ]] || stop "the step says continue after the last seed";;
    *) stop "the step record of seed $sd holds no continue flag";;
  esac
done
stop "unexpected end of the seed loop"
