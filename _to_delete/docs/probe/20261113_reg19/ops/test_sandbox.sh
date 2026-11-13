#!/bin/zsh
# Control-flow test of launch8.sh and queue_reg19f.sh in a sandbox: stub ssh, rsync, sleep and analysis step; no VM, no
# run folder, no git. It checks that every stop the rule F review asked for fires and that the happy path ends as it
# should. Usage: zsh docs/probe/20261113_reg19/ops/test_sandbox.sh   (exit 0 if every case passes)
SRC=${0:A:h}
T=$(mktemp -d /tmp/reg19_sandbox.XXXXXX)
mkdir -p $T/repo/tools $T/repo/runs $T/repo/docs/probe/20261113_reg19/ops $T/wt/runs $T/wt/configs $T/bin $T/state
S=$T/repo/docs/probe/20261113_reg19/ops
cp $SRC/session_probe.sh $SRC/launch8.sh $SRC/queue_reg19f.sh $S/
sed -e "s|^R=.*|R=$T/repo|" -e "s|^W=.*|W=$T/wt|" -e "s|^PY=.*|PY=$T/bin/fakepy|" $SRC/common.sh > $S/common.sh
cat >> $S/common.sh <<EOS
mac_checks() { SC=sandbox; cd \$R; return \${FAKE_MAC_RC:-0}; }
EOS
echo 'print("ok")' > $T/repo/tools/manifest.py
for sd in 18 19; do for k in stage2_control burst; do touch $T/wt/configs/${k}_l1pl350cl_r2.0_w3000_s$sd.yaml; done; done
for sd in 15 16 17; do for k in stage2_control burst; do id=20261112-0000${sd}_${k}_l1pl350cl_r2.0_w3000_s$sd; mkdir -p $T/repo/runs/$id; ln -s $T/repo/runs/$id $T/wt/runs/$id; done; done
echo BOOT-A > $S/session_boot_id.txt
cat > $T/bin/sleep <<'EOS'
#!/bin/sh
exit 0
EOS
cat > $T/bin/fakepy <<EOS
#!/bin/zsh
n=\$(cat $T/state/step_n 2>/dev/null || echo 0); n=\$((n + 1)); echo \$n > $T/state/step_n
[[ -f $T/state/step_rc ]] && { echo "Traceback (fake)" >&2; exit \$(cat $T/state/step_rc); }
sed -n "\${n}p" $T/state/steps
EOS
cat > $T/bin/rsync <<'EOS'
#!/bin/zsh
src=${@[-2]}; rid=${src:t}
mkdir -p runs/$rid && echo "{}" > runs/$rid/requests.jsonl && echo "$rid" > runs/$rid/config.yaml
EOS
cat > $T/bin/ssh <<EOS
#!/bin/zsh
cmd=\${@[-1]}; ST=$T/state
case \$cmd in
  *"pre-launch read"*)
    echo "# pre-launch read (fake)"; echo "2026-11-13T00:00:00+00:00"; echo "power.limit [W], temperature.gpu, utilization.gpu [%], memory.used [MiB]"
    echo "\${FAKE_LIMIT:-350.00} W, \${FAKE_TEMP:-40}, 0 %, 1 MiB"; echo "# compute apps:"; [[ -n \$FAKE_APPS ]] && echo "4242, python, 100 MiB"
    echo "# tree:"; echo "\${FAKE_TREE:-a7bb77abc863adcaad9d4516815a5ddddf2908e9}"; echo "\${FAKE_DIRTY:-0}"; echo "# boot:"; echo "\${FAKE_BOOT:-BOOT-A}"
    echo "# free_kb:"; echo "\${FAKE_FREE:-5000000}"; echo "# tmux:"; [[ -n \$FAKE_TMUX_EXISTS ]] && echo "run: 1 windows" || echo "no server running on /tmp/tmux-1000/default";;
  *"temperature.gpu --format=csv,noheader"*) echo "\${FAKE_TEMP:-40}";;
  *"tmux new-session"*) n=\$(cat \$ST/launch_n 2>/dev/null || echo 0); echo \$((n + 1)) > \$ST/launch_n; echo \$cmd | sed -n 's|.*configs/\\([^ ]*\\)\\.yaml.*|\\1|p' > \$ST/cfg;;
  *"grep -m1 -o"*) [[ -n \$FAKE_NO_RID ]] || echo "20261113-0000\$(cat \$ST/launch_n)_\$(cat \$ST/cfg)";;
  *"test -f"*"checks.json"*) [[ -n \$FAKE_NO_CHECKS ]] && exit 1 || exit 0;;
  *"tmux has-session"*) exit \${FAKE_TMUX_RC:-0};;
  *"grep 'checks'"*) echo "[run] checks {'valid': \${FAKE_VALID:-True}, 'failed': []}";;
  *"xargs sha256sum"*) rid=\$(echo \$cmd | sed -n 's|.*runs/\\([^ ]*\\) &&.*|\\1|p'); cd $T/repo/runs/\$rid && find . -type f | sort | xargs shasum -a 256; [[ -n \$FAKE_BAD_SHA ]] && echo corrupt;;
  *"python3 -c"*) echo "\${FAKE_ADOPT_VALID:-True}";;
  *) echo "fake ssh: unhandled: \$cmd" >&2; exit 9;;
esac
EOS
chmod +x $T/bin/*
pass=0; fail=0
reset() { setopt localoptions null_glob; rm -rf $T/state/* $T/repo/runs/*_s1[89] $T/wt/runs/*_s1[89] $T/repo/docs/probe/20261113_reg19/prelaunch_* $S/queue19_* $S/reg19_step_err_* $T/elsewhere; }
case_() {   # name, expected substring, expected exit code, then env assignments and the command
  local name=$1 want=$2 wantrc=$3; shift 3
  out=$(env PATH=$T/bin:$PATH "$@" 2>&1); rc=$?
  if [[ $out == *"$want"* && $rc == $wantrc ]]; then pass=$((pass + 1)); echo "ok    $name"; else fail=$((fail + 1)); echo "FAIL  $name (rc $rc, wanted $wantrc and '$want')"; echo "$out" | tail -6 | sed 's/^/        /'; fi
}
Q=$S/queue_reg19f.sh
reset; print -l "{'done': [15, 16, 17, 18], 'continue': True}" "{'done': [15, 16, 17, 18, 19], 'continue': False}" > $T/state/steps
case_ "happy path: both seeds, then QUEUE DONE" "QUEUE DONE (all five seeds run)" 0 SEEDS="18 19" ATTEMPT_SEED=18 ATTEMPT=2 zsh $Q
[[ -e $T/repo/docs/probe/20261113_reg19/prelaunch_reg19_stage2_control_l1pl350cl_r2.0_w3000_s18_attempt2.txt && -e $T/repo/docs/probe/20261113_reg19/prelaunch_reg19_burst_l1pl350cl_r2.0_w3000_s18_attempt1.txt ]] && { pass=$((pass + 1)); echo "ok    attempt 2 names only seed 18's control"; } || { fail=$((fail + 1)); echo "FAIL  probe names"; }
reset; print -l "{'done': [15, 16, 17, 18], 'continue': False}" > $T/state/steps
case_ "futility stop after seed 18" "QUEUE END futility stop" 0 SEEDS="18 19" zsh $Q
[[ $(cat $T/state/launch_n) == 2 ]] && { pass=$((pass + 1)); echo "ok    seed 19 not launched after the stop"; } || { fail=$((fail + 1)); echo "FAIL  launches $(cat $T/state/launch_n)"; }
reset; echo 1 > $T/state/step_rc
case_ "a crashed step is a stop, not a futility stop (T2)" "QUEUE STOP reg19_step failed" 1 SEEDS="18 19" zsh $Q
reset; print -l "{'done': [15, 16, 17], 'continue': True}" > $T/state/steps
case_ "a step that does not see seed 18 stops the queue (T1)" "done list is not 15..18" 1 SEEDS="18 19" zsh $Q
reset; print -l "garbage" > $T/state/steps
case_ "a step without a flag stops the queue" "done list is not 15..18" 1 SEEDS="18 19" zsh $Q
reset; print -l "{'done': [15, 16, 17, 18], 'continue': Maybe}" > $T/state/steps
case_ "an unknown flag value stops the queue" "printed no continue flag" 1 SEEDS="18" zsh $Q
reset
case_ "420 W stops the launch (T4)" "STOP: power limit 420.00" 1 FAKE_LIMIT=420.00 SEEDS="18" zsh $Q
reset
case_ "a reboot since the session probe stops the launch (T4)" "rebooted since the session probe" 1 FAKE_BOOT=BOOT-B SEEDS="18" zsh $Q
reset
case_ "another compute process stops the launch" "GPU compute process present" 1 FAKE_APPS=1 SEEDS="18" zsh $Q
reset
case_ "a VM tree off the pin stops the launch" "STOP: VM tree" 1 FAKE_TREE=deadbeef SEEDS="18" zsh $Q
reset
case_ "a dirty VM tree stops the launch" "STOP: VM tree" 1 FAKE_DIRTY=3 SEEDS="18" zsh $Q
reset
case_ "low disk stops the launch" "kB free on the VM" 1 FAKE_FREE=1000 SEEDS="18" zsh $Q
reset
case_ "an existing tmux session stops the launch" "a tmux session exists" 1 FAKE_TMUX_EXISTS=1 SEEDS="18" zsh $Q
reset
case_ "no run id within 120 s (T6)" "no run id" 1 FAKE_NO_RID=1 SEEDS="18" zsh $Q
reset
case_ "tmux gone without checks.json" "TMUX GONE, no checks.json" 1 FAKE_NO_CHECKS=1 FAKE_TMUX_RC=1 SEEDS="18" zsh $Q
reset
case_ "a run still going after the wait is not called invalid (T7)" "STILL RUNNING" 1 FAKE_NO_CHECKS=1 WAIT_MIN=2 SEEDS="18" zsh $Q
reset
case_ "an invalid run stops the queue" "QUEUE STOP after an invalid run" 1 FAKE_VALID=False SEEDS="18" zsh $Q
reset
case_ "a checksum mismatch stops the queue" "checksum mismatch" 1 FAKE_BAD_SHA=1 SEEDS="18" zsh $Q
reset
case_ "ATTEMPT 4 is refused (T5)" "ATTEMPT must be 1, 2 or 3" 2 ATTEMPT=4 SEEDS="18" zsh $Q
case_ "an unknown ATTEMPT_KIND is refused (T5)" "ATTEMPT_KIND must be" 2 ATTEMPT_KIND=control SEEDS="18" zsh $Q
case_ "a seed other than 18 or 19 is refused" "only seeds 18 and 19" 2 SEEDS="15" zsh $Q
case_ "a failed Mac-side check stops everything" "" 2 FAKE_MAC_RC=2 SEEDS="18" zsh $Q
reset; print -l "{'done': [15, 16, 17, 18], 'continue': True}" > $T/state/steps
env PATH=$T/bin:$PATH SEEDS="18" zsh $Q > /dev/null 2>&1
case_ "the same attempt is never launched twice (T5)" "this attempt was already launched" 1 SEEDS="18" zsh $Q
reset; print -l "{'done': [15, 16, 17, 18], 'continue': True}" > $T/state/steps
mkdir -p $T/elsewhere; ln -s $T/elsewhere $T/wt/runs/20261113-00001_stage2_control_l1pl350cl_r2.0_w3000_s18
case_ "a link that points elsewhere stops the step (T3)" "does not resolve to" 1 SEEDS="18" zsh $Q
reset; print -l "{'done': [15, 16, 17, 18], 'continue': True}" > $T/state/steps
case_ "adopting a finished control and burst run launches nothing (T6)" "STEP after seed 18" 0 SEEDS="18" ADOPT_SEED=18 ADOPT_CONTROL_RID=20261113-000001_stage2_control_l1pl350cl_r2.0_w3000_s18 ADOPT_BURST_RID=20261113-000002_burst_l1pl350cl_r2.0_w3000_s18 zsh $Q
[[ ! -e $T/state/launch_n ]] && { pass=$((pass + 1)); echo "ok    nothing was launched when both runs were adopted"; } || { fail=$((fail + 1)); echo "FAIL  adoption launched"; }
case_ "an adopted id of another config is refused" "is not a run of" 1 SEEDS="19" ADOPT_SEED=19 ADOPT_CONTROL_RID=20261113-000001_burst_l1pl350cl_r2.0_w3000_s19 zsh $Q
echo "passed $pass, failed $fail  (sandbox $T)"
[[ $fail == 0 ]]
