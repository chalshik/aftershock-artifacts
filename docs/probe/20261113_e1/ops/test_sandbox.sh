#!/bin/zsh
# Sandbox test of E1's operations scripts (modelled on ops_r3/test_sandbox.sh). Nothing real is touched: a throwaway
# git repo stands in for the Mac's (so the REAL mac_checks runs), a bare repo and a clone with a runs/ folder stand in
# for the VM (so the REAL vm_state.py runs against it, and vm_checkout.sh's git commands run for real), and ssh, rsync,
# sleep, uv, tmux and nvidia-smi are stubs. The fake ssh answers each command the scripts send by its pattern and
# refuses any other (exit 9); the sandbox's VM_HOST is sandbox.invalid. So nothing reaches a VM.
# Usage: zsh docs/probe/20261113_e1/ops/test_sandbox.sh      (exit 0 if every case passes)
SRC=${0:A:h}
T=$(mktemp -d ${TMPDIR:-/tmp}/e1_sandbox.XXXXXX) || exit 99
T=${T:A}
[[ $T == *e1_sandbox.* ]] || exit 99
VMH=$T/vmhome; VM=$VMH/aftershock-artifacts; BARE=$VMH/repos/aftershock-artifacts.git
REL=docs/probe/20261113_e1/ops
PD=$T/repo/docs/probe/20261113_e1
S=$T/repo/$REL
R19L=$T/repo/docs/probe/20261113_reg19/ops_r3/state/queue.lock
BOOTA=11111111-2222-3333-4444-555555555555
SW=sweep_l1pl350cl_pc_off
G=(git -c user.name=sandbox -c user.email=sandbox@example.invalid -c commit.gpgsign=false)
mkdir -p $T/bin $T/state $VMH/repos $VMH/.local/bin $T/repo && cd $T/repo && git init -q -b main . || exit 99
mkdir -p tools configs runs docs
echo 'import os, sys; sys.exit(1 if os.environ.get("FAKE_MANIFEST_FAIL") else 0)' > tools/manifest.py
echo x > pyproject.toml; echo x > uv.lock; echo 'runs/' > .gitignore; echo x > configs/other.yaml
print -r -- "# decisions (sandbox)" > docs/decisions.md
$G add -A && $G commit -q -m "REG-19's pin (sandbox)" || exit 99
C0=$(git rev-parse HEAD)
echo "sweep: x" > configs/$SW.yaml
for r in 1.5 2 2.5 3 3.5 4; do echo "rate: $r" > configs/${SW}_only_r$r.yaml; done
mkdir -p $S
cp $SRC/vm_state.py $SRC/session_probe.sh $SRC/launch.sh $SRC/queue.sh $SRC/vm_checkout.sh $SRC/e1_commit.txt $S/
sed -e "s|^R=.*|R=$T/repo|" -e "s|^VM_GIT=.*|VM_GIT=$BARE|" $SRC/common.sh > $S/common.sh
print -r -l -- "## 2026-11-14 · [REG] E1: sandbox" "text" "## 2026-11-14 · [DECISION] (owner) E1 approved as registered: sandbox" >> docs/decisions.md
$G add -A && $G commit -q -m "E1 registered and approved, scripts with e1_commit.txt UNSET" || exit 99
E1H=$(git rev-parse HEAD)
print -r -- $E1H > $S/e1_commit.txt
print -r -- "## 2026-11-15 · [RESULT] REG-19: sandbox" >> docs/decisions.md
$G add -A && $G commit -q -m "e1_commit.txt set; REG-19's result" || exit 99
HEADH=$(git rev-parse HEAD); LOCKB=$(git rev-parse ${E1H}:uv.lock)
git init -q --bare $BARE && git push -q $BARE ${C0}:refs/heads/main && git clone -q $BARE $VM 2> /dev/null && (cd $VM && git checkout -q --detach $C0) && mkdir -p $VM/runs || exit 99

cat > $T/bin/sleep <<'EOS'
#!/bin/sh
exit 0
EOS
for b in nvidia-smi tmux; do printf '#!/bin/sh\necho "fake %s: never run on the Mac" >&2\nexit 97\n' $b > $T/bin/$b; done
cat > $T/bin/uv <<'EOS'
#!/bin/sh
echo "Would use project environment at: .venv"; echo "Would uninstall 2 packages"; echo " - a==1"; echo " - b==1"
[ -n "$FAKE_UV_ADD" ] && echo " + c==2"
exit 0
EOS
cat > $T/bin/rsync <<'EOS'
#!/bin/zsh
src=${@[-2]}; rid=${src:t}
[[ $src == chalshik@sandbox.invalid:aftershock-artifacts/runs/* ]] || { echo "fake rsync: unexpected source $src" >&2; exit 9; }
[[ -n $FAKE_RSYNC_FAIL ]] && exit 1
cp -R __T__/vmhome/aftershock-artifacts/runs/$rid runs/
EOS
cat > $T/bin/ssh <<'EOS'
#!/bin/zsh
cmd=${@[-1]}; ST=__T__/state; VMH=__T__/vmhome; VM=$VMH/aftershock-artifacts; SW=sweep_l1pl350cl_pc_off
[[ ${@[-2]} == chalshik@sandbox.invalid ]] || { echo "fake ssh: unexpected host ${@[-2]}" >&2; exit 9; }
print -r -- "$cmd" >> $ST/ssh_log
real() { HOME=$VMH sh -c "$1"; }
case $cmd in
  "python3 - "*) [[ -n $FAKE_STATE_DOWN ]] && exit 255; HOME=$VMH python3 - ${=cmd#python3 - };;
  *'tmux_rc='*) [[ -n $FAKE_DOWN_NOW ]] && exit 255; echo "tmux_rc=${FAKE_TMUX_NOW:-1}";;
  *"up_since"*)
    echo "2026-11-14T00:00:00+00:00"; echo "boot_id ${FAKE_BOOT:-__BOOT__}"; echo "up_since 2026-11-13 15:20:00"; echo "kernel 6.8.0-fake"
    echo "driver ${FAKE_DRIVER:-595.99.02}"; echo "governor performance"; echo "limit_before ${FAKE_LIMIT_BEFORE:-420.00} W"; echo "apps ${FAKE_APPS_N:-0}"
    echo "boots -1 aaa;0 bbb;"; echo "prev_boot_kernel Linux version 6.8.0-fake"; echo "prev_boot_nvidia NVIDIA UNIX x86_64 Kernel Module  595.99.02";;
  *"sudo -n nvidia-smi -pl 350"*) echo "sudo: a password is required"; echo "sudo_rc 1";;
  *"limit_after"*)
    echo "limit_after ${FAKE_LIMIT:-350.00} W"; echo "tree ${FAKE_TREE:-__E1__} dirty ${FAKE_DIRTY:-0}"; echo "lock_blob ${FAKE_LOCK:-__LOCK__}"; echo "free_kb ${FAKE_FREE:-5000000}";;
  *"pre-launch read"*)
    [[ -n $FAKE_PRELAUNCH_FAIL ]] && exit 255
    echo "# pre-launch read (fake)"; echo "2026-11-14T00:00:00+00:00"; echo "power.limit [W], temperature.gpu, utilization.gpu [%], memory.used [MiB]"
    echo "${FAKE_LIMIT:-350.00} W, ${FAKE_TEMP:-40}, 0 %, 1 MiB"; echo "# compute apps:"; [[ -n $FAKE_APPS ]] && echo "4242, python, 100 MiB"
    echo "# tree:"; echo "${FAKE_TREE:-__E1__}"; echo "${FAKE_DIRTY:-0}"; echo "# lock:"; echo "${FAKE_LOCK:-__LOCK__}"
    echo "# boot:"; if [[ -n $FAKE_BOOT_EMPTY ]]; then echo ""; else echo "${FAKE_BOOT:-__BOOT__}"; fi
    echo "# free_kb:"; echo "${FAKE_FREE:-5000000}"; echo "# tmux:"; [[ -n $FAKE_TMUX_EXISTS ]] && echo "run: 1 windows" || echo "no server running on /tmp/tmux-1000/default";;
  *"temperature.gpu --format=csv,noheader"*) [[ -n $FAKE_TEMP_FAIL ]] && exit 255; echo "${FAKE_TEMP:-40}";;
  *"tmux new-session"*)
    [[ -n $FAKE_LAUNCH_FAIL ]] && exit 255
    n=$(( $(cat $ST/launch_n 2>/dev/null || echo 0) + 1 )); echo $n > $ST/launch_n
    cfg=$(print -r -- $cmd | sed -n 's|.*configs/\([^ ]*\)\.yaml.*|\1|p'); print -r -- $cfg >> $ST/launched
    log=$VMH/$(print -r -- $cmd | sed -n 's|.*> ~/\([^ ]*\.log\).*|\1|p')
    if [[ $cfg == $SW ]]; then rates=(${=FAKE_SWEEP_RATES:-1.5 2 2.5 3 3.5 4}); else rates=(${cfg##*_only_r}); fi
    : > $log
    for r in $rates; do
      m=$(( $(cat $ST/run_n 2>/dev/null || echo 0) + 1 )); echo $m > $ST/run_n
      rid=20261114-$(printf %06d $m)_${SW}_r$r
      mkdir -p $VM/runs/$rid; echo '{"t_sent": 1.0}' > $VM/runs/$rid/requests.jsonl; echo '{"git_commit": "not-read"}' > $VM/runs/$rid/env.json
      echo "[run] start {'run_id': '$rid', 'git_commit': '${FAKE_COMMIT:-__E1__}'}" >> $log
      echo "[run] server_ready {'engine_config': ['KV cache size 1 tokens']}" >> $log
      failed=""; for tok in ${=FAKE_FAIL}; do [[ ${tok%%:*} == $r ]] && failed=${tok#*:}; done
      [[ " $FAKE_NOCHECK " == *" $r "* ]] && continue
      if [[ -z $failed ]]; then
        echo '{"valid": true, "failed": [], "checks": [{"name": "no_errors", "passed": true, "detail": {"ok": 9}}]}' > $VM/runs/$rid/checks.json
        echo "[run] checks {'valid': True, 'failed': []}" >> $log
      else
        echo "{\"valid\": false, \"failed\": [\"${failed//,/\", \"}\"], \"checks\": []}" > $VM/runs/$rid/checks.json
        echo "[run] checks {'valid': False, 'failed': ['$failed']}" >> $log
      fi
    done;;
  *"grep -m1 -o"*) [[ -n $FAKE_NO_RID ]] || real "$cmd";;
  *END_OF_RUN_ID_LINES*) [[ -n $FAKE_SETTLE_DOWN ]] && exit 255; real "$cmd";;
  "tmux has-session -t run 2>/dev/null") [[ -n $FAKE_DOWN_ON_WAIT ]] && exit 255; exit ${FAKE_TMUX_RC:-1};;
  *"xargs sha256sum"*)
    [[ -n $FAKE_SHA_FAIL ]] && exit 255
    rid=$(print -r -- $cmd | sed -n 's|.*runs/\([^ ]*\) &&.*|\1|p'); cd $VM/runs/$rid && find . -type f | LC_ALL=C sort | xargs shasum -a 256; [[ -n $FAKE_BAD_SHA ]] && echo corrupt; true;;
  "nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l") echo "${FAKE_APPS_N:-0}";;
  *"uv sync --frozen --extra server --dry-run"*) echo "Resolved 120 packages in 5ms"; echo "Would make no changes"; [[ -n $FAKE_UV_VM_ADD ]] && echo " + torch==9.9"; true;;
  "cd ~/aftershock-artifacts && git "*) real "$cmd";;
  *) echo "fake ssh: unhandled: $cmd" >&2; exit 9;;
esac
EOS
/usr/bin/sed -i '' -e "s|__T__|$T|g" -e "s|__E1__|$E1H|g" -e "s|__LOCK__|$LOCKB|g" -e "s|__BOOT__|$BOOTA|g" $T/bin/ssh $T/bin/rsync
chmod +x $T/bin/*

pass=0; fail=0
reset() {
  setopt localoptions null_glob
  [[ $T == *e1_sandbox.* ]] || exit 99
  rm -rf $T/state/* $T/repo/runs/* $VM/runs/* $PD/prelaunch_* $PD/session_* $PD/vm_checkout_* $VMH/e1_*.log $R19L
  (cd $T/repo && git checkout -q main && git reset -q --hard $HEADH && git clean -fdq $REL docs/probe/20261113_reg19)
  (cd $VM && git checkout -q --detach $C0 && git clean -fdq)
  mkdir -p $S/state $VM/runs
  print -r -- $BOOTA > $S/state/session_boot_id.txt
}
case_() {   # name, expected substring, expected exit code, then env assignments and the command
  local name=$1 want=$2 wantrc=$3; shift 3
  out=$(env PATH=$T/bin:$PATH VM_HOST=sandbox.invalid "$@" 2>&1); rc=$?
  if [[ $out == *"$want"* && $rc == $wantrc ]]; then pass=$((pass + 1)); echo "ok    $name"; else fail=$((fail + 1)); echo "FAIL  $name (rc $rc, wanted $wantrc and '$want')"; print -r -- "$out" | tail -6 | sed 's/^/        /'; fi
  (( rc == 0 )) || [[ $out == *"Allowed reads while diagnosing a stop"* ]] || noallowed+=("$name")
}
noallowed=()
chk() {     # name, then a command that must succeed
  local name=$1; shift
  if "$@" > /dev/null 2>&1; then pass=$((pass + 1)); echo "ok    $name"; else fail=$((fail + 1)); echo "FAIL  $name"; fi
}
is() { [[ $1 == $2 ]]; }
run() { env PATH=$T/bin:$PATH VM_HOST=sandbox.invalid "$@" > /dev/null 2>&1; }   # a step whose output is not judged
launches() { cat $T/state/launch_n 2>/dev/null || echo 0; }
nfiles() { local f=($~1(N)); echo ${#f}; }                  # (N): a path that does not exist counts 0
rid_of() { setopt localoptions null_glob; local f=($VM/runs/*_${SW}_r$1); print -r -- ${f[$2]:t}; }   # rate, n-th folder of it
mkrun() {   # a hand-made run folder on the fake VM: run id, checks.json text ("" for none)
  mkdir -p $VM/runs/$1; [[ -z $2 ]] || print -r -- $2 > $VM/runs/$1/checks.json
}
VALID='{"valid": true, "failed": [], "checks": []}'
Q=$S/queue.sh; L=$S/launch.sh; P=$S/session_probe.sh; V=$S/vm_checkout.sh
gitc() { (cd $T/repo && "$@" > /dev/null 2>&1 && $G commit -q -am "sandbox change"); }   # a committed change in the Mac repo

echo "--- the sandbox itself"
chk "common.sh differs from the source in R and VM_GIT only" is "$(diff $SRC/common.sh $S/common.sh | grep -c '^>')" 2
chk "the real common.sh names the VM and its bare repository (the sandbox replaces both)" is "$(env -u VM_HOST zsh -c "source $SRC/common.sh; print -r -- \$H \$VM_GIT")" "chalshik@100.83.53.50 chalshik@100.83.53.50:repos/aftershock-artifacts.git"
chk "vm_state.py's code (after its docstring) names no file but checks.json and no field but valid and failed" is "$(sed -n '/^import json/,$p' $SRC/vm_state.py | grep -o '"[a-z_.-]*"' | sort -u | tr '\n' ' ')" '"-" "aftershock-artifacts" "checks.json" "failed" "invalid" "nochecks" "runs" "unreadable" "valid" '

echo "--- queue: a clean sweep, and starting it again"
reset
case_ "a clean sweep: six valid runs, QUEUE DONE" "QUEUE DONE" 0 zsh $Q
chk "one launch, of the sweep" is "$(launches) $(cat $T/state/launched)" "1 $SW"
chk "the sweep's attempt record names its log, commit and boot" sh -c "grep -q '^log ~/e1_${SW}_' $S/state/attempt_sweep_1.txt && grep -q '^commit $E1H' $S/state/attempt_sweep_1.txt && grep -q '^boot $BOOTA' $S/state/attempt_sweep_1.txt"
chk "its settle record names six runs at the registered commit" is "$(grep -c "^rid .* $E1H\$" $S/state/settled_attempt_sweep_1.txt)" 6
chk "six copies verified" is "$(nfiles "$S/state/copied_*.txt") $(nfiles "$T/repo/runs/*_${SW}_r*")" "6 6"
chk "the end record lists the six rates" is "$(grep -c '^r[0-9.]* 2026' $S/state/queue_end.txt)" 6
chk "no single-rate attempt" is "$(nfiles "$S/state/attempt_r*.txt")" 0
case_ "started again after the end: the same end" "QUEUE DONE" 0 zsh $Q
chk "nothing launched or copied again" is "$(launches) $(nfiles "$S/state/copied_*.txt")" "1 6"
chk "no command sent to the VM names a run file other than checks.json" sh -c "! grep -E 'env\.json|requests\.jsonl|events\.jsonl|config\.yaml|metrics|gpu\.jsonl|server\.log' $T/state/ssh_log | grep -v 'xargs sha256sum' | grep -q ."
chk "the launch logs are read only through their run_id lines" sh -c "! grep 'e1_' $T/state/ssh_log | grep -v \"'run_id': '\" | grep -v 'tmux new-session' | grep -q ."

echo "--- a rate the sweep never started"
reset
case_ "the sweep ends after 2.5: rates 3, 3.5, 4 follow, each as its first attempt" "QUEUE DONE" 0 FAKE_SWEEP_RATES="1.5 2 2.5" zsh $Q
chk "the queue said which rates were not started" is "$(print -r -- $out | grep -c '^NOT STARTED rate')" 3
chk "attempt 1 of rates 3, 3.5 and 4, from their single-rate configs" test -e $S/state/attempt_r3_1.txt -a -e $S/state/attempt_r3.5_1.txt -a -e $S/state/attempt_r4_1.txt
chk "no attempt 2 anywhere" is "$(nfiles "$S/state/attempt_r*_2.txt")" 0
chk "four launches: the sweep, then three single rates" is "$(launches) $(tail -1 $T/state/launched)" "4 ${SW}_only_r4"
reset
case_ "the sweep's launch command fails: its attempt is spent" "the launch command failed" 1 FAKE_LAUNCH_FAIL=1 zsh $Q
chk "and the record says so" grep -q launch_command_failed $S/state/attempt_sweep_1.txt
case_ "started again: no rate was started, so each runs alone as its first attempt" "NOT STARTED rate 1.5 by the sweep" 0 zsh $Q
chk "six single-rate launches, never a second sweep" is "$(launches) $(grep -c "^$SW\$" $T/state/launched)" "6 0"
chk "each one attempt 1" is "$(nfiles "$S/state/attempt_r*_1.txt") $(nfiles "$S/state/attempt_r*_2.txt")" "6 0"

echo "--- an invalid rate: rerun unchanged, at most three attempts in all"
reset
case_ "an invalid rate in the sweep pauses the queue before the next launch" "QUEUE STOP after an invalid run" 1 FAKE_FAIL="2:recorder" zsh $Q
chk "the invalid run is named with its failed check" is "$(print -r -- $out | grep -c "^RUN $(rid_of 2 1) INVALID failed=recorder")" 1
chk "all six runs copied, the invalid one too" is "$(nfiles "$S/state/copied_*.txt")" 6
case_ "started again: rate 2 is rerun from its single-rate config and is valid" "QUEUE DONE" 0 zsh $Q
chk "as attempt 2 of rate 2" is "$(nfiles "$S/state/attempt_r2_2.txt") $(tail -1 $T/state/launched)" "1 ${SW}_only_r2"
chk "the end record lists the valid rerun with 2 attempts" grep -q "^r2 .* attempts 2\$" $S/state/queue_end.txt
reset
run FAKE_FAIL="2:recorder" zsh $Q
case_ "the rerun is invalid again" "INVALID failed=recorder" 1 FAKE_FAIL="2:recorder" zsh $Q
case_ "attempt 3 invalid too: the rate is spent, no fourth launch; the queue ends with the hole" "QUEUE END rates without a valid run after 3 attempts: 2" 3 FAKE_FAIL="2:recorder" zsh $Q
chk "three launches, no attempt 4" is "$(launches) $(nfiles "$S/state/attempt_r2_4.txt")" "3 0"
chk "the end record says rate 2 has none" grep -q '^r2 none: the 3 attempts are spent (3 invalid)' $S/state/queue_end.txt
case_ "started again: the same end, nothing launched" "QUEUE END rates without a valid run" 3 zsh $Q
chk "still three launches" is "$(launches)" 3
reset
run FAKE_SWEEP_RATES="1.5 2" FAKE_FAIL="2:recorder" zsh $Q; run FAKE_FAIL="2:recorder" zsh $Q; run FAKE_FAIL="2:recorder" zsh $Q
case_ "a spent rate does not hold back the rates still to run" "QUEUE END rates without a valid run after 3 attempts: 2" 3 zsh $Q
chk "rates 2.5 to 4 ran as first attempts: seven launches" is "$(launches) $(nfiles "$S/state/attempt_r4_1.txt")" "7 1"

echo "--- heat"
reset
run FAKE_FAIL="2:gpu_steady" zsh $Q
case_ "a heat-invalid rate is rerun once; it fails on heat again" "INVALID failed=gpu_steady" 1 FAKE_FAIL="2:gpu_steady" zsh $Q
case_ "the second heat failure stops E1" "second heat failure (gpu_steady) among E1's runs" 1 zsh $Q
chk "two launches, no attempt 3" is "$(launches) $(nfiles "$S/state/attempt_r2_3.txt")" "2 0"
reset
run FAKE_FAIL="2:gpu_steady 3:gpu_steady" zsh $Q
case_ "two heat failures in the sweep: no rerun at all" "second heat failure" 1 zsh $Q
chk "one launch" is "$(launches)" 1
reset
run FAKE_FAIL="2:gpu_steady" zsh $Q
case_ "one heat failure: its rerun is valid" "QUEUE DONE" 0 zsh $Q
reset
run FAKE_FAIL="2:gpu_steady" zsh $Q
case_ "the heat rerun waits for 45 C and stops when the GPU stays hot" "STOP: GPU at '60' C" 1 FAKE_TEMP=60 zsh $Q
chk "spending no attempt" is "$(launches) $(nfiles "$S/state/attempt_r2_2.txt")" "1 0"

echo "--- no_errors and power_limit stop E1"
reset
run FAKE_FAIL="3:no_errors" zsh $Q
case_ "no_errors: no rerun" "E1 registers no rerun after no_errors" 1 zsh $Q
chk "one launch" is "$(launches)" 1
reset
run FAKE_FAIL="3:power_limit,recorder" zsh $Q
case_ "power_limit among other failures: no rerun" "E1 registers no rerun after power_limit" 1 zsh $Q
reset
run FAKE_SWEEP_RATES="1.5 2 2.5" FAKE_FAIL="1.5:no_errors" zsh $Q
case_ "no_errors also holds back the rates never started" "E1 registers no rerun after no_errors" 1 zsh $Q
chk "rate 3 not launched" is "$(launches) $(nfiles "$S/state/attempt_r3_1.txt")" "1 0"

echo "--- a run without checks.json"
reset
case_ "the VM goes off during rate 3 of the sweep: E1 stops" "has no checks.json" 1 FAKE_SWEEP_RATES="1.5 2 2.5 3" FAKE_NOCHECK="3" zsh $Q
LR=$(rid_of 3 1)
chk "the lost run was settled and named, the finished ones copied" is "$(grep -c '^rid ' $S/state/settled_attempt_sweep_1.txt) $(nfiles "$S/state/copied_*.txt")" "4 3"
case_ "started again without a decision: the same stop, no launch" "a new decision, recorded as $S/state/lost_ok_$LR.txt" 1 zsh $Q
chk "no launch" is "$(launches)" 1
echo "owner's decision (sandbox)" > $S/state/lost_ok_$LR.txt
case_ "with lost_ok: rate 3 runs as attempt 2, then 3.5 and 4 as attempt 1" "QUEUE DONE" 0 zsh $Q
chk "attempt 2 of rate 3; attempt 1 of 3.5 and 4" test -e $S/state/attempt_r3_2.txt -a -e $S/state/attempt_r3.5_1.txt -a -e $S/state/attempt_r4_1.txt
chk "the lost run is not copied" test ! -e $T/repo/runs/$LR
reset
run FAKE_SWEEP_RATES="1.5 2 2.5 3" FAKE_NOCHECK="3" FAKE_FAIL="2:recorder" zsh $Q
case_ "a lost run at rate 3 stops E1 before rate 2's rerun" "has no checks.json" 1 zsh $Q
chk "rate 2 not rerun" is "$(launches) $(nfiles "$S/state/attempt_r2_2.txt")" "1 0"
echo "owner's decision (sandbox)" > $S/state/lost_ok_$(rid_of 3 1).txt
case_ "with lost_ok: the paused rerun of rate 2 goes first, in the sweep's order" "QUEUE DONE" 0 zsh $Q
chk "rate 2 attempt 2, rate 3 attempt 2, rates 3.5 and 4 attempt 1" test -e $S/state/attempt_r2_2.txt -a -e $S/state/attempt_r3_2.txt -a -e $S/state/attempt_r3.5_1.txt -a -e $S/state/attempt_r4_1.txt
reset
run FAKE_FAIL="4:recorder" zsh $Q
case_ "a single-rate run that ends without checks.json stops E1 too" "has no checks.json" 1 FAKE_NOCHECK="4" zsh $Q
echo "owner's decision (sandbox)" > $S/state/lost_ok_$(rid_of 4 2).txt
case_ "with lost_ok its third attempt runs" "QUEUE DONE" 0 zsh $Q
chk "attempt 3 of rate 4" test -e $S/state/attempt_r4_3.txt

echo "--- the registered commit"
reset; gitc sh -c "echo UNSET > $REL/e1_commit.txt"
case_ "e1_commit.txt UNSET: the queue refuses" "e1_commit.txt says UNSET" 2 zsh $Q
case_ "launch.sh refuses" "e1_commit.txt says UNSET" 2 zsh $L sweep
case_ "session_probe.sh refuses" "e1_commit.txt says UNSET" 2 zsh $P
case_ "vm_checkout.sh refuses" "e1_commit.txt says UNSET" 2 zsh $V
chk "nothing launched, the VM's tree not moved" is "$(launches) $(git -C $VM rev-parse HEAD)" "0 $C0"
reset; printf %s $E1H > $S/e1_commit.txt
case_ "e1_commit.txt changed and not committed" "differs from its committed text" 2 zsh $Q
reset; gitc sh -c "echo $C0 > $REL/e1_commit.txt"
case_ "a commit without E1's registration" "no '[REG] E1' heading" 2 zsh $Q
reset; gitc sh -c "echo abc > $REL/e1_commit.txt"
case_ "e1_commit.txt not a full hash" "not one full commit hash" 2 zsh $Q
reset; gitc sh -c "echo '# y' >> $REL/queue.sh"
case_ "a script changed after the registered commit" "differs from its text at the registered commit" 2 zsh $Q
reset; echo '# y' >> $S/launch.sh
case_ "a script changed and not committed" "differs from its committed text" 2 zsh $Q
reset; gitc sh -c "grep -v 'RESULT. REG-19' docs/decisions.md > d && mv d docs/decisions.md"
case_ "no [RESULT] REG-19 in the committed log: the queue refuses" "no '[RESULT] REG-19' heading" 2 zsh $Q
reset; echo y >> $T/repo/uv.lock
case_ "uv.lock changed in the Mac's working tree" "differ in the Mac's working tree" 2 zsh $Q
reset; mkdir -p $R19L
case_ "REG-19's queue lock exists: the queue refuses" "REG-19's queue lock exists" 2 zsh $Q
case_ "and launch.sh" "REG-19's queue lock exists" 2 zsh $L sweep
chk "none of these launched anything" is "$(launches)" 0

echo "--- pre-launch stops spend no attempt"
reset
case_ "a VM tree off the registered commit" "STOP: VM tree 'deadbeef'" 1 FAKE_TREE=deadbeef zsh $Q
chk "no attempt record, but the probe is kept" is "$(nfiles "$S/state/attempt_*.txt") $(nfiles "$PD/prelaunch_e1_*.txt")" "0 1"
case_ "the same command then runs the sweep as attempt 1" "QUEUE DONE" 0 zsh $Q
reset
case_ "a dirty VM tree" "STOP: VM tree" 1 FAKE_DIRTY=3 zsh $Q
reset
case_ "another uv.lock on the VM" "the VM's uv.lock 'abc' is not the registered commit's" 1 FAKE_LOCK=abc zsh $Q
reset
case_ "420 W stops the launch (read, never set)" "STOP: power limit '420.00'" 1 FAKE_LIMIT=420.00 zsh $Q
reset
case_ "a reboot since the session probe" "rebooted since the session probe" 1 FAKE_BOOT=99999999-2222-3333-4444-555555555555 zsh $Q
reset
case_ "an empty boot id" "rebooted since the session probe (boot id '')" 1 FAKE_BOOT_EMPTY=1 zsh $Q
reset
case_ "another compute process" "GPU compute process present" 1 FAKE_APPS=1 zsh $Q
reset
case_ "low disk" "kB free on the VM" 1 FAKE_FREE=1000 zsh $Q
reset
case_ "a GPU still hot after 30 min" "STOP: GPU at '60' C" 1 FAKE_TEMP=60 zsh $Q
reset
case_ "a temperature that is not a number" "is not a number" 1 FAKE_TEMP=N/A zsh $Q
reset
case_ "a temperature that cannot be read" "could not be read (temperature)" 1 FAKE_TEMP_FAIL=1 zsh $Q
reset
case_ "a pre-launch read that fails" "the pre-launch read failed" 1 FAKE_PRELAUNCH_FAIL=1 zsh $Q
reset
case_ "a tmux session in the pre-launch read" "a tmux session exists" 1 FAKE_TMUX_EXISTS=1 zsh $Q
reset; rm $S/state/session_boot_id.txt
case_ "no session probe, no launch" "no session probe" 1 zsh $Q
chk "none of these launched anything or spent an attempt" is "$(launches) $(nfiles "$S/state/attempt_*.txt")" "0 0"

echo "--- what a started invocation can leave behind"
reset
case_ "no run id within 120 s" "no run id of rate 1.5" 1 FAKE_NO_RID=1 zsh $Q
chk "the attempt is spent" test -e $S/state/attempt_sweep_1.txt
case_ "started again: the finished runs are found on the VM and used, not relaunched" "QUEUE DONE" 0 zsh $Q
chk "one launch" is "$(launches)" 1
reset
case_ "still running after the wait" "STILL RUNNING" 1 FAKE_TMUX_RC=0 WAIT_MIN=2 zsh $Q
case_ "started again while the session is alive: no decision" "the tmux session 'run' is alive on the VM" 1 FAKE_TMUX_NOW=0 zsh $Q
case_ "started again after it ended: settled and used" "QUEUE DONE" 0 zsh $Q
chk "one launch" is "$(launches)" 1
reset
case_ "a VM that stops answering during the wait" "VM NOT REACHABLE" 1 FAKE_DOWN_ON_WAIT=1 WAIT_MIN=20 zsh $Q
reset
case_ "the VM's run folders unreadable" "the VM's run folders could not be read" 1 FAKE_STATE_DOWN=1 zsh $Q
reset
case_ "the VM not answering the tmux read" "could not be read (tmux)" 1 FAKE_DOWN_NOW=1 zsh $Q
reset; run FAKE_NO_RID=1 zsh $Q
case_ "a launch log that cannot be read: no settle" "could not be read" 1 FAKE_SETTLE_DOWN=1 zsh $Q
chk "and no settle record" test ! -e $S/state/settled_attempt_sweep_1.txt
reset
case_ "a run made at another commit is not used" "was made at commit 'deadbeef'" 1 FAKE_COMMIT=deadbeef zsh $Q

echo "--- folders and records"
reset; mkrun 20261114-090000_${SW}_r2 $VALID
case_ "an E1 folder on the VM that no launch log names" "which no settled launch log of these scripts names" 1 zsh $Q
chk "nothing launched" is "$(launches)" 0
reset; mkdir -p $T/repo/runs/20261114-090000_${SW}_r2
case_ "an E1 folder on the Mac that the VM does not list" "the Mac holds 20261114-090000_${SW}_r2" 1 zsh $Q
reset; run zsh $Q; rm -rf $VM/runs/$(rid_of 3 1)
case_ "a run a launch log names, gone from the VM" "is not on the VM" 1 zsh $Q
reset; run FAKE_FAIL="2:recorder" zsh $Q; print -r -- '{"valid": true, "failed": ["x"], "checks": []}' > $VM/runs/$(rid_of 2 1)/checks.json
case_ "a checks.json that contradicts itself" "cannot be read (fields valid and failed)" 1 zsh $Q
reset; run FAKE_FAIL="2:recorder" zsh $Q; echo x > $S/state/attempt_r2_3.txt; print -r -l -- "time x" > $S/state/settled_attempt_r2_3.txt
case_ "attempt records not numbered in order" "are not numbered 2..2" 1 zsh $Q
reset; run FAKE_FAIL="2:recorder" zsh $Q; echo x > $S/state/attempt_r2_2.txt; print -r -l -- "rid $(rid_of 3 1) $E1H" > $S/state/settled_attempt_r2_2.txt
case_ "a launch log that names a run of another rate" "a run of another rate" 1 zsh $Q
reset; run FAKE_FAIL="2:recorder" zsh $Q
mkrun 20261114-090000_${SW}_r2 $VALID; mkrun 20261114-090001_${SW}_r2 $VALID
echo x > $S/state/attempt_r2_2.txt; print -r -l -- "rid 20261114-090000_${SW}_r2 $E1H" > $S/state/settled_attempt_r2_2.txt
echo x > $S/state/attempt_r2_3.txt; print -r -l -- "rid 20261114-090001_${SW}_r2 $E1H" > $S/state/settled_attempt_r2_3.txt
case_ "two valid runs at one rate: both listed, nothing launched" "also valid, not counted (e1.first_valid counts the earliest): 20261114-090001_${SW}_r2" 0 zsh $Q
chk "the earliest is the one counted in the end record" grep -q "^r2 20261114-090000_${SW}_r2 attempts 3;" $S/state/queue_end.txt
chk "one launch (the sweep)" is "$(launches)" 1
reset; run zsh $Q; echo "r1.5 changed" > $S/state/queue_end.txt
case_ "an end record that differs from what the records say" "state/queue_end.txt differs" 1 zsh $Q

echo "--- copy and checksums"
reset
case_ "a checksum mismatch stops the queue" "checksum mismatch" 1 FAKE_BAD_SHA=1 zsh $Q
chk "no copy record" is "$(nfiles "$S/state/copied_*.txt")" 0
case_ "started again: copied, verified, done" "QUEUE DONE" 0 zsh $Q
chk "one launch" is "$(launches)" 1
reset
case_ "a failed copy" "copy failed" 1 FAKE_RSYNC_FAIL=1 zsh $Q
reset
case_ "the VM's checksums unreadable" "checksums of" 1 FAKE_SHA_FAIL=1 zsh $Q
reset
case_ "a manifest update that fails" "manifest update failed" 1 FAKE_MANIFEST_FAIL=1 zsh $Q

echo "--- launch.sh by hand, and the queue's own lock"
reset
case_ "launch.sh refuses a rate before the sweep" "it is not the turn of '2': the next step is 'launch sweep'" 2 zsh $L 2
case_ "launch.sh refuses a name that is no rate" "is neither 'sweep' nor one of E1's rates" 2 zsh $L 5
case_ "launch.sh launches the sweep by hand when it is its turn" "ENDED sweep attempt 1" 0 zsh $L sweep
case_ "a second sweep by hand is refused (the first is not settled yet)" "the next step is 'settle" 2 zsh $L sweep
chk "one launch" is "$(launches)" 1
reset; mkdir -p $S/state/queue.lock; echo $$ > $S/state/queue.lock/pid
case_ "a second queue beside a running one is refused" "another E1 queue is running" 1 zsh $Q
reset; mkdir -p $S/state/queue.lock; echo 999999 > $S/state/queue.lock/pid
case_ "a lock left by a dead queue is set aside" "QUEUE DONE" 0 zsh $Q
chk "the stale lock is kept under another name" is "$(nfiles "$S/state/queue.lock.stale_*")" 1
reset
case_ "WAIT_MIN that is not a number" "WAIT_MIN is not a number" 2 WAIT_MIN=abc zsh $Q

echo "--- session probe"
reset; rm $S/state/session_boot_id.txt
case_ "session probe at 350 W, VM at the registered commit" "SESSION OK boot_id $BOOTA" 0 zsh $P
chk "it wrote the boot id" is "$(cat $S/state/session_boot_id.txt)" $BOOTA
case_ "a second probe in the same session is refused" "a session probe exists" 2 zsh $P
case_ "RENEW=1 replaces it and keeps the old file" "SESSION OK" 0 RENEW=1 FAKE_BOOT=99999999-2222-3333-4444-555555555555 zsh $P
chk "the replaced file is kept" is "$(nfiles "$S/state/session_boot_id_replaced_*.txt")" 1
reset; rm $S/state/session_boot_id.txt
case_ "420 W: no session" "power limit is not 350.00 W" 4 FAKE_LIMIT=420.00 zsh $P
chk "and no boot id file" test ! -e $S/state/session_boot_id.txt
case_ "another driver: no session" "driver is not 595.99.02" 2 FAKE_DRIVER=600.00 zsh $P
case_ "another uv.lock on the VM: no session" "uv.lock is not the registered commit's" 2 FAKE_LOCK=abc zsh $P
case_ "the VM's tree at REG-19's pin: no session" "tree is not the registered commit" 2 FAKE_TREE=$C0 zsh $P
case_ "a locked package missing on the Mac: no session" "lacks a locked package" 2 FAKE_UV_ADD=1 zsh $P
case_ "no boot id: no session" "no boot id read" 3 FAKE_BOOT=x zsh $P
case_ "SET=1 runs the one root command when the GPU is idle" "sudo_rc 1" 0 SET=1 zsh $P
reset; rm $S/state/session_boot_id.txt
case_ "SET=1 does not touch the limit under another process" "set_skipped" 0 SET=1 FAKE_APPS_N=1 zsh $P

echo "--- vm_checkout.sh"
reset; mkdir -p $R19L
case_ "refused while REG-19's queue lock exists" "REG-19's queue lock exists" 2 zsh $V
chk "the VM's tree not moved" is "$(git -C $VM rev-parse HEAD)" $C0
reset
case_ "refused while the tmux session 'run' is alive" "the tmux session 'run' is alive on the VM" 2 FAKE_TMUX_NOW=0 zsh $V
case_ "refused while a compute process is on the GPU" "a compute process is on the GPU" 2 FAKE_APPS_N=1 zsh $V
reset; mkdir -p $S/state/queue.lock
case_ "refused while E1's own queue lock exists" "E1's queue lock exists" 2 zsh $V
reset; gitc sh -c "grep -v 'RESULT. REG-19' docs/decisions.md > d && mv d docs/decisions.md"
case_ "refused before REG-19's [RESULT]" "no '[RESULT] REG-19' heading" 2 zsh $V
reset; echo junk > $VM/untracked.txt
case_ "refused when the VM's tree is dirty" "the VM's tree is dirty" 2 zsh $V
chk "none of these moved the VM's tree" is "$(git -C $VM rev-parse HEAD)" $C0
reset
case_ "moves the VM's tree from REG-19's pin to the registered commit" "VM AT $E1H, clean" 0 zsh $V
chk "the VM is at the registered commit, detached and clean" is "$(git -C $VM rev-parse HEAD) $(git -C $VM status --short | wc -l | tr -d ' ')" "$E1H 0"
chk "the VM's bare repository holds the Mac's main" is "$(git -C $BARE rev-parse main)" $HEADH
chk "everything read is in a probe file" grep -q "^head $E1H" $PD/vm_checkout_*.txt
case_ "run again: already there" "VM ALREADY AT $E1H" 0 zsh $V
reset; (cd $VM && $G commit -q --allow-empty -m "a commit the Mac does not have")
case_ "refused when the VM's commit is not an ancestor of the registered one" "is not an ancestor of $E1H" 2 zsh $V
reset
case_ "a dry-run sync that would change packages stops after the move" "would change 1 packages" 2 FAKE_UV_VM_ADD=1 zsh $V

echo "--- every stop"
chk "every stop above printed the allowed reads (${#noallowed} did not: ${noallowed[*]})" is ${#noallowed} 0

echo "passed $pass, failed $fail  (sandbox $T)"
[[ $fail == 0 ]]
