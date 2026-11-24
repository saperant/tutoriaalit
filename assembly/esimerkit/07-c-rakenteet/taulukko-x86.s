    .text
    .globl    taulukon_summa
taulukon_summa:
    testq    %rsi, %rsi
    jle    .L4
    leaq    (%rdi,%rsi,8), %rdx
    xorl    %eax, %eax
.L3:
    addq    (%rdi), %rax
    addq    $8, %rdi
    cmpq    %rdx, %rdi
    jne    .L3
    ret
.L4:
    xorl    %eax, %eax
    ret
