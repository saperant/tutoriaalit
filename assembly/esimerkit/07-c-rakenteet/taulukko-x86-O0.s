    .text
    .globl    taulukon_summa
taulukon_summa:
    pushq    %rbp
    movq    %rsp, %rbp
    movq    %rdi, -24(%rbp)
    movq    %rsi, -32(%rbp)
    movq    $0, -8(%rbp)
    movq    $0, -16(%rbp)
    jmp    .L2
.L3:
    movq    -16(%rbp), %rax
    leaq    0(,%rax,8), %rdx
    movq    -24(%rbp), %rax
    addq    %rdx, %rax
    movq    (%rax), %rax
    addq    %rax, -8(%rbp)
    addq    $1, -16(%rbp)
.L2:
    movq    -16(%rbp), %rax
    cmpq    -32(%rbp), %rax
    jl    .L3
    movq    -8(%rbp), %rax
    popq    %rbp
    ret
