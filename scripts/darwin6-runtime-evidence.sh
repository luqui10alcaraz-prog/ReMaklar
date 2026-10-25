#!/bin/sh
# Record unchanged originals and halt cleanly. FAT must be mounted.
# SPDX-License-Identifier: MIT
set -e
out=/var/tmp/remaklar-runtime-006
cd /var/tmp/remaklar/research/samples-local
md5 bin/ls bin/pwd bin/echo bin/cat usr/bin/true usr/bin/false usr/lib/dyld usr/lib/libSystem.B.dylib usr/lib/system/libmathCommon.A.dylib usr/lib/libobjc.A.dylib System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation > "$out/darwin-originals.md5"
cd /var/tmp/jaguar
md5 usr/lib/dyld usr/lib/libSystem.B.dylib usr/lib/libobjc.A.dylib usr/lib/system/libmathCommon.A.dylib System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation System/Library/Frameworks/Foundation.framework/Versions/C/Foundation System/Library/Frameworks/AppKit.framework/Versions/C/AppKit System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/CoreGraphics.framework/Versions/A/CoreGraphics "System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/CoreGraphics.framework/Versions/A/Resources/Window Manager" "System/Library/ColorSync/Profiles/Generic RGB Profile.icc" > "$out/jaguar-originals.md5"
cd /var/tmp/remaklar
md5 build/qemu-darwin6/ppc-darwin-user/qemu-ppc build/objc-smoke-006 build/cf-smoke-006 build/mach-runtime-006 build/graphics-contracts-006 build/quartz-ppc build/foundation-ppc > "$out/owned.md5"
gnutar czf /exchange/evid006.tgz -C /var/tmp remaklar-runtime-006
sync
umount /exchange
echo RUNTIME_EVIDENCE_COMPLETE
halt
