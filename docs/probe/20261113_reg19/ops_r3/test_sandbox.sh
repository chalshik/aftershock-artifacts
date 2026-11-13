#!/bin/zsh
# Sandbox test of the REG-19 resume scripts, third version. Nothing real is touched: a throwaway git repo and worktree
# stand in for the Mac's (so the REAL mac_checks and links_ok run), a folder tree stands in for the VM (so the REAL
# vm_state.py runs against it), and ssh, rsync, sleep, uv and the analysis interpreter are stubs.
# Usage: zsh docs/probe/20261113_reg19/ops_r3/test_sandbox.sh      (exit 0 if every case passes)
SRC=${0:A:h}
T=$(mktemp -d ${TMPDIR:-/tmp}/reg19_sandbox3.XXXXXX) || exit 99
T=${T:A}                                    # one spelling of the path: a TMPDIR ending in "/" gave "//", which a shell's $PWD does not keep
[[ $T == *reg19_sandbox3.* ]] || exit 99
VM=$T/vmhome/aftershock-artifacts
PD=$T/repo/docs/probe/20261113_reg19
S=$PD/ops_r3
BOOTA=11111111-2222-3333-4444-555555555555
LOST=20261112-151030_stage2_control_l1pl350cl_r2.0_w3000_s18
C18=stage2_control_l1pl350cl_r2.0_w3000_s18; B18=burst_l1pl350cl_r2.0_w3000_s18
G=(git -c user.name=sandbox -c user.email=sandbox@example.invalid -c commit.gpgsign=false)
mkdir -p $T/bin $T/state $VM/runs $T/repo && cd $T/repo && git init -q -b main . || exit 99
mkdir -p tools configs runs harness analysis $S/state
echo 'import os, sys; sys.exit(1 if os.environ.get("FAKE_MANIFEST_FAIL") else 0)' > tools/manifest.py
echo x > pyproject.toml; echo x > uv.lock; echo 'runs/' > .gitignore
echo x > harness/checks.py; echo x > analysis/recheck.py
for sd in 15 16 17 18 19; do for k in stage2_control burst; do echo x > configs/${k}_l1pl350cl_r2.0_w3000_s$sd.yaml; done; done   # all ten, as at the real pin
$G add -A && $G commit -q -m pin || exit 99
PINH=$(git rev-parse HEAD); LOCKB=$(git rev-parse ${PINH}:uv.lock)
git worktree add -q --detach $T/wt $PINH && mkdir -p $T/wt/runs || exit 99
cp $SRC/vm_state.py $SRC/session_probe.sh $SRC/launch.sh $SRC/queue.sh $SRC/final.sh $S/
cp $SRC/state/attempt_${C18}_1.txt $SRC/state/lost_ok_$LOST.txt $S/state/
sed -e "s|^R=.*|R=$T/repo|" -e "s|^W=.*|W=$T/wt|" -e "s|^PY=.*|PY=$T/bin/fakepy|" -e "s|^PIN=.*|PIN=$PINH|" \
    -e "s|^CHECKS_COMMIT=.*|CHECKS_COMMIT=$PINH|" -e "s|^RECHECK_COMMIT=.*|RECHECK_COMMIT=$PINH|" $SRC/common.sh > $S/common.sh
mkdir -p docs && print -r -- "## 2026-11-13 · [DECISION] (delegate) REG-19 resumes for seeds 18 and 19: sandbox" > docs/decisions.md
$G add -A && $G commit -q -m scripts || exit 99
git log -1 --format=%H -- docs/probe/20261113_reg19/ops_r3/{common.sh,vm_state.py,session_probe.sh,launch.sh,queue.sh,final.sh} > $S/scripts_commit.txt
$G add -A && $G commit -q -m scripts_commit || exit 99
HEADH=$(git rev-parse HEAD)
for sd in 15 16 17; do for k in stage2_control burst; do id=20261112-0000${sd}_${k}_l1pl350cl_r2.0_w3000_s$sd; mkdir -p $T/repo/runs/$id; ln -s $T/repo/runs/$id $T/wt/runs/$id; done; done

cat > $T/bin/sleep <<'EOS'
#!/bin/sh
exit 0
EOS
cat > $T/bin/date <<'EOS'
#!/bin/sh
if [ "$*" = "-u +%H%M" ]; then echo "${FAKE_HHMM:-0600}"; else exec /bin/date "$@"; fi
EOS
cat > $T/bin/uv <<'EOS'
#!/bin/sh
echo "Would use project environment at: .venv"; echo "Would uninstall 2 packages"; echo " - a==1"; echo " - b==1"
[ -n "$FAKE_UV_ADD" ] && echo " + c==2"
exit 0
EOS
cat > $T/bin/fakepy <<'EOS'
#!/bin/zsh
ST=__T__/state
case "$*" in
  *"analysis.gate reg19_step"*)
    n=$(( $(cat $ST/step_n 2>/dev/null || echo 0) + 1 )); echo $n > $ST/step_n
    [[ -f $ST/step_stderr ]] && cat $ST/step_stderr >&2
    [[ -f $ST/step_rc ]] && { echo "Traceback (fake)" >&2; exit $(cat $ST/step_rc); }
    sed -n "${n}p" $ST/steps;;
  *"analysis.gate reg19"*)
    [[ -f $ST/final_rc ]] && exit $(cat $ST/final_rc)
    echo "{'fake': 'table', 'cwd': '$PWD'}";;
  *"analysis.recheck"*)
    echo "unseal=$AFTERSHOCK_UNSEAL pattern=${@[-1]}" >&2
    setopt null_glob; mac=(__T__/repo/runs/*_w3000_s1[5-9])
    if [[ -f $ST/recheck_json ]]; then cat $ST/recheck_json; else echo "{\"n_runs\": ${FAKE_RECHECK_N:-${#mac}}, \"n_changed\": 0, \"changed\": []}"; fi;;
  *) echo "fakepy: unhandled $*" >&2; exit 9;;
esac
EOS
cat > $T/bin/rsync <<'EOS'
#!/bin/zsh
src=${@[-2]}; rid=${src:t}
[[ -n $FAKE_RSYNC_FAIL ]] && exit 1
cp -R __T__/vmhome/aftershock-artifacts/runs/$rid runs/
EOS
cat > $T/bin/ssh <<'EOS'
#!/bin/zsh
cmd=${@[-1]}; ST=__T__/state; VM=__T__/vmhome/aftershock-artifacts
case $cmd in
  "python3 - "*) [[ -n $FAKE_STATE_DOWN ]] && exit 255; HOME=__T__/vmhome python3 - ${=cmd#python3 - };;
  *"up_since"*)
    echo "2026-11-13T00:00:00+00:00"; echo "boot_id ${FAKE_BOOT:-__BOOT__}"; echo "up_since 2026-11-12 19:48:00"; echo "kernel 6.8.0-fake"
    echo "driver ${FAKE_DRIVER:-595.99.02}"; echo "governor performance"; echo "limit_before ${FAKE_LIMIT_BEFORE:-420.00} W"; echo "apps ${FAKE_APPS_N:-0}"
    echo "boots -1 aaa;0 bbb;"; echo "prev_boot_kernel Linux version 6.8.0-fake"; echo "prev_boot_nvidia NVIDIA UNIX x86_64 Kernel Module  595.99.02";;
  *"sudo -n nvidia-smi -pl 350"*) echo "sudo: a password is required"; echo "sudo_rc 1";;
  *"limit_after"*)
    echo "limit_after ${FAKE_LIMIT:-350.00} W"; echo "tree ${FAKE_TREE:-__PIN__} dirty ${FAKE_DIRTY:-0}"; echo "lock_blob ${FAKE_LOCK:-__LOCK__}"; echo "free_kb ${FAKE_FREE:-5000000}";;
  *"pre-launch read"*)
    [[ -n $FAKE_PRELAUNCH_FAIL ]] && exit 255
    echo "# pre-launch read (fake)"; echo "2026-11-13T00:00:00+00:00"; echo "power.limit [W], temperature.gpu, utilization.gpu [%], memory.used [MiB]"
    echo "${FAKE_LIMIT:-350.00} W, ${FAKE_TEMP:-40}, 0 %, 1 MiB"; echo "# compute apps:"; [[ -n $FAKE_APPS ]] && echo "4242, python, 100 MiB"
    echo "# tree:"; echo "${FAKE_TREE:-__PIN__}"; echo "${FAKE_DIRTY:-0}"; echo "# boot:"; if [[ -n $FAKE_BOOT_EMPTY ]]; then echo ""; else echo "${FAKE_BOOT:-__BOOT__}"; fi
    echo "# free_kb:"; echo "${FAKE_FREE:-5000000}"; echo "# tmux:"; [[ -n $FAKE_TMUX_EXISTS ]] && echo "run: 1 windows" || echo "no server running on /tmp/tmux-1000/default";;
  *"temperature.gpu --format=csv,noheader"*) [[ -n $FAKE_TEMP_FAIL ]] && exit 255; echo "${FAKE_TEMP:-40}";;
  *"tmux new-session"*)
    [[ -n $FAKE_LAUNCH_FAIL ]] && exit 255
    n=$(( $(cat $ST/launch_n 2>/dev/null || echo 0) + 1 )); echo $n > $ST/launch_n
    cfg=$(print -r -- $cmd | sed -n 's|.*configs/\([^ ]*\)\.yaml.*|\1|p'); rid=20261113-$(printf %06d $n)_$cfg; echo $rid > $ST/rid
    mkdir -p $VM/runs/$rid; echo "{}" > $VM/runs/$rid/requests.jsonl; echo "name: $cfg" > $VM/runs/$rid/config.yaml
    echo "{\"git_commit\": \"${FAKE_COMMIT:-__PIN__}\"}" > $VM/runs/$rid/env.json
    failed=$FAKE_FAILED; [[ -n $FAKE_FAILED_KIND && $cfg != ${FAKE_FAILED_KIND}_* ]] && failed=""
    if [[ -z $FAKE_NO_CHECKS ]]; then
      case $failed in
        "") echo '{"valid": true, "failed": [], "checks": []}' > $VM/runs/$rid/checks.json;;
        no_errors) echo '{"valid": false, "failed": ["no_errors"], "checks": [{"name": "no_errors", "passed": false, "detail": {"ok": 9, "client_error": 2}}]}' > $VM/runs/$rid/checks.json;;
        no_errors_http) echo '{"valid": false, "failed": ["no_errors"], "checks": [{"name": "no_errors", "passed": false, "detail": {"ok": 9, "http_error": 2}}]}' > $VM/runs/$rid/checks.json;;
        *) echo "{\"valid\": false, \"failed\": [\"$failed\"], \"checks\": []}" > $VM/runs/$rid/checks.json;;
      esac
    fi;;
  *"grep -m1 -o"*) [[ -n $FAKE_NO_RID ]] || cat $ST/rid;;
  *"test -f"*"checks.json"*)
    [[ -n $FAKE_DOWN_ON_WAIT ]] && exit 255
    if [[ -n $FAKE_LATE_CHECKS ]]; then
      n=$(( $(cat $ST/late_n 2>/dev/null || echo 0) + 1 )); echo $n > $ST/late_n
      (( n <= FAKE_LATE_CHECKS )) && exit 1
    fi
    rid=$(print -r -- $cmd | sed -n 's|.*runs/\([^/]*\)/checks.json.*|\1|p'); [[ -f $VM/runs/$rid/checks.json ]];;
  *"tmux has-session"*) exit ${FAKE_TMUX_RC:-0};;
  *"xargs sha256sum"*)
    [[ -n $FAKE_SHA_FAIL ]] && exit 255
    rid=$(print -r -- $cmd | sed -n 's|.*runs/\([^ ]*\) &&.*|\1|p'); cd $VM/runs/$rid && find . -type f | LC_ALL=C sort | xargs shasum -a 256; [[ -n $FAKE_BAD_SHA ]] && echo corrupt; true;;
  *) echo "fake ssh: unhandled: $cmd" >&2; exit 9;;
esac
EOS
/usr/bin/sed -i '' -e "s|__T__|$T|g" -e "s|__PIN__|$PINH|g" -e "s|__LOCK__|$LOCKB|g" -e "s|__BOOT__|$BOOTA|g" $T/bin/ssh $T/bin/fakepy $T/bin/rsync
chmod +x $T/bin/*

pass=0; fail=0
reset() {
  setopt localoptions null_glob
  [[ $T == *reg19_sandbox3.* ]] || exit 99
  rm -rf $T/state/* $T/repo/runs/*_s1[89] $T/wt/runs/*_s1[89] $T/wt/runs/foreign $PD/prelaunch_* $PD/session_* $T/elsewhere $VM/runs/*
  (cd $T/repo && git reset -q --hard $HEADH && git clean -fdq docs/probe/20261113_reg19/ops_r3/state)
  (cd $T/wt && git checkout -q --detach $PINH && git checkout -q -- .)
  mkdir -p $VM/runs/$LOST; echo x > $VM/runs/$LOST/requests.jsonl
  print -r -- $BOOTA > $S/state/session_boot_id.txt
}
case_() {   # name, expected substring, expected exit code, then env assignments and the command
  local name=$1 want=$2 wantrc=$3; shift 3
  out=$(env PATH=$T/bin:$PATH "$@" 2>&1); rc=$?
  if [[ $out == *"$want"* && $rc == $wantrc ]]; then pass=$((pass + 1)); echo "ok    $name"; else fail=$((fail + 1)); echo "FAIL  $name (rc $rc, wanted $wantrc and '$want')"; print -r -- "$out" | tail -6 | sed 's/^/        /'; fi
}
chk() {     # name, then a command that must succeed
  local name=$1; shift
  if "$@" > /dev/null 2>&1; then pass=$((pass + 1)); echo "ok    $name"; else fail=$((fail + 1)); echo "FAIL  $name"; fi
}
is() { [[ $1 == $2 ]]; }                      # literal equality
mkrun() {   # a hand-made run folder on the fake VM: run id, checks.json text ("" for none), commit (default: the pin)
  mkdir -p $VM/runs/$1; echo "{\"git_commit\": \"${3:-$PINH}\"}" > $VM/runs/$1/env.json
  [[ -z $2 ]] || print -r -- $2 > $VM/runs/$1/checks.json
}
VALID='{"valid": true, "failed": [], "checks": []}'
launches() { cat $T/state/launch_n 2>/dev/null || echo 0; }
nfiles() { setopt localoptions null_glob; local f=($~1); echo ${#f}; }
steps() { print -l -- "$@" > $T/state/steps; }
Q=$S/queue.sh; L=$S/launch.sh; F=$S/final.sh; P=$S/session_probe.sh
S18T="{'done': [15, 16, 17, 18], 'continue': True}"; S18F="{'done': [15, 16, 17, 18], 'continue': False}"
S19F="{'done': [15, 16, 17, 18, 19], 'continue': False}"; S19T="{'done': [15, 16, 17, 18, 19], 'continue': True}"

echo "--- queue: the happy path, and starting it again"
reset; steps $S18T $S19F
case_ "happy path: both seeds, then QUEUE DONE" "QUEUE DONE (all five seeds run)" 0 zsh $Q
chk "four launches" is "$(launches)" 4
chk "seed 18's control is attempt 2, with its run id" grep -q "^rid 20261113-000001_$C18" $S/state/attempt_${C18}_2.txt
chk "no attempt 3 of seed 18's control" test ! -e $S/state/attempt_${C18}_3.txt
chk "seed 18's burst is attempt 1" test -e $S/state/attempt_${B18}_1.txt
chk "both step records exist" test -e $S/state/reg19_step_s18.txt -a -e $S/state/reg19_step_s19.txt
chk "four run folders copied and linked" is "$(nfiles "$T/wt/runs/*_s1[89]")" 4
case_ "started again after the end: same end" "QUEUE DONE (all five seeds run)" 0 zsh $Q
chk "nothing launched or stepped again" is "$(launches) $(cat $T/state/step_n)" "4 2"

echo "--- queue: the futility stop and the step"
reset; steps $S18F
case_ "futility stop after seed 18" "QUEUE END futility stop" 0 zsh $Q
chk "seed 19 not launched" is "$(launches)" 2
case_ "started again after a futility stop: still the stop" "QUEUE END futility stop" 0 zsh $Q
chk "seed 19 still not launched (N3)" is "$(launches)" 2
reset; steps garbage $S18T $S19F; echo 1 > $T/state/step_rc
case_ "a crashed step is a stop, not a futility stop" "QUEUE STOP reg19_step failed" 1 zsh $Q
chk "no step record after a crashed step" test ! -e $S/state/reg19_step_s18.txt
rm $T/state/step_rc
case_ "after the fix the queue goes on without relaunching seed 18" "QUEUE DONE (all five seeds run)" 0 zsh $Q
chk "four launches in all" is "$(launches)" 4
reset; steps "{'done': [15, 16, 17], 'continue': True}"
case_ "a step that does not see seed 18 stops the queue" "done list is not 15..18" 1 zsh $Q
chk "and leaves no record" test ! -e $S/state/reg19_step_s18.txt
reset; steps "{'done': [15, 16, 17, 18], 'continue': Maybe}"
case_ "an unknown flag value stops the queue" "printed no continue flag" 1 zsh $Q
reset; steps $S18F; echo "ValueError: fake" > $T/state/step_stderr
case_ "'continue': False with an error line on stderr is not a futility stop (N7)" "wrote an error line" 1 zsh $Q
reset; steps $S18F; echo "RuntimeWarning: mean of empty slice" > $T/state/step_stderr
case_ "a warning on stderr does not block, and is counted in the record" "stderr_lines 1" 0 zsh $Q
reset; steps $S18T $S19T
case_ "'continue': True after the last seed is a stop" "continue after the last seed" 1 zsh $Q

echo "--- launch: pre-launch stops spend no attempt"
reset; steps $S18T $S19F
case_ "420 W stops the launch" "STOP: power limit '420.00'" 1 FAKE_LIMIT=420.00 zsh $Q
chk "a pre-launch stop records no attempt (N2)" test ! -e $S/state/attempt_${C18}_2.txt
chk "but keeps its probe" is "$(nfiles "$PD/prelaunch_reg19_${C18}_*.txt")" 1
case_ "the same command then runs, as attempt 2" "QUEUE DONE" 0 zsh $Q
chk "attempt 2, not 3" test -e $S/state/attempt_${C18}_2.txt -a ! -e $S/state/attempt_${C18}_3.txt
reset
case_ "a reboot since the session probe stops the launch" "rebooted since the session probe" 1 FAKE_BOOT=99999999-2222-3333-4444-555555555555 zsh $Q
reset
case_ "an empty boot id stops the launch" "rebooted since the session probe (boot id '')" 1 FAKE_BOOT_EMPTY=1 zsh $Q
reset
case_ "another compute process stops the launch" "GPU compute process present" 1 FAKE_APPS=1 zsh $Q
reset
case_ "a VM tree off the pin stops the launch" "STOP: VM tree" 1 FAKE_TREE=deadbeef zsh $Q
reset
case_ "a dirty VM tree stops the launch" "STOP: VM tree" 1 FAKE_DIRTY=3 zsh $Q
reset
case_ "low disk stops the launch" "kB free on the VM" 1 FAKE_FREE=1000 zsh $Q
reset
case_ "an unreadable free-disk value stops the launch" "kB free on the VM" 1 FAKE_FREE=n/a zsh $Q
reset
case_ "a temperature that is not a number stops the launch" "is not a number" 1 FAKE_TEMP=N/A zsh $Q
reset
case_ "an existing tmux session stops the launch" "a tmux session exists" 1 FAKE_TMUX_EXISTS=1 zsh $Q
reset; rm $S/state/session_boot_id.txt
case_ "no session probe, no launch" "no session probe" 1 zsh $Q
chk "none of these launched anything" is "$(launches)" 0

echo "--- launch: what a started run can leave behind"
reset; steps $S18T $S19F
case_ "no run id within 120 s" "no run id" 1 FAKE_NO_RID=1 zsh $Q
chk "the attempt is spent" test -e $S/state/attempt_${C18}_2.txt
case_ "started again: the finished valid run is used, not relaunched (N4)" "RUN $C18 20261113-000001_$C18 VALID (found on the VM; not launched)" 0 zsh $Q
reset
case_ "tmux gone without checks.json" "TMUX GONE, no checks.json" 1 FAKE_NO_CHECKS=1 FAKE_TMUX_RC=1 zsh $Q
case_ "a second lost run is not rerun without its own decision" "a rerun needs its own decision" 1 zsh $Q
chk "one launch only" is "$(launches)" 1
reset
case_ "a run still going after the wait is not called invalid" "STILL RUNNING" 1 FAKE_NO_CHECKS=1 WAIT_MIN=2 zsh $Q
reset
case_ "a VM that stops answering is reported as such" "VM NOT REACHABLE" 1 FAKE_DOWN_ON_WAIT=1 WAIT_MIN=3 zsh $Q
reset; steps $S18T $S19F
case_ "the launch command failing spends the attempt" "the launch command failed" 1 FAKE_LAUNCH_FAIL=1 zsh $Q
chk "and says so in the record" grep -q launch_command_failed $S/state/attempt_${C18}_2.txt
case_ "started again: attempt 3 runs" "QUEUE DONE" 0 zsh $Q
chk "attempt 3 recorded" test -e $S/state/attempt_${C18}_3.txt
reset
case_ "the VM's state unreadable stops the queue" "could not be read" 1 FAKE_STATE_DOWN=1 zsh $Q

echo "--- REG-19's rerun rule, from checks.json alone"
reset; steps $S18T $S19F
case_ "an invalid run stops the queue and names the failed check" "INVALID failed=client_lag" 1 FAKE_FAILED=client_lag zsh $Q
case_ "the second invalid run of the config" "INVALID failed=client_lag" 1 FAKE_FAILED=client_lag zsh $Q
case_ "three attempts spent: no fourth launch" "attempts of $C18 are spent" 1 zsh $Q
chk "two launches by these scripts, three attempts with the lost one" is "$(launches)" 2
reset; steps $S18T $S19F
case_ "an invalid run, then" "INVALID failed=client_lag" 1 FAKE_FAILED=client_lag zsh $Q
case_ "its rerun is valid and the queue goes on" "QUEUE DONE" 0 zsh $Q
reset
case_ "a client error" "INVALID failed=no_errors" 1 FAKE_FAILED=no_errors zsh $Q
case_ "is not rerun (registered stop)" "registers no rerun after no_errors" 1 zsh $Q
reset
case_ "a burst that did not fill the pool" "INVALID failed=manipulation" 1 FAKE_FAILED=manipulation FAKE_FAILED_KIND=burst zsh $Q
case_ "is not rerun (registered stop)" "registers no rerun after manipulation" 1 zsh $Q
reset
case_ "a run at another power limit" "INVALID failed=power_limit" 1 FAKE_FAILED=power_limit zsh $Q
case_ "is not rerun (registered stop)" "registers no rerun after power_limit" 1 zsh $Q
reset
case_ "a heat failure" "INVALID failed=gpu_steady" 1 FAKE_FAILED=gpu_steady FAKE_FAILED_KIND=burst zsh $Q
case_ "is rerun once; a second heat failure" "INVALID failed=gpu_steady" 1 FAKE_FAILED=gpu_steady FAKE_FAILED_KIND=burst zsh $Q
case_ "stops the queue" "second heat failure" 1 zsh $Q
reset
case_ "a heat failure of the control" "INVALID failed=gpu_steady" 1 FAKE_FAILED=gpu_steady FAKE_FAILED_KIND=stage2_control zsh $Q
case_ "its rerun is valid; then a heat failure of the burst run" "INVALID failed=gpu_steady" 1 FAKE_FAILED=gpu_steady FAKE_FAILED_KIND=burst zsh $Q
case_ "is the second among REG-19's runs: the queue stops (D2)" "second heat failure (gpu_steady) among REG-19's runs" 1 zsh $Q
chk "three launches: control, control, burst" is "$(launches)" 3
reset; steps $S18T $S19F
case_ "an http error is an invalid run like any other" "INVALID failed=no_errors/other" 1 FAKE_FAILED=no_errors_http zsh $Q
case_ "and is rerun (REG-19 registers the stop for a client error only)" "QUEUE DONE" 0 zsh $Q
reset; mkrun 20261113-090000_$C18 $VALID; mkrun 20261113-100000_$C18 $VALID
case_ "two valid runs of one config stop the queue" "holds 2 valid runs" 1 zsh $Q
reset; mkrun 20261113-090000_$C18 '{"valid": true, "failed": ["x"], "checks": []}'
case_ "a checks.json that contradicts itself stops the queue" "cannot be read" 1 zsh $Q
reset; rm $S/state/attempt_${C18}_1.txt
case_ "without the lost run's attempt record nothing is launched (N1)" "a committed state record differs" 2 zsh $Q
reset; rm $S/state/lost_ok_$LOST.txt
case_ "without the decision's record the lost run is not rerun" "a committed state record differs" 2 zsh $Q
reset; echo "changed" >> $S/state/lost_ok_$LOST.txt
case_ "a changed state record stops everything" "a committed state record differs" 2 zsh $Q
chk "none of these launched anything" is "$(launches)" 0

echo "--- copy, checksums, links"
reset; steps $S18T $S19F
case_ "a checksum mismatch stops the queue" "checksum mismatch" 1 FAKE_BAD_SHA=1 zsh $Q
case_ "started again: both runs are used, copied, verified, stepped" "QUEUE DONE" 0 zsh $Q
chk "four launches in all" is "$(launches)" 4
reset
case_ "a failed copy stops the queue" "copy failed" 1 FAKE_RSYNC_FAIL=1 zsh $Q
reset
case_ "the VM's checksums unreadable stop the queue" "checksums of 20261113-000001_$C18 could not be read" 1 FAKE_SHA_FAIL=1 zsh $Q
reset; steps $S18T; mkdir -p $T/elsewhere; ln -s $T/elsewhere $T/wt/runs/20261113-000001_$C18
case_ "a link that points elsewhere stops the step" "does not resolve to" 1 zsh $Q
reset; steps $S18T; mkdir -p $T/wt/runs/20261113-000001_$C18
case_ "a real folder where a link belongs stops the step" "exists and is not a link" 1 zsh $Q
chk "and nothing was written into it (N8)" is "$(nfiles "$T/wt/runs/20261113-000001_$C18/*")" 0
reset; steps $S18T; mkdir -p $T/wt/runs/foreign
case_ "a foreign entry in the worktree's runs/ stops the step" "which is not a REG-19 run folder" 1 zsh $Q

echo "--- the Mac-side checks (real git)"
reset; echo y >> $T/wt/configs/$C18.yaml
case_ "a dirty worktree" "is dirty" 2 zsh $Q
reset; (cd $T/wt && git checkout -q --detach main)
case_ "a worktree off the pin" "is not at" 2 zsh $Q
reset; echo y >> $T/repo/uv.lock
case_ "uv.lock changed in the working tree" "differ from the pin in the working tree" 2 zsh $Q
reset; echo "# y" >> $S/queue.sh
case_ "a script changed since its commit" "differs from its committed text" 2 zsh $Q
reset; rm $S/scripts_commit.txt
case_ "scripts_commit.txt missing" "no scripts_commit.txt" 2 zsh $Q
reset; echo deadbeef > $S/scripts_commit.txt
case_ "scripts_commit.txt naming another commit" "changed since scripts_commit.txt" 2 zsh $Q
chk "none of these launched anything" is "$(launches)" 0

echo "--- launch.sh by hand"
reset; mkrun 20261113-090000_$C18 $VALID
case_ "a valid run with no attempt record is a launch outside these scripts: stop" "only 1 attempts are recorded" 2 zsh $L $C18
echo x > $S/state/attempt_${C18}_2.txt
case_ "launch.sh refuses when a valid run exists" "nothing to launch" 2 zsh $L $C18
reset
case_ "launch.sh refuses a config that exists at the pin but is not one of the four" "is not one of the four configs left" 2 zsh $L stage2_control_l1pl350cl_r2.0_w3000_s15
case_ "launch.sh refuses a name that is no config" "is not one of the four configs left" 2 zsh $L nonsense
reset
case_ "launch.sh by hand takes the next attempt number itself" "LAUNCHED 20261113-000001_$C18 (attempt 2)" 0 zsh $L $C18

echo "--- round 3: the gate, the Mac's folders, the commit, the decision, the lock, the clock"
C19=stage2_control_l1pl350cl_r2.0_w3000_s19; B19=burst_l1pl350cl_r2.0_w3000_s19
reset
case_ "by hand: seed 19 before seed 18 has a step record is refused (T1)" "seed 19 is launched only after seed 18's step record" 2 zsh $L $C19
case_ "by hand: a burst run before a valid control is refused (T1)" "only after a valid control" 2 zsh $L $B18
reset; steps $S18F; env PATH=$T/bin:$PATH zsh $Q > /dev/null 2>&1
case_ "by hand after a futility stop: seed 19 is refused (T1)" "seed 19 is launched only after seed 18's step record" 2 zsh $L $C19
case_ "by hand after a futility stop: seed 18 is not launched again (T1)" "seed 18 has a step record" 2 zsh $L $C18
chk "nothing beyond seed 18's pair was launched" is "$(launches)" 2
reset; steps garbage; env PATH=$T/bin:$PATH zsh $Q > /dev/null 2>&1                # the pair is copied, the step fails
[[ $T == *reg19_sandbox3.* ]] && rm -rf $VM/runs/20261113-00000[12]_*              # someone clears the VM's copies
case_ "a pair on the Mac that the VM no longer lists is not made again (T2)" "which the VM does not list" 1 zsh $Q
chk "no third launch" is "$(launches)" 2
reset
case_ "a run made at another commit is not counted (T3)" "not at the pin" 1 FAKE_COMMIT=deadbeef zsh $Q
reset; mkrun 20261113-090000_$C18 $VALID deadbeef; echo x > $S/state/attempt_${C18}_2.txt
case_ "a valid run found on the VM at another commit is not used (T3)" "not at the pin" 1 zsh $Q
reset; (cd $T/repo && : > docs/decisions.md && $G commit -q -am "no decision")
case_ "no queue before the decision is in the committed log (T5)" "is not in the committed docs/decisions.md" 2 zsh $Q
case_ "no launch by hand either (T5)" "is not in the committed docs/decisions.md" 2 zsh $L $C18
reset; mkdir -p $S/state/queue.lock; echo $$ > $S/state/queue.lock/pid
case_ "a second queue beside a running one is refused" "another queue is running" 1 zsh $Q
reset; steps $S18T $S19F; mkdir -p $S/state/queue.lock; echo 999999 > $S/state/queue.lock/pid
case_ "a lock left by a dead queue is set aside and the queue runs" "QUEUE DONE" 0 zsh $Q
chk "the stale lock is kept under another name" is "$(nfiles "$S/state/queue.lock.stale_*")" 1
reset
case_ "WAIT_MIN that is not a number stops before anything" "WAIT_MIN is not a number" 2 WAIT_MIN=abc zsh $Q
reset
case_ "no control is started at 15:00 UTC" "no launch of $C18" 1 FAKE_HHMM=1500 zsh $Q
case_ "nor at 12:00 UTC: its burst run would last into those hours" "no launch of $C18" 1 FAKE_HHMM=1200 zsh $Q
chk "neither spent an attempt" test ! -e $S/state/attempt_${C18}_2.txt
reset; steps $S18T $S19F; env PATH=$T/bin:$PATH FAKE_FAILED=client_lag FAKE_FAILED_KIND=burst zsh $Q > /dev/null 2>&1   # control valid, burst invalid
case_ "a burst run may still start at 12:00 UTC; the next control may not" "no launch of $C19" 1 FAKE_HHMM=1200 zsh $Q
chk "three launches: control, burst, burst" is "$(launches)" 3
reset; env PATH=$T/bin:$PATH FAKE_FAILED=client_lag FAKE_FAILED_KIND=burst zsh $Q > /dev/null 2>&1
case_ "no burst run is started at 13:00 UTC" "no launch of $B18" 1 FAKE_HHMM=1300 zsh $Q
reset; steps $S18T $S19F
case_ "at 18:00 UTC the queue runs again" "QUEUE DONE" 0 FAKE_HHMM=1800 zsh $Q
chk "the attempt record names the boot of its run" grep -q "^boot $BOOTA" $S/state/attempt_${C18}_2.txt
reset
case_ "morning window: no control is started at 03:00 UTC" "no launch of $C18" 1 FAKE_HHMM=0300 zsh $Q
case_ "nor at 00:00 UTC: its burst run would last past 02:30" "no launch of $C18" 1 FAKE_HHMM=0000 zsh $Q
case_ "nor at 04:59 UTC" "no launch of $C18" 1 FAKE_HHMM=0459 zsh $Q
chk "none of the three spent an attempt" test ! -e $S/state/attempt_${C18}_2.txt
reset; env PATH=$T/bin:$PATH FAKE_FAILED=client_lag FAKE_FAILED_KIND=burst zsh $Q > /dev/null 2>&1
case_ "no burst run is started at 01:15 UTC" "no launch of $B18" 1 FAKE_HHMM=0115 zsh $Q
reset; steps $S18T $S19F
case_ "at 05:00 UTC the queue runs again" "QUEUE DONE" 0 FAKE_HHMM=0500 zsh $Q
reset; steps $S18T $S19F
case_ "a control may still start at 23:59 UTC" "QUEUE DONE" 0 FAKE_HHMM=2359 zsh $Q

echo "--- round 3: the checks in force before each step"
reset; steps $S18T $S19F
echo '{"n_runs": 8, "n_changed": 1, "changed": [{"run": "x", "stored_valid": true, "now_valid": false, "stored_failed": [], "now_failed": ["recorder"], "recorder": {"end_ref_t": 4080.0}, "gpu_steady": {"max_temp_c": 70}}]}' > $T/state/recheck_json
case_ "a run the checks in force would fail stops the queue before the step (T4)" "operational stop before the step of seed 18" 1 zsh $Q
chk "no step record" test ! -e $S/state/reg19_step_s18.txt
chk "the saved record keeps validity" grep -q '"now_failed"' $S/state/reg19_recheck_*.json
chk "and none of the checks' details" sh -c "! grep -q 'end_ref_t\|max_temp_c' $S/state/reg19_recheck_*.json"
reset; steps $S18T $S19F
case_ "a recheck that sees another number of runs stops the queue before the step" "operational stop before the step of seed 18" 1 FAKE_RECHECK_N=6 zsh $Q

echo "--- round 3: stops that had no case"
reset
case_ "a GPU still hot after the wait" "STOP: GPU at '60' C" 1 FAKE_TEMP=60 zsh $Q
case_ "a temperature that cannot be read" "could not be read (temperature)" 1 FAKE_TEMP_FAIL=1 zsh $Q
case_ "a pre-launch read that fails" "the pre-launch read failed" 1 FAKE_PRELAUNCH_FAIL=1 zsh $Q
chk "none of the three launched" is "$(launches)" 0
chk "or spent an attempt" test ! -e $S/state/attempt_${C18}_2.txt
reset
case_ "a manifest update that fails" "manifest update failed" 1 FAKE_MANIFEST_FAIL=1 zsh $Q
reset; steps $S18T $S19F
case_ "checks.json appearing just after tmux ended is found" "QUEUE DONE" 0 FAKE_LATE_CHECKS=1 FAKE_TMUX_RC=1 zsh $Q
chk "and the launch output says so" sh -c "grep -q 'after tmux ended' $S/state/launch_${C18}_*.out"

echo "--- session probe"
reset; rm $S/state/session_boot_id.txt
case_ "session probe at 350 W" "SESSION OK boot_id $BOOTA" 0 zsh $P
chk "it wrote the boot id" is "$(cat $S/state/session_boot_id.txt)" $BOOTA
case_ "a second probe is refused" "a session probe exists" 2 zsh $P
case_ "RENEW=1 replaces it and keeps the old file" "SESSION OK" 0 RENEW=1 FAKE_BOOT=99999999-2222-3333-4444-555555555555 zsh $P
chk "the replaced file is kept" is "$(nfiles "$S/state/session_boot_id_replaced_*.txt")" 1
reset; rm $S/state/session_boot_id.txt
case_ "420 W: no session" "power limit is not 350.00 W" 4 FAKE_LIMIT=420.00 zsh $P
chk "and no boot id file" test ! -e $S/state/session_boot_id.txt
case_ "another driver: no session" "driver is not 595.99.02" 2 FAKE_DRIVER=600.00 zsh $P
case_ "another uv.lock on the VM: no session" "uv.lock is not the pin's" 2 FAKE_LOCK=abc zsh $P
case_ "a VM tree off the pin: no session" "tree is not the pin" 2 FAKE_TREE=deadbeef zsh $P
case_ "a locked package missing on the Mac: no session" "lacks a locked package" 2 FAKE_UV_ADD=1 zsh $P
case_ "an empty boot id: no session" "no boot id read" 3 FAKE_BOOT=x zsh $P
case_ "SET=1 runs the one root command when the GPU is idle" "sudo_rc 1" 0 SET=1 zsh $P
reset; rm $S/state/session_boot_id.txt
case_ "SET=1 does not touch the limit under another process" "set_skipped" 0 SET=1 FAKE_APPS_N=1 zsh $P

echo "--- the final table"
reset
case_ "no table before any step" "STOP: no table" 2 zsh $F
reset; steps $S18T $S19F; env PATH=$T/bin:$PATH zsh $Q > /dev/null 2>&1
case_ "all five seeds run: recheck, then the table from the worktree" "'cwd': '$T/wt'" 0 zsh $F
chk "the recheck ran with the seal lifted for REG-19 only" grep -q "unseal=REG-19 pattern=\*_l1pl350cl_r2.0_w3000_s1\[5-9\]" $S/state/reg19_recheck_err_*.txt
case_ "the table is computed once" "already computed or tried" 2 zsh $F
reset; steps $S18F; env PATH=$T/bin:$PATH zsh $Q > /dev/null 2>&1
case_ "after a futility stop: eight runs rechecked, then the table" "FINAL (futility stop after seed 18)" 0 FAKE_RECHECK_N=8 zsh $F
reset; steps $S18T $S19F; env PATH=$T/bin:$PATH zsh $Q > /dev/null 2>&1
echo '{"n_runs": 10, "n_changed": 1, "changed": [{"run": "x"}]}' > $T/state/recheck_json
case_ "a run whose validity the recheck changes: no table" "operational stop" 3 zsh $F
chk "and no table file" is "$(nfiles "$S/state/reg19_final_2*.txt")" 0
rm $T/state/recheck_json
case_ "fewer runs rechecked than made: no table" "operational stop" 3 FAKE_RECHECK_N=8 zsh $F
reset; steps $S18T garbage; env PATH=$T/bin:$PATH zsh $Q > /dev/null 2>&1
case_ "after an operational stop between the seeds: no table (N6)" "STOP: no table" 2 zsh $F
reset; steps $S18T $S19F; env PATH=$T/bin:$PATH zsh $Q > /dev/null 2>&1; echo y >> $T/repo/harness/checks.py
case_ "harness/checks.py changed in the working tree: no recheck, no table" "differ in the working tree" 2 zsh $F

echo "passed $pass, failed $fail  (sandbox $T)"
[[ $fail == 0 ]]
