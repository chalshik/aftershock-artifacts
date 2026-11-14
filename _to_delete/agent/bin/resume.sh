#!/bin/zsh
# Self-resume (docs/FABLE_PROMPT.md §5). launchd runs it every 20 minutes and at login; gpu_watch.sh calls it when the
# GPU becomes available. It starts ONE headless agent session (claude -p, permission mode auto) with
# agent/RESUME_PROMPT.md, and only if:
#   - agent/STOP does not exist (the owner's kill switch: `touch agent/STOP`),
#   - agent/REPORT.md does not start with "FINAL" (the study is not finished),
#   - no process named `claude` has its working directory inside this repo (an interactive or headless session is alive),
#   - no other resume.sh holds the lock.
# Test of the launch path only (starts no agent work): RESUME_TEST=1 zsh agent/bin/resume.sh
# Test of the decision only (starts nothing, logs what it would do): RESUME_DRY=1 zsh agent/bin/resume.sh
export PATH=$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
R=/Users/chalshik/Projects/aftershock-artifacts; A=$R/agent; RUN=$A/run; mkdir -p $RUN
CL=${CLAUDE_BIN:-$HOME/.local/bin/claude}
now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
cd $R || exit 1
if [[ -n $RESUME_TEST ]]; then
  $CL -p "Reply with exactly one line: RESUME_TEST_OK followed by the output of the shell command pwd. Do nothing else." --permission-mode auto > $RUN/resume-test.out 2>&1
  echo "$now test rc=$? reason=${1:-test}" >> $RUN/resume.log
  exit 0
fi
[[ -f $A/STOP ]] && exit 0
head -1 $A/REPORT.md 2>/dev/null | grep -q '^FINAL' && exit 0
for p in $(pgrep -a -x claude); do
  cwd=$(lsof -a -p $p -d cwd -Fn 2>/dev/null | sed -n 's/^n//p')
  if [[ $cwd == $R* ]]; then [[ -n $RESUME_DRY ]] && echo "$now dry: alive pid $p cwd $cwd, would not start" >> $RUN/resume.log; exit 0; fi
done
if [[ -n $RESUME_DRY ]]; then echo "$now dry: no live session, would start" >> $RUN/resume.log; exit 0; fi
mkdir $RUN/resume.lock 2>/dev/null || {
  lp=$(cat $RUN/resume.lock/pid 2>/dev/null)
  if [[ -n $lp ]] && kill -0 $lp 2>/dev/null; then exit 0; fi
  echo "$now stale lock (pid $lp) taken over" >> $RUN/resume.log
}
echo $$ > $RUN/resume.lock/pid
trap 'mv -f $RUN/resume.lock/pid $RUN/resume.lock.lastpid 2>/dev/null; rmdir $RUN/resume.lock 2>/dev/null' EXIT
echo "$now start reason=${1:-timer}" >> $RUN/resume.log
$CL -p "$(cat $A/RESUME_PROMPT.md)" --permission-mode auto > $RUN/resume-$now.out 2>&1
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) end rc=$? (started $now)" >> $RUN/resume.log
