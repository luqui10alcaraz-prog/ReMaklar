/* Own ABI smoke caller. No ObjC class metadata: compiled .m is a separate test.
 * Calls original runtime APIs/message dispatcher. SPDX-License-Identifier: MIT */
.text
.globl _start
_start:
 stwu 1,-128(1)
.macro addr reg, label
 lis \reg,\label@ha
 addi \reg,\reg,\label@l
.endm
.macro invoke offset
 lis 12,0x1000
 lwz 12,0x1000+\offset(12)
 mtctr 12
 bctrl
.endm
 /* Explicit API startup for this ABI-only caller, not a replacement crt1. */
 invoke 12 /* mach_init */
 lis 12,0x1000
 lwz 12,0x1010(12) /* address of exported _cthread_init_routine */
 lwz 12,0(12)
 mtctr 12
 bctrl
 invoke 20 /* _objcInit: invokes original CF initialization */
 addr 3,class_name
 invoke 0
 cmpwi 3,0
 beq fail
 mr 30,3
 addr 3,new_name
 invoke 4
 mr 4,3
 mr 3,30
 invoke 8
 cmpwi 3,0
 beq fail
 mr 30,3
 addr 3,free_name
 invoke 4
 mr 4,3
 mr 3,30
 invoke 8
 li 3,1
 addr 4,message
 li 5,20
 li 0,4
 sc
 b fail
 li 3,0
 li 0,1
 sc
fail:
 li 3,90
 li 0,1
 sc
class_name: .asciz "Object"
new_name: .asciz "new"
free_name: .asciz "free"
message: .ascii "objc runtime PPC OK\n"
