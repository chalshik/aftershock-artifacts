# Shared, fixed settings and functions of REG-20's arm A scripts (draft 2, 2026-11-14; first written 2026-11-13 from
# REG-19's ops_r3, which they copy wherever REG-20 does not differ; README.md lists every difference). Read from the
# environment: VM_HOST and WAIT_MIN only (session_probe.sh also reads SET and RENEW). No seed, attempt number, run id or
# control decision is typed by anyone: `next_step` derives them from the records in state/, the owner's rulings in
# owner_rulings.txt and what the VM's run folders say. Hand-written records (rerun_ok, lost_ok, settle, attempt_ok,
# nofile_ok, recheck_ok) are small text files of "key value" lines; each needs `under <the decision or ruling>` and
# `by owner|delegate`, and the scripts check that the writer is one the rulings allow (README.md, "Records").
R=/Users/chalshik/Projects/aftershock-artifacts
S=$R/docs/probe/20261113_reg20/ops
ST=$S/state
PROBE_DIR=$R/docs/probe/20261113_reg20
STAGE=${R:h}/aftershock-reg20-holding    # outside every runs/: each run is copied here, rechecked, then moved into runs/ or held here
PIN=1cface77ca001cdf5d90de9313ddd4a3af4569a1    # harness/ identical to a7bb77a (REG-19's pin); adds REG-20's configs and k1.py
PY=$R/.venv/bin/python
CHECKS_COMMIT=5ee6e38d3a15994da8bb6597b9b13ea8be08807c    # harness/checks.py as of this commit: the checks in force (A14)
RECHECK_COMMIT=72fafb5991e036eddf1c4ce40b39bc1ca81fa74e   # analysis/recheck.py as of this commit
H=chalshik@${VM_HOST:-100.83.53.50}
K=(-i $HOME/.ssh/id_ed25519_vllm -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=4)
MIN_FREE_KB=2097152                      # 2 GB free on the VM before a launch (about 240 MB per run)
MAX_ATTEMPTS=2                           # REG-20 (decisions.md 2026-11-12 [REG], standing instructions): one rerun
MAX_POWER_LOSSES=2                       # ruling 8(b): losses after a power-off that are not counted, per config
NOFILE_MIN=4096                          # REG-20: below this open-file limit in the launching shell, stop and ask
NOFILE_SET=65536                         # the soft limit the open arm's launch command sets
SETUP_CLASS=(clean_git kv_capacity trigger)   # RA3: checks whose inputs lie before the burst ends or outside the server (BELIEF; fixed here)
B=burst_l1pl350ol_r2.0_w3000_s           # + seed: arm A's open burst runs
C=stage2_control_l1pl350ol_r2.0_w3000_s  # + seed: their conditional controls
DRIFT=burst_l1pl350cl_r2.0_w3000_s15_drift
ALLCFG=(); for sd in 15 16 17 18 19; do ALLCFG+=(${B}$sd ${C}$sd); done; ALLCFG+=($DRIFT)
# The registered order: open burst runs 15-19, the drift run after the third; each open burst run's control, when due,
# right after it (it is not listed: `next_step` puts it there). Conditional controls do not count as runs.
PLAN=(${B}15 ${B}16 ${B}17 $DRIFT ${B}18 ${B}19)
# The patterns of analysis.recheck over the Mac's runs/ before the table: the open runs (burst runs and controls) and the drift run.
RECHECK_PATS=('*_l1pl350ol_r2.0_w3000_s1[5-9]' "*_$DRIFT")
# Headings in the committed docs/decisions.md. Arm A starts only when REG-19's [RESULT], the owner's rulings and the start
# decision are there, the start after both, and no stop heading follows the start. The scripts never compute REG-20's
# gate: it was computed once after REG-19's [RESULT], in commit 3c8e5dc (docs/probe/reg20/gate_<stamp>.txt and its
# stderr file, committed alone), and that committed file must read 'may_start': True on its one line. "([^0-9]|$)" keeps
# "[RESULT] REG-190" out; "([^0-9A-Za-z]|$)" keeps "starts: k1.reg20_a_may_start passed" from matching a longer word.
RESULT_PAT='^## [0-9]{4}-[0-9]{2}-[0-9]{2} · \[RESULT\] REG-19([^0-9]|$)'
RULINGS_PAT='^## [0-9]{4}-[0-9]{2}-[0-9]{2} · \[DECISION\] \(owner\) REG-20 arm A operations: the owner.s rulings([^0-9A-Za-z]|$)'
START_PAT='^## [0-9]{4}-[0-9]{2}-[0-9]{2} · \[DECISION\] \((owner|delegate)\) REG-20 arm A starts: k1\.reg20_a_may_start passed([^0-9A-Za-z]|$)'
STOP_PAT='^## [0-9]{4}-[0-9]{2}-[0-9]{2} · \[(DECISION|CORR|OPS)\]( \((owner|delegate)\))? REG-20 arm A (stops|is stopped)([^0-9A-Za-z]|$)'
GATE_DIR=docs/probe/reg20               # where REG-20's gate output is committed (3c8e5dc): gate_<stamp>.txt, gate_err_<stamp>.txt
GATE_FILE_RE='^gate_[0-9]{8}T[0-9]{6}Z\.txt$'
GATE_LINE_RE="^[{]'k_closed': [0-9]+, 'n': [0-9]+, 'best_p': [0-9.e+-]+, 'may_start': True[}]\$"
# The owner's points (draft 2, "For the owner, before the first launch") and the answers each may take.
RULINGS=$S/owner_rulings.txt
RULING_KEYS=(2a 6 7 8 9 16)
DRIVER=595.99.02                         # the pinned driver (PROTOCOL.md, section 4, Software)
SCRIPTS=(common.sh vm_state.py session_probe.sh launch.sh queue.sh final.sh control_due.py recheck_one.py)
# The code control_due.py and final.sh run on the Mac, from the repo root: k1.py's import closure at the pin,
# plus the seal (analysis/load.py's guard and analysis/withheld.py), which the pin predates, at the blobs of 2026-11-13.
JUDGED=(analysis/__init__.py analysis/k1.py analysis/gate.py analysis/margin.py analysis/derived.py analysis/floor.py analysis/stats.py)
SEAL_FILES=(analysis/load.py analysis/withheld.py)
SEAL_BLOBS=(59ef93b9ecd5882b456b907b3a7a80851b58cc5e 46b42a76a44a52051f25796fb3b917470378ccd2)
ALLOWED="Allowed reads while diagnosing a stop: 'tmux has-session -t run'; the folder names under runs/; a run's checks.json (valid, failed); in a launch log only the lines holding 'run_id', 'nofile' or '[run] checks'; the queue's RECHECK, HELD and SET ASIDE lines and the validity fields of state/recheck_*.json. Nothing else of a log or a run folder, and no analysis of a REG-20 run but control_due.py's one line (REG-20: no interim look)."

# File-name stamp, left in REPLY (as ops_r3). Call it as `stamp`, never as $(stamp).
STAMP_N=0
stamp() { STAMP_N=$((STAMP_N + 1)); REPLY="$(date -u +%Y%m%dT%H%M%SZ)_$$_$STAMP_N"; }
now() { date -u +%Y-%m-%dT%H:%M:%SZ; }
epoch() { date -j -u -f %Y-%m-%dT%H:%M:%SZ "$1" +%s 2> /dev/null; }

# Mac-side checks before every turn of the queue, every launch, the gate and the table: the pin an ancestor of HEAD;
# the files used from the Mac's working tree (manifest tool, lock files) equal to the pin's; every config REG-20 names
# present at the pin; the code that control_due.py and final.sh run equal to the pin's (k1.py's import
# closure) or to the recorded blobs (the seal); these scripts tracked, equal to their committed text, and that commit
# the one in scripts_commit.txt. Sets SC.
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

# The owner's answer on point $1, from owner_rulings.txt ("" when absent).
ruling() { awk -v k="$1" '$1 == k {print $2; exit}' $RULINGS 2> /dev/null; }

# Every point the owner rules (RA5) has an answer it may take, in a tracked, committed owner_rulings.txt. Sets MSG.
rulings_ok() {
  local k v rel=${RULINGS#$R/}
  local -a allowed
  MSG=""
  [[ -f $RULINGS ]] || { MSG="no owner_rulings.txt"; return 2; }
  git -C $R ls-files --error-unmatch $rel > /dev/null 2>&1 || { MSG="owner_rulings.txt is not tracked by git"; return 2; }
  git -C $R diff --quiet HEAD -- $rel || { MSG="owner_rulings.txt differs from its committed text"; return 2; }
  for k in $RULING_KEYS; do
    v=$(ruling $k)
    case $k in
      2a) allowed=(keep setaside stop pin_head);;
      6|8) allowed=(a b);;
      7) allowed=(lost_open not_run per_stop);;
      9) allowed=(a b);;
      16) allowed=(a b c);;
    esac
    [[ -n $v && ${allowed[(Ie)$v]} -gt 0 ]] || { MSG="the owner's ruling on point $k reads '${v:-none}' in owner_rulings.txt, not one of: ${allowed[*]}: arm A does not start (RA5)"; return 2; }
  done
  [[ $(ruling 2a) != pin_head ]] || { MSG="the owner chose a pin at or after 5ee6e38 (point 2a): common.sh's PIN changes by a reviewed commit first"; return 2; }
  return 0
}

# Arm A may start only when HEAD's docs/decisions.md holds REG-19's [RESULT] heading, the owner's rulings heading and,
# on a later line than both, the start decision's heading, with no stop heading after it; HEAD holds exactly one gate
# file in docs/probe/reg20/ whose one line reads 'may_start': True, with its stderr file and no `withheld:` line there; and every
# owner's ruling is recorded. Sets MSG and returns 2 when not.
gate_in_log() {
  local log rl gl sl tl f ge body
  local -a files gf
  MSG=""
  log=$(git -C $R show HEAD:docs/decisions.md 2> /dev/null) || { MSG="the committed docs/decisions.md cannot be read"; return 2; }
  rl=$(print -r -- "$log" | grep -n -E "$RESULT_PAT" | head -1 | cut -d: -f1)
  [[ -n $rl ]] || { MSG="no '[RESULT] REG-19' heading in the committed docs/decisions.md: arm A does not start"; return 2; }
  gl=$(print -r -- "$log" | grep -n -E "$RULINGS_PAT" | tail -1 | cut -d: -f1)
  [[ -n $gl ]] || { MSG="no '[DECISION] (owner) REG-20 arm A operations: the owner's rulings' heading in the committed docs/decisions.md: arm A does not start (RA5)"; return 2; }
  sl=$(print -r -- "$log" | grep -n -E "$START_PAT" | tail -1 | cut -d: -f1)
  [[ -n $sl ]] || { MSG="no '[DECISION] (owner|delegate) REG-20 arm A starts: k1.reg20_a_may_start passed' heading in the committed docs/decisions.md: arm A does not start"; return 2; }
  (( sl > rl )) || { MSG="the heading that starts arm A (line $sl) is not after REG-19's [RESULT] (line $rl): arm A does not start"; return 2; }
  (( sl > gl )) || { MSG="the heading that starts arm A (line $sl) is not after the owner's rulings (line $gl): arm A does not start"; return 2; }
  tl=$(print -r -- "$log" | grep -n -E "$STOP_PAT" | tail -1 | cut -d: -f1)
  [[ -z $tl ]] || (( tl < sl )) || { MSG="a heading that stops arm A (line $tl) follows the one that starts it (line $sl): arm A does not start"; return 2; }
  files=(${(f)"$(git -C $R ls-tree --name-only HEAD -- $GATE_DIR/ 2> /dev/null)"})
  gf=(); for f in $files; do [[ ${f:t} =~ $GATE_FILE_RE ]] && gf+=($f); done
  (( ${#gf} == 1 )) || { MSG="HEAD holds ${#gf} gate files ($GATE_DIR/gate_<stamp>.txt; the gate is computed once, 3c8e5dc) where exactly one is required: arm A does not start"; return 2; }
  ge=${gf[1]:h}/gate_err_${${gf[1]:t}#gate_}
  git -C $R cat-file -e HEAD:$ge 2> /dev/null || { MSG="the gate's stderr file ${ge:t} is not committed: arm A does not start"; return 2; }
  body=$(git -C $R show HEAD:$gf[1])
  [[ $(print -r -- "$body" | grep -c .) == 1 && $(print -r -- "$body" | grep -c -E "$GATE_LINE_RE") == 1 ]] || { MSG="the gate file ${gf[1]:t} does not read 'may_start': True on its one line: arm A does not start"; return 2; }
  if git -C $R show HEAD:$ge | grep -q '^withheld:'; then MSG="the gate's stderr file ${ge:t} holds a 'withheld:' line: arm A does not start"; return 2; fi
  rulings_ok || return 2
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

# Records. rv: the value of key $2 in record $1. rec_by: record $1 exists, names what it is written under and is
# written by one of $2...
rv() { [[ -f $1 ]] && sed -n "s/^$2 //p" $1 | head -1; }
rec_by() {
  local f=$1 by under; shift
  [[ -f $f ]] || return 1
  by=$(rv $f by); under=$(rv $f under)
  [[ -n $under && -n $by && ${argv[(Ie)$by]} -gt 0 ]]
}
cur_boot() { [[ -s $ST/session_boot_id.txt ]] && print -r -- "$(<$ST/session_boot_id.txt)"; }

# The attempt record of run $1 (the one holding "rid $1"): AREC, ABOOT, ANOF (nofile_log), ATIME (launch), AEND
# ("<time> <how>", from launch.sh), AARM. Returns 1 when no record names the run.
att_of() {
  local f
  AREC=""; ABOOT=""; ANOF=""; ATIME=""; AEND=""; AARM=""
  for f in $ST/attempt_*_<->.txt(N); do
    if grep -qx "rid $1" $f; then AREC=$f; break; fi
  done
  [[ -n $AREC ]] || return 1
  ABOOT=$(rv $AREC boot); ANOF=$(rv $AREC nofile_log); ATIME=$(rv $AREC time); AEND=$(rv $AREC end); AARM=$(rv $AREC arm)
  return 0
}

# A stop-and-ask failure $2 of run $1 is lifted only by state/rerun_ok_$1.txt with the line "lifts $2" (RA-O4), written
# by the owner; under ruling 6(b) a client error's record may be the delegate's when the run's launch log read an
# open-file limit of at least NOFILE_MIN and the VM did not reboot since the run's launch (draft 2, point 6(b)).
lift_ok() {
  local f=$ST/rerun_ok_$1.txt
  [[ -f $f ]] && grep -qx "lifts $2" $f || return 1
  rec_by $f owner && return 0
  if [[ $2 == no_errors/client_error && $(ruling 6) == b ]] && rec_by $f delegate; then
    att_of $1 || return 1
    [[ $ANOF == <-> ]] && (( ANOF >= NOFILE_MIN )) && [[ -n $ABOOT && $ABOOT == $(cur_boot) ]] && return 0
  fi
  return 1
}

# A run of config $1 without checks.json (lost) is counted or not by state/lost_ok_<run id>.txt ("count yes|no"),
# under ruling 8: after a power-off (the run's launch boot differs from the session's) 8(a) counts it (by owner or
# delegate) and 8(b) does not (by owner or delegate; at most MAX_POWER_LOSSES per config); a loss without a reboot, or
# one whose launch boot is unknown, is the owner's either way. Sets LCOUNT yes|no; returns 1 with MSG when not settled.
lost_count() {
  local id=$1 f=$ST/lost_ok_$1.txt c power=""
  LCOUNT=""
  att_of $id && [[ -n $ABOOT && $ABOOT != $(cur_boot) ]] && power=1
  [[ -f $f ]] || { MSG="$id has no checks.json (lost, or still running): nothing of its config is launched until a record state/lost_ok_$id.txt ('count yes|no', 'under …', 'by …') settles it under ruling 8 (the VM rebooted since its launch: ${power:+yes}${power:-no, so the record is the owner's})"; return 1; }
  c=$(rv $f count)
  [[ $c == (yes|no) ]] || { MSG="state/lost_ok_$id.txt has no 'count yes' or 'count no' line"; return 1; }
  if [[ -n $power ]]; then
    if [[ $(ruling 8) == a ]]; then
      [[ $c == yes ]] && rec_by $f owner delegate || { MSG="state/lost_ok_$id.txt: under ruling 8(a) a loss after a power-off counts ('count yes'), by owner or delegate"; return 1; }
    else
      { [[ $c == no ]] && rec_by $f owner delegate; } || { [[ $c == yes ]] && rec_by $f owner; } || { MSG="state/lost_ok_$id.txt: under ruling 8(b) a loss after a power-off is 'count no' (owner or delegate), or 'count yes' by the owner"; return 1; }
    fi
  else
    rec_by $f owner || { MSG="state/lost_ok_$id.txt: $id was lost without a reboot since its launch (or its launch boot is unknown): the owner's record only"; return 1; }
  fi
  LCOUNT=$c
  return 0
}

# REG-20's rerun rule for one config, from the attempt records, the hand-written records, the owner's rulings and the
# VM's checks.json files (VMS, read by vm_state before). Returns 0 with RID set (one valid run at the pin: use it),
# with LAUNCH set (the number of the attempt to launch), with LOST set (an open burst run invalid twice: `lost_open`,
# which REG-20 counts as cold; no control) or with SETTLED set (a slot settled by a settle record: not_run,
# control_not_run or drift_not_run; SRID names the run the record names); returns 2 with MSG set when the queue stops.
#   - every launch is one attempt; at most MAX_ATTEMPTS (one run, one rerun), plus one per attempt_ok record;
#     a loss after a power-off that a lost_ok record does not count (ruling 8(b)) is not an attempt;
#   - more run folders of the config on the VM than attempt records stop the queue (a launch outside these scripts);
#   - a run folder of the config on the Mac that the VM does not list stops the queue;
#   - a valid run is used only if it was made at the pin (env.json's git_commit), and an open one whose launch log did
#     not show an open-file limit of at least NOFILE_MIN only with state/nofile_ok_<run id>.txt (RB15);
#   - a run set aside by the recheck (state/setaside_<run id>.txt, ruling 2a) is a spent attempt, not a valid run,
#     and not one of k1's invalid runs (it never enters runs/);
#   - no rerun after a client error (`no_errors/client_error`), a burst that did not fill the pool (`manipulation`) or
#     a limit other than 350 W (`power_limit`), and a second heat failure (`gpu_steady`) among REG-20's runs stops the
#     queue, unless state/rerun_ok_<that run id>.txt lifts that failure by name (lift_ok);
#   - a run folder without checks.json is not rerun until a lost_ok record settles it (lost_count);
#   - when both attempts of an open burst run left an invalid checks.json, the seed is `lost_open` (REG-20's label),
#     unless either attempt failed only checks of SETUP_CLASS (RA3): then the queue stops, and a settle record under
#     ruling 7 says lost_open or not_run; a control or the drift run with its attempts spent stops the queue.
decide() {
  local cfg=$1 line id st failed f n_valid=0 n_heat=0 norerun="" bad="" lost="" commit="" only nmax extra n counted sf slab okrec setup_case
  local -a parts atts inval setup setas lostp cinval settles
  RID=""; LAUNCH=""; LOST=""; SETTLED=""; SRID=""; MSG=""; MINE=(); inval=(); setup=(); setas=(); lostp=()
  for line in $VMS; do
    parts=(${=line}); id=$parts[1]; st=$parts[2]; failed=$parts[3]
    if [[ -f $ST/setaside_$id.txt ]]; then st=setaside; failed=$(rv $ST/setaside_$id.txt now_failed); fi
    for f in ${(s:,:)failed}; do [[ $f == gpu_steady ]] && ! lift_ok $id gpu_steady && n_heat=$((n_heat + 1)); done   # over every REG-20 run
    [[ $id == *_$cfg ]] || continue
    MINE+=($id)
    case $st in
      valid) n_valid=$((n_valid + 1)); RID=$id; commit=$parts[4];;
      setaside) setas+=($id);;
      invalid)
        inval+=($id); only=1
        for f in ${(s:,:)failed}; do
          case $f in no_errors/client_error|manipulation|power_limit) lift_ok $id $f || norerun="$f ($id)";; esac
          [[ ${SETUP_CLASS[(Ie)$f]} -gt 0 ]] || only=""
        done
        [[ -n $only && $failed != - ]] && setup+=($id);;
      nochecks)
        if lost_count $id; then [[ $LCOUNT == no ]] && lostp+=($id); else lost=$id; fi;;
      *) bad=$id;;
    esac
  done
  atts=($ST/attempt_${cfg}_<->.txt(N))
  [[ -z $bad ]] || { RID=""; MSG="checks.json of $bad cannot be read"; return 2; }
  (( n_valid <= 1 )) || { RID=""; MSG="the VM holds $n_valid valid runs of $cfg: the owner decides"; return 2; }
  (( ${#MINE} <= ${#atts} )) || { RID=""; MSG="the VM holds ${#MINE} run folders of $cfg and only ${#atts} attempts are recorded in $ST"; return 2; }
  for id in $R/runs/*_${cfg}(N/:t); do
    [[ ${MINE[(Ie)$id]} -gt 0 ]] || { RID=""; MSG="the Mac holds $id, which the VM does not list: nothing of $cfg is launched or used; the owner decides"; return 2; }
    [[ ! -f $ST/setaside_$id.txt && ! -f $ST/held_$id.txt ]] || { RID=""; MSG="$id is in the Mac's runs/ although it is set aside or held: the owner decides"; return 2; }
  done
  settles=($ST/settle_*_${cfg}.txt(N))
  if (( n_valid == 1 )); then
    (( ${#settles} == 0 )) || { RID=""; MSG="$cfg has a valid run and a settle record: the owner decides"; return 2; }
    [[ $commit == $PIN ]] || { MSG="the valid run $RID of $cfg was made at commit '$commit', not at the pin: the owner decides"; RID=""; return 2; }
    if [[ $cfg == *_l1pl350ol_* ]]; then
      att_of $RID
      if ! [[ $ANOF == <-> ]] || (( ANOF < NOFILE_MIN )); then
        rec_by $ST/nofile_ok_$RID.txt owner delegate || { MSG="the launch log of $RID did not show an open-file limit of at least $NOFILE_MIN (attempt record: '${ANOF:-none}'): REG-20 says stop and ask; the run is used only with a record state/nofile_ok_$RID.txt ('under …', 'by …'), logged in an [OPS] entry (RB15)"; RID=""; return 2; }
      fi
    fi
    return 0
  fi
  # The attempts this config may take, and those it has spent.
  extra=0
  for f in $ST/attempt_ok_${cfg}_<->.txt(N); do
    n=${${f:t:r}##*_}
    (( n == MAX_ATTEMPTS + extra + 1 )) || { MSG="${f:t} is not numbered $((MAX_ATTEMPTS + extra + 1)): the attempt_ok records of $cfg must follow attempt $MAX_ATTEMPTS one by one"; return 2; }
    okrec=""
    rec_by $f owner && okrec=1
    [[ -z $okrec && $cfg == ${C}* && $(ruling 9) == a && $n == $((MAX_ATTEMPTS + 1)) ]] && rec_by $f delegate && okrec=1
    [[ -n $okrec ]] || { MSG="${f:t} is not written as the rulings allow (an owner's record; a delegate's only for a control's third attempt under ruling 9(a))"; return 2; }
    extra=$((extra + 1))
  done
  nmax=$((MAX_ATTEMPTS + extra))
  counted=$((${#atts} - ${#lostp}))
  setup_case=""; [[ $cfg == ${B}* ]] && (( counted >= nmax && ${#inval} >= 2 && ${#setup} > 0 )) && setup_case=1
  # A slot settled by a settle record (RB3): not_run, lost_open (RA3's case only), control_not_run, drift_not_run.
  if (( ${#settles} )); then
    (( ${#settles} == 1 )) || { MSG="$cfg has ${#settles} settle records: the owner decides"; return 2; }
    sf=$settles[1]; SRID=${${sf:t:r}#settle_}; slab=$(rv $sf label)
    [[ ${MINE[(Ie)$SRID]} -gt 0 ]] || { MSG="${sf:t} names a run the VM does not list"; SRID=""; return 2; }
    case $cfg in
      ${B}*)
        case $slab in
          not_run)
            { rec_by $sf owner || { [[ -n $setup_case && $(ruling 7) == not_run ]] && rec_by $sf delegate; }; } || { MSG="${sf:t}: label not_run needs an owner's record, or a delegate's in RA3's case under ruling 7 not_run"; return 2; }
            # k1 reads lost_open from two invalid folders of the config in runs/, so at most one may ever be there.
            cinval=(); for id in $inval; do [[ -f $ST/copied_$id.txt ]] && cinval+=($id); done
            (( ${#cinval} == 0 )) || [[ ${#cinval} == 1 && $cinval[1] == $SRID ]] || { MSG="${sf:t}: label not_run, but $cinval[1] is already in runs/ and the record names $SRID: k1 would read lost_open; the owner decides"; return 2; }
            SETTLED=not_run;;
          lost_open)
            (( ${#inval} >= 2 )) || { MSG="${sf:t}: label lost_open needs two invalid runs of $cfg (k1 reads it from them)"; return 2; }
            { rec_by $sf owner || { [[ -n $setup_case && $(ruling 7) == lost_open ]] && rec_by $sf delegate; }; } || { MSG="${sf:t}: label lost_open needs an owner's record, or a delegate's in RA3's case under ruling 7 lost_open"; return 2; }
            LOST="${inval[*]}";;
          *) MSG="${sf:t}: label '$slab' is not not_run or lost_open"; return 2;;
        esac;;
      ${C}*)
        [[ $slab == control_not_run ]] || { MSG="${sf:t}: a control's label is control_not_run"; return 2; }
        { rec_by $sf owner || { [[ $(ruling 9) == b ]] && (( counted >= nmax )) && rec_by $sf delegate; }; } || { MSG="${sf:t}: control_not_run needs an owner's record, or a delegate's after the spent attempts under ruling 9(b)"; return 2; }
        SETTLED=control_not_run;;
      $DRIFT)
        [[ $slab == drift_not_run ]] && rec_by $sf owner || { MSG="${sf:t}: the drift run is settled only by an owner's record with label drift_not_run"; return 2; }
        SETTLED=drift_not_run;;
    esac
    return 0
  fi
  [[ -z $norerun ]] || { MSG="REG-20 says stop and ask after $norerun: a rerun needs a record state/rerun_ok_<that run id>.txt with 'lifts <the failure>', 'under …' and 'by owner' (ruling 6(b): 'by delegate' for a client error when the launch log read nofile >= $NOFILE_MIN and the VM did not reboot); no rerun needs a settle record (label not_run)"; return 2; }
  [[ -z $lost ]] || return 2
  (( n_heat < 2 )) || { MSG="second heat failure (gpu_steady) among REG-20's runs: the queue stops; the owner decides (a record state/rerun_ok_<run id>.txt with 'lifts gpu_steady' and 'by owner' for the second one lets it go on)"; return 2; }
  (( ${#lostp} <= MAX_POWER_LOSSES )) || { MSG="$cfg has ${#lostp} losses after a power-off that are not counted, more than $MAX_POWER_LOSSES (ruling 8(b)): the owner decides"; return 2; }
  if (( counted >= nmax )); then
    if [[ $cfg == ${B}* ]] && (( ${#inval} >= MAX_ATTEMPTS )); then
      [[ -z $setup_case ]] || { MSG="both attempts of $cfg are invalid and ${setup[1]} failed only checks of the setup class (${SETUP_CLASS[*]}; RA3): not lost_open without a settle record (label lost_open or not_run) under ruling 7 ($(ruling 7))"; return 2; }
      LOST="${inval[*]}"; return 0
    fi
    if [[ $cfg == ${C}* ]]; then
      MSG="the $nmax attempts of $cfg are spent (${#inval} left an invalid checks.json): under ruling 9 ($(ruling 9)) the next step is a record state/attempt_ok_${cfg}_$((nmax + 1)).txt (9(a), once) or state/settle_<run id>.txt with label control_not_run (9(b)); after a third attempt, arm A stops and the owner decides"
    else
      MSG="the $nmax attempts of $cfg are spent (${#inval} left an invalid checks.json, ${#setas} set aside): operational stop, the owner decides"
    fi
    return 2
  fi
  LAUNCH=$((${#atts} + 1))
  [[ ! -e $ST/attempt_${cfg}_$LAUNCH.txt ]] || { MSG="attempt records of $cfg are not numbered 1..${#atts}"; LAUNCH=""; return 2; }
  return 0
}

# Sets ACT=copy (or ACT=hold) and ARG when a finished run of config $1 (valid or invalid: k1 counts invalid open runs
# towards `lost_open`) is not yet copied, held or set aside; `hold` when its slot is settled not_run and it is not the
# run the settle record names (it stays in the holding folder: k1 must not see a second invalid run). Returns 1 when
# none is pending. Uses SETTLED and SRID from decide.
copy_pending() {
  local line id
  local -a parts
  for line in $VMS; do
    parts=(${=line}); id=$parts[1]
    [[ $id == *_$1 && ( $parts[2] == valid || $parts[2] == invalid ) ]] || continue
    [[ -f $ST/copied_$id.txt || -f $ST/held_$id.txt || -f $ST/setaside_$id.txt ]] && continue
    ARG=$id
    if [[ $SETTLED == not_run && $id != $SRID ]]; then ACT=hold; else ACT=copy; fi
    return 0
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

# GAP: seconds from burst run $1's end (as launch.sh saw checks.json appear) to control run $2's launch; BT: whether the
# VM's boot id was the same at both launches (same|changed). "-" when a record lacks the time (RA-O1).
gap_of() {
  local e t be ce a b
  GAP="-"; BT="-"
  att_of $1 || return 0; e=$AEND; be=$ABOOT
  att_of $2 || return 0; t=$ATIME; ce=$ABOOT
  [[ -n $be && -n $ce ]] && { [[ $be == $ce ]] && BT=same || BT=changed; }
  [[ $e == *" done" ]] || return 0
  a=$(epoch ${e%% *}); b=$(epoch $t)
  [[ $a == <-> && $b == <-> ]] && GAP=$((b - a))
  return 0
}

# The next thing to do, from the plan, the state records and the VM (read once). ACT is one of:
#   copy <run id>     a finished run to copy to the holding folder, verify, recheck, and move into the Mac's runs/;
#   hold <run id>     a finished run to copy to the holding folder, verify and keep there (its slot is settled not_run);
#   due <run id>      control_due.py to run, once, on a valid open burst run already copied, rechecked and verified;
#   launch <config>   with NEXT_ATT, the attempt number;
#   done              every slot of the plan settled; SUMMARY holds one line per slot, then the copied, held and lost
#                     runs and the runs the recheck changed.
# Returns 2 with MSG when the registration, the rulings or a record stops the queue. Writes nothing.
next_step() {
  local cfg sd rid f id el c line ea eb
  local -a parts
  ACT=""; ARG=""; NEXT_ATT=""; MSG=""; SUMMARY=()
  vm_state || { MSG="the VM's run folders could not be read"; return 2; }
  for cfg in $PLAN; do
    decide $cfg || return 2
    copy_pending $cfg && return 0
    [[ -n $LAUNCH ]] && { ACT=launch; ARG=$cfg; NEXT_ATT=$LAUNCH; return 0; }
    if [[ $cfg == $DRIFT ]]; then
      if [[ $SETTLED == drift_not_run ]]; then SUMMARY+=("drift not_run ${(j:,:)MINE}"); else SUMMARY+=("drift $RID"); fi
      continue
    fi
    sd=${cfg##*_s}
    if [[ -n $LOST ]]; then
      no_control $sd lost_open || return 2
      SUMMARY+=("s$sd lost_open $LOST"); continue
    fi
    if [[ $SETTLED == not_run ]]; then
      no_control $sd not_run || return 2
      SUMMARY+=("s$sd not_run $SRID"); continue
    fi
    rid=$RID
    due_of $rid || return 2
    [[ -n $DUE ]] || { ACT=due; ARG=$rid; return 0; }
    if [[ $DUE == yes ]]; then
      decide ${C}$sd || return 2
      copy_pending ${C}$sd && return 0
      [[ -n $LAUNCH ]] && { ACT=launch; ARG=${C}$sd; NEXT_ATT=$LAUNCH; return 0; }
      if [[ $SETTLED == control_not_run ]]; then
        SUMMARY+=("s$sd $rid CONTROL_DUE yes control_not_run $SRID")
      else
        gap_of $rid $RID
        SUMMARY+=("s$sd $rid CONTROL_DUE yes control $RID gap_s $GAP boot $BT")
      fi
    else
      no_control $sd "CONTROL_DUE $DUE" || return 2
      SUMMARY+=("s$sd $rid CONTROL_DUE $DUE")
    fi
  done
  for f in $ST/copied_*.txt(N); do SUMMARY+=("copied ${${f:t:r}#copied_}"); done
  for f in $ST/held_*.txt(N); do SUMMARY+=("held ${${f:t:r}#held_} settled"); done
  for f in $ST/setaside_*.txt(N); do SUMMARY+=("held ${${f:t:r}#setaside_} set_aside"); done
  for line in $VMS; do
    parts=(${=line}); id=$parts[1]
    [[ $parts[2] == nochecks ]] || continue
    att_of $id; el="-"
    if [[ -n $ATIME && -n $AEND ]]; then ea=$(epoch $ATIME); eb=$(epoch ${AEND%% *}); [[ $ea == <-> && $eb == <-> ]] && el=$((eb - ea)); fi
    c=$(rv $ST/lost_ok_$id.txt count)
    SUMMARY+=("lost $id arm ${AARM:--} elapsed_s $el end ${${AEND##* }:--} counted ${c:--}")
  done
  for f in $ST/recheck_*.json(N); do
    [[ ${f:t} == recheck_err_* ]] && continue
    id=${${f:t:r}#recheck_}
    [[ $(python3 -c 'import json, sys; print(json.load(open(sys.argv[1])).get("changed"))' $f 2> /dev/null) == True ]] || continue
    if [[ -f $ST/setaside_$id.txt ]]; then SUMMARY+=("recheck_changed $id set_aside")
    elif [[ -f $ST/held_$id.txt ]]; then SUMMARY+=("recheck_changed $id held")
    else SUMMARY+=("recheck_changed $id kept"); fi
  done
  ACT=done
  return 0
}

# The checks in force (A14) on one run folder in the holding folder, by recheck_one.py, read-only, from main, with
# ops_r3's two guards (FILE(docs/probe/20261113_reg19/ops_r3/common.sh:206-207)): harness/checks.py and
# analysis/recheck.py equal the commits named here, and analysis/, harness/ and configs/defaults.yaml equal HEAD in the
# working tree. Only validity is kept (recheck_one.py prints nothing else, and the filter below keeps only these
# fields). Writes state/recheck_<run id>.json. Returns 2 with MSG when it cannot be run.
RECHECK_FILTER='import json, sys
d = json.load(sys.stdin)
keep = ("run", "stored_valid", "now_valid", "stored_failed", "now_failed", "changed", "error")
out = {k: d[k] for k in keep if k in d}
out["mac_head"] = sys.argv[1]
print(json.dumps(out, indent=1))'
recheck_guards() {
  cd $R || { MSG="no repo at $R"; return 2; }
  git diff --quiet $CHECKS_COMMIT -- harness/checks.py && git diff --quiet $RECHECK_COMMIT -- analysis/recheck.py || { MSG="harness/checks.py or analysis/recheck.py differ in the working tree from the commits named for the recheck"; return 2; }
  git diff --quiet HEAD -- analysis harness configs/defaults.yaml || { MSG="analysis/, harness/ or configs/defaults.yaml differ in the working tree from the Mac's HEAD"; return 2; }
  return 0
}
recheck_one() {
  local rid=$1 ts errf raw
  recheck_guards || return 2
  stamp; ts=$REPLY; errf=$ST/recheck_err_${rid}_$ts.txt
  raw=$(cd $R && $PY $S/recheck_one.py $STAGE/$rid 2> $errf) || { MSG="recheck_one.py failed on $rid (see ${errf:t}); nothing of it is copied into runs/"; return 2; }
  print -r -- "$raw" | python3 -c "$RECHECK_FILTER" "$(git -C $R rev-parse HEAD)" > $ST/recheck_$rid.tmp && mv $ST/recheck_$rid.tmp $ST/recheck_$rid.json || { MSG="the recheck of $rid cannot be read or recorded"; return 2; }
  return 0
}

# Ruling 2a applied to run $1's recheck record: prints one RECHECK line. Returns 0 (go on: unchanged, or kept as its
# checks.json says), 3 after writing state/setaside_$1.txt (a stored-valid run that today's checks fail, under ruling
# 2a setaside, or the owner's recheck_ok record with 'answer setaside'), or 2 with MSG (a stop).
recheck_apply() {
  local rid=$1 rk=$ST/recheck_$1.json r2a ans
  local -a v
  v=(${(f)"$(python3 -c 'import json, sys
d = json.load(open(sys.argv[1]))
print("error" if d.get("error") else ("changed" if d.get("changed") else "same"))
print(d.get("stored_valid")); print(d.get("now_valid"))
print(",".join(d.get("stored_failed") or []) or "-"); print(",".join(d.get("now_failed") or []) or "-")' $rk 2> /dev/null)"})
  (( ${#v} == 5 )) || { MSG="the recheck record of $rid cannot be read"; return 2; }
  case $v[1] in
    same) echo "RECHECK $rid unchanged"; return 0;;
    error) MSG="today's checks could not be applied to $rid (${rk:t}): the owner decides"; return 2;;
  esac
  r2a=$(ruling 2a)
  if [[ $r2a == stop ]]; then
    ans=$(rv $ST/recheck_ok_$rid.txt answer)
    rec_by $ST/recheck_ok_$rid.txt owner && [[ $ans == (keep|setaside) ]] || { echo "RECHECK $rid changed: stored valid=$v[2] failed=$v[4]; now valid=$v[3] failed=$v[5]"; MSG="today's checks change $rid and ruling 2a is 'stop': the owner decides with a record state/recheck_ok_$rid.txt ('answer keep|setaside', 'under …', 'by owner')"; return 2; }
  else
    ans=$r2a
  fi
  if [[ $ans == setaside && $v[2] == True && $v[3] == False ]]; then
    print -r -l -- "rid $rid" "stored_valid True" "now_failed $v[5]" "under ruling 2a ($r2a), owner_rulings.txt" "by queue" "time $(now)" > $ST/setaside_$rid.tmp && mv $ST/setaside_$rid.tmp $ST/setaside_$rid.txt || { MSG="the set-aside record of $rid could not be written"; return 2; }
    echo "SET ASIDE $rid: stored valid, now invalid (failed=$v[5]); it stays in the holding folder and its config is rerun if an attempt remains (ruling 2a $r2a)"
    return 3
  fi
  echo "RECHECK $rid changed: stored valid=$v[2] failed=$v[4]; now valid=$v[3] failed=$v[5]; kept as its checks.json says (ruling 2a $r2a)"
  return 0
}

# Copy one finished run from the VM into the holding folder, compare every file's sha256 with the VM's (as ops_r3's
# queue), apply today's checks there (recheck_one, ruling 2a), and only then move it into the Mac's runs/, compare
# again, update the manifest and write state/copied_<run id>.txt. With $2 = hold the run stays in the holding folder
# under state/held_<run id>.txt. Returns 0, 3 after a set-aside, or 2 with MSG on any failure.
copy_verify() {
  local rid=$1 how=$2 la lb a b rc
  cd $R || { MSG="no repo"; return 2; }
  la=$(ssh $K $H "cd ~/aftershock-artifacts/runs/$rid && find . -type f | LC_ALL=C sort | xargs sha256sum") || { MSG="the VM's checksums of $rid could not be read"; return 2; }
  [[ -n $la ]] || { MSG="empty checksum list for $rid"; return 2; }
  a=$(print -r -- "$la" | shasum -a 256 | cut -c1-16)
  if [[ -e $R/runs/$rid ]]; then
    [[ -z $how && -f $ST/recheck_$rid.json && ! -f $ST/setaside_$rid.txt ]] || { MSG="$rid is in runs/ without a recheck record, or is held or set aside: the owner decides"; return 2; }
  else
    mkdir -p $STAGE || { MSG="the holding folder $STAGE cannot be made"; return 2; }
    rsync -a -e "ssh ${K[*]}" "${H}:aftershock-artifacts/runs/$rid" $STAGE/ || { MSG="copy failed $rid"; return 2; }
    lb=$(cd $STAGE/$rid && find . -type f | LC_ALL=C sort | xargs shasum -a 256) || { MSG="the holding folder's checksums of $rid could not be computed"; return 2; }
    b=$(print -r -- "$lb" | shasum -a 256 | cut -c1-16)
    [[ -n $lb && $a == $b ]] || { MSG="checksum mismatch $rid (vm [$a] holding folder [$b])"; return 2; }
    if [[ ! -f $ST/recheck_$rid.json ]]; then recheck_one $rid || return 2; fi
    recheck_apply $rid; rc=$?
    (( rc == 0 )) || return $rc
    if [[ $how == hold ]]; then
      print -r -l -- "rid $rid" "files ${#${(f)la}}" "sha_of_sums $a" "where $STAGE/$rid" "why its slot is settled not_run (settle record) and k1 must not read it before REG-20's [RESULT]" "time $(now)" > $ST/held_$rid.tmp && mv $ST/held_$rid.tmp $ST/held_$rid.txt || { MSG="the hold record of $rid could not be written"; return 2; }
      echo "HELD $rid ${#${(f)la}} files sha-of-sums $a (not in runs/)"
      return 0
    fi
    [[ ! -e $R/runs/$rid ]] && mv $STAGE/$rid $R/runs/$rid || { MSG="$rid could not be moved from the holding folder into runs/"; return 2; }
  fi
  lb=$(cd runs/$rid && find . -type f | LC_ALL=C sort | xargs shasum -a 256) || { MSG="the Mac's checksums of $rid could not be computed"; return 2; }
  b=$(print -r -- "$lb" | shasum -a 256 | cut -c1-16)
  [[ -n $lb && $a == $b ]] || { MSG="checksum mismatch $rid (vm [$a] mac [$b])"; return 2; }
  python3 tools/manifest.py update > /dev/null || { MSG="manifest update failed after copying $rid"; return 2; }
  print -r -l -- "rid $rid" "files ${#${(f)la}}" "sha_of_sums $a" "time $(now)" > $ST/copied_$rid.tmp && mv $ST/copied_$rid.tmp $ST/copied_$rid.txt || { MSG="the copy record of $rid could not be written"; return 2; }
  echo "COPIED $rid ${#${(f)la}} files sha-of-sums $a"
  return 0
}
