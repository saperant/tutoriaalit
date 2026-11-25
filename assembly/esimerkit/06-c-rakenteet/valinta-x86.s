    .text
    .globl    laske
laske:
    cmpl    $6, %edi
    ja    .L11
    leaq    .L4(%rip), %rcx
    movl    %edi, %edi
    movslq    (%rcx,%rdi,4), %rax
    addq    %rcx, %rax
    jmp    *%rax
    .section    .rodata
.L4:
    .long    .L10-.L4
    .long    .L9-.L4
    .long    .L8-.L4
    .long    .L7-.L4
    .long    .L6-.L4
    .long    .L5-.L4
    .long    .L3-.L4
    .text
.L5:
    movq    %rdx, %rax
    xorq    %rsi, %rax
    ret
.L3:
    movq    %rsi, %rax
    movl    %edx, %ecx
    salq    %cl, %rax
    ret
.L10:
    leaq    (%rdx,%rsi), %rax
    ret
.L9:
    movq    %rsi, %rax
    subq    %rdx, %rax
    ret
.L8:
    movq    %rdx, %rax
    imulq    %rsi, %rax
    ret
.L7:
    movq    %rdx, %rax
    andq    %rsi, %rax
    ret
.L6:
    movq    %rdx, %rax
    orq    %rsi, %rax
    ret
.L11:
    xorl    %eax, %eax
    ret
