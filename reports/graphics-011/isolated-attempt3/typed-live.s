.text
	.align 2,0x90
.globl _rm_barrier
_rm_barrier:
	pushl %ebp
	movl %esp,%ebp
#APP
	lock; addl $0,0(%esp)
#NO_APP
	leave
	ret
	.align 2,0x90
_cas:
	pushl %ebp
	movl %esp,%ebp
	pushl %esi
	movl 8(%ebp),%edx
	movl 12(%ebp),%ecx
	movl 16(%ebp),%esi
	movl %ecx,%eax
#APP
	lock; cmpxchgl %esi,(%edx)
#NO_APP
	movl %eax,%ecx
	popl %esi
	leave
	ret
	.align 2,0x90
_native_read:
	pushl %ebp
	movl %esp,%ebp
	pushl %edi
	pushl %esi
	movl 8(%ebp),%edi
	movl 12(%ebp),%eax
	cmpl $1,%eax
	jne L5
	movb (%edi),%al
	movzbl %al,%edx
	jmp L9
L5:
	cmpl $2,%eax
	jne L6
	movzwl (%edi),%eax
	movzwl %ax,%edx
L9:
	xorl %ecx,%ecx
	movl %edx,%eax
	movl %ecx,%edx
	jmp L8
L6:
	cmpl $4,%eax
	je L7
	xorl %ecx,%ecx
	movl %ecx,%eax
	movl %ecx,%edx
	movl %ecx,%esi
#APP
	xchgl %ebx,%esi; lock; cmpxchg8b (%edi); xchgl %ebx,%esi
#NO_APP
	movl %eax,%ecx
	movl %edx,%eax
	xorl %edx,%edx
	movl %eax,%esi
	movl %edx,%edi
	movl %esi,%edi
	xorl %esi,%esi
	movl %ecx,%eax
	orl %esi,%eax
	orl %edi,%edx
	jmp L10
L7:
	movl (%edi),%eax
	xorl %edx,%edx
L10:
L8:
	popl %esi
	popl %edi
	leave
	ret
	.align 2,0x90
_native_cas:
	pushl %ebp
	movl %esp,%ebp
	subl $32,%esp
	pushl %edi
	pushl %esi
	movl 12(%ebp),%eax
	cmpl $1,%eax
	jne L12
	movzbl 16(%ebp),%eax
	movl 24(%ebp),%edx
	movl 8(%ebp),%ecx
#APP
	lock; cmpxchgb %dl,(%ecx)
#NO_APP
	cmpb 16(%ebp),%al
	sete %al
	jmp L20
L12:
	cmpl $2,%eax
	jne L14
	movzwl 16(%ebp),%eax
	movl 24(%ebp),%edx
	movl 8(%ebp),%edi
#APP
	lock; cmpxchgw %dx,(%edi)
#NO_APP
	cmpw 16(%ebp),%ax
	sete %al
	jmp L20
L14:
	cmpl $4,%eax
	je L16
	movl 16(%ebp),%ecx
	movl %ecx,-8(%ebp)
	movl 20(%ebp),%eax
	xorl %edx,%edx
	movl %eax,-12(%ebp)
	movl 24(%ebp),%esi
	movl 24(%ebp),%eax
	movl 28(%ebp),%edx
	movl %edx,-20(%ebp)
	movl $0,-16(%ebp)
	movl %ecx,%eax
	movl -12(%ebp),%edx
	movl 8(%ebp),%edi
	movl -20(%ebp),%ecx
#APP
	xchgl %ebx,%esi; lock; cmpxchg8b (%edi); xchgl %ebx,%esi; sete -1(%ebp)
#NO_APP
	movzbl -1(%ebp),%eax
	jmp L22
L16:
	addl $-4,%esp
	movl 24(%ebp),%eax
	pushl %eax
	movl 16(%ebp),%edx
	pushl %edx
	movl 8(%ebp),%ecx
	pushl %ecx
	call _cas
	cmpl 16(%ebp),%eax
	sete %al
L20:
	andl $255,%eax
L22:
	leal -40(%ebp),%esp
	popl %esi
	popl %edi
	leave
	ret
	.align 2,0x90
_field:
	pushl %ebp
	movl %esp,%ebp
	subl $32,%esp
	pushl %edi
	pushl %esi
	movl 16(%ebp),%eax
	decl %eax
	cmpl $7,%eax
	ja L27
	movl 8(%ebp),%eax
	movl 4(%eax),%eax
	movl %eax,-4(%ebp)
	cmpl %eax,12(%ebp)
	ja L27
	subl 12(%ebp),%eax
	cmpl %eax,16(%ebp)
	ja L27
	xorl %edx,%edx
	movl 8(%ebp),%ecx
	movl 12(%ecx),%ecx
	movl %ecx,-16(%ebp)
	cmpl %ecx,%edx
	jae L27
	movl %edx,-8(%ebp)
L29:
	movl -8(%ebp),%edi
	movl 8(%ebp),%esi
	addl 8(%esi),%edi
	movl (%edi),%eax
	cmpl %eax,12(%ebp)
	jb L28
	movl 12(%ebp),%ecx
	subl %eax,%ecx
	movl %ecx,%eax
	movl 4(%edi),%ecx
	cmpl %ecx,%eax
	jae L28
	movl %ecx,%esi
	subl %eax,%esi
	movl %esi,%eax
	cmpl %eax,16(%ebp)
	ja L28
	leal -1(%ecx),%eax
	cmpl $1,%eax
	jbe L33
	cmpl $4,%ecx
	je L33
	cmpl $8,%ecx
	jne L27
L33:
	movl (%edi),%eax
	movl %eax,-12(%ebp)
	xorl %edx,%edx
	divl %ecx
	testl %edx,%edx
	jne L27
	movl -4(%ebp),%esi
	cmpl %esi,-12(%ebp)
	ja L27
	movl %esi,%eax
	subl -12(%ebp),%eax
	cmpl %eax,%ecx
	ja L27
	movl 8(%edi),%eax
	testl %eax,%eax
	je L31
	cmpl $1,%eax
	jne L27
	cmpl $4,%ecx
	jne L27
L31:
	movl %edi,%eax
	jmp L35
L28:
	addl $12,-8(%ebp)
	incl %edx
	cmpl -16(%ebp),%edx
	jb L29
L27:
	xorl %eax,%eax
L35:
	popl %esi
	popl %edi
	leave
	ret
	.align 2,0x90
_logical:
	pushl %ebp
	movl %esp,%ebp
	movl 8(%ebp),%eax
	movl 12(%ebp),%edx
	movl 16(%ebp),%ecx
	cmpl $1,8(%eax)
	je L37
	movl %edx,%eax
	movl %ecx,%edx
	jmp L38
L37:
	movl %edx,%eax
	roll $5,%eax
	xorl %edx,%edx
L38:
	leave
	ret
	.align 2,0x90
_physical:
	pushl %ebp
	movl %esp,%ebp
	movl 8(%ebp),%eax
	movl 12(%ebp),%edx
	movl 16(%ebp),%ecx
	cmpl $1,8(%eax)
	je L40
	movl %edx,%eax
	movl %ecx,%edx
	jmp L41
L40:
	movl %edx,%eax
	roll $27,%eax
	xorl %edx,%edx
L41:
	leave
	ret
	.align 2,0x90
.globl _rm_read
_rm_read:
	pushl %ebp
	movl %esp,%ebp
	subl $32,%esp
	pushl %edi
	pushl %esi
	movl 8(%ebp),%edi
	addl $-4,%esp
	movl 16(%ebp),%eax
	pushl %eax
	movl 12(%ebp),%eax
	pushl %eax
	pushl %edi
	call _field
	addl $16,%esp
	movl %eax,%esi
	testl %esi,%esi
	jne L43
	movl $22,%eax
	jmp L47
L43:
	cmpl $8,4(%esi)
	jne L44
	cmpl $0,16(%edi)
	jne L44
	movl $13,%eax
	jmp L47
L44:
	addl $-4,%esp
	addl $-8,%esp
	pushl 4(%esi)
	movl (%esi),%eax
	addl (%edi),%eax
	pushl %eax
	call _native_read
	addl $16,%esp
	pushl %edx
	pushl %eax
	pushl %esi
	call _logical
	movl %eax,-8(%ebp)
	movl %edx,-4(%ebp)
	cmpl $8,16(%ebp)
	je L45
	movl $1,%eax
	xorl %edx,%edx
	movb 16(%ebp),%cl
	salb $3,%cl
	shldl %cl,%eax,%edx
	sall %cl,%eax
	testb $32,%cl
	je L48
	movl %eax,%edx
	xorl %eax,%eax
L48:
	addl $-1,%eax
	adcl $-1,%edx
	movl %eax,-16(%ebp)
	movl %edx,-12(%ebp)
	jmp L46
L45:
	movl $-1,-16(%ebp)
	movl $-1,-12(%ebp)
L46:
	movl 12(%ebp),%eax
	subl (%esi),%eax
	movl 4(%esi),%esi
	subl %eax,%esi
	movl %esi,%eax
	subl 16(%ebp),%eax
	leal 0(,%eax,8),%ecx
	movl -8(%ebp),%eax
	movl -4(%ebp),%edx
	shrdl %cl,%edx,%eax
	shrl %cl,%edx
	testb $32,%cl
	je L49
	movl %edx,%eax
	xorl %edx,%edx
L49:
	movl 20(%ebp),%ecx
	andl -16(%ebp),%eax
	andl -12(%ebp),%edx
	movl %eax,(%ecx)
	movl %edx,4(%ecx)
	xorl %eax,%eax
L47:
	leal -40(%ebp),%esp
	popl %esi
	popl %edi
	leave
	ret
	.align 2,0x90
.globl _rm_write
_rm_write:
	pushl %ebp
	movl %esp,%ebp
	subl $48,%esp
	pushl %edi
	pushl %esi
	movl 12(%ebp),%edi
	movl 16(%ebp),%esi
	addl $-4,%esp
	pushl %esi
	pushl %edi
	movl 8(%ebp),%eax
	pushl %eax
	call _field
	addl $16,%esp
	movl %eax,-4(%ebp)
	movl 8(%ebp),%edx
	cmpl $0,16(%edx)
	jne L51
	movl $13,%eax
	jmp L59
L51:
	cmpl $0,-4(%ebp)
	jne L52
	movl $22,%eax
	jmp L59
L52:
	movl %edi,%eax
	movl -4(%ebp),%ecx
	subl (%ecx),%eax
	movl 4(%ecx),%edx
	subl %eax,%edx
	movl %edx,%eax
	subl %esi,%eax
	sall $3,%eax
	movl %eax,-16(%ebp)
	cmpl $8,%esi
	je L53
	movl $1,%eax
	xorl %edx,%edx
	movl %esi,%ecx
	salb $3,%cl
	shldl %cl,%eax,%edx
	sall %cl,%eax
	testb $32,%cl
	je L60
	movl %eax,%edx
	xorl %eax,%eax
L60:
	movl %eax,%esi
	movl %edx,%edi
	addl $-1,%esi
	adcl $-1,%edi
	jmp L54
L53:
	movl $-1,%esi
	movl $-1,%edi
L54:
	movl 20(%ebp),%eax
	movl 24(%ebp),%edx
	andl %esi,%eax
	andl %edi,%edx
	movb -16(%ebp),%cl
	shldl %cl,%eax,%edx
	sall %cl,%eax
	testb $32,%cl
	je L61
	movl %eax,%edx
	xorl %eax,%eax
L61:
	movl %eax,-32(%ebp)
	movl %edx,-28(%ebp)
	shldl %cl,%esi,%edi
	sall %cl,%esi
	testb $32,%cl
	je L62
	movl %esi,%edi
	xorl %esi,%esi
L62:
	movl %esi,-24(%ebp)
	movl %edi,-20(%ebp)
L58:
	addl $-8,%esp
	movl -4(%ebp),%ecx
	pushl 4(%ecx)
	movl (%ecx),%eax
	movl 8(%ebp),%edx
	addl (%edx),%eax
	pushl %eax
	call _native_read
	addl $16,%esp
	movl %eax,-12(%ebp)
	movl %edx,-8(%ebp)
	addl $-4,%esp
	pushl %edx
	pushl %eax
	movl -4(%ebp),%ecx
	pushl %ecx
	call _logical
	addl $16,%esp
	movl %eax,%esi
	movl %edx,%edi
	movl -24(%ebp),%eax
	notl %eax
	movl -20(%ebp),%edx
	notl %edx
	andl %esi,%eax
	andl %edi,%edx
	orl -32(%ebp),%eax
	orl -28(%ebp),%edx
	addl $-8,%esp
	addl $-4,%esp
	pushl %edx
	pushl %eax
	movl -4(%ebp),%eax
	pushl %eax
	call _physical
	addl $16,%esp
	pushl %edx
	pushl %eax
	movl -12(%ebp),%edx
	movl -8(%ebp),%ecx
	pushl %ecx
	pushl %edx
	movl -4(%ebp),%ecx
	pushl 4(%ecx)
	movl (%ecx),%eax
	movl 8(%ebp),%edx
	addl (%edx),%eax
	pushl %eax
	call _native_cas
	addl $32,%esp
	testl %eax,%eax
	je L58
	xorl %eax,%eax
L59:
	leal -56(%ebp),%esp
	popl %esi
	popl %edi
	leave
	ret
	.align 2,0x90
.globl _rm_cas32
_rm_cas32:
	pushl %ebp
	movl %esp,%ebp
	subl $20,%esp
	pushl %edi
	addl $-4,%esp
	pushl $4
	movl 12(%ebp),%eax
	pushl %eax
	movl 8(%ebp),%edx
	pushl %edx
	call _field
	addl $16,%esp
	movl %eax,-4(%ebp)
	movl 8(%ebp),%ecx
	cmpl $0,16(%ecx)
	jne L64
	movl $13,%eax
	jmp L67
L64:
	cmpl $0,-4(%ebp)
	je L66
	movl 12(%ebp),%edx
	movl -4(%ebp),%eax
	cmpl (%eax),%edx
	jne L66
	cmpl $4,4(%eax)
	je L65
L66:
	movl $22,%eax
	jmp L67
L65:
	addl $-4,%esp
	addl $-4,%esp
	movl 20(%ebp),%eax
	xorl %edx,%edx
	pushl %edx
	pushl %eax
	movl -4(%ebp),%ecx
	pushl %ecx
	call _physical
	addl $16,%esp
	pushl %eax
	addl $-4,%esp
	movl 16(%ebp),%eax
	xorl %edx,%edx
	movl %eax,-12(%ebp)
	movl %edx,-8(%ebp)
	pushl %edx
	pushl %eax
	movl -4(%ebp),%edx
	pushl %edx
	call _physical
	addl $16,%esp
	pushl %eax
	movl 12(%ebp),%eax
	movl 8(%ebp),%ecx
	addl (%ecx),%eax
	pushl %eax
	call _cas
	addl $16,%esp
	movl %eax,%edi
	addl $-4,%esp
	movl -12(%ebp),%eax
	movl -8(%ebp),%edx
	pushl %edx
	pushl %eax
	movl -4(%ebp),%edx
	pushl %edx
	call _physical
	cmpl %eax,%edi
	sete %dl
	movl 24(%ebp),%eax
	movl %edx,%ecx
	andl $1,%ecx
	movl %ecx,(%eax)
	xorl %eax,%eax
L67:
	movl -24(%ebp),%edi
	leave
	ret
