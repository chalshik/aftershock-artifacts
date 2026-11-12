# launchd jobs (written and tested, NOT installed)

The agent may not install recurring launchd jobs: Claude Code's permission classifier refused it on 2026-11-13.
Without them, the agent keeps going only while its interactive session is alive (see agent/STATE.md, "Self-resume").

To make the agent restart after a crash or a reboot, and to watch the GPU without a session, the owner runs:

    cp agent/launchd/com.aftershock.gpuwatch.plist agent/launchd/com.aftershock.agent-resume.plist ~/Library/LaunchAgents/
    launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.aftershock.gpuwatch.plist
    launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.aftershock.agent-resume.plist

- `com.aftershock.gpuwatch`: `agent/bin/gpu_watch.sh` every 15 min. Read-only on the VM. Writes `agent/GPU_AVAILABLE`.
- `com.aftershock.agent-resume`: `agent/bin/resume.sh` every 20 min and at login. Starts one headless session
  (`claude -p`, permission mode auto) with `agent/RESUME_PROMPT.md`, only if no `claude` process has this repo as its
  working folder, `agent/STOP` does not exist, and `agent/REPORT.md` does not start with `FINAL`.

Stop: `touch agent/STOP`. Remove: `launchctl bootout gui/$(id -u)/com.aftershock.agent-resume` (and `…gpuwatch`).
Limit: launchd agents load at login; the Mac has no auto-login, so after a reboot nothing runs until the owner logs in.

Tested 2026-11-13: `com.aftershock.resume-test.plist` (a one-off job, loaded and unloaded) started `claude -p` from
launchd and got `RESUME_TEST_OK /Users/chalshik/Projects/aftershock-artifacts`, exit 0 (agent/run/resume.log).
`RESUME_DRY=1 zsh agent/bin/resume.sh` logged "alive pid …, would not start" with a session alive and
"no live session, would start" with the process check pointed at a name that does not exist.
