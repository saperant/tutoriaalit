    .text
    .globl    listan_summa
listan_summa:
    xorl    %eax, %eax
    testq    %rdi, %rdi
    je    .L4
.L3:
    addq    (%rdi), %rax
    movq    8(%rdi), %rdi
    testq    %rdi, %rdi
    jne    .L3
    ret
.L4:
    ret
