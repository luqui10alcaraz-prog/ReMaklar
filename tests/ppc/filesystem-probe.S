/* Own PPC32 syscall/metadata probe, no Apple code. SPDX-License-Identifier: MIT */
.text
.globl _start
_start:
/* Every unexpected success/error exits with the failing source line. */
.macro addr reg, label
 lis \reg,\label@ha
 addi \reg,\reg,\label@l
.endm
.macro call number
 li 0,\number
 sc
 b fail
.endm
.macro equal reg, value
 cmpwi \reg,\value
 bne fail
.endm
.macro step number
 li 29,\number
.endm
 step 1
 li 3,0
 call 60
 step 2
 addr 3,created
 li 4,488 /* 0750 */
 call 136
 step 3
 addr 3,payload
 li 4,2562 /* O_RDWR|O_CREAT|O_EXCL */
 li 5,416 /* 0640 */
 call 5
 mr 30,3
 step 4
 addr 4,data
 li 5,8
 call 4
 equal 3,8
 step 5
 mr 3,30
 li 4,0
 li 5,0
 li 6,0
 call 199
 equal 3,0
 equal 4,0
 step 6
 mr 3,30
 addr 4,buffer
 li 5,8
 call 3
 equal 3,8
 addr 5,buffer
 lwz 6,0(5)
 lis 7,0x4100
 ori 7,7,0x427f
 cmpw 6,7
 bne fail
 step 7
 mr 3,30
 addr 4,metadata
 call 189
 addr 5,metadata
 lhz 6,8(5)
 andi. 6,6,511
 equal 6,416
 lwz 6,48(5)
 equal 6,0
 lwz 6,52(5)
 equal 6,8
 step 8
 mr 3,30
 call 6
 step 9
 mr 3,30
 addr 4,data
 li 5,1
 li 0,4
 sc
 b closed_error
 b fail
closed_error:
 equal 3,9
 step 10
 addr 3,payload
 addr 4,renamed
 call 128
 step 11
 addr 3,renamed
 li 4,384 /* 0600 */
 call 15
 step 12
 addr 3,renamed
 li 4,9 /* WRONLY|APPEND */
 li 5,0
 call 5
 mr 30,3
 addr 4,data
 li 5,1
 call 4
 equal 3,1
 mr 3,30
 call 6
 step 13
 addr 3,renamed
 addr 4,metadata
 call 188
 addr 5,metadata
 lwz 6,52(5)
 equal 6,9
 lhz 6,8(5)
 andi. 6,6,511
 equal 6,384
 step 14
 addr 3,created
 li 0,137
 sc
 b not_empty
 b fail
not_empty:
 equal 3,66
 step 15
 addr 3,created
 call 12
 addr 3,relative
 li 4,448 /* 0700 */
 call 136
 addr 3,relative
 call 137
 step 16
 addr 3,root
 call 12
 addr 3,renamed
 call 10
 addr 3,created
 call 137
 step 17
 addr 3,payload
 addr 4,metadata
 li 0,188
 sc
 b missing
 b fail
missing:
 equal 3,2
 li 3,1
 addr 4,message
 li 5,18
 call 4
 li 3,0
 li 0,1
 sc
fail:
 mr 3,29
 li 0,1
 sc
.align 2
created: .asciz "/fixtures/fs-work/created"
payload: .asciz "/fixtures/fs-work/created/payload"
renamed: .asciz "/fixtures/fs-work/created/renamed"
relative: .asciz "sub"
root: .asciz "/"
message: .ascii "filesystem PPC OK\n"
data: .byte 0x41,0,0x42,0x7f,0x80,0xff,0x0a,0x43
.align 3
buffer: .space 8
metadata: .space 96
