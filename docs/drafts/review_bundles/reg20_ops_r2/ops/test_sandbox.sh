#!/bin/zsh
# Sandbox test of REG-20's arm A scripts, draft 2 of the operations decision (in the style of ops_r3/test_sandbox.sh).
# Nothing real is touched: a throwaway git repo stands in for the Mac's (so the REAL mac_checks, gate_in_log,
# rulings_ok, next_step, decide, copy_verify and recheck_apply run), a folder tree stands in for the VM (so the REAL
# vm_state.py runs against it), and ssh, rsync, sleep, the hour of date, uv, the manifest tool and the Python of .venv
# (control_due.py, recheck_one.py, analysis.recheck and analysis.k1) are stubs. control_due.py and recheck_one.py are
# tested by test_control_due.py.
# Usage: zsh docs/probe/20261113_reg20/ops/test_sandbox.sh      (exit 0 if every case passes)
SRC=${0:A:h}
T=$(mktemp -d ${TMPDIR:-/tmp}/reg20_sandbox.XXXXXX) || exit 99
T=${T:A}
[[ $T == *reg20_sandbox.* ]] || exit 99
VM=$T/vmhome/aftershock-artifacts
PD=$T/repo/docs/probe/20261113_reg20
S=$PD/ops
HOLD=$T/aftershock-reg20-holding
BOOTA=11111111-2222-3333-4444-555555555555
BOOTB=99999999-2222-3333-4444-555555555555
B=burst_l1pl350ol_r2.0_w3000_s; C=stage2_control_l1pl350ol_r2.0_w3000_s; D=burst_l1pl350cl_r2.0_w3000_s15_drift
G=(git -c user.name=sandbox -c user.email=sandbox@example.invalid -c commit.gpgsign=false)
mkdir -p $T/bin $T/state $VM/runs $T/repo && cd $T/repo && git init -q -b main . || exit 99
mkdir -p tools configs runs analysis harness $S/state docs
echo 'import os, sys; sys.exit(1 if os.environ.get("FAKE_MANIFEST_FAIL") else 0)' > tools/manifest.py
echo x > pyproject.toml; echo x > uv.lock; echo 'runs/' > .gitignore
for f in __init__ k1 gate margin derived floor stats load withheld tables recheck; do echo "# $f (sandbox)" > analysis/$f.py; done
for f in __init__ checks config run; do echo "# $f (sandbox)" > harness/$f.py; done
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
cp $SRC/vm_state.py $SRC/session_probe.sh $SRC/launch.sh $SRC/queue.sh $SRC/final.sh $SRC/control_due.py $SRC/recheck_one.py $S/
sed -e "s|^R=.*|R=$T/repo|" -e "s|^PY=.*|PY=$T/bin/fakepy|" -e "s|^PIN=.*|PIN=$PINH|" \
    -e "s|^SEAL_BLOBS=.*|SEAL_BLOBS=($LOADB $WHB)|" -e "s|^CHECKS_COMMIT=.*|CHECKS_COMMIT=$PINH|" \
    -e "s|^RECHECK_COMMIT=.*|RECHECK_COMMIT=$PINH|" $SRC/common.sh > $S/common.sh
for v in "R=$T/repo" "PY=$T/bin/fakepy" "PIN=$PINH" "SEAL_BLOBS=($LOADB $WHB)" "CHECKS_COMMIT=$PINH" "RECHECK_COMMIT=$PINH"; do grep -qxF -- "$v" $S/common.sh || { echo "sandbox: '$v' not set"; exit 99; }; done
(( $(diff $SRC/common.sh $S/common.sh | grep -c '^>') == 6 )) || { echo "sandbox: common.sh differs in more than six lines"; exit 99; }
# The sandbox's rulings; the real file holds `unset` for every point (a case below uses it).
sed -e 's/^2a unset$/2a keep/' -e 's/^6 unset$/6 b/' -e 's/^7 unset$/7 per_stop/' -e 's/^8 unset$/8 b/' -e 's/^9 unset$/9 a/' -e 's/^16 unset$/16 a/' $SRC/owner_rulings.txt > $S/owner_rulings.txt
(( $(grep -c ' unset$' $S/owner_rulings.txt) == 0 && $(diff $SRC/owner_rulings.txt $S/owner_rulings.txt | grep -c '^>') == 6 )) || { echo "sandbox: the rulings were not set"; exit 99; }
GATELINE="{'k_closed': 5, 'n': 5, 'best_p': 0.03125, 'may_start': True}"
GD=$T/repo/docs/probe/reg20; mkdir -p $GD      # the gate, computed once (3c8e5dc in the real repo), committed here
print -r -- "$GATELINE" > $GD/gate_20261113T230307Z.txt; : > $GD/gate_err_20261113T230307Z.txt
H_RES="## 2026-11-20 · [RESULT] REG-19: sandbox"
H_RUL="## 2026-11-20 · [DECISION] (owner) REG-20 arm A operations: the owner's rulings (sandbox)"
H_START="## 2026-11-20 · [DECISION] (owner) REG-20 arm A starts: k1.reg20_a_may_start passed (sandbox)"
LOGOK=("$H_RES" "" "$H_RUL" "" "$H_START")
print -r -l -- $LOGOK > docs/decisions.md
$G add -A && $G commit -q -m scripts || exit 99
git log -1 --format=%H -- docs/probe/20261113_reg20/ops/{common.sh,vm_state.py,session_probe.sh,launch.sh,queue.sh,final.sh,control_due.py,recheck_one.py} > $S/scripts_commit.txt
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
echo "$*" >> __T__/state/uv_calls
case "$1" in
  sync) echo "Would use project environment at: .venv"; echo "Would uninstall 2 packages"; echo " - a==1"; echo " - b==1"
        [ -n "$FAKE_UV_ADD" ] && echo " + c==2"; exit 0;;
  *) echo "fake uv: unhandled $*" >&2; exit 9;;
esac
EOS
cat > $T/bin/fakepy <<'EOS'
#!/bin/zsh
ST=__T__/state
case "$*" in
  *control_due.py*)
    n=$(( $(cat $ST/due_n 2>/dev/null || echo 0) + 1 )); echo $n > $ST/due_n; echo "${AFTERSHOCK_UNSEAL-unset} ${@[-1]}" >> $ST/due_env
    [[ -n $FAKE_DUE_EDIT ]] && echo "# edited during the control decision" >> __T__/repo/analysis/k1.py
    [[ -n $FAKE_DUE_RC ]] && { echo "Traceback (fake)" >&2; exit $FAKE_DUE_RC; }
    [[ -n $FAKE_DUE_ERRLINE ]] && echo "ValueError: fake" >&2
    [[ -n $FAKE_DUE_OUT ]] && { print -r -- "$FAKE_DUE_OUT"; exit 0; }
    rid=${@[-1]}; sd=${rid##*_s}; v=$(sed -n "$((sd - 14))p" $ST/due 2>/dev/null); echo "CONTROL_DUE ${v:-no}";;
  *recheck_one.py*)
    d=${@[-1]}; rid=${d:t}; echo "$rid ${AFTERSHOCK_UNSEAL-unset}" >> $ST/recheck_one_calls
    [[ -n $FAKE_RECHECK_RC ]] && { echo "Traceback (fake)" >&2; exit 1; }
    mode=same; [[ -n $FAKE_RECHECK_FOR && $rid == *${FAKE_RECHECK_FOR}* ]] && mode=${FAKE_RECHECK_MODE:-fail}
    python3 - "$d" "$mode" <<'EOP'
import json, sys
d, mode = sys.argv[1], sys.argv[2]
c = json.load(open(d + "/checks.json"))
row = {"run": d.rstrip("/").rsplit("/", 1)[1], "stored_valid": c["valid"], "stored_failed": c["failed"]}
if mode == "error":
    row.update({"now_valid": None, "now_failed": None, "changed": True, "error": "ValueError: fake"})
elif mode == "fail":
    row.update({"now_valid": False, "now_failed": c["failed"] + ["recorder"], "changed": True})
else:
    row.update({"now_valid": c["valid"], "now_failed": c["failed"], "changed": False})
row["recorder"] = {"last_ok_scrape_t": 2500}          # a detail that must never reach a record
print(json.dumps(row, indent=1))
EOP
    ;;
  *"-m analysis.recheck"*)
    pat=${@[-1]}; echo "${AFTERSHOCK_UNSEAL-unset} $pat" >> $ST/recheck_env
    [[ -n $FAKE_RECHECK_WITHHELD ]] && echo "withheld: recheck skipped 1 run folder(s) sealed by REG-20 (analysis/withheld.py)" >&2
    python3 - "$pat" "${FAKE_RECHECK_FOR:-}" "${FAKE_FINAL_EXTRA_CHANGED:-}" <<'EOP'
import fnmatch, json, os, sys
pat, sub, extra = sys.argv[1], sys.argv[2], sys.argv[3]
runs = sorted(n for n in os.listdir("runs") if fnmatch.fnmatchcase(n, pat) and os.path.isdir("runs/" + n))
ch = [{"run": n, "stored_valid": True, "now_valid": False, "stored_failed": [], "now_failed": ["recorder"],
       "recorder": {"last_ok_scrape_t": 2500}} for n in runs if (sub and sub in n) or (extra and extra in n)]
print(json.dumps({"n_runs": len(runs), "n_changed": len(ch), "changed": ch}, indent=1))
EOP
    ;;
  *"reg20_a_may_start"*)
    echo "$*" >> __T__/gate_calls; echo "fakepy: these scripts must never compute the gate" >&2; exit 9;;
  *"-m analysis.k1 reg20"*)
    echo "{'fake': 'table', 'unseal': '${AFTERSHOCK_UNSEAL:-unset}', 'cwd': '$PWD'}"
    [[ -n $FAKE_FINAL_WITHHELD ]] && echo "withheld: find_runs('*_x') skipped 1 run folder(s) sealed by REG-20 (analysis/withheld.py)" >&2
    [[ -n $FAKE_FINAL_EDIT ]] && echo "# edited during the table" >> __T__/repo/analysis/gate.py
    [[ -n $FAKE_FINAL_RC ]] && exit $FAKE_FINAL_RC; exit 0;;
  *) echo "fakepy: unhandled $*" >&2; exit 9;;
esac
EOS
cat > $T/bin/rsync <<'EOS'
#!/bin/zsh
src=${@[-2]}; dst=${@[-1]}; rid=${src:t}
echo "${AFTERSHOCK_UNSEAL-unset} $dst" >> __T__/state/rsync_env
[[ -n $FAKE_RSYNC_FAIL ]] && exit 1
mkdir -p $dst/$rid && cp -R __T__/vmhome/aftershock-artifacts/runs/$rid/ $dst/$rid/
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
    [[ -n $FAKE_EDIT_DURING_RUN && $cfg == *${FAKE_EDIT_FOR:-}* ]] && echo "# edited during a run" >> __T__/repo/analysis/gate.py
    mkdir -p $VM/runs/$rid; echo "{}" > $VM/runs/$rid/requests.jsonl; echo "name: $cfg" > $VM/runs/$rid/config.yaml
    echo "{\"git_commit\": \"${FAKE_COMMIT:-__PIN__}\"}" > $VM/runs/$rid/env.json
    o=$(sed -n "${n}p" $ST/outcomes 2>/dev/null)
    [[ -z $o && -n $FAKE_FAILED && $cfg == *${FAKE_FAILED_FOR:-}* ]] && o=$FAKE_FAILED
    [[ -n $FAKE_NO_CHECKS ]] && o=lost
    case $o in
      ""|ok) echo '{"valid": true, "failed": [], "checks": []}' > $VM/runs/$rid/checks.json;;
      lost) ;;
      no_errors) echo '{"valid": false, "failed": ["no_errors"], "checks": [{"name": "no_errors", "passed": false, "detail": {"ok": 9, "client_error": 2}}]}' > $VM/runs/$rid/checks.json;;
      no_errors_manip) echo '{"valid": false, "failed": ["no_errors", "manipulation"], "checks": [{"name": "no_errors", "passed": false, "detail": {"ok": 9, "client_error": 2}}]}' > $VM/runs/$rid/checks.json;;
      no_errors_http) echo '{"valid": false, "failed": ["no_errors"], "checks": [{"name": "no_errors", "passed": false, "detail": {"ok": 9, "http_error": 2}}]}' > $VM/runs/$rid/checks.json;;
      *) echo "{\"valid\": false, \"failed\": [\"${o//,/\", \"}\"], \"checks\": []}" > $VM/runs/$rid/checks.json;;
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
/usr/bin/sed -i '' -e "s|__T__|$T|g" -e "s|__PIN__|$PINH|g" -e "s|__LOCK__|$LOCKB|g" -e "s|__BOOT__|$BOOTA|g" $T/bin/ssh $T/bin/fakepy $T/bin/rsync $T/bin/uv
chmod +x $T/bin/*

pass=0; fail=0
reset() {
  setopt localoptions null_glob
  [[ $T == *reg20_sandbox.* ]] || exit 99
  rm -rf $T/state/* $T/repo/runs/* $PD/prelaunch_* $PD/session_* $VM/runs/* $HOLD
  (cd $T/repo && git reset -q --hard $HEADH && git clean -fdq docs/probe)
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
has() { [[ $out == *"$1"* ]]; }      # the last case_'s output holds this text
lacks() { [[ $out != *"$1"* ]]; }
mkrun() {   # a hand-made run folder on the fake VM: run id, checks.json text ("" for none), commit (default: the pin)
  mkdir -p $VM/runs/$1; echo "{\"git_commit\": \"${3:-$PINH}\"}" > $VM/runs/$1/env.json; echo "name: x" > $VM/runs/$1/config.yaml
  [[ -z $2 ]] || print -r -- $2 > $VM/runs/$1/checks.json
}
rec() {     # a hand-written record: path, then "key value" lines
  local f=$1; shift; print -r -l -- "$@" > $f
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
setrul() { (cd $T/repo && sed -i '' "s/^$1 .*/$1 $2/" $S/owner_rulings.txt && $G commit -q -am "ruling $1 $2"); }
gatefiles() { (cd $T/repo && git rm -q --cached $GD/gate_*.txt > /dev/null && rm -f $GD/gate_*.txt && { [[ $# == 0 ]] || print -r -- "$1" > $GD/gate_20261113T230307Z.txt; } && { [[ $# == 0 ]] || print -r -- "${2:-}" > $GD/gate_err_20261113T230307Z.txt; } && $G add -A docs && $G commit -q -m gatefiles); }
reboot_to() { print -r -- $1 > $S/state/session_boot_id.txt; }   # what RENEW=1 of the session probe leaves after a reboot
q() { env PATH=$T/bin:$PATH "$@" zsh $Q > /dev/null 2>&1; }      # run the queue quietly, for set-ups
Q=$S/queue.sh; L=$S/launch.sh; F=$S/final.sh; P=$S/session_probe.sh

echo "--- the gate: REG-19's [RESULT], the owner's rulings, then the start decision (RA1, RA5, RA-O3)"
reset; setlog "$H_RUL" "$H_START"
case_ "no [RESULT] REG-19 heading: no queue" "no '[RESULT] REG-19' heading" 2 zsh $Q
reset; setlog "$H_RES" "$H_RUL"
case_ "no heading that starts arm A: no queue" "REG-20 arm A starts: k1.reg20_a_may_start passed' heading" 2 zsh $Q
reset; setlog "$H_RUL" "$H_START" "$H_RES"
case_ "the start heading before REG-19's [RESULT]: no queue" "is not after REG-19's [RESULT]" 2 zsh $Q
reset; setlog "## 2026-11-20 · [RESULT] REG-190: sandbox" "$H_RUL" "$H_START"
case_ "a [RESULT] of REG-190 is not REG-19's" "no '[RESULT] REG-19' heading" 2 zsh $Q
reset; setlog "$H_RES" "$H_RUL" "## 2026-11-20 · [DECISION] (agent) REG-20 arm A starts: k1.reg20_a_may_start passed"
case_ "a start decision that is neither (owner) nor (delegate): no queue" "arm A starts: k1.reg20_a_may_start passed' heading" 2 zsh $Q
reset; setlog "$H_RES" "$H_RUL" "- [DECISION] (owner) REG-20 arm A starts: k1.reg20_a_may_start passed, quoted in a list"
case_ "a start decision quoted, not a heading: no queue" "arm A starts: k1.reg20_a_may_start passed' heading" 2 zsh $Q
reset; setlog "$H_RES" "$H_RUL" "## 2026-11-15 · [DECISION] (delegate) REG-20 arm A starts only after a new registration: k1.reg20_a_may_start failed (4 of 5 closed runs cold-backlogged)"
case_ "RA1: 'starts only after a new registration … failed': no queue" "arm A starts: k1.reg20_a_may_start passed' heading" 2 zsh $Q
reset; setlog "$H_RES" "$H_RUL" "## 2026-11-15 · [DECISION] (owner) REG-20 arm A starts nothing: the gate is not passed"
case_ "RA1: 'starts nothing': no queue" "arm A starts: k1.reg20_a_may_start passed' heading" 2 zsh $Q
reset; setlog "$H_RES" "$H_RUL" "## 2026-11-15 · [DECISION] (delegate) REG-20 arm A starts: k1.reg20_a_may_start failed"
case_ "RA1: 'starts: k1.reg20_a_may_start failed': no queue" "arm A starts: k1.reg20_a_may_start passed' heading" 2 zsh $Q
reset; setlog "$H_RES" "$H_RUL" "## 2026-11-15 · [DECISION] (delegate) REG-20 arm A starts: k1.reg20_a_may_start passedover"
case_ "RA1: 'passed' must end the words: no queue" "arm A starts: k1.reg20_a_may_start passed' heading" 2 zsh $Q
reset; setlog "$H_RES" "$H_START"
case_ "RA5: no owner's rulings heading: no queue" "the owner's rulings' heading" 2 zsh $Q
reset; setlog "$H_RES" "## 2026-11-20 · [DECISION] (delegate) REG-20 arm A operations: the owner's rulings" "$H_START"
case_ "RA5: the rulings heading must be the owner's" "the owner's rulings' heading" 2 zsh $Q
reset; setlog "$H_RES" "$H_START" "$H_RUL"
case_ "RA5: the start heading before the owner's rulings: no queue" "is not after the owner's rulings" 2 zsh $Q
reset; setlog $LOGOK "## 2026-11-21 · [DECISION] (owner) REG-20 arm A stops: sandbox"
case_ "RA-O3: an owner's stop heading after the start: no queue" "a heading that stops arm A" 2 zsh $Q
reset; setlog $LOGOK "## 2026-11-21 · [CORR] REG-20 arm A is stopped"
case_ "RA-O3: a [CORR] 'is stopped' heading after the start: no queue" "a heading that stops arm A" 2 zsh $Q
case_ "and no launch by hand either" "a heading that stops arm A" 2 zsh $L ${B}15
reset; setlog "$H_RES" "$H_RUL" "## 2026-11-21 · [DECISION] (owner) REG-20 arm A stops: sandbox" "" "$H_START"
case_ "RA-O3: a start heading after a stop heading: the queue runs" "QUEUE DONE" 0 zsh $Q
reset; setlog "nothing yet"; print -r -l -- $LOGOK > $T/repo/docs/decisions.md
case_ "every heading in the working tree but not committed: no queue" "no '[RESULT] REG-19' heading" 2 zsh $Q
case_ "and no launch by hand either" "STOP: no '[RESULT] REG-19' heading" 2 zsh $L ${B}15
reset; setlog "$H_RES" "" "## 2026-11-21 · [OPS] something else" "$H_RUL" "## 2026-11-21 · [DECISION] (delegate) REG-20 arm A starts: k1.reg20_a_may_start passed"
case_ "(delegate) start and an entry between: the queue runs" "QUEUE DONE" 0 zsh $Q

echo "--- the gate file in HEAD (RB5) and the owner's rulings (RA5)"
reset; gatefiles
case_ "no gate file in HEAD: no queue" "HEAD holds 0 gate files" 2 zsh $Q
reset; gatefiles "{'k_closed': 4, 'n': 5, 'best_p': 0.0625, 'may_start': False}"
case_ "a gate file reading may_start False: no queue" "does not read 'may_start': True" 2 zsh $Q
reset; gatefiles "$GATELINE"$'\n'"extra"
case_ "a gate file with a second line: no queue" "does not read 'may_start': True" 2 zsh $Q
reset; (cd $T/repo && print -r -- "$GATELINE" > $GD/gate_20261121T000000Z.txt && : > $GD/gate_err_20261121T000000Z.txt && $G add -A $GD && $G commit -q -m twogates)
case_ "two gate files: no queue (computed once)" "HEAD holds 2 gate files" 2 zsh $Q
reset; gatefiles "$GATELINE" "withheld: find_runs skipped 1 run folder(s) sealed by REG-19 (analysis/withheld.py)"
case_ "a gate stderr with a withheld line: no queue" "holds a 'withheld:' line" 2 zsh $Q
reset; (cd $T/repo && git rm -q $GD/gate_err_20261113T230307Z.txt && $G commit -q -m noerr)
case_ "a gate file without its stderr file: no queue" "is not committed" 2 zsh $Q
reset; gatefiles; (cd $T/repo && print -r -- "$GATELINE" > $PD/reg20_gate_20261120T000000Z_1_1.txt && : > $PD/reg20_gate_err_20261120T000000Z_1_1.txt && $G add -A $PD && $G commit -q -m elsewhere)
case_ "a gate file anywhere but docs/probe/reg20/ is not the gate" "HEAD holds 0 gate files" 2 zsh $Q
reset; (cd $T/repo && cp $SRC/owner_rulings.txt $S/owner_rulings.txt && $G commit -q -am "real rulings file")
case_ "RA5: the rulings file as committed for draft 2 (every point unset): no queue" "the owner's ruling on point 2a reads 'unset'" 2 zsh $Q
case_ "and no launch by hand" "reads 'unset'" 2 zsh $L ${B}15
reset; setrul 6 maybe
case_ "a ruling the point may not take: no queue" "the owner's ruling on point 6 reads 'maybe'" 2 zsh $Q
reset; setrul 2a pin_head
case_ "ruling 2a pin_head: no queue until common.sh's pin changes" "chose a pin at or after 5ee6e38" 2 zsh $Q
reset; sed -i '' 's/^9 a$/9 b/' $S/owner_rulings.txt
case_ "a ruling changed but not committed: no queue" "owner_rulings.txt differs from its committed text" 2 zsh $Q
chk "none of these launched anything" is "$(launches)" 0

echo "--- the order: 15, 16, 17, the drift run, 18, 19; a control right after its burst run only when due"
reset; dues no no no no no
case_ "no control due anywhere" "QUEUE DONE" 0 zsh $Q
chk "order B15 B16 B17 D B18 B19" is "$(order)" "B15 B16 B17 D B18 B19"
chk "one control decision per open burst run, five" is "$(wc -l < $S/state/control_due.txt | tr -d ' ')" 5
chk "each made with the seal lifted for REG-20, on its own run" sh -c "[ \$(grep -c '^REG-20 20261120-' $T/state/due_env) = 5 ]"
chk "the queue's own shell does not carry AFTERSHOCK_UNSEAL" sh -c "! grep -qv '^unset ' $T/state/rsync_env"
chk "every run is copied to the holding folder first" sh -c "! grep -v ' $HOLD/\$' $T/state/rsync_env | grep -q ."
chk "every run rechecked once, before it entered runs/ (six)" is "$(wc -l < $T/state/recheck_one_calls | tr -d ' ')" 6
chk "the end record lists the six slots" is "$(head -6 $S/state/queue_done.txt | cut -d' ' -f1 | tr '\n' ' ')" "s15 s16 s17 drift s18 s19 "
chk "and the six copied runs" is "$(grep -c '^copied 20261120-' $S/state/queue_done.txt)" 6
chk "and the rulings in force" grep -qx "rulings 2a=keep 6=b 7=per_stop 8=b 9=a 16=a" $S/state/queue_done.txt
chk "the holding folder is empty after the moves" is "$(nfiles "$HOLD/*")" 0
case_ "started again after the end: same end" "QUEUE DONE" 0 zsh $Q
chk "nothing launched again, no second look, no second recheck" is "$(launches) $(looks) $(wc -l < $T/state/recheck_one_calls | tr -d ' ')" "6 5 6"
reset; dues yes yes yes yes yes
case_ "a control due everywhere" "QUEUE DONE" 0 zsh $Q
chk "order B15 C15 B16 C16 B17 C17 D B18 C18 B19 C19" is "$(order)" "B15 C15 B16 C16 B17 C17 D B18 C18 B19 C19"
chk "the end record names each control" is "$(grep -c 'CONTROL_DUE yes control 20261120-' $S/state/queue_done.txt)" 5
chk "RA-O1: each control's gap after its burst run and the boot, recorded" is "$(grep -cE 'CONTROL_DUE yes control 20261120-[^ ]+ gap_s -?[0-9]+ boot same$' $S/state/queue_done.txt)" 5
chk "eleven copied runs" is "$(grep -c '^copied ' $S/state/queue_done.txt)" 11
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

echo "--- the control decision: one line, once, on clean code, or a stop (RB1, RA4)"
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
reset; dues yes
case_ "RB1: analysis/gate.py edited during seed 15's burst run stops the queue before its control decision" "Mac-side check failed before turn 2: STOP: the analysis code" 1 FAKE_EDIT_DURING_RUN=1 FAKE_EDIT_FOR=${B}15 zsh $Q
chk "no CONTROL line, no look, no record" eval 'lacks CONTROL && [[ $(looks) == 0 && ! -e $S/state/control_due.txt ]]'
chk "and nothing copied" is "$(nfiles "$S/state/copied_*")" 0
(cd $T/repo && git checkout -q -- analysis/gate.py)
case_ "after the edit is undone the queue goes on" "QUEUE DONE" 0 zsh $Q
chk "one look per open burst run, made on the pin's code" is "$(looks)" 5
reset; dues yes
case_ "RA4: analysis/k1.py edited during the control_due.py call: the decision is dropped" "Mac-side check failed just after the control decision on $(rid_of 1 ${B}15)" 1 FAKE_DUE_EDIT=1 zsh $Q
chk "not recorded and not shown" eval '[[ ! -e $S/state/control_due.txt ]] && lacks CONTROL_DUE'
chk "and no control launched" is "$(launches)" 1
(cd $T/repo && git checkout -q -- analysis/k1.py)
case_ "after the edit is undone the decision is made again on clean code" "QUEUE DONE" 0 zsh $Q
chk "seed 15's control ran after its burst run" is "$(order)" "B15 C15 B16 B17 D B18 B19"
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

echo "--- the recheck at each copy, in the holding folder, under ruling 2a (RB2, RA2)"
reset
case_ "2a keep: a run today's checks flag is kept as its checks.json says, and the queue goes on" "kept as its checks.json says (ruling 2a keep)" 0 FAKE_RECHECK_FOR=${B}16 zsh $Q
chk "the RECHECK line names the recomputed failure" has "RECHECK $(rid_of 2 ${B}16) changed: stored valid=True failed=-; now valid=False failed=recorder"
chk "the end record says so" grep -qx "recheck_changed $(rid_of 2 ${B}16) kept" $S/state/queue_done.txt
chk "the record keeps validity fields only" sh -c "! grep -q last_ok_scrape_t $S/state/recheck_$(rid_of 2 ${B}16).json && grep -q '\"now_valid\": false' $S/state/recheck_$(rid_of 2 ${B}16).json"
chk "the recheck ran without AFTERSHOCK_UNSEAL" sh -c "! grep -v ' unset\$' $T/state/recheck_one_calls | grep -q ."
reset; setrul 2a setaside
case_ "2a setaside: a stored-valid run that today's checks fail is set aside, and the queue stops" "after a run set aside by the recheck" 1 FAKE_RECHECK_FOR=$(rid_of 1 ${B}15) zsh $Q
chk "the SET ASIDE line" has "SET ASIDE $(rid_of 1 ${B}15): stored valid, now invalid (failed=recorder)"
chk "it is in the holding folder, not in runs/, and has no copy record" sh -c "[ -d $HOLD/$(rid_of 1 ${B}15) ] && [ ! -e $T/repo/runs/$(rid_of 1 ${B}15) ] && [ ! -e $S/state/copied_$(rid_of 1 ${B}15).txt ]"
chk "no control decision on it" is "$(looks)" 0
case_ "started again: its config is rerun as attempt 2, and the queue goes on" "QUEUE DONE" 0 zsh $Q
chk "attempt 2 of seed 15" test -e $S/state/attempt_${B}15_2.txt
chk "the end record names it held and set aside" sh -c "grep -qx 'held $(rid_of 1 ${B}15) set_aside' $S/state/queue_done.txt && grep -qx 'recheck_changed $(rid_of 1 ${B}15) set_aside' $S/state/queue_done.txt"
case_ "and final.sh accepts the folder set (the set-aside run is not in runs/)" "{'fake': 'table'" 0 zsh $F
reset; setrul 2a setaside; outs ok ok
q FAKE_RECHECK_FOR=${B}15; q FAKE_RECHECK_FOR=${B}15
case_ "2a setaside twice: the attempts are spent and the queue stops" "the 2 attempts of ${B}15 are spent (0 left an invalid checks.json, 2 set aside)" 1 zsh $Q
rec $S/state/settle_$(rid_of 2 ${B}15).txt "label not_run" "under sandbox owner decision" "by owner"
case_ "an owner's settle record (not_run) lets it go on" "QUEUE DONE" 0 zsh $Q
chk "the slot reads not_run" grep -qx "s15 not_run $(rid_of 2 ${B}15)" $S/state/queue_done.txt
reset; setrul 2a stop
case_ "2a stop: a changed run stops the queue for the owner" "ruling 2a is 'stop'" 1 FAKE_RECHECK_FOR=$(rid_of 1 ${B}15) zsh $Q
rec $S/state/recheck_ok_$(rid_of 1 ${B}15).txt "answer keep" "under sandbox" "by delegate"
case_ "a delegate's answer is not taken" "ruling 2a is 'stop'" 1 zsh $Q
rec $S/state/recheck_ok_$(rid_of 1 ${B}15).txt "answer keep" "under sandbox" "by owner"
case_ "the owner's answer 'keep' lets it go on" "QUEUE DONE" 0 zsh $Q
reset; setrul 2a stop
q FAKE_RECHECK_FOR=$(rid_of 1 ${B}15)
rec $S/state/recheck_ok_$(rid_of 1 ${B}15).txt "answer setaside" "under sandbox" "by owner"
case_ "the owner's answer 'setaside' sets it aside" "SET ASIDE $(rid_of 1 ${B}15)" 1 zsh $Q
reset
case_ "a folder today's checks cannot read stops the queue" "today's checks could not be applied" 1 FAKE_RECHECK_FOR=$(rid_of 1 ${B}15) FAKE_RECHECK_MODE=error zsh $Q
chk "nothing of it entered runs/" test ! -e $T/repo/runs/$(rid_of 1 ${B}15)
reset
case_ "a failing recheck_one.py stops the queue" "recheck_one.py failed on $(rid_of 1 ${B}15)" 1 FAKE_RECHECK_RC=1 zsh $Q
reset; echo "# y" >> $T/repo/harness/checks.py
case_ "harness/checks.py not the checks in force: no recheck, no copy" "differ in the working tree from the commits named for the recheck" 1 zsh $Q
reset; echo "# y" >> $T/repo/analysis/tables.py
case_ "any change in analysis/ (here outside k1's closure) stops the recheck (ops_r3's guard)" "analysis/, harness/ or configs/defaults.yaml differ in the working tree from the Mac's HEAD" 1 zsh $Q
reset; echo "# y" >> $T/repo/configs/defaults.yaml
case_ "configs/defaults.yaml changed: no recheck" "differ in the working tree from the Mac's HEAD" 1 zsh $Q

echo "--- reruns: one, then a stop; the records name what they lift and who wrote them (RA3, RA-O4, RB3, RB7)"
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
rec $S/state/attempt_ok_${C}15_3.txt "under sandbox ruling 9(a)" "by delegate"
case_ "ruling 9(a): a delegate's attempt_ok record gives a third attempt" "RUN ${C}15 $(rid_of 4 ${C}15) VALID" 0 zsh $Q
chk "the control launched three times before the queue went on" sh -c "[ $(grep -c "^${C}15\$" $T/state/launched) = 3 ]"
reset; dues yes; outs ok client_lag client_lag client_lag
q; q; q; rec $S/state/attempt_ok_${C}15_3.txt "under sandbox ruling 9(a)" "by delegate"
case_ "a third control attempt invalid" "RUN ${C}15 $(rid_of 4 ${C}15) INVALID" 1 zsh $Q
case_ "then arm A stops" "the 3 attempts of ${C}15 are spent" 1 zsh $Q
rec $S/state/attempt_ok_${C}15_4.txt "under sandbox" "by delegate"
case_ "a delegate's fourth attempt is refused" "is not written as the rulings allow" 1 zsh $Q
reset; dues yes; outs ok client_lag client_lag; q; q; q
rec $S/state/attempt_ok_${C}15_3.txt "under sandbox" "by owner"; rm $S/state/attempt_ok_${C}15_3.txt
rec $S/state/settle_$(rid_of 3 ${C}15).txt "label control_not_run" "under sandbox ruling 9(b)" "by delegate"
case_ "under ruling 9(a) a delegate's control_not_run is refused" "control_not_run needs an owner's record" 1 zsh $Q
setrul 9 b
case_ "under ruling 9(b) it settles the control and the queue goes on" "QUEUE DONE" 0 zsh $Q
chk "the slot reads control_not_run" grep -qx "s15 $(rid_of 1 ${B}15) CONTROL_DUE yes control_not_run $(rid_of 3 ${C}15)" $S/state/queue_done.txt
chk "both invalid control runs are on the Mac" test -e $S/state/copied_$(rid_of 2 ${C}15).txt -a -e $S/state/copied_$(rid_of 3 ${C}15).txt
case_ "and final.sh accepts the slot" "{'fake': 'table'" 0 zsh $F
reset; setrul 9 b; dues yes; outs ok client_lag client_lag; q; q; q
rec $S/state/attempt_ok_${C}15_3.txt "under sandbox" "by delegate"
case_ "under ruling 9(b) a delegate's third attempt is refused" "is not written as the rulings allow" 1 zsh $Q
reset; outs ok ok ok client_lag client_lag
case_ "the drift run invalid" "RUN $D $(rid_of 4 $D) INVALID" 1 zsh $Q
case_ "its rerun invalid" "RUN $D $(rid_of 5 $D) INVALID" 1 zsh $Q
case_ "then a stop: the drift run's two attempts are spent" "the 2 attempts of $D are spent" 1 zsh $Q
rec $S/state/settle_$(rid_of 5 $D).txt "label drift_not_run" "under sandbox" "by delegate"
case_ "a delegate's drift_not_run is refused" "settled only by an owner's record" 1 zsh $Q
rec $S/state/settle_$(rid_of 5 $D).txt "label drift_not_run" "under sandbox" "by owner"
case_ "the owner's drift_not_run lets it go on" "QUEUE DONE" 0 zsh $Q
chk "the slot reads drift not_run with both runs" grep -qx "drift not_run $(rid_of 4 $D),$(rid_of 5 $D)" $S/state/queue_done.txt
reset; dues yes yes; outs client_lag client_lag
case_ "an open burst run invalid" "INVALID failed=client_lag" 1 zsh $Q
case_ "and invalid again" "INVALID failed=client_lag" 1 zsh $Q
case_ "is lost_open (REG-20 counts it cold): the queue goes on to seed 16" "QUEUE DONE" 0 zsh $Q
chk "no control for the lost seed: B15 B15 B16 C16 B17 D B18 B19" is "$(order)" "B15 B15 B16 C16 B17 D B18 B19"
chk "the end record says lost_open with both runs" grep -q "^s15 lost_open $(rid_of 1 ${B}15) $(rid_of 2 ${B}15)$" $S/state/queue_done.txt
chk "both invalid runs are on the Mac, verified" test -e $S/state/copied_$(rid_of 1 ${B}15).txt -a -e $S/state/copied_$(rid_of 2 ${B}15).txt
chk "no look at the lost seed" is "$(looks)" 4
reset; outs kv_capacity kv_capacity
case_ "RA3: a setup-class failure (kv_capacity) is rerun as any invalid run" "INVALID failed=kv_capacity" 1 zsh $Q
case_ "and fails again" "INVALID failed=kv_capacity" 1 zsh $Q
case_ "then no lost_open: a stop" "failed only checks of the setup class" 1 zsh $Q
chk "the second invalid run is not copied yet" test ! -e $S/state/copied_$(rid_of 2 ${B}15).txt
rec $S/state/settle_$(rid_of 2 ${B}15).txt "label lost_open" "under sandbox" "by delegate"
case_ "under ruling 7 per_stop a delegate's settle is refused" "label lost_open needs an owner's record" 1 zsh $Q
rec $S/state/settle_$(rid_of 2 ${B}15).txt "label lost_open" "under sandbox" "by owner"
case_ "the owner's lost_open lets it go on" "QUEUE DONE" 0 zsh $Q
chk "the slot reads lost_open with both runs, both on the Mac" sh -c "grep -qx 's15 lost_open $(rid_of 1 ${B}15) $(rid_of 2 ${B}15)' $S/state/queue_done.txt && [ -e $S/state/copied_$(rid_of 2 ${B}15).txt ]"
reset; setrul 7 not_run; outs client_lag trigger; q; q
case_ "RA3: either attempt setup-only (here the second, trigger) stops as well" "failed only checks of the setup class" 1 zsh $Q
rec $S/state/settle_$(rid_of 2 ${B}15).txt "label not_run" "under sandbox ruling 7" "by delegate"
case_ "not_run naming the second run while the first is in runs/ is refused (k1 would read lost_open)" "k1 would read lost_open" 1 zsh $Q
rm $S/state/settle_$(rid_of 2 ${B}15).txt; rec $S/state/settle_$(rid_of 1 ${B}15).txt "label not_run" "under sandbox ruling 7" "by delegate"
case_ "under ruling 7 not_run a delegate's not_run naming the copied run settles it" "HELD $(rid_of 2 ${B}15)" 0 zsh $Q
chk "the slot reads not_run" grep -qx "s15 not_run $(rid_of 1 ${B}15)" $S/state/queue_done.txt
chk "the second run is held, not in runs/" sh -c "[ -d $HOLD/$(rid_of 2 ${B}15) ] && [ ! -e $T/repo/runs/$(rid_of 2 ${B}15) ] && grep -qx 'held $(rid_of 2 ${B}15) settled' $S/state/queue_done.txt"
case_ "and final.sh accepts the folder set" "{'fake': 'table'" 0 zsh $F
reset; setrul 7 not_run; outs client_lag trigger; q; q
rec $S/state/settle_$(rid_of 1 ${B}15).txt "label not_run" "under sandbox ruling 7" "by delegate"
case_ "a held run that today's checks change" "HELD $(rid_of 2 ${B}15)" 0 FAKE_RECHECK_FOR=$(rid_of 2 ${B}15) zsh $Q
chk "is listed as held, not kept" sh -c "grep -qx 'recheck_changed $(rid_of 2 ${B}15) held' $S/state/queue_done.txt && ! grep -q ' kept\$' $S/state/queue_done.txt"
case_ "and final.sh accepts it (it is not in runs/)" "{'fake': 'table'" 0 zsh $F
reset; setrul 7 lost_open; outs kv_capacity client_lag; q; q
rec $S/state/settle_$(rid_of 2 ${B}15).txt "label not_run" "under sandbox" "by delegate"
case_ "under ruling 7 lost_open a delegate's not_run is refused" "label not_run needs an owner's record" 1 zsh $Q
rec $S/state/settle_$(rid_of 2 ${B}15).txt "label lost_open" "under sandbox ruling 7" "by delegate"
case_ "and a delegate's lost_open is taken" "QUEUE DONE" 0 zsh $Q
reset; outs no_errors
case_ "a client error" "INVALID failed=no_errors/client_error" 1 zsh $Q
case_ "is not rerun: stop and ask" "stop and ask after no_errors/client_error" 1 zsh $Q
chk "one launch" is "$(launches)" 1
rec $S/state/rerun_ok_$(rid_of 1 ${B}15).txt "lifts manipulation" "under sandbox" "by owner"
case_ "RA-O4: a record that lifts another failure does not lift it" "stop and ask after no_errors/client_error" 1 zsh $Q
rec $S/state/rerun_ok_$(rid_of 1 ${B}15).txt "lifts no_errors/client_error" "under sandbox ruling 6(b): nofile 65536, same boot" "by delegate"
case_ "ruling 6(b): a delegate's record after a client error with nofile 65536 and the same boot: rerun" "QUEUE DONE" 0 zsh $Q
chk "as attempt 2" test -e $S/state/attempt_${B}15_2.txt
reset; outs no_errors; q; reboot_to $BOOTB
rec $S/state/rerun_ok_$(rid_of 1 ${B}15).txt "lifts no_errors/client_error" "under sandbox ruling 6(b)" "by delegate"
case_ "ruling 6(b): not the delegate's when the VM rebooted since the run's launch" "stop and ask after no_errors/client_error" 1 FAKE_BOOT=$BOOTB zsh $Q
reset; setrul 6 a; outs no_errors; q
rec $S/state/rerun_ok_$(rid_of 1 ${B}15).txt "lifts no_errors/client_error" "under sandbox" "by delegate"
case_ "ruling 6(a): a delegate's record is refused" "stop and ask after no_errors/client_error" 1 zsh $Q
rec $S/state/rerun_ok_$(rid_of 1 ${B}15).txt "lifts no_errors/client_error" "under sandbox" "by owner"
case_ "ruling 6(a): the owner's record: rerun" "QUEUE DONE" 0 zsh $Q
reset; setrul 6 a; outs no_errors; q
rec $S/state/settle_$(rid_of 1 ${B}15).txt "label not_run" "under sandbox: the owner refuses the rerun" "by owner"
case_ "the owner refuses the rerun: the seed is settled not_run (RB3) and the queue goes on" "QUEUE DONE" 0 zsh $Q
chk "the slot reads not_run, no control, one launch of seed 15" sh -c "grep -qx 's15 not_run $(rid_of 1 ${B}15)' $S/state/queue_done.txt && [ $(grep -c "^${B}15\$" $T/state/launched) = 1 ]"
chk "the refused run is on the Mac (k1 reads not_run from one invalid run)" test -e $S/state/copied_$(rid_of 1 ${B}15).txt
case_ "and final.sh accepts the not_run slot" "{'fake': 'table'" 0 zsh $F
reset; outs no_errors_manip; q
rec $S/state/rerun_ok_$(rid_of 1 ${B}15).txt "lifts no_errors/client_error" "under sandbox" "by owner"
case_ "RA-O4: client error and manipulation in one run: one lift is not enough" "stop and ask after manipulation" 1 zsh $Q
print -r -- "lifts manipulation" >> $S/state/rerun_ok_$(rid_of 1 ${B}15).txt
case_ "with both lifts named: rerun" "QUEUE DONE" 0 zsh $Q
reset; outs no_errors no_errors; rec $S/state/rerun_ok_$(rid_of 1 ${B}15).txt "lifts no_errors/client_error" "under sandbox" "by owner"
q; q
case_ "a second client error after an allowed rerun stops again" "stop and ask after no_errors/client_error ($(rid_of 2 ${B}15))" 1 zsh $Q
rec $S/state/rerun_ok_$(rid_of 2 ${B}15).txt "lifts no_errors/client_error" "under sandbox" "by delegate"
case_ "with a record for it the seed is lost_open and the queue goes on" "QUEUE DONE" 0 zsh $Q
reset; outs no_errors_http
case_ "an http error is an invalid run like any other" "INVALID failed=no_errors/other" 1 zsh $Q
case_ "and is rerun" "QUEUE DONE" 0 zsh $Q
reset; outs manipulation
case_ "a burst that did not fill the pool" "INVALID failed=manipulation" 1 zsh $Q
case_ "is not rerun: stop and ask" "stop and ask after manipulation" 1 zsh $Q
rec $S/state/rerun_ok_$(rid_of 1 ${B}15).txt "lifts manipulation" "under sandbox" "by delegate"
case_ "RB7: a delegate cannot lift it" "stop and ask after manipulation" 1 zsh $Q
reset; outs power_limit
case_ "a run at another power limit" "INVALID failed=power_limit" 1 zsh $Q
case_ "is not rerun: stop and ask" "stop and ask after power_limit" 1 zsh $Q
reset; outs gpu_steady ok gpu_steady
case_ "a heat failure" "INVALID failed=gpu_steady" 1 zsh $Q
case_ "is rerun once; a second heat failure on another run" "INVALID failed=gpu_steady" 1 zsh $Q
case_ "stops the queue" "second heat failure" 1 zsh $Q
rec $S/state/rerun_ok_$(rid_of 3 ${B}16).txt "lifts gpu_steady" "under sandbox" "by owner"
case_ "the owner's record naming gpu_steady lets it go on" "QUEUE DONE" 0 zsh $Q
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

echo "--- lost attempts (no checks.json) under ruling 8 (RA6, RB4)"
reset
case_ "tmux gone without checks.json (a lost run)" "TMUX GONE, no checks.json" 1 FAKE_NO_CHECKS=1 FAKE_TMUX_RC=1 zsh $Q
case_ "is not rerun without a record" "has no checks.json (lost, or still running)" 1 zsh $Q
rec $S/state/lost_ok_$(rid_of 1 ${B}15).txt "count yes" "under sandbox" "by delegate"
case_ "lost without a reboot: a delegate's record is refused (the owner's)" "the owner's record only" 1 zsh $Q
rec $S/state/lost_ok_$(rid_of 1 ${B}15).txt "count yes" "under sandbox" "by owner"
case_ "with the owner's record it is rerun as attempt 2" "QUEUE DONE" 0 zsh $Q
chk "the lost run is not copied, nor held" sh -c "[ ! -e $T/repo/runs/$(rid_of 1 ${B}15) ] && [ ! -e $HOLD/$(rid_of 1 ${B}15) ]"
chk "RA6: the end record lists it with its arm, elapsed time, how it ended and whether it counted" grep -qE "^lost $(rid_of 1 ${B}15) arm open elapsed_s [0-9]+ end tmux_gone counted yes$" $S/state/queue_done.txt
reset; outs lost client_lag ok
case_ "a power-off during seed 15's run" "VM NOT REACHABLE" 1 FAKE_NO_CHECKS=1 FAKE_DOWN_ON_WAIT=1 WAIT_MIN=3 zsh $Q
reboot_to $BOOTB
case_ "after the reboot nothing is launched without a record" "has no checks.json (lost, or still running)" 1 FAKE_BOOT=$BOOTB zsh $Q
rec $S/state/lost_ok_$(rid_of 1 ${B}15).txt "count no" "under sandbox ruling 8(b)" "by delegate"
case_ "ruling 8(b): a delegate's 'count no' after a power-off: relaunched, not counted" "RUN ${B}15 $(rid_of 2 ${B}15) INVALID" 1 FAKE_BOOT=$BOOTB zsh $Q
case_ "so the invalid run still has its rerun" "QUEUE DONE" 0 FAKE_BOOT=$BOOTB zsh $Q
chk "three launches of seed 15" is "$(grep -c "^${B}15\$" $T/state/launched)" 3
chk "the end record: lost, arm open, ended unreachable, not counted" grep -qE "^lost $(rid_of 1 ${B}15) arm open elapsed_s [0-9]+ end unreachable counted no$" $S/state/queue_done.txt
reset; setrul 8 a; q FAKE_NO_CHECKS=1 FAKE_DOWN_ON_WAIT=1 WAIT_MIN=3; reboot_to $BOOTB
rec $S/state/lost_ok_$(rid_of 1 ${B}15).txt "count no" "under sandbox" "by delegate"
case_ "ruling 8(a): 'count no' is refused" "under ruling 8(a) a loss after a power-off counts" 1 FAKE_BOOT=$BOOTB zsh $Q
rec $S/state/lost_ok_$(rid_of 1 ${B}15).txt "count yes" "under sandbox ruling 8(a)" "by delegate"
case_ "ruling 8(a): 'count yes' by the delegate: rerun as the second attempt" "QUEUE DONE" 0 FAKE_BOOT=$BOOTB zsh $Q
reset; outs lost lost lost
q FAKE_DOWN_ON_WAIT=1 WAIT_MIN=3; reboot_to $BOOTB; rec $S/state/lost_ok_$(rid_of 1 ${B}15).txt "count no" "under sandbox" "by delegate"
q FAKE_BOOT=$BOOTB FAKE_DOWN_ON_WAIT=1 WAIT_MIN=3; reboot_to 22222222-2222-3333-4444-555555555555; rec $S/state/lost_ok_$(rid_of 2 ${B}15).txt "count no" "under sandbox" "by delegate"
q FAKE_BOOT=22222222-2222-3333-4444-555555555555 FAKE_DOWN_ON_WAIT=1 WAIT_MIN=3; reboot_to 33333333-2222-3333-4444-555555555555; rec $S/state/lost_ok_$(rid_of 3 ${B}15).txt "count no" "under sandbox" "by delegate"
case_ "ruling 8(b): a third uncounted loss of one config stops the queue" "more than 2 (ruling 8(b))" 1 FAKE_BOOT=33333333-2222-3333-4444-555555555555 zsh $Q
chk "three launches of seed 15" is "$(launches)" 3

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
chk "the records hold the arm and the log's path" sh -c "grep -qx 'arm open' $S/state/attempt_${B}15_1.txt && grep -qx 'arm closed' $S/state/attempt_${D}_1.txt && grep -q '^log ~/${B}15_' $S/state/attempt_${B}15_1.txt"
chk "and how each wait ended" sh -c "grep -qE '^end [0-9T:Z-]+ done$' $S/state/attempt_${B}15_1.txt"
chk "the drift's record has no log line (its command sets no limit)" sh -c "! grep -q nofile_log $S/state/attempt_${D}_1.txt"
chk "the open launch command starts with the limit and execs the harness" grep -qF "tmux new-session -d -s run 'ulimit -n 65536 && echo \"nofile \$(ulimit -n)\" > ~/${B}15_" $T/state/tmux_cmds
chk "and the harness writes to the same log" grep -qF "&& exec ~/.local/bin/uv run python -m harness.run configs/${B}15.yaml >> ~/${B}15_" $T/state/tmux_cmds
chk "the drift's launch command is ops_r3's, with no limit" sh -c "grep -F 'configs/$D.yaml' $T/state/tmux_cmds | grep -qF \"run '~/.local/bin/uv run python -m harness.run configs/$D.yaml > ~/\" && ! grep -F 'configs/$D.yaml' $T/state/tmux_cmds | grep -q ulimit"
reset
case_ "a launch log whose nofile line is low: the run goes on, then the queue stops and asks" "did not show an open-file limit of at least 4096" 1 FAKE_NOFILE_LOG=1024 zsh $Q
chk "the warning names the line" grep -q "WARN: the launch log's nofile line reads 'nofile 1024'" $S/state/launch_${B}15_*.out
chk "the attempt record keeps it" grep -qx "nofile_log 1024" $S/state/attempt_${B}15_1.txt
case_ "RB15: started again, the run is not used without a nofile_ok record" "state/nofile_ok_$(rid_of 1 ${B}15).txt" 1 zsh $Q
rec $S/state/nofile_ok_$(rid_of 1 ${B}15).txt "under sandbox [OPS] entry" "by delegate"
case_ "with the record the run is used and the queue goes on" "QUEUE DONE" 0 zsh $Q
chk "six launches" is "$(launches)" 6
reset
case_ "a launch log with no nofile line stops the same way" "did not show an open-file limit" 1 FAKE_NOFILE_NOLINE=1 zsh $Q
chk "recorded as '-'" grep -qx "nofile_log -" $S/state/attempt_${B}15_1.txt

echo "--- any hour: the owner withdrew the quiet hours (2026-11-13); no start is held back for the time of day"
for hh in 0000 0230 0459 1145 1415 1759 2359 abcd; do
  reset; dues yes no unclear yes no
  case_ "the whole queue, controls included, with the clock at $hh UTC" "QUEUE DONE" 0 FAKE_HHMM=$hh zsh $Q
done
chk "eight launches in the last of them: B15 C15 B16 B17 D B18 C18 B19" is "$(order)" "B15 C15 B16 B17 D B18 C18 B19"
chk "no script reads the clock as an hour" sh -c "! grep -n 'date -u +%H%M' $S/common.sh $S/launch.sh $S/queue.sh $S/final.sh $S/session_probe.sh"

echo "--- pre-launch stops spend no attempt (as ops_r3)"
reset
case_ "420 W" "STOP: power limit '420.00'" 1 FAKE_LIMIT=420.00 zsh $Q
chk "no attempt, the probe kept" is "$(nfiles "$S/state/attempt_*") $(nfiles "$PD/prelaunch_reg20_${B}15_*.txt")" "0 1"
case_ "the same command then runs, as attempt 1" "QUEUE DONE" 0 zsh $Q
reset
case_ "a reboot since the session probe" "rebooted since the session probe" 1 FAKE_BOOT=$BOOTB zsh $Q
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
chk "the attempt is spent, and the record says how the wait ended" sh -c "[ -e $S/state/attempt_${B}15_1.txt ] && grep -qE '^end .* no_run_id$' $S/state/attempt_${B}15_1.txt"
case_ "started again: the record names no run, so its nofile line is unknown (RB15)" "state/nofile_ok_$(rid_of 1 ${B}15).txt" 1 zsh $Q
rec $S/state/nofile_ok_$(rid_of 1 ${B}15).txt "under sandbox [OPS] entry: the log's nofile line read by hand" "by delegate"
case_ "with the record the finished valid run is used, not relaunched" "QUEUE DONE" 0 zsh $Q
chk "six launches in all" is "$(launches)" 6
reset
case_ "a run still going after the wait is not called invalid" "STILL RUNNING" 1 FAKE_NO_CHECKS=1 WAIT_MIN=2 zsh $Q
reset
case_ "a VM that stops answering is reported as such" "VM NOT REACHABLE" 1 FAKE_DOWN_ON_WAIT=1 WAIT_MIN=3 zsh $Q
chk "and the record says when it stopped answering" grep -qE '^end [0-9T:Z-]+ unreachable$' $S/state/attempt_${B}15_1.txt
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
chk "no copy record, no look, nothing in runs/" is "$(nfiles "$S/state/copied_*") $(looks) $(nfiles "$T/repo/runs/*")" "0 0 0"
case_ "started again: copied, verified, and on" "QUEUE DONE" 0 zsh $Q
reset
case_ "a failed copy" "copy failed" 1 FAKE_RSYNC_FAIL=1 zsh $Q
case_ "the VM's checksums unreadable" "checksums of $(rid_of 1 ${B}15) could not be read" 1 FAKE_SHA_FAIL=1 zsh $Q
case_ "a manifest update that fails" "manifest update failed" 1 FAKE_MANIFEST_FAIL=1 zsh $Q
chk "leaves no copy record" is "$(nfiles "$S/state/copied_*")" 0
case_ "started again after it: the run already in runs/ is verified again, not copied twice, and on" "QUEUE DONE" 0 zsh $Q
chk "one launch of seed 15 in all, one recheck of it" is "$(grep -c "^${B}15\$" $T/state/launched) $(grep -c "^$(rid_of 1 ${B}15) " $T/state/recheck_one_calls)" "1 1"
reset; q FAKE_PRELAUNCH_FAIL_FROM=2; mkdir -p $T/repo/runs/$(rid_of 1 ${B}15) && rm -f $S/state/copied_* $S/state/recheck_*
case_ "a run in runs/ without a recheck record stops the queue" "in runs/ without a recheck record" 1 zsh $Q

echo "--- the Mac-side checks (real git)"
reset; echo "# y" >> $T/repo/analysis/k1.py
case_ "k1.py changed in the working tree" "differs from the pin in the working tree" 2 zsh $Q
reset; (cd $T/repo && echo "# y" >> analysis/gate.py && $G commit -q -am "gate moved")
case_ "gate.py changed by a commit after the pin" "differs from the pin in the working tree" 2 zsh $Q
reset; echo "# y" >> $T/repo/analysis/load.py
case_ "the seal's load.py not the recorded blob" "analysis/load.py is not the blob" 2 zsh $Q
reset; (cd $T/repo && echo "# y" >> analysis/withheld.py && $G commit -q -am "seal moved")
case_ "withheld.py changed by a commit" "analysis/withheld.py is not the blob" 2 zsh $Q
reset; echo y >> $T/repo/uv.lock
case_ "uv.lock changed in the working tree" "differ from the pin in the working tree" 2 zsh $Q
reset; echo "# y" >> $S/queue.sh
case_ "a script changed since its commit" "differs from its committed text" 2 zsh $Q
reset; echo "# y" >> $S/control_due.py
case_ "control_due.py changed since its commit" "differs from its committed text" 2 zsh $Q
reset; echo "# y" >> $S/recheck_one.py
case_ "recheck_one.py changed since its commit" "differs from its committed text" 2 zsh $Q
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
case_ "RENEW=1 replaces it and keeps the old file" "SESSION OK" 0 RENEW=1 FAKE_BOOT=$BOOTB zsh $P
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
case_ "after QUEUE DONE: the registered command, seal lifted for REG-20, from the repo root" "{'fake': 'table', 'unseal': 'REG-20', 'cwd': '$T/repo'}" 0 zsh $F
chk "both files written" is "$(nfiles "$S/state/reg20_final_2*.txt") $(nfiles "$S/state/reg20_final_err_*.txt")" "1 1"
chk "the recheck before it ran on both patterns with the seal lifted for REG-20" sh -c "grep -qx 'REG-20 \*_l1pl350ol_r2.0_w3000_s1\[5-9\]' $T/state/recheck_env && grep -qx 'REG-20 \*_$D' $T/state/recheck_env"
chk "its records keep validity fields only" sh -c "[ $(nfiles "$S/state/reg20_recheck_final_*.json") = 2 ] && ! grep -q last_ok_scrape_t $S/state/reg20_recheck_final_*.json"
chk "it ran under .venv's python, not uv run" sh -c "! grep -q '^run' $T/state/uv_calls 2>/dev/null"
case_ "the table is computed once" "already computed or tried" 2 zsh $F
reset; q; mkdir -p $S/state/queue.lock; echo $$ > $S/state/queue.lock/pid
case_ "not while a queue holds the lock" "a queue is running" 2 zsh $F
reset; q; rm $S/state/copied_$(rid_of 3 ${B}17).txt
case_ "not when a run the end record lists as copied has no verified copy" "has no verified copy" 2 zsh $F
reset; q; rm $T/repo/runs/$(rid_of 3 ${B}17)/checks.json
case_ "RB4: nor when a copied run has no checks.json on the Mac" "no checks.json on the Mac" 2 zsh $F
reset; q; mkdir -p $T/repo/runs/20261120-090000_${B}18
case_ "RB4, RA-O2: nor when runs/ holds a REG-20 folder the queue did not copy (a lost folder copied by hand)" "does not list as copied" 2 zsh $F
reset; q; sed -i '' '1s/.*/s15 garbled/' $S/state/queue_done.txt
case_ "nor when a slot line is not of a form the queue writes" "not of a form the queue writes" 2 zsh $F
reset; q
case_ "RB2: nor when the recheck before the table changes a run the queue did not keep" "other runs than the queue kept" 2 FAKE_FINAL_EXTRA_CHANGED=${B}17 zsh $F
chk "and no table file" is "$(nfiles "$S/state/reg20_final_2*.txt")" 0
reset; q
case_ "nor when that recheck skips a sealed folder" "skipped sealed folders" 2 FAKE_RECHECK_WITHHELD=1 zsh $F
reset; q FAKE_RECHECK_FOR=${B}16
case_ "a run kept under ruling 2a at its copy is changed again before the table: agreed, table computed" "{'fake': 'table'" 0 FAKE_RECHECK_FOR=${B}16 zsh $F
reset; q
case_ "RA-O2: a table whose stderr holds a withheld line is refused, its files kept" "holds a 'withheld:' line" 1 FAKE_FINAL_WITHHELD=1 zsh $F
chk "both files kept" is "$(nfiles "$S/state/reg20_final_2*.txt") $(nfiles "$S/state/reg20_final_err_*.txt")" "1 1"
reset; q
case_ "RA4: the code changed during the table: refused, files kept" "the Mac-side checks failed just after the table" 1 FAKE_FINAL_EDIT=1 zsh $F
reset; q
case_ "a failed table stops and keeps its files" "STOP: reg20 failed" 1 FAKE_FINAL_RC=1 zsh $F
case_ "and a second try is refused" "already computed or tried" 2 zsh $F
reset; q; setlog "$H_RES"
case_ "not without the gate's headings" "the owner's rulings' heading" 2 zsh $F

chk "no script ever tried to compute the gate (computed once, 3c8e5dc)" test ! -e $T/gate_calls
echo "passed $pass, failed $fail  (sandbox $T)"
[[ $fail == 0 ]]
