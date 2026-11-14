#!/bin/zsh
# Sandbox test of agent/bin/vm_verify_list.zsh: a fake "VM" runs dir and a fake Mac runs dir, a fake manifest.
set -u
R=${0:A:h:h:h}
T=$(mktemp -d "${TMPDIR:-/tmp}/vvl.XXXX")
mkdir -p $T/vm $T/mac
mk() { mkdir -p $T/vm/$1 $T/mac/$1; print -r -- "$2" > $T/vm/$1/a.txt; print -r -- "$2" > $T/mac/$1/a.txt; }
mk 20260101-000000_ok x1
mk 20260101-000001_okb y1; mkdir -p $T/vm/20260101-000001_okb/sub $T/mac/20260101-000001_okb/sub; echo z > $T/vm/20260101-000001_okb/sub/b.txt; echo z > $T/mac/20260101-000001_okb/sub/b.txt
mk 20260101-000002_vmextra x2; echo extra > $T/vm/20260101-000002_vmextra/extra.txt
mk 20260101-000003_vmhash x3; echo changed > $T/vm/20260101-000003_vmhash/a.txt
mk 20260101-000004_machash x4
mkdir -p $T/vm/20260101-000005_nomanifest; echo q > $T/vm/20260101-000005_nomanifest/a.txt
mk 20260101-000006_sweep_l1pl350cl_pc_off_r1.5 s
mk 20260101-000007_burst_l1pl350cl_r2.0_w3000_s15_drift d
mk 20260101-000008_ol_l1pl350ol_r2.0_w3000_s17 o
mk 20260101-000009_burst_l1pl350cl_r2.0_w3000_s16_cap c
mk 20260101-000010_ok_prefix x10; mk 20260101-000010_ok_prefixlonger x11
mk 20260101-000012_ctl_l1pl350cl_r2.0_w3000_s17 r19
mk 20260101-000011_vmmissing x5; echo m > $T/mac/20260101-000011_vmmissing/m.txt
# manifest from the Mac copy (as tools/manifest.py would), excluding the no-manifest folder
(cd $T/mac && find . -type f | sed 's|^\./||' | LC_ALL=C sort | while read f; do shasum -a 256 "$f"; done) > $T/manifest
# after the manifest: the Mac copy of machash changes (its VM copy still equals the manifest)
echo changed > $T/mac/20260101-000004_machash/a.txt
out=$(VM_RUNS=$T/vm MAC_RUNS=$T/mac MANIFEST=$T/manifest REMOTE_CMD="sh -c" zsh $R/agent/bin/vm_verify_list.zsh)
print -r -- "$out"
pass=0; fail=0
chk() { if print -r -- "$out" | grep -Eq "^$1 $2( |$)"; then (( pass++ )); else echo "FAIL: $1 expected $2"; (( fail++ )); fi; }
chk 20260101-000000_ok VERIFIED
chk 20260101-000001_okb VERIFIED
chk 20260101-000002_vmextra MISMATCH
chk 20260101-000003_vmhash MISMATCH
chk 20260101-000004_machash MISMATCH
chk 20260101-000005_nomanifest NOT_IN_MANIFEST
chk 20260101-000006_sweep_l1pl350cl_pc_off_r1.5 SKIP_SEALED
chk 20260101-000007_burst_l1pl350cl_r2.0_w3000_s15_drift SKIP_SEALED
chk 20260101-000008_ol_l1pl350ol_r2.0_w3000_s17 SKIP_SEALED
chk 20260101-000009_burst_l1pl350cl_r2.0_w3000_s16_cap SKIP_SEALED
chk 20260101-000010_ok_prefix VERIFIED
chk 20260101-000010_ok_prefixlonger VERIFIED
chk 20260101-000011_vmmissing MISMATCH
chk 20260101-000012_ctl_l1pl350cl_r2.0_w3000_s17 VERIFIED
print -r -- "$out" | grep -q "^SUMMARY verified=5 .* other=5 sealed=4$" && (( pass++ )) || { echo "FAIL: summary"; (( fail++ )); }
print -r -- "$out" | grep -q "vm_extra=1 vm_missing=0" && (( pass++ )) || { echo "FAIL: extra count"; (( fail++ )); }
print -r -- "$out" | grep -q "20260101-000003_vmhash MISMATCH .*vm_hash" && (( pass++ )) || { echo "FAIL: vm_hash detail"; (( fail++ )); }
print -r -- "$out" | grep -q "20260101-000004_machash MISMATCH .*mac_hash" && (( pass++ )) || { echo "FAIL: mac_hash detail"; (( fail++ )); }
echo "RESULT pass=$pass fail=$fail"
