# Shared, fixed settings and functions of REG-20's arm A scripts (written 2026-11-13 from REG-19's ops_r3, which they
# copy wherever REG-20 does not differ; README.md lists every difference). Read from the environment: VM_HOST and
# WAIT_MIN only (session_probe.sh also reads SET and RENEW). No seed, attempt number, run id or control decision is
# typed by anyone: `next_step` derives them from the records in state/ and from what the VM's run folders say.
R=/Users/chalshik/Projects/aftershock-artifacts
S=$R/docs/probe/20261113_reg20/ops
ST=$S/state
PROBE_DIR=$R/docs/probe/20261113_reg20
PIN=1cface77ca001cdf5d90de9313ddd4a3af4569a1    # harness/ identical to a7bb77a (REG-19's pin); adds REG-20's configs and k1.py
PY=$R/.venv/bin/python
H=chalshik@${VM_HOST:-100.83.53.50}
K=(-i $HOME/.ssh/id_ed25519_vllm -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=4)
MIN_FREE_KB=2097152                      # 2 GB free on the VM before a launch (about 240 MB per run)
MAX_ATTEMPTS=2                           # REG-20 (decisions.md 2026-11-12 [REG], standing instructions): one rerun
NOFILE_MIN=4096                          # REG-20: below this open-file limit in the launching shell, stop and ask
NOFILE_SET=65536                         # the soft limit the open arm's launch command sets
B=burst_l1pl350ol_r2.0_w3000_s           # + seed: arm A's open burst runs
C=stage2_control_l1pl350ol_r2.0_w3000_s  # + seed: their conditional controls
DRIFT=burst_l1pl350cl_r2.0_w3000_s15_drift
ALLCFG=(); for sd in 15 16 17 18 19; do ALLCFG+=(${B}$sd ${C}$sd); done; ALLCFG+=($DRIFT)
# The registered order: open burst runs 15-19, the drift run after the third; each open burst run's control, when due,
# right after it (it is not listed: `next_step` puts it there). Conditional controls do not count as runs.
PLAN=(${B}15 ${B}16 ${B}17 $DRIFT ${B}18 ${B}19)
# The two headings that allow arm A, both in the committed docs/decisions.md, the second on a later line. The scripts
# never compute REG-20's gate (k1.reg20_a_may_start) themselves. "([^0-9]|$)" keeps "[RESULT] REG-190" out.
RESULT_PAT='^## [0-9]{4}-[0-9]{2}-[0-9]{2} · \[RESULT\] REG-19([^0-9]|$)'
START_PAT='^## [0-9]{4}-[0-9]{2}-[0-9]{2} · \[DECISION\] \((owner|delegate)\) REG-20 arm A starts'
# No time-of-day limit: the owner withdrew the quiet hours on 2026-11-13 ("there is no such thing as quiet hours,
# whenever its available use it, power off happens randomly"; decisions.md 2026-11-13 [DECISION] (owner), REG-19:
# the quiet hours are withdrawn). A run starts whenever the queue reaches it.
DRIVER=595.99.02                         # the pinned driver (PROTOCOL.md, section 4, Software)
SCRIPTS=(common.sh vm_state.py session_probe.sh launch.sh queue.sh final.sh control_due.py)
# The code control_due.py and final.sh run on the Mac, from the repo root: k1.py's import closure at the pin, plus the
# seal (analysis/load.py's guard and analysis/withheld.py), which the pin predates, at the blobs of 2026-11-13.
JUDGED=(analysis/__init__.py analysis/k1.py analysis/gate.py analysis/margin.py analysis/derived.py analysis/floor.py analysis/stats.py)
SEAL_FILES=(analysis/load.py analysis/withheld.py)
SEAL_BLOBS=(59ef93b9ecd5882b456b907b3a7a80851b58cc5e 46b42a76a44a52051f25796fb3b917470378ccd2)
ALLOWED="Allowed reads while diagnosing a stop: 'tmux has-session -t run'; the folder names under runs/; a run's checks.json (valid, failed); in a launch log only the lines holding 'run_id', 'nofile' or '[run] checks'. Nothing else of a log or a run folder, and no analysis of a REG-20 run but control_due.py's one line (REG-20: no interim look)."

# File-name stamp, left in REPLY (as ops_r3). Call it as `stamp`, never as $(stamp).
STAMP_N=0
stamp() { STAMP_N=$((STAMP_N + 1)); REPLY="$(date -u +%Y%m%dT%H%M%SZ)_$$_$STAMP_N"; }

# Mac-side checks before every launch, step and table: the pin an ancestor of HEAD; the files used from the Mac's
# working tree (manifest tool, lock files) equal to the pin's; every config REG-20 names present at the pin; the code
# that control_due.py and final.sh run equal to the pin's (k1.py's import closure) or to the recorded blobs (the seal);
# these scripts tracked, equal to their committed text, and that commit the one in scripts_commit.txt. Sets SC.
mac_checks() {
  local p paths c i
  cd $R || { echo "STOP: no repo at $R"; return 2; }
  git merge-base --is-ancestor $PIN HEAD || { echo "STOP: the pin $PIN is not an ancestor of the Mac HEAD"; return 2; }
  git diff --quiet $PIN -- tools/manifest.py pyproject.toml uv.lock || { echo "STOP: tools/manifest.py, pyproject.toml or uv.lock differ from the pin in the working tree"; return 2; }
  for c in $ALLCFG; do
    git cat-file -e ${PIN}:configs/$c.yaml 2> /dev/null || { echo "STOP: no config $c.yaml at the pin"; return 2; }
  done
  for p in $JUDGED; do
    git cat-file -e ${PIN}:$p 2> /dev/null && [[ -f $R/$p ]] || { echo "STOP: $p is missing at the pin or in the working tree"; return 2; }
  done
  git diff --quiet $PIN -- $JUDGED || { echo "STOP: the analysis code control_due.py and final.sh run (${JUDGED[*]}) differs from the pin in the working tree"; return 2; }
  for i in 1 2; do
    [[ -f $R/$SEAL_FILES[i] && $(git hash-object $R/$SEAL_FILES[i]) == $SEAL_BLOBS[i] ]] || { echo "STOP: $SEAL_FILES[i] is not the blob $SEAL_BLOBS[i] recorded in common.sh"; return 2; }
  done
  paths=(${SCRIPTS[@]/#/docs/probe/20261113_reg20/ops/})
  for p in $paths; do
    git ls-files --error-unmatch $p > /dev/null 2>&1 || { echo "STOP: $p is not tracked by git"; return 2; }
  done
  git diff --quiet HEAD -- $paths || { echo "STOP: a REG-20 script differs from its committed text"; return 2; }
  SC=$(git log -1 --format=%H -- $paths)
  [[ -n $SC ]] || { echo "STOP: the REG-20 scripts are not committed"; return 2; }
  [[ -f $S/scripts_commit.txt ]] || { echo "STOP: no scripts_commit.txt"; return 2; }
  [[ $(<$S/scripts_commit.txt) == $SC ]] || { echo "STOP: the scripts changed since scripts_commit.txt (now $SC)"; return 2; }
  return 0
}

# Arm A may start only when HEAD's docs/decisions.md holds REG-19's [RESULT] heading and, on a later line, the heading
# of the decision that arm A starts. Sets MSG and returns 2 when not.
gate_in_log() {
  local log rl sl
  MSG=""
  log=$(git -C $R show HEAD:docs/decisions.md 2> /dev/null) || { MSG="the committed docs/decisions.md cannot be read"; return 2; }
  rl=$(print -r -- "$log" | grep -n -E "$RESULT_PAT" | head -1 | cut -d: -f1)
  [[ -n $rl ]] || { MSG="no '[RESULT] REG-19' heading in the committed docs/decisions.md: arm A does not start"; return 2; }
  sl=$(print -r -- "$log" | grep -n -E "$START_PAT" | tail -1 | cut -d: -f1)
  [[ -n $sl ]] || { MSG="no '[DECISION] (owner|delegate) REG-20 arm A starts' heading in the committed docs/decisions.md: arm A does not start"; return 2; }
  (( sl > rl )) || { MSG="the heading that starts arm A (line $sl) is not after REG-19's [RESULT] (line $rl): arm A does not start"; return 2; }
  return 0
}

# What the VM holds for REG-20's eleven configs: one line per run folder,
# "<run id> valid|invalid|nochecks|unreadable <failed|-> <commit|->". Read-only: vm_state.py is sent on stdin.
vm_state() {
  local out
  VMS=()
  out=$(ssh $K $H "python3 - ${ALLCFG[*]}" < $S/vm_state.py) || return 1
  [[ ${out##*$'\n'} == "END ${#ALLCFG}" ]] || return 1
  VMS=("${(@f)out}"); VMS=(${VMS[1,-2]})
  return 0
}

# REG-20's rerun rule for one config, from the attempt records, the rerun_ok records and the VM's checks.json files
# (VMS, read by vm_state before). Returns 0 with RID set (one valid run at the pin: use it), with LAUNCH set (the
# number of the attempt to launch) or with LOST set (an open burst run invalid twice: `lost_open`, which REG-20
# counts as cold; no control); returns 2 with MSG set when the registration stops the queue.
#   - every launch is one attempt; at most MAX_ATTEMPTS (one run, one rerun);
#   - more run folders of the config on the VM than attempt records stop the queue (a launch outside these scripts);
#   - a run folder of the config on the Mac that the VM does not list stops the queue;
#   - a valid run is used only if it was made at the pin (env.json's git_commit);
#   - no rerun after a client error (`no_errors/client_error`), a burst that did not fill the pool (`manipulation`) or
#     a limit other than 350 W (`power_limit`), and a second heat failure (`gpu_steady`) among REG-20's runs stops the
#     queue, unless the owner's decision is recorded as state/rerun_ok_<that run id>.txt;
#   - a run folder without checks.json (a lost run) is not rerun without state/rerun_ok_<run id>.txt either;
#   - when both attempts of an open burst run left an invalid checks.json, the seed is `lost_open` (REG-20's label);
#     a control or the drift run with its attempts spent stops the queue.
decide() {
  local cfg=$1 line parts f id n_valid=0 n_heat=0 norerun="" bad="" lost="" commit="" atts mine inval
  RID=""; LAUNCH=""; LOST=""; MSG=""; mine=(); inval=()
  for line in $VMS; do
    parts=(${=line})
    if [[ ! -f $ST/rerun_ok_$parts[1].txt ]]; then
      for f in ${(s:,:)parts[3]}; do [[ $f == gpu_steady ]] && n_heat=$((n_heat + 1)); done   # over every REG-20 run
    fi
    [[ $parts[1] == *_$cfg ]] || continue
    mine+=($parts[1])
    case $parts[2] in
      valid) n_valid=$((n_valid + 1)); RID=$parts[1]; commit=$parts[4];;
      invalid)
        inval+=($parts[1])
        if [[ ! -f $ST/rerun_ok_$parts[1].txt ]]; then
          for f in ${(s:,:)parts[3]}; do
            case $f in no_errors/client_error|manipulation|power_limit) norerun="$f ($parts[1])";; esac
          done
        fi;;
      nochecks) [[ -f $ST/rerun_ok_$parts[1].txt ]] || lost=$parts[1];;
      *) bad=$parts[1];;
    esac
  done
  atts=($ST/attempt_${cfg}_<->.txt(N))
  [[ -z $bad ]] || { RID=""; MSG="checks.json of $bad cannot be read"; return 2; }
  (( n_valid <= 1 )) || { RID=""; MSG="the VM holds $n_valid valid runs of $cfg: the owner decides"; return 2; }
  (( ${#mine} <= ${#atts} )) || { RID=""; MSG="the VM holds ${#mine} run folders of $cfg and only ${#atts} attempts are recorded in $ST"; return 2; }
  for id in $R/runs/*_${cfg}(N/:t); do
    [[ ${mine[(Ie)$id]} -gt 0 ]] || { RID=""; MSG="the Mac holds $id, which the VM does not list: nothing of $cfg is launched or used; the owner decides"; return 2; }
  done
  if (( n_valid == 1 )); then
    [[ $commit == $PIN ]] && return 0
    MSG="the valid run $RID of $cfg was made at commit '$commit', not at the pin: the owner decides"; RID=""; return 2
  fi
  [[ -z $norerun ]] || { MSG="REG-20 says stop and ask after $norerun: a rerun, or going on, needs the owner's decision recorded as $ST/rerun_ok_<that run id>.txt"; return 2; }
  [[ -z $lost ]] || { MSG="$lost has no checks.json (lost or still running): a rerun needs its own decision, recorded as $ST/rerun_ok_$lost.txt"; return 2; }
  (( n_heat < 2 )) || { MSG="second heat failure (gpu_steady) among REG-20's runs: the queue stops; the owner decides (a record state/rerun_ok_<run id>.txt for the second one lets it go on)"; return 2; }
  if (( ${#atts} >= MAX_ATTEMPTS )); then
    if [[ $cfg == ${B}* ]] && (( ${#inval} >= MAX_ATTEMPTS )); then LOST="${inval[*]}"; return 0; fi
    MSG="the $MAX_ATTEMPTS attempts of $cfg are spent (${#inval} left an invalid checks.json): operational stop, the owner decides"; return 2
  fi
  LAUNCH=$((${#atts} + 1))
  [[ ! -e $ST/attempt_${cfg}_$LAUNCH.txt ]] || { MSG="attempt records of $cfg are not numbered 1..${#atts}"; LAUNCH=""; return 2; }
  return 0
}

# Sets ACT=copy and ARG when a finished run of config $1 (valid or invalid: k1 counts invalid open runs towards
# `lost_open`) is not yet on the Mac with a verified copy record; returns 1 when none is pending.
copy_pending() {
  local line parts
  for line in $VMS; do
    parts=(${=line})
    [[ $parts[1] == *_$1 && ( $parts[2] == valid || $parts[2] == invalid ) && ! -f $ST/copied_$parts[1].txt ]] || continue
    ACT=copy; ARG=$parts[1]; return 0
  done
  return 1
}

# The recorded control decision of open burst run $1, left in DUE ("" when none yet); 2 when the record is bad.
due_of() {
  local lines
  DUE=""
  [[ -f $ST/control_due.txt ]] || return 0
  lines=("${(@f)$(awk -v r="$1" '$1 == r' $ST/control_due.txt)}"); lines=(${lines:#})
  (( ${#lines} <= 1 )) || { MSG="state/control_due.txt holds ${#lines} decisions for $1"; return 2; }
  (( ${#lines} == 1 )) || return 0
  DUE=${${(s: :)lines[1]}[3]}
  [[ ${${(s: :)lines[1]}[2]} == CONTROL_DUE && $DUE == (yes|no|unclear) ]] || { MSG="the control decision recorded for $1 is not 'CONTROL_DUE yes|no|unclear'"; DUE=""; return 2; }
  return 0
}

# No control of seed $1 may exist when none is due: no run folder on the VM or the Mac, no attempt record.
no_control() {
  local ctl=${C}$1 line atts
  atts=($ST/attempt_${ctl}_<->.txt(N) $R/runs/*_${ctl}(N/))
  for line in $VMS; do [[ ${${=line}[1]} == *_$ctl ]] && atts+=($line); done
  (( ${#atts} == 0 )) || { MSG="seed $1's control has a run or an attempt although none is due ($2): the owner decides"; return 2; }
  return 0
}

# The next thing to do, from the plan, the state records and the VM (read once). ACT is one of:
#   copy <run id>     a finished run to copy to the Mac and verify;
#   due <run id>      control_due.py to run, once, on a valid open burst run already copied and verified;
#   launch <config>   with NEXT_ATT, the attempt number;
#   done              every slot of the plan settled; SUMMARY holds one line per slot.
# Returns 2 with MSG when the registration, or a record, stops the queue. Writes nothing.
next_step() {
  local cfg sd rid
  ACT=""; ARG=""; NEXT_ATT=""; MSG=""; SUMMARY=()
  vm_state || { MSG="the VM's run folders could not be read"; return 2; }
  for cfg in $PLAN; do
    decide $cfg || return 2
    copy_pending $cfg && return 0
    [[ -n $LAUNCH ]] && { ACT=launch; ARG=$cfg; NEXT_ATT=$LAUNCH; return 0; }
    if [[ $cfg == $DRIFT ]]; then SUMMARY+=("drift $RID"); continue; fi
    sd=${cfg##*_s}
    if [[ -n $LOST ]]; then
      no_control $sd lost_open || return 2
      SUMMARY+=("s$sd lost_open $LOST"); continue
    fi
    rid=$RID
    due_of $rid || return 2
    [[ -n $DUE ]] || { ACT=due; ARG=$rid; return 0; }
    if [[ $DUE == yes ]]; then
      decide ${C}$sd || return 2
      copy_pending ${C}$sd && return 0
      [[ -n $LAUNCH ]] && { ACT=launch; ARG=${C}$sd; NEXT_ATT=$LAUNCH; return 0; }
      SUMMARY+=("s$sd $rid CONTROL_DUE yes control $RID")
    else
      no_control $sd "CONTROL_DUE $DUE" || return 2
      SUMMARY+=("s$sd $rid CONTROL_DUE $DUE")
    fi
  done
  ACT=done
  return 0
}

# Copy one finished run to the Mac, compare every file's sha256 with the VM's (as ops_r3's queue), update the
# manifest, and only then write state/copied_<run id>.txt. Returns 2 with MSG on any failure.
copy_verify() {
  local rid=$1 la lb a b
  cd $R || { MSG="no repo"; return 2; }
  rsync -a -e "ssh ${K[*]}" "${H}:aftershock-artifacts/runs/$rid" runs/ || { MSG="copy failed $rid"; return 2; }
  la=$(ssh $K $H "cd ~/aftershock-artifacts/runs/$rid && find . -type f | LC_ALL=C sort | xargs sha256sum") || { MSG="the VM's checksums of $rid could not be read"; return 2; }
  lb=$(cd runs/$rid && find . -type f | LC_ALL=C sort | xargs shasum -a 256) || { MSG="the Mac's checksums of $rid could not be computed"; return 2; }
  [[ -n $la && -n $lb ]] || { MSG="empty checksum list for $rid"; return 2; }
  a=$(print -r -- "$la" | shasum -a 256 | cut -c1-16); b=$(print -r -- "$lb" | shasum -a 256 | cut -c1-16)
  [[ $a == $b ]] || { MSG="checksum mismatch $rid (vm [$a] mac [$b])"; return 2; }
  python3 tools/manifest.py update > /dev/null || { MSG="manifest update failed after copying $rid"; return 2; }
  print -r -l -- "rid $rid" "files ${#${(f)la}}" "sha_of_sums $a" "time $(date -u +%Y-%m-%dT%H:%M:%SZ)" > $ST/copied_$rid.tmp && mv $ST/copied_$rid.tmp $ST/copied_$rid.txt || { MSG="the copy record of $rid could not be written"; return 2; }
  echo "COPIED $rid ${#${(f)la}} files sha-of-sums $a"
  return 0
}
