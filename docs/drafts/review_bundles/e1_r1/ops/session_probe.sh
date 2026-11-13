#!/bin/zsh
# E1, once per boot of the VM, before the first launch (copied from ops_r3/session_probe.sh; only the commit checked,
# the paths and the wording differ): record the VM's session (boot id, uptime, kernel, driver, governor, limit, tree,
# lock, disk) and the Mac's environment against uv.lock, and require 350.00 W, the pinned driver, and the VM's tree
# clean at the registered commit with that commit's uv.lock. Read-only, except that SET=1 first runs the one allowed
# root command, `sudo -n nvidia-smi -pl 350`, and only when no compute process is on the GPU (only with the owner's
# leave: the registration says the owner sets 350 W unless a sudoers rule exists); the limit before and after is
# written to the probe. Writes state/session_boot_id.txt, which every launch compares with the VM's boot id: a reboot
# between launches stops the queue. A second probe replaces that tripwire, so it is refused unless RENEW=1 (after a
# reboot E1 stops: a renewal needs a decisions.md entry); the replaced file is kept under another name.
source ${0:A:h}/common.sh
die() { echo "STOP: $1"; echo "$ALLOWED"; exit ${2:-2}; }
mac_checks || die "$MSG"
mkdir -p $ST
cur=$ST/session_boot_id.txt
[[ ! -e $cur || -n $RENEW ]] || die "a session probe exists ($cur); RENEW=1 replaces it, and only with a decisions.md entry"
stamp; ts=$REPLY
out=$PROBE_DIR/session_$ts.txt
[[ ! -e $out ]] || die "$out exists"
dry=$(cd $R && uv sync --frozen --dry-run --offline 2>&1) || die "the dry-run sync of the Mac's environment failed"
n_add=$(print -r -- "$dry" | grep -c '^ [+~] '); n_extra=$(print -r -- "$dry" | grep -c '^ - ')
{
  echo "# E1: session probe (agent). scripts commit $SC; Mac HEAD $(git -C $R rev-parse HEAD); registered commit $E1"
  echo "mac_venv missing_or_other_version $n_add extra $n_extra (uv sync --frozen --dry-run --offline)"
  ssh $K $H 'date -Is; echo "boot_id $(cat /proc/sys/kernel/random/boot_id)"; echo "up_since $(uptime -s)"; echo "kernel $(uname -r)";
    echo "driver $(nvidia-smi --query-gpu=driver_version --format=csv,noheader)";
    echo "governor $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo n/a)";
    echo "limit_before $(nvidia-smi --query-gpu=power.limit --format=csv,noheader)";
    echo "apps $(nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l)";
    echo "boots $(journalctl --list-boots 2>/dev/null | tail -3 | tr -s " " | tr "\n" ";")";
    echo "prev_boot_kernel $(journalctl -b -1 -k --no-pager 2>/dev/null | grep -m1 -o "Linux version [^ ]*")";
    echo "prev_boot_nvidia $(journalctl -b -1 -k --no-pager 2>/dev/null | grep -m1 -o "NVIDIA UNIX.*Kernel Module  *[0-9.]*")"'
} > $out || die "the VM could not be read" 3
if [[ -n $SET ]]; then
  if [[ $(grep '^apps ' $out | awk '{print $2}') == 0 ]]; then
    ssh $K $H 'sudo -n nvidia-smi -pl 350 2>&1; echo "sudo_rc $?"' >> $out
  else
    echo "set_skipped a compute process is on the GPU" >> $out
  fi
fi
ssh $K $H 'echo "limit_after $(nvidia-smi --query-gpu=power.limit --format=csv,noheader)"; cd ~/aftershock-artifacts && echo "tree $(git rev-parse HEAD) dirty $(git status --short | wc -l)"; echo "lock_blob $(git hash-object uv.lock)"; echo "free_kb $(df -k --output=avail ~ | tail -1 | tr -d " ")"' >> $out || die "the VM could not be read (second read)" 3
cat $out
[[ $n_add == 0 ]] || die "the Mac's .venv lacks a locked package or holds another version ($n_add)"
[[ $(grep '^limit_after ' $out | awk '{print $2}') == $LIMIT_W ]] || die "power limit is not $LIMIT_W W" 4
[[ $(grep '^tree ' $out | awk '{print $2, $4}') == "$E1 0" ]] || die "the VM's tree is not the registered commit $E1, clean (vm_checkout.sh moves it, with the owner's approval)"
[[ $(grep '^driver ' $out | awk '{print $2}') == $DRIVER ]] || die "the VM's driver is not $DRIVER (PROTOCOL section 4)"
[[ $(grep '^lock_blob ' $out | awk '{print $2}') == $(git -C $R rev-parse ${E1}:uv.lock) ]] || die "the VM's uv.lock is not the registered commit's"
boot=$(grep '^boot_id ' $out | awk '{print $2}')
[[ $boot =~ '^[0-9a-f-]{36}$' ]] || die "no boot id read" 3
if [[ -e $cur ]]; then mv $cur $ST/session_boot_id_replaced_$ts.txt || die "the earlier session file could not be set aside"; fi
print -r -- $boot > $cur
echo "SESSION OK boot_id $boot"
