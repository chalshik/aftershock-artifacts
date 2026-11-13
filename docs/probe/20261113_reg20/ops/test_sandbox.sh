#!/bin/zsh
# Sandbox test of REG-20's arm A scripts (in the style of ops_r3/test_sandbox.sh). Nothing real is touched: a
# throwaway git repo stands in for the Mac's (so the REAL mac_checks, gate_in_log, next_step and decide run), a folder
# tree stands in for the VM (so the REAL vm_state.py runs against it), and ssh, rsync, sleep, date, uv, the manifest
# tool and control_due.py are stubs. control_due.py itself is tested by test_control_due.py.
# Usage: zsh docs/probe/20261113_reg20/ops/test_sandbox.sh      (exit 0 if every case passes)
SRC=${0:A:h}
T=$(mktemp -d ${TMPDIR:-/tmp}/reg20_sandbox.XXXXXX) || exit 99
T=${T:A}
[[ $T == *reg20_sandbox.* ]] || exit 99
VM=$T/vmhome/aftershock-artifacts
PD=$T/repo/docs/probe/20261113_reg20
S=$PD/ops
BOOTA=11111111-2222-3333-4444-555555555555
B=burst_l1pl350ol_r2.0_w3000_s; C=stage2_control_l1pl350ol_r2.0_w3000_s; D=burst_l1pl350cl_r2.0_w3000_s15_drift
G=(git -c user.name=sandbox -c user.email=sandbox@example.invalid -c commit.gpgsign=false)
mkdir -p $T/bin $T/state $VM/runs $T/repo && cd $T/repo && git init -q -b main . || exit 99
mkdir -p tools configs runs analysis $S/state docs
echo 'import os, sys; sys.exit(1 if os.environ.get("FAKE_MANIFEST_FAIL") else 0)' > tools/manifest.py
echo x > pyproject.toml; echo x > uv.lock; echo 'runs/' > .gitignore
for f in __init__ k1 gate margin derived floor stats load withheld tables; do echo "# $f (sandbox)" > analysis/$f.py; done
# Configs as at the real pin: REG-20's eleven extend REG-19's partners, which extend a base; defaults.yaml beneath.
print -r -l -- "name: defaults" "workload:" "  duration_s: 999" > configs/defaults.yaml
print -r -l -- "name: base" "workload:" "  duration_s: 1500" "  sessions:" "    closed_loop: true" > configs/base_cl.yaml
for sd in 15 16 17 18 19; do
  for k in burst stage2_control; do
    print -r -l -- "extends: base_cl.yaml" "name: ${k}_l1pl350cl_r2.0_w3000_s$sd" "workload:" "  duration_s: 4080" > configs/${k}_l1pl350cl_r2.0_w3000_s$sd.yaml
    print -r -l -- "extends: ${k}_l1pl350cl_r2.0_w3000_s$sd.yaml" "name: ${k}_l1pl350ol_r2.0_w3000_s$sd" "workload:" "  sessions:" "    closed_loop: false" > configs/${k}_l1pl350ol_r2.0_w3000_s$sd.yaml
  done
done
print -r -l -- "extends: burst_l1pl350cl_r2.0_w3000_s15.yaml" "name: $D" > configs/$D.yaml
$G add -A && $G commit -q -m pin || exit 99
PINH=$(git rev-parse HEAD); LOCKB=$(git rev-parse ${PINH}:uv.lock)
LOADB=$(git hash-object analysis/load.py); WHB=$(git hash-object analysis/withheld.py)
cp $SRC/vm_state.py $SRC/session_probe.sh $SRC/launch.sh $SRC/queue.sh $SRC/final.sh $SRC/control_due.py $S/
sed -e "s|^R=.*|R=$T/repo|" -e "s|^PY=.*|PY=$T/bin/fakepy|" -e "s|^PIN=.*|PIN=$PINH|" \
    -e "s|^SEAL_BLOBS=.*|SEAL_BLOBS=($LOADB $WHB)|" $SRC/common.sh > $S/common.sh
for v in "R=$T/repo" "PY=$T/bin/fakepy" "PIN=$PINH" "SEAL_BLOBS=($LOADB $WHB)"; do grep -qxF -- "$v" $S/common.sh || { echo "sandbox: '$v' not set"; exit 99; }; done
(( $(diff $SRC/common.sh $S/common.sh | grep -c '^>') == 4 )) || { echo "sandbox: common.sh differs in more than four lines"; exit 99; }
LOGOK=("## 2026-11-20 · [RESULT] REG-19: sandbox" "" "## 2026-11-20 · [DECISION] (owner) REG-20 arm A starts: sandbox")
print -r -l -- $LOGOK > docs/decisions.md
$G add -A && $G commit -q -m scripts || exit 99
git log -1 --format=%H -- docs/probe/20261113_reg20/ops/{common.sh,vm_state.py,session_probe.sh,launch.sh,queue.sh,final.sh,control_due.py} > $S/scripts_commit.txt
$G add -A && $G commit -q -m scripts_commit || exit 99
HEADH=$(git rev-parse HEAD)

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
case "$1" in
  sync) echo "Would use project environment at: .venv"; echo "Would uninstall 2 packages"; echo " - a==1"; echo " - b==1"
        [ -n "$FAKE_UV_ADD" ] && echo " + c==2"; exit 0;;
  run) shift; echo "{'fake': 'table', 'args': '$*', 'unseal': '${AFTERSHOCK_UNSEAL:-unset}', 'cwd': '$PWD'}"
       [ -n "$FAKE_FINAL_RC" ] && exit "$FAKE_FINAL_RC"; exit 0;;
  *) echo "fake uv: unhandled $*" >&2; exit 9;;
esac
EOS
cat > $T/bin/fakepy <<'EOS'
#!/bin/zsh
ST=__T__/state
case "$*" in
  *control_due.py*)
    n=$(( $(cat $ST/due_n 2>/dev/null || echo 0) + 1 )); echo $n > $ST/due_n; echo "${AFTERSHOCK_UNSEAL-unset} ${@[-1]}" >> $ST/due_env
    [[ -n $FAKE_DUE_RC ]] && { echo "Traceback (fake)" >&2; exit $FAKE_DUE_RC; }
    [[ -n $FAKE_DUE_ERRLINE ]] && echo "ValueError: fake" >&2
    [[ -n $FAKE_DUE_OUT ]] && { print -r -- "$FAKE_DUE_OUT"; exit 0; }
    rid=${@[-1]}; sd=${rid##*_s}; v=$(sed -n "$((sd - 14))p" $ST/due 2>/dev/null); echo "CONTROL_DUE ${v:-no}";;
  *) echo "fakepy: unhandled $*" >&2; exit 9;;
esac
EOS
cat > $T/bin/rsync <<'EOS'
#!/bin/zsh
src=${@[-2]}; rid=${src:t}
echo "${AFTERSHOCK_UNSEAL-unset}" >> __T__/state/rsync_env
[[ -n $FAKE_RSYNC_FAIL ]] && exit 1
mkdir -p runs/$rid && cp -R __T__/vmhome/aftershock-artifacts/runs/$rid/ runs/$rid/
EOS
cat > $T/bin/ssh <<'EOS'
#!/bin/zsh
cmd=${@[-1]}; ST=__T__/state; VM=__T__/vmhome/aftershock-artifacts
case $cmd in
  "python3 - "*) [[ -n $FAKE_STATE_DOWN ]] && exit 255; HOME=__T__/vmhome python3 - ${=cmd#python3 - };;
  *"up_since"*)
    echo "2026-11-20T00:00:00+00:00"; echo "boot_id ${FAKE_BOOT:-__BOOT__}"; echo "up_since 2026-11-19 19:48:00"; echo "kernel 6.8.0-fake"
    echo "driver ${FAKE_DRIVER:-595.99.02}"; echo "governor performance"; echo "limit_before ${FAKE_LIMIT_BEFORE:-420.00} W"; echo "apps ${FAKE_APPS_N:-0}"
    echo "boots -1 aaa;0 bbb;"; echo "prev_boot_kernel Linux version 6.8.0-fake"; echo "prev_boot_nvidia NVIDIA UNIX x86_64 Kernel Module  595.99.02";;
  *"sudo -n nvidia-smi -pl 350"*) echo "sudo: a password is required"; echo "sudo_rc 1";;
  *"limit_after"*)
    echo "limit_after ${FAKE_LIMIT:-350.00} W"; echo "tree ${FAKE_TREE:-__PIN__} dirty ${FAKE_DIRTY:-0}"; echo "lock_blob ${FAKE_LOCK:-__LOCK__}"; echo "free_kb ${FAKE_FREE:-5000000}";;
  *"pre-launch read"*)
    n=$(( $(cat $ST/pre_n 2>/dev/null || echo 0) + 1 )); echo $n > $ST/pre_n
    [[ -n $FAKE_PRELAUNCH_FAIL ]] && exit 255
    [[ -n $FAKE_PRELAUNCH_FAIL_FROM ]] && (( n >= FAKE_PRELAUNCH_FAIL_FROM )) && exit 255
    nof=65536; [[ -n $FAKE_NOFILE && $cmd == *${FAKE_NOFILE_FOR:-}* ]] && nof=$FAKE_NOFILE
    echo "# pre-launch read (fake)"; echo "2026-11-20T00:00:00+00:00"; echo "power.limit [W], temperature.gpu, utilization.gpu [%], memory.used [MiB]"
    echo "${FAKE_LIMIT:-350.00} W, ${FAKE_TEMP:-40}, 0 %, 1 MiB"; echo "# compute apps:"; [[ -n $FAKE_APPS ]] && echo "4242, python, 100 MiB"
    echo "# tree:"; echo "${FAKE_TREE:-__PIN__}"; echo "${FAKE_DIRTY:-0}"; echo "# boot:"; if [[ -n $FAKE_BOOT_EMPTY ]]; then echo ""; else echo "${FAKE_BOOT:-__BOOT__}"; fi
    echo "# free_kb:"; echo "${FAKE_FREE:-5000000}"; echo "# nofile:"; echo "${FAKE_NOFILE_HARD:-1048576}"; print -r -- "$nof"
    echo "# tmux:"; [[ -n $FAKE_TMUX_EXISTS ]] && echo "run: 1 windows" || echo "no server running on /tmp/tmux-1000/default";;
  *"temperature.gpu --format=csv,noheader"*) [[ -n $FAKE_TEMP_FAIL ]] && exit 255; echo "${FAKE_TEMP:-40}";;
  *"tmux new-session"*)
    [[ -n $FAKE_LAUNCH_FAIL ]] && exit 255
    n=$(( $(cat $ST/launch_n 2>/dev/null || echo 0) + 1 )); echo $n > $ST/launch_n
    cfg=$(print -r -- $cmd | sed -n 's|.*configs/\([^ ]*\)\.yaml.*|\1|p'); rid=20261120-$(printf %06d $n)_$cfg; echo $rid > $ST/rid
    print -r -- $cfg >> $ST/launched; print -r -- "$cmd" >> $ST/tmux_cmds
    mkdir -p $VM/runs/$rid; echo "{}" > $VM/runs/$rid/requests.jsonl; echo "name: $cfg" > $VM/runs/$rid/config.yaml
    echo "{\"git_commit\": \"${FAKE_COMMIT:-__PIN__}\"}" > $VM/runs/$rid/env.json
    o=$(sed -n "${n}p" $ST/outcomes 2>/dev/null)
    [[ -z $o && -n $FAKE_FAILED && $cfg == *${FAKE_FAILED_FOR:-}* ]] && o=$FAKE_FAILED
    [[ -n $FAKE_NO_CHECKS ]] && o=lost
    case $o in
      ""|ok) echo '{"valid": true, "failed": [], "checks": []}' > $VM/runs/$rid/checks.json;;
      lost) ;;
      no_errors) echo '{"valid": false, "failed": ["no_errors"], "checks": [{"name": "no_errors", "passed": false, "detail": {"ok": 9, "client_error": 2}}]}' > $VM/runs/$rid/checks.json;;
      no_errors_http) echo '{"valid": false, "failed": ["no_errors"], "checks": [{"name": "no_errors", "passed": false, "detail": {"ok": 9, "http_error": 2}}]}' > $VM/runs/$rid/checks.json;;
      *) echo "{\"valid\": false, \"failed\": [\"$o\"], \"checks\": []}" > $VM/runs/$rid/checks.json;;
    esac;;
  *"'^nofile '"*) [[ -n $FAKE_NOFILE_NOLINE ]] && exit 1; [[ $(tail -1 $ST/tmux_cmds) == *"ulimit -n 65536"* ]] && echo "nofile ${FAKE_NOFILE_LOG:-65536}";;
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
  [[ $T == *reg20_sandbox.* ]] || exit 99
  rm -rf $T/state/* $T/repo/runs/* $PD/prelaunch_* $PD/session_* $VM/runs/*
  (cd $T/repo && git reset -q --hard $HEADH && git clean -fdq docs/probe/20261113_reg20/ops/state)
  mkdir -p $S/state && print -r -- $BOOTA > $S/state/session_boot_id.txt
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
is() { [[ $1 == $2 ]]; }
mkrun() {   # a hand-made run folder on the fake VM: run id, checks.json text ("" for none), commit (default: the pin)
  mkdir -p $VM/runs/$1; echo "{\"git_commit\": \"${3:-$PINH}\"}" > $VM/runs/$1/env.json
  [[ -z $2 ]] || print -r -- $2 > $VM/runs/$1/checks.json
}
VALID='{"valid": true, "failed": [], "checks": []}'
launches() { cat $T/state/launch_n 2>/dev/null || echo 0; }
looks() { cat $T/state/due_n 2>/dev/null || echo 0; }
nfiles() { setopt localoptions null_glob; local f=($~1); echo ${#f}; }
order() { [[ -f $T/state/launched ]] && sed -e "s/^${B}/B/" -e "s/^${C}/C/" -e "s/^${D}\$/D/" $T/state/launched | tr '\n' ' ' | sed 's/ $//'; }
dues() { print -l -- "$@" > $T/state/due; }
outs() { print -l -- "$@" > $T/state/outcomes; }
rid_of() { echo 20261120-$(printf %06d $1)_$2; }   # the run id the fake gives launch number $1 of config $2
setlog() { (cd $T/repo && print -r -l -- "$@" > docs/decisions.md && $G commit -q -am log); }
q() { env PATH=$T/bin:$PATH "$@" zsh $Q > /dev/null 2>&1; }      # run the queue quietly, for set-ups
Q=$S/queue.sh; L=$S/launch.sh; F=$S/final.sh; P=$S/session_probe.sh

echo "--- the gate: two headings in HEAD's docs/decisions.md, REG-19's [RESULT] first"
reset; setlog "## 2026-11-20 · [DECISION] (owner) REG-20 arm A starts: sandbox"
case_ "no [RESULT] REG-19 heading: no queue" "no '[RESULT] REG-19' heading" 2 zsh $Q
reset; setlog "## 2026-11-20 · [RESULT] REG-19: sandbox"
case_ "no heading that starts arm A: no queue" "REG-20 arm A starts' heading" 2 zsh $Q
reset; setlog "## 2026-11-20 · [DECISION] (owner) REG-20 arm A starts: sandbox" "## 2026-11-20 · [RESULT] REG-19: sandbox"
case_ "the start heading before REG-19's [RESULT]: no queue" "is not after REG-19's [RESULT]" 2 zsh $Q
reset; setlog "## 2026-11-20 · [RESULT] REG-190: sandbox" "## 2026-11-20 · [DECISION] (owner) REG-20 arm A starts: sandbox"
case_ "a [RESULT] of REG-190 is not REG-19's" "no '[RESULT] REG-19' heading" 2 zsh $Q
reset; setlog "## 2026-11-20 · [RESULT] REG-19: sandbox" "## 2026-11-20 · [DECISION] (agent) REG-20 arm A starts: sandbox"
case_ "a start decision that is neither (owner) nor (delegate): no queue" "REG-20 arm A starts' heading" 2 zsh $Q
reset; setlog "## 2026-11-20 · [RESULT] REG-19: sandbox" "- [DECISION] (owner) REG-20 arm A starts, quoted in a list"
case_ "a start decision quoted, not a heading: no queue" "REG-20 arm A starts' heading" 2 zsh $Q
reset; setlog "nothing yet"; print -r -l -- $LOGOK > $T/repo/docs/decisions.md
case_ "both headings in the working tree but not committed: no queue" "no '[RESULT] REG-19' heading" 2 zsh $Q
case_ "and no launch by hand either" "STOP: no '[RESULT] REG-19' heading" 2 zsh $L ${B}15
chk "none of these launched anything" is "$(launches)" 0
reset; setlog "## 2026-11-20 · [RESULT] REG-19: sandbox" "## 2026-11-21 · [OPS] something else" "## 2026-11-21 · [DECISION] (delegate) REG-20 arm A starts: k1.reg20_a_may_start passed"
case_ "(delegate) and an entry between them: the queue runs" "QUEUE DONE" 0 zsh $Q

echo "--- the order: 15, 16, 17, the drift run, 18, 19; a control right after its burst run only when due"
reset; dues no no no no no
case_ "no control due anywhere" "QUEUE DONE" 0 zsh $Q
chk "order B15 B16 B17 D B18 B19" is "$(order)" "B15 B16 B17 D B18 B19"
chk "one control decision per open burst run, five" is "$(wc -l < $S/state/control_due.txt | tr -d ' ')" 5
chk "each made with the seal lifted for REG-20, on its own run" sh -c "[ \$(grep -c '^REG-20 20261120-' $T/state/due_env) = 5 ]"
chk "the queue's own shell does not carry AFTERSHOCK_UNSEAL" sh -c "! grep -qv '^unset$' $T/state/rsync_env"
chk "the end record lists the six slots" is "$(head -6 $S/state/queue_done.txt | cut -d' ' -f1 | tr '\n' ' ')" "s15 s16 s17 drift s18 s19 "
case_ "started again after the end: same end" "QUEUE DONE" 0 zsh $Q
chk "nothing launched again, no second look" is "$(launches) $(looks)" "6 5"
reset; dues yes yes yes yes yes
case_ "a control due everywhere" "QUEUE DONE" 0 zsh $Q
chk "order B15 C15 B16 C16 B17 C17 D B18 C18 B19 C19" is "$(order)" "B15 C15 B16 C16 B17 C17 D B18 C18 B19 C19"
chk "the end record names each control" is "$(grep -c 'CONTROL_DUE yes control 20261120-' $S/state/queue_done.txt)" 5
reset; dues unclear unclear unclear unclear unclear
case_ "unclear everywhere" "QUEUE DONE" 0 zsh $Q
chk "unclear runs no control: B15 B16 B17 D B18 B19" is "$(order)" "B15 B16 B17 D B18 B19"
reset; dues yes no unclear yes no
case_ "mix 1 (yes no unclear yes no)" "QUEUE DONE" 0 zsh $Q
chk "order B15 C15 B16 B17 D B18 C18 B19" is "$(order)" "B15 C15 B16 B17 D B18 C18 B19"
reset; dues no unclear yes no unclear
case_ "mix 2 (no unclear yes no unclear)" "QUEUE DONE" 0 zsh $Q
chk "the drift run after seed 17's control: B15 B16 B17 C17 D B18 B19" is "$(order)" "B15 B16 B17 C17 D B18 B19"
reset; dues unclear yes no unclear yes
case_ "mix 3 (unclear yes no unclear yes)" "QUEUE DONE" 0 zsh $Q
chk "order B15 B16 C16 B17 D B18 B19 C19" is "$(order)" "B15 B16 C16 B17 D B18 B19 C19"
chk "the records keep each decision: s15 unclear, s16 yes, s17 no" is "$(cut -d' ' -f3 $S/state/control_due.txt | head -3 | tr '\n' ' ')" "unclear yes no "
chk "six slots in the end record" is "$(grep -c '^s1[5-9] \|^drift ' $S/state/queue_done.txt)" 6

echo "--- the control decision: one line, once, or a stop"
reset; dues yes
case_ "a decision line with a number in it" "printed something other than one CONTROL_DUE line" 1 FAKE_DUE_OUT="CONTROL_DUE yes 0.83" zsh $Q
chk "is not recorded" test ! -e $S/state/control_due.txt
chk "and runs no control" is "$(launches)" 1
case_ "two lines" "printed something other than one CONTROL_DUE line" 1 FAKE_DUE_OUT=$'CONTROL_DUE no\nreuse 0.1' zsh $Q
case_ "another word" "printed something other than one CONTROL_DUE line" 1 FAKE_DUE_OUT="CONTROL_DUE maybe" zsh $Q
case_ "a failed control_due.py" "control_due.py failed" 1 FAKE_DUE_RC=1 zsh $Q
case_ "an error line on its stderr" "wrote an error line" 1 FAKE_DUE_ERRLINE=1 zsh $Q
chk "none of these recorded a decision" test ! -e $S/state/control_due.txt
case_ "after the fix the queue goes on without relaunching seed 15" "QUEUE DONE" 0 zsh $Q
chk "seed 15's control ran: B15 C15 B16 B17 D B18 B19" is "$(order)" "B15 C15 B16 B17 D B18 B19"
reset; dues no; q FAKE_PRELAUNCH_FAIL_FROM=2                       # seed 15 run, decided 'no'; seed 16 not launched
chk "set-up: one launch, one decision" is "$(launches) $(looks)" "1 1"
sed -n 1p $S/state/control_due.txt >> $S/state/control_due.txt
case_ "two decisions recorded for one run stop the queue" "holds 2 decisions" 1 zsh $Q
reset; dues no; q FAKE_PRELAUNCH_FAIL_FROM=2; mkrun 20261120-090000_${C}15 $VALID
case_ "a control on the VM although none is due stops the queue" "seed 15's control has a run or an attempt although none is due" 1 zsh $Q
reset; dues no; q FAKE_PRELAUNCH_FAIL_FROM=2; echo x > $S/state/attempt_${C}15_1.txt
case_ "a control attempt record although none is due stops the queue" "although none is due" 1 zsh $Q
reset; dues no; q FAKE_PRELAUNCH_FAIL_FROM=2
case_ "launch.sh by hand: a control not due is refused" "it is not ${C}15's turn" 2 zsh $L ${C}15
chk "no second look on seed 15" is "$(looks)" 1

echo "--- reruns: one, then a stop"
reset; outs client_lag
case_ "an invalid open burst run stops the queue and names the failed check" "RUN ${B}15 $(rid_of 1 ${B}15) INVALID failed=client_lag" 1 zsh $Q
case_ "started again: copied, rerun once, valid, and the queue goes on" "QUEUE DONE" 0 zsh $Q
chk "attempt 2 of seed 15" test -e $S/state/attempt_${B}15_2.txt
chk "the invalid run is on the Mac, verified (k1 counts it)" test -e $S/state/copied_$(rid_of 1 ${B}15).txt -a -d $T/repo/runs/$(rid_of 1 ${B}15)
chk "no control decision on the invalid run" sh -c "! grep -q '$(rid_of 1 ${B}15)' $S/state/control_due.txt"
reset; dues yes; outs ok client_lag client_lag
case_ "a control invalid" "RUN ${C}15 $(rid_of 2 ${C}15) INVALID failed=client_lag" 1 zsh $Q
case_ "its rerun invalid" "RUN ${C}15 $(rid_of 3 ${C}15) INVALID failed=client_lag" 1 zsh $Q
case_ "then a stop: the control's two attempts are spent" "the 2 attempts of ${C}15 are spent" 1 zsh $Q
chk "three launches" is "$(launches)" 3
reset; outs ok ok ok client_lag client_lag
case_ "the drift run invalid" "RUN $D $(rid_of 4 $D) INVALID" 1 zsh $Q
case_ "its rerun invalid" "RUN $D $(rid_of 5 $D) INVALID" 1 zsh $Q
case_ "then a stop: the drift run's two attempts are spent" "the 2 attempts of $D are spent" 1 zsh $Q
reset; dues yes yes; outs client_lag client_lag
case_ "an open burst run invalid" "INVALID failed=client_lag" 1 zsh $Q
case_ "and invalid again" "INVALID failed=client_lag" 1 zsh $Q
case_ "is lost_open (REG-20 counts it cold): the queue goes on to seed 16" "QUEUE DONE" 0 zsh $Q
chk "no control for the lost seed: B15 B15 B16 C16 B17 D B18 B19" is "$(order)" "B15 B15 B16 C16 B17 D B18 B19"
chk "the end record says lost_open with both runs" grep -q "^s15 lost_open $(rid_of 1 ${B}15) $(rid_of 2 ${B}15)$" $S/state/queue_done.txt
chk "both invalid runs are on the Mac, verified" test -e $S/state/copied_$(rid_of 1 ${B}15).txt -a -e $S/state/copied_$(rid_of 2 ${B}15).txt
chk "no look at the lost seed" is "$(looks)" 4
reset; outs no_errors
case_ "a client error" "INVALID failed=no_errors/client_error" 1 zsh $Q
case_ "is not rerun: stop and ask" "stop and ask after no_errors/client_error" 1 zsh $Q
chk "one launch" is "$(launches)" 1
echo "owner: rerun (sandbox)" > $S/state/rerun_ok_$(rid_of 1 ${B}15).txt
case_ "with the owner's rerun_ok record it is rerun" "QUEUE DONE" 0 zsh $Q
chk "as attempt 2" test -e $S/state/attempt_${B}15_2.txt
reset; outs no_errors no_errors; echo x > $S/state/rerun_ok_$(rid_of 1 ${B}15).txt
q; q
case_ "a second client error after an allowed rerun stops again" "stop and ask after no_errors/client_error ($(rid_of 2 ${B}15))" 1 zsh $Q
echo "owner: go on (sandbox)" > $S/state/rerun_ok_$(rid_of 2 ${B}15).txt
case_ "with a record for it the seed is lost_open and the queue goes on" "QUEUE DONE" 0 zsh $Q
reset; outs no_errors_http
case_ "an http error is an invalid run like any other" "INVALID failed=no_errors/other" 1 zsh $Q
case_ "and is rerun" "QUEUE DONE" 0 zsh $Q
reset; outs manipulation
case_ "a burst that did not fill the pool" "INVALID failed=manipulation" 1 zsh $Q
case_ "is not rerun: stop and ask" "stop and ask after manipulation" 1 zsh $Q
reset; outs power_limit
case_ "a run at another power limit" "INVALID failed=power_limit" 1 zsh $Q
case_ "is not rerun: stop and ask" "stop and ask after power_limit" 1 zsh $Q
reset; outs gpu_steady ok gpu_steady
case_ "a heat failure" "INVALID failed=gpu_steady" 1 zsh $Q
case_ "is rerun once; a second heat failure on another run" "INVALID failed=gpu_steady" 1 zsh $Q
case_ "stops the queue" "second heat failure" 1 zsh $Q
reset
case_ "tmux gone without checks.json (a lost run)" "TMUX GONE, no checks.json" 1 FAKE_NO_CHECKS=1 FAKE_TMUX_RC=1 zsh $Q
case_ "is not rerun without a record" "a rerun needs its own decision" 1 zsh $Q
echo "owner: rerun (sandbox)" > $S/state/rerun_ok_$(rid_of 1 ${B}15).txt
case_ "with the record it is rerun as attempt 2" "QUEUE DONE" 0 zsh $Q
chk "the lost run is not copied" test ! -e $T/repo/runs/$(rid_of 1 ${B}15)
reset; mkrun 20261120-090000_${B}15 $VALID; mkrun 20261120-100000_${B}15 $VALID; echo x > $S/state/attempt_${B}15_1.txt; echo x > $S/state/attempt_${B}15_2.txt
case_ "two valid runs of one config stop the queue" "holds 2 valid runs" 1 zsh $Q
reset; mkrun 20261120-090000_${B}15 $VALID
case_ "a run folder with no attempt record is a launch outside these scripts" "only 0 attempts are recorded" 1 zsh $Q
reset; mkrun 20261120-090000_${B}15 '{"valid": true, "failed": ["x"], "checks": []}'; echo x > $S/state/attempt_${B}15_1.txt
case_ "a checks.json that contradicts itself stops the queue" "cannot be read" 1 zsh $Q
reset
case_ "a run made at another commit is not used" "not at the pin" 1 FAKE_COMMIT=deadbeef zsh $Q
reset; dues no; q FAKE_PRELAUNCH_FAIL_FROM=2; [[ $T == *reg20_sandbox.* ]] && rm -rf $VM/runs/$(rid_of 1 ${B}15)
case_ "a run on the Mac that the VM no longer lists is not made again" "which the VM does not list" 1 zsh $Q
chk "no second launch" is "$(launches)" 1

echo "--- the open-file limit"
reset
case_ "an open burst run with the raised limit at 1024" "reads '1024' (hard '1048576'); REG-20 needs at least 4096" 1 FAKE_NOFILE=1024 zsh $Q
chk "spends no attempt" test ! -e $S/state/attempt_${B}15_1.txt
case_ "at 4095" "reads '4095'" 1 FAKE_NOFILE=4095 zsh $Q
case_ "a limit that cannot be raised" "REG-20 needs at least 4096" 1 FAKE_NOFILE="bash: ulimit: open files: cannot modify limit: Operation not permitted" zsh $Q
chk "none launched" is "$(launches)" 0
case_ "at exactly 4096 the queue runs" "QUEUE DONE" 0 FAKE_NOFILE=4096 zsh $Q
reset; dues yes
case_ "a control is an open-loop run: 1024 stops it" "the open-file limit after 'ulimit -n 65536' reads '1024'" 1 FAKE_NOFILE=1024 FAKE_NOFILE_FOR=$C zsh $Q
chk "after its burst run" is "$(order)" "B15"
reset
case_ "the closed drift run at 1024 is only recorded" "QUEUE DONE" 0 FAKE_NOFILE=1024 FAKE_NOFILE_FOR=_drift zsh $Q
chk "its attempt record holds the read" grep -qx "nofile_raised 1024" $S/state/attempt_${D}_1.txt
chk "an open run's record holds the read and the log's nofile line" sh -c "grep -qx 'nofile_raised 65536' $S/state/attempt_${B}15_1.txt && grep -qx 'nofile_log 65536' $S/state/attempt_${B}15_1.txt"
chk "the drift's record has no log line (its command sets no limit)" sh -c "! grep -q nofile_log $S/state/attempt_${D}_1.txt"
chk "the open launch command starts with the limit and execs the harness" grep -qF "tmux new-session -d -s run 'ulimit -n 65536 && echo \"nofile \$(ulimit -n)\" > ~/${B}15_" $T/state/tmux_cmds
chk "and the harness writes to the same log" grep -qF "&& exec ~/.local/bin/uv run python -m harness.run configs/${B}15.yaml >> ~/${B}15_" $T/state/tmux_cmds
chk "the drift's launch command is ops_r3's, with no limit" sh -c "grep -F 'configs/$D.yaml' $T/state/tmux_cmds | grep -qF \"run '~/.local/bin/uv run python -m harness.run configs/$D.yaml > ~/\" && ! grep -F 'configs/$D.yaml' $T/state/tmux_cmds | grep -q ulimit"
reset
case_ "a launch log whose nofile line is low: the run goes on, then the queue stops and asks" "did not show an open-file limit of at least 4096" 1 FAKE_NOFILE_LOG=1024 zsh $Q
chk "the warning names the line" grep -q "WARN: the launch log's nofile line reads 'nofile 1024'" $S/state/launch_${B}15_*.out
chk "the attempt record keeps it" grep -qx "nofile_log 1024" $S/state/attempt_${B}15_1.txt
case_ "started again: the run is used and the queue goes on" "QUEUE DONE" 0 zsh $Q
chk "six launches" is "$(launches)" 6
reset
case_ "a launch log with no nofile line stops the same way" "did not show an open-file limit" 1 FAKE_NOFILE_NOLINE=1 zsh $Q
chk "recorded as '-'" grep -qx "nofile_log -" $S/state/attempt_${B}15_1.txt

echo "--- any hour: the owner withdrew the quiet hours (2026-11-13); no start is held back for the time of day"
for hh in 0000 0200 0230 0459 1145 1300 1415 1600 1759 2359 abcd; do
  reset; dues yes no unclear yes no
  case_ "the whole queue, controls included, with the clock at $hh UTC" "QUEUE DONE" 0 FAKE_HHMM=$hh zsh $Q
done
chk "eight launches in the last of them: B15 C15 B16 B17 D B18 C18 B19" is "$(order)" "B15 C15 B16 B17 D B18 C18 B19"
reset; dues yes; q FAKE_PRELAUNCH_FAIL_FROM=2                  # seed 15's burst run made, its control next
case_ "a control due at 13:00 UTC starts" "QUEUE DONE" 0 FAKE_HHMM=1300 zsh $Q
reset; q FAKE_PRELAUNCH_FAIL_FROM=4                            # three open burst runs made, the drift run next
chk "set-up: the drift run is next" is "$(order)" "B15 B16 B17"
case_ "the drift run at 02:00 UTC starts" "QUEUE DONE" 0 FAKE_HHMM=0200 zsh $Q
chk "no script reads the clock as an hour" sh -c "! grep -n 'date -u +%H%M' $S/common.sh $S/launch.sh $S/queue.sh $S/final.sh $S/session_probe.sh"

echo "--- pre-launch stops spend no attempt (as ops_r3)"
reset
case_ "420 W" "STOP: power limit '420.00'" 1 FAKE_LIMIT=420.00 zsh $Q
chk "no attempt, the probe kept" is "$(nfiles "$S/state/attempt_*") $(nfiles "$PD/prelaunch_reg20_${B}15_*.txt")" "0 1"
case_ "the same command then runs, as attempt 1" "QUEUE DONE" 0 zsh $Q
reset
case_ "a reboot since the session probe" "rebooted since the session probe" 1 FAKE_BOOT=99999999-2222-3333-4444-555555555555 zsh $Q
case_ "an empty boot id" "rebooted since the session probe (boot id '')" 1 FAKE_BOOT_EMPTY=1 zsh $Q
case_ "another compute process" "GPU compute process present" 1 FAKE_APPS=1 zsh $Q
case_ "the wrong pin on the VM (REG-19's a7bb77a)" "STOP: VM tree 'a7bb77abc863adcaad9d4516815a5ddddf2908e9'" 1 FAKE_TREE=a7bb77abc863adcaad9d4516815a5ddddf2908e9 zsh $Q
case_ "a dirty VM tree" "dirty='3'" 1 FAKE_DIRTY=3 zsh $Q
case_ "low disk" "kB free on the VM" 1 FAKE_FREE=1000 zsh $Q
case_ "a temperature that is not a number" "is not a number" 1 FAKE_TEMP=N/A zsh $Q
case_ "a GPU still hot after the wait" "STOP: GPU at '60' C" 1 FAKE_TEMP=60 zsh $Q
case_ "a temperature that cannot be read" "could not be read (temperature)" 1 FAKE_TEMP_FAIL=1 zsh $Q
case_ "a pre-launch read that fails" "the pre-launch read failed" 1 FAKE_PRELAUNCH_FAIL=1 zsh $Q
case_ "an existing tmux session" "a tmux session exists" 1 FAKE_TMUX_EXISTS=1 zsh $Q
rm $S/state/session_boot_id.txt
case_ "no session probe, no launch" "no session probe" 1 zsh $Q
chk "none of these launched anything" is "$(launches)" 0

echo "--- what a started run can leave behind (as ops_r3)"
reset
case_ "no run id within 120 s" "no run id" 1 FAKE_NO_RID=1 zsh $Q
chk "the attempt is spent" test -e $S/state/attempt_${B}15_1.txt
case_ "started again: the finished valid run is used, not relaunched" "QUEUE DONE" 0 zsh $Q
chk "six launches in all" is "$(launches)" 6
reset
case_ "a run still going after the wait is not called invalid" "STILL RUNNING" 1 FAKE_NO_CHECKS=1 WAIT_MIN=2 zsh $Q
reset
case_ "a VM that stops answering is reported as such" "VM NOT REACHABLE" 1 FAKE_DOWN_ON_WAIT=1 WAIT_MIN=3 zsh $Q
reset
case_ "the launch command failing spends the attempt" "the launch command failed" 1 FAKE_LAUNCH_FAIL=1 zsh $Q
chk "and says so in the record" grep -q launch_command_failed $S/state/attempt_${B}15_1.txt
case_ "started again: attempt 2 runs" "QUEUE DONE" 0 zsh $Q
chk "attempt 2 recorded" test -e $S/state/attempt_${B}15_2.txt
reset
case_ "checks.json appearing just after tmux ended is found" "QUEUE DONE" 0 FAKE_LATE_CHECKS=1 FAKE_TMUX_RC=1 zsh $Q
reset
case_ "the VM's state unreadable stops the queue" "could not be read" 1 FAKE_STATE_DOWN=1 zsh $Q

echo "--- copy and checksums"
reset
case_ "a checksum mismatch stops the queue before any decision" "checksum mismatch" 1 FAKE_BAD_SHA=1 zsh $Q
chk "no copy record, no look" is "$(nfiles "$S/state/copied_*") $(looks)" "0 0"
case_ "started again: copied, verified, and on" "QUEUE DONE" 0 zsh $Q
reset
case_ "a failed copy" "copy failed" 1 FAKE_RSYNC_FAIL=1 zsh $Q
case_ "the VM's checksums unreadable" "checksums of $(rid_of 1 ${B}15) could not be read" 1 FAKE_SHA_FAIL=1 zsh $Q
case_ "a manifest update that fails" "manifest update failed" 1 FAKE_MANIFEST_FAIL=1 zsh $Q
chk "leaves no copy record" is "$(nfiles "$S/state/copied_*")" 0
case_ "started again: on" "QUEUE DONE" 0 zsh $Q
chk "one launch of seed 15 in all" is "$(grep -c "^${B}15\$" $T/state/launched)" 1

echo "--- the Mac-side checks (real git)"
reset; echo "# y" >> $T/repo/analysis/k1.py
case_ "k1.py changed in the working tree" "differs from the pin in the working tree" 2 zsh $Q
reset; (cd $T/repo && echo "# y" >> analysis/gate.py && $G commit -q -am "gate moved")
case_ "gate.py changed by a commit after the pin" "differs from the pin in the working tree" 2 zsh $Q
reset; echo "# y" >> $T/repo/analysis/load.py
case_ "the seal's load.py not the recorded blob" "analysis/load.py is not the blob" 2 zsh $Q
reset; (cd $T/repo && echo "# y" >> analysis/withheld.py && $G commit -q -am "seal moved")
case_ "withheld.py changed by a commit" "analysis/withheld.py is not the blob" 2 zsh $Q
reset; echo "# y" >> $T/repo/analysis/tables.py
case_ "a file outside k1's import closure may change" "QUEUE DONE" 0 zsh $Q
reset; echo y >> $T/repo/uv.lock
case_ "uv.lock changed in the working tree" "differ from the pin in the working tree" 2 zsh $Q
reset; echo "# y" >> $S/queue.sh
case_ "a script changed since its commit" "differs from its committed text" 2 zsh $Q
reset; echo "# y" >> $S/control_due.py
case_ "control_due.py changed since its commit" "differs from its committed text" 2 zsh $Q
reset; rm $S/scripts_commit.txt
case_ "scripts_commit.txt missing" "no scripts_commit.txt" 2 zsh $Q
reset; echo deadbeef > $S/scripts_commit.txt
case_ "scripts_commit.txt naming another commit" "changed since scripts_commit.txt" 2 zsh $Q
chk "none of these launched anything" is "$(launches)" 0

echo "--- launch.sh by hand"
reset
case_ "a config that is not next is refused" "it is not ${B}16's turn: the next step is 'launch ${B}15'" 2 zsh $L ${B}16
case_ "the drift run first is refused" "it is not ${D}'s turn" 2 zsh $L $D
case_ "a REG-19 config is refused" "is not one of REG-20 arm A's eleven configs" 2 zsh $L burst_l1pl350cl_r2.0_w3000_s15
case_ "arm B is refused" "is not one of REG-20 arm A's eleven configs" 2 zsh $L burst_l1pl350ol_r2.5_w3000_s15
case_ "a name that is no config is refused" "is not one of REG-20 arm A's eleven configs" 2 zsh $L nonsense
case_ "the next config is launched with the attempt number derived" "LAUNCHED $(rid_of 1 ${B}15) (attempt 1)" 0 zsh $L ${B}15
case_ "after it, a launch by hand waits for the queue's copy" "the next step is 'copy $(rid_of 1 ${B}15)'" 2 zsh $L ${B}16

echo "--- the lock and the settings (as ops_r3)"
reset; mkdir -p $S/state/queue.lock; echo $$ > $S/state/queue.lock/pid
case_ "a second queue beside a running one is refused" "another queue is running" 1 zsh $Q
reset; mkdir -p $S/state/queue.lock; echo 999999 > $S/state/queue.lock/pid
case_ "a lock left by a dead queue is set aside and the queue runs" "QUEUE DONE" 0 zsh $Q
chk "the stale lock is kept under another name" is "$(nfiles "$S/state/queue.lock.stale_*")" 1
reset
case_ "WAIT_MIN that is not a number stops before anything" "WAIT_MIN is not a number" 2 WAIT_MIN=abc zsh $Q

echo "--- session probe (as ops_r3)"
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
case_ "the VM at REG-19's pin: no session" "tree is not the pin" 2 FAKE_TREE=a7bb77abc863adcaad9d4516815a5ddddf2908e9 zsh $P
case_ "a dirty VM tree: no session" "tree is not the pin" 2 FAKE_DIRTY=1 zsh $P
case_ "a locked package missing on the Mac: no session" "lacks a locked package" 2 FAKE_UV_ADD=1 zsh $P
case_ "an empty boot id: no session" "no boot id read" 3 FAKE_BOOT=x zsh $P
case_ "SET=1 runs the one root command when the GPU is idle" "sudo_rc 1" 0 SET=1 zsh $P
reset; rm $S/state/session_boot_id.txt
case_ "SET=1 does not touch the limit under another process" "set_skipped" 0 SET=1 FAKE_APPS_N=1 zsh $P

echo "--- the final table"
reset
case_ "no table before the queue has ended" "STOP: no table. The queue has not ended" 2 zsh $F
reset; q FAKE_PRELAUNCH_FAIL_FROM=4
case_ "nor mid-matrix" "STOP: no table. The queue has not ended" 2 zsh $F
reset; dues yes no no no no; q
case_ "after QUEUE DONE: the registered command, seal lifted for REG-20, from the repo root" "{'fake': 'table', 'args': 'python -m analysis.k1 reg20', 'unseal': 'REG-20', 'cwd': '$T/repo'}" 0 zsh $F
chk "both files written" is "$(nfiles "$S/state/reg20_final_2*.txt") $(nfiles "$S/state/reg20_final_err_*.txt")" "1 1"
case_ "the table is computed once" "already computed or tried" 2 zsh $F
reset; q; mkdir -p $S/state/queue.lock; echo $$ > $S/state/queue.lock/pid
case_ "not while a queue holds the lock" "a queue is running" 2 zsh $F
reset; q; rm $S/state/copied_$(rid_of 3 ${B}17).txt
case_ "not when a run the end record names has no verified copy" "has no verified copy on the Mac" 2 zsh $F
reset; q
case_ "a failed table stops and keeps its files" "STOP: reg20 failed" 1 FAKE_FINAL_RC=1 zsh $F
case_ "and a second try is refused" "already computed or tried" 2 zsh $F
reset; q; setlog "## 2026-11-20 · [RESULT] REG-19: sandbox"
case_ "not without the gate's headings" "REG-20 arm A starts' heading" 2 zsh $F

echo "passed $pass, failed $fail  (sandbox $T)"
[[ $fail == 0 ]]
