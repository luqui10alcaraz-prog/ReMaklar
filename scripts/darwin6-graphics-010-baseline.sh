#!/bin/sh
set -eu
out=/var/tmp/graphics010-baseline
exe=/var/tmp/graphics009-run12/qemu-ppc
old=/var/tmp/graphics009-run10
payload=/var/tmp/graphics009-r8
probe="$payload/run_graphics_008.pl"
test ! -e "$out";mkdir "$out";exec > "$out/session.txt" 2>&1
set -x
md5 "$exe" > "$out/runtime.txt"
for name in signals-runtime statfs-runtime iokit-open-runtime;do
 if [ "$name" = signals-runtime ];then
 perl "$probe" "$out/$name" "$exe" --root /var/tmp/jaguar "$old/$name-ppc" /tmp/signals-009-r10.ppc
 else
 perl "$probe" "$out/$name" "$exe" --root /var/tmp/jaguar "$old/$name-ppc"
 fi
done
perl "$probe" "$out/system" "$exe" --root /var/tmp/jaguar /var/tmp/graphics009-run12/system-ppc
for name in process-runtime access-runtime iokit-runtime;do perl "$probe" "$out/$name" "$exe" --root /var/tmp/jaguar "$old/$name-ppc";done
perl "$probe" "$out/exec-runtime" "$exe" --root /var/tmp/jaguar "$old/exec-runtime-ppc" /tmp/exec-009-r10.ppc
for name in objc cf;do perl "$probe" "$out/$name" "$old/$name-i386";done
perl "$payload/run_utilities.pl" "$exe" "$payload/samples" "$payload/utility-cases.tsv" "$out/utilities" > "$out/utilities.txt" 2>&1
perl "$payload/run_filesystem.pl" "$exe" "$payload/samples" "$payload/filesystem-probe.macho" "$out/filesystem" > "$out/filesystem.txt" 2>&1
for name in windowserver installer splash;do
 case "$name" in
 windowserver) target=/var/tmp/jaguar/System/Library/CoreServices/WindowServer;;
 installer) target=/var/tmp/jaguar/Applications/Utilities/Installer.app/Contents/MacOS/Installer;;
 splash) target=/var/tmp/jaguar/System/Installation/CDIS/splash;;
 esac
 if [ "$name" = splash ];then perl "$probe" "$out/$name" "$exe" --root /var/tmp/jaguar "$target" /Applications/Utilities/Installer.app/Contents/MacOS/Installer
 else perl "$probe" "$out/$name" "$exe" --root /var/tmp/jaguar "$target";fi
done
echo BASELINE010_COMPLETE
