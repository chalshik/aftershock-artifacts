# Shared, fixed settings and functions of the REG-19 resume scripts, third version (after the round-2 rule F review,
# docs/drafts/reviews-2026-11-13/rulef-reg19-resume-r2.md), revised after round 3 (rulef-reg19-resume-r3.md and
# proxy-reg19-resume-r3.md). Read from the environment: VM_HOST and WAIT_MIN only
# (session_probe.sh also reads SET and RENEW). No seed, attempt number or run id is typed by anyone: the queue derives
# them from the attempt records in state/ and from what the VM's run folders say.
R=/Users/chalshik/Projects/aftershock-artifacts
S=$R/docs/probe/20261113_reg19/ops_r3
ST=$S/state
PROBE_DIR=$R/docs/probe/20261113_reg19
W=/Users/chalshik/Projects/aftershock-reg19-pin
PIN=a7bb77abc863adcaad9d4516815a5ddddf2908e9
PY=$R/.venv/bin/python
H=chalshik@${VM_HOST:-100.83.53.50}
K=(-i $HOME/.ssh/id_ed25519_vllm -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=4)
MIN_FREE_KB=2097152                      # 2 GB free on the VM before a launch (about 240 MB per run)
MAX_ATTEMPTS=3                           # REG-19: a run once, rerun unchanged at most twice
SEEDS=(18 19)                            # the seeds left, in the registered order; not settable
ALLCFG=(); for sd in 15 16 17 18 19; do ALLCFG+=(stage2_control_l1pl350cl_r2.0_w3000_s$sd burst_l1pl350cl_r2.0_w3000_s$sd); done
LEFT=(${ALLCFG[7,10]})                   # the four configs of seeds 18 and 19: nothing else is ever launched
DECISION_PAT='^## [0-9]{4}-[0-9]{2}-[0-9]{2} · \[DECISION\] \((delegate|owner)\) REG-19 resumes for seeds 18 and 19'   # (owner) added 2026-11-13: the owner approved the resume directly
# Hours (UTC, HHMM) in which no run is started because it would run into a time of day at which the VM has been
# powered off from outside: of the seven recorded ends of a boot, five fell between 14:35 and 17:37 UTC and two between
# 02:53 and 04:40 UTC (BELIEF as to a pattern; docs/drafts/reg19_attempt3_decision_draft2.md, item 3). No run may overlap
# 02:30-05:00 or 14:15-18:00 UTC; a control is not started unless its burst run can also end before the window
# (2.45 h for a pair, 1.2 h for a run, DERIVED in that draft). Changed with the owner's attempt-3 decision.
QUIET_CONTROL_FROM=1145; QUIET_BURST_FROM=1300; QUIET_TO=1800
QUIET2_CONTROL_FROM=0000; QUIET2_BURST_FROM=0115; QUIET2_TO=0500
DRIVER=595.99.02                         # the pinned driver (PROTOCOL.md, section 4, Software)
RECHECK_PAT='*_l1pl350cl_r2.0_w3000_s1[5-9]'   # REG-19's runs, both kinds, for analysis.recheck
CHECKS_COMMIT=5ee6e38d3a15994da8bb6597b9b13ea8be08807c    # harness/checks.py as of this commit (the checks in force, A14)
RECHECK_COMMIT=72fafb5991e036eddf1c4ce40b39bc1ca81fa74e   # analysis/recheck.py as of this commit
SCRIPTS=(common.sh vm_state.py session_probe.sh launch.sh queue.sh final.sh)
RECORDS=(state/attempt_stage2_control_l1pl350cl_r2.0_w3000_s18_1.txt state/lost_ok_20261112-151030_stage2_control_l1pl350cl_r2.0_w3000_s18.txt)
CONTROL_PAT='*_stage2_control_l1pl350cl_r2.0_w3000_s1[5-9]'
BURST_PAT='*_burst_l1pl350cl_r2.0_w3000_s1[5-9]'
ALLOWED="Allowed reads while diagnosing a stop: 'tmux has-session -t run'; the folder names under runs/; a run's checks.json (valid, failed); in a launch log only the lines holding 'run_id' or '[run] checks'. Nothing else of a log or a run folder (REG-19: no interim look)."

# File-name stamp, left in REPLY: UTC time, the process id and a count of the stamps this process has taken, so that
# neither two starts in one second nor two files of one process in one second share a name. Call it as `stamp`,
# never as $(stamp): a subshell would lose the count.
STAMP_N=0
stamp() { STAMP_N=$((STAMP_N + 1)); REPLY="$(date -u +%Y%m%dT%H%M%SZ)_$$_$STAMP_N"; }

# Mac-side checks before every launch, step and table: worktree at the pin and clean; the pin an ancestor of HEAD; the
# files used from the Mac's working tree (manifest tool, lock files) equal to the pin's; these scripts tracked, equal to
# their committed text, and that commit the one recorded in scripts_commit.txt; the two state records committed with
# them (the lost run's attempt and the decision's allowance) tracked and unchanged. Sets SC.
mac_checks() {
  local st p paths recs
  cd $R || { echo "STOP: no repo at $R"; return 2; }
  [[ $(git -C $W rev-parse HEAD 2>/dev/null) == $PIN ]] || { echo "STOP: worktree $W is not at $PIN"; return 2; }
  st=$(git -C $W status --short) || { echo "STOP: git status failed in $W"; return 2; }
  [[ -z $st ]] || { echo "STOP: worktree $W is dirty"; return 2; }
  git merge-base --is-ancestor $PIN HEAD || { echo "STOP: the pin is not an ancestor of the Mac HEAD"; return 2; }
  git diff --quiet $PIN -- tools/manifest.py pyproject.toml uv.lock || { echo "STOP: tools/manifest.py, pyproject.toml or uv.lock differ from the pin in the working tree"; return 2; }
  paths=(${SCRIPTS[@]/#/docs/probe/20261113_reg19/ops_r3/})
  for p in $paths; do
    git ls-files --error-unmatch $p > /dev/null 2>&1 || { echo "STOP: $p is not tracked by git"; return 2; }
  done
  git diff --quiet HEAD -- $paths || { echo "STOP: a resume script differs from its committed text"; return 2; }
  SC=$(git log -1 --format=%H -- $paths)
  [[ -n $SC ]] || { echo "STOP: the resume scripts are not committed"; return 2; }
  [[ -f $S/scripts_commit.txt ]] || { echo "STOP: no scripts_commit.txt"; return 2; }
  [[ $(<$S/scripts_commit.txt) == $SC ]] || { echo "STOP: the scripts changed since scripts_commit.txt (now $SC)"; return 2; }
  recs=(${RECORDS[@]/#/docs/probe/20261113_reg19/ops_r3/})
  for p in $recs; do
    git ls-files --error-unmatch $p > /dev/null 2>&1 || { echo "STOP: $p is not tracked by git"; return 2; }
  done
  git diff --quiet HEAD -- $recs || { echo "STOP: a committed state record differs from its committed text"; return 2; }
  return 0
}

# The decision that allows this queue is in the committed docs/decisions.md (no launch before it is in the log).
decision_in_log() {
  git -C $R grep -q -E "$DECISION_PAT" HEAD -- docs/decisions.md && return 0
  MSG="the decision that allows this queue is not in the committed docs/decisions.md"; return 2
}

# True when a launch of config $1 now would run into the hours in which the VM has been powered off (see above).
quiet_now() {
  local now=$(date -u +%H%M) from=$QUIET_BURST_FROM from2=$QUIET2_BURST_FROM
  [[ $1 == stage2_control_* ]] && { from=$QUIET_CONTROL_FROM; from2=$QUIET2_CONTROL_FROM; }
  (( (10#$now >= from && 10#$now < QUIET_TO) || (10#$now >= 10#$from2 && 10#$now < 10#$QUIET2_TO) ))
}

# Every REG-19 run folder on the Mac is linked into the worktree, each link resolves to the Mac's folder, and nothing
# else is in the worktree's runs/. A link is made only where nothing exists at its path; nothing is written elsewhere.
links_ok() {
  local ids n_w=0 id lw lr
  [[ -d $W/runs && ! -L $W/runs ]] || { echo "STOP: $W/runs is not a real directory"; return 2; }
  ids=($R/runs/${~CONTROL_PAT}(N/:t) $R/runs/${~BURST_PAT}(N/:t))
  for id in $ids; do
    lw=$W/runs/$id; lr=$R/runs/$id
    if [[ ! -e $lw && ! -L $lw ]]; then ln -s $lr $lw || { echo "STOP: could not link $id"; return 2; }; fi
    [[ -L $lw ]] || { echo "STOP: $lw exists and is not a link"; return 2; }
    [[ ${lw:A} == ${lr:A} ]] || { echo "STOP: $lw does not resolve to $lr"; return 2; }
  done
  for id in $W/runs/*(N:t); do
    n_w=$((n_w + 1))
    [[ ${ids[(Ie)$id]} -gt 0 ]] || { echo "STOP: $W/runs holds $id, which is not a REG-19 run folder on the Mac"; return 2; }
  done
  [[ $n_w == ${#ids} ]] || { echo "STOP: $n_w entries in $W/runs against ${#ids} REG-19 folders"; return 2; }
  return 0
}

# What the VM holds for REG-19's ten configs: one line per run folder,
# "<run id> valid|invalid|nochecks|unreadable <failed|-> <commit|->". Read-only: vm_state.py is sent on stdin.
vm_state() {
  local out
  VMS=()
  out=$(ssh $K $H "python3 - ${ALLCFG[*]}" < $S/vm_state.py) || return 1
  [[ ${out##*$'\n'} == "END ${#ALLCFG}" ]] || return 1
  VMS=("${(@f)out}"); VMS=(${VMS[1,-2]})
  return 0
}

# REG-19's rerun rule for one config, from the attempt records and the VM's checks.json files only. Returns 0 with
# RID set (one valid run exists: use it, launch nothing) or with LAUNCH set (the number of the attempt to launch);
# returns 2 with MSG set when the registration, or this decision, stops the queue.
#   - every launch is one attempt, whatever it left behind; at most MAX_ATTEMPTS attempts of a config;
#   - more run folders of the config on the VM than attempt records stop the queue (a launch outside these scripts);
#   - a run folder of the config on the Mac that the VM does not list stops the queue (a valid run already copied
#     must not be made a second time);
#   - a valid run is used only if it was made at the pin (env.json's git_commit);
#   - no rerun after a `no_errors` failure that holds a `client_error`, after `manipulation` (the burst did not fill
#     the pool) or after `power_limit` (a limit other than 350 W); one rerun after `gpu_steady` (heat), and a second
#     `gpu_steady` failure among ALL of REG-19's runs stops the queue;
#   - a run folder without checks.json (a lost run) is not rerun unless a decision allows it, recorded as
#     state/lost_ok_<run id>.txt. The record for seed 18's control of 2026-11-12 is committed with these scripts.
decide() {
  local cfg=$1 line parts f id n_valid=0 n_heat=0 norerun="" bad="" lost="" commit="" atts mine
  RID=""; LAUNCH=""; MSG=""; mine=()
  vm_state || { MSG="the VM's run folders could not be read"; return 2; }
  for line in $VMS; do
    parts=(${=line})
    for f in ${(s:,:)parts[3]}; do [[ $f == gpu_steady ]] && n_heat=$((n_heat + 1)); done   # over every REG-19 run
    [[ $parts[1] == *_$cfg ]] || continue
    mine+=($parts[1])
    case $parts[2] in
      valid) n_valid=$((n_valid + 1)); RID=$parts[1]; commit=$parts[4];;
      invalid)
        for f in ${(s:,:)parts[3]}; do
          case $f in
            no_errors/client_error|manipulation|power_limit) norerun="$f ($parts[1])";;
          esac
        done;;
      nochecks) [[ -f $ST/lost_ok_$parts[1].txt ]] || lost=$parts[1];;
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
  [[ -z $norerun ]] || { MSG="REG-19 registers no rerun after $norerun: the owner decides"; return 2; }
  [[ -z $lost ]] || { MSG="$lost has no checks.json (lost or still running): a rerun needs its own decision, recorded as $ST/lost_ok_$lost.txt"; return 2; }
  (( n_heat < 2 )) || { MSG="second heat failure (gpu_steady) among REG-19's runs: REG-19 stops the queue; the owner decides"; return 2; }
  (( ${#atts} < MAX_ATTEMPTS )) || { MSG="the $MAX_ATTEMPTS attempts of $cfg are spent: operational stop, no table, the owner decides"; return 2; }
  LAUNCH=$((${#atts} + 1))
  [[ ! -e $ST/attempt_${cfg}_$LAUNCH.txt ]] || { MSG="attempt records of $cfg are not numbered 1..${#atts}"; LAUNCH=""; return 2; }
  return 0
}

# Is it this config's turn? Only the four configs of seeds 18 and 19; nothing of a seed that has a step record;
# seed 19 only after seed 18's record says 'continue': True; a burst run only after a valid control of its seed.
# launch.sh calls this before anything else, so a launch by hand cannot pass the futility stop or the order.
gate() {
  local cfg=$1 sd r18=$ST/reg19_step_s18.txt
  MSG=""
  [[ ${LEFT[(Ie)$cfg]} -gt 0 ]] || { MSG="'$cfg' is not one of the four configs left (seeds 18 and 19)"; return 2; }
  sd=${cfg##*_s}
  [[ ! -e $ST/reg19_step_s$sd.txt ]] || { MSG="seed $sd has a step record: none of its runs is launched again"; return 2; }
  if [[ $sd == 19 ]]; then
    [[ -f $r18 ]] || { MSG="seed 19 is launched only after seed 18's step record says 'continue': True"; return 2; }
    [[ $(sed -n 1p $r18) == "'done': [15, 16, 17, 18]" && $(sed -n 2p $r18) == "'continue': True" ]] || { MSG="seed 19 is launched only after seed 18's step record says 'continue': True"; return 2; }
  fi
  if [[ $cfg == burst_* ]]; then
    decide stage2_control_l1pl350cl_r2.0_w3000_s$sd || return 2
    [[ -n $RID ]] || { RID=""; LAUNCH=""; MSG="the burst run of seed $sd is launched only after a valid control of that seed"; return 2; }
    RID=""; LAUNCH=""
  fi
  return 0
}

# The checks in force (A14), applied read-only by analysis.recheck to REG-19's runs on the Mac, from main. $1 is the
# number of runs there must be. Only validity is kept: of the recheck's output, n_runs, n_changed and, for a changed
# run, its stored and recomputed `valid` and `failed`; the details of the checks are dropped before anything is
# written (they could hint at an outcome). Sets RK (the record) and RECHECK_COUNTS. Returns 0 when the count is $1 and
# nothing changed; 3 when not (an operational stop: the owner decides); 1 or 2 when the recheck could not be run.
RECHECK_FILTER='import json, sys
d = json.load(sys.stdin)
keep = ("run", "stored_valid", "now_valid", "stored_failed", "now_failed", "error")
print(json.dumps({"mac_head": sys.argv[1], "n_runs": d["n_runs"], "n_changed": d["n_changed"],
                  "changed": [{k: r[k] for k in keep if k in r} for r in d["changed"]]}, indent=1))'
recheck_ok() {
  local want=$1 ts raw
  MSG=""; RK=""; RECHECK_COUNTS=""
  cd $R || { MSG="no repo at $R"; return 2; }
  git diff --quiet $CHECKS_COMMIT -- harness/checks.py && git diff --quiet $RECHECK_COMMIT -- analysis/recheck.py || { MSG="harness/checks.py or analysis/recheck.py differ in the working tree from the commits named for the recheck"; return 2; }
  git diff --quiet HEAD -- analysis harness configs/defaults.yaml || { MSG="analysis/, harness/ or configs/defaults.yaml differ in the working tree from the Mac's HEAD"; return 2; }
  stamp; ts=$REPLY; RK=$ST/reg19_recheck_$ts.json; RKERR=$ST/reg19_recheck_err_$ts.txt
  [[ ! -e $RK ]] || { MSG="$RK exists"; return 2; }
  raw=$(AFTERSHOCK_UNSEAL=REG-19 $PY -m analysis.recheck "$RECHECK_PAT" 2> $RKERR) || { MSG="analysis.recheck failed (see $RKERR)"; return 1; }
  print -r -- "$raw" | python3 -c "$RECHECK_FILTER" "$(git rev-parse HEAD)" > $RK || { MSG="the recheck's output cannot be read"; return 1; }
  RECHECK_COUNTS=$(python3 -c 'import json, sys; d = json.load(open(sys.argv[1])); print(d["n_runs"], d["n_changed"])' $RK) || { MSG="the recheck's record cannot be read"; return 1; }
  [[ $RECHECK_COUNTS == "$want 0" ]] && return 0
  MSG="the recheck gives '$RECHECK_COUNTS' (runs, changed) where '$want 0' is required (${RK:t}: validity fields only)"; return 3
}
